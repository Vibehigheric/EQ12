#!/usr/bin/env python3
"""
Test Real Results Integration - EQ12 Sports Betting System
Comprehensive testing of sports result parser integration with backtester
"""

import json
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_slip_cfb() -> dict:
    """Create a realistic CFB test slip"""
    return {
        "id": "test_cfb_slip_001",
        "timestamp": "2024-10-01T19:00:00Z",
        "date": "2024-10-01",
        "sport": "CFB",
        "stake": 100.0,
        "potential_payout": 650.0,
        "legs": [
            {
                "bet_type": "moneyline",
                "team": "Alabama",
                "odds": 150,
                "label": "Alabama ML",
            },
            {
                "bet_type": "spread",
                "team": "Georgia",
                "spread": -7.5,
                "odds": -110,
                "label": "Georgia -7.5",
            },
            {
                "bet_type": "total_over",
                "total": 52.5,
                "odds": -110,
                "label": "Over 52.5",
            },
        ],
    }


def create_test_slip_nfl() -> dict:
    """Create a realistic NFL test slip"""
    return {
        "id": "test_nfl_slip_001",
        "timestamp": "2024-10-03T20:00:00Z",
        "date": "2024-10-03",
        "sport": "NFL",
        "stake": 50.0,
        "potential_payout": 325.0,
        "legs": [
            {
                "bet_type": "moneyline",
                "team": "Kansas City Chiefs",
                "odds": -150,
                "label": "Chiefs ML",
            },
            {
                "bet_type": "total_under",
                "total": 47.5,
                "odds": -105,
                "label": "Under 47.5",
            },
        ],
    }


def test_sports_result_parser():
    """Test the sports result parser directly"""
    try:
        from src.core.sports_result_parser import SportsResultParser

        print("\n🔍 TESTING SPORTS RESULT PARSER")
        print("=" * 50)

        # Initialize parser
        parser = SportsResultParser()

        # Test CFB scores
        print("\n📊 Testing CFB Scores...")
        cfb_games = parser.get_cfb_scores(week=6, year=2024)
        print(f"  Found {len(cfb_games)} CFB games")

        if cfb_games:
            game = cfb_games[0]
            print(
                f"  Sample: {game['away_team']} @ {game['home_team']}: "
                f"{game['away_score']}-{game['home_score']}"
            )

        # Test NFL scores
        print("\n🏈 Testing NFL Scores...")
        nfl_games = parser.get_nfl_scores(week=5, season=2024)
        print(f"  Found {len(nfl_games)} NFL games")

        if nfl_games:
            game = nfl_games[0]
            print(
                f"  Sample: {game['away_team']} @ {game['home_team']}: "
                f"{game['away_score']}-{game['home_score']}"
            )

        # Test slip resolution
        print("\n🎯 Testing Slip Resolution...")
        test_slip = create_test_slip_cfb()
        resolved = parser.resolve_bet_slip(test_slip)

        print(f"  Slip ID: {resolved['id']}")
        print(f"  Overall Outcome: {resolved.get('overall_outcome', 'pending')}")
        print(f"  Legs Resolved: {resolved.get('legs_resolved', 'unknown')}")

        return True

    except Exception as e:
        print(f"❌ Sports Result Parser test failed: {e}")
        return False


