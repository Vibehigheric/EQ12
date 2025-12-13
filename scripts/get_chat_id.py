#!/usr/bin/env python3
"""
Get Telegram Chat ID Helper
Send /start to @EdgeGodParlay_bot first, then run this script
"""

import asyncio

import aiohttp


async def get_updates():
    bot_token = "7913469072:AAHlN0XQyZG1G8uHGnbjLacUbh6QybTb8pc"

    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

    try:
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            response_data = await response.json()

            print("Recent Telegram Updates:")
            print("=" * 50)

            if response_data.get("ok") and response_data.get("result"):
                for update in response_data["result"][-5:]:  # Last 5 updates
                    message = update.get("message", {})
                    chat = message.get("chat", {})

                    print(f"Chat ID: {chat.get('id')}")
                    print(f"Chat Type: {chat.get('type')}")
                    print(f"From: {message.get('from', {}).get('first_name', 'Unknown')}")
                    print(f"Text: {message.get('text', 'No text')}")
                    print("-" * 30)

                if response_data["result"]:
                    last_chat_id = response_data["result"][-1]["message"]["chat"]["id"]
                    print(f"\n✅ Latest Chat ID: {last_chat_id}")
                    print("\nTo test, run:")
                    print(f"$env:TELEGRAM_CHAT_ID = '{last_chat_id}'")
                    return last_chat_id
                else:
                    print("❌ No updates found. Send /start to @EdgeGodParlay_bot first")
            else:
                print("❌ No updates found or API error")

    except Exception as e:
        print(f"Error: {e}")

    return None


if __name__ == "__main__":
    asyncio.run(get_updates())
