#!/usr/bin/env python3
"""
EQ12 Complete Sports Betting Setup
Sets up the complete integrated system: optimizer + extension + Discord + bankroll
"""

import sys
from pathlib import Path


def create_env_template():
    """Create .env template for easy configuration"""
    env_template = """# EQ12 Sports Betting Configuration
# Copy this to .env and fill in your values

# API Keys
ODDS_API_KEY=your_odds_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Discord Integration
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Bankroll Settings
STARTING_BALANCE=1000.0
DISCORD_NOTIFICATIONS=true

# Extension Settings
BRIDGE_PORT=8000
EXTENSION_AUTO_FILL=true

# Notification Settings
NOTIFY_NEW_PARLAYS=true
NOTIFY_SETTLEMENTS=true
DAILY_SUMMARY=true
"""

    env_file = Path(".env.template")
    with open(env_file, "w") as f:
        f.write(env_template)

    print(f"📋 Created environment template: {env_file}")
    print("   Copy to .env and fill in your values")


def setup_discord_webhook():
    """Interactive Discord webhook setup"""
    print("\n🎮 Discord Integration Setup")
    print("=" * 40)

    print("To set up Discord notifications:")
    print("1. Create a Discord server or use existing one")
    print("2. Go to Server Settings > Integrations > Webhooks")
    print("3. Create New Webhook")
    print("4. Copy the webhook URL")
    print("5. Set DISCORD_WEBHOOK_URL in your .env file")
    print()

    webhook_url = input("Enter Discord webhook URL (or press Enter to skip): ").strip()

    if webhook_url:
        # Test the webhook
        try:
            import requests

            test_payload = {
                "embeds": [
                    {
                        "title": "🚀 EQ12 Setup Complete!",
                        "description": "Your sports betting optimizer is ready to go!",
                        "color": 0x00FF00,
                        "fields": [
                            {"name": "Status", "value": "✅ Ready", "inline": True},
                            {
                                "name": "Features",
                                "value": "Optimizer + Extension + Discord",
                                "inline": True,
                            },
                        ],
                    }
                ]
            }

            response = requests.post(webhook_url, json=test_payload, timeout=10)
            if response.status_code == 204:
                print("✅ Discord webhook test successful!")

                # Save to .env file
                env_file = Path(".env")
                if env_file.exists():
                    content = env_file.read_text()
                    if "DISCORD_WEBHOOK_URL=" in content:
                        # Update existing
                        lines = content.split("\n")
                        for i, line in enumerate(lines):
                            if line.startswith("DISCORD_WEBHOOK_URL="):
                                lines[i] = f"DISCORD_WEBHOOK_URL={webhook_url}"
                                break
                        content = "\n".join(lines)
                    else:
                        # Add new
                        content += f"\nDISCORD_WEBHOOK_URL={webhook_url}\n"

                    env_file.write_text(content)
                    print("💾 Discord webhook saved to .env file")
                else:
                    # Create new .env file
                    env_file.write_text(f"DISCORD_WEBHOOK_URL={webhook_url}\n")
                    print("💾 Created .env file with Discord webhook")

                return True
            print(f"❌ Discord webhook test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Discord webhook test error: {e}")

    return False


def create_launch_script():
    """Create convenient launch scripts"""

    # Windows batch script
    batch_script = """@echo off
echo 🚀 EQ12 Sports Betting System
echo ============================

echo Starting Python optimizer...
python -m src.promos.master_optimizer --sport nfl --promo mystery --promo-date 2025-10-03 --token 25

echo.
echo Starting bridge server...
cd ../sports-betting-extension
start python bridge.py

echo.
echo System ready! Load the browser extension and check Discord for notifications.
pause
"""

    with open("launch_eq12.bat", "w") as f:
        f.write(batch_script)

    # PowerShell script
    ps_script = """# EQ12 Sports Betting System Launcher
Write-Host "🚀 EQ12 Sports Betting System" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green

Write-Host "`nStarting Python optimizer..." -ForegroundColor Yellow
python -m src.promos.master_optimizer --sport nfl --promo mystery --promo-date 2025-10-03 --token 25

Write-Host "`nStarting bridge server..." -ForegroundColor Yellow
Set-Location "../sports-betting-extension"
Start-Process python -ArgumentList "bridge.py" -WindowStyle Normal

Write-Host "`nSystem ready! Load the browser extension and check Discord for notifications." -ForegroundColor Green
"""

    with open("launch_eq12.ps1", "w") as f:
        f.write(ps_script)

    # Python launch script
    py_script = """#!/usr/bin/env python3
'''
EQ12 Complete System Launcher
Starts optimizer, bridge server, and opens browser extension guide
'''

import subprocess
import sys
import webbrowser
import time
from pathlib import Path

def main():
    print("🚀 EQ12 Sports Betting System")
    print("============================")

    # Check if we're in the right directory
    if not Path("src/promos/master_optimizer.py").exists():
        print("❌ Please run from the sports-betting-optimizer directory")
        sys.exit(1)

    # Run optimizer
    print("\\n📊 Running optimizer...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "src.promos.master_optimizer",
            "--sport", "nfl",
            "--promo", "mystery",
            "--promo-date", "2025-10-03",
            "--token", "25"
        ], check=True)
        print("✅ Optimizer completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Optimizer failed: {e}")
        return

    # Start bridge server
    print("\\n🌉 Starting bridge server...")
    bridge_dir = Path("../sports-betting-extension")
    if bridge_dir.exists():
        try:
            subprocess.Popen([
                sys.executable, "bridge.py"
            ], cwd=bridge_dir)
            print("✅ Bridge server started")
        except Exception as e:
            print(f"❌ Failed to start bridge server: {e}")
    else:
        print("⚠️ Bridge directory not found")

    # Open extension guide
    print("\\n📖 Opening browser extension guide...")
    time.sleep(2)

    extension_dir = Path("../sports-betting-extension")
    if (extension_dir / "README.md").exists():
        try:
            webbrowser.open((extension_dir / "README.md").as_uri())
        except:
            pass

    print("\\n🎉 EQ12 System is ready!")
    print("1. Load the browser extension")
    print("2. Check Discord for notifications")
    print("3. Run 'python settle_bets.py' to manage your bankroll")

if __name__ == "__main__":
    main()
"""

    with open("launch_eq12.py", "w") as f:
        f.write(py_script)

    print("📝 Created launch scripts:")
    print("   - launch_eq12.bat (Windows)")
    print("   - launch_eq12.ps1 (PowerShell)")
    print("   - launch_eq12.py (Python)")


