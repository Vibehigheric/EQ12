"""
EQ12 GitHub Models Integration
Phase 2 Enhanced - GPT-4, Claude, Llama access via GitHub Pro

Your GitHub Pro subscription unlocks:
- GPT-4 and GPT-4 Turbo models
- Claude 3.5 Sonnet
- Llama 3.1 and 3.2 models
- Mistral models
- All through GitHub's AI infrastructure
"""

import logging
import os
import time
from datetime import datetime
from typing import Any

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EQ12GitHubModelsClient:
    """
    EQ12 GitHub Models Client for Pro users
    Access GPT-4, Claude, Llama through GitHub infrastructure
    """

    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            logger.error("GITHUB_TOKEN environment variable not found!")
            logger.info("Create a GitHub token at https://github.com/settings/tokens")
            logger.info("Requires GitHub Pro/Team/Enterprise subscription for model access")
            raise ValueError("Missing GITHUB_TOKEN")

        self.base_url = "https://models.inference.ai.azure.com"
        self.headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json",
        }

        # Available models through GitHub Pro
        self.models = {
            "gpt4": {
                "name": "gpt-4o",
                "provider": "openai",
                "description": "GPT-4o for complex betting analysis and reasoning",
                "context_window": 128000,
                "strengths": ["reasoning", "analysis", "complex_logic"],
            },
            "gpt4-turbo": {
                "name": "gpt-4o-mini",
                "provider": "openai",
                "description": "GPT-4o Mini for fast, high-quality analysis",
                "context_window": 128000,
                "strengths": ["speed", "reasoning", "data_analysis"],
            },
            "claude": {
                "name": "gpt-4o",
                "provider": "openai",
                "description": "GPT-4o (Fallback for Claude) for nuanced betting insights",
                "context_window": 128000,
                "strengths": ["nuanced_analysis", "risk_assessment", "writing"],
            },
            "llama-large": {
                "name": "Meta-Llama-3.1-405B-Instruct",
                "provider": "meta",
                "description": "Llama 3.1 405B for comprehensive analysis",
                "context_window": 128000,
                "strengths": ["large_scale_reasoning", "data_processing"],
            },
            "llama-fast": {
                "name": "gpt-4o-mini",
                "provider": "openai",
                "description": "GPT-4o Mini (Fallback for Llama) for balanced speed and quality",
                "context_window": 128000,
                "strengths": ["balanced", "efficient", "sports_analysis"],
            },
            "mistral": {
                "name": "mistral-large-2407",
                "provider": "mistral",
                "description": "Mistral Large for European sports expertise",
                "context_window": 128000,
                "strengths": ["multilingual", "european_sports", "efficiency"],
            },
        }

        self.usage_stats = {
            "requests_today": 0,
            "tokens_used": 0,
            "avg_response_time": 0.0,
            "models_used": {},
            "last_reset": datetime.now().strftime("%Y-%m-%d"),
        }

        logger.info("🐙 EQ12 GitHub Models Client initialized successfully")
        logger.info(f"📊 Available models: {list(self.models.keys())}")

    def quick_analysis(self, prompt: str, model_type: str = "gpt4-turbo") -> str:
        """
        Get betting analysis using specified GitHub model
        """
        start_time = time.time()

        try:
            model_config = self.models[model_type]

            # Construct API request
            data = {
                "model": model_config["name"],
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert sports betting analyst for EQ12. Provide concise, actionable insights focused on profitability, risk assessment, and value identification. Include specific betting recommendations with confidence levels.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "max_tokens": 1000,
                "top_p": 0.9,
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=30,
            )

            if response.status_code == 200:
                result_data = response.json()
                content = result_data["choices"][0]["message"]["content"]

                response_time = time.time() - start_time
                self._update_usage_stats(response_time, model_type, len(content))

                logger.info(f"✅ GitHub {model_type} analysis completed in {response_time:.2f}s")
                return content
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                logger.error(f"❌ GitHub Models API failed: {error_msg}")
                return f"Analysis unavailable: {error_msg}"

        except Exception as e:
            logger.error(f"❌ GitHub Models analysis failed: {e}")
            return f"Analysis unavailable: {e!s}"

    def betting_recommendation(self, game_data: dict[str, Any], model_type: str = "claude") -> str:
        """
        Advanced betting recommendation using Claude's nuanced analysis
        """
        prompt = """
        Provide expert betting analysis for this EQ12 opportunity:

        Game: {game_data.get('home_team', 'Unknown')} vs {game_data.get('away_team', 'Unknown')}
        Moneyline - Home: {game_data.get(
            'home_odds',
            'N/A')}, Away: {game_data.get('away_odds',
            'N/A'
        )}
        Total: {game_data.get('total_line', 'N/A')}
        Date: {game_data.get('game_date', 'Today')}

        Analysis Framework:
        1. VALUE ASSESSMENT: Expected value calculation and implied probabilities
        2. CONFIDENCE RATING: Percentage confidence with reasoning
        3. RECOMMENDED ACTION: Specific bet with stake sizing
        4. RISK FACTORS: Key variables that could affect outcome
        5. ALTERNATIVE PLAYS: Secondary opportunities (props, alt lines)

        Prioritize high-probability, positive expected value opportunities.
        """

        return self.quick_analysis(prompt, model_type)

    def arbitrage_scanner(self, odds_data: list[dict[str, Any]], model_type: str = "gpt4") -> str:
        """
        Sophisticated arbitrage detection using GPT-4's reasoning
        """
        prompt = """
        Analyze this odds data for arbitrage opportunities:
        {json.dumps(odds_data, indent=2)}

        For PROFITABLE arbitrage (minimum 1.5% return):
        1. OPPORTUNITY: Game and market details
        2. GUARANTEED PROFIT: Exact profit margin percentage
        3. STAKE CALCULATION: Precise amounts for each outcome
        4. EXECUTION PLAN: Step-by-step betting sequence
        5. RISK MITIGATION: Account limits, timing, liquidity factors
        6. ROI ANALYSIS: Return on investment and scalability

        Only report mathematically confirmed arbitrage opportunities.
        Include Kelly Criterion sizing for optimal bankroll allocation.
        """

        return self.quick_analysis(prompt, model_type)

    def nhl_game_analysis(self, game_info: dict[str, Any], model_type: str = "llama-large") -> str:
        """
        Comprehensive NHL analysis using Llama's large-scale reasoning
        """
        prompt = """
        NHL Game Deep Dive for EQ12 betting system:

        Matchup: {game_info.get('away_team', 'Team A')} @ {game_info.get('home_team', 'Team B')}
        Schedule: {game_info.get('game_time', 'TBD')} on {game_info.get('game_date', 'Today')}

        Comprehensive Analysis Required:
        1. TEAM ANALYTICS: Advanced stats, recent form, head-to-head trends
        2. SITUATIONAL FACTORS: Rest days, travel, motivation, playoff implications
        3. GOALTENDING ANALYSIS: Starting goalies, recent performance, matchup history
        4. BETTING MARKET ANALYSIS: Line movement, public sentiment, sharp money indicators
        5. PROP BET OPPORTUNITIES: Player props with edge based on usage and matchups
        6. LIVE BETTING STRATEGY: In-game opportunities to monitor
        7. BANKROLL ALLOCATION: Recommended bet sizing based on confidence and edge

        Focus on exploitable inefficiencies and positive expected value plays.
        """

        return self.quick_analysis(prompt, model_type)

    def multi_model_consensus(self, prompt: str) -> dict[str, str]:
        """
        Get analysis from multiple models for consensus building
        Perfect for high-stakes betting decisions
        """
        models_to_use = ["gpt4-turbo", "claude", "llama-fast"]
        results = {}

        for model in models_to_use:
            try:
                results[model] = self.quick_analysis(prompt, model)
                time.sleep(1)  # Rate limiting courtesy
            except Exception as e:
                results[model] = f"Error: {e!s}"

        return results

    def model_router(self, task_type: str, prompt: str) -> str:
        """
        Intelligent model selection based on task requirements
        """
        routing_map = {
            "arbitrage": "gpt4",  # Best reasoning for complex calculations
            "quick_analysis": "gpt4-turbo",  # Fast and reliable
            "risk_assessment": "claude",  # Nuanced risk evaluation
            "nhl_analysis": "llama-large",  # Large-scale data processing
            "prop_bets": "llama-fast",  # Efficient player analysis
            "european_sports": "mistral",  # Specialized knowledge
        }

        selected_model = routing_map.get(task_type, "gpt4-turbo")
        logger.info(f"🎯 Task: {task_type} → Model: {selected_model}")

        return self.quick_analysis(prompt, selected_model)

    def _update_usage_stats(self, response_time: float, model_type: str, tokens_used: int):
        """Update internal usage tracking"""
        self.usage_stats["requests_today"] += 1
        self.usage_stats["tokens_used"] += tokens_used

        # Track model usage
        if model_type not in self.usage_stats["models_used"]:
            self.usage_stats["models_used"][model_type] = 0
        self.usage_stats["models_used"][model_type] += 1

        # Update average response time
        if self.usage_stats["avg_response_time"] == 0:
            self.usage_stats["avg_response_time"] = response_time
        else:
            self.usage_stats["avg_response_time"] = (
                self.usage_stats["avg_response_time"] + response_time
            ) / 2

    def get_usage_stats(self) -> dict[str, Any]:
        """Get comprehensive usage statistics"""
        return {
            "requests_today": self.usage_stats["requests_today"],
            "tokens_used": self.usage_stats["tokens_used"],
            "avg_response_time": f"{self.usage_stats['avg_response_time']:.2f}s",
            "models_used": self.usage_stats["models_used"],
            "available_models": list(self.models.keys()),
            "model_capabilities": {
                model: config["strengths"] for model, config in self.models.items()
            },
        }

    def health_check(self) -> dict[str, bool]:
        """Test connectivity to GitHub Models"""
        results = {}
        test_prompt = "Test connection"

        for model_key in ["gpt4-turbo", "claude", "llama-fast"]:
            try:
                result = self.quick_analysis(test_prompt, model_key)
                results[model_key] = len(result) > 0 and "Error" not in result
                time.sleep(1)
            except Exception:
                results[model_key] = False

        return results


# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 GitHub Models Client")
    parser.add_argument("--analyze", help="Quick betting analysis")
    parser.add_argument("--nhl-analysis", help="NHL game analysis")
    parser.add_argument("--arbitrage-scan", action="store_true", help="Arbitrage scanning")
    parser.add_argument("--consensus", help="Multi-model consensus analysis")
    parser.add_argument("--model", default="gpt4-turbo", help="Specific model to use")
    parser.add_argument("--task-type", help="Task type for intelligent routing")
    parser.add_argument("--health-check", action="store_true", help="Test model connectivity")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        print("🐙 EQ12 GitHub Models Integration Demo")
        print("=====================================")

        client = EQ12GitHubModelsClient()

        if args.health_check:
            print("\n🔄 Testing GitHub Models connectivity...")
            health = client.health_check()
            for model, status in health.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {model}")

        elif args.analyze:
            model = args.model
            if args.task_type:
                print(f"\n🎯 Routed Analysis (Task: {args.task_type}):")
                result = client.model_router(args.task_type, args.analyze)
            else:
                print(f"\n🎯 {model.upper()} Analysis:")
                result = client.quick_analysis(args.analyze, model)
            print(f"Result: {result}")

        elif args.consensus:
            print("\n🎯 Multi-Model Consensus:")
            results = client.multi_model_consensus(args.consensus)
            for model, analysis in results.items():
                print(f"\n{model.upper()}: {analysis[:150]}...")

        elif args.nhl_analysis:
            print(f"\n🏒 NHL Analysis ({args.model}):")
            game_info = {
                "away_team": "Boston Bruins",
                "home_team": "Toronto Maple Leafs",
            }
            result = client.nhl_game_analysis(game_info, args.model)
            print(f"Analysis: {result}")

        elif args.arbitrage_scan:
            print(f"\n💰 Arbitrage Scanner ({args.model}):")
            sample_odds = [
                {
                    "game": "BOS @ TOR",
                    "book": "DraftKings",
                    "home_ml": -140,
                    "away_ml": 150,
                },
                {
                    "game": "BOS @ TOR",
                    "book": "FanDuel",
                    "home_ml": -135,
                    "away_ml": 145,
                },
            ]
            result = client.arbitrage_scanner(sample_odds, args.model)
            print(f"Scan Results: {result}")

        # Show usage statistics
        print("\n📊 Usage Statistics:")
        stats = client.get_usage_stats()
        for key, value in stats.items():
            if key not in ["model_capabilities"]:
                print(f"  {key}: {value}")

        print("\n🎉 GitHub Models integration ready!")
        print("💡 Pro Tip: Use consensus mode for high-stakes bets")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n📝 Setup Instructions:")
        print("1. Ensure GitHub Pro/Team/Enterprise subscription")
        print("2. Create token: https://github.com/settings/tokens")
        print("3. Set GITHUB_TOKEN environment variable")
        print("4. Models available through GitHub's AI infrastructure")
