# Performance

Full-frame runtime and peak memory of `cal-disp run` on the F08882 golden pair
(7733 × 9464 pixels, factor-6 fit grid), on aurora (32 cores,
`NUMPY_MADVISE_HUGEPAGE=0`). Peak memory is the `Maximum memory usage` line
the run logs; `scripts/check_env_budget.py --peak-memory-log` checks it against
`peak_memory_gb` in `budget.yaml` (7 GB; the plan's target is 4 GB, Venti T47).

| Configuration | Venti | fit | whole run | peak |
|---|---|---|---|---|
| gamma 0.3 golden, direct `estimate_calibration_surface` | `1150c52` | | | 5.38 GB |
| gamma 0.3 golden through `calibrate_pair` (first wiring) | `1150c52` | | | 7.46 GB |
| gamma 0.3 golden through `calibrate_pair` | `f7da024` | | | 5.84 GB |
| gamma 0.3 golden through `calibrate_pair` | `2b2678b` | | | 6.02 GB |
| v0.5: loclin 50 km, two passes, coh⁸ + robust, σ_CAL (first wiring) | `f7da024` | 42 s | 96 s | 8.81 GB |
| v0.5, same | `2b2678b` | 22 s | 55 s | 7.27 GB |

What moved the numbers (Venti commits on the `mgovorcin/venti-dev` stack):

- `f7da024`: `calibrate_pair` without the extra full-frame arrays: no
  defensive copy of the displacement, one shared read-only zero layer for
  unused components, the working field built in place, the GNSS field kept
  in float32, the component sum computed once (−1.6 GB on the gamma route).
- `2b2678b`: the loclin full-frame maps (surface, coverage, σ_fit, n_eff,
  σ_CAL) kept in the displacement's float32 instead of float64 (−1.5 GB,
  and half the runtime).

The v0.5 configuration is 0.27 GB above the 7 GB budget, which is defined on
the gamma golden run. The remaining full-frame float32 copies (displacement,
mask, GNSS field and its sigma, the components) are the target of Venti T47
(memory and runtime toward a small EC2 instance).
