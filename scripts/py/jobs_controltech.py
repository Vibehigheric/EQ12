#!/usr/bin/env python3
r"""jobs_controltech.py — TOS-friendly Control Technician job finder (Indeed RSS)"""

import datetime as dt
import json
import os
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

KEYWORDS = [
    k.strip()
    for k in os.getenv(
        "JOB_KEYWORDS", "Control Technician,Controls Technician,Building Automation"
    ).split(",")
]
LOCATIONS = [l.strip() for l in os.getenv("LOCATIONS", "Buffalo,NY;Remote").split(";")]
OUT_DIR = Path(os.getenv("OUT_DIR", "C:/EQ12/logs")).expanduser()
OUT_DIR.mkdir(parents=True, exist_ok=True)


def indeed_rss(q, l):
    try:
        url = f"https://www.indeed.com/rss?q={urllib.parse.quote(q)}&l={urllib.parse.quote(l)}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        items = []
        for item in root.findall(".//item"):
            title = item.findtext("title") or ""
            link = item.findtext("link") or ""
            pub = item.findtext("{http://purl.org/dc/elements/1.1/}date") or ""
            items.append(
                {
                    "title": title,
                    "link": link,
                    "published": pub,
                    "source": "Indeed",
                    "query": q,
                    "location": l,
                }
            )
        return items
    except Exception as e:
        return [{"error": str(e), "source": "Indeed", "query": q, "location": l}]


def main() -> None:
    results = []
    for kw in KEYWORDS:
        for loc in LOCATIONS:
            results.extend(indeed_rss(kw, loc))
            time.sleep(0.2)
    out = {
        "type": "jobs",
        "ts": dt.datetime.now(dt.UTC).isoformat(),
        "total": len(results),
        "results": results[:200],
    }
    snap = OUT_DIR / "jobs_controltech.json"
    snap.write_text(json.dumps(out))
    print(json.dumps({"ok": True, "snapshot": str(snap), "count": len(results)}))


if __name__ == "__main__":
    main()
