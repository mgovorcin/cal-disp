"""End-to-end test of ``run_calibration`` against the installed Venti."""

from __future__ import annotations

import socket
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from cal_disp.config._algorithm import AlgorithmParameters, CalibrationOptions
from cal_disp.workflow import run_calibration


@pytest.fixture
def no_network(monkeypatch):
    """Fail on any network connection (GNSS must come from pre-staged files)."""

    def _blocked(*_args, **_kwargs):
        raise RuntimeError("network access attempted during an offline run")

    monkeypatch.setattr(socket.socket, "connect", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)


@pytest.mark.usefixtures("no_network")
@pytest.mark.parametrize("grid_type", ["constant", "variable"])
def test_run_calibration_offline(
    tmp_path: Path,
    sample_disp_product: Path,
    sample_static_los: Path,
    sample_unr_data: tuple[Path, Path],
    grid_type: str,
):
    lookup_file, tenv8_dir = sample_unr_data
    output_dir = tmp_path / "out"

    out_path = run_calibration(
        disp_file=sample_disp_product,
        unr_grid_latlon_file=lookup_file,
        unr_timeseries_dir=tenv8_dir,
        output_dir=output_dir,
        los_file=sample_static_los,
        algorithm_parameters=AlgorithmParameters(
            calibration_options=CalibrationOptions(grid_type=grid_type)
        ),
    )

    assert out_path.exists()
    with xr.open_dataset(out_path) as ds:
        calibration = ds["calibration"].values
        calibration_std = ds["calibration_std"].values
        uncertainty_source = ds["calibration_std"].attrs["uncertainty_source"]
    with xr.open_dataset(sample_disp_product) as disp:
        valid = np.isfinite(disp["displacement"].values)

    assert calibration.shape == (1, *valid.shape)
    assert np.isfinite(calibration[0][valid]).all()
    # calibration_std holds the GNSS reference uncertainty (m), documented as such
    assert calibration_std.shape == calibration.shape
    assert (calibration_std[0][valid] > 0).all()
    assert (calibration_std[0][valid] < 0.01).all()
    assert uncertainty_source.startswith("GNSS reference uncertainty")
    # GNSS came only from the pre-staged files of this grid type
    staged = {p.name for p in tenv8_dir.glob(f"*_IGS20_{grid_type}.tenv8")}
    used = {p.name for p in (output_dir / "scratch" / "gnss").glob("*.tenv8")}
    assert used == staged
    assert len(staged) == 4


def test_run_calibration_rejects_mismatched_unr_type(
    tmp_path: Path,
    sample_disp_product: Path,
    sample_static_los: Path,
    sample_unr_data: tuple[Path, Path],
):
    lookup_file, tenv8_dir = sample_unr_data
    with pytest.raises(ValueError, match="does not match the calibration grid_type"):
        run_calibration(
            disp_file=sample_disp_product,
            unr_grid_latlon_file=lookup_file,
            unr_timeseries_dir=tenv8_dir,
            output_dir=tmp_path / "out",
            los_file=sample_static_los,
            calibration_reference_type="variable",
        )


def test_run_calibration_requires_staged_grid_type(
    tmp_path: Path,
    sample_disp_product: Path,
    sample_static_los: Path,
    sample_unr_data: tuple[Path, Path],
):
    lookup_file, tenv8_dir = sample_unr_data
    for path in tenv8_dir.glob("*_constant.tenv8"):
        path.unlink()
    with pytest.raises(FileNotFoundError, match="--grid-type constant"):
        run_calibration(
            disp_file=sample_disp_product,
            unr_grid_latlon_file=lookup_file,
            unr_timeseries_dir=tenv8_dir,
            output_dir=tmp_path / "out",
            los_file=sample_static_los,
        )


