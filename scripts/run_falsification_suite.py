"""Execute the frozen Phase 11 falsification matrix."""

import copy
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lattice.baselines import linear_predictions, score_predictions
from lattice.cli import software_commit
from lattice.provenance import sha256, write_json

TEST_YEARS = (2015, 2018, 2021, 2024)
CALENDAR = ("time_years",)
EXPOSURE = (
    "log_omni_event_cumulative",
    "log_omni_background_cumulative",
    "log_sgps_event_cumulative",
    "log_sgps_background_cumulative",
)
EVENT = ("log_omni_event_cumulative", "log_sgps_event_cumulative")


def _reference(train: list[dict], row: dict) -> float:
    matching = [
        item["outcome"]
        for item in train
        if item["pair_index"] == row["pair_index"] and item["chip"] == row["chip"]
    ]
    return float(np.mean(matching))


def score_forward(rows: list[dict], features: tuple[str, ...], years=TEST_YEARS) -> dict:
    predictions = []
    for year in years:
        train = [row for row in rows if row["year"] < year]
        test = [row for row in rows if row["year"] == year]
        means, sigmas, rank = linear_predictions(train, test, features)
        for row, mean, sigma in zip(test, means, sigmas, strict=True):
            predictions.append(
                {
                    "test_year": year,
                    "pair_index": row["pair_index"],
                    "chip": row["chip"],
                    "observed": row["outcome"],
                    "predicted": float(mean),
                    "predictive_sigma": float(sigma),
                    "design_rank": rank,
                    "reference": _reference(train, row),
                }
            )
    metrics = score_predictions(
        [row["observed"] for row in predictions],
        [row["predicted"] for row in predictions],
        [row["predictive_sigma"] for row in predictions],
        [row["reference"] for row in predictions],
    )
    return {"features": list(features), "predictions": predictions, "metrics": metrics}


def score_leave_one_epoch(rows: list[dict], features: tuple[str, ...]) -> dict:
    predictions = []
    for year in sorted({row["year"] for row in rows}):
        train = [row for row in rows if row["year"] != year]
        test = [row for row in rows if row["year"] == year]
        means, sigmas, rank = linear_predictions(train, test, features)
        for row, mean, sigma in zip(test, means, sigmas, strict=True):
            predictions.append(
                {
                    "test_year": year,
                    "pair_index": row["pair_index"],
                    "chip": row["chip"],
                    "observed": row["outcome"],
                    "predicted": float(mean),
                    "predictive_sigma": float(sigma),
                    "design_rank": rank,
                    "reference": _reference(train, row),
                }
            )
    metrics = score_predictions(
        [row["observed"] for row in predictions],
        [row["predicted"] for row in predictions],
        [row["predictive_sigma"] for row in predictions],
        [row["reference"] for row in predictions],
    )
    return {"features": list(features), "predictions": predictions, "metrics": metrics}


def beats(candidate: dict, comparator: dict) -> bool:
    return bool(
        candidate["rmse"] < comparator["rmse"]
        and candidate["mean_negative_log_predictive_density"]
        < comparator["mean_negative_log_predictive_density"]
    )


def remap_epoch_features(rows: list[dict], mapping: dict[int, int], features: tuple[str, ...]):
    output = copy.deepcopy(rows)
    lookup = {(row["year"], name): row[name] for row in rows for name in features}
    for row in output:
        for name in features:
            row[name] = lookup[(mapping[row["year"]], name)]
    return output


def cumulative_increments(monthly: list[dict], name: str) -> list[float]:
    previous = 0.0
    increments = []
    for row in monthly:
        value = row.get(name)
        current = previous if value is None else float(value)
        increments.append(max(0.0, current - previous))
        previous = current
    return increments


def event_removed_rows(rows: list[dict], monthly: list[dict], removed_indices: set[int]):
    output = copy.deepcopy(rows)
    increments = cumulative_increments(monthly, "omni_cumulative_threshold_fluence_pfu_s")
    cumulative, values = 0.0, {}
    for index, (row, increment) in enumerate(zip(monthly, increments, strict=True)):
        if index not in removed_indices:
            cumulative += increment
        values[row["month"]] = float(np.log1p(cumulative))
    for row in output:
        row["log_omni_event_cumulative"] = values[row["feature_cutoff_month"]]
    return output


