"""Join replication outcomes to exposure state without assigning causal meaning."""

import argparse
import json
from pathlib import Path

import numpy as np

from lattice.cli import software_commit
from lattice.provenance import sha256, write_json
from lattice.replication import finite_spearman


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary", default="results/hst_replication/primary.json")
    parser.add_argument("--metadata", default="results/hst_replication/metadata.json")
    parser.add_argument("--operating-state", default="results/hst_replication/operating_state.json")
    parser.add_argument("--output", default="results/hst_replication/nuisance_summary.json")
    args = parser.parse_args()
    root = Path.cwd()
    paths = {name: root / value for name, value in vars(args).items() if name != "output"}
    primary = json.loads(paths["primary"].read_text())["measurements"]
    metadata = json.loads(paths["metadata"].read_text())
    operating = json.loads(paths["operating_state"].read_text())["exposures"]
    if len(primary) != 32 or len(metadata) != 32 or len(operating) != 32:
        raise ValueError("Nuisance join requires the complete frozen replication design")
    if any(row.get("analysis_role") != "replication" for row in primary + metadata):
        raise ValueError("Nuisance join received a non-replication outcome")

    meta_by_key = {(r["pair_id"], r["chip"]): r for r in metadata}
    state_by_pair = {}
    for exposure in operating:
        state_by_pair.setdefault(exposure["pair_id"], []).append(exposure)
    joined = []
    for row in primary:
        meta = meta_by_key[(row["pair_id"], row["chip"])]
        state = sorted(state_by_pair[row["pair_id"]], key=lambda r: r["rootname"])
        if len(state) != 2 or any(r["analysis_role"] != "replication" for r in state):
            raise ValueError("Operating-state pair mismatch")
        backgrounds = [
            frame["background_electrons"]["spatial_quantiles_16_50_84"][1]
            for frame in meta["frames"]
        ]
        if any(value is None for value in backgrounds):
            raise ValueError("Missing replication background summary")
        temperatures = [r["channels"]["JWDETMP1"]["value"] for r in state]
        joined.append(
            {
                "year": row["year"],
                "pair_id": row["pair_id"],
                "pair_index": row["pair_index"],
                "chip": row["chip"],
                "parallel_fraction": row["parallel_fraction"]["mean"],
                "blank_fraction": row["blank_fraction"]["mean"],
                "commanded_gain": row["commanded_gain"],
                "background_electrons_frame_medians": backgrounds,
                "background_electrons_pair_mean": float(np.mean(backgrounds)),
                "jwdetmp1_degrees_c_values": temperatures,
                "jwdetmp1_degrees_c_pair_mean": float(np.mean(temperatures)),
                "flash_duration_seconds": [r["acquisition"]["FLASHDUR"] for r in state],
                "flash_status": [r["acquisition"]["FLASHSTA"] for r in state],
                "b_side_operations": [r["acquisition"]["BSIDEOPS"] for r in state],
                "shutter_positions": [r["acquisition"]["SHUTRPOS"] for r in state],
                "rootnames": [r["rootname"] for r in state],
            }
        )

    outcome = [r["parallel_fraction"] for r in joined]
    correlations = {
        "calendar_year": finite_spearman([r["year"] for r in joined], outcome),
        "background_electrons": finite_spearman(
            [r["background_electrons_pair_mean"] for r in joined], outcome
        ),
        "jwdetmp1_engineering_channel": finite_spearman(
            [r["jwdetmp1_degrees_c_pair_mean"] for r in joined], outcome
        ),
        "commanded_gain": finite_spearman([r["commanded_gain"] for r in joined], outcome),
    }
    result = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "source_sha256": sha256(root / "src/lattice/replication.py"),
        "input_sha256": {name: sha256(path) for name, path in paths.items()},
        "evidence": "OBSERVED OUTCOMES JOINED TO OBSERVED ENGINEERING STATE",
        "interpretation": (
            "Descriptive, unadjusted associations only; time, post-flash, background, gain and "
            "electronics state are confounded. JWDETMP1 is retained literally because the active "
            "sensor mapping is unverified."
        ),
        "rows": joined,
        "descriptive_spearman": correlations,
    }
    write_json(root / args.output, result)
    print("Wrote 32 replication pair-by-chip nuisance rows and descriptive correlations")


if __name__ == "__main__":
    main()
