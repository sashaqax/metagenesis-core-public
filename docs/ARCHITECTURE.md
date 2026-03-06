# Architecture

## The verification proof loop

```
Your data (CSV, measurements, model output)
           │
           ▼
    runner.run_job()
    backend/progress/runner.py
           │
           ├──── normal mode ────┐
           │                     │
           └──── canary mode ────┤
                                 │
                                 ▼
              run_artifact.json + ledger_snapshot.jsonl
              (per claim, per mode)
                                 │
                                 ▼
              evidence_index.json
              backend/progress/evidence_index.py
                                 │
                                 ▼
              Submission Pack
              scripts/steward_submission_pack.py
                ├── pack_manifest.json  (SHA-256 + root_hash)
                ├── evidence_index.json
                ├── claims/dossier_<ID>.md
                └── evidence/<CLAIM_ID>/
                      ├── normal/run_artifact.json
                      ├── normal/ledger_snapshot.jsonl
                      ├── canary/run_artifact.json
                      └── canary/ledger_snapshot.jsonl
                                 │
                                 ▼
              mg.py verify
              scripts/mg.py
                ├── integrity check (SHA-256 — detects file changes)
                └── semantic check  (detects content removal)
                         │
                         ▼
                    PASS or FAIL
                    (with specific reason)
```

## Why two verification layers

**Integrity alone is not enough.**

An adversary can:
1. Remove job_snapshot from run_artifact.json
2. Recompute all SHA-256 hashes
3. Produce a bundle where integrity = PASS

Semantic verification catches this:
- integrity: PASS (hashes match)
- semantic: FAIL (job_snapshot missing)

Proven by adversarial test:
`tests/steward/test_cert02_pack_includes_evidence_and_semantic_verify.py`
`::test_semantic_negative_missing_job_snapshot_fails_verify`

## Governance loop

```
Every pull request
        │
        ▼
  steward_audit.py
        │
        ├── required files exist?
        ├── phase 42 locked?
        ├── runner dispatch kinds == claim_index job_kinds?
        └── canonical_state claims == claim_index claims?
                │
         all pass?
           │        │
          YES        NO
           │        │
        merge    blocked
```

No claim without implementation.
No implementation without claim.
Enforced on every PR — not by human review.

## Calibration anchor and drift

```
Verified result (e.g. MTR-1: E = 70 GPa)
        │
        ▼
   DRIFT-01 anchor point
        │
   New computation: E = 76 GPa
        │
   drift = |76 - 70| / 70 * 100 = 8.6%
        │
   threshold = 5.0%
        │
   drift_detected = True
   correction_required = True
```

## Active claims

| Claim | File | job_kind |
|-------|------|---------|
| MTR-1 | backend/progress/mtr1_calibration.py | mtr1_youngs_modulus_calibration |
| MTR-2 | backend/progress/mtr2_thermal_conductivity.py | mtr2_thermal_paste_conductivity_calibration |
| MTR-3 | backend/progress/mtr3_thermal_multilayer.py | mtr3_thermal_multilayer_contact_calibration |
| SYSID-01 | backend/progress/sysid1_arx_calibration.py | sysid1_arx_calibration |
| DATA-PIPE-01 | backend/progress/datapipe1_quality_certificate.py | datapipe1_quality_certificate |
| DRIFT-01 | backend/progress/drift_monitor.py | drift_calibration_monitor |
