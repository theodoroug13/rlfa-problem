# RLFA Problem (Radio Link Frequency Assignment) — CSP Solver in Python

A Python implementation for solving the **Radio Link Frequency Assignment Problem (RLFAP)** as a **Constraint Satisfaction Problem (CSP)**.

In short: we assign a frequency to each radio link from an allowed set of frequencies, while satisfying interference constraints between “nearby” links.

---

## Problem summary

Each radio link is modeled as a variable with its own domain (allowed frequencies). The main constraints are typically of the form:

|F1 - F2| > k12

Meaning two links must be separated by at least `k12` in frequency to avoid interference.

RLFAP is **NP-hard** and is commonly used as a benchmark for CSP techniques.

---

## Repository contents

- `rlfa.py` — main entry point / runner (loads an instance, runs a solver, prints results)
- `csp.py` — CSP primitives + solving utilities (constraints, consistency checks, search helpers)
- `search.py` — generic search routines used by the CSP solver
- `utils.py` — helper utilities
- `rlfap/` — problem instances / datasets (inputs for the solver)
- `sortedcontainers/` — vendored dependency used by the implementation

---

## Getting started

### Requirements
- Python 3.x

### Run
From the repository root:

    python rlfa.py

If the script supports CLI flags/arguments:

    python rlfa.py --help

---

## Input format (instances)

Instances usually provide:
- **Variables**: radio links
- **Domains**: allowed frequencies per link
- **Constraints**: pairs of links with separation requirements

This repo includes an `rlfap/` directory intended for storing/reading these instances.

---

## Ideas for extensions

If you want to make this even more “portfolio-ready”:

- Add a `requirements.txt` (even if you vendor dependencies)
- Add an `examples/` section with 1–2 commands that reproduce a run + sample output
- Add a short “Methods” section describing what heuristics/consistency methods you used and what they improve

---

## Author

**Giorgos Theodorou**  
GitHub: https://github.com/theodoroug13
