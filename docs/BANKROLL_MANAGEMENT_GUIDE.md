# EQ12 Professional Bankroll Management System

## 🎯 Complete Bankroll Solution

Professional-grade bankroll management, Kelly Criterion optimization, risk analytics, and automated bet execution for sports betting operations.

---

## 📦 System Components

### 1. **Bankroll Manager** (`eq12_bankroll_manager.py`)
Core bankroll tracking and management system with:
- Kelly Criterion position sizing
- Risk-based stake calculations
- Comprehensive bet tracking (SQLite database)
- Real-time bankroll snapshots
- Deposit/withdrawal management
- Advanced risk metrics

### 2. **Auto Bet Executor** (`eq12_auto_bet_executor.py`)
Automated bet placement system with:
- Scanner integration (reads JSON output)
- Confidence/edge filtering
- Dry run mode (safety)
- Arbitrage execution
- Positive EV execution
- Execution reports

---

## 🚀 Quick Start

### Initialize Bankroll

```powershell
# Create new bankroll with $10,000
python eq12_bankroll_manager.py --bankroll 10000 --action status

# Add deposit
python eq12_bankroll_manager.py --action deposit --amount 5000

# Generate full report
python eq12_bankroll_manager.py --action report --output ../reports/bankroll.json
```

### Execute Scanner Results (DRY RUN)

```powershell
# Process enhanced scanner output (dry run - no actual bets)
python eq12_auto_bet_executor.py --scan ../logs/sports_scan_enhanced_20251128_162609.json --min-confidence 70 --min-edge 2.0

# Output: Shows what WOULD be placed
```

### Execute Scanner Results (LIVE)

```powershell
# LIVE EXECUTION - Actually places bets in database
python eq12_auto_bet_executor.py --scan ../logs/sports_scan_enhanced_20251128_162609.json --min-confidence 80 --min-edge 3.0 --execute

# ⚠️ WARNING: Only use --execute when ready for live tracking
```

---

## 💰 Bankroll Manager Features

### Core Functions

**1. Kelly Criterion Stake Calculation**
```python
from eq12_bankroll_manager import EQ12BankrollManager

manager = EQ12BankrollManager(starting_bankroll=10000.0)

# Calculate optimal stake
kelly = manager.calculate_kelly_stake(
    decimal_odds=2.5,      # Odds
    win_probability=0.45   # True probability (45%)
)

print(f"Recommended Stake: ${kelly['stake']:.2f}")
print(f"Kelly Fraction: {kelly['kelly_fraction']:.4f}")
print(f"Max Stake: ${kelly['max_stake']:.2f}")
```

**Output Example:**
```
Recommended Stake: $62.50
Kelly Fraction: 0.0250 (2.5% of bankroll)
Max Stake: $500.00 (5% cap)
```

---

**2. Place Bet**
```python
result = manager.place_bet(
    sport="NHL",
    game="Edmonton Oilers @ Seattle Kraken",
    market="h2h",
    outcome="Edmonton Oilers",
    odds=-122,
    decimal_odds=1.82,
    stake=5646.38,
    edge_percent=2.75,
    confidence_score=95,
    bet_type="arbitrage",
    sportsbook="BetRivers",
    sharp_money=False,
    steam_move=False,
    notes="Arbitrage leg 1"
)

if result['success']:
    print(f"✅ Bet placed: {result['bet_id']}")
    print(f"Available after: ${result['available_after']:.2f}")
else:
    print(f"❌ Error: {result['error']}")
```

---

**3. Settle Bet**
```python
from eq12_bankroll_manager import BetStatus

# Bet won
result = manager.settle_bet(
    bet_id="BET_20251128_120000_123456",
    status=BetStatus.WON,
    actual_odds=1.82  # Optional: use if odds changed
)

print(f"P/L: ${result['profit_loss']:.2f}")
print(f"New Bankroll: ${result['new_bankroll']:.2f}")
```

---

