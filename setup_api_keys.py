"""
EQ12 API Key Setup Script
========================

This script helps you set up your API keys correctly to fix the common
429 (insufficient_quota) and 401 (invalid_api_key) errors.

Run this script to:
1. Create a .env file from the template
2. Set environment variables persistently
3. Test your API connections
4. Verify billing status

Author: EQ12 Development Team
License: MIT
"""

import os
import subprocess
import sys
from pathlib import Path

# Import UTF-8 fix first
from eq12_console_fix import safe_print


def check_prerequisites():
    """Check if all required dependencies are installed."""
    missing_deps = []

    try:
        import openai

        if openai.__version__ < "2.1.0":
            safe_print("⚠️ OpenAI SDK version is outdated. Please upgrade:")
            safe_print("   pip install --upgrade openai>=2.1.0")
    except ImportError:
        missing_deps.append("openai>=2.1.0")

    try:
        import dotenv
    except ImportError:
        missing_deps.append("python-dotenv")

    try:
        import requests
    except ImportError:
        missing_deps.append("requests")

    if missing_deps:
        safe_print("❌ Missing required dependencies:")
        for dep in missing_deps:
            safe_print(f"   - {dep}")
        safe_print("\nInstall them with:")
        safe_print(f"   pip install {' '.join(missing_deps)}")
        return False

    return True


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    template_file = Path(".env.template")

    if env_file.exists():
        safe_print("✅ .env file already exists")
        return True

    if not template_file.exists():
        safe_print("❌ .env.template not found. Creating a basic one...")
        basic_template = """# EQ12 API Configuration
OPENAI_API_KEY=sk-REPLACE_WITH_YOUR_REAL_OPENAI_API_KEY
ODDS_API_KEY=REPLACE_WITH_YOUR_ODDS_API_KEY
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
"""
        template_file.write_text(basic_template, encoding="utf-8")

    # Copy template to .env
    content = template_file.read_text(encoding="utf-8")
    env_file.write_text(content, encoding="utf-8")
    safe_print("✅ Created .env file from template")
    safe_print("📝 Please edit .env file and add your real API keys")
    return True


def get_api_key(key_name: str, current_value: str = "") -> str | None:
    """Interactively get an API key from user."""
    if current_value and not any(
        placeholder in current_value.lower()
        for placeholder in ["replace", "test", "example", "your_"]
    ):
        safe_print(f"✅ {key_name} is already configured")
        return current_value

    safe_print(f"\n🔑 {key_name} Setup:")

    if key_name == "OpenAI API Key":
        safe_print("   1. Go to: https://platform.openai.com/api-keys")
        safe_print("   2. Click 'Create new secret key'")
        safe_print("   3. Copy the key (starts with 'sk-')")
        safe_print(
            "   ⚠️  CRITICAL: Set up billing at https://platform.openai.com/settings/organization/billing"
        )
        safe_print(
            "   ⚠️  CRITICAL: Set usage limits at https://platform.openai.com/settings/organization/limits"
        )
    elif key_name == "The Odds API Key":
        safe_print("   1. Go to: https://the-odds-api.com/")
        safe_print("   2. Sign up for a free account")
        safe_print("   3. Copy your API key from the dashboard")

    while True:
        key = input(f"\nEnter your {key_name} (or 'skip' to skip): ").strip()

        if key.lower() == "skip":
            return None

        if not key:
            continue

        # Validate format
        if key_name == "OpenAI API Key":
            if not key.startswith("sk-"):
                safe_print("❌ OpenAI API keys should start with 'sk-'")
                continue
            if len(key) < 20:
                safe_print("❌ OpenAI API key seems too short")
                continue

        return key


def set_environment_variables(
    openai_key: str | None = None,
    odds_key: str | None = None,
    telegram_token: str | None = None,
    telegram_chat: str | None = None,
):
    """Set environment variables persistently on Windows."""
    safe_print("\n🔧 Setting environment variables...")

    if openai_key:
        try:
            # Set for current session
            os.environ["OPENAI_API_KEY"] = openai_key

            # Set persistently (Windows only)
            if os.name == "nt":
                subprocess.run(
                    ["setx", "OPENAI_API_KEY", openai_key, "/M"], check=True, capture_output=True
                )

            safe_print("✅ OPENAI_API_KEY set")
        except Exception as e:
            safe_print(f"⚠️ Could not set OPENAI_API_KEY persistently: {e}")
            safe_print("   You may need to run as administrator")

    if odds_key:
        try:
            os.environ["ODDS_API_KEY"] = odds_key

            if os.name == "nt":
                subprocess.run(
                    ["setx", "ODDS_API_KEY", odds_key, "/M"], check=True, capture_output=True
                )

            safe_print("✅ ODDS_API_KEY set")
        except Exception as e:
            safe_print(f"⚠️ Could not set ODDS_API_KEY persistently: {e}")

    if telegram_token:
        try:
            os.environ["TELEGRAM_BOT_TOKEN"] = telegram_token

            if os.name == "nt":
                subprocess.run(
                    ["setx", "TELEGRAM_BOT_TOKEN", telegram_token, "/M"],
                    check=True,
                    capture_output=True,
                )

            safe_print("✅ TELEGRAM_BOT_TOKEN set")
        except Exception as e:
            safe_print(f"⚠️ Could not set TELEGRAM_BOT_TOKEN persistently: {e}")


