"""Freeze replicated and temporal-holdout HST products from metadata only."""

import json
from calendar import monthrange
from pathlib import Path
from urllib.parse import quote

from astroquery.mast import Observations

from lattice.cli import software_commit
from lattice.cohort import select_date_pairs
from lattice.provenance import register, verify, write_json
from lattice.time import utc_to_mjd


def product_spec(product, row, kind, query_hash, product_hash):
    name = str(product["productFilename"])
    uri = str(product["dataURI"])
    processing = "RAW uncalibrated dark" if kind == "raw" else "SPT engineering support product"
    instrument = "ACS/WFC" if kind == "raw" else "ACS/WFC telemetry"
    return dict(
        mission="HST",
        instrument=instrument,
        tier="A",
        usage_note="MAST public HST data; acknowledge NASA/ESA/STScI and programmes",
        pipeline_version="RAW; inspect calibration headers"
        if kind == "raw"
        else "read from OPUS_VER where supplied",
        processing_level=processing,
        source_identifier=uri,
        original_filename=name,
        url="https://mast.stsci.edu/api/v0.1/Download/file?uri=" + quote(uri, safe=""),
        observation_id=row["observation_id"],
        mjd=row["mjd"],
        cohort_year=row["year"],
        pair_id=row["pair_id"],
        pair_index=row["pair_index"],
        analysis_role=row["analysis_role"],
        expected_size_bytes=int(product["size"]),
        query_sha256=query_hash,
        product_query_sha256=product_hash,
        selection_reason="Outcome-blind first compatible pair on one of the first three "
        "distinct MJD days in the frozen monthly window; exact role in "
        "HST_REPLICATION_PROTOCOL.md",
    )


