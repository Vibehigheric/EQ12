import json
import sys
import time

print(
    json.dumps(
        {
            "type": "crypto",
            "headless": "--headless" in sys.argv,
            "pairs": ["BTC-USD", "ETH-USD"],
            "note": "Implement exchange API here.",
        }
    )
)
time.sleep(0.2)
