"""Release parameter files (Venti plan T49): gamma reproducible, v0.5 = T46 set."""

import re
from pathlib import Path

import yaml

from cal_disp.config._algorithm import AlgorithmParameters

ROOT = Path(__file__).resolve().parents[1]


def _golden_build_config() -> dict:
    """The algorithm parameters scripts/build_golden_output.sh writes for the golden."""
    script = (ROOT / "scripts" / "build_golden_output.sh").read_text()
    m = re.search(r"algorithm_parameters\.yaml\" <<'EOF'\n(.*?)\nEOF", script, re.S)
    assert m, "no algorithm_parameters heredoc in build_golden_output.sh"
    return yaml.safe_load(m.group(1))


def _load(name: str) -> AlgorithmParameters:
    return AlgorithmParameters.model_validate(
        yaml.safe_load((ROOT / "configs" / name).read_text())
    )


def test_gamma_file_is_the_golden_configuration():
    """Decision 0001: the gamma file reproduces the 0.3 golden's parameters."""
    golden = AlgorithmParameters.model_validate(_golden_build_config())
    assert _load("algorithm_parameters_gamma.yaml") == golden
    cal = golden.calibration_options
    assert cal.window_size_meters == 600_000.0
    assert cal.apply_tropo_correction is False
    assert cal.unwrap_error_correction is False
    assert cal.surface.method == "windowed_plane"


def test_v05_file_is_the_t46_benchmark_set():
    cal = _load("algorithm_parameters_v05.yaml").calibration_options
    assert cal.surface.method == "loclin"
    assert cal.surface.cutoff_wavelength_meters == 50_000.0
    assert cal.surface.two_pass and cal.surface.fill_gaps
    assert (cal.weights.coherence_power, cal.weights.robust) == (8.0, True)
    assert cal.gnss.buffer_meters == 50_000.0
    assert cal.gnss.exclude_defo_nodes and cal.gnss.reinterpolate_excluded
    # per-frame settings come from the frame table, not this file
    assert cal.surface.regions == "none"
    assert cal.surface.fit_mask is None
    # owner 2026-10-14: sigma_CAL wherever the calibration has a value
    assert cal.uncertainty.extrapolate_sigma is True
    # owner 2026-10-09: off until a trade study confirms it
    assert cal.unwrap_error_correction is False
