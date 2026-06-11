#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


MLB_TZ = ZoneInfo("America/New_York")
ARTIFACT_FILES = [
    "odds_snapshot.json",
    "projections.json",
    "edges.json",
    "watchlist.json",
    "release_card.md",
    "no_bet_report.md",
    "workflow_summary.md",
]


def fetch_json(url: str) -> Any:
    request = Request(url, headers={"User-Agent": "EQ12-MLB-Enrichment/1.0"})
    with urlopen(request, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_team(name: str | None) -> str:
    if not name:
        return ""
    return (
        name.lower()
        .replace(".", "")
        .replace(",", "")
        .replace("&", "and")
        .replace("  ", " ")
        .strip()
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_model_artifacts() -> list[str]:
    roots = [Path("models"), Path("artifacts"), Path("outputs"), Path("data")]
    matches: list[str] = []
    suffixes = {".joblib", ".json", ".pkl", ".pt", ".bin", ".duckdb"}
    for root in roots:
      if not root.exists():
        continue
      for path in root.rglob("*"):
        if not path.is_file():
          continue
        name = path.name.lower()
        if "mlb" not in name or path.suffix.lower() not in suffixes:
          continue
        matches.append(path.as_posix())
    return sorted(matches)[:50]


def fetch_odds_snapshot(date_text: str, warnings: list[str]) -> dict[str, Any]:
    api_key = os.getenv("ODDS_API_KEY") or os.getenv("THE_ODDS_API_KEY")
    if not api_key:
        warnings.append("odds_api_key_missing")
        return {
            "date": date_text,
            "generated_at": datetime.now(MLB_TZ).isoformat(),
            "system_status": "DEGRADED",
            "warnings": warnings.copy(),
            "games": [],
        }

    params = urlencode(
        {
            "apiKey": api_key,
            "regions": "us",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american",
            "dateFormat": "iso",
        }
    )
    url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds?{params}"
    try:
        payload = fetch_json(url)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        warnings.append(f"odds_fetch_failed: {exc}")
        return {
            "date": date_text,
            "generated_at": datetime.now(MLB_TZ).isoformat(),
            "system_status": "DEGRADED",
            "warnings": warnings.copy(),
            "games": [],
            "source_url": url,
        }

    snapshot_games = []
    for event in payload:
        event_games = {
            "event_id": event.get("id"),
            "home_team": event.get("home_team"),
            "away_team": event.get("away_team"),
            "commence_time": event.get("commence_time"),
            "bookmakers": [],
        }
        for bookmaker in event.get("bookmakers", []):
            markets = {}
            for market in bookmaker.get("markets", []):
                outcomes = market.get("outcomes", [])
                markets[market.get("key")] = outcomes
            event_games["bookmakers"].append(
                {
                    "key": bookmaker.get("key"),
                    "title": bookmaker.get("title"),
                    "last_update": bookmaker.get("last_update"),
                    "markets": markets,
                }
            )
        snapshot_games.append(event_games)

    return {
        "date": date_text,
        "generated_at": datetime.now(MLB_TZ).isoformat(),
        "system_status": "OK" if snapshot_games else "DEGRADED",
        "source_url": url,
        "warnings": warnings.copy(),
        "games": snapshot_games,
    }


def build_odds_index(odds_snapshot: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    indexed: dict[tuple[str, str], dict[str, Any]] = {}
    for game in odds_snapshot.get("games", []):
        key = (normalize_team(game.get("away_team")), normalize_team(game.get("home_team")))
        indexed[key] = game
    return indexed


def best_h2h_lines(bookmakers: list[dict[str, Any]]) -> dict[str, Any]:
    best: dict[str, Any] = {}
    for bookmaker in bookmakers:
        for outcome in bookmaker.get("markets", {}).get("h2h", []):
            name = outcome.get("name")
            price = outcome.get("price")
            if name is None or price is None:
                continue
            current = best.get(name)
            if current is None or price > current["price"]:
                best[name] = {
                    "price": price,
                    "bookmaker": bookmaker.get("title"),
                    "last_update": bookmaker.get("last_update"),
                }
    return best


def age_minutes(timestamp: str | None) -> float | None:
    if not timestamp:
        return None
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return None
    return round((datetime.now(parsed.tzinfo) - parsed).total_seconds() / 60, 2)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build MLB daily enrichment artifacts.")
    parser.add_argument("--date", default=datetime.now(MLB_TZ).date().isoformat())
    parser.add_argument("--slate", default="artifacts/mlb/slate_context.json")
    parser.add_argument("--artifacts-dir", default="artifacts/mlb")
    args = parser.parse_args()

    artifacts_dir = Path(args.artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    slate_path = Path(args.slate)
    warnings: list[str] = []
    source_files_used = [slate_path.as_posix()]
    generated_at = datetime.now(MLB_TZ).isoformat()

    if not slate_path.exists():
        raise FileNotFoundError(f"Missing slate context: {slate_path}")

    slate = load_json(slate_path)
    odds_snapshot = fetch_odds_snapshot(args.date, warnings)
    write_json(artifacts_dir / "odds_snapshot.json", odds_snapshot)
    source_files_used.append((artifacts_dir / "odds_snapshot.json").as_posix())

    model_artifacts = find_model_artifacts()
    odds_index = build_odds_index(odds_snapshot)
    projections: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    watchlist: list[dict[str, Any]] = []
    blocked_games: list[dict[str, Any]] = []
    release_grade_candidates: list[dict[str, Any]] = []

    for game in slate.get("games", []):
        away_key = normalize_team(game.get("away_team"))
        home_key = normalize_team(game.get("home_team"))
        odds_game = odds_index.get((away_key, home_key))

        pitchers_ready = bool(game.get("home_pitcher", {}).get("name") and game.get("away_pitcher", {}).get("name"))
        lineup_ready = False
        market_ready = odds_game is not None
        market_lines = best_h2h_lines(odds_game.get("bookmakers", [])) if odds_game else {}
        freshest_update = None
        for line in market_lines.values():
            if not freshest_update or (line.get("last_update") or "") > freshest_update:
                freshest_update = line.get("last_update")
        freshness_minutes = age_minutes(freshest_update)
        fresh_enough = freshness_minutes is not None and freshness_minutes <= 60
        model_ready = bool(model_artifacts)

        reasons: list[str] = []
        if not pitchers_ready:
            reasons.append("probable_pitchers_missing")
        if not lineup_ready:
            reasons.append("confirmed_lineups_missing")
        if not market_ready:
            reasons.append("markets_missing")
        elif not fresh_enough:
            reasons.append("market_data_stale")
        if not model_ready:
            reasons.append("model_artifacts_missing")

        completeness_score = 0
        completeness_score += 25 if pitchers_ready else 0
        completeness_score += 25 if lineup_ready else 0
        completeness_score += 25 if market_ready and fresh_enough else 0
        completeness_score += 25 if model_ready else 0

        projection = {
            "game_id": game["game_id"],
            "away_team": game.get("away_team"),
            "home_team": game.get("home_team"),
            "status": game.get("status"),
            "start_time": game.get("start_time"),
            "pitchers_confirmed": pitchers_ready,
            "lineups_confirmed": lineup_ready,
            "markets_available": market_ready,
            "market_freshness_minutes": freshness_minutes,
            "model_artifacts_available": model_ready,
            "completeness_score": completeness_score,
            "release_grade": False,
            "blocked_reasons": reasons,
        }
        projections.append(projection)

        edge_record = {
            "game_id": game["game_id"],
            "away_team": game.get("away_team"),
            "home_team": game.get("home_team"),
            "official_play": False,
            "best_market_lines": market_lines,
            "release_blocked": True,
            "blocked_reasons": reasons,
        }
        edges.append(edge_record)

        if market_ready and pitchers_ready:
            watchlist.append(
                {
                    "game_id": game["game_id"],
                    "away_team": game.get("away_team"),
                    "home_team": game.get("home_team"),
                    "official_play": False,
                    "classification": "BEST_AVAILABLE_PROXY",
                    "completeness_score": completeness_score,
                    "best_market_lines": market_lines,
                    "watch_reasons": reasons or ["monitor_lineups_and_model_release"],
                }
            )

        if reasons:
            blocked_games.append(
                {
                    "game_id": game["game_id"],
                    "matchup": f'{game.get("away_team")} at {game.get("home_team")}',
                    "reasons": reasons,
                }
            )
        else:
            release_grade_candidates.append(projection)

    watchlist.sort(key=lambda item: item["completeness_score"], reverse=True)

    projections_payload = {
        "date": args.date,
        "generated_at": generated_at,
        "system_status": "OK",
        "source_files_used": source_files_used,
        "warnings": warnings,
        "model_artifacts_found": model_artifacts,
        "games": projections,
    }
    edges_payload = {
        "date": args.date,
        "generated_at": generated_at,
        "system_status": "OK",
        "official_release_count": len(release_grade_candidates),
        "games": edges,
        "warnings": warnings,
    }
    watchlist_payload = {
        "date": args.date,
        "generated_at": generated_at,
        "system_status": "OK",
        "official_play": False,
        "watchlist": watchlist,
        "warnings": warnings,
    }

    write_json(artifacts_dir / "projections.json", projections_payload)
    write_json(artifacts_dir / "edges.json", edges_payload)
    write_json(artifacts_dir / "watchlist.json", watchlist_payload)

    release_card = [
        f"# MLB Release Card - {args.date}",
        "",
        "NO RELEASE-GRADE MLB PLAYS TODAY",
        "",
        "Reason: release-grade gates require confirmed lineups, fresh markets, confirmed pitchers, and validated model artifacts.",
        "This run produced only proxy watchlist entries.",
    ]
    (artifacts_dir / "release_card.md").write_text("\n".join(release_card) + "\n", encoding="utf-8")

    no_bet_lines = [
        f"# MLB No-Bet Report - {args.date}",
        "",
        f"Blocked games: {len(blocked_games)}",
        "",
    ]
    for blocked in blocked_games:
        no_bet_lines.append(f"## {blocked['matchup']}")
        for reason in blocked["reasons"]:
            no_bet_lines.append(f"- {reason}")
        no_bet_lines.append("")
    (artifacts_dir / "no_bet_report.md").write_text("\n".join(no_bet_lines), encoding="utf-8")

    workflow_summary = [
        f"# MLB Workflow Summary - {args.date}",
        "",
        f"- Generated at: {generated_at}",
        f"- Slate games found: {slate.get('games_found', len(slate.get('games', [])))}",
        f"- Odds games found: {len(odds_snapshot.get('games', []))}",
        f"- Model artifacts found: {len(model_artifacts)}",
        f"- Release-grade plays: {len(release_grade_candidates)}",
        f"- Proxy watchlist entries: {len(watchlist)}",
        f"- Blocked games: {len(blocked_games)}",
        "",
        "## Output files",
    ]
    for filename in ["slate_context.json", *ARTIFACT_FILES]:
        workflow_summary.append(f"- artifacts/mlb/{filename}")
    if warnings:
        workflow_summary.append("")
        workflow_summary.append("## Warnings")
        for warning in warnings:
            workflow_summary.append(f"- {warning}")
    (artifacts_dir / "workflow_summary.md").write_text("\n".join(workflow_summary) + "\n", encoding="utf-8")

    print(f"Wrote MLB artifacts to {artifacts_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