@pytest.fixture
def captured_core(monkeypatch):
    """Replace Venti's core with a recorder returning a zero surface."""
    from venti import surface

    calls: list[dict] = []

    def _fake(disp, gnss_los, mask, ref_point, window_size, **kwargs):
        calls.append(
            {
                "disp": disp,
                "gnss_los": gnss_los,
                "mask": mask,
                "ref_point": ref_point,
                "window_size": window_size,
                **kwargs,
            }
        )
        return surface.CalibrationSurface(np.zeros_like(disp))

    monkeypatch.setattr(surface, "estimate_calibration_surface", _fake)
    return calls


@pytest.mark.parametrize("apply_set", [True, False])
def test_run_calibration_venti_core_inputs(
    tmp_path: Path,
    sample_disp_product_with_corrections: Path,
    sample_static_los: Path,
    sample_unr_data: tuple[Path, Path],
    captured_core,
    apply_set: bool,
):
    lookup_file, tenv8_dir = sample_unr_data
    options = CalibrationOptions(
        apply_solid_earth_tide_correction=apply_set,
        downsample_factor=2,
        downsample_weighted=True,
        event_mask_buffer_pixels=2,
    )

    out_path = run_calibration(
        disp_file=sample_disp_product_with_corrections,
        unr_grid_latlon_file=lookup_file,
        unr_timeseries_dir=tenv8_dir,
        output_dir=tmp_path / "out",
        los_file=sample_static_los,
        algorithm_parameters=AlgorithmParameters(calibration_options=options),
    )

    (call,) = captured_core
    with xr.open_dataset(
        sample_disp_product_with_corrections, group="corrections"
    ) as corr:
        set_layer = corr["solid_earth_tide"].values
    with xr.open_dataset(sample_disp_product_with_corrections) as disp:
        coherence = disp["temporal_coherence"].values

    # SET is handed to Venti as a correction (removed before the fit)
    if apply_set:
        (correction,) = call["corrections"]
        np.testing.assert_allclose(correction, set_layer, rtol=1e-6)
    else:
        assert list(call["corrections"]) == []
    # Displacement in m, GNSS converted from mm to m, valid reference pixel
    assert call["disp"].dtype == np.float32
    assert np.nanmax(np.abs(call["gnss_los"])) < 0.01
    assert call["mask"][call["ref_point"]]
    assert call["window_size"] == options.window_size_pixels
    assert call["options"].model_dump(
        include={"apply_solid_earth_tide_correction", "event_mask_buffer_pixels"}
    ) == {
        "apply_solid_earth_tide_correction": apply_set,
        "event_mask_buffer_pixels": 2,
    }
    assert call["downsample_factor"] == 2
    np.testing.assert_allclose(call["downsample_weights"], coherence, rtol=1e-6)

    with xr.open_dataset(out_path) as ds:
        applied = ds["calibration"].attrs["corrections_applied"]
    assert applied == ("solid_earth_tide" if apply_set else "none")


def test_run_calibration_without_set_layer_warns(
    tmp_path: Path,
    sample_disp_product: Path,
    sample_static_los: Path,
    sample_unr_data: tuple[Path, Path],
    captured_core,
    caplog,
):
    lookup_file, tenv8_dir = sample_unr_data
    run_calibration(
        disp_file=sample_disp_product,
        unr_grid_latlon_file=lookup_file,
        unr_timeseries_dir=tenv8_dir,
        output_dir=tmp_path / "out",
        los_file=sample_static_los,
    )

    assert list(captured_core[0]["corrections"]) == []
    assert "calibrating without SET" in caplog.text


def test_find_reference_point(tmp_path: Path):
    from cal_disp.workflow import _find_reference_point

    coherence = np.full((40, 50), 0.3, dtype=np.float32)
    coherence[5:15, 30:45] = 0.99  # best block
    coherence[30, 5] = 1.0  # higher, but masked out
    mask = np.ones(coherence.shape, dtype=bool)
    mask[30, 5] = False
    ds = xr.Dataset(
        {"temporal_coherence": (["y", "x"], coherence)},
        coords={"y": 1000.0 - 30.0 * np.arange(40), "x": 30.0 * np.arange(50)},
    )

    row, col = _find_reference_point(ds, mask, tmp_path)

    assert 5 <= row < 15
    assert 30 <= col < 45


