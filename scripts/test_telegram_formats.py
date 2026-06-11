#!/usr/bin/env python3
"""
Test Telegram with a simple message to see what works
"""

import asyncio

import aiohttp


async def test_simple():
    bot_token = "TELEGRAM_BOT_TOKEN_PLACEHOLDER"

    # Try different chat ID formats
    test_chat_ids = [
        "-5475370304",  # Original
        "5475370304",  # Without minus
        "-1005475370304",  # Supergroup format
    ]

    for chat_id in test_chat_ids:
        print(f"Testing chat ID: {chat_id}")

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": f"🧪 Test message to chat ID: {chat_id}"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    result = await response.json()

                    if response.status == 200:
                        print(f"✅ SUCCESS: {chat_id} works!")
                        return chat_id
                    else:
                        print(f"❌ Failed: {result.get('description', 'Unknown error')}")

        except Exception as e:
            print(f"❌ Error: {e}")

        print("-" * 40)

    print("\n💡 Instructions to get correct chat ID:")
    print("1. Search for @EdgeGodParlay_bot on Telegram")
    print("2. Start a chat and send: /start")
    print("3. Run: python get_chat_id.py")

    return None


if __name__ == "__main__":
    asyncio.run(test_simple())
