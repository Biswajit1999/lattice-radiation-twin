# Frozen forced-response detector-to-science-bias protocol

Protocol frozen: **2026-09-13**, after retaining both moment-estimator failures
and before implementing or running this experiment.

## Motivation and estimator class

Phase 10a unweighted moments and Phase 10b fixed Gaussian weighted moments fail
their common minimum-valid-pairs gate. Both results remain unchanged. Phase 10c
tests fixed-template, linearized response statistics. This estimator is suited
to controlled injection experiments where the pristine analytic source and
background are known; it is not a blind source-measurement algorithm.

The image population, CTI scenarios, 3-pixel circular Gaussian weight, aperture,
paired noise fields, seeds and ring-test inputs remain identical to Phase 10b.
The pristine noiseless weighted source defines fixed positive normalization
constants for every source type and flux.

## Frozen response statistics

For each noisy clean/trailed pair, subtract the known background and compute the
difference in weighted linear sums. With coordinates relative to the fixed
pristine centre, report:

- weighted flux response `delta_F / F_ref`;
- forced centroid responses `delta_Mx / F_ref` and `delta_My / F_ref`;
- trace-size response `delta_T / T_ref`;
- first-order ellipticity responses
  `delta_e1 = (delta_D - e1_ref * delta_T) / T_ref` and
  `delta_e2 = (2 * delta_X - e2_ref * delta_T) / T_ref`, where
  `D = Nxx - Nyy`, `T = Nxx + Nyy`, and `X = Nxy`.

The same formula is applied to noiseless pairs. All denominators come from the
positive noiseless pristine template and are never estimated from a noisy image.
The y response is converted with 100 milliarcseconds per Euclid VIS pixel.
Median and 2.5/97.5 percentiles are stored over all 32 paired fields.

The noiseless ring test continues to use the fixed weighted moments from Phase
10b because those analytic images have positive finite flux and trace. Its
interpretation remains an algorithm-response diagnostic.

## Frozen gates

The implementation passes only if:

1. all 32/32 forced responses are finite in every one of 432 source scenarios;
2. exactly 54 finite noiseless ring scenarios are present;
3. all intervals are ordered;
4. charge conservation remains `<= 1e-12` relative error;
5. every zero-capture response and the zero-capture x control are `<= 1e-12`;
6. the noiseless full-distance y response is positive and non-decreasing over
   captured fractions `{0.001, 0.003, 0.01}`;
7. the Phase 10a and 10b result and protocol files remain byte-identical and all
   four hashes are recorded;
8. observational amplitude, calendar, posterior, cosmological-shear and blocked
   HST/Gaia claims remain absent.

A pass establishes stable forced-response computation for the fixed analytic
scenario grid. It does not validate captured fraction, the linear CTI model, a
survey measurement pipeline, or mission performance.
