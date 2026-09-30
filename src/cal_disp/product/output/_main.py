"""Build main group for calibration products."""

import xarray as xr

from cal_disp._version import __version__

from ._utils import make_spatial_ref


def build_main_dataset(
    calibration: xr.DataArray,
    calibration_std: xr.DataArray | None,
    spatial_ref: xr.DataArray | None,
    sensor: str,
    metadata: dict[str, str] | None,
) -> xr.Dataset:
    """Build main dataset (root group) with calibration data.

    Parameters
    ----------
    calibration : xr.DataArray
        Calibration correction at full DISP resolution.
    calibration_std : xr.DataArray or None
        Calibration uncertainty at full resolution.
    spatial_ref : xr.DataArray or None
        Spatial reference data variable from input DISP product. Its CRS
        attributes are kept verbatim; ``GeoTransform`` is set for this grid.
    sensor : str
        Sensor type: "S1" or "NI".
    metadata : dict[str, str] or None
        Additional metadata.

    Returns
    -------
    xr.Dataset
        Main dataset with calibration data and attributes.

    """
    data_vars: dict[str, xr.DataArray] = {}

    # Calibration with description
    calibration = calibration.copy()
    calibration.attrs.update(
        {
            "description": "Calibration layer for DISP displacement",
            "long_name": "Calibration for DISP",
            "units": "meters",
            "grid_mapping": "spatial_ref",
            "dtype": "float32",
            "coordinates": "time y x",
        }
    )
    data_vars["calibration"] = calibration

    # Calibration uncertainty
    if calibration_std is not None:
        calibration_std = calibration_std.copy()
        calibration_std.attrs.update(
            {
                "description": "Uncertainty in DISP calibration",
                "long_name": "DISP Calibration Uncertainty",
                "units": "meters",
                "grid_mapping": "spatial_ref",
                "dtype": "float32",
                "coordinates": "time y x",
            }
        )
        data_vars["calibration_std"] = calibration_std

    # Spatial reference: DISP CRS attributes + GeoTransform of this grid
    if spatial_ref is not None:
        data_vars["spatial_ref"] = make_spatial_ref(
            spatial_ref, calibration.x.values, calibration.y.values
        )

    ds = xr.Dataset(data_vars)

    # Add global attributes with type information
    base_attrs = {
        "Conventions": "CF-1.8",
        "title": f"OPERA L4 DISP-CAL-{sensor} Calibration Product",
        "institution": "NASA JPL",
        "contact": "operaops@jpl.nasa.gov",
        "source": "OPERA",
        "platform": sensor,
        "spatial_resolution": "30 meteres",
        "temporal_resolution": "12 days",
        "source_url": "https://www.jpl.nasa.gov/go/opera/products/disp-product-suite/",
        "references": "https://opera-adt.github.io/cal-disp/",
        "mision_name": "OPERA",
        "description": f"OPERA Calibration for {sensor} Surface Displacement product",
        "comment": (
            "Subtract calibration layer from DISP displacement to obtain "
            "calibrated displacement"
        ),
        "software": "cal_disp",
        "software_version": __version__,
        "reference_document": "TBD",
        "history": "TBD",
    }

    ds.attrs.update(base_attrs)

    if metadata:
        ds.attrs.update(metadata)

    return ds