def main():
    root = Path.cwd()
    commit = software_commit(root)
    old_queries = json.loads((root / "data/manifests/hst_queries.json").read_text())
    development = {int(r["source_identifier"].split("/")[-2]): r for r in old_queries}
    common = dict(
        mission="HST",
        instrument="ACS/WFC",
        tier="A",
        usage_note="MAST public HST data; acknowledge NASA/ESA/STScI and programmes",
        pipeline_version="archive metadata; calibration version read from FITS later",
    )
    Observations.TIMEOUT = 90
    holdout_record = None
    holdout_pairs = []
    attempts = []
    months = [(2025, month) for month in range(7, 13)] + [(2026, month) for month in range(1, 9)]
    for year, month in months:
        start = utc_to_mjd(f"{year}-{month:02d}-01")
        query = dict(
            obs_collection="HST",
            instrument_name="ACS/WFC",
            target_name="DARK*",
            t_min=[start, start + monthrange(year, month)[1]],
            t_exptime=[900, 1200],
            dataRights="PUBLIC",
        )
        name = (
            "query_replication_2025.json"
            if (year, month) == (2025, 7)
            else (f"query_replication_{year}_{month:02d}.json")
        )
        snapshot = root / "data/metadata/hst" / name
        if snapshot.exists():
            saved = json.loads(snapshot.read_text())
            if saved["query"] != query:
                raise ValueError(f"Existing query definition differs: {snapshot}")
            rows = saved["rows"]
        else:
            table = Observations.query_criteria(**query)
            rows = [{key: str(row[key]) for key in table.colnames} for row in table]
            rows.sort(key=lambda row: (float(row["t_min"]), row["obs_id"]))
            write_json(snapshot, {"query": query, "rows": rows})
        pairs = select_date_pairs(rows)
        record = register(
            snapshot,
            dict(
                common,
                source_identifier=f"MAST/CAOM/ACS-DARK/{year}/{month}",
                original_filename=snapshot.name,
                url="https://mast.stsci.edu/api/v0/invoke",
                processing_level="archive query JSON snapshot",
                selection_reason=json.dumps(query),
                eligible_distinct_day_pairs=len(pairs),
            ),
            root,
            commit,
        )
        attempts.append(record)
        if len(pairs) == 3:
            holdout_record, holdout_pairs = record, pairs
            break
    if holdout_record is None:
        raise ValueError("No eligible three-pair temporal holdout in frozen month sequence")
    write_json(
        root / "data/manifests/hst_replication_queries.json",
        [development[y] for y in sorted(development)] + attempts,
    )
    selections = []
    for selected_year, record in sorted(development.items()):
        archive_rows = json.loads(verify(record, root).read_text())["rows"]
        pairs = select_date_pairs(archive_rows)
        if len(pairs) != 3:
            raise ValueError(f"Need exactly three eligible pairs for {selected_year}")
        for pair_index, pair in enumerate(pairs, 1):
            role = "development" if pair_index == 1 else "replication"
            pair_id = f"{selected_year}-{pair_index}"
            for row in pair:
                selections.append(
                    dict(
                        observation_id=row["obs_id"].lower(),
                        archive_obsid=row["obsid"],
                        mjd=float(row["t_min"]),
                        exptime=float(row["t_exptime"]),
                        year=selected_year,
                        pair_index=pair_index,
                        pair_id=pair_id,
                        analysis_role=role,
                        query_sha256=record["sha256"],
                    )
                )
    holdout_year = int(holdout_record["source_identifier"].split("/")[-2])
    holdout_month = int(holdout_record["source_identifier"].split("/")[-1])
    for pair_index, pair in enumerate(holdout_pairs, 1):
        pair_id = f"{holdout_year}-{holdout_month:02d}-{pair_index}"
        for row in pair:
            selections.append(
                dict(
                    observation_id=row["obs_id"].lower(),
                    archive_obsid=row["obsid"],
                    mjd=float(row["t_min"]),
                    exptime=float(row["t_exptime"]),
                    year=holdout_year,
                    month=holdout_month,
                    pair_index=pair_index,
                    pair_id=pair_id,
                    analysis_role="temporal_holdout",
                    query_sha256=holdout_record["sha256"],
                )
            )
    products = Observations.get_product_list([row["archive_obsid"] for row in selections])
    product_rows = [{key: str(row[key]) for key in products.colnames} for row in products]
    product_rows.sort(key=lambda row: (row["obsID"], row["productFilename"]))
    product_snapshot = root / "data/metadata/hst/replication_product_query.json"
    write_json(product_snapshot, product_rows)
    product_record = register(
        product_snapshot,
        dict(
            common,
            source_identifier="MAST/CAOM/products/replicated-raw-spt-cohort",
            original_filename=product_snapshot.name,
            url="https://mast.stsci.edu/api/v0/invoke",
            processing_level="archive product query JSON",
            selection_reason="RAW and SPT products for frozen three-pair July cohorts",
        ),
        root,
        commit,
    )
    write_json(root / "data/manifests/hst_replication_products.json", [product_record])
    existing_raw = {
        r["original_filename"]
        for r in json.loads((root / "data/manifests/hst_raw_plan_retrieved.json").read_text())
    }
    existing_support = {
        r["original_filename"]
        for r in json.loads((root / "data/manifests/hst_support_plan_retrieved.json").read_text())
    }
    raw_plan, support_plan = [], []
    for row in selections:
        for kind, suffix, existing, plan in (
            ("raw", "_raw.fits", existing_raw, raw_plan),
            ("support", "_spt.fits", existing_support, support_plan),
        ):
            name = row["observation_id"] + suffix
            found = [p for p in products if str(p["productFilename"]).lower() == name]
            if len(found) != 1:
                raise ValueError(f"Expected exactly one public product for {name}")
            if name not in existing:
                plan.append(
                    product_spec(found[0], row, kind, row["query_sha256"], product_record["sha256"])
                )
    write_json(root / "data/manifests/hst_replicated_cohort.json", selections)
    write_json(root / "data/manifests/hst_replication_raw_plan.json", raw_plan)
    write_json(root / "data/manifests/hst_replication_support_plan.json", support_plan)
    print(
        f"Frozen {len(selections) // 2} pairs: {len(raw_plan)} new RAW "
        f"({sum(r['expected_size_bytes'] for r in raw_plan)} bytes), "
        f"{len(support_plan)} new SPT"
    )


if __name__ == "__main__":
    main()
