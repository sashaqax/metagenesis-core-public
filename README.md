# MetaGenesis Core

A verification protocol layer that makes computational scientific claims
tamper-evident, reproducible, and independently auditable by any third
party — offline, without trusting any single party.

## What this is

MetaGenesis Core is NOT a simulation platform.
It is a governance-enforced verification infrastructure for computational
scientific claims.

Four verified innovations:
1. Bidirectional claim coverage enforcement (steward_audit.py)
2. Tamper-evident evidence bundles with semantic verification (mg.py)
3. Policy-gate immutable evidence anchors (mg_policy_gate_policy.json)
4. Dual-mode canary execution pipeline (runner.py)

Proven by adversarial tests. Steward audit passes on every PR.

## Verify in 5 minutes
```bash
git clone https://github.com/YOUR_USERNAME/metagenesis-core-public
cd metagenesis-core-public
pip install -r requirements.txt
python demos/open_data_demo_01/run_demo.py
```

Expected output: PASS — manifest_ok: true, semantic_ok: true, errors: []

## Active claims

| ID | Domain | Status |
|----|--------|--------|
| MTR-1 | Young's modulus calibration | verified |
| MTR-2 | Thermal paste conductivity | verified |
| MTR-3 | Thermal multilayer contact | verified |
| SYSID-01 | ARX model calibration | verified |
| DATA-PIPE-01 | Data pipeline quality certificate | verified |

## Key property: semantic tamper detection

An adversary can remove evidence, recompute all SHA-256 hashes,
restore integrity check to PASS — and semantic verification still
catches the tampering (FAIL).

This is the core innovation. Not integrity alone. Integrity + semantics.

## Patent status

USPTO Provisional Patent Application filed: 2026-03-05
Application #: 63/996,819

## License

MIT
