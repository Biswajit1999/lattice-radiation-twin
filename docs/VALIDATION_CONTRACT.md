# Validation contract

Preregistered before final held-out results. Time series use forward-chaining splits; fit transformations and lag selection on training data only. Final temporal holdout is evaluated once after development choices are frozen.

Required controls: synthetic injection and recovery; zero CTI; background and trail-direction controls; transfer-distance and signal dependence; known latent-parameter recovery; prior/posterior prediction; interval coverage; shuffled event dates; reversed time; irrelevant bands; zero events; calendar only; alternative lag priors; temporal binning; removal of major events; leave-one-event and leave-one-epoch prediction; alternate detector subsets; synthetic null.

Baselines B0–B5: linear time, polynomial/spline time, solar sinusoid, cumulative proton fluence, events plus background, autoregressive/state-space. Report RMSE, MAE, predictive density and interval coverage where defined. Model complexity needs out-of-sample support. Failed hypotheses are retained.

The temporal holdout was selected from archive metadata on 2026-09-09, after the initial development result and before its pixels were downloaded or opened. The deterministic fallback rule selected three August 2025 pairs: jfd2c9wqq/jfd2cawwq, jfd2cea1q/jfd2cfa6q and jfd2cjt5q/jfd2cktbq. They remain unexamined. Pixel preprocessing, nuisance covariates, baseline models, metrics and failure thresholds must be versioned and pushed before extracting this holdout. The development-informed status limits what this holdout can validate; see `HST_REPLICATION_PROTOCOL.md`.