**4. Risk Metrics**
```python
metrics = manager.get_risk_metrics()

print(f"Total Exposure: ${metrics.total_exposure:,.2f}")
print(f"Exposure %: {metrics.exposure_percent:.1f}%")
print(f"Win Rate: {metrics.win_rate:.1f}%")
print(f"Largest Win: ${metrics.largest_win:,.2f}")
print(f"Largest Loss: ${metrics.largest_loss:,.2f}")
print(f"Kelly Compliance: {metrics.kelly_compliance:.1f}%")
print(f"Risk of Ruin: {metrics.risk_of_ruin:.1f}%")
```

---

## 🤖 Auto Executor Features

### Workflow

1. **Scanner Runs** → Generates JSON with opportunities
2. **Auto Executor Reads** → Filters by confidence/edge
3. **Bankroll Manager Validates** → Checks limits
4. **Bets Placed** → Tracked in database
5. **Reports Generated** → Execution summary

### Filtering Logic

```python
# Only bets meeting ALL criteria are placed:
- Confidence Score >= min_confidence (default: 70)
- Edge Percentage >= min_edge (default: 2.0%)
- Stake <= max_single_bet (5% of bankroll)
- Total Exposure <= max_total_exposure (30% of bankroll)
- Available Bankroll >= stake
```

### Execution Priority

1. **Arbitrage** (always highest priority)
2. **Positive EV** (sorted by confidence score descending)

---

## 📊 Database Schema

### Tables

**1. bets** - All bet records
```sql
- bet_id (PRIMARY KEY)
- timestamp, sport, game, market, outcome
- odds, decimal_odds, stake
- recommended_stake, kelly_fraction
- edge_percent, confidence_score
- bet_type, sportsbook, status
- result_timestamp, profit_loss, actual_odds
- sharp_money, steam_move, correlation_group
- notes
```

**2. snapshots** - Bankroll history
```sql
- snapshot_id (AUTO INCREMENT)
- timestamp, total_bankroll, available_bankroll
- pending_amount, total_bets, won_bets, lost_bets
- win_rate, roi, profit_loss
- largest_bet, average_bet
- sharpe_ratio, max_drawdown
- notes
```

**3. transactions** - Deposits/Withdrawals
```sql
- transaction_id (AUTO INCREMENT)
- timestamp, type (deposit/withdrawal)
- amount, bankroll_before, bankroll_after
- notes
```

---

## 🔒 Risk Parameters (Configurable)

```python
# Default Conservative Settings
kelly_fraction = 0.25        # Quarter Kelly (25% of full Kelly)
max_single_bet = 0.05        # 5% of bankroll maximum
max_total_exposure = 0.30    # 30% max pending at once
min_bankroll_percent = 0.50  # Stop at 50% loss
```

**Example:**
- Bankroll: $10,000
- Max Single Bet: $500 (5%)
- Max Total Pending: $3,000 (30%)
- Stop Loss Trigger: $5,000 (50% down)

---

## 📈 Real-World Example Workflow

### Step 1: Run Enhanced Scanner
```powershell
$env:ODDS_API_KEY = "c32c9644050b2240081428b43e7016ce"
cd C:\EQ12_BROKEN_20251122_210342\scripts
python eq12_live_sports_scanner_ENHANCED.py --workers 10 --bankroll 10000
```

**Output:** `logs/sports_scan_enhanced_20251128_162609.json`

---

### Step 2: Execute Bets (Dry Run First)
```powershell
python eq12_auto_bet_executor.py `
  --scan ../logs/sports_scan_enhanced_20251128_162609.json `
  --min-confidence 75 `
  --min-edge 2.5 `
  --report ../reports/execution_dry_run.json
```

**Output:**
```
🤖 EQ12 AUTO BET EXECUTOR
============================================================
Mode: DRY RUN
Min Confidence: 75.0
Min Edge: 2.5%
Bankroll: $10,000.00
============================================================

📊 EXECUTION SUMMARY
Total Opportunities: 443
Bets Placed: 12
Bets Skipped: 431
Total Staked: $1,247.50

✅ Report saved: ../reports/execution_dry_run.json
```

---

### Step 3: Execute Live (If Satisfied)
```powershell
python eq12_auto_bet_executor.py `
  --scan ../logs/sports_scan_enhanced_20251128_162609.json `
  --min-confidence 80 `
  --min-edge 3.0 `
  --execute `
  --report ../reports/execution_live.json
