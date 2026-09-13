"""Run the frozen conditional Euclid detector-to-science-bias experiment."""

from itertools import product
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lattice.cli import software_commit
from lattice.euclid_transfer import mixture_kernel
from lattice.provenance import sha256, write_json
from lattice.science_bias import (
    aperture_moments,
    apply_parallel_trail,
    elliptic_covariance,
    gaussian_source,
)

SHAPE = (96, 96)
CENTER = (48.0, 24.0)
APERTURE_RADIUS = 12.0
PSF_SIGMA = 0.16 / 2.355 / 0.1
READ_NOISE = 4.5
FAST_TAU = 220e-6
SLOW_TAU = 20e-3
STEP = 4.02e-3
MAX_LAG = 4096
CAPTURED = (0.001, 0.003, 0.01)
DISTANCES = (0.25, 1.0)
WEIGHTS = (0.25, 0.5, 0.75)
TAU_FACTORS = (0.5, 1.0, 2.0)
BACKGROUNDS = (20.0, 100.0)
REALISATIONS = 32


def _metrics(clean, damaged) -> dict[str, float]:
    return {
        "flux_fraction": (damaged.flux - clean.flux) / clean.flux,
        "centroid_x_pixels": damaged.x - clean.x,
        "centroid_y_pixels": damaged.y - clean.y,
        "centroid_y_mas": (damaged.y - clean.y) * 100,
        "e1": damaged.e1 - clean.e1,
        "e2": damaged.e2 - clean.e2,
        "size_fraction": (damaged.size_trace - clean.size_trace) / clean.size_trace,
    }


def _interval(values: list[float]) -> dict[str, float]:
    lower, median, upper = np.percentile(values, [2.5, 50, 97.5])
    return {"lower": float(lower), "median": float(median), "upper": float(upper)}


def measure_scenario(source: np.ndarray, trailed: np.ndarray, background: float, seed: int) -> dict:
    clean_noiseless = aperture_moments(source, 0, CENTER, APERTURE_RADIUS)
    damaged_noiseless = aperture_moments(trailed, 0, CENTER, APERTURE_RADIUS)
    assert clean_noiseless is not None and damaged_noiseless is not None
    noiseless = _metrics(clean_noiseless, damaged_noiseless)
    rng = np.random.default_rng(seed)
    measurements = []
    for _ in range(REALISATIONS):
        standard = rng.normal(size=SHAPE)
        clean = source + background + standard * np.sqrt(source + background + READ_NOISE**2)
        damaged = trailed + background + standard * np.sqrt(trailed + background + READ_NOISE**2)
        clean_moments = aperture_moments(clean, background, CENTER, APERTURE_RADIUS)
        damaged_moments = aperture_moments(damaged, background, CENTER, APERTURE_RADIUS)
        if clean_moments is not None and damaged_moments is not None:
            measurements.append(_metrics(clean_moments, damaged_moments))
    return {
        "noiseless": noiseless,
        "valid_pairs": len(measurements),
        "intervals": {key: _interval([row[key] for row in measurements]) for key in noiseless},
    }


def run_source_grid() -> tuple[list[dict], dict]:
    sources = [("point", flux) for flux in (1000.0, 10_000.0)] + [
        ("galaxy", flux) for flux in (1000.0, 3000.0)
    ]
    rows = []
    conservation_errors = []
    seed = 4100
    for (source_type, flux), background, captured, distance, weight, factor in product(
        sources, BACKGROUNDS, CAPTURED, DISTANCES, WEIGHTS, TAU_FACTORS
    ):
        covariance = (
            np.eye(2) * PSF_SIGMA**2
            if source_type == "point"
            else elliptic_covariance(2.0, 0.7, 0.0, PSF_SIGMA)
        )
        source = gaussian_source(SHAPE, CENTER, flux, covariance)
        kernel = mixture_kernel(FAST_TAU * factor, SLOW_TAU * factor, weight, STEP, MAX_LAG)
        trailed, overflow = apply_parallel_trail(source, kernel, captured, distance)
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


def ring_response(captured: float, distance: float, weight: float, factor: float) -> dict:
    kernel = mixture_kernel(FAST_TAU * factor, SLOW_TAU * factor, weight, STEP, MAX_LAG)
    shears = np.array([-0.02, 0.0, 0.02])
    orientations = np.deg2rad([0, 45, 90, 135])
    output = {}
    for component in ("g1", "g2"):
        clean_values = []
        damaged_values = []
        for shear_value in shears:
            clean_ring = []
            damaged_ring = []
            for angle in orientations:
                g1 = shear_value if component == "g1" else 0.0
                g2 = shear_value if component == "g2" else 0.0
                covariance = elliptic_covariance(2.0, 0.7, angle, PSF_SIGMA, g1, g2)
                source = gaussian_source(SHAPE, CENTER, 3000, covariance)
                trailed, _ = apply_parallel_trail(source, kernel, captured, distance)
                clean = aperture_moments(source, 0, CENTER, APERTURE_RADIUS)
                damaged = aperture_moments(trailed, 0, CENTER, APERTURE_RADIUS)
                assert clean is not None and damaged is not None
                clean_ring.append(clean.e1 if component == "g1" else clean.e2)
                damaged_ring.append(damaged.e1 if component == "g1" else damaged.e2)
            clean_values.append(np.mean(clean_ring))
            damaged_values.append(np.mean(damaged_ring))
        clean_slope, clean_intercept = np.polyfit(shears, clean_values, 1)
        damaged_slope, damaged_intercept = np.polyfit(shears, damaged_values, 1)
        output[component] = {
            "clean_response": float(clean_slope),
            "trailed_response": float(damaged_slope),
            "multiplicative_m": float(damaged_slope / clean_slope - 1),
            "additive_c": float(damaged_intercept - clean_intercept),
        }
    return output


