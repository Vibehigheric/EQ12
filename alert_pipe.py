import os

try:
    from telegram import Bot
except Exception:
    Bot = None  # Optional dependency


def format_markdown(results: list[dict], header: str) -> str:
    lines = [f"*{header}*"]
    for r in results:
        title = (r.get("title") or "Untitled").strip()
        url = r.get("url") or ""
        src = r.get("source") or "?"
        lines.append(f"• [{title}]({url})  _({src})_")
    return "\n".join(lines[:60])  # safety cap


def send_telegram(results: list[dict], header: str = "MetaSearch Results") -> str | None:
    token = os.getenv("TG_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    if not token or not chat_id:
        return "Telegram disabled: set TG_TOKEN and TG_CHAT_ID."
    if Bot is None:
        return "python-telegram-bot not installed. pip install python-telegram-bot"
    bot = Bot(token)
    text = format_markdown(results, header)
    bot.send_message(
        chat_id=chat_id, text=text, parse_mode="Markdown", disable_web_page_preview=True
    )
    return None
