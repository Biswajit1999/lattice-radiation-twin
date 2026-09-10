import numpy as np
import pytest

from lattice.state_space import (
    StateSpaceData,
    filter_and_smooth,
    fit,
    pack,
    simulate,
    unpack,
)

PARAMETERS = {
    "drift": 0.012,
    "chip_deviation": 0.002,
    "background_coefficient": 0.008,
    "event_coefficient": 0.018,
    "annealing_rate": 0.06,
    "pair2_offset": 0.015,
    "pair3_offset": 0.025,
    "process_scale": 0.008,
    "observation_scale": 0.02,
}


def synthetic(epochs=16):
    rng = np.random.default_rng(7321)
    times = np.arange(epochs, dtype=float)
    background = np.sin(np.arange(epochs - 1) * 0.37)
    event = (rng.random(epochs - 1) < 0.2).astype(float)
    return simulate(PARAMETERS, times, background, event, rng)


def test_parameter_transform_round_trip():
    recovered = unpack(pack(PARAMETERS))
    assert recovered == pytest.approx(PARAMETERS)


def test_exact_filter_and_smoother_track_synthetic_state():
    data, truth = synthetic(epochs=48)
    result = filter_and_smooth(pack(PARAMETERS), data)
    assert np.isfinite(result["negative_log_likelihood"])
    assert result["smoothed_mean"].shape == truth.shape
    assert (
        np.sqrt(np.mean((result["smoothed_mean"] - truth) ** 2)) < PARAMETERS["observation_scale"]
    )


def test_optimizer_returns_finite_identified_model():
    data, _ = synthetic()
    result = fit(data)
    assert result["success"]
    assert np.isfinite(result["objective"])
    assert result["parameters"]["process_scale"] > 0
    assert result["parameters"]["observation_scale"] > 0


@pytest.mark.parametrize(
    "name",
    ("annealing_rate", "event_coefficient", "background_coefficient", "process_scale"),
)
def test_ablation_fixes_named_parameter_at_exact_zero(name):
    data, _ = synthetic()
    result = fit(data, fixed_zero=(name,))
    assert result["success"]
    assert result["parameters"][name] == 0.0
    assert result["fixed_zero"] == [name]


def test_ablation_rejects_unknown_parameter():
    data, _ = synthetic()
    with pytest.raises(ValueError, match="Unknown fixed-zero"):
        fit(data, fixed_zero=("invented",))


def test_input_contract_rejects_reversed_time():
    observations = np.zeros((3, 2, 2))
    data = StateSpaceData(
        times=np.asarray([0.0, 2.0, 1.0]),
        background=np.zeros(2),
        event=np.zeros(2),
        observations=observations,
    )
    with pytest.raises(ValueError, match="strictly increasing"):
        data.validate()
