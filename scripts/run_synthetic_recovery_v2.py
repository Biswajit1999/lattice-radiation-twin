"""Execute the frozen v2 100-replicate synthetic recovery checks."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chisquare

from lattice.cli import software_commit
from lattice.provenance import sha256, write_json
from lattice.state_space_v2 import (
    PHYSICAL_NAMES,
    PRIOR_LOG_SDS,
    PRIOR_MEDIANS,
    SIGNED_PRIOR_SDS,
    fit,
    laplace_covariance,
    simulate,
)

TRUTH = {
    "drift": 0.012,
    "chip_deviation": 0.002,
    "background_coefficient": 0.008,
    "event_coefficient": 0.018,
    "annealing_rate": 0.06,
    "pair_contrast": 0.010,
    "process_scale": 0.008,
    "observation_scale": 0.02,
}


def covariates(rng: np.random.Generator, epochs: int):
    background = np.zeros(epochs - 1)
    innovations = rng.normal(size=epochs - 1)
    for index in range(1, epochs - 1):
        background[index] = 0.65 * background[index - 1] + innovations[index]
    event = (rng.random(epochs - 1) < 0.16) * rng.lognormal(0.0, 0.35, epochs - 1)
    background = (background - np.mean(background)) / np.std(background)
    event = (event - np.mean(event)) / np.std(event)
    return background, event


def physical_samples(theta_samples: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "drift": np.exp(theta_samples[:, 0]),
        "chip_deviation": theta_samples[:, 1],
        "background_coefficient": np.exp(theta_samples[:, 2]),
        "event_coefficient": np.exp(theta_samples[:, 3]),
        "annealing_rate": np.exp(theta_samples[:, 4]),
        "pair_contrast": theta_samples[:, 5],
        "process_scale": np.exp(theta_samples[:, 6]),
        "observation_scale": np.exp(theta_samples[:, 7]),
    }


def one_replicate(index: int) -> dict:
    rng = np.random.default_rng(831_000 + index)
    epochs = 48
    times = np.arange(epochs, dtype=float)
    background, event = covariates(rng, epochs)
    data, states = simulate(TRUTH, times, background, event, rng)
    result = fit(data)
    covariance = laplace_covariance(data, result["theta"])
    posterior_rng = np.random.default_rng(1_091_000 + index)
    theta_samples = posterior_rng.multivariate_normal(
        result["theta"], covariance, size=512, check_valid="ignore"
    )
    samples = physical_samples(theta_samples)
    intervals = {
        name: [float(np.quantile(samples[name], 0.025)), float(np.quantile(samples[name], 0.975))]
        for name in PHYSICAL_NAMES
    }
    ranks = {name: int(np.sum(samples[name] < TRUTH[name])) for name in PHYSICAL_NAMES}
    parameters = result["parameters"]
    predicted_mean = (
        result["smoothed_mean"][:, :, None]
        + np.asarray([0.0, parameters["pair_contrast"]])[None, None, :]
    )
    state_variance = np.diagonal(result["smoothed_covariance"], axis1=1, axis2=2)
    predicted_sigma = np.sqrt(state_variance[:, :, None] + parameters["observation_scale"] ** 2)
    residual = np.abs(data.observations - predicted_mean)
    return {
        "replicate": index,
        "success": result["success"],
        "message": result["message"],
        "iterations": result["iterations"],
        "parameters": parameters,
        "intervals_95": intervals,
        "ranks_of_512": ranks,
        "latent_squared_error_sum": float(np.sum((result["smoothed_mean"] - states) ** 2)),
        "latent_value_count": int(states.size),
        "predictive_90_covered": int(np.sum(residual <= 1.6448536269514722 * predicted_sigma)),
        "predictive_95_covered": int(np.sum(residual <= 1.959963984540054 * predicted_sigma)),
        "predictive_value_count": int(residual.size),
    }


def draw_prior_parameters(rng: np.random.Generator) -> dict[str, float]:
    parameters = {
        name: float(rng.lognormal(np.log(PRIOR_MEDIANS[name]), PRIOR_LOG_SDS[name]))
        for name in PRIOR_MEDIANS
    }
    parameters["chip_deviation"] = float(rng.normal(0, SIGNED_PRIOR_SDS["chip_deviation"]))
    parameters["pair_contrast"] = float(rng.normal(0, SIGNED_PRIOR_SDS["pair_contrast"]))
    return parameters


def one_sbc_replicate(index: int) -> dict:
    rng = np.random.default_rng(1_331_000 + index)
    truth = draw_prior_parameters(rng)
    epochs = 48
    times = np.arange(epochs, dtype=float)
    background, event = covariates(rng, epochs)
    data, _ = simulate(truth, times, background, event, rng)
    result = fit(data)
    covariance = laplace_covariance(data, result["theta"])
    posterior_rng = np.random.default_rng(1_591_000 + index)
    theta_samples = posterior_rng.multivariate_normal(
        result["theta"], covariance, size=512, check_valid="ignore"
    )
    samples = physical_samples(theta_samples)
    return {
        "replicate": index,
        "truth": truth,
        "success": result["success"],
        "message": result["message"],
        "iterations": result["iterations"],
        "ranks_of_512": {name: int(np.sum(samples[name] < truth[name])) for name in PHYSICAL_NAMES},
    }


def prior_predictive(seed: int, draws: int = 1000) -> dict:
    rng = np.random.default_rng(seed)
    epochs = 48
    times = np.arange(epochs, dtype=float)
    background, event = covariates(rng, epochs)
    outside = 0
    total = 0
    minima = []
    maxima = []
    for _ in range(draws):
        data, _ = simulate(draw_prior_parameters(rng), times, background, event, rng)
        values = data.observations
        outside += int(np.sum((values < -0.25) | (values > 0.75)))
        total += values.size
        minima.append(float(np.min(values)))
        maxima.append(float(np.max(values)))
    fraction = outside / total
    return {
        "draws": draws,
        "values": total,
        "fraction_outside_minus_0_25_to_0_75": fraction,
        "minimum_quantile_01": float(np.quantile(minima, 0.01)),
        "maximum_quantile_99": float(np.quantile(maxima, 0.99)),
        "pass": fraction <= 0.01,
    }


def summarize_rank_checks(replicates: list[dict]) -> dict:
    checks = {}
    for name in PHYSICAL_NAMES:
        ranks = np.asarray([row["ranks_of_512"][name] for row in replicates])
        histogram, _ = np.histogram(ranks, bins=np.linspace(0, 512, 11))
        _, p_value = chisquare(histogram)
        edge_fraction = float(np.mean((ranks <= 25) | (ranks >= 487)))
        checks[name] = {
            "ten_bin_counts": histogram.tolist(),
            "chi_square_uniformity_p": float(p_value),
            "edge_fraction": edge_fraction,
            "pass": bool(p_value >= 0.01 and edge_fraction <= 0.20),
        }
    return checks


def summarize(replicates: list[dict], prior: dict, sbc_replicates: list[dict]) -> dict:
    successes = sum(row["success"] for row in replicates)
    coverage = {}
    estimates = {}
    for name in PHYSICAL_NAMES:
        estimates[name] = [row["parameters"][name] for row in replicates]
        coverage[name] = float(
            np.mean(
                [
                    row["intervals_95"][name][0] <= TRUTH[name] <= row["intervals_95"][name][1]
                    for row in replicates
                ]
            )
        )
    fixed_truth_rank_checks = summarize_rank_checks(replicates)
    sbc_rank_checks = summarize_rank_checks(sbc_replicates)
    sbc_successes = sum(row["success"] for row in sbc_replicates)
    overall_coverage = float(np.mean(list(coverage.values())))
    standardized_bias = {
        name: abs(float(np.mean(estimates[name])) - TRUTH[name])
        / max(float(np.std(estimates[name], ddof=1)), 1e-12)
        for name in (
            "drift",
            "event_coefficient",
            "background_coefficient",
            "annealing_rate",
        )
    }
    median_standardized_bias = float(np.median(list(standardized_bias.values())))
    latent_rmse = float(
        np.sqrt(
            sum(row["latent_squared_error_sum"] for row in replicates)
            / sum(row["latent_value_count"] for row in replicates)
        )
    )
    predictive_90 = sum(row["predictive_90_covered"] for row in replicates) / sum(
        row["predictive_value_count"] for row in replicates
    )
    predictive_95 = sum(row["predictive_95_covered"] for row in replicates) / sum(
        row["predictive_value_count"] for row in replicates
    )
    gates = {
        "prior_predictive": prior["pass"],
        "laplace_interval_coverage_at_least_0_90": overall_coverage >= 0.90,
        "median_standardized_bias_below_0_35": median_standardized_bias < 0.35,
        "latent_rmse_below_half_observation_noise": latent_rmse < 0.0100,
        "predictive_90_coverage_in_range": 0.85 <= predictive_90 <= 0.95,
        "predictive_95_coverage_in_range": 0.90 <= predictive_95 <= 0.99,
        "optimizer_success_at_least_95": successes >= 95,
        "simulation_based_calibration": all(value["pass"] for value in sbc_rank_checks.values()),
        "sbc_optimizer_success_at_least_95": sbc_successes >= 95,
    }
    return {
        "truth": TRUTH,
        "replicate_count": len(replicates),
        "optimizer_successes": successes,
        "sbc_replicate_count": len(sbc_replicates),
        "sbc_optimizer_successes": sbc_successes,
        "parameter_estimates": {
            name: {
                "mean": float(np.mean(values)),
                "standard_deviation": float(np.std(values, ddof=1)),
                "median": float(np.median(values)),
            }
            for name, values in estimates.items()
        },
        "laplace_interval_coverage_95": coverage,
        "overall_laplace_interval_coverage_95": overall_coverage,
        "standardized_ensemble_bias": standardized_bias,
        "median_absolute_standardized_ensemble_bias": median_standardized_bias,
        "latent_state_rmse": latent_rmse,
        "posterior_predictive_90_coverage": predictive_90,
        "posterior_predictive_95_coverage": predictive_95,
        "fixed_truth_rank_checks": fixed_truth_rank_checks,
        "sbc_rank_checks": sbc_rank_checks,
        "prior_predictive": prior,
        "gates": gates,
        "synthetic_recovery_gate": "PASS" if all(gates.values()) else "FAIL",
    }


def make_figure(summary: dict, output: Path) -> None:
    names = list(PHYSICAL_NAMES)
    biases = [
        (summary["parameter_estimates"][name]["mean"] - TRUTH[name])
        / max(summary["parameter_estimates"][name]["standard_deviation"], 1e-12)
        for name in names
    ]
    coverage = [summary["laplace_interval_coverage_95"][name] for name in names]
    figure, axes = plt.subplots(1, 2, figsize=(10.2, 4.4), constrained_layout=True)
    axes[0].barh(names, biases, color="#5b3c88")
    axes[0].axvline(0, color="black", linewidth=0.8)
    axes[0].set_xlabel("ensemble bias / empirical SD")
    axes[0].set_title("V2 synthetic parameter recovery")
    axes[1].barh(names, coverage, color="#2a9d8f")
    axes[1].axvline(0.90, color="#d1495b", linestyle="--", linewidth=1)
    axes[1].set_xlim(0, 1)
    axes[1].set_xlabel("nominal 95% interval coverage")
    axes[1].set_title("V2 Laplace interval calibration")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicates", type=int, default=100)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.replicates < 100:
        raise ValueError("The frozen v2 protocol requires at least 100 recovery replicates")
    print(f"Running {args.replicates} v2 recovery replicates with {args.workers} workers")
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        replicates = list(pool.map(one_replicate, range(args.replicates)))
        print(f"Running {args.replicates} prior-drawn SBC replicates")
        sbc_replicates = list(pool.map(one_sbc_replicate, range(args.replicates)))
    prior = prior_predictive(541_902)
    result = summarize(replicates, prior, sbc_replicates)
    root = Path.cwd()
    result.update(
        model_version="V2_REFERENCE_ANCHORED_LOG_PRIORS",
        software_commit=software_commit(root),
        script_sha256=sha256(Path(__file__)),
        source_sha256=sha256(root / "src/lattice/state_space_v2.py"),
        protocol_sha256=sha256(root / "docs/CORE_MODEL_V2_PROTOCOL.md"),
        v1_result_sha256=sha256(root / "results/core_model/synthetic_recovery.json"),
        ablation_result_sha256=sha256(root / "results/core_model/synthetic_ablations.json"),
        evidence="SIMULATED",
        observational_fit="NOT RUN",
        physical_inference_gate="CLOSED",
        replicate_details=replicates,
        sbc_replicate_details=sbc_replicates,
    )
    output = root / "results/core_model"
    write_json(output / "synthetic_recovery_v2.json", result)
    make_figure(result, root / "paper/figures/synthetic_recovery_v2")
    print(
        f"V2 synthetic recovery gate={result['synthetic_recovery_gate']}; "
        f"optimizer successes={result['optimizer_successes']}/{args.replicates}; "
        "observational fit=NOT RUN"
    )


if __name__ == "__main__":
    main()
