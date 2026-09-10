import copy

import numpy as np
import pytest

from lattice.baselines import evaluate_forward_chaining, gaussian_crps


def synthetic_rows():
    rows = []
    for year_index, year in enumerate(range(2003, 2025, 3)):
        for pair in (2, 3):
            for chip in (1, 2):
                time = float(year - 2003)
                rows.append(
                    {
                        "year": year,
                        "pair_index": pair,
                        "chip": chip,
                        "outcome": 0.01 * time + 0.002 * (pair == 3) - 0.001 * (chip == 2),
                        "measurement_se": 0.01,
                        "time_years": time,
                        "time_years_squared": time**2,
                        "solar_cycle_sin": float(np.sin(2 * np.pi * time / 11)),
                        "solar_cycle_cos": float(np.cos(2 * np.pi * time / 11)),
                        "log_omni_cumulative": float(year_index),
                        "log_sgps_cumulative": float(max(year_index - 5, 0)),
                        "log_omni_event_cumulative": float(year_index) / 2,
                        "log_omni_background_cumulative": float(year_index) / 3,
                        "log_sgps_event_cumulative": float(max(year_index - 5, 0)) / 2,
                        "log_sgps_background_cumulative": float(max(year_index - 5, 0)) / 3,
                    }
                )
    return rows


def test_gaussian_crps_at_predictive_mean():
    assert gaussian_crps(0.0, 0.0, 1.0) == pytest.approx((np.sqrt(2) - 1) / np.sqrt(np.pi))


def test_forward_chaining_is_complete_and_future_blind():
    rows = synthetic_rows()
    predictions, metrics = evaluate_forward_chaining(rows)
    assert set(predictions) == set(metrics)
    assert all(len(values) == 16 for values in predictions.values())
    assert all(np.isfinite(metric["mean_crps"]) for metric in metrics.values())

    changed = copy.deepcopy(rows)
    for row in changed:
        if row["year"] == 2024:
            row["outcome"] += 100
    future_predictions, _ = evaluate_forward_chaining(changed)
    for name in predictions:
        assert [row["predicted"] for row in predictions[name] if row["test_year"] == 2015] == [
            row["predicted"] for row in future_predictions[name] if row["test_year"] == 2015
        ]
