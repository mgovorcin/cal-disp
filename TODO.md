# TODO

Planned work that is deliberately **not** in the current release. Items marked
*changes the golden* alter the calibration values: do them together, then
rebuild the golden dataset (`scripts/build_golden_output.sh`) and re-run
`scripts/run_validation.sh` and `docs/notebooks/00_calibration_walkthrough.ipynb`.

## Algorithm

- [ ] **Sample UNR grid stations within a 100 km buffer around the frame**
  (*changes the golden*). Today `_setup_gnss_reference`
  (`src/cal_disp/workflow.py`) passes the frame bounds to Venti's
  `GNSSReference`, which selects grid points strictly inside that box
  (`find_stations_in_bounds`, padding 0), so nothing constrains the GNSS field
  at the frame edges and the RBF extrapolates there. What is needed:
  1. Selection: pad the bounds by 100 km (new algorithm parameter, e.g.
     `gnss_buffer_meters: 100000.0`) and use only staged files, so the
     workflow never downloads.
  2. Staging: `cal-disp download unr` uses `margin_deg=0.5` (about 55 km);
     raise it to a metric 100 km buffer and re-stage the golden GNSS inputs.
  3. LOS at the extra stations: Venti projects each station to LOS with the
     LOS vector sampled **at the station** from the frame's LOS raster and
     drops stations with no look (`venti/gnss/los.py::_sample_los`), so
     stations outside the swath are discarded — widening the box alone has no
     effect (already 106 in-box grid points become 74 on F08882). Either
     extrapolate the LOS vectors beyond the swath (smooth fit of e/n/u over the
     valid pixels, renormalised; check the error by holding out the swath
     edges), or change Venti to interpolate E/N/U to the grid first and project
     per pixel.
  4. Update stage 3 of the walkthrough notebook (station map: frame outline,
     buffer outline, used vs dropped stations).
- [ ] **Unwrapping-error correction** is off by default. Venti segments the
  valid mask into connected components instead of phase discontinuities and
  references the first island; see `docs/notebooks/01_unwrap_cycle_length.ipynb`.
  Needs a phase-discontinuity segmentation in Venti and validation on products
  with known unwrapping errors before it is enabled (*changes the golden*).
- [ ] **Add the unwrapping shifts back into CAL** (do together with the item
  above). CAL should hold every term removed before the fit (troposphere, SET,
  unwrapping shifts, reference offset) plus the fitted surface, so that
  `DISP - CAL` matches the GNSS field at long wavelengths. Venti's
  `estimate_calibration_surface` (`venti/surface.py`) adds back
  `total_correction` and `disp0` but not the `correct_region_offset` shifts,
  which only reach the copy used for the fit; with the correction enabled the
  calibrated DISP would keep the unwrapping errors. Return the per-pixel shift
  (multiples of λ/2) from Venti and add it to the surface.
  Order: the unwrapping error is in the raw unwrapped phase, so the shift
  is applied to the raw DISP first, before the troposphere and SET
  corrections (today Venti removes the corrections first and corrects
  unwrapping afterwards). Caveat for *estimating* the cycle count: on the
  F08882 test case below the jump measured on the raw DISP is 2.38 x λ/2 but
  2.92 x λ/2 once the troposphere is removed (the differential delay across
  the bay biases it), so rounding the raw jump would give 2 cycles instead of
  3. Either estimate on the corrected DISP and apply the integer shift to the
  raw DISP, or accept a shift only when the raw jump is close to an integer
  number of cycles. Test case: on
  F08882 the coastal strip at E 327-343 km, N 3249-3261 km (UTM 15N; DISP
  connected component 10, cut off from the mainland by water) sits
  +3 x λ/2 (8.3 cm) above the mainland after calibration, in both the gamma
  0.3 delivery and the current golden; CAL there should rise by 8.3 cm.
- [ ] **Fitted surface near masked areas** (Venti, *changes the golden*):
  unfitted blocks are 0 rather than NaN before upsampling, which pulls the
  plane toward 0 within a few pixels of masked blocks; `_find_data_extent` is
  off by one (last row/column never fitted); the Hann taper is 0 on window
  edges.
- [ ] **Plane fit robustness** (Venti, *changes the golden*): replace the
  global 15/85 % quantile trim + IDW fill and the every-50th-pixel decimation
  with a robust (Huber/MAD) fit on all pixels.
- [ ] **`calibration_std`** is the RBF-interpolated station sigma (clipped at 0
  where the cubic RBF overshoots), not the uncertainty of the fitted surface;
  Venti discards the propagated `plane_std`. Carry the fit covariance, or
  document the layer as "reference sigma only" (*changes the golden*).
- [ ] **GNSS interpolation**: `Rbf(function="cubic", smooth=1)` has no
  effective regularisation in metre units and no polynomial term; consider
  `RBFInterpolator(kernel="thin_plate_spline", degree=1)` and a minimum-station
  guard (*changes the golden*).
- [ ] **Auxiliary 3-D model** is an all-zero placeholder; write it only once the
  decomposition exists, or mark it as a placeholder in the product.
- [ ] **`mask_file`** is accepted but not applied (a warning is logged);
  `run_calibration` takes no external mask yet.
- [ ] **NISAR**: `StaticLayer` filename pattern is Sentinel-1 only.

## Performance

- [ ] Peak memory is about 18 GB per frame. Largest contributors: the float64
  point array and interpolator for all DEM pixels in
  `interpolate_to_dem_surface` (twice), and float64 copies in Venti's unwrap
  correction. `worker_settings` (`n_workers`, `block_shape`) are accepted but
  unused: implement block processing or remove them from the runconfig.

## Product

- [ ] Confirm the default `product_data_access` URL (currently built by analogy
  with the DISP-S1 ASF search URL) and the `reference_document` value
  (currently the documentation site; no JPL document number is known).
- [ ] `iono_files` and `tiles_files` are rejected as unsupported; implement or
  remove from the interface.

## Operations

- [ ] Build the Docker image from the new `docker/conda-lock.txt` and
  `Dockerfile` (no Docker daemon was available when they were changed) and run
  `scripts/run_validation.sh` inside it; rebuild the delivery golden in that
  image.
- [ ] CI: add a lint job (pre-commit) and an image smoke test
  (`cal-disp --help`, `python -c "import netCDF4, cal_disp.workflow"`).
- [ ] Remaining untested paths: `find_nearest_scenes`, `generate_s1_burst_tiles`,
  `generate_event_mask`.
