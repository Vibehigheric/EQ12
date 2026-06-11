#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


MLB_TZ = ZoneInfo("America/New_York")


def run_step(command: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Poll MLB lineups and rerun enrichment until remaining games confirm.")
    parser.add_argument("--date", default=datetime.now(MLB_TZ).date().isoformat())
    parser.add_argument("--artifacts-dir", default="artifacts/mlb")
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--poll-seconds", type=int, default=300)
    parser.add_argument("--max-runs", type=int, default=0)
    args = parser.parse_args()

    artifacts_dir = Path(args.artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    slate_path = artifacts_dir / "slate_context.json"
    status_path = artifacts_dir / "lineup_monitor_status.json"

    env = os.environ.copy()
    date_text = args.date

    run_count = 0
    while True:
        run_count += 1
        validate = run_step(["python", "scripts/validate_odds_keys.py"], env=env)
        build = run_step(
            [
                "python",
                "scripts/build_mlb_slate_timing_context.py",
                "--date",
                date_text,
                "--out",
                str(slate_path),
            ],
            env=env,
        )
        enrich = run_step(
            [
                "python",
                "scripts/run_mlb_data_enrichment.py",
                "--date",
                date_text,
                "--slate",
                str(slate_path),
                "--artifacts-dir",
                str(artifacts_dir),
            ],
            env=env,
        )

        projections = load_json(artifacts_dir / "projections.json") if (artifacts_dir / "projections.json").exists() else {"games": []}
        remaining = []
        confirmed = []
        for game in projections.get("games", []):
            status = game.get("status")
            matchup = f"{game.get('away_team')} at {game.get('home_team')}"
            if game.get("lineups_confirmed"):
                confirmed.append(matchup)
                continue
            if status not in {"Final", "Completed Early"}:
                remaining.append(
                    {
                        "matchup": matchup,
                        "status": status,
                        "start_time": game.get("start_time"),
                        "blocked_reasons": game.get("blocked_reasons", []),
                    }
                )

        payload = {
            "date": date_text,
            "generated_at": datetime.now(MLB_TZ).isoformat(),
            "run_count": run_count,
            "validate_return_code": validate.returncode,
            "build_return_code": build.returncode,
            "enrich_return_code": enrich.returncode,
            "confirmed_games": confirmed,
            "remaining_games": remaining,
            "all_remaining_confirmed": len(remaining) == 0,
            "loop_enabled": args.loop,
            "poll_seconds": args.poll_seconds,
        }
        status_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Wrote {status_path}")

        if not args.loop:
            break
        if payload["all_remaining_confirmed"]:
            break
        if args.max_runs and run_count >= args.max_runs:
            break
        if datetime.now(MLB_TZ).date().isoformat() != date_text:
            break
        time.sleep(max(30, args.poll_seconds))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
