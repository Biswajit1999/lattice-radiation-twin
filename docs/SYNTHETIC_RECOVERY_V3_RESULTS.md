# Core model v3 synthetic recovery result

Status: **PASSED — synthetic computational calibration established**.

The frozen v3 harness was executed after the protocol, sampler and production
script were committed. It contains 100 fixed-truth recovery datasets, 100
separate prior-drawn simulation-based calibration (SBC) datasets and 1,000
prior-predictive draws. Every input is simulated. The complete result is
`results/core_model/synthetic_recovery_v3.json`.

## Frozen gate results

| Check | Frozen requirement | V3 result | Pass |
|---|---:|---:|:---:|
| Fixed-truth usable chains | at least 95/100 | 99/100 | yes |
| SBC usable chains | at least 95/100 | 99/100 | yes |
| Overall 95% posterior interval coverage | at least 0.90 | 0.9688 | yes |
| Median absolute standardized ensemble bias | below 0.35 | 0.2694 | yes |
| Latent-state RMSE | below 0.0100 | 0.00797 | yes |
| Posterior-predictive 90% coverage | 0.85–0.95 | 0.9444 | yes |
| Posterior-predictive 95% coverage | 0.90–0.99 | 0.9768 | yes |
| Prior-predictive values outside [-0.25, 0.75] | at most 1% | 0.0052% | yes |
| Canonical prior-drawn SBC | every scalar check passes | 8/8 parameters | yes |

The exact-posterior sampler corrects the v2 failure without changing the model,
prior, truth or thresholds. The process-scale SBC chi-square uniformity p-value
is 0.9114 with edge fraction 0.08, compared with p = 6.40e-8 in v2. The other
seven canonical SBC p-values range from 0.3345 to 0.8677, and all edge fractions
are at most 0.15.

One fixed-truth dataset and one SBC dataset fail the per-dataset ESS requirement
and are retained. Across the full populations, maximum rank-normalized R-hat is
1.0491 for fixed truth and 1.0297 for SBC. Minimum bulk ESS is 40.6 and 77.4,
respectively; these minima occur in the two unusable datasets. The frozen
population requirement is at least 95 usable datasets, so both 99/100 counts
pass.

## Recovery detail and limits

Parameterwise nominal 95% interval coverage ranges from 0.93 to 0.99. The
fixed-truth process-scale posterior mean is 0.00713 for truth 0.008, with 0.98
interval coverage. Fixed-truth rank histograms remain nonuniform for drift and
process scale. These repeated-dataset, single-truth ranks are retained as
diagnostics; the preregistered calibration gate is the separate prior-drawn SBC
population, for which every parameter passes.

This PASS establishes synthetic computational calibration for the v2 state
equation under the v3 inference method. It does not establish detector physics,
radiation causation, cross-mission transfer or forecast skill. No observational
posterior was fitted. The physical-inference gate remains closed, and all six
August 2025 temporal-holdout pixel arrays remain unopened. Exact-zero ablations
under v3 inference, lag/proxy sensitivity and whole-epoch forward validation
must be specified and completed before physical interpretation.

All five recorded provenance hashes match the executed v3 script, v2 model,
posterior sampler, frozen protocol and retained v2 result.

![V3 exact-posterior recovery and interval calibration](../paper/figures/synthetic_recovery_v3.png)
