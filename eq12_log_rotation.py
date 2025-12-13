#!/usr/bin/env python3
"""
EQ12 Log Rotation and Cleanup Utility

Automatically manages log files in the EQ12 system by:
- Rotating logs when they exceed size limits
- Archiving old logs with compression
- Cleaning up logs older than retention period
- Sending alerts for critical log events

Usage:
    python eq12_log_rotation.py --rotate-all
    python eq12_log_rotation.py --cleanup --days 30
    python eq12_log_rotation.py --check-errors
"""

import argparse
import gzip
import json
import logging
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/log_rotation.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EQ12LogRotator:
    """EQ12 Log rotation and management system."""

    def __init__(self, log_dir: str = "C:/EQ12/logs"):
        """Initialize the log rotator.

        Args:
            log_dir: Directory containing log files
        """
        self.log_dir = Path(log_dir)
        self.max_size_mb = 100  # Max file size in MB
        self.retention_days = 90  # Keep logs for 90 days
        self.error_patterns = ["ERROR", "CRITICAL", "FATAL", "Exception"]

    def rotate_logs(self) -> dict[str, Any]:
        """Rotate logs that exceed size limits.

        Returns:
            Dictionary with rotation results
        """
        results = {
            "rotated_files": [],
            "errors": [],
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            for log_file in self.log_dir.glob("*.log"):
                if log_file.stat().st_size > (self.max_size_mb * 1024 * 1024):
                    self._rotate_single_file(log_file, results)

        except Exception as e:
            logger.error(f"Error during log rotation: {e}")
            results["errors"].append(str(e))

        return results

    def _rotate_single_file(self, log_file: Path, results: dict[str, Any]) -> None:
        """Rotate a single log file.

        Args:
            log_file: Path to log file to rotate
            results: Results dictionary to update
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archived_name = f"{log_file.stem}_{timestamp}.log.gz"
            archived_path = self.log_dir / "archive" / archived_name

            # Create archive directory if it doesn't exist
            archived_path.parent.mkdir(exist_ok=True)

            # Compress and move the file
            with open(log_file, "rb") as f_in, gzip.open(archived_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

            # Clear the original file
            log_file.write_text("")

            results["rotated_files"].append(
                {
                    "original": str(log_file),
                    "archived": str(archived_path),
                    "size_mb": round(archived_path.stat().st_size / (1024 * 1024), 2),
                }
            )

            logger.info(f"Rotated {log_file.name} to {archived_name}")

        except Exception as e:
            logger.error(f"Failed to rotate {log_file}: {e}")
            results["errors"].append(f"{log_file.name}: {e!s}")

    def cleanup_old_logs(self, days: int | None = None) -> dict[str, Any]:
        """Clean up logs older than retention period.

        Args:
            days: Override default retention period

        Returns:
            Dictionary with cleanup results
        """
        retention_days = days or self.retention_days
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        results = {
            "deleted_files": [],
            "freed_space_mb": 0,
            "errors": [],
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            # Clean up archived logs
            archive_dir = self.log_dir / "archive"
            if archive_dir.exists():
                for archive_file in archive_dir.glob("*.gz"):
                    file_time = datetime.fromtimestamp(archive_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        size_mb = archive_file.stat().st_size / (1024 * 1024)
                        archive_file.unlink()

                        results["deleted_files"].append(str(archive_file))
                        results["freed_space_mb"] += size_mb

            # Clean up old regular log files
            for log_file in self.log_dir.glob("*.log.*"):
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    size_mb = log_file.stat().st_size / (1024 * 1024)
                    log_file.unlink()

                    results["deleted_files"].append(str(log_file))
                    results["freed_space_mb"] += size_mb

            results["freed_space_mb"] = round(results["freed_space_mb"], 2)
            logger.info(
                f"Cleaned up {len(results['deleted_files'])} old log files, "
                f"freed {results['freed_space_mb']} MB"
            )

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            results["errors"].append(str(e))

        return results

    def check_errors(self) -> dict[str, Any]:
        """Scan recent logs for error patterns.

        Returns:
            Dictionary with error analysis results
        """
        results = {
            "error_files": {},
            "total_errors": 0,
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            for log_file in self.log_dir.glob("*.log"):
                errors = self._scan_file_for_errors(log_file)
                if errors:
                    results["error_files"][str(log_file)] = errors
                    results["total_errors"] += len(errors)

            logger.info(
                f"Found {results['total_errors']} errors across {len(results['error_files'])} files"
            )

        except Exception as e:
            logger.error(f"Error during error checking: {e}")

        return results

    def _scan_file_for_errors(self, log_file: Path) -> list[dict[str, Any]]:
        """Scan a single log file for errors.

        Args:
            log_file: Path to log file to scan

        Returns:
            List of error entries found
        """
        errors = []
        try:
            with open(log_file, encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    for pattern in self.error_patterns:
                        if pattern in line.upper():
                            errors.append(
                                {
                                    "line_number": line_num,
                                    "pattern": pattern,
                                    # Truncate long lines
                                    "content": line.strip()[:200],
                                }
                            )
                            break

        except Exception as e:
            logger.warning(f"Could not scan {log_file}: {e}")

        return errors

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive log status report.

        Returns:
            Dictionary with complete log analysis
        """
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "log_directory": str(self.log_dir),
            "files": {},
            "summary": {
                "total_files": 0,
                "total_size_mb": 0,
                "largest_file": None,
                "oldest_file": None,
                "needs_rotation": [],
            },
        }

        try:
            largest_size = 0
            oldest_time = datetime.now()

            for log_file in self.log_dir.glob("*.log"):
                stat = log_file.stat()
                size_mb = stat.st_size / (1024 * 1024)
                mod_time = datetime.fromtimestamp(stat.st_mtime)

                report["files"][str(log_file)] = {
                    "size_mb": round(size_mb, 2),
                    "modified": mod_time.isoformat(),
                    "needs_rotation": size_mb > self.max_size_mb,
                }

                report["summary"]["total_files"] += 1
                report["summary"]["total_size_mb"] += size_mb

                if size_mb > largest_size:
                    largest_size = size_mb
                    report["summary"]["largest_file"] = str(log_file)

                if mod_time < oldest_time:
                    oldest_time = mod_time
                    report["summary"]["oldest_file"] = str(log_file)

                if size_mb > self.max_size_mb:
                    report["summary"]["needs_rotation"].append(str(log_file))

            report["summary"]["total_size_mb"] = round(report["summary"]["total_size_mb"], 2)

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            report["error"] = str(e)

        return report


