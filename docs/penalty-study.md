# OpsShield — QUBO Penalty Study

## Purpose

This experiment evaluates how the QUBO constraint-penalty coefficient affects QAOA results for the synthetic incident-response optimization problem.

The goal is to maximize remediation benefit while respecting the engineering-effort budget and two incompatibility constraints.

## Experimental setup

- QAOA depth (`reps`): 1
- Optimizer iteration limit: 60
- Measurement shots: 4,096
- Random seed: 7
- Exact classical optimum: benefit score 28
- Optimal selection: A1, A3, A5, A6
- Required effort: 7 of 7 units

Only the penalty coefficient was changed between the two reported runs.

## Results

| Metric | Penalty 144 | Penalty 45 |
|---|---:|---:|
| Expected QUBO energy | 1501.7321 | 746.8133 |
| Feasible samples | 464 | 337 |
| Feasibility yield | 11.33% | 8.23% |
| Best feasible benefit | 28 | 28 |
| Gap to exact optimum | 0 | 0 |
| Occurrences of the optimal bitstring | 9 | 4 |

## Interpretation

Both runs sampled the exact classical optimum, selecting A1, A3, A5, and A6 for a total benefit score of 28.

Penalty 144 produced 127 more feasible samples than penalty 45, improving feasibility yield by approximately 3.10 percentage points in this experiment.

The expected QUBO energies are not directly comparable as solution-quality metrics because the penalty changes the scale of the cost function.

These results do not establish a universally optimal penalty. More runs and additional random seeds are needed to evaluate sensitivity and repeatability.

## Limitations

- The problem uses synthetic benefit and effort scores.
- The experiment uses a local statevector simulator, not a physical quantum processor.
- Results from one seed cannot establish statistical robustness.
- No quantum advantage over classical optimization is demonstrated.
- The exact classical solver remains the reference for solution quality on this small instance.

## Next experiment

Test intermediate penalty values while keeping the QAOA settings fixed. Compare feasibility yield, optimal-solution frequency, and the gap to the exact classical optimum. Preserve each run's parameters and result files.
