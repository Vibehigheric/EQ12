#!/usr/bin/env python3
"""
EQ12 Log to JSONL Converter

Parses EQ12 boundary logs and converts them to structured JSONL format
for analysis and monitoring.

Usage:
    python logs_to_jsonl.py [LOG_DIR] [--output OUTPUT.jsonl] [--filter PATTERN]

Examples:
    python logs_to_jsonl.py C:/EQ12/logs
    python logs_to_jsonl.py C:/EQ12/logs --filter "*boundary*"
    python logs_to_jsonl.py --output analysis.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

try:
    from eq12.parsing.logs import parse_eq12_errorboundary_log
except ImportError:
    print("❌ Error: Cannot import eq12.parsing.logs")
    print("   Make sure you're running from the EQ12 root directory")
    sys.exit(1)


def find_log_files(log_dir: Path, pattern: str = "*.log") -> list[Path]:
    """Find all log files matching the pattern."""
    try:
        files = list(log_dir.glob(pattern))
        # Sort by modification time (newest first)
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return files
    except Exception as e:
        print(f"❌ Error finding log files: {e}")
        return []


def parse_generic_log_line(line: str, file_path: Path) -> dict | None:
    """
    Parse a generic log line into structured format.

    Handles common EQ12 log formats:
    - [timestamp] - module - level - message
    - timestamp | level | message
    - ISO timestamp: message
    """
    line = line.strip()
    if not line:
        return None

    patterns = [
        # [2024-10-05 10:30:45] - eq12_bot - ERROR - Rate limit exceeded
        r"^\[(?P<timestamp>[^\]]+)\]\s*-\s*(?P<module>[^-]+?)\s*-\s*(?P<level>[^-]+?)\s*-\s*(?P<message>.+)$",
        # 2024-10-05T10:30:45 | ERROR | Rate limit exceeded
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T?\d{2}:\d{2}:\d{2}[^\|]*)\s*\|\s*(?P<level>[^\|]+?)\s*\|\s*(?P<message>.+)$",
        # 2024-10-05 10:30:45: Rate limit exceeded
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}[^:]*?):\s*(?P<message>.+)$",
        # Just message (use file timestamp)
        r"^(?P<message>.+)$",
    ]

    for pattern in patterns:
        match = re.match(pattern, line)
        if match:
            data = match.groupdict()

            # Normalize timestamp
            if "timestamp" in data:
                timestamp = data["timestamp"].strip()
                # Try to parse various formats
                for fmt in [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%d %H:%M:%S.%f",
                ]:
                    try:
                        parsed_ts = datetime.strptime(timestamp.split(".")[0], fmt)
                        data["timestamp"] = parsed_ts.isoformat()
                        break
                    except ValueError:
                        continue
                else:
                    # Fallback to file modification time
                    data["timestamp"] = datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).isoformat()
            else:
                data["timestamp"] = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()

            # Add metadata
            data["source_file"] = str(file_path.name)
            data["log_type"] = "generic"

            # Normalize level
            if "level" not in data:
                data["level"] = "INFO"
            data["level"] = data["level"].strip().upper()

            # Normalize module
            if "module" not in data:
                data["module"] = file_path.stem
            data["module"] = data["module"].strip()

            # Extract additional context from message
            message = data["message"]

            # Look for common patterns
            if "rate limit" in message.lower():
                data["error_type"] = "rate_limit"
            elif "quota" in message.lower():
                data["error_type"] = "quota_exceeded"
            elif "timeout" in message.lower():
                data["error_type"] = "timeout"
            elif "connection" in message.lower():
                data["error_type"] = "connection_error"
            elif any(word in message.lower() for word in ["error", "failed", "exception"]):
                data["error_type"] = "general_error"

            # Extract backoff/retry info
            backoff_match = re.search(
                r"(?:backoff|retry|wait)[\s:]*(\d+(?:\.\d+)?)\s*(?:sec|second|min|minute)?",
                message.lower(),
            )
            if backoff_match:
                data["backoff_seconds"] = float(backoff_match.group(1))

            # Extract attempt numbers
            attempt_match = re.search(r"attempt[\s:]*(\d+)", message.lower())
            if attempt_match:
                data["attempt_number"] = int(attempt_match.group(1))

            return data

    return None


def process_log_file(log_file: Path) -> Iterator[dict]:
    """Process a single log file and yield structured records."""
    try:
        # First try specialized EQ12 boundary log parser
        if "boundary" in log_file.name.lower() or "error" in log_file.name.lower():
            try:
                boundary_results = parse_eq12_errorboundary_log(str(log_file))
                if boundary_results:
                    for record in boundary_results:
                        yield record
                    return
            except Exception:
                pass  # Fall back to generic parser

        # Generic line-by-line parsing
        with open(log_file, encoding="utf-8", errors="replace") as f:
            line_number = 0
            for line in f:
                line_number += 1
                record = parse_generic_log_line(line, log_file)
                if record:
                    record["line_number"] = line_number
                    yield record

    except Exception as e:
        # Emit error record
        yield {
            "timestamp": datetime.now().isoformat(),
            "source_file": str(log_file.name),
            "log_type": "parser_error",
            "level": "ERROR",
            "message": f"Failed to parse log file: {e}",
            "error_type": "parser_error",
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="EQ12 Log to JSONL Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python logs_to_jsonl.py C:/EQ12/logs
  python logs_to_jsonl.py C:/EQ12/logs --filter "*boundary*"
  python logs_to_jsonl.py --output analysis.jsonl --filter "*.log"
        """,
    )

    parser.add_argument(
        "log_directory",
        nargs="?",
        type=Path,
        default=Path("C:/EQ12/logs"),
        help="Directory containing log files (default: C:/EQ12/logs)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSONL file (default: logs_YYYYMMDD_HHMMSS.jsonl)",
    )

    parser.add_argument("--filter", default="*.log", help="File pattern filter (default: *.log)")

    parser.add_argument("--limit", type=int, help="Maximum number of records to process")

    args = parser.parse_args()

    # Validate log directory
    if not args.log_directory.exists():
        print(f"❌ Error: Log directory does not exist: {args.log_directory}")
        sys.exit(1)

    # Set default output file
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = Path(f"logs_{timestamp}.jsonl")

    print("📚 EQ12 Log to JSONL Converter")
    print(f"   Source: {args.log_directory}")
    print(f"   Filter: {args.filter}")
    print(f"   Output: {args.output}")

    # Find log files
    print("\n🔍 Finding log files...")
    log_files = find_log_files(args.log_directory, args.filter)

    if not log_files:
        print("   No log files found matching pattern.")
        return

    print(f"   Found {len(log_files):,} log files")

    # Process files
    print("\n📝 Processing logs...")
    record_count = 0
    error_count = 0

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as jsonl_file:
        for i, log_file in enumerate(log_files, 1):
            print(f"   [{i:,}/{len(log_files):,}] {log_file.name}")

            file_records = 0
            for record in process_log_file(log_file):
                json_line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
                jsonl_file.write(json_line + "\n")

                record_count += 1
                file_records += 1

                if record.get("log_type") == "parser_error":
                    error_count += 1

                # Check limit
                if args.limit and record_count >= args.limit:
                    print(f"   Reached limit of {args.limit:,} records")
                    break

            print(f"      → {file_records:,} records")

            if args.limit and record_count >= args.limit:
                break

    # Summary
    print("\n📊 Conversion Summary:")
    print(f"   Files Processed: {i:,}")
    print(f"   Records Created: {record_count:,}")
    print(f"   Parse Errors: {error_count:,}")
    print(
        f"   Output Size: {args.output.stat().st_size:,} bytes ({args.output.stat().st_size / 1024:.1f} KB)"
    )

    print(f"\n✨ JSONL file created: {args.output}")

    # Show sample records
    if record_count > 0:
        print("\n📖 Sample Records:")
        with open(args.output, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 3:  # Show first 3 records
                    break
                record = json.loads(line)
                timestamp = record.get("timestamp", "N/A")[:19]
                level = record.get("level", "INFO")
                message = record.get("message", "")[:50] + (
                    "..." if len(record.get("message", "")) > 50 else ""
                )
                print(f"   {timestamp} | {level:<5} | {message}")


if __name__ == "__main__":
    main()
