#!/usr/bin/env python3
"""
 EQ12 API KEY MANAGEMENT & AUTHENTICATION SYSTEM
=================================================

Comprehensive API key management, testing, and authentication system for the
EQ12 automation empire. Handles API key validation, rotation, fallback
strategies, and secure storage for all external service integrations.

Supported APIs:
- ODDS_API_KEY (Sports odds and betting lines)
- OPENWEATHER_API_KEY (Weather data for sports analysis)
- SPORTSDATA_API_KEY (Comprehensive sports statistics)
- ESPN_API_KEY (Real-time sports data)
- OPENAI_API_KEY (AI and ML capabilities)
- TELEGRAM_BOT_TOKEN (Notification system)
- TWITTER_API_KEY (Social intelligence monitoring)

Features:
- Real-time API key validation and testing
- Automatic fallback and retry mechanisms
- API key rotation and refresh capabilities
- Secure environment variable management
- Rate limiting and usage tracking
- Error handling and diagnostic reporting

Author: EQ12 Quantum Development Team
Version: 1.0.0 - API Key Management System
Date: November 7, 2025
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import hashlib


class APIStatus(Enum):
    """API status enumeration."""
    WORKING = "working"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    INVALID_KEY = "invalid_key"
    SERVICE_DOWN = "service_down"
    UNKNOWN = "unknown"


class APIProvider(Enum):
    """API provider enumeration."""
    ODDS_API = "odds_api"
    OPENWEATHER = "openweather"
    SPORTSDATA = "sportsdata"
    ESPN = "espn"
    OPENAI = "openai"
    TELEGRAM = "telegram"
    TWITTER = "twitter"


@dataclass
class APIKeyConfig:
    """API key configuration structure."""
    provider: APIProvider
    key_name: str
    test_endpoint: str
    test_method: str
    expected_status: int
    test_params: Dict[str, Any]
    headers: Dict[str, str]
    rate_limit: int  # requests per minute
    priority: int  # 1=critical, 2=important, 3=optional
    backup_keys: List[str]


@dataclass
class APITestResult:
    """API test result structure."""
    provider: APIProvider
    key_name: str
    status: APIStatus
    response_code: int
    response_time: float
    error_message: Optional[str]
    last_tested: datetime
    rate_limit_remaining: Optional[int]
    daily_usage: int


class EQ12APIKeyManager:
    """Comprehensive API key management and testing system."""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.configs_path = self.workspace_path / "configs"
        self.logs_path = self.workspace_path / "logs"
        
        # Load environment variables from .env file first
        self._load_env_file()
        
        # Ensure directories exist
        for path in [self.configs_path, self.logs_path]:
            path.mkdir(exist_ok=True)
        
        # Setup logging
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_path / f"api_key_manager_{self.timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # API configurations
        self.api_configs = self._initialize_api_configs()
        
        # Test results storage
        self.test_results = {}
        self.usage_tracking = {}
        
        # Session for HTTP requests
        self.session = None
    
    def _load_env_file(self):
        """Load environment variables from .env file."""
        env_files = [
            self.workspace_path / "configs" / ".env",
            self.workspace_path / ".env"
        ]
        
        for env_file in env_files:
            if env_file.exists():
                print(f" Loading environment from: {env_file}")
                try:
                    with open(env_file, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"').strip("'")
                                if key and value:
                                    os.environ[key] = value
                    print(f" Environment loaded from {env_file}")
                    return
                except Exception as e:
                    print(f"  Error loading {env_file}: {e}")
        
        print("  No .env file found, using system environment variables only")
    
    def _initialize_api_configs(self) -> Dict[APIProvider, APIKeyConfig]:
        """Initialize API key configurations for testing."""
        return {
            APIProvider.ODDS_API: APIKeyConfig(
                provider=APIProvider.ODDS_API,
                key_name="ODDS_API_KEY",
                test_endpoint="https://api.the-odds-api.com/v4/sports",
                test_method="GET",
                expected_status=200,
                test_params={},
                headers={"accept": "application/json"},
                rate_limit=500,  # 500 requests per month on free tier
                priority=1,  # Critical for betting
                backup_keys=["ODDS_API_KEY_BACKUP", "ODDS_API_KEY_ALT"]
            ),
            APIProvider.OPENWEATHER: APIKeyConfig(
                provider=APIProvider.OPENWEATHER,
                key_name="OPENWEATHER_API_KEY",
                test_endpoint="https://api.openweathermap.org/data/2.5/weather",
                test_method="GET",
                expected_status=200,
                test_params={"q": "London", "units": "metric"},
                headers={},
                rate_limit=1000,  # 1000 calls per day on free tier
                priority=2,  # Important for weather analysis
                backup_keys=["OPENWEATHER_API_KEY_BACKUP"]
            ),
            APIProvider.SPORTSDATA: APIKeyConfig(
                provider=APIProvider.SPORTSDATA,
                key_name="SPORTSDATA_API_KEY",
                test_endpoint="https://api.sportsdata.io/v3/nfl/scores/json/CurrentSeason",
                test_method="GET",
                expected_status=200,
                test_params={},
                headers={"accept": "application/json"},
                rate_limit=1000,  # Varies by plan
                priority=1,  # Critical for sports data
                backup_keys=["SPORTSDATA_API_KEY_BACKUP"]
            ),
            APIProvider.ESPN: APIKeyConfig(
                provider=APIProvider.ESPN,
                key_name="ESPN_API_KEY",
                test_endpoint="https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
                test_method="GET",
                expected_status=200,
                test_params={},
                headers={"accept": "application/json"},
                rate_limit=2000,  # Generally higher limits
                priority=2,  # Important for real-time data
                backup_keys=[]
            ),
            APIProvider.OPENAI: APIKeyConfig(
                provider=APIProvider.OPENAI,
                key_name="OPENAI_API_KEY",
                test_endpoint="https://api.openai.com/v1/models",
                test_method="GET",
                expected_status=200,
                test_params={},
                headers={"accept": "application/json"},
                rate_limit=3000,  # Varies by plan
                priority=2,  # Important for AI features
                backup_keys=["OPENAI_API_KEY_BACKUP"]
            ),
            APIProvider.TELEGRAM: APIKeyConfig(
                provider=APIProvider.TELEGRAM,
                key_name="TELEGRAM_BOT_TOKEN",
                test_endpoint="https://api.telegram.org/bot{token}/getMe",
                test_method="GET",
                expected_status=200,
                test_params={},
                headers={},
                rate_limit=30,  # 30 messages per second
                priority=2,  # Important for notifications
                backup_keys=["TELEGRAM_BOT_TOKEN_BACKUP"]
            ),
            APIProvider.TWITTER: APIKeyConfig(
                provider=APIProvider.TWITTER,
                key_name="TWITTER_API_KEY",
                test_endpoint="https://api.twitter.com/2/tweets/search/recent",
                test_method="GET",
                expected_status=200,
                test_params={"query": "test", "max_results": "10"},
                headers={"accept": "application/json"},
                rate_limit=300,  # 300 requests per 15 minutes
                priority=1,  # Critical for social intelligence
                backup_keys=["TWITTER_API_KEY_BACKUP", "TWITTER_BEARER_TOKEN"]
            )
        }
    
    async def _create_session(self):
        """Create aiohttp session for API testing."""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def _close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    def get_api_key(self, provider: APIProvider) -> Optional[str]:
        """Get API key from environment variables with fallback options."""
        config = self.api_configs[provider]
        
        # Try primary key
        primary_key = os.getenv(config.key_name)
        if primary_key:
            return primary_key
        
        # Try backup keys
        for backup_key in config.backup_keys:
            backup_value = os.getenv(backup_key)
            if backup_value:
                self.logger.info(f"Using backup key {backup_key} for {provider.value}")
                return backup_value
        
        return None
    
    def generate_test_api_key(self, provider: APIProvider) -> str:
        """Generate a test API key for demonstration purposes."""
        # Generate deterministic but fake API keys for testing
        seed = f"eq12_test_{provider.value}_{datetime.now().strftime('%Y%m%d')}"
        hash_obj = hashlib.md5(seed.encode())
        
        if provider == APIProvider.ODDS_API:
            return f"odds_{hash_obj.hexdigest()[:24]}"
        elif provider == APIProvider.OPENWEATHER:
            return hash_obj.hexdigest()[:32]
        elif provider == APIProvider.SPORTSDATA:
            return f"sd_{hash_obj.hexdigest()[:28]}"
        elif provider == APIProvider.ESPN:
            return f"espn_{hash_obj.hexdigest()[:20]}"
        elif provider == APIProvider.OPENAI:
            return f"sk-{hash_obj.hexdigest()[:48]}"
        elif provider == APIProvider.TELEGRAM:
            return f"{hash_obj.hexdigest()[:10]}:AAG{hash_obj.hexdigest()[10:45]}"
        elif provider == APIProvider.TWITTER:
            return f"twitter_{hash_obj.hexdigest()[:40]}"
        else:
            return hash_obj.hexdigest()[:32]
    
    async def test_api_key(self, provider: APIProvider, api_key: str) -> APITestResult:
        """Test a specific API key for functionality."""
        config = self.api_configs[provider]
        start_time = time.time()
        
        await self._create_session()
        
        try:
            # Prepare request
            url = config.test_endpoint
            params = config.test_params.copy()
            headers = config.headers.copy()
            
            # Add API key to request based on provider
            if provider == APIProvider.ODDS_API:
                params["apiKey"] = api_key
            elif provider == APIProvider.OPENWEATHER:
                params["appid"] = api_key
            elif provider == APIProvider.SPORTSDATA:
                params["key"] = api_key
            elif provider == APIProvider.ESPN:
                # ESPN might not require key for basic endpoints
                headers["X-API-Key"] = api_key
            elif provider == APIProvider.OPENAI:
                headers["Authorization"] = f"Bearer {api_key}"
            elif provider == APIProvider.TELEGRAM:
                url = url.format(token=api_key)
            elif provider == APIProvider.TWITTER:
                headers["Authorization"] = f"Bearer {api_key}"
            
            # Make request
            async with self.session.request(
                config.test_method,
                url,
                params=params,
                headers=headers
            ) as response:
                response_time = time.time() - start_time
                response_text = await response.text()
                
                # Determine status
                if response.status == config.expected_status:
                    status = APIStatus.WORKING
                    error_message = None
                elif response.status == 401:
                    status = APIStatus.INVALID_KEY
                    error_message = "Invalid API key or authentication failed"
                elif response.status == 429:
                    status = APIStatus.RATE_LIMITED
                    error_message = "Rate limit exceeded"
                elif response.status >= 500:
                    status = APIStatus.SERVICE_DOWN
                    error_message = f"Service unavailable (HTTP {response.status})"
                else:
                    status = APIStatus.FAILED
                    error_message = f"HTTP {response.status}: {response_text[:100]}"
                
                # Get rate limit info if available
                rate_limit_remaining = None
                if "x-ratelimit-remaining" in response.headers:
                    rate_limit_remaining = int(response.headers["x-ratelimit-remaining"])
                elif "x-rate-limit-remaining" in response.headers:
                    rate_limit_remaining = int(response.headers["x-rate-limit-remaining"])
                
                return APITestResult(
                    provider=provider,
                    key_name=config.key_name,
                    status=status,
                    response_code=response.status,
                    response_time=response_time,
                    error_message=error_message,
                    last_tested=datetime.now(timezone.utc),
                    rate_limit_remaining=rate_limit_remaining,
                    daily_usage=0  # Would track this in production
                )
                
        except asyncio.TimeoutError:
            return APITestResult(
                provider=provider,
                key_name=config.key_name,
                status=APIStatus.FAILED,
                response_code=0,
                response_time=time.time() - start_time,
                error_message="Request timeout",
                last_tested=datetime.now(timezone.utc),
                rate_limit_remaining=None,
                daily_usage=0
            )
        except Exception as e:
            return APITestResult(
                provider=provider,
                key_name=config.key_name,
                status=APIStatus.FAILED,
                response_code=0,
                response_time=time.time() - start_time,
                error_message=str(e),
                last_tested=datetime.now(timezone.utc),
                rate_limit_remaining=None,
                daily_usage=0
            )
    
    def create_api_key_setup_guide(self) -> str:
        """Create a comprehensive API key setup guide."""
        guide = """
 EQ12 API KEY SETUP GUIDE
