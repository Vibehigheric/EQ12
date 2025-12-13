#!/usr/bin/env python3
r"""Fetch all in-season games using The Odds API.

Dry-run by default. Pass --apply to perform real HTTP requests (requires ODDS_API_KEY env).

Writes JSON output to C:\EQ12\logs\in_season_games.json by default when --apply is used.

TODO: add pytest unit tests for schema and richer error handling.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

import requests

# Import EQ12 rate limiting system
try:
    pass

    RATE_LIMITING_AVAILABLE = True
except ImportError:
    RATE_LIMITING_AVAILABLE = False

ROOT = Path(__file__).resolve().parents[1]
shared_path = ROOT / "openai-python-project"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

from eq12_shared import CredentialError, CredentialManager

DEFAULT_REGIONS = "us"
DEFAULT_MARKETS = "h2h,spreads,totals"


def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def get_active_sports(api_host: str, api_key: str) -> list[str]:
    url = f"{api_host}/v4/sports?apiKey={api_key}"
    logging.info("Fetching active sports from %s", url)
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    return [s["key"] for s in data if s.get("active")]


def get_upcoming_games_for_sport(
    api_host: str, api_key: str, sport_key: str, regions: str, markets: str
):
    url = f"{api_host}/v4/sports/{sport_key}/odds/?apiKey={api_key}&regions={regions}&markets={markets}"
    logging.info("Fetching odds for sport %s", sport_key)
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return resp.json()


def ensure_logs_dir() -> Path:
    p = Path(os.environ.get("EQ12_LOGS", r"C:\EQ12\logs"))
    p.mkdir(parents=True, exist_ok=True)
    return p


def main(argv: list[str] | None = None) -> int:
    setup_logging()
    p = argparse.ArgumentParser(description="Fetch all in-season games from The Odds API (EQ12)")
    p.add_argument("--regions", default=DEFAULT_REGIONS)
    p.add_argument("--markets", default=DEFAULT_MARKETS)
    p.add_argument("--api-host", default="https://api.the-odds-api.com")
    p.add_argument(
        "--out-json",
        default=None,
        help="Path to write JSON output (defaults to logs/in_season_games.json when --apply)",
    )
    p.add_argument(
        "--apply",
        action="store_true",
        help="Perform real API calls (default is dry-run)",
    )
    p.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between sport requests (seconds)",
    )
    args = p.parse_args(argv)

    logging.info("Args: %s", args)

    if not args.apply:
        logging.info("Dry-run mode (no HTTP requests). Use --apply to perform real API calls.")
        return 0

    manager = CredentialManager()
    try:
        api_key = manager.ensure_env(
            "odds_api.api_key",
            "ODDS_API_KEY",
            prompt="Enter The Odds API key: ",
            mask_input=True,
        )
    except CredentialError as err:
        logging.error("ODDS API key unavailable: %s", err)
        return 2

    logs = ensure_logs_dir()
    out_path = Path(args.out_json) if args.out_json else logs / "in_season_games.json"

    all_games = []
    try:
        sports = get_active_sports(args.api_host, api_key)
    except Exception as e:
        logging.exception("Failed to fetch active sports: %s", e)
        return 3

    logging.info("Found %d active sports", len(sports))
    for sport in sports:
        try:
            games = get_upcoming_games_for_sport(
                args.api_host, api_key, sport, args.regions, args.markets
            )
            if games:
                all_games.extend(games)
        except requests.exceptions.HTTPError as e:
            status = getattr(e.response, "status_code", None)
            logging.warning("HTTP error for sport %s: %s", sport, e)
            if status == 429:
                logging.warning("Rate limited; backing off and retrying sport %s", sport)
                time.sleep(60)
                try:
                    games = get_upcoming_games_for_sport(
                        args.api_host, api_key, sport, args.regions, args.markets
                    )
                    if games:
                        all_games.extend(games)
                except Exception:
                    logging.exception("Retry failed for sport %s", sport)
        except Exception:
            logging.exception("Error fetching games for sport %s", sport)

        time.sleep(args.delay)

    # Write results
    out_path.write_text(json.dumps(all_games, indent=2), encoding="utf-8")
    logging.info("Wrote %d games to %s", len(all_games), out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
