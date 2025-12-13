#!/usr/bin/env python3
"""
EQ12 Production Model Client - Usage Examples
Expert-level integration patterns for OpenAI models with EQ12 constraints.

This demonstrates the complete workflow from raw odds → normalized data → parlays
using the task-specific model selection from your expert guide.
"""

# Import our production client
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from eq12_client import EQ12Config, EQ12ModelClient


def main():
    """Complete EQ12 model integration example following expert patterns."""

    print("🎰 EQ12 Production Model Client - Usage Examples")
    print("=" * 60)

    # ✅ Initialize with EQ12-specific constraints
    config = EQ12Config(
        allowed_books=["draftkings", "fanduel", "betmgm"],
        min_ev_threshold=0.03,  # 3% minimum edge
        kelly_cap_per_leg=0.025,  # 2.5% Kelly cap per leg
        max_correlation_risk=0.15,  # Low correlation tolerance
        stale_data_threshold_minutes=15,  # Fresh data only
    )

    client = EQ12ModelClient(config)

    # ✅ Example 1: Extract odds from raw sportsbook data
    print("\n📊 STEP 1: Extract & normalize odds (gpt-4o-mini)")
    raw_odds_data = """
    DraftKings NFL Week 5:
    Kansas City Chiefs -3.0 (-110) vs Buffalo Bills +3.0 (-110)
    Total: Over 47.5 (-110), Under 47.5 (-110)
    Last updated: 2025-10-05 7:30 PM ET
    
    FanDuel NFL:
    Chiefs -2.5 (-105) vs Bills +2.5 (-115)  
    Total: O47.5 (-108), U47.5 (-112)
    Updated: Oct 5, 2025 7:35 PM
    
    BetMGM:
    KC Chiefs -3 (-108) vs BUF Bills +3 (-112)
    Over/Under: 47.5 O(-110)/U(-110)
    """

    odds_result = client.extract_odds(raw_odds_data)

    if odds_result["success"]:
        print(f"✅ Extracted {len(odds_result['data']['rows'])} odds entries")
        print(f"   Books found: {odds_result['data']['books_found']}")
        print(f"   Model used: {odds_result['model_used']} ({odds_result['tokens']} tokens)")

        # Show sample extracted data
        for row in odds_result["data"]["rows"][:3]:
            print(f"   • {row['book']}: {row['selection']} @ {row['american_odds']}")
    else:
        print(f"❌ Odds extraction failed: {odds_result['error']}")
        return

    # ✅ Example 2: Build parlays with constraints (gpt-4o)
    print("\n🎯 STEP 2: Build parlays with reasoning (gpt-4o)")
    parlay_result = client.build_parlays(
        odds_data=odds_result["data"]["rows"],
        bankroll=1000,  # $1000 bankroll
        min_ev=0.025,  # 2.5% minimum edge
        max_legs=4,  # Maximum 4-leg parlays
    )

    if parlay_result["success"]:
        parlays = parlay_result["data"]["parlays"]
        print(f"✅ Generated {len(parlays)} profitable parlays")
        print(f"   Model used: {parlay_result['model_used']} ({parlay_result['tokens']} tokens)")

        for i, parlay in enumerate(parlays[:2], 1):  # Show first 2 parlays
            print(f"\n   💰 Parlay #{i} ({parlay['book']}):")
            print(f"      Combined odds: {parlay['combined_odds']}")
            print(f"      Stake: ${parlay['stake_recommendation']:.2f}")
            print(f"      Risk level: {parlay['risk_assessment']['overall_risk']}")
            print(f"      Expected ROI: {parlay.get('expected_roi', 'N/A')}")

            for leg in parlay["legs"]:
                print(f"      • {leg['selection']} @ {leg['odds']}")
    else:
        print(f"❌ Parlay building failed: {parlay_result['error']}")
        return

    # ✅ Example 3: Generate human explanations (gpt-4o-mini)
    print("\n📝 STEP 3: Generate explanations (gpt-4o-mini)")

    if parlays:
        best_parlay = parlays[0]  # Take the first parlay
        explanation_result = client.explain_parlay(best_parlay)

        if explanation_result["success"]:
            print("✅ Generated human explanation:")
            print(
                f"   Model used: {explanation_result['model_used']} ({explanation_result['tokens']} tokens)"
            )
            print(f"\n📋 {explanation_result['explanation']}")
        else:
            print(f"❌ Explanation failed: {explanation_result['error']}")

    # ✅ Example 4: Validate and repair if needed (gpt-4o)
    print("\n🔧 STEP 4: Validate & repair (gpt-4o)")

    # Simulate corrupted data for repair example
    corrupted_parlay = {
        "parlay_id": "invalid_test",
        "book": "unknown_book",  # Invalid book
        "legs": [
            {"game_id": "same_game", "selection": "Team A", "odds": "invalid"},
            {
                "game_id": "same_game",
                "selection": "Team B",
                "odds": "+150",
            },  # Correlation violation
        ],
        "combined_odds": "not_a_number",
    }

    repair_result = client.validate_and_repair(corrupted_parlay)

    if repair_result["success"]:
        print("✅ Validation and repair completed:")
        print(f"   Model used: {repair_result['model_used']} ({repair_result['tokens']} tokens)")
        print(f"   Violations found: {len(repair_result['data']['violations_found'])}")
        print(f"   Repair successful: {repair_result['data']['repair_successful']}")

        if repair_result["data"]["violations_found"]:
            print("   Issues detected:")
            for violation in repair_result["data"]["violations_found"]:
                print(f"   • {violation}")
    else:
        print(f"❌ Validation failed: {repair_result['error']}")

    # ✅ Performance summary
    print("\n📊 PERFORMANCE SUMMARY")
    print("=" * 40)
    total_tokens = sum(
        [
            odds_result.get("tokens", 0),
            parlay_result.get("tokens", 0),
            explanation_result.get("tokens", 0) if "explanation_result" in locals() else 0,
            repair_result.get("tokens", 0),
        ]
    )

    total_time = sum(
        [
            odds_result.get("execution_time", 0),
            parlay_result.get("execution_time", 0),
            explanation_result.get("execution_time", 0) if "explanation_result" in locals() else 0,
            repair_result.get("execution_time", 0),
        ]
    )

    print(f"Total tokens used: {total_tokens:,}")
    print(f"Total execution time: {total_time:.2f}s")
    print("Models used: gpt-4o-mini (extract/explain) + gpt-4o (build/repair)")
    print("\n✅ EQ12 Expert Model Integration - Complete! 🎰")


