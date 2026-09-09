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
