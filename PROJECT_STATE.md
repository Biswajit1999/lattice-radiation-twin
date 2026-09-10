# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 4o - HST historical replication complete; physical-inference gate remains closed
- Completed milestones: Phases 0/2 and ingestion foundation pushed; 54 HST RAW/SPT files acquired with six holdout arrays sealed; 48 historical frames calibrated with official ACSCCD; independent pair-separated replication, familywise blank controls, engineering-state join and development comparison executed.
- Current tests and status: 25 passed in 3.32s; Ruff passed. All 32 replication products and 21 unique reference objects pass full hash/header verification; the latest clean Linux Scientific checks passed before result generation.
- Known scientific risks: background/post-flash, gain and electronics conditions are strongly time-confounded; active temperature sensor and pixel dwell times unresolved; three selected pairs per historical epoch remain sparse; column bootstrap excludes calibration uncertainty; eight epochs cannot resolve event lags; the physical-inference gate is closed.
- Data successfully obtained: 54 HST RAW darks (1923143040 bytes), 54 matched SPT files (3110400 bytes), 21 CRDS references (2229229440 bytes), committed MAST query snapshots, and three production OMNI annual files (8619840 bytes). Six August 2025 holdout RAW files are checksum-pinned but their FITS arrays remain unopened.
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Calibrated HST exposure-averaged temperature and clock dwell-time telemetry not established. OMNI energetic-proton flux ends in 2020; a later source is required.
- Last successful commit SHA: fe25d0958f9d675599a27fdb3140bf9331c01dfb
- Last successful push: origin/main and clean Linux Scientific checks verified at fe25d0958f9d675599a27fdb3140bf9331c01dfb before this checkpoint.
- Exact next action: Build the continuous measured space-environment timeline and transparent mission-specific exposure proxies, without opening the six HST temporal-holdout arrays.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
