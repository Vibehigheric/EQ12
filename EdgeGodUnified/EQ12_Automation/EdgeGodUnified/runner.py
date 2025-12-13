import csv
import json
import logging
import os
import sys

# Set up logging
logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# === Auto-normalize odds spreadsheets into data/sample_lines.csv ===
try:
    import os
    import subprocess
    import sys
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "normalizer.py")], check=False)
except Exception as e:
    print("[normalizer] skipped:", e)
# === End normalize ===

import json

from builder.parlay_builder import build_parlays

from utils.gmail_utils import gmail_service, send_email
from utils.telegram_utils import send_telegram_message


def load_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            try: row["odds"] = int(row["odds"]) if row.get("odds") else None
            except: row["odds"] = None
            try: row["true_prob"] = float(row["true_prob"]) if row.get("true_prob") else None
            except: row["true_prob"] = None
            try: row["proj_over_2_prob"] = float(row["proj_over_2_prob"]) if row.get("proj_over_2_prob") else None
            except: row["proj_over_2_prob"] = None
            rows.append(row)
    return rows

def format_ticket(name, legs, win_prob):
    lines = [f"=== {name} ===", f"True win prob (MC): {win_prob:.2%}"]
    for l in legs:
        star = "**" if l.get("starred") else ""
        lines.append(f"- {star}{l['display_name']}{star} | {l['market']} {l['side']} | odds {l['odds']} | true p={l['true_prob']:.2f}")
    return "\n".join(lines)

def main() -> None:
    try:

        cfg = json.load(open("config.json","r",encoding="utf-8")

    except json.JSONDecodeError as e:

        logging.error(f"Failed to parse JSON from {file_path}: {e}")

        raise

    except FileNotFoundError as e:

        logging.error(f"JSON file not found: {e}")

        raise)
    rows = load_rows("data/sample_lines.csv")
    tickets = build_parlays(rows, cfg)

    sections = []
    for key in ["five_leg_mixed","ten_leg_mixed","hr_three_leg"]:
        legs = tickets.get(key, [])
        wp = tickets.get(key + "_true_win_prob", 0.0)
        sections.append(format_ticket(key, legs, wp))

    body = "\n\n".join(sections)
    logger.info(body)

    if cfg.get("telegram_enabled"):
        send_telegram_message(cfg.get("telegram_bot_token"), cfg.get("telegram_chat_id"), body[:3900])

    try:
        svc = gmail_service()
        send_email(svc, cfg.get("email_recipient"), "EdgeGod Unified – Daily Tickets", body)
    except Exception:
        pass

if __name__ == "__main__":
    main()