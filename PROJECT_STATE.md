# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 7b - exact state-space engine and 100-replicate recovery harness implemented before batch execution
- Completed milestones: Phases 0/2 and ingestion foundation pushed; HST replication, environment layer and B0–B5 benchmark complete; core protocol preregistered; exact Kalman filter/RTS smoother, constrained MAP estimator, Laplace approximation, prior/predictive checks and SBC recovery harness implemented.
- Current tests and status: 37 passed in 7.30s; Ruff check passed and all 44 Python files are formatted. A complete 48-epoch single-replicate dry run converged and the smoothed-state test recovers synthetic trajectories below the observation-noise scale.
- Known scientific risks: background/post-flash, gain and electronics conditions are strongly time-confounded; active temperature sensor and pixel dwell times unresolved; three selected pairs per historical epoch remain sparse; column bootstrap excludes calibration uncertainty; eight epochs cannot resolve event lags; OMNI particle contamination is unchecked; SGPS and OMNI lack calibration overlap; the physical-inference gate is closed.
- Data successfully obtained: 54 HST RAW darks (1923143040 bytes), 54 matched SPT files (3110400 bytes), 21 CRDS references (2229229440 bytes), committed MAST query snapshots, 23 OMNI annual files (66132672 bytes), and 1,883 GOES-R SGPS daily files (1045894251 bytes). Six August 2025 holdout RAW files are checksum-pinned but their FITS arrays remain unopened.
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Calibrated HST exposure-averaged temperature and clock dwell-time telemetry not established. OMNI energetic-proton flux ends on 2020-03-04; the standard SGPS archive begins in November 2020, with no empirical overlap for intercalibration.
- Last successful commit SHA: 2d97f8a605b6cc1a29d53847379d4ca78a794493
- Last successful push: origin/main verified at 2d97f8a605b6cc1a29d53847379d4ca78a794493 before this checkpoint.
- Exact next action: Execute the frozen 100-replicate synthetic recovery and retain every failed gate before considering any observational latent-state fit or holdout access.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
