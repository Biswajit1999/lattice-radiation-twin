import numpy as np

from lattice.replication import bootstrap_slope, compare_cohort_rows, finite_spearman


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


def test_cohort_comparison_preserves_each_epoch_and_chip():
    development = []
    replication = []
    for year in range(2003, 2025, 3):
        for chip in (1, 2):
            mean = 0.01 * (year - 2003) + 0.001 * chip
            development.append(
                {
                    "year": year,
                    "chip": chip,
                    "parallel_fraction": {"mean": mean, "lo": mean - 0.01, "hi": mean + 0.01},
                }
            )
            for pair_index, offset in ((2, -0.002), (3, 0.002)):
                replication.append(
                    {
                        "year": year,
                        "chip": chip,
                        "pair_index": pair_index,
                        "analysis_role": "replication",
                        "parallel_fraction": {
                            "mean": mean + offset,
                            "lo": mean + offset - 0.01,
                            "hi": mean + offset + 0.01,
                        },
                    }
                )
    rows, metrics = compare_cohort_rows(development, replication)
    assert len(rows) == 16
    assert metrics["mean_absolute_difference"] < 1e-12
    assert metrics["development_within_replication_pair_range_count"] == 16
    assert metrics["overlapping_95_interval_count_of_32"] == 32
