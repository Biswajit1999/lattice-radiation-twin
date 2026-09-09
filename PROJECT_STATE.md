# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 4d - pinned official calibration experiment specified
- Completed milestones: Phases 0/2 and ingestion foundation pushed; 16 HST RAW files verified; eight-epoch paired-dark extraction and synthetic recovery executed. Calibrated phase-4 gate remains open.
- Current tests and status: 16 passed in 8.70s; Ruff passed.
- Known scientific risks: RAW native-DN selection spans commanded gains 1/2; reference bias and temperature unresolved; bootstrap excludes calibration uncertainty; sparse epochs cannot resolve event lags.
- Data successfully obtained: 16 HST RAW darks (566645760 bytes), committed MAST query snapshots, three production OMNI annual files (8619840 bytes).
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Operational HST temperature not yet reconstructed.
- Last successful commit SHA: 617f5c7496da08648dff6186cc3e2d892f900f71
- Last successful push: origin/main verified at 617f5c7496da08648dff6186cc3e2d892f900f71 before this checkpoint.
- Exact next action: Resolve reference plan under hst_1356.pmap, checkpoint, then retrieve and run ACSCCD on preserved RAW copies.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
