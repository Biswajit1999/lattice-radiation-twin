# Frozen synthetic ablation plan

Status: **SPECIFIED BEFORE ABLATION EXECUTION**. The first synthetic recovery
failure is known and permanently retained. This plan diagnoses that specification;
it does not change its gates or authorize observational fitting.

## Paired design

Regenerate the same 100 synthetic datasets used by
`run_synthetic_recovery.py`: seeds 731000–731099, 48 equally spaced epochs, two
chips, two pair observations per chip, and the retained truth values. Use the
full-model MAP estimates stored in
`results/core_model/synthetic_recovery.json`. Fit four reduced models to every
dataset, setting exactly one physical term to zero:

1. annealing rate;
2. event coefficient;
3. continuous-background coefficient; and
4. process-noise scale.

The named term is removed from optimization and its prior penalty. Other priors,
bounds, initialization and optimizer settings remain unchanged. These are
synthetic inputs; no observational outcome or holdout pixel is permitted.

## Diagnostics

For each paired fit, retain optimizer status, maximized negative log likelihood,
AIC, BIC, latent-state RMSE and observation RMSE. The observation count is 192;
the full model has nine fitted parameters and each ablation has eight. Summaries
report medians and interquartile ranges of the paired change (ablation minus full),
the fraction with positive BIC change, and the latent-RMSE ratio.

These quantities are descriptive diagnostics. No ablation pass/fail threshold is
introduced after observing the recovery failure. A term with a large positive BIC
change is needed to represent the simulated full-model truth; a small or negative
change suggests weak finite-sample identification. Either result leaves the
synthetic recovery gate failed.

## Provenance and next decision

The output must hash this plan, the ablation script, state-space source, frozen
core protocol and retained recovery result. Any narrower prior, altered state
equation or reparameterization will be written as a new protocol version and
committed before another 100-replicate recovery batch.
