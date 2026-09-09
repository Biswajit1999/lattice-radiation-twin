import numpy as np

from lattice.replication import bootstrap_slope, finite_spearman


def test_bootstrap_slope_recovers_direction_deterministically():
    year = np.arange(8.0)
    value = 0.03 * year + np.array([0.0, 0.002, -0.001, 0.001, 0.0, -0.002, 0.001, 0.0])
    first = bootstrap_slope(year, value, n_boot=2_000)
    second = bootstrap_slope(year, value, n_boot=2_000)
    assert first == second
    assert first["slope_per_year"] > 0
    assert first["lo"] > 0


def test_finite_spearman_preserves_missingness():
    result = finite_spearman([1, 2, None, 4], [2, 4, 100, 8])
    assert result["n"] == 3
    assert result["rho"] == 1
