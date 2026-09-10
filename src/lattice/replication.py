"""Small deterministic statistics used by the HST replication assessment."""

import numpy as np
from scipy.stats import spearmanr


def bootstrap_slope(year, value, *, seed=314159, n_boot=20_000):
    """Return an OLS slope and epoch-bootstrap interval without pooling pair strata."""
    year = np.asarray(year, dtype=float)
    value = np.asarray(value, dtype=float)
    centered = year - year.mean()
    slope = float(np.sum(centered * (value - value.mean())) / np.sum(centered**2))
    rng = np.random.default_rng(seed)
    slopes = []
    for draw in rng.integers(0, len(year), size=(n_boot, len(year))):
        xx, yy = year[draw], value[draw]
        xx_centered = xx - xx.mean()
        denominator = np.sum(xx_centered**2)
        if denominator > 0:
            slopes.append(np.sum(xx_centered * (yy - yy.mean())) / denominator)
    lo, hi = np.quantile(slopes, [0.025, 0.975])
    return {
        "slope_per_year": slope,
        "lo": float(lo),
        "hi": float(hi),
        "n_epochs": int(len(year)),
        "bootstrap_resamples_retained": len(slopes),
    }


def finite_spearman(x, y):
    """Return a descriptive rank correlation, retaining an explicit sample size."""
    pairs = [(a, b) for a, b in zip(x, y, strict=True) if a is not None and b is not None]
    if len(pairs) < 3:
        return {"n": len(pairs), "rho": None, "pvalue_unadjusted": None}
    xx, yy = np.asarray(pairs, dtype=float).T
    result = spearmanr(xx, yy)
    return {
        "n": len(pairs),
        "rho": float(result.statistic) if np.isfinite(result.statistic) else None,
        "pvalue_unadjusted": float(result.pvalue) if np.isfinite(result.pvalue) else None,
    }


def compare_cohort_rows(development, replication):
    """Compare one development pair with the mean of two replication pairs per epoch/chip."""
    expected = {(year, chip) for year in range(2003, 2025, 3) for chip in (1, 2)}
    development_by_key = {(r["year"], r["chip"]): r for r in development}
    if len(development) != 16 or set(development_by_key) != expected:
        raise ValueError("Development summary is not the frozen 8 x 2 design")
    if len(replication) != 32 or any(r.get("analysis_role") != "replication" for r in replication):
        raise ValueError("Replication summary is not the frozen 8 x 2 x 2 design")
    rows = []
    for year, chip in sorted(expected):
        dev = development_by_key[(year, chip)]["parallel_fraction"]
        reps = sorted(
            (r for r in replication if r["year"] == year and r["chip"] == chip),
            key=lambda r: r["pair_index"],
        )
        if [r["pair_index"] for r in reps] != [2, 3]:
            raise ValueError("Missing or duplicate replication pair index")
        rep_values = [r["parallel_fraction"]["mean"] for r in reps]
        rep_intervals = [[r["parallel_fraction"]["lo"], r["parallel_fraction"]["hi"]] for r in reps]
        rep_mean = float(np.mean(rep_values))
        rows.append(
            {
                "year": year,
                "chip": chip,
                "development_mean": dev["mean"],
                "development_95_interval": [dev["lo"], dev["hi"]],
                "replication_pair_means": rep_values,
                "replication_pair_95_intervals": rep_intervals,
                "development_interval_overlaps_replication_intervals": [
                    dev["lo"] <= interval[1] and interval[0] <= dev["hi"]
                    for interval in rep_intervals
                ],
                "replication_mean": rep_mean,
                "development_minus_replication_mean": dev["mean"] - rep_mean,
                "development_within_replication_pair_range": (
                    min(rep_values) <= dev["mean"] <= max(rep_values)
                ),
            }
        )
    differences = np.array([r["development_minus_replication_mean"] for r in rows])
    dev_values = np.array([r["development_mean"] for r in rows])
    rep_values = np.array([r["replication_mean"] for r in rows])
    metrics = {
        "n_epoch_chip_comparisons": len(rows),
        "mean_absolute_difference": float(np.mean(np.abs(differences))),
        "root_mean_square_difference": float(np.sqrt(np.mean(differences**2))),
        "pearson_correlation": float(np.corrcoef(dev_values, rep_values)[0, 1]),
        "development_within_replication_pair_range_count": sum(
            r["development_within_replication_pair_range"] for r in rows
        ),
        "overlapping_95_interval_count_of_32": sum(
            sum(r["development_interval_overlaps_replication_intervals"]) for r in rows
        ),
    }
    return rows, metrics
