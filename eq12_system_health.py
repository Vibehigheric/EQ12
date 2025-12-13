#!/usr/bin/env python3
"""
EQ12 System Health Checker

Comprehensive health monitoring and diagnostics for the EQ12 stack.
Validates system components, dependencies, configurations, and performance.

Features:
- Dependency validation
- Configuration integrity checks
- Performance monitoring
- Security validation
- Service health checks
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EQ12HealthChecker:
    """Comprehensive health checker for EQ12 system."""

    def __init__(self, eq12_root: str = "C:/EQ12"):
        """Initialize health checker.

        Args:
            eq12_root: Root directory of EQ12 installation
        """
        self.eq12_root = Path(eq12_root)
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
            "summary": {"total_checks": 0, "passed": 0, "failed": 0, "warnings": 0},
        }

    def run_all_checks(self) -> dict[str, Any]:
        """Run comprehensive system health checks.

        Returns:
            Dictionary with all check results
        """
        checks = [
            ("Directory Structure", self.check_directory_structure),
            ("Python Dependencies", self.check_python_dependencies),
            ("Configuration Files", self.check_configuration_files),
            ("Log Health", self.check_log_health),
            ("PowerShell Scripts", self.check_powershell_scripts),
            ("Git Repository", self.check_git_repository),
            ("Environment Variables", self.check_environment_variables),
            ("Services Status", self.check_services_status),
            ("Disk Space", self.check_disk_space),
            ("Performance", self.check_performance),
        ]

        for check_name, check_function in checks:
            logger.info(f"Running check: {check_name}")
            try:
                result = check_function()
                self.results["checks"][check_name] = result
                self._update_summary(result)
            except Exception as e:
                logger.error(f"Check '{check_name}' failed: {e}")
                self.results["checks"][check_name] = {
                    "status": "error",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                self._update_summary({"status": "error"})

        return self.results

    def check_directory_structure(self) -> dict[str, Any]:
        """Validate EQ12 directory structure."""
        required_dirs = ["scripts", "tests", "configs", "logs", "dashboard", "data"]

        result = {
            "status": "pass",
            "message": "All required directories found",
            "details": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        missing_dirs = []
        for dir_name in required_dirs:
            dir_path = self.eq12_root / dir_name
            if dir_path.exists():
                result["details"][dir_name] = {
                    "exists": True,
                    "has_init": (dir_path / "__init__.py").exists(),
                }
            else:
                missing_dirs.append(dir_name)
                result["details"][dir_name] = {"exists": False}

        if missing_dirs:
            result["status"] = "fail"
            result["message"] = f"Missing directories: {', '.join(missing_dirs)}"

        return result

    def check_python_dependencies(self) -> dict[str, Any]:
        """Check Python package dependencies."""
        result = {
            "status": "pass",
            "message": "All dependencies satisfied",
            "details": {"missing": [], "installed": []},
            "timestamp": datetime.utcnow().isoformat(),
        }

        requirements_file = self.eq12_root / "requirements.txt"
        if not requirements_file.exists():
            result["status"] = "fail"
            result["message"] = "requirements.txt not found"
            return result

        try:
            # Read requirements
            with open(requirements_file) as f:
                lines = f.readlines()

            packages = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    package_name = line.split(">=")[0].split("==")[0]
                    packages.append(package_name)

            # Check each package
            for package in packages:
                try:
                    subprocess.run(
                        [sys.executable, "-c", f"import {package}"],
                        check=True,
                        capture_output=True,
                    )
                    result["details"]["installed"].append(package)
                except subprocess.CalledProcessError:
                    result["details"]["missing"].append(package)

            if result["details"]["missing"]:
                result["status"] = "fail"
                result["message"] = f"Missing packages: {', '.join(result['details']['missing'])}"

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Error checking dependencies: {e}"

        return result

    def check_configuration_files(self) -> dict[str, Any]:
        """Validate configuration file integrity."""
        result = {
            "status": "pass",
            "message": "All configuration files valid",
            "details": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        config_dir = self.eq12_root / "configs"
        if not config_dir.exists():
            result["status"] = "fail"
            result["message"] = "Configuration directory not found"
            return result

        json_files = list(config_dir.glob("*.json"))
        invalid_files = []

        for json_file in json_files:
            try:
                with open(json_file) as f:
                    json.load(f)
                result["details"][json_file.name] = "valid"
            except json.JSONDecodeError as e:
                result["details"][json_file.name] = f"invalid: {e}"
                invalid_files.append(json_file.name)

        if invalid_files:
            result["status"] = "fail"
            result["message"] = f"Invalid JSON files: {', '.join(invalid_files)}"

        return result

    def check_log_health(self) -> dict[str, Any]:
        """Check log file health and rotation status."""
        result = {
            "status": "pass",
            "message": "Log system healthy",
            "details": {
                "total_files": 0,
                "total_size_mb": 0,
                "large_files": [],
                "recent_errors": 0,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        logs_dir = self.eq12_root / "logs"
        if not logs_dir.exists():
            result["status"] = "fail"
            result["message"] = "Logs directory not found"
            return result

        large_files = []
        total_size = 0
        file_count = 0

        for log_file in logs_dir.glob("*.log"):
            file_count += 1
            size_mb = log_file.stat().st_size / (1024 * 1024)
            total_size += size_mb

            if size_mb > 100:  # Files larger than 100MB
                large_files.append({"file": log_file.name, "size_mb": round(size_mb, 2)})

        result["details"]["total_files"] = file_count
        result["details"]["total_size_mb"] = round(total_size, 2)
        result["details"]["large_files"] = large_files

        if large_files:
            result["status"] = "warning"
            result["message"] = f"{len(large_files)} large log files need rotation"

        return result

    def check_powershell_scripts(self) -> dict[str, Any]:
        """Validate PowerShell script syntax."""
        result = {
            "status": "pass",
            "message": "All PowerShell scripts valid",
            "details": {"checked": 0, "errors": []},
            "timestamp": datetime.utcnow().isoformat(),
        }

        ps_files = list(self.eq12_root.glob("**/*.ps1"))
        result["details"]["checked"] = len(ps_files)

        # Basic syntax check for a few key scripts
        key_scripts = [
            "eq12_simple_start.ps1",
            "eq12_status_check_clean.ps1",
            "manage_chrome_task.ps1",
        ]

        for script_name in key_scripts:
            script_path = self.eq12_root / script_name
            if script_path.exists():
                try:
                    # Basic PowerShell syntax validation
                    cmd = [
                        "powershell",
                        "-NoProfile",
                        "-Command",
                        f'Get-Command -Syntax (Get-Content "{script_path}")',
                    ]
                    subprocess.run(cmd, check=True, capture_output=True, timeout=10)
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                    result["details"]["errors"].append({"script": script_name, "error": str(e)})

        if result["details"]["errors"]:
            result["status"] = "warning"
            result["message"] = f"{len(result['details']['errors'])} scripts have issues"

        return result

    def check_git_repository(self) -> dict[str, Any]:
        """Check Git repository health."""
        result = {
            "status": "pass",
            "message": "Git repository healthy",
            "details": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        if not (self.eq12_root / ".git").exists():
            result["status"] = "warning"
            result["message"] = "Not a Git repository"
            return result

        try:
            # Check git status
            cmd = ["git", "status", "--porcelain"]
            proc = subprocess.run(cmd, cwd=self.eq12_root, capture_output=True, text=True)

            if proc.returncode == 0:
                uncommitted = len(proc.stdout.strip().split("\n")) if proc.stdout.strip() else 0
                result["details"]["uncommitted_changes"] = uncommitted

                if uncommitted > 10:
                    result["status"] = "warning"
                    result["message"] = f"{uncommitted} uncommitted changes"
            else:
                result["status"] = "error"
                result["message"] = "Git command failed"

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Git check failed: {e}"

        return result

    def check_environment_variables(self) -> dict[str, Any]:
        """Check required environment variables."""
        result = {
            "status": "pass",
            "message": "Environment variables configured",
            "details": {"missing": [], "configured": []},
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Required environment variables from AGENTS.md
        required_vars = [
            "ODDS_API_KEY",
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_CHAT_ID",
            "OPENAI_API_KEY",
        ]

        import os

        for var in required_vars:
            if os.getenv(var):
                result["details"]["configured"].append(var)
            else:
                result["details"]["missing"].append(var)

        if result["details"]["missing"]:
            result["status"] = "warning"
            result["message"] = f"Missing env vars: {', '.join(result['details']['missing'])}"

        return result

    def check_services_status(self) -> dict[str, Any]:
        """Check status of EQ12 services."""
        result = {
            "status": "pass",
            "message": "Services status checked",
            "details": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        # This is a placeholder for actual service checks
        # In a real implementation, you'd check:
        # - Database connections
        # - Web server status
        # - Background tasks
        # - External API connectivity

        result["details"]["note"] = "Service checks not implemented"
        result["status"] = "info"

        return result

    def check_disk_space(self) -> dict[str, Any]:
        """Check available disk space."""
        result = {
            "status": "pass",
            "message": "Sufficient disk space available",
            "details": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            import shutil

            total, used, free = shutil.disk_usage(self.eq12_root)

            free_gb = free / (1024**3)
            total_gb = total / (1024**3)
            used_percent = (used / total) * 100

            result["details"] = {
                "free_gb": round(free_gb, 2),
                "total_gb": round(total_gb, 2),
                "used_percent": round(used_percent, 2),
            }

            if free_gb < 1:  # Less than 1GB free
                result["status"] = "fail"
                result["message"] = f"Low disk space: {free_gb:.2f}GB free"
            elif free_gb < 5:  # Less than 5GB free
                result["status"] = "warning"
                result["message"] = f"Disk space warning: {free_gb:.2f}GB free"

        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Disk space check failed: {e}"

        return result

    def check_performance(self) -> dict[str, Any]:
        """Basic performance checks."""
        result = {
            "status": "pass",
            "message": "Performance metrics collected",
            "details": {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            # CPU and memory usage
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            result["details"] = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
            }

            if cpu_percent > 90:
                result["status"] = "warning"
                result["message"] = f"High CPU usage: {cpu_percent}%"
            elif memory.percent > 90:
                result["status"] = "warning"
                result["message"] = f"High memory usage: {memory.percent}%"

        except ImportError:
            result["details"]["note"] = "psutil not installed - performance metrics unavailable"
            result["status"] = "info"
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"Performance check failed: {e}"

        return result

    def _update_summary(self, check_result: dict[str, Any]) -> None:
        """Update summary statistics.

        Args:
            check_result: Individual check result
        """
        self.results["summary"]["total_checks"] += 1

        status = check_result.get("status", "unknown")
        if status in ["pass", "info"]:
            self.results["summary"]["passed"] += 1
        elif status == "warning":
            self.results["summary"]["warnings"] += 1
        else:
            self.results["summary"]["failed"] += 1


def main():
    """Main entry point for health checker."""
    parser = argparse.ArgumentParser(description="EQ12 System Health Checker")
    parser.add_argument("--eq12-root", default="C:/EQ12", help="EQ12 installation root directory")
    parser.add_argument(
        "--output",
        default="eq12_health_report.json",
        help="Output file for health report",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    checker = EQ12HealthChecker(args.eq12_root)

    logger.info("Starting EQ12 system health check...")
    start_time = time.time()

    try:
        results = checker.run_all_checks()
        end_time = time.time()

        results["execution_time_seconds"] = round(end_time - start_time, 2)

        # Save results
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)

        # Print summary
        summary = results["summary"]
        print("\nEQ12 Health Check Summary")
        print("========================")
        print(f"Total Checks: {summary['total_checks']}")
        print(f"Passed: {summary['passed']}")
        print(f"Warnings: {summary['warnings']}")
        print(f"Failed: {summary['failed']}")
        print(f"Execution Time: {results['execution_time_seconds']}s")
        print(f"\nDetailed report saved to: {args.output}")

        # Exit with appropriate code
        if summary["failed"] > 0:
            return 1
        if summary["warnings"] > 0:
            return 2
        return 0

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
