#!/usr/bin/env python3
"""
EQ12 Production Automation Orchestrator
Coordinates forum learning, issue creation, and NFL content generation.

Usage:
    python eq12_production_orchestrator.py --full-cycle
    python eq12_production_orchestrator.py --nfl-only
    python eq12_production_orchestrator.py --monitor
"""

import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/orchestrator.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class AutomationTask:
    """Represents an automated task"""

    name: str
    command: list[str]
    schedule_time: str
    enabled: bool
    last_run: datetime | None = None
    next_run: datetime | None = None


class EQ12ProductionOrchestrator:
    """Coordinates all EQ12 automation systems"""

    def __init__(self):
        self.base_dir = Path("C:/EQ12")
        self.logs_dir = self.base_dir / "logs"
        self.data_dir = self.base_dir / "data"

        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

        # Rate limiting configuration
        self.rate_limits = {
            "github_api": {"requests_per_hour": 5000, "current_hour_count": 0},
            "forum_scraping": {"requests_per_hour": 30, "current_hour_count": 0},
            "post_creation": {"posts_per_day": 10, "current_day_count": 0},
        }

        # Budget guards
        self.budget_limits = {
            "openai_daily": float(os.getenv("OPENAI_DAILY_BUDGET", "50.0")),
            "current_spend": 0.0,
            "betting_daily": float(os.getenv("BETTING_DAILY_LIMIT", "100.0")),
            "current_betting": 0.0,
        }

        # Task definitions
        self.automation_tasks = [
            AutomationTask(
                name="forum_intelligence_gathering",
                command=["python", "eq12_forum_learner.py", "--report"],
                schedule_time="daily_06:00",
                enabled=True,
            ),
            AutomationTask(
                name="github_issue_creation",
                command=["python", "eq12_forum_actions.py", "--create-issues", "--max-issues", "3"],
                schedule_time="daily_07:00",
                enabled=True,
            ),
            AutomationTask(
                name="nfl_content_generation",
                command=["python", "eq12_nfl_week6_seeder.py", "--generate-posts", "--export-json"],
                schedule_time="daily_08:00",
                enabled=True,
            ),
            AutomationTask(
                name="bills_megaparlay_analysis",
                command=["python", "eq12_bills_analyzer.py", "--update-parlay", "--live-odds"],
                schedule_time="hourly_during_games",
                enabled=True,
            ),
            AutomationTask(
                name="budget_guard_check",
                command=["python", "eq12_opsbot/budget_guard.py", "--check-all"],
                schedule_time="every_15_minutes",
                enabled=True,
            ),
        ]

    def check_rate_limits(self, service: str) -> bool:
        """Check if service is within rate limits"""
        if service not in self.rate_limits:
            return True

        limits = self.rate_limits[service]
        current_hour = datetime.now().hour

        # Reset hourly counters
        if not hasattr(self, "_last_hour_check"):
            self._last_hour_check = current_hour

        if current_hour != self._last_hour_check:
            for service_name in self.rate_limits:
                self.rate_limits[service_name]["current_hour_count"] = 0
            self._last_hour_check = current_hour

        # Check limit
        if "requests_per_hour" in limits:
            return limits["current_hour_count"] < limits["requests_per_hour"]
        elif "posts_per_day" in limits:
            return limits["current_day_count"] < limits["posts_per_day"]

        return True

    def increment_rate_limit(self, service: str) -> None:
        """Increment rate limit counter"""
        if service in self.rate_limits:
            if "current_hour_count" in self.rate_limits[service]:
                self.rate_limits[service]["current_hour_count"] += 1
            if "current_day_count" in self.rate_limits[service]:
                self.rate_limits[service]["current_day_count"] += 1

    def check_budget_guards(self) -> bool:
        """Check if within budget limits"""
        if self.budget_limits["current_spend"] >= self.budget_limits["openai_daily"]:
            logger.warning(
                f"OpenAI daily budget exceeded: ${self.budget_limits['current_spend']:.2f}"
            )
            return False

        if self.budget_limits["current_betting"] >= self.budget_limits["betting_daily"]:
            logger.warning(
                f"Betting daily limit exceeded: ${self.budget_limits['current_betting']:.2f}"
            )
            return False

        return True

    def execute_task(self, task: AutomationTask) -> dict[str, Any]:
        """Execute an automation task with safety guards"""
        logger.info(f"Executing task: {task.name}")

        # Check rate limits
        if not self.check_rate_limits("github_api"):
            return {"error": "Rate limit exceeded", "task": task.name}

        # Check budget guards
        if not self.check_budget_guards():
            return {"error": "Budget limit exceeded", "task": task.name}

        try:
            # Execute command
            result = subprocess.run(
                task.command,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            task.last_run = datetime.now(UTC)

            # Log results
            task_result = {
                "task": task.name,
                "timestamp": task.last_run.isoformat(),
                "exit_code": result.returncode,
                "stdout": result.stdout[-1000:] if result.stdout else "",  # Last 1000 chars
                "stderr": result.stderr[-1000:] if result.stderr else "",
                "success": result.returncode == 0,
            }

            # Save task log
            task_log_file = (
                self.logs_dir / f"task_{task.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with task_log_file.open("w", encoding="utf-8") as f:
                json.dump(task_result, f, indent=2)

            if result.returncode == 0:
                logger.info(f"Task {task.name} completed successfully")
                self.increment_rate_limit("github_api")
            else:
                logger.error(f"Task {task.name} failed with exit code {result.returncode}")

            return task_result

        except subprocess.TimeoutExpired:
            logger.error(f"Task {task.name} timed out")
            return {"error": "Timeout", "task": task.name}
        except Exception as e:
            logger.error(f"Task {task.name} failed: {e}")
            return {"error": str(e), "task": task.name}

    def run_full_cycle(self) -> dict[str, Any]:
        """Run complete automation cycle"""
        logger.info("Starting full EQ12 automation cycle")

        cycle_results = {
            "cycle_start": datetime.now(UTC).isoformat(),
            "tasks_executed": [],
            "errors": [],
            "summary": {},
        }

        # Execute tasks in order
        for task in self.automation_tasks:
            if not task.enabled:
                continue

            result = self.execute_task(task)
            cycle_results["tasks_executed"].append(result)

            if "error" in result:
                cycle_results["errors"].append(result)

            # Brief pause between tasks
            time.sleep(5)

        # Generate summary
        successful_tasks = [r for r in cycle_results["tasks_executed"] if r.get("success", False)]
        cycle_results["summary"] = {
            "total_tasks": len(self.automation_tasks),
            "executed_tasks": len(cycle_results["tasks_executed"]),
            "successful_tasks": len(successful_tasks),
            "failed_tasks": len(cycle_results["errors"]),
            "cycle_duration_seconds": (
                datetime.now(UTC)
                - datetime.fromisoformat(cycle_results["cycle_start"].replace("Z", "+00:00"))
            ).total_seconds(),
        }

        # Save cycle results
        cycle_file = (
            self.logs_dir / f"automation_cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with cycle_file.open("w", encoding="utf-8") as f:
            json.dump(cycle_results, f, indent=2)

        logger.info(f"Automation cycle complete. Results saved to {cycle_file}")
        return cycle_results

    def run_nfl_focus(self) -> dict[str, Any]:
        """Run NFL-focused automation (Bills mega-parlay + Week 6 content)"""
        logger.info("Starting NFL-focused automation")

        nfl_tasks = [
            task for task in self.automation_tasks if "nfl" in task.name or "bills" in task.name
        ]

        results = []
        for task in nfl_tasks:
            if task.enabled:
                result = self.execute_task(task)
                results.append(result)
                time.sleep(3)

        nfl_result = {
            "focus": "NFL Week 6",
            "timestamp": datetime.now(UTC).isoformat(),
            "tasks_executed": results,
            "bills_parlay_ready": any("bills" in str(r) for r in results),
        }

        return nfl_result

    def setup_scheduling(self) -> None:
        """Setup automated scheduling for all tasks"""
        logger.info("Setting up automated task scheduling")

        # Daily tasks
        schedule.every().day.at("06:00").do(
            lambda: self.execute_task(
                next(t for t in self.automation_tasks if t.name == "forum_intelligence_gathering")
            )
        )

        schedule.every().day.at("07:00").do(
            lambda: self.execute_task(
                next(t for t in self.automation_tasks if t.name == "github_issue_creation")
            )
        )

        schedule.every().day.at("08:00").do(
            lambda: self.execute_task(
                next(t for t in self.automation_tasks if t.name == "nfl_content_generation")
            )
        )

        # Budget checks every 15 minutes
        schedule.every(15).minutes.do(
            lambda: self.execute_task(
                next(t for t in self.automation_tasks if t.name == "budget_guard_check")
            )
        )

        # Game day hourly (during NFL games)
        if self._is_game_day():
            schedule.every().hour.do(
                lambda: self.execute_task(
                    next(t for t in self.automation_tasks if t.name == "bills_megaparlay_analysis")
                )
            )

    def _is_game_day(self) -> bool:
        """Check if today is an NFL game day"""
        today = datetime.now().weekday()
        return today in [0, 3, 6]  # Monday, Thursday, Sunday

    def monitor_mode(self) -> None:
        """Run in continuous monitoring mode"""
        logger.info("Starting EQ12 monitoring mode")

        self.setup_scheduling()

        try:
            while True:
                schedule.run_pending()

                # Health check every hour
                if datetime.now().minute == 0:
                    self._health_check()

                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")

    def _health_check(self) -> dict[str, Any]:
        """Perform system health check"""
        health = {
            "timestamp": datetime.now(UTC).isoformat(),
            "rate_limits": self.rate_limits,
            "budget_status": self.budget_limits,
            "disk_space": self._check_disk_space(),
            "log_file_count": len(list(self.logs_dir.glob("*.log"))),
            "cache_size_mb": self._calculate_cache_size(),
        }

        # Log health status
        health_file = (
            self.logs_dir / f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with health_file.open("w", encoding="utf-8") as f:
            json.dump(health, f, indent=2)

        return health

    def _check_disk_space(self) -> dict[str, Any]:
        """Check available disk space"""
        try:
            import shutil

            total, used, free = shutil.disk_usage(self.base_dir)
            return {
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "usage_percent": round((used / total) * 100, 1),
            }
        except Exception as e:
            return {"error": str(e)}

    def _calculate_cache_size(self) -> float:
        """Calculate total cache size in MB"""
        try:
            total_size = 0
            for file_path in self.data_dir.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return round(total_size / (1024**2), 2)  # MB
        except Exception:
            return 0.0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Production Automation Orchestrator")
    parser.add_argument(
        "--full-cycle", action="store_true", help="Run complete automation cycle once"
    )
    parser.add_argument("--nfl-only", action="store_true", help="Run NFL-focused automation only")
    parser.add_argument("--monitor", action="store_true", help="Run in continuous monitoring mode")
    parser.add_argument("--health-check", action="store_true", help="Perform system health check")

    args = parser.parse_args()

    orchestrator = EQ12ProductionOrchestrator()

    if args.full_cycle:
        result = orchestrator.run_full_cycle()
        print(json.dumps(result["summary"], indent=2))

    elif args.nfl_only:
        result = orchestrator.run_nfl_focus()
        print(json.dumps(result, indent=2))

    elif args.monitor:
        orchestrator.monitor_mode()

    elif args.health_check:
        health = orchestrator._health_check()
        print(json.dumps(health, indent=2))

    else:
        print("🚀 EQ12 Production Automation Orchestrator")
        print("\nAvailable commands:")
        print("  --full-cycle    Run complete automation cycle")
        print("  --nfl-only      Focus on NFL Week 6 content")
        print("  --monitor       Continuous monitoring mode")
        print("  --health-check  System health status")
        print("\n⚡ Ready for NFL Week 6 automation!")


if __name__ == "__main__":
    main()
