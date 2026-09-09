# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 4a - HST cohort and synthetic extraction validation; real-data gate pending
- Completed milestones: phase 0 foundation and phase 2 literature audit pushed; strict provenance/download and temporal conversion tests implemented.
- Current tests and status: 16 passed in 1.57s; Ruff passed.
- Known scientific risks: radiation proxies are not physical dose; observational trap parameters may be unidentifiable; Gaia/Euclid calibration time series may not be public.
- Data successfully obtained: three OMNI annual pilot files (2003, 2014, 2023), checksum verified; production re-fetch under committed acquisition code pending.
- Data unavailable: HST images pending; MAST query returned 80 January 2023 dark records. Gaia/Euclid calibration series not located.
- Last successful commit SHA: 97f7e72d713ab4021f95b4f07c3f7ec9d2d07c63
- Last successful push: origin/main verified at 97f7e72d713ab4021f95b4f07c3f7ec9d2d07c63 before this checkpoint.
- Exact next action: Freeze RAW product plan and checkpoint before retrieving the full paired-dark pilot.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
