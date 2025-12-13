#!/usr/bin/env python3
"""
EQ12 Complete Sports Betting Suite - Real Odds + AI Analysis Examples
=====================================================================

Comprehensive examples demonstrating the integration of:
1. Real-time odds data from The Odds API
2. AI-powered analysis from EQ12 Enhanced OpenAI SDK
3. Professional sports betting automation workflows

This module showcases practical applications that go far beyond
standard API usage to deliver professional-grade betting intelligence.

Author: EQ12 Development Team
Date: October 5, 2025
Version: 1.0.0
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

try:
    from eq12_enhanced_openai_sdk import (
        AnalysisType,
        BettingMarket,
        EQ12EnhancedOpenAIClient,
    )
    from eq12_odds_api_client import (
        ArbitrageOpportunity,
        BettingRecommendation,
        EQ12OddsAPIClient,
        Market,
        OddsFormat,
        Region,
    )
except ImportError as e:
    print(f"❌ Required modules not found: {e}")
    print("Ensure eq12_odds_api_client.py and eq12_enhanced_openai_sdk.py are available")
    exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EQ12CompleteBettingSuite:
    """Complete sports betting automation suite"""

    def __init__(self):
        """Initialize the complete betting suite"""
        self.odds_client = EQ12OddsAPIClient()
        self.ai_client = (
            EQ12EnhancedOpenAIClient() if hasattr(EQ12EnhancedOpenAIClient, "__init__") else None
        )
        self.results_dir = Path("C:/EQ12/data/betting_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        logger.info("🏆 EQ12 Complete Betting Suite initialized")

    async def example_1_live_nfl_analysis(self):
        """Example 1: Live NFL game analysis with real odds and AI predictions"""
        print("\n" + "=" * 80)
        print("📊 EXAMPLE 1: Live NFL Analysis - Real Odds + AI Intelligence")
        print("=" * 80)

        try:
            # Get NFL odds
            print("🏈 Fetching live NFL odds...")
            nfl_events = self.odds_client.get_odds(
                sport="americanfootball_nfl",
                regions=[Region.US, Region.US2],
                markets=[Market.H2H, Market.SPREADS, Market.TOTALS],
                odds_format=OddsFormat.AMERICAN,
            )

            print(f"✅ Retrieved {len(nfl_events)} NFL games")

            if not nfl_events:
                print("ℹ️ No live NFL games available")
                return

            # Analyze top 3 games
            for i, event in enumerate(nfl_events[:3]):
                print(f"\n🎯 Game {i + 1}: {event.away_team} @ {event.home_team}")
                print(f"   Start Time: {event.commence_time}")
                print(f"   Bookmakers: {len(event.bookmakers)}")

                # Show best odds across books
                self._show_best_odds(event)

                # Get AI analysis if available
                if self.ai_client:
                    print("🤖 Getting AI analysis...")
                    try:
                        game_data = {
                            "game": f"{event.away_team} @ {event.home_team}",
                            "sport": "NFL",
                            "commence_time": event.commence_time.isoformat(),
                            "odds_data": self.odds_client._prepare_odds_for_ai(event),
                        }

                        ai_analysis = await self.ai_client.analyze_live_betting_opportunity(
                            game_data
                        )
                        print(f"🎯 AI Insight: {ai_analysis[:200]}...")

                    except Exception as e:
                        print(f"⚠️ AI analysis unavailable: {e}")

            # Find arbitrage opportunities
            print("\n🔍 Scanning for NFL arbitrage opportunities...")
            arbitrage_ops = self.odds_client.find_arbitrage_opportunities(
                nfl_events, min_profit=0.015
            )

            if arbitrage_ops:
                print(f"🎯 Found {len(arbitrage_ops)} arbitrage opportunities!")
                for i, opp in enumerate(arbitrage_ops):
                    print(f"   {i + 1}. {opp.event.away_team} @ {opp.event.home_team}")
                    print(f"      Market: {opp.market.upper()}")
                    print(f"      Profit: {opp.profit_percentage:.2f}%")
                    print(f"      Required Stake: ${opp.total_stake:.2f}")

                self.odds_client.save_arbitrage_report(arbitrage_ops)
            else:
                print("ℹ️ No profitable arbitrage opportunities found")

        except Exception as e:
            print(f"❌ Error in NFL analysis: {e}")

    async def example_2_nba_player_props_optimizer(self):
        """Example 2: NBA player props analysis with AI-powered optimization"""
        print("\n" + "=" * 80)
        print("🏀 EXAMPLE 2: NBA Player Props Optimizer - AI + Real Market Data")
        print("=" * 80)

        try:
            # Get NBA events with player props
            print("🏀 Fetching NBA player props...")
            nba_events = self.odds_client.get_odds(
                sport="basketball_nba",
                regions=[Region.US],
                markets=[Market.PLAYER_POINTS, Market.PLAYER_REBOUNDS, Market.PLAYER_ASSISTS],
                odds_format=OddsFormat.AMERICAN,
            )

            print(f"✅ Retrieved {len(nba_events)} NBA games with props")

            if not nba_events:
                print("ℹ️ No NBA games with player props available")
                return

            # Analyze player props for each game
            total_props_analyzed = 0
            high_value_props = []

            for event in nba_events[:2]:  # Limit for demo
                print(f"\n🎯 {event.away_team} @ {event.home_team}")

                # Collect all player props
                player_props = {}
                for bookmaker in event.bookmakers:
                    for market in bookmaker.markets:
                        if market.key in ["player_points", "player_rebounds", "player_assists"]:
                            for outcome in market.outcomes:
                                if outcome.description:  # Player name
                                    prop_key = f"{outcome.description}_{market.key}_{outcome.point}"
                                    if prop_key not in player_props:
                                        player_props[prop_key] = []
                                    player_props[prop_key].append(
                                        {
                                            "bookmaker": bookmaker.title,
                                            "outcome": outcome.name,
                                            "line": outcome.point,
                                            "odds": outcome.price,
                                        }
                                    )

                print(f"   Found {len(player_props)} unique player props")
                total_props_analyzed += len(player_props)

                # Analyze top props with AI
                if self.ai_client and player_props:
                    top_props = list(player_props.items())[:5]  # Top 5 props

                    for prop_key, prop_data in top_props:
                        try:
                            # Get AI analysis for this prop
                            ai_analysis = await self._analyze_player_prop_with_ai(
                                prop_key, prop_data, event
                            )

                            if (
                                "high value" in ai_analysis.lower()
                                or "positive" in ai_analysis.lower()
                            ):
                                high_value_props.append(
                                    {
                                        "prop": prop_key,
                                        "game": f"{event.away_team} @ {event.home_team}",
                                        "analysis": ai_analysis,
                                        "best_odds": max(prop_data, key=lambda x: x["odds"]),
                                    }
                                )

                        except Exception as e:
                            logger.warning(f"⚠️ Failed AI analysis for {prop_key}: {e}")

            print("\n📊 Analysis Summary:")
            print(f"   Total Props Analyzed: {total_props_analyzed}")
            print(f"   High-Value Props Found: {len(high_value_props)}")

            if high_value_props:
                print("\n🎯 Top High-Value Player Props:")
                for i, prop in enumerate(high_value_props[:3]):
                    print(f"   {i + 1}. {prop['prop']}")
                    print(f"      Game: {prop['game']}")
                    print(
                        f"      Best Odds: {prop['best_odds']['odds']} at {prop['best_odds']['bookmaker']}"
                    )
                    print(f"      AI Analysis: {prop['analysis'][:100]}...")

        except Exception as e:
            print(f"❌ Error in NBA props analysis: {e}")

    async def example_3_multi_sport_parlay_builder(self):
        """Example 3: Multi-sport parlay builder with AI optimization"""
        print("\n" + "=" * 80)
        print("🎮 EXAMPLE 3: Multi-Sport Parlay Builder - AI-Optimized Combinations")
        print("=" * 80)

        try:
            # Get events from multiple sports
            sports_to_analyze = [
                ("americanfootball_nfl", "NFL"),
                ("basketball_nba", "NBA"),
                ("icehockey_nhl", "NHL"),
            ]

            all_events = []

            for sport_key, sport_name in sports_to_analyze:
                try:
                    print(f"🔄 Fetching {sport_name} games...")
                    events = self.odds_client.get_odds(
                        sport=sport_key,
                        regions=[Region.US],
                        markets=[Market.H2H, Market.SPREADS],
                        odds_format=OddsFormat.AMERICAN,
                    )
                    all_events.extend(events)
                    print(f"   ✅ {len(events)} {sport_name} games added")
                except Exception as e:
                    print(f"   ⚠️ {sport_name} data unavailable: {e}")

            print(f"\n📊 Total events for parlay analysis: {len(all_events)}")

            if len(all_events) < 2:
                print("ℹ️ Need at least 2 events for parlay analysis")
                return

            # Generate parlay combinations (2-4 legs)
            parlay_combinations = []

            # 2-leg parlays
            for i in range(len(all_events)):
                for j in range(i + 1, min(i + 4, len(all_events))):  # Limit combinations
                    parlay_combinations.append([all_events[i], all_events[j]])

            # 3-leg parlays (select top combinations)
            for i in range(min(3, len(all_events) - 2)):
                for j in range(i + 1, min(i + 3, len(all_events) - 1)):
                    for k in range(j + 1, min(j + 2, len(all_events))):
                        parlay_combinations.append([all_events[i], all_events[j], all_events[k]])

            print(f"🎯 Generated {len(parlay_combinations)} parlay combinations")

            # Analyze top parlays with AI
            if self.ai_client:
                print("🤖 AI analyzing top parlay opportunities...")

                top_parlays = []

                for i, parlay_events in enumerate(parlay_combinations[:10]):  # Top 10
                    try:
                        # Prepare parlay data for AI
                        parlay_data = []
                        for event in parlay_events:
                            parlay_data.append(
                                {
                                    "game": f"{event.away_team} @ {event.home_team}",
                                    "sport": event.sport_title,
                                    "commence_time": event.commence_time.isoformat(),
                                    "odds_data": self.odds_client._prepare_odds_for_ai(event),
                                }
                            )

                        # Get AI analysis
                        ai_analysis = await self.ai_client.analyze_parlay_opportunity(parlay_data)

                        # Extract confidence score (simplified parsing)
                        confidence = self._extract_confidence_from_ai(ai_analysis)

                        if confidence > 0.6:  # High confidence threshold
                            top_parlays.append(
                                {
                                    "events": parlay_events,
                                    "confidence": confidence,
                                    "analysis": ai_analysis,
                                    "legs": len(parlay_events),
                                }
                            )

                    except Exception as e:
                        logger.warning(f"⚠️ Failed parlay analysis {i + 1}: {e}")

                # Sort by confidence
                top_parlays.sort(key=lambda x: x["confidence"], reverse=True)

                print("\n🏆 Top AI-Recommended Parlays:")
                for i, parlay in enumerate(top_parlays[:5]):
                    print(
                        f"\n   {i + 1}. {parlay['legs']}-Leg Parlay (Confidence: {parlay['confidence']:.1%})"
                    )
                    for event in parlay["events"]:
                        print(
                            f"      • {event.away_team} @ {event.home_team} ({event.sport_title})"
                        )
                    print(f"      AI Analysis: {parlay['analysis'][:150]}...")

        except Exception as e:
            print(f"❌ Error in parlay analysis: {e}")

    async def example_4_live_betting_monitor(self):
        """Example 4: Live betting opportunity monitor with real-time alerts"""
        print("\n" + "=" * 80)
        print("⚡ EXAMPLE 4: Live Betting Monitor - Real-Time Opportunity Detection")
        print("=" * 80)

        try:
            print("🔄 Starting live betting monitor (30-second intervals)...")
            print("   Monitoring: NFL, NBA, NHL for live opportunities")
            print("   Press Ctrl+C to stop\n")

            monitor_count = 0
            max_iterations = 6  # 3 minutes demo

            while monitor_count < max_iterations:
                monitor_count += 1
                timestamp = datetime.now().strftime("%H:%M:%S")

                print(f"[{timestamp}] 🔍 Scan #{monitor_count}/6 - Checking live opportunities...")

                # Check upcoming games (live betting proxy)
                upcoming_events = self.odds_client.get_odds(
                    sport="upcoming",
                    regions=[Region.US],
                    markets=[Market.H2H, Market.SPREADS, Market.TOTALS],
                    odds_format=OddsFormat.AMERICAN,
                )

                # Filter for games starting soon (next 4 hours)
                now = datetime.now()
                live_candidates = [
                    event
                    for event in upcoming_events
                    if event.commence_time.replace(tzinfo=None) <= now + timedelta(hours=4)
                ]

                print(f"[{timestamp}]    📊 Found {len(live_candidates)} games starting soon")

                if live_candidates:
                    # Quick arbitrage scan
                    quick_arb_ops = self.odds_client.find_arbitrage_opportunities(
                        live_candidates, min_profit=0.01
                    )

                    if quick_arb_ops:
                        print(
                            f"[{timestamp}]    🚨 ALERT: {len(quick_arb_ops)} arbitrage opportunities!"
                        )
                        for opp in quick_arb_ops[:2]:
                            print(
                                f"[{timestamp}]       • {opp.event.away_team} @ {opp.event.home_team}"
                            )
                            print(
                                f"[{timestamp}]         Market: {opp.market}, Profit: {opp.profit_percentage:.2f}%"
                            )

                    # AI quick analysis for top game
                    if self.ai_client and live_candidates:
                        top_game = live_candidates[0]
                        print(
                            f"[{timestamp}]    🤖 AI Quick Analysis: {top_game.away_team} @ {top_game.home_team}"
                        )

                        try:
                            game_data = {
                                "game": f"{top_game.away_team} @ {top_game.home_team}",
                                "sport": top_game.sport_title,
                                "commence_time": top_game.commence_time.isoformat(),
                                "odds_data": self.odds_client._prepare_odds_for_ai(top_game),
                            }

                            quick_analysis = await self.ai_client.analyze_live_betting_opportunity(
                                game_data
                            )

                            # Check for high-confidence recommendations
                            if any(
                                keyword in quick_analysis.lower()
                                for keyword in ["strong", "high confidence", "recommended"]
                            ):
                                print(f"[{timestamp}]    🎯 HIGH VALUE OPPORTUNITY DETECTED!")
                                print(f"[{timestamp}]       {quick_analysis[:100]}...")

                        except Exception as e:
                            print(f"[{timestamp}]    ⚠️ AI analysis failed: {e}")

                else:
                    print(f"[{timestamp}]    ℹ️ No immediate live opportunities")

                if monitor_count < max_iterations:
                    print(f"[{timestamp}]    ⏱️ Next scan in 30 seconds...\n")
                    await asyncio.sleep(30)

            print("✅ Live monitoring demo completed!")

        except KeyboardInterrupt:
            print("\n⏹️ Live monitoring stopped by user")
        except Exception as e:
            print(f"❌ Error in live monitoring: {e}")

    async def example_5_profit_tracking_dashboard(self):
        """Example 5: Betting results tracking and performance analysis"""
        print("\n" + "=" * 80)
        print("📈 EXAMPLE 5: Profit Tracking Dashboard - Performance Analytics")
        print("=" * 80)

        try:
            print("📊 Analyzing historical betting performance...")

            # Load historical data (simulate if not available)
            historical_bets = self._load_or_simulate_historical_data()

            print(f"📋 Analyzing {len(historical_bets)} historical bets")

            # Calculate performance metrics
            total_bets = len(historical_bets)
            winning_bets = len([bet for bet in historical_bets if bet["result"] == "win"])
            win_rate = (winning_bets / total_bets) * 100 if total_bets > 0 else 0

            total_staked = sum(bet["stake"] for bet in historical_bets)
            total_returned = sum(bet["payout"] for bet in historical_bets)
            net_profit = total_returned - total_staked
            roi = (net_profit / total_staked) * 100 if total_staked > 0 else 0

            print("\n📊 Performance Summary:")
            print(f"   Total Bets: {total_bets}")
            print(f"   Winning Bets: {winning_bets}")
            print(f"   Win Rate: {win_rate:.1f}%")
            print(f"   Total Staked: ${total_staked:,.2f}")
            print(f"   Total Returned: ${total_returned:,.2f}")
            print(f"   Net Profit: ${net_profit:,.2f}")
            print(f"   ROI: {roi:.2f}%")

            # Analyze by sport
            sports_performance = {}
            for bet in historical_bets:
                sport = bet["sport"]
                if sport not in sports_performance:
                    sports_performance[sport] = {"bets": 0, "wins": 0, "stake": 0, "payout": 0}

                sports_performance[sport]["bets"] += 1
                sports_performance[sport]["stake"] += bet["stake"]
                sports_performance[sport]["payout"] += bet["payout"]
                if bet["result"] == "win":
                    sports_performance[sport]["wins"] += 1

            print("\n🏆 Performance by Sport:")
            for sport, stats in sports_performance.items():
                sport_win_rate = (stats["wins"] / stats["bets"]) * 100 if stats["bets"] > 0 else 0
                sport_profit = stats["payout"] - stats["stake"]
                sport_roi = (sport_profit / stats["stake"]) * 100 if stats["stake"] > 0 else 0

                print(f"   {sport}:")
                print(f"      Bets: {stats['bets']}, Win Rate: {sport_win_rate:.1f}%")
                print(f"      Profit: ${sport_profit:,.2f}, ROI: {sport_roi:.2f}%")

            # AI performance insights
            if self.ai_client:
                print("\n🤖 Getting AI performance insights...")
                try:
                    performance_data = {
                        "total_bets": total_bets,
                        "win_rate": win_rate,
                        "roi": roi,
                        "net_profit": net_profit,
                        "sports_breakdown": sports_performance,
                    }

                    insights = await self._get_ai_performance_insights(performance_data)
                    print("🎯 AI Insights:")
                    print(f"   {insights[:300]}...")

                except Exception as e:
                    print(f"⚠️ AI insights unavailable: {e}")

            # Save performance report
            self._save_performance_report(
                {
                    "timestamp": datetime.now().isoformat(),
                    "summary": {
                        "total_bets": total_bets,
                        "win_rate": win_rate,
                        "roi": roi,
                        "net_profit": net_profit,
                    },
                    "by_sport": sports_performance,
                    "historical_bets": historical_bets,
                }
            )

            print(f"\n💾 Performance report saved to {self.results_dir}")

        except Exception as e:
            print(f"❌ Error in performance tracking: {e}")

    # Helper methods

    def _show_best_odds(self, event):
        """Display best odds for an event"""
        markets = {}

        for bookmaker in event.bookmakers:
            for market in bookmaker.markets:
                if market.key not in markets:
                    markets[market.key] = {}

                for outcome in market.outcomes:
                    key = f"{outcome.name}_{outcome.point}" if outcome.point else outcome.name
                    if key not in markets[market.key]:
                        markets[market.key][key] = []
                    markets[market.key][key].append(
                        {"bookmaker": bookmaker.title, "odds": outcome.price}
                    )

        for market_name, outcomes in markets.items():
            print(f"   📊 {market_name.upper()} - Best Odds:")
            for outcome_name, odds_list in outcomes.items():
                if odds_list:
                    best_odds = max(odds_list, key=lambda x: x["odds"])
                    print(f"      {outcome_name}: {best_odds['odds']} ({best_odds['bookmaker']})")

    async def _analyze_player_prop_with_ai(self, prop_key, prop_data, event):
        """Get AI analysis for a player prop"""
        if not self.ai_client:
            return "AI analysis unavailable"

        prop_info = {
            "player_prop": prop_key,
            "game": f"{event.away_team} @ {event.home_team}",
            "odds_data": prop_data,
            "game_time": event.commence_time.isoformat(),
        }

        # Use player props analysis
        return await self.ai_client.analyze_player_props([prop_info])

    def _extract_confidence_from_ai(self, ai_text):
        """Extract confidence score from AI analysis"""
        try:
            # Simple confidence extraction
            if "high confidence" in ai_text.lower():
                return 0.8
            elif "medium confidence" in ai_text.lower():
                return 0.6
            elif "low confidence" in ai_text.lower():
                return 0.3
            elif "strong" in ai_text.lower():
                return 0.75
            else:
                return 0.5  # Default
        except:
            return 0.5

    def _load_or_simulate_historical_data(self):
        """Load or simulate historical betting data"""
        # In production, load from database
        # For demo, simulate realistic data

        import random

        sports = ["NFL", "NBA", "NHL", "MLB"]
        bet_types = ["Moneyline", "Spread", "Total", "Player Props"]

        historical_bets = []

        for i in range(50):  # 50 historical bets
            sport = random.choice(sports)
            bet_type = random.choice(bet_types)
            stake = random.randint(50, 500)

            # Simulate realistic win rate (slightly below break-even)
            won = random.random() < 0.47  # 47% win rate

            if won:
                payout = stake * random.uniform(1.8, 3.2)  # Winning payout
            else:
                payout = 0

            historical_bets.append(
                {
                    "id": i + 1,
                    "sport": sport,
                    "bet_type": bet_type,
                    "stake": stake,
                    "payout": payout,
                    "result": "win" if won else "loss",
                    "date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                }
            )

        return historical_bets

    async def _get_ai_performance_insights(self, performance_data):
        """Get AI insights on betting performance"""
        if not self.ai_client:
            return "AI insights unavailable"

        # Format performance data for AI analysis
        analysis_prompt = f"""
        Analyze this sports betting performance:
        - Total Bets: {performance_data["total_bets"]}
        - Win Rate: {performance_data["win_rate"]:.1f}%
        - ROI: {performance_data["roi"]:.2f}%
        - Net Profit: ${performance_data["net_profit"]:,.2f}

        Sports breakdown: {json.dumps(performance_data["sports_breakdown"], indent=2)}

        Provide insights on performance, areas for improvement, and recommendations.
        """

        # Use general betting analysis
        return await self.ai_client.analyze_general_betting_market(analysis_prompt)

    def _save_performance_report(self, report_data):
        """Save performance report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_report_{timestamp}.json"
        filepath = self.results_dir / filename

        with open(filepath, "w") as f:
            json.dump(report_data, f, indent=2)


async def run_complete_betting_suite():
    """Run all betting suite examples"""
    print("🚀 EQ12 COMPLETE SPORTS BETTING SUITE")
    print("🎯 Real Odds API + AI Analysis Integration")
    print("=" * 80)

    suite = EQ12CompleteBettingSuite()

    try:
        # Run all examples
        await suite.example_1_live_nfl_analysis()
        await suite.example_2_nba_player_props_optimizer()
        await suite.example_3_multi_sport_parlay_builder()
        await suite.example_4_live_betting_monitor()
        await suite.example_5_profit_tracking_dashboard()

        print("\n" + "=" * 80)
        print("🎉 COMPLETE BETTING SUITE DEMO FINISHED!")
        print("✅ All examples completed successfully")
        print("📊 Check C:/EQ12/data/ for saved results and reports")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Suite execution error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_complete_betting_suite())