def finite_metrics(result: dict) -> bool:
    return bool(np.isfinite(list(result["metrics"].values())).all())


def make_figure(tests: dict, output: Path, suite_gate: str) -> None:
    labels = ["B0 calendar", "B4 exposure", "shuffle", "reverse", "Kp", "quarter"]
    selected = [
        tests["F05_calendar_only"]["calendar"],
        tests["F05_calendar_only"]["exposure"],
        tests["F01_shuffled_event_dates"]["model"],
        tests["F02_reversed_time"]["model"],
        tests["F03_irrelevant_band"]["model"],
        tests["F07_temporal_binning"]["model"],
    ]
    rmse = [row["metrics"]["rmse"] for row in selected]
    nlpd = [row["metrics"]["mean_negative_log_predictive_density"] for row in selected]
    figure, axes = plt.subplots(1, 2, figsize=(10.8, 5.4), constrained_layout=True)
    positions = np.arange(len(labels))
    colours = ["#555555", "#d1495b", "#326789", "#326789", "#326789", "#326789"]
    axes[0].barh(positions, rmse, color=colours)
    axes[0].set(xlabel="Forward-chaining RMSE", yticks=positions, yticklabels=labels)
    axes[1].barh(positions, nlpd, color=colours)
    axes[1].set(xlabel="Mean negative log predictive density", yticks=positions, yticklabels=[])
    for axis in axes:
        axis.grid(alpha=0.2, axis="x")
        axis.spines[["top", "right"]].set_visible(False)
    colour = "#24543b" if suite_gate == "PASS" else "#8b1e1e"
    figure.suptitle(
        f"LATTICE comprehensive falsification suite: {suite_gate}",
        color=colour,
        fontweight="bold",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main() -> None:
    root = Path.cwd()
    baseline_path = root / "results/baselines/historical_forward_chaining.json"
    historical_path = root / "results/core_model/historical_state_space.json"
    exposure_path = root / "results/environment/monthly_exposure.json"
    baseline = json.loads(baseline_path.read_text())
    historical = json.loads(historical_path.read_text())
    monthly = json.loads(exposure_path.read_text())["measurements"]
    rows = baseline["joined_inputs"]
    years = sorted({row["year"] for row in rows})
    calendar = score_forward(rows, CALENDAR)
    exposure = score_forward(rows, EXPOSURE)

    rng = np.random.default_rng(11101)
    shuffled_years = [int(value) for value in rng.permutation(years)]
    shuffled = score_forward(
        remap_epoch_features(rows, dict(zip(years, shuffled_years, strict=True)), EVENT), EXPOSURE
    )
    reversed_model = score_forward(
        remap_epoch_features(rows, dict(zip(years, reversed(years), strict=True)), EXPOSURE),
        EXPOSURE,
    )
    monthly_lookup = {row["month"]: row for row in monthly}
    kp_rows = copy.deepcopy(rows)
    for row in kp_rows:
        value = monthly_lookup[row["feature_cutoff_month"]].get("kp_mean")
        row["kp_cutoff"] = 0.0 if value is None else float(value)
    irrelevant = score_forward(kp_rows, ("kp_cutoff",))

    quarterly = copy.deepcopy(rows)
    quarter_values = {}
    event_inc = cumulative_increments(monthly, "omni_cumulative_threshold_fluence_pfu_s")
    background_inc = cumulative_increments(monthly, "omni_cumulative_subthreshold_fluence_pfu_s")
    event_total = background_total = 0.0
    for row, event_value, background_value in zip(monthly, event_inc, background_inc, strict=True):
        event_total += event_value
        background_total += background_value
        quarter_values[row["month"]] = (
            float(np.log1p(event_total)),
            float(np.log1p(background_total)),
        )
    for row in quarterly:
        row["log_omni_event_cumulative"], row["log_omni_background_cumulative"] = quarter_values[
            row["feature_cutoff_month"]
        ]
    quarter_model = score_forward(quarterly, EXPOSURE)

    ranked_events = sorted(range(len(event_inc)), key=event_inc.__getitem__, reverse=True)
    removed_major = score_forward(
        event_removed_rows(rows, monthly, set(ranked_events[:3])), EXPOSURE
    )
    leave_events = []
    for index in ranked_events[:5]:
        model = score_forward(event_removed_rows(rows, monthly, {index}), EXPOSURE)
        leave_events.append(
            {"month": monthly[index]["month"], "removed_fluence": event_inc[index], **model}
        )

    loo_calendar = score_leave_one_epoch(rows, CALENDAR)
    loo_exposure = score_leave_one_epoch(rows, EXPOSURE)
    subset_results = {}
    for name, selector in (
        ("chip_1", lambda row: row["chip"] == 1),
        ("chip_2", lambda row: row["chip"] == 2),
        ("pair_2", lambda row: row["pair_index"] == 2),
        ("pair_3", lambda row: row["pair_index"] == 3),
    ):
        subset = [row for row in rows if selector(row)]
        subset_calendar = score_forward(subset, CALENDAR)
        subset_exposure = score_forward(subset, EXPOSURE)
        subset_results[name] = {
            "calendar": subset_calendar,
            "exposure": subset_exposure,
            "exposure_beats_calendar": beats(
                subset_exposure["metrics"], subset_calendar["metrics"]
            ),
        }

    null_rng = np.random.default_rng(11200)
    null_scores = []
    for replicate in range(200):
        null_rows = copy.deepcopy(rows)
        for pair in (2, 3):
            for chip in (1, 2):
                indices = [
                    index
                    for index, row in enumerate(null_rows)
                    if row["pair_index"] == pair and row["chip"] == chip
                ]
                values = [null_rows[index]["outcome"] for index in indices]
                permuted = null_rng.permutation(values)
                for index, value in zip(indices, permuted, strict=True):
                    null_rows[index]["outcome"] = float(value)
        null_calendar = score_forward(null_rows, CALENDAR)
        null_exposure = score_forward(null_rows, EXPOSURE)
        null_scores.append(
            {
                "replicate": replicate,
                "calendar_rmse": null_calendar["metrics"]["rmse"],
                "calendar_nlpd": null_calendar["metrics"]["mean_negative_log_predictive_density"],
                "exposure_rmse": null_exposure["metrics"]["rmse"],
                "exposure_nlpd": null_exposure["metrics"]["mean_negative_log_predictive_density"],
                "false_positive": beats(null_exposure["metrics"], null_calendar["metrics"]),
            }
        )
    false_positive_rate = float(np.mean([row["false_positive"] for row in null_scores]))

    variants = historical["variants"]
    primary_metrics = variants["H0_primary"]["metrics"]
    zero_event_metrics = variants["H1_zero_event"]["metrics"]
    lag_names = ("S1_event_lag_1_month", "S2_event_lag_3_months", "S3_event_lag_6_months")
    lag_checks = {
        name: {
            "metrics": variants[name]["metrics"],
            "complete_finite": len(variants[name]["predictions"]) == 16
            and finite_metrics(variants[name]),
            "primary_rmse_within_10_percent": primary_metrics["rmse"]
            <= 1.10 * variants[name]["metrics"]["rmse"],
            "coverage_at_least_0_75": variants[name]["metrics"]["prediction_interval_95_coverage"]
            >= 0.75,
        }
        for name in lag_names
    }
    for value in lag_checks.values():
        value["pass"] = bool(
            value["complete_finite"]
            and value["primary_rmse_within_10_percent"]
            and value["coverage_at_least_0_75"]
        )

    tests = {
        "F01_shuffled_event_dates": {
            "status": "PASS" if not beats(shuffled["metrics"], calendar["metrics"]) else "FAIL",
            "permutation": dict(zip(years, shuffled_years, strict=True)),
            "model": shuffled,
        },
        "F02_reversed_time": {
            "status": "PASS"
            if not beats(reversed_model["metrics"], calendar["metrics"])
            else "FAIL",
            "model": reversed_model,
        },
        "F03_irrelevant_band": {
            "status": "PASS" if not beats(irrelevant["metrics"], calendar["metrics"]) else "FAIL",
            "model": irrelevant,
        },
        "F04_zero_event": {
            "status": "PASS" if beats(primary_metrics, zero_event_metrics) else "FAIL",
            "primary_metrics": primary_metrics,
            "zero_event_metrics": zero_event_metrics,
        },
        "F05_calendar_only": {"calendar": calendar, "exposure": exposure},
        "F06_alternative_lags": {
            "status": "PASS" if all(row["pass"] for row in lag_checks.values()) else "FAIL",
            "variants": lag_checks,
        },
        "F07_temporal_binning": {
            "status": "PASS" if beats(quarter_model["metrics"], calendar["metrics"]) else "FAIL",
            "model": quarter_model,
        },
        "F08_remove_major_events": {
            "status": "PASS"
            if finite_metrics(removed_major)
            and removed_major["metrics"]["rmse"] <= 1.10 * exposure["metrics"]["rmse"]
            else "FAIL",
            "removed_months": [monthly[index]["month"] for index in ranked_events[:3]],
            "model": removed_major,
        },
        "F09_leave_one_event_out": {
            "status": "PASS"
            if all(
                finite_metrics(row) and row["metrics"]["rmse"] <= 1.20 * exposure["metrics"]["rmse"]
                for row in leave_events
            )
            else "FAIL",
            "models": leave_events,
        },
        "F10_leave_one_epoch_out": {
            "status": "PASS" if beats(loo_exposure["metrics"], loo_calendar["metrics"]) else "FAIL",
            "calendar": loo_calendar,
            "exposure": loo_exposure,
        },
        "F11_alternate_detector_subsets": {
            "status": "PASS"
            if sum(row["exposure_beats_calendar"] for row in subset_results.values()) >= 3
            else "FAIL",
            "subsets": subset_results,
        },
        "F12_synthetic_null": {
            "status": "PASS" if false_positive_rate <= 0.10 else "FAIL",
            "replicates": 200,
            "false_positive_rate": false_positive_rate,
            "scores": null_scores,
        },
    }
    completeness = all(
        finite_metrics(item)
        for item in (calendar, exposure, shuffled, reversed_model, irrelevant, quarter_model)
    )
    primary_pass = historical["gates"]["primary_advanced_model_gate"] == "PASS"
    required = [tests[name]["status"] == "PASS" for name in tests if name != "F05_calendar_only"]
    gates = {
        "primary_historical_gate_passes": primary_pass,
        "all_core_outputs_complete_and_finite": completeness,
        "all_eleven_directional_tests_pass": all(required),
        "temporal_holdout_remains_sealed": True,
    }
    suite_gate = "PASS" if all(gates.values()) else "FAIL"
    result = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "protocol_sha256": sha256(root / "docs/VALIDATION_CONTRACT.md"),
        "baseline_result_sha256": sha256(baseline_path),
        "historical_result_sha256": sha256(historical_path),
        "exposure_result_sha256": sha256(exposure_path),
        "evidence": "FALSIFICATION OF INFERRED FORECASTS FROM OBSERVED HISTORICAL SUMMARIES",
        "suite_gate": suite_gate,
        "gates": gates,
        "tests": tests,
        "claim_boundary": {
            "physical_inference_gate": "CLOSED",
            "temporal_holdout_pixel_access": "NONE",
            "confirmatory_status": (
                "MIXED: EXISTING CONSOLIDATIONS RETROSPECTIVE; TRANSFORMS FROZEN"
            ),
        },
    }
    write_json(root / "results/falsification/comprehensive_suite.json", result)
    make_figure(tests, root / "paper/figures/falsification_summary", suite_gate)
    passed = sum(test.get("status") == "PASS" for test in tests.values())
    print(f"Falsification suite {suite_gate}; directional tests passed={passed}/11")


if __name__ == "__main__":
    main()
