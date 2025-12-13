
# EQ12 GODSTACK — Google + Bing + Swagbucks + News + Autosuggest

A production-minded toolkit that glues **Google (CSE + News RSS)**, **Bing (Web + News + Autosuggest)**,
and **Swagbucks public offer scraping** into one SQLite-backed pipeline with Telegram alerts.
Drop it into your EQ12 and plug each script into your betting / travel / cannabis / fleet / housing / education stacks.

## Components
- `clients.py` — Bing + Google API wrappers (web, news, autosuggest).
- `db.py` — SQLite with tables `results` and `offers`.
- `alert_pipe.py` — Telegram glue.
- `meta_search.py` — dual-engine web search (Google CSE + Bing) with dedupe + DB + optional Telegram.
- `news_aggregator.py` — **Bing News API** + **Google News RSS** → DB.
- `swagbucks_offers.py` — Playwright scraper for Swagbucks public offers → DB + Telegram optional.
- `autosuggest_merge.py` — merges Bing + Google autosuggest for SEO/keyword generation.

## Install (Windows / EQ12)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
# Playwright browsers (for swagbucks scraping)
python -m playwright install chromium
```
Copy `.env.example` → `.env` and fill:
- `BING_KEY` (+ optional `BING_NEWS_ENDPOINT` override)
- `GOOGLE_KEY`, `GOOGLE_CSE_ID`
- `TG_TOKEN`, `TG_CHAT_ID` (optional)
- `META_DB_PATH` (optional path to .sqlite3)

## Usage
**Web search (dual):**
```powershell
python meta_search.py --query "Buffalo dispensary news" --telegram --show-latest
```

**News (Bing News + Google News RSS):**
```powershell
python news_aggregator.py --query "NHL injuries" 
```

**Swagbucks offers (public pages):**
```powershell
python swagbucks_offers.py --telegram
```

**Autosuggest merge (SEO/keywords):**
```powershell
python autosuggest_merge.py --query "Buffalo cheap flights" --json
```

## Scheduling (Task Scheduler)
Create daily jobs similar to:
```powershell
schtasks /create /sc hourly /mo 1 /tn "EQ12_Godstack_News" /tr "`"%CD%\.venv\Scripts\python.exe`" `"%CD%\news_aggregator.py`" --query-file queries_news.txt"
schtasks /create /sc daily /st 06:00 /tn "EQ12_Godstack_Swagbucks" /tr "`"%CD%\.venv\Scripts\python.exe`" `"%CD%\swagbucks_offers.py`" --telegram"
```

## Notes / Ethics
- Respect provider TOS. Swagbucks scraping targets **public offer lists** only. Avoid automating login or rewards workflows.
- Google News API is not public; we use **RSS**, which is allowed. For web search, we use **Google CSE**.
- For richer ranking, add your LLM step after DB insert to score and filter results per stack.
