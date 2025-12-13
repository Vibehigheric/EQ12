
# EQ12 MetaSearch (Bing + Google) — Integratable Toolkit

Fuse **Bing** (Azure Cognitive Services) and **Google Custom Search** into one pipeline on your EQ12,
store results to SQLite, and optionally push summaries to Telegram. Designed to be dropped into any of your stacks
(betting, travel, cannabis/CBD, fleet/Turo, housing/credit, education).

## Features
- Unified wrapper over **Bing Web Search API** and **Google Custom Search (CSE)**.
- **De-duplication by URL** so your alerts don't double-post.
- **SQLite** storage with schema auto-init.
- **Telegram** alert pipe (optional).
- Clean CLI with `--query` or `--query-file` modes.
- Retry/backoff on transient HTTP failures.

## Install (EQ12 / Windows)
```powershell
cd C:\Users\%USERNAME%\Downloads
# Unzip the archive, then:
cd eq12_meta_search
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
# (Optional) populate .env (copy from .env.example) or set ENV vars in Windows
```
> Tip: Use a system-wide secrets store or a `keys\credentials.json` if you already adopted an EQ12 CredentialManager.

## Configure
Create a `.env` in this folder (copy `.env.example`) or set environment variables:
- `BING_KEY` — Azure Bing Search API key
- `GOOGLE_KEY` — Google CSE API key
- `GOOGLE_CSE_ID` — your custom search engine ID
- `TG_TOKEN` + `TG_CHAT_ID` — for Telegram alerts (optional)
- `META_DB_PATH` — custom path for the SQLite DB (optional)

## Quick Start
Run a single query with both engines and print the latest rows:
```powershell
.\.venv\Scripts\activate
python meta_search.py --query "Buffalo dispensary news" --show-latest
```
Send a Telegram summary too:
```powershell
python meta_search.py --query "BUF to LAX flight deals" --telegram
```

Batch mode (one query per line in a file):
```powershell
python meta_search.py --query-file queries.txt --count 10 --telegram
```

Disable one engine if desired:
```powershell
python meta_search.py --query "NHL injuries tonight" --no-google
python meta_search.py --query "NHL injuries tonight" --no-bing
```

## Scheduling (Windows Task Scheduler)
Create a daily job at 06:00 that reads `queries.txt` and posts alerts:
```powershell
$task = "EQ12_MetaSearch_Daily"
$cmd  = "C:\Path\to\eq12_meta_search\.venv\Scripts\python.exe"
$args = "C:\Path\to\eq12_meta_search\meta_search.py --query-file C:\Path\to\eq12_meta_search\queries.txt --telegram"
schtasks /create /sc daily /st 06:00 /tn $task /tr "`"$cmd`" `"$args`""
```

## Integrating with Your Stacks
- **Betting**: feed injuries/team news queries hourly; cross-check with OddsAPI before auto-alerting.
- **Travel**: combine Google for fare/blog depth with Bing for images; push pages to your affiliate builder.
- **Cannabis/CBD**: use Google Maps/Places in your separate module, and this MetaSearch for regulatory/news terms.
- **Fleet/Turo**: run Autosuggest (separate) to build keyword lists; use MetaSearch for recalls/market conditions.
- **Housing/Credit**: combine gov/edu queries (CSE) with Bing’s structured JSON to populate your affordability dashboard.

## Notes
- Google CSE returns max 10 results per request; paginate if you need more.
- Respect both providers' TOS and rate limits.
- Extend `clients.py` with Bing News or Image search if you need those endpoints for a stack.
- For richer ranking, plug your LLM into an enrichment step after saving to SQLite.
