# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 5a - continuous OMNI and post-2020 GOES-R SGPS acquisition plans frozen
- Completed milestones: Phases 0/2 and ingestion foundation pushed; HST historical replication complete with the physical-inference gate closed; continuous 2003–2025 OMNI and daily GOES-R SGPS plans, parsers and distinct LEO/L2 proxy bases implemented before bulk retrieval.
- Current tests and status: 29 passed in 3.18s; Ruff passed. OMNI fill handling, SGPS band integration/completeness, numeric archive-version selection and distinct mission basis terms have compact tests.
- Known scientific risks: background/post-flash, gain and electronics conditions are strongly time-confounded; active temperature sensor and pixel dwell times unresolved; three selected pairs per historical epoch remain sparse; column bootstrap excludes calibration uncertainty; eight epochs cannot resolve event lags; the physical-inference gate is closed.
- Data successfully obtained: 54 HST RAW darks (1923143040 bytes), 54 matched SPT files (3110400 bytes), 21 CRDS references (2229229440 bytes), committed MAST query snapshots, and three production OMNI annual files (8619840 bytes). Six August 2025 holdout RAW files are checksum-pinned but their FITS arrays remain unopened.
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Calibrated HST exposure-averaged temperature and clock dwell-time telemetry not established. OMNI energetic-proton flux ends in 2020; a later source is required.
- Last successful commit SHA: 3fa03aeedcddef3bd8d833d6cbe0c1c2edbc15a1
- Last successful push: origin/main verified at 3fa03aeedcddef3bd8d833d6cbe0c1c2edbc15a1 before this checkpoint.
- Exact next action: Retrieve and checksum-pin the frozen 23-file OMNI plan and 1,883-file SGPS plan, then aggregate measured environment and proxy bases without opening the six HST temporal-holdout arrays.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
