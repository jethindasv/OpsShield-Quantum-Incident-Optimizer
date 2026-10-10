# Benchmark protocol

1. Run the exact classical solver first and record its selected actions, effort, and benefit.
2. Run QAOA with fixed `reps=1`, `seed=7`, and a declared shot count.
3. Record the total shots, feasible shots, feasibility yield, best feasible sampled score, and gap to the exact optimum.
4. Repeat with at least three declared seeds if time permits. Do not silently discard unsuccessful or infeasible runs.
5. Optionally compare `reps=1` and `reps=2` if local simulation runtime permits. Report actual runtime and all parameter settings.
6. Do not state that QAOA outperforms classical optimization unless the measurements demonstrate it under a fair, explicitly described comparison. No quantum advantage is claimed by this repository.
