"""Verify all registered calibration inputs, references, outputs and logs."""

import argparse
import json
from pathlib import Path

from astropy.io import fits

from lattice.cohort import select_analysis_records
from lattice.provenance import sha256, verify


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", default="results/calibration/products.json")
    parser.add_argument("--raw-manifest", default="data/manifests/hst_raw_plan_retrieved.json")
    parser.add_argument(
        "--reference-manifest",
        action="append",
        default=[],
        help="Repeat for each manifest supplying pinned references",
    )
    parser.add_argument("--assignments", default="data/manifests/hst_reference_assignments.json")
    parser.add_argument("--required-role")
    args = parser.parse_args()
    root = Path.cwd()
    products = json.loads((root / args.receipt).read_text())
    raw = select_analysis_records(
        json.loads((root / args.raw_manifest).read_text()), args.required_role
    )
    reference_manifests = args.reference_manifest or [
        "data/manifests/hst_references_plan_retrieved.json"
    ]
    refs = []
    for manifest in reference_manifests:
        refs.extend(json.loads((root / manifest).read_text()))
    assignments = json.loads((root / args.assignments).read_text())
    if args.required_role and assignments.get("analysis_role") != args.required_role:
        raise ValueError("Reference assignments do not match the required analysis role")
    if len({p["observation_id"] for p in products}) != len(products):
        raise ValueError("Duplicate calibration receipt")
    if {p["observation_id"] for p in products} != {p["observation_id"] for p in raw}:
        raise ValueError("Calibration cohort incomplete or differs from frozen RAW plan")
    if any(p["raw_record"].get("analysis_role") == "temporal_holdout" for p in products):
        raise ValueError("Refusing a calibration receipt containing temporal-holdout records")
    ref_hashes = {}
    for r in refs:
        name = r["original_filename"]
        if name in ref_hashes and ref_hashes[name] != r["sha256"]:
            raise ValueError(f"Conflicting reference hashes for {name}")
        ref_hashes[name] = r["sha256"]
        verify(r, root)
    for p in products:
        verify(p["raw_record"], root)
        for path_key, hash_key in (("output_path", "output_sha256"), ("log_path", "log_sha256")):
            path = (root / p[path_key]).resolve()
            if not path.is_relative_to(root.resolve()) or sha256(path) != p[hash_key]:
                raise ValueError("Calibration output/log path or hash mismatch")
        required_names = set(assignments["assignments"][p["observation_id"]].values())
        missing = required_names - ref_hashes.keys()
        if missing:
            raise ValueError(
                f"Missing pinned references for {p['observation_id']}: {sorted(missing)}"
            )
        expected = {name: ref_hashes[name] for name in required_names}
        if p["crds_context"] != assignments["context"] or p["reference_sha256"] != expected:
            raise ValueError("Reference assignment mismatch")
        with fits.open(root / p["output_path"], memmap=False) as hdus:
            header = hdus[0].header
            if header["ROOTNAME"].lower() != p["observation_id"]:
                raise ValueError("Calibrated exposure identity mismatch")
            for key in ("BIASCORR", "BLEVCORR", "DQICORR"):
                if header[key] != "COMPLETE":
                    raise ValueError(f"Incomplete {key}")
            for key in ("PCTECORR", "DARKCORR", "FLSHCORR", "SINKCORR", "FLATCORR"):
                if header[key] != "OMIT":
                    raise ValueError(f"Unexpected applied correction {key}")
            for key, value in p["calibrated_gains"].items():
                if header[key] != value or value <= 0:
                    raise ValueError("Gain receipt mismatch")
            for hdu in hdus:
                if hdu.name == "SCI":
                    if hdu.header["BUNIT"] != "ELECTRONS" or hdu.data.shape != (2048, 4096):
                        raise ValueError("Geometry or unit mismatch")
    print(
        f"Verified {len(products)} calibrated exposures and "
        f"{len(ref_hashes)} unique reference objects"
    )


if __name__ == "__main__":
    main()
