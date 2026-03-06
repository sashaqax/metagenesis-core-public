#!/usr/bin/env python3
"""
STEW-04 Submission Pack Builder Tests.

Build pack into pytest tmp_path; assert required files and content.
"""

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

import steward_submission_pack


class TestStew04SubmissionPack:
    """STEW-04: deterministic submission pack generator."""

    def test_build_pack_creates_required_files(self, tmp_path):
        """Build pack into tmp_path; assert overview, canonical snapshot, phase registry JSON, claims dir."""
        index_path = _ROOT / "reports/scientific_claim_index.md"
        canonical_path = _ROOT / "reports/canonical_state.md"
        phase_registry_path = _ROOT / "reports/phase_registry_v0_1.md"
        steward_submission_pack.build_submission_pack(
            tmp_path,
            index_path=index_path,
            canonical_path=canonical_path,
            phase_registry_path=phase_registry_path,
        )
        assert (tmp_path / "overview.md").exists()
        assert (tmp_path / "canonical_state_snapshot.md").exists()
        assert (tmp_path / "phase_registry_snapshot.json").exists()
        assert (tmp_path / "claims" / "dossier_MTR-1.md").exists()
        assert (tmp_path / "claims" / "dossier_MTR-2.md").exists()

    def test_overview_contains_mtr1_and_mtr2(self, tmp_path):
        """Overview must list MTR-1 and MTR-2."""
        index_path = _ROOT / "reports/scientific_claim_index.md"
        canonical_path = _ROOT / "reports/canonical_state.md"
        phase_registry_path = _ROOT / "reports/phase_registry_v0_1.md"
        steward_submission_pack.build_submission_pack(
            tmp_path,
            index_path=index_path,
            canonical_path=canonical_path,
            phase_registry_path=phase_registry_path,
        )
        overview = (tmp_path / "overview.md").read_text(encoding="utf-8")
        assert "MTR-1" in overview
        assert "MTR-2" in overview

    def test_dossiers_contain_required_fields(self, tmp_path):
        """Each dossier must contain job_kind, reproduction, job_snapshot.result, V&V/threshold, canary."""
        index_path = _ROOT / "reports/scientific_claim_index.md"
        canonical_path = _ROOT / "reports/canonical_state.md"
        phase_registry_path = _ROOT / "reports/phase_registry_v0_1.md"
        steward_submission_pack.build_submission_pack(
            tmp_path,
            index_path=index_path,
            canonical_path=canonical_path,
            phase_registry_path=phase_registry_path,
        )
        for name in ("dossier_MTR-1.md", "dossier_MTR-2.md"):
            path = tmp_path / "claims" / name
            assert path.exists(), f"Dossier {name} not created"
            text = path.read_text(encoding="utf-8")
            assert "job_kind" in text
            assert "reproduction" in text
            assert "job_snapshot.result" in text
            assert "V&V" in text or "threshold" in text.lower()
            assert "canary" in text.lower()
