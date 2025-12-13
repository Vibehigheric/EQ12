# EQ12 Enhanced OpenAI SDK Examples
# Professional Sports Betting AI Integration Examples

"""
This file demonstrates advanced usage patterns for the EQ12 Enhanced OpenAI SDK.
These examples show how to combine expert-level SDK development with
professional sports betting analysis capabilities.
"""

from datetime import datetime, timedelta

# Import our enhanced SDK components
from eq12_enhanced_openai_sdk import (
    AnalysisType,
    BettingMarket,
    EQ12EnhancedOpenAIClient,
    GameData,
)
from eq12_sdk_development_tools import EQ12SDKDevelopmentTools


class EQ12SportsBettingExamples:
    """
    Complete examples demonstrating expert sports betting AI capabilities
    """

    def __init__(self):
        # Initialize enhanced client with full features
        self.client = EQ12EnhancedOpenAIClient(
            enable_usage_tracking=True,
            enable_telegram_integration=False,  # Set to True for production
        )

        # Initialize development tools
        self.dev_tools = EQ12SDKDevelopmentTools()

    def example_1_basic_odds_analysis(self):
        """
        Example 1: Basic odds analysis for value betting

        This demonstrates how to analyze a single game for betting opportunities.
        """
        print("\n" + "=" * 60)
        print("📊 Example 1: Professional Odds Analysis")
        print("=" * 60)

        # Create sample game data (NFL example)
        game = GameData(
            game_id="nfl_2025_week5_kc_buf",
            sport="football",
            home_team="Kansas City Chiefs",
            away_team="Buffalo Bills",
            commence_time=datetime.now() + timedelta(hours=72),  # Game in 3 days
            odds={
                # Moneyline odds
                "chiefs_ml": -165,
                "bills_ml": +145,
                # Point spread
                "chiefs_spread": -3.5,
                "bills_spread": +3.5,
                "spread_odds": -110,
                # Total points
                "over_total": 47.5,
                "under_total": 47.5,
                "total_odds": -110,
                # Book information
                "book": "DraftKings",
                "last_update": datetime.now().isoformat(),
            },
            market_type=BettingMarket.MONEYLINE,
        )

        print(f"🏈 Analyzing: {game.away_team} @ {game.home_team}")
        print(f"   Game ID: {game.game_id}")
        print(f"   Kickoff: {game.commence_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Odds: Chiefs {game.odds['chiefs_ml']}, Bills {game.odds['bills_ml']}")

        try:
            # Perform AI-powered value betting analysis
            recommendation = self.client.sports_betting_analysis(
                game_data=game,
                analysis_type=AnalysisType.VALUE_BETTING,
                custom_context="""
                Additional context for analysis:
                - Chiefs coming off bye week (well-rested)
                - Bills missing WR1 due to injury
                - Weather: Clear, 45°F, no wind
                - Historical H2H: Chiefs 6-4 in last 10 meetings
                - Public betting: 65% on Chiefs
                """,
            )

            print("\n✅ Analysis Complete:")
            print(f"   Recommendation Type: {recommendation.recommendation_type}")
            print(f"   Confidence Level: {recommendation.confidence:.1%}")
            print(f"   Expected Value: +{recommendation.expected_value:.1f}%")
            print(f"   Suggested Stake: ${recommendation.suggested_stake:.2f}")
            print(f"   Risk Assessment: {recommendation.risk_level}")
            print(f"   Reasoning: {recommendation.reasoning[:200]}...")

            return recommendation

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            print("Note: This requires a valid OpenAI API key with available quota")
            return None

    def example_2_multi_game_parlay_optimization(self):
        """
        Example 2: Advanced parlay optimization across multiple games

        This shows how to build optimal parlay combinations using AI analysis.
        """
        print("\n" + "=" * 60)
        print("🎯 Example 2: AI Parlay Optimization")
        print("=" * 60)

        # Create multiple games for parlay consideration
        games = [
            GameData(
                game_id="nfl_game_1",
                sport="football",
                home_team="Kansas City Chiefs",
                away_team="Buffalo Bills",
                commence_time=datetime.now() + timedelta(hours=72),
                odds={"chiefs_ml": -165, "bills_ml": +145},
            ),
            GameData(
                game_id="nfl_game_2",
                sport="football",
                home_team="Dallas Cowboys",
                away_team="New York Giants",
                commence_time=datetime.now() + timedelta(hours=76),
                odds={"cowboys_ml": -280, "giants_ml": +240},
            ),
            GameData(
                game_id="nba_game_1",
                sport="basketball",
                home_team="Los Angeles Lakers",
                away_team="Boston Celtics",
                commence_time=datetime.now() + timedelta(hours=24),
                odds={"lakers_ml": +110, "celtics_ml": -130},
            ),
        ]

        bankroll = 5000.00  # $5,000 bankroll

        print(f"💰 Bankroll: ${bankroll:,.2f}")
        print(f"🎲 Available Games: {len(games)}")

        for i, game in enumerate(games, 1):
            print(f"   Game {i}: {game.away_team} @ {game.home_team}")

        try:
            # AI-powered parlay optimization
            optimized_parlays = self.client.optimize_parlay(
                games=games, bankroll=bankroll, risk_tolerance="medium", max_legs=3
            )

            print("\n✅ Parlay Optimization Complete:")

            for i, parlay in enumerate(optimized_parlays, 1):
                print(f"\n🏆 Recommended Parlay {i}:")
                print(f"   Legs: {len(parlay.legs)}")
                print(f"   Total Odds: +{parlay.total_odds}")
                print(f"   Expected Value: +{parlay.expected_value:.1f}%")
                print(f"   Confidence Score: {parlay.confidence_score:.1%}")
                print(f"   Risk Rating: {parlay.risk_rating}")
                print(
                    f"   Suggested Stake: ${parlay.suggested_stake:.2f} ({parlay.suggested_stake / bankroll:.1%} of bankroll)"
                )
                print(f"   Reasoning: {parlay.reasoning[:150]}...")

                # Show individual legs
                for j, leg in enumerate(parlay.legs, 1):
                    print(f"      Leg {j}: {leg.team} ({leg.bet_type}) - {leg.odds:+d} odds")

            return optimized_parlays

        except Exception as e:
            print(f"❌ Parlay optimization failed: {e}")
            print("Note: This requires a valid OpenAI API key with available quota")
            return []

    def example_3_live_betting_analysis(self):
        """
        Example 3: Real-time live betting analysis with streaming

        This demonstrates streaming analysis for in-game betting decisions.
        """
        print("\n" + "=" * 60)
        print("📡 Example 3: Live Betting Analysis Stream")
        print("=" * 60)

        # Create live game scenario
        live_game = GameData(
            game_id="live_nfl_chiefs_bills",
            sport="football",
            home_team="Kansas City Chiefs",
            away_team="Buffalo Bills",
            commence_time=datetime.now(),  # Game happening now
            odds={
                # Live odds (different from pre-game)
                "live_chiefs_ml": -220,
                "live_bills_ml": +185,
                "live_total_over": 52.5,
                "live_total_under": 52.5,
            },
            live_data={
                "quarter": 2,
                "time_remaining": "5:42",
                "score": {"chiefs": 21, "bills": 14},
                "possession": "bills",
                "down_distance": "3rd & 8",
                "field_position": "bills_35",
                "recent_scoring": [
                    "Chiefs TD (Mahomes 15-yard pass to Kelce)",
                    "Bills FG (42 yards)",
                    "Chiefs TD (Hunt 3-yard rush)",
                    "Bills TD (Allen 25-yard pass to Diggs)",
                ],
                "momentum": "even",
                "weather": {"temp": 45, "wind": 8, "conditions": "clear"},
            },
        )

        print(f"🔴 LIVE GAME: {live_game.away_team} @ {live_game.home_team}")
        print(
            f"   Score: {live_game.live_data['score']['bills']} - {live_game.live_data['score']['chiefs']}"
        )
        print(
            f"   Time: Q{live_game.live_data['quarter']} - {live_game.live_data['time_remaining']}"
        )
        print(
            f"   Situation: {live_game.live_data['down_distance']} at {live_game.live_data['field_position']}"
        )
        print(
            f"   Live Odds: Chiefs {live_game.odds['live_chiefs_ml']}, Bills {live_game.odds['live_bills_ml']}"
        )

        async def run_live_analysis():
            try:
                print("\n📊 Starting live analysis stream...")

                # Stream real-time analysis
                analysis_chunks = []
                async for chunk in self.client.stream_live_analysis(live_game):
                    print(f"📡 Live Update: {chunk[:100]}...")
                    analysis_chunks.append(chunk)

                    # In real implementation, you'd process each chunk for betting decisions
                    if len(analysis_chunks) >= 5:  # Limit for demo
                        break

                full_analysis = "".join(analysis_chunks)
                print(f"\n✅ Live analysis complete ({len(analysis_chunks)} updates received)")
                print(f"📋 Full Analysis: {full_analysis[:300]}...")

                return full_analysis

            except Exception as e:
                print(f"❌ Live analysis failed: {e}")
                print("Note: This requires a valid OpenAI API key with available quota")
                return None

        # Run async live analysis
        try:
            import asyncio

            result = asyncio.run(run_live_analysis())
            return result
        except Exception as e:
            print(f"⚠️ Async execution skipped: {e}")
            print("Live analysis would stream real-time updates in production")
            return None

    def example_4_player_props_analysis(self):
        """
        Example 4: Statistical analysis of player proposition bets

        This shows how to analyze player props using historical data and AI.
        """
        print("\n" + "=" * 60)
        print("🏃 Example 4: Player Props Analysis")
        print("=" * 60)

        # Game context
        game = GameData(
            game_id="nfl_props_analysis",
            sport="football",
            home_team="Kansas City Chiefs",
            away_team="Buffalo Bills",
            commence_time=datetime.now() + timedelta(hours=48),
            odds={"chiefs_ml": -165, "bills_ml": +145},
        )

        # Available player props
        player_props = {
            "patrick_mahomes": {
                "passing_yards": {
                    "over": 275.5,
                    "under": 275.5,
                    "odds_over": -115,
                    "odds_under": -105,
                },
                "passing_touchdowns": {
                    "over": 1.5,
                    "under": 1.5,
                    "odds_over": -140,
                    "odds_under": +120,
                },
                "completions": {"over": 23.5, "under": 23.5, "odds_over": -110, "odds_under": -110},
                "interceptions": {"over": 0.5, "under": 0.5, "odds_over": +165, "odds_under": -200},
                "recent_stats": {
                    "last_5_games_avg": {
                        "yards": 285.4,
                        "tds": 2.2,
                        "completions": 24.8,
                        "ints": 0.4,
                    },
                    "vs_bills_career": {
                        "yards": 302.1,
                        "tds": 2.7,
                        "completions": 26.3,
                        "ints": 0.8,
                    },
                },
            },
            "josh_allen": {
                "passing_yards": {
                    "over": 250.5,
                    "under": 250.5,
                    "odds_over": -105,
                    "odds_under": -115,
                },
                "rushing_yards": {
                    "over": 35.5,
                    "under": 35.5,
                    "odds_over": -110,
                    "odds_under": -110,
                },
                "total_touchdowns": {
                    "over": 1.5,
                    "under": 1.5,
                    "odds_over": -125,
                    "odds_under": +105,
                },
                "recent_stats": {
                    "last_5_games_avg": {"pass_yards": 268.2, "rush_yards": 42.1, "total_tds": 2.4},
                    "vs_chiefs_career": {"pass_yards": 244.6, "rush_yards": 38.9, "total_tds": 1.9},
                },
            },
            "travis_kelce": {
                "receiving_yards": {
                    "over": 65.5,
                    "under": 65.5,
                    "odds_over": -120,
                    "odds_under": +100,
                },
                "receptions": {"over": 5.5, "under": 5.5, "odds_over": -130, "odds_under": +110},
                "touchdowns": {"over": 0.5, "under": 0.5, "odds_over": +145, "odds_under": -175},
                "recent_stats": {
                    "last_5_games_avg": {"yards": 72.8, "receptions": 6.2, "tds": 0.8},
                    "red_zone_targets": 2.1,
                    "target_share": 0.22,
                },
            },
        }

        print(f"🎯 Analyzing player props for: {game.away_team} @ {game.home_team}")
        print(f"📊 Players: {len(player_props)} with prop bets available")

        for player, props in player_props.items():
            non_stats_props = {k: v for k, v in props.items() if k != "recent_stats"}
            print(f"   {player.replace('_', ' ').title()}: {len(non_stats_props)} props")

        try:
            # AI-powered prop analysis
            prop_recommendations = self.client.analyze_player_props(
                game_data=game, player_props=player_props
            )

            print("\n✅ Props Analysis Complete:")
            print(f"📈 Recommendations Generated: {len(prop_recommendations)}")

            for i, rec in enumerate(prop_recommendations, 1):
                print(f"\n🎯 Prop Recommendation {i}:")
                print(f"   Game: {rec.game_id}")
                print(f"   Type: {rec.recommendation_type}")
                print(f"   Confidence: {rec.confidence:.1%}")
                print(f"   Expected Value: +{rec.expected_value:.1f}%")
                print(f"   Suggested Stake: ${rec.suggested_stake:.2f}")
                print(f"   Risk Level: {rec.risk_level}")
                print(f"   Analysis: {rec.reasoning[:200]}...")

            return prop_recommendations

        except Exception as e:
            print(f"❌ Props analysis failed: {e}")
            print("Note: This requires a valid OpenAI API key with available quota")
            return []

    def example_5_sdk_development_workflow(self):
        """
        Example 5: Expert SDK development and customization workflow

        This demonstrates how to modify and enhance the OpenAI SDK for sports betting.
        """
        print("\n" + "=" * 60)
        print("🔧 Example 5: Expert SDK Development Workflow")
        print("=" * 60)

        print("👨‍💻 SDK Development Capabilities:")
        print("   - Clone official OpenAI Python SDK repository")
        print("   - Apply custom EQ12 sports betting extensions")
        print("   - Install in development mode for immediate changes")
        print("   - Performance benchmarking and optimization")
        print("   - Build custom distributions")

        # Get current SDK development status
        status = self.dev_tools.get_sdk_status()

        print("\n📊 Current SDK Development Status:")
        print(f"   Workspace Directory: {status['workspace_directory']}")
        print(f"   Repository Cloned: {'✅' if status['repository_cloned'] else '❌'}")
        print(f"   Current Branch: {status.get('current_branch', 'Not available')}")
        print(f"   Local Modifications: {'✅' if status.get('local_modifications') else '❌'}")
        print(f"   EQ12 Patches Applied: {'✅' if status['eq12_patches_applied'] else '❌'}")
        print(f"   Git Available: {'✅' if status['git_available'] else '❌'}")
        print(f"   Last Benchmark: {status.get('last_benchmark', 'None')}")

        if not status["repository_cloned"]:
            print("\n🚀 To start SDK development:")
            print("   1. Run: python eq12_sdk_development_tools.py")
            print("   2. Or use VS Code task: 'EQ12: Initialize SDK Development Environment'")

        else:
            print("\n✅ SDK development environment ready!")
            print(f"   - Modify code in: {status['workspace_directory']}/openai-python/src/openai/")
            print("   - Changes reflected immediately (development install)")
            print("   - Run benchmarks to test performance")

        # Show example of what you can do with SDK access
        print("\n🔬 Example SDK Customizations Available:")
        print("   - Add sports-specific prompt templates")
        print("   - Implement custom rate limiting for betting operations")
        print("   - Add automatic retry logic for live betting")
        print("   - Integrate with EQ12 logging and alerting systems")
        print("   - Optimize token usage for cost-effective operations")
        print("   - Add streaming improvements for real-time analysis")

        return status

    def example_6_performance_optimization(self):
        """
        Example 6: Performance monitoring and optimization

        This shows how to optimize SDK performance for high-frequency sports betting.
        """
        print("\n" + "=" * 60)
        print("⚡ Example 6: Performance Optimization")
        print("=" * 60)

        # Get current performance metrics
        metrics = self.client.get_performance_metrics()

        print("📊 Current Performance Metrics:")
        if metrics.get("total_requests", 0) > 0:
            print(f"   Total API Requests: {metrics['total_requests']}")
            print(f"   Average Response Time: {metrics['avg_request_time']:.3f}s")
            print(f"   Fastest Response: {metrics['min_request_time']:.3f}s")
            print(f"   Slowest Response: {metrics['max_request_time']:.3f}s")

            if self.client.usage_tracker:
                usage = metrics["usage_stats"]
                print(f"   Total Tokens Used: {usage['total_tokens']:,}")
                print(f"   Estimated Cost: ${usage['cost_estimate']:.4f}")
                print(f"   Models Used: {usage['models_used']}")

        else:
            print("   No requests made yet in this session")

        print("\n⚡ Performance Optimization Strategies:")
        print("   🎯 Model Selection:")
        print("      - Use gpt-4o-mini for quick odds calculations")
        print("      - Use gpt-4o for complex parlay optimization")
        print("      - Use specialized models for different analysis types")

        print("   🔄 Request Optimization:")
        print("      - Batch multiple games in single requests")
        print("      - Use streaming for real-time analysis")
        print("      - Implement smart caching for repeated queries")

        print("   💰 Cost Management:")
        print("      - Monitor token usage with built-in tracking")
        print("      - Use temperature tuning for consistency")
        print("      - Implement usage alerts and limits")

        print("   ⚡ Speed Improvements:")
        print("      - Async requests for parallel processing")
        print("      - Connection pooling and keep-alive")
        print("      - Local SDK modifications for edge cases")

        # Example of running a quick performance test
        if self.client.usage_tracker:
            session_stats = self.client.usage_tracker.get_session_stats()
            print("\n📈 Session Statistics:")
            print(f"   Session Duration: {session_stats['session_duration']:.1f}s")
            print(f"   Requests Made: {session_stats['requests']}")
            print(f"   Average Tokens per Request: {session_stats['avg_tokens_per_request']:.1f}")
            print(f"   Analysis Types Used: {list(session_stats['analysis_types'].keys())}")

        return metrics


