import requests


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> None:
    if not bot_token or not chat_id:
        return None
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    try:
        r = requests.post(url, data=data, timeout=10)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}
