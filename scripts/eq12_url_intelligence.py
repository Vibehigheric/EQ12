"""
EQ12 URL INTELLIGENCE SCANNER - Production Grade
Async, hash-based change detection, SQLite history, category analyzers
"""

import asyncio
import aiohttp
import argparse
import hashlib
import json
import logging
import os
import sqlite3
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(1)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "..", "logs", "url_intelligence.db")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("EQ12.URLIntelligence")


@dataclass
class URLTask:
    name: str
    url: str
    category: str
    interval_minutes: int


@contextmanager
def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT UNIQUE,
            category TEXT,
            created_at TEXT
        )""")
        
        conn.execute("""CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY,
            url_id INTEGER,
            fetched_at TEXT,
            status_code INTEGER,
            content_hash TEXT,
            content_length INTEGER,
            error TEXT,
            meta_json TEXT,
            FOREIGN KEY(url_id) REFERENCES urls(id)
        )""")
        
        conn.execute("""CREATE INDEX IF NOT EXISTS idx_snap
            ON snapshots(url_id, fetched_at DESC)""")
        
        conn.execute("""CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY,
            started_at TEXT,
            finished_at TEXT,
            total INTEGER,
            success INTEGER,
            changed INTEGER,
            errors INTEGER
        )""")
    
    logger.info(f"Database: {DB_PATH}")


def upsert_url(task: URLTask) -> int:
    with get_db() as conn:
        cur = conn.execute("SELECT id FROM urls WHERE url = ?", (task.url,))
        row = cur.fetchone()
        if row:
            return row["id"]
        
        cur = conn.execute(
            "INSERT INTO urls (name, url, category, created_at) VALUES (?, ?, ?, ?)",
            (task.name, task.url, task.category, datetime.now(timezone.utc).isoformat())
        )
        return cur.lastrowid


def get_last_snap(url_id: int):
    with get_db() as conn:
        cur = conn.execute(
            "SELECT * FROM snapshots WHERE url_id = ? ORDER BY fetched_at DESC LIMIT 1",
            (url_id,)
        )
        return cur.fetchone()


def insert_snap(url_id, status, hash_val, length, error, meta):
    with get_db() as conn:
        conn.execute(
            """INSERT INTO snapshots 
            (url_id, fetched_at, status_code, content_hash, content_length, error, meta_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (url_id, datetime.now(timezone.utc).isoformat(), status, hash_val, length, error, json.dumps(meta))
        )


class AnalyzerRegistry:
    def __init__(self):
        self.reg = {}
    
    def register(self, cat, fn):
        self.reg.setdefault(cat, []).append(fn)
    
    def run(self, cat, task, text, meta):
        for fn in self.reg.get(cat, []):
            try:
                meta = fn(task, text, meta) or meta
            except:
                pass
        return meta


analyzers = AnalyzerRegistry()


def analyze_sports(task, text, meta):
    keywords = ["statcast", "mlb", "odds", "prop"]
    found = [k for k in keywords if k in text.lower()]
    if found:
        meta["sports_kw"] = found
    return meta


def analyze_maps(task, text, meta):
    if "openstreetmap" in text.lower():
        meta["osm_detected"] = True
    return meta


analyzers.register("sports_stats", analyze_sports)
analyzers.register("maps_routing", analyze_maps)


