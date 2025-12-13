# EQ12 JobSearchBot — $40/hr+ Job Alerts to Gmail + Telegram

This bot searches multiple keywords and locations for jobs paying **$40/hr+**, then sends you a daily email (with CSV attachment) **and** a Telegram message.

## Contents
- `job_alert_runner.py` — Orchestrator (run daily)
- `job_fetcher.py` — Adzuna API fetch + normalize + format
- `gmail_utils.py` — Gmail API auth + email send (+ attachments)
- `telegram_utils.py` — Telegram sendMessage helper
- `config.json` — Settings (keywords, locations, min hourly, Gmail recipient, API keys)
- `requirements.txt` — Python dependencies
- `install.ps1` — PowerShell installer for Windows/EQ12
- `logs/` — CSV logs per run

## Prereqs
- Python 3.10+ on your EQ12
- A Google Cloud project with **Gmail API** enabled; download `credentials.json`
- Adzuna API credentials (free tier OK): `adzuna_app_id`, `adzuna_app_key`
- (Optional) Telegram Bot: `telegram_bot_token`, `telegram_chat_id`

## Setup
1. **Copy Package** to your EQ12 (e.g., `C:\EQ12_Automation\JobSearchBot`).
2. **Run Installer** in PowerShell:
   ```powershell
   cd C:\EQ12_Automation\JobSearchBot
   .\install.ps1
   ```
3. **Add credentials**:
   - Place your **Google** `credentials.json` in the same folder.
   - Edit `config.json` with:
     - your Gmail recipient
     - keywords/locations
     - Adzuna keys
     - Telegram bot token + chat id (if using Telegram)
4. **First Run (auth Gmail)**:
   ```powershell
   python C:\EQ12_Automation\JobSearchBot\job_alert_runner.py
   ```
   A browser window will open to authorize Gmail.
5. **Schedule Daily** via Windows Task Scheduler at 7:00 AM.

## Notes
- $40/hr is compared by annualizing to `$40 * 2080 = $83,200/yr` with `salary_min` from the API.
- Results are **deduped by URL** and sorted by salary desc.
- A CSV is saved under `logs/jobs_YYYYMMDD.csv` and attached to the daily email.

## Extend
- Add more job sources (Jooble, JobSearchAPI) in `job_fetcher.py`.
- Push alerts to other channels (Slack, Discord) similarly to Telegram.
- Share `gmail_utils.py` with your other EQ12 automations for unified email output.

---

© 2025 — Prepared for your EQ12 automation stack.
