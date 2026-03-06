#!/usr/bin/env python3
"""
OPEN-DATA-DEMO-01: Offline-verifiable demo using existing MTR-1 pipeline.

Uses open dataset from demos/open_data_demo_01/data/. Runs runner (normal + canary),
builds pack with evidence, verifies pack, prints PASS or FAIL.
No new claims. No new runner modules. No network required.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Run from repo root so dataset_relpath and mg scripts resolve
DEMO_DIR = Path(__file__).resolve().parent
REPO_ROOT = DEMO_DIR.parent.parent  # demos/open_data_demo_01 -> demos -> repo root
DATASET_RELPATH = "demos/open_data_demo_01/data/strain_stress_open.csv"


def _run_job(canary_mode: bool) -> None:
    """Run MTR-1 with open dataset via existing ProgressRunner."""
    os.environ["MG_PROGRESS_ARTIFACT_DIR"] = str(DEMO_DIR)
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    (DEMO_DIR / "progress_runs").mkdir(parents=True, exist_ok=True)
    (DEMO_DIR / "ledger_snapshots").mkdir(parents=True, exist_ok=True)

    from backend.ledger.ledger_store import LedgerStore
    from backend.progress.mtr1_calibration import JOB_KIND as MTR1_KIND
    from backend.progress.runner import ProgressRunner
    from backend.progress.store import JobStore

    job_store = JobStore()
    ledger_store = LedgerStore(file_path=str(DEMO_DIR / "ledger.jsonl"))
    runner = ProgressRunner(job_store=job_store, ledger_store=ledger_store)

    payload = {
        "kind": MTR1_KIND,
        "dataset_relpath": DATASET_RELPATH,
        "elastic_strain_max": 0.002,
    }
    job = runner.create_job(payload=payload)
    runner.run_job(job.job_id, canary_mode=canary_mode)


def _mg(args: list) -> int:
    """Run mg CLI from repo root. Returns exit code."""
    cmd = [sys.executable, str(REPO_ROOT / "scripts" / "mg.py")] + args
    return subprocess.run(cmd, cwd=str(REPO_ROOT), executable=sys.executable).returncode


def main() -> int:
    os.chdir(REPO_ROOT)
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    data_path = REPO_ROOT / DATASET_RELPATH
    if not data_path.exists():
        print("FAIL: Dataset not found at " + DATASET_RELPATH)
        return 1

    # 1. Run normal and canary evidence
    _run_job(canary_mode=False)
    _run_job(canary_mode=True)

    # 2. Pack build with evidence
    pack_dir = DEMO_DIR / "pack"
    pack_dir.mkdir(parents=True, exist_ok=True)
    rc_build = _mg([
        "pack", "build",
        "--output", str(pack_dir),
        "--include-evidence",
        "--source-reports-dir", str(DEMO_DIR),
    ])
    if rc_build != 0:
        print("FAIL: Pack build failed (exit code " + str(rc_build) + ")")
        return 1

    # 3. Verify pack, write JSON report
    report_path = DEMO_DIR / "VERIFY_REPORT.json"
    rc_verify = _mg(["verify", "--pack", str(pack_dir), "--json", str(report_path)])
    if rc_verify != 0:
        print("FAIL: Pack verify failed (exit code " + str(rc_verify) + ")")
        return 1

    # 4. Check report
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print("FAIL: Could not read VERIFY_REPORT.json: " + str(e))
        return 1

    manifest_ok = report.get("manifest_ok") is True
    semantic_ok = report.get("semantic_ok") is True
    errors = report.get("errors") or []

    if manifest_ok and semantic_ok and len(errors) == 0:
        print("PASS")
        return 0
    reason = "; ".join(errors) if errors else ("manifest_ok=" + str(manifest_ok) + ", semantic_ok=" + str(semantic_ok))
    print("FAIL: " + reason)
    return 1


if __name__ == "__main__":
    sys.exit(main())
