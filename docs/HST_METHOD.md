# HST paired-dark pilot: preregistered extraction

This is an exploratory RAW-dark measurement, **not yet a validated longitudinal trap-density anchor**. The first acquisition probe was inspected only for geometry and calibration metadata before freezing these choices. No time-series fit or held-out model score has been examined.

The fixed pilot years are 2003, 2006, 2009, 2012, 2015, 2018, 2021, 2024. Query public ACS/WFC DARK exposures of 900–1200 s starting in the 31-day July window. Sort by exposure start and observation ID and select the first pair separated by at most one day. Retain exclusions. Many calibration exposures have no FLT; use **RAW consistently** for this pilot. No outcome-dependent replacement of a year.

Read full-frame SCI arrays by CCDCHIP, crop with LTV1/LTV2, and orient rows away from the parallel register. WFC2 increases with native y; WFC1 is reversed. Verify shape and native COUNTS units. RAW gain calibration values are unpopulated in the first probe. Therefore retain DN and commanded CCDGAIN as strata; **do not call these electrons**. Temperature is missing and explicitly null until matched telemetry is obtained.

Estimate each pixel's background from the median at same-row x offsets ±3, ±4. Constant row bias cancels, but this does not remove pixel bias structure, electronics bias shifts or cross-talk. Find persistent peaks in both frames, 100–3000 DN above local background, agreement within 30%, and local maxima. Reject edges, amplifier boundaries, and neighbouring off-column features exceeding 20% of the peak within five rows. One-frame cosmic rays are rejected; persistent electronic defects are not conclusively excluded. RAW DQ is uninitialised and must not be advertised as calibrated bad-pixel rejection.

Measure the sum of five downstream minus five upstream pixels divided by the peak signal. Retain the five-pixel profile, leading trail, serial asymmetry and offset-column blank control. These are dimensionless **trailing observables**, not per-transfer physical CTI. Bin by chip, commanded gain, native signal (100–300, 300–1000, 1000–3000 DN) and transfer distance (16–512, 512–1024, 1024–1536, 1536–2032). Use a column-cluster bootstrap for the mean and a 95% interval, seed 271828, 400 resamples. Require at least ten peaks in five columns. The interval excludes calibration, selection and temperature systematics.

Primary pilot view: 300–1000 DN and 1024–2032 transfers per chip; display gain changes explicitly. This selection is fixed before extraction. Do not combine it into a single physical damage curve across gain/electronics/temperature regimes.

Validation gate: synthetic trail recovery; sign reversal with wrong orientation; zero-trail and blank controls; persistence against cosmic rays; observed known-direction and transfer-distance dependence; stable processing/gain/temperature comparison; matched bias/reference calibration. Positive RAW asymmetry alone does not pass the gate. Compare with [Anderson & Bedin](https://arxiv.org/abs/1007.3987) and [ArCTIc](https://doi.org/10.1093/mnras/staf2186) concepts; no external CTI code copied.

Geometry and calibration reference: [ACS bias issues](https://hst-docs.stsci.edu/acsdhb/chapter-4-acs-data-processing-considerations/4-2-bias-issues), [ACS photometry / transfer distance](https://hst-docs.stsci.edu/acsdhb/chapter-5-acs-data-analysis/5-1-photometry), accessed 2026-09-09. Post-servicing bias effects require more than local-background subtraction.

Metadata-only refinement before extraction: restrict to individual observation roots ending in q and require exposure durations to agree within 1%. Aggregated s products appeared in the initial FLT query and cannot serve as independent RAW dark exposures. The frozen original query snapshots are preserved.
