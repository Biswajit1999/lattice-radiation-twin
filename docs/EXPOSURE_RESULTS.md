# Continuous environment and exposure-proxy result

The frozen acquisition retrieved and SHA-256 verified 23 NASA OMNI annual files (66,132,672 bytes) and 1,883 NOAA GOES-R SGPS daily files (1,045,894,251 bytes). The result spans 276 calendar months from January 2003 through December 2025. F10.7 and Kp have valid monthly means throughout.

The particle series contains 200 months with observed OMNI >10 MeV flux, 62 months with the SGPS band-integrated proxy and 14 months with neither. The missing months comprise January–July 2003 and April–October 2020. March 2020 has 11.7% OMNI coverage. March 2021 has 82.0% SGPS coverage because four daily files are absent from the upstream archive. No missing interval was filled, divided by coverage or treated as zero.

OMNI contributes 133,113 valid particle hours. Every one has quality flag `-1`, meaning magnetospheric contamination was not checked. SGPS contributes 541,399 valid five-minute reconstructions from 543,456 possible slots in its selected calendar interval. Its differential support ends at 404 MeV in 1,518 GOES-16 files and 390 MeV in 365 GOES-18 files before the separate >500 MeV channel. The derived value is therefore a proxy constructed from observed channels. It is not interchangeable with the OMNI integral channel.

The threshold screen identifies 118 contiguous OMNI runs and 196 SGPS proxy runs at 10 pfu. It is useful for event covariates but does not classify detector damage. The SGPS runs are not official NOAA S1 events. Exact event boundaries, peak values, nominal-cadence fluences and durations are in `results/environment/threshold_events.json`.

`results/environment/monthly_exposure.json` records the observed activity indices, the two instrument particle summaries, separate cumulative fluences, coverage, rolling terms, source-specific event timing, solar-cycle coordinate and unfit HST/LEO and L2 response bases. Kp enters only the HST/LEO basis. The inverse-F10.7 term is explicitly a GCR proxy. No response coefficient, lag, shielding kernel, inferred effective detector exposure or physical dose has been estimated.

There is no standard-archive overlap suitable for empirical OMNI–SGPS intercalibration. The two cumulative series remain separate, and the April–October 2020 gap remains visible. This phase establishes an independently testable exposure layer; it does not reopen the physical-inference gate.

![Observed external environment and particle proxy coverage](../paper/figures/environment_timeline.png)
