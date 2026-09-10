"""Parsers and transparent transforms for measured space-environment data."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
from netCDF4 import Dataset, num2date

OMNI_COLUMNS = {
    "year": (0, None),
    "day_of_year": (1, None),
    "hour": (2, None),
    "bz_gsm_nt": (16, 999.9),
    "proton_density_cm3": (23, 999.9),
    "solar_wind_speed_km_s": (24, 9999.0),
    "kp": (38, 99.0),
    "sunspot_number": (39, 999.0),
    "dst_nt": (40, 99999.0),
    "ae_nt": (41, 9999.0),
    "proton_flux_gt1_mev": (42, 999999.99),
    "proton_flux_gt2_mev": (43, 99999.99),
    "proton_flux_gt4_mev": (44, 99999.99),
    "proton_flux_gt10_mev": (45, 99999.99),
    "proton_flux_gt30_mev": (46, 99999.99),
    "proton_flux_gt60_mev": (47, 99999.99),
    "magnetosphere_flux_flag": (48, None),
    "ap_nt": (49, 999.0),
    "f107_sfu": (50, 999.9),
}


def goes_version_key(filename):
    """Sort NOAA hyphenated product versions numerically rather than lexicographically."""
    value = filename.rsplit("_v", 1)[1].removesuffix(".nc")
    return tuple(int(part) for part in value.split("-"))


def parse_omni_line(line: str) -> dict:
    """Parse one 55/57-word OMNI2 hourly ASCII record and convert fills to nulls."""
    words = line.split()
    if len(words) not in {55, 57}:
        raise ValueError(f"Expected 55 or 57 OMNI2 words, received {len(words)}")
    values = {}
    for name, (index, fill) in OMNI_COLUMNS.items():
        value = float(words[index])
        values[name] = None if fill is not None and value == fill else value
    year = int(values.pop("year"))
    day = int(values.pop("day_of_year"))
    hour = int(values.pop("hour"))
    values["kp"] = values["kp"] / 10 if values["kp"] is not None else None
    values["time_utc"] = (
        datetime(year, 1, 1, tzinfo=UTC) + timedelta(days=day - 1, hours=hour)
    ).isoformat()
    return values


def read_omni(path: Path) -> list[dict]:
    with path.open(encoding="ascii") as stream:
        return [parse_omni_line(line) for line in stream if line.strip()]


def read_sgps_gt10(path: Path) -> dict:
    """Integrate SGPS differential bands above 10 MeV and append its >500 MeV channel."""
    with Dataset(path) as data:
        required = {
            "time",
            "AvgDiffProtonFlux",
            "DiffValidL1bSamplesInAvg",
            "DiffProtonLowerEnergy",
            "DiffProtonUpperEnergy",
            "AvgIntProtonFlux",
            "IntValidL1bSamplesInAvg",
        }
        if missing := required - data.variables.keys():
            raise ValueError(f"Missing SGPS variables: {sorted(missing)}")
        lower = np.asarray(data["DiffProtonLowerEnergy"][:], dtype=float)
        upper = np.asarray(data["DiffProtonUpperEnergy"][:], dtype=float)
        widths = np.clip(upper - np.maximum(lower, 10_000.0), 0, None)
        flux = np.ma.asarray(data["AvgDiffProtonFlux"][:], dtype=float)
        valid = np.asarray(data["DiffValidL1bSamplesInAvg"][:]) > 0
        flux = np.ma.masked_where(~valid, flux)
        band_integral = np.ma.sum(flux * widths[None, :, :], axis=2)
        integral = np.ma.asarray(data["AvgIntProtonFlux"][:], dtype=float)
        integral_valid = np.asarray(data["IntValidL1bSamplesInAvg"][:]) > 0
        integral = np.ma.masked_where(~integral_valid, integral)
        relevant = widths > 0
        complete = np.all(valid | ~relevant[None, :, :], axis=2) & integral_valid
        by_detector = np.ma.masked_where(~complete, band_integral + integral)
        combined = np.ma.mean(by_detector, axis=1)
        times = num2date(
            data["time"][:],
            units=data["time"].units,
            only_use_cftime_datetimes=False,
            only_use_python_datetimes=True,
        )
        return {
            "time_utc": [value.replace(tzinfo=UTC).isoformat() for value in times],
            "proton_flux_gt10_mev_derived": [
                None if np.ma.is_masked(value) else float(value) for value in combined
            ],
            "method": (
                "Integrated L2 differential bins from 10 to 500 MeV plus the L2 >500 MeV "
                "integral channel; east/west detector mean where valid"
            ),
            "units": "protons cm^-2 s^-1 sr^-1",
        }


def response_basis(*, proton_flux_gt10_mev, kp, f107_sfu) -> dict:
    """Return unfit mission-specific basis terms; these are proxies, never physical dose."""
    sep = None if proton_flux_gt10_mev is None else float(np.log1p(proton_flux_gt10_mev))
    geomagnetic_activity = None if kp is None else float(np.clip(kp / 9, 0, 1))
    gcr_proxy = None if f107_sfu is None else float(70.0 / max(f107_sfu, 1.0))
    return {
        "shared_external": {"sep_log1p": sep, "inverse_f107_gcr_proxy": gcr_proxy},
        "hst_leo": {
            "sep_log1p": sep,
            "sep_x_geomagnetic_activity": (
                None if sep is None or geomagnetic_activity is None else sep * geomagnetic_activity
            ),
            "inverse_f107_gcr_proxy": gcr_proxy,
        },
        "l2": {"sep_log1p": sep, "inverse_f107_gcr_proxy": gcr_proxy},
    }