def test_run_calibration_clips_negative_std(
    tmp_path: Path,
    sample_disp_product: Path,
    sample_static_los: Path,
    sample_unr_data: tuple[Path, Path],
    monkeypatch,
):
    """RBF-interpolated GNSS sigmas can overshoot below 0: never written."""
    import venti.gnss

    def _overshooting_std(**kwargs):
        std = np.full(kwargs["los_east"].shape, 0.5, dtype=np.float32)  # mm
        std[: len(std) // 2] = -0.3
        return std

    monkeypatch.setattr(venti.gnss, "compute_gnss_los_std", _overshooting_std)
    lookup_file, tenv8_dir = sample_unr_data
    out_path = run_calibration(
        disp_file=sample_disp_product,
        unr_grid_latlon_file=lookup_file,
        unr_timeseries_dir=tenv8_dir,
        output_dir=tmp_path / "out",
        los_file=sample_static_los,
    )

    with xr.open_dataset(out_path) as ds:
        std = ds["calibration_std"].values[0]
    assert std.min() == 0  # negative sigmas clipped, not written
    np.testing.assert_array_equal(std[:80], 0)
    np.testing.assert_allclose(std[120:], 0.0005)


def test_gnss_field_on_fit_grid_matches_full_resolution(
    tmp_path: Path,
    sample_disp_product: Path,
    sample_static_los: Path,
    sample_unr_data: tuple[Path, Path],
    captured_core,
):
    """With downsample_factor > 1 the GNSS field is computed on the coarse
    fit grid and upsampled; it must match the full-resolution field."""
    import rasterio

    # Real LOS rasters vary smoothly; the fixture's is random per pixel, which
    # would change the LOS each station samples on the coarse grid.
    smooth_los = tmp_path / "smooth_los.tif"
    with rasterio.open(sample_static_los) as src:
        profile = src.profile
    xx = np.linspace(0, 1, 200, dtype=np.float32)[None, :].repeat(200, axis=0)
    east, north = -0.6 + 0.05 * xx, np.full_like(xx, -0.1)
    up = np.sqrt(1 - east**2 - north**2)
    with rasterio.open(smooth_los, "w", **profile) as dst:
        dst.write(np.stack([east, north, up]))

    lookup_file, tenv8_dir = sample_unr_data
    for factor in (1, 4):
        run_calibration(
            disp_file=sample_disp_product,
            unr_grid_latlon_file=lookup_file,
            unr_timeseries_dir=tenv8_dir,
            output_dir=tmp_path / f"out{factor}",
            los_file=smooth_los,
            algorithm_parameters=AlgorithmParameters(
                calibration_options=CalibrationOptions(
                    grid_type="variable", downsample_factor=factor
                )
            ),
        )
    full, coarse = (call["gnss_los"] for call in captured_core)
    cache = np.load(
        tmp_path
        / "out4/scratch/gnss"
        / next(
            p.name
            for p in (tmp_path / "out4/scratch/gnss").glob("gnss_los_disp_*.npy")
            if "std" not in p.name
        )
    )

    assert cache.shape == (50, 50)  # computed on the fit grid
    assert coarse.shape == full.shape == (200, 200)
    spread = np.ptp(full)
    assert spread > 0
    # Between the outermost block centres (pixels 2..198) it is interpolated
    inner = (slice(2, 199), slice(2, 199))
    np.testing.assert_allclose(coarse[inner], full[inner], atol=0.005 * spread)
    # In the 2-pixel edge band the edge value is held
    np.testing.assert_allclose(coarse, full, atol=0.03 * spread)
