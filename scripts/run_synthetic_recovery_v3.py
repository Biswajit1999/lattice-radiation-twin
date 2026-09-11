"""Run frozen v3 exact-posterior recovery and canonical SBC."""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chisquare

from lattice.cli import software_commit
from lattice.posterior import chain_diagnostics, sample_independence_metropolis_t
from lattice.provenance import sha256, write_json
from lattice.state_space_v2 import (
    PARAMETER_NAMES,
    PHYSICAL_NAMES,
    PRIOR_LOG_SDS,
    PRIOR_MEDIANS,
    SIGNED_PRIOR_SDS,
    filter_and_smooth,
    fit,
    laplace_covariance,
    negative_log_posterior,
    simulate,
)

BURN_IN = 100
DRAWS_PER_CHAIN = 2000
CHAINS = 2
POSTERIOR_STATE_DRAWS = 64
PROPOSAL_DEGREES_OF_FREEDOM = 5.0
PROPOSAL_SCALE = 0.8
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


def draw_prior_parameters(rng: np.random.Generator) -> dict[str, float]:
    parameters = {
        name: float(rng.lognormal(np.log(PRIOR_MEDIANS[name]), PRIOR_LOG_SDS[name]))
        for name in PRIOR_MEDIANS
    }
    parameters["chip_deviation"] = float(rng.normal(0, SIGNED_PRIOR_SDS["chip_deviation"]))
    parameters["pair_contrast"] = float(rng.normal(0, SIGNED_PRIOR_SDS["pair_contrast"]))
    return parameters


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


def sample_parameters(data, base_seed: int) -> dict:
    fitted = fit(data)
    covariance = laplace_covariance(data, fitted["theta"])

    def log_posterior(theta):
        return -negative_log_posterior(theta, data)

    results = [
        sample_independence_metropolis_t(
            log_posterior,
            location=fitted["theta"],
            proposal_covariance=covariance,
            seed=base_seed + 10_000 * chain,
            burn_in=BURN_IN,
            draws=DRAWS_PER_CHAIN,
            degrees_of_freedom=PROPOSAL_DEGREES_OF_FREEDOM,
            scale=PROPOSAL_SCALE,
        )
        for chain in range(CHAINS)
    ]
    chains = np.asarray([row["draws"] for row in results])
    diagnostics = chain_diagnostics(chains, PARAMETER_NAMES)
    usable = all(
        value["rank_normalized_rhat"] <= 1.05 and value["bulk_effective_sample_size"] >= 100
        for value in diagnostics.values()
    )
    return {
        "theta": chains.reshape(-1, len(PARAMETER_NAMES)),
        "diagnostics": diagnostics,
        "usable": usable,
        "map_success": fitted["success"],
        "map_message": fitted["message"],
        "map_iterations": fitted["iterations"],
        "sampling_acceptance": [row["sampling_acceptance"] for row in results],
        "warmup_acceptance": [row["warmup_acceptance"] for row in results],
    }


def interval_and_ranks(samples: dict[str, np.ndarray], truth: dict[str, float]):
    intervals = {
        name: [float(np.quantile(samples[name], 0.025)), float(np.quantile(samples[name], 0.975))]
        for name in PHYSICAL_NAMES
    }
    ranks = {name: int(np.sum(samples[name] < truth[name])) for name in PHYSICAL_NAMES}
    means = {name: float(np.mean(samples[name])) for name in PHYSICAL_NAMES}
    return intervals, ranks, means


def state_and_predictive_summary(data, states: np.ndarray, theta: np.ndarray) -> dict:
    indices = np.linspace(0, len(theta) - 1, POSTERIOR_STATE_DRAWS, dtype=int)
    conditional_means = []
    conditional_variances = []
    predictive_means = []
    predictive_variances = []
    for index in indices:
        result = filter_and_smooth(theta[index], data)
        parameters = physical_samples(theta[index : index + 1])
        state_mean = result["smoothed_mean"]
        state_variance = np.diagonal(result["smoothed_covariance"], axis1=1, axis2=2)
        pair_offsets = np.asarray([0.0, parameters["pair_contrast"][0]])
        prediction = state_mean[:, :, None] + pair_offsets[None, None, :]
        prediction_variance = state_variance[:, :, None] + parameters["observation_scale"][0] ** 2
        conditional_means.append(state_mean)
        conditional_variances.append(state_variance)
        predictive_means.append(prediction)
        predictive_variances.append(prediction_variance)
    conditional_means = np.asarray(conditional_means)
    conditional_variances = np.asarray(conditional_variances)
    predictive_means = np.asarray(predictive_means)
    predictive_variances = np.asarray(predictive_variances)
    state_mean = np.mean(conditional_means, axis=0)
    state_variance = np.mean(conditional_variances + conditional_means**2, axis=0) - state_mean**2
    predictive_mean = np.mean(predictive_means, axis=0)
    predictive_variance = (
        np.mean(predictive_variances + predictive_means**2, axis=0) - predictive_mean**2
    )
    predictive_sigma = np.sqrt(np.maximum(predictive_variance, 0.0))
    residual = np.abs(data.observations - predictive_mean)
    return {
        "latent_squared_error_sum": float(np.sum((state_mean - states) ** 2)),
        "latent_value_count": int(states.size),
        "mean_state_posterior_variance": float(np.mean(state_variance)),
        "predictive_90_covered": int(np.sum(residual <= 1.6448536269514722 * predictive_sigma)),
        "predictive_95_covered": int(np.sum(residual <= 1.959963984540054 * predictive_sigma)),
        "predictive_value_count": int(residual.size),
    }


