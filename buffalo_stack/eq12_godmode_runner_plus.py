#!/usr/bin/env python3
"""
EQ12 Godmode Runner Plus (Buffalo Stack Integration)
- Runs all automation modules in sequence
- Anchors Civil Service Tracker for 14215 (union jobs)
- Hooks betting, travel, dropship bots if present
- Integrates with ChatGPT refactoring when API key is provided
"""

import argparse
import datetime
import json
import logging
import os
import pathlib
import subprocess
import sys
from typing import Any

# Import EQ12 standardized configuration
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from eq12_config import load_eq12_env, setup_eq12_logging

BASE = pathlib.Path(__file__).resolve().parent
LOGS = BASE / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

# Load environment variables at startup using standardized function
load_eq12_env()

# Set up standardized logging
logger = setup_eq12_logging(__name__, log_level=logging.INFO)
logfile = LOGS / f"eq12_runner_{datetime.date.today()}.log"


def prompt_for_api_keys() -> dict[str, str]:
    """Prompt for API keys if not set in environment"""
    api_keys = {}

    # Check if we have all required API keys already
    openai_key = os.environ.get("OPENAI_API_KEY")
    odds_key = os.environ.get("ODDS_API_KEY")
    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    tg_chat = os.environ.get("TELEGRAM_CHAT_ID")

    # Count how many keys we already have
    existing_keys = sum([bool(openai_key), bool(odds_key), bool(tg_token and tg_chat)])

    if existing_keys > 0:
        print(f"🔑 Found {existing_keys} saved API key(s) from previous session")

    # OpenAI API Key for ChatGPT refactoring
    if not openai_key:
        print("🔑 OpenAI API Key not found in environment.")
        openai_key = input(
            "Enter your OpenAI API Key (or press Enter to skip ChatGPT features): "
        ).strip()
        if openai_key:
            api_keys["OPENAI_API_KEY"] = openai_key
            os.environ["OPENAI_API_KEY"] = openai_key
            print("✅ OpenAI API Key set for this session")
        else:
            print("⚠️  ChatGPT features will be disabled")
    else:
        print("✅ OpenAI API Key loaded from saved configuration")

    # Odds API Key for betting automation
    if not odds_key:
        print("🔑 Odds API Key not found in environment.")
        odds_key = input(
            "Enter your Odds API Key (or press Enter to skip betting features): "
        ).strip()
        if odds_key:
            api_keys["ODDS_API_KEY"] = odds_key
            os.environ["ODDS_API_KEY"] = odds_key
            print("✅ Odds API Key set for this session")
    else:
        print("✅ Odds API Key loaded from saved configuration")

    # Telegram Bot credentials
    if not tg_token or not tg_chat:
        print("🔑 Telegram credentials not complete.")
        if not tg_token:
            tg_token = input("Enter Telegram Bot Token (or press Enter to skip): ").strip()
            if tg_token:
                api_keys["TELEGRAM_BOT_TOKEN"] = tg_token
                os.environ["TELEGRAM_BOT_TOKEN"] = tg_token

        if not tg_chat:
            tg_chat = input("Enter Telegram Chat ID (or press Enter to skip): ").strip()
            if tg_chat:
                api_keys["TELEGRAM_CHAT_ID"] = tg_chat
                os.environ["TELEGRAM_CHAT_ID"] = tg_chat

        if tg_token and tg_chat:
            print("✅ Telegram credentials set for this session")
    else:
        print("✅ Telegram credentials loaded from saved configuration")

    return api_keys


def save_api_keys_to_env(api_keys: dict[str, str]) -> None:
    """Save API keys to .env file for persistence"""
    env_file = BASE / ".env"
    if api_keys:
        if input("Save API keys to .env file for future use? (y/N): ").lower().startswith("y"):
            with open(env_file, "a", encoding="utf-8") as f:
                f.write(f"\n# Added by EQ12 Godmode Runner - {datetime.datetime.now()}\n")
                for key, value in api_keys.items():
                    f.write(f"{key}={value}\n")
            print(f"✅ API keys saved to {env_file}")
        else:
            print("📝 API keys not saved (will prompt again next time)")
    else:
        print("📝 No new API keys to save")


