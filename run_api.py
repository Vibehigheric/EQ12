# run_api.py
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting EQ12 Webhook Hub...")
    print("📡 Endpoints:")
    print("   • http://localhost:8787/health")
    print("   • http://localhost:8787/webhooks/openai")
    print("   • http://localhost:8787/webhooks/odds")
    print("   • http://localhost:8787/webhooks/github")
    print("   • http://localhost:8787/docs (API documentation)")

    uvicorn.run("eq12_webhooks:app", host="0.0.0.0", port=8787, workers=2)
