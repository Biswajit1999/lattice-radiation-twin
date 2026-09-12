# Frozen detector-to-science-bias protocol

Protocol frozen: **2026-09-12**, before the production image-domain run.

## Scope and model qualification

This first Phase 10 experiment quantifies Euclid VIS bias under the numerically
verified conditional release kernel from Phase 9. `arcticpy==2.6`, the published
ArCTIc Python package, was evaluated as an independent implementation but has no
Windows/Python 3.12 wheel and requires Microsoft C++ Build Tools that are absent
from the build host. It is not added as a non-working dependency.

The internal kernel passes exact causality and charge-conservation tests but does
not model signal-dependent occupancy, recapture, or four-phase/tri-level clock
dynamics. Results must therefore be labelled **CONDITIONAL LINEAR CTI
SCENARIOS**, not Euclid performance predictions. HST and Gaia image-bias runs
remain blocked by their failed/unavailable physical amplitudes and are recorded
as unavailable rather than filled with Euclid parameters.

## Frozen image population

All stamps are 96 x 96 Euclid pixels at 0.1 arcsec/pixel, with the source centred
at `(x, y) = (48, 24)` so downstream parallel trails have 71 pixels of measured
support. The PSF is a circular Gaussian with FWHM 0.16 arcsec.

- Point sources use total fluxes `{1000, 10000}` electrons.
- Faint galaxies are elliptical Gaussians with intrinsic major-axis sigma 2.0
  pixels, axis ratio 0.7, four ring-test orientations `{0, 45, 90, 135}` degrees,
  and total fluxes `{1000, 3000}` electrons.
- Uniform backgrounds are `{20, 100}` electrons/pixel.
- Gaussian read noise is 4.5 electrons, the published upper bound.

The experiment uses 32 fixed paired standard-normal noise fields per scenario.
The same field is scaled by each clean or trailed model's shot-plus-background-
plus-read variance. This common-random-number design estimates the CTI increment
with lower Monte Carlo noise; it is not a detector posterior.

## Frozen CTI scenarios

Only parallel transfer is used for morphology because the science image is
clocked by rows. The fixed axes are:

- full-array captured fraction `{0.001, 0.003, 0.01}`;
- transfer-distance fraction `{0.25, 1}`;
- fast-species mixture weight `{0.25, 0.5, 0.75}`;
- common emission-timescale factor `{0.5, 1, 2}`.

All values are sensitivity scenarios. No mission date, trap-density estimate,
HST coefficient, Gaia coefficient, or posterior sample is used.

## Frozen measurements

Known background is subtracted. Flux and unweighted first/second moments are
measured inside a fixed 12-pixel circular aperture centred on the pristine source
location. The metrics are:

- fractional aperture-flux bias;
- x and y centroid bias in pixels and y bias in milliarcseconds;
- `e1 = (Qxx - Qyy) / (Qxx + Qyy)` and
  `e2 = 2 Qxy / (Qxx + Qyy)`;
- fractional trace-size bias from `Qxx + Qyy`.

Each scenario reports the median and 2.5/97.5 percentiles over the 32 paired
noise realisations. Invalid moment measurements are counted and never silently
dropped.

For the galaxy ring test, input reduced shears `g1 = {-0.02, 0, 0.02}` and
`g2 = {-0.02, 0, 0.02}` are applied separately. Ring-averaged measured
ellipticity is regressed on input shear for pristine and trailed images. The
conditional multiplicative term is `m = R_cti / R_clean - 1`; the additive term
is the trailed-minus-pristine intercept. These are algorithm-response diagnostics
for the simulated Gaussian population, not a Euclid cosmological shear
measurement.

## Frozen gates

The run passes its implementation gate only if:

1. every noiseless source conserves input flux before aperture truncation to
   relative error `<= 1e-12`, including recorded overflow;
2. zero-capture scenarios have absolute noiseless metric bias `<= 1e-12`;
3. all scenario summaries are finite and each retains at least 30/32 valid
   paired measurements;
4. a noiseless point source at full distance has non-decreasing positive y
   centroid shift as captured fraction rises from 0.001 to 0.01;
5. the untrailed x-centroid control remains unchanged to `<= 1e-12` noiselessly;
6. every reported interval is ordered lower <= median <= upper;
7. HST/Gaia amplitudes, calendar forecasts, and posterior intervals are absent.

Passing these gates validates the experiment's numerical behaviour. It does not
validate the scenario amplitudes or the linear CTI approximation.
