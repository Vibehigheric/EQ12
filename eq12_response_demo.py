#!/usr/bin/env python3
"""
EQ12 Model Response System - Interactive Demo
Demonstrates all major capabilities of the comprehensive response system
"""

import asyncio
import json
import os
from typing import Any

# Demo banner
BANNER = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 EQ12 MODEL RESPONSE SYSTEM DEMO 🚀                    ║
║                                                                               ║
║  Comprehensive AI-Powered Sports Betting Analysis Platform                    ║
║  • Advanced Parlay Optimization with Correlation Analysis                     ║
║  • Real-time Live Betting with Momentum Detection                            ║
║  • NFL Slate Analysis with Weather & Injury Integration                      ║
║  • NBA Player Prop            print(
                f"\\nUsage: {usage.get('prompt_tokens', 0)} prompt + {usage.get('completion_tokens', 0)} completion = {usage.get('total_tokens', 0)} total tokens"
            )ith Usage Rate Optimization                             ║
║  • Sharp Steam Detection & Professional Following                            ║
║  • Kelly Criterion Portfolio Management                                       ║
║                                                                               ║
║  Powered by OpenAI Responses API with Full Tool Integration                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

# Sample data for demonstrations
DEMO_DATA = {
    "parlay_legs": [
        {
            "game": "Lakers vs Warriors",
            "market": "spread",
            "selection": "Lakers -3.5",
            "odds": -110,
            "probability": 0.55,
        },
        {
            "game": "Lakers vs Warriors",
            "market": "total",
            "selection": "Over 225.5",
            "odds": -105,
            "probability": 0.52,
        },
        {
            "game": "Celtics vs Heat",
            "market": "moneyline",
            "selection": "Celtics",
            "odds": -150,
            "probability": 0.60,
        },
    ],
    "nfl_games": [
        {
            "home": "Patriots",
            "away": "Bills",
            "spread": "Bills -3.5",
            "total": 44.5,
            "weather": {"wind": "18mph", "temp": "28°F", "precipitation": "None"},
        },
        {
            "home": "Cowboys",
            "away": "Eagles",
            "spread": "Eagles -7",
            "total": 51.5,
            "weather": {"wind": "5mph", "temp": "45°F", "precipitation": "Light rain"},
        },
        {
            "home": "Chiefs",
            "away": "Broncos",
            "spread": "Chiefs -10.5",
            "total": 48.5,
            "weather": {"wind": "12mph", "temp": "35°F", "precipitation": "None"},
        },
    ],
    "nba_props": [
        {
            "player": "LeBron James",
            "team": "Lakers",
            "market": "points",
            "line": 26.5,
            "over_odds": -110,
            "under_odds": -110,
            "recent_avg": 28.2,
            "usage_rate": 31.5,
        },
        {
            "player": "Stephen Curry",
            "team": "Warriors",
            "market": "threes_made",
            "line": 4.5,
            "over_odds": +105,
            "under_odds": -125,
            "recent_avg": 5.1,
            "attempts_per_game": 11.8,
        },
        {
            "player": "Jayson Tatum",
            "team": "Celtics",
            "market": "rebounds",
            "line": 8.5,
            "over_odds": -105,
            "under_odds": -115,
            "recent_avg": 8.8,
            "matchup_advantage": "Favorable vs Heat frontcourt",
        },
    ],
    "line_movements": [
        {
            "game": "Patriots vs Bills",
            "market": "spread",
            "opening": "Bills -2.5",
            "current": "Bills -3.5",
            "movement": 1.0,
            "public_percentage": 35,
            "sharp_indicator": True,
            "timestamp": "2024-01-01T10:00:00Z",
        },
        {
            "game": "Cowboys vs Eagles",
            "market": "total",
            "opening": 52.5,
            "current": 51.5,
            "movement": -1.0,
            "public_percentage": 72,
            "volume_spike": True,
            "timestamp": "2024-01-01T10:15:00Z",
        },
    ],
    "portfolio_positions": [
        {
            "id": "pos_001",
            "game": "Lakers vs Warriors",
            "selection": "Lakers ML",
            "stake": 200,
            "odds": -130,
            "max_win": 154,
            "correlation_group": "NBA_West",
        },
        {
            "id": "pos_002",
            "game": "Patriots vs Bills",
            "selection": "Under 44.5",
            "stake": 150,
            "odds": -110,
            "max_win": 136,
            "correlation_group": "NFL_AFC_East",
        },
    ],
    "new_opportunities": [
        {
            "id": "opp_001",
            "game": "Celtics vs Heat",
            "selection": "Celtics -4.5",
            "odds": -108,
            "estimated_edge": 0.065,
            "confidence": "HIGH",
            "correlation_group": "NBA_East",
        },
        {
            "id": "opp_002",
            "game": "Chiefs vs Broncos",
            "selection": "Over 48.5",
            "odds": +102,
            "estimated_edge": 0.041,
            "confidence": "MEDIUM",
            "correlation_group": "NFL_AFC_West",
        },
    ],
}


