"""Parsers and transparent transforms for measured space-environment data."""

import calendar
from collections import defaultdict
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
    """Build a transparent >10 MeV proxy from SGPS differential and integral channels."""
    with Dataset(path) as data:
        time_name = "time" if "time" in data.variables else "L2_SciData_TimeStamp"
        required = {
            time_name,
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
        valid_counts = np.ma.asarray(data["DiffValidL1bSamplesInAvg"][:])
        valid = np.ma.filled(valid_counts, 0) > 0
        valid &= ~np.ma.getmaskarray(flux)
        flux = np.ma.masked_where(~valid, flux)
        band_integral = np.ma.sum(flux * widths[None, :, :], axis=2)
        integral = np.ma.asarray(data["AvgIntProtonFlux"][:], dtype=float)
        integral_counts = np.ma.asarray(data["IntValidL1bSamplesInAvg"][:])
        integral_valid = np.ma.filled(integral_counts, 0) > 0
        integral_valid &= ~np.ma.getmaskarray(integral)
        integral = np.ma.masked_where(~integral_valid, integral)
        relevant = widths > 0
        complete = np.all(valid | ~relevant[None, :, :], axis=2) & integral_valid
        by_detector = np.ma.masked_where(~complete, band_integral + integral)
        combined = np.ma.mean(by_detector, axis=1)
        sensor_count = np.sum(~np.ma.getmaskarray(by_detector), axis=1)
        sensor_difference = np.ma.abs(by_detector[:, 0] - by_detector[:, 1])
        sensor_difference = np.ma.masked_where(sensor_count != 2, sensor_difference)
        times = num2date(
            data[time_name][:],
            units=data[time_name].units,
            only_use_cftime_datetimes=False,
            only_use_python_datetimes=True,
        )
        return {
            "time_utc": [value.replace(tzinfo=UTC).isoformat() for value in times],
            "proton_flux_gt10_mev_derived": [
                None if np.ma.is_masked(value) else float(value) for value in combined
            ],
            "valid_sensor_count": [int(value) for value in sensor_count],
            "east_west_absolute_difference": [
                None if np.ma.is_masked(value) else float(value) for value in sensor_difference
            ],
            "method": (
                "Integrated the portions above 10 MeV of every reported differential energy "
                "interval, added the L2 >500 MeV integral channel, and averaged complete "
                "east/west sensor reconstructions"
            ),
            "units": "protons cm^-2 s^-1 sr^-1",
            "quantity_class": "PROXY derived from OBSERVED differential and integral channels",
            "time_variable": time_name,
            "maximum_reported_differential_upper_energy_mev": float(np.max(upper) / 1000),
        }


def _mean(values):
    finite = [float(value) for value in values if value is not None and np.isfinite(value)]
    return float(np.mean(finite)) if finite else None


def _month_sequence(start: str, end: str) -> list[str]:
    year, month = (int(value) for value in start.split("-"))
    end_year, end_month = (int(value) for value in end.split("-"))
    result = []
    while (year, month) <= (end_year, end_month):
        result.append(f"{year:04d}-{month:02d}")
        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1
    return result


def summarize_particle_samples(
    samples, *, source: str, step_seconds: int, start: str, end: str, threshold: float = 10.0
) -> tuple[dict[str, dict], list[dict]]:
    """Summarize an ordered particle series without filling gaps or rescaling coverage."""
    buckets = defaultdict(lambda: {"values": [], "directional": [], "threshold_samples": 0})
    events = []
    active = None
    previous_time = None

    def finish_event():
        nonlocal active
        if active is not None:
            active["end_utc"] = active.pop("last_time_utc")
            active["duration_seconds"] = active["sample_count"] * step_seconds
            events.append(active)
            active = None

    for time_utc, flux, directional_difference in samples:
        stamp = datetime.fromisoformat(time_utc)
        month = time_utc[:7]
        if start <= month <= end and flux is not None and np.isfinite(flux):
            value = float(flux)
            buckets[month]["values"].append(value)
            if directional_difference is not None and np.isfinite(directional_difference):
                buckets[month]["directional"].append(float(directional_difference))
            contiguous = previous_time is not None and stamp - previous_time == timedelta(
                seconds=step_seconds
            )
            if value >= threshold:
                buckets[month]["threshold_samples"] += 1
                if active is None or not contiguous:
                    finish_event()
                    active = {
                        "source": source,
                        "quantity_class": "OBSERVED" if source == "OMNI" else "PROXY",
                        "threshold_pfu": threshold,
                        "start_utc": time_utc,
                        "last_time_utc": time_utc,
                        "sample_count": 1,
                        "integrated_fluence_pfu_s": value * step_seconds,
                        "peak_flux_pfu": value,
                    }
                else:
                    active["last_time_utc"] = time_utc
                    active["sample_count"] += 1
                    active["integrated_fluence_pfu_s"] += value * step_seconds
                    active["peak_flux_pfu"] = max(active["peak_flux_pfu"], value)
            else:
                finish_event()
            previous_time = stamp
        else:
            finish_event()
            previous_time = None
    finish_event()

    monthly = {}
    for month in _month_sequence(start, end):
        year, number = (int(value) for value in month.split("-"))
        expected = calendar.monthrange(year, number)[1] * 86400 // step_seconds
        bucket = buckets[month]
        values = bucket["values"]
        monthly[month] = {
            "source": source,
            "valid_samples": len(values),
            "expected_samples": expected,
            "coverage_fraction": len(values) / expected,
            "flux_mean_pfu": _mean(values),
            "fluence_pfu_s": float(np.sum(values) * step_seconds) if values else None,
            "threshold_samples": bucket["threshold_samples"],
            "threshold_event_marker": bucket["threshold_samples"] > 0,
            "east_west_absolute_difference_mean_pfu": _mean(bucket["directional"]),
        }
    return monthly, events


def summarize_omni_environment(rows, *, start: str, end: str) -> dict[str, dict]:
    """Return monthly arithmetic means and explicit valid counts for OMNI observations."""
    fields = (
        "bz_gsm_nt",
        "proton_density_cm3",
        "solar_wind_speed_km_s",
        "kp",
        "sunspot_number",
        "dst_nt",
        "ae_nt",
        "ap_nt",
        "f107_sfu",
    )
    buckets = defaultdict(lambda: defaultdict(list))
    for row in rows:
        month = row["time_utc"][:7]
        if start <= month <= end:
            for field in fields:
                if row[field] is not None:
                    buckets[month][field].append(row[field])
    result = {}
    for month in _month_sequence(start, end):
        values = buckets[month]
        result[month] = {f"{field}_mean": _mean(values[field]) for field in fields} | {
            f"{field}_valid_hours": len(values[field]) for field in fields
        }
    return result


def solar_cycle_coordinate(month: str) -> dict:
    """Return a calendar coordinate anchored to official SILSO cycle minima."""
    year, number = (int(value) for value in month.split("-"))
    index = year * 12 + number - 1
    minima = ((23, 1996, 8), (24, 2008, 12), (25, 2019, 12))
    eligible = [entry for entry in minima if entry[1] * 12 + entry[2] - 1 <= index]
    cycle, minimum_year, minimum_month = eligible[-1]
    return {
        "solar_cycle_number": cycle,
        "months_since_cycle_minimum": index - (minimum_year * 12 + minimum_month - 1),
    }


def build_monthly_exposure(omni_rows, sgps_samples, *, start="2003-01", end="2025-12"):
    """Combine observations and proxies while retaining the OMNI/SGPS discontinuity."""
    environment = summarize_omni_environment(omni_rows, start=start, end=end)
    omni_samples = [(row["time_utc"], row["proton_flux_gt10_mev"], None) for row in omni_rows]
    omni, omni_events = summarize_particle_samples(
        omni_samples, source="OMNI", step_seconds=3600, start=start, end=end
    )
    sgps, sgps_events = summarize_particle_samples(
        sgps_samples, source="SGPS", step_seconds=300, start=start, end=end
    )
    events = omni_events + sgps_events
    cumulative_omni = 0.0
    cumulative_sgps = 0.0
    omni_started = False
    sgps_started = False
    rows = []
    for month in _month_sequence(start, end):
        omni_fluence = omni[month]["fluence_pfu_s"]
        sgps_fluence = sgps[month]["fluence_pfu_s"]
        if omni_fluence is not None:
            cumulative_omni += omni_fluence
            omni_started = True
        if sgps_fluence is not None:
            cumulative_sgps += sgps_fluence
            sgps_started = True
        if sgps[month]["valid_samples"]:
            particle = sgps[month]
            particle_source = "SGPS"
        elif omni[month]["valid_samples"]:
            particle = omni[month]
            particle_source = "OMNI"
        else:
            particle = {
                "flux_mean_pfu": None,
                "fluence_pfu_s": None,
                "coverage_fraction": 0.0,
                "threshold_event_marker": False,
            }
            particle_source = "GAP"
        env = environment[month]
        basis = response_basis(
            proton_flux_gt10_mev=particle["flux_mean_pfu"],
            kp=env["kp_mean"],
            f107_sfu=env["f107_sfu_mean"],
        )
        row = {
            "month": month,
            "evidence_type": "OBSERVED EXTERNAL ENVIRONMENT + TRANSPARENT PROXIES",
            **solar_cycle_coordinate(month),
            **env,
            "omni_p10": omni[month],
            "sgps_band_integrated_p10_proxy": sgps[month],
            "particle_source": particle_source,
            "particle_flux_mean_pfu": particle["flux_mean_pfu"],
            "particle_fluence_pfu_s": particle["fluence_pfu_s"],
            "particle_coverage_fraction": particle["coverage_fraction"],
            "particle_threshold_event_marker": particle["threshold_event_marker"],
            "omni_cumulative_observed_fluence_pfu_s": (cumulative_omni if omni_started else None),
            "sgps_cumulative_proxy_fluence_pfu_s": cumulative_sgps if sgps_started else None,
            "response_basis": basis,
        }
        rows.append(row)

    for index, row in enumerate(rows):
        prior = rows[index - 1] if index else None
        row["f107_change_from_previous_month_sfu"] = (
            row["f107_sfu_mean"] - prior["f107_sfu_mean"]
            if prior and row["f107_sfu_mean"] is not None and prior["f107_sfu_mean"] is not None
            else None
        )
        window = rows[max(0, index - 2) : index + 1]
        ap_values = [item["ap_nt_mean"] for item in window]
        row["ap_rolling_3_month_mean_nt"] = _mean(ap_values) if len(window) == 3 else None
        same_source = len(window) == 3 and len({item["particle_source"] for item in window}) == 1
        complete_enough = same_source and all(
            item["particle_coverage_fraction"] >= 0.8 for item in window
        )
        row["particle_rolling_3_month_fluence_pfu_s"] = (
            float(sum(item["particle_fluence_pfu_s"] for item in window))
            if complete_enough and row["particle_source"] != "GAP"
            else None
        )
        year, number = (int(value) for value in row["month"].split("-"))
        month_end = (
            datetime(year + 1, 1, 1, tzinfo=UTC)
            if number == 12
            else datetime(year, number + 1, 1, tzinfo=UTC)
        )
        eligible = [
            event
            for event in events
            if event["source"] == row["particle_source"]
            and datetime.fromisoformat(event["end_utc"]) < month_end
        ]
        row["days_since_source_threshold_event"] = (
            (month_end - datetime.fromisoformat(eligible[-1]["end_utc"])).total_seconds() / 86400
            if eligible
            else None
        )
    return rows, events


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
