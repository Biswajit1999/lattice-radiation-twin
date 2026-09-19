"""Diagnostics for separating calendar time from cumulative exposure proxies."""

from collections.abc import Sequence

import numpy as np

EXPOSURE_FEATURES = (
    "log_omni_event_cumulative",
    "log_omni_background_cumulative",
    "log_sgps_event_cumulative",
    "log_sgps_background_cumulative",
)


def collapse_epochs(
    rows: Sequence[dict],
    feature_names: Sequence[str],
    constant_within_epoch: Sequence[str] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return one predictor vector and inverse-variance weighted outcome per epoch."""
    constant = set(feature_names if constant_within_epoch is None else constant_within_epoch)
    years = np.array(sorted({int(row["year"]) for row in rows}), dtype=int)
    predictors, outcomes = [], []
    for year in years:
        group = [row for row in rows if int(row["year"]) == year]
        for name in constant:
            values = np.array([row[name] for row in group], dtype=float)
            if not np.allclose(values, values[0], rtol=0.0, atol=1e-12):
                raise ValueError(f"Predictors vary within epoch {year}")
        errors = np.array([row["measurement_se"] for row in group], dtype=float)
        if np.any(errors <= 0) or not np.isfinite(errors).all():
            raise ValueError("measurement_se must be finite and positive")
        weights = errors**-2
        outcomes.append(np.average([row["outcome"] for row in group], weights=weights))
        predictors.append(np.mean([[row[name] for name in feature_names] for row in group], axis=0))
    return years, np.asarray(predictors), np.asarray(outcomes)


def standardize_columns(values: np.ndarray) -> np.ndarray:
    """Sample-standardize columns, rejecting non-informative predictors."""
    standard_deviation = np.std(values, axis=0, ddof=1)
    if np.any(~np.isfinite(standard_deviation)) or np.any(standard_deviation <= 0):
        raise ValueError("Every predictor must have finite non-zero variance")
    return (values - np.mean(values, axis=0)) / standard_deviation


def variance_inflation_factors(standardized: np.ndarray) -> np.ndarray:
    """Compute OLS variance-inflation factors for standardized predictors."""
    factors = []
    for index in range(standardized.shape[1]):
        target = standardized[:, index]
        others = np.delete(standardized, index, axis=1)
        design = np.column_stack([np.ones(len(target)), others])
        residual = target - design @ np.linalg.lstsq(design, target, rcond=None)[0]
        r_squared = 1.0 - float(residual @ residual) / float(target @ target)
        factors.append(float(np.inf if r_squared >= 1.0 else 1.0 / (1.0 - r_squared)))
    return np.asarray(factors)


def audit_identifiability(rows: Sequence[dict]) -> dict:
    """Audit component identifiability using one independent predictor row per epoch."""
    feature_names = ("time_years", *EXPOSURE_FEATURES)
    years, predictors, outcome = collapse_epochs(
        rows, feature_names, constant_within_epoch=EXPOSURE_FEATURES
    )
    standardized = standardize_columns(predictors)
    outcome_standardized = standardize_columns(outcome[:, None])[:, 0]
    design = np.column_stack([np.ones(len(years)), standardized])
    rank = int(np.linalg.matrix_rank(design))
    parameter_count = int(design.shape[1])
    correlations = np.corrcoef(predictors, rowvar=False)
    vifs = variance_inflation_factors(standardized)

    exposure_standardized = standardized[:, 1:]
    exposure_singular_values = np.linalg.svd(exposure_standardized, compute_uv=False)
    variance_fractions = exposure_singular_values**2 / np.sum(exposure_singular_values**2)

    coefficients = []
    for held_index, held_year in enumerate(years):
        training = np.arange(len(years)) != held_index
        fit = np.linalg.lstsq(design[training], outcome_standardized[training], rcond=None)[0][1:]
        coefficients.append(
            {"held_out_year": int(held_year), **dict(zip(feature_names, fit, strict=True))}
        )
    coefficient_matrix = np.array(
        [[row[name] for name in feature_names] for row in coefficients], dtype=float
    )
    positive_fractions = np.mean(coefficient_matrix > 0, axis=0)
    coefficient_ranges = np.ptp(coefficient_matrix, axis=0)

    exposure_correlation = correlations[1:, 1:]
    off_diagonal = np.abs(exposure_correlation[np.triu_indices(len(EXPOSURE_FEATURES), 1)])
    maximum_pairwise_correlation = float(np.max(off_diagonal))
    residual_degrees_of_freedom = int(len(years) - rank)
    exposure_sign_stable = {
        name: bool(fraction in (0.0, 1.0))
        for name, fraction in zip(EXPOSURE_FEATURES, positive_fractions[1:], strict=True)
    }
    thresholds = {
        "maximum_absolute_pairwise_exposure_correlation": 0.95,
        "maximum_variance_inflation_factor": 10.0,
        "minimum_residual_degrees_of_freedom": len(EXPOSURE_FEATURES),
        "require_leave_one_epoch_out_sign_stability": True,
    }
    gates = {
        "pairwise_exposure_correlation": maximum_pairwise_correlation
        < thresholds["maximum_absolute_pairwise_exposure_correlation"],
        "variance_inflation": float(np.max(vifs)) < thresholds["maximum_variance_inflation_factor"],
        "residual_degrees_of_freedom": residual_degrees_of_freedom
        >= thresholds["minimum_residual_degrees_of_freedom"],
        "leave_one_epoch_out_sign_stability": all(exposure_sign_stable.values()),
    }
    return {
        "unique_epochs": int(len(years)),
        "years": years.tolist(),
        "feature_names": list(feature_names),
        "parameter_count_with_intercept": parameter_count,
        "design_rank": rank,
        "residual_degrees_of_freedom": residual_degrees_of_freedom,
        "standardized_design_condition_number": float(np.linalg.cond(design)),
        "correlation_matrix": correlations.tolist(),
        "variance_inflation_factors": dict(zip(feature_names, vifs.tolist(), strict=True)),
        "exposure_singular_values": exposure_singular_values.tolist(),
        "exposure_variance_fractions": variance_fractions.tolist(),
        "leave_one_epoch_out_coefficients": coefficients,
        "positive_coefficient_fractions": dict(
            zip(feature_names, positive_fractions.tolist(), strict=True)
        ),
        "coefficient_ranges": dict(zip(feature_names, coefficient_ranges.tolist(), strict=True)),
        "maximum_absolute_pairwise_exposure_correlation": maximum_pairwise_correlation,
        "exposure_sign_stable": exposure_sign_stable,
        "thresholds": thresholds,
        "gates": gates,
        "component_attribution_gate": "PASS" if all(gates.values()) else "FAIL",
    }
