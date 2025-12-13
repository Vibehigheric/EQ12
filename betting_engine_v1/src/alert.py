import os
import requests
from datetime import datetime

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    """
    Send a message to the configured Telegram channel.
    """
    print(f"[{datetime.now()}] Sending Telegram alert...")
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Telegram credentials not found.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"[{datetime.now()}] Alert sent successfully.")
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")

if __name__ == "__main__":
    # Test alert
    send_telegram_alert("🚀 *Betting Engine V1* is online.\nSystem check complete.")
