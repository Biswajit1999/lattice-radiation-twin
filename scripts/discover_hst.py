"""Freeze a deterministic paired-dark cohort using live MAST metadata."""

import argparse
import json
from pathlib import Path
from urllib.parse import quote

from astroquery.mast import Observations

from lattice.cli import software_commit
from lattice.provenance import register, write_json
from lattice.time import utc_to_mjd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", nargs="+", type=int, required=True)
    parser.add_argument("--month", type=int, default=7)
    args = parser.parse_args()
    root = Path.cwd()
    commit = software_commit(root)
    Observations.TIMEOUT = 60
    plan, snapshots, exclusions = [], [], []
    for year in sorted(set(args.years)):
        start = utc_to_mjd(f"{year}-{args.month:02d}-01")
        query = dict(
            obs_collection="HST",
            instrument_name="ACS/WFC",
            target_name="DARK*",
            t_min=[start, start + 31],
            t_exptime=[900, 1200],
            dataRights="PUBLIC",
        )
        table = Observations.query_criteria(**query)
        rows = [{k: str(row[k]) for k in table.colnames} for row in table]
        rows.sort(key=lambda r: (float(r["t_min"]), r["obs_id"]))
        selected = []
        for i in range(len(rows) - 1):
            if float(rows[i + 1]["t_min"]) - float(rows[i]["t_min"]) <= 1.0:
                selected = rows[i : i + 2]
                break
        snap = root / f"data/cache/hst/query_{year}.json"
        write_json(snap, {"query": query, "rows": rows, "selected": selected})
        common = dict(
            mission="HST",
            instrument="ACS/WFC",
            tier="A",
            usage_note="MAST public HST data; acknowledge NASA/ESA/STScI and programmes; "
            "https://archive.stsci.edu/publishing/doi",
            pipeline_version="archive metadata; calibration version read from FITS later",
        )
        snapshots.append(
            register(
                snap,
                dict(
                    common,
                    source_identifier=f"MAST/CAOM/ACS-DARK/{year}/{args.month}",
                    original_filename=snap.name,
                    url="https://mast.stsci.edu/api/v0/invoke",
                    processing_level="archive query JSON snapshot",
                    selection_reason=json.dumps(query),
                ),
                root,
                commit,
            )
        )
        write_json(root / "data/manifests/hst_queries.json", snapshots)
        if not selected:
            exclusions.append({"year": year, "reason": "No adjacent public dark pair in window"})
            print(f"{year}: no pair", flush=True)
            continue
        products = Observations.get_product_list([r["obsid"] for r in selected])
        for row in selected:
            chosen = [
                p
                for p in products
                if str(p["productFilename"]).lower() == row["obs_id"].lower() + "_flt.fits"
            ]
            if not chosen:
                exclusions.append({"observation": row["obs_id"], "reason": "No FLT product"})
                continue
            product = chosen[0]
            uri = str(product["dataURI"])
            spec = dict(
                common,
                source_identifier=uri,
                original_filename=str(product["productFilename"]),
                url="https://mast.stsci.edu/api/v0.1/Download/file?uri=" + quote(uri, safe=""),
                processing_level="FLT calibrated, not pixel CTE corrected",
                selection_reason="First chronological public 900-1200 s DARK pair within one day "
                f"in preselected {year}-{args.month:02d} window",
                observation_id=row["obs_id"],
                mjd=float(row["t_min"]),
                expected_size_bytes=int(product["size"]),
                cohort_year=year,
            )
            plan.append(spec)
        write_json(root / "data/manifests/hst_plan.json", plan)
        write_json(root / "data/manifests/hst_exclusions.json", exclusions)
        print(f"{year}: {len(selected)} observations; {len(plan)} total FLTs", flush=True)


if __name__ == "__main__":
    main()
