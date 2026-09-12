import copy

import numpy as np
import pytest
from astropy.time import Time

from lattice.historical_state_space import (
    ObservationalStateSpaceModel,
    build_fold,
    score_historical_predictions,
)
from lattice.state_space_v2 import pack, simulate

PARAMETERS = {
    "drift": 0.012,
    "chip_deviation": 0.002,
    "background_coefficient": 0.008,
    "event_coefficient": 0.018,
    "annealing_rate": 0.06,
    "pair_contrast": 0.010,
    "process_scale": 0.008,
    "observation_scale": 0.02,
}


def mock_outcomes():
    rows = []
    for year_index, year in enumerate(range(2003, 2025, 3)):
        mjd = float(Time(f"{year}-08-01").mjd)
        for chip in (1, 2):
            for pair in (2, 3):
                mean = 0.01 * year_index + 0.002 * chip + 0.001 * (pair == 3)
                rows.append(
                    {
                        "analysis_role": "replication",
                        "year": year,
                        "mjd": mjd,
                        "chip": chip,
                        "pair_index": pair,
                        "parallel_fraction": {"mean": mean, "lo": mean - 0.004, "hi": mean + 0.004},
                    }
                )
    return rows


def mock_exposure():
    rows = []
    for number in range(12 * 2002, 12 * 2025):
        year, month = divmod(number, 12)
        value = 1 + (number % 17)
        rows.append(
            {
                "month": f"{year:04d}-{month + 1:02d}",
                "sunspot_number_mean": float(value),
                "response_basis": {
                    "hst_leo": {
                        "inverse_f107_gcr_proxy": 1 / (50 + value),
                        "sep_x_geomagnetic_activity": float(value % 5),
                    },
                    "shared_external": {"sep_log1p": float(value % 7)},
                },
            }
        )
    return rows


def test_fold_uses_only_replication_rows_and_training_scaling():
    outcomes = mock_outcomes()
    exposure = mock_exposure()
    fold = build_fold(outcomes, exposure, 2015)
    assert fold.training_years == (2003, 2006, 2009, 2012)
    assert fold.training_data.observations.shape == (4, 2, 2)
    assert fold.observed.shape == (2, 2)
    assert len(fold.feature_metadata["coverage"]) == 4
    altered = copy.deepcopy(exposure)
    for row in altered:
        if row["month"] > "2015-07":
            row["response_basis"]["hst_leo"]["sep_x_geomagnetic_activity"] = 1e9
    repeated = build_fold(outcomes, altered, 2015)
    np.testing.assert_array_equal(fold.training_data.event, repeated.training_data.event)
    assert fold.test_event == repeated.test_event


def test_fold_rejects_non_replication_outcome():
    outcomes = mock_outcomes()
    outcomes[0]["analysis_role"] = "holdout"
    with pytest.raises(ValueError, match="non-replication"):
        build_fold(outcomes, mock_exposure(), 2015)


def test_exact_zero_model_removes_parameter_and_keeps_finite_posterior():
    rng = np.random.default_rng(44)
    data, _ = simulate(
        PARAMETERS,
        np.arange(5, dtype=float),
        np.asarray([-1.0, 0.2, 0.7, -0.4]),
        np.asarray([0.0, 1.0, 0.0, 0.5]),
        rng,
    )
    model = ObservationalStateSpaceModel(("event_coefficient",))
    theta = model.reduce_theta(pack(PARAMETERS))
    assert "log_event_coefficient" not in model.parameter_names
    assert model.unpack(theta)["event_coefficient"] == 0.0
    assert np.isfinite(model.negative_log_posterior(theta, data))


def test_forecast_is_deterministic_and_has_four_positive_spreads():
    rng = np.random.default_rng(51)
    data, _ = simulate(
        PARAMETERS,
        np.arange(5, dtype=float),
        np.asarray([-1.0, 0.2, 0.7, -0.4]),
        np.asarray([0.0, 1.0, 0.0, 0.5]),
        rng,
    )
    model = ObservationalStateSpaceModel()
    theta = np.tile(pack(PARAMETERS), (32, 1))
    first = model.forecast(data, 5.0, 0.1, 0.2, np.full((2, 2), 0.003), theta, 100)
    second = model.forecast(data, 5.0, 0.1, 0.2, np.full((2, 2), 0.003), theta, 100)
    for key in first:
        np.testing.assert_array_equal(first[key], second[key])
    assert first["mean"].shape == (4,)
    assert np.all(first["standard_deviation"] > 0)


def test_historical_score_uses_frozen_baseline_metrics():
    rows = [
        {
            "observed": value,
            "predicted": value + 0.01,
            "predictive_sigma": 0.02,
            "reference": 0.0,
        }
        for value in (0.1, 0.2, 0.3, 0.4)
    ]
    metrics = score_historical_predictions(rows)
    assert metrics["n"] == 4
    assert metrics["rmse"] == pytest.approx(0.01)
