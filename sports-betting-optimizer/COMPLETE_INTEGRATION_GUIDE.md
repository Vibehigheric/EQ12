# 🎮💰 EQ12 Complete Integration Guide

## Discord + Bankroll + Extension + Settlement System

This guide shows you how to use the **complete integrated EQ12 sports betting system** with Discord notifications, automatic bankroll tracking, browser extension integration, and settlement tools.

---

## 🚀 What's New in the Complete System

### 📈 Enhanced Features Added:
1. **🎮 Discord Integration** - Real-time notifications for parlays and settlements
2. **💰 Bankroll Tracker** - Automatic P/L tracking with settlement tools
3. **⚖️ Settlement CLI** - Interactive bet settlement with Discord notifications
4. **🌉 Enhanced Bridge** - Improved WebSocket communication
5. **📊 Analytics Dashboard** - ROI, win rate, and performance metrics

---

## ⚡ Quick Integration Setup

### 1️⃣ Run Complete Setup
```bash
# In your sports-betting-optimizer directory
python setup_complete_system.py
```

This creates:
- 📁 `betting-bridge/data/` directory structure
- 📋 `.env.template` with all configuration options
- 🚀 Launch scripts (Python, PowerShell, Batch)
- 📖 `QUICK_START.md` guide

### 2️⃣ Configure Discord (Optional)
```bash
# Set up Discord webhook interactively
python setup_complete_system.py
# Choose 'y' when prompted for Discord setup

# OR manually add to .env:
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_here
```

### 3️⃣ Test Integration
```bash
# Test all components
python -m src.core.bankroll_tracker      # Test bankroll
python -m src.core.discord_integration   # Test Discord
python -m src.core.slip_export           # Test export

# Run full test
python test_integration_complete.py
```

---

## 🔄 New Workflow (Fully Automated)

### Morning: Run Optimizer
```bash
python -m src.promos.master_optimizer --sport nfl --promo mystery --promo-date 2025-10-03 --token 25
```

**What happens automatically:**
1. 📊 Optimizer finds best EV parlay
2. 📤 **Exports to bridge** → `betting-bridge/data/parlays/latest.json`
3. 💰 **Logs to bankroll** → `betting-bridge/data/bankroll.csv` (pending status)
4. 🎮 **Discord notification** → "🎯 New Optimal Parlay Found!"
5. 📱 **Extension alert** → Browser notification with parlay details

### Midday: Extension Integration
1. **Start bridge server**: `python bridge.py` (in sports-betting-extension folder)
2. **Load browser extension** (Chrome/Firefox)
3. **Automatic notification** when new parlay available
4. **One-click bet slip filling** on DraftKings/FanDuel

### Evening: Settlement
```bash
# Interactive settlement mode
python settle_bets.py --interactive

# Or quick settlement
python settle_bets.py --settle "2025-10-03-nfl-mystery" --result won --payout 250
```

**What happens automatically:**
1. ✅ **Bankroll updated** with win/loss and new balance
2. 🎮 **Discord notification** → "✅ Slip Settled: WON"
3. 📊 **Statistics recalculated** (ROI, win rate, etc.)

---

## 🎮 Discord Integration Details

### Notification Types

#### 🎯 New Parlay Alert
```
🎯 New Optimal Parlay Found!
Sport: NFL
Expected Value: $25.75
Win Probability: 34.2%
Boosted Payout: $425.00

🎲 Parlay Legs (3 total)
1. Chiefs -3.5 (-110)
2. Over 45.5 (-105)
3. Dolphins ML (+150)
```

#### ✅ Settlement Notification
```
✅ Slip Settled: WON
Result: WON
Profit/Loss: $350.00
New Balance: $1,350.00
ROI: 35.0%
```

#### 📊 Daily Summary
```
📊 Daily Bankroll Summary
Total Slips: 15 | Pending: 3 | Settled: 12
Won: 8 (66.7%) | Lost: 4 | Push: 0
Current Balance: $1,250.75
Total P/L: $250.75 | ROI: 12.5%
```

