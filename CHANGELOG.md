# Changelog

Product-affecting entries are marked **[product]**. Numbers on the golden pair
(F08882, 2022-01-11 → 2022-07-22) compare against the 0.3 golden.

## [0.5.0] — unreleased (draft, Venti plan T49)

v0.5 replaces the gamma windowed-plane surface with Venti's local-linear
surface and adds remove-restore, the 50 km GNSS buffer, per-frame settings and
σ_CAL. Validated on 10 benchmark frames (T46: all PASS under decisions 0002 and
0003; disp2vlm_validation `docs/vnv/v0.5-calval-report.md`). **The defaults are
not switched yet**: T49.1 flips `configs/algorithm_parameters.yaml` to
`configs/algorithm_parameters_v05.yaml` after VnV sign-off (T50).

### Added
- `configs/algorithm_parameters_v05.yaml` (the T46 set) and
  `configs/algorithm_parameters_gamma.yaml` (decision 0001, reproduces the 0.3
  golden); `tests/test_release_configs.py` keeps both in step.
- **[product]** v0.5 route through Venti `calibrate_pair` with schema-v2 options:
  `surface` (loclin, 50 km half-response cutoff, robust two-pass tie), `weights`
  (coherence⁸ × robust), `tropo` (per-frame mode), `uncertainty` (σ_CAL),
  `gnss`, `unwrap` (#6).
- **[product]** GNSS field from the UNR grid with nodes up to 50 km outside the
  frame (R-G2, R-G5) (#10).
- **[product]** Remove-restore from the Venti area and event databases
  (`defo_area_db_json`, `event_db_json`): deforming areas and event footprints
  are left out of the fit and restored; GNSS nodes inside them are excluded and
  re-interpolated (#11).
- **[product]** Per-frame stable-pixel fit mask (`surface.fit_mask`, packaged
  with Venti; F08882 only) (#15).
- **[product]** `/metadata/gnss_provenance` record on the v0.5 route (#13).
- Runconfig `mask_file` is applied (#4).
- Unwrap-error correction runs on the loclin route when enabled; off by
  default (owner 2026-10-09) (#7).
- Optional non-secular σ term; the `calibration_std` text states what σ_CAL
  covers (#9).

### Changed
- Venti pinned to the mgovorcin/venti-dev v0.5 stack (#3, #14, #15).
- Core install drops `opera-utils[disp]`; dependency and memory budget in
  `budget.yaml` (#5); peak memory v0.5 7.27 → 4.1 GB, gamma 6.0 → 3.8 GB (#8).
- UNR downloads go through geepers' verified downloader (#14).
- CI runs pre-commit on pull requests (#12).

### Fixed
- Frame-table overrides: Venti's zero-padded frame keys (`"08882"`) are found;
  before, no frame-table setting reached a run (#16).

### Golden pair: v0.5 vs 0.3 (measured 2026-10-14 outside Docker; T49.3 re-measures in the image)

v0.5 parameters + Venti frame table + area/event databases, as production will
run them:

| layer | median \|Δ\| | p99 \|Δ\| | max \|Δ\| | NaN share |
|---|---|---|---|---|
| `calibration` | 12.2 mm | 56.3 mm | 112.6 mm | 33.9% (water; unchanged) |
| `calibration_std` | 0.46 mm | 2.9 mm | 3.8 mm | 0% → 63.8% (see open issue) |
| `auxiliary/*` | 0 | 0 | 0 | unchanged |

### Open before the release
- **`calibration_std` is NaN where the fit coverage is low.** Venti
  `fit_sigma` returns NaN below a kernel coverage of 1e-3, and the coherence⁸
  weights leave little coverage on decorrelated land. On T46 products σ_CAL is
  NaN on 5–18% of land (Central Valley, Montana), 42–65% (Houston, New York),
  ~60% (Hawaii) and 85–89% (Puerto Rico). The gate and TS-E4 use station pixels
  (coherent), so they did not see it. Needs a decision: an extrapolated,
  inflated σ there, or NaN documented as "no estimate".
- Per-frame `uncertainty.k_grid` (TS-G1) and tropo modes reach runs only
  through the frame table; the T46 runs did not pass it (k_grid 3.9 everywhere).
- Frame-table `frame.plate` is recorded but not used by any calibration step.

## [0.3.0] — gamma (golden 2026-10-06, not tagged)

Decision 0001 (`docs/decisions/0001-gamma-config.md`): 600 km window, tropo off,
unwrap correction off; golden rebuilt with `scripts/build_golden_output.sh`.
`configs/algorithm_parameters.yaml` and the model defaults still carry the
pre-decision values (30 km window, tropo on); runs that follow the README
therefore do not reproduce gamma. Use `configs/algorithm_parameters_gamma.yaml`.
