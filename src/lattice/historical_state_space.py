"""Frozen historical HST state-space validation machinery."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC
from typing import Any

import numpy as np
from astropy.time import Time
from scipy.optimize import minimize

from lattice.baselines import score_predictions
from lattice.posterior import chain_diagnostics, sample_independence_metropolis_t
from lattice.state_space import INITIAL_STATE_SD, StateSpaceData, finite_hessian, transition
from lattice.state_space_v2 import (
    PARAMETER_NAMES,
    PHYSICAL_NAMES,
    POSITIVE_NAMES,
    PRIOR_LOG_SDS,
    PRIOR_MEDIANS,
    SIGNED_PRIOR_SDS,
    initial_from_data,
)

TEST_YEARS = (2015, 2018, 2021, 2024)
PAIR_INDICES = (2, 3)
CHIPS = (1, 2)
FIXED_ZERO_VARIANTS = {
    "H1_zero_event": ("event_coefficient",),
    "H2_zero_background": ("background_coefficient",),
    "H3_zero_annealing": ("annealing_rate",),
    "H4_zero_process": ("process_scale",),
}
SENSITIVITY_VARIANTS = {
    "S1_event_lag_1_month": {"event_lag_months": 1},
    "S2_event_lag_3_months": {"event_lag_months": 3},
    "S3_event_lag_6_months": {"event_lag_months": 6},
    "S4_shared_event_proxy": {"event_proxy": "shared_sep_log1p"},
    "S5_inverse_sunspot_background": {"background_proxy": "inverse_sunspot"},
}


def _physical_to_transformed(name: str) -> str:
    return f"log_{name}" if name in POSITIVE_NAMES else name


@dataclass(frozen=True)
class HistoricalFold:
    test_year: int
    training_years: tuple[int, ...]
    training_data: StateSpaceData
    test_time: float
    test_background: float
    test_event: float
    observed: np.ndarray
    measurement_se: np.ndarray
    feature_metadata: dict[str, Any]


class ObservationalStateSpaceModel:
    """V2/v3 model with optional exact-zero transition components."""

    def __init__(self, fixed_zero: tuple[str, ...] = ()) -> None:
        unknown = set(fixed_zero) - set(PHYSICAL_NAMES)
        if unknown:
            raise ValueError(f"Unknown fixed-zero parameters: {sorted(unknown)}")
        self.fixed_zero = tuple(fixed_zero)
        self.active_physical_names = tuple(
            name for name in PHYSICAL_NAMES if name not in self.fixed_zero
        )
        self.parameter_names = tuple(
            _physical_to_transformed(name) for name in self.active_physical_names
        )

    def reduce_theta(self, full_theta: np.ndarray) -> np.ndarray:
        full = dict(zip(PARAMETER_NAMES, np.asarray(full_theta, dtype=float), strict=True))
        return np.asarray([full[name] for name in self.parameter_names])

    def unpack(self, theta: np.ndarray) -> dict[str, float]:
        if len(theta) != len(self.parameter_names):
            raise ValueError("Theta does not match active parameters")
        transformed = dict(zip(self.parameter_names, np.asarray(theta, dtype=float), strict=True))
        parameters: dict[str, float] = {}
        for name in PHYSICAL_NAMES:
            if name in self.fixed_zero:
                parameters[name] = 0.0
            elif name in POSITIVE_NAMES:
                parameters[name] = float(np.exp(transformed[f"log_{name}"]))
            else:
                parameters[name] = float(transformed[name])
        return parameters

    def filter(self, theta: np.ndarray, data: StateSpaceData) -> dict[str, Any]:
        data.validate()
        parameters = self.unpack(theta)
        observation_matrix = np.asarray([[1, 0], [1, 0], [0, 1], [0, 1]], dtype=float)
        offsets = np.asarray([0.0, parameters["pair_contrast"], 0.0, parameters["pair_contrast"]])
        observation_covariance = np.eye(4) * parameters["observation_scale"] ** 2
        epochs = len(data.times)
        predicted_mean = np.zeros((epochs, 2))
        predicted_covariance = np.zeros((epochs, 2, 2))
        filtered_mean = np.zeros((epochs, 2))
        filtered_covariance = np.zeros((epochs, 2, 2))
        predicted_covariance[0] = np.eye(2) * INITIAL_STATE_SD**2
        negative_log_likelihood = 0.0
        for index in range(epochs):
            observed = data.observations[index].reshape(-1)
            innovation = observed - offsets - observation_matrix @ predicted_mean[index]
            covariance = (
                observation_matrix @ predicted_covariance[index] @ observation_matrix.T
                + observation_covariance
            )
            sign, logdet = np.linalg.slogdet(covariance)
            if sign <= 0:
                return {"negative_log_likelihood": np.inf}
            solved = np.linalg.solve(covariance, innovation)
            negative_log_likelihood += 0.5 * (4 * np.log(2 * np.pi) + logdet + innovation @ solved)
            gain = np.linalg.solve(covariance, observation_matrix @ predicted_covariance[index]).T
            filtered_mean[index] = predicted_mean[index] + gain @ innovation
            filtered_covariance[index] = (
                np.eye(2) - gain @ observation_matrix
            ) @ predicted_covariance[index]
            filtered_covariance[index] = (
                filtered_covariance[index] + filtered_covariance[index].T
            ) / 2
            if index < epochs - 1:
                dt = data.times[index + 1] - data.times[index]
                matrix, offset, process = transition(
                    parameters, dt, data.background[index], data.event[index]
                )
                predicted_mean[index + 1] = matrix @ filtered_mean[index] + offset
                predicted_covariance[index + 1] = (
                    matrix @ filtered_covariance[index] @ matrix.T + process
                )
        return {
            "negative_log_likelihood": float(negative_log_likelihood),
            "filtered_mean": filtered_mean,
            "filtered_covariance": filtered_covariance,
        }

    def negative_log_posterior(self, theta: np.ndarray, data: StateSpaceData) -> float:
        likelihood = self.filter(theta, data)["negative_log_likelihood"]
        if not np.isfinite(likelihood):
            return np.inf
        transformed = dict(zip(self.parameter_names, theta, strict=True))
        penalty = 0.0
        for name in POSITIVE_NAMES:
            if name not in self.fixed_zero:
                centered = transformed[f"log_{name}"] - np.log(PRIOR_MEDIANS[name])
                penalty += 0.5 * (centered / PRIOR_LOG_SDS[name]) ** 2
        for name in ("chip_deviation", "pair_contrast"):
            if name not in self.fixed_zero:
                penalty += 0.5 * (transformed[name] / SIGNED_PRIOR_SDS[name]) ** 2
        return float(likelihood + penalty)

    def fit(self, data: StateSpaceData) -> dict[str, Any]:
        initial = self.reduce_theta(initial_from_data(data))
        bounds = []
        for name in self.parameter_names:
            bounds.append((-0.5, 0.5) if name in SIGNED_PRIOR_SDS else (-9, 0))
        result = minimize(
            self.negative_log_posterior,
            initial,
            args=(data,),
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": 600, "ftol": 1e-10, "gtol": 1e-7, "maxls": 40},
        )
        return {
            "success": bool(result.success and np.isfinite(result.fun)),
            "message": str(result.message),
            "theta": result.x,
            "parameters": self.unpack(result.x),
            "objective": float(result.fun),
            "iterations": int(result.nit),
        }

    def laplace_covariance(self, data: StateSpaceData, theta: np.ndarray) -> np.ndarray:
        hessian = finite_hessian(lambda value: self.negative_log_posterior(value, data), theta)
        eigenvalues, eigenvectors = np.linalg.eigh((hessian + hessian.T) / 2)
        eigenvalues = np.maximum(eigenvalues, 1e-6)
        return (eigenvectors / eigenvalues) @ eigenvectors.T

    def sample(
        self,
        data: StateSpaceData,
        base_seed: int,
        burn_in: int = 100,
        draws_per_chain: int = 2000,
    ) -> dict[str, Any]:
        fitted = self.fit(data)
        covariance = self.laplace_covariance(data, fitted["theta"])
        results = [
            sample_independence_metropolis_t(
                lambda theta: -self.negative_log_posterior(theta, data),
                location=fitted["theta"],
                proposal_covariance=covariance,
                seed=base_seed + 10_000 * chain,
                burn_in=burn_in,
                draws=draws_per_chain,
                degrees_of_freedom=5.0,
                scale=0.8,
            )
            for chain in range(2)
        ]
        chains = np.asarray([row["draws"] for row in results])
        diagnostics = chain_diagnostics(chains, self.parameter_names)
        usable = all(
            value["rank_normalized_rhat"] <= 1.05 and value["bulk_effective_sample_size"] >= 100
            for value in diagnostics.values()
        )
        return {
            "theta": chains.reshape(-1, len(self.parameter_names)),
            "chain_diagnostics": diagnostics,
            "usable_chains": usable,
            "map_success": fitted["success"],
            "map_message": fitted["message"],
            "map_iterations": fitted["iterations"],
            "sampling_acceptance": [row["sampling_acceptance"] for row in results],
            "warmup_acceptance": [row["warmup_acceptance"] for row in results],
        }

    def forecast(
        self,
        data: StateSpaceData,
        test_time: float,
        test_background: float,
        test_event: float,
        measurement_se: np.ndarray,
        theta_draws: np.ndarray,
        seed: int,
    ) -> dict[str, Any]:
        measurement_se = np.asarray(measurement_se, dtype=float).reshape(4)
        rng = np.random.default_rng(seed)
        predictive = np.empty((len(theta_draws), 4))
        conditional_means = np.empty_like(predictive)
        conditional_variances = np.empty_like(predictive)
        for index, theta in enumerate(theta_draws):
            parameters = self.unpack(theta)
            filtered = self.filter(theta, data)
            dt = test_time - data.times[-1]
            matrix, offset, process = transition(parameters, dt, test_background, test_event)
            state_mean = matrix @ filtered["filtered_mean"][-1] + offset
            state_covariance = matrix @ filtered["filtered_covariance"][-1] @ matrix.T + process
            mean = np.asarray(
                [
                    state_mean[0],
                    state_mean[0] + parameters["pair_contrast"],
                    state_mean[1],
                    state_mean[1] + parameters["pair_contrast"],
                ]
            )
            variance = (
                np.asarray(
                    [
                        state_covariance[0, 0],
                        state_covariance[0, 0],
                        state_covariance[1, 1],
                        state_covariance[1, 1],
                    ]
                )
                + parameters["observation_scale"] ** 2
                + measurement_se**2
            )
            conditional_means[index] = mean
            conditional_variances[index] = variance
            predictive[index] = rng.normal(mean, np.sqrt(np.maximum(variance, 0.0)))
        means = np.mean(conditional_means, axis=0)
        variances = np.mean(conditional_variances + conditional_means**2, axis=0) - means**2
        return {
            "mean": means,
            "standard_deviation": np.sqrt(np.maximum(variances, 0.0)),
            "lower_95": np.quantile(predictive, 0.025, axis=0),
            "upper_95": np.quantile(predictive, 0.975, axis=0),
        }


def _month_from_mjd(mjd: float) -> str:
    stamp = Time(mjd, format="mjd").to_datetime(timezone=UTC)
    if stamp.month == 1:
        return f"{stamp.year - 1:04d}-12"
    return f"{stamp.year:04d}-{stamp.month - 1:02d}"


def _month_number(month: str) -> int:
    year, value = (int(part) for part in month.split("-"))
    return 12 * year + value - 1


def _month_string(number: int) -> str:
    year, month = divmod(number, 12)
    return f"{year:04d}-{month + 1:02d}"


def _proxy(row: dict, kind: str) -> float | None:
    if kind == "hst_event":
        return row["response_basis"]["hst_leo"]["sep_x_geomagnetic_activity"]
    if kind == "shared_sep_log1p":
        return row["response_basis"]["shared_external"]["sep_log1p"]
    if kind == "inverse_f107":
        return row["response_basis"]["hst_leo"]["inverse_f107_gcr_proxy"]
    if kind == "inverse_sunspot":
        value = row.get("sunspot_number_mean")
        return None if value is None else 1.0 / max(float(value), 1.0)
    raise ValueError(f"Unknown proxy {kind}")


def interval_proxy(
    exposure_by_month: dict[str, dict],
    start_month: str,
    end_month: str,
    kind: str,
    lag_months: int = 0,
) -> tuple[float, float]:
    start = _month_number(start_month) - lag_months
    end = _month_number(end_month) - lag_months
    if end <= start:
        raise ValueError("Environment interval must contain at least one complete month")
    values = []
    for number in range(start + 1, end + 1):
        row = exposure_by_month.get(_month_string(number))
        values.append(None if row is None else _proxy(row, kind))
    valid = [float(value) for value in values if value is not None and np.isfinite(value)]
    coverage = len(valid) / len(values)
    if coverage < 0.75:
        raise ValueError(f"{kind} coverage {coverage:.3f} is below 0.75")
    if kind in {"hst_event", "shared_sep_log1p"}:
        return float(sum(valid) / len(values)), coverage
    return float(np.mean(valid)), coverage


def build_epochs(outcomes: list[dict]) -> list[dict[str, Any]]:
    if any(row.get("analysis_role") != "replication" for row in outcomes):
        raise ValueError("Historical state-space input contains a non-replication outcome")
    years = sorted({int(row["year"]) for row in outcomes})
    if years != list(range(2003, 2025, 3)) or len(outcomes) != 32:
        raise ValueError("Expected the frozen 8 x 2 x 2 replication design")
    epochs = []
    for year in years:
        rows = [row for row in outcomes if int(row["year"]) == year]
        lookup = {(int(row["chip"]), int(row["pair_index"])): row for row in rows}
        expected = {(chip, pair) for chip in CHIPS for pair in PAIR_INDICES}
        if set(lookup) != expected:
            raise ValueError(f"Epoch {year} does not have all chip/pair strata")
        observation = np.asarray(
            [
                [lookup[(chip, pair)]["parallel_fraction"]["mean"] for pair in PAIR_INDICES]
                for chip in CHIPS
            ]
        )
        measurement_se = np.asarray(
            [
                [
                    max(
                        (
                            lookup[(chip, pair)]["parallel_fraction"]["hi"]
                            - lookup[(chip, pair)]["parallel_fraction"]["lo"]
                        )
                        / (2 * 1.96),
                        1e-4,
                    )
                    for pair in PAIR_INDICES
                ]
                for chip in CHIPS
            ]
        )
        mjds = [float(row["mjd"]) for row in rows]
        epochs.append(
            {
                "year": year,
                "mjd": float(np.mean(mjds)),
                "cutoff_month": _month_from_mjd(min(mjds)),
                "observation": observation,
                "measurement_se": measurement_se,
            }
        )
    return epochs


def build_fold(
    outcomes: list[dict],
    exposure_rows: list[dict],
    test_year: int,
    event_lag_months: int = 0,
    event_proxy: str = "hst_event",
    background_proxy: str = "inverse_f107",
) -> HistoricalFold:
    epochs = [row for row in build_epochs(outcomes) if row["year"] <= test_year]
    if test_year not in TEST_YEARS or len(epochs) < 5:
        raise ValueError("Fold must be one of the four frozen test years")
    exposure_by_month = {row["month"]: row for row in exposure_rows}
    background_raw = []
    event_raw = []
    coverage = []
    for earlier, later in zip(epochs[:-1], epochs[1:], strict=True):
        background_value, background_coverage = interval_proxy(
            exposure_by_month,
            earlier["cutoff_month"],
            later["cutoff_month"],
            background_proxy,
        )
        event_value, event_coverage = interval_proxy(
            exposure_by_month,
            earlier["cutoff_month"],
            later["cutoff_month"],
            event_proxy,
            event_lag_months,
        )
        background_raw.append(background_value)
        event_raw.append(event_value)
        coverage.append(
            {
                "from_year": earlier["year"],
                "to_year": later["year"],
                "background": background_coverage,
                "event": event_coverage,
            }
        )
    training_transition_count = len(epochs) - 2

    def standardize(values: list[float]) -> tuple[np.ndarray, float, float]:
        training = np.asarray(values[:training_transition_count], dtype=float)
        center = float(np.mean(training))
        scale = float(np.std(training))
        if scale == 0:
            scale = 1.0
        return (np.asarray(values) - center) / scale, center, scale

    background, background_center, background_scale = standardize(background_raw)
    event, event_center, event_scale = standardize(event_raw)
    training_epochs = epochs[:-1]
    first_mjd = training_epochs[0]["mjd"]
    times = np.asarray([(row["mjd"] - first_mjd) / 365.25 for row in training_epochs])
    test_time = (epochs[-1]["mjd"] - first_mjd) / 365.25
    data = StateSpaceData(
        times=times,
        background=background[:-1],
        event=event[:-1],
        observations=np.asarray([row["observation"] for row in training_epochs]),
    )
    data.validate()
    return HistoricalFold(
        test_year=test_year,
        training_years=tuple(row["year"] for row in training_epochs),
        training_data=data,
        test_time=float(test_time),
        test_background=float(background[-1]),
        test_event=float(event[-1]),
        observed=np.asarray(epochs[-1]["observation"]),
        measurement_se=np.asarray(epochs[-1]["measurement_se"]),
        feature_metadata={
            "event_lag_months": event_lag_months,
            "event_proxy": event_proxy,
            "background_proxy": background_proxy,
            "background_center": background_center,
            "background_scale": background_scale,
            "event_center": event_center,
            "event_scale": event_scale,
            "coverage": coverage,
        },
    )


def score_historical_predictions(predictions: list[dict]) -> dict:
    return score_predictions(
        [row["observed"] for row in predictions],
        [row["predicted"] for row in predictions],
        [row["predictive_sigma"] for row in predictions],
        [row["reference"] for row in predictions],
    )
