"""Build monthly observed environment and transparent mission-response proxies."""

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lattice.cli import software_commit
from lattice.exposure import build_monthly_exposure, read_omni, read_sgps_gt10
from lattice.provenance import sha256, verify, write_json


def load_receipts(path: Path) -> list[dict]:
    rows = json.loads(path.read_text())
    if not isinstance(rows, list):
        raise ValueError(f"Receipt must contain a list: {path}")
    return rows


def make_figure(rows: list[dict], output: Path) -> None:
    dates = [datetime.strptime(row["month"], "%Y-%m") for row in rows]
    f107 = [row["f107_sfu_mean"] for row in rows]
    kp = [row["kp_mean"] for row in rows]
    omni = [
        row["omni_p10"]["fluence_pfu_s"] if row["particle_source"] == "OMNI" else np.nan
        for row in rows
    ]
    sgps = [
        row["sgps_band_integrated_p10_proxy"]["fluence_pfu_s"]
        if row["particle_source"] == "SGPS"
        else np.nan
        for row in rows
    ]
    figure, axes = plt.subplots(3, 1, figsize=(10.2, 7.6), sharex=True, constrained_layout=True)
    axes[0].plot(dates, f107, color="#d1495b", linewidth=1.5)
    axes[0].set_ylabel("F10.7 [sfu]")
    axes[0].set_title("Observed external environment and particle proxy coverage")
    axes[0].text(
        0.01,
        0.91,
        "OBSERVED · NASA OMNI",
        transform=axes[0].transAxes,
        fontsize=8,
        color="#6b1d2a",
    )
    axes[1].plot(dates, omni, color="#1d70a2", linewidth=1.25, label="OMNI observed >10 MeV")
    axes[1].plot(
        dates,
        sgps,
        color="#5b3c88",
        linewidth=1.25,
        label="SGPS band-integrated >10 MeV proxy",
    )
    axes[1].set_yscale("log")
    axes[1].set_ylabel("Monthly fluence\n[pfu s]")
    axes[1].legend(frameon=False, fontsize=8, loc="upper left")
    axes[1].axvspan(datetime(2020, 4, 1), datetime(2020, 11, 1), color="#c8c8c8", alpha=0.45)
    axes[1].text(
        datetime(2020, 7, 15),
        0.04,
        "explicit gap",
        rotation=90,
        ha="center",
        va="bottom",
        transform=axes[1].get_xaxis_transform(),
        fontsize=8,
    )
    axes[2].plot(dates, kp, color="#2a9d8f", linewidth=1.25)
    axes[2].set_ylabel("Kp")
    axes[2].set_xlabel("Calendar month")
    axes[2].text(
        0.01,
        0.91,
        "OBSERVED · HST/LEO shielding covariate; excluded from L2 basis",
        transform=axes[2].transAxes,
        fontsize=8,
        color="#155c53",
    )
    for axis in axes:
        axis.grid(alpha=0.2, linewidth=0.6)
        axis.spines[["top", "right"]].set_visible(False)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--omni-receipt", default="data/manifests/omni_continuous_plan_retrieved.json"
    )
    parser.add_argument("--sgps-receipt", default="data/manifests/goes_sgps_plan_retrieved.json")
    parser.add_argument("--output-dir", default="results/environment")
    args = parser.parse_args()
    root = Path.cwd()
    omni_receipt_path = root / args.omni_receipt
    sgps_receipt_path = root / args.sgps_receipt
    omni_receipts = load_receipts(omni_receipt_path)
    sgps_receipts = load_receipts(sgps_receipt_path)

    omni_rows = []
    for record in omni_receipts:
        omni_rows.extend(read_omni(verify(record, root)))
    sgps_samples = []
    schemas = Counter()
    support_maxima = Counter()
    for index, record in enumerate(sgps_receipts, start=1):
        series = read_sgps_gt10(verify(record, root))
        schemas[series["time_variable"]] += 1
        support_maxima[series["maximum_reported_differential_upper_energy_mev"]] += 1
        sgps_samples.extend(
            zip(
                series["time_utc"],
                series["proton_flux_gt10_mev_derived"],
                series["east_west_absolute_difference"],
                strict=True,
            )
        )
        if index % 250 == 0:
            print(f"Parsed {index}/{len(sgps_receipts)} SGPS files")

    monthly, events = build_monthly_exposure(omni_rows, sgps_samples)
    output = root / args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    monthly_path = output / "monthly_exposure.json"
    events_path = output / "threshold_events.json"
    write_json(monthly_path, {"measurements": monthly})
    write_json(events_path, {"events": events})
    make_figure(monthly, root / "paper/figures/environment_timeline")

    flags = Counter(
        str(int(row["magnetosphere_flux_flag"]))
        for row in omni_rows
        if row["proton_flux_gt10_mev"] is not None
    )
    particle_months = Counter(row["particle_source"] for row in monthly)
    summary = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "source_sha256": sha256(root / "src/lattice/exposure.py"),
        "input_receipts": {
            "omni": {
                "path": args.omni_receipt,
                "sha256": sha256(omni_receipt_path),
                "objects": len(omni_receipts),
                "bytes": sum(row["size_bytes"] for row in omni_receipts),
            },
            "sgps": {
                "path": args.sgps_receipt,
                "sha256": sha256(sgps_receipt_path),
                "objects": len(sgps_receipts),
                "bytes": sum(row["size_bytes"] for row in sgps_receipts),
            },
        },
        "monthly_output_sha256": sha256(monthly_path),
        "events_output_sha256": sha256(events_path),
        "month_count": len(monthly),
        "particle_months_by_source": dict(sorted(particle_months.items())),
        "threshold_events_by_source": dict(
            sorted(Counter(event["source"] for event in events).items())
        ),
        "omni_valid_particle_hours": sum(row["omni_p10"]["valid_samples"] for row in monthly),
        "omni_particle_quality_flags": dict(sorted(flags.items())),
        "sgps_valid_five_minute_samples": sum(
            row["sgps_band_integrated_p10_proxy"]["valid_samples"] for row in monthly
        ),
        "sgps_time_schemas_by_file": dict(sorted(schemas.items())),
        "sgps_differential_support_maxima_mev_by_file": {
            str(key): value for key, value in sorted(support_maxima.items())
        },
        "quantity_boundaries": {
            "omni": "OBSERVED external environment; particle flag -1 means contamination unchecked",
            "sgps": "PROXY integrated from OBSERVED SGPS L2 channel products",
            "response_basis": "PROXY; unfit and not detector dose",
            "inferred_effective_exposure": "NOT ESTIMATED",
            "physical_dose": "NOT ESTIMATED",
        },
        "splice_status": "NO EMPIRICAL INTERCALIBRATION; independent cumulative series retained",
        "physical_inference_gate": "CLOSED",
    }
    write_json(output / "summary.json", summary)
    print(
        f"Wrote {len(monthly)} months and {len(events)} threshold events; "
        "physical-inference gate remains CLOSED"
    )


if __name__ == "__main__":
    main()
