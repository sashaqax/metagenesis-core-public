#!/usr/bin/env python3
"""
STEW-02 Claim Coverage Governance Tests.

Asserts steward audit passes (bidirectional runner <-> claim index coverage).
"""

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

import steward_audit


class TestSteward02ClaimCoverage:
    """STEW-02: claim coverage governance."""

    def test_steward_audit_returns_success(self):
        """run_audit() must return True (bidirectional coverage + canonical state)."""
        assert steward_audit.run_audit() is True
