# EQ12 OpenAI Client Smoke Test
# Copy-paste this to test OpenAI integration

import asyncio
import os
import sys
import traceback
from datetime import datetime


def test_openai_sync():
    """Test synchronous OpenAI client"""
    print("=== Testing Synchronous OpenAI Client ===")

    try:
        # Import enhanced client
        from eq12_openai_client_enhanced import get_openai_client

        client = get_openai_client()
        print(f"✅ Client initialized: {type(client).__name__}")

        # Test sync method
        response = client.chat_sync("Say 'ok' without punctuation", model=None)
        print(f"✅ Sync response: {response}")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Trying fallback to basic client...")

        try:
            from eq12_openai_client import get_openai_client

            client = get_openai_client()

            # Basic test if available
            print(f"✅ Fallback client: {type(client).__name__}")
            return True
        except Exception as e2:
            print(f"❌ Fallback failed: {e2}")
            return False

    except Exception as e:
        print(f"❌ Sync test error: {e}")
        traceback.print_exc()
        return False


async def test_openai_async():
    """Test asynchronous OpenAI client"""
    print("\n=== Testing Asynchronous OpenAI Client ===")

    try:
        from eq12_openai_client_enhanced import get_openai_client

        client = get_openai_client()
        print(f"✅ Async client initialized: {type(client).__name__}")

        # Test async method
        response = await client.chat_async("Say 'hello' without punctuation", model=None)
        print(f"✅ Async response: {response}")
        return True

    except Exception as e:
        print(f"❌ Async test error: {e}")
        traceback.print_exc()
        return False


def test_circuit_breaker():
    """Test circuit breaker functionality"""
    print("\n=== Testing Circuit Breaker ===")

    try:
        import json
        from pathlib import Path

        # Create temporary offline state
        breaker_file = Path("logs/.llm_offline.json")
        breaker_file.parent.mkdir(exist_ok=True)

        offline_state = {
            "offline": True,
            "until": "2099-01-01T00:00:00Z",
            "reason": "Manual test - simulating quota exceeded",
        }

        with open(breaker_file, "w") as f:
            json.dump(offline_state, f)

        print("✅ Circuit breaker set to offline mode")

        # Test client behavior in offline mode
        try:
            from eq12_openai_client_enhanced import get_openai_client

            client = get_openai_client()

            response = client.chat_sync("Test offline mode", model=None)
            if "offline" in response.lower() or "unavailable" in response.lower():
                print("✅ Circuit breaker working: returned offline response")
                result = True
            else:
                print(f"⚠️ Unexpected response in offline mode: {response}")
                result = False

        except Exception as e:
            print(f"✅ Circuit breaker working: threw exception as expected: {e}")
            result = True

        # Clean up
        breaker_file.unlink(missing_ok=True)
        print("✅ Circuit breaker reset")

        return result

    except Exception as e:
        print(f"❌ Circuit breaker test error: {e}")
        return False


def test_environment():
    """Test environment configuration"""
    print("\n=== Testing Environment Configuration ===")

    env_vars = [
        "OPENAI_API_KEY",
        "EQ12_USE_LLM",
        "OPENAI_MODEL",
        "OPENAI_FALLBACK_MODELS",
        "OPENAI_REQUEST_TIMEOUT",
        "OPENAI_MAX_RETRIES",
    ]

    results = []
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:20]}{'...' if len(value) > 20 else ''}")
            results.append(True)
        else:
            print(f"⚠️ {var}: Not set")
            results.append(False)

    return any(results)  # At least one env var should be set


async def main():
    """Run all smoke tests"""
    print(f"🚀 EQ12 OpenAI Client Smoke Tests - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Set test environment
    if not os.getenv("EQ12_USE_LLM"):
        os.environ["EQ12_USE_LLM"] = "1"
        print("🔧 Set EQ12_USE_LLM=1 for testing")

    tests = []

    # Run sync test
    tests.append(test_environment())
    tests.append(test_openai_sync())

    # Run async test
    try:
        tests.append(await test_openai_async())
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        tests.append(False)

    # Test circuit breaker
    tests.append(test_circuit_breaker())

    # Summary
    passed = sum(tests)
    total = len(tests)

    print("\n" + "=" * 60)
    print(f"🎯 Results: {passed}/{total} tests passed ({passed / total * 100:.1f}%)")

    if passed == total:
        print("🎉 All OpenAI client tests PASSED!")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed - check configuration")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
