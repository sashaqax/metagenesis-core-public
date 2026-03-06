#!/usr/bin/env python3
"""
Evidence Index v1 tests.

Purpose: Validate build_evidence_index and evidence API contract.
"""

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from backend.progress.evidence_index import build_evidence_index


def _setup_evidence_artifacts(tmp_path: Path, trace_id: str) -> None:
    """Create progress_runs and ledger_snapshots with one run artifact and one snapshot."""
    reports = tmp_path / "reports"
    progress_runs = reports / "progress_runs"
    ledger_snapshots = reports / "ledger_snapshots"
    progress_runs.mkdir(parents=True)
    ledger_snapshots.mkdir(parents=True)

    run_artifact = {
        "trace_id": trace_id,
        "kind": "success",
        "job_id": "job_test1",
    }
    (progress_runs / f"job_test1_trace_{trace_id}_success.json").write_text(
        json.dumps(run_artifact)
    )

    snapshot_line = {"trace_id": trace_id, "action": "job_completed", "meta": {}}
    (ledger_snapshots / f"trace_{trace_id}.jsonl").write_text(
        json.dumps(snapshot_line) + "\n"
    )


class TestEvidenceIndex:
    """Evidence index build and mapping."""

    def test_build_evidence_index_returns_mapping_with_two_artifacts(
        self, tmp_path, monkeypatch
    ):
        trace_id = "trace_abc123"
        _setup_evidence_artifacts(tmp_path, trace_id)
        monkeypatch.setenv("MG_PROGRESS_ARTIFACT_DIR", str(tmp_path / "reports"))

        index = build_evidence_index()

        assert trace_id in index
        entry = index[trace_id]
        assert entry["trace_id"] == trace_id
        artifacts = entry["artifacts"]
        assert len(artifacts) == 2

        types = {a["type"] for a in artifacts}
        assert "run_artifact" in types
        assert "ledger_snapshot" in types
        for a in artifacts:
            assert "path" in a
            assert a["type"] in ("run_artifact", "ledger_snapshot")
            assert isinstance(a["size"], int)

    def test_build_evidence_index_empty_when_dirs_missing(self, tmp_path, monkeypatch):
        monkeypatch.setenv("MG_PROGRESS_ARTIFACT_DIR", str(tmp_path / "reports"))
        index = build_evidence_index()
        assert index == {}

    def test_build_evidence_index_returns_dict_for_nonexistent_dir(self):
        """Lightweight: build_evidence_index used by API returns dict (no server/import)."""
        result = build_evidence_index(Path("/nonexistent"))
        assert isinstance(result, dict)
        assert result == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