### Discord Quest Integration
Based on Discord's Quest system, the integration includes achievement-style notifications:
- 🎯 **Daily Bet Quest**: Complete daily optimization
- 💎 **Big Win Achievement**: Celebrate wins over $500
- 🔥 **Streak Tracker**: Win streaks of 3+ bets
- 🆕 **New Sport Explorer**: Try different sports

---

## 💰 Bankroll Management

### Automatic Tracking Features

#### CSV Structure
```csv
timestamp,id,sport,stake,ev,result,payout,profit_loss,balance,roi
2025-10-03T15:00:00,2025-10-03-nfl-mystery,nfl,100,25.75,pending,0,0,1000,0
2025-10-03T22:30:00,2025-10-03-nfl-mystery,nfl,100,25.75,won,425,325,1325,32.5
```

#### Statistics Tracked
- **Current Balance**: Real-time bankroll amount
- **Total Wagered**: Sum of all stakes
- **Profit/Loss**: Net earnings across all bets
- **ROI**: Return on investment percentage
- **Win Rate**: Percentage of winning bets
- **Pending Count**: Bets awaiting settlement

### Settlement CLI Tools

#### Interactive Mode
```bash
$ python settle_bets.py --interactive

⚖️ EQ12 Bet Settlement CLI
========================================
🎮 Interactive Settlement Mode
Type 'help' for commands, 'quit' to exit

EQ12> list
📋 Pending Slips:
----------------
1. ID: 2025-10-03-nfl-mystery
   Sport: NFL
   Stake: $100.00
   Expected Value: $25.75
   Date: 2025-10-03

EQ12> won 2025-10-03-nfl-mystery 425
✅ Settlement successful!
   Result: WON
   Profit/Loss: $325.00
   New Balance: $1,325.00
🎮 Discord notification sent: settled

EQ12> stats
📊 Bankroll Statistics:
==================================================
💰 Current Balance: $1,325.00
📊 Total Slips: 1
⏳ Pending: 0
✅ Settled: 1

🏆 Performance:
   Won: 1 (100.0%)
   Lost: 0
   Push: 0

💸 Total Wagered: $100.00
📈 Total P/L: $325.00
📊 ROI: 325.00%
```

#### Command Reference
```bash
# Settlement commands
EQ12> won SLIP_ID PAYOUT_AMOUNT     # Mark as won
EQ12> lost SLIP_ID                  # Mark as lost
EQ12> push SLIP_ID                  # Mark as push (tie)

# Information commands
EQ12> list                          # Show pending bets
EQ12> stats                         # Show statistics
EQ12> help                          # Show all commands
EQ12> quit                          # Exit program
```

---

## 🌉 Bridge Server Enhancement

### New Features
- **File Watching**: Automatically detects new parlay exports
- **WebSocket Broadcasting**: Pushes updates to all connected extensions
- **HTTP API**: REST endpoints for manual polling
- **CORS Support**: Cross-origin requests from extensions
- **Error Handling**: Graceful failure recovery

### API Endpoints
```bash
# REST API
GET /parlays/latest.json           # Get latest parlay
GET /bankroll/stats               # Get bankroll statistics
GET /health                       # Server health check

# WebSocket
ws://localhost:8000/ws            # Real-time parlay updates
```

### Starting the Bridge
```bash
cd ../sports-betting-extension
python bridge.py

# Output:
🌉 EQ12 Bridge Server Starting...
📁 Monitoring: betting-bridge/data/parlays/
🔌 WebSocket server: ws://localhost:8000/ws
📡 HTTP server: http://localhost:8000
✅ Server ready for connections!
```

---

## 📱 Enhanced Browser Extension

### New Capabilities
- **Automatic Notifications**: Desktop alerts for new parlays
- **Settlement Tracking**: Shows pending vs settled bets
- **Performance Display**: Win rate and ROI in popup
- **Multi-Sportsbook**: Support for DraftKings, FanDuel, BetMGM
- **Safety Checks**: Confirms odds before auto-filling

