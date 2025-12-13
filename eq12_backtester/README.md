# EQ12 Historic Backtester

🎯 **Professional-grade backtesting engine for sports betting, trading, and affiliate optimization**

The EQ12 Historic Backtester is a comprehensive, automated, high-fidelity backtest engine designed to maximize profits across all sports markets. Built for the EQ12 GODSTACK automation platform.

## Features

### 🏆 Core Capabilities
- **Time-Machine Profit Loop**: Historic backtesting with precise edge detection
- **Multi-Sport Support**: MLB, NFL, NBA, UFC with expandable architecture
- **Advanced Analytics**: Kelly criterion sizing, EV calculations, drawdown analysis
- **Parlay Optimization**: EQ12-specific rules with correlation matrices
- **Professional Reporting**: HTML dashboards, charts, CSV exports, Telegram notifications

### 📊 Supported Markets
- **MLB**: Home runs, total bases, strikeouts, RBI, hits
- **NFL**: Touchdown props, rushing/passing yards, spreads, totals
- **NBA**: Points, rebounds, assists, 3-pointers, player props
- **UFC**: Fight outcomes, round betting, method of victory
- **Expandable**: API-driven architecture for new sports

### 🎲 EQ12 Parlay Rules
- No moneyline + spread same game parlays
- Home run overs only (no HR unders)
- 3+ star requirement for total bases/hits
- Auto-lock high-confidence bets
- Correlation-aware combinations

## Installation

### Prerequisites
- Python 3.8+
- Windows 10/11 (for task scheduler integration)
- VS Code (optional, for task integration)

### Quick Install
```powershell
# Run the automated installer
powershell -ExecutionPolicy Bypass -File "C:\EQ12\Install-EQ12-Backtester.ps1"
```

### Manual Setup
```bash
# Install Python dependencies
pip install pandas numpy matplotlib seaborn requests pytest black

# Verify installation
python C:\EQ12\eq12_backtester\run.py --help
```

## Usage

### Command Line Interface

#### Historical Backtesting
```bash
# Backtest MLB home runs for 2024 season
python run.py backtest --sport MLB --market HR --start 2024-04-01 --end 2024-10-01

# NFL touchdown props with custom bankroll
python run.py backtest --sport NFL --market TD --bankroll 5000 --start 2024-09-01

# Multi-sport comprehensive backtest
python run.py backtest --all-sports --start 2024-01-01 --end 2024-12-31
```

#### Parlay Optimization
```bash
# Optimize same-game parlays for today
python run.py parlay --sport MLB --type same_game

# Multi-game parlay optimization
python run.py parlay --sport NFL --type multi_game --min-odds 150

# Moonshot parlay generation (high-risk/high-reward)
python run.py parlay --type moonshot --min-payout 10000
```

#### Edge Scanning (Daily Automation)
```bash
# Scan all markets for profitable opportunities
python run.py scan

# Scan specific sport with Telegram alerts
python run.py scan --sport NBA --telegram

# Generate daily report with charts
python run.py scan --report --charts
```

#### Paper Trading Simulation
```bash
# Run 30-day paper trading simulation
python run.py paper --days 30

# Simulate with specific strategies
python run.py paper --strategy conservative --bankroll 10000

# Live paper trading (real-time simulation)
python run.py paper --live
```

### VS Code Integration

Use the integrated tasks via VS Code:

1. **Ctrl+Shift+P** → `Tasks: Run Task`
2. Select from:
   - `EQ12: Run Historical Backtest`
   - `EQ12: Optimize Parlays`
   - `EQ12: Daily Edge Scan`
   - `EQ12: Paper Trading Simulation`

### Windows Task Scheduler

The installer creates a daily automated task:
- **Task Name**: `EQ12_Daily_Backtest`
- **Schedule**: Daily at 9:00 AM
- **Action**: Runs edge scan with Telegram notifications

## Configuration

### Environment Variables

Set these for full functionality:

```bash
# API Access
ODDS_API_KEY=your_odds_api_key_here
ESPN_API_KEY=your_espn_key_here

# Telegram Notifications
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# OpenAI Integration (optional)
OPENAI_API_KEY=your_openai_key
```

### Config Files

#### `configs/backtest_config.json`
```json
{
  "default_bankroll": 1000,
  "kelly_fraction": 0.25,
  "max_bet_size": 0.1,
  "min_edge": 0.02,
  "risk_tolerance": "moderate"
}
```

## Architecture

### Module Structure
```
eq12_backtester/
├── core/
│   ├── __init__.py
│   └── engine.py          # Core backtesting engine
├── data/
│   ├── __init__.py
│   └── loader.py          # API and data integration
├── simulators/
│   ├── __init__.py
│   └── sport_simulators.py # Sport-specific simulation
├── optimizers/
│   ├── __init__.py
│   └── parlay_optimizer.py # EQ12 parlay rules
├── reports/               # Generated reports
├── reporting.py           # Report generation
└── run.py                # CLI interface
```

### Core Classes

#### `EQ12BacktesterEngine`
- Main backtesting logic
- Kelly criterion position sizing
- Performance analytics
- Risk management

#### `EQ12DataLoader`
- API integration (OddsAPI, ESPN)
- Data normalization and caching
- Team/player name mapping

#### `EQ12ParlayOptimizer`
- EQ12-specific betting rules
- Correlation analysis
- Combination generation

