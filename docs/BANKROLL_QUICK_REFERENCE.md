# EQ12 Bankroll Expert - Quick Reference Card

## 🚀 INSTANT COMMANDS

### Check Bankroll Status
```powershell
python eq12_bankroll_manager.py --action status
```

### View Live Dashboard
```powershell
python eq12_bankroll_dashboard.py
```

### Run Scanner + Auto Execute (DRY RUN)
```powershell
# Step 1: Run scanner
$env:ODDS_API_KEY = "ODDS_API_KEY_PLACEHOLDER"
python eq12_live_sports_scanner_ENHANCED.py --workers 10 --bankroll 10000

# Step 2: Auto execute bets (DRY RUN - safe!)
python eq12_auto_bet_executor.py --scan ../logs/sports_scan_enhanced_*.json --min-confidence 75 --min-edge 2.5
```

---

## 💡 COMMON WORKFLOWS

### Workflow 1: Daily Betting Routine

```powershell
# Morning: Check bankroll
python eq12_bankroll_dashboard.py

# Midday: Scan opportunities
python eq12_live_sports_scanner_ENHANCED.py --workers 10 --bankroll 10000

# Review opportunities (dry run)
python eq12_auto_bet_executor.py --scan ../logs/sports_scan_enhanced_*.json --min-confidence 80

# Evening: Generate report
python eq12_bankroll_manager.py --action report --output ../reports/daily_report.json
```

---

### Workflow 2: Place Single Bet (Manual)

```python
from eq12_bankroll_manager import EQ12BankrollManager

manager = EQ12BankrollManager()

# Place bet
result = manager.place_bet(
    sport="NHL",
    game="Edmonton @ Seattle",
    market="h2h",
    outcome="Edmonton Oilers",
    odds=-122,
    decimal_odds=1.82,
    stake=5646.38,  # From scanner recommendation
    edge_percent=2.75,
    confidence_score=95,
    bet_type="arbitrage",
    sportsbook="BetRivers"
)

print(f"Bet ID: {result['bet_id']}")
```

---

### Workflow 3: Settle Bets

```python
from eq12_bankroll_manager import EQ12BankrollManager, BetStatus

manager = EQ12BankrollManager()

# Settle winning bet
manager.settle_bet("BET_20251128_120000_001", BetStatus.WON)

# Settle losing bet
manager.settle_bet("BET_20251128_120000_002", BetStatus.LOST)

# Check updated status
python eq12_bankroll_dashboard.py
```

---

## 📊 KEY METRICS EXPLAINED

### Kelly Fraction
- **0.25** = Quarter Kelly (RECOMMENDED - Conservative)
- **0.50** = Half Kelly (Moderate)
- **1.00** = Full Kelly (Aggressive - NOT recommended)

### Confidence Scores
- **95-100**: Arbitrage (guaranteed profit)
- **80-94**: Very high confidence (sharp money + steam)
- **70-79**: High confidence
- **60-69**: Moderate confidence
- **< 60**: Low confidence (avoid)

### Edge Percentage
- **10%+**: Exceptional (rare)
- **5-10%**: Excellent
- **2-5%**: Good
- **< 2%**: Marginal

### Risk Metrics
- **Max Single Bet**: 5% of bankroll
- **Max Total Exposure**: 30% of bankroll
- **Win Rate Target**: 52%+ (after vig)
- **ROI Target**: 2-5% monthly

---

## ⚡ EMERGENCY COMMANDS

### Stop All Betting
```python
# Set max exposure to 0% (blocks all new bets)
from eq12_bankroll_manager import EQ12BankrollManager
manager = EQ12BankrollManager()
manager.max_total_exposure = 0.0
```

### Cancel All Pending
```python
import sqlite3
conn = sqlite3.connect('../logs/eq12_bankroll.db')
cursor = conn.cursor()
cursor.execute("UPDATE bets SET status = 'cancelled' WHERE status = 'pending'")
conn.commit()
conn.close()
```

### Backup Database
```powershell
Copy-Item ../logs/eq12_bankroll.db ../logs/eq12_bankroll_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db
```

---

## 🎯 RECOMMENDED SETTINGS

### Conservative (Beginner)
```python
kelly_fraction = 0.25
max_single_bet = 0.03  # 3%
min_confidence = 80
min_edge = 3.0
```

### Standard (Recommended)
```python
kelly_fraction = 0.25
max_single_bet = 0.05  # 5%
min_confidence = 75
min_edge = 2.5
```

### Aggressive (Advanced)
```python
kelly_fraction = 0.50
max_single_bet = 0.07  # 7%
min_confidence = 65
min_edge = 2.0
```

---

## 📁 FILE LOCATIONS

```
logs/
├── eq12_bankroll.db              # Main database
├── sports_scan_enhanced_*.json   # Scanner outputs

reports/
├── bankroll_report.json          # Daily reports
├── execution_*.json              # Execution summaries
└── bankroll_dashboard_full.json  # Full analytics

scripts/
├── eq12_bankroll_manager.py      # Core manager
├── eq12_auto_bet_executor.py     # Auto executor
└── eq12_bankroll_dashboard.py    # Dashboard
```

---

## 🆘 TROUBLESHOOTING

**"Insufficient bankroll"**
```powershell
python eq12_bankroll_manager.py --action deposit --amount 1000
```

**"Bet exceeds max limit"**
- Check: `max_single_bet` parameter (default 5%)
- Reduce stake or increase bankroll

**"Database locked"**
```powershell
Get-Process python | Stop-Process
```

**"No opportunities found"**
- Lower `min-confidence` (try 70)
- Lower `min-edge` (try 2.0)
- Check scanner found opportunities

---

## 📞 QUICK HELP

```powershell
# Bankroll Manager help
python eq12_bankroll_manager.py --help

# Auto Executor help
python eq12_auto_bet_executor.py --help

# Dashboard help
python eq12_bankroll_dashboard.py --help
```

---

## ✅ PRE-FLIGHT CHECKLIST

Before going live:

- [ ] Bankroll initialized: `python eq12_bankroll_manager.py --action status`
- [ ] Scanner tested: `python eq12_live_sports_scanner_ENHANCED.py`
- [ ] Dry run successful: `python eq12_auto_bet_executor.py --scan ...`
- [ ] Risk limits set appropriately
- [ ] Database backed up
- [ ] Understand Kelly sizing
- [ ] Know how to settle bets
- [ ] Emergency stop procedure ready

---

**Version:** 1.0.0  
**Updated:** 2025-11-28  
**Status:** Production Ready ✅
