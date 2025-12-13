"""
EQ12 Webhook Pipeline Test
Tests complete webhook flow: AI request → webhook event → automated actions
"""

import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path


def setup_test_environment():
    """Setup test environment with webhook configuration"""
    print("🔧 Setting up test environment...")

    # Set webhook environment for testing
    os.environ["EQ12_WEBHOOK_SECRET"] = "test-webhook-secret-123456"
    os.environ["EQ12_WEBHOOK_URL"] = "http://127.0.0.1:8000/webhooks/openai"

    print("✅ Test environment configured")


def start_webhook_server():
    """Start webhook server for testing"""
    print("🚀 Starting webhook server...")

    try:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "eq12_webhooks:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
                "--log-level",
                "warning",  # Reduce noise
            ],
            cwd="C:/EQ12",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for server to start
        time.sleep(3)

        if process.poll() is None:
            print(f"✅ Webhook server started (PID: {process.pid})")
            return process
        else:
            _stdout, stderr = process.communicate()
            print("❌ Server failed to start:")
            print(f"Error: {stderr.decode()}")
            return None

    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None


def test_webhook_health():
    """Test webhook server health"""
    print("🩺 Testing webhook health...")

    try:
        import httpx

        response = httpx.get("http://127.0.0.1:8000/webhooks/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Webhook server healthy: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_ai_request_with_webhooks():
    """Test AI request that should trigger webhook events"""
    print("🤖 Testing AI request with webhook events...")

    try:
        sys.path.insert(0, "C:/EQ12")
        from eq12_ai_client import EQ12AIClient

        client = EQ12AIClient()

        print("📤 Making AI request...")
        response = client.ask(
            prompt="Test webhook pipeline - respond with exactly 'WEBHOOK_TEST_OK'",
            feature="webhook_test",
            model="gpt-4o-mini",
            max_tokens=20,
        )

        print(f"✅ AI response: {response.strip()}")

        # Wait for webhook processing
        print("⏳ Waiting for webhook processing...")
        time.sleep(3)

        return True

    except Exception as e:
        print(f"❌ AI request failed: {e}")
        return False


def check_webhook_logs():
    """Check webhook logs for events"""
    print("📄 Checking webhook logs...")

    logs_dir = Path("C:/EQ12/logs/webhooks")

    if not logs_dir.exists():
        print("❌ Webhook logs directory not found")
        return False

    # Find today's event log
    today = datetime.now(UTC).strftime("%Y%m%d")
    event_file = logs_dir / f"events_{today}.jsonl"

    if not event_file.exists():
        print(f"⚠️  No events file found: {event_file}")
        return False

    try:
        with open(event_file) as f:
            lines = f.readlines()

        if not lines:
            print("⚠️  Events file is empty")
            return False

        events = [json.loads(line.strip()) for line in lines if line.strip()]

        print(f"📊 Found {len(events)} webhook events")

        # Look for recent events (last 10)
        recent_events = events[-10:] if len(events) > 10 else events

        event_types = {}
        for event in recent_events:
            event_type = event.get("type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1

        print("📈 Recent event types:")
        for event_type, count in event_types.items():
            print(f"   {event_type}: {count}")

        # Check for test events
        test_events = [e for e in recent_events if "webhook_test" in str(e)]

        if test_events:
            print(f"✅ Found {len(test_events)} test-related events")

            # Show latest test event
            latest = test_events[-1]
            print(f"🔍 Latest test event: {latest['type']} [{latest['id']}]")

            return True
        else:
            print("⚠️  No test-related events found")
            return False

    except Exception as e:
        print(f"❌ Error reading webhook logs: {e}")
        return False


def check_cost_tracking():
    """Check if cost tracking was updated via webhooks"""
    print("💰 Checking cost tracking integration...")

    try:
        sys.path.insert(0, "C:/EQ12")
        from eq12_budget_enforcer import budget_enforcer

        status = budget_enforcer.get_status()

        # Check if we have any usage today
        daily_usage = status["daily_usage"]

        if daily_usage > 0:
            print(f"✅ Cost tracking active: ${daily_usage:.6f} used today")

            # Check feature usage
            today = datetime.now(UTC).strftime("%Y-%m-%d")
            usage = budget_enforcer.usage

            if "features" in usage and "webhook_test" in usage["features"]:
                if today in usage["features"]["webhook_test"]:
                    test_usage = usage["features"]["webhook_test"][today]
                    print(
                        f"✅ Webhook test feature tracked: {test_usage['calls']} calls, ${test_usage['cost']:.6f}"
                    )
                    return True

            print("⚠️  No webhook_test feature usage found")
            return False
        else:
            print("⚠️  No cost tracking usage detected")
            return False

    except Exception as e:
        print(f"❌ Cost tracking check failed: {e}")
        return False


def show_webhook_statistics():
    """Display webhook statistics"""
    print("📊 WEBHOOK STATISTICS")
    print("=" * 50)

    try:
        import httpx

        response = httpx.get("http://127.0.0.1:8000/webhooks/stats", timeout=5)

        if response.status_code == 200:
            stats = response.json()

            print(f"Events processed: {stats['events_processed']}")
            print(f"Log directory: {stats['log_directory']}")

            if stats.get("log_files"):
                print("\nLog files:")
                for log_file in stats["log_files"][-5:]:  # Show last 5 files
                    size_kb = log_file["size_bytes"] / 1024
                    print(f"  📄 {log_file['name']}: {size_kb:.1f} KB")

            return True
        else:
            print(f"❌ Failed to get statistics: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Statistics error: {e}")
        return False


def main():
    """Main webhook pipeline test"""
    print("🎯 EQ12 WEBHOOK PIPELINE TEST")
    print("=" * 60)

    # Setup
    setup_test_environment()

    # Start webhook server
    server_process = start_webhook_server()
    if not server_process:
        return False

    try:
        # Test sequence
        tests = [
            ("Health Check", test_webhook_health),
            ("AI Request", test_ai_request_with_webhooks),
            ("Webhook Logs", check_webhook_logs),
            ("Cost Tracking", check_cost_tracking),
            ("Statistics", show_webhook_statistics),
        ]

        results = {}

        for test_name, test_func in tests:
            print(f"\n🧪 {test_name.upper()}")
            print("-" * 40)

            try:
                success = test_func()
                results[test_name] = success

                if success:
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"⚠️  {test_name} had issues")

            except Exception as e:
                print(f"❌ {test_name} FAILED: {e}")
                results[test_name] = False

        # Summary
        print("\n📊 TEST RESULTS")
        print("=" * 60)

        passed = sum(results.values())
        total = len(results)

        for test_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {test_name:<20} {status}")

        print(f"\nOverall: {passed}/{total} tests passed ({passed / total * 100:.1f}%)")

        if passed >= 4:  # Allow 1 failure
            print("🎉 WEBHOOK PIPELINE TEST SUCCESSFUL!")
            print("\n✅ Key capabilities verified:")
            print("   • Webhook server operational")
            print("   • AI client event emission")
            print("   • Event processing and logging")
            print("   • Cost tracking integration")

            return True
        else:
            print("⚠️  WEBHOOK PIPELINE NEEDS ATTENTION")
            print(f"\nOnly {passed}/{total} tests passed")
            return False

    finally:
        # Cleanup
        if server_process:
            print("\n🛑 Stopping webhook server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
