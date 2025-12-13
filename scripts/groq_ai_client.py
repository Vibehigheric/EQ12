"""
EQ12 Groq AI Client - Ultra-Fast Inference Integration
====================================================

Groq provides 14,400 free requests per day with ultra-fast inference speeds.
Perfect for real-time sports analysis and betting decision support.

Setup Instructions:
1. Sign up at https://console.groq.com/
2. Get your API key from the dashboard
3. Set environment variable: GROQ_API_KEY=your_key_here
4. Install groq: pip install groq

Models Available (Free Tier):
- Llama 3.3 70B: 1,000 req/day, 12,000 tokens/min
- Llama 4 Scout: 1,000 req/day, 30,000 tokens/min
- Gemma 2 9B: 14,400 req/day, 15,000 tokens/min
- DeepSeek R1 Distill: 1,000 req/day, 6,000 tokens/min
"""

import logging
import os
import time
from dataclasses import dataclass
from typing import Any

from groq import Groq

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GroqUsageStats:
    """Track Groq API usage for monitoring."""

    requests_today: int = 0
    tokens_used: int = 0
    last_reset: str = ""
    average_response_time: float = 0.0


class EQ12GroqClient:
    """
    EQ12 Groq AI Client for ultra-fast inference.
    Optimized for sports betting analysis and real-time decision making.
    """

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.error("GROQ_API_KEY environment variable not found!")
            logger.info("Sign up at https://console.groq.com/ to get your free API key")
            raise ValueError("Missing GROQ_API_KEY")

        # Initialize Groq client with OpenAI-compatible base URL
        # Using official Groq OpenAI compatibility: https://api.groq.com/openai/v1
        self.client = Groq(api_key=self.api_key)
        self.usage_stats = GroqUsageStats()

        # GROQ INTEGRATION CAPABILITIES (from groq-api-cookbook)
        self.integration_features = {
            "function_calling": True,  # eCommerce, SQL, stock market analysis
            "tool_use": True,  # Parallel tool execution
            "json_mode": True,  # Structured output generation
            "guardrails": True,  # Llama Guard content filtering
            "mcp_support": True,  # Model Context Protocol
            "rag_compatible": True,  # RAG with LangChain/LlamaIndex
            "real_time_voice": True,  # Audio processing with Whisper
            "observability": True,  # MLflow, Arize monitoring
        }

        # EQ12 STRATEGIC DECISION ENGINE - Hardcoded task routing
        self.decision_engine = {
            "speed_critical_tasks": ["arbitrage", "live_odds", "quick_bets"],
            "accuracy_critical_tasks": ["complex_parlays", "risk_management"],
            "recommended_model_by_task": {
                "arbitrage": "ultra_fast",  # <0.5s response needed
                "live_betting": "ultra_fast",  # Real-time decisions
                "nhl_analysis": "balanced",  # Speed + accuracy balance
                "game_prediction": "balanced",  # Moderate complexity
                "complex_parlay": "compound",  # Advanced reasoning
                "risk_assessment": "fallback_to_openai",  # Safety critical
            },
            "performance_targets": {
                "arbitrage_response_time": "0.3-0.6s",
                "nhl_analysis_time": "0.8-1.2s",
                "daily_request_budget": 14400,
                "cost_per_month": 0,  # FREE TIER ONLY
            },
        }

        # EQ12 HARDCODED STRATEGY: Use Groq for real-time analysis, OpenAI for complex reasoning
        # Based on official Groq rate limits from console.groq.com
        self.models = {
            "ultra_fast": {
                "name": "llama-3.1-8b-instant",
                "requests_per_minute": 30,
                "requests_per_day": 14400,  # 14.4K per day
                "tokens_per_minute": 6000,
                "tokens_per_day": 500000,  # 500K per day
                "description": "REAL-TIME: Arbitrage detection, quick odds analysis, live betting decisions",
                "use_cases": ["arbitrage", "quick_analysis", "real_time_odds", "speed_critical"],
            },
            "balanced": {
                "name": "llama-3.3-70b-versatile",
                "requests_per_minute": 30,
                "requests_per_day": 1000,
                "tokens_per_minute": 12000,
                "tokens_per_day": 100000,
                "description": "BALANCED: NHL analysis, betting recommendations, moderate complexity",
                "use_cases": ["nhl_analysis", "betting_recommendations", "game_analysis"],
            },
            "compound": {
                "name": "groq/compound",
                "requests_per_minute": 30,
                "requests_per_day": 250,
                "tokens_per_minute": 70000,
                "tokens_per_day": "unlimited",
                "description": "ADVANCED: Complex reasoning when OpenAI unavailable",
                "use_cases": ["complex_reasoning", "multi_game_analysis", "advanced_strategies"],
            },
        }

        # EQ12 STRATEGIC RECOMMENDATION SYSTEM
        self.usage_strategy = {
            "primary_use": "Real-time analysis and arbitrage detection",
            "recommended_for": [
                "Live odds monitoring (ultra-fast response needed)",
                "Arbitrage opportunity scanning (speed critical)",
                "Quick betting decisions (under 1 second)",
                "Player prop analysis (moderate complexity)",
                "Game outcome predictions (balanced speed/accuracy)",
            ],
            "avoid_for": [
                "Complex multi-game parlays (use OpenAI GPT-4)",
                "Deep statistical modeling (use OpenAI o1)",
                "Long-form betting guides (use Claude)",
                "Risk management frameworks (use OpenAI for safety)",
            ],
            "fallback_strategy": "Always maintain OpenAI for complex reasoning tasks",
        }

        logger.info("🚀 EQ12 Groq Client initialized successfully")
        logger.info(f"📊 Available models: {list(self.models.keys())}")

    def quick_analysis(self, prompt: str, model_type: str = "ultra_fast") -> str:
        """
        EQ12 STRATEGIC METHOD: Ultra-fast AI analysis for real-time betting decisions
        HARDCODED STRATEGY: Use for arbitrage detection, live odds, quick bets

        Args:
            prompt: The analysis request
            model_type: 'ultra_fast', 'balanced', or 'compound'

        Returns:
            AI analysis response with <1s target response time
        """
        start_time = time.time()

        try:
            model_config = self.models.get(model_type, self.models["ultra_fast"])

            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert sports betting analyst for EQ12. Provide concise, actionable insights focused on profitability and risk assessment.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model=model_config["name"],
                max_tokens=1000,
                temperature=0.1,  # Low temperature for consistent analysis
                top_p=0.9,
            )

            response_time = time.time() - start_time
            self._update_usage_stats(response_time)

            result = response.choices[0].message.content

            logger.info(f"✅ Groq analysis completed in {response_time:.2f}s using {model_type}")
            return result

        except Exception as e:
            logger.error(f"❌ Groq analysis failed: {e!s}")
            return f"Analysis unavailable: {e!s}"

    def betting_recommendation(self, game_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate betting recommendations for a specific game.

        Args:
            game_data: Dictionary containing game information

        Returns:
            Betting analysis and recommendations
        """
        prompt = """
        Analyze this betting opportunity for EQ12:

        Game: {game_data.get('matchup', 'N/A')}
        Odds: {game_data.get('odds', 'N/A')}
        Market: {game_data.get('market', 'N/A')}

        Provide:
        1. Risk assessment (1-10 scale)
        2. Expected value calculation
        3. Recommended bet size (as % of bankroll)
        4. Key factors supporting the recommendation
        5. Stop-loss conditions

        Be specific and actionable.
        """

        analysis = self.quick_analysis(prompt, "balanced")

        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "game": game_data.get("matchup", "Unknown"),
            "analysis": analysis,
            "model_used": "groq_smart",
            "confidence": "high" if "recommend" in analysis.lower() else "medium",
        }

    def arbitrage_scanner(self, odds_data: list[dict]) -> str:
        """
        Ultra-fast arbitrage opportunity scanning.

        Args:
            odds_data: List of odds from different bookmakers

        Returns:
            Arbitrage analysis
        """
        prompt = """
        URGENT: Scan for arbitrage opportunities in this odds data:

        {odds_data}

        Calculate:
        1. Implied probabilities for each outcome
        2. Total implied probability
        3. Arbitrage percentage (if <100%)
        4. Optimal bet distribution
        5. Guaranteed profit amount

        Respond immediately with YES/NO for arbitrage opportunity, followed by details.
        """

        return self.quick_analysis(prompt, "ultra_fast")  # Use fastest model for arbitrage

    def nhl_game_analysis(self, home_team: str, away_team: str, odds: dict) -> str:
        """
        Specialized NHL game analysis for tonight's games.

        Args:
            home_team: Home team name
            away_team: Away team name
            odds: Odds dictionary

        Returns:
            NHL-specific analysis
        """
        prompt = """
        NHL BETTING ANALYSIS for EQ12:

        Game: {away_team} @ {home_team}
        Current Odds: {odds}

        Analyze:
        1. Moneyline value (both teams)
        2. Over/under assessment
        3. Puck line opportunities
        4. Key player props to watch
        5. Home ice advantage impact

        Provide specific betting recommendations with confidence levels.
        Focus on profitable opportunities for EQ12's NHL betting strategy.
        """

        return self.quick_analysis(prompt, "balanced")

    def get_usage_stats(self) -> dict[str, Any]:
        """Get current usage statistics."""
        return {
            "requests_today": self.usage_stats.requests_today,
            "tokens_used": self.usage_stats.tokens_used,
            "avg_response_time": f"{self.usage_stats.average_response_time:.2f}s",
            "available_models": list(self.models.keys()),
            "rate_limits": {
                model: config["requests_per_day"] for model, config in self.models.items()
            },
        }

    def _update_usage_stats(self, response_time: float):
        """Update internal usage tracking."""
        self.usage_stats.requests_today += 1

        # Update average response time
        if self.usage_stats.average_response_time == 0:
            self.usage_stats.average_response_time = response_time
        else:
            # Simple moving average
            self.usage_stats.average_response_time = (
                self.usage_stats.average_response_time * 0.9 + response_time * 0.1
            )


def demo_groq_integration():
    """Demonstrate Groq integration with EQ12."""
    print("🚀 EQ12 Groq Integration Demo")
    print("=" * 40)

    try:
        client = EQ12GroqClient()

        # Demo 1: Quick betting analysis
        print("\n📊 Demo 1: Quick Betting Analysis")
        analysis = client.quick_analysis(
            "Should I bet on Colorado Avalanche tonight? They're +150 against Vegas Golden Knights."
        )
        print(f"Analysis: {analysis[:200]}...")

        # Demo 2: NHL game analysis
        print("\n🏒 Demo 2: NHL Game Analysis")
        nhl_analysis = client.nhl_game_analysis(
            "Vegas Golden Knights",
            "Colorado Avalanche",
            {"ml_home": -180, "ml_away": +150, "total": 6.5},
        )
        print(f"NHL Analysis: {nhl_analysis[:200]}...")

        # Demo 3: Usage stats
        print("\n📈 Demo 3: Usage Statistics")
        stats = client.get_usage_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Make sure to set GROQ_API_KEY environment variable")


if __name__ == "__main__":
    demo_groq_integration()
