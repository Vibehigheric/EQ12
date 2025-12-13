#!/usr/bin/env python3
"""Cross-platform bookmark sync helper for EQ12.

Writes a Netscape-format bookmarks HTML file and can export/import JSON lists.
Dry-run by default; pass --apply to write files.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_bookmarks(path: Path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON string: {e}")
        data = {}  # Safe fallback
    if not isinstance(data, list):
        raise ValueError("bookmarks JSON must be a list")
    return data


def build_netscape_html(bookmarks: list) -> str:
    lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        "<TITLE>EQ12 Bookmarks</TITLE>",
        "<H1>EQ12 Bookmarks</H1>",
        "<DL><p>",
    ]
    for bm in bookmarks:
        title = bm.get("title", "").replace('"', "")
        url = bm.get("url", "")
        lines.append(f'    <DT><A HREF="{url}">{title}</A>')
    lines.append("</DL><p>")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--bookmarks",
        type=Path,
        default=Path("C:/EQ12/configs/bookmarks.json"))
    p.add_argument("--profile", type=Path, default=Path("C:/EQ12/profiles/firefox-bot"))
    p.add_argument("--out-html", type=Path, help="Write netscape HTML to this file")
    p.add_argument("--apply", action="store_true", help="Perform writes")
    args = p.parse_args()

    if not args.bookmarks.exists():
        print("Bookmarks JSON not found:", args.bookmarks, file=sys.stderr)
        raise SystemExit(2)

    bms = load_bookmarks(args.bookmarks)
    html = build_netscape_html(bms)

    if args.out_html:
        if args.apply:
            args.out_html.parent.mkdir(parents=True, exist_ok=True)
            args.out_html.write_text(html, encoding="utf-8")
            print("Wrote", args.out_html)
        else:
            print("Dry-run: would write", args.out_html)
    else:
        # default: write to profile/bookmarks_auto.html when apply
        out = args.profile / "bookmarks_auto.html"
        if args.apply:
            args.profile.mkdir(parents=True, exist_ok=True)
            out.write_text(html, encoding="utf-8")
            print("Wrote", out)
        else:
            print("Dry-run: would write", out)


if __name__ == "__main__":
    main()
