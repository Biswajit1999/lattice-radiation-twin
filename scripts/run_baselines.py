"""Run the preregistered B0--B5 historical forward-chaining benchmark."""

import json
from datetime import UTC
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from astropy.time import Time

from lattice.baselines import evaluate_forward_chaining
from lattice.cli import software_commit
from lattice.provenance import sha256, write_json


def previous_month(mjd: float) -> str:
    stamp = Time(mjd, format="mjd").to_datetime(timezone=UTC)
    if stamp.month == 1:
        return f"{stamp.year - 1:04d}-12"
    return f"{stamp.year:04d}-{stamp.month - 1:02d}"


def positive_log(value) -> float:
    return float(np.log1p(max(0.0, value or 0.0)))


def join_inputs(outcomes: list[dict], exposure_rows: list[dict]) -> list[dict]:
    exposure = {row["month"]: row for row in exposure_rows}
    joined = []
    for row in outcomes:
        if row.get("analysis_role") != "replication":
            raise ValueError("Historical baseline received a non-replication outcome")
        month = previous_month(row["mjd"])
        env = exposure[month]
        interval = row["parallel_fraction"]
        measurement_se = max((interval["hi"] - interval["lo"]) / (2 * 1.96), 1e-4)
        time_years = (row["mjd"] - 52640.0) / 365.25
        phase = 2 * np.pi * time_years / 11.0
        joined.append(
            {
                "year": row["year"],
                "mjd": row["mjd"],
                "feature_cutoff_month": month,
                "pair_index": row["pair_index"],
                "chip": row["chip"],
                "outcome": interval["mean"],
                "measurement_se": measurement_se,
                "time_years": time_years,
                "time_years_squared": time_years**2,
                "solar_cycle_sin": float(np.sin(phase)),
                "solar_cycle_cos": float(np.cos(phase)),
                "log_omni_cumulative": positive_log(env["omni_cumulative_observed_fluence_pfu_s"]),
                "log_sgps_cumulative": positive_log(env["sgps_cumulative_proxy_fluence_pfu_s"]),
                "log_omni_event_cumulative": positive_log(
                    env["omni_cumulative_threshold_fluence_pfu_s"]
                ),
                "log_omni_background_cumulative": positive_log(
                    env["omni_cumulative_subthreshold_fluence_pfu_s"]
                ),
                "log_sgps_event_cumulative": positive_log(
                    env["sgps_cumulative_threshold_proxy_fluence_pfu_s"]
                ),
                "log_sgps_background_cumulative": positive_log(
                    env["sgps_cumulative_subthreshold_proxy_fluence_pfu_s"]
                ),
            }
        )
    expected = {
        (year, pair, chip) for year in range(2003, 2025, 3) for pair in (2, 3) for chip in (1, 2)
    }
    observed = {(row["year"], row["pair_index"], row["chip"]) for row in joined}
    if len(joined) != 32 or observed != expected:
        raise ValueError("Baseline input is not the frozen 8 x 2 x 2 replication design")
    return joined


def make_figure(predictions: dict, output: Path) -> None:
    names = list(predictions)
    figure, axes = plt.subplots(2, 3, figsize=(10.8, 6.4), sharex=True, sharey=True)
    for axis, name in zip(axes.flat, names, strict=True):
        values = predictions[name]
        years = np.asarray([row["test_year"] for row in values])
        observed = np.asarray([row["observed"] for row in values])
        predicted = np.asarray([row["predicted"] for row in values])
        sigma = np.asarray([row["predictive_sigma"] for row in values])
        for year in sorted(set(years)):
            selected = years == year
            axis.errorbar(
                np.full(np.sum(selected), year) + np.linspace(-0.18, 0.18, np.sum(selected)),
                predicted[selected],
                yerr=1.96 * sigma[selected],
                fmt="o",
                color="#5b3c88",
                alpha=0.75,
                markersize=3,
            )
            axis.scatter(
                np.full(np.sum(selected), year),
                observed[selected],
                marker="x",
                color="#d1495b",
                s=20,
            )
        axis.set_title(name.replace("_", " "), fontsize=9)
        axis.set_xticks([2015, 2018, 2021, 2024])
        axis.grid(alpha=0.2)
        axis.spines[["top", "right"]].set_visible(False)
    axes.flat[0].errorbar([], [], yerr=[], fmt="o", color="#5b3c88", label="forecast ±95%")
    axes.flat[0].scatter([], [], marker="x", color="#d1495b", label="observed")
    axes.flat[0].legend(frameon=False, fontsize=8, loc="upper left")
    figure.supxlabel("Held-out epoch")
    figure.supylabel("Parallel trail fraction")
    figure.suptitle("Forward-chaining historical baseline forecasts")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main():
    root = Path.cwd()
    outcome_path = root / "results/hst_replication/primary.json"
    exposure_path = root / "results/environment/monthly_exposure.json"
    protocol_path = root / "docs/BASELINE_PROTOCOL.md"
    outcomes = json.loads(outcome_path.read_text())["measurements"]
    exposure = json.loads(exposure_path.read_text())["measurements"]
    joined = join_inputs(outcomes, exposure)
    predictions, metrics = evaluate_forward_chaining(joined)
    best_rmse = min(value["rmse"] for value in metrics.values())
    best_nlpd = min(value["mean_negative_log_predictive_density"] for value in metrics.values())
    b0 = metrics["B0_calendar_linear"]
    exposure_support = any(
        metrics[name]["rmse"] < b0["rmse"]
        and metrics[name]["mean_negative_log_predictive_density"]
        < b0["mean_negative_log_predictive_density"]
        for name in ("B3_cumulative_particle", "B4_event_background")
    )
    result = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "source_sha256": sha256(root / "src/lattice/baselines.py"),
        "protocol_sha256": sha256(protocol_path),
        "outcome_sha256": sha256(outcome_path),
        "exposure_sha256": sha256(exposure_path),
        "evidence": "INFERRED FORECAST SCORES FROM OBSERVED HISTORICAL SUMMARIES",
        "folds": [
            {"test_year": year, "training_years": [value for value in range(2003, year, 3)]}
            for year in (2015, 2018, 2021, 2024)
        ],
        "joined_inputs": joined,
        "predictions": predictions,
        "metrics": metrics,
        "screens": {
            "all_models_complete": all(len(value) == 16 for value in predictions.values()),
            "exposure_model_beats_B0_on_rmse_and_nlpd": exposure_support,
            "physical_inference_gate": "CLOSED",
        },
        "future_advanced_model_thresholds": {
            "maximum_rmse": 0.95 * best_rmse,
            "maximum_mean_negative_log_predictive_density": best_nlpd,
            "minimum_interval_coverage": 0.75,
            "note": "Must satisfy every threshold on untouched temporal predictions.",
        },
    }
    output = root / "results/baselines"
    write_json(output / "historical_forward_chaining.json", result)
    make_figure(predictions, root / "paper/figures/baseline_forecasts")
    print(
        f"Scored {len(predictions)} baselines over 16 predictions each; "
        f"exposure support={exposure_support}; physical-inference gate=CLOSED"
    )


if __name__ == "__main__":
    main()
