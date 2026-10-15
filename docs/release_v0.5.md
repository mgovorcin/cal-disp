# Releasing v0.5 (Venti plan T49–T51)

The steps that turn the validated v0.5 algorithm into the default. Each one
changes what a run produces, so they happen together, after the VnV sign-off
(T50.3), in this order.

## 0. Before you start
- [x] VnV report signed off (owner 2026-10-15; OPERA CalVal pending) (disp2vlm_validation `docs/vnv/v0.5-calval-report.md`).
- [x] Decision on `calibration_std` NaN where the fit coverage is low (2026-10-14: extrapolated σ, `uncertainty.extrapolate_sigma`)
      (CHANGELOG, "Open before the release").
- [x] Frame-key fix merged (#16), so the frame table reaches runs.

## 1. Flip the defaults (T49.1)
- [x] `cp configs/algorithm_parameters_v05.yaml configs/algorithm_parameters.yaml`
      (keep the field documentation; only the values change).
- [x] Model defaults in `src/cal_disp/config/_algorithm.py` follow the file.
- [x] `scripts/build_golden_output.sh` writes the v0.5 parameters and adds the
      static ancillaries production uses:
      `algorithm_parameters_overrides_json` (Venti
      `load_frame_table().write(path, materialize=True)`), `defo_area_db_json`
      and `event_db_json` (Venti `data/`).
- [x] `tests/test_release_configs.py`: the gamma test reads its own copy of the
      0.3 parameters (the build script now writes v0.5).

## 2. Image (T49.2)
- [x] `docker build --network=host -t cal-disp:0.5.0-rc -f docker/Dockerfile .`
      (docker-build skill); the env budget check (`budget.yaml`) passes.

## 3. Golden (T49.3)
- [x] Regenerate inside the image: `scripts/build_golden_output.sh`.
- [x] `scripts/run_validation.sh --golden-dir test_golden` passes in the image.
- [x] New `MANIFEST.sha256`; archive the 0.3 golden under `test_golden/archive/`.
- [x] Gamma reproduction: a run with `configs/algorithm_parameters_gamma.yaml`
      matches the archived 0.3 golden.

## 4. Changelog (T49.4)
- [x] Re-measure the golden-pair table in the image and update `CHANGELOG.md`.
- [x] Date the `[0.5.0]` entry.

## 5. Release (T51)
- [x] Tag `v0.5.0` on the merge commit (`438b84e`, 2026-10-15); image `cal-disp:0.5.0` built from the tag and validated against the golden.
- [ ] Push the image to the registry (owner).
