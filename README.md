# OpsShield — Quantum Incident Response Optimizer

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
