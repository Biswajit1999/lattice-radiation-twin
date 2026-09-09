"""Record pilot limitations without turning nominal controls into discovery claims."""

import json
from pathlib import Path

from lattice.provenance import sha256, write_json


def main():
    root = Path.cwd()
    path = root / "results/hst/primary.json"
    rows = json.loads(path.read_text())["measurements"]
    controls = {}
    for key in ("blank_fraction", "serial_fraction"):
        controls[key] = [
            dict(year=r["year"], chip=r["chip"], **r[key])
            for r in rows
            if r[key]["mean"] is not None and (r[key]["lo"] > 0 or r[key]["hi"] < 0)
        ]
    result = dict(
        primary_sha256=sha256(path),
        evidence="OBSERVED",
        calibrated_anchor_passed=False,
        selected_primary_peaks=sum(r["parallel_fraction"]["n"] for r in rows),
        epochs=sorted({r["year"] for r in rows}),
        commanded_gains=sorted({r["commanded_gain"] for r in rows}),
        nominal_95_percent_control_intervals_excluding_zero=controls,
        multiplicity_note="Unadjusted intervals; some exclusions are expected by chance. "
        "These are not evidence of physical causation or definitive contamination.",
        unresolved=[
            "Matched reference bias and calibrated gain not applied",
            "Temperature/clocking/annealing telemetry not reconstructed",
            "RAW selection and electronics systematics not propagated",
            "Sparse epochs cannot resolve individual event response or temporal lags",
            "Column bootstrap excludes between-exposure and calibration uncertainty",
        ],
        blocked_claims=["physical trap density", "radiation causation", "cross-mission forecast"],
        next_experiment="Apply pinned CALACS/CRDS bias and gain calibration to independent "
        "paired darks, with matched operating-state telemetry and blind controls",
    )
    write_json(root / "results/hst/validation_gate.json", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
