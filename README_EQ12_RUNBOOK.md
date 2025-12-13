# EQ12 NFL Betting System - Tight Runbook Implementation

A production-ready NFL betting system implementing the complete **tight runbook** with focus on **DraftKings, FanDuel, and BetMGM** only. Built for maximum efficiency with proper timezone handling, rate limiting, and comprehensive error handling.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- The Odds API key (set as `ODDS_API_KEY` environment variable)
- Windows/Linux environment

### Installation
```bash
# Clone or copy files to C:\EQ12\
cd C:\EQ12

# Install required packages
pip install requests pyyaml asyncio dataclasses

# Set your API key
set ODDS_API_KEY=your_api_key_here
# or export ODDS_API_KEY=your_api_key_here (Linux)
```

### Quick Demo
```bash
# Run complete demonstration of all runbook features
python eq12_cli.py --demo

# Run API health checks only  
python eq12_cli.py --health-check

# Create example configuration files
python eq12_cli.py --create-config

# Start production scheduler (runs continuously)
python eq12_cli.py --run-scheduler
```

## 📋 Tight Runbook Implementation

### Core Query Types (All Implemented)

#### 🔍 **Ingest & Health (Pre-flight)**
- ✅ API heartbeat & quota monitoring
- ✅ Clock sanity checks (UTC timezone handling)
- ✅ Book availability snapshots (DK/FD/BetMGM)

#### 📊 **Core Market Pulls (Game Odds)**
- ✅ Today + next 24h slate filtering
- ✅ Last-minute steaming window (≤60m to kickoff)
- ✅ Line movement polling with diff detection

#### 🎯 **Targeted Market Pulls (Value Hunting)**
- ✅ Moneylines only (`markets=h2h`)
- ✅ Spreads with hooks (`±0.5, ±1.5, ±2.5, ±3.5, ±6.5, ±7.5, ±9.5, ±10.5`)
- ✅ Totals with hooks (`37.5-52.5 range`)
- ✅ Alternate lines scanning

#### 🧮 **Modeling & Edge Computation**
- ✅ Implied vs model probability calculation
- ✅ Kelly sizing with market-specific caps
- ✅ Minimum EV filtering (2-3% live, 5-8% pregame)
- ✅ Best-book selector across DK/FD/BetMGM
- ✅ Duplicate/conflict detection

#### 🎰 **Parlay Builders (Book-Specific)**
- ✅ Max legs (YOLO) - top N edges per book
- ✅ Balanced risk - mixed ML + hook spreads/totals
- ✅ Conservative high-EV - only 6-8%+ EV, hooks preferred
- ✅ Spread-only (hooks) - key numbers only
- ✅ Totals-only (hooks) - key numbers only
- ✅ Close games - |spread| ≤ 3.0, price ≥ -120

#### 📈 **Line Movement & CLV**
- ✅ Movement tracker with price/point diffs
- ✅ Steam alerts (|Δprice| ≥ 10 or |Δpoint| ≥ 0.5 within 10m)
- ✅ CLV ledger for grabbed vs close prices

#### ⚖️ **Risk, Rules & Compliance**
- ✅ Single-book per parlay enforcement
- ✅ Correlated legs blocking
- ✅ Limit/hold checks

#### 🏆 **Results & Settlement**
- ✅ Scores/finals fetching for grading
- ✅ Settlement job framework
- ✅ Backtest summaries by strategy/book/market

## ⏰ Scheduler Cadence (Exact Runbook Specs)

| Job Type | Frequency | Description |
|----------|-----------|-------------|
| **Odds Polling** | 30-60s (10-15s when T<10m) | Standard market pulls |
| **Steam Scanning** | 30s | Line movement alerts |
| **Settlement & CLV** | 15-30m | Grading and CLV calculation |
| **Health/Quality** | 1-5m | API health and data quality |
| **Value Hunting** | 90-120s | Market-specific opportunities |
| **Parlay Building** | 3m | Book-specific parlay construction |

## 🗂️ File Structure

```
C:\EQ12\
├── eq12_api_client.py      # Core API client (all runbook queries)
├── eq12_scheduler.py       # Production scheduler with exact cadence  
├── eq12_cli.py            # CLI runner and demos
├── configs/
│   ├── eq12_scheduler_config.yaml    # Job configurations
│   ├── example_model_probabilities.json
│   └── betting_limits.json
└── logs/
    ├── eq12_scheduler.log
    ├── odds_polling_*.json
    └── settlement_*.json
```

## 🔧 Configuration

### Scheduler Config (`configs/eq12_scheduler_config.yaml`)
```yaml
jobs:
  - name: "odds_polling_standard"
    enabled: true
    interval_seconds: 45
    function: "odds_polling"
    params:
      markets: ["h2h", "spreads", "totals"]
    timeout_seconds: 60
    
  - name: "steam_detection"
    enabled: true  
    interval_seconds: 30
    function: "steam_detection"
    params:
      price_threshold: 10
      point_threshold: 0.5
    timeout_seconds: 45
    
  # ... (12 more jobs with exact runbook specs)
```

