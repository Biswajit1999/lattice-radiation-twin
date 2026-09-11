# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 7g - separate v2 engine and dual recovery/SBC harness implemented before batch execution
- Completed milestones: Phases 0/2 and ingestion foundation pushed; HST replication, environment layer and B0–B5 benchmark complete; core v1 recovery failure and all 400 paired ablations retained; v2 reference-anchored engine, fixed-truth recovery and separate prior-drawn SBC harness implemented.
- Current tests and status: 46 tests passed in 16.04s; Ruff check and formatting passed. One complete v2 fixed-truth recovery and one prior-drawn SBC smoke replicate converged. The frozen 1,000-draw v2 prior check placed 0% of 192,000 values outside range. The two 100-replicate batches have not run; observational fitting remains prohibited.
- Known scientific risks: the first priors are too broad for the trail-fraction scale; annealing and process noise show recovery/calibration problems; latent trajectories are not recovered accurately enough; background/post-flash, gain and electronics conditions are strongly time-confounded; active temperature sensor and pixel dwell times unresolved; three selected pairs per historical epoch remain sparse; column bootstrap excludes calibration uncertainty; eight epochs cannot resolve event lags; OMNI particle contamination is unchecked; SGPS and OMNI lack calibration overlap; the physical-inference gate is closed.
- Data successfully obtained: 54 HST RAW darks (1923143040 bytes), 54 matched SPT files (3110400 bytes), 21 CRDS references (2229229440 bytes), committed MAST query snapshots, 23 OMNI annual files (66132672 bytes), and 1,883 GOES-R SGPS daily files (1045894251 bytes). Six August 2025 holdout RAW files are checksum-pinned but their FITS arrays remain unopened.
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Calibrated HST exposure-averaged temperature and clock dwell-time telemetry not established. OMNI energetic-proton flux ends on 2020-03-04; the standard SGPS archive begins in November 2020, with no empirical overlap for intercalibration.
- Last successful commit SHA: 9486d6dc02cb35f558266fc29b4b52ea1c2e74a4
- Last successful push: origin/main verified at 9486d6dc02cb35f558266fc29b4b52ea1c2e74a4 before this checkpoint.
- Exact next action: run the frozen 100 fixed-truth v2 recoveries and 100 prior-drawn SBC replicates, retain every failed gate, and do not fit observational outcomes or open the holdout.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
