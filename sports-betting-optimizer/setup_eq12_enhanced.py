#!/usr/bin/env python3
"""
EQ12 Enhanced System Setup - Complete integration setup with Expert Kelly System
Final setup script that integrates all EQ12 components with Expert Kelly Integration
"""

import json
import sys
from pathlib import Path


def setup_expert_kelly_integration():
    """Setup Expert Kelly Integration as central bankroll management"""
    print("🧮 Setting up Expert Kelly Integration System...")

    # Check if Kelly setup script exists
    kelly_setup = Path("setup_expert_kelly.py")
    if kelly_setup.exists():
        try:
            import subprocess

            result = subprocess.run(
                [sys.executable, str(kelly_setup)], capture_output=True, text=True
            )
            if result.returncode == 0:
                print("   ✅ Expert Kelly Integration System initialized")
            else:
                print(f"   ⚠️ Kelly setup warning: {result.stderr}")
        except Exception as e:
            print(f"   ❌ Kelly setup failed: {e}")
    else:
        print("   ⚠️ Kelly setup script not found - creating minimal Kelly config")
        create_minimal_kelly_config()


def create_minimal_kelly_config():
    """Create minimal Kelly configuration if full setup unavailable"""

    kelly_config = {
        "kelly_criterion": {
            "enabled": True,
            "default_fraction": 0.25,
            "max_bankroll_risk": 0.15,
            "min_edge_threshold": 0.01,
            "environments": {
                "dev": {"kelly_fraction": 0.10, "starting_balance": 500.0},
                "staging": {"kelly_fraction": 0.20, "starting_balance": 1000.0},
                "production": {"kelly_fraction": 0.25, "starting_balance": 2000.0},
            },
        },
        "azure_ml_integration": {
            "enabled": True,
            "multi_environment": True,
            "auto_deploy": False,
        },
        "statistical_models": {
            "probability_estimation": True,
            "correlation_analysis": True,
            "multi_bet_optimization": True,
        },
    }

    config_dir = Path("configs")
    config_dir.mkdir(exist_ok=True)

    with open(config_dir / "kelly_config.json", "w") as f:
        json.dump(kelly_config, f, indent=2)

    print("   📄 Created minimal Kelly configuration")


