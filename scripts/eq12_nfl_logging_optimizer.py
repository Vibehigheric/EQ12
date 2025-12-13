#!/usr/bin/env python3
"""
EQ12 NFL Parlay Logging Frequency Optimizer

Implements intelligent logging frequency based on time of day and NFL game schedule
to prevent the excessive logging that was creating 1,513+ log files.

Key Features:
- Hourly logging during normal hours (was every minute)
- 30-minute intervals during peak hours (9 AM - 11 PM)
- 2-hour intervals during off hours (11 PM - 9 AM)
- 15-minute intervals on NFL game days (Sunday/Monday)
- Automatic log rotation and compression
- Scheduled task management for Windows

Author: EQ12 AI Agent
Version: 1.0.0
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/nfl_logging_optimizer.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class NFLLoggingFrequencyOptimizer:
    """Optimizes NFL parlay logging frequency to prevent excessive log generation"""

    def __init__(self):
        self.eq12_root = Path("C:/EQ12")
        self.configs_dir = self.eq12_root / "configs"
        self.logs_dir = self.eq12_root / "logs"

        # Load frequency configuration
        self.config_file = self.configs_dir / "nfl_logging_frequency.json"
        self.load_frequency_config()

        # NFL game days (typically Sunday and Monday)
        self.nfl_game_days = [6, 0]  # Sunday=6, Monday=0 in Python weekday()

    def load_frequency_config(self) -> dict[str, Any]:
        """Load logging frequency configuration"""
        try:
            with open(self.config_file) as f:
                self.frequency_config = json.load(f)

            logger.info(f"Loaded frequency config: {self.config_file}")
            return self.frequency_config

        except Exception as e:
            logger.error(f"Error loading frequency config: {e}")
            # Create default config
            self.frequency_config = {
                "current_interval": "hourly",
                "recommended_interval": "hourly",
                "peak_hours_interval": "every_30_minutes",
                "off_hours_interval": "every_2_hours",
                "game_day_interval": "every_15_minutes",
                "max_log_size_mb": 5,
                "enable_compression": True,
            }
            return self.frequency_config

    def determine_optimal_interval(self) -> dict[str, Any]:
        """Determine optimal logging interval based on current time and NFL schedule"""
        now = datetime.now()
        current_hour = now.hour
        current_weekday = now.weekday()

        # Check if it's an NFL game day
        is_game_day = current_weekday in self.nfl_game_days

        # Determine time period
        is_peak_hours = 9 <= current_hour <= 23  # 9 AM to 11 PM
        is_off_hours = current_hour < 9 or current_hour > 23  # 11 PM to 9 AM

        # Determine optimal interval
        if is_game_day and is_peak_hours:
            interval = self.frequency_config["game_day_interval"]
            interval_minutes = 15
            reason = "NFL game day during peak hours"
        elif is_peak_hours:
            interval = self.frequency_config["peak_hours_interval"]
            interval_minutes = 30
            reason = "Peak hours (9 AM - 11 PM)"
        elif is_off_hours:
            interval = self.frequency_config["off_hours_interval"]
            interval_minutes = 120
            reason = "Off hours (11 PM - 9 AM)"
        else:
            interval = self.frequency_config["recommended_interval"]
            interval_minutes = 60
            reason = "Default hourly interval"

        return {
            "interval": interval,
            "interval_minutes": interval_minutes,
            "reason": reason,
            "is_game_day": is_game_day,
            "is_peak_hours": is_peak_hours,
            "current_time": now.isoformat(),
        }

    def update_scheduled_tasks(self) -> dict[str, Any]:
        """Update Windows scheduled tasks for NFL parlay logging"""
        logger.info("Updating NFL parlay logging scheduled tasks...")

        try:
            # Check for existing NFL parlay tasks
            existing_tasks = self.get_nfl_scheduled_tasks()

            optimal_config = self.determine_optimal_interval()
            interval_minutes = optimal_config["interval_minutes"]

            updated_tasks = []

            for task_name in existing_tasks:
                try:
                    # Update task frequency
                    update_result = self.update_task_frequency(
                        task_name, interval_minutes)
                    if update_result["success"]:
                        updated_tasks.append(task_name)
                        logger.info(
                            f"Updated task {task_name} to {interval_minutes} minute interval")
                    else:
                        logger.warning(
                            f"Failed to update task {task_name}: {
                                update_result.get('error')}")

                except Exception as e:
                    logger.error(f"Error updating task {task_name}: {e}")

            # Create new optimized task if none exist
            if not existing_tasks:
                create_result = self.create_optimized_task(interval_minutes)
                if create_result["success"]:
                    updated_tasks.append(create_result["task_name"])

            return {
                "success": True,
                "updated_tasks": updated_tasks,
                "total_tasks_updated": len(updated_tasks),
                "optimal_config": optimal_config,
                "description": f"Updated {
                    len(updated_tasks)} NFL parlay tasks to {interval_minutes} minute intervals",
            }

        except Exception as e:
            logger.error(f"Error updating scheduled tasks: {e}")
            return {
                "success": False,
                "error": str(e),
                "description": f"Failed to update scheduled tasks: {e}",
            }

    def get_nfl_scheduled_tasks(self) -> list:
        """Get list of NFL parlay related scheduled tasks"""
        try:
            # PowerShell command to find NFL-related tasks
            ps_command = """
