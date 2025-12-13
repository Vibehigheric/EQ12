#!/usr/bin/env python3
"""
EQ12 God Mode Commander - Simplified Version
One-click launcher for all EQ12 systems with comprehensive monitoring

This script demonstrates the EQ12 ecosystem integration:
- Java Gmail automation
- Advanced Python patterns
- System health monitoring
- Real-time dashboard
- Legal compliance framework
"""

import logging
import subprocess
import sys
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/godmode_simple.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EQ12GodModeCommander:
    """Simplified God Mode Commander for EQ12 systems"""

    def __init__(self, eq12_root: str = "C:/EQ12"):
        self.eq12_root = Path(eq12_root)
        self.processes: dict[str, subprocess.Popen] = {}
        self.god_mode_active = False

    def show_banner(self):
        """Display EQ12 banner"""
        banner = """
█████████████████████████████████████████████████████████████████████████████
█                                                                           █
█    ███████  ███████  ████    ██████      ████████████   █████    █████    █
█    ██       ██    ██  ██      ██   ██    ██             ██   ██  ██   ██   █
█    █████    ███████   ██      ██████     ██  ████████   █████    █████     █
█    ██       ██   ██   ██      ██   ██    ██       ██    ██  ██   ██  ██    █
█    ███████  ██    ██ ████    ██    ██     ████████████   ██   ██  ██   ██   █
█                                                                           █
█                    GOD MODE COMMANDER - SYSTEM ORCHESTRATOR               █
█                    Expert Java & Python Integration Demo                  █
█                                                                           █
█████████████████████████████████████████████████████████████████████████████
"""
        print(banner)
        print("🚀 EQ12 GOD MODE COMMANDER - Ultimate System Control")
        print("=" * 80)

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("C:/")

            # Check EQ12 modules
            modules = {
                "Backtester": (self.eq12_root / "eq12_backtester" / "run.py").exists(),
                "Java Integration": (self.eq12_root / "eq12_java_integration" / "pom.xml").exists(),
                "Chrome Automation": (self.eq12_root / "chrome_governance_automation.py").exists(),
                "System Scanner": (self.eq12_root / "eq12_system_scanner.py").exists(),
                "Enhanced Python": (self.eq12_root / "eq12_enhanced_python.py").exists(),
                "Unified Dashboard": (self.eq12_root / "eq12_unified_dashboard.py").exists(),
            }

            # Count EQ12 processes
            eq12_processes = []
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    if any(
                        keyword in proc.info["name"].lower()
                        for keyword in ["python", "java", "chrome", "firefox"]
                    ):
                        eq12_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Calculate health score
            health_score = 100
            if cpu_percent > 80:
                health_score -= 20
            if memory.percent > 85:
                health_score -= 20
            if disk.percent > 90:
                health_score -= 30

            return {
                "timestamp": datetime.now().isoformat(),
                "god_mode_active": self.god_mode_active,
                "health_score": max(0, health_score),
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent,
                "modules": modules,
                "active_processes": len(eq12_processes),
                "eq12_size_mb": self._get_directory_size(self.eq12_root) / (1024 * 1024),
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        try:
            total = 0
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    total += file_path.stat().st_size
            return total
        except Exception:
            return 0

    def show_status_dashboard(self):
        """Display system status dashboard"""
        status = self.get_system_status()

        print("\n📊 EQ12 SYSTEM STATUS DASHBOARD")
        print("-" * 80)

        # System Health
        health_color = (
            "🟢" if status["health_score"] > 80 else "🟡" if status["health_score"] > 60 else "🔴"
        )
        print(f"🏥 System Health: {health_color} {status['health_score']:.1f}%")
        print(f"   CPU Usage: {status['cpu_usage']:.1f}%")
        print(f"   Memory Usage: {status['memory_usage']:.1f}%")
        print(f"   Disk Usage: {status['disk_usage']:.1f}%")

        # Module Status
        print("\n🔧 EQ12 Modules:")
        for module, exists in status["modules"].items():
            status_emoji = "✅" if exists else "❌"
            print(f"   {status_emoji} {module}")

        # Resources
        print("\n💾 System Resources:")
        print(f"   Active Processes: {status['active_processes']}")
        print(f"   EQ12 Size: {status['eq12_size_mb']:.1f} MB")
        print(f"   God Mode: {'🟢 ACTIVE' if status['god_mode_active'] else '⚫ INACTIVE'}")

        print(f"\n🕐 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def activate_god_mode(self) -> dict[str, Any]:
        """Activate God Mode - launch all EQ12 systems"""
        logger.info("🚀 ACTIVATING EQ12 GOD MODE")
        self.god_mode_active = True

        # Define systems to launch
        systems = [
            {
                "name": "EQ12 System Scanner",
                "command": ["python", str(self.eq12_root / "eq12_system_scanner.py")],
                "background": False,
            },
            {
                "name": "Chrome Governance Automation",
                "command": [
                    "python",
                    str(self.eq12_root / "chrome_governance_automation.py"),
                    "--setup-profile",
                ],
                "background": True,
            },
            {
                "name": "EQ12 Backtester",
                "command": [
                    "python",
                    str(self.eq12_root / "eq12_backtester" / "run.py"),
                    "--help",
                ],
                "background": False,
            },
        ]

        launched = []
        failed = []

        print("\n🚀 LAUNCHING GOD MODE SYSTEMS...")
        print("-" * 50)

        for system in systems:
            try:
                print(f"   Launching {system['name']}... ", end="", flush=True)

                if not Path(system["command"][1]).exists():
                    print("❌ File not found")
                    failed.append(f"{system['name']} - File not found")
                    continue

                if system["background"]:
                    proc = subprocess.Popen(
                        system["command"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=(
                            subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                        ),
                    )
                    self.processes[system["name"]] = proc
                    print(f"✅ Started (PID: {proc.pid})")
                else:
                    subprocess.run(system["command"], capture_output=True, text=True, timeout=30)
                    print("✅ Completed")

                launched.append(system["name"])
                time.sleep(1)

            except Exception as e:
                print(f"❌ Error: {e}")
                failed.append(f"{system['name']} - {e!s}")

        # Launch Java Gmail Bot if available
        java_dir = self.eq12_root / "eq12_java_integration"
        if java_dir.exists() and (java_dir / "pom.xml").exists():
            try:
                print("   Launching Java Gmail Automation Bot... ", end="", flush=True)
                subprocess.run(
                    [
                        "mvn",
                        "compile",
                        "exec:java",
                        "-Dexec.mainClass=EQ12EmailAutomationBot",
                    ],
                    cwd=java_dir,
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                print("✅ Java integration ready")
                launched.append("Java Gmail Bot")
            except Exception as e:
                print(f"❌ Java error: {e}")
                failed.append(f"Java Gmail Bot - {e!s}")

        # Launch dashboard if available
        dashboard_file = self.eq12_root / "eq12_unified_dashboard.py"
        if dashboard_file.exists():
            try:
                print("   Launching Unified Dashboard... ", end="", flush=True)
                proc = subprocess.Popen(
                    ["python", str(dashboard_file), "--port", "8080"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0),
                )
                self.processes["Dashboard"] = proc
                print("✅ Started on http://localhost:8080")
                launched.append("Unified Dashboard")

                # Open browser after delay
                import threading

                threading.Timer(3.0, lambda: webbrowser.open("http://localhost:8080")).start()

            except Exception as e:
                print(f"❌ Dashboard error: {e}")
                failed.append(f"Unified Dashboard - {e!s}")

        # Summary
        print("\n✅ GOD MODE ACTIVATION SUMMARY:")
        print(f"   Successfully Launched: {len(launched)} systems")
        print(f"   Failed Launches: {len(failed)} systems")

        if launched:
            print("\n🟢 LAUNCHED SYSTEMS:")
            for system in launched:
                print(f"   • {system}")

        if failed:
            print("\n🔴 FAILED SYSTEMS:")
            for system in failed:
                print(f"   • {system}")

        print("\n🎉 EQ12 GOD MODE ACTIVATED!")
        print("   Monitor systems at: http://localhost:8080")

        return {
            "launched": launched,
            "failed": failed,
            "total_processes": len(self.processes),
        }

    def deactivate_god_mode(self) -> dict[str, Any]:
        """Deactivate God Mode - stop all processes"""
        logger.info("🛑 DEACTIVATING EQ12 GOD MODE")
        self.god_mode_active = False

        stopped = []
        failed = []

        print("\n🛑 STOPPING GOD MODE SYSTEMS...")
        print("-" * 50)

        for name, proc in self.processes.items():
            try:
                if proc.poll() is None:  # Still running
                    print(f"   Stopping {name}... ", end="", flush=True)
                    proc.terminate()

                    try:
                        proc.wait(timeout=5)
                        print("✅ Stopped")
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        print("✅ Terminated")

                    stopped.append(name)
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
                failed.append(f"{name} - {e!s}")

        self.processes.clear()

        print("\n✅ GOD MODE DEACTIVATION SUMMARY:")
        print(f"   Stopped Processes: {len(stopped)}")
        print(f"   Failed Stops: {len(failed)}")
        print("\n🔴 EQ12 GOD MODE DEACTIVATED")

        return {"stopped": stopped, "failed": failed}

    def show_legal_compliance(self):
        """Show legal compliance information"""
        print("\n⚖️ LEGAL COMPLIANCE FRAMEWORK")
        print("=" * 80)
        print("🚨 IMPORTANT: Betting & Gambling Disclaimer")
        print("-" * 50)
        print("• Educational Use Only: EQ12 is for research and educational purposes")
        print("• Age Verification: Must be 21+ years old to use betting features")
        print("• Responsible Gaming: Only bet what you can afford to lose")
        print("• No Guarantees: Past performance does not guarantee future results")
        print("• Local Laws: Users must comply with all applicable local laws")
        print("\n📞 Problem Gambling Resources:")
        print("• National Council on Problem Gambling: ncpgambling.org")
        print("• Gamblers Anonymous: gamblersanonymous.org")
        print("• SAMHSA Helpline: 1-800-662-4357")
        print("\n⚠️ Risk Warning: All betting involves risk of financial loss")

    def run_interactive(self):
        """Run interactive God Mode Commander"""
        while True:
            self.show_banner()
            self.show_status_dashboard()

            print("\n🎮 EQ12 GOD MODE COMMANDER MENU")
            print("-" * 50)
            print("1. 🚀 Activate God Mode (Launch All Systems)")
            print("2. 🛑 Deactivate God Mode (Stop All Systems)")
            print("3. 📊 Refresh System Status")
            print("4. 🌐 Open Dashboard (http://localhost:8080)")
            print("5. ⚖️ Legal Compliance Information")
            print("6. 🔄 Run System Scanner")
            print("7. ☕ Demo Java Gmail Bot")
            print("8. 🐍 Demo Advanced Python Patterns")
            print("0. ❌ Exit")

            try:
                choice = input("\nSelect option (0-8): ").strip()

                if choice == "1":
                    print("\n🚨 WARNING: This will launch all EQ12 systems!")
                    confirm = input("Continue? (y/N): ").strip().lower()
                    if confirm == "y":
                        self.activate_god_mode()
                        input("\nPress Enter to continue...")

                elif choice == "2":
                    if self.god_mode_active or self.processes:
                        self.deactivate_god_mode()
                        input("\nPress Enter to continue...")
                    else:
                        print("\n⚠️ God Mode is not currently active.")
                        time.sleep(2)

                elif choice == "3":
                    print("\n🔄 Refreshing system status...")
                    time.sleep(1)
                    continue

                elif choice == "4":
                    print("\n🌐 Opening dashboard...")
                    webbrowser.open("http://localhost:8080")
                    time.sleep(2)

                elif choice == "5":
                    self.show_legal_compliance()
                    input("\nPress Enter to continue...")

                elif choice == "6":
                    scanner_file = self.eq12_root / "eq12_system_scanner.py"
                    if scanner_file.exists():
                        print("\n🔄 Running EQ12 System Scanner...")
                        try:
                            subprocess.run(
                                ["python", str(scanner_file)],
                                cwd=self.eq12_root,
                                timeout=60,
                            )
                            print("✅ System scan completed")
                        except Exception as e:
                            print(f"❌ Scanner error: {e}")
                    else:
                        print("❌ System scanner not found")
                    input("\nPress Enter to continue...")

                elif choice == "7":
                    java_dir = self.eq12_root / "eq12_java_integration"
                    if java_dir.exists():
                        print("\n☕ Demonstrating Java Gmail Automation Bot...")
                        print("📧 Features: OAuth2 authentication, email processing, notifications")
                        print("🔧 Technologies: Java 17+, Gmail API, SQLite, Maven")
                        print("📁 Location: eq12_java_integration/EQ12EmailAutomationBot.java")
                    else:
                        print("❌ Java integration not found")
                    input("\nPress Enter to continue...")

                elif choice == "8":
                    python_file = self.eq12_root / "eq12_enhanced_python.py"
                    if python_file.exists():
                        print("\n🐍 Demonstrating Advanced Python Patterns...")
                        print("✨ Features: Dataclasses, async/await, type hints, decorators")
                        print("🔧 Technologies: Python 3.8+, asyncio, typing, context managers")
                        print("📁 Location: eq12_enhanced_python.py")
                    else:
                        print("❌ Enhanced Python module not found")
                    input("\nPress Enter to continue...")

                elif choice == "0":
                    if self.god_mode_active or self.processes:
                        confirm = (
                            input(
                                "\n🛑 God Mode is active. Stop all processes before exiting? (y/N): "
                            )
                            .strip()
                            .lower()
                        )
                        if confirm == "y":
                            self.deactivate_god_mode()

                    print("\n👋 Goodbye! EQ12 God Mode Commander shutting down...")
                    logger.info("God Mode Commander session ended")
                    break

                else:
                    print("\n❌ Invalid option. Please select 0-8.")
                    time.sleep(2)

            except KeyboardInterrupt:
                print("\n\n🛑 Interrupted by user")
                if self.god_mode_active or self.processes:
                    print("Stopping all processes...")
                    self.deactivate_god_mode()
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                time.sleep(2)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 God Mode Commander")
    parser.add_argument(
        "--action",
        choices=["start", "stop", "status", "interactive"],
        default="interactive",
        help="Action to perform",
    )
    parser.add_argument("--eq12-root", default="C:/EQ12", help="EQ12 root directory")

    args = parser.parse_args()

    try:
        commander = EQ12GodModeCommander(args.eq12_root)

        if args.action == "start":
            commander.show_banner()
            commander.activate_god_mode()
        elif args.action == "stop":
            commander.show_banner()
            commander.deactivate_god_mode()
        elif args.action == "status":
            commander.show_banner()
            commander.show_status_dashboard()
        else:  # interactive
            commander.run_interactive()

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