def one_fixed_truth(index: int) -> dict:
    rng = np.random.default_rng(1_831_000 + index)
    times = np.arange(48, dtype=float)
    background, event = covariates(rng, len(times))
    data, states = simulate(TRUTH, times, background, event, rng)
    posterior = sample_parameters(data, 2_091_000 + index)
    samples = physical_samples(posterior["theta"])
    intervals, ranks, means = interval_and_ranks(samples, TRUTH)
    state = state_and_predictive_summary(data, states, posterior["theta"])
    return {
        "replicate": index,
        "usable_chains": posterior["usable"],
        "map_success": posterior["map_success"],
        "map_message": posterior["map_message"],
        "map_iterations": posterior["map_iterations"],
        "sampling_acceptance": posterior["sampling_acceptance"],
        "warmup_acceptance": posterior["warmup_acceptance"],
        "chain_diagnostics": posterior["diagnostics"],
        "posterior_means": means,
        "intervals_95": intervals,
        "ranks_of_4000": ranks,
        **state,
    }


def one_sbc(index: int) -> dict:
    rng = np.random.default_rng(2_331_000 + index)
    truth = draw_prior_parameters(rng)
    times = np.arange(48, dtype=float)
    background, event = covariates(rng, len(times))
    data, _ = simulate(truth, times, background, event, rng)
    posterior = sample_parameters(data, 2_591_000 + index)
    samples = physical_samples(posterior["theta"])
    _, ranks, means = interval_and_ranks(samples, truth)
    return {
        "replicate": index,
        "truth": truth,
        "usable_chains": posterior["usable"],
        "map_success": posterior["map_success"],
        "map_message": posterior["map_message"],
        "map_iterations": posterior["map_iterations"],
        "sampling_acceptance": posterior["sampling_acceptance"],
        "warmup_acceptance": posterior["warmup_acceptance"],
        "chain_diagnostics": posterior["diagnostics"],
        "posterior_means": means,
        "ranks_of_4000": ranks,
    }


def prior_predictive(seed: int, draws: int = 1000) -> dict:
    rng = np.random.default_rng(seed)
    times = np.arange(48, dtype=float)
    background, event = covariates(rng, len(times))
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


def rank_checks(rows: list[dict]) -> dict:
    checks = {}
    for name in PHYSICAL_NAMES:
        ranks = np.asarray([row["ranks_of_4000"][name] for row in rows])
        histogram, _ = np.histogram(ranks, bins=np.linspace(0, 4000, 11))
        _, p_value = chisquare(histogram)
        edge_fraction = float(np.mean((ranks <= 200) | (ranks >= 3800)))
        checks[name] = {
            "ten_bin_counts": histogram.tolist(),
            "chi_square_uniformity_p": float(p_value),
            "edge_fraction": edge_fraction,
            "pass": bool(p_value >= 0.01 and edge_fraction <= 0.20),
        }
    return checks


def summarize(fixed: list[dict], sbc: list[dict], prior: dict) -> dict:
    coverage = {}
    estimates = {}
    for name in PHYSICAL_NAMES:
        estimates[name] = [row["posterior_means"][name] for row in fixed]
        coverage[name] = float(
            np.mean(
                [
                    row["intervals_95"][name][0] <= TRUTH[name] <= row["intervals_95"][name][1]
                    for row in fixed
                ]
            )
        )
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
            sum(row["latent_squared_error_sum"] for row in fixed)
            / sum(row["latent_value_count"] for row in fixed)
        )
    )
    predictive_90 = sum(row["predictive_90_covered"] for row in fixed) / sum(
        row["predictive_value_count"] for row in fixed
    )
    predictive_95 = sum(row["predictive_95_covered"] for row in fixed) / sum(
        row["predictive_value_count"] for row in fixed
    )
    sbc_checks = rank_checks(sbc)
    fixed_usable = sum(row["usable_chains"] for row in fixed)
    sbc_usable = sum(row["usable_chains"] for row in sbc)
    gates = {
        "prior_predictive": prior["pass"],
        "posterior_interval_coverage_at_least_0_90": overall_coverage >= 0.90,
        "median_standardized_bias_below_0_35": median_standardized_bias < 0.35,
        "latent_rmse_below_half_observation_noise": latent_rmse < 0.0100,
        "predictive_90_coverage_in_range": 0.85 <= predictive_90 <= 0.95,
        "predictive_95_coverage_in_range": 0.90 <= predictive_95 <= 0.99,
        "fixed_truth_usable_chains_at_least_95": fixed_usable >= 95,
        "sbc_usable_chains_at_least_95": sbc_usable >= 95,
        "simulation_based_calibration": all(value["pass"] for value in sbc_checks.values()),
    }
    return {
        "truth": TRUTH,
        "fixed_truth_replicate_count": len(fixed),
        "sbc_replicate_count": len(sbc),
        "fixed_truth_usable_chains": fixed_usable,
        "sbc_usable_chains": sbc_usable,
        "parameter_estimates": {
            name: {
                "mean": float(np.mean(values)),
                "standard_deviation": float(np.std(values, ddof=1)),
                "median": float(np.median(values)),
            }
            for name, values in estimates.items()
        },
        "posterior_interval_coverage_95": coverage,
        "overall_posterior_interval_coverage_95": overall_coverage,
        "standardized_ensemble_bias": standardized_bias,
        "median_absolute_standardized_ensemble_bias": median_standardized_bias,
        "latent_state_rmse": latent_rmse,
        "posterior_predictive_90_coverage": predictive_90,
        "posterior_predictive_95_coverage": predictive_95,
        "fixed_truth_rank_checks": rank_checks(fixed),
        "sbc_rank_checks": sbc_checks,
        "prior_predictive": prior,
        "gates": gates,
        "synthetic_recovery_gate": "PASS" if all(gates.values()) else "FAIL",
    }


