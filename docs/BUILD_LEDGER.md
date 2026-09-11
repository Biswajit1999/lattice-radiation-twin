# Build ledger

## 2026-09-09 — Phase 0

Inspected parent workspace; unrelated projects are preserved. Parent Git repository has untracked work and no remote. GitHub CLI is authenticated as Biswajit1999. The target repository does not exist. The new repository inherits the existing Biswajit Jana Git author identity without changing configuration. Use `C:\Program Files\Git\cmd\git.exe` on this host: the bare `git` command resolves first to an unexpected system32 executable.

No scientific findings claimed. Foundation checks will be run before checkpoint.

Validation: Python 3.12.14, pytest 1 passed, Ruff check and format passed. The bundled Python runtime is used; system Anaconda is Python 3.9 and does not meet the contract.

## 2 - targeted primary-source novelty audit complete

docs: audit prior CTI radiation inference and constrain novelty claims

Validation: 1 passed in 0.02s; Ruff passed. Previous verified remote: `dd1c8fa724d55f8efde4d2ef1ac8cd5e375eaa33`. Next: Implement strict provenance and deterministic archive fetch commands before HST modelling.

## 3 - provenance ingestion foundation complete; mission acquisition pending

feat: add bounded checksum-pinned acquisition, MAST cohort discovery and CI

Validation: 11 passed in 0.76s; Ruff passed. Previous verified remote: `c727e287f5c098c12fb59145837f85d0d6043ff2`. Next: Reacquire OMNI with committed code and discover paired HST darks spanning the ACS baseline; checkpoint before bulk FITS download.

## 4a - HST cohort and synthetic extraction validation; real-data gate pending

feat: preregister paired-RAW HST extraction and verify synthetic trail controls

Validation: 16 passed in 1.57s; Ruff passed. Previous verified remote: `97f7e72d713ab4021f95b4f07c3f7ec9d2d07c63`. Next: Freeze RAW product plan and checkpoint before retrieving the full paired-dark pilot.

## 4b - RAW cohort frozen before 567 MB acquisition

feat: freeze 16 HST RAW products and provenance-linked longitudinal extraction

Validation: 16 passed in 1.63s; Ruff passed. Previous verified remote: `ed85c7c20e3d3e5b5e56b4a3e20fe2ef7e127492`. Next: Download the pinned RAW cohort, run the pilot and evaluate calibration/controls before any latent model.

## 4b - acquisition size guard checked; metadata snapshots archived

fix: preserve replayable MAST snapshots and strengthen UTC validation

Validation: 16 passed in 1.76s; Ruff passed. Previous verified remote: `86af042d7346a09238be778a777cebaf57d1b34f`. Next: Resume RAW acquisition with 60 MB per-object bound (one listed object is 51.5 MB), then extract the frozen pilot.

## 4c - RAW longitudinal pilot preserved; calibrated comparison next

feat: preserve observed HST pilot, controls, reproducible figures and methods draft

Validation: 16 passed in 22.61s; Ruff passed. Previous verified remote: `79102fe64a335ed998736b0c8263647d4663d716`. Next: Use the available Ubuntu WSL environment for pinned HSTCAL 3.2.0 and CRDS hst_1356.pmap reference calibration.

## 4d - pinned official calibration experiment specified

feat: specify official ACSCCD calibration and pinned CRDS reference discovery

Validation: 16 passed in 8.70s; Ruff passed. Previous verified remote: `617f5c7496da08648dff6186cc3e2d892f900f71`. Next: Resolve reference plan under hst_1356.pmap, checkpoint, then retrieve and run ACSCCD on preserved RAW copies.

## 4e - 17 CRDS references frozen before bulk calibration acquisition

feat: pin CRDS assignments and preserve official calibration execution receipts

Validation: 16 passed in 2.28s; Ruff passed. Previous verified remote: `21ebf6d7674e0a5f4477a87ae5f51251de8a4a43`. Next: Retrieve 17 bounded calibration references and run ACSCCD first on a single preserved RAW copy, then the cohort.

## 4f - calibration references acquired; HSTIO path handling repaired

fix: run HSTIO with relative paths and validate calibrated extraction masks

Validation: 18 passed in 1.58s; Ruff passed. Previous verified remote: `d3b84c3824842db99336846ee7db2c145485fe45`. Next: Repeat single-frame ACSCCD validation using relative filenames; retain the failed path-parsing log and then calibrate the full cohort.

## 4g - first official calibration validated; cohort calibration underway

feat: validate first official ACSCCD product and prepare matched telemetry acquisition

Validation: 18 passed in 1.71s; Ruff passed. Previous verified remote: `35573b09c4cedfcb0e7144c48fec45d766d114d4`. Next: Calibrate remaining RAW frames and retrieve matched SPT products; compare calibrated controls without replacing the RAW pilot.

