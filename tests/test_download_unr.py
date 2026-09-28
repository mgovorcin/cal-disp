"""Tests for UNR grid staging (URL and local file name per grid type)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from cal_disp.download._stage_unr import download_grid_file


@pytest.mark.parametrize(
    ("grid_type", "remote_dir"),
    [("constant", "time_contsant_gridded"), ("variable", "time_variable_gridded")],
)
def test_download_grid_file(tmp_path: Path, grid_type, remote_dir):
    session = MagicMock()
    session.get.return_value.content = b"2022.0 0 0 0 1 1 1 0\n"

    path = download_grid_file(12, tmp_path, grid_type=grid_type, session=session)

    url = session.get.call_args.args[0]
    assert (
        url
        == f"https://geodesy.unr.edu/grid_timeseries/Version0.3/{remote_dir}"
        "/IGS20/000012_IGS20.tenv8"
    )
    # Same name Venti's download_station looks for, so staged files are reused
    assert path == tmp_path / f"000012_IGS20_{grid_type}.tenv8"
    assert path.read_bytes() == b"2022.0 0 0 0 1 1 1 0\n"


def test_constant_grid_unavailable(tmp_path: Path):
    with pytest.raises(ValueError, match="constant grid only"):
        download_grid_file(12, tmp_path, version="0.2", grid_type="constant")
