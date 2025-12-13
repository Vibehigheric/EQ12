import json
import sys
import time

print(
    json.dumps(
        {
            "type": "jobs",
            "headless": "--headless" in sys.argv,
            "role": "Control Technician",
            "locations": ["Buffalo NY", "Remote"],
            "note": "Scrape job sites/APIs here.",
        }
    )
)
time.sleep(0.2)