### Extension Popup Interface
```
┌─────────────────────────────────┐
│ 🎯 EQ12 Sports Betting         │
├─────────────────────────────────┤
│ 📊 Latest Parlay               │
│ Sport: NFL | EV: $25.75        │
│ Win%: 34.2% | Payout: $425     │
│                                 │
│ [📋 View Details] [🎰 Apply]    │
├─────────────────────────────────┤
│ 💰 Bankroll Status             │
│ Balance: $1,325.00             │
│ Pending: 2 | ROI: 15.5%       │
│                                 │
│ [⚖️ Settle Bets] [📊 Stats]     │
└─────────────────────────────────┘
```

---

## 🔧 Advanced Configuration

### Environment Variables (.env)
```bash
# Core API Keys
ODDS_API_KEY=your_odds_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Discord Integration
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Bankroll Settings
STARTING_BALANCE=1000.0
NOTIFY_SETTLEMENTS=true
DAILY_SUMMARY=true

# Bridge Server
BRIDGE_PORT=8000
CORS_ORIGINS=chrome-extension://*,moz-extension://*

# Optimization Settings
MIN_PER_LEG_DECIMAL=1.2
MAX_LEGS=5
ALLOW_WHOLE_LINES=false
```

### Custom Notification Settings
```python
# Custom Discord integration
from src.core.discord_integration import DiscordIntegration

discord = DiscordIntegration()

# Send custom achievement
discord.create_quest_notification(
    quest_type="profit_streak",
    description="5 winning bets in a row! You're on fire! 🔥"
)

# Send daily summary with custom data
custom_stats = {
    "total_slips": 50,
    "win_rate": 68.5,
    "roi": 24.3,
    "total_profit_loss": 1250.75
}
discord.send_daily_summary(custom_stats)
```

---

## 🛠️ Troubleshooting Integration

### Common Issues

#### 🔴 "Import Error" when running scripts
**Solution:**
```bash
# Ensure you're in the sports-betting-optimizer directory
cd sports-betting-optimizer

# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or use module syntax
python -m src.promos.master_optimizer
```

#### 🔴 Discord notifications not working
**Solution:**
```bash
# Test webhook manually
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test message"}'

# Verify .env file
cat .env | grep DISCORD_WEBHOOK_URL

# Test Python integration
python -c "
from src.core.discord_integration import DiscordIntegration
discord = DiscordIntegration()
print('Testing...')
# This will send a test message if webhook is configured
"
```

#### 🔴 Bankroll CSV permission errors
**Solution:**
```bash
# Check permissions
ls -la betting-bridge/data/bankroll.csv

# Fix permissions (Linux/Mac)
chmod 644 betting-bridge/data/bankroll.csv

# Windows: Right-click → Properties → Security → Full Control
```

#### 🔴 Extension not receiving WebSocket updates
**Solution:**
```bash
# Check bridge server is running
ps aux | grep bridge.py

# Test WebSocket manually
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: test" \
  -H "Sec-WebSocket-Version: 13" \
  http://localhost:8000/ws

# Reload extension in browser
# Chrome: chrome://extensions → Reload
# Firefox: about:addons → Reload
```

---

## 📊 Analytics & Reporting

### Daily Performance Script
```python
#!/usr/bin/env python3
# daily_report.py

from src.core.bankroll_tracker import get_bankroll_stats
from src.core.discord_integration import send_daily_summary_to_discord

def generate_daily_report():
    """Generate and send daily performance report"""

    # Get current stats
    stats = get_bankroll_stats()

    # Print to console
    print("📊 Daily Performance Report")
    print(f"Balance: ${stats['current_balance']:.2f}")
    print(f"Win Rate: {stats['win_rate']:.1f}%")
    print(f"ROI: {stats['roi']:.2f}%")

    # Send to Discord
    send_daily_summary_to_discord(stats)

    # Save to logs
    import json
    from datetime import datetime

    log_file = f"logs/daily_report_{datetime.now().strftime('%Y%m%d')}.json"
    with open(log_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"📄 Report saved to {log_file}")

if __name__ == "__main__":
    generate_daily_report()
```

