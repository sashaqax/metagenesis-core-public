#!/usr/bin/env python3
"""
STEW-01 Steward Audit Tests

Runs steward_audit in-process; asserts success.
"""

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

import steward_audit


class TestStewardAudit:
    """STEW-01 steward audit in-process."""

    def test_steward_audit_returns_success(self):
        """Run steward_audit via import; assert it returns True."""
        assert steward_audit.run_audit() is True
