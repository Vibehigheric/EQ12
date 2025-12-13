#!/usr/bin/env python3
"""
EQ12 Bulk XML Task Repair Utility

Scans C:\EQ12 for XML files, calls repair_task_xml_file on each,
and prints a comprehensive report of fixed/failed files.

Usage:
    python repair_all_tasks.py [--root PATH] [--pattern GLOB] [--dry-run]

Example:
    python repair_all_tasks.py --root "C:\EQ12" --pattern "**/*.xml"
    python repair_all_tasks.py --dry-run  # Preview only, no changes
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from eq12.parsing.normalize_xml import repair_task_xml_file
except ImportError:
    print("❌ Error: Cannot import eq12.parsing.normalize_xml")
    print("   Make sure you're running from the EQ12 root directory")
    print("   and the parsing module is properly installed.")
    sys.exit(1)


def scan_xml_files(root_path: Path, pattern: str = "**/*.xml") -> list[Path]:
    """Scan for XML files matching the pattern."""
    try:
        files = list(root_path.glob(pattern))
        # Filter out obvious non-task XML files
        exclude_patterns = [
            "**/logs/**",
            "**/.venv/**",
            "**/node_modules/**",
            "**/envs/**",
            "**/__pycache__/**",
        ]

        filtered_files = []
        for file in files:
            if not any(file.match(pattern) for pattern in exclude_patterns):
                filtered_files.append(file)

        return filtered_files
    except Exception as e:
        print(f"❌ Error scanning files: {e}")
        return []


def repair_single_file(file_path: Path, dry_run: bool = False) -> dict[str, Any]:
    """Repair a single XML file and return results."""
    result = {
        "file": str(file_path),
        "status": "unknown",
        "error": None,
        "size_before": 0,
        "size_after": 0,
        "output_path": None,
    }

    try:
        result["size_before"] = file_path.stat().st_size

        if dry_run:
            # Just validate, don't modify
            with open(file_path, encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Basic validation checks
            if not content.strip().startswith("<?xml"):
                result["status"] = "needs_repair"
                result["error"] = "Missing or invalid XML declaration"
            elif "&" in content and not all(
                entity in content for entity in ["&amp;", "&lt;", "&gt;"]
            ):
                result["status"] = "needs_repair"
                result["error"] = "Contains unescaped entities"
            else:
                result["status"] = "valid"

        else:
            # Perform actual repair
            repair_result = repair_task_xml_file(str(file_path))

            if repair_result.get("fixed"):
                result["status"] = "repaired"
                result["output_path"] = repair_result["path"]
                result["size_after"] = Path(repair_result["path"]).stat().st_size
            else:
                result["status"] = "valid"
                result["size_after"] = result["size_before"]

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def print_summary_table(results: list[dict[str, Any]]) -> None:
    """Print a formatted summary table."""
    from collections import Counter

    # Count by status
    status_counts = Counter(r["status"] for r in results)

    # Calculate totals
    total_files = len(results)
    total_size_before = sum(r["size_before"] for r in results)
    total_size_after = sum(r["size_after"] for r in results)

    print("\n" + "=" * 80)
    print("📊 EQ12 XML REPAIR SUMMARY")
    print("=" * 80)

    # Status breakdown
    print("\n📈 Status Breakdown:")
    for status, count in status_counts.most_common():
        emoji = {
            "valid": "✅",
            "repaired": "🔧",
            "needs_repair": "⚠️",
            "error": "❌",
            "unknown": "❓",
        }.get(status, "•")
        print(f"   {emoji} {status.replace('_', ' ').title()}: {count:,} files")

    # Size analysis
    print("\n📏 Size Analysis:")
    print(f"   Total Files: {total_files:,}")
    print(f"   Size Before: {total_size_before:,} bytes ({total_size_before / 1024:.1f} KB)")
    if total_size_after > 0:
        print(f"   Size After:  {total_size_after:,} bytes ({total_size_after / 1024:.1f} KB)")
        size_diff = total_size_after - total_size_before
        print(f"   Difference:  {size_diff:+,} bytes ({size_diff / 1024:+.1f} KB)")

    # Errors section
    errors = [r for r in results if r["status"] == "error"]
    if errors:
        print(f"\n❌ Errors ({len(errors)} files):")
        for result in errors[:5]:  # Show first 5 errors
            print(f"   • {Path(result['file']).name}: {result['error']}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more errors")

    # Repairs section
    repairs = [r for r in results if r["status"] == "repaired"]
    if repairs:
        print(f"\n🔧 Repairs ({len(repairs)} files):")
        for result in repairs[:5]:  # Show first 5 repairs
            print(f"   • {Path(result['file']).name} → {Path(result['output_path']).name}")
        if len(repairs) > 5:
            print(f"   ... and {len(repairs) - 5} more repairs")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="EQ12 Bulk XML Task Repair Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python repair_all_tasks.py --root "C:\\\\EQ12" --pattern "**/*.xml"
  python repair_all_tasks.py --dry-run  # Preview only
  python repair_all_tasks.py --pattern "configs/*.xml"  # Just configs
        """,
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=Path("C:/EQ12"),
        help="Root directory to scan (default: C:/EQ12)",
    )

    parser.add_argument(
        "--pattern",
        default="**/*.xml",
        help="Glob pattern for XML files (default: **/*.xml)",
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying files"
    )

    parser.add_argument("--output", type=Path, help="Save detailed results to JSON file")

    args = parser.parse_args()

    # Validate root path
    if not args.root.exists():
        print(f"❌ Error: Root path does not exist: {args.root}")
        sys.exit(1)

    print("🔍 EQ12 XML Task Repair Utility")
    print(f"   Root: {args.root}")
    print(f"   Pattern: {args.pattern}")
    print(f"   Mode: {'DRY RUN (preview only)' if args.dry_run else 'REPAIR (will modify files)'}")

    # Scan for XML files
    print("\n📁 Scanning for XML files...")
    xml_files = scan_xml_files(args.root, args.pattern)

    if not xml_files:
        print("   No XML files found matching pattern.")
        return

    print(f"   Found {len(xml_files):,} XML files")

    # Process files
    print("\n🔧 Processing files...")
    results = []

    for i, file_path in enumerate(xml_files, 1):
        print(f"   [{i:,}/{len(xml_files):,}] {file_path.name}", end="", flush=True)

        result = repair_single_file(file_path, args.dry_run)
        results.append(result)

        # Status indicator
        status_emoji = {
            "valid": "✅",
            "repaired": "🔧",
            "needs_repair": "⚠️",
            "error": "❌",
        }.get(result["status"], "❓")

        print(f" {status_emoji}")

    # Print summary
    print_summary_table(results)

    # Save detailed results if requested
    if args.output:
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "root_path": str(args.root),
            "pattern": args.pattern,
            "dry_run": args.dry_run,
            "total_files": len(results),
            "results": results,
        }

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\n📋 Detailed results saved to: {args.output}")

    print("\n✨ Task complete!")


if __name__ == "__main__":
    main()
