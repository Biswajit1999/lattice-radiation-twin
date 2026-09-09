"""Audit calibrated controls and operating-state confounding without gate inflation."""

import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lattice.cli import software_commit
from lattice.provenance import sha256, write_json


def main():
    root = Path.cwd()
    directory = root / "results/hst_calibrated"
    paths = {
        "primary": directory / "primary.json",
        "binned": directory / "measurements.json",
        "raw": root / "results/hst/primary.json",
        "operating": root / "results/hst/operating_state.json",
    }
    inputs = {k: json.loads(p.read_text()) for k, p in paths.items()}
    rows = inputs["primary"]["measurements"]
    raw = {(r["year"], r["chip"]): r for r in inputs["raw"]["measurements"]}
    controls = {
        key: [
            dict(year=r["year"], chip=r["chip"], **r[key])
            for r in rows
            if r[key]["mean"] is not None and (r[key]["lo"] > 0 or r[key]["hi"] < 0)
        ]
        for key in ("blank_fraction", "serial_fraction")
    }
    comparisons = []
    for r in rows:
        old = raw[r["year"], r["chip"]]
        acquisitions = [
            e["acquisition"] for e in inputs["operating"]["exposures"] if e["year"] == r["year"]
        ]
        comparisons.append(
            dict(
                year=r["year"],
                chip=r["chip"],
                raw=old["parallel_fraction"],
                calibrated=r["parallel_fraction"],
                acquisitions=acquisitions,
            )
        )
    result = dict(
        software_commit=software_commit(root),
        script_sha256=sha256(Path(__file__)),
        input_sha256={k: sha256(p) for k, p in paths.items()},
        evidence="OBSERVED",
        calibration_pipeline_executed=True,
        physical_damage_inference_gate_passed=False,
        selected_primary_peaks=sum(r["parallel_fraction"]["n"] for r in rows),
        comparisons=comparisons,
        nominal_95_percent_control_intervals_excluding_zero=controls,
        interpretation="Intervals are unadjusted diagnostics, not hypothesis-test discoveries. "
        "RAW and calibrated bins select different populations; differences do not isolate "
        "the causal effect of calibration.",
        unresolved=[
            "Post-flash and background differ across epochs",
            "Operating temperature sensor mapping and clock dwell times unresolved",
            "Sink correction omitted; calibration uncertainty not propagated",
            "One pair per epoch cannot estimate between-exposure reproducibility",
            "Serial array-axis asymmetry is not amplifier-oriented serial CTI",
            "Eight development epochs cannot establish event response or exposure lags",
        ],
    )
    write_json(directory / "validation_gate.json", result)
    plot(inputs["binned"]["measurements"], root)
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "selected_primary_peaks",
                    "physical_damage_inference_gate_passed",
                    "nominal_95_percent_control_intervals_excluding_zero",
                )
            },
            indent=2,
        )
    )


def plot(rows, root):
    plt.rcParams.update({"font.size": 8, "pdf.fonttype": 42, "figure.dpi": 150})
    fig, axes = plt.subplots(2, 3, figsize=(10, 6), sharex=True, layout="constrained")
    years = sorted({r["year"] for r in rows})
    colors = plt.colormaps["viridis"](np.linspace(0.05, 0.9, len(years)))
    for chip, row_axes in zip((1, 2), axes, strict=True):
        for signal, ax in zip(([100, 300], [300, 1000], [1000, 3000]), row_axes, strict=True):
            for year, color in zip(years, colors, strict=True):
                subset = [
                    r
                    for r in rows
                    if r["chip"] == chip
                    and r["year"] == year
                    and r["signal_electrons"] == signal
                    and r["parallel_fraction"]["mean"] is not None
                ]
                y = np.array([r["parallel_fraction"]["mean"] for r in subset])
                lo = np.array([r["parallel_fraction"]["lo"] for r in subset])
                hi = np.array([r["parallel_fraction"]["hi"] for r in subset])
                ax.errorbar(
                    [np.mean(r["transfers"]) for r in subset],
                    y,
                    yerr=[y - lo, hi - y],
                    color=color,
                    lw=0.8,
                    marker=".",
                    markersize=3,
                    label=str(year),
                )
            ax.axhline(0, color="0.5", lw=0.5)
            ax.set_title(f"WFC{chip}; {signal[0]}–{signal[1]} electrons")
            ax.grid(alpha=0.15)
            if chip == 2:
                ax.set_xlabel("Parallel transfers (bin centre)")
        row_axes[0].set_ylabel("Five-pixel parallel trail / peak")
    axes[0, 0].legend(ncol=2, fontsize=6)
    fig.suptitle(
        "OBSERVED • Calibrated development sample\n"
        "95% column-bootstrap intervals; operating conditions differ between epochs"
    )
    fig.savefig(root / "paper/figures/hst_calibrated_controls.pdf")
    fig.savefig(root / "results/hst_calibrated/hst_calibrated_controls.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
