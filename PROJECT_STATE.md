# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 7m - historical state-space validation harness implemented before execution
- Completed milestones: Phases 0/2 and ingestion foundation pushed; HST replication, environment layer and B0–B5 benchmark complete; v1 recovery/ablations and v2 recovery/SBC failures retained; v3 heavy-tailed exact-posterior inference passes every frozen synthetic gate; observational whole-epoch validation rules and implementation are complete.
- Current tests and status: 59 tests passed in 18.18s; Ruff check and formatting passed. All 24 real-input fold/sensitivity builds pass role, temporal-cutoff and coverage validation without fitting outcomes. Synthetic full, zero-event and zero-process smoke fits produce finite posterior forecasts. No observational state-space posterior has run at this checkpoint.
- Known scientific risks: fixed-truth drift and process-scale rank histograms remain nonuniform diagnostics despite passing canonical SBC; background/post-flash, gain and electronics conditions are strongly time-confounded; active temperature sensor and pixel dwell times unresolved; three selected pairs per historical epoch remain sparse; column bootstrap excludes calibration uncertainty; eight epochs cannot resolve event lags; OMNI particle contamination is unchecked; SGPS and OMNI lack calibration overlap; the physical-inference gate is closed.
- Data successfully obtained: 54 HST RAW darks (1923143040 bytes), 54 matched SPT files (3110400 bytes), 21 CRDS references (2229229440 bytes), committed MAST query snapshots, 23 OMNI annual files (66132672 bytes), and 1,883 GOES-R SGPS daily files (1045894251 bytes). Six August 2025 holdout RAW files are checksum-pinned but their FITS arrays remain unopened.
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Calibrated HST exposure-averaged temperature and clock dwell-time telemetry not established. OMNI energetic-proton flux ends on 2020-03-04; the standard SGPS archive begins in November 2020, with no empirical overlap for intercalibration.
- Last successful commit SHA: 537840eb31b7a3d21f07b11a0751e0ecab5ed28a
- Last successful push: origin/main verified at 537840eb31b7a3d21f07b11a0751e0ecab5ed28a before this checkpoint.
- Exact next action: execute the frozen historical primary model, exact-zero ablations and lag/proxy sensitivities; retain every failed gate and leave the temporal holdout sealed.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
