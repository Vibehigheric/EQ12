"""
EQ12 Log Parser

Specialized parsing for EQ12 boundary logs, error tracking, and structured logging.
Converts various log formats to JSONL for analysis and monitoring.

Key functions:
- parse_eq12_errorboundary_log(): Parse boundary/error logs to JSONL
- parse_eq12_general_log(): Parse standard EQ12 logs
- extract_error_patterns(): Extract rate limits, quotas, backoff timing
- log_to_jsonl(): Convert any log format to JSONL
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

# Common EQ12 log patterns
LOG_PATTERNS = {
    "boundary": re.compile(
        r"(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s*"
        r".*?attempt[_\s]*(?P<attempt_id>\d+)\s*"
        r".*?(?P<error_type>rate_limit|quota_exhausted|timeout|connection_error)\s*"
        r".*?(?:backoff[_\s]*(?P<backoff>\d+)|wait[_\s]*(?P<wait>\d+))?",
        re.IGNORECASE,
    ),
    "standard": re.compile(
        r"^\[?(?P<timestamp>[^\]]+)\]?\s*[-:]?\s*"
        r"(?P<module>[^-:]+)\s*[-:]?\s*"
        r"(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)\s*[-:]?\s*"
        r"(?P<message>.*)",
        re.IGNORECASE,
    ),
    "error": re.compile(
        r"(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\s*"
        r".*?(?P<error_code>E\d{3,4}|HTTP[_\s]*\d{3})\s*"
        r".*?(?P<description>.*)",
        re.IGNORECASE,
    ),
    "performance": re.compile(
        r"(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\s*"
        r".*?(?P<operation>[^:]+):\s*"
        r"(?P<duration>\d+\.?\d*)(?P<unit>ms|s)\s*"
        r"(?:.*?(?P<details>.*))?",
        re.IGNORECASE,
    ),
}


def _parse_timestamp(timestamp_str: str) -> str:
    """
    Parse various timestamp formats to ISO format.

    Args:
        timestamp_str: Raw timestamp string

    Returns:
        ISO formatted timestamp string
    """
    # Common timestamp formats in EQ12 logs
    formats = [
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]

    # Clean up the timestamp string
    cleaned = timestamp_str.strip().replace("[", "").replace("]", "")

    for fmt in formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.isoformat()
        except ValueError:
            continue

    # If all parsing fails, return cleaned string
    return cleaned


def parse_eq12_errorboundary_log(
    log_path: str | Path, output_path: str | Path | None = None
) -> list[dict[str, Any]]:
    """
    Parse EQ12 boundary/error logs and extract structured data.

    Captures:
    - Attempt IDs
    - Error types (rate_limit, quota_exhausted, timeout, etc.)
    - Backoff/wait times
    - Timestamps
    - Error context

    Args:
        log_path: Path to log file
        output_path: Optional JSONL output path

    Returns:
        List of parsed log entries

    Example:
        entries = parse_eq12_errorboundary_log("logs/boundary.log")
        # [{"timestamp": "2025-10-05T10:30:45", "attempt_id": 3,
        #   "error_type": "rate_limit", "backoff_seconds": 30, ...}]
    """
    log_file = Path(log_path)

    if not log_file.exists():
        raise FileNotFoundError(f"Log file not found: {log_file}")

    entries = []

    try:
        content = log_file.read_text(encoding="utf-8", errors="replace")
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Try boundary pattern first
            match = LOG_PATTERNS["boundary"].search(line)
            if match:
                groups = match.groupdict()

                entry = {
                    "line_number": line_num,
                    "timestamp": _parse_timestamp(groups["timestamp"]),
                    "attempt_id": int(groups["attempt_id"]),
                    "error_type": groups["error_type"].lower(),
                    "raw_line": line,
                }

                # Add backoff time if present
                if groups["backoff"]:
                    entry["backoff_seconds"] = int(groups["backoff"])
                elif groups["wait"]:
                    entry["backoff_seconds"] = int(groups["wait"])

                entries.append(entry)
                continue

            # Try error pattern
            match = LOG_PATTERNS["error"].search(line)
            if match:
                groups = match.groupdict()

                entry = {
                    "line_number": line_num,
                    "timestamp": _parse_timestamp(groups["timestamp"]),
                    "error_code": groups["error_code"],
                    "description": groups["description"].strip(),
                    "raw_line": line,
                }

                entries.append(entry)
                continue

            # Try standard log pattern as fallback
            match = LOG_PATTERNS["standard"].search(line)
            if match:
                groups = match.groupdict()

                entry = {
                    "line_number": line_num,
                    "timestamp": _parse_timestamp(groups["timestamp"]),
                    "module": groups["module"].strip(),
                    "level": groups["level"].upper(),
                    "message": groups["message"].strip(),
                    "raw_line": line,
                }

                entries.append(entry)

    except Exception as e:
        raise RuntimeError(f"Error parsing log file: {e}")

    # Write JSONL output if requested
    if output_path:
        output_file = Path(output_path)
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for entry in entries:
                    f.write(json.dumps(entry, default=str) + "\n")
        except Exception as e:
            raise RuntimeError(f"Error writing output file: {e}")

    return entries


def extract_error_patterns(log_entries: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Extract error patterns and statistics from parsed log entries.

    Args:
        log_entries: Parsed log entries from parse_eq12_errorboundary_log

    Returns:
        Statistics and patterns dictionary
    """
    stats = {
        "total_entries": len(log_entries),
        "error_types": {},
        "attempt_counts": {},
        "backoff_times": [],
        "time_range": {"start": None, "end": None},
        "error_frequency": {},
    }

    for entry in log_entries:
        # Count error types
        error_type = entry.get("error_type", "unknown")
        stats["error_types"][error_type] = stats["error_types"].get(error_type, 0) + 1

        # Count attempts
        attempt_id = entry.get("attempt_id")
        if attempt_id:
            stats["attempt_counts"][attempt_id] = stats["attempt_counts"].get(attempt_id, 0) + 1

        # Collect backoff times
        backoff = entry.get("backoff_seconds")
        if backoff:
            stats["backoff_times"].append(backoff)

        # Track time range
        timestamp = entry.get("timestamp")
        if timestamp:
            if stats["time_range"]["start"] is None or timestamp < stats["time_range"]["start"]:
                stats["time_range"]["start"] = timestamp
            if stats["time_range"]["end"] is None or timestamp > stats["time_range"]["end"]:
                stats["time_range"]["end"] = timestamp

    # Calculate backoff statistics
    if stats["backoff_times"]:
        stats["backoff_stats"] = {
            "min": min(stats["backoff_times"]),
            "max": max(stats["backoff_times"]),
            "avg": sum(stats["backoff_times"]) / len(stats["backoff_times"]),
        }

    return stats


