#!/usr/bin/env python
import argparse
import sys

from alert_pipe import send_telegram
from clients import BingClient, GoogleClient
from db import init_db, latest_by_query, upsert_results


def dedupe_by_url(rows: list[dict]) -> list[dict]:
    seen, out = set(), []
    for r in rows:
        url = r.get("url")
        if not url:
            continue
        if url in seen:
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


def parse_args():
    p = argparse.ArgumentParser(description="EQ12 MetaSearch (Bing + Google)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--query", help="Single query string")
    g.add_argument("--query-file", help="Path to a file with one query per line")
    p.add_argument("--count", type=int, default=10, help="Results per engine (default 10)")
    p.add_argument("--no-bing", action="store_true", help="Disable Bing")
    p.add_argument("--no-google", action="store_true", help="Disable Google")
    p.add_argument("--telegram", action="store_true", help="Send a Telegram message with results")
    p.add_argument(
        "--show-latest",
        action="store_true",
        help="After saving, print the latest rows for the query",
    )
    return p.parse_args()


def main():
    args = parse_args()
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
        print(f"[ok] {q}: fetched {len(rows)} unique; saved up to {saved} (dedup on url)")

        if args.telegram and rows:
            err = send_telegram(rows, header=f"MetaSearch: {q}")
            if err:
                print(f"[note] Telegram not sent: {err}")

        if args.show_latest:
            latest = latest_by_query(q, limit=20)
            for r in latest:
                print(f"- ({r['source']}) {r['title']} :: {r['url']}")


if __name__ == "__main__":
    main()
