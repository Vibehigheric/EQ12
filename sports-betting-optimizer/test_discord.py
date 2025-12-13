#!/usr/bin/env python3
"""
EQ12 Discord Integration Test - Test Discord webhook functionality
Usage: python test_discord.py [--webhook-url URL] [--test-type TYPE]
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.integrations.discord_integration import (
        DiscordNotifier,
        create_bet_alert_embed,
        create_bet_settlement_embed,
        create_daily_summary_embed,
        notify_bet_alert_sync,
        notify_bet_settlement_sync,
    )

    DISCORD_AVAILABLE = True
except ImportError as e:
    print(f"❌ Discord integration not available: {e}")
    DISCORD_AVAILABLE = False


def test_webhook_sync(webhook_url: str) -> None:
    """Test synchronous Discord webhook functionality"""
    print("🔄 Testing synchronous Discord webhook...")

    # Test 1: Simple bet alert
    success = notify_bet_alert_sync(
        bet_id="test-sync-001",
        sport="NFL",
        stake=50.0,
        ev=4.2,
        odds=2.1,
        webhook_url=webhook_url,
    )
    print(f"✅ Bet alert test: {'SUCCESS' if success else 'FAILED'}")

    # Test 2: Bet settlement
    success = notify_bet_settlement_sync(
        bet_id="test-sync-001",
        sport="NFL",
        stake=50.0,
        result="win",
        payout=105.0,
        profit_loss=55.0,
        new_balance=1055.0,
        webhook_url=webhook_url,
    )
    print(f"✅ Settlement test: {'SUCCESS' if success else 'FAILED'}")


async def test_webhook_async(webhook_url: str) -> None:
    """Test asynchronous Discord webhook functionality"""
    print("🔄 Testing asynchronous Discord webhook...")

    notifier = DiscordNotifier(webhook_url)

    # Test 1: Rich bet alert embed
    alert_embed = create_bet_alert_embed(
        bet_id="test-async-001",
        sport="NBA",
        stake=75.0,
        ev=6.8,
        odds=2.3,
        boost_pct=25.0,
        book="DraftKings",
        alert_type="BOOST",
    )

    success = await notifier.send_async(content="🚨 **ASYNC TEST ALERT**", embeds=[alert_embed])
    print(f"✅ Async alert test: {'SUCCESS' if success else 'FAILED'}")

    # Test 2: Settlement embed
    settlement_embed = create_bet_settlement_embed(
        bet_id="test-async-001",
        sport="NBA",
        stake=75.0,
        result="win",
        payout=172.5,
        profit_loss=97.5,
        new_balance=1152.5,
    )

    success = await notifier.send_async(
        content="🎉 **ASYNC TEST SETTLEMENT**", embeds=[settlement_embed]
    )
    print(f"✅ Async settlement test: {'SUCCESS' if success else 'FAILED'}")


def test_embed_creation() -> None:
    """Test Discord embed creation without sending"""
    print("🧪 Testing Discord embed creation...")

    # Test bet alert embed
    alert_embed = create_bet_alert_embed(
        bet_id="embed-test-001",
        sport="CFB",
        stake=100.0,
        ev=8.5,
        odds=3.2,
        boost_pct=15.0,
    )

    required_fields = ["title", "color", "timestamp", "fields"]
    embed_valid = all(field in alert_embed for field in required_fields)
    print(f"✅ Alert embed: {'VALID' if embed_valid else 'INVALID'}")

    if embed_valid:
        print(f"   Title: {alert_embed['title']}")
        print(f"   Fields: {len(alert_embed['fields'])} fields")

    # Test settlement embed
    settlement_embed = create_bet_settlement_embed(
        bet_id="embed-test-001",
        sport="CFB",
        stake=100.0,
        result="loss",
        payout=0.0,
        profit_loss=-100.0,
        new_balance=900.0,
    )

    embed_valid = all(field in settlement_embed for field in required_fields)
    print(f"✅ Settlement embed: {'VALID' if embed_valid else 'INVALID'}")

    if embed_valid:
        print(f"   Title: {settlement_embed['title']}")
        print(f"   Color: {settlement_embed['color']:06X}")

    # Test daily summary embed
    mock_stats = {
        "total_profit_loss": 125.50,
        "win_rate": 65.0,
        "roi": 8.2,
        "settled_bets": 12,
        "wins": 8,
        "losses": 4,
        "current_balance": 1125.50,
    }

    summary_embed = create_daily_summary_embed(mock_stats)
    embed_valid = all(field in summary_embed for field in required_fields)
    print(f"✅ Summary embed: {'VALID' if embed_valid else 'INVALID'}")


def interactive_webhook_test() -> None:
    """Interactive webhook testing mode"""
    print("🎮 EQ12 Discord Integration Test Suite")
    print("=" * 45)

    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        webhook_url = input("Discord Webhook URL: ").strip()
        if not webhook_url:
            print("❌ Webhook URL required for testing")
            return

    print(f"🔗 Using webhook: {webhook_url[:50]}...")

    while True:
        print("\nTest options:")
        print("1. Test embed creation (no webhook)")
        print("2. Test sync webhook")
        print("3. Test async webhook")
        print("4. Send custom message")
        print("q. Quit")

        choice = input("\nChoice: ").strip().lower()

        if choice == "q" or choice == "quit":
            break
        if choice == "1":
            test_embed_creation()
        elif choice == "2":
            test_webhook_sync(webhook_url)
        elif choice == "3":
            asyncio.run(test_webhook_async(webhook_url))
        elif choice == "4":
            message = input("Custom message: ").strip()
            if message:
                notifier = DiscordNotifier(webhook_url)
                success = notifier.send_sync(content=f"🧪 **Test Message**\n{message}")
                print(f"✅ Custom message: {'SENT' if success else 'FAILED'}")
        else:
            print("❌ Invalid choice")


def test_browser_extension_format() -> None:
    """Test browser extension compatible webhook format"""
    print("🌐 Testing browser extension webhook format...")

    from src.integrations.discord_integration import create_extension_webhook_payload

    # Test simple alert payload
    bet_data = {
        "id": "ext-test-001",
        "sport": "NFL",
        "stake": 25.0,
        "ev": 3.2,
        "odds": 1.95,
        "book": "FanDuel",
    }

    payload = create_extension_webhook_payload(
        message="New +EV opportunity detected!", bet_data=bet_data, alert_type="VALUE"
    )

    required_keys = ["content", "username"]
    payload_valid = all(key in payload for key in required_keys)
    print(f"✅ Extension payload: {'VALID' if payload_valid else 'INVALID'}")

    if payload_valid:
        print(f"   Content length: {len(payload['content'])} chars")
        print(f"   Has embeds: {'embeds' in payload}")

        # Show example JS usage
        print("\n📝 Browser Extension Usage:")
        print("```javascript")
        print("// In your extension background script:")
        print("const payload = " + str(payload).replace("'", '"'))
        print("")
        print("fetch(DISCORD_WEBHOOK_URL, {")
        print("  method: 'POST',")
        print("  headers: {'Content-Type': 'application/json'},")
        print("  body: JSON.stringify(payload)")
        print("});")
        print("```")


def main():
    if not DISCORD_AVAILABLE:
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="EQ12 Discord Integration Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_discord.py                        # Interactive mode
  python test_discord.py --test-type sync      # Test sync only
  python test_discord.py --test-type async     # Test async only
  python test_discord.py --test-type embeds    # Test embeds only
  python test_discord.py --test-type extension # Test extension format
        """,
    )

    parser.add_argument(
        "--webhook-url",
        type=str,
        help="Discord webhook URL (or use DISCORD_WEBHOOK_URL env var)",
    )
    parser.add_argument(
        "--test-type",
        choices=["sync", "async", "embeds", "extension"],
        help="Specific test type to run",
    )
    parser.add_argument("--interactive", "-i", action="store_true", help="Force interactive mode")

    args = parser.parse_args()

    # Set webhook URL
    webhook_url = args.webhook_url or os.getenv("DISCORD_WEBHOOK_URL")

    # Specific test types
    if args.test_type == "embeds":
        test_embed_creation()
        return
    if args.test_type == "extension":
        test_browser_extension_format()
        return
    if args.test_type == "sync" and webhook_url:
        test_webhook_sync(webhook_url)
        return
    if args.test_type == "async" and webhook_url:
        asyncio.run(test_webhook_async(webhook_url))
        return

    # Interactive mode (default)
    interactive_webhook_test()
    print("👋 Testing complete!")


if __name__ == "__main__":
    main()
