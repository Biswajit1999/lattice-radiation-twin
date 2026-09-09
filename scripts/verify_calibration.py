"""Verify all registered calibration inputs, references, outputs and logs."""

import json
from pathlib import Path

from astropy.io import fits

from lattice.provenance import sha256, verify


def main():
    root = Path.cwd()
    products = json.loads((root / "results/calibration/products.json").read_text())
    raw = json.loads((root / "data/manifests/hst_raw_plan_retrieved.json").read_text())
    refs = json.loads((root / "data/manifests/hst_references_plan_retrieved.json").read_text())
    assignments = json.loads((root / "data/manifests/hst_reference_assignments.json").read_text())
    if len({p["observation_id"] for p in products}) != len(products):
        raise ValueError("Duplicate calibration receipt")
    if {p["observation_id"] for p in products} != {p["observation_id"] for p in raw}:
        raise ValueError("Calibration cohort incomplete or differs from frozen RAW plan")
    ref_hashes = {r["original_filename"]: r["sha256"] for r in refs}
    for r in refs:
        verify(r, root)
    for p in products:
        verify(p["raw_record"], root)
        for path_key, hash_key in (("output_path", "output_sha256"), ("log_path", "log_sha256")):
            path = (root / p[path_key]).resolve()
            if not path.is_relative_to(root.resolve()) or sha256(path) != p[hash_key]:
                raise ValueError("Calibration output/log path or hash mismatch")
        expected = {
            name: ref_hashes[name]
            for name in assignments["assignments"][p["observation_id"]].values()
            if name in ref_hashes
        }
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
    print(f"Verified {len(products)} calibrated exposures and {len(refs)} reference objects")


if __name__ == "__main__":
    main()
