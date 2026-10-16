# Golden dataset, v0.5.1

Frame F08882 (Houston), pair 2022-01-11 → 2022-07-22. The data live outside
git (`test_golden/`, 4.9 GB); `MANIFEST_0.5.1.sha256` pins every config,
input, static-ancillary and golden-output file
(`cd test_golden && sha256sum -c ../docs/golden/MANIFEST_0.5.1.sha256`).

| Item | Value |
|---|---|
| Configuration | v0.5 (`configs/algorithm_parameters_v05.yaml`, the defaults), with the Venti frame table (0.6-draft: regions + stable-pixel fit mask for F08882) and the area (1.1-draft) and event (1.0-draft) databases in `input_data/static_ancillary/` |
| Built | 2026-10-16, inside `cal-disp:0.5.1-rc` (`sha256:a7d61bc66b1b3d612d43a52cd753eac62d546237eb4fcaaffe44daa08052ae2b`, version `0.5.1rc1`), with `scripts/build_golden_output.sh --skip-download` |
| Golden product | `OPERA_L4_DISP-CAL-S1_IW_F08882_VV_20220111T002651Z_20220722T002657Z_v1.0_20261016T174302Z.nc` |
| Change vs 0.5.0 | data layers bit-identical; `/metadata` adds `algorithm_schema_version`, `frame_parameters_version`, `components_applied` |
| Validation in the image | passed at 1e-6, peak 5.76 GB (`test_golden/validation_0.5.1.log`) |
| Change vs 0.3 | `calibration` median \|Δ\| 12.2 mm (max 113 mm); `calibration_std` NaN exactly where `calibration` is (CHANGELOG) |
| Previous golden (v0.5.0, 2026-10-15) | archived in `test_golden/archive/golden_v0.5.0_20261015/`; manifest `MANIFEST_0.5.0.sha256` |
| Gamma 0.3 golden (2026-10-06) | archived in `test_golden/archive/golden_v0.3_20261006/`; manifest `MANIFEST_0.3.0.sha256`; reproduced by `configs/algorithm_parameters_gamma.yaml` (data layers at 1e-6) |

Rebuilding: see the header of `scripts/build_golden_output.sh`. A change to
the configuration or to anything that moves the product is a new golden: rebuild
in the image, validate, regenerate this manifest.
