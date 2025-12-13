#!/usr/bin/env python3
"""
EQ12 Sports Betting Integration Setup
One-command setup for optimizer → extension bridge integration
"""

import sys
from pathlib import Path


def setup_integration():
    """Setup complete optimizer → extension integration"""
    print("🔧 EQ12 Sports Betting Integration Setup")
    print("=" * 50)

    # Verify we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / "src" / "promos" / "master_optimizer.py").exists():
        print("❌ Please run this from the sports-betting-optimizer directory")
        print(f"   Current: {current_dir}")
        print("   Expected: Contains src/promos/master_optimizer.py")
        return False

    print("✅ Found optimizer directory")

    # Check core slip export
    slip_export_path = current_dir / "src" / "core" / "slip_export.py"
    if slip_export_path.exists():
        print("✅ Found slip export helper")
    else:
        print("❌ Missing src/core/slip_export.py")
        return False

    # Create bridge directory structure
    bridge_dir = current_dir / "betting-bridge"
    parlays_dir = bridge_dir / "data" / "parlays"
    parlays_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created bridge directory: {bridge_dir}")

    # Verify master_optimizer integration
    master_optimizer_path = current_dir / "src" / "promos" / "master_optimizer.py"
    with open(master_optimizer_path) as f:
        content = f.read()

    if "slip_export" in content and "export_optimizer_result" in content:
        print("✅ Master optimizer has extension integration")
    else:
        print("❌ Master optimizer missing integration code")
        return False

    print("\n🎯 Integration Setup Complete!")
    print("\nNext Steps:")
    print("1️⃣  Test the integration:")
    print("   python test_integration_complete.py")
    print("\n2️⃣  Run optimizer with automatic export:")
    print("   python -m src.promos.master_optimizer --sport nfl --promo mystery")
    print("\n3️⃣  Start bridge server (in sports-betting-extension):")
    print("   python bridge.py")
    print("\n4️⃣  Load browser extension and enjoy automatic parlay updates!")

    return True


def test_quick_export():
    """Quick test of the slip export functionality"""
    print("\n🧪 Quick Export Test...")

    try:
        sys.path.insert(0, str(Path.cwd() / "src"))
        from src.core.slip_export import export_slip

        # Test data
        test_slip = {
            "id": "2025-10-03-test",
            "sport": "nfl",
            "ev": 12.34,
            "stake": 100,
            "legs": [{"label": "Test ML", "american": 150, "game": "TEST @ GAME"}],
        }

        # Export test slip
        output = export_slip(test_slip)
        if Path(output).exists():
            print(f"✅ Test export successful: {output}")
            return True
        print(f"❌ Test export failed: {output}")
        return False

    except Exception as e:
        print(f"❌ Test export error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Setting up EQ12 Optimizer → Extension Integration...")

    if setup_integration():
        if test_quick_export():
            print("\n🎉 SETUP COMPLETE!")
            print("Your optimizer will now automatically export parlays to the extension!")
        else:
            print("\n⚠️  Setup complete but test failed")
    else:
        print("\n❌ Setup failed - check the errors above")
        sys.exit(1)
