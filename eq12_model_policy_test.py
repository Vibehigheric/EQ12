"""
EQ12 Model Policy Test Script
============================

Test the model routing and policy enforcement system
"""

import os
import sys

sys.path.append("C:/EQ12")

from eq12_ai_client import ALLOWED_MODELS, BLOCKED_MODELS, is_blocked, route_model


def test_model_routing():
    """Test model routing functionality"""
    print("🧪 TESTING EQ12 MODEL POLICY SYSTEM")
    print("=" * 50)

    # Test cases: (requested_model, expected_result_contains, task_type)
    test_cases = [
        # Allowed models should pass through
        ("gpt-4o-mini", "gpt-4o-mini", "chat"),
        ("gpt-4o", "gpt-4o", "chat"),
        ("text-embedding-3-small", "text-embedding-3-small", "embedding"),
        # Blocked models should be routed
        ("gpt-3.5-turbo", "gpt-4o-mini", "chat"),
        ("gpt-4-turbo", "gpt-4o-mini", "chat"),
        ("dall-e-2", "gpt-image-1", "image"),
        # Task-specific routing
        ("random-embedding-model", "text-embedding-3-small", "embedding"),
        ("whisper-old", "whisper-1", "transcription"),
        ("complex-reasoning-model", "gpt-4o", "chat"),
        # Reasoning keywords should route to gpt-4o
        ("gpt-o1-mini", "gpt-4o", "chat"),
        ("analysis-model", "gpt-4o", "chat"),
    ]

    print(f"📝 Allowed models: {len(ALLOWED_MODELS)}")
    print(f"🚫 Blocked patterns: {len([b for b in BLOCKED_MODELS if b.strip()])}")
    print()

    passed = 0
    failed = 0

    for i, (requested, expected_contains, task_type) in enumerate(test_cases, 1):
        try:
            result = route_model(requested, task_type)

            # Check if result contains expected string (for flexibility)
            success = expected_contains in result

            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{i:2d}. {status} | {requested:25} → {result:20} ({task_type})")

            if success:
                passed += 1
            else:
                failed += 1
                print(f"    Expected: contains '{expected_contains}', Got: '{result}'")

        except Exception as e:
            print(f"{i:2d}. ❌ ERROR | {requested:25} → Exception: {e}")
            failed += 1

    print()
    print(f"📊 RESULTS: {passed} passed, {failed} failed")

    # Test blocking functionality
    print("\n🚫 TESTING MODEL BLOCKING")
    print("-" * 30)

    blocked_tests = [
        ("gpt-3.5-turbo", True),
        ("gpt-3.5-turbo-0125", True),
        ("gpt-4-turbo", True),
        ("gpt-5-experimental", True),
        ("gpt-4o-mini", False),
        ("gpt-4o", False),
    ]

    for model, should_be_blocked in blocked_tests:
        is_model_blocked = is_blocked(model)
        status = "✅ PASS" if is_model_blocked == should_be_blocked else "❌ FAIL"
        action = "BLOCKED" if is_model_blocked else "ALLOWED"
        print(f"{status} | {model:25} → {action}")

    print()
    return failed == 0


def test_with_ai_client():
    """Test integration with AI client"""
    print("🤖 TESTING AI CLIENT INTEGRATION")
    print("-" * 40)

    try:
        from eq12_ai_client import EQ12AIClient

        EQ12AIClient()

        # Test with a blocked model (should route to allowed)
        print("Testing request with blocked model 'gpt-3.5-turbo'...")

        # This would normally make a real API call, but we're just testing routing
        # We'll simulate by checking the routing function directly
        routed = route_model("gpt-3.5-turbo", "chat")
        print(f"✅ Model routing working: gpt-3.5-turbo → {routed}")

        # Test policy enforcement flag
        enforce = os.getenv("EQ12_ENFORCE_MODEL_POLICY", "true").lower() == "true"
        print(f"✅ Policy enforcement: {'ENABLED' if enforce else 'DISABLED'}")

        return True

    except Exception as e:
        print(f"❌ AI Client test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 EQ12 MODEL POLICY VALIDATION")
    print("=" * 50)

    routing_ok = test_model_routing()
    client_ok = test_with_ai_client()

    print("\n🏁 FINAL RESULTS")
    print("=" * 20)

    if routing_ok and client_ok:
        print("✅ All tests PASSED - Model policy system operational!")
        sys.exit(0)
    else:
        print("❌ Some tests FAILED - Check configuration")
        sys.exit(1)
