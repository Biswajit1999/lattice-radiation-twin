import numpy as np
import pytest
from netCDF4 import Dataset

from lattice.exposure import (
    build_monthly_exposure,
    goes_version_key,
    parse_omni_line,
    read_sgps_gt10,
    response_basis,
)

OMNI_LINE = (
    "2003 1 0 2312 51 52 57 36 6.5 6.3 25.9 150.5 -5.0 2.8 2.8 2.0 3.4 0.2 "
    "1.2 0.4 0.7 0.9 54536. 4.8 407. -2.1 -4.6 0.046 1.57 6386. 0.4 5. 0.8 1.1 "
    "0.005 -1.38 0.86 6.9 10 52 -4 25 999999.99 99999.99 99999.99 99999.99 "
    "99999.99 99999.99 0 4 111.2 -0.2 -11 15 5.2"
)


def test_omni_parser_converts_fills_and_units():
    row = parse_omni_line(OMNI_LINE)
    assert row["time_utc"] == "2003-01-01T00:00:00+00:00"
    assert row["kp"] == pytest.approx(1.0)
    assert row["f107_sfu"] == pytest.approx(111.2)
    assert row["proton_flux_gt10_mev"] is None


def make_sgps(path, *, old_time_name=False):
    with Dataset(path, "w") as data:
        time_dimension = "record_number" if old_time_name else "time"
        time_name = "L2_SciData_TimeStamp" if old_time_name else "time"
        data.createDimension(time_dimension, 2)
        data.createDimension("detector", 2)
        data.createDimension("channel", 2)
        time = data.createVariable(time_name, "f8", (time_dimension,))
        time.units = "seconds since 2000-01-01 12:00:00 UTC"
        time[:] = [0, 300]
        flux = data.createVariable(
            "AvgDiffProtonFlux", "f4", (time_dimension, "detector", "channel")
        )
        flux[:] = 2.0
        valid = data.createVariable(
            "DiffValidL1bSamplesInAvg",
            "u4",
            (time_dimension, "detector", "channel"),
        )
        valid[:] = 300
        lower = data.createVariable("DiffProtonLowerEnergy", "f4", ("detector", "channel"))
        upper = data.createVariable("DiffProtonUpperEnergy", "f4", ("detector", "channel"))
        lower[:] = [[1_000, 10_000], [1_000, 10_000]]
        upper[:] = [[10_000, 20_000], [10_000, 20_000]]
        integral = data.createVariable("AvgIntProtonFlux", "f4", (time_dimension, "detector"))
        integral[:] = 1.0
        int_valid = data.createVariable(
            "IntValidL1bSamplesInAvg", "u4", (time_dimension, "detector")
        )
        int_valid[:] = 300


def test_sgps_band_integration(tmp_path):
    path = tmp_path / "sgps.nc"
    make_sgps(path)
    result = read_sgps_gt10(path)
    assert result["proton_flux_gt10_mev_derived"] == [20001.0, 20001.0]
    with Dataset(path, "a") as data:
        data["DiffValidL1bSamplesInAvg"][0, 0, 1] = 0
        data["DiffValidL1bSamplesInAvg"][0, 1, 1] = 0
    result = read_sgps_gt10(path)
    assert result["proton_flux_gt10_mev_derived"][0] is None


def test_sgps_supports_historical_time_name_and_masked_validity(tmp_path):
    path = tmp_path / "sgps-old.nc"
    make_sgps(path, old_time_name=True)
    with Dataset(path, "a") as data:
        data["DiffValidL1bSamplesInAvg"][0, :, 1] = np.ma.masked
    result = read_sgps_gt10(path)
    assert result["time_utc"][0] == "2000-01-01T12:00:00+00:00"
    assert result["proton_flux_gt10_mev_derived"][0] is None


def test_response_bases_keep_leo_and_l2_distinct():
    basis = response_basis(proton_flux_gt10_mev=99, kp=4.5, f107_sfu=140)
    assert basis["shared_external"]["sep_log1p"] == pytest.approx(np.log(100))
    assert "sep_x_geomagnetic_activity" in basis["hst_leo"]
    assert "sep_x_geomagnetic_activity" not in basis["l2"]


def test_goes_filename_versions_are_sorted_numerically():
    assert goes_version_key("sci_sgps-l2-avg5m_g16_d20240101_v3-0-10.nc") > goes_version_key(
        "sci_sgps-l2-avg5m_g16_d20240101_v3-0-2.nc"
    )


def test_monthly_exposure_keeps_instrument_gap_and_response_domains_distinct():
    omni = []
    for line in (OMNI_LINE, OMNI_LINE.replace("2003 1 0", "2003 1 1")):
        row = parse_omni_line(line)
        row["proton_flux_gt10_mev"] = 20.0
        omni.append(row)
    sgps = [
        ("2003-03-01T00:00:00+00:00", 30.0, 2.0),
        ("2003-03-01T00:05:00+00:00", 5.0, 1.0),
    ]
    rows, events = build_monthly_exposure(omni, sgps, start="2003-01", end="2003-03")
    assert [row["particle_source"] for row in rows] == ["OMNI", "GAP", "SGPS"]
    assert rows[0]["particle_fluence_pfu_s"] == pytest.approx(40 * 3600)
    assert rows[1]["particle_flux_mean_pfu"] is None
    assert "sep_x_geomagnetic_activity" in rows[0]["response_basis"]["hst_leo"]
    assert "sep_x_geomagnetic_activity" not in rows[0]["response_basis"]["l2"]
    assert [(event["source"], event["sample_count"]) for event in events] == [
        ("OMNI", 2),
        ("SGPS", 1),
    ]
