"""Reproducible analytic injection experiment; not a full physical CCD simulator."""

from pathlib import Path

import numpy as np

from lattice.cli import software_commit
from lattice.hst import paired_trails
from lattice.provenance import sha256, write_json


def main():
    outcomes = []
    for seed in range(20):
        rng = np.random.default_rng(seed)
        for fraction in (0.0, 0.01, 0.05, 0.1):
            a = rng.normal(1000, 2, (192, 192))
            b = rng.normal(1200, 2, (192, 192))
            weights = np.exp(-np.arange(1, 6) / 2)
            weights /= weights.sum()
            for y in (30, 70, 110, 150):
                for x in (30, 60, 130, 160):
                    peak = 500.0
                    for image in (a, b):
                        image[y, x] += peak
                        image[y + 1 : y + 6, x] += fraction * peak * weights
            result = paired_trails(a, b)
            outcomes.append(
                dict(
                    seed=seed,
                    truth_fraction=fraction,
                    n=len(result["x"]),
                    recovered_fraction=float(np.mean(result["parallel_fraction"])),
                    blank_fraction=float(np.mean(result["blank_fraction"])),
                )
            )
    errors = np.array([r["recovered_fraction"] - r["truth_fraction"] for r in outcomes])
    result = dict(
        software_commit=software_commit(Path.cwd()),
        script_sha256=sha256(Path(__file__)),
        extractor_sha256=sha256(Path("src/lattice/hst.py")),
        evidence="SIMULATED",
        tier="C",
        trials=outcomes,
        description="Analytic five-pixel exponential injection; no trap occupancy physics",
        recovery_rmse=float(np.sqrt(np.mean(errors**2))),
        max_absolute_error=float(abs(errors).max()),
        pass_threshold_rmse=0.005,
        passed=bool(np.sqrt(np.mean(errors**2)) < 0.005),
    )
    write_json(Path("results/hst/synthetic_recovery.json"), result)
    print({k: v for k, v in result.items() if k != "trials"})


if __name__ == "__main__":
    main()
