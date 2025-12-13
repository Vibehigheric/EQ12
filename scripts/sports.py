#!/usr/bin/env python3
r"""sports.py — The Odds API integration (managed via keys/credentials.json)"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
shared_path = ROOT / "openai-python-project"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

from eq12_shared import CredentialError, CredentialManager

credential_manager = CredentialManager()

SPORTS = [
    s.strip()
    for s in os.getenv("SPORTS", "baseball_mlb,americanfootball_nfl").split(",")
    if s.strip()
]
REGIONS = os.getenv("REGIONS", "us")
MARKETS = os.getenv("MARKETS", "h2h,spreads,totals")
OUT_DIR = Path(os.getenv("OUT_DIR", r"C:/EQ12/logs")).expanduser()
OUT_DIR.mkdir(parents=True, exist_ok=True)
BASE = "https://api.the-odds-api.com/v4"


def _odds_api_key() -> str:
    return credential_manager.ensure_env(
        "odds_api.api_key",
        "ODDS_API_KEY",
        prompt="Enter The Odds API key: ",
        mask_input=True,
    )


def fetch_sport(sport_key: str, *, attempt: int = 1) -> dict[str, Any]:
    try:
        api_key = _odds_api_key()
    except CredentialError as err:
        return {"sport": sport_key, "ok": False, "error": f"Credential error: {err}"}

    try:
        response = requests.get(
            f"{BASE}/sports/{sport_key}/odds",
            params={
                "apiKey": api_key,
                "regions": REGIONS,
                "markets": MARKETS,
                "oddsFormat": "american",
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        return {"sport": sport_key, "ok": False, "error": str(exc)}

    if response.status_code == 401 and attempt < 2:
        credential_manager.invalidate(
            "odds_api.api_key",
            prompt="The Odds API key was rejected. Enter a new key: ",
            mask_input=True,
        )
        return fetch_sport(sport_key, attempt=attempt + 1)

    if response.status_code != 200:
        return {
            "sport": sport_key,
            "ok": False,
            "error": f"HTTP {response.status_code}: {response.text}",
        }

    data = response.json()
    snapshot = OUT_DIR / f"odds_{sport_key}.json"
    snapshot.write_text(json.dumps(data), encoding="utf-8")
    return {
        "sport": sport_key,
        "ok": True,
        "count": len(data),
        "snapshot": str(snapshot),
    }


def main() -> None:
    results = [fetch_sport(s) for s in SPORTS]
    payload = {
        "type": "sports",
        "ts": dt.datetime.now(dt.UTC).isoformat(),
        "results": results,
    }
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
