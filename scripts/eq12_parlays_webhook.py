#!/usr/bin/env python3
"""
EQ12 Parlays Webhook (Gumroad Ping)
- Accepts x-www-form-urlencoded POSTs at /gumroad/ping
- Verifies sale via Gumroad API
- Only processes events for the configured PARLAYS product
- On sale: grant access (record in local registry)
- On refund: revoke access

Env:
  GUMROAD_ACCESS_TOKEN  (Creator API token)
  GUMROAD_PARLAYS_PRODUCT_ID  (target product id)
  WEBHOOK_SECRET (optional shared secret; if set, require header X-Webhook-Secret match)

Run locally:
  uvicorn scripts.eq12_parlays_webhook:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse

app = FastAPI()

DATA_REGISTRY = Path("data/parlays_access.json")
DATA_REGISTRY.parent.mkdir(parents=True, exist_ok=True)

API_BASE = "https://api.gumroad.com/v2"


def _post_form(url: str, data: dict[str, str]) -> dict:
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
        return json.loads(raw)


def _get_sale(access_token: str, sale_id: str) -> dict:
    url = f"{API_BASE}/sales/{urllib.parse.quote(sale_id)}"
    data = {"access_token": access_token}
    # Gumroad uses GET with form data; emulate via POST method="GET"
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="GET")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
        return json.loads(raw)


def load_registry() -> dict:
    if DATA_REGISTRY.exists():
        try:
            return json.loads(DATA_REGISTRY.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_registry(data: dict) -> None:
    DATA_REGISTRY.write_text(json.dumps(data, indent=2), encoding="utf-8")


@app.post("/gumroad/ping")
async def gumroad_ping(request: Request) -> Response:
    # Enforce secret if configured
    secret = os.environ.get("WEBHOOK_SECRET")
    if secret:
        header = request.headers.get("X-Webhook-Secret")
        if header != secret:
            raise HTTPException(status_code=403, detail="invalid secret")

    form = await request.form()
    payload = dict(form.items())

    access_token = os.environ.get("GUMROAD_ACCESS_TOKEN")
    product_target = os.environ.get("GUMROAD_PARLAYS_PRODUCT_ID")
    if not access_token or not product_target:
        raise HTTPException(status_code=500, detail="server not configured")

    sale_id = payload.get("sale_id") or payload.get("order_number")
    product_id = payload.get("product_id")
    refunded = payload.get("refunded")

    # Only parlay product is handled
    if not product_id or product_id != product_target:
        return PlainTextResponse("ignored (not parlays)")

    if not sale_id:
        raise HTTPException(status_code=400, detail="missing sale_id")

    # Verify via API
    try:
        sale_resp = _get_sale(access_token, sale_id)
    except Exception as exc:  # network or API error
        raise HTTPException(status_code=502, detail=f"verify error: {exc}") from exc

    ok = sale_resp.get("success")
    sale = sale_resp.get("sale") or {}
    if not ok:
        raise HTTPException(status_code=400, detail="sale verify failed")

    email = sale.get("purchase_email") or sale.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="missing email")

    # Update registry
    reg = load_registry()
    reg.setdefault("parlays", {})

    if refunded == "true" or sale.get("refunded"):
        reg["parlays"].pop(email, None)
        action = "revoked"
    else:
        reg["parlays"][email] = {
            "sale_id": sale_id,
            "product_id": product_id,
            "created_at": sale.get("created_at"),
            "license_key": sale.get("license_key"),
        }
        action = "granted"

    save_registry(reg)
    return PlainTextResponse(f"ok {action}")
