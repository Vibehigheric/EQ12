#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


MLB_TZ = ZoneInfo("America/New_York")


def fetch_json(url: str) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "EQ12-MLB-Slate/1.0"})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_pitcher(side: dict[str, Any]) -> dict[str, Any]:
    probable = side.get("probablePitcher") or {}
    if not probable:
        return {"id": None, "name": None}
    return {
        "id": probable.get("id"),
        "name": probable.get("fullName"),
    }


def build_games(payload: dict[str, Any]) -> list[dict[str, Any]]:
    games: list[dict[str, Any]] = []
    for date_block in payload.get("dates", []):
        for game in date_block.get("games", []):
            teams = game.get("teams", {})
            home = teams.get("home", {})
            away = teams.get("away", {})
            games.append(
                {
                    "game_id": str(game.get("gamePk")),
                    "game_date": date_block.get("date"),
                    "start_time": game.get("gameDate"),
                    "status": (game.get("status") or {}).get("detailedState"),
                    "venue": (game.get("venue") or {}).get("name"),
                    "home_team": (home.get("team") or {}).get("name"),
                    "away_team": (away.get("team") or {}).get("name"),
                    "home_pitcher": normalize_pitcher(home),
                    "away_pitcher": normalize_pitcher(away),
                }
            )
    return games


def main() -> int:
    parser = argparse.ArgumentParser(description="Build today's MLB slate timing context.")
    parser.add_argument("--date", default=datetime.now(MLB_TZ).date().isoformat())
    parser.add_argument("--out", default="artifacts/mlb/slate_context.json")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    url = (
        "https://statsapi.mlb.com/api/v1/schedule"
        f"?sportId=1&date={args.date}&hydrate=probablePitcher,venue"
    )

    warnings: list[str] = []
    games: list[dict[str, Any]] = []
    system_status = "OK"

    try:
        payload = fetch_json(url)
        games = build_games(payload)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        payload = {}
        system_status = "DEGRADED"
        warnings.append(f"schedule_fetch_failed: {exc}")

    context = {
        "date": args.date,
        "generated_at": datetime.now(MLB_TZ).isoformat(),
        "system_status": system_status,
        "source_url": url,
        "games_found": len(games),
        "warnings": warnings,
        "games": games,
    }
    out_path.write_text(json.dumps(context, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
