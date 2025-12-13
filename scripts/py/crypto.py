import datetime as dt
import json
import os
from pathlib import Path

import requests

#!/usr/bin/env python3

PAIRS = [p.strip() for p in os.getenv("PAIRS", "BTC-USD,ETH-USD").split(",") if p.strip()]
OUT_DIR = Path(os.getenv("OUT_DIR", "C:/EQ12/logs")).expanduser()
OUT_DIR.mkdir(parents=True, exist_ok=True)
BINANCE = os.getenv("BINANCE", "0") == "1"


def coinbase_spot(pair) -> None:
    try:
        r = requests.get(f"https://api.coinbase.com/v2/prices/{pair}/spot", timeout=10)
        data = r.json()
        return float(data["data"]["amount"])
    except Exception:
        return None


def binance_book(symbol="BTCUSDT") -> None:
    try:
        r = requests.get(
            "https://api.binance.com/api/v3/depth",
            params={"symbol": symbol, "limit": 5},
            timeout=10,
        ).json()
        return {"bids": r.get("bids", []), "asks": r.get("asks", [])}
    except Exception:
        return None


def main() -> None:
    out = {
        "type": "crypto",
        "ts": dt.datetime.now(dt.UTC).isoformat(),
        "pairs": PAIRS,
        "results": [],
    }
    for p in PAIRS:
        entry = {"pair": p, "coinbase_spot": coinbase_spot(p)}
        if BINANCE and p.endswith("-USD"):
            symbol = p.replace("-", "")
            if symbol.endswith("USD"):
                symbol += "T"
            entry["binance_book"] = binance_book(symbol)
        out["results"].append(entry)
    snap = OUT_DIR / "crypto_latest.json"
    with open(snap, "w", encoding="utf-8") as f:
        try:
            json.dump(out, f)

        except OSError as e:
            logging.error(f"Failed to write JSON: {e}")

            raise
    print(json.dumps(out))


if __name__ == "__main__":
    main()