#### `EQ12ReportGenerator`
- HTML dashboard creation
- Chart generation (matplotlib)
- CSV exports
- Telegram integration

## API Integration

### Supported APIs
- **The Odds API**: Real-time odds and lines
- **ESPN API**: Player stats and game data
- **Custom APIs**: Extensible architecture

### Data Sources
- Historical odds data
- Player statistics
- Team performance metrics
- Weather data (for outdoor sports)
- Injury reports

## Performance Metrics

### Core Analytics
- **ROI**: Return on investment percentage
- **Sharpe Ratio**: Risk-adjusted returns
- **Win Rate**: Percentage of winning bets
- **Max Drawdown**: Largest peak-to-trough loss
- **Kelly Sizing**: Optimal bet sizing
- **Expected Value**: Theoretical profit per bet

### Advanced Metrics
- **Correlation Analysis**: Multi-bet relationships
- **Market Efficiency**: Edge detection across books
- **Temporal Patterns**: Time-based performance
- **Volatility Analysis**: Risk measurement

## Reporting

### HTML Dashboards
- Interactive performance charts
- Market breakdown analysis
- Equity curve visualization
- Drawdown analysis

### CSV Exports
- Detailed bet-by-bet results
- Performance summaries
- Market analytics
- Custom date ranges

### Telegram Integration
- Real-time notifications
- Daily performance summaries
- Edge alerts
- Automated reports

## Testing

### Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_backtester.py -v
pytest tests/test_parlay_optimizer.py -v

# Run with coverage
pytest --cov=eq12_backtester tests/
```

### Test Data
- Synthetic historical odds
- Mock API responses
- Edge case scenarios
- Performance benchmarks

## EQ12 GODSTACK Integration

### Task Automation
- Daily edge scanning
- Automated parlay generation
- Performance monitoring
- Alert systems

### File Integration
```
C:\EQ12\
├── eq12_backtester\        # Backtester system
├── logs\                   # Execution logs
├── configs\                # Configuration files
└── dashboard\              # Web dashboards
```

### Workflow Integration
1. **Morning Scan**: Daily edge detection at 9 AM
2. **Parlay Generation**: Optimal combinations for day's games
3. **Performance Tracking**: Real-time P&L monitoring
4. **Evening Report**: Daily summary and analytics

## Examples

### Basic Backtest
```python
from eq12_backtester.core.engine import EQ12BacktesterEngine

# Initialize backtester
engine = EQ12BacktesterEngine(initial_bankroll=1000)

# Add historical bets
engine.add_bet('MLB_HR', 'Judge', 'over', 2.5, -110, True, '2024-07-15')

# Run analysis
results = engine.calculate_performance()
print(f"ROI: {results['roi_percent']:.2f}%")
```

### Parlay Optimization
```python
from eq12_backtester.optimizers.parlay_optimizer import EQ12ParlayOptimizer

# Initialize optimizer
optimizer = EQ12ParlayOptimizer()

# Generate optimal parlays
parlays = optimizer.generate_parlays('MLB', max_legs=4, min_payout=500)

for parlay in parlays:
    print(f"Parlay: {parlay['description']} | Payout: {parlay['payout']}")
```

### Custom Reporting
```python
from eq12_backtester.reporting import EQ12ReportGenerator

# Generate comprehensive report
reporter = EQ12ReportGenerator()
report_file = reporter.generate_backtest_report(results, "Q3 2024 Performance")

# Export to CSV
csv_file = reporter.export_csv_report(results)
```

## Troubleshooting

### Common Issues

#### Python Import Errors
```bash
# Add EQ12 to Python path
export PYTHONPATH="C:\EQ12:$PYTHONPATH"
```

#### API Connection Issues
```bash
# Test API connectivity
python -c "from eq12_backtester.data.loader import EQ12DataLoader; loader = EQ12DataLoader(); loader.test_apis()"
```

#### Task Scheduler Issues
```bash
# Reinstall Windows task
powershell -ExecutionPolicy Bypass -File "Install-EQ12-Backtester.ps1" -Action Install
```

### Debugging

#### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Performance Profiling
```bash
python -m cProfile -o backtest_profile.txt run.py backtest --sport MLB
```

## Contributing

### Development Setup
```bash
# Install development dependencies
pip install black pytest pytest-cov mypy

# Format code
black eq12_backtester/

# Run type checking
mypy eq12_backtester/
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Comprehensive docstrings
- Unit tests for new features

### Adding New Sports
1. Create simulator in `simulators/sport_simulators.py`
2. Add API integration in `data/loader.py`
3. Update CLI options in `run.py`
4. Add tests in `tests/`

## License

Part of the EQ12 GODSTACK automation platform.
For internal use and authorized development only.

## Support

### Documentation
- **Full API Docs**: `C:\EQ12\docs\backtester_api.html`
- **Configuration Guide**: `C:\EQ12\docs\config_guide.md`
- **Troubleshooting**: `C:\EQ12\docs\troubleshooting.md`

### Logs
- **Installation**: `C:\EQ12\logs\backtester_install_*.log`
- **Runtime**: `C:\EQ12\logs\backtester_*.log`
- **Performance**: `C:\EQ12\logs\performance_*.log`

### Contact
- **EQ12 GODSTACK Team**: Internal development channel
- **Issue Tracking**: EQ12 project management system
- **Feature Requests**: EQ12 enhancement pipeline

---

**🎯 EQ12 Historic Backtester - Think like an expert, profit like a champion!**