## 4h - calibrated HST development cohort measured; physical-inference gate open

feat: complete calibrated HST development cohort

Validation: 20 passed in 1.82s; Ruff passed. Previous verified remote: `5996763da9de730dd2944d4556133bba65d0ee39`. Next: Freeze and acquire a replicated ACS/WFC dark cohort with background/electronics strata and an untouched temporal holdout.

## 4i - replicated HST cohort and August 2025 holdout frozen before acquisition

data: freeze replicated HST cohort and temporal holdout

Validation: 21 passed in 1.80s; Ruff passed. Previous verified remote: `32ddc11ee956282e708d43986a9b96d2fde1c9d4`. Next: Download and checksum-verify the 32 replication and six holdout RAW/SPT products without opening holdout pixels.

## 4j - replicated HST cohort acquired; August 2025 pixels remain sealed

data: acquire replicated HST cohort and preserve provenance bytes

Validation: 21 passed in 1.78s; Ruff passed. Previous verified remote: `600f02ab0d3af65ff5a319f44c25da58fe66ec6f`. Next: Resolve pinned CRDS assignments and calibrate only the 32 replication RAW files; keep all six holdout pixel arrays unopened.

## 4k - replication-only CRDS assignments frozen; four bias references pending

feat: freeze replication-only ACS calibration plan

Validation: 22 passed in 1.68s; Ruff passed. Previous verified remote: `92884ea77fd0e56399edf768868f1a18115771e2`. Next: Download and verify the four missing pinned bias references, then calibrate only the 32 replication RAW files; keep holdout arrays unopened.

## 4l - all replication CRDS references verified; 32-frame calibration pending

data: acquire replication bias references

Validation: 22 passed in 1.64s; Ruff passed. Previous verified remote: `23163670ced8b2df8a4bfd79b76a11f23659d8d6`. Next: Run official ACSCCD on only the 32 replication RAW files with the pinned context and references; keep holdout arrays unopened.

## 4m - replication analysis and familywise control screen frozen

feat: freeze replicated HST outcome screens

Validation: 22 passed in 28.76s under concurrent calibration I/O; Ruff passed. The original 16-product calibration receipt remained independently verifiable. Previous verified remote: `8c3f004a5104668e4eced616903177de06e63e2a`. Next: Complete and verify the 32 replication calibrations, then run the frozen pair-stratified directional and Bonferroni blank-control screens without opening the six holdout arrays.

## 4n - replication engineering-state join frozen

feat: freeze replication nuisance summary

Validation: 24 passed in 5.96s; Ruff passed. Previous verified remote: `f11e2de00d17d3707a0eba72541d0126cf481388`. Next: Complete and verify the 32 replication calibrations, then join the outcome to literal background, gain, post-flash and engineering-channel state without treating the descriptive correlations as causal.

Clean Linux CI for this checkpoint exposed that tests could import the top-level `scripts` namespace on Windows but not in the packaged runner. The tested slope and rank-correlation functions were moved into `src/lattice/replication.py`; 24 local tests and Ruff then passed before the corrective push.

Before outcome extraction, the replication plot labels were made explicit and every generated replication summary was linked to the exact `HST_REPLICATION_PROTOCOL.md` bytes. Clean Linux Scientific checks passed at `835f9c103a2c3a83e102aae2094547da34311d85` before this provenance correction.

## 4o - independent HST historical replication completed

science: replicate calibrated HST longitudinal observable

Validation: 25 passed in 3.32s; Ruff passed. All 32 replication BLV products, 21 unique references, source objects, logs, headers, gains and correction states verified. Four pair-by-chip slopes passed the frozen positive-direction screen and zero of 32 simultaneous blank controls failed; the physical-inference gate remains closed because operating state and background are time-confounded. A workstation sleep interrupted one unregistered derived frame; the exact cache artifact was verified, removed and deterministically regenerated after the runner revalidated 27 receipts. Previous verified remote: `fe25d0958f9d675599a27fdb3140bf9331c01dfb`. Next: Build continuous measured environment features and transparent, mission-specific exposure proxies without opening the six temporal-holdout arrays.

## 5a - continuous environment acquisition and parser contract frozen

feat: freeze continuous OMNI and GOES-R exposure inputs

Validation: 29 passed in 3.18s; Ruff passed. The plan covers 23 complete OMNI years and 1,883 available GOES-R SGPS days. Sixty-two monthly NOAA listings are checksum-preserved; ten pre-November 2020 GOES-16 directories, four missing March 2021 days and 23 superseded daily versions remain explicit exclusions. The SGPS >10 MeV derivation requires complete contributing bands; distinct HST/LEO and Gaia/Euclid L2 response bases remain labelled proxies. Previous verified remote: `3fa03aeedcddef3bd8d833d6cbe0c1c2edbc15a1`. Next: Bulk-retrieve and checksum-pin the frozen plans before aggregation; keep the HST holdout sealed.

