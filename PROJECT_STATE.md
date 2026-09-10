# LATTICE project state

- Current objective: establish an open, provenance-first cross-mission CCD radiation digital twin.
- Current phase: 5 - continuous measured environment and transparent mission-response proxies complete; baseline preregistration next
- Completed milestones: Phases 0/2 and ingestion foundation pushed; HST historical replication complete with the physical-inference gate closed; 2003–2025 OMNI activity, OMNI particle measurements, post-2020 SGPS channel products, threshold runs, rolling features and distinct HST/LEO and L2 proxy bases are checksum-linked and reproducible.
- Current tests and status: 31 passed in 2.98s; Ruff check passed and all files are formatted. Tests cover OMNI fills, both historical SGPS time schemas, masked validity counters, band integration, event/gap handling, archive-version selection and distinct mission bases.
- Known scientific risks: background/post-flash, gain and electronics conditions are strongly time-confounded; active temperature sensor and pixel dwell times unresolved; three selected pairs per historical epoch remain sparse; column bootstrap excludes calibration uncertainty; eight epochs cannot resolve event lags; OMNI particle contamination is unchecked; SGPS and OMNI lack calibration overlap; the physical-inference gate is closed.
- Data successfully obtained: 54 HST RAW darks (1923143040 bytes), 54 matched SPT files (3110400 bytes), 21 CRDS references (2229229440 bytes), committed MAST query snapshots, 23 OMNI annual files (66132672 bytes), and 1,883 GOES-R SGPS daily files (1045894251 bytes). Six August 2025 holdout RAW files are checksum-pinned but their FITS arrays remain unopened.
- Data unavailable: Gaia granular engineering CTI and Euclid trap-pumping series not located. Euclid Q1 pixels not yet fetched. Calibrated HST exposure-averaged temperature and clock dwell-time telemetry not established. OMNI energetic-proton flux ends on 2020-03-04; the standard SGPS archive begins in November 2020, with no empirical overlap for intercalibration.
- Last successful commit SHA: 6715a67b40984e80fca064733285856cd4482d5f
- Last successful push: origin/main verified at 6715a67b40984e80fca064733285856cd4482d5f before this checkpoint.
- Exact next action: Freeze B0–B5 forward-chaining metrics and failure thresholds against the 24 historical HST pairs and environment features before opening any August 2025 holdout pixel array.

State entries record the last completed commit before the current checkpoint; a commit cannot contain its own hash. The build ledger records phase transitions.
