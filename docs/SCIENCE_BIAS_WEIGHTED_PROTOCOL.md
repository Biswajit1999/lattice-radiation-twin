# Frozen weighted detector-to-science-bias protocol

Protocol frozen: **2026-09-13**, after retaining the Phase 10a failure and before
implementing or running this follow-up.

## Motivation and separation

Phase 10a failed because background-subtracted unweighted moments inside a
12-pixel aperture retained as few as 8/32 valid paired measurements. That result
and its output remain unchanged. Phase 10b is a separately versioned experiment
using a standard fixed Gaussian weight to limit background-noise variance. It is
not a post-hoc replacement for Phase 10a.

## Frozen estimator

The image population, CTI grid, detector constants, paired noise fields, random
seeds and ring-test shears are identical to Phase 10a. Within the same 12-pixel
circular aperture, define a circular Gaussian weight centred at the pristine
source position with fixed sigma `3.0` pixels. The weight is never recentered or
adapted to a noisy image.

Known background is subtracted before weighting. Weighted flux, centroid and
central second moments are computed from `weight * (image - background)`. The
reported flux metric is the fractional change in this weighted flux; centroid,
ellipticity and trace-size metrics use the weighted moments. This is an
algorithm-response diagnostic and not a total-flux estimator.

The same weight is used for clean and trailed members of every paired noise
realisation. Invalid non-positive weighted flux or trace measurements are
counted. Each scenario reports median and 2.5/97.5 percentiles over 32 pairs.

## Frozen gates

The run passes only if:

1. all seven unchanged Phase 10a numerical and claim-boundary gates pass,
   including at least 30/32 valid pairs in every scenario;
2. every scenario metric and ring-response value is finite;
3. the full grid contains exactly 432 source scenarios and 54 ring scenarios;
4. the zero-capture weighted biases are `<= 1e-12` in absolute value;
5. the noiseless full-distance y-centroid shift is positive and non-decreasing
   over captured fractions `{0.001, 0.003, 0.01}`;
6. the absolute zero-capture x-centroid control is `<= 1e-12`;
7. the original Phase 10a result file and protocol hashes are recorded as the
   diagnosed predecessor and are not modified by the run.

A pass validates numerical execution and measurement stability for the fixed
analytic scenarios only. The captured fractions remain sensitivity values. The
run must continue to withhold observational damage amplitude, calendar
forecast, HST/Gaia propagation, Euclid performance claims and posterior CTI
uncertainty.
