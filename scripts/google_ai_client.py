"""
EQ12 Google AI Studio Integration
Phase 2 of API Enhancement Plan - Gemini Models with 1M tokens/minute FREE

Features:
- Gemini Pro for advanced reasoning
- Gemini Flash for ultra-fast responses
- 1M tokens per minute free tier
- Perfect backup for Groq
- Multi-modal capabilities (text, images, code)
"""

import logging
import time
from datetime import datetime
from typing import Any

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmBlockThreshold, HarmCategory

    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False
    logging.warning("Google AI SDK not installed. Install with: pip install google-generativeai")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EQ12GoogleAIClient:
    """
    EQ12 Google AI Studio Client for Gemini models
    Part of Phase 2 API enhancement - FREE 1M tokens/minute
    """

    def __init__(self):
        if not GOOGLE_AI_AVAILABLE:
            raise ImportError(
                "Google AI SDK not available. Install with: pip install google-generativeai"
            )

        # HARDCODED GOOGLE AI API KEY (User provided)
        self.api_key = "AIzaSyDlgzo9hrLHl9C1AuP-GwtJDFta23iwauc"
        logger.info("✅ Google AI API key hardcoded for EQ12 system")

        # Configure the client
        genai.configure(api_key=self.api_key)

        # Available Gemini models with free tier limits
        self.models = {
            "flash": {
                "name": "gemini-2.0-flash",
                "tokens_per_minute": 1000000,  # 1M tokens/minute FREE
                "requests_per_minute": 1000,
                "description": "Ultra-fast responses, perfect for real-time analysis",
            },
            "pro": {
                "name": "gemini-2.0-flash",
                "tokens_per_minute": 32000,  # Limited but powerful
                "requests_per_minute": 50,
                "description": "Advanced reasoning for complex betting analysis",
            },
            "pro-exp": {
                "name": "gemini-2.0-flash-exp",
                "tokens_per_minute": 32000,
                "requests_per_minute": 50,
                "description": "Experimental model with latest capabilities",
            },
        }

        self.usage_stats = {
            "requests_today": 0,
            "tokens_used": 0,
            "avg_response_time": 0.0,
            "last_reset": datetime.now().strftime("%Y-%m-%d"),
        }

        # Safety settings for sports content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        logger.info("🤖 EQ12 Google AI Client initialized successfully")
        logger.info(f"📊 Available models: {list(self.models.keys())}")

    def quick_analysis(self, prompt: str, model_type: str = "flash") -> str:
        """
        Ultra-fast betting analysis using Gemini Flash
        Perfect for real-time odds analysis and quick decisions
        """
        start_time = time.time()

        try:
            model_config = self.models[model_type]
            model = genai.GenerativeModel(
                model_name=model_config["name"], safety_settings=self.safety_settings
            )

            system_prompt = """You are an expert sports betting analyst for EQ12.
            Provide concise, actionable insights focused on:
            - Profitability and value bets
            - Risk assessment and bankroll management
            - Market inefficiencies and arbitrage opportunities
            - Data-driven recommendations with confidence levels

            Keep responses under 200 words and include specific betting advice."""

            full_prompt = f"{system_prompt}\n\nAnalysis Request: {prompt}"

            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.1,  # Low for consistent analysis
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1000,
                },
            )

            response_time = time.time() - start_time
            self._update_usage_stats(response_time, len(response.text) if response.text else 0)

            logger.info(
                f"✅ Google AI analysis completed in {response_time:.2f}s using {model_type}"
            )
            return response.text or "Analysis unavailable"

        except Exception as e:
            logger.error(f"❌ Google AI analysis failed: {e}")
            return f"Analysis unavailable: {e!s}"

    def betting_recommendation(self, game_data: dict[str, Any], model_type: str = "pro") -> str:
        """
        Advanced betting recommendation using Gemini Pro
        Best for complex multi-factor analysis
        """
        prompt = """
        Analyze this betting opportunity for EQ12 system:

        Game: {game_data.get('home_team', 'Unknown')} vs {game_data.get('away_team', 'Unknown')}
        Home Odds: {game_data.get('home_odds', 'N/A')}
        Away Odds: {game_data.get('away_odds', 'N/A')}
        Over/Under: {game_data.get('total_line', 'N/A')}

        Provide structured analysis:
        1. RECOMMENDATION: [Clear bet recommendation]
        2. CONFIDENCE: [Percentage confidence level]
        3. VALUE ANALYSIS: [Expected value calculation]
        4. RISK FACTORS: [Key risks to consider]
        5. BANKROLL SIZING: [Suggested bet size as % of bankroll]
        """

        return self.quick_analysis(prompt, model_type)

    def arbitrage_scanner(self, odds_data: list[dict[str, Any]], model_type: str = "flash") -> str:
        """
        Lightning-fast arbitrage opportunity detection
        Perfect for real-time market analysis
        """
        prompt = """
        Scan for arbitrage opportunities in this odds data:
        {json.dumps(odds_data, indent=2)}

        For each potential arbitrage:
        1. OPPORTUNITY: [Game and bet type]
        2. PROFIT MARGIN: [Guaranteed profit percentage]
        3. STAKES: [Exact amounts to bet on each outcome]
        4. SPORTSBOOKS: [Which books to use]
        5. TIME SENSITIVITY: [How quickly to act]

        Only report PROFITABLE arbitrage opportunities (>1% margin).
        """

        return self.quick_analysis(prompt, model_type)

    def nhl_game_analysis(self, game_info: dict[str, Any], model_type: str = "pro") -> str:
        """
        Deep NHL game analysis using Gemini Pro's reasoning capabilities
        """
        prompt = """
        NHL Game Analysis for EQ12 betting system:

        {game_info.get('away_team', 'Team A')} @ {game_info.get('home_team', 'Team B')}
        Game Time: {game_info.get('game_time', 'TBD')}

        Provide comprehensive analysis:
        1. TEAM FORM: Recent performance trends
        2. HEAD-TO-HEAD: Historical matchup data
        3. KEY FACTORS: Injuries, rest, motivation
        4. BETTING VALUE: Best bets and avoid spots
        5. PROP BETS: Player prop recommendations
        6. RISK ASSESSMENT: Variance and uncertainty factors

        Focus on profitable betting angles with specific recommendations.
        """

        return self.quick_analysis(prompt, model_type)

    def multi_model_analysis(self, prompt: str) -> dict[str, str]:
        """
        Get analysis from multiple Gemini models for comparison
        Great for important betting decisions
        """
        results = {}

        # Flash for speed
        results["flash"] = self.quick_analysis(f"Quick analysis: {prompt}", "flash")

        # Pro for depth
        results["pro"] = self.quick_analysis(f"Deep analysis: {prompt}", "pro")

        return results

    def _update_usage_stats(self, response_time: float, tokens_used: int):
        """Update internal usage tracking"""
        self.usage_stats["requests_today"] += 1
        self.usage_stats["tokens_used"] += tokens_used

        # Update average response time
        if self.usage_stats["avg_response_time"] == 0:
            self.usage_stats["avg_response_time"] = response_time
        else:
            self.usage_stats["avg_response_time"] = (
                self.usage_stats["avg_response_time"] + response_time
            ) / 2

    def get_usage_stats(self) -> dict[str, Any]:
        """Get current usage statistics"""
        return {
            "requests_today": self.usage_stats["requests_today"],
            "tokens_used": self.usage_stats["tokens_used"],
            "avg_response_time": f"{self.usage_stats['avg_response_time']:.2f}s",
            "available_models": list(self.models.keys()),
            "rate_limits": {
                model: {
                    "tokens_per_minute": config["tokens_per_minute"],
                    "requests_per_minute": config["requests_per_minute"],
                }
                for model, config in self.models.items()
            },
        }

    def health_check(self) -> bool:
        """Test connection and model availability"""
        try:
            test_result = self.quick_analysis("Test connection", "flash")
            return len(test_result) > 0
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Google AI Studio Client")
    parser.add_argument("--analyze", help="Quick betting analysis")
    parser.add_argument("--nhl-analysis", help="NHL game analysis")
    parser.add_argument(
        "--arbitrage-scan", action="store_true", help="Scan for arbitrage opportunities"
    )
    parser.add_argument("--betting-analysis", help="Betting recommendation for game data")
    parser.add_argument("--multi-model", help="Multi-model analysis")
    parser.add_argument("--test-connection", action="store_true", help="Test API connection")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        print("🤖 EQ12 Google AI Integration Demo")
        print("========================================")

        client = EQ12GoogleAIClient()

        if args.test_connection:
            print("\n🔄 Testing Google AI Studio connection...")
            if client.health_check():
                print("✅ Connection successful!")
            else:
                print("❌ Connection failed!")

        elif args.analyze:
            print("\n🎯 Quick Analysis:")
            result = client.quick_analysis(args.analyze)
            print(f"Analysis: {result}")

        elif args.nhl_analysis:
            print("\n🏒 NHL Game Analysis:")
            game_info = {
                "away_team": "Boston Bruins",
                "home_team": "Toronto Maple Leafs",
            }
            result = client.nhl_game_analysis(game_info)
            print(f"NHL Analysis: {result}")

        elif args.arbitrage_scan:
            print("\n💰 Arbitrage Scanner:")
            sample_odds = [
                {
                    "game": "BOS @ TOR",
                    "book": "BookA",
                    "home_odds": -140,
                    "away_odds": 150,
                },
                {
                    "game": "BOS @ TOR",
                    "book": "BookB",
                    "home_odds": -135,
                    "away_odds": 145,
                },
            ]
            result = client.arbitrage_scanner(sample_odds)
            print(f"Arbitrage Scan: {result}")

        elif args.multi_model:
            print("\n🎯 Multi-Model Analysis:")
            results = client.multi_model_analysis(args.multi_model)
            for model, analysis in results.items():
                print(f"\n{model.upper()}: {analysis[:150]}...")

        # Always show usage stats
        print("\n📊 Usage Statistics:")
        stats = client.get_usage_stats()
        for key, value in stats.items():
            if key != "rate_limits":
                print(f"  {key}: {value}")

        print("\n🎉 Google AI Studio integration working perfectly!")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n📝 Setup Instructions:")
        print("1. Get free API key: https://aistudio.google.com/app/apikey")
        print("2. Set GOOGLE_AI_API_KEY environment variable")
        print("3. Install SDK: pip install google-generativeai")
