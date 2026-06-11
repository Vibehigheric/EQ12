#!/usr/bin/env python3
"""
Quick Telegram API Test
"""

import asyncio

import aiohttp


async def test_telegram():
    bot_token = "TELEGRAM_BOT_TOKEN_PLACEHOLDER"
    chat_id = "-5475370304"

    print(f"Bot Token: {bot_token[:10]}...")
    print(f"Chat ID: {chat_id}")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": "🧪 EQ12 Test Message - If you see this, Telegram integration works!",
        "parse_mode": "Markdown",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                response_text = await response.text()
                print(f"Status: {response.status}")
                print(f"Response: {response_text}")

                if response.status == 200:
                    print("✅ SUCCESS: Telegram message sent!")
                    return True
                else:
                    print("❌ FAILED: Check bot token and chat ID")

                    # Try getting bot info
                    bot_url = f"https://api.telegram.org/bot{bot_token}/getMe"
                    async with session.get(bot_url) as bot_response:
                        bot_text = await bot_response.text()
                        print(f"Bot Info: {bot_text}")

                    return False
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(test_telegram())
