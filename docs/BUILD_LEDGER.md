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

## 7i - v3 exact-likelihood posterior inference frozen

docs: freeze elliptical-slice v3 inference protocol

Validation: 46 tests passed in 28.29s; Ruff check and formatting passed. V3
changes inference only: the v2 model, priors and truth remain fixed. The
protocol replaces MAP-centered Laplace draws with two-chain elliptical slice
sampling in the Gaussian transformed-prior coordinates. It freezes burn-in,
draws, seeds, rank-normalized R-hat, bulk ESS, posterior state-mixture rules and
the unchanged recovery/SBC thresholds. A host benchmark measured 5.75 ms per
48-epoch likelihood evaluation. No sampler implementation or v3 result exists at
this checkpoint. Previous verified remote:
`ec8d04f56c002bfbe9cfc032e1e474e5f2db4d1f`. Next: implement and validate the
sampler before checkpointing the long synthetic run.

## 7i1 - v3 sampler choice corrected after mixing smoke tests

docs: replace poorly mixing elliptical slice proposal

A two-chain state-space smoke run showed that full-vector elliptical slice
sampling mixed poorly (process-scale R-hat 1.98, bulk ESS 2.8). A
Laplace-preconditioned Metropolis smoke run reduced maximum R-hat to 1.068 and
raised minimum bulk ESS to 52 with 1,000 retained draws per chain and sampling
acceptance 0.195/0.238. Before production, the protocol was amended to freeze
750 burn-in and 2,000 retained draws per chain. Laplace is proposal geometry only;
exact posterior acceptance remains decisive. Previous verified remote:
`858759b7ab4521b4ed44a637618d5bf04802e3de`. Next: complete the sampler and
posterior-mixture implementation, test it, and checkpoint before the long run.

## 7i2 - heavy-tailed independence sampler selected before production

docs: freeze heavy-tailed v3 independence sampling

The full-budget random-walk smoke still failed chain usability (maximum R-hat
1.072, minimum ESS 47). A multivariate t5 independence proposal centered on the
MAP and scaled to 0.8 of the Laplace geometry achieved acceptance 0.401/0.368,
maximum R-hat 1.0125 and minimum ESS 302 with the frozen 2,000 draws per chain.
The protocol now fixes 100 discarded iterations, no production adaptation, and
the exact proposal-density correction. Previous verified remote:
`2e1e07c017871ee1f184262ae17e10ba2d97c3a1`. Next: finish and test the production
harness, then checkpoint before the long run.

## 7j - v3 exact-posterior recovery harness implemented

feat: implement heavy-tailed posterior recovery

Validation: 54 tests passed in 29.94s; Ruff check and formatting passed. The
reusable sampler passes correlated-Gaussian recovery, determinism and chain-
diagnostic tests. One complete fixed-truth production-budget dataset passed chain
usability with maximum R-hat 1.0123 and minimum ESS 328; one prior-drawn dataset
passed with maximum R-hat 1.0057 and minimum ESS 516. The harness combines 64
posterior smoothers for latent and predictive uncertainty, retains compact chain
diagnostics, and emits progress every ten datasets. Neither 100-replicate
population has run at this checkpoint. Previous verified remote:
`52081ad426ed744567a956f688f60204fd8f0c18`. Next: run and retain both frozen
synthetic populations without observational or holdout access.

## 7k - v3 synthetic recovery and canonical SBC pass

science: validate v3 synthetic posterior recovery

The frozen production command completed 100 fixed-truth and 100 prior-drawn SBC
datasets. Both populations retained 99/100 usable-chain results, above the
95/100 threshold. Overall 95% interval coverage is 0.9688, median absolute
standardized ensemble bias is 0.2694, latent-state RMSE is 0.00797, and 90%/95%
predictive coverage is 0.9444/0.9768. All eight canonical SBC rank checks pass;
process-scale uniformity improves from p=6.40e-8 in v2 to p=0.9114 in v3. All
five stored provenance hashes match. Fixed-truth drift and process-scale rank
histograms remain flagged diagnostics. No observational posterior was fitted and
no temporal-holdout pixel array was opened. Previous verified remote:
`dc1a08eafdf77fb8e87d36a4a2aaa49488cc9ff8`. Next: freeze v3 exact-zero
ablations, lag/proxy sensitivity and whole-epoch forward validation before
observational inference.

## 7l - historical state-space validation contract frozen

docs: freeze historical state-space validation

