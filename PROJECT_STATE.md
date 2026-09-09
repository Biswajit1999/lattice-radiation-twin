# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 3 - provenance ingestion foundation complete; mission acquisition pending
- Completed milestones: phase 0 foundation and phase 2 literature audit pushed; strict provenance/download and temporal conversion tests implemented.
- Current tests and status: 11 passed in 0.76s; Ruff passed.
- Known scientific risks: radiation proxies are not physical dose; observational trap parameters may be unidentifiable; Gaia/Euclid calibration time series may not be public.
- Data successfully obtained: three OMNI annual pilot files (2003, 2014, 2023), checksum verified; production re-fetch under committed acquisition code pending.
- Data unavailable: HST images pending; MAST query returned 80 January 2023 dark records. Gaia/Euclid calibration series not located.
- Last successful commit SHA: c727e287f5c098c12fb59145837f85d0d6043ff2
- Last successful push: origin/main verified at c727e287f5c098c12fb59145837f85d0d6043ff2 before this checkpoint.
- Exact next action: Reacquire OMNI with committed code and discover paired HST darks spanning the ACS baseline; checkpoint before bulk FITS download.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
