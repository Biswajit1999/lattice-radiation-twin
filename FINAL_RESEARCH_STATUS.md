# LATTICE final research status

Status date: **2026-09-13**  
Release scope: **bounded first research release complete**  
Scientific attribution status: **FAILED / physical-inference gate closed**

## 1. What was actually demonstrated

- A provenance-pinned HST ACS/WFC pipeline calibrated 48 historical exposures
  and replicated a positive longitudinal trailing observable across two
  independent pairs, two chips and eight epochs from 2003--2024. The replication
  sample contains 102,604 primary peak measurements; all four time slopes are
  positive with positive 95% epoch-bootstrap intervals, and none of 32 adjusted
  blank-control intervals excludes zero.
- A continuous external-environment layer preserves 23 OMNI annual files and
  1,883 GOES-R SGPS daily files with an explicit 2020 coverage gap and proxy
  labels. These data are external environment measurements, not detector dose.
- The v3 exact-posterior state-space computation passes all synthetic recovery
  gates, including 99/100 usable fixed-truth and prior-drawn SBC datasets,
  latent-state RMSE 0.00797 and process-scale SBC p=0.9114.
- A Euclid-specific conditional charge-release grid passes all numerical gates
  across 810 scenarios, with maximum kernel-mass error `3.33e-16` and propagated
  charge error `7.28e-16`.
- A fixed-template forced-response image experiment passes all gates across 432
  point/galaxy scenarios with 32/32 finite paired responses and 54 finite ring
  scenarios. Its median conditional y-centroid response is 0.139 mas across the
  fixed sensitivity grid.
- The static React/TypeScript/Three.js research interface is live, responsive,
  reduced-motion aware and generated from provenance-linked result JSON.
- A dedicated identifiability audit shows why the four cumulative exposure
  components cannot be interpreted separately from this sparse historical
  design; it preserves rather than relaxes the closed attribution gate.
- All eleven required publication figure roles have reproducible PDF outputs,
  and the release-candidate manuscript reports the complete bounded result.

## 2. What failed

- Exposure-informed B3/B4 baselines do not beat calendar-linear B0 on both RMSE
  and predictive density. B0 RMSE is 0.04024; B4 RMSE is 0.04055.
- The observational v3 state-space primary model fails its frozen thresholds:
  RMSE is 0.04977 and NLPD is -1.6480. Removing the event term improves both
  scores to 0.03527 and -1.9286.
- The comprehensive falsification suite fails. Five of eleven directional tests
  pass, only two of four detector subsets favour exposure, and the 200-dataset
  synthetic-null false-positive rate is 0.35 versus the frozen 0.10 maximum.
- The component-identifiability audit fails all four diagnostics: two residual
  degrees of freedom, maximum exposure correlation 0.9981, maximum VIF 4,881.4,
  and unstable leave-one-epoch coefficient signs.
- The original unweighted and fixed-weight noisy moment experiments fail their
  validity gates at worst-case counts of 8/32 and 23/32. They remain retained
  and are not replaced by the later forced-response pass.
- Direct quantitative Gaia CTI validation, an HST-versus-L2 predictive score,
  observational Euclid damage amplitude and posterior science-bias propagation
  could not be completed with the public data located.

## 3. Which hypotheses survived

- The measured HST trailing observable increases over the sampled historical
  interval and replicates under the frozen extraction and control design.
- The exact-posterior v3 algorithm can recover the specified latent model in
  synthetic data.
- Mission-specific conditional Euclid release and fixed-template image-response
  calculations are numerically stable over their frozen scenario grids.
- The shuffled-date, reversed-time and Kp negative controls correctly fail to
  outperform calendar time.

The hypothesis that the current external radiation proxies identify and improve
prediction of HST detector damage **did not survive**. No cross-mission amplitude
transfer hypothesis survived a direct observational test.

## 4. Which quantities remain model-dependent

- Euclid captured fraction, trap-species weights and emission-time sensitivities;
- shielding and detector-response kernels for HST, Gaia and Euclid;
- SGPS band integration and every mission-response basis;
- latent damage state, annealing, event and background coefficients;
- conditional centroid, flux, ellipticity, size and shear-response envelopes;
- any calendar trajectory, mission forecast or posterior science-impact interval.

## 5. Which data could not be obtained publicly

- the reported 26-epoch Gaia engineering serial-CTI series and device-level
  calibration measurements;
- processed Euclid trap-pumping results, trap models, CTI calibration and CTI
  time-evolution series;
- an empirically overlapping OMNI/SGPS interval for cross-calibration;
- verified HST exposure-averaged active-sensor temperature and clock dwell time.

Thirty-six raw Euclid parallel trap-pumping acquisitions are public, but reducing
them to validated trap measurements is a separate mission-specific project.

## 6. Exact reproduction commands

Use Python 3.12 and Node 20.19 or later from the repository root:

```sh
python -m pip install -r requirements-tested.txt
python -m pip install -e '.[dev]'
ruff check .
ruff format --check .
pytest -q
python scripts/build_exposure.py
python scripts/run_baselines.py
python scripts/run_synthetic_recovery_v3.py --replicates 100 --workers 4
python scripts/run_historical_state_space.py
python scripts/audit_gaia_availability.py
python scripts/audit_euclid_availability.py
python scripts/run_euclid_transfer.py
python scripts/run_science_bias.py
python scripts/run_science_bias_weighted.py
python scripts/run_science_bias_forced.py
python scripts/run_falsification_suite.py
python scripts/run_identifiability_audit.py
python scripts/make_publication_figures.py
python scripts/export_web_data.py
cd web
npm ci
npm run lint
npm run build
```

HST calibration, archive retrieval and role-filtered replication commands are in
`docs/REPRODUCIBILITY.md`. The six temporal-holdout FITS arrays must not be
opened when reproducing this release.

## 7. Latest audited Git commit SHA

The v0.2.0 science, website and publication content was audited at:

`ef2a5509fb787330178e045ec69f1ea16d4ed11b`

Scientific CI and Pages both passed for this commit. This status document is
committed in a subsequent checkpoint because a file cannot contain the hash of
the commit that contains itself. Use `git rev-parse HEAD` for the final
status-document commit; it is also reported in the release and remote history.

## 8. Live website status

**LIVE and verified**: <https://biswajit1999.github.io/lattice-radiation-twin/>

The deployed page returned HTTP 200, the public evidence JSON matched the
deployed commit, and the GitHub Pages workflow passed. Scientific CI also passed
Python 3.12 tests, Ruff, evidence export, clean npm install, ESLint and the Vite
production build.

## 9. Next experiment with greatest information gain

Build a larger HST engineering-calibration cohort with independently measured
background, post-flash, active-sensor temperature, gain/electronics state and
clock timing at substantially more epochs. Freeze a pair-aware measurement-error
model and temporal thresholds before opening any new final holdout. This directly
targets the confounding and null false-positive failure that further proxy-model
tuning cannot resolve. In parallel, a validated reduction of the 36 public
Euclid raw trap-pumping acquisitions would provide the first observational
amplitude for the conditional transfer and science-response pipeline.
