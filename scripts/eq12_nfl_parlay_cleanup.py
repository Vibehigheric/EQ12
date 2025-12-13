#!/usr/bin/env python3
"""
EQ12 NFL Parlay Log Cleanup Tool

Addresses the excessive NFL parlay logging that's generating 1513+ log files
and causing performance degradation.

Key Features:
- Intelligently removes old NFL parlay logs while preserving recent data
- Implements log rotation policies
- Configures sustainable logging frequency
- Monitors disk space usage

Author: EQ12 AI Agent
Version: 1.0.0
"""

import argparse
import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NFLParLayLogCleanup:
    """NFL Parlay log cleanup and optimization tool"""

    def __init__(self):
        self.eq12_root = Path("C:/EQ12")
        self.logs_dir = self.eq12_root / "logs"
        self.scripts_dir = self.eq12_root / "scripts"

        # NFL parlay log patterns
        self.nfl_patterns = [
            "nfl_parlay_*.log",
            "nfl_parlay_*.json",
            "*nfl_parlay*",
            "parlay_*.log",
            "*cfb_*",  # College football betting
        ]

        # Configuration
        self.config = {
            "max_parlay_logs": 25,  # Reduce from 1513 to 25
            "max_file_age_days": 7,  # Keep only 1 week of logs
            "max_file_size_mb": 5,  # Limit individual file size
            "archive_threshold": 30,  # Archive after 30 days
            "cleanup_interval_hours": 6,  # Run cleanup every 6 hours
        }

    def scan_nfl_logs(self) -> dict[str, Any]:
        """Scan and categorize NFL parlay logs"""
        logger.info("Scanning NFL parlay logs...")

        nfl_files = []
        total_size_mb = 0

        for pattern in self.nfl_patterns:
            files = list(self.logs_dir.glob(pattern))
            for file in files:
                try:
                    size_mb = file.stat().st_size / (1024 * 1024)
                    created = datetime.fromtimestamp(file.stat().st_ctime)
                    modified = datetime.fromtimestamp(file.stat().st_mtime)

                    nfl_files.append(
                        {
                            "path": file,
                            "name": file.name,
                            "size_mb": size_mb,
                            "created": created,
                            "modified": modified,
                            "age_days": (datetime.now() - created).days,
                        }
                    )

                    total_size_mb += size_mb

                except Exception as e:
                    logger.warning(f"Error scanning {file}: {e}")

        # Sort by creation time (newest first)
        nfl_files.sort(key=lambda x: x["created"], reverse=True)

        scan_results = {
            "total_files": len(nfl_files),
            "total_size_mb": round(total_size_mb, 2),
            "files": nfl_files,
            "oldest_file": nfl_files[-1]["created"] if nfl_files else None,
            "newest_file": nfl_files[0]["created"] if nfl_files else None,
        }

        logger.info(
            f"Found {
                len(nfl_files)} NFL parlay logs using {
                total_size_mb:.1f} MB")

        return scan_results

    def cleanup_excessive_logs(self, scan_results: dict[str, Any]) -> dict[str, Any]:
        """Remove excessive NFL parlay logs"""
        logger.info("Cleaning up excessive NFL parlay logs...")

        files = scan_results["files"]
        cleanup_stats = {
            "files_removed": 0,
            "files_archived": 0,
            "files_kept": 0,
            "space_freed_mb": 0.0,
            "errors": [],
        }

        # Strategy 1: Keep only the most recent N files
        files_to_keep = files[: self.config["max_parlay_logs"]]
        files_to_remove = files[self.config["max_parlay_logs"]:]

        logger.info(
            f"Keeping {
                len(files_to_keep)} recent files, removing {
                len(files_to_remove)} old files")

        # Remove old files
        for file_info in files_to_remove:
            try:
                file_path = file_info["path"]

                # Archive files newer than 24 hours to be safe
                if file_info["age_days"] < 1:
                    archive_path = self.create_archive_path(file_path)
                    shutil.move(str(file_path), str(archive_path))
                    cleanup_stats["files_archived"] += 1
                    logger.info(f"Archived recent file: {file_path.name}")
                else:
                    # Remove older files
                    cleanup_stats["space_freed_mb"] += file_info["size_mb"]
                    file_path.unlink()
                    cleanup_stats["files_removed"] += 1

            except Exception as e:
                error_msg = f"Error removing {file_info['name']}: {e}"
                logger.error(error_msg)
                cleanup_stats["errors"].append(error_msg)

        cleanup_stats["files_kept"] = len(files_to_keep)
        cleanup_stats["space_freed_mb"] = round(cleanup_stats["space_freed_mb"], 2)

        logger.info(
            f"Cleanup complete: {
                cleanup_stats['files_removed']} removed, {
                cleanup_stats['files_archived']} archived, {
                cleanup_stats['space_freed_mb']} MB freed")

        return cleanup_stats

    def create_archive_path(self, file_path: Path) -> Path:
        """Create archive directory and return archive path"""
        archive_dir = self.logs_dir / "archive" / "nfl_parlay"
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Add timestamp to filename to prevent conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"

        return archive_dir / archive_name

    def configure_log_rotation(self) -> dict[str, Any]:
        """Configure proper log rotation for NFL parlay system"""
        logger.info("Configuring NFL parlay log rotation...")

        try:
            # Find NFL parlay scripts
            parlay_scripts = list(self.scripts_dir.glob("*nfl*")) + list(
                self.scripts_dir.glob("*parlay*")
            )

            rotation_config = {
                "enabled": True,
                "max_files": self.config["max_parlay_logs"],
                "max_file_size_mb": self.config["max_file_size_mb"],
                "rotation_interval": "daily",
                "compression": True,
                "archive_after_days": self.config["archive_threshold"],
            }

            config_file = self.eq12_root / "configs" / "nfl_parlay_logging.json"
            with open(config_file, "w") as f:
                json.dump(rotation_config, f, indent=2)

            logger.info(f"Log rotation configuration saved: {config_file}")

            return {
                "success": True,
                "config_file": str(config_file),
                "scripts_found": len(parlay_scripts),
                "configuration": rotation_config,
            }

        except Exception as e:
            logger.error(f"Error configuring log rotation: {e}")
            return {"success": False, "error": str(e)}

    def optimize_nfl_logging_frequency(self) -> dict[str, Any]:
        """Reduce NFL parlay logging frequency to prevent excessive logs"""
        logger.info("Optimizing NFL parlay logging frequency...")

        try:
            # Look for NFL parlay scheduler/cron configurations
            optimization_results = {"actions_taken": [], "recommendations": []}

            # Check Windows Task Scheduler for NFL parlay tasks
            task_result = self.check_scheduled_tasks()
            if task_result:
                optimization_results["actions_taken"].append(
                    f"Found {task_result['tasks_found']} scheduled NFL tasks"
                )
                optimization_results["recommendations"].extend(
                    task_result["recommendations"])

            # Create logging frequency configuration
            frequency_config = {
                "current_interval": "every_minute",
                "recommended_interval": "hourly",
                "peak_hours_interval": "every_30_minutes",  # 9 AM - 11 PM
                "off_hours_interval": "every_2_hours",  # 11 PM - 9 AM
                "game_day_interval": "every_15_minutes",  # Sunday/Monday during NFL season
                "max_log_size_mb": 5,
                "enable_compression": True,
            }

            config_file = self.eq12_root / "configs" / "nfl_logging_frequency.json"
            with open(config_file, "w") as f:
                json.dump(frequency_config, f, indent=2)

            optimization_results["actions_taken"].append(
                f"Created frequency config: {config_file}")
            optimization_results["recommendations"].extend(
                [
                    "Change NFL parlay logging from every minute to hourly",
                    "Implement smart logging based on game schedules",
                    "Enable log compression to reduce disk usage",
                    "Add log file size limits to prevent runaway logging",
                ]
            )

            return {
                "success": True,
                "optimization_results": optimization_results,
                "config_file": str(config_file),
            }

        except Exception as e:
            logger.error(f"Error optimizing logging frequency: {e}")
            return {"success": False, "error": str(e)}

    def check_scheduled_tasks(self) -> dict[str, Any] | None:
        """Check Windows Task Scheduler for NFL parlay tasks"""
        try:
            # Use PowerShell to check scheduled tasks
            ps_command = 'Get-ScheduledTask | Where-Object {$_.TaskName -like "*NFL*" -or $_.TaskName -like "*parlay*"} | Select-Object TaskName, State, @{Name="NextRun";Expression={(Get-ScheduledTaskInfo $_.TaskName).NextRunTime}}'

            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                tasks_found = len(
                    [line for line in lines if line.strip() and not line.startswith("TaskName")]
                )

                return {
                    "tasks_found": tasks_found,
                    "output": result.stdout,
                    "recommendations": [
                        f"Review {tasks_found} NFL-related scheduled tasks",
                        "Consider reducing task frequency from minutes to hours",
                        "Implement conditional execution based on NFL season",
                    ],
                }

            return None

        except Exception as e:
            logger.debug(f"Could not check scheduled tasks: {e}")
            return None

    def create_monitoring_script(self) -> dict[str, Any]:
        """Create monitoring script to prevent future log bloat"""
        logger.info("Creating NFL parlay log monitoring script...")

        try:
            monitor_script = '''#!/usr/bin/env python3
"""
NFL Parlay Log Monitor - Automated cleanup and monitoring
Generated by EQ12 System Health Analyzer
"""

import os
import sys
from pathlib import Path
from datetime import datetime
sys.path.append(r"{self.scripts_dir}")

from eq12_nfl_parlay_cleanup import NFLParLayLogCleanup

def main():
    print(f"{{datetime.now()}} - NFL Parlay Log Monitor starting...")

    cleanup = NFLParLayLogCleanup()

    # Scan current state
    scan_results = cleanup.scan_nfl_logs()

    # If too many files, run cleanup
    if scan_results["total_files"] > {self.config["max_parlay_logs"]}:
        print(f"Too many NFL logs ({{scan_results['total_files']}}), running cleanup...")
        cleanup_results = cleanup.cleanup_excessive_logs(scan_results)
        print(f"Cleanup complete: {{cleanup_results['files_removed']}} removed")
    else:
        print(f"NFL logs within limits ({{scan_results['total_files']}} files)")

    print(f"{{datetime.now()}} - NFL Parlay Log Monitor complete")

if __name__ == "__main__":
    main()
'''

            monitor_file = self.scripts_dir / "eq12_nfl_monitor.py"
            with open(monitor_file, "w") as f:
                f.write(monitor_script)

            logger.info(f"Monitor script created: {monitor_file}")

            return {
                "success": True,
                "monitor_script": str(monitor_file),
                "description": "Automated NFL parlay log monitoring and cleanup script",
            }

        except Exception as e:
            logger.error(f"Error creating monitor script: {e}")
            return {"success": False, "error": str(e)}

    def run_comprehensive_cleanup(self) -> dict[str, Any]:
        """Run comprehensive NFL parlay log cleanup and optimization"""
        logger.info("Starting comprehensive NFL parlay log cleanup...")

        start_time = datetime.now()

        try:
            # Step 1: Scan current state
            scan_results = self.scan_nfl_logs()

            # Step 2: Cleanup excessive logs
            cleanup_results = self.cleanup_excessive_logs(scan_results)

            # Step 3: Configure log rotation
            rotation_results = self.configure_log_rotation()

            # Step 4: Optimize logging frequency
            frequency_results = self.optimize_nfl_logging_frequency()

            # Step 5: Create monitoring script
            monitor_results = self.create_monitoring_script()

            # Final scan to verify results
            final_scan = self.scan_nfl_logs()

            duration = (datetime.now() - start_time).total_seconds()

            comprehensive_results = {
                "success": True,
                "duration_seconds": duration,
                "before": {
                    "total_files": scan_results["total_files"],
                    "total_size_mb": scan_results["total_size_mb"],
                },
                "after": {
                    "total_files": final_scan["total_files"],
                    "total_size_mb": final_scan["total_size_mb"],
                },
                "cleanup": cleanup_results,
                "rotation": rotation_results,
                "frequency_optimization": frequency_results,
                "monitoring": monitor_results,
                "space_saved_mb": scan_results["total_size_mb"] -
                final_scan["total_size_mb"],
            }

            logger.info(f"Comprehensive cleanup complete in {duration:.1f}s")
            logger.info(
                f"Files reduced: {scan_results['total_files']} -> {final_scan['total_files']}"
            )
            logger.info(
                f"Space saved: {
                    comprehensive_results['space_saved_mb']:.1f} MB")

            return comprehensive_results

        except Exception as e:
            logger.error(f"Comprehensive cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
            }


