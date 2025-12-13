#!/usr/bin/env python3
"""
EQ12 GODSTACK - Secrets Validator
Runs at startup in Codespaces or locally.
Checks for required environment variables and warns if any are missing.
"""

import os
import sys

REQUIRED_SECRETS = [
    "TG_TOKEN",  # Telegram bot token
    "TG_CHAT_ID",  # Telegram chat/channel ID
    "OPENAI_SERVICE_KEY",  # Service key for enrichment
    "BING_KEY",  # Bing API key
    "GOOGLE_KEY",  # Google API key
    "GOOGLE_CSE_ID",  # Google Custom Search ID
    "CODECOV_TOKEN",  # Codecov reporting token
    "SONAR_TOKEN",  # SonarCloud API token
]


def main():
    missing = []
    for secret in REQUIRED_SECRETS:
        if not os.getenv(secret):
            missing.append(secret)

    if not missing:
        print("✅ All required secrets are present.")
        sys.exit(0)
    else:
        print("🚨 Missing required secrets:")
        for s in missing:
            print(f"  - {s}")
        print("\nℹ️ Add them under: Repo → Settings → Codespaces → Secrets")
        sys.exit(1)


if __name__ == "__main__":
    main()