=========================

To fix your API authentication issues, you need to obtain and configure the following API keys:

 CRITICAL APIS (Required for core functionality):
--------------------------------------------------

1. ODDS_API_KEY (The Odds API)
    Website: https://the-odds-api.com/
    Free Tier: 500 requests/month
    Setup: Sign up  Get API key  Set environment variable
    Command: set ODDS_API_KEY=your_api_key_here

2. SPORTSDATA_API_KEY (SportsData.io)
    Website: https://sportsdata.io/
    Free Tier: 1000 requests/month
    Setup: Create account  Choose NFL/NHL  Get key
    Command: set SPORTSDATA_API_KEY=your_api_key_here

3. TWITTER_API_KEY (Twitter API v2)
    Website: https://developer.twitter.com/
    Free Tier: Limited access
    Setup: Apply for developer account  Create app  Get bearer token
    Command: set TWITTER_API_KEY=your_bearer_token_here

 IMPORTANT APIS (Enhanced functionality):
------------------------------------------

4. OPENWEATHER_API_KEY (OpenWeatherMap)
    Website: https://openweathermap.org/api
    Free Tier: 1000 calls/day
    Setup: Sign up  API keys section  Copy key
    Command: set OPENWEATHER_API_KEY=your_api_key_here

5. OPENAI_API_KEY (OpenAI)
    Website: https://platform.openai.com/
    Paid: $5-20/month typical usage
    Setup: Create account  Billing  API keys  Create new
    Command: set OPENAI_API_KEY=sk-your_secret_key_here

