#!/usr/bin/env python3
"""
Extension Integration Setup
Quick setup for browser extension integration with existing optimizer
"""

import json
import subprocess
import sys
from pathlib import Path


def setup_bridge_directory():
    """Create betting-bridge directory structure"""
    print("📁 Setting up bridge directory...")

    # Create directory structure
    bridge_dir = Path("betting-bridge")
    bridge_dir.mkdir(exist_ok=True)

    (bridge_dir / "data" / "parlays").mkdir(parents=True, exist_ok=True)
    (bridge_dir / "config").mkdir(exist_ok=True)

    # Create basic server.py if it doesn't exist
    server_file = bridge_dir / "server.py"
    if not server_file.exists():
        server_code = '''#!/usr/bin/env python3
"""
Simple FastAPI bridge server for extension integration
"""

import json
import uvicorn
from fastapi import FastAPI, WebSocket
from pathlib import Path

app = FastAPI()
parlays_dir = Path("data/parlays")

@app.get("/parlays/latest.json")
async def get_latest_parlay():
    """Serve latest parlay for extension"""
    latest_file = parlays_dir / "latest.json"
    if latest_file.exists():
        with open(latest_file) as f:
            return json.load(f)
    return {"error": "No parlay available"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    await websocket.send_text(json.dumps({
        "type": "connected",
        "message": "Bridge server connected"
    }))

    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except Exception:
        pass

if __name__ == "__main__":
    print("🚀 Starting bridge server on http://localhost:8000")
    uvicorn.run(app, host="localhost", port=8000)
'''
        with open(server_file, "w") as f:
            f.write(server_code)

    # Create config file
    config_file = bridge_dir / "config" / "credentials.json"
    if not config_file.exists():
        config = {"bridge": {"token": "your_secret_token_here"}}
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

    print(f"✅ Bridge directory created: {bridge_dir.absolute()}")
    return bridge_dir


def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")

    packages = ["fastapi", "uvicorn", "websockets"]

    try:
        for package in packages:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                check=True,
                capture_output=True,
            )
        print("✅ Dependencies installed")

    except subprocess.CalledProcessError as e:
        print(f"❌ Dependency installation failed: {e}")
        return False

    return True


def test_integration():
    """Test the extension integration"""
    print("🧪 Testing integration...")

    try:
        # Run the test script
        result = subprocess.run(
            [sys.executable, "test_extension_integration.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("✅ Integration test passed")
            return True
        print(f"❌ Integration test failed: {result.stderr}")
        return False

    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


def create_usage_guide():
    """Create usage guide"""
    guide = """
# 🎯 Extension Integration - Usage Guide

## Quick Start

1. **Start Bridge Server:**
   ```bash
   cd betting-bridge
   python server.py
   ```

2. **Load Browser Extension:**
   - Chrome: chrome://extensions/ → Load Unpacked
   - Firefox: about:debugging → Load Temporary Add-on

3. **Run Your Optimizer:**
   ```bash
   python -m src.promos.master_optimizer --sport nfl --promo mystery --token 25
   ```

4. **Check Extension:**
   - Extension should show notification
   - Click extension icon to see parlay
   - Navigate to DraftKings and apply to bet slip

## Files Created

- `betting-bridge/` - Bridge server directory
- `betting-bridge/data/parlays/latest.json` - Latest parlay (auto-generated)
- `betting-bridge/server.py` - Simple FastAPI server
- `src/extension_slip_exporter.py` - Export module
- `test_extension_integration.py` - Integration test

## Troubleshooting

- **No parlay in extension:** Check that latest.json exists in betting-bridge/data/parlays/
- **Extension not connecting:** Make sure server.py is running on localhost:8000
- **Import errors:** Run from optimizer root directory

## Extension Features

- Real-time parlay notifications
- One-click DraftKings bet slip filling
- Professional popup interface
- Cross-browser compatibility (Chrome + Firefox)

Your optimizer now automatically exports slips to the browser extension!
"""

    with open("EXTENSION_USAGE.md", "w") as f:
        f.write(guide.strip())

    print("📋 Usage guide created: EXTENSION_USAGE.md")


def main():
    """Main setup function"""
    print("🎯 EXTENSION INTEGRATION SETUP")
    print("=" * 40)

    # Check if we're in the optimizer directory
    if not (Path("src") / "promos" / "master_optimizer.py").exists():
        print("❌ Please run from the sports-betting-optimizer root directory")
        sys.exit(1)

    # Setup bridge directory
    bridge_dir = setup_bridge_directory()

    # Install dependencies
    if not install_dependencies():
        print("⚠️  Dependency installation failed - manual installation required")

    # Test integration
    test_passed = test_integration()

    # Create usage guide
    create_usage_guide()

    # Summary
    print("\n" + "=" * 40)
    print("🎉 SETUP COMPLETE")
    print("=" * 40)

    if test_passed:
        print("✅ Integration working correctly")
    else:
        print("⚠️  Some tests failed - check logs above")

    print(f"\n📁 Bridge directory: {bridge_dir.absolute()}")
    print("📋 Usage guide: EXTENSION_USAGE.md")

    print("\n🚀 Next Steps:")
    print("1. Start bridge server: cd betting-bridge && python server.py")
    print("2. Load extension in browser (see EXTENSION_USAGE.md)")
    print("3. Run optimizer - parlays will auto-export to extension!")


if __name__ == "__main__":
    main()
