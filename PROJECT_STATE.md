# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 4c - RAW longitudinal pilot preserved; calibrated comparison next
- Completed milestones: Phases 0/2 and ingestion foundation pushed; 16 HST RAW files verified; eight-epoch paired-dark extraction and synthetic recovery executed. Calibrated phase-4 gate remains open.
- Current tests and status: 16 passed in 22.61s; Ruff passed.
- Known scientific risks: RAW native-DN selection spans commanded gains 1/2; reference bias and temperature unresolved; bootstrap excludes calibration uncertainty; sparse epochs cannot resolve event lags.
- Data successfully obtained: 16 HST RAW darks (566645760 bytes), committed MAST query snapshots, three production OMNI annual files (8619840 bytes).
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Operational HST temperature not yet reconstructed.
- Last successful commit SHA: 79102fe64a335ed998736b0c8263647d4663d716
- Last successful push: origin/main verified at 79102fe64a335ed998736b0c8263647d4663d716 before this checkpoint.
- Exact next action: Use the available Ubuntu WSL environment for pinned HSTCAL 3.2.0 and CRDS hst_1356.pmap reference calibration.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
