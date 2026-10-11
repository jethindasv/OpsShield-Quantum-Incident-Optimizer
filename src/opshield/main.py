"""Command-line entry point for OpsShield."""
from __future__ import annotations

import argparse
import json

from .model import ACTIONS, BUDGET, CONFLICTS, exact_classical_solution
from .model import ACTIONS, BUDGET, CONFLICTS, PENALTY, exact_classical_solution
from .solver import run_qaoa


def print_problem() -> None:
    print("\nOPSSHIELD | Synthetic remediation planning instance")
    print(f"Effort budget: {BUDGET} engineer-hour units")
    print("Data are synthetic and for demonstration only.\n")
    for action in ACTIONS:
        print(f"{action.action_id} | effort={action.effort} | benefit={action.benefit:2d} | {action.name}")
    labels = [(ACTIONS[i].action_id, ACTIONS[j].action_id) for i, j in CONFLICTS]
    print(f"Mutually incompatible pairs in this change window: {labels}\n")
    exact = exact_classical_solution()
    print("Exact classical baseline:")
    print(f"  Selected: {', '.join(exact['selected_ids'])}")
    print(f"  Effort: {exact['effort']}/{BUDGET}")
    print(f"  Total benefit: {exact['benefit']}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the OpsShield QAOA experiment locally.")
    parser.add_argument("--reps", type=int, default=1, help="QAOA depth; start with 1.")
    parser.add_argument("--maxiter", type=int, default=60, help="COBYLA objective-evaluation limit.")
    parser.add_argument("--shots", type=int, default=4096, help="Number of statevector samples.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed for repeatability.")
    parser.add_argument(
    "--penalty",
    type=float,
    default=PENALTY,
    help="QUBO constraint penalty coefficient.",
)
    parser.add_argument("--output-dir", default="artifacts", help="Directory for JSON report and charts.")
    parser.add_argument("--skip-qaoa", action="store_true", help="Print model and exact baseline only.")
    args = parser.parse_args()

    print_problem()
    if args.skip_qaoa:
        return

    print("Running QAOA on the local statevector simulator...")
    report = run_qaoa(reps=args.reps, maxiter=args.maxiter, shots=args.shots, seed=args.seed, output_dir=args.output_dir,penalty=args.penalty,)
    print("\nQAOA summary")
    print(f"  QUBO penalty: {report['qubo_penalty']}")
    print(f"  Expected QUBO energy: {report['final_expected_qubo_energy']:.4f}")
    print(f"  Feasibility yield: {report['feasibility_yield']:.1%}")
    print(f"  Exact classical benefit: {report['exact_classical_optimum']['benefit']}")
    candidate = report["best_feasible_qaoa_sample"]
    if candidate:
        print(f"  Best feasible QAOA sample: {', '.join(candidate['selected_ids'])}")
        print(f"  Sample benefit: {candidate['benefit']} (effort {candidate['effort']}/{BUDGET})")
        print(f"  Gap to exact benefit: {report['exact_classical_optimum']['benefit'] - candidate['benefit']}")
    else:
        print("  No feasible QAOA sample observed. Increase shots or test a different seed/depth.")
    print(f"\nSaved {args.output_dir}/results.json and charts in {args.output_dir}/")


if __name__ == "__main__":
    main()
