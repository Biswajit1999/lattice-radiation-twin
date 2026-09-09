# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 4j - replicated HST cohort acquired; August 2025 pixels remain sealed
- Completed milestones: Phases 0/2 and ingestion foundation pushed; 16 HST RAW/SPT files and 17 CRDS references verified; all 16 frames calibrated with official ACSCCD; calibrated eight-epoch extraction, controls and synthetic trail recovery executed.
- Current tests and status: 21 passed in 1.78s; Ruff passed.
- Known scientific risks: background/post-flash and electronics conditions differ by epoch; active temperature sensor and pixel dwell times unresolved; one nominal blank control excludes zero; one pair per epoch and bootstrap exclude between-exposure/calibration uncertainty; sparse epochs cannot resolve event lags.
- Data successfully obtained: 54 HST RAW darks (1923143040 bytes), 54 matched SPT files (3110400 bytes), 17 CRDS references (1543392000 bytes), committed MAST query snapshots, and three production OMNI annual files (8619840 bytes). Six August 2025 holdout RAW files are checksum-pinned but their FITS arrays remain unopened.
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Calibrated HST exposure-averaged temperature and clock dwell-time telemetry not established. OMNI energetic-proton flux ends in 2020; a later source is required.
- Last successful commit SHA: 600f02ab0d3af65ff5a319f44c25da58fe66ec6f
- Last successful push: origin/main verified at 600f02ab0d3af65ff5a319f44c25da58fe66ec6f before this checkpoint.
- Exact next action: Resolve pinned CRDS assignments and calibrate only the 32 replication RAW files; keep all six holdout pixel arrays unopened.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
