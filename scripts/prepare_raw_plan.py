"""Select individual RAW dark pairs from frozen observation-query snapshots."""

import json
from pathlib import Path
from urllib.parse import quote

from astroquery.mast import Observations

from lattice.cli import software_commit
from lattice.provenance import register, verify, write_json


def main():
    root = Path.cwd()
    selected = []
    query_records = json.loads((root / "data/manifests/hst_queries.json").read_text())
    for record in query_records:
        snapshot = json.loads(verify(record, root).read_text())
        rows = [r for r in snapshot["rows"] if r["obs_id"].lower().endswith("q")]
        rows.sort(key=lambda r: (float(r["t_min"]), r["obs_id"]))
        for i, row in enumerate(rows):
            matches = [
                b
                for b in rows[i + 1 :]
                if 0 < float(b["t_min"]) - float(row["t_min"]) <= 1
                and abs(float(b["t_exptime"]) / float(row["t_exptime"]) - 1) <= 0.01
            ]
            if matches:
                for r in (row, matches[0]):
                    selected.append(
                        dict(
                            r,
                            query_sha256=record["sha256"],
                            cohort_year=int(record["source_identifier"].split("/")[-2]),
                        )
                    )
                break
    products = Observations.get_product_list([r["obsid"] for r in selected])
    snapshot_path = root / "data/cache/hst/raw_product_query.json"
    write_json(snapshot_path, [{k: str(p[k]) for k in products.colnames} for p in products])
    common = dict(
        mission="HST",
        instrument="ACS/WFC",
        tier="A",
        usage_note="MAST public HST data; acknowledge NASA/ESA/STScI and programmes",
        pipeline_version="RAW; inspect OPUS_VER, CAL_VER and calibration switches",
    )
    snapshot_record = register(
        snapshot_path,
        dict(
            common,
            source_identifier="MAST/CAOM/products/paired-raw-pilot",
            original_filename=snapshot_path.name,
            url="https://mast.stsci.edu/api/v0/invoke",
            processing_level="archive product query JSON",
            selection_reason="RAW products for " + ",".join(r["obsid"] for r in selected),
        ),
        root,
        software_commit(root),
    )
    write_json(root / "data/manifests/hst_raw_products.json", [snapshot_record])
    plan = []
    for row in selected:
        name = row["obs_id"].lower() + "_raw.fits"
        found = [p for p in products if str(p["productFilename"]).lower() == name]
        if len(found) != 1:
            raise ValueError(f"Expected exactly one RAW product for {name}; no silent replacement")
        product = found[0]
        uri = str(product["dataURI"])
        plan.append(
            dict(
                common,
                source_identifier=uri,
                original_filename=name,
                url="https://mast.stsci.edu/api/v0.1/Download/file?uri=" + quote(uri, safe=""),
                processing_level="RAW uncalibrated dark",
                observation_id=row["obs_id"],
                mjd=float(row["t_min"]),
                cohort_year=row["cohort_year"],
                expected_size_bytes=int(product["size"]),
                query_sha256=row["query_sha256"],
                product_query_sha256=snapshot_record["sha256"],
                selection_reason="First chronological individual (q) dark pair within 1 day; "
                "exposure durations agree within 1%; frozen July cohort",
            )
        )
    write_json(root / "data/manifests/hst_raw_plan.json", plan)
    print(f"Frozen {len(plan)} RAW products, {sum(r['expected_size_bytes'] for r in plan)} bytes")


if __name__ == "__main__":
    main()
