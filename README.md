# RLFA / RLFAP — CSP Solver (Python)

This repository solves the **Radio Link Frequency Assignment Problem (RLFAP)** by modeling it as a **Constraint Satisfaction Problem (CSP)**.

Each radio link is a variable with an allowed set of frequencies (domain). Constraints between pairs of links enforce minimum separation, using operators like `<`, `>`, `=` depending on the instance specification.

---

## What’s implemented

### Parsing & modeling
- **`parse_files(...)`**: parses the three RLFA instance files (variables, domains, constraints).
- **`RLFA` class**: extends a generic CSP and builds a `constraints_map` keyed by `(Xi, Xj)` for fast constraint lookup.

### Solvers compared (run from `rlfa.py`)
- **FC + MRV**: Forward Checking with **Minimum Remaining Values** variable ordering.
- **MAC + dom/wdeg**: Maintain Arc Consistency with a **dom/wdeg** variable heuristic.
  - Includes a modified **revise/AC-3** pipeline that can update constraint weights on domain wipe-out.
- **FC-CBJ + dom/wdeg**: Forward Checking with **Conflict-Directed Backjumping**, implemented from scratch.

### Metrics & timeout
- Prints a results table including:
  - runtime,
  - number of assignments (visited nodes),
  - number of constraint checks,
  - solved/unsolved,
  - and **TIMEOUT** if execution exceeds the time limit (1 minute).

---

## Repository structure (high level)

- `rlfa.py` — main runner: loads an instance, runs solvers, prints metrics
- `csp.py`, `search.py`, `utils.py` — CSP/search utilities (AIMA-based)
- `sortedcontainers/` — vendored dependency used by the implementation
- `rlfap/` — RLFA benchmark instances (variables/domains/constraints files)

---

## How to run

1. Choose the instance files inside `rlfa.py` (currently selected in `main`).
2. Run:

```bash
python rlfa.py
# or (linux)
python3 rlfa.py
