"""Run the frozen paired-dark pilot and export provenance-linked measurements."""

import argparse
import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from lattice.cli import software_commit
from lattice.hst import dq_sample_mask, paired_trails, read_blv, read_raw, summarize
from lattice.provenance import sha256, verify, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--calibrated", action="store_true")
    args = parser.parse_args()
    root = Path.cwd()
    manifest = root / (
        "results/calibration/products.json"
        if args.calibrated
        else "data/manifests/hst_raw_plan_retrieved.json"
    )
    records = json.loads(manifest.read_text())
    if args.calibrated:
        records = [
            dict(
                p["raw_record"],
                cache_path=p["output_path"],
                sha256=p["output_sha256"],
                size_bytes=p["size_bytes"],
            )
            for p in records
        ]
    rows, primary, metadata, profiles = [], [], [], []
    for year in sorted({r["cohort_year"] for r in records}):
        pair = [r for r in records if r["cohort_year"] == year]
        if len(pair) != 2:
            raise ValueError(f"Exactly two records required for {year}")
        paths = [verify(r, root) for r in pair]
        for chip in (1, 2):
            if args.calibrated:
                a, dqa, ma = read_blv(paths[0], chip)
                b, dqb, mb = read_blv(paths[1], chip)
            else:
                a, ma = read_raw(paths[0], chip)
                b, mb = read_raw(paths[1], chip)
            if ma["CCDGAIN"] != mb["CCDGAIN"] or ma["CCDAMP"] != mb["CCDAMP"]:
                raise ValueError("Pair has incompatible gain/readout settings")
            values = paired_trails(a, b)
            if args.calibrated:
                good = dq_sample_mask(dqa, dqb)[values["y"], values["x"]]
                values = {key: value[good] for key, value in values.items()}
                del dqa, dqb
            metadata.append(
                dict(
                    year=year, chip=chip, frames=[ma, mb], source_sha256=[r["sha256"] for r in pair]
                )
            )
            common = dict(
                year=year,
                chip=chip,
                mjd=(ma["EXPSTART"] + mb["EXPSTART"]) / 2,
                commanded_gain=ma["CCDGAIN"],
                source_sha256=[r["sha256"] for r in pair],
                observable="five-pixel downstream-minus-upstream / peak",
                units="dimensionless, electron selection"
                if args.calibrated
                else "dimensionless, native DN selection",
                evidence="OBSERVED",
                interval="95% column-cluster bootstrap; calibration systematics excluded",
            )
            for low, high in ((100, 300), (300, 1000), (1000, 3000)):
                for near, far in ((16, 512), (512, 1024), (1024, 1536), (1536, 2032)):
                    sel = (
                        (values["peak_dn"] >= low)
                        & (values["peak_dn"] < high)
                        & (values["transfer"] >= near)
                        & (values["transfer"] < far)
                    )
                    row = dict(common, transfers=[near, far])
                    row["signal_electrons" if args.calibrated else "signal_dn"] = [low, high]
                    for key in (
                        "parallel_fraction",
                        "leading_fraction",
                        "serial_fraction",
                        "blank_fraction",
                    ):
                        row[key] = summarize(values[key][sel], values["x"][sel])
                    rows.append(row)
            sel = (
                (values["peak_dn"] >= 300)
                & (values["peak_dn"] < 1000)
                & (values["transfer"] >= 1024)
                & (values["transfer"] < 2032)
            )
            result = dict(common)
            for key in (
                "parallel_fraction",
                "leading_fraction",
                "serial_fraction",
                "blank_fraction",
            ):
                result[key] = summarize(values[key][sel], values["x"][sel])
            primary.append(result)
            profile = [
                summarize(values["profile_fraction"][sel, k], values["x"][sel]) for k in range(5)
            ]
            profiles.append(dict(common, profile=profile))
            print(
                f"{year} chip {chip}: {len(values['x'])} persistent peaks; "
                f"primary={result['parallel_fraction']}",
                flush=True,
            )
            del a, b, values
    output = root / ("results/hst_calibrated" if args.calibrated else "results/hst")
    output.mkdir(parents=True, exist_ok=True)
    context = dict(
        software_commit=software_commit(root),
        script_sha256=sha256(Path(__file__)),
        manifest_sha256=sha256(manifest),
        method_sha256=sha256(
            root / ("docs/CALIBRATION_COMPARISON.md" if args.calibrated else "docs/HST_METHOD.md")
        ),
        source_sha256={p.name: sha256(p) for p in (root / "src/lattice").glob("*.py")},
        status="Calibrated development comparison; physical inference gate pending"
        if args.calibrated
        else "EXPLORATORY RAW PILOT; calibrated anchor gate not passed",
        seed=271828,
        bootstrap_resamples=400,
    )
    write_json(output / "measurements.json", dict(context, measurements=rows))
    write_json(output / "primary.json", dict(context, measurements=primary))
    write_json(output / "metadata.json", metadata)
    write_json(output / "profiles.json", dict(context, measurements=profiles))
    plot(primary, root, calibrated=args.calibrated)


def plot(primary, root, calibrated=False):
    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "figure.dpi": 140,
        }
    )
    fig, axes = plt.subplots(2, 1, figsize=(7, 6), sharex=True, layout="constrained")
    colors = {1: "#2166ac", 2: "#b35806"}
    for chip in (1, 2):
        data = [
            r for r in primary if r["chip"] == chip and r["parallel_fraction"]["mean"] is not None
        ]
        for axis, key in zip(axes, ("parallel_fraction", "blank_fraction"), strict=True):
            for gain in sorted({r["commanded_gain"] for r in data}):
                subset = [r for r in data if r["commanded_gain"] == gain]
                yy = np.array([r[key]["mean"] for r in subset])
                lo = np.array([r[key]["lo"] for r in subset])
                hi = np.array([r[key]["hi"] for r in subset])
                axis.errorbar(
                    [r["year"] for r in subset],
                    yy,
                    yerr=[yy - lo, hi - yy],
                    fmt="o" if gain == 1 else "s",
                    color=colors[chip],
                    capsize=3,
                    label=f"WFC{chip}; commanded gain {gain}",
                )
            axis.axhline(0, color="0.5", lw=0.7)
            axis.grid(alpha=0.15)
    axes[0].set_ylabel("Parallel trail / peak")
    axes[1].set_ylabel("Offset-column blank / peak")
    axes[1].set_xlabel("Calendar year (one paired epoch per selected year)")
    axes[0].legend(fontsize=7)
    title = (
        "OBSERVED • ACSCCD calibrated darks\n300–1000 electrons; 1024–2032 transfers"
        if calibrated
        else "OBSERVED • ACS/WFC RAW-dark pilot\n300–1000 DN; 1024–2032 transfers"
    )
    axes[0].set_title(title)
    fig.suptitle(
        "Development observable; not an inferred trap density"
        if calibrated
        else "Exploratory observable; not a calibrated damage history",
        fontsize=10,
    )
    figure_dir = root / "paper/figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    stem = "hst_calibrated_longitudinal" if calibrated else "hst_raw_longitudinal"
    fig.savefig(figure_dir / (stem + ".pdf"))
    output = root / ("results/hst_calibrated" if calibrated else "results/hst")
    fig.savefig(output / (stem + ".png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
