from __future__ import annotations

import json
from pathlib import Path


SPEC_FILES = [
    "specs/edgegod_system_spec.yaml",
    "specs/edgegod_database_schema.sql",
    "specs/edgegod_api_contracts.json",
    "specs/edgegod_orchestration_flow.yaml",
    "specs/edgegod_feature_registry.yaml",
    "specs/edgegod_model_registry.yaml",
    "specs/edgegod_live_state_events.yaml",
    "specs/edgegod_clv_ledger_schema.sql",
    "specs/edgegod_monte_carlo_schema.yaml",
    "specs/edgegod_agent_protocol.yaml",
]


def test_required_spec_files_exist() -> None:
    for relative_path in SPEC_FILES:
        assert Path(relative_path).exists(), f"missing required spec file: {relative_path}"


def test_api_contracts_json_is_valid() -> None:
    payload = json.loads(Path("specs/edgegod_api_contracts.json").read_text(encoding="utf-8"))
    assert payload["version"] == "1.0"
    assert "artifacts" in payload
    assert any(item["name"] == "release_card" for item in payload["artifacts"])


def test_system_spec_mentions_readiness_thresholds() -> None:
    content = Path("specs/edgegod_system_spec.yaml").read_text(encoding="utf-8")
    assert "readiness:" in content
    assert "release: 0.80" in content
    assert "confidence_min: 0.70" in content
