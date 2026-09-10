"""Run the frozen paired synthetic ablations after the first recovery failure."""

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from lattice.cli import software_commit
from lattice.provenance import sha256, write_json
from lattice.state_space import StateSpaceData, filter_and_smooth, fit, pack, simulate

ABLATIONS = {
    "no_annealing": "annealing_rate",
    "no_event": "event_coefficient",
    "no_background": "background_coefficient",
    "no_process_noise": "process_scale",
}


def covariates(rng: np.random.Generator, epochs: int) -> tuple[np.ndarray, np.ndarray]:
    background = np.zeros(epochs - 1)
    innovations = rng.normal(size=epochs - 1)
    for index in range(1, epochs - 1):
        background[index] = 0.65 * background[index - 1] + innovations[index]
    event = (rng.random(epochs - 1) < 0.16) * rng.lognormal(0.0, 0.35, epochs - 1)
    background = (background - np.mean(background)) / np.std(background)
    event = (event - np.mean(event)) / np.std(event)
    return background, event


def scores(
    data: StateSpaceData,
    states: np.ndarray,
    parameters: dict[str, float],
    fixed_zero: tuple[str, ...] = (),
) -> dict[str, float]:
    result = filter_and_smooth(pack_for_filter(parameters), data, fixed_zero)
    pair_offsets = np.asarray([parameters["pair2_offset"], parameters["pair3_offset"]])
    predicted = result["smoothed_mean"][:, :, None] + pair_offsets[None, None, :]
    return {
        "negative_log_likelihood": result["negative_log_likelihood"],
        "latent_rmse": float(np.sqrt(np.mean((result["smoothed_mean"] - states) ** 2))),
        "observation_rmse": float(np.sqrt(np.mean((data.observations - predicted) ** 2))),
    }


def pack_for_filter(parameters: dict[str, float]) -> np.ndarray:
    values = dict(parameters)
    for name in ("annealing_rate", "process_scale", "observation_scale"):
        if values[name] == 0:
            values[name] = 0.01
    return pack(values)


def information_criteria(negative_log_likelihood: float, parameters: int, observations: int):
    return {
        "aic": float(2 * negative_log_likelihood + 2 * parameters),
        "bic": float(2 * negative_log_likelihood + parameters * np.log(observations)),
    }


def one_replicate(payload: tuple[int, dict, dict]) -> dict:
    index, truth, full_parameters = payload
    rng = np.random.default_rng(731_000 + index)
    epochs = 48
    times = np.arange(epochs, dtype=float)
    background, event = covariates(rng, epochs)
    data, states = simulate(truth, times, background, event, rng)
    full = scores(data, states, full_parameters)
    full.update(information_criteria(full["negative_log_likelihood"], 9, data.observations.size))
    reduced = {}
    for label, parameter in ABLATIONS.items():
        fitted = fit(data, fixed_zero=(parameter,))
        ablated = scores(data, states, fitted["parameters"], (parameter,))
        ablated.update(
            information_criteria(ablated["negative_log_likelihood"], 8, data.observations.size)
        )
        reduced[label] = {
            "fixed_zero": parameter,
            "success": fitted["success"],
            "message": fitted["message"],
            "iterations": fitted["iterations"],
            "parameters": fitted["parameters"],
            **ablated,
            "delta_negative_log_likelihood": float(
                ablated["negative_log_likelihood"] - full["negative_log_likelihood"]
            ),
            "delta_aic": float(ablated["aic"] - full["aic"]),
            "delta_bic": float(ablated["bic"] - full["bic"]),
            "latent_rmse_ratio": float(ablated["latent_rmse"] / full["latent_rmse"]),
        }
    return {"replicate": index, "full": full, "ablations": reduced}


def distribution(values: list[float]) -> dict[str, float]:
    array = np.asarray(values)
    return {
        "median": float(np.median(array)),
        "quartile_25": float(np.quantile(array, 0.25)),
        "quartile_75": float(np.quantile(array, 0.75)),
    }