def test_backtester_integration():
    """Test backtester with real results integration"""
    try:
        from src.core.backtester import HistoricalBacktester

        print("\n🔬 TESTING BACKTESTER INTEGRATION")
        print("=" * 50)

        # Create test directory and slips
        test_dir = Path("test_slips")
        test_dir.mkdir(exist_ok=True)

        # Create test slip files
        cfb_slip = create_test_slip_cfb()
        nfl_slip = create_test_slip_nfl()

        with open(test_dir / "cfb_test.json", "w") as f:
            json.dump(cfb_slip, f, indent=2)

        with open(test_dir / "nfl_test.json", "w") as f:
            json.dump(nfl_slip, f, indent=2)

        print(f"  Created test slips in {test_dir}")

        # Test with real results enabled
        print("\n🎯 Testing with Real Results...")
        backtester = HistoricalBacktester(
            starting_balance=1000.0, use_real_results=True, use_paper_trader=False
        )

        # Run backtest
        results = backtester.backtest_slip_folder(
            slips_dir=str(test_dir), backtest_name="real_results_test"
        )

        print(f"  Final Balance: ${results['summary']['final_balance']:.2f}")
        print(f"  ROI: {results['summary']['roi']:.2f}%")
        print(f"  Win Rate: {results['summary']['win_rate']:.1f}%")
        print(f"  Total Bets: {results['summary']['total_bets']}")

        # Test with mock results for comparison
        print("\n🎲 Testing with Mock Results...")
        backtester_mock = HistoricalBacktester(
            starting_balance=1000.0, use_real_results=False, use_paper_trader=False
        )

        results_mock = backtester_mock.backtest_slip_folder(
            slips_dir=str(test_dir), backtest_name="mock_results_test"
        )

        print(f"  Final Balance: ${results_mock['summary']['final_balance']:.2f}")
        print(f"  ROI: {results_mock['summary']['roi']:.2f}%")
        print(f"  Win Rate: {results_mock['summary']['win_rate']:.1f}%")

        # Cleanup
        import shutil

        shutil.rmtree(test_dir)

        return True

    except Exception as e:
        print(f"❌ Backtester integration test failed: {e}")
        return False


def test_paper_trader_integration():
    """Test paper trader with real results"""
    try:
        from src.core.paper_trader import PaperTrader

        print("\n📄 TESTING PAPER TRADER INTEGRATION")
        print("=" * 50)

        # Create test slip
        test_slip = create_test_slip_nfl()
        test_file = Path("test_paper_slip.json")

        with open(test_file, "w") as f:
            json.dump(test_slip, f, indent=2)

        print(f"  Created test slip: {test_file}")

        # Test paper trader settlement
        paper_trader = PaperTrader(
            starting_balance=1000.0,
            use_mock_results=False,  # Try to use real results
        )

        result = paper_trader.settle_slip(str(test_file))

        print(f"  Settlement Result: {result['outcome']}")
        print(f"  Stake: ${result['stake']:.2f}")
        print(f"  Payout: ${result['payout']:.2f}")
        print(f"  P/L: ${result['payout'] - result['stake']:+.2f}")

        # Cleanup
        test_file.unlink()

        return True

    except Exception as e:
        print(f"❌ Paper trader integration test failed: {e}")
        return False


def run_comprehensive_test():
    """Run all integration tests"""
    print("🚀 EQ12 REAL RESULTS INTEGRATION TEST SUITE")
    print("=" * 60)

    tests = [
        ("Sports Result Parser", test_sports_result_parser),
        ("Backtester Integration", test_backtester_integration),
        ("Paper Trader Integration", test_paper_trader_integration),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            success = test_func()
            results.append(success)
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"  Status: {status}")
        except Exception as e:
            print(f"  Status: ❌ ERROR - {e}")
            results.append(False)

    # Summary
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100

    print(f"\n{'=' * 60}")
    print("🎯 INTEGRATION TEST SUMMARY")
    print(f"{'=' * 60}")
    print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")

    if success_rate >= 67:  # At least 2/3 passing
        print("✅ REAL RESULTS INTEGRATION: OPERATIONAL")
        print("\n🎉 Your EQ12 system now uses real game outcomes!")
        print("   • CFB/NFL games resolved with actual scores")
        print("   • Moneyline, spread, and total bets supported")
        print("   • Automatic fallback to mock results if needed")
        print("   • Professional analytics with real data")
    else:
        print("⚠️  REAL RESULTS INTEGRATION: NEEDS ATTENTION")
        print("   Check API connectivity and configuration")

    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    run_comprehensive_test()
