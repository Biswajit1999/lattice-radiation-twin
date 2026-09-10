# Synthetic ablation results

Status: **DIAGNOSTIC COMPLETE — recovery gate remains failed**.

The four exact-zero ablations specified in `CORE_ABLATION_PLAN.md` were fitted to
the same 100 seeded, 48-epoch synthetic datasets as the retained recovery batch.
All 400 reduced-model optimizations succeeded. The complete paired output is in
`results/core_model/synthetic_ablations.json`.

## Paired comparisons

Values are medians, with interquartile ranges in parentheses. Changes are
ablation minus the retained full-model fit, so a positive delta BIC indicates
loss of support after removing the term.

| Removed term | Delta BIC | Positive delta BIC | Latent-RMSE ratio | Reduced latent RMSE |
|---|---:|---:|---:|---:|
| Annealing | 12.77 (8.71–19.33) | 98% | 1.046 (0.770–1.415) | 0.01354 |
| Event response | 68.86 (57.90–75.65) | 100% | 1.281 (1.064–1.471) | 0.01522 |
| Background response | 28.26 (22.14–33.73) | 100% | 1.099 (0.993–1.223) | 0.01351 |
| Process noise | 9.80 (0.29–19.25) | 75% | 1.335 (1.065–1.685) | 0.01750 |

Event response is the clearest representational term under the simulated
full-model truth. Removing it gives the largest likelihood and BIC loss and
raises median latent RMSE by 28.1%. Background response is also consistently
supported, with positive paired BIC change in every dataset.

Annealing removal usually loses BIC support, but its latent-RMSE ratio has a wide
interquartile range crossing one. This weak and variable recovery effect is
consistent with the annealing rank nonuniformity in the main synthetic batch.
The data can detect that a decay term improves representation more reliably than
they can recover its contribution to each latent trajectory.

Process-noise removal has the weakest and most variable BIC evidence: one quarter
of paired datasets favour the reduced deterministic transition after the
dimension penalty. Yet its median latent-RMSE ratio is the largest. Process noise
helps reconstruct the simulated stochastic state, while its scale remains poorly
calibrated and only variably selected in a 48-epoch sample.

## Decision boundary

These results diagnose a simulation whose truth contains all four terms; they are
not observational evidence that any term describes a real detector. They do not
repair the broad prior predictive distribution, the failed latent-RMSE gate or
the annealing/process-scale SBC failures. The first specification remains failed,
no observational model has been fitted, and the physical-inference and temporal-
holdout gates remain closed.

The diagnostics support retaining event and background terms in a revised
synthetic specification. Annealing and process noise require a versioned
identifiability change rather than deletion based on this result alone. Any new
priors or parameterization must be frozen before another recovery batch.

![Paired synthetic ablation diagnostics](../paper/figures/synthetic_ablations.png)
