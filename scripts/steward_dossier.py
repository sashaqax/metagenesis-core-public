#!/usr/bin/env python3
"""
STEW-03 Claim Dossier Builder v0.1

Reads reports/scientific_claim_index.md and produces one dossier per claim
in a target output directory. No network. No LLM. No new deps.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = REPO_ROOT / "reports/scientific_claim_index.md"


def _read(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _parse_claim_sections(text: str) -> list[dict]:
    """Split by ## headings and parse each claim's table into a dict."""
    sections = re.split(r"\n##\s+", text)
    claims = []
    for block in sections:
        block = block.strip()
        if not block or "**claim_id**" not in block:
            continue
        data = {}
        for line in block.split("\n"):
            line = line.strip()
            if not line.startswith("|") or line == "|-------|--------|" or "| Field |" in line:
                continue
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                key = re.sub(r"\*+", "", parts[0]).strip().lower().replace(" ", "_").replace("&", "and")
                key = re.sub(r"[^\w]", "_", key).strip("_")
                value = parts[1]
                data[key] = value
                if "claim_id" in key or parts[0].strip() == "**claim_id**":
                    data["claim_id"] = value
        claim_id = data.get("claim_id", "").strip()
        if claim_id:
            if "claim_id" not in data:
                data["claim_id"] = claim_id
            claims.append(data)
    return claims


def _dossier_content(claim: dict) -> str:
    """Generate deterministic dossier markdown for one claim."""
    claim_id = claim.get("claim_id", "")
    job_kind = claim.get("job_kind", "")
    reproduction = claim.get("reproduction", "")
    vv = claim.get("vandv_thresholds", claim.get("vv_thresholds", ""))
    canary = claim.get("notes__canary_vs_normal", claim.get("notes_canary_vs_normal", ""))
    if not vv:
        for k, v in claim.items():
            if "threshold" in k.lower():
                vv = v
                break
    if not canary:
        for k, v in claim.items():
            if "canary" in k.lower():
                canary = v
                break
    lines = [
        f"# Claim Dossier: {claim_id}",
        "",
        "| Field | Value |",
        "|-------|--------|",
        f"| **claim_id** | {claim_id} |",
        f"| **job_kind** | {job_kind} |",
        f"| **reproduction** | {reproduction} |",
        "| **evidence location** | job_snapshot.result |",
        f"| **V&V thresholds** | {vv} |",
        f"| **canary vs normal** | {canary} |",
        "",
    ]
    return "\n".join(lines)


def build_dossiers(output_dir: Path, index_path: Path = None) -> list[Path]:
    """
    Read scientific claim index and write one dossier per claim into output_dir.
    Returns list of created dossier paths.
    """
    path = index_path or INDEX_PATH
    if not path.exists():
        raise FileNotFoundError(f"Claim index not found: {path}")
    text = _read(path)
    claims = _parse_claim_sections(text)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    created = []
    for claim in claims:
        claim_id = claim.get("claim_id", "").strip()
        if not claim_id:
            continue
        safe_name = re.sub(r"[^\w\-]", "_", claim_id)
        out_file = output_dir / f"{safe_name}.md"
        out_file.write_text(_dossier_content(claim), encoding="utf-8")
        created.append(out_file)
    return created


def main():
    import argparse
    p = argparse.ArgumentParser(description="STEW-03 Claim Dossier Builder")
    p.add_argument("--output", "-o", type=Path, default=REPO_ROOT / "reports/dossiers", help="Output directory")
    p.add_argument("--index", type=Path, default=INDEX_PATH, help="Scientific claim index path")
    args = p.parse_args()
    created = build_dossiers(args.output, args.index)
    print(f"Built {len(created)} dossiers: {[str(p) for p in created]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
