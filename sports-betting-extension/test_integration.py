#!/usr/bin/env python3
"""
Extension Integration Test Suite
"""

import asyncio
import json
import subprocess
import sys
import time
from datetime import datetime

import websockets


async def test_websocket_connection():
    """Test basic WebSocket connection"""
    print("🔌 Testing WebSocket connection...")

    try:
        async with websockets.connect("ws://localhost:8765", timeout=5) as ws:
            # Send test message
            await ws.send(
                json.dumps(
                    {
                        "type": "extension_connected",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            )

            # Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(response)

            if data.get("type") == "status":
                print("✅ WebSocket connection successful")
                return True
            print(f"⚠️  Unexpected response: {data}")
            return False

    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False


async def test_parlay_request():
    """Test parlay generation request"""
    print("🎯 Testing parlay request...")

    try:
        async with websockets.connect("ws://localhost:8765", timeout=10) as ws:
            # Send parlay request
            request = {
                "type": "request_parlay",
                "sport": "nfl",
                "promo": "mystery",
                "stake": 100,
                "max_legs": 4,
            }

            await ws.send(json.dumps(request))

            # Wait for parlay response
            response = await asyncio.wait_for(ws.recv(), timeout=15)
            data = json.loads(response)

            if data.get("type") == "new_parlay":
                parlay = data.get("parlay", {})
                legs = parlay.get("legs", [])

                print(f"✅ Parlay generated: {len(legs)} legs")
                print(f"   Sport: {parlay.get('sport')}")
                print(f"   EV: {parlay.get('ev')}")
                print(f"   Stake: ${parlay.get('stake')}")

                for i, leg in enumerate(legs, 1):
                    print(f"   Leg {i}: {leg.get('label')} ({leg.get('odds')})")

                return True
            print(f"⚠️  No parlay received: {data}")
            return False

    except Exception as e:
        print(f"❌ Parlay request failed: {e}")
        return False


def test_extension_files():
    """Test that extension files exist and are valid"""
    print("📁 Testing extension files...")

    from pathlib import Path

    required_files = [
        "manifest.json",
        "background.js",
        "popup/popup.html",
        "popup/popup.js",
        "content-draftkings.js",
        "polyfill/browser-polyfill.min.js",
    ]

    missing_files = []

    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    print("✅ All extension files present")

    # Test manifest.json validity
    try:
        with open("manifest.json") as f:
            manifest = json.load(f)

        if manifest.get("manifest_version") == 3:
            print("✅ Manifest V3 valid")
        else:
            print("⚠️  Manifest version issue")

    except Exception as e:
        print(f"❌ Manifest validation failed: {e}")
        return False

    return True


def check_optimizer_integration():
    """Check if optimizer repo is properly integrated"""
    print("🔗 Checking optimizer integration...")

    from pathlib import Path

    # Check for optimizer repo
    optimizer_paths = [
        Path("../sports-betting-optimizer"),
        Path("../../sports-betting-optimizer"),
        Path("sports-betting-optimizer"),
    ]

    optimizer_found = False

    for path in optimizer_paths:
        if path.exists() and (path / "src" / "promos" / "master_optimizer.py").exists():
            print(f"✅ Optimizer found: {path}")

            # Check if patched
            master_file = path / "src" / "promos" / "master_optimizer.py"

            with open(master_file) as f:
                content = f.read()

            if "EXTENSION_INTEGRATION_PATCH" in content:
                print("✅ Optimizer patched for extension")
            else:
                print("⚠️  Optimizer not patched - run launch.py to auto-patch")

            optimizer_found = True
            break

    if not optimizer_found:
        print("⚠️  Optimizer repo not found - extension will use mock data")

    return True


async def run_full_test():
    """Run complete test suite"""
    print("🧪 EXTENSION INTEGRATION TEST SUITE")
    print("=" * 50)

    tests = [
        ("Extension Files", test_extension_files),
        ("Optimizer Integration", check_optimizer_integration),
        ("WebSocket Connection", test_websocket_connection),
        ("Parlay Generation", test_parlay_request),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")

        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            results[test_name] = result

        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)

    passed = 0
    total = len(tests)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1

    print(f"\nSummary: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Extension ready to use.")
        print("\n📋 Next steps:")
        print("1. Load extension in Chrome/Firefox developer mode")
        print("2. Start bridge server: python launch.py")
        print("3. Navigate to DraftKings and test parlay application")
    else:
        print("⚠️  Some tests failed. Check issues above.")

    return passed == total


if __name__ == "__main__":
    # Check if bridge server is running
    print("🚀 Starting test suite...")

    # Try to start bridge server if not running
    try:
        subprocess.Popen(
            [sys.executable, "simple_bridge.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print("⏳ Starting bridge server...")
        time.sleep(3)  # Give server time to start

    except Exception:
        print("⚠️  Could not auto-start bridge server")

    # Run tests
    asyncio.run(run_full_test())
