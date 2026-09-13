# Validation contract

Preregistered before final held-out results. Time series use forward-chaining splits; fit transformations and lag selection on training data only. Final temporal holdout is evaluated once after development choices are frozen.

Required controls: synthetic injection and recovery; zero CTI; background and trail-direction controls; transfer-distance and signal dependence; known latent-parameter recovery; prior/posterior prediction; interval coverage; shuffled event dates; reversed time; irrelevant bands; zero events; calendar only; alternative lag priors; temporal binning; removal of major events; leave-one-event and leave-one-epoch prediction; alternate detector subsets; synthetic null.

Baselines B0–B5: linear time, polynomial/spline time, solar sinusoid, cumulative proton fluence, events plus background, autoregressive/state-space. Report RMSE, MAE, predictive density and interval coverage where defined. Model complexity needs out-of-sample support. Failed hypotheses are retained.

The temporal holdout was selected from archive metadata on 2026-09-09, after the initial development result and before its pixels were downloaded or opened. The deterministic fallback rule selected three August 2025 pairs: jfd2c9wqq/jfd2cawwq, jfd2cea1q/jfd2cfa6q and jfd2cjt5q/jfd2cktbq. They remain unexamined. Pixel preprocessing, nuisance covariates, baseline models, metrics and failure thresholds must be versioned and pushed before extracting this holdout. The development-informed status limits what this holdout can validate; see `HST_REPLICATION_PROTOCOL.md`.

## Phase 11 executable falsification matrix

Frozen: **2026-09-13**, before computing the new transformed-control results.
The B0--B5 and observational state-space results were already known, so tests
that merely consolidate those outputs are retrospective. Newly generated
shuffle, reversal, band, binning, event-removal, subset and null results are
prospectively fixed here. The suite uses only the 32 existing replication
summaries and committed monthly environment table. The six August 2025 holdout
pixel arrays remain sealed and are forbidden inputs.

All predictive comparisons use RMSE and mean negative log predictive density
(NLPD), with MAE, 95% coverage, CRPS and out-of-sample R2 retained. “Beats B0”
means strictly lower RMSE and strictly lower NLPD on identical predictions.
Transformations are fit within each training fold; no held-out outcome enters
feature construction or scaling.

The frozen tests are:

1. **F01 shuffled event dates:** permute the eight epoch-level event-feature
   vectors with NumPy seed `11101`, applying one shared permutation to all four
   detector strata. The shuffled exposure model must not beat B0.
2. **F02 reversed time:** reverse the eight epoch-level environment-feature
   vectors while retaining outcome chronology. The reversed exposure model must
   not beat B0.
3. **F03 irrelevant radiation band:** use cutoff-month mean Kp as a negative-
   control feature. It must not beat B0.
4. **F04 zero-event model:** reuse the exact-zero-event observational state-
   space result. Attribution support requires the primary model to have lower
   RMSE and NLPD than this ablation.
5. **F05 calendar-only model:** reuse B0 as the mandatory reference.
6. **F06 alternative lag priors:** reuse the fixed 1, 3 and 6 month state-space
   sensitivities. Each must produce 16 finite predictions; robustness requires
   primary RMSE within 10% of each finite sensitivity and coverage at least 0.75.
7. **F07 temporal binning:** construct non-overlapping calendar-quarter OMNI
   event and background sums through each cutoff, then log-transform cumulative
   values. The resulting exposure model must beat B0 on both primary scores for
   robustness support.
8. **F08 removal of major Solar events:** identify the three largest monthly
   OMNI threshold fluences using exposure data only, set those event increments
   to zero, reconstruct cumulative event exposure, and refit. Robustness requires
   RMSE no worse than 10% above the unmodified exposure model and finite scores.
9. **F09 leave-one-event-out:** repeat the event-removal calculation separately
   for each of the five largest monthly OMNI threshold fluences. Every result
   must be finite; attribution stability requires all RMSE values within 20% of
   the unmodified exposure model.
10. **F10 leave-one-epoch-out prediction:** for each of eight epochs, train B0
    and the exposure model on the other seven epochs and predict all four held-
    out strata. This interpolation/extrapolation diagnostic is explicitly
    non-temporal. Exposure support requires lower pooled RMSE and NLPD than B0.
11. **F11 alternate detector subsets:** repeat forward chaining for chip 1,
    chip 2, pair 2 and pair 3 subsets, with stratum indicators rebuilt from the
    available subset. Every subset must be finite; attribution stability
    requires the exposure model to beat its matching calendar comparator in at
    least three of four subsets.
12. **F12 synthetic null:** within each detector stratum, randomly permute the
    eight outcomes in 200 datasets with seed `11200`. The false-positive rate is
    the fraction in which the exposure model beats B0 on both scores and must be
    at most 0.10.

The suite-level radiation-attribution gate passes only if the already frozen
primary historical gate passes, F04 supports the event term, the negative
controls F01--F03 pass, all finite/completeness checks pass, F07 and F10 support
exposure, F08--F09 and F11 meet their robustness rules, and F12 controls false
positives. Any failure is retained. No result from this suite can reopen the
physical-inference gate or authorize the sealed temporal holdout.