### Model Probabilities (`configs/example_model_probabilities.json`)
```json
{
  "game1_h2h_Team A_None": 0.55,
  "game1_spreads_Team A_-3.5": 0.52,
  "game1_totals_Over_47.5": 0.51
}
```

## 🎯 Usage Examples

### API Client Direct Usage
```python
from eq12_api_client import create_client, BookMaker

# Initialize client
client = create_client()

# Health checks
health = client.heartbeat()
clock_check = client.clock_sanity_check()
availability = client.book_availability_snapshot()

# Market pulls
games_24h = client.get_24h_slate()
steaming = client.get_steaming_window()
moneylines = client.get_moneylines_only()
spread_hooks = client.get_spreads_with_hooks()

# Parlay building
dk_balanced = client.build_balanced_risk_parlay(BookMaker.DRAFTKINGS)
fd_conservative = client.build_conservative_high_ev_parlay(BookMaker.FANDUEL)
```

### Scheduler Usage
```python
from eq12_scheduler import EQ12Scheduler
import asyncio

# Initialize and start scheduler
scheduler = EQ12Scheduler("configs/eq12_scheduler_config.yaml")
await scheduler.start()  # Runs continuously with all jobs
```

### CLI Usage
```bash
# Complete system demo
python eq12_cli.py --demo

# Production scheduler
python eq12_cli.py --run-scheduler

# Health check only
python eq12_cli.py --health-check

# Create configs
python eq12_cli.py --create-config
```

## 📊 Key Features

### ✅ **Bookmaker Focus (DK/FD/BetMGM Only)**
- Hardcoded to exactly 3 books as specified
- Book-specific parlay builders
- No mixed-book parlays (compliance)

### ✅ **Timezone Handling**
- All timestamps UTC-aware
- Proper `commence_time` parsing
- Clock sanity checks prevent naive datetime bugs

### ✅ **Hook Numbers (Key Numbers)**
- **Spreads**: `±0.5, ±1.5, ±2.5, ±3.5, ±6.5, ±7.5, ±9.5, ±10.5`
- **Totals**: `37.5, 38.5, 39.5, 40.5, 41.5, 42.5, 43.5, 44.5, 45.5, 46.5, 47.5, 48.5, 49.5, 50.5, 51.5, 52.5`

### ✅ **Production Ready**
- Comprehensive error handling
- Rate limiting and retry logic
- Structured logging to `C:/EQ12/logs/`
- Async job execution
- Signal handling for graceful shutdown

### ✅ **Edge Computation**
- Kelly criterion with market caps (ML: 5%, Spreads: 3%)
- American odds ↔ probability conversion
- EV calculation: `(model_prob - implied_prob) / implied_prob * 100`

## 🚨 Important Notes

### API Requirements
- **The Odds API key required** - set as `ODDS_API_KEY` environment variable
- **Respects rate limits** - built-in retry strategy and backoff
- **UTC timestamps only** - prevents timezone bugs

### Compliance
- **Single book per parlay** - no cross-book mixing
- **Conflict detection** - prevents opposite sides same game
- **One leg per game** - avoids correlation (unless explicit SGP)

### Performance
- **Async execution** - multiple jobs run concurrently
- **Configurable timeouts** - prevents hanging requests  
- **Result caching** - efficient data structures
- **Memory management** - limited result history

## 🔄 Development & Customization

### Adding New Jobs
1. Add job function to `EQ12Scheduler` class
2. Update `configs/eq12_scheduler_config.yaml`
3. Define parameters and timeout settings

### Adding New Books
1. Add to `BookMaker` enum in `eq12_api_client.py`
2. Update hardcoded book lists in queries
3. Add parlay builder configurations

### Model Integration  
1. Update `example_model_probabilities.json`
2. Implement `calculate_edges()` with your model
3. Adjust EV thresholds per strategy

## 🐛 Troubleshooting

### Common Issues
```bash
# API key not set
export ODDS_API_KEY=your_key_here

# Missing directories
python eq12_cli.py --create-config

# Rate limit errors
# Built-in retry handles this automatically

# Timezone warnings
# All handled with UTC-aware datetimes
```

### Logs
- **Scheduler**: `C:/EQ12/logs/eq12_scheduler.log`
- **Job Results**: `C:/EQ12/logs/{job_name}_{timestamp}.json`
- **API Errors**: Console and log files

## 📈 Next Steps

1. **Integrate your ML model** - update model probabilities
2. **Add alerting** - Discord/Slack notifications for steams
3. **Database integration** - persistent storage for results
4. **Web dashboard** - real-time monitoring UI
5. **Backtesting** - historical performance analysis

---

**Built following the exact tight runbook specifications for maximum production efficiency.** 🚀