def create_comprehensive_readme():
    """Create comprehensive README with all new features"""
    readme_content = """# EQ12 Sports Betting Optimization System 🎯

## Complete Automation Suite with Discord & Kelly Integration

### 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install requests aiohttp
   ```

2. **Set Environment Variables**:
   ```bash
   # Required for Discord notifications
   export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your_webhook_here"

   # Optional for live odds
   export ODDS_API_KEY="your_odds_api_key"
   ```

3. **Run System Setup**:
   ```bash
   python setup_eq12_enhanced.py
   ```

### 📊 Core Features

#### 1. Kelly Criterion Calculator (`kelly_calculator.py`)
- **Optimal Stake Sizing**: Calculate mathematically optimal bet sizes
- **Risk Management**: Configurable Kelly fractions and maximum stakes
- **Multi-outcome Support**: Handle parlays and complex bets
- **Interactive Mode**: CLI for quick calculations

```bash
# Interactive Kelly calculator
python kelly_calculator.py

# Single calculation: $1000 bankroll, 2.1 odds, 4.2% EV
python kelly_calculator.py 1000 2.1 4.2

# Test scenarios
python kelly_calculator.py --test
```

**Example Output**:
```
🧮 KELLY CRITERION ANALYSIS
💰 Current Bankroll:     $1,000.00
🎲 Decimal Odds:         2.10
📈 Expected Value:       +4.20%
✅ Recommended Stake:    $20.05
📊 % of Bankroll:        2.00%
🚨 Risk Level:           MEDIUM
```

#### 2. Discord Integration (`src/integrations/discord_integration.py`)
- **Automated Alerts**: Real-time bet opportunity notifications
- **Rich Embeds**: Professional Discord formatting with colors/emojis
- **Settlement Updates**: Automatic win/loss notifications with P&L
- **Cross-browser Support**: Works in Chrome, Firefox, and Edge extensions

**Discord Features**:
- 🟢 **+EV Alerts**: Green embeds for profitable opportunities
- 🔴 **Settlements**: Red/green based on win/loss outcomes
- 🟡 **Daily Summaries**: Performance reports with statistics
- ⚪ **Error Notifications**: System status and error alerts

```python
# Python integration
from src.integrations.discord_integration import notify_bet_alert_sync

success = notify_bet_alert_sync(
    bet_id="chiefs-001",
    sport="NFL",
    stake=50.0,
    ev=4.2,
    odds=2.1
)
```

```javascript
// Browser extension integration
await EQ12Discord.alertBetOpportunity({
    id: 'chiefs-001',
    sport: 'NFL',
    stake: 50.0,
    ev: 4.2,
    odds: 2.1,
    book: 'DraftKings'
});
```

#### 3. Enhanced Bankroll Management (`src/core/bankroll_tracker_clean.py`)
- **Automatic Kelly Sizing**: Optional stake adjustment using Kelly criterion
- **Discord Integration**: Automatic notifications for bets and settlements
- **CSV Persistence**: All data stored in human-readable CSV format
- **Settlement Tracking**: Complete win/loss/push/void handling

```python
# Add bet with Kelly sizing and Discord notification
from src.core.bankroll_tracker_clean import update_bankroll, settle_slip

# Log new bet (with optional Kelly adjustment)
update_bankroll(
    slip={
        'id': 'game-001',
        'sport': 'NFL',
        'stake': 50.0,
        'ev': 4.2,
        'odds': 2.1
    },
    use_kelly_sizing=True,    # Adjust stake using Kelly
    send_discord=True         # Send Discord alert
)

# Settle bet when game ends
settle_slip(
    slip_id='game-001',
    result='win',             # 'win', 'loss', 'push', 'void'
    payout=105.0,            # Total returned (stake + profit)
    send_discord=True        # Send Discord settlement notification
)
```

#### 4. CLI Utilities

**Bankroll Settlement** (`bankroll_settle.py`):
```bash
# Interactive settlement mode
python bankroll_settle.py

# Quick settlement
python bankroll_settle.py game-001 win 105.0

# View pending bets
python bankroll_settle.py --pending
```

**Bankroll Reporting** (`bankroll_report.py`):
```bash
# Full report
python bankroll_report.py

# Last 7 days only
python bankroll_report.py --days 7

# JSON output
python bankroll_report.py --format json
```

**Discord Testing** (`test_discord.py`):
```bash
# Test embed creation (no webhook needed)
python test_discord.py --test-type embeds

# Test actual webhook (requires DISCORD_WEBHOOK_URL)
python test_discord.py --test-type sync

# Interactive testing
python test_discord.py
```

### 🏈 Browser Extension Integration

The system includes complete browser extension support with Discord integration:

**Extension Features**:
- Cross-browser compatibility (Chrome, Firefox, Edge)
- Real-time bet detection and EV calculation
- Automatic Discord notifications
- Kelly-sized stake recommendations
- One-click bet slip export to optimizer

**Extension Files**:
- `src/extensions/discord_extension.js` - Discord webhook integration
- `betting-bridge/` - WebSocket bridge for real-time communication
- Auto-fill scripts for DraftKings, FanDuel, BetMGM

### 📈 Workflow Examples

#### Complete Betting Workflow
1. **Optimizer finds +EV bet** → Automatically exports to bridge
2. **Discord alert sent** → Notification with stake recommendation
3. **Extension receives bet** → Auto-fills sportsbook with Kelly-sized stake
4. **Bet placed** → Logged to bankroll with Discord confirmation
5. **Game settles** → Manual or automatic settlement with Discord update

#### Daily Summary Workflow
```bash
# Morning: Generate overnight report
python bankroll_report.py --days 1

# During day: Monitor for opportunities
python src/promos/master_optimizer.py --export-bridge

# Evening: Settle completed bets
python bankroll_settle.py --interactive

# Night: Generate daily summary
python bankroll_report.py --format json | python -c "
import json, sys
data = json.load(sys.stdin)
# Custom daily summary logic
"
```

### ⚙️ Configuration

**Kelly Settings** (`configs/kelly_settings.json`):
```json
{
  "default_bankroll": 1000.0,
  "max_stake_percentage": 0.10,
  "kelly_fraction": 0.25,
  "min_stake": 5.0,
  "max_stake": 500.0
}
```

**Discord Settings** (`configs/discord_settings.json`):
```json
{
  "notification_types": {
    "bet_alerts": true,
    "settlements": true,
    "daily_summaries": true,
    "errors": true
  },
  "username": "EQ12 Sports Bot"
}
```

### 🔧 Advanced Usage

#### Custom Kelly Calculations
```python
from src.utils.kelly_criterion import KellyCriterion

calculator = KellyCriterion(
    bankroll=1000.0,
    kelly_fraction=0.25,  # Use 25% of full Kelly
    max_stake_pct=0.10    # Never risk more than 10%
)

result = calculator.calculate_ev_kelly_stake(
    decimal_odds=2.1,
    ev_percentage=4.2
)

print(f"Recommended stake: ${result['recommended_stake']:.2f}")
print(f"Risk level: {result['risk_level']}")
```

#### Parlay Kelly Calculation
```python
parlay_legs = [
    {"odds": 1.91, "win_prob": 0.55},  # Chiefs -7
    {"odds": 1.83, "win_prob": 0.60},  # Over 48.5
]

parlay_result = calculator.calculate_parlay_kelly_stake(parlay_legs)
print(f"Parlay recommendation: ${parlay_result['recommended_stake']:.2f}")
```

#### Custom Discord Embeds
```python
from src.integrations.discord_integration import DiscordNotifier, create_bet_alert_embed

notifier = DiscordNotifier("your_webhook_url")

# Custom embed
custom_embed = create_bet_alert_embed(
    bet_id="custom-001",
    sport="UFC",
    stake=100.0,
    ev=15.2,
    odds=3.5,
    boost_pct=50.0,
    book="BetMGM",
    alert_type="BOOST"
)

await notifier.send_async(
    content="🥊 **UFC BOOST ALERT**",
    embeds=[custom_embed]
)
```

### 📱 Mobile & API Integration

The system supports mobile betting through API integration:

```python
# Mobile-friendly quick functions
from src.core.bankroll_tracker_clean import compute_win_payout
from src.utils.kelly_criterion import quick_kelly_stake

# Quick Kelly calculation for mobile app
stake = quick_kelly_stake(1000.0, 2.1, 4.2)  # $20.05

# Quick payout calculation
payout = compute_win_payout(50.0, 2.1, 25.0)  # $82.50 with 25% boost
```

### 🛡️ Security & Privacy

- **Webhook URLs**: Stored securely in browser extension storage
- **API Keys**: Environment variables only, never hardcoded
- **Local Data**: All bankroll data stored locally in CSV format
- **No Cloud Dependencies**: System runs entirely locally

### 🎯 Performance Tips

1. **Kelly Fraction**: Start with 0.25 (25% Kelly) for conservative approach
2. **Discord Rate Limits**: Built-in retry logic handles Discord API limits
3. **Bankroll Updates**: Use per-bet updates for accurate Kelly calculations
4. **EV Threshold**: Set minimum 2.0% EV to reduce noise
5. **Confidence Scaling**: Scale Kelly stakes by confidence in edge (0.5-1.0)

### 📞 Support & Troubleshooting

**Common Issues**:
- Discord webhook 404: Check webhook URL in settings
- Kelly calculation errors: Verify odds > 1.0 and EV > 0
- Import errors: Run `pip install requests aiohttp`
- Bankroll file not found: Run setup script to create directories

**Debug Commands**:
```bash
# Test all components
python kelly_calculator.py --test
python test_discord.py --test-type embeds
python bankroll_report.py

# Check environment
python -c "import os; print('Discord:', bool(os.getenv('DISCORD_WEBHOOK_URL')))"
```

### 📊 Example Daily Workflow

```bash
# 1. Morning check
python bankroll_report.py

# 2. Run optimizer with Kelly + Discord
python src/promos/master_optimizer.py --use-kelly --discord-alerts

# 3. Settle yesterday's bets
python bankroll_settle.py --interactive

# 4. Generate updated report
python bankroll_report.py --days 7 --format json > daily_report.json
```

---

**🎉 EQ12 v2.0 - Now with complete Discord integration, Kelly criterion optimization, and comprehensive bankroll management!**
"""

    Path("README_ENHANCED.md").write_text(readme_content, encoding="utf-8")
    print("✅ Created comprehensive README_ENHANCED.md")
    return True


