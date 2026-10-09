# Performance

Full-frame runtime and peak memory of `cal-disp run` on the F08882 golden pair
(7733 × 9464 pixels, factor-6 fit grid), on aurora (32 cores,
`NUMPY_MADVISE_HUGEPAGE=0`). Peak memory is the `Maximum memory usage` line
the run logs; `scripts/check_env_budget.py --peak-memory-log` checks it against
`peak_memory_gb` in `budget.yaml` (4.5 GB since 2026-10-09; the plan's target is
4 GB, Venti T47).

| Configuration | Venti | fit | whole run | peak |
|---|---|---|---|---|
| gamma 0.3 golden, direct `estimate_calibration_surface` | `1150c52` | | | 5.38 GB |
| gamma 0.3 golden through `calibrate_pair` (first wiring) | `1150c52` | | | 7.46 GB |
| gamma 0.3 golden through `calibrate_pair` | `f7da024` | | | 5.84 GB |
| gamma 0.3 golden through `calibrate_pair` | `2b2678b` | | | 6.02 GB |
| v0.5: loclin 50 km, two passes, coh⁸ + robust, σ_CAL (first wiring) | `f7da024` | 42 s | 96 s | 8.81 GB |
| v0.5, same | `2b2678b` | 22 s | 55 s | 7.27 GB |
| gamma 0.3 golden, T47 (cal-disp memory changes + Venti) | `07d149e` | | | 3.6–4.0 GB |
| v0.5, T47 | `07d149e` | | 48–83 s | 4.0–4.1 GB |

What moved the numbers (Venti commits on the `mgovorcin/venti-dev` stack):

- `f7da024`: `calibrate_pair` without the extra full-frame arrays: no
  defensive copy of the displacement, one shared read-only zero layer for
  unused components, the working field built in place, the GNSS field kept
  in float32, the component sum computed once (−1.6 GB on the gamma route).
- `2b2678b`: the loclin full-frame maps (surface, coverage, σ_fit, n_eff,
  σ_CAL) kept in the displacement's float32 instead of float64 (−1.5 GB,
  and half the runtime).

- T47 (2026-10-09), profiled with memray on the golden pair; every change
  leaves the product bit-identical (`cal-disp validate --rtol 0 --atol 0`):
  - cal-disp: the LOS bands are freed once the GNSS field is projected
    (−0.9 GB); masks and coherence are read in row blocks like the
    displacement, so xarray keeps no decoded copy in the dataset (−0.6 GB);
    the reference pixel uses the coherence already loaded; the SET layer is
    not copied a second time (−0.3 GB);
  - Venti `4ac24f7`: `calibrate_pair(diagnostic_maps=False)` skips the
    full-resolution coverage / σ_fit / n_eff maps the product never writes,
    and `cal_reference_offset` (one constant) is a read-only view (−0.9 GB);
  - Venti `07d149e`: the medians the run logs were taken on full-frame maps,
    and `np.nanmedian` copies its input (−0.3 GB at the peak); the zero
    component is a view.

v0.5 went from 7.27 to about 4.1 GB and gamma from 6.0 to about 3.8 GB.
Runtimes on aurora vary with the machine's load (48 s idle, up to 83 s at a
load average of 35). What is left at the peak is the working set itself:
displacement, valid mask, GNSS field and σ, coherence, the working field,
the surface and σ_CAL (about 0.3 GB each).
