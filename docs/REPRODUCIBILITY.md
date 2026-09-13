# Reproduction and evidence boundaries

Use Python 3.12. The tested direct numerical/software versions are in `requirements-tested.txt`; this is not a transitive or cross-platform lock.

Git attributes disable implicit line-ending conversion on manifests, archived
metadata, results, source, analysis scripts and method contracts because their
provenance hashes refer to literal bytes. Source formatting remains explicit
through Ruff. Do not normalize those files in an editor. Earlier checkpoints
preceded this portability fix; use the current checkpoint's preserved evidence
bytes for cross-platform verification.

```sh
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-tested.txt
python -m pip install -e '.[dev]'
ruff check .
ruff format --check .
pytest -q
mypy src/lattice/provenance.py --ignore-missing-imports
```

Replay the **frozen** cohort, not a fresh query, for the published pilot:

```sh
lattice fetch-plan data/manifests/hst_raw_plan.json --max-mb 60
lattice verify data/manifests/hst_raw_plan_retrieved.json
lattice fetch-plan data/manifests/omni_pinned_plan.json --max-mb 20
lattice verify data/manifests/omni_pinned_plan_retrieved.json
python scripts/validate_hst.py
python scripts/analyze_hst.py
python scripts/assess_hst_gate.py
```

The versioned retrieved manifest pins downloads on a new checkout even when the cache is absent. RAW payloads total 566,645,760 bytes; the three environment objects total 8,619,840 bytes. They remain ignored. Upstream checksum changes are errors, not automatic version updates. MAST observation and product query snapshots are small and committed under `data/metadata/hst`; verify them with their manifests.

Fresh discovery is a **new cohort version**, not exact reproduction:

```sh
python scripts/discover_hst.py --years 2003 2006 2009 2012 2015 2018 2021 2024
python scripts/prepare_raw_plan.py
```

Archive query membership and products may change. Preserve old manifests before deliberately introducing a new cohort. The original `hst_plan.json` records the unsuccessful uniform-FLT route; use `hst_raw_plan.json` for the pilot. `omni.json` records the early acquisition smoke test with a dirty-source disclosure; use the pinned production retrieval manifest for analysis.

`analyze_hst.py` generates machine-readable primary, binned, profile and operational-metadata outputs plus the PDF and PNG pilot plot. It fixes bootstrap seeds. Source files, input manifest and method document hashes accompany its measurements. Floating-point/plot bytes may vary by library/platform even when measurement values agree; retrieval byte equality is stricter.

GitHub CI runs synthetic/mock tests without archive downloads. This validates software behaviour, not mission physics. The RAW pilot has no locked temporal holdout and cannot support a forecast comparison. The retained conditional science-bias run fails its frozen measurement-validity gate and does not establish mission performance.

## Official calibration comparison

Install HSTCAL 3.2.0 in a Linux environment. The exact Linux package URLs used on this host are preserved in `docs/hstcal-linux-explicit.txt`; ACSCCD reports 10.4.1 (08-Aug-2025). With micromamba available, create an environment from this explicit specification. On Windows use Ubuntu WSL. Executable and per-product reference hashes are recorded in `results/calibration/products.json`.

```sh
micromamba create -y -n hstcal -f docs/hstcal-linux-explicit.txt
lattice fetch-plan data/manifests/hst_references_plan.json --max-mb 200
lattice fetch-plan data/manifests/hst_support_plan.json --max-mb 2
python scripts/extract_hst_telemetry.py
# Native Linux: use the absolute path to the environment's acsccd.e.
python scripts/run_acsccd.py --acsccd /absolute/path/to/env/bin/acsccd.e
# Windows: add --wsl-distro Ubuntu and supply the Linux executable path.
python scripts/analyze_hst.py --calibrated
python scripts/assess_calibrated_hst.py
```

Run from the repository root. The runner stages relative paths because HSTIO does not handle embedded spaces in FITS path expressions. Large reference and calibrated FITS files stay in the ignored cache. BLV means a bias/gain/overscan-calibrated intermediate with dark, CTI and flash correction omitted, not a fully calibrated science FLT. The telemetry export retains both temperature channels without selecting one; see `HST_OPERATING_STATE.md`.

## Independent historical replication

The retrieved replication manifests contain 32 analysis exposures and six checksum-pinned temporal-holdout exposures. Role filters are mandatory: the following commands reject holdout records. The holdout may be downloaded and byte-verified, but these commands do not open its pixels.