def main():
    """Main setup function with Expert Kelly Integration"""
    print("🎯 EQ12 ENHANCED SYSTEM SETUP WITH EXPERT KELLY INTEGRATION")
    print("=" * 60)

    # 1. Setup Expert Kelly Integration System
    setup_expert_kelly_integration()

    # 2. Create enhanced documentation
    print("\n📚 Creating enhanced documentation...")
    success = create_comprehensive_readme()

    if success:
        print("\n🎉 EQ12 Enhanced Setup with Expert Kelly Integration Complete!")
        print("\n📊 Expert Kelly Integration:")
        print("  • kelly_cli.py - Main Kelly Criterion interface")
        print("  • quick_kelly.py - Fast Kelly calculations")
        print("  • switch_kelly_env.py - Environment switching")
        print("  • KELLY_INTEGRATION_GUIDE.md - Complete Kelly documentation")
        print("\n📚 Documentation:")
        print("  • README_ENHANCED.md - Complete feature guide")
        print("\n🧪 Test Commands:")
        print("  • python kelly_cli.py --comprehensive-report")
        print("  • python quick_kelly.py 2.1 0.52 --bankroll 1000")
        print("  • python kelly_cli.py --multi-bet-analysis --bets-file sample_bets.json")
        print("  • python kelly_calculator.py --test")
        print("  • python test_discord.py --test-type embeds")
        print("  • python bankroll_report.py")
        print("\n🚀 Quick Start:")
        print("  1. Set DISCORD_WEBHOOK_URL environment variable")
        print("  2. Run: python kelly_calculator.py 1000 2.1 4.2")
        print("  3. Check: python test_discord.py --test-type embeds")

    return success


if __name__ == "__main__":
    main()
