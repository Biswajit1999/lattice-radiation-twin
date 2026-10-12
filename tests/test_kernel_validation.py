import numpy as np

from lattice.euclid_transfer import mixture_kernel
from lattice.kernel_validation import (
    image_window_convergence,
    mixture_recovery_experiment,
    recover_mixture_from_counts,
    required_lags_for_tail,
)


def test_tail_budget_is_minimal_and_meets_tolerance():
    tau, step, tolerance = 0.02, 0.00402, 1e-9
    lags = required_lags_for_tail(tau, step, tolerance)
    assert np.exp(-lags * step / tau) <= tolerance
    assert np.exp(-(lags - 1) * step / tau) > tolerance


def test_noiseless_mixture_histogram_recovers_parameters():
    truth = mixture_kernel(0.004, 0.020, 0.6, 0.00402, 40)
    probabilities = np.append(truth.probability, truth.tail_probability)
    result = recover_mixture_from_counts(probabilities * 1e10, 0.00402)
    assert result["converged"]
    assert abs(result["fast_tau_seconds"] / 0.004 - 1) < 1e-3
    assert abs(result["slow_tau_seconds"] / 0.020 - 1) < 1e-3
    assert abs(result["fast_weight"] - 0.6) < 1e-3


def test_recovery_bias_is_small_at_high_counts():
    result = mixture_recovery_experiment((2_000_000,), replicates=12)[0]
    assert result["convergence_fraction"] == 1
    assert abs(result["median_fast_tau_bias_fraction"]) < 0.05
    assert abs(result["median_slow_tau_bias_fraction"]) < 0.05
    assert abs(result["median_weight_bias"]) < 0.03


def test_finite_window_converges_and_conserves_charge():
    rows = image_window_convergence((24, 48, 96, 128))
    assert rows[-1]["centroid_relative_error_vs_largest"] == 0
    assert (
        rows[0]["centroid_relative_error_vs_largest"]
        > rows[-2]["centroid_relative_error_vs_largest"]
    )
    assert max(row["charge_closure_error"] for row in rows) < 1e-12
