# OpsShield — Quantum Incident Response Optimizer
# OpsShield — Quantum Incident Response Optimizer

## Project Metadata

- **Project Title:** OpsShield — Quantum Incident Response Optimizer
- **Team Name:** [Jethindas V]
- **Chosen Track:** Track 2 — Open-Domain Optimization & Real-World Solvers
- **Video Presentation Link:** [Watch the OpsShield presentation](https://drive.google.com/file/d/1DlkGHTkU1ygNpyaQcI3794S6Wsx_5Ga3/view?usp=drive_link)
- **Live Demo Timestamp in Video:** [06:40]

### Team Members (Maximum 4)

| Name | Email | GitHub Username |
|---|---|---|
| [Jethindas V] | [jethindas25imcs11007@iiitkottayam.ac.in] | [@jethindasv] |


---


**Tagline:** When everything cannot be fixed at once, fix what matters most.

OpsShield is a hackathon-sized demonstration of converting a risk-aware IT remediation planning dilemma into a QUBO and testing it with Qiskit QAOA. A classical exhaustive search provides the exact baseline.

> **Important scope note:** All incidents, actions, effort estimates, benefits, and compatibility constraints are synthetic. OpsShield is an educational optimization experiment, not a production incident-management system. The project makes no claim of quantum advantage.

## Problem

Choose a portfolio of remediation actions that maximizes illustrative risk-reduction benefit while respecting a seven-unit engineering effort budget and two mutually exclusive change-window pairs. Binary slack variables make the `<= budget` constraint representable as an equality penalty in the QUBO.

The model has six action variables plus three slack variables (nine qubits). An exact classical search evaluates the 64 action portfolios to establish the true feasible optimum for this small instance.

## Technology

- Python 3.12
- Qiskit 2.5.x `QAOAAnsatz`
- `StatevectorEstimator` and `StatevectorSampler` for local simulation
- SciPy COBYLA optimizer
- Exact classical exhaustive search
- Matplotlib result charts

## Setup in VS Code on Windows

Use the already-working `qiskit-fallfest312` environment if it is still present at `%USERPROFILE%\qiskit-fallfest312`:

```powershell
& "$env:USERPROFILE\qiskit-fallfest312\Scripts\Activate.ps1"
python --version
python -m pip install -e ".[dev]"
```

If creating a new environment instead, use Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

In VS Code, select the matching Python interpreter via **Ctrl+Shift+P → Python: Select Interpreter**.

## Run the classical baseline first

```powershell
python -m opshield.main --skip-qaoa
```

Expected exact baseline for the supplied synthetic model:

- Actions: `A1`, `A3`, `A5`, `A6`
- Effort: `7/7`
- Benefit score: `28`

If this changes, stop and investigate before running QAOA.

## Run the QAOA experiment

```powershell
python -m opshield.main --reps 1 --maxiter 60 --shots 4096 --seed 7
```

The program writes:

- `artifacts/results.json` — parameters, feasibility yield, exact baseline, and observed QAOA outcome.
- `artifacts/qaoa_energy.png` — optimizer objective trace.
- `artifacts/sample_distribution.png` — most frequent sampled bitstrings.

QAOA is stochastic and may not observe a feasible or optimal sample in every run. The report explicitly records this rather than hiding it.

## Tests

```powershell
python -m pytest -q
```

The pure problem-model tests do not require IBM account credentials. Start with local simulation; hardware is optional and should only be attempted once the model and simulator run correctly.
## Experimental Results

All experiments below use a local Qiskit statevector simulator, QAOA depth 1, a maximum of 60 optimizer iterations, and 4,096 shots per run unless otherwise noted.

### QUBO penalty sweep

The random seed was fixed at 7 while the constraint-penalty coefficient was varied.

| Penalty | Feasible samples | Feasibility yield | Best feasible benefit |
|---:|---:|---:|---:|
| 45 | 337 / 4096 | 8.23% | 28 |
| 90 | 326 / 4096 | 7.96% | 28 |
| 120 | 341 / 4096 | 8.33% | 28 |
| 144 | 464 / 4096 | 11.33% | 28 |

### Repeatability check

With penalty 144, three random seeds produced the following feasibility yields:

| Seed | Feasibility yield | Best feasible benefit |
|---:|---:|---:|
| 7 | 11.33% | 28 |
| 21 | 6.8% | 28 |
| 42 | 6.7% | 28 |

The exact classical optimum is a benefit score of 28, achieved by selecting A1, A3, A5 and A6 within the effort budget. All reported QAOA runs sampled this optimum at least once.

### Interpretation and limitations

Penalty 144 had the highest feasibility yield in the four-value penalty sweep using seed 7. The repeatability results show that the yield varies with the random seed; these experiments do not establish a universally optimal penalty.

The problem uses synthetic action benefits, effort requirements and compatibility constraints. All quantum experiments reported here used a local statevector simulator, not a physical quantum processor. The results do not demonstrate quantum advantage over classical optimization.

The exact classical solver remains the reference for solution quality on this small instance. Larger problem sizes, additional seeds, and further benchmarking are needed to assess scalability and robustness.

## Suggested submission contents

- This README and the mathematical formulation in `docs/problem-formulation.md`.
- Exact model and solver code in `src/opshield/`.
- Automated checks in `tests/`.
- Real generated benchmark data and plots in `artifacts/`.
- A short presentation stating the problem, equations, QAOA method, exact baseline, results, limitations, and next steps.

## Reproducibility and security

- Commit files and results as the work is completed during the event window.
- Never commit API keys, CRNs, access tokens, passwords, local `.env` files, or account screenshots.
- The baseline and QAOA simulator do not need IBM Quantum credentials. Real hardware execution is intentionally optional.
- Do not edit or backdate Git commit timestamps. Follow the organizers' exact submission rules.

## Optional repeatability check

After the first run succeeds, repeat with separate output directories so each run is preserved:

```powershell
python -m opshield.main --reps 1 --maxiter 60 --shots 4096 --seed 21 --output-dir artifacts/seed_21
python -m opshield.main --reps 1 --maxiter 60 --shots 4096 --seed 42 --output-dir artifacts/seed_42
```

Report variability across seeds rather than choosing only the best result. Do not overwrite or omit a run simply because it produced no feasible sample.
