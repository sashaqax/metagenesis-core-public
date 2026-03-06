#!/usr/bin/env python3
"""
STEW-07: General claim job_kind coverage.

Asserts that ALL claim job_kinds from scientific_claim_index.md
exist in runner dispatch (not only mtr*).
"""

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

import steward_audit


class TestStew07JobkindCoverage:
    """STEW-07 job_kind coverage."""

    def test_run_audit_returns_true(self) -> None:
        """run_audit() must pass."""
        assert steward_audit.run_audit() is True

    def test_claim_job_kinds_non_empty_and_subset_of_runner(self) -> None:
        """Extracted claim job_kinds set is non-empty and subset of runner dispatch kinds."""
        claim_kinds = steward_audit._extract_claim_index_job_kinds()
        runner_kinds = steward_audit._extract_runner_dispatch_kinds()
        assert len(claim_kinds) > 0, "Claim job_kinds must be non-empty"
        assert claim_kinds <= runner_kinds, (
            f"Claim job_kinds {sorted(claim_kinds)} must be subset of runner kinds {sorted(runner_kinds)}"
        )
