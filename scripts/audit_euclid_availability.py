"""Audit public Euclid Q1 VIS and trap-pumping product availability."""

import csv
import io
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from lattice.cli import software_commit
from lattice.provenance import sha256, write_json

TAP_ROOT = "https://eas.esac.esa.int/tap-server/tap"
ARCHIVE_URL = "https://eas.esac.esa.int/sas/"
DPDD_URL = "https://euclid.esac.esa.int/dr/q1/dpdd/visdpd/visintro.html"
SEARCH_TOKENS = ("cti", "trap", "pumping")


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def table_tokens(value: str) -> set[str]:
    return set(re.split(r"[^a-z0-9]+", value.lower()))


def parse_tables(xml_bytes: bytes) -> list[dict[str, str]]:
    """Extract table names and archive hierarchy labels from VOSI XML."""
    root = ET.fromstring(xml_bytes)
    tables = []
    for element in root.iter():
        if _local_name(element.tag) != "table":
            continue
        name = next(
            (child.text or "" for child in element if _local_name(child.tag) == "name"),
            "",
        )
        hierarchy = next(
            (value for key, value in element.attrib.items() if _local_name(key) == "hierarchy"),
            "",
        )
        tables.append({"name": name, "hierarchy": hierarchy})
    return sorted(tables, key=lambda row: row["name"])


def matching_tables(tables: list[dict[str, str]]) -> dict[str, list[str]]:
    return {
        token: [
            row["name"]
            for row in tables
            if token in table_tokens(f"{row['name']} {row['hierarchy']}")
        ]
        for token in SEARCH_TOKENS
    }


def tap_csv(query: str) -> list[dict[str, str]]:
    payload = urlencode(
        {"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": query}
    ).encode()
    request = Request(f"{TAP_ROOT}/sync", data=payload)
    with urlopen(request, timeout=120) as response:
        text = response.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(text)))


def get_table_inventory() -> list[dict[str, str]]:
    with urlopen(f"{TAP_ROOT}/tables", timeout=120) as response:
        return parse_tables(response.read())


def probe_fits_signature(file_name: str) -> dict[str, object]:
    query = urlencode({"RETRIEVAL_TYPE": "FILE", "release": "q1", "file_name": file_name})
    request = Request(
        f"https://eas.esac.esa.int/sas-dd/data?{query}",
        headers={"Range": "bytes=0-79", "User-Agent": "LATTICE-research/0.1"},
    )
    with urlopen(request, timeout=120) as response:
        signature = response.read(80)
        status = response.status
        disposition = response.headers.get("Content-Disposition", "")
    return {
        "http_status": status,
        "fits_signature": signature.startswith(b"SIMPLE  ="),
        "content_disposition": disposition,
        "bytes_read": len(signature),
        "full_product_downloaded": False,
    }


def summarize_raw_inventory(rows: list[dict[str, str]]) -> dict[str, object]:
    kinds = Counter((row["category"], row["first_type"], row["second_type"]) for row in rows)
    return {
        "vis_raw_frame_count": len(rows),
        "counts_by_kind": [
            {
                "category": key[0],
                "first_type": key[1],
                "second_type": key[2],
                "count": count,
            }
            for key, count in sorted(kinds.items())
        ],
    }


