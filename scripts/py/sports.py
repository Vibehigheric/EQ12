#!/usr/bin/env python3
r"""sports.py — The Odds API integration (set ODDS_API_KEY)"""

import datetime as dt
import json
import os
from pathlib import Path

import requests

# EQ12 Elite Copilot Master Prompt
#
# You are an **expert automation + PowerShell/Python engineer**.
# You are working on the EQ12 Elite Stack (stocks, crypto, sports, jobs, recycle, dashboard).
#
# ALWAYS DO:
# - Mirror Crypto JSON exporter pattern across all modules.
# - Fix issues globally — if you patch one (
    stocks), also patch others (crypto,
    jobs,
    recycle,
    sports
).
# - Dashboard = C:\EQ12\dashboard\index.html → always table-based, consistent format.
# - Add JSON exporters (# TODO: export this as JSON for dashboard).
# - Add pytest unit tests (# TODO: add pytest unit test for JSON schema).
# - For PowerShell:
#   - Use CmdletBinding() and Verb-Noun names (e.g., Get-EQ12Status).
#   - Wrap errors with try/catch, log to C:\EQ12\logs.
# - For Python:
#   - Always output valid JSON + CSV.
#   - Handle API keys (ODDS_API_KEY, Coinbase, yfinance).
# - Hard-code $env:ODDS_API_KEY read from C:\EQ12\keys\oddsapi.txt.
#
# CHAIN PROMPTS:
# 1. Write base function
# 2. Add JSON export
# 3. Add pytest schema unit test
# 4. Rewrite in PowerShell style if PS1/PSM1
# 5. Add dashboard integration (table row builder)
#
# EXAMPLES:
# - Stocks: JSON like Crypto, includes EMA20, EMA50, RSI14, MOM5, signal.
# - Sports: Use Odds API → log odds_{sport}.json.
# - Jobs: Log to jobs_controltech.json.
# - Recycle: Export to recycle_report.json.
#
# LOGGING:
# - C:\EQ12\logs\elite_run_*.log for elite run.
# - Each module logs its JSON.
# - Dashboard builds tables from JSON logs.
#
# WATCHDOG:
# - eq12-watchdog.ps1 runs hourly:
#   - eq12-elite-run
#   - eq12-build-dashboard
#   - Telegram alert if FAIL > 0.
#
# ---
#
# ⚡ Copilot: ALWAYS treat this file as law.
# ⚡ No silent failures.
# ⚡ No $null paths.
# ⚡ Apply fixes consistently across all modules.

# === EQ12 Copilot Master Patch ===
# Apply these rules across all EQ12 scripts:
#
# 1. Runner Stability
#    - Define Retry-Exec BEFORE any calls.
#    - Replace invalid Write-Host interpolations:
#         ("[{0}] FAIL {1}: {2}" -f $Name, $i, $_.Exception.Message)
#    - Ensure $ok/$fail counters increment and final summary always logs.
#
# 2. Dashboard Build
#    - Always set $dashboardDir = "C:\EQ12\dashboard" and create if missing.
#    - Define $html = Join-Path $dashboardDir "index.html".
#    - Pre-seed HTML with <html><body> wrapper, close with </body></html>.
#    - Use Add-Content -Path $html (not $html as variable only).
#    - Auto-launch dashboard: Start-Process $html.
#
# 3. Odds API Integration
#    - Ensure $env:ODDS_API_KEY loads from C:\EQ12\keys\oddsapi.txt.
#    - If missing, prompt once, save, and reuse.
#    - In sports.py and PowerShell, always call https://api.the-odds-api.com with apiKey=$env:ODDS_API_KEY.
#
# 4. JSON Export Consistency
#    - Stocks, Crypto, Sports, Jobs, Recycle must export results to C:\EQ12\logs\*.json.
#    - Dashboard reads JSON logs and renders table-based panels for ALL modules.
#
# 5. Copilot Rewrite Rules
#    - PowerShell: rewrite functions with [CmdletBinding()] and Verb-Noun style.
#    - Python: add `# TODO: export this as JSON for dashboard`.
#    - Add `# TODO: add pytest unit test for this function`.
#    - Mirror Crypto’s working export pattern in Stocks, Sports, Jobs, Recycle.
#
# 6. Error Hardening
#    - Always wrap API/network calls in try/except or try/catch with logging.
#    - Default to empty JSON snapshot if data fetch fails, so dashboard never breaks.
#
# === End Patch ===

API_KEY = os.getenv("ODDS_API_KEY", "")
SPORTS = [s.strip() for s in os.getenv("SPORTS", "baseball_mlb,americanfootball_nfl").split(",")]
REGIONS = os.getenv("REGIONS", "us")
MARKETS = os.getenv("MARKETS", "h2h,spreads,totals")
OUT_DIR = Path(os.getenv("OUT_DIR", "C:/EQ12/logs")).expanduser()
OUT_DIR.mkdir(parents=True, exist_ok=True)
BASE = "https://api.the-odds-api.com/v4"


def fetch_sport(sport_key):
    if not API_KEY:
        return {"sport": sport_key, "ok": False, "error": "ODDS_API_KEY not set"}
    try:
        r = requests.get(
            f"{BASE}/sports/{sport_key}/odds",
            params={
                "apiKey": API_KEY,
                "regions": REGIONS,
                "markets": MARKETS,
                "oddsFormat": "american",
            },
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        snap = OUT_DIR / f"odds_{sport_key}.json"
        snap.write_text(json.dumps(data))
        return {
            "sport": sport_key,
            "ok": True,
            "count": len(data),
            "snapshot": str(snap),
        }
    except Exception as e:
        return {"sport": sport_key, "ok": False, "error": str(e)}


def main() -> None:
    results = [fetch_sport(s) for s in SPORTS]
    print(
        json.dumps(
            {
                "type": "sports",
                "ts": dt.datetime.now(dt.UTC).isoformat(),
                "results": results,
            }
        )
    )


if __name__ == "__main__":
    main()