Get-ScheduledTask | Where-Object {
    $_.TaskName -like "*NFL*" -or
    $_.TaskName -like "*parlay*" -or
    $_.TaskName -like "*EQ12*parlay*" -or
    $_.Actions.Execute -like "*nfl*" -or
    $_.Actions.Arguments -like "*nfl*"
} | Select-Object -ExpandProperty TaskName
"""

            result = subprocess.run(
                ["powershell", "-Command", ps_command], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0 and result.stdout.strip():
                tasks = [line.strip()
                         for line in result.stdout.strip().split("\n") if line.strip()]
                logger.info(f"Found {len(tasks)} NFL-related scheduled tasks")
                return tasks
            else:
                logger.info("No NFL-related scheduled tasks found")
                return []

        except Exception as e:
            logger.error(f"Error getting NFL scheduled tasks: {e}")
            return []

    def update_task_frequency(self, task_name: str,
                              interval_minutes: int) -> dict[str, Any]:
        """Update the frequency of a specific scheduled task"""
        try:
            # PowerShell command to update task trigger
            ps_command = """
$Task = Get-ScheduledTask -TaskName "{task_name}"
$NewTrigger = (
    New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes {interval_minutes}) -RepetitionDuration (New-TimeSpan -Days 365) -At (Get-Date)
)
Set-ScheduledTask -TaskName "{task_name}" -Trigger $NewTrigger
Write-Output "Task updated successfully"
"""

            result = subprocess.run(
                ["powershell", "-Command", ps_command], capture_output=True, text=True, timeout=30
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if result.stderr else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_optimized_task(self, interval_minutes: int) -> dict[str, Any]:
        """Create new optimized NFL parlay logging task"""
        try:
            task_name = "EQ12NFLParlay_Optimized"
            self.eq12_root / "scripts" / "eq12_nfl_monitor.py"

            # Create PowerShell script for the task
            ps_command = """
