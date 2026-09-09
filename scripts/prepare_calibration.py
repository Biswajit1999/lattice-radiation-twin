"""Resolve a pinned CRDS context into a reviewable reference-download plan."""

import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

from astropy.io import fits

from lattice.cli import software_commit
from lattice.provenance import register, verify, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", default="hst_1356.pmap")
    args = parser.parse_args()
    root = Path.cwd()
    records = json.loads((root / "data/manifests/hst_raw_plan_retrieved.json").read_text())
    requests, assignments = [], {}
    for record in records:
        raw = verify(record, root)
        header = fits.getheader(raw)
        header = {k: str(v) for k, v in header.items() if k and k not in {"COMMENT", "HISTORY"}}
        payload = dict(
            jsonrpc="1.0",
            id=1,
            method="get_best_references",
            params=[args.context, header, ["ccdtab", "biasfile", "oscntab", "bpixtab", "satufile"]],
        )
        endpoint = "https://hst-crds.stsci.edu/json/"
        request = Request(
            endpoint,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=60) as response:
            result = json.load(response)
        if result["error"]:
            raise RuntimeError(result["error"])
        requests.append(dict(request=payload, response=result))
        assignments[record["observation_id"]] = result["result"]
        print(record["observation_id"], result["result"], flush=True)
    snapshot = root / "data/metadata/hst/crds_reference_query.json"
    write_json(snapshot, requests)
    common = dict(
        mission="HST",
        instrument="ACS/WFC",
        tier="A",
        pipeline_version=f"CRDS context {args.context}",
        usage_note="STScI HST calibration reference data; acknowledge STScI/CRDS; "
        "https://hst-crds.stsci.edu",
    )
    record = register(
        snapshot,
        dict(
            common,
            source_identifier=f"CRDS/{args.context}/paired-dark",
            original_filename=snapshot.name,
            url=endpoint,
            processing_level="reference assignment query snapshot",
            selection_reason="Fixed RAW cohort: DQI, bias, gain, overscan, saturation references",
        ),
        root,
        software_commit(root),
    )
    write_json(root / "data/manifests/crds_queries.json", [record])
    write_json(
        root / "data/manifests/hst_reference_assignments.json",
        dict(context=args.context, assignments=assignments, query_sha256=record["sha256"]),
    )
    names = sorted(
        {
            name
            for refs in assignments.values()
            for name in refs.values()
            if name.lower().endswith(".fits")
        }
    )
    plan = [
        dict(
            common,
            source_identifier=f"CRDS/hst/{name}",
            original_filename=name,
            url=f"https://hst-crds.stsci.edu/unchecked_get/references/hst/{name}",
            processing_level="calibration reference",
            selection_reason="Selected by pinned CRDS for paired-dark bias/gain calibration",
        )
        for name in names
    ]
    write_json(root / "data/manifests/hst_references_plan.json", plan)
    print(f"Prepared {len(plan)} unique references; payloads not downloaded")


if __name__ == "__main__":
    main()
