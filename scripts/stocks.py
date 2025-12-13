import datetime as dt
import json
import os
from pathlib import Path

import yfinance as yf

#!/usr/bin/env python3

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
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["RSI14"] = rsi(df["Close"], 14)
        df["MOM5"] = df["Close"].pct_change(5)
        last = df.iloc[-1]
        signal = "NEUTRAL"
        if last["EMA20"] > last["EMA50"] and last["RSI14"] < 70:
            signal = "BULLISH"
        if last["EMA20"] < last["EMA50"] and last["RSI14"] > 30:
            signal = "BEARISH"
        csv_path = OUT_DIR / f"stocks_{ticker}.csv"
        df.to_csv(csv_path)
        return {
            "ticker": ticker,
            "ok": True,
            "close": float(last["Close"]),
            "ema20": float(last["EMA20"]),
            "ema50": float(last["EMA50"]),
            "rsi14": float(last["RSI14"]),
            "mom5": float(last["MOM5"]),
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
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