### Weekly Analysis
```bash
# Run weekly analysis
python -c "
from src.core.bankroll_tracker import BankrollTracker
import pandas as pd

tracker = BankrollTracker()
stats = tracker.get_stats()

print('📈 Weekly Performance Summary')
print(f'Total Bets: {stats[\"total_slips\"]}')
print(f'Win Rate: {stats[\"win_rate\"]:.1f}%')
print(f'Total ROI: {stats[\"roi\"]:.2f}%')
print(f'Current Balance: \${stats[\"current_balance\"]:.2f}')
"
```

---

## 🎯 Next Steps & Advanced Usage

### 1️⃣ Automated Daily Runs
Set up automated daily optimization:

**Windows (Task Scheduler):**
```batch
# Create daily_optimizer.bat
@echo off
cd C:\path\to\sports-betting-optimizer
python -m src.promos.master_optimizer --sport nfl --promo mystery --promo-date %DATE:~10,4%-%DATE:~4,2%-%DATE:~7,2% --token 25
```

**Linux/Mac (cron):**
```bash
# Add to crontab (daily at 10 AM)
0 10 * * * cd /path/to/sports-betting-optimizer && python -m src.promos.master_optimizer --sport nfl --promo mystery --promo-date $(date +\%Y-\%m-\%d) --token 25
```

### 2️⃣ Multi-Sport Automation
```bash
# Script to run multiple sports
#!/bin/bash
PROMO_DATE=$(date +%Y-%m-%d)

echo "🏈 Running NFL optimization..."
python -m src.promos.master_optimizer --sport nfl --promo mystery --promo-date $PROMO_DATE --token 25

echo "🏀 Running NBA optimization..."
python -m src.promos.master_optimizer --sport nba --promo stepped --promo-date $PROMO_DATE

echo "⚽ Running Soccer optimization..."
python -m src.promos.master_optimizer --sport soccer --promo mystery --promo-date $PROMO_DATE --token 33
```

### 3️⃣ Advanced Analytics Integration
```python
# advanced_analytics.py
import pandas as pd
from src.core.bankroll_tracker import BankrollTracker

def calculate_advanced_metrics():
    """Calculate Sharpe ratio, max drawdown, Kelly sizing"""

    tracker = BankrollTracker()

    # Load historical data
    df = pd.read_csv(tracker.bankroll_path)

    # Calculate rolling performance
    df['rolling_balance'] = df['balance'].rolling(window=7).mean()
    df['daily_return'] = df['profit_loss'] / df['stake']

    # Sharpe ratio (risk-adjusted return)
    sharpe = df['daily_return'].mean() / df['daily_return'].std() * (365 ** 0.5)

    # Maximum drawdown
    rolling_max = df['balance'].expanding().max()
    drawdown = (df['balance'] - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    # Kelly criterion sizing
    win_rate = len(df[df['result'] == 'won']) / len(df[df['result'] != 'pending'])
    avg_win = df[df['result'] == 'won']['profit_loss'].mean()
    avg_loss = abs(df[df['result'] == 'lost']['profit_loss'].mean())

    kelly_f = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win

    return {
        'sharpe_ratio': sharpe,
        'max_drawdown': max_drawdown,
        'kelly_fraction': kelly_f,
        'recommended_bet_size': kelly_f * tracker.get_current_balance()
    }
```

---

## 🎉 You're Now Running the Complete System!

Your EQ12 setup now includes:

- ✅ **Automated Optimization** with real-time Discord alerts
- ✅ **Browser Extension Integration** with WebSocket updates
- ✅ **Complete Bankroll Management** with settlement tracking
- ✅ **Interactive CLI Tools** for bet management
- ✅ **Performance Analytics** with ROI and win rate tracking
- ✅ **Multi-Sport Support** across all major leagues
- ✅ **Cross-Platform Compatibility** (Windows/Mac/Linux)

### 🔥 Your New Betting Workflow:
1. **Morning**: Run optimizer → Auto Discord alert + Extension notification
2. **Midday**: One-click bet placement via browser extension
3. **Evening**: Interactive settlement → Auto bankroll update + Discord celebration
4. **Weekly**: Review performance analytics and optimize strategy

**You're now equipped with the most advanced sports betting optimization system available!** 🚀💰

---

*Remember: Bet responsibly and within your means. This system is for educational and analytical purposes.*
