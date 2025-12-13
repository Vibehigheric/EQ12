#!/usr/bin/env python3
"""
Test Extension Integration
Verifies that optimizer exports slips correctly to bridge format
"""

import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from extension_slip_exporter import ExtensionSlipExporter

    # Test the exporter
    print("🧪 Testing Extension Slip Exporter...")

    exporter = ExtensionSlipExporter()
    print(f"✅ Bridge path: {exporter.bridge_path}")

    # Create mock optimizer result (matching your Leg dataclass)
    class MockLeg:
        def __init__(self, label, american, game):
            self.label = label
            self.american = american
            self.game = game

    mock_result = {
        "legs": [
            MockLeg("Chiefs -3.5", -110, "KC @ DEN"),
            MockLeg("Over 45.5", -105, "KC @ DEN"),
            MockLeg("Mahomes 2+ TDs", 120, "KC @ DEN"),
        ],
        "ev": 12.34,
        "stake": 100,
        "combined_american": 264,
        "p_win": 0.3785,
        "boosted_payout": 425.0,
        "boost_pct": 25,
    }

    # Test export
    slip_data = exporter.export_parlay(
        optimizer_result=mock_result,
        sport="nfl",
        promo_type="mystery",
        promo_date="2025-10-03",
    )

    print("\n📄 Generated slip data:")
    print(json.dumps(slip_data, indent=2))

    # Verify files were created
    latest_file = exporter.export_dir / "latest.json"
    if latest_file.exists():
        print(f"✅ Latest slip file: {latest_file}")

        with open(latest_file) as f:
            saved_data = json.load(f)

        print("📋 Saved data preview:")
        print(f"   ID: {saved_data['id']}")
        print(f"   Sport: {saved_data['sport']}")
        print(f"   EV: ${saved_data['ev']}")
        print(f"   Legs: {saved_data['legs_count']}")

        for i, leg in enumerate(saved_data["legs"], 1):
            print(f"     {i}. {leg['label']} ({leg['american']:+d}) | {leg['game']}")

    else:
        print("❌ Latest slip file not created")

    print("\n🎯 Integration Test Complete!")
    print("Your optimizer will now automatically export slips for the browser extension.")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the optimizer root directory.")
except Exception as e:
    print(f"❌ Test failed: {e}")

print("\n📋 Next Steps:")
print(
    "1. Run your optimizer: python -m src.promos.master_optimizer --sport nfl --promo mystery --token 25"
)
print("2. Check that latest.json is created in betting-bridge/data/parlays/")
print("3. Start the bridge server and load the browser extension")
print("4. Extension should receive the parlay automatically!")