def make_figure(result: dict, output: Path) -> None:
    trap = result["q1_inventory"]["raw_parallel_trap_pumping"]
    counts = [
        result["q1_inventory"]["calibrated_vis_quad_frames"],
        trap["frame_count"],
        result["q1_inventory"]["processed_trap_result_products"],
    ]
    labels = [
        "Calibrated VIS\nquad frames",
        "Raw parallel\ntrap frames",
        "Processed trap\nresult products",
    ]
    colours = ["#326789", "#e07a5f", "#9a9a9a"]
    dates = [datetime.fromisoformat(row["obs_time_utc"]) for row in trap["frames"]]

    figure, axes = plt.subplots(1, 2, figsize=(10.4, 4.6), constrained_layout=True)
    axes[0].bar(labels, counts, color=colours)
    axes[0].set_yscale("symlog", linthresh=1)
    axes[0].set_ylabel("Public Q1 archive records")
    axes[0].set_title("Available Euclid VIS products")
    for index, value in enumerate(counts):
        axes[0].text(index, max(value, 0.22), str(value), ha="center", va="bottom")
    axes[0].spines[["top", "right"]].set_visible(False)
    axes[0].grid(axis="y", alpha=0.2)

    axes[1].scatter(dates, [1] * len(dates), color="#e07a5f", s=24)
    axes[1].set_ylim(0.75, 1.25)
    axes[1].set_yticks([])
    axes[1].xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    axes[1].tick_params(axis="x", rotation=35)
    axes[1].set_title("Raw trap-pumping acquisition times")
    axes[1].text(
        0.5,
        0.18,
        f"{trap['frame_count']} frames x {trap['detectors_per_frame']} CCDs\n"
        "Processed trap catalogue not distributed",
        transform=axes[1].transAxes,
        ha="center",
        va="center",
        fontsize=9,
    )
    axes[1].spines[["top", "right", "left"]].set_visible(False)
    figure.suptitle("Euclid Q1 availability audit — metadata only; no figure digitisation")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main() -> None:
    root = Path.cwd()
    constraint_path = root / "data/literature/euclid_constraints.json"
    constraints = json.loads(constraint_path.read_text())
    tables = get_table_inventory()
    matches = matching_tables(tables)
    raw_rows = tap_csv(
        "SELECT rawframe_oid,file_name,product_id,obs_time_utc,observation_id,"
        "category,first_type,second_type,width,height "
        "FROM q1.raw_frame WHERE instrument_name='VIS' ORDER BY obs_time_utc"
    )
    raw_summary = summarize_raw_inventory(raw_rows)
    trap_rows = [row for row in raw_rows if row["first_type"] == "TRAP_PUMPING"]
    calibrated_count = int(
        tap_csv("SELECT COUNT(*) AS n FROM q1.calibrated_frame WHERE instrument_name='VIS'")[0]["n"]
    )
    detector_count = int(
        tap_csv(
            "SELECT COUNT(*) AS n FROM q1.raw_detector AS d "
            "JOIN q1.raw_frame AS r ON d.l1_raw_frame_oid=r.rawframe_oid "
            "WHERE r.instrument_name='VIS' AND r.first_type='TRAP_PUMPING'"
        )[0]["n"]
    )
    detectors_per_frame = detector_count // len(trap_rows)
    signature = probe_fits_signature(trap_rows[0]["file_name"])
    result = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "constraint_source_sha256": sha256(constraint_path),
        "retrieved_utc": datetime.now(UTC).isoformat(),
        "archive": {
            "service": "ESA Euclid Science Archive Q1 TAP",
            "url": ARCHIVE_URL,
            "tap_url": TAP_ROOT,
            "table_count": len(tables),
            "tables": tables,
            "exact_table_token_matches": matches,
        },
        "q1_inventory": {
            **raw_summary,
            "calibrated_vis_quad_frames": calibrated_count,
            "raw_parallel_trap_pumping": {
                "frame_count": len(trap_rows),
                "detector_record_count": detector_count,
                "detectors_per_frame": detectors_per_frame,
                "date_start": trap_rows[0]["obs_time_utc"],
                "date_end": trap_rows[-1]["obs_time_utc"],
                "frame_dimensions": [
                    int(trap_rows[0]["width"]),
                    int(trap_rows[0]["height"]),
                ],
                "frames": [
                    {
                        "rawframe_oid": int(row["rawframe_oid"]),
                        "observation_id": int(row["observation_id"]),
                        "obs_time_utc": row["obs_time_utc"],
                        "file_name": row["file_name"],
                        "product_id": row["product_id"],
                    }
                    for row in trap_rows
                ],
                "first_file_signature_probe": signature,
            },
            "processed_trap_result_products": 0,
            "processed_cti_time_evolution_products": 0,
            "official_release_matrix": {
                "url": DPDD_URL,
                "DpdVisCTICalibrationResults": "NOT DISTRIBUTED IN Q1",
                "DpdVisCTITimeEvolutionModel": "NOT DISTRIBUTED IN Q1",
                "DpdVisTrapPumpingModel": "NOT DISTRIBUTED IN Q1",
                "DpdVisTrapPumpingResults": "NOT DISTRIBUTED IN Q1",
            },
        },
        "literature_constraints": constraints,
        "availability_gate": {
            "public_calibrated_vis_frames": "AVAILABLE",
            "public_raw_parallel_trap_pumping_frames": "AVAILABLE",
            "machine_readable_processed_trap_series": "NOT DISTRIBUTED IN Q1",
            "raw_trap_series_integration": (
                "DEFERRED UNTIL EUCLID-SPECIFIC MULTI-FRAME REDUCTION IS VALIDATED"
            ),
            "forward_pixel_simulation": "CONDITIONALLY AVAILABLE",
            "observational_euclid_damage_amplitude": "NOT IDENTIFIED",
            "figure_digitisation": "NOT PERFORMED",
            "large_product_download": "NOT PERFORMED",
        },
        "current_release_context": {
            "q2_publication_date": "2026-06-24",
            "q2_doi": "10.57780/esa-ab289b7",
            "q2_scope": (
                "VIS Galactic-bulge images, astrometry and photometry; no trap product advertised"
            ),
        },
        "evidence": (
            "LIVE OFFICIAL TAP METADATA, 80-BYTE FITS SIGNATURE PROBE, OFFICIAL RELEASE "
            "MATRIX, AND PUBLISHED CONSTRAINTS"
        ),
    }
    output = root / "results/euclid/availability_audit.json"
    write_json(output, result)
    make_figure(result, root / "paper/figures/euclid_availability_audit")
    print(
        f"Euclid Q1 tables={len(tables)}; calibrated VIS={calibrated_count}; "
        f"raw trap frames={len(trap_rows)}; processed trap results=0; "
        "large download=NOT PERFORMED"
    )


if __name__ == "__main__":
    main()
