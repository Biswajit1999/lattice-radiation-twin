"""Generate numerical validation evidence for the conditional transfer model."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

from lattice.kernel_validation import (
    image_window_convergence,
    mixture_recovery_experiment,
    tail_budget_sweep,
)


def _write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    output = root / "results/numerical_validation"
    output.mkdir(parents=True, exist_ok=True)
    tail = tail_budget_sweep()
    recovery = mixture_recovery_experiment()
    window = image_window_convergence()
    _write_csv(output / "kernel_tail_budget.csv", tail)
    _write_csv(output / "mixture_recovery.csv", recovery)
    _write_csv(output / "image_window_convergence.csv", window)
    payload = {
        "schema": "lattice-kernel-validation/1",
        "data_class": "synthetic numerical validation",
        "supports_mission_trap_inference": False,
        "tail_budget": tail,
        "mixture_recovery": recovery,
        "image_window_convergence": window,
    }
    (output / "summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    figure, axes = plt.subplots(1, 2, figsize=(10, 4.2), constrained_layout=True)
    axes[0].loglog(
        [row["tau_seconds"] for row in tail if row["tail_tolerance"] == 1e-9],
        [row["required_lags"] for row in tail if row["tail_tolerance"] == 1e-9],
        marker="o",
    )
    axes[0].set(
        xlabel="Release time constant (s)",
        ylabel="Lags required for tail <= 1e-9",
        title="Kernel truncation budget",
    )
    axes[1].loglog(
        [row["height_pixels"] for row in window],
        [max(row["centroid_relative_error_vs_largest"], 1e-16) for row in window],
        marker="o",
        color="#9a3412",
    )
    axes[1].set(
        xlabel="Image height (pixels)",
        ylabel="Centroid relative error vs 128 px",
        title="Finite-window convergence",
    )
    figure.suptitle("Synthetic conditional-transfer numerics; no mission trap inference")
    figure.savefig(root / "paper/figures/kernel_numerical_validation.png", dpi=180)
    plt.close(figure)
    print(json.dumps({"recovery": recovery, "finest_window": window[-1]}, indent=2))


if __name__ == "__main__":
    main()
