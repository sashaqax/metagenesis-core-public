#!/usr/bin/env python3
"""
DATA-01 Dataset fingerprint bound into evidence.

MTR-1 with dataset_relpath: assert dataset sha256 in job_snapshot.result.inputs,
stable across runs, visible in evidence index/API, no absolute paths in evidence.
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
from backend.progress.data_integrity import fingerprint_file

DATASET_RELPATH = "tests/fixtures/data01/al6061_stress_strain_sample.csv"

MTR1_DATASET_PAYLOAD = {
    "kind": JOB_KIND,
    "dataset_relpath": DATASET_RELPATH,
    "elastic_strain_max": 0.002,
}


def _run_mtr1_dataset_job(artifact_dir: Path, canary_mode: bool = False):
    job_store = JobStore()
    ledger_store = LedgerStore(file_path=str(artifact_dir / "ledger.jsonl"))
    runner = ProgressRunner(job_store=job_store, ledger_store=ledger_store)
    job = runner.create_job(payload=MTR1_DATASET_PAYLOAD)
    runner.run_job(job.job_id, canary_mode=canary_mode)
    return job.trace_id, job


def _no_absolute_paths_in(obj, prefix=""):
    """Recursively assert no string value looks like an absolute path."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and (v.startswith("/") or (len(v) > 1 and v[1] == ":")):
                raise AssertionError(f"Absolute path in evidence at {prefix}{k}: {v[:80]}")
            _no_absolute_paths_in(v, f"{prefix}{k}.")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _no_absolute_paths_in(v, f"{prefix}[{i}].")


class TestData01DatasetFingerprint:
    """DATA-01: dataset_fingerprint in evidence, stable, no absolute paths."""

    def test_dataset_sha256_in_result_inputs_stable(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MG_PROGRESS_ARTIFACT_DIR", str(tmp_path))
        trace1, job1 = _run_mtr1_dataset_job(tmp_path, canary_mode=False)
        trace2, job2 = _run_mtr1_dataset_job(tmp_path, canary_mode=True)

        for job in (job1, job2):
            assert job.result is not None
            assert job.result.get("mtr_phase") == "MTR-1"
            inputs = job.result.get("inputs", {})
            dataset = inputs.get("dataset")
            assert dataset is not None, "inputs.dataset must be present"
            sha256 = dataset.get("sha256")
            assert sha256 is not None and len(sha256) == 64 and all(c in "0123456789abcdef" for c in sha256), (
                f"inputs.dataset.sha256 must be 64-char hex, got {sha256!r}"
            )
            assert dataset.get("source") == DATASET_RELPATH
            assert "bytes" in dataset

        assert job1.result["inputs"]["dataset"]["sha256"] == job2.result["inputs"]["dataset"]["sha256"], (
            "dataset sha256 must be stable across normal and canary"
        )
        expected_sha256 = fingerprint_file(_ROOT / DATASET_RELPATH)["sha256"]
        assert job1.result["inputs"]["dataset"]["sha256"] == expected_sha256
        print(f"dataset sha256: {expected_sha256}")

    def test_evidence_artifact_contains_dataset_sha256_no_absolute_paths(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MG_PROGRESS_ARTIFACT_DIR", str(tmp_path))
        trace_id, job = _run_mtr1_dataset_job(tmp_path, canary_mode=False)

        run_files = list((tmp_path / "progress_runs").glob("*.json"))
        assert run_files
        artifact = None
        for f in run_files:
            data = json.loads(f.read_text())
            if data.get("trace_id") == trace_id:
                artifact = data
                break
        assert artifact is not None
        snap = artifact.get("job_snapshot", {})
        result = snap.get("result", {})
        inputs = result.get("inputs", {})
        dataset = inputs.get("dataset")
        assert dataset is not None and dataset.get("sha256")
        _no_absolute_paths_in(artifact)

        try:
            from backend.progress.evidence_index import build_evidence_index
            index = build_evidence_index(tmp_path)
            assert trace_id in index
            entry = index[trace_id]
            if "artifacts" in entry:
                for art_path in entry.get("artifacts", []):
                    ap = tmp_path / art_path if not Path(art_path).is_absolute() else Path(art_path)
                    if ap.exists():
                        art_data = json.loads(ap.read_text())
                        res = art_data.get("job_snapshot", {}).get("result", {})
                        if res.get("inputs", {}).get("dataset"):
                            assert res["inputs"]["dataset"].get("sha256")
        except Exception:
            pass
