#!/usr/bin/env python3
"""
Gumroad Resource Subscriptions helper for EQ12
- Subscribes your creator account to key resources
  (sale, refund, disputes, subscription events)
- Requires env:
  - GUMROAD_ACCESS_TOKEN
  - GUMROAD_PING_URL (HTTPS endpoint for receiving POSTs)

Usage (local):
  set GUMROAD_ACCESS_TOKEN=...
  set GUMROAD_PING_URL=https://your.site/gumroad/ping
  python scripts/gumroad_subscribe.py

In CI, pass via env/secrets.
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.gumroad.com/v2/resource_subscriptions"
RESOURCES = [
    "sale",
    "refund",
    "dispute",
    "dispute_won",
    "cancellation",
    "subscription_updated",
    "subscription_ended",
    "subscription_restarted",
]


def _post(url: str, data: dict, method: str = "POST") -> dict:
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
        return json.loads(raw)


def subscribe_all(token: str, post_url: str) -> list[dict]:
    results = []
    for name in RESOURCES:
        payload = {
            "access_token": token,
            "resource_name": name,
            "post_url": post_url,
        }
        try:
            out = _post(API, payload, method="PUT")
            results.append(
                {
                    "resource": name,
                    "ok": out.get("success", False),
                    "response": out,
                }
            )
        except Exception as e:
            results.append({"resource": name, "ok": False, "error": str(e)})
        time.sleep(0.1)
    return results


def list_subscriptions(token: str, name: str) -> dict:
    payload = {"access_token": token, "resource_name": name}
    try:
        out = _post(API, payload, method="GET")
        return out
    except Exception as e:
        return {"success": False, "error": str(e)}


def main() -> int:
    token = os.environ.get("GUMROAD_ACCESS_TOKEN")
    post_url = os.environ.get("GUMROAD_PING_URL")
    if not token or not post_url:
        print("Missing env GUMROAD_ACCESS_TOKEN or GUMROAD_PING_URL", file=sys.stderr)
        return 2
    if not post_url.lower().startswith("https://"):
        print("GUMROAD_PING_URL must be HTTPS", file=sys.stderr)
        return 2

    print("Subscribing to Gumroad resources...")
    results = subscribe_all(token, post_url)
    ok = all(r.get("ok") for r in results)
    print(json.dumps({"type": "subscribe_results", "results": results}, indent=2))

    print("\nListing current subscriptions per resource...")
    listing = {}
    for name in RESOURCES:
        listing[name] = list_subscriptions(token, name)
    print(json.dumps({"type": "list_results", "listing": listing}, indent=2))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
