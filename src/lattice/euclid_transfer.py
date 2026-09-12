"""Mission-specific conditional Euclid charge-release kernels."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ReleaseKernel:
    lag: np.ndarray
    probability: np.ndarray
    tail_probability: float

    @property
    def represented_mass(self) -> float:
        return float(np.sum(self.probability))

    @property
    def mean_lag_given_represented_release(self) -> float:
        mass = self.represented_mass
        return float(np.sum(self.lag * self.probability) / mass)


def release_kernel(tau_seconds: float, step_seconds: float, max_lag: int) -> ReleaseKernel:
    """Discretise exponential release while preserving the beyond-window tail."""
    if tau_seconds <= 0 or step_seconds <= 0 or max_lag < 1:
        raise ValueError("tau, step and max_lag must be positive")
    lag = np.arange(1, max_lag + 1, dtype=float)
    edges = np.arange(max_lag + 1, dtype=float) * step_seconds
    survival = np.exp(-edges / tau_seconds)
    probability = survival[:-1] - survival[1:]
    return ReleaseKernel(lag, probability, float(survival[-1]))


def mixture_kernel(
    fast_tau_seconds: float,
    slow_tau_seconds: float,
    fast_weight: float,
    step_seconds: float,
    max_lag: int,
) -> ReleaseKernel:
    if not 0 <= fast_weight <= 1:
        raise ValueError("fast_weight must lie in [0, 1]")
    fast = release_kernel(fast_tau_seconds, step_seconds, max_lag)
    slow = release_kernel(slow_tau_seconds, step_seconds, max_lag)
    probability = fast_weight * fast.probability + (1 - fast_weight) * slow.probability
    tail = fast_weight * fast.tail_probability + (1 - fast_weight) * slow.tail_probability
    return ReleaseKernel(fast.lag, probability, float(tail))


def trail_impulse(
    input_electrons: float,
    full_array_captured_fraction: float,
    transfer_distance_fraction: float,
    kernel: ReleaseKernel,
) -> tuple[np.ndarray, float]:
    """Propagate an impulse and return pixels plus charge released beyond the window."""
    if input_electrons < 0:
        raise ValueError("input_electrons must be non-negative")
    if not 0 <= full_array_captured_fraction <= 1:
        raise ValueError("captured fraction must lie in [0, 1]")
    if not 0 <= transfer_distance_fraction <= 1:
        raise ValueError("transfer distance fraction must lie in [0, 1]")
    effective = full_array_captured_fraction * transfer_distance_fraction
    output = np.empty(len(kernel.probability) + 1, dtype=float)
    output[0] = input_electrons * (1 - effective)
    output[1:] = input_electrons * effective * kernel.probability
    beyond = input_electrons * effective * kernel.tail_probability
    return output, float(beyond)
