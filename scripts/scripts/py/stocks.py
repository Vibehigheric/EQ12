import json
import sys
import time

print(
    json.dumps(
        {
            "type": "stocks",
            "headless": "--headless" in sys.argv,
            "tickers": ["AAPL", "NVDA", "MSFT"],
            "note": "Implement yfinance/API here.",
        }
    )
)
time.sleep(0.2)
