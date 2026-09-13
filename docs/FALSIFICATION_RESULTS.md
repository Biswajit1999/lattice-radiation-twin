# Comprehensive falsification result

The frozen Phase 11 suite **fails**. Five of eleven directional tests pass, all
core outputs are finite, and the temporal holdout remains sealed. The already
failed historical primary gate and the combined directional-test gate remain
false, so the physical-inference gate stays closed.

The shuffled-event, reversed-time and Kp negative controls pass by failing to
beat calendar time. Removing the three largest OMNI event months and the five
leave-one-event-out runs remain within their preregistered stability limits.

Six tests fail. The primary state-space model does not beat its exact-zero-event
ablation. Alternative lags do not satisfy all robustness checks. The exposure
model does not beat calendar time under the temporal-binning or leave-one-epoch-
out comparisons. It wins only two of four detector-subset comparisons rather
than the required three. On 200 within-stratum synthetic-null permutations, the
exposure model beats calendar time on both scores in 35% of runs, above the
fixed 10% false-positive limit.

For the original forward-chaining comparison, B0 calendar-linear has RMSE
`0.04024` and NLPD `-1.76925`; B4 event-plus-background has RMSE `0.04055` and
NLPD `-1.78239`. B4 improves NLPD slightly but worsens RMSE, so it does not meet
the two-metric rule. No exposure-attribution hypothesis is promoted.

The test matrix consolidates previously known baseline/state-space results and
new prospectively frozen transformations. It does not access or authorize the
six August 2025 holdout pixel arrays. Machine-readable output is stored at
`results/falsification/comprehensive_suite.json`.
