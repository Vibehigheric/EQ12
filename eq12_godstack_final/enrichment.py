#!/usr/bin/env python
"""
Enrichment pipeline: takes rows from DB (results/offers), calls GPT with Service Key,
and appends summarized/ranked content back into DB (optional) or prints to console/Telegram.
"""

import os
import sqlite3
import sys

from openai import OpenAI

DB_PATH = os.getenv("META_DB_PATH", "meta_search.sqlite3")
SERVICE_KEY = os.getenv("OPENAI_SERVICE_KEY")


def fetch_recent_results(limit=50) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "SELECT query, title, snippet, url, source, fetched_at FROM results ORDER BY fetched_at DESC LIMIT ?",
        (limit,),
    )
    cols = [c[0] for c in cur.description]
    rows = [dict(zip(cols, r, strict=False)) for r in cur.fetchall()]
    conn.close()
    return rows


def enrich(rows: list[dict], stack: str = "general") -> str:
    if not SERVICE_KEY:
        raise RuntimeError("Missing OPENAI_SERVICE_KEY env var.")
    client = OpenAI(api_key=SERVICE_KEY)
    text = "\n".join([f"{r['title']} :: {r['snippet']} ({r['url']})" for r in rows])
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"You are an expert analyst for {stack}. Summarize and rank items by actionable value. Return bullet points.",
            },
            {"role": "user", "content": text},
        ],
    )
    return resp.choices[0].message.content


def main():
    stack = sys.argv[1] if len(sys.argv) > 1 else "general"
    rows = fetch_recent_results()
    summary = enrich(rows, stack=stack)
    print("=== Enrichment Summary ===")
    print(summary)


if __name__ == "__main__":
    main()
