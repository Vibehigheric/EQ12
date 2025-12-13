#!/usr/bin/env python3
"""
EQ12 API Connection Test
=======================

Minimal test script to verify OpenAI API connectivity after applying fixes.
Tests for the common 429 (insufficient_quota) and 401 (invalid_api_key) errors.

Run this after setting up your API keys to verify everything works.

Author: EQ12 Development Team
License: MIT
"""

# UTF-8 console fix for Windows
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# Core imports
try:
    from dotenv import load_dotenv

    load_dotenv()  # Load OPENAI_API_KEY, ODDS_API_KEY, etc.
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")

try:
    from openai import OpenAI
except ImportError:
    print("❌ OpenAI SDK not installed. Install with: pip install openai>=2.1.0")
    sys.exit(1)


def test_openai_simple() -> bool:
    """Test basic OpenAI connection with minimal request."""
    print("🧪 Testing OpenAI API connection...")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("   Set it with: export OPENAI_API_KEY=sk-your-key-here")
        return False

    if "test-key" in api_key.lower() or "replace" in api_key.lower():
        print("❌ API key contains placeholder text")
        print("   Replace with real OpenAI API key starting with 'sk-'")
        return False

    try:
        client = OpenAI(api_key=api_key)

        # Minimal test request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Reply with the string OK"}],
            max_tokens=5,
            temperature=0,
        )

        result = response.choices[0].message.content.strip()
        print(f"✅ OpenAI API Success! Response: '{result}'")

        # Check usage info
        if response.usage:
            print(f"   Tokens used: {response.usage.total_tokens}")

        return True

    except Exception as e:
        error_msg = str(e)
        print(f"❌ OpenAI API Error: {error_msg}")

        # Specific error guidance
        if "insufficient_quota" in error_msg or "429" in error_msg:
            print("🚫 BILLING ISSUE:")
            print("   1. Go to: https://platform.openai.com/settings/organization/billing")
            print("   2. Add payment method and credits")
            print("   3. Go to: https://platform.openai.com/settings/organization/limits")
            print("   4. Set usage limits above $0")
        elif "invalid_api_key" in error_msg or "401" in error_msg:
            print("🔑 API KEY ISSUE:")
            print("   1. Get new key: https://platform.openai.com/api-keys")
            print("   2. Ensure it starts with 'sk-'")
            print("   3. Set OPENAI_API_KEY environment variable")
        elif "rate_limit_exceeded" in error_msg:
            print("⏱️ RATE LIMIT: Wait a moment and try again")
        else:
            print("❓ Check your internet connection and API key")

        return False


def test_odds_api_simple() -> bool:
    """Test The Odds API connection."""
    print("\n🧪 Testing The Odds API connection...")

    api_key = os.environ.get("ODDS_API_KEY")
    if not api_key:
        print("⚠️ ODDS_API_KEY not found (optional for OpenAI testing)")
        return True

    try:
        import requests

        response = requests.get(
            "https://api.the-odds-api.com/v4/sports", params={"apiKey": api_key}, timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Odds API Success! Found {len(data)} sports")
            return True
        else:
            print(f"❌ Odds API Error: {response.status_code}")
            return False

    except ImportError:
        print("⚠️ requests not installed. Install with: pip install requests")
        return True
    except Exception as e:
        print(f"❌ Odds API Error: {e}")
        return False


def main():
    """Run all API tests."""
    print("🚀 EQ12 API Connection Test")
    print("=" * 40)

    # Test OpenAI (required)
    openai_ok = test_openai_simple()

    # Test Odds API (optional)
    odds_ok = test_odds_api_simple()

    print("\n" + "=" * 40)
    print("📋 Test Results:")
    print(f"   OpenAI API: {'✅ WORKING' if openai_ok else '❌ FAILED'}")
    print(f"   Odds API:   {'✅ WORKING' if odds_ok else '⚠️ NOT CONFIGURED'}")

    if openai_ok:
        print("\n🎉 Core API tests passed!")
        print("Your EQ12 platform should work correctly now.")
        print("\n📝 Next steps:")
        print("   1. Run: python eq12_enhanced_openai_sdk.py")
        print("   2. Try: python eq12_nfl_parlay_optimizer.py --help")
    else:
        print("\n💡 Fix the OpenAI API issues above, then run this test again.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
