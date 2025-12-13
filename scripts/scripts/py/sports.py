import json
import sys
import time

print(
    json.dumps(
        {
            "type": "sports",
            "headless": "--headless" in sys.argv,
            "markets": ["MLB", "NFL", "Soccer"],
            "note": "Pull odds, model, props here.",
        }
    )
)
time.sleep(0.2)
