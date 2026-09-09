"""Join exact matched engineering products to acquisition-state headers."""

import json
from pathlib import Path

from astropy.io import fits

from lattice.cli import software_commit
from lattice.provenance import sha256, verify, write_json
from lattice.telemetry import read_support


def main():
    root = Path.cwd()
    raw_path = root / "data/manifests/hst_raw_plan_retrieved.json"
    support_path = root / "data/manifests/hst_support_plan_retrieved.json"
    raw = json.loads(raw_path.read_text())
    support = json.loads(support_path.read_text())
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
        row.update(year=r["cohort_year"], raw_sha256=r["sha256"], support_sha256=s["sha256"])
        rows.append(row)
    result = dict(
        software_commit=software_commit(root),
        script_sha256=sha256(Path(__file__)),
        source_sha256=sha256(root / "src/lattice/telemetry.py"),
        manifest_sha256={"raw": sha256(raw_path), "support": sha256(support_path)},
        interpretation="Engineering snapshots, not exposure-averaged calibrated thermometry",
        exposures=rows,
    )
    write_json(root / "results/hst/operating_state.json", result)
    print(f"Preserved matched telemetry for {len(rows)} exposures")


if __name__ == "__main__":
    main()
