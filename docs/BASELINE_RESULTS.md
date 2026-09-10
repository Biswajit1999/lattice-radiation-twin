# Historical forward-chaining baseline result

The preregistered B0–B5 benchmark produced 16 predictions per model: four pair-by-chip strata at each held-out epoch in 2015, 2018, 2021 and 2024. Every prediction was generated from earlier epochs only, using environment features cut off at the end of the preceding UTC month.

| Model | RMSE | MAE | mean NLPD | 95% coverage | mean CRPS | predictive R² |
|---|---:|---:|---:|---:|---:|---:|
| B0 calendar linear | 0.04024 | 0.03353 | -1.7692 | 0.8750 | 0.02339 | 0.8521 |
| B1 calendar quadratic | 0.05429 | 0.04483 | -1.4087 | 0.8750 | 0.03190 | 0.7309 |
| B2 solar-cycle sinusoid | 0.11852 | 0.11545 | -0.0140 | 0.7500 | 0.08034 | -0.2824 |
| B3 cumulative particle | 0.07093 | 0.05881 | -1.1925 | 0.9375 | 0.04109 | 0.5407 |
| B4 event + background | 0.04055 | 0.03582 | -1.7824 | 0.9375 | 0.02341 | 0.8499 |
| B5 local-level drift | 0.04802 | 0.04155 | -1.5893 | 0.9375 | 0.02853 | 0.7895 |

B0 has the lowest RMSE. B4 has the lowest mean negative log predictive density, but its RMSE is 0.76% higher than B0. The preregistered exposure-support screen required B3 or B4 to beat B0 on both quantities. It therefore fails. B2’s negative predictive R² also shows that an 11-year sinusoid alone is not a useful historical forecast for this outcome.

These comparisons do not show that the environment is irrelevant. The exposure history changes instruments without overlap, the outcome has only eight epochs, detector background and operating state are time-confounded, and B4’s design is rank-deficient in early folds before SGPS begins. They show that these frozen low-dimensional exposure proxies do not improve the historical forecast on the required joint screen.

The future advanced-model targets fixed by this result are RMSE at or below 0.0382313, mean NLPD below -1.78239, and 95% interval coverage of at least 0.75 on untouched temporal predictions. Passing those numerical targets would justify predictive complexity; it would not by itself establish a physical radiation-dose interpretation.

The physical-inference gate remains **CLOSED**. The August 2025 holdout pixel arrays remain unopened.

![Forward-chaining historical baseline forecasts](../paper/figures/baseline_forecasts.png)