def log_to_jsonl(log_path: str | Path, output_path: str | Path, log_type: str = "auto") -> int:
    """
    Convert any log format to JSONL.

    Args:
        log_path: Input log file path
        output_path: Output JSONL file path
        log_type: 'auto', 'boundary', 'standard', or 'general'

    Returns:
        Number of entries processed
    """
    if log_type == "auto":
        # Try to detect log type from content sample
        log_file = Path(log_path)
        sample = log_file.read_text(encoding="utf-8", errors="replace")[:2000]

        if "attempt" in sample.lower() and any(
            term in sample.lower() for term in ["rate_limit", "quota", "backoff"]
        ):
            log_type = "boundary"
        else:
            log_type = "standard"

    # Parse based on detected/specified type
    if log_type == "boundary":
        entries = parse_eq12_errorboundary_log(log_path, output_path)
    else:
        # Use the ingest_any module for general parsing
        from .ingest_any import load_any

        result = load_any(log_path)
        if isinstance(result, dict) and "log_entries" in result:
            entries = result["log_entries"]
        else:
            # Fallback: treat as text and split by lines
            content = Path(log_path).read_text(encoding="utf-8", errors="replace")
            entries = [
                {"line_number": i, "content": line.strip()}
                for i, line in enumerate(content.split("\n"), 1)
                if line.strip()
            ]

        # Write JSONL
        with open(output_path, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry, default=str) + "\n")

    return len(entries)


def parse_performance_log(log_path: str | Path) -> list[dict[str, Any]]:
    """
    Parse performance/timing logs for operation analysis.

    Args:
        log_path: Path to performance log file

    Returns:
        List of performance entries with timing data
    """
    log_file = Path(log_path)
    entries = []

    content = log_file.read_text(encoding="utf-8", errors="replace")

    for line_num, line in enumerate(content.split("\n"), 1):
        line = line.strip()
        if not line:
            continue

        match = LOG_PATTERNS["performance"].search(line)
        if match:
            groups = match.groupdict()

            duration = float(groups["duration"])
            unit = groups["unit"].lower()

            # Normalize to milliseconds
            duration_ms = duration * 1000 if unit == "s" else duration

            entry = {
                "line_number": line_num,
                "timestamp": _parse_timestamp(groups["timestamp"]),
                "operation": groups["operation"].strip(),
                "duration_ms": duration_ms,
                "duration_original": f"{groups['duration']}{groups['unit']}",
                "details": groups.get("details", "").strip() or None,
                "raw_line": line,
            }

            entries.append(entry)

    return entries


# CLI entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python logs.py <command> <log_file> [output_file]")
        print("Commands:")
        print("  boundary - Parse boundary/error logs")
        print("  jsonl - Convert to JSONL format")
        print("  stats - Show error statistics")
        print("  perf - Parse performance logs")
        sys.exit(1)

    command = sys.argv[1]
    log_file = sys.argv[2] if len(sys.argv) > 2 else None
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    if not log_file:
        print("Error: Log file path required")
        sys.exit(1)

    try:
        if command == "boundary":
            entries = parse_eq12_errorboundary_log(log_file, output_file)
            print(f"✅ Parsed {len(entries)} boundary log entries")

        elif command == "jsonl":
            if not output_file:
                output_file = Path(log_file).with_suffix(".jsonl")
            count = log_to_jsonl(log_file, output_file)
            print(f"✅ Converted {count} entries to JSONL: {output_file}")

        elif command == "stats":
            entries = parse_eq12_errorboundary_log(log_file)
            stats = extract_error_patterns(entries)
            print(json.dumps(stats, indent=2, default=str))

        elif command == "perf":
            entries = parse_performance_log(log_file)
            if output_file:
                with open(output_file, "w") as f:
                    json.dump(entries, f, indent=2, default=str)
            print(f"✅ Parsed {len(entries)} performance log entries")

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
