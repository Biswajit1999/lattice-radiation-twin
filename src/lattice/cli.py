"""Deterministic acquisition entry points; frozen manifests are replay inputs."""

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from lattice.provenance import fetch, verify, write_json


def software_commit(root: Path) -> str:
    git = shutil.which("git.exe") or shutil.which("git")
    return subprocess.check_output([git, "rev-parse", "HEAD"], cwd=root, text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True)
    omni = sub.add_parser("fetch-omni")
    omni.add_argument("--years", nargs="+", type=int, required=True)
    check = sub.add_parser("verify")
    check.add_argument("manifest", type=Path)
    replay = sub.add_parser("fetch-plan")
    replay.add_argument("plan", type=Path)
    replay.add_argument("--max-mb", type=int, default=200)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == "verify":
        records = json.loads(args.manifest.read_text())
        for record in records:
            verify(record, root)
        print(f"Verified {len(records)} objects")
        return
    commit = software_commit(root)
    if args.command == "fetch-omni":
        specs = [
            {
                "source_identifier": f"NASA-SPDF/OMNI2/hourly/{year}",
                "mission": "OMNI",
                "instrument": "multi-spacecraft compilation",
                "original_filename": f"omni2_{year}.dat",
                "tier": "A",
                "url": f"https://spdf.gsfc.nasa.gov/pub/data/omni/low_res_omni/omni2_{year}.dat",
                "processing_level": "hourly merged near-Earth environment",
                "pipeline_version": "OMNI2; upstream revision unspecified, bytes pinned by SHA-256",
                "usage_note": "NASA SPDF public data; acknowledge OMNI and upstream PIs; "
                "https://omniweb.gsfc.nasa.gov/html/ow_data.html",
                "selection_reason": "Preselected calendar years for HST environment alignment",
            }
            for year in sorted(set(args.years))
        ]
        target = root / "data/manifests/omni.json"
        max_bytes = 20_000_000
    else:
        specs = json.loads(args.plan.read_text())
        target = root / "data/manifests" / (args.plan.stem + "_retrieved.json")
        max_bytes = args.max_mb * 1_000_000
    records = json.loads(target.read_text()) if target.exists() else []
    for spec in specs:
        previous = next(
            (r for r in records if r["source_identifier"] == spec["source_identifier"]), None
        )
        if previous:
            try:
                verify(previous, root)
                print(f"Cached and verified {previous['original_filename']}")
                continue
            except FileNotFoundError:
                pass
        record = fetch(
            spec, root, commit, max_bytes, expected_sha256=(previous or spec).get("sha256")
        )
        records = [r for r in records if r["source_identifier"] != spec["source_identifier"]]
        records.append(record)
        write_json(target, records)
        print(f"Retrieved {record['original_filename']} {record['size_bytes']} bytes")


if __name__ == "__main__":
    main()
