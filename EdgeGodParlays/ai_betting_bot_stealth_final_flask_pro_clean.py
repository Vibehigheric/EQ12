#!/usr/bin/env python3
"""
EdgeGod Parlays Bot - Buffalo Stack Integration
AI-powered betting bot for parlay generation and analysis
"""

import datetime
import logging
import os
import pathlib
import sys

import requests
from flask import Flask, request

BASE = pathlib.Path(__file__).resolve().parent
ROOT = BASE.parent / "buffalo_stack"
LOGS = ROOT / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

# Add Buffalo Stack to path for shared utilities
sys.path.insert(0, str(ROOT))


def load_env_file() -> bool:
    """Load environment variables from .env file"""
    env_file = ROOT / ".env"
    if env_file.exists():
        try:
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        if key and value and not os.environ.get(key):
                            os.environ[key] = value
        except Exception:
            pass


# Load environment variables at startup
load_env_file()

app = Flask(__name__)


def get_telegram_credentials() -> bool:
    """Get Telegram bot credentials from environment"""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logging.warning("Telegram credentials not found in environment")
        return None, None

    return bot_token, chat_id


def send_telegram_message(message, chat_id, bot_token) -> bool:
    """Send message via Telegram bot"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")
        return False


def build_mlb_context() -> bool:
    """Build MLB context for betting analysis"""
    # Placeholder for actual MLB data fetching
    ctx = "MLB Games Today:\n- No games currently available"
    games = []
    roster_map = {}
    return ctx, games, roster_map


def build_wnba_context() -> bool:
    """Build WNBA context for betting analysis"""
    # Placeholder for actual WNBA data fetching
    ctx = "WNBA Games Today:\n- No games currently available"
    games = []
    return ctx, games


@app.route("/webhook", methods=["POST"])
def telegram_webhook() -> bool:
    """Handle incoming Telegram webhook messages"""
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return "OK", 200

        message = data["message"]
        text = message.get("text", "").strip()
        chat_id = message["chat"]["id"]

        bot_token, _ = get_telegram_credentials()
        if not bot_token:
            logging.error("No Telegram bot token available")
            return "OK", 200

        if text == "/context_mlb":
            ctx, games, roster_map = build_mlb_context()
            send_telegram_message(f"📊 TODAY'S MLB\\n{ctx}", chat_id, bot_token)

        elif text == "/context_wnba":
            ctx, games = build_wnba_context()
            send_telegram_message(f"🏀 TODAY'S WNBA\\n{ctx}", chat_id, bot_token)

        elif text == "/parlays":
            send_telegram_message("🎯 Generating optimal parlays...", chat_id, bot_token)
            # Placeholder for parlay generation

        elif text == "/status":
            send_telegram_message("✅ EdgeGod Parlays Bot is active", chat_id, bot_token)

        else:
            # Echo unknown commands
            send_telegram_message(f"Unknown command: {text}", chat_id, bot_token)

        return "OK", 200

    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return "Error", 500


def main() -> bool:
    """Main EdgeGod Parlays Bot function"""
    logging.basicConfig(
        filename=LOGS / f"edgegod_parlays_{datetime.date.today()}.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    logging.info("=== EdgeGod Parlays Bot Started ===")
    print("[EDGEGOD] EdgeGod Parlays Bot - Buffalo Stack Integration")

    try:
        bot_token, chat_id = get_telegram_credentials()

        if bot_token and chat_id:
            print(f"[TELEGRAM] Bot configured with token: {bot_token[:10]}...")
            print(f"[TELEGRAM] Default chat ID: {chat_id}")
        else:
            print("[WARNING] Telegram credentials not configured")
            print("[INFO] Bot will run in local mode only")

        print("[SUCCESS] EdgeGod Parlays Bot initialized successfully")
        print("[INFO] Available commands: /context_mlb, /context_wnba, /parlays, /status")

        logging.info("EdgeGod Parlays Bot initialized successfully")
        return 0

    except Exception as e:
        error_msg = f"EdgeGod Parlays Bot failed: {e}"
        logging.error(error_msg)
        print(f"[ERROR] {error_msg}")
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EdgeGod Parlays Bot")
    parser.add_argument("--server", action="store_true", help="Run Flask server")
    parser.add_argument("--port", type=int, default=5000, help="Server port")
    args = parser.parse_args()

    try:
        if args.server:
            print(f"[SERVER] Starting Flask server on port {args.port}")
            app.run(host="0.0.0.0", port=args.port, debug=False)
        else:
            sys.exit(main())
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] EdgeGod Parlays Bot interrupted by user")
        sys.exit(130)
    except Exception as e:
        logging.exception(f"Fatal error: {e}")
        print(f"[FATAL] Fatal error: {e}")
        sys.exit(1)
