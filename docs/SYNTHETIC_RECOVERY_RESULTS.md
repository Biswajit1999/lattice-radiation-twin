# Synthetic recovery result

Status: **FAILED — observational fitting remains prohibited**.

The frozen 100-replicate experiment in `CORE_MODEL_PROTOCOL.md` was executed
against software commit `bdc0ca1ae4ba9cc67c7253ed701471fe6c3c742b`. All
replicates used 48 synthetic epochs and known parameters. The complete
machine-readable output, including every replicate, interval and SBC rank, is
`results/core_model/synthetic_recovery.json`.

## Gate results

| Check | Frozen requirement | Result | Pass |
|---|---:|---:|:---:|
| Optimizer success | at least 95/100 | 100/100 | yes |
| Overall 95% Laplace interval coverage | at least 0.90 | 0.9256 | yes |
| Median absolute standardized ensemble bias | below 0.35 | 0.2808 | yes |
| Latent-state RMSE | below 0.0100 | 0.01721 | **no** |
| Posterior-predictive 90% coverage | 0.85–0.95 | 0.9380 | yes |
| Posterior-predictive 95% coverage | 0.90–0.99 | 0.9743 | yes |
| Prior-predictive values outside [-0.25, 0.75] | at most 1% | 34.50% | **no** |
| Fixed-truth rank calibration | every scalar check passes | annealing and process scale fail | **no** |

The prior predictive 1% minimum-extrema quantile was -3.4103 and the 99%
maximum-extrema quantile was 3.6863. These ranges are incompatible with the
preregistered trail-fraction plausibility interval. The prior specification is
therefore too broad for this observable.

The latent-state RMSE was 0.01721 against a threshold of half the simulated
observation scale, 0.0100. Successful optimization and acceptable aggregate
predictive coverage do not establish recovery of the hidden trajectory.

Annealing ranks failed the preregistered uniformity diagnostic with
chi-square p = 4.24e-9 and an edge fraction of 0.22. Process-scale ranks failed
with p = 3.02e-6 and an edge fraction of 0.16. Their nonuniform ranks indicate
calibration or identifiability problems that the pooled interval-coverage number
does not reveal. Individual 95% coverage was 0.89 for annealing and background,
0.90 for chip deviation, 0.94 for drift, 0.96 for event response, 0.93 for
observation scale, 0.94 and 0.96 for the two pair offsets, and 0.92 for process
scale. Because the truth was fixed across all 100 datasets, these ranks are a
repeated-sampling calibration diagnostic rather than canonical SBC, which draws
truth from the prior for every replicate. The v2 protocol corrects that design.

## Interpretation boundary

This is simulated evidence about the estimator. It is not detector evidence and
does not support a radiation-dose interpretation. The recovery thresholds are
unchanged after observing the result. No observational posterior was fitted, the
physical-inference gate remains closed, and the six August 2025 HST holdout pixel
arrays remain sealed.

The frozen annealing, event, background and process-noise ablations are now
reported in `CORE_ABLATION_RESULTS.md`. Any narrower prior or reparameterization
will be a new version committed before another recovery batch. This failed
specification and its complete output remain part of the permanent evidence trail.

![Synthetic parameter recovery and interval coverage](../paper/figures/synthetic_recovery.png)
