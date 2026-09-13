"""Export compact, provenance-linked evidence for the static research site."""

import json
from pathlib import Path

import numpy as np

from lattice.cli import software_commit
from lattice.provenance import sha256, write_json


def load(path: Path):
    return json.loads(path.read_text())


def main() -> None:
    root = Path.cwd()
    hst_path = root / "results/hst_replication/primary.json"
    environment_path = root / "results/environment/monthly_exposure.json"
    baseline_path = root / "results/baselines/historical_forward_chaining.json"
    historical_path = root / "results/core_model/historical_state_space.json"
    gaia_path = root / "results/gaia/availability_audit.json"
    euclid_path = root / "results/euclid/conditional_transfer.json"
    science_path = root / "results/science_bias/conditional_euclid_bias_forced.json"
    falsification_path = root / "results/falsification/comprehensive_suite.json"
    paths = {
        "hst_replication": hst_path,
        "environment": environment_path,
        "baselines": baseline_path,
        "historical_state_space": historical_path,
        "gaia_audit": gaia_path,
        "euclid_transfer": euclid_path,
        "science_bias": science_path,
        "falsification": falsification_path,
    }
    hst = load(hst_path)
    environment = load(environment_path)
    baseline = load(baseline_path)
    historical = load(historical_path)
    gaia = load(gaia_path)
    euclid = load(euclid_path)
    science = load(science_path)
    falsification = load(falsification_path)

    hst_epochs = []
    for year in sorted({row["year"] for row in hst["measurements"]}):
        values = [
            row["parallel_fraction"]["mean"] for row in hst["measurements"] if row["year"] == year
        ]
        hst_epochs.append({"year": year, "parallel_fraction_mean": float(np.mean(values))})
    yearly_environment = []
    for year in range(2003, 2026):
        rows = [row for row in environment["measurements"] if row["month"].startswith(str(year))]
        observed = [row["particle_fluence_pfu_s"] for row in rows if row["particle_fluence_pfu_s"]]
        yearly_environment.append(
            {
                "year": year,
                "particle_fluence_sum": float(np.sum(observed)) if observed else None,
                "quantity": "OBSERVED" if year <= 2020 else "PROXY",
            }
        )
    forced_rows = science["source_scenarios"]
    metrics = {}
    for name in ("centroid_y_mas", "flux_fraction", "e1", "e2", "size_fraction"):
        values = [row["intervals"][name]["median"] for row in forced_rows]
        metrics[name] = {
            "minimum": float(np.min(values)),
            "median": float(np.median(values)),
            "maximum": float(np.max(values)),
        }
    tests = [
        {"id": name.split("_")[0], "name": name, "status": value.get("status", "REFERENCE")}
        for name, value in falsification["tests"].items()
    ]
    output = {
        "generated_by_commit": software_commit(root),
        "quantity_legend": ["OBSERVED", "INFERRED", "SIMULATED", "FORECAST"],
        "headline": {
            "physical_inference_gate": "CLOSED",
            "falsification_suite": falsification["suite_gate"],
            "falsification_passed": sum(row["status"] == "PASS" for row in tests),
            "falsification_directional_total": 11,
            "null_false_positive_rate": falsification["tests"]["F12_synthetic_null"][
                "false_positive_rate"
            ],
            "conditional_science_gate": science["implementation_gate"],
        },
        "missions": [
            {
                "id": "hst",
                "name": "HST ACS/WFC",
                "region": "Low Earth orbit",
                "detector": "two 4096 × 2048 CCDs",
                "status": "OBSERVED",
                "summary": "Replicated longitudinal trailing observable; attribution gate closed.",
            },
            {
                "id": "gaia",
                "name": "Gaia",
                "region": "Sun–Earth L2",
                "detector": "106 CCD focal plane",
                "status": "INFERRED",
                "summary": (
                    f"Literature timing constraint; {gaia['archive']['table_count']} archive "
                    "tables audited and no public engineering CTI series found."
                ),
            },
            {
                "id": "euclid",
                "name": "Euclid VIS",
                "region": "Sun–Earth L2",
                "detector": "6 × 6 CCD mosaic",
                "status": "SIMULATED",
                "summary": (
                    "Conditional transfer grid passes "
                    f"{euclid['diagnostics']['scenario_count']} scenarios; observed damage "
                    "amplitude unavailable."
                ),
            },
        ],
        "hst_epochs": hst_epochs,
        "environment_years": yearly_environment,
        "forecast_scores": {
            name: {
                "rmse": value["rmse"],
                "nlpd": value["mean_negative_log_predictive_density"],
            }
            for name, value in baseline["metrics"].items()
        },
        "historical_primary": {
            "gate": historical["gates"]["primary_advanced_model_gate"],
            "rmse": historical["variants"]["H0_primary"]["metrics"]["rmse"],
            "nlpd": historical["variants"]["H0_primary"]["metrics"][
                "mean_negative_log_predictive_density"
            ],
        },
        "science_bias": {
            "quantity": "SIMULATED",
            "result_class": science["result_class"],
            "scenario_count": science["diagnostics"]["scenario_count"],
            "paired_responses": science["diagnostics"]["minimum_valid_pairs"],
            "metrics": metrics,
            "claim_boundary": science["claim_boundary"],
        },
        "falsification_tests": tests,
        "provenance": {name: sha256(path) for name, path in paths.items()},
    }
    write_json(root / "web/public/data/evidence.json", output)
    print(
        f"Exported website evidence at {output['generated_by_commit']}; "
        f"falsification={output['headline']['falsification_suite']}"
    )


if __name__ == "__main__":
    main()
