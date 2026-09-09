# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 4b - RAW cohort frozen before 567 MB acquisition
- Completed milestones: phase 0 foundation and phase 2 literature audit pushed; strict provenance/download and temporal conversion tests implemented.
- Current tests and status: 16 passed in 1.63s; Ruff passed.
- Known scientific risks: radiation proxies are not physical dose; observational trap parameters may be unidentifiable; Gaia/Euclid calibration time series may not be public.
- Data successfully obtained: three OMNI annual pilot files (2003, 2014, 2023), checksum verified; production re-fetch under committed acquisition code pending.
- Data unavailable: HST images pending; MAST query returned 80 January 2023 dark records. Gaia/Euclid calibration series not located.
- Last successful commit SHA: ed85c7c20e3d3e5b5e56b4a3e20fe2ef7e127492
- Last successful push: origin/main verified at ed85c7c20e3d3e5b5e56b4a3e20fe2ef7e127492 before this checkpoint.
- Exact next action: Download the pinned RAW cohort, run the pilot and evaluate calibration/controls before any latent model.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
