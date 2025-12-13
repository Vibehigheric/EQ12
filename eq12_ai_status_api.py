#!/usr/bin/env python3
"""
EQ12 AI Services Status API - Simple Flask endpoint for dashboard integration
"""

import logging
import os

import requests
from flask import Flask, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


def get_openai_status():
    """Check OpenAI API connection status"""
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            # Try reading from file
            key_file = "C:/EQ12/keys/openai_api_key.txt"
            if os.path.exists(key_file):
                with open(key_file) as f:
                    api_key = f.read().strip()

        if not api_key:
            return {"status": "disconnected", "message": "No API key configured"}

        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=5)

        if response.status_code == 200:
            models = len(response.json().get("data", []))
            return {
                "status": "connected",
                "message": f"OpenAI API active with {models} models available",
                "models": models,
            }
        return {"status": "error", "message": f"HTTP {response.status_code}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.route("/api/openai/status")
def openai_status():
    """OpenAI API status endpoint"""
    return jsonify(get_openai_status())


@app.route("/api/copilot/status")
def copilot_status():
    """Copilot status endpoint (uses OpenAI API)"""
    openai_result = get_openai_status()
    return jsonify(
        {
            "status": openai_result["status"],
            "message": f"Copilot ready via OpenAI API - {openai_result['message']}",
            "api_backend": "openai",
        }
    )


@app.route("/api/chatgpt/status")
def chatgpt_status():
    """ChatGPT status endpoint (uses OpenAI API)"""
    openai_result = get_openai_status()
    return jsonify(
        {
            "status": openai_result["status"],
            "message": f"ChatGPT ready via OpenAI API - {openai_result['message']}",
            "api_backend": "openai",
        }
    )


@app.route("/api/status/all")
def all_status():
    """Combined status for all AI services"""
    openai_result = get_openai_status()
    return jsonify(
        {
            "openai": openai_result,
            "copilot": {
                "status": openai_result["status"],
                "message": "Copilot integration via OpenAI API",
                "api_backend": "openai",
            },
            "chatgpt": {
                "status": openai_result["status"],
                "message": "ChatGPT integration via OpenAI API",
                "api_backend": "openai",
            },
            "overall_status": openai_result["status"],
        }
    )


if __name__ == "__main__":
    print("🚀 Starting EQ12 AI Services Status API...")
    print("📡 Endpoints available:")
    print("   - /api/openai/status")
    print("   - /api/copilot/status")
    print("   - /api/chatgpt/status")
    print("   - /api/status/all")

    app.run(host="0.0.0.0", port=8082, debug=True)