def advanced_example():
    """Advanced usage patterns for production scenarios."""

    print("\n🚀 ADVANCED USAGE PATTERNS")
    print("=" * 50)

    config = EQ12Config(
        allowed_books=["draftkings", "fanduel", "betmgm"],
        min_ev_threshold=0.04,  # Higher threshold for selectivity
        kelly_cap_per_leg=0.02,  # Conservative Kelly
        max_correlation_risk=0.1,  # Very low correlation
        stale_data_threshold_minutes=10,  # Very fresh data only
    )

    client = EQ12ModelClient(config)

    # ✅ Pattern 1: Batch processing with error handling
    print("\n📦 Batch Processing Example:")

    multiple_sources = [
        "DraftKings: Patriots -7 (-110) vs Jets +7 (-110)",
        "FanDuel: Lakers +5.5 (-108) vs Warriors -5.5 (-112)",
        "BetMGM: Over 225.5 (-110) Under 225.5 (-110) Lakers vs Warriors",
    ]

    batch_results = []
    for i, source in enumerate(multiple_sources, 1):
        print(f"   Processing source {i}...")
        result = client.extract_odds(source)
        batch_results.append(result)

        if result["success"]:
            print(f"   ✅ Extracted {len(result['data']['rows'])} entries")
        else:
            print(f"   ❌ Failed: {result['error']}")

    successful_extractions = [r for r in batch_results if r["success"]]
    print(
        f"\n   📊 Batch complete: {len(successful_extractions)}/{len(multiple_sources)} successful"
    )

    # ✅ Pattern 2: Custom configuration for different risk profiles
    print("\n⚙️  Custom Risk Profile Example:")

    # Conservative profile
    EQ12Config(
        allowed_books=["draftkings"],  # Single book only
        min_ev_threshold=0.05,  # 5% minimum edge
        kelly_cap_per_leg=0.015,  # 1.5% Kelly cap
        max_correlation_risk=0.05,  # Very low correlation
    )

    # Aggressive profile
    EQ12Config(
        allowed_books=["draftkings", "fanduel", "betmgm"],
        min_ev_threshold=0.02,  # 2% minimum edge
        kelly_cap_per_leg=0.03,  # 3% Kelly cap
        max_correlation_risk=0.2,  # Higher correlation tolerance
    )

    print("   Conservative config: Single book, 5% min EV, 1.5% Kelly cap")
    print("   Aggressive config: All books, 2% min EV, 3% Kelly cap")
    print("   → Easily switch between risk profiles!")


if __name__ == "__main__":
    # Run basic examples
    main()

    # Run advanced patterns
    advanced_example()

    print("\n🎯 Examples complete! Check the integration guide for production deployment.")
    print("📁 Next: Integrate with your EQ12 scheduler workflow.")
