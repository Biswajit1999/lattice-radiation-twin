# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 7k - v3 frozen synthetic recovery and canonical SBC passed
- Completed milestones: Phases 0/2 and ingestion foundation pushed; HST replication, environment layer and B0–B5 benchmark complete; v1 recovery/ablations and v2 recovery/SBC failures retained; v3 heavy-tailed exact-posterior inference passes every frozen synthetic gate.
- Current tests and status: the v3 production run completed 100 fixed-truth and 100 prior-drawn SBC datasets with 99/100 usable chains in each population. Overall 95% interval coverage is 0.9688, median absolute standardized bias is 0.2694, latent RMSE is 0.00797, predictive coverage is 0.9444/0.9768, and all eight canonical SBC checks pass. Observational fitting remains prohibited pending the downstream sensitivity and forward-validation protocol.
- Known scientific risks: fixed-truth drift and process-scale rank histograms remain nonuniform diagnostics despite passing canonical SBC; background/post-flash, gain and electronics conditions are strongly time-confounded; active temperature sensor and pixel dwell times unresolved; three selected pairs per historical epoch remain sparse; column bootstrap excludes calibration uncertainty; eight epochs cannot resolve event lags; OMNI particle contamination is unchecked; SGPS and OMNI lack calibration overlap; the physical-inference gate is closed.
- Data successfully obtained: 54 HST RAW darks (1923143040 bytes), 54 matched SPT files (3110400 bytes), 21 CRDS references (2229229440 bytes), committed MAST query snapshots, 23 OMNI annual files (66132672 bytes), and 1,883 GOES-R SGPS daily files (1045894251 bytes). Six August 2025 holdout RAW files are checksum-pinned but their FITS arrays remain unopened.
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Calibrated HST exposure-averaged temperature and clock dwell-time telemetry not established. OMNI energetic-proton flux ends on 2020-03-04; the standard SGPS archive begins in November 2020, with no empirical overlap for intercalibration.
- Last successful commit SHA: dc1a08eafdf77fb8e87d36a4a2aaa49488cc9ff8
- Last successful push: origin/main verified at dc1a08eafdf77fb8e87d36a4a2aaa49488cc9ff8 before this checkpoint.
- Exact next action: freeze the post-recovery sensitivity and whole-epoch forward-validation protocol before any observational fit or temporal-holdout pixel access.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
