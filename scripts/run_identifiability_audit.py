"""Quantify whether the historical design separates time from exposure components."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lattice.cli import software_commit
from lattice.identifiability import audit_identifiability
from lattice.provenance import sha256, write_json


def make_figure(audit: dict, output: Path) -> None:
    names = [
        "calendar",
        "OMNI event",
        "OMNI background",
        "SGPS event",
        "SGPS background",
    ]
    correlation = np.asarray(audit["correlation_matrix"])
    coefficients = audit["leave_one_epoch_out_coefficients"]
    years = [row["held_out_year"] for row in coefficients]
    feature_names = audit["feature_names"]
    matrix = np.array([[row[name] for name in feature_names] for row in coefficients])

    figure, axes = plt.subplots(1, 2, figsize=(12.4, 5.8), constrained_layout=True)
    image = axes[0].imshow(correlation, vmin=-1, vmax=1, cmap="coolwarm")
    axes[0].set_xticks(range(len(names)), names, rotation=35, ha="right")
    axes[0].set_yticks(range(len(names)), names)
    axes[0].set_title("Epoch-level predictor correlation")
    for row in range(len(names)):
        for column in range(len(names)):
            axes[0].text(column, row, f"{correlation[row, column]:.2f}", ha="center", va="center")
    figure.colorbar(image, ax=axes[0], fraction=0.046, label="Pearson correlation")

    for index, name in enumerate(names[1:], start=1):
        axes[1].plot(years, matrix[:, index], marker="o", label=name)
    axes[1].axhline(0, color="#555555", linewidth=1)
    axes[1].set(
        title="Exposure coefficients after leaving out one epoch",
        xlabel="Held-out epoch",
        ylabel="Standardized OLS coefficient",
    )
    axes[1].grid(alpha=0.2)
    axes[1].legend(fontsize=8)
    figure.suptitle("LATTICE historical component-identifiability audit: FAIL", fontweight="bold")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main() -> None:
    root = Path.cwd()
    baseline_path = root / "results/baselines/historical_forward_chaining.json"
    protocol_path = root / "docs/IDENTIFIABILITY_PROTOCOL.md"
    rows = json.loads(baseline_path.read_text())["joined_inputs"]
    audit = audit_identifiability(rows)
    output = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "protocol_sha256": sha256(protocol_path),
        "baseline_result_sha256": sha256(baseline_path),
        "evidence": "DIAGNOSTIC AUDIT OF OBSERVED HISTORICAL SUMMARY DESIGN",
        **audit,
        "claim_boundary": (
            "This post hoc design diagnostic quantifies separability of the existing "
            "epoch-level predictors. It does not estimate radiation damage, validate a "
            "causal effect, or reopen the closed physical-inference gate."
        ),
    }
    output_path = root / "results/identifiability/historical_design.json"
    write_json(output_path, output)
    make_figure(output, root / "paper/figures/identifiability_audit")
    print(
        f"Component-attribution gate {output['component_attribution_gate']}; "
        f"epochs={output['unique_epochs']}; residual_df={output['residual_degrees_of_freedom']}; "
        f"max_vif={max(output['variance_inflation_factors'].values()):.1f}"
    )


if __name__ == "__main__":
    main()
