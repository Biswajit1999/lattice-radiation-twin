"""Run the frozen observational HST state-space validation experiment."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lattice.cli import software_commit
from lattice.historical_state_space import (
    FIXED_ZERO_VARIANTS,
    SENSITIVITY_VARIANTS,
    TEST_YEARS,
    ObservationalStateSpaceModel,
    build_fold,
    score_historical_predictions,
)
from lattice.provenance import sha256, write_json

BURN_IN = 100
DRAWS_PER_CHAIN = 2000
BASE_SEED = 2_831_000
PRIMARY_MAXIMUM_RMSE = 0.038231325787485455
PRIMARY_MAXIMUM_NLPD = -1.782393718891921
PRIMARY_MINIMUM_COVERAGE = 0.75


def run_variant(
    name: str,
    outcomes: list[dict],
    exposure: list[dict],
    variant_index: int,
    fixed_zero: tuple[str, ...] = (),
    settings: dict | None = None,
) -> dict:
    settings = settings or {}
    model = ObservationalStateSpaceModel(fixed_zero)
    predictions = []
    folds = []
    for fold_index, test_year in enumerate(TEST_YEARS):
        fold = build_fold(outcomes, exposure, test_year, **settings)
        seed = BASE_SEED + 100_000 * variant_index + 100 * fold_index
        posterior = model.sample(
            fold.training_data,
            seed,
            burn_in=BURN_IN,
            draws_per_chain=DRAWS_PER_CHAIN,
        )
        forecast = model.forecast(
            fold.training_data,
            fold.test_time,
            fold.test_background,
            fold.test_event,
            fold.measurement_se,
            posterior["theta"],
            seed + 50,
        )
        observed = fold.observed.reshape(-1)
        reference = np.mean(fold.training_data.observations, axis=0).reshape(-1)
        for position, (chip, pair_index) in enumerate(((1, 2), (1, 3), (2, 2), (2, 3))):
            predictions.append(
                {
                    "test_year": test_year,
                    "chip": chip,
                    "pair_index": pair_index,
                    "observed": float(observed[position]),
                    "predicted": float(forecast["mean"][position]),
                    "predictive_sigma": float(forecast["standard_deviation"][position]),
                    "lower_95": float(forecast["lower_95"][position]),
                    "upper_95": float(forecast["upper_95"][position]),
                    "reference": float(reference[position]),
                }
            )
        physical_draws = [model.unpack(theta) for theta in posterior["theta"]]
        folds.append(
            {
                "test_year": test_year,
                "training_years": list(fold.training_years),
                "feature_metadata": fold.feature_metadata,
                "test_background": fold.test_background,
                "test_event": fold.test_event,
                "usable_chains": posterior["usable_chains"],
                "map_success": posterior["map_success"],
                "map_message": posterior["map_message"],
                "map_iterations": posterior["map_iterations"],
                "sampling_acceptance": posterior["sampling_acceptance"],
                "warmup_acceptance": posterior["warmup_acceptance"],
                "chain_diagnostics": posterior["chain_diagnostics"],
                "posterior_parameters": {
                    parameter: {
                        "mean": float(np.mean([row[parameter] for row in physical_draws])),
                        "lower_95": float(
                            np.quantile([row[parameter] for row in physical_draws], 0.025)
                        ),
                        "upper_95": float(
                            np.quantile([row[parameter] for row in physical_draws], 0.975)
                        ),
                    }
                    for parameter in model.active_physical_names
                },
            }
        )
        print(f"{name}: {test_year} complete", flush=True)
    return {
        "name": name,
        "fixed_zero": list(fixed_zero),
        "settings": settings,
        "folds": folds,
        "predictions": predictions,
        "metrics": score_historical_predictions(predictions),
        "all_folds_usable": all(row["usable_chains"] for row in folds),
    }


def evaluate_gates(results: dict[str, dict]) -> dict:
    primary = results["H0_primary"]
    metrics = primary["metrics"]
    finite = all(
        np.isfinite(row["predicted"])
        and np.isfinite(row["predictive_sigma"])
        and row["predictive_sigma"] > 0
        for row in primary["predictions"]
    )
    primary_checks = {
        "all_four_folds_usable": primary["all_folds_usable"],
        "sixteen_finite_positive_variance_predictions": len(primary["predictions"]) == 16
        and finite,
        "rmse_at_most_frozen_threshold": metrics["rmse"] <= PRIMARY_MAXIMUM_RMSE,
        "nlpd_below_frozen_threshold": metrics["mean_negative_log_predictive_density"]
        < PRIMARY_MAXIMUM_NLPD,
        "interval_coverage_at_least_0_75": metrics["prediction_interval_95_coverage"]
        >= PRIMARY_MINIMUM_COVERAGE,
    }
    ablation_support = {}
    for label, variant in (
        ("event", "H1_zero_event"),
        ("background", "H2_zero_background"),
    ):
        reduced = results[variant]["metrics"]
        ablation_support[label] = {
            "lower_rmse_than_exact_zero": metrics["rmse"] < reduced["rmse"],
            "lower_nlpd_than_exact_zero": metrics["mean_negative_log_predictive_density"]
            < reduced["mean_negative_log_predictive_density"],
        }
        ablation_support[label]["supported"] = all(ablation_support[label].values())
    sensitivity = {}
    for name in SENSITIVITY_VARIANTS:
        result = results[name]
        variant_metrics = result["metrics"]
        finite_variant = all(
            np.isfinite(row["predicted"])
            and np.isfinite(row["predictive_sigma"])
            and row["predictive_sigma"] > 0
            for row in result["predictions"]
        )
        sensitivity[name] = {
            "finite": len(result["predictions"]) == 16 and finite_variant,
            "coverage_at_least_0_75": variant_metrics["prediction_interval_95_coverage"] >= 0.75,
            "rmse_within_10_percent_of_primary": variant_metrics["rmse"] <= 1.10 * metrics["rmse"],
        }
        sensitivity[name]["pass"] = all(sensitivity[name].values())
    primary_pass = all(primary_checks.values())
    attribution_robust = (
        primary_pass
        and all(value["supported"] for value in ablation_support.values())
        and all(value["pass"] for value in sensitivity.values())
    )
    return {
        "primary_checks": primary_checks,
        "primary_advanced_model_gate": "PASS" if primary_pass else "FAIL",
        "exact_zero_exposure_support": ablation_support,
        "sensitivity_checks": sensitivity,
        "exposure_attribution_robustness": "PASS" if attribution_robust else "FAIL",
        "physical_inference_gate": "CLOSED",
        "temporal_holdout": "SEALED",
    }


def make_forecast_figure(primary: dict, output: Path) -> None:
    predictions = primary["predictions"]
    figure, axis = plt.subplots(figsize=(8.4, 4.8), constrained_layout=True)
    for year in TEST_YEARS:
        rows = [row for row in predictions if row["test_year"] == year]
        positions = year + np.linspace(-0.18, 0.18, len(rows))
        means = np.asarray([row["predicted"] for row in rows])
        lower = np.asarray([row["lower_95"] for row in rows])
        upper = np.asarray([row["upper_95"] for row in rows])
        axis.errorbar(
            positions,
            means,
            yerr=np.vstack((means - lower, upper - means)),
            fmt="o",
            color="#5b3c88",
            markersize=4,
        )
        axis.scatter(
            np.full(len(rows), year),
            [row["observed"] for row in rows],
            marker="x",
            color="#d1495b",
        )
    axis.set(
        title="Historical v3 state-space forecasts",
        xlabel="Held-out epoch",
        ylabel="Parallel trail fraction",
        xticks=TEST_YEARS,
    )
    axis.grid(alpha=0.2)
    axis.spines[["top", "right"]].set_visible(False)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def make_sensitivity_figure(results: dict[str, dict], output: Path) -> None:
    names = list(results)
    rmse = [results[name]["metrics"]["rmse"] for name in names]
    nlpd = [results[name]["metrics"]["mean_negative_log_predictive_density"] for name in names]
    figure, axes = plt.subplots(1, 2, figsize=(11.2, 5.4), constrained_layout=True)
    positions = np.arange(len(names))
    axes[0].barh(positions, rmse, color="#5b3c88")
    axes[0].axvline(PRIMARY_MAXIMUM_RMSE, color="#d1495b", linestyle="--")
    axes[0].set(xlabel="RMSE", yticks=positions, yticklabels=names)
    axes[1].barh(positions, nlpd, color="#2a9d8f")
    axes[1].axvline(PRIMARY_MAXIMUM_NLPD, color="#d1495b", linestyle="--")
    axes[1].set(xlabel="Mean negative log predictive density", yticks=positions, yticklabels=[])
    for axis in axes:
        axis.grid(alpha=0.2, axis="x")
        axis.spines[["top", "right"]].set_visible(False)
    figure.suptitle("Frozen historical state-space ablations and sensitivities")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main() -> None:
    root = Path.cwd()
    outcome_path = root / "results/hst_replication/primary.json"
    exposure_path = root / "results/environment/monthly_exposure.json"
    outcomes = json.loads(outcome_path.read_text())["measurements"]
    exposure = json.loads(exposure_path.read_text())["measurements"]
    specifications = [("H0_primary", (), {})]
    specifications.extend((name, fixed, {}) for name, fixed in FIXED_ZERO_VARIANTS.items())
    specifications.extend((name, (), settings) for name, settings in SENSITIVITY_VARIANTS.items())
    results = {
        name: run_variant(name, outcomes, exposure, index, fixed, settings)
        for index, (name, fixed, settings) in enumerate(specifications)
    }
    gates = evaluate_gates(results)
    result = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "source_sha256": sha256(root / "src/lattice/historical_state_space.py"),
        "model_source_sha256": sha256(root / "src/lattice/state_space_v2.py"),
        "sampler_source_sha256": sha256(root / "src/lattice/posterior.py"),
        "baseline_source_sha256": sha256(root / "src/lattice/baselines.py"),
        "protocol_sha256": sha256(root / "docs/HISTORICAL_STATE_SPACE_PROTOCOL.md"),
        "outcome_sha256": sha256(outcome_path),
        "exposure_sha256": sha256(exposure_path),
        "v3_result_sha256": sha256(root / "results/core_model/synthetic_recovery_v3.json"),
        "evidence": "INFERRED FORECASTS FROM OBSERVED HISTORICAL SUMMARIES AND PROXY EXPOSURE",
        "sampler": {
            "chains": 2,
            "burn_in_per_chain": BURN_IN,
            "draws_per_chain": DRAWS_PER_CHAIN,
            "proposal": "multivariate_student_t_independence",
            "proposal_degrees_of_freedom": 5.0,
            "proposal_scale": 0.8,
        },
        "variants": results,
        "gates": gates,
        "observational_state_space_fit": "RUN",
        "temporal_holdout_pixel_access": "NOT RUN",
    }
    write_json(root / "results/core_model/historical_state_space.json", result)
    make_forecast_figure(results["H0_primary"], root / "paper/figures/historical_state_space")
    make_sensitivity_figure(results, root / "paper/figures/historical_state_space_sensitivity")
    print(
        f"Historical primary gate={gates['primary_advanced_model_gate']}; "
        f"attribution robustness={gates['exposure_attribution_robustness']}; "
        "physical-inference gate=CLOSED; temporal holdout=SEALED"
    )


if __name__ == "__main__":
    main()
