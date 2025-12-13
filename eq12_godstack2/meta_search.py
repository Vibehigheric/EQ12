#!/usr/bin/env python
import argparse
import sys

from alert_pipe import send_results
from clients import BingClient, GoogleClient
from db import init_db, latest_by_query, upsert_results


def dedupe_by_url(rows: list[dict]) -> list[dict]:
    seen, out = set(), []
    for r in rows:
        url = r.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(r)
    return out


def run_search(query: str, count: int = 10, include_bing=True, include_google=True) -> list[dict]:
    rows: list[dict] = []
    if include_bing:
        try:
            rows += BingClient().web_search(query, count=count)
        except Exception as e:
            print(f"[warn] Bing search failed: {e}", file=sys.stderr)
    if include_google:
        try:
            rows += GoogleClient().web_search(query, count=count)
        except Exception as e:
            print(f"[warn] Google search failed: {e}", file=sys.stderr)
    return dedupe_by_url(rows)


def main():
    p = argparse.ArgumentParser(description="EQ12 MetaSearch (Google + Bing)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--query")
    g.add_argument("--query-file")
    p.add_argument("--count", type=int, default=10)
    p.add_argument("--no-bing", action="store_true")
    p.add_argument("--no-google", action="store_true")
    p.add_argument("--telegram", action="store_true")
    p.add_argument("--show-latest", action="store_true")
    args = p.parse_args()

    init_db()

    queries = []
    if args.query:
        queries = [args.query.strip()]
    else:
        with open(args.query_file, encoding="utf-8") as f:
            queries = [line.strip() for line in f if line.strip()]

    for q in queries:
        rows = run_search(
            q,
            count=args.count,
            include_bing=not args.no_bing,
            include_google=not args.no_google,
        )
        saved = upsert_results(q, rows)
        print(f"[ok] {q}: fetched {len(rows)} unique; saved up to {saved}")
        if args.telegram and rows:
            err = send_results(rows, header=f"MetaSearch: {q}")
            if err:
                print(f"[note] Telegram not sent: {err}")
        if args.show_latest:
            for r in latest_by_query(q, limit=20):
                print(f"- ({r['source']}) {r['title']} :: {r['url']}")


if __name__ == "__main__":
    main()