def summarize(rows: list[dict]) -> dict:
    summary = {}
    for label, parameter in ABLATIONS.items():
        fits = [row["ablations"][label] for row in rows]
        summary[label] = {
            "fixed_zero": parameter,
            "optimizer_successes": int(sum(row["success"] for row in fits)),
            "delta_negative_log_likelihood": distribution(
                [row["delta_negative_log_likelihood"] for row in fits]
            ),
            "delta_aic": distribution([row["delta_aic"] for row in fits]),
            "delta_bic": distribution([row["delta_bic"] for row in fits]),
            "fraction_delta_bic_positive": float(np.mean([row["delta_bic"] > 0 for row in fits])),
            "latent_rmse": distribution([row["latent_rmse"] for row in fits]),
            "latent_rmse_ratio": distribution([row["latent_rmse_ratio"] for row in fits]),
            "observation_rmse": distribution([row["observation_rmse"] for row in fits]),
        }
    return summary


def make_figure(summary: dict, output: Path) -> None:
    labels = list(ABLATIONS)
    display = [label.replace("no_", "no ").replace("_", " ") for label in labels]
    delta_bic = [summary[label]["delta_bic"]["median"] for label in labels]
    rmse_ratio = [summary[label]["latent_rmse_ratio"]["median"] for label in labels]
    figure, axes = plt.subplots(1, 2, figsize=(10.2, 4.3), constrained_layout=True)
    axes[0].barh(display, delta_bic, color="#5b3c88")
    axes[0].axvline(0, color="black", linewidth=0.8)
    axes[0].set_xlabel("median paired ΔBIC (ablation − full)")
    axes[0].set_title("Representation loss")
    axes[1].barh(display, rmse_ratio, color="#2a9d8f")
    axes[1].axvline(1, color="#d1495b", linestyle="--", linewidth=1)
    axes[1].set_xlabel("median latent-RMSE ratio")
    axes[1].set_title("State-recovery change")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output.with_suffix(".png"), dpi=180)
    figure.savefig(output.with_suffix(".pdf"))
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--recovery-result", default="results/core_model/synthetic_recovery.json")
    args = parser.parse_args()
    root = Path.cwd()
    recovery_path = root / args.recovery_result
    recovery = json.loads(recovery_path.read_text(encoding="utf-8"))
    if recovery["replicate_count"] != 100 or recovery["synthetic_recovery_gate"] != "FAIL":
        raise ValueError("Ablations require the retained failed 100-replicate result")
    payloads = [
        (row["replicate"], recovery["truth"], row["parameters"])
        for row in recovery["replicate_details"]
    ]
    print(f"Running {len(payloads)} paired datasets x {len(ABLATIONS)} ablations")
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(one_replicate, payloads))
    summary = summarize(rows)
    result = {
        "evidence": "SIMULATED",
        "design": "PAIRED_ABLATIONS_OF_RETAINED_FAILED_SPECIFICATION",
        "replicate_count": len(rows),
        "ablation_count_per_replicate": len(ABLATIONS),
        "observational_fit": "NOT RUN",
        "physical_inference_gate": "CLOSED",
        "synthetic_recovery_gate": "REMAINS FAILED",
        "summary": summary,
        "replicate_details": rows,
        "software_commit": software_commit(root),
        "script_sha256": sha256(Path(__file__)),
        "source_sha256": sha256(root / "src/lattice/state_space.py"),
        "plan_sha256": sha256(root / "docs/CORE_ABLATION_PLAN.md"),
        "protocol_sha256": sha256(root / "docs/CORE_MODEL_PROTOCOL.md"),
        "parent_recovery_sha256": sha256(recovery_path),
    }
    output = root / "results/core_model"
    write_json(output / "synthetic_ablations.json", result)
    make_figure(summary, root / "paper/figures/synthetic_ablations")
    print("Synthetic ablations complete; recovery gate=REMAINS FAILED; observational fit=NOT RUN")


if __name__ == "__main__":
    main()