def main():
    """Main entry point for the log rotation utility."""
    parser = argparse.ArgumentParser(description="EQ12 Log Rotation Utility")
    parser.add_argument(
        "--rotate-all",
        action="store_true",
        help="Rotate all logs exceeding size limits",
    )
    parser.add_argument("--cleanup", action="store_true", help="Clean up old log files")
    parser.add_argument(
        "--days", type=int, default=90, help="Retention period in days (default: 90)"
    )
    parser.add_argument("--check-errors", action="store_true", help="Scan logs for error patterns")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive log report")
    parser.add_argument(
        "--log-dir",
        default="C:/EQ12/logs",
        help="Log directory path (default: C:/EQ12/logs)",
    )

    args = parser.parse_args()

    if not any([args.rotate_all, args.cleanup, args.check_errors, args.report]):
        parser.print_help()
        return 1

    rotator = EQ12LogRotator(args.log_dir)

    try:
        results = {}

        if args.rotate_all:
            logger.info("Starting log rotation...")
            results["rotation"] = rotator.rotate_logs()

        if args.cleanup:
            logger.info(f"Starting cleanup (retention: {args.days} days)...")
            results["cleanup"] = rotator.cleanup_old_logs(args.days)

        if args.check_errors:
            logger.info("Scanning for errors...")
            results["errors"] = rotator.check_errors()

        if args.report:
            logger.info("Generating report...")
            results["report"] = rotator.generate_report()

        # Save results to JSON file
        output_file = (
            Path(args.log_dir) / f"log_management_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results saved to {output_file}")
        print(json.dumps(results, indent=2))

        return 0

    except Exception as e:
        logger.error(f"Log management failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
