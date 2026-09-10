"""Execute the frozen 100-replicate synthetic recovery and predictive checks."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chisquare

from lattice.cli import software_commit
from lattice.provenance import sha256, write_json
from lattice.state_space import fit, laplace_covariance, simulate

PHYSICAL_NAMES = (
    "drift",
    "chip_deviation",
    "background_coefficient",
    "event_coefficient",
    "annealing_rate",
    "pair2_offset",
    "pair3_offset",
    "process_scale",
    "observation_scale",
)
TRUTH = {
    "drift": 0.012,
    "chip_deviation": 0.002,
    "background_coefficient": 0.008,
    "event_coefficient": 0.018,
    "annealing_rate": 0.06,
    "pair2_offset": 0.015,
    "pair3_offset": 0.025,
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
    values = {name: theta_samples[:, index] for index, name in enumerate(PHYSICAL_NAMES[:4])}
    values["pair2_offset"] = theta_samples[:, 5]
    values["pair3_offset"] = theta_samples[:, 6]
    values["annealing_rate"] = np.exp(theta_samples[:, 4])
    values["process_scale"] = np.exp(theta_samples[:, 7])
    values["observation_scale"] = np.exp(theta_samples[:, 8])
    return values


def one_replicate(index: int) -> dict:
    rng = np.random.default_rng(731_000 + index)
    epochs = 48
    times = np.arange(epochs, dtype=float)
    background, event = covariates(rng, epochs)
    data, states = simulate(TRUTH, times, background, event, rng)
    result = fit(data)
    covariance = laplace_covariance(data, result["theta"])
    posterior_rng = np.random.default_rng(991_000 + index)
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
        + np.asarray([parameters["pair2_offset"], parameters["pair3_offset"]])[None, None, :]
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
        parameters = {
            "drift": rng.normal(0, 0.05),
            "chip_deviation": rng.normal(0, 0.025),
            "background_coefficient": rng.normal(0, 0.05),
            "event_coefficient": rng.normal(0, 0.05),
            "annealing_rate": abs(rng.normal(0, 0.2)),
            "pair2_offset": rng.normal(0, 0.1),
            "pair3_offset": rng.normal(0, 0.1),
            "process_scale": abs(rng.normal(0, 0.03)) + 1e-6,
            "observation_scale": abs(rng.normal(0, 0.05)) + 1e-6,
        }
        data, _ = simulate(parameters, times, background, event, rng)
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


def summarize(replicates: list[dict], prior: dict) -> dict:
    successes = sum(row["success"] for row in replicates)
    coverage = {}
    rank_checks = {}
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
        ranks = np.asarray([row["ranks_of_512"][name] for row in replicates])
        histogram, _ = np.histogram(ranks, bins=np.linspace(0, 512, 11))
        _, p_value = chisquare(histogram)
        edge_fraction = float(np.mean((ranks <= 25) | (ranks >= 487)))
        rank_checks[name] = {
            "ten_bin_counts": histogram.tolist(),
            "chi_square_uniformity_p": float(p_value),
            "edge_fraction": edge_fraction,
            "pass": bool(p_value >= 0.01 and edge_fraction <= 0.20),
        }
    all_coverage = float(np.mean(list(coverage.values())))
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
        "laplace_interval_coverage_at_least_0_90": all_coverage >= 0.90,
        "median_standardized_bias_below_0_35": median_standardized_bias < 0.35,
        "latent_rmse_below_half_observation_noise": (
            latent_rmse < 0.5 * TRUTH["observation_scale"]
        ),
        "predictive_90_coverage_in_range": 0.85 <= predictive_90 <= 0.95,
        "predictive_95_coverage_in_range": 0.90 <= predictive_95 <= 0.99,
        "optimizer_success_at_least_95": successes >= 95,
        "simulation_based_calibration": all(value["pass"] for value in rank_checks.values()),
    }
    return {
        "truth": TRUTH,
        "replicate_count": len(replicates),
        "optimizer_successes": successes,
        "parameter_estimates": {
            name: {
                "mean": float(np.mean(values)),
                "standard_deviation": float(np.std(values, ddof=1)),
                "median": float(np.median(values)),
            }
            for name, values in estimates.items()
        },
        "laplace_interval_coverage_95": coverage,
        "overall_laplace_interval_coverage_95": all_coverage,
        "standardized_ensemble_bias": standardized_bias,
        "median_absolute_standardized_ensemble_bias": median_standardized_bias,
        "latent_state_rmse": latent_rmse,
        "posterior_predictive_90_coverage": predictive_90,
        "posterior_predictive_95_coverage": predictive_95,
        "sbc_rank_checks": rank_checks,
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
    axes[0].set_title("Synthetic parameter recovery")
    axes[1].barh(names, coverage, color="#2a9d8f")
    axes[1].axvline(0.90, color="#d1495b", linestyle="--", linewidth=1)
    axes[1].set_xlim(0, 1)
    axes[1].set_xlabel("nominal 95% interval coverage")
    axes[1].set_title("Laplace interval calibration")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicates", type=int, default=100)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.replicates < 100:
        raise ValueError("The frozen protocol requires at least 100 recovery replicates")
    print(f"Running {args.replicates} recovery replicates with {args.workers} workers")
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        replicates = list(pool.map(one_replicate, range(args.replicates)))
    prior = prior_predictive(441_902)
    result = summarize(replicates, prior)
    root = Path.cwd()
    result.update(
        software_commit=software_commit(root),
        script_sha256=sha256(Path(__file__)),
        source_sha256=sha256(root / "src/lattice/state_space.py"),
        protocol_sha256=sha256(root / "docs/CORE_MODEL_PROTOCOL.md"),
        evidence="SIMULATED",
        observational_fit="NOT RUN",
        physical_inference_gate="CLOSED",
        replicate_details=replicates,
    )
    output = root / "results/core_model"
    write_json(output / "synthetic_recovery.json", result)
    make_figure(result, root / "paper/figures/synthetic_recovery")
    print(
        f"Synthetic recovery gate={result['synthetic_recovery_gate']}; "
        f"optimizer successes={result['optimizer_successes']}/{args.replicates}; "
        "observational fit=NOT RUN"
    )


if __name__ == "__main__":
    main()
