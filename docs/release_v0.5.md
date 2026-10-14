# Releasing v0.5 (Venti plan T49–T51)

The steps that turn the validated v0.5 algorithm into the default. Each one
changes what a run produces, so they happen together, after the VnV sign-off
(T50.3), in this order.

## 0. Before you start
- [ ] VnV report signed off (disp2vlm_validation `docs/vnv/v0.5-calval-report.md`).
- [ ] Decision on `calibration_std` NaN where the fit coverage is low
      (CHANGELOG, "Open before the release").
- [ ] Frame-key fix merged (#16), so the frame table reaches runs.

## 1. Flip the defaults (T49.1)
- [ ] `cp configs/algorithm_parameters_v05.yaml configs/algorithm_parameters.yaml`
      (keep the field documentation; only the values change).
- [ ] Model defaults in `src/cal_disp/config/_algorithm.py` follow the file.
- [ ] `scripts/build_golden_output.sh` writes the v0.5 parameters and adds the
      static ancillaries production uses:
      `algorithm_parameters_overrides_json` (Venti
      `load_frame_table().write(path, materialize=True)`), `defo_area_db_json`
      and `event_db_json` (Venti `data/`).
- [ ] `tests/test_release_configs.py`: the gamma test reads its own copy of the
      0.3 parameters (the build script now writes v0.5).

## 2. Image (T49.2)
- [ ] `docker build --network=host -t cal-disp:0.5.0-rc -f docker/Dockerfile .`
      (docker-build skill); the env budget check (`budget.yaml`) passes.

## 3. Golden (T49.3)
- [ ] Regenerate inside the image: `scripts/build_golden_output.sh`.
- [ ] `scripts/run_validation.sh --golden-dir test_golden` passes in the image.
- [ ] New `MANIFEST.sha256`; archive the 0.3 golden under `test_golden/archive/`.
- [ ] Gamma reproduction: a run with `configs/algorithm_parameters_gamma.yaml`
      matches the archived 0.3 golden.

## 4. Changelog (T49.4)
- [ ] Re-measure the golden-pair table in the image and update `CHANGELOG.md`.
- [ ] Date the `[0.5.0]` entry.

## 5. Release (T51)
- [ ] Tag `v0.5.0` on the merge commit; push the image.
