#!/usr/bin/env python3
"""
Sports Betting Extension Launcher
Starts WebSocket bridge and integrates with existing optimizer
"""

import asyncio
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """Check and install required dependencies"""
    try:
        import websockets

        print("✅ WebSockets available")
    except ImportError:
        print("📦 Installing websockets...")
        subprocess.run([sys.executable, "-m", "pip", "install", "websockets"])

    try:
        import watchdog

        print("✅ Watchdog available")
    except ImportError:
        print("📦 Installing watchdog...")
        subprocess.run([sys.executable, "-m", "pip", "install", "watchdog"])


def find_optimizer_repo():
    """Find the sports betting optimizer repository"""
    current_dir = Path.cwd()

    search_paths = [
        current_dir / "sports-betting-optimizer",
        current_dir.parent / "sports-betting-optimizer",
        current_dir / ".." / "sports-betting-optimizer",
    ]

    for path in search_paths:
        if path.exists() and (path / "src" / "promos" / "master_optimizer.py").exists():
            return path.resolve()

    return None


def patch_optimizer_for_extension(optimizer_path: Path):
    """Add extension integration to existing optimizer"""

    master_optimizer_file = optimizer_path / "src" / "promos" / "master_optimizer.py"

    if not master_optimizer_file.exists():
        return False

    # Read current content
    with open(master_optimizer_file) as f:
        content = f.read()

    # Check if already patched
    if "# EXTENSION_INTEGRATION_PATCH" in content:
        print("✅ Optimizer already patched for extension")
        return True

    # Add integration code
    integration_code = '''
# EXTENSION_INTEGRATION_PATCH - Auto-generated
try:
    import asyncio
    import json
    import websockets
    from datetime import datetime, timezone

    async def push_to_extension(parlay_data):
        """Push parlay to browser extension"""
        try:
            async with websockets.connect("ws://localhost:8765", timeout=2) as ws:
                message = {
                    "type": "new_parlay",
                    "parlay": {
                        "sport": parlay_data.get("sport", "nfl"),
                        "promo_type": parlay_data.get("promo_type", "mystery"),
                        "ev": f"+{parlay_data.get('ev', 0):.1f}%",
                        "stake": parlay_data.get("stake", 100),
                        "legs": parlay_data.get("legs", []),
                        "boost_percentage": parlay_data.get("boost", 0),
                        "potential_payout": f"${parlay_data.get('payout', 0):.0f}",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                }
                await ws.send(json.dumps(message))
                print("📱 Parlay sent to extension")
        except:
            pass  # Silent fail if extension not available

    EXTENSION_INTEGRATION = True
except ImportError:
    EXTENSION_INTEGRATION = False
    async def push_to_extension(data): pass
# END EXTENSION_INTEGRATION_PATCH
'''

    # Find best place to insert (after imports, before main functions)
    lines = content.split("\n")
    insert_pos = 0

    for i, line in enumerate(lines):
        if line.startswith("def ") or line.startswith("class ") or line.startswith("if __name__"):
            insert_pos = i
            break

    # Insert integration code
    lines.insert(insert_pos, integration_code)

    # Write back to file
    with open(master_optimizer_file, "w") as f:
        f.write("\n".join(lines))

    print(f"✅ Patched optimizer: {master_optimizer_file}")
    return True


async def start_bridge_server():
    """Start the WebSocket bridge server"""
    try:
        from enhanced_bridge import EnhancedBettingBridge

        bridge = EnhancedBettingBridge()
        print("🚀 Starting enhanced bridge with optimizer integration...")
        await bridge.start()

    except ImportError:
        # Fall back to simple bridge
        from simple_bridge import SimpleBettingBridge

        bridge = SimpleBettingBridge()
        print("🚀 Starting simple bridge (mock data mode)...")
        await bridge.start()


def print_setup_instructions():
    """Print setup instructions for the extension"""
    print("\n" + "=" * 60)
    print("🎯 SPORTS BETTING EXTENSION SETUP")
    print("=" * 60)
    print("1. Install Browser Extension:")
    print("   Chrome: chrome://extensions/ → Load Unpacked")
    print("   Firefox: about:debugging → Load Temporary Add-on")
    print()
    print("2. Extension Features:")
    print("   📱 Real-time parlay notifications")
    print("   🎯 One-click DraftKings bet slip filling")
    print("   ⚙️  Configurable sports/promos/stakes")
    print("   🔄 Live connection status")
    print()
    print("3. Usage:")
    print("   • Navigate to sportsbook.draftkings.com")
    print("   • Click extension icon in toolbar")
    print("   • Request parlay or wait for auto-generation")
    print("   • Review parlay details")
    print("   • Click 'Apply to Bet Slip' for auto-fill")
    print()
    print("4. Keyboard Shortcuts:")
    print("   • Ctrl+Shift+B: Toggle extension overlay")
    print("   • Ctrl+Enter: Apply current parlay (when popup open)")
    print("=" * 60)


async def main():
    """Main launcher function"""
    print("🎯 Sports Betting Extension Launcher")
    print("=" * 40)

    # Check dependencies
    print("📋 Checking dependencies...")
    check_dependencies()

    # Find optimizer
    optimizer_path = find_optimizer_repo()

    if optimizer_path:
        print(f"✅ Found optimizer: {optimizer_path}")

        # Patch optimizer for extension integration
        if patch_optimizer_for_extension(optimizer_path):
            print("✅ Optimizer integration ready")
        else:
            print("⚠️  Could not patch optimizer - manual integration required")
    else:
        print("⚠️  Optimizer repo not found - using mock data mode")

    print("\n🚀 Starting WebSocket bridge server...")

    # Print setup instructions
    print_setup_instructions()

    print("\n🔌 WebSocket server starting on ws://localhost:8765")
    print("💡 Keep this terminal open while using the extension")
    print("🛑 Press Ctrl+C to stop\n")

    # Start the bridge server
    try:
        await start_bridge_server()
    except KeyboardInterrupt:
        print("\n🛑 Bridge server stopped")
    except Exception as e:
        print(f"\n❌ Server error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
