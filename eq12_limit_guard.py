# eq12_limit_guard.py
from __future__ import annotations

import json
import os
import threading
from datetime import date, datetime
from functools import wraps

LOCK = threading.Lock()
USAGE_FILE = os.path.join(os.getcwd(), "logs", "api_usage.jsonl")
DAILY_BUDGET_USD = float(os.getenv("EQ12_DAILY_BUDGET_USD", "25.0"))


def _today():
    return date.today().isoformat()


def _sum_today():
    total = 0.0
    if not os.path.exists(USAGE_FILE):
        return 0.0
    with open(USAGE_FILE, encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line)
                if row.get("day") == _today():
                    total += float(row.get("cost_usd", 0))
            except Exception:
                pass
    return total


def _append_usage(service: str, est_cost: float, meta: dict):
    os.makedirs(os.path.dirname(USAGE_FILE), exist_ok=True)
    rec = {
        "day": _today(),
        "ts": datetime.utcnow().isoformat() + "Z",
        "service": service,
        "cost_usd": round(est_cost, 6),
        **meta,
    }
    with open(USAGE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def require_budget(service: str, est_cost_usd: float):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with LOCK:
                spent = _sum_today()
                if spent + est_cost_usd > DAILY_BUDGET_USD:
                    raise RuntimeError(f"Budget exceeded: ${spent:.2f}/${DAILY_BUDGET_USD:.2f}")
                _append_usage(service, est_cost_usd, {"fn": fn.__name__})
            return fn(*args, **kwargs)

        return wrapper

    return deco
