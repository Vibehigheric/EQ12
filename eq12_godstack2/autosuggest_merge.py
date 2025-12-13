#!/usr/bin/env python
import argparse
import json
import sys
import urllib.parse

import requests

from clients import BingClient

# Google suggest (unofficial) returns JSONP-ish; we'll use a documented endpoint used by Chrome:
GOOGLE_SUGGEST = "https://suggestqueries.google.com/complete/search?client=chrome&q={q}"


def google_suggest(q: str) -> list[str]:
    url = GOOGLE_SUGGEST.format(q=urllib.parse.quote_plus(q))
    js = requests.get(url, timeout=15).json()
    # js structure: [query, [suggestion1, suggestion2, ...], ...]
    if isinstance(js, list) and len(js) > 1 and isinstance(js[1], list):
        return [str(x) for x in js[1]]
    return []


def main():
    p = argparse.ArgumentParser(description="EQ12 Autosuggest Merger (Bing + Google)")
    p.add_argument("--query", required=True)
    p.add_argument("--json", action="store_true", help="Print JSON list")
    args = p.parse_args()

    bing = BingClient()
    b = []
    g = []
    try:
        b = bing.autosuggest(args.query)
    except Exception as e:
        print(f"[warn] Bing autosuggest failed: {e}", file=sys.stderr)
    try:
        g = google_suggest(args.query)
    except Exception as e:
        print(f"[warn] Google suggest failed: {e}", file=sys.stderr)

    merged = []
    seen = set()
    for s in b + g:
        if s not in seen:
            seen.add(s)
            merged.append(s)

    if args.json:
        print(json.dumps(merged, ensure_ascii=False, indent=2))
    else:
        for s in merged:
            print("-", s)


if __name__ == "__main__":
    main()
