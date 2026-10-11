"""Local simulator QAOA workflow and honest baseline comparison."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any
import json

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize
from qiskit.circuit.library import QAOAAnsatz
from qiskit.primitives import StatevectorEstimator, StatevectorSampler

from .model import (
    ACTIONS,
    BUDGET,
    PENALTY,
    N_ACTIONS,
    N_VARIABLES,
    exact_classical_solution,
    is_qubo_feasible,
    selected_benefit,
    selected_effort,
    has_conflict,
    qubo_to_hamiltonian,
)


def bits_from_count_key(bitstring: str) -> list[int]:
    """Translate Qiskit's displayed (MSB-left) bitstring to qubit-index order."""
    return [int(char) for char in bitstring.replace(" ", "")[::-1]]


def _action_summary(action_bits: list[int]) -> dict[str, Any]:
    return {
        "bits": action_bits,
        "selected_ids": [ACTIONS[i].action_id for i, bit in enumerate(action_bits) if bit],
        "selected_names": [ACTIONS[i].name for i, bit in enumerate(action_bits) if bit],
        "effort": selected_effort(action_bits),
        "benefit": selected_benefit(action_bits),
        "feasible": selected_effort(action_bits) <= BUDGET and not has_conflict(action_bits),
    }


def run_qaoa(
    reps: int = 1,
    maxiter: int = 60,
    shots: int = 4096,
    seed: int = 7,
    output_dir: str | Path = "artifacts",
    penalty: float = PENALTY,
) -> dict[str, Any]:
    """Optimize and sample the OpsShield QUBO using QAOA on a local statevector simulator."""
    if reps < 1 or maxiter < 1 or shots < 1:
        raise ValueError("reps, maxiter and shots must all be positive.")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    hamiltonian = qubo_to_hamiltonian(penalty=penalty)
    ansatz = QAOAAnsatz(cost_operator=hamiltonian, reps=reps)
    estimator = StatevectorEstimator(seed=seed)
    rng = np.random.default_rng(seed)
    initial_point = rng.uniform(0.0, np.pi, size=ansatz.num_parameters)
    energy_history: list[float] = []

    def objective(parameters: np.ndarray) -> float:
        result = estimator.run([(ansatz, hamiltonian, parameters)]).result()[0]
        energy = float(np.asarray(result.data.evs).reshape(-1)[0])
        energy_history.append(energy)
        return energy

    optimized = minimize(
        objective,
        initial_point,
        method="COBYLA",
        options={"maxiter": maxiter, "rhobeg": 0.35},
        tol=1e-3,
    )

    measured = ansatz.assign_parameters(optimized.x)
    measured.measure_all()
    sampler = StatevectorSampler(seed=seed, default_shots=shots)
    sample_result = sampler.run([measured], shots=shots).result()[0]
    counts: dict[str, int] = sample_result.data.meas.get_counts()
    total_shots = sum(counts.values())

    feasible_counts: Counter[str] = Counter()
    best_sampled_feasible: dict[str, Any] | None = None
    for bitstring, count in counts.items():
        all_bits = bits_from_count_key(bitstring)
        if len(all_bits) != N_VARIABLES:
            continue
        action_bits = all_bits[:N_ACTIONS]
        if is_qubo_feasible(all_bits):
            feasible_counts[bitstring] += int(count)
            candidate = _action_summary(action_bits)
            candidate["bitstring"] = bitstring
            candidate["shots"] = int(count)
            if best_sampled_feasible is None or candidate["benefit"] > best_sampled_feasible["benefit"]:
                best_sampled_feasible = candidate

    exact = exact_classical_solution()
    feasibility_yield = sum(feasible_counts.values()) / total_shots if total_shots else 0.0

    # Energy history figure
    plt.figure(figsize=(8, 4.5))
    plt.plot(range(1, len(energy_history) + 1), energy_history, marker=".", linewidth=1)
    plt.xlabel("Objective evaluation")
    plt.ylabel("Expected QUBO energy (lower is better)")
    plt.title("OpsShield QAOA optimization trace")
    plt.tight_layout()
    plt.savefig(output_path / "qaoa_energy.png", dpi=160)
    plt.close()

    # Show the most common measured bitstrings; this is not necessarily the best solution.
    top_counts = dict(Counter(counts).most_common(12))
    plt.figure(figsize=(9, 4.5))
    labels = list(top_counts.keys())
    values = [top_counts[label] / total_shots for label in labels]
    plt.bar(labels, values)
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Measured bitstring (Qiskit display order)")
    plt.ylabel("Observed frequency")
    plt.title("OpsShield QAOA sample distribution (top outcomes)")
    plt.tight_layout()
    plt.savefig(output_path / "sample_distribution.png", dpi=160)
    plt.close()

    report: dict[str, Any] = {
        "project": "OpsShield — Quantum Incident Response Optimizer",
        "dataset_note": "Synthetic demonstration data only; not production incident data.",
        "algorithm": "QAOAAnsatz + StatevectorEstimator + StatevectorSampler",
        "qaoa_reps": reps,
        "qubo_penalty": float(penalty),
        "optimizer": "COBYLA",
        "maxiter": maxiter,
        "shots": shots,
        "seed": seed,
        "num_qubits": N_VARIABLES,
        "optimizer_success": bool(optimized.success),
        "optimizer_message": str(optimized.message),
        "final_expected_qubo_energy": float(optimized.fun),
        "objective_evaluations": len(energy_history),
        "total_shots": int(total_shots),
        "feasible_shots": int(sum(feasible_counts.values())),
        "feasibility_yield": float(feasibility_yield),
        "exact_classical_optimum": exact,
        "best_feasible_qaoa_sample": best_sampled_feasible,
        "top_measured_bitstrings": top_counts,
        "artifacts": ["qaoa_energy.png", "sample_distribution.png"],
        "limitations": [
            "This is a small statevector-simulation experiment, not evidence of quantum advantage.",
            "The exact classical baseline is the reference for solution quality on this instance.",
            "The data and scores are synthetic and must not be interpreted as a real incident recommendation.",
        ],
    }
    (output_path / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
