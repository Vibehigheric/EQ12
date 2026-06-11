#!/usr/bin/env python3
"""
Release-safe daily betting slip export.

This workflow entrypoint never fabricates official betting recommendations.
It exports a daily manifest describing what source artifacts were found and
whether a release-grade slip board is available.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPORTS_DIR = REPO_ROOT / "exports"
LOGS_DIR = REPO_ROOT / "logs"
REPORTS_DIR = REPO_ROOT / "reports"
OUTPUT_DIR = EXPORTS_DIR / "betting_slips"


def find_existing_sources() -> list[str]:
    candidates: Iterable[Path] = (
        list(REPORTS_DIR.glob("*.json")) +
        list(REPORTS_DIR.glob("*.csv")) +
        list((REPO_ROOT / "outputs").glob("**/*.json")) +
        list((REPO_ROOT / "data").glob("**/*.csv"))
    )
    paths = []
    for path in candidates:
        if path.is_file():
            try:
                relative = path.relative_to(REPO_ROOT)
            except ValueError:
                relative = path
            paths.append(str(relative))
    return sorted(set(paths))[:100]


def build_manifest() -> dict:
    sources = find_existing_sources()
    release_grade_available = any("approved" in source.lower() for source in sources)
    warnings = []

    if not sources:
        warnings.append("No source artifacts were found; exported placeholder manifest only.")

    if not release_grade_available:
        warnings.append(
            "No approved release-grade betting slip source was found; no official card exported."
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "system_status": "OK",
        "release_grade_available": release_grade_available,
        "source_artifacts_found": len(sources),
        "source_artifacts": sources,
        "warnings": warnings,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest()
    stamp = datetime.now().strftime("%Y%m%d")
    manifest_path = OUTPUT_DIR / f"daily_betting_slip_manifest_{stamp}.json"
    summary_path = OUTPUT_DIR / f"daily_betting_slip_summary_{stamp}.md"

    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)

    lines = [
        "# EQ12 Daily Betting Slip Export",
        "",
        f"- Generated at: `{manifest['generated_at']}`",
        f"- Release-grade available: `{manifest['release_grade_available']}`",
        f"- Source artifacts found: `{manifest['source_artifacts_found']}`",
        "",
    ]

    if manifest["warnings"]:
        lines.append("## Warnings")
        lines.extend(f"- {warning}" for warning in manifest["warnings"])
        lines.append("")

    if manifest["source_artifacts"]:
        lines.append("## Source Artifacts")
        lines.extend(f"- `{source}`" for source in manifest["source_artifacts"])

    with open(summary_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")

    print(f"Manifest written to {manifest_path}")
    print(f"Summary written to {summary_path}")


if __name__ == "__main__":
    main()