def run_population(function, count: int, workers: int, label: str) -> list[dict]:
    rows = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(function, index): index for index in range(count)}
        for completed, future in enumerate(as_completed(futures), start=1):
            row = future.result()
            rows[row["replicate"]] = row
            if completed % 10 == 0 or completed == count:
                print(f"{label}: {completed}/{count} complete", flush=True)
    return [rows[index] for index in range(count)]


def make_figure(summary: dict, output: Path) -> None:
    names = list(PHYSICAL_NAMES)
    biases = [
        (summary["parameter_estimates"][name]["mean"] - TRUTH[name])
        / max(summary["parameter_estimates"][name]["standard_deviation"], 1e-12)
        for name in names
    ]
    coverage = [summary["posterior_interval_coverage_95"][name] for name in names]
    figure, axes = plt.subplots(1, 2, figsize=(10.2, 4.4), constrained_layout=True)
    axes[0].barh(names, biases, color="#5b3c88")
    axes[0].axvline(0, color="black", linewidth=0.8)
    axes[0].set_xlabel("ensemble bias / empirical SD")
    axes[0].set_title("V3 posterior recovery")
    axes[1].barh(names, coverage, color="#2a9d8f")
    axes[1].axvline(0.90, color="#d1495b", linestyle="--", linewidth=1)
    axes[1].set_xlim(0, 1)
    axes[1].set_xlabel("95% posterior interval coverage")
    axes[1].set_title("V3 interval calibration")
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
        raise ValueError("The frozen v3 protocol requires at least 100 replicates")
    fixed = run_population(one_fixed_truth, args.replicates, args.workers, "fixed truth")
    sbc = run_population(one_sbc, args.replicates, args.workers, "prior-drawn SBC")
    prior = prior_predictive(1_541_902)
    result = summarize(fixed, sbc, prior)
    root = Path.cwd()
    result.update(
        model_version="V3_EXACT_POSTERIOR_METROPOLIS",
        sampler={
            "chains": CHAINS,
            "burn_in_per_chain": BURN_IN,
            "draws_per_chain": DRAWS_PER_CHAIN,
            "posterior_state_draws": POSTERIOR_STATE_DRAWS,
            "proposal": "multivariate_student_t_independence",
            "proposal_degrees_of_freedom": PROPOSAL_DEGREES_OF_FREEDOM,
            "proposal_scale": PROPOSAL_SCALE,
        },
        software_commit=software_commit(root),
        script_sha256=sha256(Path(__file__)),
        model_source_sha256=sha256(root / "src/lattice/state_space_v2.py"),
        sampler_source_sha256=sha256(root / "src/lattice/posterior.py"),
        protocol_sha256=sha256(root / "docs/CORE_MODEL_V3_PROTOCOL.md"),
        v2_result_sha256=sha256(root / "results/core_model/synthetic_recovery_v2.json"),
        evidence="SIMULATED",
        observational_fit="NOT RUN",
        physical_inference_gate="CLOSED",
        fixed_truth_details=fixed,
        sbc_details=sbc,
    )
    output = root / "results/core_model"
    write_json(output / "synthetic_recovery_v3.json", result)
    make_figure(result, root / "paper/figures/synthetic_recovery_v3")
    print(
        f"V3 gate={result['synthetic_recovery_gate']}; "
        f"fixed usable={result['fixed_truth_usable_chains']}/{args.replicates}; "
        f"SBC usable={result['sbc_usable_chains']}/{args.replicates}; "
        "observational fit=NOT RUN"
    )


if __name__ == "__main__":
    main()