## 5b - continuous environment and transparent exposure proxies complete

science: build verified continuous environment and mission proxy layer

Validation: 31 passed in 2.98s; Ruff check and formatting passed. All 23 OMNI annual objects and 1,883 SGPS daily objects verified against committed receipts. The result contains 276 months, 118 observed OMNI threshold runs and 196 SGPS proxy threshold runs. Fourteen particle months remain explicit gaps. The parser supports 536 historical and 1,347 current time-coordinate files and treats masked validity counters as invalid. OMNI/SGPS cumulative fluences remain separate because there is no empirical overlap. Previous verified remote: `6715a67b40984e80fca064733285856cd4482d5f`. Next: Preregister and benchmark B0–B5 with forward-chaining validation before opening the six temporal-holdout arrays.

## 6a - historical baseline benchmark preregistered before execution

feat: freeze forward-chaining B0–B5 benchmark

Validation: 33 passed in 2.92s; Ruff check and formatting passed. The protocol fixes four expanding whole-epoch folds, training-only scaling, B0–B5 definitions, Gaussian predictive scores, an exposure-support screen and future advanced-model thresholds. Event and subthreshold cumulative fluence fields were added deterministically to the verified monthly exposure product. The historical benchmark has not been executed, and the temporal-holdout pixels remain unopened. Previous verified remote: `ea902773ffeef8bf7235d9b93058c6b90734e9dc`. Next: Run the frozen benchmark on only the 32 historical replication summaries and inspect the result.

## 6b - historical B0–B5 benchmark complete

science: benchmark historical exposure proxies against calendar time

Validation: all six models produced 16 finite forward predictions; 33 tests passed in 3.07s and Ruff check/formatting passed. B0 calendar-linear has the lowest RMSE (0.04024). B4 event-plus-background has lower mean NLPD but RMSE 0.04055, so B3/B4 do not beat B0 on both preregistered metrics. The exposure-support screen fails and the physical-inference gate remains closed. Previous verified remote: `2c70aa5ddf681d1e0569b2055f6ff1dc7ca73506`. Next: Freeze the core latent-state model and its identifiability/failure rules without using the temporal holdout.

## 7a - core latent-state protocol frozen

docs: freeze core latent-state and synthetic recovery gates

Validation: 33 passed in 3.28s; Ruff check and formatting passed. The exact linear-Gaussian transition, mission-specific response rule, initial HST observation equation, priors, identifiability constraints, ablations, lag grid, prior/predictive checks and 100-replicate synthetic recovery thresholds are fixed before implementation. NumPy/SciPy exact Gaussian inference was selected because PyMC, JAX and NumPyro are absent from the tested environment. No observational latent-state fit or holdout access occurred. Previous verified remote: `7b60f4116860bb291e8a884ba9c411bf5c64623b`. Next: Implement and test the synthetic recovery gate.

## 7b - exact Gaussian state-space engine frozen before recovery batch

feat: implement exact state-space recovery engine

Validation: 37 passed in 7.30s; Ruff check and formatting passed. The implementation exposes the two-chip transition, pair-specific observation offsets, exact Kalman likelihood, RTS smoother, constrained MAP objective, observation-derived initialization, finite-difference Laplace covariance, prior predictive simulation, predictive coverage and SBC ranks. A 48-epoch single-replicate dry run succeeded; the 100-replicate result has not been observed. Previous verified remote: `2d97f8a605b6cc1a29d53847379d4ca78a794493`. Next: Execute the frozen 100-replicate recovery batch and retain the result whether it passes or fails.

## 7c - first frozen synthetic recovery gate failed and retained

science: retain failed synthetic recovery gate

Validation: 37 tests passed in 8.11s; Ruff check and formatting passed; all stored
provenance hashes and result invariants matched. The 100-replicate batch produced
100 optimizer successes, 0.9256 overall 95%
Laplace interval coverage, 0.9380/0.9743 posterior-predictive coverage and 0.2808
median standardized ensemble bias. It nevertheless failed the frozen gate:
latent-state RMSE was 0.01721 against a 0.0100 threshold; 34.50% of prior-predictive
values fell outside [-0.25, 0.75]; and SBC ranks failed for annealing and process
scale. The thresholds were not changed, no observational model was fit, and the
temporal-holdout arrays remained unopened. Previous verified remote:
`bdc0ca1ae4ba9cc67c7253ed701471fe6c3c742b`. Next: run the four frozen synthetic
ablations, then version any revised prior or reparameterization before rerunning
recovery.

