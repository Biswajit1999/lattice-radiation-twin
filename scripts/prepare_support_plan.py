"""Select observed SPT telemetry products for the fixed RAW cohort."""

import json
from pathlib import Path
from urllib.parse import quote

from lattice.provenance import write_json


def main():
    root = Path.cwd()
    raw = json.loads((root / "data/manifests/hst_raw_plan.json").read_text())
    products = json.loads((root / "data/metadata/hst/raw_product_query.json").read_text())
    plan = []
    for record in raw:
        name = record["observation_id"] + "_spt.fits"
        matched = [p for p in products if p["productFilename"] == name]
        if len(matched) != 1:
            raise ValueError(f"Missing/ambiguous support product: {name}")
        uri = matched[0]["dataURI"]
        plan.append(
            dict(
                source_identifier=uri,
                original_filename=name,
                mission="HST",
                instrument="ACS/WFC telemetry",
                tier="A",
                observation_id=record["observation_id"],
                url="https://mast.stsci.edu/api/v0.1/Download/file?uri=" + quote(uri, safe=""),
                processing_level="SPT engineering support product",
                pipeline_version="read from OPUS_VER where supplied",
                usage_note="MAST public HST engineering data; acknowledge NASA/ESA/STScI",
                selection_reason="Matched operational metadata for fixed RAW paired-dark cohort",
            )
        )
    write_json(root / "data/manifests/hst_support_plan.json", plan)
    print(f"Prepared {len(plan)} SPT products")


if __name__ == "__main__":
    main()