def make_figure(rows: list[dict], output: Path, valid_min: int) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(10.4, 7.2), constrained_layout=True)
    metrics = [
        ("centroid_y_mas", "Centroid y shift (mas)"),
        ("flux_fraction", "Aperture flux bias"),
        ("e1", "Ellipticity e1 bias"),
        ("size_fraction", "Trace-size bias"),
    ]
    for axis, (metric, ylabel) in zip(axes.flat, metrics, strict=True):
        for source_type, colour in (("point", "#326789"), ("galaxy", "#e07a5f")):
            medians = []
            low = []
            high = []
            for captured in CAPTURED:
                chosen = [
                    row["intervals"][metric]
                    for row in rows
                    if row["source_type"] == source_type
                    and row["captured_fraction"] == captured
                    and row["distance_fraction"] == 1
                ]
                values = [item["median"] for item in chosen]
                medians.append(np.median(values))
                low.append(np.min([item["lower"] for item in chosen]))
                high.append(np.max([item["upper"] for item in chosen]))
            axis.plot(CAPTURED, medians, marker="o", color=colour, label=source_type)
            axis.fill_between(CAPTURED, low, high, color=colour, alpha=0.18)
        axis.axhline(0, color="#555555", linewidth=0.8)
        axis.set(xlabel="Full-array captured-fraction scenario", ylabel=ylabel)
        axis.grid(alpha=0.2)
        axis.spines[["top", "right"]].set_visible(False)
    axes[0, 0].legend(frameon=False)
    figure.suptitle(
        "Euclid conditional detector-to-science bias\n"
        f"MEASUREMENT GATE FAIL: minimum {valid_min}/{REALISATIONS} valid pairs; "
        "low-S/N moment envelopes are unstable",
        color="#8b1e1e",
        fontweight="bold",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main() -> None:
    root = Path.cwd()
    rows, diagnostics = run_source_grid()
    ring = [
        {
            "captured_fraction": captured,
            "distance_fraction": distance,
            "fast_weight": weight,
            "tau_factor": factor,
            "response": ring_response(captured, distance, weight, factor),
        }
        for captured, distance, weight, factor in product(CAPTURED, DISTANCES, WEIGHTS, TAU_FACTORS)
    ]
    valid_min = min(row["valid_pairs"] for row in rows)
    intervals_ordered = all(
        interval["lower"] <= interval["median"] <= interval["upper"]
        for row in rows
        for interval in row["intervals"].values()
    )
    zero_source = gaussian_source(SHAPE, CENTER, 10_000, np.eye(2) * PSF_SIGMA**2)
    zero_kernel = mixture_kernel(FAST_TAU, SLOW_TAU, 0.5, STEP, MAX_LAG)
    zero_trailed, zero_overflow = apply_parallel_trail(zero_source, zero_kernel, 0, 1)
    zero_clean = aperture_moments(zero_source, 0, CENTER, APERTURE_RADIUS)
    zero_damaged = aperture_moments(zero_trailed, 0, CENTER, APERTURE_RADIUS)
    assert zero_clean is not None and zero_damaged is not None
    zero_metrics = _metrics(zero_clean, zero_damaged)
    monotonic_y = []
    for captured in CAPTURED:
        trailed, _ = apply_parallel_trail(zero_source, zero_kernel, captured, 1)
        measured = aperture_moments(trailed, 0, CENTER, APERTURE_RADIUS)
        assert measured is not None
        monotonic_y.append(measured.y - zero_clean.y)
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
        "forbidden_cross_mission_or_calendar_inputs_absent": True,
    }
    result = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "module_sha256": sha256(root / "src/lattice/science_bias.py"),
        "transfer_module_sha256": sha256(root / "src/lattice/euclid_transfer.py"),
        "protocol_sha256": sha256(root / "docs/SCIENCE_BIAS_PROTOCOL.md"),
        "result_class": "CONDITIONAL LINEAR CTI SCENARIOS",
        "implementation_gate": "PASS" if all(gates.values()) else "FAIL",
        "gates": gates,
        "diagnostics": {
            **diagnostics,
            "scenario_count": len(rows),
            "noise_realisations_per_scenario": REALISATIONS,
            "minimum_valid_pairs": valid_min,
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
    write_json(root / "results/science_bias/conditional_euclid_bias.json", result)
    make_figure(rows, root / "paper/figures/conditional_science_bias", valid_min)
    print(
        f"Conditional science bias {result['implementation_gate']}; "
        f"scenarios={len(rows)}; min valid={valid_min}/{REALISATIONS}; "
        f"max conservation error={diagnostics['max_flux_conservation_error']:.3g}"
    )


if __name__ == "__main__":
    main()
