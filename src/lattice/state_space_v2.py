"""Reference-anchored exact Gaussian state-space model for LATTICE v2."""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from lattice.state_space import INITIAL_STATE_SD, StateSpaceData, finite_hessian, transition

PARAMETER_NAMES = (
    "log_drift",
    "chip_deviation",
    "log_background_coefficient",
    "log_event_coefficient",
    "log_annealing_rate",
    "pair_contrast",
    "log_process_scale",
    "log_observation_scale",
)
PHYSICAL_NAMES = (
    "drift",
    "chip_deviation",
    "background_coefficient",
    "event_coefficient",
    "annealing_rate",
    "pair_contrast",
    "process_scale",
    "observation_scale",
)
POSITIVE_NAMES = (
    "drift",
    "background_coefficient",
    "event_coefficient",
    "annealing_rate",
    "process_scale",
    "observation_scale",
)
PRIOR_MEDIANS = {
    "drift": 0.010,
    "background_coefficient": 0.008,
    "event_coefficient": 0.015,
    "annealing_rate": 0.080,
    "process_scale": 0.006,
    "observation_scale": 0.020,
}
PRIOR_LOG_SDS = {
    "drift": 0.30,
    "background_coefficient": 0.40,
    "event_coefficient": 0.40,
    "annealing_rate": 0.30,
    "process_scale": 0.35,
    "observation_scale": 0.25,
}
SIGNED_PRIOR_SDS = {"chip_deviation": 0.006, "pair_contrast": 0.015}


@dataclass(frozen=True)
class FitResult:
    success: bool
    message: str
    theta: np.ndarray
    parameters: dict[str, float]
    objective: float
    iterations: int
    state: dict


def unpack(theta: np.ndarray) -> dict[str, float]:
    transformed = dict(zip(PARAMETER_NAMES, np.asarray(theta, dtype=float), strict=True))
    values = {
        "chip_deviation": transformed["chip_deviation"],
        "pair_contrast": transformed["pair_contrast"],
    }
    for name in POSITIVE_NAMES:
        values[name] = np.exp(transformed[f"log_{name}"])
    return {name: float(values[name]) for name in PHYSICAL_NAMES}


def pack(parameters: dict[str, float]) -> np.ndarray:
    values = dict(parameters)
    for name in POSITIVE_NAMES:
        if values[name] <= 0:
            raise ValueError(f"{name} must be positive")
        values[f"log_{name}"] = np.log(values[name])
    return np.asarray([values[name] for name in PARAMETER_NAMES], dtype=float)


def simulate(
    parameters: dict[str, float],
    times: np.ndarray,
    background: np.ndarray,
    event: np.ndarray,
    rng: np.random.Generator,
) -> tuple[StateSpaceData, np.ndarray]:
    epochs = len(times)
    states = np.zeros((epochs, 2))
    states[0] = rng.normal(0, INITIAL_STATE_SD, 2)
    for index, dt in enumerate(np.diff(times)):
        matrix, offset, process = transition(parameters, dt, background[index], event[index])
        states[index + 1] = (
            matrix @ states[index] + offset + rng.multivariate_normal(np.zeros(2), process)
        )
    pair_offsets = np.asarray([0.0, parameters["pair_contrast"]])
    observations = states[:, :, None] + pair_offsets[None, None, :]
    observations += rng.normal(0, parameters["observation_scale"], observations.shape)
    data = StateSpaceData(
        times=np.asarray(times, dtype=float),
        background=np.asarray(background, dtype=float),
        event=np.asarray(event, dtype=float),
        observations=observations,
    )
    data.validate()
    return data, states


def filter_and_smooth(theta: np.ndarray, data: StateSpaceData) -> dict:
    data.validate()
    parameters = unpack(theta)
    observation_matrix = np.asarray([[1, 0], [1, 0], [0, 1], [0, 1]], dtype=float)
    pair_offsets = np.asarray([0.0, parameters["pair_contrast"], 0.0, parameters["pair_contrast"]])
    observation_covariance = np.eye(4) * parameters["observation_scale"] ** 2
    epochs = len(data.times)
    predicted_mean = np.zeros((epochs, 2))
    predicted_covariance = np.zeros((epochs, 2, 2))
    filtered_mean = np.zeros((epochs, 2))
    filtered_covariance = np.zeros((epochs, 2, 2))
    transition_matrices = np.zeros((epochs - 1, 2, 2))
    predicted_covariance[0] = np.eye(2) * INITIAL_STATE_SD**2
    negative_log_likelihood = 0.0

    for index in range(epochs):
        observed = data.observations[index].reshape(-1)
        innovation = observed - pair_offsets - observation_matrix @ predicted_mean[index]
        innovation_covariance = (
            observation_matrix @ predicted_covariance[index] @ observation_matrix.T
            + observation_covariance
        )
        sign, logdet = np.linalg.slogdet(innovation_covariance)
        if sign <= 0:
            return {"negative_log_likelihood": np.inf}
        solved = np.linalg.solve(innovation_covariance, innovation)
        negative_log_likelihood += 0.5 * (4 * np.log(2 * np.pi) + logdet + innovation @ solved)
        gain = np.linalg.solve(
            innovation_covariance, observation_matrix @ predicted_covariance[index]
        ).T
        filtered_mean[index] = predicted_mean[index] + gain @ innovation
        filtered_covariance[index] = (np.eye(2) - gain @ observation_matrix) @ predicted_covariance[
            index
        ]
        filtered_covariance[index] = (filtered_covariance[index] + filtered_covariance[index].T) / 2
        if index < epochs - 1:
            dt = data.times[index + 1] - data.times[index]
            matrix, offset, process = transition(
                parameters, dt, data.background[index], data.event[index]
            )
            transition_matrices[index] = matrix
            predicted_mean[index + 1] = matrix @ filtered_mean[index] + offset
            predicted_covariance[index + 1] = (
                matrix @ filtered_covariance[index] @ matrix.T + process
            )

    smoothed_mean = filtered_mean.copy()
    smoothed_covariance = filtered_covariance.copy()
    for index in range(epochs - 2, -1, -1):
        gain = np.linalg.solve(
            predicted_covariance[index + 1],
            transition_matrices[index] @ filtered_covariance[index],
        ).T
        smoothed_mean[index] += gain @ (smoothed_mean[index + 1] - predicted_mean[index + 1])
        smoothed_covariance[index] += (
            gain @ (smoothed_covariance[index + 1] - predicted_covariance[index + 1]) @ gain.T
        )
        smoothed_covariance[index] = (smoothed_covariance[index] + smoothed_covariance[index].T) / 2
    return {
        "negative_log_likelihood": float(negative_log_likelihood),
        "filtered_mean": filtered_mean,
        "filtered_covariance": filtered_covariance,
        "smoothed_mean": smoothed_mean,
        "smoothed_covariance": smoothed_covariance,
    }


