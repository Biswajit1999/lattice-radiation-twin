import numpy as np
import pytest

from lattice.time import utc_to_mjd, year_doy_hour_to_mjd


def test_mjd_epoch_and_leap_day():
    assert utc_to_mjd("2000-01-01T12:00:00") == 51544.5
    result = year_doy_hour_to_mjd(np.array([2024]), np.array([60]), np.array([0]))
    assert result[0] == utc_to_mjd("2024-02-29")


def test_utc_leap_second():
    a = utc_to_mjd("2016-12-31T23:59:60")
    b = utc_to_mjd("2017-01-01T00:00:00")
    assert 0.999 < (b - a) * 86400 < 1.001


def test_invalid_day():
    with pytest.raises(ValueError):
        year_doy_hour_to_mjd(np.array([2023]), np.array([366]), np.array([0]))
