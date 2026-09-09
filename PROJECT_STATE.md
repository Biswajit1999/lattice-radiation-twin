# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 4n - replication nuisance join frozen; calibration in progress
- Completed milestones: Phases 0/2 and ingestion foundation pushed; 54 HST RAW/SPT files acquired with six holdout arrays sealed; initial 16 frames calibrated with official ACSCCD; calibrated eight-epoch extraction and controls executed; CRDS assignments, independent outcome screens and an engineering-state join frozen for 32 replication frames only.
- Current tests and status: 24 passed in 3.47s; Ruff passed. The clean-runner import failure at the previous checkpoint is fixed by placing tested statistics in the installable package.
- Known scientific risks: background/post-flash and electronics conditions differ by epoch; active temperature sensor and pixel dwell times unresolved; one nominal blank control excludes zero; one pair per epoch and bootstrap exclude between-exposure/calibration uncertainty; sparse epochs cannot resolve event lags.
- Data successfully obtained: 54 HST RAW darks (1923143040 bytes), 54 matched SPT files (3110400 bytes), 21 CRDS references (2229229440 bytes), committed MAST query snapshots, and three production OMNI annual files (8619840 bytes). Six August 2025 holdout RAW files are checksum-pinned but their FITS arrays remain unopened.
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Calibrated HST exposure-averaged temperature and clock dwell-time telemetry not established. OMNI energetic-proton flux ends in 2020; a later source is required.
- Last successful commit SHA: 55d78496a34e7c1e4ccf73278d12c3ac2fce66d3
- Last successful push: origin/main verified at 55d78496a34e7c1e4ccf73278d12c3ac2fce66d3 before this checkpoint; its Scientific checks run exposed a Linux-only script import failure corrected here.
- Exact next action: Complete official ACSCCD processing for only the 32 replication RAW files, verify every product, then execute the frozen replication summaries and screens; keep holdout arrays unopened.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