def negative_log_posterior(theta: np.ndarray, data: StateSpaceData) -> float:
    result = filter_and_smooth(theta, data)
    likelihood = result["negative_log_likelihood"]
    if not np.isfinite(likelihood):
        return np.inf
    transformed = dict(zip(PARAMETER_NAMES, theta, strict=True))
    penalty = 0.0
    for name in POSITIVE_NAMES:
        centered = transformed[f"log_{name}"] - np.log(PRIOR_MEDIANS[name])
        penalty += 0.5 * (centered / PRIOR_LOG_SDS[name]) ** 2
    penalty += 0.5 * (transformed["chip_deviation"] / SIGNED_PRIOR_SDS["chip_deviation"]) ** 2
    penalty += 0.5 * (transformed["pair_contrast"] / SIGNED_PRIOR_SDS["pair_contrast"]) ** 2
    return float(likelihood + penalty)


def initial_from_data(data: StateSpaceData) -> np.ndarray:
    data.validate()
    pair_contrast = float(np.mean(data.observations[:, :, 1] - data.observations[:, :, 0]))
    pair_offsets = np.asarray([0.0, pair_contrast])
    state_proxy = np.mean(data.observations - pair_offsets[None, None, :], axis=2)
    rows = []
    target = []
    for index, dt in enumerate(np.diff(data.times)):
        for chip, sign in enumerate((-1.0, 1.0)):
            rows.append(
                [
                    state_proxy[index, chip],
                    dt,
                    dt * sign,
                    dt * data.background[index],
                    dt * data.event[index],
                ]
            )
            target.append(state_proxy[index + 1, chip])
    coefficients, *_ = np.linalg.lstsq(np.asarray(rows), np.asarray(target), rcond=None)
    phi = float(np.clip(coefficients[0], 0.25, 0.999))
    median_dt = float(np.median(np.diff(data.times)))
    annealing = max(-np.log(phi) / median_dt, 0.005)
    fitted = np.asarray(rows) @ coefficients
    process = float(np.clip(np.std(np.asarray(target) - fitted), 0.003, 0.05))
    pair_differences = data.observations[:, :, 1] - data.observations[:, :, 0]
    observation = float(np.clip(np.std(pair_differences) / np.sqrt(2), 0.005, 0.08))
    return pack(
        {
            "drift": float(np.clip(coefficients[1], 0.001, 0.1)),
            "chip_deviation": float(np.clip(coefficients[2], -0.05, 0.05)),
            "background_coefficient": float(np.clip(coefficients[3], 0.001, 0.1)),
            "event_coefficient": float(np.clip(coefficients[4], 0.001, 0.1)),
            "annealing_rate": annealing,
            "pair_contrast": pair_contrast,
            "process_scale": process,
            "observation_scale": observation,
        }
    )


def fit(data: StateSpaceData, initial: np.ndarray | None = None) -> dict:
    if initial is None:
        initial = initial_from_data(data)
    bounds = [(-9, 0), (-0.5, 0.5), (-9, 0), (-9, 0), (-9, 0), (-0.5, 0.5), (-9, 0), (-9, 0)]
    result = minimize(
        negative_log_posterior,
        np.asarray(initial),
        args=(data,),
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": 600, "ftol": 1e-10, "gtol": 1e-7, "maxls": 40},
    )
    state = filter_and_smooth(result.x, data)
    return {
        "success": bool(result.success and np.isfinite(result.fun)),
        "message": str(result.message),
        "theta": result.x,
        "parameters": unpack(result.x),
        "objective": float(result.fun),
        "iterations": int(result.nit),
        **state,
    }


def laplace_covariance(data: StateSpaceData, theta: np.ndarray) -> np.ndarray:
    hessian = finite_hessian(lambda value: negative_log_posterior(value, data), theta)
    eigenvalues, eigenvectors = np.linalg.eigh((hessian + hessian.T) / 2)
    eigenvalues = np.maximum(eigenvalues, 1e-6)
    return (eigenvectors / eigenvalues) @ eigenvectors.T
