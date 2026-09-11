import numpy as np
import pytest

from lattice.state_space_v2 import (
    PARAMETER_NAMES,
    filter_and_smooth,
    fit,
    pack,
    simulate,
    transformed_prior,
    unpack,
)

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


def synthetic(epochs=20):
    rng = np.random.default_rng(18_220)
    times = np.arange(epochs, dtype=float)
    background = np.sin(np.arange(epochs - 1) * 0.37)
    event = (rng.random(epochs - 1) < 0.2).astype(float)
    return simulate(PARAMETERS, times, background, event, rng)


def test_v2_parameter_transform_round_trip():
    assert unpack(pack(PARAMETERS)) == pytest.approx(PARAMETERS)


def test_v2_transformed_prior_matches_parameter_order():
    mean, standard_deviation = transformed_prior()
    assert mean.shape == standard_deviation.shape == (len(PARAMETER_NAMES),)
    assert np.all(standard_deviation > 0)
    assert unpack(mean)["drift"] == pytest.approx(0.010)


def test_v2_reference_pair_has_zero_offset_in_expectation():
    data, states = synthetic(epochs=200)
    first_residual = np.mean(data.observations[:, :, 0] - states)
    second_residual = np.mean(data.observations[:, :, 1] - states)
    assert first_residual == pytest.approx(0.0, abs=0.004)
    assert second_residual == pytest.approx(PARAMETERS["pair_contrast"], abs=0.004)


def test_v2_filter_tracks_synthetic_state():
    data, truth = synthetic(epochs=48)
    result = filter_and_smooth(pack(PARAMETERS), data)
    assert np.isfinite(result["negative_log_likelihood"])
    assert np.sqrt(np.mean((result["smoothed_mean"] - truth) ** 2)) < 0.01


def test_v2_optimizer_returns_finite_model():
    data, _ = synthetic()
    result = fit(data)
    assert result["success"]
    assert np.isfinite(result["objective"])
    assert result["parameters"]["drift"] > 0
    assert result["parameters"]["process_scale"] > 0
