# Golden dataset, v0.5.7

Frame F08882 (Houston), pair 2022-01-11 → 2022-07-22. The data live outside
git (`test_golden/`, 4.9 GB); `MANIFEST_0.5.7.sha256` pins every config,
input, static-ancillary and golden-output file
(`cd test_golden && sha256sum -c ../docs/golden/MANIFEST_0.5.7.sha256`).

| Item | Value |
|---|---|
| Configuration | v0.5 (`configs/algorithm_parameters_v05.yaml`, the defaults), with the Venti frame table (0.9-draft; for F08882: regions + stable-pixel fit mask) and the area (1.1-draft) and event (1.0-draft) databases in `input_data/static_ancillary/` |
| Built | 2026-10-28, inside `cal-disp:0.5.7-rc` (`sha256:7bc0eb081018bfc41e9079fd7298e84a2e6e44b23d1047e6bd57bbf3131032ed`, version `0.5.7rc1`), with `scripts/build_golden_output.sh --skip-download` |
| Golden product | `OPERA_L4_DISP-CAL-S1_IW_F08882_VV_20220111T002651Z_20220722T002657Z_v1.0_20261028T072840Z.nc` |
| Change vs 0.5.5 | data layers (incl. `/plate_motion`, `/auxiliary`) bit-identical; `/metadata/frame_parameters_version` `0.8-draft` → `0.9-draft` (Venti `9537925`, coastal frame entries); runconfig gains the empty `fit_mask_file` field (0.5.6) |
| Validation in the image | passed at 1e-6 (`test_golden/validation_0.5.7.log`) |
| Change vs 0.3 | `calibration` median \|Δ\| 12.2 mm (max 113 mm); `calibration_std` NaN exactly where `calibration` is (CHANGELOG) |
| Previous golden (v0.5.5/0.5.6, 2026-10-22) | archived in `test_golden/archive/golden_v0.5.5_20261022/`; manifest `MANIFEST_0.5.5.sha256` |
| v0.5.4 golden (2026-10-22) | archived in `test_golden/archive/golden_v0.5.4_20261022/`; manifest `MANIFEST_0.5.4.sha256` |
| v0.5.2/0.5.3 golden (2026-10-20) | archived in `test_golden/archive/golden_v0.5.2_20261020/`; manifest `MANIFEST_0.5.2.sha256` |
| v0.5.1 golden (2026-10-16) | archived in `test_golden/archive/golden_v0.5.1_20261016/`; manifest `MANIFEST_0.5.1.sha256` |
| v0.5.0 golden (2026-10-15) | archived in `test_golden/archive/golden_v0.5.0_20261015/`; manifest `MANIFEST_0.5.0.sha256` |
| Gamma 0.3 golden (2026-10-06) | archived in `test_golden/archive/golden_v0.3_20261006/`; manifest `MANIFEST_0.3.0.sha256`; reproduced by `configs/algorithm_parameters_gamma.yaml` (data layers at 1e-6) |

Rebuilding: see the header of `scripts/build_golden_output.sh`. A change to
the configuration or to anything that moves the product is a new golden: rebuild
in the image, validate, regenerate this manifest.
