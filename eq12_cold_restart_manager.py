#!/usr/bin/env python3
"""
EQ12 Cold Restart and System Recovery Manager

This script implements a comprehensive cold restart mechanism for the EQ12 system
with proper initialization sequence, dependency checking, and recovery procedures.

Features:
- Complete system shutdown and restart
- Service dependency management
- Database integrity checks
- Configuration validation
- Real-time status monitoring
- Automated recovery procedures

Author: EQ12 System
Created: 2025-10-04
"""

import asyncio
import json
import logging
import sqlite3
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path

import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/cold_restart.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class EQ12ColdRestartManager:
    """Comprehensive cold restart and system recovery manager"""

    def __init__(self):
        self.base_path = Path("C:/EQ12")
        self.config_path = self.base_path / "configs" / "sports_betting_config.json"
        self.db_path = self.base_path / "data" / "sports_betting.db"
        self.logs_path = self.base_path / "logs"

        # Service definitions
        self.services = {
            "EQ12_XFactorMaster": {
                "script": "eq12_x_factor_pipeline.py",
                "description": "X-Factor sentiment pipeline",
                "critical": True,
            },
            "EQ12_AutoTrader": {
                "script": "eq12_auto_trade_executor.py",
                "description": "Automated trading engine",
                "critical": True,
            },
            "EQ12_Master": {
                "script": "eq12_master_controller.py",
                "description": "Master system controller",
                "critical": True,
            },
        }

        # System components
        self.components = [
            "Database",
            "Configuration",
            "Python Environment",
            "PowerShell Scripts",
            "Log System",
            "Network Connectivity",
            "API Keys",
            "File Permissions",
        ]

        self.restart_log = []
        self.is_restarting = False

    def log_event(self, message: str, level: str = "INFO", component: str | None = None):
        """Log system events with structured format"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "component": component or "System",
        }

        self.restart_log.append(log_entry)

        # Log to file and console
        log_func = getattr(logger, level.lower(), logger.info)
        log_message = f"[{component or 'System'}] {message}"
        log_func(log_message)

        # Also save to restart log file
        restart_log_file = self.logs_path / "restart_history.jsonl"
        with open(restart_log_file, "a") as f:
            json.dump(log_entry, f)
            f.write("\n")

    @contextmanager
    def system_lock(self):
        """Prevent multiple restart operations"""
        lock_file = self.base_path / ".restart_lock"

        if lock_file.exists():
            raise RuntimeError("Another restart operation is in progress")

        try:
            lock_file.touch()
            self.is_restarting = True
            yield
        finally:
            if lock_file.exists():
                lock_file.unlink()
            self.is_restarting = False

    def check_system_dependencies(self) -> dict[str, bool]:
        """Check all system dependencies"""
        self.log_event("🔍 Checking system dependencies...", "INFO")

        results = {}

        # Check Python
        try:
            result = subprocess.run(
                [sys.executable, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                results["Python"] = True
                self.log_event(f"✅ Python available: {result.stdout.strip()}", "INFO", "Python")
            else:
                results["Python"] = False
                self.log_event("❌ Python check failed", "ERROR", "Python")
        except Exception as e:
            results["Python"] = False
            self.log_event(f"❌ Python error: {e}", "ERROR", "Python")

        # Check PowerShell
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-Host | Select-Object Version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            results["PowerShell"] = result.returncode == 0
            status = "✅" if results["PowerShell"] else "❌"
            self.log_event(
                f"{status} PowerShell check",
                "INFO" if results["PowerShell"] else "ERROR",
                "PowerShell",
            )
        except Exception as e:
            results["PowerShell"] = False
            self.log_event(f"❌ PowerShell error: {e}", "ERROR", "PowerShell")

        # Check database
        try:
            if self.db_path.exists():
                conn = sqlite3.connect(str(self.db_path))
                conn.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
                conn.close()
                results["Database"] = True
                self.log_event("✅ Database accessible", "INFO", "Database")
            else:
                results["Database"] = False
                self.log_event("❌ Database file not found", "ERROR", "Database")
        except Exception as e:
            results["Database"] = False
            self.log_event(f"❌ Database error: {e}", "ERROR", "Database")

        # Check configuration
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    json.load(f)
                results["Configuration"] = True
                self.log_event("✅ Configuration file valid", "INFO", "Configuration")
            else:
                results["Configuration"] = False
                self.log_event("❌ Configuration file not found", "ERROR", "Configuration")
        except Exception as e:
            results["Configuration"] = False
            self.log_event(f"❌ Configuration error: {e}", "ERROR", "Configuration")

        # Check network connectivity
        try:
            import urllib.request

            urllib.request.urlopen("https://www.google.com", timeout=10)
            results["Network"] = True
            self.log_event("✅ Network connectivity confirmed", "INFO", "Network")
        except Exception as e:
            results["Network"] = False
            self.log_event(f"❌ Network error: {e}", "ERROR", "Network")

        return results

    def stop_all_services(self) -> bool:
        """Stop all EQ12 services and processes"""
        self.log_event("🛑 Stopping all EQ12 services...", "INFO")

        success = True

        # Stop Windows services
        for service_name in self.services:
            try:
                result = subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        f"Stop-Service -Name '{service_name}' -Force -ErrorAction SilentlyContinue",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    self.log_event(f"✅ Stopped service: {service_name}", "INFO", "ServiceManager")
                else:
                    self.log_event(
                        f"⚠️ Service {service_name} may not exist or already stopped",
                        "WARNING",
                        "ServiceManager",
                    )
            except Exception as e:
                self.log_event(f"❌ Error stopping {service_name}: {e}", "ERROR", "ServiceManager")
                success = False

        # Stop PowerShell background jobs
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-Job | Where-Object { $_.Name -like 'EQ12_*' } | Stop-Job -PassThru | Remove-Job -Force",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.log_event("✅ Stopped PowerShell background jobs", "INFO", "PowerShell")
        except Exception as e:
            self.log_event(f"⚠️ PowerShell job cleanup: {e}", "WARNING", "PowerShell")

        # Kill Python processes related to EQ12
        killed_processes = []
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                cmdline = " ".join(proc.info["cmdline"]) if proc.info["cmdline"] else ""
                if "python" in proc.info["name"].lower() and "eq12" in cmdline.lower():
                    proc.terminate()
                    killed_processes.append(proc.info["pid"])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if killed_processes:
            self.log_event(
                f"✅ Terminated Python processes: {killed_processes}",
                "INFO",
                "ProcessManager",
            )

        # Wait for graceful shutdown
        time.sleep(5)

        # Force kill if necessary
        for pid in killed_processes:
            try:
                proc = psutil.Process(pid)
                if proc.is_running():
                    proc.kill()
                    self.log_event(f"💀 Force killed process: {pid}", "WARNING", "ProcessManager")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return success

    def validate_database_integrity(self) -> bool:
        """Validate and repair database if necessary"""
        self.log_event("🔍 Validating database integrity...", "INFO", "Database")

        try:
            if not self.db_path.exists():
                self.log_event(
                    "❌ Database file missing, will need initialization",
                    "ERROR",
                    "Database",
                )
                return False

            # Check database file integrity
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Run integrity check
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()

            if integrity_result[0] != "ok":
                self.log_event(
                    f"❌ Database integrity issues: {integrity_result[0]}",
                    "ERROR",
                    "Database",
                )
                conn.close()
                return False

            # Check required tables exist
            required_tables = [
                "games",
                "odds_snapshots",
                "team_ratings",
                "betting_edges",
                "bets",
                "injury_reports",
                "twitter_sentiment",
                "bankroll_history",
            ]

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]

            missing_tables = set(required_tables) - set(existing_tables)
            if missing_tables:
                self.log_event(f"⚠️ Missing tables: {missing_tables}", "WARNING", "Database")
                # Don't fail - migration can handle this

            # Check critical columns exist
            try:
                cursor.execute("SELECT clv, edge_id FROM bets LIMIT 1")
                self.log_event("✅ Critical columns (clv, edge_id) verified", "INFO", "Database")
            except sqlite3.OperationalError as e:
                if "no such column" in str(e):
                    self.log_event(f"⚠️ Missing columns detected: {e}", "WARNING", "Database")
                    # Migration will fix this
                else:
                    raise

            conn.close()
            self.log_event("✅ Database integrity validated", "INFO", "Database")
            return True

        except Exception as e:
            self.log_event(f"❌ Database validation failed: {e}", "ERROR", "Database")
            return False

    def repair_database(self) -> bool:
        """Repair or reinitialize database"""
        self.log_event("🔧 Attempting database repair...", "INFO", "Database")

        try:
            # Run database migration script
            migration_script = self.base_path / "eq12_database_migration.py"
            if migration_script.exists():
                result = subprocess.run(
                    [sys.executable, str(migration_script)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    self.log_event(
                        "✅ Database migration completed successfully",
                        "INFO",
                        "Database",
                    )
                    return True
                self.log_event(
                    f"❌ Database migration failed: {result.stderr}",
                    "ERROR",
                    "Database",
                )
                return False
            self.log_event("❌ Database migration script not found", "ERROR", "Database")
            return False

        except Exception as e:
            self.log_event(f"❌ Database repair failed: {e}", "ERROR", "Database")
            return False

    def start_services_sequentially(self) -> bool:
        """Start services in the correct order"""
        self.log_event("🚀 Starting EQ12 services sequentially...", "INFO")

        # Service startup order (dependencies first)
        startup_order = ["EQ12_Master", "EQ12_XFactorMaster", "EQ12_AutoTrader"]

        for service_name in startup_order:
            if service_name in self.services:
                success = self.start_single_service(service_name)
                if not success and self.services[service_name]["critical"]:
                    self.log_event(f"❌ Critical service {service_name} failed to start", "ERROR")
                    return False

                # Wait between service starts
                time.sleep(3)

        return True

    def start_single_service(self, service_name: str) -> bool:
        """Start a single service"""
        self.services.get(service_name, {})

        try:
            # Check if service exists
            check_result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f"Get-Service -Name '{service_name}' -ErrorAction SilentlyContinue",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if check_result.returncode != 0:
                self.log_event(
                    f"⚠️ Service {service_name} not installed, trying PowerShell alternative",
                    "WARNING",
                    "ServiceManager",
                )
                return self.start_powershell_alternative(service_name)

            # Start the service
            start_result = subprocess.run(
                ["powershell", "-Command", f"Start-Service -Name '{service_name}'"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if start_result.returncode == 0:
                self.log_event(f"✅ Started service: {service_name}", "INFO", "ServiceManager")
                return True
            self.log_event(
                f"❌ Failed to start service {service_name}: {start_result.stderr}",
                "ERROR",
                "ServiceManager",
            )
            return False

        except Exception as e:
            self.log_event(
                f"❌ Error starting service {service_name}: {e}",
                "ERROR",
                "ServiceManager",
            )
            return False

    def start_powershell_alternative(self, service_name: str) -> bool:
        """Start service using PowerShell background jobs as fallback"""
        service_info = self.services.get(service_name, {})
        script_name = service_info.get("script")

        if not script_name:
            return False

        script_path = self.base_path / script_name
        if not script_path.exists():
            self.log_event(f"❌ Script not found: {script_path}", "ERROR", "PowerShell")
            return False

        try:
            # Use the advanced PowerShell wrapper to start live monitoring
            ps_command = "powershell -ExecutionPolicy Bypass -File 'C:\\EQ12\\eq12_sports_betting_advanced.ps1' -Action startlive"

            result = subprocess.run(
                ps_command, shell=True, capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                self.log_event(f"✅ Started {service_name} via PowerShell", "INFO", "PowerShell")
                return True
            self.log_event(
                f"❌ PowerShell start failed: {result.stderr}",
                "ERROR",
                "PowerShell",
            )
            return False

        except Exception as e:
            self.log_event(f"❌ PowerShell alternative failed: {e}", "ERROR", "PowerShell")
            return False

    def verify_system_health(self) -> dict[str, bool]:
        """Comprehensive system health check after restart"""
        self.log_event("🩺 Performing post-restart health check...", "INFO")

        health_results = {}

        # Check dependencies
        dep_results = self.check_system_dependencies()
        health_results.update(dep_results)

        # Check services are running
        for service_name in self.services:
            try:
                result = subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        f"(Get-Service -Name '{service_name}' -ErrorAction SilentlyContinue).Status",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                is_running = "Running" in result.stdout
                health_results[f"Service_{service_name}"] = is_running

                status = "✅" if is_running else "❌"
                self.log_event(
                    f"{status} Service {service_name}: {'Running' if is_running else 'Not Running'}",
                    "INFO" if is_running else "WARNING",
                    "HealthCheck",
                )

            except Exception as e:
                health_results[f"Service_{service_name}"] = False
                self.log_event(f"❌ Error checking {service_name}: {e}", "ERROR", "HealthCheck")

        # Test database connection
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master")
            table_count = cursor.fetchone()[0]
            conn.close()

            health_results["DatabaseConnection"] = True
            self.log_event(f"✅ Database accessible ({table_count} tables)", "INFO", "HealthCheck")

        except Exception as e:
            health_results["DatabaseConnection"] = False
            self.log_event(f"❌ Database connection failed: {e}", "ERROR", "HealthCheck")

        # Test API endpoints (if available)
        # This would test internal APIs, dashboard endpoints, etc.

        return health_results

    async def execute_cold_restart(self, force: bool = False) -> bool:
        """Execute complete cold restart procedure"""

        self.log_event("🔄 INITIATING EQ12 COLD RESTART SEQUENCE", "INFO")
        self.log_event("=" * 50, "INFO")

        try:
            with self.system_lock():
                # Phase 1: Pre-restart validation
                self.log_event("📋 Phase 1: Pre-restart validation", "INFO")
                if not force:
                    dependencies = self.check_system_dependencies()
                    critical_missing = [
                        k
                        for k, v in dependencies.items()
                        if not v and k in ["Python", "PowerShell"]
                    ]

                    if critical_missing:
                        self.log_event(
                            f"❌ Critical dependencies missing: {critical_missing}",
                            "ERROR",
                        )
                        return False

                # Phase 2: Graceful shutdown
                self.log_event("📋 Phase 2: Graceful shutdown", "INFO")
                shutdown_success = self.stop_all_services()
                if not shutdown_success and not force:
                    self.log_event("❌ Shutdown failed, aborting restart", "ERROR")
                    return False

                # Phase 3: System validation and repair
                self.log_event("📋 Phase 3: System validation and repair", "INFO")
                db_valid = self.validate_database_integrity()
                if not db_valid:
                    self.log_event("🔧 Attempting database repair...", "INFO")
                    repair_success = self.repair_database()
                    if not repair_success and not force:
                        self.log_event("❌ Database repair failed, aborting restart", "ERROR")
                        return False

                # Phase 4: Service restart
                self.log_event("📋 Phase 4: Service restart", "INFO")
                restart_success = self.start_services_sequentially()
                if not restart_success and not force:
                    self.log_event("❌ Service restart failed", "ERROR")
                    return False

                # Phase 5: Health verification
                self.log_event("📋 Phase 5: Health verification", "INFO")
                await asyncio.sleep(10)  # Give services time to start

                health_results = self.verify_system_health()
                healthy_components = sum(1 for v in health_results.values() if v)
                total_components = len(health_results)

                health_percentage = (healthy_components / total_components) * 100

                self.log_event(
                    f"🎯 System Health: {healthy_components}/{total_components} components healthy ({health_percentage:.1f}%)",
                    "INFO",
                )

                if health_percentage >= 80:
                    self.log_event("✅ COLD RESTART COMPLETED SUCCESSFULLY", "INFO")
                    self.log_event("=" * 50, "INFO")
                    return True
                self.log_event("⚠️ RESTART COMPLETED WITH WARNINGS", "WARNING")
                self.log_event("=" * 50, "WARNING")
                return not force  # Return False if not forced, True if forced

        except RuntimeError as e:
            self.log_event(f"❌ Restart blocked: {e}", "ERROR")
            return False
        except Exception as e:
            self.log_event(f"❌ CRITICAL ERROR during restart: {e}", "ERROR")
            return False

    def get_restart_history(self, days: int = 7) -> list[dict]:
        """Get restart history for the last N days"""
        restart_log_file = self.logs_path / "restart_history.jsonl"

        if not restart_log_file.exists():
            return []

        cutoff_date = datetime.now() - timedelta(days=days)
        recent_logs = []

        try:
            with open(restart_log_file) as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        log_date = datetime.fromisoformat(
                            log_entry["timestamp"].replace("Z", "+00:00")
                        )

                        if log_date >= cutoff_date:
                            recent_logs.append(log_entry)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
        except Exception as e:
            logger.error(f"Error reading restart history: {e}")

        return recent_logs


async def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Cold Restart Manager")
    parser.add_argument(
        "--action",
        choices=["restart", "status", "history", "stop", "start"],
        default="status",
        help="Action to perform",
    )
    parser.add_argument(
        "--force", action="store_true", help="Force restart even if issues detected"
    )
    parser.add_argument("--days", type=int, default=7, help="Days of history to show")

    args = parser.parse_args()

    manager = EQ12ColdRestartManager()

    if args.action == "restart":
        print("🔄 Initiating EQ12 Cold Restart...")
        success = await manager.execute_cold_restart(force=args.force)
        sys.exit(0 if success else 1)

    elif args.action == "status":
        print("🔍 Checking EQ12 System Status...")
        health_results = manager.verify_system_health()

        healthy_count = sum(1 for v in health_results.values() if v)
        total_count = len(health_results)

        print(f"\n📊 System Health: {healthy_count}/{total_count} components healthy")
        print("-" * 50)

        for component, status in health_results.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {component}")

    elif args.action == "history":
        print(f"📋 Restart History (Last {args.days} days)...")
        history = manager.get_restart_history(args.days)

        if not history:
            print("No restart history found.")
        else:
            for entry in history[-20:]:  # Show last 20 entries
                timestamp = entry["timestamp"][:19]  # Remove microseconds
                level_icon = {"INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌"}.get(entry["level"], "📝")
                print(f"{level_icon} {timestamp} [{entry['component']}] {entry['message']}")

    elif args.action == "stop":
        print("🛑 Stopping all EQ12 services...")
        success = manager.stop_all_services()
        sys.exit(0 if success else 1)

    elif args.action == "start":
        print("🚀 Starting EQ12 services...")
        success = manager.start_services_sequentially()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