def create_quick_setup_guide():
    """Create a quick setup guide"""

    guide = """# 🚀 EQ12 Quick Setup Guide

## 📋 Prerequisites
1. Python 3.8+ installed
2. Git (for cloning repos)
3. Chrome or Firefox browser
4. Discord account (for notifications)

## ⚡ Quick Start (5 minutes)

### 1️⃣ Install Dependencies
```bash
pip install requests websockets fastapi uvicorn
```

### 2️⃣ Set up Environment
```bash
# Copy template and edit
cp .env.template .env
# Edit .env with your API keys and Discord webhook
```

### 3️⃣ Test the System
```bash
# Run optimizer
python -m src.promos.master_optimizer --sport nfl --promo mystery --promo-date 2025-10-03 --token 25

# In another terminal, start bridge server
cd ../sports-betting-extension
python bridge.py

# Load browser extension from sports-betting-extension folder
```

### 4️⃣ Manage Your Bankroll
```bash
# Interactive settlement
python settle_bets.py --interactive

# Quick commands
python settle_bets.py --list  # Show pending bets
python settle_bets.py --stats # Show bankroll stats
```

## 🔧 Advanced Configuration

### Discord Integration
1. Create Discord server webhook
2. Set `DISCORD_WEBHOOK_URL` in .env
3. Automatic notifications for new parlays and settlements

### Browser Extension
1. Open Chrome/Firefox
2. Go to Extensions > Developer Mode
3. Load Unpacked > Select sports-betting-extension folder
4. Extension will auto-connect to bridge server

### Bankroll Tracking
- Automatic tracking of all bets
- Win/loss settlement with Discord notifications
- ROI and performance statistics
- CSV export for analysis

## 🎯 Daily Workflow

1. **Morning**: Run optimizer for today's games
   ```bash
   python -m src.promos.master_optimizer --sport nfl --promo mystery --promo-date $(date +%Y-%m-%d) --token 25
   ```

2. **Check Extension**: New parlay appears automatically in browser

3. **Place Bets**: Use extension to auto-fill sportsbook bet slips

4. **Evening**: Settle completed bets
   ```bash
   python settle_bets.py --interactive
   ```

5. **Check Stats**: Review performance
   ```bash
   python settle_bets.py --stats
   ```

## 📊 Files Created

- `betting-bridge/data/parlays/latest.json` - Latest parlay for extension
- `betting-bridge/data/bankroll.csv` - Complete betting history
- `logs/` - Detailed logs and snapshots

## 🆘 Troubleshooting

### Optimizer Issues
- Check ODDS_API_KEY in .env
- Verify date format (YYYY-MM-DD)
- Ensure games are available for the date

### Extension Issues
- Check bridge server is running (python bridge.py)
- Verify WebSocket connection in browser console
- Reload extension if connection lost

### Discord Issues
- Test webhook URL in Discord server settings
- Check DISCORD_WEBHOOK_URL in .env
- Verify server permissions

### Bankroll Issues
- Check CSV file permissions
- Verify slip IDs match exactly
- Use interactive mode for complex settlements

## 🎉 You're Ready!

Your EQ12 system now includes:
- ✅ Automated parlay optimization
- ✅ Real-time browser extension integration
- ✅ Discord notifications
- ✅ Complete bankroll tracking
- ✅ Win/loss settlement tools
- ✅ Performance analytics

Happy betting! 🎯
"""

    with open("QUICK_START.md", "w") as f:
        f.write(guide)

    print("📖 Created QUICK_START.md guide")


def main():
    """Main setup function"""
    print("🚀 EQ12 Complete Sports Betting Setup")
    print("=" * 50)

    print("Setting up integrated system...")

    # Create directory structure
    directories = ["betting-bridge/data/parlays", "logs"]

    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {dir_path}")

    # Create configuration files
    create_env_template()
    create_launch_script()
    create_quick_setup_guide()

    # Optional Discord setup
    print()
    setup_discord = input("Set up Discord notifications now? (y/n): ").strip().lower()
    if setup_discord in ["y", "yes"]:
        setup_discord_webhook()

    # Test import
    print("\n🧪 Testing imports...")
    try:
        sys.path.insert(0, "src")
        from src.core.bankroll_tracker import BankrollTracker
        from src.core.discord_integration import DiscordIntegration
        from src.core.slip_export import export_slip

        print("✅ All modules import successfully")
    except ImportError as e:
        print(f"⚠️ Import issue: {e}")
        print("   This is normal if dependencies aren't installed yet")

    print("\n🎉 Setup Complete!")
    print("\nNext Steps:")
    print("1. Install dependencies: pip install requests websockets fastapi uvicorn")
    print("2. Set up your .env file with API keys")
    print("3. Run: python launch_eq12.py")
    print("4. Load the browser extension")
    print("5. Check Discord for notifications")
    print("\n📖 See QUICK_START.md for detailed instructions")


if __name__ == "__main__":
    main()
