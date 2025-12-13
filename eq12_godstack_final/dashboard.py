#!/usr/bin/env python
import os
import sqlite3

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse

DB_PATH = os.getenv("META_DB_PATH", "meta_search.sqlite3")

app = FastAPI(title="EQ12 GODSTACK Dashboard")


def query_db(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(sql, params)
    cols = [c[0] for c in cur.description]
    rows = [dict(zip(cols, r, strict=False)) for r in cur.fetchall()]
    conn.close()
    return rows


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>EQ12 GODSTACK Dashboard</h2>
    <ul>
      <li><a href='/results'>Latest Results</a></li>
      <li><a href='/offers'>Latest Offers</a></li>
    </ul>
    """


@app.get("/results")
def get_results(q: str = Query(None, description="Filter by query")):
    if q:
        rows = query_db(
            "SELECT query,title,url,snippet,source,fetched_at FROM results WHERE query LIKE ? ORDER BY fetched_at DESC LIMIT 100",
            (f"%{q}%",),
        )
    else:
        rows = query_db(
            "SELECT query,title,url,snippet,source,fetched_at FROM results ORDER BY fetched_at DESC LIMIT 100"
        )
    return rows


@app.get("/offers")
def get_offers():
    rows = query_db(
        "SELECT source,title,url,reward,category,fetched_at FROM offers ORDER BY fetched_at DESC LIMIT 100"
    )
    return rows
