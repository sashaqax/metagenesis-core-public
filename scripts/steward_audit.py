#!/usr/bin/env python3
"""
STEW-01/STEW-02 Deterministic Steward / Repository Guardian.

Validates canonical state, phase registry, claim invariants, and bidirectional
claim coverage (runner dispatch <-> scientific_claim_index job_kinds).
NO LLM. NO network. NO new deps. Stdlib only.
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REQUIRED_FILES = [
    "reports/canonical_state.md",
    "reports/phase_registry_v0_1.md",
    "backend/progress/runner.py",
    "reports/scientific_claim_index.md",
]


def _read(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _required_files_exist() -> tuple[bool, list[str]]:
    missing = []
    for rel in REQUIRED_FILES:
        if not (REPO_ROOT / rel).exists():
            missing.append(rel)
    return len(missing) == 0, missing


def _parse_phase_registry() -> tuple[bool, str, dict]:
    path = REPO_ROOT / "reports/phase_registry_v0_1.md"
    text = _read(path)
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if not match:
        return False, "No fenced JSON block in phase_registry_v0_1.md", {}
    try:
        data = json.loads(match.group(1).strip())
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in phase registry: {e}", {}
    return True, "", data


def _phase_42_locked(data: dict) -> tuple[bool, str]:
    phases = data.get("phases") or []
    for p in phases:
        if p.get("phase") == 42:
            if p.get("locked") is True:
                return True, ""
            return False, "Phase 42 must be locked"
    return False, "Phase 42 missing from registry"


def _extract_runner_dispatch_kinds() -> set[str]:
    """Extract all job kinds dispatched in runner (payload.get('kind') == ...)."""
    runner_path = REPO_ROOT / "backend/progress/runner.py"
    text = _read(runner_path)
    kinds = set()
    # Find modules that import JOB_KIND (used for dispatch)
    for m in re.finditer(r"from\s+backend\.progress\.(\w+)\s+import[^\n]*JOB_KIND", text):
        module = m.group(1)
        py_path = REPO_ROOT / "backend/progress" / f"{module}.py"
        if not py_path.exists():
            continue
        mod_text = _read(py_path)
        match = re.search(r'JOB_KIND\s*=\s*["\']([^"\']+)["\']', mod_text)
        if match:
            kinds.add(match.group(1))
    return kinds


def _extract_claim_index_job_kinds() -> set[str]:
    """Extract all job_kind values from reports/scientific_claim_index.md (robust regex, backticks)."""
    path = REPO_ROOT / "reports/scientific_claim_index.md"
    text = _read(path)
    kinds = set()
    for m in re.finditer(r"\*\*job_kind\*\*\s*\|\s*`([^`]+)`", text, re.IGNORECASE):
        kinds.add(m.group(1).strip())
    return kinds


def _claim_coverage_bidirectional() -> tuple[bool, list[str]]:
    """Enforce every claim job_kind exists in runner dispatch; every runner kind in claim index."""
    reasons = []
    runner_kinds = _extract_runner_dispatch_kinds()
    claim_kinds = _extract_claim_index_job_kinds()
    only_in_runner = runner_kinds - claim_kinds
    only_in_claim = claim_kinds - runner_kinds
    if only_in_runner:
        reasons.append(f"Kind(s) in runner but missing from scientific_claim_index: {sorted(only_in_runner)}")
    if only_in_claim:
        missing = sorted(only_in_claim)
        reasons.append(f"job_kind(s) in scientific_claim_index but not dispatched in runner: {missing}")
    return len(reasons) == 0, reasons


def _extract_canonical_claim_ids(path: Path) -> list[str]:
    """Parse | **current_claims_list** | MTR-1, MTR-2, MTR-3 | -> ['MTR-1','MTR-2','MTR-3']."""
    text = _read(path)
    for line in text.split("\n"):
        line = line.strip()
        if not line.startswith("|") or "current_claims_list" not in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        for i, part in enumerate(parts):
            if "current_claims_list" in part.replace("*", "").lower():
                if i + 1 < len(parts):
                    value = parts[i + 1]
                    return [x.strip() for x in value.split(",") if x.strip()]
                break
    raise ValueError("current_claims_list not found or empty in canonical_state.md")


def _extract_claim_index_claim_ids(path: Path) -> list[str]:
    """Parse claim IDs from scientific_claim_index.md: headings and table claim_id rows. Dedupe, stable order."""
    text = _read(path)
    claim_ids = []
    for m in re.finditer(r"^##\s+(?:Claim:?\s+)?(MTR-\d+)\s*$", text, re.MULTILINE):
        claim_ids.append(m.group(1))
    for line in text.split("\n"):
        line = line.strip()
        if "claim_id" not in line or "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        for i, part in enumerate(parts):
            if "claim_id" in part.replace("*", "").lower():
                if i + 1 < len(parts):
                    value = parts[i + 1].strip()
                    if value and value not in claim_ids:
                        claim_ids.append(value)
                break
    if not claim_ids:
        raise ValueError("No claim_ids parsed from scientific_claim_index.md")
    return list(dict.fromkeys(claim_ids))


def _canonical_claim_sync(canonical_ids: list[str], index_ids: list[str]) -> tuple[bool, list[str]]:
    """Enforce set equality. Return (ok, reasons)."""
    reasons = []
    missing = set(index_ids) - set(canonical_ids)
    extra = set(canonical_ids) - set(index_ids)
    if missing:
        reasons.append(f"Claims in scientific_claim_index but missing from canonical_state: {sorted(missing)}")
    if extra:
        reasons.append(f"Claims in canonical_state but missing from scientific_claim_index: {sorted(extra)}")
    return len(reasons) == 0, reasons


def run_audit() -> bool:
    reasons = []
    all_ok = True

    ok, missing = _required_files_exist()
    if not ok:
        all_ok = False
        reasons.append(f"Missing required files: {missing}")

    ok, err, data = _parse_phase_registry()
    if not ok:
        all_ok = False
        reasons.append(err)
    else:
        ok, err = _phase_42_locked(data)
        if not ok:
            all_ok = False
            reasons.append(err)

    ok, err_list = _claim_coverage_bidirectional()
    if not ok:
        all_ok = False
        reasons.extend(err_list)

    canonical_sync_ok = False
    try:
        canonical_ids = _extract_canonical_claim_ids(REPO_ROOT / "reports/canonical_state.md")
        index_ids = _extract_claim_index_claim_ids(REPO_ROOT / "reports/scientific_claim_index.md")
        canonical_sync_ok, sync_reasons = _canonical_claim_sync(canonical_ids, index_ids)
        if not canonical_sync_ok:
            all_ok = False
            reasons.extend(sync_reasons)
    except ValueError as e:
        all_ok = False
        reasons.append(str(e))

    if all_ok:
        print("STEWARD AUDIT: PASS")
        print("  Required files exist.")
        print("  Phase registry JSON valid; phase 42 locked.")
        print("  Claim coverage: all claim job_kinds dispatched in runner; runner kinds in claim index.")
        print(f"  canonical_state claims: {canonical_ids}")
        print(f"  claim_index claims: {index_ids}")
        print("  canonical sync: PASS")
    else:
        print("STEWARD AUDIT: FAIL")
        for r in reasons:
            print(f"  - {r}")
    return all_ok


def main():
    success = run_audit()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
