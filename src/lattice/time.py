"""Explicit UTC conversions; MJD is never interpreted as Unix time."""

import numpy as np
from astropy.time import Time


def utc_to_mjd(utc: str) -> float:
    return float(Time(utc, scale="utc").mjd)


def year_doy_hour_to_mjd(year: np.ndarray, doy: np.ndarray, hour: np.ndarray) -> np.ndarray:
    from datetime import datetime, timedelta

    values = []
    for y, d, h in zip(year, doy, hour, strict=True):
        if not (1 <= d <= 366 and 0 <= h <= 23):
            raise ValueError("Invalid day or hour")
        dt = datetime(int(y), 1, 1) + timedelta(days=int(d) - 1, hours=int(h))
        if dt.year != int(y):
            raise ValueError("Invalid day for year")
        values.append(dt.isoformat())
    return np.asarray(Time(values, scale="utc").mjd)
