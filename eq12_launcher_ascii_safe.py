#!/usr/bin/env python3
"""
EQ12 ASCII-SAFE LAUNCHER - CORRUPTION IMMUNE VERSION
===================================================
100% ASCII-only command interface. Zero Unicode, zero corruption.
Guaranteed to work forever without encoding issues.

Author: EQ12 AI Development Team
Version: ASCII-SAFE 1.0
Date: November 16, 2025
Location: Buffalo NY 14215 Content Empire
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Force UTF-8 but only use ASCII output
os.environ["PYTHONUTF8"] = "1"
(
    sys.stdout.reconfigure(encoding="ascii", errors="replace")
    if hasattr(sys.stdout, "reconfigure")
    else None
)


def ascii_only(text):
    """Ensure text is pure ASCII"""
    return str(text).encode("ascii", "ignore").decode("ascii")


def safe_print(text, color_code=""):
    """Print text safely with optional color"""
    clean_text = ascii_only(text)
    if color_code:
        print(f"\033[{color_code}m{clean_text}\033[0m")
    else:
        print(clean_text)


def clear_screen():
    """Clear terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


class EQ12ASCIISafeLauncher:
    """ASCII-safe command launcher - immune to corruption"""

    def __init__(self):
        self.workspace = Path("C:/EQ12")
        self.scripts_dir = self.workspace / "scripts"
        self.logs_dir = self.workspace / "logs"
        self.status = self._check_system_status()

    def _check_system_status(self):
        """Check system status without Unicode"""
        critical_files = [
            "eq12_run_odds.py",
            "eq12_run_parlay.py",
            "eq12_betting_suite.py",
            "eq12_master_revenue_orchestrator.py",
        ]

        files_found = 0
        for file in critical_files:
            if (self.scripts_dir / file).exists() or (self.workspace / file).exists():
                files_found += 1

        health_score = (files_found / len(critical_files)) * 100

        return {
            "health_score": health_score,
            "files_found": files_found,
            "total_files": len(critical_files),
            "status": "OPERATIONAL" if health_score >= 75 else "DEGRADED",
        }

    def display_header(self):
        """Display ASCII-safe header"""
        safe_print("=" * 75)
        safe_print("EQ12 ASCII-SAFE LAUNCHER v1.0 - BUFFALO NY 14215", "96")
        safe_print("CORRUPTION-IMMUNE COMMAND CENTER", "93")
        safe_print("=" * 75)
        safe_print(
            f"STATUS: {self.status['status']}",
            "92" if self.status["status"] == "OPERATIONAL" else "91",
        )
        safe_print(
            f"HEALTH: {self.status['health_score']:.1f}% ({self.status['files_found']}/{self.status['total_files']} modules)",
            "92",
        )
        safe_print("CONTENT EMPIRE: ACTIVE", "92")
        safe_print("=" * 75)

    def display_menu(self):
        """Display command menu"""
        safe_print("\nREVENUE AND BETTING OPERATIONS:")
        safe_print("  1   run-odds         -> High-frequency market data feed")
        safe_print("  2   run-parlay       -> AI parlay constructor")
        safe_print("  3   betting-suite    -> Full betting pipeline")
        safe_print("  4   revenue-cycle    -> Complete revenue generation")

        safe_print("\nSYSTEM MANAGEMENT:")
        safe_print("  5   health-check     -> System validation")
        safe_print("  6   repair-all       -> Auto-repair tools")
        safe_print("  7   safe-run         -> Protected script execution")
        safe_print("  8   integrity-check  -> File corruption scan")

        safe_print("\nDATA AND ANALYTICS:")
        safe_print("  9   build-dashboard  -> Generate dashboard")
        safe_print("  10  export-data      -> Export data files")
        safe_print("  11  live-metrics     -> Real-time monitoring")
        safe_print("  12  backup-system    -> Create full backup")

        safe_print("\nEMERGENCY OPERATIONS:")
        safe_print("  99  emergency-mode   -> Crisis recovery")
        safe_print("  exit                 -> Quit launcher")
        safe_print("=" * 75)

    def execute_command(self, cmd_input):
        """Execute command safely"""
        cmd = ascii_only(cmd_input.strip().lower())

        if cmd == "exit":
            return False

        # Command mapping
        commands = {
            "1": ("run-odds", "eq12_run_odds.py", ["--mode", "single", "--verbose"]),
            "2": ("run-parlay", "eq12_run_parlay.py", ["--legs", "3", "--count", "1"]),
            "3": ("betting-suite", "eq12_betting_suite.py", ["--mode", "sequential"]),
            "4": (
                "revenue-cycle",
                "eq12_master_revenue_orchestrator.py",
                ["--mode", "comprehensive"],
            ),
            "5": ("health-check", "eq12_system_integrity_validator.py", []),
            "6": ("repair-all", "eq12_global_ps_repair_v2.ps1", []),
            "7": ("safe-run", "eq12_safe_run.cmd", []),
            "8": ("integrity-check", "eq12_system_integrity_validator.py", []),
            "9": ("build-dashboard", "eq12_build_dashboard.py", []),
            "10": ("export-data", "eq12_export_data.py", []),
            "11": ("live-metrics", "eq12_live_metrics.py", []),
            "12": ("backup-system", "eq12_backup_system.py", []),
            "99": ("emergency-mode", "eq12_emergency_repair.ps1", ["-AutoFix"]),
        }

        if cmd not in commands:
            safe_print(f"ERROR: Unknown command: {cmd}", "91")
            return True

        name, script, args = commands[cmd]
        safe_print(f"\nEXECUTING: {name}", "93")
        safe_print("-" * 60)

        # Find script
        script_path = self.scripts_dir / script
        if not script_path.exists():
            script_path = self.workspace / script

        if not script_path.exists():
            safe_print(f"ERROR: Script not found: {script}", "91")
            return True

        try:
            # Execute based on file type
            if script.endswith(".py"):
                cmd_list = [sys.executable, str(script_path)] + args
            elif script.endswith(".ps1"):
                cmd_list = [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script_path),
                ] + args
            elif script.endswith(".cmd"):
                cmd_list = [str(script_path)] + args
            else:
                safe_print(f"ERROR: Unsupported script type: {script}", "91")
                return True

            start_time = time.time()
            result = subprocess.run(
                cmd_list, capture_output=True, text=True, encoding="utf-8", errors="replace"
            )
            execution_time = time.time() - start_time

            if result.returncode == 0:
                safe_print(f"SUCCESS ({execution_time:.2f}s)", "92")
                if result.stdout:
                    output = ascii_only(result.stdout[:500])
                    safe_print(f"OUTPUT:\n{output}...", "37")
            else:
                safe_print(f"FAILED (Code: {result.returncode})", "91")
                if result.stderr:
                    error = ascii_only(result.stderr[:300])
                    safe_print(f"ERROR:\n{error}...", "91")

        except Exception as e:
            safe_print(f"EXECUTION ERROR: {ascii_only(str(e))}", "91")

        safe_print("-" * 60)
        return True

    def save_session_log(self):
        """Save session log"""
        self.logs_dir.mkdir(exist_ok=True)

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "launcher_version": "ascii-safe-1.0",
            "system_status": self.status,
            "location": "Buffalo NY 14215",
        }

        log_file = (
            self.logs_dir / f"launcher_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        try:
            with open(log_file, "w", encoding="ascii", errors="replace") as f:
                json.dump(log_data, f, indent=2, ensure_ascii=True)
        except Exception:
            pass  # Fail silently to prevent corruption

    def run(self):
        """Main execution loop"""
        clear_screen()
        self.display_header()
        self.display_menu()

        safe_print("\nSELECT COMMAND (enter number or 'exit'):")

        while True:
            try:
                user_input = input("\nEQ12> ")

                if not self.execute_command(user_input):
                    break

            except KeyboardInterrupt:
                safe_print("\n\nLauncher terminated by user.", "93")
                break
            except Exception as e:
                safe_print(f"Input error: {ascii_only(str(e))}", "91")
                continue

        self.save_session_log()
        safe_print("Buffalo NY 14215 Content Empire - Session Complete!", "92")


def main():
    """Entry point"""
    launcher = EQ12ASCIISafeLauncher()
    launcher.run()


if __name__ == "__main__":
    main()
