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

GitHub CI runs synthetic/mock tests without archive downloads. This validates software behaviour, not mission physics. The RAW pilot has no locked temporal holdout and cannot support a forecast comparison. No latent-state recovery, cross-mission validation or science-bias result has been demonstrated.

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
