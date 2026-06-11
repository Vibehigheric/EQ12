from __future__ import annotations

import json
from pathlib import Path

from scripts import validate_odds_keys


def test_mask_key_masks_middle() -> None:
    assert validate_odds_keys.mask_key("abcdefghijklmnop") == "abcd...mnop"


def test_map_status_covers_expected_codes() -> None:
    assert validate_odds_keys.map_status(200, [{"id": "game"}]) == "VALID"
    assert validate_odds_keys.map_status(200, []) == "VALID_EMPTY"
    assert validate_odds_keys.map_status(401, None) == "INVALID_KEY"
    assert validate_odds_keys.map_status(403, None) == "FORBIDDEN_OR_QUOTA"
    assert validate_odds_keys.map_status(429, None) == "RATE_LIMITED"


def test_collect_candidates_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("ODDS_API_KEY", "1234567890123456")
    monkeypatch.delenv("THE_ODDS_API_KEY", raising=False)
    monkeypatch.delenv("THEODDSAPI_KEY", raising=False)
    monkeypatch.delenv("ODDSAPI_API_KEY", raising=False)
    monkeypatch.delenv("SPORTS_ODDS_API_KEY", raising=False)
    monkeypatch.delenv("EQ12_ODDS_API_KEY", raising=False)
    candidates = validate_odds_keys.collect_candidates()
    assert any(item["env_name"] == "ODDS_API_KEY" for item in candidates)


def test_main_writes_health_report_without_keys(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ODDS_API_KEY", raising=False)
    monkeypatch.delenv("THE_ODDS_API_KEY", raising=False)
    monkeypatch.delenv("THEODDSAPI_KEY", raising=False)
    monkeypatch.delenv("ODDSAPI_API_KEY", raising=False)
    monkeypatch.delenv("SPORTS_ODDS_API_KEY", raising=False)
    monkeypatch.delenv("EQ12_ODDS_API_KEY", raising=False)
    assert validate_odds_keys.main() == 0
    payload = json.loads(Path("artifacts/mlb/odds_key_health.json").read_text(encoding="utf-8"))
    assert payload["provider_status"] == "NO_CONFIGURED_KEYS"
    assert payload["keys_tested_count"] == 0
