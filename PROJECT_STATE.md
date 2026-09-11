# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 7j - v3 sampler, diagnostics and posterior-state mixture implemented before production
- Completed milestones: Phases 0/2 and ingestion foundation pushed; HST replication, environment layer and B0–B5 benchmark complete; v1 recovery/ablations and v2 recovery/SBC failures retained; v3 heavy-tailed independence sampler, rank diagnostics, fixed-truth/SBC harness and posterior state mixture implemented.
- Current tests and status: 54 tests passed in 29.94s; Ruff check and formatting passed. Both production-budget v3 smoke datasets passed every R-hat/ESS criterion. The earlier v2 run passed its primary recovery gates but failed canonical process-scale SBC; no v3 population result exists yet and observational fitting remains prohibited.
- Known scientific risks: the v1 priors were too broad; v2 Laplace inference underestimates process scale despite adequate latent RMSE; a new sampler may mix poorly or remain computationally expensive; background/post-flash, gain and electronics conditions are strongly time-confounded; active temperature sensor and pixel dwell times unresolved; three selected pairs per historical epoch remain sparse; column bootstrap excludes calibration uncertainty; eight epochs cannot resolve event lags; OMNI particle contamination is unchecked; SGPS and OMNI lack calibration overlap; the physical-inference gate is closed.
- Data successfully obtained: 54 HST RAW darks (1923143040 bytes), 54 matched SPT files (3110400 bytes), 21 CRDS references (2229229440 bytes), committed MAST query snapshots, 23 OMNI annual files (66132672 bytes), and 1,883 GOES-R SGPS daily files (1045894251 bytes). Six August 2025 holdout RAW files are checksum-pinned but their FITS arrays remain unopened.
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Calibrated HST exposure-averaged temperature and clock dwell-time telemetry not established. OMNI energetic-proton flux ends on 2020-03-04; the standard SGPS archive begins in November 2020, with no empirical overlap for intercalibration.
- Last successful commit SHA: 52081ad426ed744567a956f688f60204fd8f0c18
- Last successful push: origin/main verified at 52081ad426ed744567a956f688f60204fd8f0c18 before this checkpoint.
- Exact next action: run the frozen 100 fixed-truth and 100 prior-drawn v3 populations, retain every failed gate, and do not fit observations or open the holdout.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
