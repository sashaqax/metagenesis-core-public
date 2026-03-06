#!/usr/bin/env python3
"""
CERT-02 / PACK-02: Evidence-Inclusive Submission Pack + Semantic Verify.

Tests that:
1) Pack builder includes evidence bundles when --include-evidence is set
2) Pack contains pack_manifest.json, evidence_index.json, evidence/<CLAIM_ID>/{normal,canary}/*
3) mg verify passes for a valid evidence-inclusive pack
4) mg verify fails with clear message when semantic invariants are violated
   (e.g. run_artifact missing job_snapshot) even if integrity (sha/root_hash) passes
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

DATASET_RELPATH = "tests/fixtures/data01/al6061_stress_strain_sample.csv"


def _run_mtr1_evidence(source_reports_dir: Path, canary_mode: bool) -> None:
    """Run MTR-1 (normal or canary) with dataset + UQ; write progress_runs and ledger_snapshots."""
    import os

    from backend.ledger.ledger_store import LedgerStore
    from backend.progress.mtr1_calibration import JOB_KIND
    from backend.progress.runner import ProgressRunner
    from backend.progress.store import JobStore

    os.environ["MG_PROGRESS_ARTIFACT_DIR"] = str(source_reports_dir)
    source_reports_dir.mkdir(parents=True, exist_ok=True)
    job_store = JobStore()
    ledger_store = LedgerStore(file_path=str(source_reports_dir / "ledger.jsonl"))
    runner = ProgressRunner(job_store=job_store, ledger_store=ledger_store)
    payload = {
        "kind": JOB_KIND,
        "dataset_relpath": DATASET_RELPATH,
        "elastic_strain_max": 0.002,
        "uq_samples": 200,
        "uq_seed": 42,
    }
    job = runner.create_job(payload=payload)
    runner.run_job(job.job_id, canary_mode=canary_mode)


def _mg(args: list[str]) -> tuple[int, str]:
    """Run mg CLI; return (exit_code, combined stdout+stderr)."""
    result = subprocess.run(
        [sys.executable, str(_ROOT / "scripts" / "mg.py")] + args,
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
    )
    return result.returncode, (result.stdout or "") + (result.stderr or "")


def _build_pack_with_evidence(tmp_path: Path, source_reports_dir: Path, pack_out: Path) -> int:
    """Build pack with --include-evidence. Returns exit code."""
    return _mg([
        "pack", "build",
        "--output", str(pack_out),
        "--include-evidence",
        "--source-reports-dir", str(source_reports_dir),
    ])[0]


def _verify_pack(pack_dir: Path) -> tuple[int, str]:
    """Run mg verify --pack. Returns (exit_code, output)."""
    return _mg(["verify", "--pack", str(pack_dir)])


class TestCert02PackIncludesEvidenceAndSemanticVerify:
    """CERT-02 evidence-inclusive pack and semantic verification."""

    def test_pack_includes_evidence_and_verify_passes(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """Generate MTR-1 evidence, build pack with evidence, assert structure, verify passes."""
        monkeypatch.delenv("MG_PROGRESS_ARTIFACT_DIR", raising=False)

        source_reports_dir = tmp_path / "source_reports"
        pack_out = tmp_path / "pack_out"

        _run_mtr1_evidence(source_reports_dir, canary_mode=False)
        _run_mtr1_evidence(source_reports_dir, canary_mode=True)

        rc = _build_pack_with_evidence(tmp_path, source_reports_dir, pack_out)
        assert rc == 0, "Pack build should succeed"

        assert (pack_out / "pack_manifest.json").exists()
        assert (pack_out / "evidence_index.json").exists()
        assert (pack_out / "evidence" / "MTR-1" / "normal" / "run_artifact.json").exists()
        assert (pack_out / "evidence" / "MTR-1" / "normal" / "ledger_snapshot.jsonl").exists()
        assert (pack_out / "evidence" / "MTR-1" / "canary" / "run_artifact.json").exists()
        assert (pack_out / "evidence" / "MTR-1" / "canary" / "ledger_snapshot.jsonl").exists()

        vrc, vout = _verify_pack(pack_out)
        assert vrc == 0, f"mg verify should PASS: {vout}"
        assert "PASS" in vout

    def test_semantic_negative_missing_job_snapshot_fails_verify(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """Corrupt run_artifact (remove job_snapshot), update manifest so integrity passes; verify must FAIL."""
        monkeypatch.delenv("MG_PROGRESS_ARTIFACT_DIR", raising=False)

        source_reports_dir = tmp_path / "source_reports"
        pack_out = tmp_path / "pack_out"

        _run_mtr1_evidence(source_reports_dir, canary_mode=False)
        _run_mtr1_evidence(source_reports_dir, canary_mode=True)

        rc = _build_pack_with_evidence(tmp_path, source_reports_dir, pack_out)
        assert rc == 0

        run_artifact_path = pack_out / "evidence" / "MTR-1" / "normal" / "run_artifact.json"
        data = json.loads(run_artifact_path.read_text(encoding="utf-8"))
        assert "job_snapshot" in data
        del data["job_snapshot"]
        run_artifact_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        manifest_path = pack_out / "pack_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        run_rel = "evidence/MTR-1/normal/run_artifact.json"
        new_sha = hashlib.sha256(run_artifact_path.read_bytes()).hexdigest()
        for e in manifest["files"]:
            if e["relpath"] == run_rel:
                e["sha256"] = new_sha
                e["bytes"] = run_artifact_path.stat().st_size
                break

        lines = "\n".join(
            f"{e['relpath']}:{e['sha256']}"
            for e in sorted(manifest["files"], key=lambda x: x["relpath"])
        )
        manifest["root_hash"] = hashlib.sha256(lines.encode("utf-8")).hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        vrc, vout = _verify_pack(pack_out)
        assert vrc != 0, f"mg verify must FAIL on semantic violation: {vout}"
        assert "job_snapshot" in vout or "missing required key" in vout