def test_openai_connection(api_key: str) -> bool:
    """Test OpenAI API connection and billing status."""
    safe_print("\n🧪 Testing OpenAI connection...")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        # Try a minimal request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Reply with just 'OK'"}],
            max_tokens=5,
            temperature=0,
        )

        if response.choices and response.choices[0].message.content:
            safe_print("✅ OpenAI API connection successful!")
            safe_print(f"   Response: {response.choices[0].message.content}")
            return True
        else:
            safe_print("⚠️ OpenAI API connected but no response content")
            return False

    except Exception as e:
        error_msg = str(e)

        if "insufficient_quota" in error_msg or "429" in error_msg:
            safe_print("❌ OpenAI billing/quota issue:")
            safe_print("   Your account needs billing configured and usage limits set")
            safe_print("   1. Go to: https://platform.openai.com/settings/organization/billing")
            safe_print("   2. Add a payment method")
            safe_print("   3. Go to: https://platform.openai.com/settings/organization/limits")
            safe_print("   4. Set usage limits above $0")
        elif "invalid_api_key" in error_msg or "401" in error_msg:
            safe_print("❌ Invalid OpenAI API key:")
            safe_print("   Check that your key starts with 'sk-' and is correct")
            safe_print("   Get a new key at: https://platform.openai.com/api-keys")
        else:
            safe_print(f"❌ OpenAI API test failed: {error_msg}")

        return False


def test_odds_api_connection(api_key: str) -> bool:
    """Test The Odds API connection."""
    safe_print("\n🧪 Testing The Odds API connection...")

    try:
        import requests

        # Test with a simple sports list request
        response = requests.get(
            "https://api.the-odds-api.com/v4/sports", params={"apiKey": api_key}, timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                safe_print("✅ The Odds API connection successful!")
                safe_print(f"   Found {len(data)} available sports")
                return True
            else:
                safe_print("⚠️ The Odds API connected but returned unexpected data")
                return False
        else:
            safe_print(f"❌ The Odds API request failed: {response.status_code}")
            safe_print(f"   Response: {response.text}")
            return False

    except Exception as e:
        safe_print(f"❌ The Odds API test failed: {e}")
        return False


def main():
    """Main setup workflow."""
    safe_print("🚀 EQ12 API Key Setup - Fixing 429/401 Errors")
    safe_print("=" * 50)

    # Check prerequisites
    if not check_prerequisites():
        return 1

    # Create .env file
    if not create_env_file():
        return 1

    # Load existing .env if it exists
    env_file = Path(".env")
    if env_file.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass

    # Get current values
    current_openai = os.getenv("OPENAI_API_KEY", "")
    current_odds = os.getenv("ODDS_API_KEY", "")
    os.getenv("TELEGRAM_BOT_TOKEN", "")
    os.getenv("TELEGRAM_CHAT_ID", "")

    # Interactive setup
    safe_print("\n🔧 API Key Configuration:")

    openai_key = get_api_key("OpenAI API Key", current_openai)
    odds_key = get_api_key("The Odds API Key", current_odds)

    # Optional Telegram setup
    safe_print("\n📱 Telegram Integration (Optional):")
    setup_telegram = input("Set up Telegram notifications? (y/n): ").lower().startswith("y")

    telegram_token = None
    telegram_chat = None

    if setup_telegram:
        safe_print("   1. Message @BotFather on Telegram")
        safe_print("   2. Create a new bot with /newbot")
        safe_print("   3. Get your bot token")
        safe_print("   4. Get your chat ID by messaging your bot then visiting:")
        safe_print("      https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")

        telegram_token = input("\nEnter Telegram Bot Token (or skip): ").strip()
        if telegram_token and telegram_token.lower() != "skip":
            telegram_chat = input("Enter Telegram Chat ID (or skip): ").strip()
            if telegram_chat.lower() == "skip":
                telegram_chat = None

    # Set environment variables
    if any([openai_key, odds_key, telegram_token]):
        set_environment_variables(openai_key, odds_key, telegram_token, telegram_chat)

    # Test connections
    test_results = []

    if openai_key:
        test_results.append(("OpenAI", test_openai_connection(openai_key)))

    if odds_key:
        test_results.append(("Odds API", test_odds_api_connection(odds_key)))

    # Final summary
    safe_print("\n" + "=" * 50)
    safe_print("📋 Setup Summary:")

    for service, success in test_results:
        status = "✅ WORKING" if success else "❌ FAILED"
        safe_print(f"   {service}: {status}")

    if all(result[1] for result in test_results):
        safe_print("\n🎉 All API connections successful!")
        safe_print("Your EQ12 platform is ready to use!")
    else:
        safe_print("\n⚠️ Some API connections failed.")
        safe_print("Please check the error messages above and fix the issues.")

    safe_print("\n📝 Next Steps:")
    safe_print("   1. Restart your terminal/IDE to load new environment variables")
    safe_print("   2. Run: python eq12_enhanced_openai_sdk.py --test")
    safe_print("   3. Check your usage at: https://platform.openai.com/usage")

    return 0 if all(result[1] for result in test_results) else 1


if __name__ == "__main__":
    sys.exit(main())
