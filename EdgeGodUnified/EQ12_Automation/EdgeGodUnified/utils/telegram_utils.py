import requests


def send_telegram_message(bot_token, chat_id, text) -> None:
    if not bot_token or not chat_id:
        return None
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data={"chat_id": chat_id, "text": text[:3900]},
            timeout=10,
        )
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}
