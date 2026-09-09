# Reproduction and evidence boundaries

Use Python 3.12. The tested direct numerical/software versions are in `requirements-tested.txt`; this is not a transitive or cross-platform lock.

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
