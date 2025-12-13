import os

try:
    from telegram import Bot
except Exception:
    Bot = None


def _fmt_results(results: list[dict], header: str) -> str:
    lines = [f"*{header}*"]
    for r in results:
        t = (r.get("title") or "Untitled").strip()
        u = r.get("url") or ""
        s = r.get("source") or "?"
        lines.append(f"• [{t}]({u}) _({s})_")
    return "\n".join(lines[:60])


def _fmt_offers(offers: list[dict], header: str) -> str:
    lines = [f"*{header}*"]
    for o in offers:
        t = (o.get("title") or "Untitled").strip()
        u = o.get("url") or ""
        s = o.get("source") or "offer"
        r = o.get("reward") or ""
        c = o.get("category") or ""
        extra = f" — {r}" if r else ""
        if c:
            extra += f" [{c}]"
        lines.append(f"• [{t}]({u}) _({s})_{extra}")
    return "\n".join(lines[:60])


def send_telegram_text(text: str) -> str | None:
    token = os.getenv("TG_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    if not token or not chat_id:
        return "Telegram disabled: set TG_TOKEN and TG_CHAT_ID."
    if Bot is None:
        return "python-telegram-bot not installed. pip install python-telegram-bot"
    Bot(token).send_message(
        chat_id=chat_id, text=text, parse_mode="Markdown", disable_web_page_preview=True
    )
    return None


def send_results(results: list[dict], header: str):
    return send_telegram_text(_fmt_results(results, header))


def send_offers(offers: list[dict], header: str):
    return send_telegram_text(_fmt_offers(offers, header))
