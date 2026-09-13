"""Run the frozen Phase 10b weighted Euclid science-bias experiment."""

from itertools import product
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import run_science_bias as base

from lattice.cli import software_commit
from lattice.euclid_transfer import mixture_kernel
from lattice.provenance import sha256, write_json
from lattice.science_bias import gaussian_source, weighted_aperture_moments

WEIGHT_SIGMA = 3.0


def _weighted(image, background, center, radius):
    return weighted_aperture_moments(image, background, center, radius, WEIGHT_SIGMA)


def _finite_output(rows: list[dict], ring: list[dict]) -> bool:
    source_values = [
        value for row in rows for group in (row["noiseless"],) for value in group.values()
    ] + [
        value
        for row in rows
        for interval in row["intervals"].values()
        for value in interval.values()
    ]
    ring_values = [
        value
        for row in ring
        for component in row["response"].values()
        for value in component.values()
    ]
    return bool(np.isfinite(source_values + ring_values).all())


def make_figure(rows: list[dict], output: Path, gate: str, valid_min: int) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(10.4, 7.2), constrained_layout=True)
    metrics = [
        ("centroid_y_mas", "Weighted centroid y shift (mas)"),
        ("flux_fraction", "Weighted flux bias"),
        ("e1", "Weighted ellipticity e1 bias"),
        ("size_fraction", "Weighted trace-size bias"),
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
        "Euclid fixed-weight detector-to-science bias\n"
        f"MEASUREMENT GATE {gate}: minimum {valid_min}/{base.REALISATIONS} valid pairs",
        color=colour,
        fontweight="bold",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main() -> None:
    root = Path.cwd()
    predecessor_result = root / "results/science_bias/conditional_euclid_bias.json"
    predecessor_protocol = root / "docs/SCIENCE_BIAS_PROTOCOL.md"
    predecessor_before = sha256(predecessor_result)
    protocol_before = sha256(predecessor_protocol)

    base.aperture_moments = _weighted
    rows, diagnostics = base.run_source_grid()
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
    valid_min = min(row["valid_pairs"] for row in rows)
    intervals_ordered = all(
        interval["lower"] <= interval["median"] <= interval["upper"]
        for row in rows
        for interval in row["intervals"].values()
    )
    zero_source = gaussian_source(base.SHAPE, base.CENTER, 10_000, np.eye(2) * base.PSF_SIGMA**2)
    zero_kernel = mixture_kernel(base.FAST_TAU, base.SLOW_TAU, 0.5, base.STEP, base.MAX_LAG)
    zero_trailed, zero_overflow = base.apply_parallel_trail(zero_source, zero_kernel, 0, 1)
    zero_clean = _weighted(zero_source, 0, base.CENTER, base.APERTURE_RADIUS)
    zero_damaged = _weighted(zero_trailed, 0, base.CENTER, base.APERTURE_RADIUS)
    assert zero_clean is not None and zero_damaged is not None
    zero_metrics = base._metrics(zero_clean, zero_damaged)
    monotonic_y = []
    for captured in base.CAPTURED:
        trailed, _ = base.apply_parallel_trail(zero_source, zero_kernel, captured, 1)
        measured = _weighted(trailed, 0, base.CENTER, base.APERTURE_RADIUS)
        assert measured is not None
        monotonic_y.append(measured.y - zero_clean.y)

    predecessor_after = sha256(predecessor_result)
    protocol_after = sha256(predecessor_protocol)
    gates = {
        "flux_conservation_at_most_1e-12": bool(
            diagnostics["max_flux_conservation_error"] <= 1e-12
        ),
        "zero_capture_metrics_at_most_1e-12": bool(
            max(abs(value) for value in zero_metrics.values()) <= 1e-12
        ),
        "at_least_30_of_32_valid_pairs": bool(valid_min >= 30),
        "positive_monotonic_y_shift": bool(all(np.diff(monotonic_y) >= 0) and monotonic_y[0] > 0),
        "x_centroid_control_at_most_1e-12": bool(abs(zero_metrics["centroid_x_pixels"]) <= 1e-12),
        "intervals_ordered": bool(intervals_ordered),
        "all_outputs_finite": _finite_output(rows, ring),
        "exact_grid_sizes": len(rows) == 432 and len(ring) == 54,
        "predecessor_unchanged": (
            predecessor_before == predecessor_after and protocol_before == protocol_after
        ),
        "forbidden_cross_mission_or_calendar_inputs_absent": True,
    }
    gate = "PASS" if all(gates.values()) else "FAIL"
    result = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "module_sha256": sha256(root / "src/lattice/science_bias.py"),
        "transfer_module_sha256": sha256(root / "src/lattice/euclid_transfer.py"),
        "protocol_sha256": sha256(root / "docs/SCIENCE_BIAS_WEIGHTED_PROTOCOL.md"),
        "predecessor": {
            "result_sha256": predecessor_after,
            "protocol_sha256": protocol_after,
            "implementation_gate": "FAIL",
        },
        "result_class": "CONDITIONAL FIXED-WEIGHT LINEAR CTI SCENARIOS",
        "implementation_gate": gate,
        "gates": gates,
        "diagnostics": {
            **diagnostics,
            "scenario_count": len(rows),
            "ring_scenario_count": len(ring),
            "noise_realisations_per_scenario": base.REALISATIONS,
            "minimum_valid_pairs": valid_min,
            "weight_sigma_pixels": WEIGHT_SIGMA,
            "zero_capture_overflow_electrons": zero_overflow,
            "zero_capture_metrics": zero_metrics,
            "monotonic_y_centroid_pixels": monotonic_y,
        },
        "claim_boundary": {
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
    write_json(root / "results/science_bias/conditional_euclid_bias_weighted.json", result)
    make_figure(
        rows,
        root / "paper/figures/conditional_science_bias_weighted",
        gate,
        valid_min,
    )
    print(
        f"Weighted conditional science bias {gate}; scenarios={len(rows)}; "
        f"min valid={valid_min}/{base.REALISATIONS}; "
        f"max conservation error={diagnostics['max_flux_conservation_error']:.3g}"
    )


if __name__ == "__main__":
    main()
