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
    with xr.open_dataset(sample_disp_product) as disp:
        valid = np.isfinite(disp["displacement"].values)

    assert calibration.shape == (1, *valid.shape)
    assert np.isfinite(calibration[0][valid]).all()
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
