import json
import os
from datetime import datetime

from gmail_utils import gmail_service, send_email
from job_fetcher import (
    fetch_jobs_multi,
    format_for_email,
    format_for_telegram,
    normalize_and_filter,
)
from telegram_utils import send_telegram_message


def load_config() -> None:
    with open("config.json", encoding="utf-8") as f:
        return json.load(f)


def ensure_dirs() -> None:
    os.makedirs("logs", exist_ok=True)


def save_csv(items) -> None:
    if not items:
        return None
    path = os.path.join("logs", f"jobs_{datetime.now().strftime('%Y%m%d')}.csv")
    headers = [
        "title",
        "company",
        "location",
        "salary_min",
        "salary_max",
        "url",
        "created",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write(",".join(headers) + "\n")
        for it in items:
            row = [
                it.get("title", "{}").replace(",", " "),
                it.get("company", "{}").replace(",", " "),
                it.get("location", "{}").replace(",", " "),
                str(int(it.get("salary_min", 0))),
                str(int(it.get("salary_max", 0) or it.get("salary_min", 0))),
                it.get("url", ""),
                (it.get("created") or "").replace(",", " "),
            ]
            f.write(",".join(row) + "\n")
    return path


def main() -> None:
    cfg = load_config()
    ensure_dirs()

    raw = fetch_jobs_multi(
        cfg.get("adzuna_app_id"),
        cfg.get("adzuna_app_key"),
        cfg.get("keywords", []),
        cfg.get("locations", []),
        cfg.get("min_hourly", 40),
    )
    items = normalize_and_filter(raw, cfg.get("min_hourly", 40))

    email_body = "Here are today's $40/hr+ job matches:\n\n" + (
        format_for_email(items) if items else "None found."
    )
    csv_path = save_csv(items)

    # Gmail
    try:
        svc = gmail_service()
        attachments = [csv_path] if csv_path else None
        send_email(
            svc,
            cfg.get("recipient"),
            "Daily $40+/hr Job Matches",
            email_body,
            attachments=attachments,
        )
    except Exception:
        pass

    # Telegram
    if cfg.get("telegram_enabled", False):
        try:
            msg = format_for_telegram(items, limit=12)
            send_telegram_message(cfg.get("telegram_bot_token"), cfg.get("telegram_chat_id"), msg)
        except Exception:
            pass


if __name__ == "__main__":
    main()