```sh
python scripts/extract_hst_telemetry.py --raw-manifest data/manifests/hst_replication_raw_plan_retrieved.json --support-manifest data/manifests/hst_replication_support_plan_retrieved.json --output results/hst_replication/operating_state.json --required-role replication
python scripts/run_acsccd.py --acsccd /absolute/path/to/env/bin/acsccd.e --raw-manifest data/manifests/hst_replication_raw_plan_retrieved.json --assignments data/manifests/hst_replication_reference_assignments.json --reference-manifest data/manifests/hst_references_plan_retrieved.json --reference-manifest data/manifests/hst_replication_references_plan_retrieved.json --receipt results/calibration/replication_products.json --required-role replication
python scripts/verify_calibration.py --receipt results/calibration/replication_products.json --raw-manifest data/manifests/hst_replication_raw_plan_retrieved.json --reference-manifest data/manifests/hst_references_plan_retrieved.json --reference-manifest data/manifests/hst_replication_references_plan_retrieved.json --assignments data/manifests/hst_replication_reference_assignments.json --required-role replication
python scripts/analyze_hst.py --products results/calibration/replication_products.json --output-dir results/hst_replication --figure-stem hst_replication_longitudinal --required-role replication
python scripts/assess_hst_replication.py
python scripts/compare_hst_cohorts.py
python scripts/summarize_hst_replication_nuisance.py
```

On Windows add `--wsl-distro Ubuntu` to the ACSCCD command and use the Linux executable path. The 32 derived BLV files total 5,370,808,320 bytes and remain ignored; their hashes and logs are committed in the calibration receipt. The analysis retains each pair separately. `assessment.json` applies the preregistered four-slope direction screen and 32-control Bonferroni family, while `nuisance_summary.json` labels its unadjusted correlations as descriptive.

## Continuous environment layer

The production environment replay uses the frozen 23-file OMNI plan and 1,883-file SGPS plan. The retrieved manifests pin every object hash; the payloads total 1,112,026,923 bytes and remain ignored. The aggregation command verifies each object again before opening it.

```sh
lattice fetch-plan data/manifests/omni_continuous_plan.json --max-mb 4
lattice fetch-plan data/manifests/goes_sgps_plan.json --max-mb 2
lattice verify data/manifests/omni_continuous_plan_retrieved.json
lattice verify data/manifests/goes_sgps_plan_retrieved.json
python scripts/build_exposure.py
```

This writes the monthly table, threshold-run table, provenance summary and PDF/PNG timeline. The transform supports both historical SGPS time-coordinate names. It leaves missing samples and the OMNI–SGPS gap missing, retains separate cumulative series, and labels the SGPS reconstruction and mission response bases as proxies.

## Historical B0–B5 benchmark

The baseline code and `docs/BASELINE_PROTOCOL.md` were committed and pushed before the historical command was executed. It reads only the 32 replication summaries and the monthly exposure product. Environment features stop at the end of the UTC month before each exposure.

```sh
python scripts/run_baselines.py
```

The command writes all 96 predictions, pooled metrics, exact input/protocol/source hashes and the frozen advanced-model target values to `results/baselines/historical_forward_chaining.json`. It also regenerates the PDF/PNG forecast figure. The six August 2025 holdout pixel arrays are not inputs.

## Synthetic latent-state recovery

The state-space protocol and implementation were committed and pushed before the
100-replicate batch. The command uses only simulated data and fixed seeds:

```sh
python scripts/run_synthetic_recovery.py --replicates 100 --workers 4
```

It writes every replicate, interval, posterior-predictive count, fixed-truth rank and
provenance hash to `results/core_model/synthetic_recovery.json`, plus the PDF/PNG
diagnostic figure. The retained batch failed the latent-RMSE, prior-predictive and
rank-calibration gates. Those ranks are a repeated-sampling diagnostic rather
than canonical prior-drawn SBC. It explicitly records `observational_fit` as
`NOT RUN`; no mission
outcome or temporal-holdout pixel array is an input.

The four diagnostic ablations reuse those exact seeds and the stored full-model
fits. Their plan and implementation are frozen before execution:

```sh
python scripts/run_core_ablations.py --workers 4
```

This command sets annealing, event response, background response and process
noise exactly to zero in turn. It compares paired likelihood, information
criteria and reconstruction errors without changing the failed recovery gate. It
writes all 400 fits to `results/core_model/synthetic_ablations.json` and generates
the PDF/PNG figure under `paper/figures/synthetic_ablations`.

## Reference-anchored v2 recovery

The v2 protocol separates fixed-truth recovery from canonical prior-drawn SBC.
Its implementation must be committed before this command runs:

```sh
python scripts/run_synthetic_recovery_v2.py --replicates 100 --workers 4
```

The command performs 100 fixed-truth fits and a separate 100 fits whose truths
are drawn from the frozen v2 priors. It also executes the independent 1,000-draw
prior-predictive gate. All inputs are simulated. The result and figure are written
under `results/core_model/synthetic_recovery_v2.json` and
`paper/figures/synthetic_recovery_v2.{pdf,png}`.

The retained production run passes the prior, latent-RMSE, aggregate interval,
bias, predictive and optimizer gates but fails canonical SBC for process scale.
Its output records both 100-replicate populations separately and explicitly marks
the observational fit as not run.

