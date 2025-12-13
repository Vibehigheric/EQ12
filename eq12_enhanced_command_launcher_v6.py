#!/usr/bin/env python3
"""
EQ12 Enhanced Command Launcher v6.0 - ASCII-SAFE HARDENED EDITION
================================================================

UTF-8 corruption-proof command interface for the EQ12 automation empire.
All emoji and Unicode characters removed for terminal safety.

Author: EQ12 AI Development Team
Version: 6.0.0 - ASCII-SAFE HARDENED
Date: November 16, 2025
Buffalo NY 14215 - Content Empire Command Center
"""

import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path


# ASCII-safe output enforcement
def ascii_safe(text):
    """Convert text to ASCII-safe version"""
    return str(text).encode("ascii", "ignore").decode("ascii")


def safe_print(text, color=None):
    """Print ASCII-safe text"""
    safe_text = ascii_safe(text)
    if color:
        print(f"\033[{color}m{safe_text}\033[0m")
    else:
        print(safe_text)


# Force UTF-8 encoding
os.environ["PYTHONUTF8"] = "1"


class EQ12EnhancedCommandLauncherV6:
    """ASCII-safe enhanced command launcher with full EQ12 system integration."""

    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.scripts_path = self.workspace_path / "scripts"
        self.logs_path = self.workspace_path / "logs"
        self.dashboard_path = self.workspace_path / "dashboard"

        # Ensure directories exist
        self.logs_path.mkdir(exist_ok=True)
        self.dashboard_path.mkdir(exist_ok=True)

        # Initialize command registry with real file validation
        self.command_registry = self._initialize_command_registry()
        self.system_status = self._get_real_system_status()

    def _check_file_exists(self, script_name: str) -> bool:
        """Check if a script actually exists on disk"""
        script_path = self.scripts_path / script_name
        if script_path.exists():
            return True

        # Check alternative locations
        alt_path = self.workspace_path / script_name
        return alt_path.exists()

    def _get_real_system_status(self) -> dict:
        """Get REAL system status by checking actual files"""
        critical_modules = [
            "eq12_business_intelligence_tracker.py",
            "eq12_quantum_revenue_deployment_engine.py",
            "eq12_master_revenue_orchestrator.py",
            "eq12_advanced_revenue_reporter_claude.py",
            "eq12_total_system_launcher.py",
        ]

        modules_found = 0
        for module in critical_modules:
            if self._check_file_exists(module):
                modules_found += 1

        health_percentage = (modules_found / len(critical_modules)) * 100
        api_coverage = f"{modules_found}/{len(critical_modules)} modules"

        return {
            "status": "OPERATIONAL" if modules_found >= 4 else "DEGRADED",
            "modules_found": modules_found,
            "total_modules": len(critical_modules),
            "health_score": f"{health_percentage:.1f}%",
            "api_coverage": api_coverage,
            "last_scan": datetime.now(UTC).isoformat(),
            "usb_system_ready": self._check_file_exists(
                "eq12_5usb_system_validator.ps1"
            ),
            "self_healing_active": self._check_file_exists("eq12_self_healing_v5.py"),
            "content_empire_active": True,
        }

    def _initialize_command_registry(self) -> dict:
        """Initialize command registry with real file validation"""
        return {
            "REVENUE AND BETTING OPERATIONS": {
                "1": {
                    "name": "run-odds",
                    "description": "High-frequency market data feed",
                    "script": "eq12_run_odds.py",
                    "args": ["--mode", "single", "--verbose"],
                    "status": (
                        "OPERATIONAL"
                        if self._check_file_exists("eq12_run_odds.py")
                        else "MISSING"
                    ),
                },
                "2": {
                    "name": "run-parlay",
                    "description": "AI parlay constructor and EV calculator",
                    "script": "eq12_run_parlay.py",
                    "args": ["--legs", "3", "--count", "1", "--verbose"],
                    "status": (
                        "OPERATIONAL"
                        if self._check_file_exists("eq12_run_parlay.py")
                        else "MISSING"
                    ),
                },
                "3": {
                    "name": "betting-suite",
                    "description": "Full autonomous betting pipeline",
                    "script": "eq12_betting_suite.py",
                    "args": ["--mode", "sequential", "--verbose"],
                    "status": (
                        "OPERATIONAL"
                        if self._check_file_exists("eq12_betting_suite.py")
                        else "MISSING"
                    ),
                },
                "4": {
                    "name": "revenue-cycle",
                    "description": "Complete revenue generation cycle",
                    "script": "eq12_master_revenue_orchestrator.py",
                    "args": ["--mode", "comprehensive"],
                    "status": (
                        "OPERATIONAL"
                        if self._check_file_exists(
                            "eq12_master_revenue_orchestrator.py"
                        )
                        else "MISSING"
                    ),
                },
            },
            "SYSTEM MANAGEMENT": {
                "5": {
                    "name": "health-check",
                    "description": "Comprehensive system validation",
                    "script": "eq12_final_system_validation.py",
                    "args": [],
                    "status": (
                        "OPERATIONAL"
                        if self._check_file_exists("eq12_final_system_validation.py")
                        else "MISSING"
                    ),
                },
                "6": {
                    "name": "repair-all",
                    "description": "Auto-repair PowerShell + system fixes",
                    "script": "eq12_emergency_repair.ps1",
                    "args": ["-AutoFix"],
                    "type": "powershell",
                    "status": (
                        "OPERATIONAL"
                        if self._check_file_exists("eq12_emergency_repair.ps1")
                        else "MISSING"
                    ),
                },
                "7": {
                    "name": "safe-run",
                    "description": "Run script with corruption protection",
                    "script": "eq12_safe_launcher_v4.ps1",
                    "args": [],
                    "type": "powershell",
                    "status": (
                        "OPERATIONAL"
                        if self._check_file_exists("eq12_safe_launcher_v4.ps1")
                        else "MISSING"
                    ),
                },
            },
            "EMERGENCY AND RECOVERY": {
                "18": {
                    "name": "emergency-mode",
                    "description": "Crisis recovery protocol",
                    "script": "eq12_self_healing_wrapper_minimal.ps1",
                    "args": ["test"],
                    "type": "powershell",
                    "status": (
                        "OPERATIONAL"
                        if self._check_file_exists(
                            "eq12_self_healing_wrapper_minimal.ps1"
                        )
                        else "MISSING"
                    ),
                },
                "21": {
                    "name": "godmode",
                    "description": "Ultimate system override",
                    "script": "eq12_total_system_launcher.py",
                    "args": ["--mode", "full", "--verbose"],
                    "status": (
                        "OPERATIONAL"
                        if self._check_file_exists("eq12_total_system_launcher.py")
                        else "MISSING"
                    ),
                },
            },
            "VALIDATION AND REPAIR": {
                "30": {
                    "name": "validate-scripts",
                    "description": "Validate all PowerShell scripts",
                    "script": "eq12_script_validator.ps1",
                    "args": [],
                    "type": "powershell",
                    "status": "OPERATIONAL",
                },
                "31": {
                    "name": "fix-encoding",
                    "description": "Fix UTF-8 encoding issues",
                    "script": "eq12_script_validator.ps1",
                    "args": ["-AutoFix", "-BackupFiles"],
                    "type": "powershell",
                    "status": "OPERATIONAL",
                },
            },
        }

    def display_header(self):
        """Display ASCII-safe EQ12 header with real system status"""
        print("\n" + "=" * 80)
        safe_print("EQ12 ENHANCED COMMAND LAUNCHER v6.0 - BUFFALO NY 14215", "96")
        safe_print("ASCII-SAFE CORRUPTION-PROOF COMMAND CENTER", "93")
        print("=" * 80)
        safe_print(
            f"STATUS: {self.system_status['status']}",
            "92" if self.system_status["status"] == "OPERATIONAL" else "91",
        )
        safe_print(f"MODULES: {self.system_status['api_coverage']}", "92")
        safe_print(f"HEALTH SCORE: {self.system_status['health_score']}", "93")
        safe_print(
            f"USB SYSTEM: {'READY' if self.system_status['usb_system_ready'] else 'MISSING'}",
            "92" if self.system_status["usb_system_ready"] else "91",
        )
        safe_print(
            f"SELF-HEALING: {'ACTIVE' if self.system_status['self_healing_active'] else 'MISSING'}",
            "92" if self.system_status["self_healing_active"] else "91",
        )
        safe_print("CONTENT EMPIRE: ACTIVE (Buffalo NY 14215)", "92")
        print("=" * 80)

    def display_commands(self):
        """Display available commands with real status indicators"""
        for category, commands in self.command_registry.items():
            print(f"\n{category}:")
            for cmd_id, cmd_data in commands.items():
                status_indicator = (
                    "[OK]" if cmd_data["status"] == "OPERATIONAL" else "[MISSING]"
                )
                status_color = "92" if cmd_data["status"] == "OPERATIONAL" else "91"
                safe_print(
                    f"  {cmd_id:<2} {cmd_data['name']:<15} -> {cmd_data['description']} {status_indicator}",
                    status_color,
                )
        print("\n  exit                   -> Exit launcher")
        print("=" * 80)

    def execute_command(self, command_input: str) -> bool:
        """Execute a command by ID or name with error handling"""
        if command_input.lower() == "exit":
            return False

        # Find command in registry
        command_data = None
        for category, commands in self.command_registry.items():
            if command_input in commands:
                command_data = commands[command_input]
                break
            # Also check by name
            for cmd_id, cmd_data in commands.items():
                if command_input == cmd_data["name"]:
                    command_data = cmd_data
                    break

        if not command_data:
            safe_print(f"ERROR: Unknown command: {command_input}", "91")
            return True

        # Check if script exists before execution
        if command_data["status"] == "MISSING":
            safe_print(f"ERROR: Script missing: {command_data['script']}", "91")
            return True

        # Execute command
        print(f"\nEXECUTING: {command_data['name']}")
        safe_print(f"Description: {command_data['description']}", "96")
        print("-" * 60)

        try:
            if command_data.get("type") == "powershell":
                # Use safe launcher for PowerShell
                safe_launcher = self.workspace_path / "eq12_safe_launcher.ps1"
                script_path = self.scripts_path / command_data["script"]
                if not script_path.exists():
                    script_path = self.workspace_path / command_data["script"]

                cmd = [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(safe_launcher),
                    str(script_path),
                    *command_data.get("args", []),
                ]
            else:
                # Python command
                script_path = self.scripts_path / command_data["script"]
                if not script_path.exists():
                    script_path = self.workspace_path / command_data["script"]
                cmd = [sys.executable, str(script_path), *command_data.get("args", [])]

            start_time = time.time()
            result = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
            )
            execution_time = time.time() - start_time

            if result.returncode == 0:
                safe_print(f"SUCCESS ({execution_time:.2f}s)", "92")
                if result.stdout:
                    print(f"OUTPUT:\n{ascii_safe(result.stdout[:1000])}...")
            else:
                safe_print(f"FAILED (Code: {result.returncode})", "91")
                if result.stderr:
                    safe_print(f"ERROR:\n{ascii_safe(result.stderr[:500])}...", "91")

        except Exception as e:
            safe_print(f"EXECUTION ERROR: {ascii_safe(str(e))}", "91")

        print("-" * 60)
        return True

    def save_session_log(self):
        """Save session activity to log file"""
        log_data = {
            "session_start": datetime.now(UTC).isoformat(),
            "launcher_version": "6.0-ascii-safe",
            "system_status": self.system_status,
            "commands_available": sum(
                len(commands) for commands in self.command_registry.values()
            ),
            "workspace": str(self.workspace_path),
        }

        log_file = (
            self.logs_path
            / f"command_session_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2, ensure_ascii=True)

    def run_interactive(self):
        """Run interactive command launcher"""
        self.display_header()
        self.display_commands()

        print("\nSELECT YOUR COMMAND (or type number):")

        while True:
            try:
                user_input = input("\nEQ12> ").strip()

                if not user_input:
                    continue

                if not self.execute_command(user_input):
                    break

            except KeyboardInterrupt:
                print("\n\nExiting EQ12 Command Launcher...")
                break
            except Exception as e:
                safe_print(f"Error: {ascii_safe(str(e))}", "91")
                continue

        self.save_session_log()
        safe_print("Buffalo NY 14215 Content Empire - Session Complete!", "92")


def main():
    """Main entry point"""
    launcher = EQ12EnhancedCommandLauncherV6()
    launcher.run_interactive()


if __name__ == "__main__":
    main()