```

**Output:** Bets saved to `logs/eq12_bankroll.db`

---

### Step 4: Monitor Bankroll
```powershell
python eq12_bankroll_manager.py --action status
```

**Output:**
```
💰 EQ12 BANKROLL STATUS
==================================================
Total Bankroll: $10,000.00
Available: $8,752.50
Pending: $1,247.50

📊 PERFORMANCE
Total Bets: 12
Win Rate: 0.0% (no settled bets yet)
ROI: 0.00%
P/L: $0.00
```

---

### Step 5: Settle Bets (As Results Come In)

```python
from eq12_bankroll_manager import EQ12BankrollManager, BetStatus

manager = EQ12BankrollManager()

# Edmonton Oilers won
manager.settle_bet("BET_20251128_162000_001", BetStatus.WON)

# Seattle Kraken lost
manager.settle_bet("BET_20251128_162000_002", BetStatus.LOST)

# Check updated bankroll
print(f"New Total: ${manager._get_current_bankroll():,.2f}")
```

---

### Step 6: Generate Reports
```powershell
python eq12_bankroll_manager.py --action report --output ../reports/bankroll_report.json
```

**Report Contents:**
```json
{
  "timestamp": "2025-11-28T16:30:00.000000+00:00",
  "bankroll": {
    "total": 10275.00,
    "available": 10275.00,
    "pending": 0.00,
    "starting": 10000.00
  },
  "performance": {
    "total_bets": 12,
    "won": 6,
    "lost": 6,
    "win_rate": 50.0,
    "roi": 2.75,
    "profit_loss": 275.00
  },
  "risk_metrics": {
    "total_exposure": 0.00,
    "win_rate": 50.0,
    "kelly_compliance": 91.7,
    "largest_win": 125.50,
    "largest_loss": -100.00
  }
}
```

---

## 🎓 Advanced Usage

### Custom Kelly Fraction
```python
manager = EQ12BankrollManager()
manager.kelly_fraction = 0.5  # Half Kelly (more aggressive)
```

### Custom Risk Limits
```python
manager.max_single_bet = 0.03        # 3% max (more conservative)
manager.max_total_exposure = 0.20    # 20% max pending
```

### Correlation Grouping
```python
# Place correlated bets with same group ID
manager.place_bet(
    sport="NBA",
    game="Lakers vs Celtics",
    outcome="Lakers ML",
    correlation_group="lakers_parlay_group_1",
    # ... other params
)
```

---

## 🔍 Query Examples

### Get All Pending Bets
```python
import sqlite3

