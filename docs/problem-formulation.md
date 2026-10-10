# OpsShield problem formulation

## Use case

A hypothetical infrastructure team has a limited maintenance window and several candidate remediation actions. Each action has an effort cost and a benefit score representing an illustrative reduction in operational risk. Some pairs cannot be implemented in the same window. The team selects a subset that maximizes the total benefit without exceeding the effort budget or selecting a conflicting pair.

All names, scores, effort costs, and conflicts in this repository are synthetic demonstration values. They are not drawn from any employer or production environment.

## Decision variables

For each action `i`, `x_i = 1` means select it and `x_i = 0` means do not select it. Three binary slack variables with weights 1, 2, and 4 encode unused effort units from zero to seven.

## Objective and constraints

Let `b_i` be benefit, `e_i` effort, and `H=7` the available budget. Minimize:

`C(x,s) = -sum_i b_i*x_i + P*(sum_i e_i*x_i + s_0 + 2*s_1 + 4*s_2 - H)^2 + P*(x_0*x_1 + x_2*x_3)`

The first penalty enforces the budget using binary slack. The second enforces the two incompatibility rules. The penalty P is chosen above the sum of all benefits so a violated hard constraint is more expensive than any possible benefit gain in this specific instance.

This expands to a QUBO because binary variables satisfy `x_i^2 = x_i`. The cost is mapped to a diagonal Pauli Hamiltonian using `x_i = (I - Z_i)/2`.

## Classical benchmark

Enumerate all `2^6 = 64` action combinations. Reject combinations exceeding the budget or containing a conflicting pair. Select the remaining combination with the highest total benefit. This exact feasible optimum is the reference for QAOA solution quality on this small instance.

## Evaluation metrics

- Best observed feasible QAOA sample and its benefit.
- Exact classical feasible optimum and benefit.
- Gap in benefit between QAOA's best feasible observed sample and the exact optimum.
- Feasibility yield: measured shots whose action and slack bits satisfy every QUBO constraint divided by all measured shots.
- Optimizer's final expected QUBO energy and evaluation trace.

A small statevector run is a method demonstration, not evidence of quantum advantage. The classical baseline is expected to be very strong on six binary decisions.
