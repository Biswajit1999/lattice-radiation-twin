import numpy as np
import pytest

from lattice.euclid_transfer import mixture_kernel, release_kernel, trail_impulse


def test_release_kernel_preserves_mass_and_tail():
    kernel = release_kernel(0.020, 0.00402, 4096)
    assert np.all(kernel.probability >= 0)
    assert abs(kernel.represented_mass + kernel.tail_probability - 1) < 1e-12


def test_published_slow_species_has_longer_parallel_release_lag():
    fast = release_kernel(220e-6, 4.02e-3, 4096)
    slow = release_kernel(20e-3, 4.02e-3, 4096)
    assert slow.mean_lag_given_represented_release > fast.mean_lag_given_represented_release


def test_impulse_is_causal_and_charge_conserving():
    kernel = mixture_kernel(220e-6, 20e-3, 0.5, 4.02e-3, 4096)
    output, beyond = trail_impulse(100_000, 0.01, 1.0, kernel)
    assert np.all(output >= 0)
    assert abs(output.sum() + beyond - 100_000) / 100_000 < 1e-12
    assert output[0] == 99_000


def test_transfer_distance_scales_captured_charge():
    kernel = release_kernel(20e-3, 4.02e-3, 64)
    near, near_tail = trail_impulse(100_000, 0.01, 0.25, kernel)
    far, far_tail = trail_impulse(100_000, 0.01, 1.0, kernel)
    assert np.isclose(far[1:].sum() + far_tail, 4 * (near[1:].sum() + near_tail))


@pytest.mark.parametrize(
    ("tau", "step", "lag"),
    [(0, 1, 1), (1, 0, 1), (1, 1, 0)],
)
def test_release_kernel_rejects_invalid_inputs(tau, step, lag):
    with pytest.raises(ValueError):
        release_kernel(tau, step, lag)