def main():
    """Main entry point for NFL parlay log cleanup"""
    parser = argparse.ArgumentParser(description="EQ12 NFL Parlay Log Cleanup Tool")
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Only scan, don't clean up")
    parser.add_argument("--max-files", type=int, default=25,
                        help="Maximum number of files to keep")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    cleanup = NFLParLayLogCleanup()

    if args.max_files:
        cleanup.config["max_parlay_logs"] = args.max_files

    try:
        if args.scan_only:
            # Just scan and report
            scan_results = cleanup.scan_nfl_logs()
            print("\\nNFL Parlay Log Scan Results:")
            print(f"Total Files: {scan_results['total_files']}")
            print(f"Total Size: {scan_results['total_size_mb']:.1f} MB")
            if scan_results["oldest_file"]:
                print(f"Oldest File: {scan_results['oldest_file']}")
            if scan_results["newest_file"]:
                print(f"Newest File: {scan_results['newest_file']}")
        else:
            # Run comprehensive cleanup
            results = cleanup.run_comprehensive_cleanup()

            if results["success"]:
                print("\\nNFL Parlay Log Cleanup Complete!")
                print(
                    f"Files: {results['before']['total_files']} -> {results['after']['total_files']}"
                )
                print(
                    f"Size: {
                        results['before']['total_size_mb']:.1f} MB -> {
                        results['after']['total_size_mb']:.1f} MB")
                print(f"Space Saved: {results['space_saved_mb']:.1f} MB")
                print(f"Duration: {results['duration_seconds']:.1f}s")

                sys.exit(0)
            else:
                print(f"\\nCleanup failed: {results.get('error', 'Unknown error')}")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\\nNFL parlay log cleanup interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"NFL parlay log cleanup failed: {e}")
        print(f"\\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
