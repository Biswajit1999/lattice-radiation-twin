"""Numerical validation for conditional charge-release kernels.

All experiments here are synthetic. They test numerical truncation, mixture
parameter recovery, and finite image-window effects; they do not estimate a
Euclid or HST trap population.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from scipy.optimize import least_squares
from scipy.special import expit, logit

from lattice.euclid_transfer import mixture_kernel, release_kernel
from lattice.science_bias import apply_parallel_trail, gaussian_source


def required_lags_for_tail(
    tau_seconds: float,
    step_seconds: float,
    tail_tolerance: float,
) -> int:
    """Smallest lag window whose exponential survival mass is within tolerance."""
    if tau_seconds <= 0 or step_seconds <= 0 or not 0 < tail_tolerance < 1:
        raise ValueError("tau/step must be positive and tolerance in (0, 1)")
    return max(1, int(np.ceil(-tau_seconds * np.log(tail_tolerance) / step_seconds)))


def tail_budget_sweep(
    tau_seconds: Iterable[float] = (220e-6, 1e-3, 5e-3, 20e-3, 50e-3),
    tail_tolerances: Iterable[float] = (1e-3, 1e-6, 1e-9, 1e-12),
    step_seconds: float = 4.02e-3,
) -> list[dict[str, float]]:
    """Audit the kernel window needed for declared omitted-mass budgets."""
    rows = []
    for tau in tau_seconds:
        for tolerance in tail_tolerances:
            lags = required_lags_for_tail(tau, step_seconds, tolerance)
            kernel = release_kernel(tau, step_seconds, lags)
            rows.append(
                {
                    "tau_seconds": float(tau),
                    "step_seconds": step_seconds,
                    "tail_tolerance": float(tolerance),
                    "required_lags": lags,
                    "window_seconds": lags * step_seconds,
                    "achieved_tail_probability": kernel.tail_probability,
                    "mass_closure_error": abs(
                        kernel.represented_mass + kernel.tail_probability - 1.0
                    ),
                }
            )
    return rows


def recover_mixture_from_counts(
    counts: np.ndarray,
    step_seconds: float,
) -> dict[str, float]:
    """Recover a two-exponential mixture from multinomial release counts.

    The final count is the explicitly represented beyond-window tail. Fast and
    slow timescales are ordered by construction to avoid label switching.
    """
    counts = np.asarray(counts, dtype=float)
    if counts.ndim != 1 or counts.size < 6 or np.any(counts < 0) or counts.sum() <= 0:
        raise ValueError("counts must be a non-negative one-dimensional release histogram")
    max_lag = counts.size - 1
    observed = counts / counts.sum()
    sigma = np.sqrt(np.maximum(observed * (1 - observed) / counts.sum(), 1 / counts.sum() ** 2))

    def unpack(raw: np.ndarray) -> tuple[float, float, float]:
        fast = float(np.exp(raw[0]))
        slow = fast + float(np.exp(raw[1]))
        weight = float(expit(raw[2]))
        return fast, slow, weight

    def residual(raw: np.ndarray) -> np.ndarray:
        fast, slow, weight = unpack(raw)
        kernel = mixture_kernel(fast, slow, weight, step_seconds, max_lag)
        model = np.append(kernel.probability, kernel.tail_probability)
        return (model - observed) / sigma

    initial = np.array([np.log(step_seconds), np.log(4 * step_seconds), logit(0.5)])
    fit = least_squares(residual, initial, max_nfev=10_000)
    fast, slow, weight = unpack(fit.x)
    information = fit.jac.T @ fit.jac
    return {
        "fast_tau_seconds": fast,
        "slow_tau_seconds": slow,
        "fast_weight": weight,
        "reduced_chi_square": float(np.sum(fit.fun**2) / (counts.size - 3)),
        "information_condition_number": float(np.linalg.cond(information)),
        "converged": bool(fit.success),
    }


def mixture_recovery_experiment(
    electron_counts: Iterable[int] = (100_000, 1_000_000, 10_000_000),
    *,
    replicates: int = 50,
    seed: int = 20261011,
    fast_tau_seconds: float = 4.0e-3,
    slow_tau_seconds: float = 20.0e-3,
    fast_weight: float = 0.6,
    step_seconds: float = 4.02e-3,
    max_lag: int = 40,
) -> list[dict[str, float]]:
    """Run seeded mixture recovery as count precision changes."""
    if replicates < 2:
        raise ValueError("at least two replicates are required")
    truth = mixture_kernel(fast_tau_seconds, slow_tau_seconds, fast_weight, step_seconds, max_lag)
    probabilities = np.append(truth.probability, truth.tail_probability)
    rng = np.random.default_rng(seed)
    rows = []
    for total in electron_counts:
        if total <= 0:
            raise ValueError("electron counts must be positive")
        recovered = [
            recover_mixture_from_counts(rng.multinomial(int(total), probabilities), step_seconds)
            for _ in range(replicates)
        ]
        rows.append(
            {
                "released_electrons": int(total),
                "replicates": replicates,
                "convergence_fraction": float(np.mean([row["converged"] for row in recovered])),
                "median_fast_tau_bias_fraction": float(
                    np.median([row["fast_tau_seconds"] / fast_tau_seconds - 1 for row in recovered])
                ),
                "median_slow_tau_bias_fraction": float(
                    np.median([row["slow_tau_seconds"] / slow_tau_seconds - 1 for row in recovered])
                ),
                "median_weight_bias": float(
                    np.median([row["fast_weight"] - fast_weight for row in recovered])
                ),
                "median_information_condition_number": float(
                    np.median([row["information_condition_number"] for row in recovered])
                ),
            }
        )
    return rows


def image_window_convergence(
    heights: Iterable[int] = (24, 32, 48, 64, 96, 128),
    *,
    captured_fraction: float = 0.02,
) -> list[dict[str, float]]:
    """Quantify finite-array loss and centroid-response convergence."""
    kernel = release_kernel(20e-3, 4.02e-3, 4096)
    rows = []
    for height in heights:
        if height < 16:
            raise ValueError("image height must be at least 16 pixels")
        width = 33
        center = (16.0, height / 4)
        clean = gaussian_source((height, width), center, 100_000.0, np.eye(2) * 2.0**2)
        damaged, overflow = apply_parallel_trail(clean, kernel, captured_fraction, 1.0)
        y = np.indices(clean.shape, dtype=float)[0]
        clean_centroid = float(np.sum(clean * y) / clean.sum())
        damaged_centroid = float(np.sum(damaged * y) / damaged.sum())
        rows.append(
            {
                "height_pixels": int(height),
                "centroid_shift_pixels": damaged_centroid - clean_centroid,
                "overflow_fraction": overflow / clean.sum(),
                "charge_closure_error": abs(damaged.sum() + overflow - clean.sum()) / clean.sum(),
            }
        )
    reference = rows[-1]["centroid_shift_pixels"]
    for row in rows:
        row["centroid_relative_error_vs_largest"] = abs(
            row["centroid_shift_pixels"] - reference
        ) / abs(reference)
    return rows
