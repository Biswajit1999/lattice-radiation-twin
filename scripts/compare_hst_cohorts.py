"""Compare the frozen development pair with independent HST replication pairs."""

import argparse
import json
from pathlib import Path

from lattice.cli import software_commit
from lattice.provenance import sha256, write_json
from lattice.replication import compare_cohort_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--development", default="results/hst_calibrated/primary.json")
    parser.add_argument("--replication", default="results/hst_replication/primary.json")
    parser.add_argument("--output", default="results/hst_replication/development_comparison.json")
    args = parser.parse_args()
    root = Path.cwd()
    development_path = root / args.development
    replication_path = root / args.replication
    development = json.loads(development_path.read_text())["measurements"]
    replication = json.loads(replication_path.read_text())["measurements"]
    rows, metrics = compare_cohort_rows(development, replication)
    result = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "source_sha256": sha256(root / "src/lattice/replication.py"),
        "input_sha256": {
            "development": sha256(development_path),
            "replication": sha256(replication_path),
        },
        "evidence": "OBSERVED COHORT COMPARISON",
        "interpretation": (
            "The replication mean is descriptive, not a pooled measurement-error model. "
            "Agreement does not remove shared time-varying operating-state confounding."
        ),
        "metrics": metrics,
        "rows": rows,
    }
    write_json(root / args.output, result)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
