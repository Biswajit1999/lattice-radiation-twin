# Core model v2 synthetic recovery result

Status: **FAILED — process-scale calibration remains invalid**.

The reference-anchored v2 model was executed only after its protocol and
implementation were separately committed. The production run contains 100
fixed-truth recovery datasets, 100 separate prior-drawn SBC datasets, and 1,000
prior-predictive draws. All inputs are simulated. The complete output is
`results/core_model/synthetic_recovery_v2.json`.

## Frozen gate results

| Check | Frozen requirement | V2 result | Pass |
|---|---:|---:|:---:|
| Fixed-truth optimizer success | at least 95/100 | 100/100 | yes |
| SBC optimizer success | at least 95/100 | 100/100 | yes |
| Overall 95% Laplace interval coverage | at least 0.90 | 0.9075 | yes |
| Median standardized bias | below 0.35 | 0.3075 | yes |
| Latent-state RMSE | below 0.0100 | 0.00808 | yes |
| Posterior-predictive 90% coverage | 0.85–0.95 | 0.9350 | yes |
| Posterior-predictive 95% coverage | 0.90–0.99 | 0.9720 | yes |
| Prior-predictive values outside [-0.25, 0.75] | at most 1% | 0/192,000 | yes |
| Canonical prior-drawn SBC | every scalar check passes | process scale fails | **no** |

V2 resolves the two largest v1 failures. Anchoring the first observation pair
reduces latent-state RMSE from 0.01721 to 0.00808. The log-scale priors reduce the
out-of-range prior-predictive fraction from 34.50% to zero in the frozen draw.

## Remaining calibration failure

Seven of eight canonical SBC rank checks pass. Process scale fails with
chi-square uniformity p = 6.40e-8 and edge fraction 0.16. Its ten-bin counts are
3, 6, 2, 3, 11, 13, 10, 8, 18 and 26, placing excessive mass in high ranks. This
means the prior-drawn truth is too often above the Laplace posterior draws. The
fixed-truth estimates show the same direction: mean process scale is 0.00635 for
truth 0.008, with standardized ensemble bias -1.121 and only 0.82 nominal 95%
interval coverage.

The issue is now narrower than v1. Event response, background response,
annealing, drift, chip deviation, pair contrast and observation scale all pass
the canonical SBC rule. Fixed-truth parameterwise coverage is 0.99 for event,
0.95 for background, 0.89 for annealing and drift, 0.82 for chip deviation, 0.96
for pair contrast, 0.82 for process scale and 0.94 for observation scale. The
protocol uses aggregate coverage, which passes; the poor process-scale coverage
still agrees with the SBC failure and must not be ignored.

## Interpretation and next method change

V2 remains simulated method evidence, not a detector result. The reference
anchor and prior revision are retained, but the MAP-centered Gaussian Laplace
approximation is inadequate for the skewed variance-component posterior. The
next version should change the inference approximation for process scale and
validate it with prior-drawn SBC before another fixed-truth claim. Changing the
truth, weakening the SBC threshold, or fitting observations would not address
this failure.

No observational posterior was fitted. The physical-inference gate and all six
August 2025 temporal-holdout pixel arrays remain closed.

![V2 fixed-truth recovery and Laplace coverage](../paper/figures/synthetic_recovery_v2.png)
