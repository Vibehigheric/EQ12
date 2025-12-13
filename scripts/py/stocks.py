#!/usr/bin/env python3
"""
stocks.py — EQ12 stock fetcher with EMA/RSI/Momentum + CSV snapshot
"""

import datetime as dt
import json
import os
import sys
from pathlib import Path

import yfinance as yf

# Tickers list (env override possible)
TICKERS = os.getenv("TICKERS", "AAPL,NVDA,MSFT,SPY").split(",")
OUT_DIR = Path(os.getenv("OUT_DIR", "C:/EQ12/logs")).expanduser()
OUT_DIR.mkdir(parents=True, exist_ok=True)


def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1 / period, adjust=False).mean().replace(0, 1e-9)
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def analyze(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False, auto_adjust=False)
        if df.empty:
            return {"ticker": ticker, "ok": False, "error": "no data"}

        # Technicals
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["RSI14"] = rsi(df["Close"], 14)
        df["MOM5"] = df["Close"].pct_change(5)

        # Use only last row for signals
        last = df.iloc[-1]
        ema20 = (
            last["EMA20"].iloc[0]
            if hasattr(last["EMA20"], "iloc")
            else (last["EMA20"].item() if hasattr(last["EMA20"], "item") else last["EMA20"])
        )
        ema50 = (
            last["EMA50"].iloc[0]
            if hasattr(last["EMA50"], "iloc")
            else (last["EMA50"].item() if hasattr(last["EMA50"], "item") else last["EMA50"])
        )
        rsi14 = (
            last["RSI14"].iloc[0]
            if hasattr(last["RSI14"], "iloc")
            else (last["RSI14"].item() if hasattr(last["RSI14"], "item") else last["RSI14"])
        )
        signal = "NEUTRAL"
        if ema20 > ema50 and rsi14 < 70:
            signal = "BULLISH"
        elif ema20 < ema50 and rsi14 > 30:
            signal = "BEARISH"

        # Save snapshot CSV
        csv_path = OUT_DIR / f"stocks_{ticker}.csv"
        df.to_csv(csv_path)

        return {
            "ticker": ticker,
            "ok": True,
            "close": (
                last["Close"].iloc[0]
                if hasattr(last["Close"], "iloc")
                else (last["Close"].item() if hasattr(last["Close"], "item") else last["Close"])
            ),
            "ema20": ema20,
            "ema50": ema50,
            "rsi14": rsi14,
            "mom5": (
                last["MOM5"].iloc[0]
                if hasattr(last["MOM5"], "iloc")
                else (last["MOM5"].item() if hasattr(last["MOM5"], "item") else last["MOM5"])
            ),
            "signal": signal,
            "csv": str(csv_path),
        }
    except Exception as e:
        return {"ticker": ticker, "ok": False, "error": str(e)}


def main() -> None:
    results = [analyze(t.strip().upper()) for t in TICKERS if t.strip()]
    summary = {
        "type": "stocks",
        "ts": dt.datetime.now(dt.UTC).isoformat(),
        "tickers": TICKERS,
        "results": results,
    }
    # Write JSON snapshot for dashboard (OUT_DIR)
    summary_path = OUT_DIR / "stocks_latest.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        try:
            json.dump(summary, f)

        except OSError as e:
            logging.error(f"Failed to write JSON: {e}")

            raise
    # Also write to C:\EQ12\logs\stocks_latest.json for dashboard
    try:
        with open(r"C:\EQ12\logs\stocks_latest.json", "w", encoding="utf-8") as f:
            try:
                json.dump(summary, f)

            except OSError as e:
                logging.error(f"Failed to write JSON: {e}")

                raise
    except Exception as e:
        print(
            f"Warning: Could not write to C:EQ12\\logs\\\\stocks_latest.json: {e}",
            file=sys.stderr,
        )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