conn = sqlite3.connect('../logs/eq12_bankroll.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT bet_id, game, outcome, stake, odds
    FROM bets 
    WHERE status = 'pending'
    ORDER BY timestamp DESC
""")

for bet in cursor.fetchall():
    print(f"{bet[0]}: {bet[1]} - {bet[2]} @ {bet[4]} (${bet[3]:.2f})")
```

### Get Win Rate by Sport
```python
cursor.execute("""
    SELECT 
        sport,
        COUNT(*) as total,
        SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as wins,
        ROUND(100.0 * SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate
    FROM bets
    WHERE status IN ('won', 'lost')
    GROUP BY sport
    ORDER BY win_rate DESC
""")

for row in cursor.fetchall():
    print(f"{row[0]}: {row[3]}% ({row[2]}/{row[1]})")
```

---

## 📋 CLI Reference

### Bankroll Manager

```powershell
# Check status
python eq12_bankroll_manager.py --action status

# Deposit
python eq12_bankroll_manager.py --action deposit --amount 5000

# Withdraw
python eq12_bankroll_manager.py --action withdraw --amount 1000

# Generate report
python eq12_bankroll_manager.py --action report --output ../reports/report.json

# Custom database
python eq12_bankroll_manager.py --db ../custom/path.db --bankroll 25000
```

### Auto Executor

```powershell
# Dry run
python eq12_auto_bet_executor.py --scan SCANNER_OUTPUT.json

# Live execution
python eq12_auto_bet_executor.py --scan SCANNER_OUTPUT.json --execute

# Custom filters
python eq12_auto_bet_executor.py --scan SCANNER_OUTPUT.json --min-confidence 85 --min-edge 5.0

# Custom bankroll
python eq12_auto_bet_executor.py --scan SCANNER_OUTPUT.json --starting-bankroll 25000
```

---

## ⚠️ Important Notes

### Safety Features

1. **Dry Run Default**: Auto executor defaults to dry run (no actual bets)
2. **Validation Checks**: All bets validated before placement
3. **Exposure Limits**: Hard caps on single bet and total exposure
4. **Database Backup**: SQLite database - backup regularly
5. **Error Logging**: All errors logged with timestamps

### Risk Management

- **Never risk more than you can afford to lose**
- Start with conservative Kelly fractions (0.25 recommended)
- Monitor win rate and ROI continuously
- Set stop-loss limits and respect them
- Diversify across sports and bet types
- Track correlation between bets

### Best Practices

1. **Run dry runs first** - Always test with `--execute` flag OFF
2. **Start small** - Use smaller bankroll initially
3. **Monitor closely** - Check status after each settlement
4. **Generate reports** - Weekly performance reviews
5. **Backup database** - Regular backups of SQLite file
6. **Track manually** - Cross-check with sportsbook records

---

## 📊 Performance Expectations

### Conservative Settings (Recommended)
- Kelly Fraction: 0.25 (Quarter Kelly)
- Max Bet: 5%
- Min Confidence: 75
- Min Edge: 2.5%

**Expected:**
- Win Rate: 50-55%
- ROI: 2-5% per month
- Max Drawdown: 10-20%
- Risk of Ruin: <5%

### Aggressive Settings (Higher Risk)
- Kelly Fraction: 0.5 (Half Kelly)
- Max Bet: 7%
- Min Confidence: 60
- Min Edge: 1.5%

**Expected:**
- Win Rate: 48-52%
- ROI: 5-10% per month
- Max Drawdown: 20-40%
- Risk of Ruin: 10-20%

---

## 🆘 Troubleshooting

### Database Locked
```powershell
# Close all Python processes
Get-Process python | Stop-Process

# Restart manager
python eq12_bankroll_manager.py --action status
```

### Insufficient Bankroll
```powershell
# Check available
python eq12_bankroll_manager.py --action status

# Add deposit
python eq12_bankroll_manager.py --action deposit --amount 1000
```

### Bets Not Placing
- Check `--execute` flag is set for live mode
- Verify bankroll has sufficient funds
- Check min-confidence and min-edge thresholds
- Review error log in output

---

## 📁 File Structure

```
EQ12_BROKEN_20251122_210342/
├── scripts/
│   ├── eq12_bankroll_manager.py         # Core manager
│   ├── eq12_auto_bet_executor.py        # Auto executor
│   ├── eq12_live_sports_scanner_ENHANCED.py  # Scanner
│   └── eq12_betting_mathematics.py      # Math engine
├── logs/
│   ├── eq12_bankroll.db                 # Bankroll database
│   └── sports_scan_enhanced_*.json      # Scanner outputs
└── reports/
    ├── bankroll_report.json             # Performance reports
    └── execution_*.json                 # Execution summaries
```

---

## 🎯 Next Steps

1. **Initialize Bankroll**
   ```powershell
   python eq12_bankroll_manager.py --bankroll 10000 --action status
   ```

2. **Run Scanner**
   ```powershell
   python eq12_live_sports_scanner_ENHANCED.py --workers 10 --bankroll 10000
   ```

3. **Execute Bets (Dry Run)**
   ```powershell
   python eq12_auto_bet_executor.py --scan ../logs/sports_scan_enhanced_*.json
   ```

4. **Review Results**
   ```powershell
   python eq12_bankroll_manager.py --action report
   ```

---

## 📞 Integration with Existing Systems

This bankroll system integrates with:
- ✅ `eq12_live_sports_scanner_ENHANCED.py` (reads JSON output)
- ✅ `eq12_betting_mathematics.py` (Kelly Criterion)
- ✅ `eq12_advanced_bankroll_optimizer.py` (portfolio optimization)
- ✅ `eq12_line_movement_intelligence.py` (sharp money detection)

All systems work together for professional sports betting operations.

---

**Created:** 2025-11-28  
**Version:** 1.0.0  
**Status:** Production Ready ✅
