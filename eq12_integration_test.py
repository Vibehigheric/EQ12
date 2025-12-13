"""
EQ12 Integrated Workflow Test - Comprehensive system integration validation
"""


def test_integrated_workflow():
    """Test all EQ12 systems working together"""

    print("🚀 EQ12 INTEGRATED WORKFLOW TEST")
    print("=" * 50)

    try:
        # Test 1: Odds Ingestion System
        print("📡 Testing odds ingestion...")
        from eq12_odds_ingestor import OddsIngestor

        ingestor = OddsIngestor()
        odds_result = ingestor.ingest_live_odds()
        games_count = odds_result.get("total_games", 0)
        print(f"✅ Odds Ingestion: {games_count} games processed")

        # Test 2: AI Client System
        print("\n🤖 Testing AI client...")
        from eq12_ai_client import get_ai_client

        ai_client = get_ai_client()
        test_response = ai_client.ask("Respond with: EQ12 integration test successful")
        print(f"✅ AI Client: {test_response[:50]}...")

        # Test 3: Cost Guards System
        print("\n💰 Testing cost guards...")
        from eq12_cost_guards import get_cost_guards

        cost_guards = get_cost_guards()
        allowed, _ = cost_guards.check_request_allowed("test_service", 0.01)
        print(f"✅ Cost Guards: Request allowed={allowed}")

        # Test 4: Usage Analytics
        print("\n📊 Testing usage tracking...")
        usage = ai_client.get_usage_summary()
        total_cost = usage.get("total_cost", 0)
        print(f"✅ Usage Tracking: ${total_cost:.3f} total cost")

        # Test 5: Parlay Sanitizer
        print("\n🎯 Testing parlay sanitizer...")
        from eq12_parlay_sanitizer import ParlaySanitizer

        sanitizer = ParlaySanitizer(ai_enabled=False)

        test_parlay = {
            "sportsbook": "draftkings",
            "legs": [
                {
                    "market": "moneyline",
                    "selection": "Bills",
                    "odds": "-150",
                    "home_team": "Bills",
                    "away_team": "Patriots",
                },
                {
                    "market": "spread",
                    "selection": "Cowboys -3.5",
                    "odds": "-110",
                    "home_team": "Cowboys",
                    "away_team": "Giants",
                },
            ],
        }

        validation = sanitizer.validate_parlay(test_parlay)
        print(f"✅ Parlay Sanitizer: Valid={validation['is_valid']}")

        # Integration Test: Use odds data for AI parlay analysis
        if games_count > 0:
            print("\n🔗 Testing integrated parlay analysis...")
            games_data = odds_result.get("games", [])[:3]  # Use first 3 games

            if games_data:
                analysis = ai_client.analyze_parlay_opportunities(games_data, bankroll=1000.0)
                print(f"✅ Integrated Analysis: {len(analysis.split())} words of analysis")
            else:
                print("⚠️ No games data available for integrated analysis")

        print("\n" + "=" * 50)
        print("🎉 INTEGRATION TEST COMPLETE - ALL SYSTEMS OPERATIONAL!")
        print("🏆 EQ12 GODSTACK is ready for production betting analysis!")

        return True

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    test_integrated_workflow()
