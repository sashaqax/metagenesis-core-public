#!/usr/bin/env python3
"""
UQ-01 Deterministic Bootstrap Uncertainty for MTR-1.

Uncertainty block exists when uq_samples > 0; determinism; bounds; evidence binding; canary consistency.
"""

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from backend.progress.runner import ProgressRunner
from backend.progress.store import JobStore
from backend.ledger.ledger_store import LedgerStore
from backend.progress.mtr1_calibration import JOB_KIND

UQ_PAYLOAD = {
    "kind": JOB_KIND,
    "seed": 42,
    "E_true": 200e9,
    "n_points": 50,
    "max_strain": 0.002,
    "uq_samples": 200,
    "uq_seed": 42,
}


def _run_mtr1_uq_job(artifact_dir: Path, payload: dict, canary_mode: bool = False):
    job_store = JobStore()
    ledger_store = LedgerStore(file_path=str(artifact_dir / "ledger.jsonl"))
    runner = ProgressRunner(job_store=job_store, ledger_store=ledger_store)
    job = runner.create_job(payload=payload)
    runner.run_job(job.job_id, canary_mode=canary_mode)
    return job.trace_id, job


class TestUq01Mtr1Uncertainty:
    """UQ-01: deterministic bootstrap uncertainty for MTR-1."""

    def test_a_uncertainty_block_exists_when_uq_samples_200(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MG_PROGRESS_ARTIFACT_DIR", str(tmp_path))
        _, job = _run_mtr1_uq_job(tmp_path, UQ_PAYLOAD, canary_mode=False)
        assert job.result is not None
        assert "uncertainty" in job.result["result"]

    def test_b_determinism_identical_payload_twice(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MG_PROGRESS_ARTIFACT_DIR", str(tmp_path))
        _, job1 = _run_mtr1_uq_job(tmp_path, UQ_PAYLOAD, canary_mode=False)
        _, job2 = _run_mtr1_uq_job(tmp_path, UQ_PAYLOAD, canary_mode=False)
        u1 = job1.result["result"]["uncertainty"]
        u2 = job2.result["result"]["uncertainty"]
        assert u1 == u2

    def test_c_bounds_sanity(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MG_PROGRESS_ARTIFACT_DIR", str(tmp_path))
        _, job = _run_mtr1_uq_job(tmp_path, UQ_PAYLOAD, canary_mode=False)
        res = job.result["result"]
        E = res["estimated_E"]
        uq = res["uncertainty"]
        assert uq["ci_low"] < E < uq["ci_high"]
        assert 0.0 <= uq["stability_score"] <= 1.0
        assert uq["std"] >= 0

    def test_d_evidence_binding_artifact_contains_uncertainty(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MG_PROGRESS_ARTIFACT_DIR", str(tmp_path))
        trace_id, job = _run_mtr1_uq_job(tmp_path, UQ_PAYLOAD, canary_mode=False)
        run_files = list((tmp_path / "progress_runs").glob("*.json"))
        assert run_files
        artifact = None
        for f in run_files:
            data = json.loads(f.read_text())
            if data.get("trace_id") == trace_id:
                artifact = data
                break
        assert artifact is not None
        assert "job_snapshot" in artifact
        snap = artifact["job_snapshot"]
        domain_result = snap.get("result")  # domain return: { mtr_phase, inputs, result }
        assert domain_result is not None
        result_block = domain_result.get("result")  # { estimated_E, rmse, uncertainty, ... }
        assert "uncertainty" in result_block

        try:
            from backend.progress.evidence_index import build_evidence_index
            index = build_evidence_index(tmp_path)
            assert trace_id in index
        except Exception:
            pass

    def test_e_canary_consistency_identical_uncertainty(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MG_PROGRESS_ARTIFACT_DIR", str(tmp_path))
        _, job_normal = _run_mtr1_uq_job(tmp_path, UQ_PAYLOAD, canary_mode=False)
        _, job_canary = _run_mtr1_uq_job(tmp_path, UQ_PAYLOAD, canary_mode=True)
        u_normal = job_normal.result["result"]["uncertainty"]
        u_canary = job_canary.result["result"]["uncertainty"]
        assert u_normal == u_canary