The observational contract fixes the 32 replication-only summaries, complete
pre-epoch environment months, HST-specific background/event proxies, four
whole-epoch forward folds and the numerical advanced-model thresholds inherited
from B0–B5. It also preregisters four exact-zero fits, three event lags, two
proxy substitutions, sampler usability rules and a separate exposure-attribution
robustness classification. No model or alternative may be selected after seeing
the scores. The six August 2025 holdout arrays remain unopened. Previous verified
remote: `84da01d6b48b9d1038884ba4c0f938b14330e6ef`. Next: implement and test the
frozen joining, fitting and forecast harness before any observational execution.

## 7m - historical state-space validation harness implemented

feat: implement historical state-space validation

Validation: 59 tests passed in 18.18s; Ruff check and formatting passed. The new
module rejects non-replication outcomes, constructs complete-month exposure
intervals, applies training-fold-only standardization, supports exact-zero
transition terms and generates deterministic mixture forecasts. All 24 real-
input fold/sensitivity specifications pass schema, cutoff and minimum-coverage
validation without posterior fitting. Synthetic full, zero-event and zero-
process smoke fits converge and produce finite forecasts. The production script
scores the primary model, four ablations and five fixed sensitivities and records
nine provenance hashes. No observational state-space posterior has run. Previous
verified remote: `537840eb31b7a3d21f07b11a0751e0ecab5ed28a`. Next: checkpoint this
implementation, then execute the frozen observational experiment once while
keeping the temporal holdout sealed.

## 7n - historical state-space forecast and attribution fail

science: retain failed historical state-space validation

All 40 preregistered fits completed. H0 has usable chains in all four folds and
16 finite forecasts, with 1.000 interval coverage, but fails RMSE (0.04977 versus
0.03823 maximum) and mean negative log predictive density (-1.6480 versus below
-1.7824). The exact-zero event model improves both scores to 0.03527 and -1.9286;
the exact-zero background model also improves both scores but has one low-ESS
fold. The inverse-sunspot sensitivity has attractive descriptive scores but two
unusable folds and cannot replace H0. Every failed gate and all nine matching
provenance hashes are retained. No temporal-holdout pixel was opened. Previous
verified remote: `5baecf45205dc31f58129aac138f8b19c9d0a1c7`. Next: publish this failed
result, then begin the Gaia public-data availability and external-validation
audit without tuning H0.

## 8 - Gaia public-data and literature validation bounded

science: audit Gaia CTI validation availability

A live official Gaia TAP schema query returned 248 tables and no exact CTI,
charge-injection, calibration or engineering table. Seven constraints explicitly
stated by Pagani et al. are stored as published narrative/table evidence; no plot
was digitised. The local shared L2 SEP proxy marks September 2017 as an event and
ranks it 7/200 among OMNI months, consistent with the published event timing but
not a Gaia dose or CTI-amplitude validation. The requested direct quantitative
Gaia comparison and HST-versus-L2 model score are blocked by unavailable public
engineering measurements. Previous verified remote:
`908b3f2934660230eaf938bedb0e9b833901495a`. Next: verify current Euclid Q1 VIS
and trap-pumping availability before a transfer experiment.

## 9a - Euclid public-data boundary verified

science: audit Euclid Q1 transfer inputs

A live official Euclid TAP query returned 103 tables, 836 calibrated VIS
quad-frame records and 1,112 raw VIS records. Thirty-six parallel trap-pumping
raw frames map to 1,296 detector records, with 36 CCDs per acquisition; an
80-byte request verified the first product's FITS signature without downloading
the full file. The official Q1 release matrix explicitly withholds processed
trap-result, trap-model, CTI-calibration and CTI time-evolution products. Q2 is
current but advertises imaging, astrometry and photometry rather than trap
products. Previous verified remote:
`e81fa5f33e87d4d50026a0df6d0088b07483d9d4`. Next: run a bounded,
mission-specific Euclid forward simulation with damage amplitude kept simulated.

## 9b - Euclid conditional-transfer protocol frozen

science: freeze Euclid transfer gates

The mission-specific forward experiment is fixed before execution. It uses the
published 153 K operating point, 14.3 microsecond serial transfer, 4.02
millisecond parallel transfer, 4096 x 4132 pixel geometry and two approximate
published emission-time features. Fixed scenario grids cover trap-timescale
sensitivity, mixture weight, captured fraction and transfer distance. Charge
conservation, causality, timing preservation and claim-boundary gates are set in
advance. HST and Gaia fitted amplitudes are forbidden inputs. Previous verified
remote: `4bf0fb04b953e65bfb77b92c2bfa815c3f8ee22e`. Next: implement and run the
frozen grid.

