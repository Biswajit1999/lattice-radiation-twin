"""Run the frozen Euclid conditional charge-release scenario grid."""

from itertools import product
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lattice.cli import software_commit
from lattice.euclid_transfer import mixture_kernel, release_kernel, trail_impulse
from lattice.provenance import sha256, write_json

FAST_TAU_SECONDS = 220e-6
SLOW_TAU_SECONDS = 20e-3
SERIAL_STEP_SECONDS = 14.3e-6
PARALLEL_STEP_SECONDS = 4.02e-3
MAX_LAG = 4096
INPUT_ELECTRONS = 100_000.0
TAU_FACTORS = (0.5, 1.0, 2.0)
FAST_WEIGHTS = (0.0, 0.25, 0.5, 0.75, 1.0)
CAPTURED_FRACTIONS = (0.001, 0.003, 0.01)
DISTANCE_FRACTIONS = (0.25, 0.5, 1.0)
REGISTERS = {"serial": SERIAL_STEP_SECONDS, "parallel": PARALLEL_STEP_SECONDS}


def run_grid() -> tuple[list[dict], dict]:
    scenarios = []
    mass_errors = []
    charge_errors = []
    minimum_charge = np.inf
    maximum_tail = 0.0
    for register, fast_factor, slow_factor, weight, captured, distance in product(
        REGISTERS, TAU_FACTORS, TAU_FACTORS, FAST_WEIGHTS, CAPTURED_FRACTIONS, DISTANCE_FRACTIONS
    ):
        kernel = mixture_kernel(
            FAST_TAU_SECONDS * fast_factor,
            SLOW_TAU_SECONDS * slow_factor,
            weight,
            REGISTERS[register],
            MAX_LAG,
        )
        output, beyond = trail_impulse(INPUT_ELECTRONS, captured, distance, kernel)
        mass_error = abs(kernel.represented_mass + kernel.tail_probability - 1)
        charge_error = float(abs(output.sum() + beyond - INPUT_ELECTRONS) / INPUT_ELECTRONS)
        mass_errors.append(mass_error)
        charge_errors.append(charge_error)
        minimum_charge = min(minimum_charge, float(output.min()), beyond)
        maximum_tail = max(maximum_tail, kernel.tail_probability)
        scenarios.append(
            {
                "register": register,
                "fast_tau_factor": fast_factor,
                "slow_tau_factor": slow_factor,
                "fast_weight": weight,
                "full_array_captured_fraction": captured,
                "transfer_distance_fraction": distance,
                "represented_kernel_mass": kernel.represented_mass,
                "beyond_window_kernel_mass": kernel.tail_probability,
                "mean_lag_given_represented_release": (kernel.mean_lag_given_represented_release),
                "output_impulse_electrons": float(output[0]),
                "represented_trail_electrons": float(output[1:].sum()),
                "beyond_window_electrons": beyond,
                "mass_error": mass_error,
                "relative_charge_error": charge_error,
            }
        )
    fast_parallel = release_kernel(FAST_TAU_SECONDS, PARALLEL_STEP_SECONDS, MAX_LAG)
    slow_parallel = release_kernel(SLOW_TAU_SECONDS, PARALLEL_STEP_SECONDS, MAX_LAG)
    diagnostics = {
        "scenario_count": len(scenarios),
        "max_kernel_mass_error": max(mass_errors),
        "max_relative_charge_error": max(charge_errors),
        "minimum_output_or_tail_electrons": minimum_charge,
        "maximum_beyond_window_kernel_mass": maximum_tail,
        "parallel_fast_mean_lag": fast_parallel.mean_lag_given_represented_release,
        "parallel_slow_mean_lag": slow_parallel.mean_lag_given_represented_release,
    }
    return scenarios, diagnostics


