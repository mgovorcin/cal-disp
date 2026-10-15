# Golden dataset, v0.5

Frame F08882 (Houston), pair 2022-01-11 → 2022-07-22. The data live outside
git (`test_golden/`, 4.9 GB); `MANIFEST_0.5.0.sha256` pins every config,
input, static-ancillary and golden-output file
(`cd test_golden && sha256sum -c ../docs/golden/MANIFEST_0.5.0.sha256`).

| Item | Value |
|---|---|
| Configuration | v0.5 (`configs/algorithm_parameters_v05.yaml`, the defaults), with the Venti frame table (0.6-draft: regions + stable-pixel fit mask for F08882) and the area (1.1-draft) and event (1.0-draft) databases in `input_data/static_ancillary/` |
| Built | 2026-10-15, inside `cal-disp:0.5.0-rc` (`sha256:d3f0fafcabaf6d2d0898e6c5f4402a0423b42f4097daeca4dc88d95493fadc18`, version `0.5.0rc1`), with `scripts/build_golden_output.sh --skip-download` |
| Golden product | `OPERA_L4_DISP-CAL-S1_IW_F08882_VV_20220111T002651Z_20220722T002657Z_v1.0_20261015T164653Z.nc` |
| Validation in the image | passed at 1e-6, peak 5.76 GB (`test_golden/validation_0.5.0.log`) |
| Change vs 0.3 | `calibration` median \|Δ\| 12.2 mm (max 113 mm); `calibration_std` NaN exactly where `calibration` is (CHANGELOG) |
| Previous golden (gamma 0.3, 2026-10-06) | archived in `test_golden/archive/golden_v0.3_20261006/`; manifest `MANIFEST_0.3.0.sha256`; reproduced by `configs/algorithm_parameters_gamma.yaml` (data layers at 1e-6) |

Rebuilding: see the header of `scripts/build_golden_output.sh`. A change to
the configuration or to anything that moves the product is a new golden: rebuild
in the image, validate, regenerate this manifest.