def run_task(name: str, cmd: str, required: bool = False) -> tuple[bool, str]:
    """Run a task with logging and error handling"""
    logging.info(f"=== Starting {name} ===")
    print(f"[EQ12] {name} ...", flush=True)

    try:
        # Check if the command file exists
        if cmd.startswith("python "):
            script_path = cmd.split('"')[1] if '"' in cmd else cmd.split()[1]
            if not os.path.exists(script_path):
                msg = f"{name} skipped (script not found: {script_path})"
                logging.info(msg)
                logger.warning(msg)
                return False, msg

        result = subprocess.run(
            cmd, shell=True, check=False, capture_output=True, text=True, timeout=300
        )

        if result.returncode == 0:
            logging.info(f"{name} completed OK")
            logger.info(f"✅ {name} completed successfully")
            if result.stdout.strip():
                logging.info(f"{name} output: {result.stdout.strip()}")
            return True, "Success"
        error_msg = f"{name} failed with code {result.returncode}"
        if result.stderr:
            error_msg += f": {result.stderr.strip()}"
        logging.warning(error_msg)
        logger.error(error_msg)

        if required:
            raise subprocess.CalledProcessError(result.returncode, cmd)
        return False, error_msg

    except subprocess.TimeoutExpired:
        error_msg = f"{name} timed out after 5 minutes"
        logging.error(error_msg)
        logger.warning(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"{name} crashed: {e}"
        logging.exception(error_msg)
        logger.error(error_msg)
        if required:
            raise
        return False, error_msg


def main() -> None:
    parser = argparse.ArgumentParser(description="EQ12 Godmode Runner Plus")
    parser.add_argument(
        "--skip-api-prompts",
        action="store_true",
        help="Skip API key prompting (use environment only)",
    )
    parser.add_argument("--civil-only", action="store_true", help="Run only civil service tracker")
    parser.add_argument("--betting-only", action="store_true", help="Run only betting automation")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would run without executing"
    )

    args = parser.parse_args()

    logger.info("=== EQ12 Master Profile Loaded (Buffalo Stack 14215) ===")
    logger.info(f"📝 Logs: {logfile}")

    # API Key Management
    if not args.skip_api_prompts:
        api_keys = prompt_for_api_keys()
        if api_keys:
            save_api_keys_to_env(api_keys)

    # Define all available tasks
    all_tasks = [
        (
            "Civil Service Tracker",
            f'python "{BASE}/civil/civil_service_tracker.py"',
            True,
        ),
        (
            "EdgeGod Parlays Bot",
            f'python "{BASE.parent}/EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro_clean.py"',
            False,
        ),
        (
            "Travel Bot",
            f'python "{BASE.parent}/scripts/travel_deals_scraper.py"',
            False,
        ),
        ("AliDropship Sync", f'python "{BASE}/dropship/sync.py"', False),
        ("Odds Parser", f'python "{BASE.parent}/scripts/odds_parser.py"', False),
        ("Parlay Builder", f'python "{BASE.parent}/scripts/parlay_builder.py"', False),
    ]

    # Filter tasks based on arguments
    if args.civil_only:
        tasks = [task for task in all_tasks if "Civil" in task[0]]
    elif args.betting_only:
        tasks = [
            task
            for task in all_tasks
            if any(word in task[0] for word in ["EdgeGod", "Odds", "Parlay"])
        ]
    else:
        tasks = all_tasks

    if args.dry_run:
        print("\n🔍 DRY RUN - Tasks that would execute:")
        for name, cmd, required in tasks:
            status = "REQUIRED" if required else "OPTIONAL"
            print(f"  • {name} ({status}): {cmd}")
        return

    print(f"\n🚀 Executing {len(tasks)} tasks...")

    # Execute tasks
    success_count: int = 0
    required_failures: list[str] = []
    results: list[dict[str, Any]] = []
    for name, cmd, required in tasks:
        success, message = run_task(name, cmd, required=False)  # Don't fail fast, log all results
        results.append({"name": name, "success": success, "message": message, "required": required})
        if success:
            success_count += 1
        elif required:
            required_failures.append(name)

    # Summary
    print(f"\n📊 Summary: {success_count}/{len(tasks)} tasks completed successfully")

    if required_failures:
        print(f"❌ Critical failures: {', '.join(required_failures)}")
        logging.error(f"Required tasks failed: {required_failures}")
        sys.exit(1)
    elif success_count == 0:
        print("❌ No tasks executed successfully!")
        logging.error("Complete failure - no tasks executed")
        sys.exit(1)
    else:
        print("✅ EQ12 Godmode run completed")
        logging.info(f"Run completed: {success_count}/{len(tasks)} successful")

    # Save run summary
    summary = {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_tasks": len(tasks),
        "successful_tasks": success_count,
        "failed_tasks": len(tasks) - success_count,
        "required_failures": required_failures,
    }

    summary_file = LOGS / f"run_summary_{datetime.date.today()}.json"
    with open(summary_file, "w") as f:
        try:
            json.dump(summary, f, indent=2)

        except OSError as e:
            logging.error(f"Failed to write JSON: {e}")

            raise


# Enterprise-grade reliability
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  EQ12 Godmode run interrupted by user")
        sys.exit(130)
    except Exception as e:
        logging.exception(f"Fatal error in main: {e}")
        print(f"💥 Fatal error: {e}")
        sys.exit(1)
