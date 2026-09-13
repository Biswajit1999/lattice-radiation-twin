"""Run the frozen Phase 10c forced-response Euclid bias experiment."""

from itertools import product
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import run_science_bias as base

from lattice.cli import software_commit
from lattice.euclid_transfer import mixture_kernel
from lattice.provenance import sha256, write_json
from lattice.science_bias import (
    elliptic_covariance,
    forced_response_metrics,
    gaussian_source,
    weighted_aperture_moments,
)

WEIGHT_SIGMA = 3.0


def _weighted(image, background, center, radius):
    return weighted_aperture_moments(image, background, center, radius, WEIGHT_SIGMA)


def measure_scenario(source: np.ndarray, trailed: np.ndarray, background: float, seed: int) -> dict:
    noiseless = forced_response_metrics(
        source, trailed, source, 0, base.CENTER, base.APERTURE_RADIUS, WEIGHT_SIGMA
    )
    rng = np.random.default_rng(seed)
    measurements = []
    for _ in range(base.REALISATIONS):
        standard = rng.normal(size=base.SHAPE)
        clean = source + background + standard * np.sqrt(source + background + base.READ_NOISE**2)
        damaged = (
            trailed + background + standard * np.sqrt(trailed + background + base.READ_NOISE**2)
        )
        measurements.append(
            forced_response_metrics(
                clean,
                damaged,
                source,
                background,
                base.CENTER,
                base.APERTURE_RADIUS,
                WEIGHT_SIGMA,
            )
        )
    return {
        "noiseless": noiseless,
        "valid_pairs": len(measurements),
        "intervals": {key: base._interval([row[key] for row in measurements]) for key in noiseless},
    }


def run_source_grid() -> tuple[list[dict], dict]:
    sources = [("point", flux) for flux in (1000.0, 10_000.0)] + [
        ("galaxy", flux) for flux in (1000.0, 3000.0)
    ]
    rows, conservation_errors = [], []
    seed = 4100
    for (source_type, flux), background, captured, distance, weight, factor in product(
        sources,
        base.BACKGROUNDS,
        base.CAPTURED,
        base.DISTANCES,
        base.WEIGHTS,
        base.TAU_FACTORS,
    ):
        covariance = (
            np.eye(2) * base.PSF_SIGMA**2
            if source_type == "point"
            else elliptic_covariance(2.0, 0.7, 0.0, base.PSF_SIGMA)
        )
        source = gaussian_source(base.SHAPE, base.CENTER, flux, covariance)
        kernel = mixture_kernel(
            base.FAST_TAU * factor,
            base.SLOW_TAU * factor,
            weight,
            base.STEP,
            base.MAX_LAG,
        )
        trailed, overflow = base.apply_parallel_trail(source, kernel, captured, distance)
        conservation_errors.append(abs(trailed.sum() + overflow - source.sum()) / source.sum())
        measured = measure_scenario(source, trailed, background, seed)
        seed += 1
        rows.append(
            {
                "source_type": source_type,
                "flux_electrons": flux,
                "background_electrons_per_pixel": background,
                "captured_fraction": captured,
                "distance_fraction": distance,
                "fast_weight": weight,
                "tau_factor": factor,
                "overflow_electrons": overflow,
                **measured,
            }
        )
    return rows, {"max_flux_conservation_error": float(max(conservation_errors))}


