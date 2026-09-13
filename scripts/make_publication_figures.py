"""Generate the remaining required publication figures from versioned inputs."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lattice.cli import software_commit
from lattice.euclid_transfer import mixture_kernel
from lattice.provenance import sha256, write_json
from lattice.science_bias import (
    apply_parallel_trail,
    elliptic_covariance,
    gaussian_source,
)


def save(figure, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(stem.with_suffix(".png"), dpi=180)
    figure.savefig(stem.with_suffix(".pdf"))
    plt.close(figure)


def conceptual_figure(output: Path) -> None:
    figure, axis = plt.subplots(figsize=(11, 5.8), constrained_layout=True)
    axis.set_xlim(-5.2, 6.5)
    axis.set_ylim(-2.8, 2.8)
    axis.set_facecolor("#08131d")
    figure.patch.set_facecolor("#08131d")
    axis.scatter(-4, 0, s=2700, color="#e2a44f", edgecolor="#f3ca83", linewidth=2)
    axis.scatter(0, 0, s=900, color="#4f9fc0", edgecolor="#8ad1e5", linewidth=2)
    earth_orbit = plt.Circle((0, 0), 0.72, fill=False, color="#8298a3", linestyle="--")
    l2_region = plt.Circle((4.4, 0), 0.58, fill=False, color="#8298a3", linestyle="--")
    axis.add_patch(earth_orbit)
    axis.add_patch(l2_region)
    axis.scatter(0.68, 0.18, marker="s", s=80, color="#e6edf0")
    axis.scatter(4.18, 0.22, marker="D", s=90, color="#74c5d8")
    axis.scatter(4.62, -0.22, marker="s", s=90, color="#d9a45f")
    axis.annotate("Sun", (-4, -1.02), ha="center", color="#e9eff1", fontsize=12)
    axis.annotate("Earth", (0, -1.02), ha="center", color="#e9eff1", fontsize=12)
    axis.annotate("HST · LEO", (0.8, 0.62), color="#e9eff1", fontsize=11)
    axis.annotate("Gaia", (3.78, 0.72), color="#74c5d8", fontsize=11)
    axis.annotate("Euclid", (4.7, -0.82), color="#d9a45f", fontsize=11)
    axis.annotate("Sun–Earth L2 region", (4.4, 1.25), ha="center", color="#a8bac2")
    axis.plot([-3.2, -0.7], [0, 0], color="#4f6671", linewidth=1)
    axis.plot([0.7, 3.8], [0, 0], color="#4f6671", linewidth=1)
    axis.text(
        0.5,
        -2.25,
        "SCHEMATIC GEOMETRY · positions and distances not to scale",
        ha="center",
        color="#d9a45f",
        fontsize=10,
        family="monospace",
    )
    axis.set_title(
        "Mission environments and detector architectures",
        color="#f0f5f6",
        fontsize=18,
        pad=16,
    )
    axis.axis("off")
    save(figure, output)


def event_audit_figure(rows: list[dict], output: Path) -> dict:
    years = sorted({row["year"] for row in rows})
    detector = []
    event = []
    for year in years:
        selected = [row for row in rows if row["year"] == year]
        detector.append(float(np.mean([row["outcome"] for row in selected])))
        event.append(
            float(
                selected[0]["log_omni_event_cumulative"] + selected[0]["log_sgps_event_cumulative"]
            )
        )
    detector_change = np.diff(detector)
    event_change = np.diff(event)
    correlation = float(np.corrcoef(detector_change, event_change)[0, 1])
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.8), constrained_layout=True)
    axes[0].plot(years, detector, marker="o", color="#326789", label="detector observable")
    event_scaled = np.asarray(event) / max(event)
    axes[0].bar(
        years, event_scaled, width=1.4, color="#d9a45f", alpha=0.35, label="event proxy / max"
    )
    axes[0].set(xlabel="Historical epoch", ylabel="Mean trail fraction / scaled proxy")
    axes[0].legend(frameon=False)
    axes[1].scatter(event_change, detector_change, color="#d1495b", s=45)
    for year, x, y in zip(years[1:], event_change, detector_change, strict=True):
        axes[1].annotate(str(year), (x, y), xytext=(4, 4), textcoords="offset points", fontsize=8)
    axes[1].axhline(0, color="#666666", linewidth=0.8)
    axes[1].set(xlabel="Change in cumulative event proxy", ylabel="Change in detector observable")
    for axis in axes:
        axis.grid(alpha=0.2)
        axis.spines[["top", "right"]].set_visible(False)
    figure.suptitle(
        "Event-response audit: sparse epochs do not resolve attribution\n"
        f"Descriptive increment correlation r={correlation:.2f}; no causal estimate",
        color="#8b1e1e",
        fontweight="bold",
    )
    save(figure, output)
    return {
        "years": years,
        "detector_epoch_means": detector,
        "combined_log_event_proxy": event,
        "detector_increments": detector_change.tolist(),
        "event_proxy_increments": event_change.tolist(),
        "descriptive_increment_correlation": correlation,
        "claim": "DESCRIPTIVE; EVENT ATTRIBUTION NOT RESOLVED",
    }


def cti_image_figure(output: Path) -> dict:
    shape, center = (96, 96), (48.0, 24.0)
    psf_sigma = 0.16 / 2.355 / 0.1
    kernel = mixture_kernel(220e-6, 20e-3, 0.5, 4.02e-3, 4096)
    scenarios = [
        ("Point source", gaussian_source(shape, center, 3000, np.eye(2) * psf_sigma**2)),
        (
            "Faint galaxy",
            gaussian_source(shape, center, 3000, elliptic_covariance(2.0, 0.7, 0.35, psf_sigma)),
        ),
    ]
    figure, axes = plt.subplots(2, 3, figsize=(9.4, 6.1), constrained_layout=True)
    summaries = []
    for row_index, (label, clean) in enumerate(scenarios):
        damaged, overflow = apply_parallel_trail(clean, kernel, 0.003, 1.0)
        difference = damaged - clean
        limit = np.percentile(clean, 99.8)
        diff_limit = max(abs(np.percentile(difference, 0.2)), abs(np.percentile(difference, 99.8)))
        for column, (image, title) in enumerate(
            ((clean, "Clean"), (damaged, "Damaged"), (difference, "Residual"))
        ):
            axes[row_index, column].imshow(
                image,
                origin="lower",
                cmap="RdBu_r" if column == 2 else "magma",
                vmin=-diff_limit if column == 2 else 0,
                vmax=diff_limit if column == 2 else limit,
            )
            axes[row_index, column].set_title(title)
            axes[row_index, column].set_xticks([])
            axes[row_index, column].set_yticks([])
        axes[row_index, 0].set_ylabel(label)
        summaries.append(
            {
                "source": label,
                "input_electrons": float(clean.sum()),
                "stamp_electrons": float(damaged.sum()),
                "overflow_electrons": overflow,
            }
        )
    figure.suptitle(
        "Conditional Euclid CTI image simulation\n"
        "SIMULATED · captured fraction 0.003 · full transfer distance",
        fontweight="bold",
    )
    save(figure, output)
    return {
        "quantity": "SIMULATED",
        "captured_fraction": 0.003,
        "transfer_distance_fraction": 1.0,
        "fast_weight": 0.5,
        "tau_factor": 1.0,
        "sources": summaries,
        "claim": "CONDITIONAL SCENARIO; OBSERVED DAMAGE AMPLITUDE UNAVAILABLE",
    }


def main() -> None:
    root = Path.cwd()
    baseline_path = root / "results/baselines/historical_forward_chaining.json"
    transfer_path = root / "results/euclid/conditional_transfer.json"
    baseline = json.loads(baseline_path.read_text())
    conceptual_figure(root / "paper/figures/mission_concept")
    event = event_audit_figure(
        baseline["joined_inputs"], root / "paper/figures/event_response_audit"
    )
    cti = cti_image_figure(root / "paper/figures/cti_image_simulation")
    result = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "baseline_result_sha256": sha256(baseline_path),
        "transfer_result_sha256": sha256(transfer_path),
        "mission_concept": {
            "quantity": "SCHEMATIC",
            "geometry": "NOT TO SCALE",
            "missions": ["HST ACS/WFC", "Gaia", "Euclid VIS"],
        },
        "event_response_audit": event,
        "cti_image_simulation": cti,
    }
    write_json(root / "results/publication/required_figure_inputs.json", result)
    print("Generated publication Figures 1, 4, and 9 with bounded claims")


if __name__ == "__main__":
    main()