$Action = New-ScheduledTaskAction -Execute "python" -Argument '"{script_path}"'
$Trigger = (
    New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes {interval_minutes}) -RepetitionDuration (New-TimeSpan -Days 365) -At (Get-Date)
)
$Settings = (
    New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType InteractiveToken
Register-ScheduledTask -TaskName "{task_name}" -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "EQ12 NFL Parlay Optimized Logging - {interval_minutes} minute intervals"
Write-Output "Task created successfully"
"""

            result = subprocess.run(
                ["powershell", "-Command", ps_command], capture_output=True, text=True, timeout=30
            )

            return {
                "success": result.returncode == 0,
                "task_name": task_name,
                "interval_minutes": interval_minutes,
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if result.stderr else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def implement_log_rotation(self) -> dict[str, Any]:
        """Implement log rotation for NFL parlay logs"""
        logger.info("Implementing NFL parlay log rotation...")

        try:
            rotation_config = {
                "enabled": True,
                "max_files_per_type": 25,
                "max_file_size_mb": self.frequency_config["max_log_size_mb"],
                "compression_enabled": self.frequency_config["enable_compression"],
                "archive_after_days": 7,
                "cleanup_schedule": "daily",
            }

            # Save rotation configuration
            rotation_file = self.configs_dir / "nfl_parlay_rotation.json"
            with open(rotation_file, "w") as f:
                json.dump(rotation_config, f, indent=2)

            # Create rotation script
            rotation_script = self.create_rotation_script(rotation_config)

            return {
                "success": True,
                "config_file": str(rotation_file),
                "rotation_script": rotation_script,
                "configuration": rotation_config,
                "description": "Implemented NFL parlay log rotation with compression",
            }

        except Exception as e:
            logger.error(f"Error implementing log rotation: {e}")
            return {
                "success": False,
                "error": str(e),
                "description": f"Failed to implement log rotation: {e}",
            }

    def create_rotation_script(self, config: dict[str, Any]) -> str:
        """Create automatic log rotation script"""
        rotation_script = '''#!/usr/bin/env python3
"""
Automatic NFL Parlay Log Rotation
Generated by EQ12 NFL Logging Frequency Optimizer
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

def rotate_nfl_logs():
    logs_dir = Path("C:/EQ12/logs")
    archive_dir = logs_dir / "archive" / "nfl_parlay"
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Find NFL parlay logs
    nfl_logs = list(logs_dir.glob("*nfl*parlay*.log")) + list(logs_dir.glob("*nfl*parlay*.json"))

    # Keep only the most recent {config["max_files_per_type"]} files
    nfl_logs.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    files_to_archive = nfl_logs[{config["max_files_per_type"]}:]

    for log_file in files_to_archive:
        try:
            # Check file size
            size_mb = log_file.stat().st_size / (1024 * 1024)

            if size_mb > {config["max_file_size_mb"]}:
                # Compress and archive large files
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_name = f"{{log_file.stem}}_{{timestamp}}.gz"
                archive_path = archive_dir / archive_name

                with open(log_file, 'rb') as f_in:
                    with gzip.open(archive_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                log_file.unlink()
                print(f"Archived and compressed: {{log_file.name}} -> {{archive_name}}")
            else:
                # Just move smaller files
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_name = f"{{log_file.stem}}_{{timestamp}}{{log_file.suffix}}"
                archive_path = archive_dir / archive_name

                shutil.move(str(log_file), str(archive_path))
                print(f"Archived: {{log_file.name}} -> {{archive_name}}")

        except Exception as e:
            print(f"Error archiving {{log_file}}: {{e}}")

    print(f"Log rotation complete - processed {{len(files_to_archive)}} files")

if __name__ == "__main__":
    rotate_nfl_logs()
'''

        script_path = self.eq12_root / "scripts" / "eq12_nfl_log_rotator.py"
        with open(script_path, "w") as f:
            f.write(rotation_script)

        logger.info(f"Created log rotation script: {script_path}")
        return str(script_path)

    def run_comprehensive_optimization(self) -> dict[str, Any]:
        """Run comprehensive NFL parlay logging optimization"""
        logger.info("Starting comprehensive NFL parlay logging optimization...")

        start_time = datetime.now()

        try:
            results = {
                "timestamp": start_time.isoformat(),
                "optimizations_applied": [],
                "total_optimizations": 0,
                "errors": [],
            }

            # 1. Determine optimal logging interval
            optimal_config = self.determine_optimal_interval()
            results["optimal_configuration"] = optimal_config
            logger.info(
                f"Optimal interval: {
                    optimal_config['interval']} ({
                    optimal_config['reason']})")

            # 2. Update scheduled tasks
            task_update_result = self.update_scheduled_tasks()
            if task_update_result["success"]:
                results["optimizations_applied"].append(
                    "Updated scheduled task frequencies")
                results["task_updates"] = task_update_result
            else:
                results["errors"].append(
                    f"Task update failed: {
                        task_update_result.get('error')}")

            # 3. Implement log rotation
            rotation_result = self.implement_log_rotation()
            if rotation_result["success"]:
                results["optimizations_applied"].append(
                    "Implemented log rotation and compression")
                results["log_rotation"] = rotation_result
            else:
                results["errors"].append(
                    f"Log rotation failed: {
                        rotation_result.get('error')}")

            # 4. Update frequency configuration
            self.frequency_config["current_interval"] = optimal_config["interval"]
            self.frequency_config["last_optimization"] = start_time.isoformat()

            with open(self.config_file, "w") as f:
                json.dump(self.frequency_config, f, indent=2)

            results["optimizations_applied"].append("Updated frequency configuration")

            # Calculate final results
            results["total_optimizations"] = len(results["optimizations_applied"])
            results["duration_seconds"] = (datetime.now() - start_time).total_seconds()
            results["success"] = len(results["errors"]) == 0

            logger.info(
                f"NFL parlay logging optimization completed in {
                    results['duration_seconds']:.1f}s")
            logger.info(f"Applied {results['total_optimizations']} optimizations")

            return results

        except Exception as e:
            logger.error(f"Comprehensive optimization failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
            }

    def print_optimization_summary(self, results: dict[str, Any]):
        """Print optimization summary"""
        print("\\n" + "=" * 70)
        print("NFL PARLAY LOGGING FREQUENCY OPTIMIZATION REPORT")
        print("=" * 70)

        print("\\nOPTIMIZATION SUMMARY:")
        print(f"  Status: {'SUCCESS' if results.get('success') else 'PARTIAL'}")
        print(f"  Optimizations Applied: {results.get('total_optimizations', 0)}")
        print(f"  Duration: {results.get('duration_seconds', 0):.1f} seconds")

        if "optimal_configuration" in results:
            config = results["optimal_configuration"]
            print("\\nCURRENT OPTIMAL SETTINGS:")
            print(
                f"  Logging Interval: {
                    config['interval']} ({
                    config['interval_minutes']} minutes)")
            print(f"  Reason: {config['reason']}")
            print(f"  Game Day: {'Yes' if config['is_game_day'] else 'No'}")
            print(f"  Peak Hours: {'Yes' if config['is_peak_hours'] else 'No'}")

        if results.get("optimizations_applied"):
            print("\\nAPPLIED OPTIMIZATIONS:")
            for i, optimization in enumerate(results["optimizations_applied"], 1):
                print(f"  {i}. {optimization}")

        if results.get("errors"):
            print("\\nERRORS ENCOUNTERED:")
            for i, error in enumerate(results["errors"], 1):
                print(f"  {i}. {error}")

        print("\\nNEXT STEPS:")
        print("  1. Monitor NFL parlay logs for reduced file generation")
        print("  2. Verify scheduled tasks are running at optimized intervals")
        print("  3. Check log rotation is working properly")
        print("  4. Adjust intervals if needed based on NFL game schedule")


def main():
    """Main entry point for NFL parlay logging optimization"""
    parser = argparse.ArgumentParser(
        description="EQ12 NFL Parlay Logging Frequency Optimizer")
    parser.add_argument(
        "--show-current",
        action="store_true",
        help="Show current optimal interval")
    parser.add_argument(
        "--update-tasks",
        action="store_true",
        help="Update scheduled tasks only")
    parser.add_argument(
        "--setup-rotation",
        action="store_true",
        help="Setup log rotation only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    optimizer = NFLLoggingFrequencyOptimizer()

    try:
        if args.show_current:
            # Show current optimal configuration
            config = optimizer.determine_optimal_interval()
            print("\\nCurrent Optimal NFL Parlay Logging Configuration:")
            print(
                f"  Interval: {
                    config['interval']} ({
                    config['interval_minutes']} minutes)")
            print(f"  Reason: {config['reason']}")
            print(f"  Is Game Day: {config['is_game_day']}")
            print(f"  Is Peak Hours: {config['is_peak_hours']}")

        elif args.update_tasks:
            # Update scheduled tasks only
            result = optimizer.update_scheduled_tasks()
            print(
                f"\\nTask Update Result: {
                    'SUCCESS' if result['success'] else 'FAILED'}")
            print(f"Tasks Updated: {result.get('total_tasks_updated', 0)}")

        elif args.setup_rotation:
            # Setup log rotation only
            result = optimizer.implement_log_rotation()
            print(
                f"\\nLog Rotation Setup: {
                    'SUCCESS' if result['success'] else 'FAILED'}")

        else:
            # Run comprehensive optimization
            results = optimizer.run_comprehensive_optimization()
            optimizer.print_optimization_summary(results)

            # Exit with appropriate code
            sys.exit(0 if results.get("success") else 1)

    except KeyboardInterrupt:
        print("\\nNFL parlay logging optimization interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"NFL parlay logging optimization failed: {e}")
        print(f"\\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
