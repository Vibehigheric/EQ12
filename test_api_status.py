#!/usr/bin/env python3
"""
Quick API status test for EQ12 dashboard
"""

import json
import os
import sys

import requests


def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            # Try reading from file
            key_file = "C:/EQ12/keys/openai_api_key.txt"
            if os.path.exists(key_file):
                with open(key_file) as f:
                    api_key = f.read().strip()

        if not api_key:
            return {"status": "error", "message": "No API key found"}

        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)

        if response.status_code == 200:
            return {
                "status": "connected",
                "message": "OpenAI API connected",
                "models": len(response.json().get("data", [])),
            }
        return {"status": "error", "message": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    """Main test function"""
    print("🔍 Testing API Connections...")

    # Test OpenAI
    openai_result = test_openai_connection()
    print(f"📡 OpenAI API: {openai_result}")

    # Create status for dashboard
    status = {
        "openai": openai_result,
        "chatgpt": openai_result,  # Same API key
        "copilot": {
            "status": "not_configured",
            "message": "Copilot uses same OpenAI API",
        },
        "timestamp": str(sys.version_info),
    }

    # Save status
    os.makedirs("C:/EQ12/logs", exist_ok=True)
    with open("C:/EQ12/logs/api_status.json", "w") as f:
        json.dump(status, f, indent=2)

    print("✅ Status saved to logs/api_status.json")
    return status


if __name__ == "__main__":
    main()
