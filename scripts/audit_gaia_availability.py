"""Audit official Gaia Archive tables and published CTI constraints."""

import json
import re
from datetime import UTC, datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from astroquery.gaia import Gaia

from lattice.cli import software_commit
from lattice.provenance import sha256, write_json

SEARCH_TOKENS = ("cti", "charge", "injection", "calibration", "engineering")


def table_tokens(name: str) -> set[str]:
    return set(re.split(r"[^a-z0-9]+", name.lower()))


def matching_tables(names: list[str]) -> dict[str, list[str]]:
    return {
        token: [name for name in names if token in table_tokens(name)] for token in SEARCH_TOKENS
    }


def event_comparison(exposure_rows: list[dict]) -> dict:
    target = next(row for row in exposure_rows if row["month"] == "2017-09")
    ranked = sorted(
        (
            (row["response_basis"]["shared_external"]["sep_log1p"], row["month"])
            for row in exposure_rows
            if row["particle_source"] == "OMNI"
            and row["response_basis"]["shared_external"]["sep_log1p"] is not None
        ),
        reverse=True,
    )
    rank = next(index for index, (_, month) in enumerate(ranked, start=1) if month == "2017-09")
    return {
        "published_event_date": "2017-09-10",
        "comparison_month": "2017-09",
        "local_particle_source": target["particle_source"],
        "local_threshold_event_marker": target["particle_threshold_event_marker"],
        "local_shared_l2_sep_log1p": target["response_basis"]["shared_external"]["sep_log1p"],
        "rank_among_omni_months_descending": rank,
        "omni_month_count": len(ranked),
        "top_decile_event_proxy": rank <= max(1, len(ranked) // 10),
        "date_consistency": "PASS" if target["particle_threshold_event_marker"] else "FAIL",
        "amplitude_validation": "NOT RUN; published engineering series unavailable",
    }


def make_figure(exposure_rows: list[dict], result: dict, output: Path) -> None:
    selected = [row for row in exposure_rows if "2014-01" <= row["month"] <= "2025-03"]
    dates = [datetime.strptime(row["month"], "%Y-%m") for row in selected]
    values = [
        np.nan
        if row["response_basis"]["shared_external"]["sep_log1p"] is None
        else row["response_basis"]["shared_external"]["sep_log1p"]
        for row in selected
    ]
    figure, axis = plt.subplots(figsize=(9.2, 4.8), constrained_layout=True)
    axis.plot(dates, values, color="#5b3c88", linewidth=1.1, label="shared L2 SEP proxy")
    event_date = datetime(2017, 9, 1)
    event_value = next(
        value for date, value in zip(dates, values, strict=True) if date == event_date
    )
    axis.scatter([event_date], [event_value], color="#d1495b", zorder=3)
    axis.annotate(
        "Published Gaia step: 10 Sep 2017\nproxy rank: 7 / 200 OMNI months",
        xy=(event_date, event_value),
        xytext=(datetime(2018, 7, 1), np.nanmax(values) * 0.87),
        arrowprops={"arrowstyle": "->", "color": "#d1495b"},
        fontsize=9,
    )
    gate = result["availability_gate"]
    axis.text(
        0.99,
        0.96,
        f"Gaia CTI tables: {gate['official_archive_candidate_table_count']} / "
        f"{result['archive']['table_count']}\nDirect quantitative validation: blocked",
        transform=axis.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox={"facecolor": "white", "edgecolor": "#999999", "alpha": 0.9},
    )
    axis.set(
        title="Gaia literature-constraint and public-data audit",
        xlabel="Month",
        ylabel="Near-Earth shared SEP proxy, log(1 + flux)",
    )
    axis.grid(alpha=0.2)
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(frameon=False, loc="upper left")
    axis.text(
        0.01,
        0.02,
        "Proxy timing is not Gaia detector dose; no CTI figure was digitised.",
        transform=axis.transAxes,
        fontsize=8,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main() -> None:
    root = Path.cwd()
    constraint_path = root / "data/literature/gaia_constraints.json"
    exposure_path = root / "results/environment/monthly_exposure.json"
    constraints = json.loads(constraint_path.read_text())
    exposure = json.loads(exposure_path.read_text())["measurements"]
    tables = sorted(table.name for table in Gaia.load_tables(only_names=True))
    matches = matching_tables(tables)
    direct_tables = sorted({name for values in matches.values() for name in values})
    result = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "constraint_source_sha256": sha256(constraint_path),
        "exposure_source_sha256": sha256(exposure_path),
        "retrieved_utc": datetime.now(UTC).isoformat(),
        "archive": {
            "service": "ESA Gaia Archive TAP schema via astroquery.gaia",
            "url": "https://gea.esac.esa.int/archive/",
            "table_count": len(tables),
            "table_names": tables,
            "exact_token_matches": matches,
            "candidate_engineering_tables": direct_tables,
        },
        "literature_constraints": constraints,
        "l2_environment_comparison": {
            "continuous_component": {
                "published": "steeper damage accumulation near solar minimum",
                "lattice_basis": "inverse_f107_gcr_proxy",
                "structural_sign_consistency": "PASS",
                "quantitative_validation": "NOT RUN; published engineering series unavailable",
            },
            "september_2017_event": event_comparison(exposure),
        },
        "availability_gate": {
            "machine_readable_gaia_cti_series": "NOT LOCATED",
            "official_archive_candidate_table_count": len(direct_tables),
            "direct_quantitative_validation": "BLOCKED",
            "literature_constraint_validation": "AVAILABLE",
            "same_functional_form_vs_hst": "NOT TESTABLE WITH PUBLIC TABLES LOCATED",
            "figure_digitisation": "NOT PERFORMED",
        },
        "evidence": (
            "OFFICIAL ARCHIVE SCHEMA METADATA, PUBLISHED CONSTRAINTS, AND LOCAL ENVIRONMENT PROXY"
        ),
    }
    output = root / "results/gaia/availability_audit.json"
    write_json(output, result)
    make_figure(exposure, result, root / "paper/figures/gaia_literature_validation")
    print(
        f"Gaia tables={len(tables)}; candidate engineering tables={len(direct_tables)}; "
        "direct validation=BLOCKED; figure digitisation=NOT PERFORMED"
    )


if __name__ == "__main__":
    main()
