"""Apply the frozen directional and control screens to HST replication summaries."""

import argparse
import json
from pathlib import Path

import numpy as np

from lattice.cli import software_commit
from lattice.provenance import sha256, write_json


def bootstrap_slope(year, value, *, seed=314159, n_boot=20_000):
    """Return an OLS slope and epoch-bootstrap interval without pooling pair strata."""
    year = np.asarray(year, dtype=float)
    value = np.asarray(value, dtype=float)
    centered = year - year.mean()
    slope = float(np.sum(centered * (value - value.mean())) / np.sum(centered**2))
    rng = np.random.default_rng(seed)
    slopes = []
    for draw in rng.integers(0, len(year), size=(n_boot, len(year))):
        xx, yy = year[draw], value[draw]
        xx_centered = xx - xx.mean()
        denominator = np.sum(xx_centered**2)
        if denominator > 0:
            slopes.append(np.sum(xx_centered * (yy - yy.mean())) / denominator)
    lo, hi = np.quantile(slopes, [0.025, 0.975])
    return {
        "slope_per_year": slope,
        "lo": float(lo),
        "hi": float(hi),
        "n_epochs": int(len(year)),
        "bootstrap_resamples_retained": len(slopes),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary", default="results/hst_replication/primary.json")
    parser.add_argument("--output", default="results/hst_replication/assessment.json")
    args = parser.parse_args()
    root = Path.cwd()
    primary_path = root / args.primary
    rows = json.loads(primary_path.read_text())["measurements"]
    expected = {
        (year, pair, chip) for year in range(2003, 2025, 3) for pair in (2, 3) for chip in (1, 2)
    }
    observed = {(r["year"], r["pair_index"], r["chip"]) for r in rows}
    if len(rows) != 32 or observed != expected:
        raise ValueError("Replication primary summary is not the frozen 8 x 2 x 2 design")
    if any(r.get("analysis_role") != "replication" for r in rows):
        raise ValueError("Replication assessment received a non-replication record")

    slopes = []
    for pair_index in (2, 3):
        for chip in (1, 2):
            subset = sorted(
                (r for r in rows if r["pair_index"] == pair_index and r["chip"] == chip),
                key=lambda r: r["year"],
            )
            result = bootstrap_slope(
                [r["year"] for r in subset],
                [r["parallel_fraction"]["mean"] for r in subset],
                seed=314159 + 10 * pair_index + chip,
            )
            result.update(
                pair_index=pair_index,
                chip=chip,
                direction_pass=result["slope_per_year"] > 0 and result["lo"] > 0,
            )
            slopes.append(result)

    differences = []
    for year in range(2003, 2025, 3):
        for chip in (1, 2):
            pair = sorted(
                (r for r in rows if r["year"] == year and r["chip"] == chip),
                key=lambda r: r["pair_index"],
            )
            differences.append(
                {
                    "year": year,
                    "chip": chip,
                    "pair_2": pair[0]["parallel_fraction"]["mean"],
                    "pair_3": pair[1]["parallel_fraction"]["mean"],
                    "absolute_difference": abs(
                        pair[0]["parallel_fraction"]["mean"] - pair[1]["parallel_fraction"]["mean"]
                    ),
                }
            )
    for row in differences:
        endpoints = [r for r in rows if r["chip"] == row["chip"] and r["year"] in {2003, 2024}]
        early = np.mean([r["parallel_fraction"]["mean"] for r in endpoints if r["year"] == 2003])
        late = np.mean([r["parallel_fraction"]["mean"] for r in endpoints if r["year"] == 2024])
        scale = abs(late - early)
        row["fraction_of_chip_2003_to_2024_change"] = (
            row["absolute_difference"] / scale if scale > 0 else None
        )

    blank_failures = []
    for row in rows:
        interval = row["blank_fraction_familywise"]
        if interval["lo"] > 0 or interval["hi"] < 0:
            blank_failures.append(
                {
                    "year": row["year"],
                    "pair_index": row["pair_index"],
                    "chip": row["chip"],
                    "mean": interval["mean"],
                    "lo": interval["lo"],
                    "hi": interval["hi"],
                }
            )

    direction_pass = all(row["direction_pass"] for row in slopes)
    blank_pass = not blank_failures
    result = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "primary_sha256": sha256(primary_path),
        "evidence": "INFERRED SCREEN FROM OBSERVED REPLICATION SUMMARIES",
        "directional_slopes": slopes,
        "within_epoch_pair_differences": differences,
        "blank_control_failures": blank_failures,
        "direction_screen_pass": direction_pass,
        "blank_control_screen_pass": blank_pass,
        "replication_screen_pass": direction_pass and blank_pass,
        "physical_inference_gate": "CLOSED",
        "gate_note": (
            "A pair-aware nuisance and measurement-error baseline comparison remains required, "
            "regardless of this screen."
        ),
    }
    write_json(root / args.output, result)
    print(
        f"Replication screen: direction={direction_pass}; blank={blank_pass}; "
        "physical inference gate=CLOSED"
    )


if __name__ == "__main__":
    main()
