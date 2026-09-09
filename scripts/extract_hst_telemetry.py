"""Join exact matched engineering products to acquisition-state headers."""

import argparse
import json
from pathlib import Path

from astropy.io import fits

from lattice.cli import software_commit
from lattice.cohort import select_analysis_records
from lattice.provenance import sha256, verify, write_json
from lattice.telemetry import read_support


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-manifest", default="data/manifests/hst_raw_plan_retrieved.json")
    parser.add_argument(
        "--support-manifest", default="data/manifests/hst_support_plan_retrieved.json"
    )
    parser.add_argument("--output", default="results/hst/operating_state.json")
    parser.add_argument("--required-role")
    args = parser.parse_args()
    root = Path.cwd()
    raw_path = root / args.raw_manifest
    support_path = root / args.support_manifest
    raw = select_analysis_records(json.loads(raw_path.read_text()), args.required_role)
    support = select_analysis_records(json.loads(support_path.read_text()), args.required_role)
    by_root = {r["original_filename"].split("_")[0]: r for r in support}
    if len(by_root) != len(support):
        raise ValueError("Duplicate support exposure")
    rows = []
    for r in raw:
        obs = r["original_filename"].split("_")[0]
        s = by_root[obs]
        row = read_support(verify(s, root), obs)
        with fits.open(verify(r, root), memmap=False) as hdus:
            h = hdus[0].header
            if h["ROOTNAME"].lower() != obs:
                raise ValueError("RAW identity mismatch")
            keys = [
                "EXPSTART",
                "DATE-OBS",
                "EXPTIME",
                "FLASHDUR",
                "FLASHSTA",
                "SHUTRPOS",
                "CCDGAIN",
                "CCDAMP",
                "BSIDEOPS",
            ]
            row["acquisition"] = {k: h.get(k) for k in keys}
        row.update(
            year=r["cohort_year"],
            pair_id=r.get("pair_id"),
            pair_index=r.get("pair_index"),
            analysis_role=r.get("analysis_role", "development"),
            raw_sha256=r["sha256"],
            support_sha256=s["sha256"],
        )
        rows.append(row)
    result = dict(
        software_commit=software_commit(root),
        script_sha256=sha256(Path(__file__)),
        source_sha256=sha256(root / "src/lattice/telemetry.py"),
        manifest_sha256={"raw": sha256(raw_path), "support": sha256(support_path)},
        interpretation="Engineering snapshots, not exposure-averaged calibrated thermometry",
        exposures=rows,
    )
    write_json(root / args.output, result)
    print(f"Preserved matched telemetry for {len(rows)} exposures")


if __name__ == "__main__":
    main()