class EQ12ResponseDemo:
    """Interactive demo of EQ12 Model Response System"""

    def __init__(self):
        self.api_available = False
        self.system = None
        self.demo_mode = True  # Enable demo mode for testing without API

    async def initialize(self):
        """Initialize the response system"""
        print("🔧 Initializing EQ12 Model Response System...")

        try:
            # Check if we have API access
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("⚠️  No OpenAI API key found. Running in demo mode.")
                self.demo_mode = True
            else:
                print("✅ API key found. Attempting to initialize live system...")

                # Try to import and initialize
                try:
                    from eq12_unified_responses import EQ12UnifiedResponseSystem

                    self.system = EQ12UnifiedResponseSystem()

                    # Test health
                    health = await self.system.health_check()
                    if health.get("status") == "healthy":
                        self.api_available = True
                        self.demo_mode = False
                        print("✅ EQ12 Response System fully operational!")
                    else:
                        print(f"⚠️  System health check failed: {health.get('status')}")
                        self.demo_mode = True

                except ImportError as e:
                    print(f"⚠️  Could not import response modules: {e}")
                    self.demo_mode = True

        except Exception as e:
            print(f"⚠️  Initialization failed: {e}")
            self.demo_mode = True

        if self.demo_mode:
            print("🎭 Running in demo mode with simulated responses.")

        print()

    async def run_demo(self):
        """Run the interactive demo"""
        print(BANNER)
        await self.initialize()

        while True:
            print("\n" + "=" * 80)
            print("🎯 EQ12 RESPONSE SYSTEM - MAIN MENU")
            print("=" * 80)
            print("1. 🎲 Advanced Parlay Analysis")
            print("2. 🏈 NFL Sunday Slate Analysis")
            print("3. 🏀 NBA Player Props Analysis")
            print("4. ⚡ Live Betting Momentum Analysis")
            print("5. 🔍 Sharp Steam Detection")
            print("6. 📊 Kelly Criterion Portfolio Optimization")
            print("7. 🔄 Batch Process Multiple Opportunities")
            print("8. 📺 Live Monitoring Session Demo")
            print("9. 🩺 System Health & Status")
            print()
            print("🆕 NEW OPENAI RESPONSES API PATTERNS:")
            print("A. 🔤 Simple Response (gpt-4.1)")
            print("B. 🌐 Web Search Preview Demo")
            print("C. 🧠 O3-Mini Reasoning Analysis")
            print("D. 🎬 Streaming Response Demo")
            print()
            print("0. 🚪 Exit Demo")
            print()

            try:
                choice = input("Select option (0-9, A-D): ").strip().upper()

                if choice == "0":
                    print("\n👋 Thanks for exploring EQ12 Model Response System!")
                    break
                elif choice == "1":
                    await self.demo_parlay_analysis()
                elif choice == "2":
                    await self.demo_nfl_slate_analysis()
                elif choice == "3":
                    await self.demo_nba_props_analysis()
                elif choice == "4":
                    await self.demo_live_betting_analysis()
                elif choice == "5":
                    await self.demo_steam_detection()
                elif choice == "6":
                    await self.demo_portfolio_optimization()
                elif choice == "7":
                    await self.demo_batch_processing()
                elif choice == "8":
                    await self.demo_live_monitoring()
                elif choice == "9":
                    await self.demo_system_status()
                elif choice == "A":
                    await self.demo_simple_response()
                elif choice == "B":
                    await self.demo_web_search_preview()
                elif choice == "C":
                    await self.demo_o3_reasoning()
                elif choice == "D":
                    await self.demo_streaming_response()
                else:
                    print("❌ Invalid option. Please select 0-9 or A-D.")

            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

    async def demo_parlay_analysis(self):
        """Demo parlay analysis capabilities"""
        print("\n" + "🎲 ADVANCED PARLAY ANALYSIS DEMO" + "\n" + "=" * 50)

        # Display sample parlay
        print("📋 Sample Parlay Legs:")
        for i, leg in enumerate(DEMO_DATA["parlay_legs"], 1):
            print(f"   {i}. {leg['game']} - {leg['selection']} ({leg['odds']:+d})")

        bankroll = float(input("\n💰 Enter bankroll amount ($): ") or "5000")

        print(f"\n🔄 Analyzing parlay with ${bankroll:,.2f} bankroll...")

        if not self.demo_mode and self.system:
            try:
                from eq12_unified_responses import quick_parlay_analysis

                result = await quick_parlay_analysis(DEMO_DATA["parlay_legs"], bankroll=bankroll)
                self._display_real_result(result, "Parlay Analysis")

            except Exception as e:
                print(f"❌ API call failed: {e}")
                self._display_demo_parlay_result(bankroll)
        else:
            self._display_demo_parlay_result(bankroll)

    def _display_demo_parlay_result(self, bankroll: float):
        """Display simulated parlay analysis result"""
        print("\n✅ PARLAY ANALYSIS COMPLETE")
        print("-" * 40)
        print("Overall Rating: ⭐⭐⭐⭐ GOOD")
        print("Expected Value: +5.2%")
        print("True Odds: +650")
        print("Sportsbook Odds: +600")
        print(f"Kelly Recommended Stake: ${bankroll * 0.021:,.2f} (2.1% of bankroll)")
        print(f"Maximum Loss: ${bankroll * 0.021:,.2f}")
        print(f"Expected Profit: ${bankroll * 0.021 * 6.5:,.2f}")
        print()
        print("🔍 Key Insights:")
        print("• Lakers spread and total show negative correlation (-0.3)")
        print("• Adding Celtics ML creates diversification value")
        print("• Weather not a factor for indoor NBA games")
        print("• Recommend reducing stake size due to correlation risk")
        print()
        print("⚠️ Risk Factors:")
        print("• Correlated legs increase overall variance")
        print("• Lakers injury news could impact both legs")
        print("• Consider hedging opportunities during games")

    async def demo_nfl_slate_analysis(self):
        """Demo NFL slate analysis"""
        print("\n" + "🏈 NFL SUNDAY SLATE ANALYSIS DEMO" + "\n" + "=" * 50)

        # Display sample games
        print("📋 Sample NFL Games:")
        for i, game in enumerate(DEMO_DATA["nfl_games"], 1):
            weather = game["weather"]
            print(f"   {i}. {game['away']} @ {game['home']} ({game['spread']})")
            print(f"      Total: {game['total']} | Weather: {weather['temp']}, {weather['wind']}")

        bankroll = float(input("\n💰 Enter bankroll amount ($): ") or "10000")

        print(f"\n🔄 Analyzing NFL slate with ${bankroll:,.2f} bankroll...")

        if not self.demo_mode and self.system:
            try:
                from eq12_unified_responses import quick_nfl_slate_analysis

                result = await quick_nfl_slate_analysis(DEMO_DATA["nfl_games"], bankroll=bankroll)
                self._display_real_result(result, "NFL Slate Analysis")

            except Exception as e:
                print(f"❌ API call failed: {e}")
                self._display_demo_nfl_result(bankroll)
        else:
            self._display_demo_nfl_result(bankroll)

    def _display_demo_nfl_result(self, bankroll: float):
        """Display simulated NFL slate result"""
        print("\n✅ NFL SLATE ANALYSIS COMPLETE")
        print("-" * 40)
        print("🌟 TOP PLAYS:")
        print(f"1. Patriots/Bills UNDER 44.5 - 3 units (${bankroll * 0.06:,.2f})")
        print("   • Wind 18mph + cold temp favors under")
        print("   • Expected Value: +7.2%")
        print()
        print(f"2. Eagles -7 vs Cowboys - 2 units (${bankroll * 0.04:,.2f})")
        print("   • Cowboys struggle in primetime road games")
        print("   • Expected Value: +4.8%")
        print()
        print("🔗 CORRELATION OPPORTUNITIES:")
        print("• AFC East Weather Stack: Patriots/Bills Under + Jets/Dolphins Under")
        print("• NFC East Division Stack: Eagles -7 + Commanders ML")
        print()
        print("⚠️ AVOID LIST:")
        print("• Chiefs -10.5 (public favorite, line inflated)")
        print("• Cowboys +7 (road primetime fade spot)")
        print()
        print("📊 SLATE SUMMARY:")
        print("• Total Games Analyzed: 16")
        print("• Weather Concerns: 3 games")
        print("• Sharp Movement Detected: 5 games")
        print(f"• Recommended Total Allocation: ${bankroll * 0.25:,.2f} (25%)")

    async def demo_nba_props_analysis(self):
        """Demo NBA props analysis"""
        print("\n" + "🏀 NBA PLAYER PROPS ANALYSIS DEMO" + "\n" + "=" * 50)

        # Display sample props
        print("📋 Sample NBA Props:")
        for i, prop in enumerate(DEMO_DATA["nba_props"], 1):
            print(
                f"   {i}. {prop['player']} ({prop['team']}) - {prop['market']} O/U {prop['line']}"
            )
            print(f"      Over: {prop['over_odds']:+d} | Under: {prop['under_odds']:+d}")

        print("\n🔄 Analyzing NBA props with usage rates and matchups...")

        if not self.demo_mode and self.system:
            try:
                from eq12_unified_responses import quick_nba_slate_analysis

                # Adapt NBA props for analysis
                games_data = [
                    {"home": "Warriors", "away": "Lakers"},
                    {"home": "Heat", "away": "Celtics"},
                ]
                result = await quick_nba_slate_analysis(games_data, bankroll=5000.0)
                self._display_real_result(result, "NBA Props Analysis")

            except Exception as e:
                print(f"❌ API call failed: {e}")
                self._display_demo_nba_props_result()
        else:
            self._display_demo_nba_props_result()

    def _display_demo_nba_props_result(self):
        """Display simulated NBA props result"""
        print("\n✅ NBA PROPS ANALYSIS COMPLETE")
        print("-" * 40)
        print("🌟 TOP PROPS:")
        print("1. LeBron James OVER 26.5 Points - 2 units")
        print("   • Usage rate up to 34.2% with AD out")
        print("   • Warriors allow 28.1 PPG to opposing forwards")
        print("   • Expected Value: +6.8%")
        print()
        print("2. Stephen Curry OVER 4.5 Threes - 1.5 units")
        print("   • Lakers rank 28th in 3-point defense")
        print("   • Curry averaging 5.1 made 3s in last 10 games")
        print("   • Expected Value: +4.1%")
        print()
        print("🔗 SAME GAME PARLAY OPPORTUNITIES:")
        print("• LeBron O26.5 Pts + Lakers ML (positive correlation)")
        print("• Curry O4.5 3s + Warriors TT O115.5 (shooting correlation)")
        print()
        print("📊 MARKET INTELLIGENCE:")
        print("• Sharp money on Tatum rebounds (line moved from 8.5 to 9)")
        print("• Heavy public betting on LeBron points (75% of tickets)")
        print("• Alt line value: LeBron O25.5 at +odds better value")
        print()
        print("⚠️ INJURY IMPACT:")
        print("• Anthony Davis OUT - increases LeBron usage +3.2%")
        print("• Marcus Smart probable - minimal impact on Tatum props")

    async def demo_live_betting_analysis(self):
        """Demo live betting momentum analysis"""
        print("\n" + "⚡ LIVE BETTING MOMENTUM ANALYSIS DEMO" + "\n" + "=" * 50)

        # Simulate live game state
        game_state = {
            "game": "Lakers vs Warriors",
            "score": "Lakers 68, Warriors 71",
            "time": "3rd Quarter 8:42",
            "live_spread": "Warriors -2.5",
            "live_total": "228.5",
            "momentum": [
                "Warriors 12-3 run last 4 minutes",
                "LeBron has 3 fouls",
                "Curry 4/6 from three",
            ],
        }

        print("📺 LIVE GAME SITUATION:")
        print(f"🏀 {game_state['game']}")
        print(f"⏱️  {game_state['time']}")
        print(f"📊 Score: {game_state['score']}")
        print(f"📈 Live Spread: {game_state['live_spread']}")
        print(f"📈 Live Total: {game_state['live_total']}")
        print()
        print("🔥 MOMENTUM FACTORS:")
        for factor in game_state["momentum"]:
            print(f"   • {factor}")

        print("\n🔄 Analyzing live betting opportunities...")

        if not self.demo_mode and self.system:
            try:
                result = await self.system.analyze_betting_opportunity(
                    "live_betting", {"game_state": game_state}
                )
                self._display_real_result(result, "Live Betting Analysis")

            except Exception as e:
                print(f"❌ API call failed: {e}")
                self._display_demo_live_result()
        else:
            self._display_demo_live_result()

    def _display_demo_live_result(self):
        """Display simulated live betting result"""
        print("\n✅ LIVE BETTING ANALYSIS COMPLETE")
        print("-" * 40)
        print("🚨 IMMEDIATE OPPORTUNITIES:")
        print("1. Lakers +2.5 at +105 - BET NOW")
        print("   • Warriors momentum likely to regress")
        print("   • LeBron foul trouble creates value on spread")
        print("   • Max stake: $200")
        print("   • Exit: Hedge if Lakers take lead")
        print()
        print("2. UNDER 228.5 at -110 - CONSIDER")
        print("   • Game pace slowing in 2nd half")
        print("   • Both teams tightening defense")
        print("   • Expected closing: 226.5")
        print()
        print("🔄 HEDGE RECOMMENDATIONS:")
        print("• If you have Warriors -3.5 pregame: hedge Lakers +2.5 for guaranteed profit")
        print("• OVER 225.5 pregame: wait for total to drop below 225 to hedge")
        print()
        print("💰 CASH OUT ALERTS:")
        print("• Warriors season win total OVER: cash out at 75% value")
        print("• LeBron MVP odds: hold position, value increasing")
        print()
        print("⏰ TIMING: Execute within next 2 minutes before timeout adjustments")

    async def demo_steam_detection(self):
        """Demo steam move detection"""
        print("\n" + "🔍 SHARP STEAM DETECTION DEMO" + "\n" + "=" * 50)

        # Display line movements
        print("📈 RECENT LINE MOVEMENTS:")
        for i, move in enumerate(DEMO_DATA["line_movements"], 1):
            direction = "📈" if move["movement"] > 0 else "📉"
            print(f"   {i}. {move['game']} - {move['market']}")
            print(f"      {move['opening']} → {move['current']} {direction}")
            print(
                f"      Public: {move['public_percentage']}% | Sharp: {move.get('sharp_indicator', False)}"
            )

        print("\n🔄 Detecting sharp steam moves...")

        if not self.demo_mode and self.system:
            try:
                from eq12_unified_responses import quick_steam_detection

                result = await quick_steam_detection(DEMO_DATA["line_movements"])
                self._display_real_result(result, "Steam Detection")

            except Exception as e:
                print(f"❌ API call failed: {e}")
                self._display_demo_steam_result()
        else:
            self._display_demo_steam_result()

    def _display_demo_steam_result(self):
        """Display simulated steam detection result"""
        print("\n✅ STEAM DETECTION COMPLETE")
        print("-" * 40)
        print("🚨 ALERT LEVEL: HIGH")
        print()
        print("🎯 DETECTED STEAM MOVES:")
        print("1. Patriots vs Bills - Spread")
        print("   • Line moved Bills -2.5 → -3.5 (1 point)")
        print("   • Only 35% public money on Bills")
        print("   • Classic reverse line movement")
        print("   • Confidence: 95%")
        print("   • FOLLOW: Bills -3.5")
        print()
        print("2. Cowboys vs Eagles - Total")
        print("   • Total moved 52.5 → 51.5 (-1 point)")
        print("   • 72% public on OVER but line dropping")
        print("   • Volume spike detected at multiple books")
        print("   • Confidence: 88%")
        print("   • FOLLOW: Under 51.5")
        print()
        print("⚡ EXECUTION PLAN:")
        print("• Best books: DraftKings, FanDuel (still have old lines)")
        print("• Optimal sizing: 1.5-2 units on each steam move")
        print("• Time window: Next 15-30 minutes before lines catch up")
        print()
        print("⚠️ RISK WARNINGS:")
        print("• Steam moves can reverse if injury news breaks")
        print("• Don't chase steam on props (less reliable)")
        print("• Limit exposure to 10% of bankroll on steam follows")

    async def demo_portfolio_optimization(self):
        """Demo portfolio optimization"""
        print("\n" + "📊 KELLY CRITERION PORTFOLIO OPTIMIZATION DEMO" + "\n" + "=" * 50)

        # Display current positions
        print("📋 CURRENT POSITIONS:")
        total_risk = 0
        for pos in DEMO_DATA["portfolio_positions"]:
            print(f"   • {pos['game']}: {pos['selection']} - ${pos['stake']} at {pos['odds']:+d}")
            total_risk += pos["stake"]

        print(f"\n💰 Current Risk: ${total_risk:,.2f}")

        # Display new opportunities
        print("\n🎯 NEW OPPORTUNITIES:")
        for opp in DEMO_DATA["new_opportunities"]:
            print(f"   • {opp['game']}: {opp['selection']} at {opp['odds']:+d}")
            print(f"     Edge: {opp['estimated_edge']:.1%} | Confidence: {opp['confidence']}")

        bankroll = float(input("\n💰 Enter total bankroll ($): ") or "25000")
        risk_tolerance = (
            input("📊 Risk tolerance (conservative/moderate/aggressive): ") or "moderate"
        )

        print(f"\n🔄 Optimizing portfolio with ${bankroll:,.2f} bankroll...")

        if not self.demo_mode and self.system:
            try:
                result = await self.system.analyze_betting_opportunity(
                    "portfolio_optimization",
                    {
                        "current_positions": DEMO_DATA["portfolio_positions"],
                        "new_opportunities": DEMO_DATA["new_opportunities"],
                    },
                    bankroll=bankroll,
                )
                self._display_real_result(result, "Portfolio Optimization")

            except Exception as e:
                print(f"❌ API call failed: {e}")
                self._display_demo_portfolio_result(bankroll, risk_tolerance)
        else:
            self._display_demo_portfolio_result(bankroll, risk_tolerance)

    def _display_demo_portfolio_result(self, bankroll: float, risk_tolerance: str):
        """Display simulated portfolio optimization result"""
        print("\n✅ PORTFOLIO OPTIMIZATION COMPLETE")
        print("-" * 40)
        print("📊 RECOMMENDED POSITION SIZING:")
        print(f"1. Celtics -4.5: ${bankroll * 0.026:,.2f} (2.6% Kelly)")
        print("   • Edge: 6.5% | Risk Score: 3.2/10")
        print(f"   • Expected Return: ${bankroll * 0.026 * 0.065:,.2f}")
        print()
        print(f"2. Chiefs/Broncos Over 48.5: ${bankroll * 0.018:,.2f} (1.8% Kelly)")
        print("   • Edge: 4.1% | Risk Score: 2.8/10")
        print(f"   • Expected Return: ${bankroll * 0.018 * 0.041:,.2f}")
        print()
        print("📈 PORTFOLIO METRICS:")
        print(f"• Total Allocated: ${bankroll * 0.18:,.2f} (18% of bankroll)")
        print("• Expected Portfolio Return: +12.4% monthly")
        print("• Portfolio Volatility: 8.9%")
        print("• Sharpe Ratio: 1.39")
        print(f"• Value at Risk (95%): ${bankroll * 0.032:,.2f}")
        print()
        print("🔗 CORRELATION ANALYSIS:")
        print("• NBA positions show -0.12 correlation (good diversification)")
        print("• NFL positions show +0.18 correlation (acceptable)")
        print("• Recommend max 3 positions per sport")
        print()
        print("⚠️ RISK MANAGEMENT:")
        print(f"• Stop-loss trigger: -{5 + (5 if risk_tolerance == 'aggressive' else 0)}% drawdown")
        print("• Position limit: 5% max per single bet")
        print("• Rebalance weekly or after 10% bankroll change")

    async def demo_batch_processing(self):
        """Demo batch processing of multiple opportunities"""
        print("\n" + "🔄 BATCH PROCESSING DEMO" + "\n" + "=" * 50)

        opportunities = [
            {"type": "parlay", "data": {"legs": DEMO_DATA["parlay_legs"][:2]}},
            {"type": "nfl_slate", "data": {"games": DEMO_DATA["nfl_games"][:2]}},
            {"type": "steam_detection", "data": {"line_movements": DEMO_DATA["line_movements"]}},
        ]

        print(f"📋 Processing {len(opportunities)} opportunities in parallel:")
        for i, opp in enumerate(opportunities, 1):
            print(f"   {i}. {opp['type'].replace('_', ' ').title()}")

        bankroll = float(input("\n💰 Enter bankroll ($): ") or "10000")

        print("\n🔄 Processing all opportunities...")

        if not self.demo_mode and self.system:
            try:
                results = await self.system.batch_analyze_opportunities(
                    opportunities, bankroll=bankroll
                )
                print(f"\n✅ Batch processing completed: {len(results)} results")
                for i, result in enumerate(results, 1):
                    status = "✅" if result["status"] == "completed" else "❌"
                    print(f"   {status} Opportunity {i}: {result['status']}")

            except Exception as e:
                print(f"❌ Batch processing failed: {e}")
                self._display_demo_batch_result()
        else:
            self._display_demo_batch_result()

    def _display_demo_batch_result(self):
        """Display simulated batch processing result"""
        print("\n✅ BATCH PROCESSING COMPLETE")
        print("-" * 40)
        print("📊 RESULTS SUMMARY:")
        print("   ✅ Parlay Analysis: COMPLETED (5.2% edge found)")
        print("   ✅ NFL Slate Analysis: COMPLETED (3 plays identified)")
        print("   ✅ Steam Detection: COMPLETED (2 steam moves detected)")
        print()
        print("🏆 TOP RECOMMENDATIONS:")
        print("1. Patriots/Bills Under 44.5 (NFL) - 3 units")
        print("2. Lakers/Celtics 3-leg parlay - 1.5 units")
        print("3. Bills -3.5 steam follow - 2 units")
        print()
        print("⏱️ Total processing time: 2.3 seconds (parallel execution)")
        print("💰 Total recommended allocation: 22% of bankroll")

    async def demo_live_monitoring(self):
        """Demo live monitoring session"""
        print("\n" + "📺 LIVE MONITORING SESSION DEMO" + "\n" + "=" * 50)

        games = ["Patriots vs Bills", "Lakers vs Warriors", "Cowboys vs Eagles"]

        print("🎮 Starting live monitoring session for:")
        for i, game in enumerate(games, 1):
            print(f"   {i}. {game}")

        print("\n🔄 Initializing real-time monitoring...")

        if not self.demo_mode and self.system:
            try:
                session_id = await self.system.start_live_monitoring_session(games)
                print(f"✅ Session started: {session_id}")

                # Simulate checking status
                await asyncio.sleep(1)
                status = await self.system.get_session_status(session_id)
                print(f"📊 Session status: {status.get('session_info', {}).get('type', 'Active')}")

                # Stop session
                stopped = self.system.stop_session(session_id)
                print(f"🛑 Session stopped: {'✅' if stopped else '❌'}")

            except Exception as e:
                print(f"❌ Live monitoring failed: {e}")
                self._display_demo_monitoring_result()
        else:
            self._display_demo_monitoring_result()

    def _display_demo_monitoring_result(self):
        """Display simulated monitoring result"""
        print("\n✅ LIVE MONITORING ACTIVE")
        print("-" * 40)
        print("📡 Session ID: live_1704067200")
        print("⏱️  Started: 12:00:00 PM EST")
        print("🎮 Status: Monitoring 3 games")
        print()
        print("🔔 REAL-TIME ALERTS:")
        print("   📈 Patriots spread moved -2.5 → -3 (steam detected)")
        print("   ⚡ Lakers momentum shift: 8-0 run (live bet alert)")
        print("   🌟 Cowboys line value: +7.5 available at DK")
        print()
        print("📊 STREAMING UPDATES:")
        print("   • Win probabilities updating every 30 seconds")
        print("   • Line movement alerts with sharp indicators")
        print("   • Optimal betting windows highlighted")
        print("   • Hedge recommendations based on portfolio")
        print()
        print("🛑 Session can be stopped anytime with session ID")

    async def demo_system_status(self):
        """Demo system status and health check"""
        print("\n" + "🩺 SYSTEM HEALTH & STATUS DEMO" + "\n" + "=" * 50)

        print("🔍 Checking system components...")

        if self.system:
            try:
                health = await self.system.health_check()
                status = self.system.get_system_status()

                print(f"\n✅ SYSTEM HEALTH: {health.get('status', 'Unknown').upper()}")
                print("-" * 30)
                print(f"🔑 API Key: {health.get('checks', {}).get('api_key', 'Unknown')}")
                print(f"🚀 Core API: {health.get('checks', {}).get('core_api', 'Unknown')}")
                print(f"📋 Templates: {health.get('checks', {}).get('templates', 'Unknown')}")
                print(
                    f"🌐 API Connection: {health.get('checks', {}).get('api_connection', 'Unknown')}"
                )

                print("\n📊 SYSTEM STATUS:")
                print(f"• Core API Available: {status.get('core_api_available', False)}")
                print(f"• Templates Available: {status.get('templates_available', False)}")
                print(f"• Active Sessions: {status.get('active_sessions', 0)}")

            except Exception as e:
                print(f"❌ Status check failed: {e}")
                self._display_demo_status_result()
        else:
            self._display_demo_status_result()

    def _display_demo_status_result(self):
        """Display simulated status result"""
        print("\n✅ SYSTEM STATUS: OPERATIONAL")
        print("-" * 30)
        print("🔑 API Key: Present")
        print("🚀 Core API: Loaded")
        print("📋 Templates: Loaded")
        print("🌐 API Connection: Available")
        print()
        print("📊 MODULE STATUS:")
        print("• eq12_model_responses: ✅ Loaded")
        print("• eq12_response_templates: ✅ Loaded")
        print("• eq12_unified_responses: ✅ Loaded")
        print()
        print("🎮 CAPABILITIES:")
        print("• ✅ Parlay Analysis with Correlation Detection")
        print("• ✅ NFL Slate Analysis with Weather Integration")
        print("• ✅ NBA Props with Usage Rate Optimization")
        print("• ✅ Live Betting with Momentum Tracking")
        print("• ✅ Steam Detection with Sharp Following")
        print("• ✅ Kelly Portfolio Optimization")
        print("• ✅ Batch Processing & Live Monitoring")
        print()
        print("⚡ PERFORMANCE:")
        print("• Average Response Time: 1.2 seconds")
        print("• Daily API Calls: 1,247")
        print("• Success Rate: 99.8%")

    def _display_real_result(self, result: dict[str, Any], analysis_type: str):
        """Display real API result"""
        print(f"\n✅ {analysis_type.upper()} COMPLETE")
        print("-" * 50)
        print(f"Response ID: {result.get('id', 'N/A')}")
        print(f"Model: {result.get('model', 'N/A')}")
        print(f"Status: {result.get('status', 'N/A')}")

        if "output" in result:
            try:
                output = (
                    json.loads(result["output"]["text"])
                    if isinstance(result["output"]["text"], str)
                    else result["output"]["text"]
                )
                print("\nAnalysis Result:")
                print(
                    json.dumps(output, indent=2)[:1000] + "..."
                    if len(str(output)) > 1000
                    else json.dumps(output, indent=2)
                )
            except:
                print(f"\nRaw Output: {str(result['output'])[:500]}...")

        if "usage" in result:
            usage = result["usage"]
            usage_str = f"Usage: {usage.get('prompt_tokens', 0)} prompt + "
            usage_str += f"{usage.get('completion_tokens', 0)} completion = "
            usage_str += f"{usage.get('total_tokens', 0)} total tokens"
            print(f"\n{usage_str}")

    async def demo_simple_response(self):
        """Demo simple response using gpt-4.1"""
        print("\n" + "🔤 SIMPLE RESPONSE DEMO (GPT-4.1)" + "\n" + "=" * 50)

        question = input("Enter a question: ") or "Tell me about sports betting."

        print("\n🔄 Generating simple response...")

        if not self.demo_mode and self.system:
            try:
                result = await self.system.simple_response_example(question)
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                else:
                    print(f"\n✅ Response ID: {result.get('id', 'N/A')}")
                    print(f"Response: {result.get('response', 'N/A')}")
            except Exception as e:
                print(f"❌ Simple response failed: {e}")
                self._display_demo_simple_result(question)
        else:
            self._display_demo_simple_result(question)

    def _display_demo_simple_result(self, question: str):
        """Display simulated simple response"""
        print("\n✅ SIMPLE RESPONSE COMPLETE")
        print("-" * 40)
        print(f"Question: {question}")
        print("\nResponse:")
        print("Sports betting involves predicting outcomes of sporting events.")
        print("Key factors include odds analysis, bankroll management, and ")
        print("understanding probability. The EQ12 system helps optimize ")
        print("betting strategies using advanced AI analysis.")

    async def demo_web_search_preview(self):
        """Demo web search preview tool"""
        print("\n" + "🌐 WEB SEARCH PREVIEW DEMO" + "\n" + "=" * 50)

        query = input("Enter search query: ") or "Latest NFL injury news today"

        print("\n🔄 Searching web with preview tool...")

        if not self.demo_mode and self.system:
            try:
                result = await self.system.web_search_response_example(query)
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                else:
                    print(f"\n✅ Search ID: {result.get('id', 'N/A')}")
                    print(f"Results: {result.get('search_result', 'N/A')}")
            except Exception as e:
                print(f"❌ Web search failed: {e}")
                self._display_demo_web_search_result(query)
        else:
            self._display_demo_web_search_result(query)

    def _display_demo_web_search_result(self, query: str):
        """Display simulated web search result"""
        print("\n✅ WEB SEARCH COMPLETE")
        print("-" * 40)
        print(f"Query: {query}")
        print("\n🔍 Search Results:")
        print("• Josh Allen (Bills): Questionable with shoulder injury")
        print("• Travis Kelce (Chiefs): Expected to play despite ankle issue")
        print("• Cooper Kupp (Rams): Listed as probable, full practice")
        print("• Saquon Barkley (Giants): Game-time decision")
        print("\n📊 Betting Impact:")
        impact_msg = "Bills spread may move if Allen sits. Monitor inactives 90 "
        impact_msg += "min before kickoff."
        print(impact_msg)

    async def demo_o3_reasoning(self):
        """Demo O3-mini reasoning analysis"""
        print("\n" + "🧠 O3-MINI REASONING DEMO" + "\n" + "=" * 50)

        question_default = "Should I bet Lakers -3.5 or take the over 225.5?"
        question = input("Enter complex question: ") or question_default
        effort = input("Reasoning effort (low/medium/high): ") or "high"

        print(f"\n🔄 Analyzing with {effort} reasoning effort...")

        if not self.demo_mode and self.system:
            try:
                result = await self.system.reasoning_response_example(question, effort)
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                else:
                    print(f"\n✅ Analysis ID: {result.get('id', 'N/A')}")
                    print(f"Reasoning: {result.get('reasoning', 'N/A')}")
            except Exception as e:
                print(f"❌ Reasoning analysis failed: {e}")
                self._display_demo_reasoning_result(question, effort)
        else:
            self._display_demo_reasoning_result(question, effort)

    def _display_demo_reasoning_result(self, question: str, effort: str):
        """Display simulated reasoning result"""
        print("\n✅ O3-MINI REASONING COMPLETE")
        print("-" * 40)
        print(f"Question: {question}")
        print(f"Effort Level: {effort.upper()}")
        print("\n🧠 Step-by-Step Reasoning:")
        print("1. Analyze Lakers spread (-3.5):")
        print("   - Home court advantage: +2.5 points")
        print("   - Recent form: Lakers 7-3 last 10 games")
        print("   - Matchup: Favorable vs Warriors defense")
        print("2. Analyze total (225.5):")
        print("   - Both teams average 115+ PPG")
        print("   - Pace factor: Fast-paced matchup expected")
        print("   - Defense: Both teams struggle on defensive end")
        print("\n🎯 RECOMMENDATION:")
        rec_msg = "Take OVER 225.5 (-110). Higher probability (58%) than "
        rec_msg += "Lakers -3.5 (52%)."
        print(rec_msg)
        print("Reasoning: Pace and offensive efficiency favor high-scoring game.")

    async def demo_streaming_response(self):
        """Demo streaming response"""
        print("\n" + "🎬 STREAMING RESPONSE DEMO" + "\n" + "=" * 50)

        input("Enter question for streaming: ") or "Analyze Patriots vs Bills game"

        print("\n🔄 Streaming response (simulated)...")
        print("\n📡 LIVE STREAM:")

        # Simulate streaming output
        streaming_text = [
            "Analyzing Patriots vs Bills matchup...",
            "Key factors: Weather conditions, Bills -3.5 spread",
            "Patriots at home in cold weather historically strong",
            "Bills offense may struggle in windy conditions",
            "Recommendation: Consider Patriots +3.5 and Under total",
            "✅ Analysis complete",
        ]

        import time

        for chunk in streaming_text:
            print(f"🔸 {chunk}")
            if not self.demo_mode:
                await asyncio.sleep(0.5)  # Simulate streaming delay
            else:
                time.sleep(0.3)  # Faster for demo

        print("\n📊 FINAL RECOMMENDATION:")
        print("Patriots +3.5 (-110) - 2 units")
        print("Under 44.5 (-105) - 1.5 units")
        print("Parlay Patriots +3.5 & Under for enhanced value")


async def main():
    """Run the EQ12 Response System Demo"""
    demo = EQ12ResponseDemo()
    await demo.run_demo()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Check that all required modules are installed and API keys are configured.")
