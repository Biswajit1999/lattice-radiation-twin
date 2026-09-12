# Frozen historical state-space validation protocol

Status: **SPECIFIED BEFORE OBSERVATIONAL STATE-SPACE FITTING**. The v3 synthetic
recovery and canonical SBC gate has passed. No observational state-space
posterior has been fitted, and the six August 2025 temporal-holdout pixel arrays
remain unopened.

## Purpose and evidence boundary

This experiment asks whether the synthetically calibrated state-space structure
improves whole-epoch forecasts of the replicated HST trailing summary and whether
its event and background terms survive prespecified ablations and exposure
sensitivities. It is an observational predictive test of proxy inputs. It cannot
identify detector dose, a trap population or a causal radiation response.

The only outcomes are the 32 records in
`results/hst_replication/primary.json` whose role is `replication`: eight epochs,
two ACS/WFC chips and two independent pair indices. Development-pair outcomes,
the 2025 holdout and pixel arrays are prohibited. The environment source is the
frozen monthly table in `results/environment/monthly_exposure.json`.

## Primary inputs

The four pair-by-chip observations at each epoch retain their calibrated mean
parallel-trail fractions. Times are decimal years from the first epoch. Pair
index 2 is the reference observation and pair index 3 receives the single pair
contrast used in v2/v3. The observation equation retains the v3 common residual
scale; a held-out record's bootstrap standard error is added in quadrature only
to its forecast variance because the bootstrap interval excludes shared
calibration uncertainty.

For each transition, use complete UTC environment months after the earlier
epoch's cutoff through the month preceding the forecast epoch. The primary
background covariate is the arithmetic mean of
`response_basis.hst_leo.inverse_f107_gcr_proxy`. The primary event covariate is
the sum of valid `response_basis.hst_leo.sep_x_geomagnetic_activity` values
divided by the number of calendar months in the interval. This denominator
retains missing particle months as missing exposure rather than silently
renormalizing the available values upward. Every transition must have at least
75% valid event months or the primary experiment fails input validation.

Within each fold, center and scale the two transition covariates using training
transitions only. Apply those training values unchanged to the test transition.
Zero variance maps that covariate to zero and is recorded. No outcome, exposure
or scaling information later than the held-out epoch may enter a fit.

## Primary model and posterior forecast

The primary model H0 keeps the v2 state and observation equations, v2 priors and
v3 exact-posterior heavy-tailed independence sampler. It uses two chains, 100
discarded iterations and 2,000 retained draws per chain. Seeds are 2,831,000 and
2,831,001 for the 2015 fold, increasing by 100 for each subsequent fold. A fold
is usable only when every transformed parameter has rank-normalized R-hat at
most 1.05 and bulk ESS at least 100.

Fit expanding histories ending in 2012, 2015, 2018 and 2021, and predict the
complete 2015, 2018, 2021 and 2024 epochs, respectively. Each posterior draw
propagates the last filtered two-chip state through the held-out transition and
then through the observation equation. The predictive distribution includes
state, process, residual observation and held-out bootstrap variances. Retain
posterior predictive means, standard deviations and equal-tail 95% intervals
for all 16 predictions.

Report the same pooled metrics as B0–B5: RMSE, MAE, mean Gaussian negative log
predictive density, 95% interval coverage, mean Gaussian CRPS and out-of-sample
R-squared relative to each training stratum mean. The score calculation must be
shared with the frozen baseline implementation.

## Frozen primary gate

The historical baseline result fixes the numerical requirements. H0 passes the
advanced-model forecast gate only if all four folds are usable, all 16 forecasts
are finite with positive variance, and it simultaneously:

1. has RMSE at most 0.038231325787485455;
2. has mean negative log predictive density below -1.782393718891921; and
3. has empirical 95% interval coverage at least 0.75.

These thresholds are not changed after execution. Failure is retained and
prohibits observational parameter interpretation. A pass supports historical
prediction of this calibrated summary only; it does not establish radiation
causation or authorize the temporal holdout.

## Exact-zero ablations

Repeat the identical four folds with one term removed from both the transition
and prior at a time: event coefficient, background coefficient, annealing rate
and process-noise scale. Each reduced model uses the same data cutoffs, feature
scaling, posterior budget and forecast scores. Compare each with H0 using paired
prediction errors and pooled changes in RMSE, negative log predictive density
and CRPS.

Event or background exposure support requires H0 to have both lower RMSE and
lower mean negative log predictive density than the corresponding exact-zero
model. Annealing and process-noise ablations are structural diagnostics without
a separate physical claim. No ablation may replace H0 after scores are known.

## Lag and proxy sensitivity

The primary event lag is zero complete months. Repeat H0 with event exposure
shifted later by 1, 3 and 6 complete months. Repeat it once with the unshielded
`response_basis.shared_external.sep_log1p` event proxy and once with the monthly
inverse sunspot-number proxy, `1 / max(sunspot_number_mean, 1)`, in place of the
F10.7 background proxy. Each alternative is centered and scaled inside its
training fold and must meet the same 75% coverage rule.

Sensitivity variants are reported in the frozen order and cannot be searched,
combined or selected as a replacement primary model. Exposure attribution is
classified as robust only if H0 passes the primary gate, both event/background
exact-zero comparisons support H0, and every lag/proxy variant retains finite
predictions, at least 0.75 interval coverage and RMSE no more than 10% above H0.
Otherwise the predictive and attribution outcomes are reported separately and
the physical-inference gate stays closed.

## Output, provenance and next boundary

Write every joined input, fold definition, chain diagnostic, posterior forecast,
metric, ablation comparison, sensitivity result and gate to
`results/core_model/historical_state_space.json`. Record hashes for this
protocol, the outcome and exposure inputs, the v3 result, the model and sampler
sources, and the execution script. Generate PDF and PNG forecast and sensitivity
figures from that machine-readable result.

The final temporal holdout remains sealed after this experiment. Before it can
be opened, the complete falsification suite, holdout preprocessing, nuisance
covariates and one-shot failure rule must be separately frozen and pushed.
