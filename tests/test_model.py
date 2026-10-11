from itertools import product

from opshield.model import (
    ACTIONS,
    BUDGET,
    N_ACTIONS,
    N_VARIABLES,
    exact_classical_solution,
    is_action_selection_feasible,
    is_qubo_feasible,
    qubo_coefficients,
    evaluate_qubo,
    selected_benefit,
    selected_effort,
)


def test_exact_baseline_is_feasible_and_expected():
    best = exact_classical_solution()
    assert is_action_selection_feasible(best["bits"])
    assert best["effort"] <= BUDGET
    assert best["selected_ids"] == ["A1", "A3", "A5", "A6"]
    assert best["benefit"] == 28
    assert best["effort"] == 7


def test_all_action_bitstrings_have_consistent_effort_and_benefit():
    for bits in product((0, 1), repeat=N_ACTIONS):
        assert selected_effort(bits) == sum(ACTIONS[i].effort * bits[i] for i in range(N_ACTIONS))
        assert selected_benefit(bits) == sum(ACTIONS[i].benefit * bits[i] for i in range(N_ACTIONS))


def test_best_exact_solution_beats_all_feasible_selections():
    optimum = exact_classical_solution()["benefit"]
    for bits in product((0, 1), repeat=N_ACTIONS):
        if is_action_selection_feasible(bits):
            assert selected_benefit(bits) <= optimum


def test_qubo_feasibility_for_known_optimal_selection_with_slack():
    # A1+A3+A5+A6 consumes 7 units, so all slack bits are zero.
    bits = [1, 0, 1, 0, 1, 1, 0, 0, 0]
    assert len(bits) == N_VARIABLES
    assert is_qubo_feasible(bits)


def test_qubo_energy_of_feasible_optimum_is_negative_benefit():
    bits = [1, 0, 1, 0, 1, 1, 0, 0, 0]
    assert evaluate_qubo(bits) == -28.0


def test_qubo_coefficients_have_expected_dimensions():
    offset, linear, quadratic = qubo_coefficients()
    assert offset > 0
    assert len(linear) == N_VARIABLES
    assert quadratic

def test_qubo_penalty_is_configurable():
    # A1 + A2 violates the first conflict rule.
    # Its effort is 5; the slack bit of weight 2 fills the budget.
    bits = [1, 1, 0, 0, 0, 0, 0, 1, 0]

    assert evaluate_qubo(bits, penalty=45) == 26.0
    assert evaluate_qubo(bits, penalty=144) == 125.0