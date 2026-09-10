"""Preregistered temporal baselines and proper Gaussian forecast scores."""

from math import erf, exp, pi, sqrt

import numpy as np

BASELINE_FEATURES = {
    "B0_calendar_linear": ("time_years",),
    "B1_calendar_quadratic": ("time_years", "time_years_squared"),
    "B2_solar_cycle_sinusoid": ("solar_cycle_sin", "solar_cycle_cos"),
    "B3_cumulative_particle": ("log_omni_cumulative", "log_sgps_cumulative"),
    "B4_event_background": (
        "log_omni_event_cumulative",
        "log_omni_background_cumulative",
        "log_sgps_event_cumulative",
        "log_sgps_background_cumulative",
    ),
}


def gaussian_crps(observed: float, mean: float, sigma: float) -> float:
    """Continuous ranked probability score for a Gaussian predictive distribution."""
    z = (observed - mean) / sigma
    pdf = exp(-(z**2) / 2) / sqrt(2 * pi)
    cdf = 0.5 * (1 + erf(z / sqrt(2)))
    return sigma * (z * (2 * cdf - 1) + 2 * pdf - 1 / sqrt(pi))


def _design(rows: list[dict], features: tuple[str, ...], scaling=None):
    raw = np.asarray([[float(row[name]) for name in features] for row in rows], dtype=float)
    if scaling is None:
        centers = np.mean(raw, axis=0)
        scales = np.std(raw, axis=0)
        scales = np.where(scales > 0, scales, 1.0)
    else:
        centers, scales = scaling
    values = (raw - centers) / scales
    strata = np.asarray(
        [
            [
                1.0,
                float(row["pair_index"] == 3),
                float(row["chip"] == 2),
                float(row["pair_index"] == 3 and row["chip"] == 2),
            ]
            for row in rows
        ]
    )
    return np.column_stack([strata, values]), (centers, scales)


def linear_predictions(train: list[dict], test: list[dict], features: tuple[str, ...]):
    """Fit an OLS baseline with four pair-by-chip stratum intercepts."""
    design, scaling = _design(train, features)
    target = np.asarray([row["outcome"] for row in train])
    beta, _, rank, _ = np.linalg.lstsq(design, target, rcond=None)
    residual = target - design @ beta
    degrees = max(len(target) - rank, 1)
    residual_variance = max(float(residual @ residual / degrees), 1e-8)
    covariance = residual_variance * np.linalg.pinv(design.T @ design)
    test_design, _ = _design(test, features, scaling)
    means = test_design @ beta
    variances = residual_variance + np.einsum("ij,jk,ik->i", test_design, covariance, test_design)
    variances += np.asarray([row["measurement_se"] ** 2 for row in test])
    return means, np.sqrt(np.maximum(variances, 1e-8)), int(rank)


def state_space_predictions(train: list[dict], test: list[dict]):
    """Forecast each stratum from its last level and recency-weighted local drift."""
    means = []
    sigmas = []
    for target in test:
        history = sorted(
            (
                row
                for row in train
                if row["pair_index"] == target["pair_index"] and row["chip"] == target["chip"]
            ),
            key=lambda row: row["time_years"],
        )
        if len(history) < 3:
            raise ValueError("B5 requires at least three earlier epochs per stratum")
        increments = np.asarray(
            [
                (later["outcome"] - earlier["outcome"])
                / (later["time_years"] - earlier["time_years"])
                for earlier, later in zip(history[:-1], history[1:], strict=True)
            ]
        )
        weights = 0.5 ** np.arange(len(increments) - 1, -1, -1)
        drift = float(np.average(increments, weights=weights))
        horizon = target["time_years"] - history[-1]["time_years"]
        means.append(history[-1]["outcome"] + drift * horizon)
        innovation = increments - drift
        process_variance = max(float(np.mean(innovation**2) * horizon**2), 1e-8)
        sigmas.append(sqrt(process_variance + target["measurement_se"] ** 2))
    return np.asarray(means), np.asarray(sigmas), None


def score_predictions(observed, predicted, sigma, reference) -> dict:
    observed = np.asarray(observed, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    error = observed - predicted
    return {
        "n": len(observed),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "mae": float(np.mean(np.abs(error))),
        "mean_negative_log_predictive_density": float(
            np.mean(0.5 * np.log(2 * pi * sigma**2) + 0.5 * (error / sigma) ** 2)
        ),
        "prediction_interval_95_coverage": float(np.mean(np.abs(error) <= 1.96 * sigma)),
        "mean_crps": float(
            np.mean(
                [
                    gaussian_crps(value, mean, spread)
                    for value, mean, spread in zip(observed, predicted, sigma, strict=True)
                ]
            )
        ),
        "out_of_sample_r2_vs_training_stratum_mean": float(
            1 - np.sum(error**2) / np.sum((observed - np.asarray(reference)) ** 2)
        ),
    }


def evaluate_forward_chaining(rows: list[dict], test_years=(2015, 2018, 2021, 2024)):
    """Evaluate B0--B5 using expanding windows and whole-epoch test folds."""
    predictions = {name: [] for name in (*BASELINE_FEATURES, "B5_local_level_drift")}
    for test_year in test_years:
        train = [row for row in rows if row["year"] < test_year]
        test = [row for row in rows if row["year"] == test_year]
        if len(test) != 4 or len({row["year"] for row in train}) < 4:
            raise ValueError("Each fold requires four held-out strata and at least four epochs")
        reference = {
            (pair, chip): np.mean(
                [
                    row["outcome"]
                    for row in train
                    if row["pair_index"] == pair and row["chip"] == chip
                ]
            )
            for pair in (2, 3)
            for chip in (1, 2)
        }
        for name, features in BASELINE_FEATURES.items():
            means, sigmas, rank = linear_predictions(train, test, features)
            for row, mean, sigma in zip(test, means, sigmas, strict=True):
                predictions[name].append(
                    {
                        "test_year": test_year,
                        "pair_index": row["pair_index"],
                        "chip": row["chip"],
                        "observed": row["outcome"],
                        "predicted": float(mean),
                        "predictive_sigma": float(sigma),
                        "training_rows": len(train),
                        "design_rank": rank,
                        "reference": float(reference[(row["pair_index"], row["chip"])]),
                    }
                )
        means, sigmas, rank = state_space_predictions(train, test)
        for row, mean, sigma in zip(test, means, sigmas, strict=True):
            predictions["B5_local_level_drift"].append(
                {
                    "test_year": test_year,
                    "pair_index": row["pair_index"],
                    "chip": row["chip"],
                    "observed": row["outcome"],
                    "predicted": float(mean),
                    "predictive_sigma": float(sigma),
                    "training_rows": len(train),
                    "design_rank": rank,
                    "reference": float(reference[(row["pair_index"], row["chip"])]),
                }
            )
    metrics = {}
    for name, values in predictions.items():
        metrics[name] = score_predictions(
            [row["observed"] for row in values],
            [row["predicted"] for row in values],
            [row["predictive_sigma"] for row in values],
            [row["reference"] for row in values],
        )
    return predictions, metrics
