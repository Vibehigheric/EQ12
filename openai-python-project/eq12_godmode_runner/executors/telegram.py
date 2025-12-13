"""
Telegram Executor for EQ12 God Mode Commander++
Handles urgent notifications and real-time alerts
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import requests

from eq12_shared import CredentialError, CredentialManager

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
credential_manager = CredentialManager()


def _load_config() -> dict:
    if _CONFIG_PATH.exists():
        with _CONFIG_PATH.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return {}


def _telegram_credentials() -> tuple[str, str]:
    token = credential_manager.ensure_env(
        "telegram.bot_token",
        "TELEGRAM_BOT_TOKEN",
        prompt="Enter Telegram bot token: ",
        mask_input=True,
    )
    chat_id = credential_manager.ensure_env(
        "telegram.chat_id",
        "TELEGRAM_CHAT_ID",
        prompt="Enter Telegram chat id: ",
        mask_input=False,
    )
    return token, chat_id


def _should_retry(status: int, body: str) -> tuple[bool, str | None]:
    lowered = body.lower()
    if status in {401, 403}:
        return True, "token"
    if status == 400 and ("chat" in lowered and "not found" in lowered):
        return True, "chat_id"
    return False, None


def send_message(msg: str, message_type: str = "alert", *, attempt: int = 1) -> bool:
    """Send message to Telegram with formatting based on type."""
    cfg = _load_config()
    telegram_config = cfg.get("telegram", {})
    if not telegram_config.get("enabled", True):
        print("Telegram notifications are disabled in config.json")
        return False

    try:
        token, chat_id = _telegram_credentials()
    except CredentialError as err:
        print(f"Telegram credential error: {err}")
        return False

    if message_type == "sports":
        formatted_msg = f"""
�Y?+ **EQ12 SPORTS DISPATCH**
�Y". {datetime.now().strftime('%Y-%m-%d %H:%M')}

�YZ_ **Action:**
{msg}

�Y" *Auto-dispatched by God Mode Commander++*
"""
    elif message_type == "urgent":
        formatted_msg = f"""
�Ys" **URGENT EQ12 ALERT** �Ys"
�?� {datetime.now().strftime('%H:%M')}

�Y"� **Immediate Action Required:**
{msg}

�Y" *God Mode Commander++ Dispatch*
"""
    elif message_type == "travel":
        formatted_msg = f"""
�o^�,? **EQ12 TRAVEL DISPATCH**
�Y". {datetime.now().strftime('%Y-%m-%d %H:%M')}

�YZ� **Travel Action:**
{msg}

�Y" *Auto-dispatched by God Mode Commander++*
"""
    else:
        formatted_msg = f"""
�Y"< **EQ12 NOTIFICATION**
�Y? {datetime.now().strftime('%Y-%m-%d %H:%M')}

�Y"? **Message:**
{msg}

�Y" *God Mode Commander++*
"""

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": formatted_msg, "parse_mode": "Markdown"}

    try:
        response = requests.post(url, data=payload, timeout=10)
    except requests.RequestException as req_err:
        print(f"❌ Telegram executor error: {req_err}")
        return False

    if response.status_code == 200:
        print(f"�o. Telegram message sent successfully ({message_type})")
        return True

    retry, field = _should_retry(response.status_code, response.text)
    if retry and attempt < 2:
        if field == "token":
            credential_manager.invalidate(
                "telegram.bot_token",
                prompt="Telegram bot token invalid. Enter a new token: ",
                mask_input=True,
            )
        elif field == "chat_id":
            credential_manager.invalidate(
                "telegram.chat_id",
                prompt="Telegram chat id invalid. Enter a new chat id: ",
                mask_input=False,
            )
        return send_message(msg, message_type, attempt=attempt + 1)

    print(f"❌ Telegram API error: {response.status_code} - {response.text}")
    return False


def send_sports_alert(action: str) -> bool:
    """Send sports-specific alert."""
    return send_message(action, "sports")


def send_urgent_alert(action: str) -> bool:
    """Send urgent alert."""
    return send_message(action, "urgent")


def send_travel_alert(action: str) -> bool:
    """Send travel-specific alert."""
    return send_message(action, "travel")


if __name__ == "__main__":
    test_msg = "Test message from EQ12 God Mode Commander++"
    print("Testing Telegram executor...")
    result = send_message(test_msg)
    if result:
        print("�o. Telegram executor test successful")
    else:
        print("❌ Telegram executor test failed")