## 9c - Euclid conditional transfer executed

science: run Euclid conditional charge transfer

The frozen grid completed 810 mission-specific serial and parallel release
scenarios. All numerical gates pass: maximum kernel mass error is 3.33e-16 and
maximum relative propagated-charge error is 7.28e-16. At the published parallel
timing, the conditional mean release lags are about 1.000 pixels for the 220
microsecond feature and 5.492 pixels for the 20 millisecond feature. The result
is explicitly a scenario envelope. It does not estimate trap density, damage
amplitude, species mixture, posterior uncertainty or a calendar trajectory.
Previous verified remote: `b48f71411bb944d1daf58754005eab03494330fb`.
Next: propagate the fixed scenarios into image-domain science-bias diagnostics.

## 10a - Conditional science-bias protocol frozen

science: freeze Euclid image-bias gates

The first image-domain experiment is fixed before execution. It uses analytic
Euclid-scale point sources and faint galaxies, a published-scale PSF and read
noise, fixed backgrounds, transfer positions, captured fractions, species
mixtures and timescale sensitivities. Thirty-two paired noise fields define
measurement intervals. Flux, centroid, ellipticity, size and ring-test shear
response metrics and numerical gates are frozen. ArCTIc 2.6 was checked but
cannot build on this Windows/Python 3.12 host without Microsoft C++ Build Tools;
it is not added as a broken dependency. Previous verified remote:
`fbc9d0866b9f9e667ed2bc3fd45b44046037b4c0`. Next: implement the frozen
conditional experiment using the verified Phase 9 kernel.

## 10b - Conditional science-bias measurement gate fails

science: retain failed Euclid image-bias gate

The frozen run completed 432 source scenarios with 32 paired noise fields each
and 54 noiseless ring-test scenarios. Charge conservation, zero capture,
directionality, x-axis control, interval ordering and claim-boundary gates pass.
The fixed unweighted estimator retains only 8/32 valid pairs in the worst case;
369/432 scenarios miss the 30/32 threshold. The implementation gate fails, and
the unstable low-signal morphology intervals are retained without tuning or
promotion. Previous verified remote:
`c2bd7628b8f6ff240993210a7334a31f3d957706`. Next: specify a separately frozen
weighted-moment follow-up while preserving this failure.

## 10c - Weighted science-bias follow-up frozen

science: freeze weighted image-bias gates

The follow-up is versioned separately after the Phase 10a failure. It preserves
the image population, scenario grid, noise realisations and claim boundaries,
but fixes a non-adaptive circular Gaussian weight with sigma 3 pixels before
implementation. Valid-pair, finiteness, grid-size, zero-capture, directionality
and predecessor-integrity gates are preregistered. Previous verified remote:
`be2c992de49692d9a0aeaff0eae3012ac89ba42b`. Next: implement and execute the
weighted experiment without modifying the failed predecessor.

## 10d - Weighted science-bias measurement gate fails

science: retain failed weighted image-bias gate

The fixed 3-pixel Gaussian weight improves the minimum paired-measurement count
from 8/32 to 23/32 and reduces scenarios below the threshold from 369/432 to
42/432, but does not pass the frozen 30/32 requirement. All other gates pass,
including predecessor-integrity, finite outputs, exact grid size, conservation,
zero capture, directionality and claim boundaries. The output is retained as a
second failed experiment without changing the weight after inspection. Previous
verified remote: `93977be7e23a61c93f6c9a223c57874349664d7f`. Next: preregister a
model-fit or forced-measurement estimator as a distinct experiment.

## 10e - Forced-response science-bias protocol frozen

science: freeze forced-response bias gates

The third image-domain experiment replaces noisy ratio estimators with fixed-
template linearized response statistics. Its analytic pristine template supplies
all denominators, while the scenario population, paired fields and fixed weight
remain unchanged. Complete finite grids, conservation, zero capture,
directionality, predecessor-integrity and claim-boundary gates are fixed before
implementation. Previous verified remote:
`d020ff3c0fc439b0d52f3c54b36f94e7b48d91f5`. Next: implement and execute the
forced-response grid without modifying either retained failure.

## 10f - Forced-response science-bias implementation passes

science: run forced-response bias grid

All 432 source scenarios retain 32/32 finite paired responses, all 54 ring
scenarios are finite, and every frozen implementation gate passes. Maximum
relative charge-conservation error is 4.55e-16; zero-capture and x-control
responses are zero; y response is positive and monotonic; and both predecessor
experiments remain byte-identical. The result validates controlled fixed-template
response computation only. Captured fractions are not observed, posterior
uncertainty is unavailable, and HST/Gaia science propagation remains blocked.
Previous verified remote: `319a862913ac46e4cf81648b4794d87c7de7764d`.
Next: preregister the comprehensive falsification suite.