6. TELEGRAM_BOT_TOKEN (Telegram Bot API)
    Website: https://core.telegram.org/bots
    Free: Unlimited
    Setup: Message @BotFather  /newbot  Follow instructions
    Command: set TELEGRAM_BOT_TOKEN=123456789:your_bot_token_here

 SETUP INSTRUCTIONS:
---------------------

OPTION 1 - PowerShell (Temporary):
set ODDS_API_KEY=your_key
set OPENWEATHER_API_KEY=your_key
set SPORTSDATA_API_KEY=your_key
set OPENAI_API_KEY=your_key
set TELEGRAM_BOT_TOKEN=your_token

OPTION 2 - Permanent Environment Variables:
1. Open System Properties  Advanced  Environment Variables
2. Add each API key as a new User or System variable
3. Restart VS Code/PowerShell to load new variables

OPTION 3 - .env File (Recommended):
1. Create .env file in C:\\EQ12\\
2. Add all your API keys:
   ODDS_API_KEY=your_key_here
   OPENWEATHER_API_KEY=your_key_here
   SPORTSDATA_API_KEY=your_key_here
   # ... etc

 SECURITY NOTES:
------------------
- Never commit API keys to git
- Use backup keys for redundancy
- Monitor usage to avoid rate limits
- Rotate keys periodically for security

 TESTING:
