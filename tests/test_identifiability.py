import json
from pathlib import Path

import numpy as np
import pytest

from lattice.identifiability import (
    audit_identifiability,
    collapse_epochs,
    standardize_columns,
    variance_inflation_factors,
)


def test_collapse_epochs_uses_one_predictor_vector_and_weighted_outcome():
    rows = [
        {"year": 2020, "x": 2.0, "outcome": 1.0, "measurement_se": 1.0},
        {"year": 2020, "x": 2.0, "outcome": 3.0, "measurement_se": 0.5},
        {"year": 2021, "x": 4.0, "outcome": 5.0, "measurement_se": 1.0},
    ]
    years, predictors, outcomes = collapse_epochs(rows, ("x",))
    assert years.tolist() == [2020, 2021]
    assert predictors[:, 0].tolist() == [2.0, 4.0]
    assert outcomes.tolist() == pytest.approx([2.6, 5.0])


def test_collapse_epochs_rejects_within_epoch_predictor_drift():
    rows = [
        {"year": 2020, "x": 1.0, "outcome": 1.0, "measurement_se": 1.0},
        {"year": 2020, "x": 1.1, "outcome": 1.0, "measurement_se": 1.0},
    ]
    with pytest.raises(ValueError, match="vary within epoch"):
        collapse_epochs(rows, ("x",))


def test_variance_inflation_detects_near_duplicate_predictors():
    x = np.arange(12, dtype=float)
    values = np.column_stack([x, x + 1e-4 * x**2, np.sin(x)])
    factors = variance_inflation_factors(standardize_columns(values))
    assert factors[0] > 1_000
    assert factors[1] > 1_000


def test_committed_historical_design_fails_component_attribution_gate():
    result = json.loads(Path("results/baselines/historical_forward_chaining.json").read_text())
    audit = audit_identifiability(result["joined_inputs"])
    assert audit["unique_epochs"] == 8
    assert audit["residual_degrees_of_freedom"] == 2
    assert audit["component_attribution_gate"] == "FAIL"
    assert not all(audit["gates"].values())