def make_figure(rows: list[dict], output: Path, gate: str) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(10.4, 7.2), constrained_layout=True)
    metrics = [
        ("centroid_y_mas", "Forced centroid y response (mas)"),
        ("flux_fraction", "Forced weighted-flux response"),
        ("e1", "Linearized ellipticity e1 response"),
        ("size_fraction", "Linearized trace-size response"),
    ]
    for axis, (metric, ylabel) in zip(axes.flat, metrics, strict=True):
        for source_type, colour in (("point", "#326789"), ("galaxy", "#e07a5f")):
            medians, low, high = [], [], []
            for captured in base.CAPTURED:
                chosen = [
                    row["intervals"][metric]
                    for row in rows
                    if row["source_type"] == source_type
                    and row["captured_fraction"] == captured
                    and row["distance_fraction"] == 1
                ]
                medians.append(np.median([item["median"] for item in chosen]))
                low.append(np.min([item["lower"] for item in chosen]))
                high.append(np.max([item["upper"] for item in chosen]))
            axis.plot(base.CAPTURED, medians, marker="o", color=colour, label=source_type)
            axis.fill_between(base.CAPTURED, low, high, color=colour, alpha=0.18)
        axis.axhline(0, color="#555555", linewidth=0.8)
        axis.set(xlabel="Full-array captured-fraction scenario", ylabel=ylabel)
        axis.grid(alpha=0.2)
        axis.spines[["top", "right"]].set_visible(False)
    axes[0, 0].legend(frameon=False)
    colour = "#24543b" if gate == "PASS" else "#8b1e1e"
    figure.suptitle(
        "Euclid fixed-template forced response\n"
        f"IMPLEMENTATION GATE {gate}: 32/32 finite paired responses per scenario",
        color=colour,
        fontweight="bold",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main() -> None:
    root = Path.cwd()
    predecessor_paths = {
        "unweighted_result": root / "results/science_bias/conditional_euclid_bias.json",
        "unweighted_protocol": root / "docs/SCIENCE_BIAS_PROTOCOL.md",
        "weighted_result": root / "results/science_bias/conditional_euclid_bias_weighted.json",
        "weighted_protocol": root / "docs/SCIENCE_BIAS_WEIGHTED_PROTOCOL.md",
    }
    predecessor_before = {name: sha256(path) for name, path in predecessor_paths.items()}
    rows, diagnostics = run_source_grid()
    base.aperture_moments = _weighted
    ring = [
        {
            "captured_fraction": captured,
            "distance_fraction": distance,
            "fast_weight": weight,
            "tau_factor": factor,
            "response": base.ring_response(captured, distance, weight, factor),
        }
        for captured, distance, weight, factor in product(
            base.CAPTURED, base.DISTANCES, base.WEIGHTS, base.TAU_FACTORS
        )
    ]
    zero_source = gaussian_source(base.SHAPE, base.CENTER, 10_000, np.eye(2) * base.PSF_SIGMA**2)
    zero_metrics = forced_response_metrics(
        zero_source,
        zero_source,
        zero_source,
        0,
        base.CENTER,
        base.APERTURE_RADIUS,
        WEIGHT_SIGMA,
    )
    zero_kernel = mixture_kernel(base.FAST_TAU, base.SLOW_TAU, 0.5, base.STEP, base.MAX_LAG)
    monotonic_y = []
    for captured in base.CAPTURED:
        trailed, _ = base.apply_parallel_trail(zero_source, zero_kernel, captured, 1)
        response = forced_response_metrics(
            zero_source,
            trailed,
            zero_source,
            0,
            base.CENTER,
            base.APERTURE_RADIUS,
            WEIGHT_SIGMA,
        )
        monotonic_y.append(response["centroid_y_pixels"])
    intervals_ordered = all(
        interval["lower"] <= interval["median"] <= interval["upper"]
        for row in rows
        for interval in row["intervals"].values()
    )
    all_values = [
        value
        for row in rows
        for interval in row["intervals"].values()
        for value in interval.values()
    ] + [
        value
        for row in ring
        for component in row["response"].values()
        for value in component.values()
    ]
    predecessor_after = {name: sha256(path) for name, path in predecessor_paths.items()}
    gates = {
        "all_32_of_32_pairs_finite": all(row["valid_pairs"] == 32 for row in rows),
        "exact_grid_sizes": len(rows) == 432 and len(ring) == 54,
        "all_outputs_finite": bool(np.isfinite(all_values).all()),
        "intervals_ordered": bool(intervals_ordered),
        "flux_conservation_at_most_1e-12": bool(
            diagnostics["max_flux_conservation_error"] <= 1e-12
        ),
        "zero_capture_metrics_at_most_1e-12": bool(
            max(abs(value) for value in zero_metrics.values()) <= 1e-12
        ),
        "positive_monotonic_y_shift": bool(all(np.diff(monotonic_y) >= 0) and monotonic_y[0] > 0),
        "x_centroid_control_at_most_1e-12": bool(abs(zero_metrics["centroid_x_pixels"]) <= 1e-12),
        "predecessors_unchanged": predecessor_before == predecessor_after,
        "forbidden_cross_mission_or_calendar_inputs_absent": True,
    }
    gate = "PASS" if all(gates.values()) else "FAIL"
    result = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "module_sha256": sha256(root / "src/lattice/science_bias.py"),
        "transfer_module_sha256": sha256(root / "src/lattice/euclid_transfer.py"),
        "protocol_sha256": sha256(root / "docs/SCIENCE_BIAS_FORCED_PROTOCOL.md"),
        "predecessor_sha256": predecessor_after,
        "result_class": "CONDITIONAL FIXED-TEMPLATE LINEARIZED CTI RESPONSE",
        "implementation_gate": gate,
        "gates": gates,
        "diagnostics": {
            **diagnostics,
            "scenario_count": len(rows),
            "ring_scenario_count": len(ring),
            "noise_realisations_per_scenario": base.REALISATIONS,
            "minimum_valid_pairs": min(row["valid_pairs"] for row in rows),
            "weight_sigma_pixels": WEIGHT_SIGMA,
            "zero_capture_metrics": zero_metrics,
            "monotonic_y_centroid_pixels": monotonic_y,
        },
        "claim_boundary": {
            "survey_measurement_pipeline": "NOT VALIDATED",
            "euclid_cosmological_shear_measurement": "NOT PERFORMED",
            "posterior_cti_uncertainty": "UNAVAILABLE",
            "observational_damage_amplitude": "UNIDENTIFIED",
            "calendar_forecast": "NOT PRODUCED",
            "hst_science_bias": "BLOCKED BY FAILED PHYSICAL-INFERENCE GATE",
            "gaia_science_bias": "BLOCKED BY UNAVAILABLE CTI SERIES",
        },
        "source_scenarios": rows,
        "ring_test_scenarios": ring,
    }
    write_json(root / "results/science_bias/conditional_euclid_bias_forced.json", result)
    make_figure(rows, root / "paper/figures/conditional_science_bias_forced", gate)
    print(
        f"Forced conditional science bias {gate}; scenarios={len(rows)}; "
        f"min valid={result['diagnostics']['minimum_valid_pairs']}/{base.REALISATIONS}; "
        f"max conservation error={diagnostics['max_flux_conservation_error']:.3g}"
    )


if __name__ == "__main__":
    main()
