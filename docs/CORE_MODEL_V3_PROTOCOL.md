# Frozen core model v3 inference protocol

Status: **SPECIFIED BEFORE V3 IMPLEMENTATION OR SAMPLING**. V2 passed its prior,
latent-state, aggregate interval, bias and predictive gates but failed canonical
SBC for process scale. No observational latent-state fit or temporal-holdout pixel
access has occurred.

## Scope of the revision

V3 keeps the complete v2 state equation, reference-pair observation equation,
parameterization, priors, synthetic truth, covariate generator and prior gate.
It changes only posterior inference. No prior is adjusted after the v2 result.

The v2 process-scale posterior is bounded and skewed in physical coordinates.
Its MAP-centered Laplace draws underestimate process scale: fixed-truth mean
0.00635 versus truth 0.008, 0.82 interval coverage, and canonical SBC
p=6.40e-8. A Gaussian curvature approximation is therefore no longer accepted
for posterior validation.

## Exact-likelihood posterior sampling

The exact Kalman marginal likelihood remains unchanged. In the eight-dimensional
transformed parameter vector, V3 will use a Laplace-preconditioned random-walk
Metropolis sampler. The Laplace covariance supplies proposal geometry only; all
accept/reject decisions use the exact Kalman likelihood and v2 prior, so the
Laplace approximation does not define the retained posterior.

For every fixed-truth and prior-drawn SBC dataset, run two independent chains.
Each chain starts near the MAP, uses the finite-difference Laplace covariance,
adapts only a scalar proposal multiplier during 750 burn-in iterations toward
acceptance 0.234, then freezes the proposal and retains 2,000 iterations without
thinning. The pooled posterior therefore contains 4,000 draws. A non-finite MAP,
proposal covariance or retained posterior is a hard sampling failure.

The implementation must be verified against a correlated Gaussian target,
deterministic repeatability tests and deliberately separated chains. A benchmark
on this host measured 2,000 48-epoch Kalman likelihood evaluations in 11.49
seconds (5.75 ms each); the long production run will be checkpointed before
execution.

Full-vector elliptical slice sampling was considered first because the transformed
prior is Gaussian. A disclosed two-chain smoke run with 100 burn-in and 200 draws
gave process-scale R-hat 1.98 and bulk ESS 2.8, so it was rejected before any v3
production result. A preconditioned Metropolis smoke run with 500 burn-in and
1,000 draws gave sampling acceptance 0.195/0.238, maximum R-hat 1.068 and minimum
bulk ESS 52. The frozen production budget doubles retained draws and increases
burn-in; its convergence gates remain decisive.

## Convergence and posterior summaries

Compute split rank-normalized R-hat and bulk effective sample size for all eight
transformed parameters. A dataset has usable chains only when every R-hat is at
most 1.05 and every bulk ESS is at least 100. At least 95 of 100 fixed-truth
datasets and 95 of 100 prior-drawn SBC datasets must have usable chains.

Parameter intervals and SBC ranks use the pooled 4,000 draws. For latent-state
and posterior-predictive summaries, select 64 evenly spaced pooled draws. Run the
exact smoother for each, average conditional state means for the posterior state
mean, and combine conditional state covariance with between-draw mean variance.
Predictive intervals also combine observation-scale draws and pair contrast.

## Frozen seeds

- Fixed-truth data: 1,831,000–1,831,099.
- Fixed-truth ESS chains: deterministic derivations of 2,091,000–2,091,099.
- Prior-drawn SBC truth/data: 2,331,000–2,331,099.
- Prior-drawn SBC chains: deterministic derivations of 2,591,000–2,591,099.
- Prior-predictive gate: 1,541,902.

## Gates

The v2 numerical gates remain unchanged:

1. overall 95% posterior interval coverage at least 0.90;
2. median absolute standardized ensemble bias below 0.35 for drift, event,
   background and annealing;
3. latent-state RMSE below 0.0100;
4. posterior-predictive 90% coverage within [0.85, 0.95] and 95% coverage within
   [0.90, 0.99];
5. prior-predictive out-of-range fraction at most 1%;
6. every canonical SBC ten-bin chi-square p-value at least 0.01 and edge fraction
   at most 0.20; and
7. the fixed-truth and SBC chain-usability counts each at least 95 of 100.

V3 passes only if every gate passes. A failure is retained without changing the
thresholds. An ESS pass establishes synthetic computational calibration only; it
does not establish detector physics or authorize opening the temporal holdout.

## Downstream boundary

Observational fitting remains prohibited until v3 synthetic recovery and
canonical SBC pass. Even then, exact-zero ablations, lag/proxy sensitivity and
whole-epoch forward validation must be specified and completed before physical
interpretation.
