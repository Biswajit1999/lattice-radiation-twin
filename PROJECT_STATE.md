# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 4h - calibrated HST development cohort measured; physical-inference gate open
- Completed milestones: Phases 0/2 and ingestion foundation pushed; 16 HST RAW/SPT files and 17 CRDS references verified; all 16 frames calibrated with official ACSCCD; calibrated eight-epoch extraction, controls and synthetic trail recovery executed.
- Current tests and status: 20 passed in 1.82s; Ruff passed.
- Known scientific risks: background/post-flash and electronics conditions differ by epoch; active temperature sensor and pixel dwell times unresolved; one nominal blank control excludes zero; one pair per epoch and bootstrap exclude between-exposure/calibration uncertainty; sparse epochs cannot resolve event lags.
- Data successfully obtained: 16 HST RAW darks (566645760 bytes), 16 matched SPT files (921600 bytes), 17 CRDS references (1543392000 bytes), committed MAST query snapshots, and three production OMNI annual files (8619840 bytes).
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Calibrated HST exposure-averaged temperature and clock dwell-time telemetry not established. OMNI energetic-proton flux ends in 2020; a later source is required.
- Last successful commit SHA: 5996763da9de730dd2944d4556133bba65d0ee39
- Last successful push: origin/main verified at 5996763da9de730dd2944d4556133bba65d0ee39 before this checkpoint.
- Exact next action: Freeze and acquire a replicated ACS/WFC dark cohort with background/electronics strata and an untouched temporal holdout.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
