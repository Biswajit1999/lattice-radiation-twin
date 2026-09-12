# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 7n - frozen historical state-space forecast and attribution gates failed
- Completed milestones: Phases 0/2 and ingestion foundation pushed; HST replication, environment layer and B0–B5 benchmark complete; v1 recovery/ablations and v2 recovery/SBC failures retained; v3 exact-posterior inference passes every synthetic gate; the historical state-space primary, ablations and sensitivities are executed and retained.
- Current tests and status: all 40 historical fits completed. H0 has four usable folds and 16 finite forecasts but fails RMSE (0.04977 versus 0.03823 maximum) and predictive density (-1.6480 versus below -1.7824). Its zero-event model is better on both metrics. The primary advanced-model and exposure-attribution gates fail; physical inference stays closed and the holdout stays sealed.
- Known scientific risks: fixed-truth drift and process-scale rank histograms remain nonuniform diagnostics despite passing canonical SBC; background/post-flash, gain and electronics conditions are strongly time-confounded; active temperature sensor and pixel dwell times unresolved; three selected pairs per historical epoch remain sparse; column bootstrap excludes calibration uncertainty; eight epochs cannot resolve event lags; OMNI particle contamination is unchecked; SGPS and OMNI lack calibration overlap; the physical-inference gate is closed.
- Data successfully obtained: 54 HST RAW darks (1923143040 bytes), 54 matched SPT files (3110400 bytes), 21 CRDS references (2229229440 bytes), committed MAST query snapshots, 23 OMNI annual files (66132672 bytes), and 1,883 GOES-R SGPS daily files (1045894251 bytes). Six August 2025 holdout RAW files are checksum-pinned but their FITS arrays remain unopened.
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Calibrated HST exposure-averaged temperature and clock dwell-time telemetry not established. OMNI energetic-proton flux ends on 2020-03-04; the standard SGPS archive begins in November 2020, with no empirical overlap for intercalibration.
- Last successful commit SHA: 5baecf45205dc31f58129aac138f8b19c9d0a1c7
- Last successful push: origin/main verified at 5baecf45205dc31f58129aac138f8b19c9d0a1c7 before this checkpoint.
- Exact next action: retain and publish the failed historical result, then begin the Phase 8 Gaia public-data availability and external-validation audit without reopening H0 tuning.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
