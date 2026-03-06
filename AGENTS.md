# AGENTS.md — Rules for AI Agents Working in This Repo

This file tells Cursor, Claude, Copilot, and any other AI agent
the rules of this repository. Read this before making any change.

---

## What this repo is

MetaGenesis Core is a verification protocol layer.
It makes computational scientific claims tamper-evident,
reproducible, and independently auditable offline.

It is NOT a simulation platform.
It is NOT an AI coordination system.
It is NOT a molecular assembler or bio-computational system.

---

## Hard rules — never violate these

**1. Never invent implementations.**
If a file, function, or test does not exist in the repo,
say: "Not found in current project context. Please add: <path>"
Do not generate placeholder code and claim it is real.

**2. steward_audit must PASS after every change.**
Before completing any task, run:
python scripts/steward_audit.py
If it outputs anything other than STEWARD AUDIT: PASS — stop and fix.

**3. Never use forbidden language.**
Forbidden: "tamper-proof", "impossible", "unforgeable", "100% test success",
"19x performance", "GPT-5 integration", "VacuumGenesisEngine", "500+ modules"
Required: "tamper-evident under trusted verifier assumptions"

**4. Never add a claim without all four components.**
A claim requires ALL of:
  a) implementation file in backend/progress/
  b) test file in tests/
  c) entry in reports/scientific_claim_index.md (with job_kind in backticks)
  d) claim_id added to reports/canonical_state.md current_claims_list

**5. Never touch these without explicit instruction.**
- reports/canonical_state.md (except to add claim to current_claims_list)
- scripts/steward_audit.py
- tests/steward/test_cert02_pack_includes_evidence_and_semantic_verify.py
- .github/workflows/

**6. Separate FACTS from ASSUMPTIONS.**
Every technical claim must reference: file path + function name.
If you are not sure something exists, say so explicitly.

---

## How to add a new claim (correct procedure)

Step 1 — Create implementation:
File: backend/progress/<claim_id_lower>.py
Required: JOB_KIND constant, run_<name>() function returning dict with mtr_phase key

Step 2 — Register in runner:
File: backend/progress/runner.py, function _execute_job_logic()
Add dispatch block following the exact pattern of existing claims

Step 3 — Add to claim index:
File: reports/scientific_claim_index.md
Add section with: claim_id, job_kind (in backticks), V&V thresholds, reproduction command

Step 4 — Update canonical state:
File: reports/canonical_state.md
Add claim_id to current_claims_list pipe-separated value

Step 5 — Write tests:
File: tests/steward/test_<claim_id_lower>.py
Required: test no-drift/success case, test failure case, test adversarial edge case

Step 6 — Verify:
python scripts/steward_audit.py → STEWARD AUDIT: PASS
python -m pytest tests/steward tests/materials -q → all passed

---

## Acceptance commands (run before any commit)

python scripts/steward_audit.py
python -m pytest tests/steward tests/materials -q
python demos/open_data_demo_01/run_demo.py
grep -r "tamper-proof\|GPT-5\|19x\|VacuumGenesis" docs/ scripts/ backend/

All must pass. grep must return empty.

---

## Architecture in one paragraph

Job runs via runner.run_job() → produces run_artifact.json + ledger_snapshot.jsonl
→ evidence_index maps artifacts to claims → steward_submission_pack bundles everything
→ mg.py verify checks integrity (SHA-256) then semantic invariants (job_snapshot present,
canary_mode correct, payload.kind matches) → PASS or FAIL.
Steward_audit enforces bidirectional coverage: runner kinds == claim_index kinds == canonical_state.
