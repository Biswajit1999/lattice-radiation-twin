# Validation contract

Preregistered before final held-out results. Time series use forward-chaining splits; fit transformations and lag selection on training data only. Final temporal holdout is evaluated once after development choices are frozen.

Required controls: synthetic injection and recovery; zero CTI; background and trail-direction controls; transfer-distance and signal dependence; known latent-parameter recovery; prior/posterior prediction; interval coverage; shuffled event dates; reversed time; irrelevant bands; zero events; calendar only; alternative lag priors; temporal binning; removal of major events; leave-one-event and leave-one-epoch prediction; alternate detector subsets; synthetic null.

Baselines B0–B5: linear time, polynomial/spline time, solar sinusoid, cumulative proton fluence, events plus background, autoregressive/state-space. Report RMSE, MAE, predictive density and interval coverage where defined. Model complexity needs out-of-sample support. Failed hypotheses are retained.

No final holdout has been selected or examined. Detailed cohort, units, exclusions and model-selection protocol must be frozen before observational evaluation.
