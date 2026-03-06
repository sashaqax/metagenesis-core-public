# Submission Pack Overview

## Project

- **Project:** MetaGenesis Core
- **Owner:** MetaGenesis

## Proof-loop summary

Execution → Evidence (progress_runs, ledger_snapshots) → Evidence Index → Evidence API (GET /api/evidence/{trace_id}). All domain results live under `job_snapshot.result` in run artifacts.

## Governance invariants

- Policy Gate: all changed paths must match allowlist; locked paths blocked.
- Steward audit: required files exist; phase 42 locked; bidirectional claim coverage (runner mtr* kinds ↔ scientific_claim_index).
- Case opening protocol: contract (kind/payload), normal + canary, evidence artifacts, V&V + reproducibility shape.

## Claims

MTR-1, MTR-2, MTR-3, DATA-PIPE-01, SYSID-01

## Reproduction commands

- `python -m pytest tests/materials/test_mtr1_youngs_modulus.py -v`
- `python -m pytest tests/materials/test_mtr2_thermal_paste_conductivity.py -v`
- `python -m pytest tests/materials/test_mtr3_thermal_multilayer.py -v`
- `python -m pytest tests/data/test_datapipe01_quality_certificate.py -v`
- `python -m pytest tests/systems/test_sysid01_arx_calibration.py -v`

## Evidence location rule

Domain results are stored in **job_snapshot.result** in the run artifact JSON (reports/progress_runs/ or configured artifact dir).
