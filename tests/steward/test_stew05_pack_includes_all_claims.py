#!/usr/bin/env python3
"""
STEW-05 Packability Enforcement Invariant.

Every claim_id in reports/scientific_claim_index.md MUST have a dossier file
in the generated submission pack. CI-enforced via this test.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _parse_claim_ids_from_index(index_path: Path) -> list[str]:
    """Extract claim IDs from index: headings (## Claim: ID / ## Claim ID / ## ID) and table claim_id rows."""
    text = index_path.read_text(encoding="utf-8")
    claim_ids = []

    # (a) Headings: "## Claim: <ID>", "## Claim <ID>", or "## MTR-1" style
    for m in re.finditer(r"^##\s+(?:Claim:?\s+)?(MTR-\d+)\s*$", text, re.MULTILINE):
        claim_ids.append(m.group(1))

    # (b) Table rows containing claim_id: | **claim_id** | VALUE |
    for line in text.split("\n"):
        line = line.strip()
        if "claim_id" not in line or "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        for i, part in enumerate(parts):
            if "claim_id" in part.replace("*", "").lower():
                if i + 1 < len(parts):
                    value = parts[i + 1].strip()
                    if value and value not in claim_ids:
                        claim_ids.append(value)
                break

    return list(dict.fromkeys(claim_ids))


class TestStew05PackIncludesAllClaims:
    """STEW-05: submission pack must include a dossier for every claim in the index."""

    def test_every_claim_has_dossier_in_generated_pack(self, tmp_path):
        """Generate pack via subprocess; assert claims/ contains dossier_<CLAIM_ID>.md for each claim_id."""
        index_path = REPO_ROOT / "reports" / "scientific_claim_index.md"
        assert index_path.exists(), f"Index not found: {index_path}"

        claim_ids = _parse_claim_ids_from_index(index_path)
        if not claim_ids:
            pytest.fail(
                "STEW-05: Parsed 0 claim_ids from scientific_claim_index.md. "
                "Expect headings like '## MTR-1' or '## Claim: <ID>' or table rows with **claim_id**."
            )

        tmp_pack_dir = tmp_path / "pack"
        tmp_pack_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "steward_submission_pack.py"),
            "-o", str(tmp_pack_dir),
            "--index", str(index_path),
        ]
        subprocess.run(cmd, cwd=str(REPO_ROOT), check=True, capture_output=True, text=True)

        claims_dir = tmp_pack_dir / "claims"
        missing = []
        for cid in claim_ids:
            dossier_path = claims_dir / f"dossier_{cid}.md"
            if not dossier_path.exists():
                missing.append(f"dossier_{cid}.md")
            elif dossier_path.stat().st_size == 0:
                missing.append(f"dossier_{cid}.md (empty)")

        if missing:
            pytest.fail(
                f"STEW-05: Submission pack missing or empty dossiers for: {', '.join(missing)}. "
                f"Claim IDs from index: {claim_ids}."
            )

        # Expose for summary: claim_ids detected (asserted implicitly by no missing)
        assert claim_ids, "claim_ids list should be non-empty after parse"
