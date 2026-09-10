# Frozen historical baseline protocol

Status: **PREREGISTERED BEFORE BASELINE EXECUTION**. This document and the implementation are committed before `scripts/run_baselines.py` is run on the historical outcomes. The six August 2025 temporal-holdout pixel arrays remain unopened.

## Outcome and unit of prediction

The outcome is the mean calibrated five-pixel parallel trail fraction for each of the 32 independent replication summaries: eight epochs × two pair indices × two ACS/WFC chips. Development-pair measurements are excluded. Pair-by-chip stratum intercepts are included in B0–B4. The bootstrap interval width is converted to an approximate standard error only for predictive variance; the regressions are unweighted because that interval excludes shared calibration systematics.

Each test unit is a whole epoch containing all four strata. Expanding-window folds train through 2012, 2015, 2018 and 2021 and test 2015, 2018, 2021 and 2024 respectively. This yields 16 predictions per baseline. No time series is shuffled. Features are standardized from the training fold only.

Environment features use the last completed UTC month before an exposure. This avoids using environment measurements obtained later in the observation month and imposes a documented lag of up to 31 days. Missing pre-series cumulative fluence is zero; measured gaps are never filled. OMNI and SGPS cumulative quantities receive independent coefficients.

## Frozen baselines

- **B0 calendar linear:** elapsed time plus the four pair-by-chip stratum intercepts.
- **B1 calendar quadratic:** elapsed time and squared elapsed time plus stratum intercepts.
- **B2 solar-cycle sinusoid:** fixed 11-year sine and cosine terms plus stratum intercepts. It is a descriptive calendar baseline, not measured particle dose.
- **B3 cumulative particle:** independent `log1p` cumulative OMNI observed fluence and SGPS band-integrated proxy fluence plus stratum intercepts. It does not splice the instruments.
- **B4 event + continuous background:** independent `log1p` cumulative above-10-pfu and subthreshold fluence terms for OMNI and SGPS plus stratum intercepts. SGPS threshold terms remain proxy quantities.
- **B5 local-level drift:** for each stratum, forecast from its last observed level using a recency-weighted mean of earlier per-year increments. Innovation dispersion and the held-out bootstrap standard error define predictive variance. This is a transparent local linear state-space baseline.

B0–B4 use ordinary least squares and a Moore–Penrose inverse when a source feature has no variance in an early training fold. Such a feature is centered to zero and cannot affect that fold’s prediction. Prediction variance contains residual variance, coefficient-estimation variance and the held-out approximate measurement variance. A variance floor of `1e-8` prevents a degenerate Gaussian score.

## Frozen metrics and screens

Report pooled RMSE, MAE, mean Gaussian negative log predictive density, empirical 95% prediction-interval coverage, mean Gaussian CRPS and out-of-sample R². The R² denominator is the expanding-fold training mean for the same pair-by-chip stratum; it is a predictive comparison and may be negative.

All six baselines fail implementation validation if they do not each produce 16 finite predictions with positive predictive standard deviations. B3/B4 provide historical exposure support only if at least one beats B0 on both pooled RMSE and mean negative log predictive density. This screen does not establish causation and cannot open the physical-inference gate by itself.

A later advanced model justifies added complexity only if, on untouched temporal predictions, it simultaneously:

1. reduces RMSE by at least 5% relative to the best frozen baseline;
2. has lower mean negative log predictive density than the best frozen baseline; and
3. has 95% interval coverage of at least 75%.

The historical benchmark fixes numerical target values for those criteria. No selection among models, lags or features may use the August 2025 holdout. The holdout remains sealed until the latent-model specification, optimization bounds and posterior-predictive failure rules are separately frozen and pushed.
