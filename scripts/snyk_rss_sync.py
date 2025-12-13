#!/usr/bin/env python3
"""
Snyk RSS feed watcher for EQ12
- Fetches https://updates.snyk.io/rss/
- Persists last seen items to data/snyk_rss_state.json
- Prints new items as JSON lines to stdout for CI to consume
"""

import json
import os
import sys
from datetime import UTC, datetime
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

FEED_URL = os.environ.get("SNYK_UPDATES_RSS", "https://updates.snyk.io/rss/")
STATE_PATH = os.path.join("data", "snyk_rss_state.json")


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def ensure_dirs():
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)


def load_state() -> dict:
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_state(state: dict) -> None:
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def fetch_feed_xml(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "EQ12-Snyk-Feed/1.0"})
    with urlopen(req, timeout=30) as resp:
        return resp.read()


def parse_items(xml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    # RSS 2.0: <rss><channel><item>
    channel = root.find("channel") if root.tag.endswith("rss") else None
    items = root.findall(".//item") if channel is None else channel.findall("item")

    parsed = []
    for item in items:

        def txt(tag, _item=item):
            el = _item.find(tag)
            return el.text.strip() if el is not None and el.text else ""

        parsed.append(
            {
                "title": txt("title"),
                "link": txt("link"),
                "pubDate": txt("pubDate"),
                "guid": txt("guid") or txt("link"),
                "description": txt("description"),
            }
        )
    return parsed


def main() -> int:
    ensure_dirs()
    state = load_state()
    seen = set(state.get("seen_guids", []))

    try:
        xml_bytes = fetch_feed_xml(FEED_URL)
        items = parse_items(xml_bytes)
    except Exception as e:
        print(json.dumps({"type": "error", "message": str(e)}))
        return 1

    new_items = [it for it in items if it.get("guid") and it["guid"] not in seen]

    # Print new items as JSON lines for workflow
    for it in reversed(new_items):  # oldest first
        print(json.dumps({"type": "snyk_update", **it}))
        seen.add(it["guid"])

    state["seen_guids"] = list(seen)
    state["last_checked"] = now_iso()
    save_state(state)

    return 0


if __name__ == "__main__":
    sys.exit(main())