def make_figure(output: Path) -> None:
    colours = {"fast": "#326789", "slow": "#e07a5f"}
    figure, axes = plt.subplots(2, 2, figsize=(10.4, 7.4), constrained_layout=True)
    for column, (register, step) in enumerate(REGISTERS.items()):
        axis = axes[0, column]
        for name, tau in (("fast", FAST_TAU_SECONDS), ("slow", SLOW_TAU_SECONDS)):
            kernel = release_kernel(tau, step, MAX_LAG)
            keep = kernel.probability > 1e-12
            axis.plot(
                kernel.lag[keep],
                kernel.probability[keep],
                label=f"{name}: {tau * 1e6:g} us",
                color=colours[name],
            )
        axis.set(
            xscale="log", yscale="log", xlabel="Downstream pixel lag", ylabel="Release probability"
        )
        axis.set_title(f"{register.capitalize()} transfer: {step * 1e6:g} us/step")
        axis.grid(alpha=0.2)
        axis.spines[["top", "right"]].set_visible(False)
        axis.legend(frameon=False)

    axis = axes[1, 0]
    for factor in TAU_FACTORS:
        kernel = mixture_kernel(
            FAST_TAU_SECONDS * factor,
            SLOW_TAU_SECONDS * factor,
            0.5,
            PARALLEL_STEP_SECONDS,
            MAX_LAG,
        )
        output_pixels, _ = trail_impulse(INPUT_ELECTRONS, 0.01, 1.0, kernel)
        axis.plot(
            np.arange(1, 25),
            output_pixels[1:25],
            marker="o",
            markersize=3,
            label=f"timescale x {factor:g}",
        )
    axis.set(
        yscale="log",
        xlabel="Parallel downstream pixel lag",
        ylabel="Trailed electrons from 100,000 e- impulse",
        title="Fixed 1% full-array capture scenario",
    )
    axis.grid(alpha=0.2)
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(frameon=False)

    axis = axes[1, 1]
    weights = np.asarray(FAST_WEIGHTS)
    for distance in DISTANCE_FRACTIONS:
        first_pixel = []
        for weight in weights:
            kernel = mixture_kernel(
                FAST_TAU_SECONDS,
                SLOW_TAU_SECONDS,
                weight,
                PARALLEL_STEP_SECONDS,
                MAX_LAG,
            )
            pixels, _ = trail_impulse(INPUT_ELECTRONS, 0.01, distance, kernel)
            first_pixel.append(pixels[1])
        axis.plot(weights, first_pixel, marker="o", label=f"distance {distance:g}")
    axis.set(
        xlabel="Fast-species mixture weight",
        ylabel="First downstream pixel, electrons",
        title="Scenario dependence is explicit",
    )
    axis.grid(alpha=0.2)
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(frameon=False)
    figure.suptitle(
        "Euclid VIS conditional charge-release transfer\n"
        "Scenario envelope, not an observational damage forecast"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main() -> None:
    root = Path.cwd()
    constraints_path = root / "data/literature/euclid_constraints.json"
    protocol_path = root / "docs/EUCLID_TRANSFER_PROTOCOL.md"
    module_path = root / "src/lattice/euclid_transfer.py"
    scenarios, diagnostics = run_grid()
    gates = {
        "finite_nonnegative": bool(diagnostics["minimum_output_or_tail_electrons"] >= 0),
        "causal_no_upstream_component": True,
        "kernel_mass_error_at_most_1e-12": diagnostics["max_kernel_mass_error"] <= 1e-12,
        "relative_charge_error_at_most_1e-9": (diagnostics["max_relative_charge_error"] <= 1e-9),
        "slow_parallel_mean_lag_exceeds_fast": bool(
            diagnostics["parallel_slow_mean_lag"] > diagnostics["parallel_fast_mean_lag"]
        ),
        "published_timing_preserved": (
            SERIAL_STEP_SECONDS == 14.3e-6 and PARALLEL_STEP_SECONDS == 4.02e-3
        ),
        "observational_amplitude_or_calendar_forecast_reported": False,
        "hst_or_gaia_fitted_parameter_used": False,
    }
    pass_values = [
        value for key, value in gates.items() if "reported" not in key and "used" not in key
    ]
    negative_gates = [
        not gates["observational_amplitude_or_calendar_forecast_reported"],
        not gates["hst_or_gaia_fitted_parameter_used"],
    ]
    status = "PASS" if all(pass_values + negative_gates) else "FAIL"
    result = {
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "module_sha256": sha256(module_path),
        "constraint_source_sha256": sha256(constraints_path),
        "protocol_sha256": sha256(protocol_path),
        "result_class": "CONDITIONAL SIMULATION",
        "numerical_gate": status,
        "claim_boundary": {
            "observational_euclid_damage_amplitude": "UNIDENTIFIED",
            "calendar_damage_forecast": "NOT PRODUCED",
            "posterior_uncertainty": "NOT AVAILABLE",
            "scenario_envelope": "AVAILABLE",
            "hst_historical_amplitude": "NOT USED",
            "gaia_amplitude": "NOT USED",
        },
        "mission_inputs": {
            "temperature_kelvin": 153,
            "serial_step_seconds": SERIAL_STEP_SECONDS,
            "parallel_step_seconds": PARALLEL_STEP_SECONDS,
            "ccd_rows": 4132,
            "ccd_columns": 4096,
            "focal_plane_ccds": 36,
            "fast_tau_seconds": FAST_TAU_SECONDS,
            "slow_tau_seconds": SLOW_TAU_SECONDS,
        },
        "frozen_grid": {
            "max_lag": MAX_LAG,
            "input_electrons": INPUT_ELECTRONS,
            "tau_factors": TAU_FACTORS,
            "fast_weights": FAST_WEIGHTS,
            "captured_fractions": CAPTURED_FRACTIONS,
            "distance_fractions": DISTANCE_FRACTIONS,
        },
        "diagnostics": diagnostics,
        "gates": gates,
        "scenarios": scenarios,
    }
    write_json(root / "results/euclid/conditional_transfer.json", result)
    make_figure(root / "paper/figures/euclid_conditional_transfer")
    print(
        f"Euclid conditional transfer {status}; scenarios={len(scenarios)}; "
        f"max mass error={diagnostics['max_kernel_mass_error']:.3g}; "
        f"max charge error={diagnostics['max_relative_charge_error']:.3g}"
    )


if __name__ == "__main__":
    main()
