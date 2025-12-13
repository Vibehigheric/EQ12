import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.getenv("META_DB_PATH", "meta_search.sqlite3")

SCHEMA = """
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    title TEXT,
    url TEXT UNIQUE,
    snippet TEXT,
    source TEXT,
    published_at TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_results_query ON results(query);
CREATE INDEX IF NOT EXISTS idx_results_source ON results(source);

CREATE TABLE IF NOT EXISTS offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    title TEXT,
    url TEXT UNIQUE,
    reward TEXT,
    category TEXT,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def upsert_results(query: str, rows: list[dict]) -> int:
    if not rows:
        return 0
    count = 0
    with get_conn() as conn:
        for r in rows:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO results(query, title, url, snippet, source, published_at) VALUES (?,?,?,?,?,?)",
                    (
                        query,
                        r.get("title"),
                        r.get("url"),
                        r.get("snippet"),
                        r.get("source"),
                        r.get("published_at"),
                    ),
                )
                count += 1
            except Exception:
                pass
    return count


def latest_by_query(query: str, limit: int = 20) -> list[dict]:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT title, url, snippet, source, published_at, fetched_at FROM results WHERE query=? ORDER BY fetched_at DESC LIMIT ?",
            (query, limit),
        )
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row, strict=False)) for row in cur.fetchall()]


def upsert_offers(rows: list[dict]) -> int:
    if not rows:
        return 0
    count = 0
    with get_conn() as conn:
        for r in rows:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO offers(source, title, url, reward, category) VALUES (?,?,?,?,?)",
                    (
                        r.get("source"),
                        r.get("title"),
                        r.get("url"),
                        r.get("reward"),
                        r.get("category"),
                    ),
                )
                count += 1
            except Exception:
                pass
    return count


def latest_offers(limit: int = 20) -> list[dict]:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT source, title, url, reward, category, fetched_at FROM offers ORDER BY fetched_at DESC LIMIT ?",
            (limit,),
        )
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row, strict=False)) for row in cur.fetchall()]
