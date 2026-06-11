from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts import run_mlb_data_enrichment


def test_no_valid_odds_key_writes_exact_no_bet_message(monkeypatch, tmp_path) -> None:
    artifacts_dir = tmp_path / "artifacts" / "mlb"
    artifacts_dir.mkdir(parents=True)
    slate_path = artifacts_dir / "slate_context.json"
    slate_path.write_text(
        json.dumps(
            {
                "games_found": 1,
                "games": [
                    {
                        "game_id": "test-game",
                        "away_team": "Away",
                        "home_team": "Home",
                        "status": "Scheduled",
                        "start_time": "2026-06-11T19:00:00-04:00",
                        "away_pitcher": {"name": "Pitcher A"},
                        "home_pitcher": {"name": "Pitcher B"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (artifacts_dir / "odds_key_health.json").write_text(
        json.dumps({"provider_status": "NO_VALID_KEYS", "keys_tested_count": 2}),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(run_mlb_data_enrichment, "collect_odds_api_candidates", lambda: [])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_mlb_data_enrichment.py",
            "--date",
            "2026-06-11",
            "--slate",
            str(slate_path),
            "--artifacts-dir",
            str(artifacts_dir),
        ],
    )

    assert run_mlb_data_enrichment.main() == 0
    release_card = (artifacts_dir / "release_card.md").read_text(encoding="utf-8")
    assert "NO RELEASE-GRADE MLB PLAYS TODAY" in release_card
    assert "Reason: no valid odds API key available" in release_card
    assert "Mode: NO_BET_HOLD" in release_card
