"""Problem data, QUBO construction, exact classical baseline and validation.

All data are synthetic demonstration values, not production incident data.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class RemediationAction:
    action_id: str
    name: str
    effort: int
    benefit: int
    rationale: str


ACTIONS: tuple[RemediationAction, ...] = (
    RemediationAction("A1", "Restore WAN redundancy", 3, 10,
                      "Protects connectivity for multiple critical sites."),
    RemediationAction("A2", "Correct edge firewall policy", 2, 9,
                      "Reduces exposure caused by a known policy error."),
    RemediationAction("A3", "Expand critical storage capacity", 2, 8,
                      "Reduces risk of a capacity-related service interruption."),
    RemediationAction("A4", "Patch virtualization host", 3, 7,
                      "Reduces platform vulnerability and stability risk."),
    RemediationAction("A5", "Patch externally exposed server", 1, 6,
                      "Reduces exposure on an internet-facing workload."),
    RemediationAction("A6", "Repair monitoring coverage gap", 1, 4,
                      "Improves detection and response for a critical service."),
)

BUDGET = 7  # engineer-hour units in the synthetic example
# Binary slack bits represent 0..7 unused effort units.
SLACK_WEIGHTS: tuple[int, ...] = (1, 2, 4)
# These conflicts model actions that cannot share this change window.
CONFLICTS: tuple[tuple[int, int], ...] = ((0, 1), (2, 3))
# Each violated hard constraint costs more than the total possible benefit.
PENALTY = sum(action.benefit for action in ACTIONS) + 1
N_ACTIONS = len(ACTIONS)
N_SLACK = len(SLACK_WEIGHTS)
N_VARIABLES = N_ACTIONS + N_SLACK


def selected_effort(action_bits: Iterable[int]) -> int:
    bits = list(action_bits)
    return sum(action.effort * int(bits[i]) for i, action in enumerate(ACTIONS))


def selected_benefit(action_bits: Iterable[int]) -> int:
    bits = list(action_bits)
    return sum(action.benefit * int(bits[i]) for i, action in enumerate(ACTIONS))


def has_conflict(action_bits: Iterable[int]) -> bool:
    bits = list(action_bits)
    return any(int(bits[i]) and int(bits[j]) for i, j in CONFLICTS)


def is_action_selection_feasible(action_bits: Iterable[int]) -> bool:
    bits = list(action_bits)
    return (
        len(bits) == N_ACTIONS
        and selected_effort(bits) <= BUDGET
        and not has_conflict(bits)
    )


def qubo_coefficients(
    penalty: float = PENALTY,
) -> tuple[float, np.ndarray, dict[tuple[int, int], float]]:
    """Return offset, linear and quadratic coefficients for the QUBO.

    C(x) = -benefit
           + penalty * (effort + slack - budget)^2
           + penalty * (x_A1*x_A2 + x_A3*x_A4).

    Because variables are binary, x_i**2 == x_i.
    """
    offset = 0.0
    linear = np.zeros(N_VARIABLES, dtype=float)
    quadratic: dict[tuple[int, int], float] = {}

    # Maximize benefit by minimizing negative benefit.
    for i, action in enumerate(ACTIONS):
        linear[i] -= action.benefit

    weights = [action.effort for action in ACTIONS] + list(SLACK_WEIGHTS)
    constant = -BUDGET
    offset += penalty * (constant ** 2)

    # Expand penalty * (constant + sum_i weights_i*x_i)^2.
    # For binary variables, x_i**2 = x_i.
    for i, weight_i in enumerate(weights):
        linear[i] += penalty * (
            weight_i ** 2 + 2 * constant * weight_i
        )

        for j in range(i + 1, N_VARIABLES):
            weight_j = weights[j]
            key = (i, j)
            quadratic[key] = (
                quadratic.get(key, 0.0)
                + penalty * 2 * weight_i * weight_j
            )

    # Penalize selecting incompatible actions.
    for i, j in CONFLICTS:
        key = (i, j) if i < j else (j, i)
        quadratic[key] = quadratic.get(key, 0.0) + penalty

    return offset, linear, quadratic


def evaluate_qubo(
    bits: Iterable[int],
    penalty: float = PENALTY,
) -> float:
    """Evaluate the QUBO directly, using action and slack bits in qubit-index order."""
    values = [int(bit) for bit in bits]
    if len(values) != N_VARIABLES or any(bit not in (0, 1) for bit in values):
        raise ValueError(f"Expected {N_VARIABLES} binary values.")
    offset, linear, quadratic = qubo_coefficients(penalty)
    score = offset + float(np.dot(linear, values))
    for (i, j), coefficient in quadratic.items():
        score += coefficient * values[i] * values[j]
    return float(score)


def is_qubo_feasible(bits: Iterable[int]) -> bool:
    """Whether budget equality with slack and all conflict constraints are satisfied."""
    values = [int(bit) for bit in bits]
    if len(values) != N_VARIABLES:
        return False
    action_bits = values[:N_ACTIONS]
    slack_value = sum(weight * values[N_ACTIONS + i] for i, weight in enumerate(SLACK_WEIGHTS))
    return (
        selected_effort(action_bits) + slack_value == BUDGET
        and not has_conflict(action_bits)
    )


def exact_classical_solution() -> dict[str, object]:
    """Brute-force all 2^6 action selections for the exact feasible optimum."""
    best: dict[str, object] | None = None
    for bits in product((0, 1), repeat=N_ACTIONS):
        if not is_action_selection_feasible(bits):
            continue
        effort = selected_effort(bits)
        benefit = selected_benefit(bits)
        candidate: dict[str, object] = {
            "bits": list(bits),
            "selected_ids": [ACTIONS[i].action_id for i, bit in enumerate(bits) if bit],
            "selected_names": [ACTIONS[i].name for i, bit in enumerate(bits) if bit],
            "effort": effort,
            "benefit": benefit,
        }
        if best is None or benefit > int(best["benefit"]):
            best = candidate
    if best is None:
        raise RuntimeError("No feasible action selection found.")
    return best


def qubo_to_hamiltonian(penalty: float = PENALTY):
    """Map the QUBO to a SparsePauliOp using x_i=(I-Z_i)/2."""
    from qiskit.quantum_info import SparsePauliOp

    offset, linear, quadratic = qubo_coefficients(penalty)
    identity_coefficient = offset + float(np.sum(linear)) / 2.0
    z_coefficients = -linear / 2.0

    for (i, j), coefficient in quadratic.items():
        identity_coefficient += coefficient / 4.0
        z_coefficients[i] -= coefficient / 4.0
        z_coefficients[j] -= coefficient / 4.0

    terms: dict[str, complex] = {"I" * N_VARIABLES: complex(identity_coefficient)}
    # Qiskit Pauli labels are written from highest-index qubit (left) to qubit 0 (right).
    for i, coefficient in enumerate(z_coefficients):
        if abs(coefficient) > 1e-12:
            label = ["I"] * N_VARIABLES
            label[N_VARIABLES - 1 - i] = "Z"
            key = "".join(label)
            terms[key] = terms.get(key, 0.0j) + complex(coefficient)

    for (i, j), coefficient in quadratic.items():
        if abs(coefficient) <= 1e-12:
            continue
        label = ["I"] * N_VARIABLES
        label[N_VARIABLES - 1 - i] = "Z"
        label[N_VARIABLES - 1 - j] = "Z"
        key = "".join(label)
        terms[key] = terms.get(key, 0.0j) + complex(coefficient / 4.0)

    return SparsePauliOp.from_list(
        [(label, coeff) for label, coeff in terms.items() if abs(coeff) > 1e-12]
    ).simplify()
