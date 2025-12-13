#!/usr/bin/env python3
"""
EQ12 Production Status Dashboard
Real-time monitoring of EdgeFinder service and all EQ12 components.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import psutil


class EQ12StatusMonitor:
    """Production status monitor for EQ12 stack."""

    def __init__(self):
        self.eq12_root = Path("C:/EQ12")
        self.logs_dir = self.eq12_root / "logs"
        self.scripts_dir = self.eq12_root / "scripts"

    def get_service_status(self) -> dict:
        """Get status of all EQ12 services."""
        status = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "services": {},
            "files": {},
            "environment": {},
            "performance": {},
        }

        # Check EdgeFinder service
        status["services"]["edgefinder"] = self.check_process_status(
            "eq12_edgefinder.py")

        # Check key files
        key_files = [
            "eq12_math.py",
            "eq12_timezone.py",
            "eq12_parlay_builder.py",
            "eq12_responses_client.py",
            "eq12_edgefinder.py",
        ]

        for filename in key_files:
            file_path = self.scripts_dir / filename
            status["files"][filename] = {
                "exists": file_path.exists(),
                "size_kb": (
                    file_path.stat().st_size //
                    1024 if file_path.exists() else 0),
                "modified": (
                    datetime.fromtimestamp(
                        file_path.stat().st_mtime).isoformat() if file_path.exists() else None),
            }

        # Check environment variables
        env_vars = [
            "ODDS_API_KEY",
            "OPENAI_API_KEY",
            "TELEGRAM_TOKEN",
            "TELEGRAM_CHAT_ID",
        ]

        for var in env_vars:
            value = os.getenv(var)
            status["environment"][var] = {
                "configured": bool(value),
                "length": len(value) if value else 0,
            }

        # System performance
        status["performance"] = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_free_gb": psutil.disk_usage("C:").free // (1024**3),
        }

        # Recent logs
        status["recent_activity"] = self.get_recent_activity()

        return status

    def check_process_status(self, script_name: str) -> dict:
        """Check if a Python script is currently running."""
        running_processes = []

        for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
            try:
                if proc.info["name"] and "python" in proc.info["name"].lower():
                    cmdline = " ".join(proc.info["cmdline"] or [])
                    if script_name in cmdline:
                        running_processes.append(
                            {
                                "pid": proc.info["pid"],
                                "started": datetime.fromtimestamp(
                                    proc.info["create_time"]
                                ).isoformat(),
                                "cmdline": (
                                    cmdline[:100] + "..." if len(cmdline) > 100 else cmdline
                                ),
                            }
                        )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {
            "running": len(running_processes) > 0,
            "process_count": len(running_processes),
            "processes": running_processes,
        }

    def get_recent_activity(self) -> dict:
        """Get recent log activity."""
        activity = {"log_files": [], "recent_parlays": 0, "last_edgefinder_run": None}

        if not self.logs_dir.exists():
            return activity

        # Check recent log files
        for log_file in self.logs_dir.glob("*.log"):
            try:
                stat = log_file.stat()
                activity["log_files"].append(
                    {
                        "name": log_file.name,
                        "size_kb": stat.st_size // 1024,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    }
                )
            except Exception:
                continue

        # Check for recent parlay files
        parlay_files = list(self.logs_dir.glob("parlays_*.json"))
        activity["recent_parlays"] = len([f for f in parlay_files if datetime.fromtimestamp(
            f.stat().st_mtime) > datetime.now() - timedelta(hours=1)])

        # Check EdgeFinder log
        edgefinder_log = self.logs_dir / "edgefinder.log"
        if edgefinder_log.exists():
            try:
                # Read last few lines to find latest activity
                with open(edgefinder_log) as f:
                    lines = f.readlines()
                    if lines:
                        # Simple heuristic: look for timestamp in last line
                        last_line = lines[-1]
                        if last_line.strip():
                            activity["last_edgefinder_run"] = "Recently active"
            except Exception:
                pass

        return activity

    def generate_status_report(self) -> str:
        """Generate human-readable status report."""
        status = self.get_service_status()

        report = []
        report.append("🔍 EQ12 Production Status Report")
        report.append("=" * 50)
        report.append(f"Generated: {status['timestamp']}")
        report.append("")

        # Services
        report.append("🚀 Services:")
        edgefinder = status["services"]["edgefinder"]
        if edgefinder["running"]:
            report.append(
                f"  ✅ EdgeFinder: Running ({
                    edgefinder['process_count']} processes)")
        else:
            report.append("  ❌ EdgeFinder: Not running")

        report.append("")

        # Core Files
        report.append("📁 Core Files:")
        for filename, info in status["files"].items():
            if info["exists"]:
                report.append(f"  ✅ {filename}: {info['size_kb']}KB")
            else:
                report.append(f"  ❌ {filename}: Missing")

        report.append("")

        # Environment
        report.append("🔧 Environment:")
        for var, info in status["environment"].items():
            if info["configured"]:
                report.append(f"  ✅ {var}: Configured ({info['length']} chars)")
            else:
                report.append(f"  ❌ {var}: Missing")

        report.append("")

        # Performance
        perf = status["performance"]
        report.append("📊 Performance:")
        report.append(f"  CPU: {perf['cpu_percent']:.1f}%")
        report.append(f"  Memory: {perf['memory_percent']:.1f}%")
        report.append(f"  Disk Free: {perf['disk_free_gb']}GB")

        report.append("")

        # Recent Activity
        activity = status["recent_activity"]
        report.append("⚡ Recent Activity:")
        report.append(f"  Log files: {len(activity['log_files'])}")
        report.append(f"  Parlays (last hour): {activity['recent_parlays']}")
        if activity["last_edgefinder_run"]:
            report.append(f"  EdgeFinder: {activity['last_edgefinder_run']}")

        return "\n".join(report)

    def save_status_snapshot(self):
        """Save detailed status to JSON file."""
        status = self.get_service_status()

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = self.logs_dir / f"status_snapshot_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(status, f, indent=2)

        print(f"📊 Status snapshot saved: {filename.name}")


def main():
    """Main entry point for status monitoring."""
    monitor = EQ12StatusMonitor()

    # Generate and display status report
    report = monitor.generate_status_report()
    print(report)
    print()

    # Save detailed snapshot
    monitor.save_status_snapshot()

    # Offer to start EdgeFinder if not running
    status = monitor.get_service_status()
    if not status["services"]["edgefinder"]["running"]:
        print("💡 EdgeFinder is not running. Start it with:")
        print("   python C:/EQ12/scripts/eq12_edgefinder.py")


if __name__ == "__main__":
    main()
