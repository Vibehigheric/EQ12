#!/usr/bin/env python
import argparse
import sys

import feedparser

from clients import BingClient
from db import init_db, upsert_results

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


def google_news(query: str, count: int = 10) -> list[dict]:
    url = GOOGLE_NEWS_RSS.format(query=query.replace(" ", "+"))
    feed = feedparser.parse(url)
    rows = []
    for entry in (feed.entries or [])[:count]:
        rows.append(
            {
                "title": entry.get("title"),
                "url": entry.get("link"),
                "snippet": entry.get("summary"),
                "source": "google_news",
                "published_at": entry.get("published"),
            }
        )
    return rows


def dedupe_by_url(rows: list[dict]) -> list[dict]:
    seen, out = set(), []
    for r in rows:
        u = r.get("url")
        if not u or u in seen:
            continue
        seen.add(u)
        out.append(r)
    return out


def main():
    p = argparse.ArgumentParser(description="EQ12 News Aggregator (Bing News + Google News RSS)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--query")
    g.add_argument("--query-file")
    p.add_argument("--count", type=int, default=10)
    args = p.parse_args()

    init_db()
    bing = BingClient()

    queries = []
    if args.query:
        queries = [args.query.strip()]
    else:
        with open(args.query_file, encoding="utf-8") as f:
            queries = [line.strip() for line in f if line.strip()]

    for q in queries:
        rows: list[dict] = []
        try:
            rows += bing.news_search(q, count=args.count, freshness="Day")
        except Exception as e:
            print(f"[warn] Bing News failed: {e}", file=sys.stderr)
        try:
            rows += google_news(q, count=args.count)
        except Exception as e:
            print(f"[warn] Google News RSS failed: {e}", file=sys.stderr)

        rows = dedupe_by_url(rows)
        saved = upsert_results(q, rows)
        print(f"[ok] {q}: news fetched {len(rows)}; saved up to {saved}")


if __name__ == "__main__":
    main()
