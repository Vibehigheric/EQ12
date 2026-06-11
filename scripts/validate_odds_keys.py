#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


CANDIDATE_ENV_NAMES = (
    "THEODDSAPI_KEY",
    "THE_ODDS_API_KEY",
    "ODDS_API_KEY",
    "ODDSAPI_API_KEY",
    "SPORTS_ODDS_API_KEY",
    "EQ12_ODDS_API_KEY",
)
PLACEHOLDER_PATTERNS = (
    "PLACEHOLDER",
    "REPLACE_ME",
    "YOUR_API_KEY_HERE",
    "YOUR_KEY_HERE",
    "DEMO_KEY",
)
ARTIFACT_PATH = Path("artifacts/mlb/odds_key_health.json")
TEST_URL = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def mask_key(value: str) -> str:
    stripped = value.strip()
    if len(stripped) <= 8:
        return "*" * len(stripped)
    return f"{stripped[:4]}...{stripped[-4:]}"


def is_viable_key(value: str | None) -> bool:
    if not value:
        return False
    stripped = value.lstrip("\ufeff").strip()
    if len(stripped) < 12:
        return False
    upper = stripped.upper()
    return not any(token in upper for token in PLACEHOLDER_PATTERNS)


def load_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip("'").strip('"')
    except OSError:
        return {}
    return values


def load_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def collect_candidates() -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    seen: set[str] = set()

    def add_candidate(env_name: str, source: str, value: str | None) -> None:
        if not is_viable_key(value):
            return
        normalized = value.lstrip("\ufeff").strip()
        if normalized in seen:
            return
        seen.add(normalized)
        candidates.append(
            {
                "env_name": env_name,
                "source": source,
                "key": normalized,
            }
        )

    for env_name in CANDIDATE_ENV_NAMES:
        add_candidate(env_name, f"env:{env_name}", os.getenv(env_name))

    dotenv_values = load_dotenv(Path(".env"))
    for env_name in CANDIDATE_ENV_NAMES:
        add_candidate(env_name, f"dotenv:{env_name}", dotenv_values.get(env_name))

    config_files = {
        "keys/oddsapi.txt": Path("keys/oddsapi.txt"),
        "keys/odds_api_key.txt": Path("keys/odds_api_key.txt"),
        "keys/credentials.json": Path("keys/credentials.json"),
        "keys/creds.json": Path("keys/creds.json"),
    }
    for label, path in config_files.items():
        if path.suffix.lower() == ".txt" and path.exists():
            try:
                add_candidate("FILE_KEY", f"file:{label}", path.read_text(encoding="utf-8"))
            except OSError:
                continue
            continue

        payload = load_json_file(path)
        if not payload:
            continue
        odds_api = payload.get("odds_api")
        if isinstance(odds_api, dict):
            for nested_key in ("api_key", "key"):
                add_candidate("FILE_KEY", f"file:{label}:odds_api.{nested_key}", odds_api.get(nested_key))
        for env_name in CANDIDATE_ENV_NAMES:
            add_candidate(env_name, f"file:{label}:{env_name}", payload.get(env_name))

    return candidates


def request_odds(key: str) -> tuple[int, list[Any] | None, dict[str, str]]:
    params = urlencode(
        {
            "apiKey": key,
            "regions": "us",
            "markets": "h2h",
            "oddsFormat": "american",
        }
    )
    request = Request(
        f"{TEST_URL}?{params}",
        headers={"User-Agent": "EQ12-Odds-Key-Validator/1.0"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
            headers = {k.lower(): v for k, v in response.headers.items()}
            return int(response.status), payload if isinstance(payload, list) else [], headers
    except HTTPError as exc:
        headers = {k.lower(): v for k, v in exc.headers.items()}
        return exc.code, None, headers
    except (URLError, TimeoutError, json.JSONDecodeError):
        return 0, None, {}


def map_status(http_status: int, payload: list[Any] | None) -> str:
    if http_status == 200:
        if payload:
            return "VALID"
        return "VALID_EMPTY"
    if http_status == 401:
        return "INVALID_KEY"
    if http_status == 403:
        return "FORBIDDEN_OR_QUOTA"
    if http_status == 429:
        return "RATE_LIMITED"
    if http_status >= 500:
        return "PROVIDER_ERROR"
    if http_status == 0:
        return "REQUEST_ERROR"
    return "UNKNOWN_ERROR"


def write_github_env(selected: dict[str, Any] | None, provider_status: str) -> None:
    github_env = os.getenv("GITHUB_ENV")
    if not github_env:
        return
    env_path = Path(github_env)
    lines = [f"ODDS_PROVIDER_STATUS={provider_status}"]
    if selected is not None:
        lines.extend(
            [
                f"SELECTED_ODDS_API_KEY={selected['key']}",
                f"SELECTED_ODDS_KEY_SOURCE={selected['source']}",
                f"SELECTED_ODDS_KEY_ENV_NAME={selected['env_name']}",
                f"ODDS_API_KEY={selected['key']}",
            ]
        )
    existing = ""
    if env_path.exists():
        existing = env_path.read_text(encoding="utf-8")
    env_path.write_text(existing + "\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tested_at = now_utc()
    candidates = collect_candidates()
    results: list[dict[str, Any]] = []
    selected: dict[str, Any] | None = None

    for candidate in candidates:
        http_status, payload, headers = request_odds(candidate["key"])
        status = map_status(http_status, payload)
        record = {
            "env_name": candidate["env_name"],
            "key_masked": mask_key(candidate["key"]),
            "status": status,
            "http_status": http_status,
            "quota_remaining_if_available": headers.get("x-requests-remaining")
            or headers.get("x-ratelimit-remaining"),
            "selected": False,
            "tested_at": tested_at,
            "source": candidate["source"],
        }
        if selected is None and status in {"VALID", "VALID_EMPTY"}:
            record["selected"] = True
            selected = candidate
        results.append(record)

    invalid_key_count = sum(1 for item in results if item["status"] == "INVALID_KEY")
    rate_limited_count = sum(1 for item in results if item["status"] == "RATE_LIMITED")
    provider_status = "NO_CONFIGURED_KEYS"
    if selected is not None:
        provider_status = "VALID_KEY_SELECTED"
    elif any(item["status"] == "FORBIDDEN_OR_QUOTA" for item in results):
        provider_status = "FORBIDDEN_OR_QUOTA"
    elif any(item["status"] == "RATE_LIMITED" for item in results):
        provider_status = "RATE_LIMITED"
    elif any(item["status"] == "PROVIDER_ERROR" for item in results):
        provider_status = "PROVIDER_ERROR"
    elif results:
        provider_status = "NO_VALID_KEYS"

    report = {
        "tested_at": tested_at,
        "provider_status": provider_status,
        "keys_tested_count": len(results),
        "selected_env_name": selected["env_name"] if selected else None,
        "selected_key_masked": mask_key(selected["key"]) if selected else None,
        "invalid_key_count": invalid_key_count,
        "rate_limited_count": rate_limited_count,
        "results": results,
    }
    ARTIFACT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_github_env(selected, provider_status)
    print(
        json.dumps(
            {
                "provider_status": provider_status,
                "keys_tested_count": len(results),
                "selected_env_name": report["selected_env_name"],
                "selected_key_masked": report["selected_key_masked"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
