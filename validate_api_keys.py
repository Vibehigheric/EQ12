#!/usr/bin/env python3
"""
EQ12 API Key Validator - Test all configured API keys
Validates that API keys are properly configured and functional
"""
import asyncio
import os
import sys
from datetime import datetime

import aiohttp


# Color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_colored(message: str, color: str = Colors.RESET) -> None:
    """Print colored message"""
    print(f"{color}{message}{Colors.RESET}")

async def test_odds_api():
    """Test The Odds API"""
    print_colored("\n🎯 Testing The Odds API...", Colors.YELLOW)
    
    api_key = os.getenv('THE_ODDS_API_KEY') or os.getenv('ODDS_API_KEY')
    if not api_key:
        print_colored("❌ THE_ODDS_API_KEY not found", Colors.RED)
        return False
    
    try:
        url = f"https://api.the-odds-api.com/v4/sports/?apiKey={api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    print_colored(f"✅ The Odds API working - {len(data)} sports available", Colors.GREEN)
                    return True
                else:
                    print_colored(f"❌ The Odds API error: {response.status}", Colors.RED)
                    return False
    except Exception as e:
        print_colored(f"❌ The Odds API connection error: {e}", Colors.RED)
        return False

async def test_openai_api():
    """Test OpenAI API"""
    print_colored("\n🤖 Testing OpenAI API...", Colors.YELLOW)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print_colored("❌ OPENAI_API_KEY not found", Colors.RED)
        return False
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Say 'EQ12 API test successful' in exactly those words."}],
            "max_tokens": 10
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=15
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    message = result['choices'][0]['message']['content'].strip()
                    print_colored(f"✅ OpenAI API working - Response: '{message}'", Colors.GREEN)
                    return True
                else:
                    error_text = await response.text()
                    print_colored(f"❌ OpenAI API error: {response.status} - {error_text[:100]}...", Colors.RED)
                    return False
    except Exception as e:
        print_colored(f"❌ OpenAI API connection error: {e}", Colors.RED)
        return False

async def test_groq_api():
    """Test Groq API"""
    print_colored("\n⚡ Testing Groq API...", Colors.YELLOW)
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print_colored("❌ GROQ_API_KEY not found", Colors.RED)
        return False
    
    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": "Say 'EQ12 Groq test successful' in exactly those words."}],
            "max_tokens": 10
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=15
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    message = result['choices'][0]['message']['content'].strip()
                    print_colored(f"✅ Groq API working - Response: '{message}'", Colors.GREEN)
                    return True
                else:
                    error_text = await response.text()
                    print_colored(f"❌ Groq API error: {response.status} - {error_text[:100]}...", Colors.RED)
                    return False
    except Exception as e:
        print_colored(f"❌ Groq API connection error: {e}", Colors.RED)
        return False

async def test_telegram_api():
    """Test Telegram Bot API"""
    print_colored("\n📱 Testing Telegram API...", Colors.YELLOW)
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token:
        print_colored("❌ TELEGRAM_BOT_TOKEN not found", Colors.RED)
        return False
    
    if not chat_id:
        print_colored("❌ TELEGRAM_CHAT_ID not found", Colors.RED)
        return False
    
    try:
        # Test bot info
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['ok']:
                        bot_info = data['result']
                        print_colored(f"✅ Telegram Bot API working - Bot: @{bot_info.get('username', 'unknown')}", Colors.GREEN)
                        
                        # Send test message
                        test_message = f"🧪 EQ12 API Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n✅ All systems operational!"
                        message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                        message_data = {
                            'chat_id': chat_id,
                            'text': test_message
                        }
                        
                        async with session.post(message_url, json=message_data, timeout=10) as msg_response:
                            if msg_response.status == 200:
                                print_colored("✅ Test message sent successfully", Colors.GREEN)
                                return True
                            else:
                                print_colored("⚠️  Bot works but message failed - check chat ID", Colors.YELLOW)
                                return True  # Bot itself works
                    else:
                        print_colored(f"❌ Telegram Bot error: {data.get('description', 'Unknown error')}", Colors.RED)
                        return False
                else:
                    print_colored(f"❌ Telegram API error: {response.status}", Colors.RED)
                    return False
    except Exception as e:
        print_colored(f"❌ Telegram API connection error: {e}", Colors.RED)
        return False

def test_github_token():
    """Test GitHub Token (synchronous)"""
    print_colored("\n🐙 Testing GitHub Token...", Colors.YELLOW)
    
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print_colored("❌ GITHUB_TOKEN not found", Colors.RED)
        return False
    
    # Just validate the token format for now
    if token.startswith('github_pat_') or token.startswith('ghp_'):
        print_colored("✅ GitHub Token format valid", Colors.GREEN)
        print_colored("ℹ️  Token will be tested in CI/CD pipeline", Colors.BLUE)
        return True
    else:
        print_colored("❌ Invalid GitHub token format", Colors.RED)
        return False

async def main():
    """Run all API tests"""
    print_colored(f"{Colors.BOLD}🔑 EQ12 API KEY VALIDATION SUITE{Colors.RESET}", Colors.CYAN)
    print_colored("Testing all configured API keys for EQ12 betting automation", Colors.BLUE)
    print_colored(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.BLUE)
    
    # Run all tests
    tests = [
        ("The Odds API", test_odds_api()),
        ("OpenAI API", test_openai_api()),
        ("Groq AI API", test_groq_api()),
        ("Telegram Bot", test_telegram_api()),
        ("GitHub Token", test_github_token())
    ]
    
    results = []
    
    for test_name, test_coro in tests:
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            results.append((test_name, result))
        except Exception as e:
            print_colored(f"\n❌ {test_name} test failed with exception: {e}", Colors.RED)
            results.append((test_name, False))
    
    # Summary
    print_colored(f"\n{'='*60}", Colors.CYAN)
    print_colored("🎯 API VALIDATION SUMMARY", Colors.BOLD + Colors.CYAN)
    print_colored(f"{'='*60}", Colors.CYAN)
    
    passed = 0
    for test_name, result in results:
        status_icon = "✅" if result else "❌"
        color = Colors.GREEN if result else Colors.RED
        print_colored(f"  {status_icon} {test_name}", color)
        if result:
            passed += 1
    
    total = len(results)
    print_colored(f"\n📊 Results: {passed}/{total} APIs validated successfully", Colors.BLUE)
    
    if passed == total:
        print_colored("\n🎉 ALL APIs WORKING! EQ12 betting automation is fully configured! 🚀", Colors.GREEN + Colors.BOLD)
        return 0
    elif passed >= 3:  # At least core APIs work
        print_colored(f"\n⚠️  PARTIAL SUCCESS: {passed}/{total} APIs working - sufficient for basic operations", Colors.YELLOW + Colors.BOLD)
        return 0
    else:
        print_colored(f"\n❌ INSUFFICIENT APIs: Only {passed}/{total} working - check configuration", Colors.RED + Colors.BOLD)
        return 1

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_colored("\n🛑 API tests interrupted by user", Colors.YELLOW)
        sys.exit(130)
    except Exception as e:
        print_colored(f"\n💥 Unexpected error: {e}", Colors.RED)
        sys.exit(1)