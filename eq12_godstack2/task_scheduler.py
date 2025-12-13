#!/usr/bin/env python3
"""
EQ12 GODSTACK Task Scheduler Controller
Automated task execution wrapper for Windows Task Scheduler integration.

Author: EQ12 AI Assistant
Created: 2025-01-27
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

# Setup logging
LOG_DIR = Path("C:/EQ12/logs") if os.name == "nt" else Path("/workspaces/EQ12/logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "eq12_scheduler.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


class EQ12TaskScheduler:
    """Task scheduler controller for automated GODSTACK operations"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.log_dir = LOG_DIR

        # Task configurations
        self.tasks = {
            "news_collection": {
                "script": "news_aggregator.py",
                "args": ["--query", "general", "--auto"],
                "description": "Collect latest news from multiple sources",
            },
            "offers_scraping": {
                "script": "swagbucks_offers.py",
                "args": ["--auto"],
                "description": "Scrape Swagbucks offers and deals",
            },
            "meta_search": {
                "script": "meta_search.py",
                "args": ["--auto-queries", "--popular"],
                "description": "Execute popular search queries",
            },
            "enrichment_analysis": {
                "script": "enrichment.py",
                "args": ["--hours", "24", "--auto"],
                "description": "Generate GPT analysis of recent data",
            },
            "autosuggest_generation": {
                "script": "autosuggest_merge.py",
                "args": ["--trending", "--auto"],
                "description": "Generate trending keyword suggestions",
            },
        }

    def run_task(self, task_name: str) -> dict:
        """Execute a scheduled task"""

        if task_name not in self.tasks:
            raise ValueError(f"Unknown task: {task_name}")

        task = self.tasks[task_name]

        logger.info(f"Starting task: {task_name}")
        logger.info(f"Description: {task['description']}")

        try:
            # Prepare command
            cmd = ["python", task["script"]] + task["args"]

            logger.info(f"Executing: {' '.join(cmd)}")

            # Execute with timeout
            result = subprocess.run(
                cmd,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Create execution report
            report = {
                "task_name": task_name,
                "timestamp": datetime.now(UTC).isoformat(),
                "command": " ".join(cmd),
                "return_code": result.returncode,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "description": task["description"],
            }

            # Save report
            report_file = (
                self.log_dir
                / f"task_report_{task_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            if report["success"]:
                logger.info(f"Task {task_name} completed successfully")
            else:
                logger.error(f"Task {task_name} failed with code {result.returncode}")
                logger.error(f"Error: {result.stderr}")

            return report

        except subprocess.TimeoutExpired:
            logger.error(f"Task {task_name} timed out")
            return {
                "task_name": task_name,
                "timestamp": datetime.now(UTC).isoformat(),
                "success": False,
                "error": "Task execution timed out",
            }
        except Exception as e:
            logger.error(f"Error executing task {task_name}: {e}")
            return {
                "task_name": task_name,
                "timestamp": datetime.now(UTC).isoformat(),
                "success": False,
                "error": str(e),
            }

    def run_sequence(self, task_sequence: list) -> dict:
        """Run a sequence of tasks"""

        logger.info(f"Starting task sequence: {task_sequence}")

        sequence_report = {
            "sequence": task_sequence,
            "start_time": datetime.now(UTC).isoformat(),
            "tasks": [],
            "success_count": 0,
            "failure_count": 0,
        }

        for task_name in task_sequence:
            report = self.run_task(task_name)
            sequence_report["tasks"].append(report)

            if report["success"]:
                sequence_report["success_count"] += 1
            else:
                sequence_report["failure_count"] += 1

        sequence_report["end_time"] = datetime.now(UTC).isoformat()
        sequence_report["overall_success"] = sequence_report["failure_count"] == 0

        # Save sequence report
        sequence_file = (
            self.log_dir / f"sequence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(sequence_file, "w") as f:
            json.dump(sequence_report, f, indent=2)

        logger.info(
            f"Sequence completed: {sequence_report['success_count']} success, {sequence_report['failure_count']} failures"
        )

        return sequence_report

    def list_tasks(self) -> dict:
        """List available tasks"""
        return {name: task["description"] for name, task in self.tasks.items()}


def main():
    parser = argparse.ArgumentParser(description="EQ12 GODSTACK Task Scheduler")
    parser.add_argument("--task", type=str, help="Execute specific task")
    parser.add_argument("--sequence", type=str, nargs="+", help="Execute task sequence")
    parser.add_argument("--list", action="store_true", help="List available tasks")
    parser.add_argument("--daily", action="store_true", help="Run daily collection sequence")
    parser.add_argument("--hourly", action="store_true", help="Run hourly update sequence")

    args = parser.parse_args()

    scheduler = EQ12TaskScheduler()

    try:
        if args.list:
            # List available tasks
            tasks = scheduler.list_tasks()
            print("\nAvailable EQ12 GODSTACK Tasks:")
            print("=" * 50)
            for name, description in tasks.items():
                print(f"📋 {name}: {description}")
            return None

        if args.task:
            # Execute single task
            report = scheduler.run_task(args.task)
            print(f"Task {args.task}: {'✅ SUCCESS' if report['success'] else '❌ FAILED'}")
            if not report["success"]:
                print(f"Error: {report.get('error', 'Unknown error')}")

        elif args.sequence:
            # Execute task sequence
            report = scheduler.run_sequence(args.sequence)
            print(
                f"Sequence: {report['success_count']} success, {report['failure_count']} failures"
            )

        elif args.daily:
            # Daily collection sequence
            daily_tasks = ["news_collection", "offers_scraping", "enrichment_analysis"]
            report = scheduler.run_sequence(daily_tasks)
            print(
                f"Daily sequence: {'✅ SUCCESS' if report['overall_success'] else '❌ PARTIAL FAILURE'}"
            )

        elif args.hourly:
            # Hourly update sequence
            hourly_tasks = ["autosuggest_generation", "meta_search"]
            report = scheduler.run_sequence(hourly_tasks)
            print(
                f"Hourly sequence: {'✅ SUCCESS' if report['overall_success'] else '❌ PARTIAL FAILURE'}"
            )

        else:
            parser.print_help()

    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        print(f"❌ Scheduler error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
