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

| Metric | Penalty 45 | Penalty 90 | Penalty 120 | Penalty 144 |
|---|---:|---:|---:|---:|
| Feasible samples | 337 | 326 | 341 | 464 |
| Total shots | 4096 | 4096 | 4096 | 4096 |
| Feasibility yield | 8.23% | 7.96% | 8.33% | 11.33% |
| Best feasible benefit | 28 | 28 | 28 | 28 |
| Gap to exact optimum | 0 | 0 | 0 | 0 |


Penalty 144 achieved the highest feasibility yield in the four
seed-7 experiments. All four runs sampled the exact classical
optimum, with benefit 28.

This is preliminary evidence, not proof that penalty 144 is
universally optimal. Additional random seeds are required to
evaluate repeatability.

Expected QUBO energies are not directly comparable across
penalty values because the penalty changes the objective scale.

## Repeatability study: penalty 144

The penalty-144 configuration was evaluated with three random seeds,
keeping QAOA depth 1, maxiter 60 and 4096 shots fixed.

| Seed | Feasibility yield | Best feasible benefit |
|---:|---:|---:|
| 7 | 11.33% | 28 |
| 21 | 6.8% | 28 |
| 42 | 6.7% | 28 |

All three runs sampled the exact classical optimum, with benefit 28.

Feasibility yield varied by seed. Therefore, the earlier observation
that penalty 144 performed best in the four-value seed-7 penalty sweep
does not establish that it is the best setting in general.

The results use synthetic incident-response data and a local
statevector simulator. They do not demonstrate quantum advantage.
Further evaluation would require more seeds, penalty settings and
larger problem instances.