def run_all_examples():
    """
    Run all examples to demonstrate the complete EQ12 Enhanced OpenAI SDK capabilities
    """
    print("🚀 EQ12 Enhanced OpenAI SDK - Complete Examples Suite")
    print("=" * 80)
    print("Demonstrating expert SDK development + professional sports betting AI")
    print("=" * 80)

    # Initialize examples class
    examples = EQ12SportsBettingExamples()

    results = {}

    # Run all examples
    try:
        print("\n🔄 Running Example Suite...")

        # Example 1: Basic odds analysis
        results["odds_analysis"] = examples.example_1_basic_odds_analysis()

        # Example 2: Parlay optimization
        results["parlay_optimization"] = examples.example_2_multi_game_parlay_optimization()

        # Example 3: Live betting (async)
        results["live_betting"] = examples.example_3_live_betting_analysis()

        # Example 4: Player props
        results["player_props"] = examples.example_4_player_props_analysis()

        # Example 5: SDK development
        results["sdk_development"] = examples.example_5_sdk_development_workflow()

        # Example 6: Performance optimization
        results["performance"] = examples.example_6_performance_optimization()

        # Summary
        print("\n" + "=" * 80)
        print("🎉 Example Suite Complete!")
        print("=" * 80)

        successful_examples = sum(1 for result in results.values() if result is not None)
        total_examples = len(results)

        print(f"✅ Examples Completed: {successful_examples}/{total_examples}")
        print("📊 Results Summary:")

        for example_name, result in results.items():
            status = "✅ Success" if result is not None else "⚠️  Skipped (API key required)"
            print(f"   {example_name.replace('_', ' ').title()}: {status}")

        if successful_examples > 0:
            print("\n🎯 Key Capabilities Demonstrated:")
            print("   - Expert-level OpenAI SDK development and customization")
            print("   - Professional sports betting AI analysis")
            print("   - Advanced parlay optimization algorithms")
            print("   - Real-time live betting analysis")
            print("   - Statistical player props analysis")
            print("   - Performance monitoring and optimization")
            print("   - Complete EQ12 system integration")

        # Cleanup
        if hasattr(examples.client, "cleanup_session"):
            examples.client.cleanup_session()

        return results

    except Exception as e:
        print(f"❌ Example suite error: {e}")
        return results


if __name__ == "__main__":
    # Run the complete example suite
    results = run_all_examples()

    print("\n📚 For more information:")
    print("   - Complete Guide: EQ12_ENHANCED_OPENAI_GUIDE.md")
    print("   - SDK Source: eq12_enhanced_openai_sdk.py")
    print("   - Development Tools: eq12_sdk_development_tools.py")
    print("   - VS Code Tasks: Use Ctrl+Shift+P → 'Tasks: Run Task'")
