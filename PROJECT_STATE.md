# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 4b - acquisition size guard checked; metadata snapshots archived
- Completed milestones: phase 0 foundation and phase 2 literature audit pushed; strict provenance/download and temporal conversion tests implemented.
- Current tests and status: 16 passed in 1.76s; Ruff passed.
- Known scientific risks: radiation proxies are not physical dose; observational trap parameters may be unidentifiable; Gaia/Euclid calibration time series may not be public.
- Data successfully obtained: three OMNI annual pilot files (2003, 2014, 2023), checksum verified; production re-fetch under committed acquisition code pending.
- Data unavailable: HST images pending; MAST query returned 80 January 2023 dark records. Gaia/Euclid calibration series not located.
- Last successful commit SHA: 86af042d7346a09238be778a777cebaf57d1b34f
- Last successful push: origin/main verified at 86af042d7346a09238be778a777cebaf57d1b34f before this checkpoint.
- Exact next action: Resume RAW acquisition with 60 MB per-object bound (one listed object is 51.5 MB), then extract the frozen pilot.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