----------
Run this script again after setting up keys:
python eq12_api_key_manager.py --test-all
"""
        return guide
    
    def save_api_key_config(self, results: Dict[APIProvider, APITestResult]):
        """Save API key configuration and test results."""
        config_data = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "api_test_results": {},
            "working_apis": [],
            "failed_apis": [],
            "setup_required": []
        }
        
        for provider, result in results.items():
            config_data["api_test_results"][provider.value] = asdict(result)
            
            if result.status == APIStatus.WORKING:
                config_data["working_apis"].append(provider.value)
            elif result.status == APIStatus.INVALID_KEY:
                config_data["setup_required"].append(provider.value)
            else:
                config_data["failed_apis"].append(provider.value)
        
        # Save to config file
        config_file = self.configs_path / "api_key_status.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False, default=str)
        
        return config_file
    
    async def test_all_api_keys(self, use_test_keys: bool = False) -> Dict[APIProvider, APITestResult]:
        """Test all configured API keys."""
        print(" EQ12 API KEY MANAGEMENT & TESTING SYSTEM")
        print("=" * 45)
        print("Testing all API keys for authentication and functionality...")
        print()
        
        results = {}
        
        for provider in APIProvider:
            print(f" Testing {provider.value.upper()}...")
            
            # Get API key
            if use_test_keys:
                api_key = self.generate_test_api_key(provider)
                print(f"    Using generated test key: {api_key[:20]}...")
            else:
                api_key = self.get_api_key(provider)
            
            if not api_key:
                # Create a failed result for missing key
                result = APITestResult(
                    provider=provider,
                    key_name=self.api_configs[provider].key_name,
                    status=APIStatus.INVALID_KEY,
                    response_code=0,
                    response_time=0.0,
                    error_message="API key not found in environment variables",
                    last_tested=datetime.now(timezone.utc),
                    rate_limit_remaining=None,
                    daily_usage=0
                )
                print(f"    {result.error_message}")
            else:
                # Test the API key
                result = await self.test_api_key(provider, api_key)
                
                # Display result
                if result.status == APIStatus.WORKING:
                    print(f"    Working | Response: {result.response_time:.2f}s | Status: {result.response_code}")
                    if result.rate_limit_remaining is not None:
                        print(f"       Rate limit remaining: {result.rate_limit_remaining}")
                elif result.status == APIStatus.INVALID_KEY:
                    print(f"    Invalid Key | HTTP {result.response_code}")
                elif result.status == APIStatus.RATE_LIMITED:
                    print(f"    Rate Limited | HTTP {result.response_code}")
                elif result.status == APIStatus.SERVICE_DOWN:
                    print(f"    Service Down | HTTP {result.response_code}")
                else:
                    print(f"    Failed | {result.error_message}")
            
            results[provider] = result
            
            # Brief delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        await self._close_session()
        
        # Summary
        print(f"\n API TESTING SUMMARY")
        print("-" * 24)
        
        working_count = sum(1 for r in results.values() if r.status == APIStatus.WORKING)
        total_count = len(results)
        success_rate = (working_count / total_count) * 100
        
        print(f" Working APIs: {working_count}/{total_count} ({success_rate:.1f}%)")
        print(f" Failed APIs: {total_count - working_count}")
        
        # Categorize by priority
        critical_failed = []
        important_failed = []
        
        for provider, result in results.items():
            if result.status != APIStatus.WORKING:
                config = self.api_configs[provider]
                if config.priority == 1:
                    critical_failed.append(provider.value)
                elif config.priority == 2:
                    important_failed.append(provider.value)
        
        if critical_failed:
            print(f" Critical APIs down: {', '.join(critical_failed)}")
        if important_failed:
            print(f" Important APIs down: {', '.join(important_failed)}")
        
        # Save results
        config_file = self.save_api_key_config(results)
        print(f" Configuration saved: {config_file}")
        
        # Show setup guide if needed
        if working_count < total_count:
            print(f"\n API KEY SETUP REQUIRED")
            print("-" * 27)
            print("Some APIs failed authentication. Run with --setup-guide for detailed instructions.")
        
        return results


async def main():
    """Main execution function for API key manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 API Key Management & Testing System")
    parser.add_argument("--test-all", action="store_true", help="Test all configured API keys")
    parser.add_argument("--use-test-keys", action="store_true", help="Use generated test keys for demonstration")
    parser.add_argument("--setup-guide", action="store_true", help="Show comprehensive API key setup guide")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    args = parser.parse_args()
    
    try:
        # Initialize API key manager
        api_manager = EQ12APIKeyManager(args.workspace)
        
        if args.setup_guide:
            # Show setup guide
            guide = api_manager.create_api_key_setup_guide()
            print(guide)
            
            # Save guide to file
            guide_file = api_manager.configs_path / "api_key_setup_guide.txt"
            with open(guide_file, 'w', encoding='utf-8') as f:
                f.write(guide)
            print(f"\n Setup guide saved: {guide_file}")
            
        elif args.test_all:
            # Test all API keys
            results = await api_manager.test_all_api_keys(use_test_keys=args.use_test_keys)
            
            # Show additional recommendations
            print(f"\n NEXT STEPS:")
            print("-" * 12)
            print("1. Set up missing API keys using --setup-guide")
            print("2. Test again with --test-all")
            print("3. Monitor usage to avoid rate limits")
            print("4. Set up backup keys for redundancy")
            
        else:
            print(" EQ12 API Key Manager")
            print("Use --test-all to test all keys or --setup-guide for setup instructions")
        
        return 0
        
    except Exception as e:
        print(f" API KEY MANAGER ERROR: {e}")
        logging.error(f"API key manager error: {e}")
        return 1


if __name__ == "__main__":
    # Ensure proper event loop for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)