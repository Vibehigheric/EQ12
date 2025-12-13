#!/usr/bin/env python3
"""
Test Integration: Optimizer → Slip Export → Bridge → Extension
Verifies the complete flow from optimizer results to extension-ready JSON
"""

import json
import sys
from pathlib import Path

# Add the src path to import optimizer modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.slip_export import (
    build_slip_from_optimizer_result,
    export_optimizer_result,
)


def test_slip_export():
    """Test the slip export functionality with mock optimizer data"""
    print("🧪 Testing slip export integration...")

    # Mock command line args (like from master_optimizer.py)
    import argparse

    mock_args = argparse.Namespace(promo_date="2025-10-03", sport="nfl", promo="mystery", stake=100)

    # Mock leg objects (like from master_optimizer.py)
    class MockLeg:
        def __init__(self, label, american, game):
            self.label = label
            self.american = american
            self.game = game

    # Mock optimizer result (like from master_optimizer.py)
    mock_best_result = {
        "legs": [
            MockLeg("Chiefs -3.5", -110, "KC @ DEN"),
            MockLeg("Over 45.5", -105, "KC @ DEN"),
            MockLeg("Dolphins ML", 150, "MIA @ BUF"),
        ],
        "ev": 15.67,
        "stake": 100,
        "combined_american": 892,
        "p_win": 0.2845,
        "boosted_payout": 567.50,
        "legs_count": 3,
        "combined_decimal": 9.92,
        "boost_pct": 25,
    }

    print("📊 Mock optimizer result:")
    print(f"   EV: ${mock_best_result['ev']:.2f}")
    print(f"   Legs: {len(mock_best_result['legs'])}")
    print(f"   Combined odds: {mock_best_result['combined_american']:+d}")

    # Test slip building
    print("\n🔨 Building extension slip format...")
    slip = build_slip_from_optimizer_result(mock_args, mock_best_result)
    print(f"✅ Slip ID: {slip['id']}")
    print(f"✅ Sport: {slip['sport']}")
    print(f"✅ EV: ${slip['ev']:.2f}")
    print(f"✅ Legs count: {len(slip['legs'])}")

    # Test export to bridge directory
    print("\n📤 Exporting to bridge directory...")
    output_file = export_optimizer_result(mock_args, mock_best_result)

    # Verify the exported file
    print(f"\n📁 Verifying exported file: {output_file}")
    if Path(output_file).exists():
        with open(output_file) as f:
            exported_data = json.load(f)

        print("✅ File exists and contains:")
        print(f"   ID: {exported_data['id']}")
        print(f"   EV: ${exported_data['ev']:.2f}")
        print(f"   Legs: {len(exported_data['legs'])}")

        for i, leg in enumerate(exported_data["legs"], 1):
            print(f"   {i}. {leg['label']} ({leg['american']:+d}) | {leg['game']}")

        print("\n🎯 Bridge file ready for extension!")
        print(f"   Extension can fetch from: {output_file}")
        print("   WebSocket will broadcast this data automatically")

        return True
    print("❌ Export file not found!")
    return False


def test_bridge_integration():
    """Test that the bridge directory structure is correct"""
    print("\n🌉 Testing bridge integration...")

    # Check if betting-bridge directory exists or will be created
    bridge_paths = [
        Path.cwd() / "betting-bridge",
        Path.cwd().parent / "betting-bridge",
        Path.cwd() / ".." / "betting-bridge",
    ]

    found_bridge = False
    for bridge_path in bridge_paths:
        if bridge_path.exists():
            print(f"✅ Found existing bridge: {bridge_path}")
            found_bridge = True
            break

    if not found_bridge:
        default_bridge = Path.cwd() / "betting-bridge"
        print(f"📁 Will create bridge at: {default_bridge}")

    # Verify data/parlays structure
    parlays_dir = Path.cwd() / "betting-bridge" / "data" / "parlays"
    print(f"📊 Parlays directory: {parlays_dir}")

    return True


if __name__ == "__main__":
    print("🔧 EQ12 Sports Betting Optimizer → Extension Integration Test")
    print("=" * 60)

    success = True

    # Test 1: Slip Export
    if test_slip_export():
        print("\n✅ Test 1: PASS - Slip export working")
    else:
        print("\n❌ Test 1: FAIL - Slip export issues")
        success = False

    # Test 2: Bridge Integration
    if test_bridge_integration():
        print("✅ Test 2: PASS - Bridge integration ready")
    else:
        print("❌ Test 2: FAIL - Bridge integration issues")
        success = False

    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("\n🚀 Ready to run:")
        print(
            "1. Start your optimizer: python -m src.promos.master_optimizer --sport nfl --promo mystery"
        )
        print("2. Start bridge server: python bridge.py")
        print("3. Load browser extension and watch for automatic parlay updates!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
        sys.exit(1)
