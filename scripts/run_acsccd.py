"""Run official ACSCCD on copies; preserve raw/reference hashes and calibration receipts."""

import argparse
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from astropy.io import fits

from lattice.cli import software_commit
from lattice.cohort import select_analysis_records
from lattice.provenance import sha256, verify, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--acsccd", required=True)
    parser.add_argument("--wsl-distro")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--raw-manifest", default="data/manifests/hst_raw_plan_retrieved.json")
    parser.add_argument("--assignments", default="data/manifests/hst_reference_assignments.json")
    parser.add_argument("--reference-manifest", action="append")
    parser.add_argument("--receipt", default="results/calibration/products.json")
    parser.add_argument("--required-role")
    args = parser.parse_args()
    root = Path.cwd()
    assignments = json.loads((root / args.assignments).read_text())
    reference_manifests = args.reference_manifest or [
        "data/manifests/hst_references_plan_retrieved.json"
    ]
    reference_records = [
        record
        for manifest in reference_manifests
        for record in json.loads((root / manifest).read_text())
    ]
    raw_records = json.loads((root / args.raw_manifest).read_text())
    raw_records = select_analysis_records(raw_records, args.required_role)
    work = root / "data/cache/acsccd"
    refs = work / "refs"
    refs.mkdir(parents=True, exist_ok=True)
    ref_hashes = {}
    for record in reference_records:
        source = verify(record, root)
        target = refs / record["original_filename"]
        if not target.exists():
            os.link(source, target)
        if sha256(target) != record["sha256"]:
            raise ValueError("Staged reference does not match manifest")
        ref_hashes[record["original_filename"]] = record["sha256"]
    if args.wsl_distro:
        prefix = ["wsl.exe", "-d", args.wsl_distro, "--exec"]
        linux_root = subprocess.check_output(
            prefix + ["wslpath", "-u", str(root)], text=True
        ).strip()

        def native(path):
            return linux_root + "/" + path.relative_to(root).as_posix()
    else:
        prefix = []

        def native(path):
            return str(path)

    version = subprocess.check_output(prefix + [args.acsccd, "--version"], text=True).strip()
    executable_hash = (
        subprocess.check_output(prefix + ["sha256sum", args.acsccd], text=True).split()[0]
        if prefix
        else sha256(Path(args.acsccd))
    )
    receipt_path = root / args.receipt
    products = json.loads(receipt_path.read_text()) if receipt_path.exists() else []
    for raw_record in raw_records[: args.limit]:
        raw = verify(raw_record, root)
        obs = raw_record["observation_id"]
        output = work / f"{obs}_blv_tmp.fits"
        previous = next((p for p in products if p["observation_id"] == obs), None)
        if previous:
            if sha256(root / previous["output_path"]) != previous["output_sha256"]:
                raise ValueError("Existing calibrated output changed")
            print(f"Verified existing {obs}", flush=True)
            continue
        if output.exists():
            raise ValueError(f"Unregistered output exists: {output}; inspect before retry")
        prepared = work / raw.name
        shutil.copyfile(raw, prepared)
        selected = assignments["assignments"][obs]
        with fits.open(prepared, mode="update", memmap=False) as hdus:
            header = hdus[0].header
            for key, value in selected.items():
                header[key.upper()] = "jref$" + value if value.lower().endswith(".fits") else "N/A"
            for key in ("DQICORR", "BIASCORR", "BLEVCORR"):
                header[key] = "PERFORM"
            for key in (
                "PCTECORR",
                "DARKCORR",
                "FLATCORR",
                "SINKCORR",
                "FLSHCORR",
                "PHOTCORR",
                "CRCORR",
                "EXPSCORR",
            ):
                header[key] = "OMIT"
            hdus.flush()
        execution_prefix = (
            ["wsl.exe", "-d", args.wsl_distro, "--cd", native(work), "--exec"]
            if args.wsl_distro
            else []
        )
        command = execution_prefix + [
            "env",
            "jref=refs/",
            args.acsccd,
            prepared.name,
            output.name,
        ]
        result = subprocess.run(command, cwd=work, capture_output=True, text=True, timeout=600)
        logs = root / "results/calibration/logs"
        logs.mkdir(parents=True, exist_ok=True)
        log = logs / f"{obs}.txt"
        if log.exists():
            previous_log = logs / (obs + "_previous_" + sha256(log)[:12] + ".txt")
            shutil.copyfile(log, previous_log)
        log.write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode or not output.exists() or "ERROR:" in result.stdout:
            raise RuntimeError(f"ACSCCD failed for {obs}: see {log}")
        with fits.open(output, memmap=False) as hdus:
            h = hdus[0].header
            if h["BIASCORR"] != "COMPLETE" or h["BLEVCORR"] != "COMPLETE":
                raise ValueError("Calibration switches not complete")
            for hdu in hdus:
                if hdu.name == "SCI":
                    if hdu.data.shape != (2048, 4096) or hdu.header["BUNIT"] != "ELECTRONS":
                        raise ValueError("Unexpected output geometry or units")
            gains = {key: h[key] for key in ("ATODGNA", "ATODGNB", "ATODGNC", "ATODGND")}
            if any(value <= 0 for value in gains.values()):
                raise ValueError("Calibrated gains not populated")
        verify(raw_record, root)
        products.append(
            dict(
                observation_id=obs,
                cohort_year=raw_record["cohort_year"],
                raw_record=raw_record,
                output_path=output.relative_to(root).as_posix(),
                output_sha256=sha256(output),
                size_bytes=output.stat().st_size,
                prepared_input_sha256=sha256(prepared),
                created_at=datetime.now(UTC).isoformat(),
                software_commit=software_commit(root),
                script_sha256=sha256(Path(__file__)),
                executable_sha256=executable_hash,
                acsccd_version=version,
                crds_context=assignments["context"],
                reference_sha256={
                    name: ref_hashes[name] for name in selected.values() if name in ref_hashes
                },
                command=command,
                log_path=log.relative_to(root).as_posix(),
                log_sha256=sha256(log),
                calibrated_gains=gains,
                evidence="OBSERVED",
                processing_level="locally calibrated BLV",
                note="Bias/gain/overscan calibrated; dark and CTI correction deliberately omitted",
            )
        )
        write_json(receipt_path, products)
        print(f"Calibrated {obs}: {version}; gains={gains}", flush=True)


if __name__ == "__main__":
    main()
