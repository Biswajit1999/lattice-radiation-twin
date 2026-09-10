# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 6 - historical B0–B5 benchmark complete; core latent-model specification next
- Completed milestones: Phases 0/2 and ingestion foundation pushed; HST historical replication and 2003–2025 environment/proxy layer complete; six preregistered baselines evaluated across four whole-epoch forward folds. B0 has the lowest RMSE; the exposure-support screen failed; the physical-inference gate remains closed.
- Current tests and status: 33 passed in 3.07s; Ruff check and formatting passed. All six baselines produced 16 finite historical predictions. Synthetic tests verify Gaussian CRPS, complete B0–B5 output and blindness of an early fold to later outcomes.
- Known scientific risks: background/post-flash, gain and electronics conditions are strongly time-confounded; active temperature sensor and pixel dwell times unresolved; three selected pairs per historical epoch remain sparse; column bootstrap excludes calibration uncertainty; eight epochs cannot resolve event lags; OMNI particle contamination is unchecked; SGPS and OMNI lack calibration overlap; the physical-inference gate is closed.
- Data successfully obtained: 54 HST RAW darks (1923143040 bytes), 54 matched SPT files (3110400 bytes), 21 CRDS references (2229229440 bytes), committed MAST query snapshots, 23 OMNI annual files (66132672 bytes), and 1,883 GOES-R SGPS daily files (1045894251 bytes). Six August 2025 holdout RAW files are checksum-pinned but their FITS arrays remain unopened.
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Calibrated HST exposure-averaged temperature and clock dwell-time telemetry not established. OMNI energetic-proton flux ends on 2020-03-04; the standard SGPS archive begins in November 2020, with no empirical overlap for intercalibration.
- Last successful commit SHA: 2c70aa5ddf681d1e0569b2055f6ff1dc7ca73506
- Last successful push: origin/main verified at 2c70aa5ddf681d1e0569b2055f6ff1dc7ca73506 before this checkpoint.
- Exact next action: Specify the core latent-state transition and observation model, identifiability constraints, optimization bounds and posterior-predictive failure rules before fitting it or opening any August 2025 holdout pixel array.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
