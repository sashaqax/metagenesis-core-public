#!/usr/bin/env python3
"""
STEW-03 Claim Dossier Builder Tests.

Run builder into a temporary directory; assert dossiers created with key fields.
"""

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

import steward_dossier


class TestSteward03DossierBuilder:
    """STEW-03: dossier builder."""

    def test_build_dossiers_creates_mtr1_and_mtr2(self, tmp_path):
        """Build into tmp dir; assert MTR-1 and MTR-2 dossiers exist."""
        index = _ROOT / "reports/scientific_claim_index.md"
        created = steward_dossier.build_dossiers(tmp_path, index_path=index)
        assert len(created) >= 2
        names = {p.name for p in created}
        assert "MTR-1.md" in names
        assert "MTR-2.md" in names

    def test_dossiers_contain_key_fields(self, tmp_path):
        """Each dossier must contain claim_id, job_kind, reproduction, evidence location, V&V, canary."""
        index = _ROOT / "reports/scientific_claim_index.md"
        steward_dossier.build_dossiers(tmp_path, index_path=index)
        for name in ("MTR-1.md", "MTR-2.md"):
            path = tmp_path / name
            assert path.exists(), f"Dossier {name} not created"
            text = path.read_text(encoding="utf-8")
            assert "claim_id" in text
            assert "job_kind" in text
            assert "reproduction" in text
            assert "job_snapshot.result" in text
            assert "V&V" in text or "threshold" in text.lower()
            assert "canary" in text.lower()