class URLScanner:
    def __init__(self, tasks, user_agent, max_con, per_host, timeout):
        self.tasks = tasks
        self.user_agent = user_agent
        self.max_con = max_con
        self.per_host = per_host
        self.timeout = timeout
        self.sems = {}
        self.run_id = None
        self.success = 0
        self.changed = 0
        self.errors = 0
        self.changed_urls = []
    
    def get_sem(self, host):
        if host not in self.sems:
            self.sems[host] = asyncio.Semaphore(self.per_host)
        return self.sems[host]
    
    async def fetch(self, sess, task):
        host = urlparse(task.url).netloc
        sem = self.get_sem(host)
        meta = {"url": task.url, "name": task.name, "category": task.category}
        
        async with sem:
            try:
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with sess.get(task.url, headers={"User-Agent": self.user_agent}, timeout=timeout, ssl=False) as r:
                    meta["content_type"] = r.headers.get("Content-Type", "")
                    content = await r.read()
                    meta["bytes"] = len(content)
                    return r.status, content, meta, None
            except Exception as e:
                return 0, None, meta, str(e)
    
    @staticmethod
    def hash_content(data):
        return hashlib.sha256(data).hexdigest()
    
    async def process(self, sess, task):
        url_id = upsert_url(task)
        status, content, meta, error = await self.fetch(sess, task)
        
        if error:
            logger.warning(f"Error: {task.url}: {error}")
            insert_snap(url_id, None, None, None, error, meta)
            self.errors += 1
            return
        
        hash_val = None
        length = None
        text = ""
        
        if content:
            hash_val = self.hash_content(content)
            length = len(content)
            try:
                text = content[:50000].decode("utf-8", errors="ignore")
            except:
                pass
        
        if text:
            meta = analyzers.run(task.category, task, text, meta)
        
        last = get_last_snap(url_id)
        changed = False
        
        if not last:
            changed = True
            meta["reason"] = "first"
        elif last["content_hash"] != hash_val:
            changed = True
            meta["reason"] = "changed"
        
        insert_snap(url_id, status, hash_val, length, None, meta)
        
        self.success += 1
        if changed:
            self.changed += 1
            self.changed_urls.append(f"{task.name}")
            logger.info(f"✅ CHANGED: {task.name}")
        else:
            logger.info(f"⚪ unchanged: {task.name}")
    
    async def run_once(self):
        with get_db() as conn:
            cur = conn.execute(
                "INSERT INTO runs (started_at, total, success, changed, errors) VALUES (?, 0, 0, 0, 0)",
                (datetime.now(timezone.utc).isoformat(),)
            )
            self.run_id = cur.lastrowid
        
        logger.info(f"Run #{self.run_id}: {len(self.tasks)} URLs")
        
        conn_obj = aiohttp.TCPConnector(limit=self.max_con, ssl=False)
        async with aiohttp.ClientSession(connector=conn_obj) as sess:
            await asyncio.gather(*(self.process(sess, t) for t in self.tasks))
        
        with get_db() as conn:
            conn.execute(
                "UPDATE runs SET finished_at=?, total=?, success=?, changed=?, errors=? WHERE id=?",
                (datetime.now(timezone.utc).isoformat(), len(self.tasks), self.success, self.changed, self.errors, self.run_id)
            )
        
        logger.info(f"Run #{self.run_id} done: ✅{self.success} 🔄{self.changed} ❌{self.errors}")
        
        return {
            "run_id": self.run_id,
            "total": len(self.tasks),
            "success": self.success,
            "changed": self.changed,
            "errors": self.errors,
            "changed_urls": self.changed_urls
        }


def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    
    glob = cfg.get("global", {}) or {}
    items = cfg.get("urls", []) or []
    
    tasks = []
    for it in items:
        tasks.append(URLTask(
            name=it["name"],
            url=it["url"],
            category=it.get("category", "generic"),
            interval_minutes=int(it.get("interval_minutes", glob.get("default_interval_minutes", 60)))
        ))
    return glob, tasks


async def send_telegram(token, chat, msg):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat, "text": msg, "parse_mode": "Markdown"}
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, json=data) as r:
                return r.status == 200
    except:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--run-once", action="store_true")
    parser.add_argument("--telegram", action="store_true")
    args = parser.parse_args()
    
    init_db()
    
    glob, tasks = load_config(args.config)
    if not tasks:
        logger.error("No URLs")
        sys.exit(1)
    
    scanner = URLScanner(
        tasks=tasks,
        user_agent=glob.get("user_agent", "EQ12/1.0"),
        max_con=int(glob.get("max_concurrent", 20)),
        per_host=int(glob.get("per_host_limit", 5)),
        timeout=int(glob.get("request_timeout_seconds", 15))
    )
    
    async def run():
        res = await scanner.run_once()
        
        if args.telegram and res["changed"] > 0:
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            chat = os.getenv("TELEGRAM_CHAT_ID")
            if token and chat:
                msg = f"🔔 *EQ12 URL Scanner*\n\nRun #{res['run_id']}\n✅ {res['success']} | 🔄 {res['changed']} | ❌ {res['errors']}"
                await send_telegram(token, chat, msg)
    
    if args.run_once:
        asyncio.run(run())
    else:
        try:
            while True:
                asyncio.run(run())
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Stopped")


if __name__ == "__main__":
    main()