## 11a - Comprehensive falsification matrix frozen

science: freeze falsification matrix

Twelve requested tests are specified with deterministic transformations, seeds,
metrics and pass rules. Existing baseline and state-space consolidations are
labelled retrospective; newly transformed controls are fixed before execution.
The suite uses the 32 replication summaries and monthly exposure table only.
The August 2025 temporal-holdout FITS arrays remain sealed and forbidden.
Previous verified remote: `cdfc68ff64adb316e40a741bf37a80373cfdbe3c`.
Next: implement the matrix and retain its suite-level result regardless of sign.

## 11b - Comprehensive falsification suite fails

science: retain failed falsification suite

Five of eleven directional tests pass. Shuffled dates, reversed time and Kp
negative controls behave as required, and major-event removal and leave-one-
event-out satisfy their stability limits. Exact-zero-event support, alternative
lags, temporal binning, leave-one-epoch-out exposure support, detector subsets
and synthetic-null calibration fail. The null false-positive rate is 0.35
against the frozen 0.10 maximum. All outputs are finite and the temporal holdout
remains sealed. Previous verified remote:
`61a95d565c8513494658ebc7aea2ad2c01b4c3c2`. Next: publish the bounded evidence
in a tested static research interface without softening failed gates.

## 12 - Static research interface implemented locally

web: build evidence-driven research interface

The React/TypeScript site implements the five required environment, detector,
timeline, science-impact and evidence views. Three.js is lazy loaded; Motion is
restrained and reduced-motion aware; the schematic has pause and keyboard
controls plus a non-WebGL text equivalent. All scientific values come from a
Python-generated compact JSON carrying source hashes. Desktop and 390-pixel
mobile views were inspected. Local TypeScript build and ESLint pass. Previous
verified remote: `131ef00bc260e768fb49d709fa4997201c22ac62`. Next: run the
combined validation, push, and verify GitHub Pages.

## 12b - Research website deployed and cross-platform CI repaired

web: verify live Pages deployment

The GitHub Pages workflow succeeds and the public URL returns HTTP 200 with
evidence generated from commit `9a4964591a0f72aeba4051d05246aad82de9880f`.
Desktop and 390-pixel mobile layouts and the detector/image state controls pass
interactive inspection. Scientific CI exposed Linux import discovery for two
tests that import analysis scripts; `scripts/__init__.py` makes those entry
points an explicit package. All 78 tests and Ruff checks pass locally after the
repair. Next: push the repair, require green remote CI, then audit publication
figure and manuscript completeness.

## 13/14 - Required figures and bounded manuscript completed

paper: complete publication output set

The eleven required figure roles now map to reproducible PDF outputs. New
mission-context, event-response-audit and conditional CTI image figures are
generated together with compact machine-readable inputs. The event panel reports
a descriptive increment correlation of -0.07 and explicitly rejects a causal
interpretation. The manuscript abstract, introduction, mission context,
validation, limitations and conclusions now reflect the actual pass/fail record.
Previous verified remote: `a8adb885c56eaf144d94f1724222d0e0234eadb2`.
Next: final provenance/status audit and release checkpoint.

## 18 - Bounded first research release complete

release: record final scientific status

The final status separates completed execution from the failed attribution
hypothesis. It records demonstrated results, failures, surviving bounded
hypotheses, model-dependent quantities, unavailable public data, reproduction
commands, audited SHA, live Pages status and the next highest-information
experiment. The temporal holdout remains sealed. Previous verified remote:
`9928c0e61c02039cf1e6f34708486bb1a74d0bf9`. Next: expand mission-specific
engineering calibration before defining any new final holdout.

## 19 - Research interface visual system rebuilt

web: replace generic dashboard treatment with an editorial mission dossier

The public interface now uses a distinct archival-paper and signal-orange visual
system, an asymmetric research-dossier layout, annotated instrument plates and a
substantially richer Sun–Earth–L2 scene. The scene includes solar particle flow,
Earth atmosphere and magnetosphere, an orbiting HST representation, an L2 halo,
and separate Gaia and Euclid silhouettes. Detector, timeline, image-response and
verdict sections were redesigned without changing any scientific values or claim
boundaries. Desktop and 390-pixel mobile views, selectors, motion controls,
reduced-motion behavior, lint, production build and all 78 Python tests pass.
