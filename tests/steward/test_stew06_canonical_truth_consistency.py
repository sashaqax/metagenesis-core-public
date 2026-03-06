#!/usr/bin/env python3
"""
STEW-06 Canonical Truth Consistency Tests.

Enforce canonical_state current_claims_list matches scientific_claim_index claim_ids.
"""

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

import steward_audit


class TestStew06CanonicalTruthConsistency:
    """STEW-06: canonical_state and claim index must match."""

    def test_run_audit_returns_true(self):
        """run_audit() must succeed when canonical sync passes."""
        assert steward_audit.run_audit() is True

    def test_canonical_includes_mtr3_and_sets_match(self):
        """Direct extractor check: MTR-3 in canonical list; canonical set == claim_index set."""
        canonical_path = _ROOT / "reports" / "canonical_state.md"
        index_path = _ROOT / "reports" / "scientific_claim_index.md"
        canonical_ids = steward_audit._extract_canonical_claim_ids(canonical_path)
        index_ids = steward_audit._extract_claim_index_claim_ids(index_path)
        assert "MTR-3" in canonical_ids
        assert set(canonical_ids) == set(index_ids)