## 7d - paired synthetic ablations frozen before execution

feat: freeze exact-zero state-space ablations

Validation: 42 tests passed in 12.44s; Ruff check and formatting passed. The
diagnostic plan fixes the same 100 seeds and full-model fits as the retained
failed batch. The implementation removes annealing, event response, continuous
background response and process noise separately from both optimization and prior
penalty, then reports paired likelihood, AIC/BIC, latent RMSE and observation RMSE.
No new pass threshold is introduced. Exact-zero unit tests and one four-model
smoke fit passed. Previous verified remote:
`5b761e0e584785a78ef546773b685f6e2de8485f`. Next: execute and retain all 400
paired reduced-model fits without using observational outcomes or holdout pixels.

## 7e - paired synthetic ablations complete

science: diagnose failed state-space recovery with paired ablations

Validation: 42 tests passed in 14.93s; Ruff check and formatting passed; all five
stored provenance hashes and ablation result invariants matched. All 400
reduced-model optimizations succeeded. Removing event response produced
median paired delta BIC 68.86 and latent-RMSE ratio 1.281; background removal gave
28.26 and 1.099. Annealing removal gave delta BIC 12.77 but a variable RMSE ratio
whose interquartile range crossed one. Process-noise removal gave the weakest
median delta BIC, 9.80, positive in 75% of datasets, while raising median latent
RMSE by 33.5%. These simulated diagnostics do not change the failed recovery or
physical-inference gates. Previous verified remote:
`c0690a82cd6ac77fe82247ff32060c022d4b7fd9`. Next: freeze a versioned prior and
identifiability revision before another synthetic recovery batch.

## 7f - v2 identifiability and prior revision frozen

docs: freeze core model v2 recovery protocol

Validation: 42 tests passed in 25.05s; Ruff check and formatting passed. The v2
protocol retains event/background structure, anchors the first pair offset
at exact zero, and replaces broad half-normal accumulation/annealing priors with
explicit log-scale priors. A disclosed 2,000-draw prior-design exploration placed
0.0818% of selected-candidate values outside the plausibility interval. New
recovery and prior-predictive seeds are fixed, while every v1 recovery threshold
is preserved. No v2 implementation or recovery result exists at this checkpoint.
Previous verified remote: `69a9f872c501c49d6fe0b1257a17e7725eb2ee04`.
Next: implement and unit-test v2, then checkpoint before its 100-replicate run.

## 7f1 - canonical SBC requirement corrected before v2 execution

docs: require prior-drawn simulation-based calibration

The v1 batch ranked one fixed truth across repeated datasets. That is a useful
repeated-sampling calibration diagnostic but not canonical SBC. Before any v2
batch, the protocol was corrected to add a separate 100-replicate experiment in
which all eight truths are drawn from the v2 prior. Its truth/data and posterior
seeds are frozen, and at least 95 optimizations plus every existing rank-uniformity
threshold must pass. Previous verified remote:
`8930586720eb764e1d24861d88e576581a4dc061`. Next: complete the v2 implementation
and checkpoint it before either the fixed-truth recovery or prior-drawn SBC run.

## 7g - v2 engine and canonical SBC harness frozen before batch

feat: implement reference-anchored v2 recovery

Validation: 46 tests passed in 16.04s; Ruff check and formatting passed. V2 is
implemented separately from the retained v1 source. A complete fixed-truth smoke
replicate and a prior-drawn SBC smoke replicate converged. The frozen 1,000-draw
prior check produced zero values outside the allowed interval. The production
command will perform 100 fixed-truth recovery fits and 100 separate prior-drawn
SBC fits; neither batch has run at this checkpoint. Previous verified remote:
`9486d6dc02cb35f558266fc29b4b52ea1c2e74a4`. Next: execute both frozen batches,
retain the result, and leave observational/holdout data unused.

## 7h - v2 recovery improves state estimation but fails process-scale SBC

science: retain failed v2 process-scale calibration

Validation: 46 tests passed in 28.29s; Ruff check and formatting passed; all five
stored provenance hashes and v2 result invariants matched. Both 100-replicate
populations completed with 100 optimizer successes. V2 passed
prior plausibility, aggregate 95% coverage (0.9075), median standardized bias
(0.3075), latent RMSE (0.00808) and 90%/95% predictive coverage
(0.9350/0.9720). Canonical prior-drawn SBC failed only for process scale with
p=6.40e-8. Its fixed-truth mean was 0.00635 for truth 0.008 and its interval
coverage was 0.82. The v2 gate therefore failed; no observational fit or holdout
access occurred. Previous verified remote:
`24b76ea1dab4d54e0bf551589ed45482bdfbe8f3`. Next: freeze an inference change for
the skewed process-scale posterior before further recovery.