## Heavy-tailed v3 posterior recovery

V3 keeps the v2 model and replaces Laplace posterior draws with an exact-posterior
independence sampler. Its multivariate t5 proposal uses Laplace geometry only to
improve sampling efficiency. Run the checkpointed harness with:

```sh
python scripts/run_synthetic_recovery_v3.py --replicates 100 --workers 4
```

The command performs 100 fixed-truth and 100 prior-drawn SBC datasets, each with
two 2,000-draw chains, then writes compact diagnostics and summaries rather than
all posterior draws. It uses only synthetic inputs and records the v3 protocol,
model, sampler, script and v2-result hashes. The retained production run passes
all frozen gates with 99/100 usable datasets in each population. Canonical SBC
passes for all eight parameters, including process scale at p=0.9114. The result
explicitly records the observational fit as not run and leaves the physical-
inference gate closed.

## Historical v3 state-space validation

The historical protocol and implementation must both be committed before the
observational command is executed. It accepts only the 32 replication summaries
and builds every exposure feature from complete months preceding its forecast
epoch:

```sh
python scripts/run_historical_state_space.py
```

The command evaluates the frozen primary model, four exact-zero ablations and
five lag/proxy sensitivities in the same four whole-epoch folds as B0–B5. It
writes all inputs, forecasts, chain diagnostics, scores, gates and provenance
hashes to `results/core_model/historical_state_space.json` and generates the
historical forecast and sensitivity figures. It rejects any non-replication
outcome; the August 2025 holdout is not an input. The retained run completes all
40 fits but fails the primary RMSE and predictive-density thresholds. Its
exact-zero event model outperforms H0 on both scores, so exposure attribution
also fails. The full result and all nine provenance hashes are retained.

## Gaia availability and literature validation

Query the current official Gaia Archive schema and compare the frozen L2
environment basis with the explicitly published September 2017 event constraint:

```sh
python scripts/audit_gaia_availability.py
```

The command stores all returned table names, exact-token searches, access time,
input/source hashes and the event-month comparison in
`results/gaia/availability_audit.json`. Its 2026-09-12 run found 248 tables and
zero candidate CTI/engineering tables. Network schema results can change, so a
later run is a new availability audit. Literature values come from the committed
constraint table; no figure digitisation is performed.

## Euclid availability audit

Query the current official Q1 TAP schema and product metadata, then perform a
bounded 80-byte FITS-signature probe without downloading a full frame:

```sh
python scripts/audit_euclid_availability.py
```

The command stores the table inventory, raw VIS product classes, all 36 public
parallel trap-pumping frame identifiers, detector-record count, source hashes,
and release-matrix boundary in `results/euclid/availability_audit.json`. The
2026-09-12 run found 836 calibrated VIS quad frames, 36 raw trap-pumping frames,
and zero distributed processed trap-result products. A later run is a new live
availability audit. No full Euclid FITS product or publication figure is an
input to this result.

## Euclid conditional transfer

Run the frozen mission-specific charge-release grid:

```sh
python scripts/run_euclid_transfer.py
```

The script reads only the committed Euclid constraint table and frozen protocol.
It writes all 810 scenarios and numerical gates to
`results/euclid/conditional_transfer.json` and regenerates the transfer figure.
The production run passes causality, non-negativity, kernel-mass and propagated-
charge conservation gates. It does not read Euclid pixels, HST fitted parameters
or Gaia fitted parameters, and it does not generate an observational amplitude
or calendar forecast.

## Conditional detector-to-science bias

Run the frozen analytic image population and paired-noise experiment:

```sh
python scripts/run_science_bias.py
```

The command writes 432 source scenarios, 54 noiseless ring-test scenarios,
provenance hashes and all frozen gates to
`results/science_bias/conditional_euclid_bias.json`. It regenerates the PDF/PNG
failure figure. The retained production run fails because only 8/32 paired
measurements are valid in its worst low-signal scenario, below the fixed 30/32
threshold. Reproduction should return the failure; it must not be interpreted
as a validated Euclid bias envelope.

Run the separately frozen fixed-weight follow-up with:

```sh
python scripts/run_science_bias_weighted.py
```

It records the failed predecessor hashes and verifies they remain unchanged. The
retained run should also return `FAIL`: its minimum is 23/32 valid pairs, below
the unchanged 30/32 gate. Its distinct JSON and figure names prevent overwriting
the first experiment.

The preregistered fixed-template response experiment is reproduced with:

```sh
python scripts/run_science_bias_forced.py
```

It must retain both failed predecessor experiment hashes and generate 432 source
scenarios with 32/32 finite responses plus 54 finite ring scenarios. Its passing
result validates the controlled linearized response calculation, not a blind
survey pipeline or observational Euclid performance.
