"""SQLite logging backend for EQ12 Commander++"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS action_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at REAL NOT NULL,
    plan_json TEXT NOT NULL,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS task_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at REAL NOT NULL,
    task TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    result_json TEXT
);
"""


class CommanderDatabase:
    """Simple wrapper around SQLite for analytics and logging."""

    def __init__(self, base_dir: Path):
        self.db_path = base_dir / "eq12_commander.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    def store_action_plan(
        self, plan: dict[str, Any], metadata: dict[str, Any] | None = None
    ) -> int:
        payload = json.dumps(plan, ensure_ascii=False)
        metadata_json = json.dumps(metadata or {}, ensure_ascii=False)
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO action_plans (created_at, plan_json, metadata) VALUES (?, ?, ?)",
                (time.time(), payload, metadata_json),
            )
            conn.commit()
            return cursor.lastrowid

    def log_execution(self, task: str, priority: str, status: str, result: dict[str, Any]) -> int:
        result_json = json.dumps(result, ensure_ascii=False)
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO task_executions (created_at, task, priority, status, result_json) VALUES (?, ?, ?, ?, ?)",
                (time.time(), task, priority, status, result_json),
            )
            conn.commit()
            return cursor.lastrowid

    def summary(self) -> dict[str, Any]:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM action_plans")
            plans = cursor.fetchone()[0]
            cursor.execute(
                "SELECT priority, status, COUNT(*) FROM task_executions GROUP BY priority, status"
            )
            rows = cursor.fetchall()
        summary: dict[str, dict[str, int]] = {}
        for priority, status, count in rows:
            summary.setdefault(priority, {})[status] = count
        return {"plans": plans, "executions": summary}


def build_database(config: dict, base_dir: Path) -> CommanderDatabase:
    return CommanderDatabase(base_dir)
