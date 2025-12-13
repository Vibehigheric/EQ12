# OmniScraper

A state-machine based scraper that fetches active sports and odds, with retries, chunked processing, and optional SQLite persistence.

Usage:

python scripts/omni_run.py --api-key <KEY> --out out.json --db data.db

By default the script runs in non-dry mode if `--dry-run` is not provided. Set `ODDS_API_KEY` env var to avoid passing the key on the command line.
