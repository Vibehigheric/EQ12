# EQ12 EdgeGod Expert Engine - Installation & Setup Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   cd C:\EQ12\EdgeGodParlays
   pip install -r requirements_edgegod.txt
   ```

2. **Configure Environment**
   ```bash
   copy .env.example .env
   # Edit .env with your API keys
   ```

3. **Launch Engine**
   ```bash
   python launch_edgegod.py
   ```

4. **Access Dashboard**
   - [API Endpoints](http://localhost:8080)
   - [Interactive Documentation](http://localhost:8080/docs)
   - [Health Status](http://localhost:8080/health)

## Configuration

### Required Environment Variables

Create `.env` file with these required variables:

```env
# API Configuration
ODDS_API_KEY=your_odds_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Bankroll Management
BANKROLL_BASE=1000
MAX_SINGLE_BET_PERCENTAGE=0.05
MIN_EDGE_THRESHOLD=0.02

# Logging
EQ12_LOGS=C:\EQ12\logs
DEBUG_MODE=false
```

### Optional Configuration

```env
# Advanced Settings
KELLY_FRACTION=0.25
MAX_PARLAY_LEGS=4
MIN_CORRELATION_THRESHOLD=-0.3
INJURY_CHECK_ENABLED=true

# Alert Settings
MIN_ALERT_EDGE=0.05
ALERT_COOLDOWN_MINUTES=30
```

## API Endpoints

### Core Analysis
- `GET /health` - Health check
- `POST /analyze/slate/{date}` - Analyze full slate
- `POST /analyze/game` - Analyze specific game
- `POST /construct/parlay` - Build optimal parlay

### Bankroll Management
- `GET /bankroll/status` - Current bankroll status
- `POST /bankroll/bet` - Calculate bet sizing
- `GET /bankroll/history` - Betting history

### Data Endpoints
- `GET /data/games/{date}` - Get games for date
- `GET /data/odds/{game_id}` - Get odds for game
- `POST /data/refresh` - Refresh all data

## Features

### 🎯 Expert Analysis
- **Kelly Criterion Sizing**: Optimal bet sizing based on edge
- **MLB Injury Analysis**: Automatic injury list exclusions
- **Correlation Detection**: Identify correlated outcomes
- **Value Identification**: Find positive expected value bets

### 📊 Parlay Construction
- **Smart Correlation**: Avoid negatively correlated outcomes
- **Dynamic Sizing**: Adjust for parlay complexity
- **Risk Assessment**: Calculate true parlay probabilities
- **Profit Optimization**: Maximize expected value

### 💰 Bankroll Management
- **Kelly Sizing**: Mathematically optimal bet sizes
- **Risk Controls**: Maximum bet percentage limits
- **Performance Tracking**: Win/loss analysis
- **Drawdown Protection**: Automatic position sizing

### 📱 Real-Time Alerts
- **Telegram Integration**: Instant notifications
- **Value Alerts**: High-edge opportunities
- **Line Movement**: Significant odds changes
- **Injury Updates**: Player status changes

## Usage Examples

### Analyze Today's Slate
```python
import requests

# Get today's analysis
response = requests.post('http://localhost:8080/analyze/slate/today')
analysis = response.json()

print(f"Total Games: {analysis['summary']['total_games']}")
print(f"Value Bets: {analysis['summary']['value_bets_found']}")
```

### Calculate Bet Size
```python
# Calculate optimal bet for 5% edge
bet_data = {
    "odds": -110,
    "probability": 0.55,
    "bankroll": 1000
}

response = requests.post('http://localhost:8080/bankroll/bet', json=bet_data)
sizing = response.json()

print(f"Recommended Bet: ${sizing['recommended_bet']}")
print(f"Kelly Percentage: {sizing['kelly_percentage']:.1%}")
```

### Build Parlay
```python
# Construct 3-leg parlay
parlay_request = {
    "games": ["game_1", "game_2", "game_3"],
    "max_legs": 3,
    "min_edge": 0.02
}

response = requests.post('http://localhost:8080/construct/parlay', json=parlay_request)
parlay = response.json()

print(f"Parlay Odds: {parlay['combined_odds']}")
print(f"Expected Value: {parlay['expected_value']:.1%}")
```

## Monitoring

### Log Files
- `edgegod_engine.log` - Application logs
- `C:\EQ12\logs\` - Analysis snapshots
- `bankroll_history.json` - Betting records

### Health Checks
```bash
# Check engine status
curl http://localhost:8080/health

# Verify API connectivity
curl http://localhost:8080/data/refresh
```

### Performance Metrics
- API response times
- Analysis accuracy
- Profit/loss tracking
- Alert delivery rates

## Troubleshooting

### Common Issues

1. **API Key Invalid**
   ```
   Error: 401 Unauthorized
   Solution: Verify ODDS_API_KEY in .env
   ```

2. **Telegram Not Working**
   ```
   Error: Telegram API failed
   Solution: Check BOT_TOKEN and CHAT_ID
   ```

3. **No Games Found**
   ```
   Error: No games available
   Solution: Check date format (YYYY-MM-DD)
   ```

### Debug Mode
Enable debug logging:
```env
DEBUG_MODE=true
```

### API Limits
- The Odds API: 500 requests/month (free tier)
- Telegram: 30 messages/second
- Rate limiting: Built-in backoff

## Integration

### PowerShell Wrapper
```powershell
# Start engine
& python "C:\EQ12\EdgeGodParlays\launch_edgegod.py"

# Check status
Invoke-RestMethod -Uri "http://localhost:8080/health"
```

### Scheduled Tasks
Create Windows Task Scheduler entry:
- Program: `python`
- Arguments: `C:\EQ12\EdgeGodParlays\launch_edgegod.py`
- Start In: `C:\EQ12\EdgeGodParlays`

### CI/CD Integration
GitHub Actions workflow for testing:
```yaml
- name: Test EdgeGod Engine
  run: |
    cd EdgeGodParlays
    pip install -r requirements_edgegod.txt
    python -m pytest test_edgegod.py
```

## Security

### API Keys
- Store in `.env` file (never commit)
- Use environment variables in production
- Rotate keys regularly

### Network Security
- Run on localhost by default
- Use reverse proxy for external access
- Enable HTTPS in production

### Data Protection
- Logs contain no sensitive data
- Bankroll data encrypted at rest
- API responses sanitized

## Support

For issues or questions:
1. Check logs: `edgegod_engine.log`
2. Verify configuration: `.env`
3. Test endpoints: `/docs`
4. Review EQ12 documentation: `AGENTS.md`

## Advanced Configuration

### Custom Strategies
Extend the engine by modifying:
- `MLBExpertAnalyzer` - Game analysis logic
- `ParlayConstructor` - Parlay building rules
- `BankrollManager` - Sizing algorithms

### API Extensions
Add custom endpoints in `edgegod_expert_engine.py`:
```python
@app.get("/custom/strategy")
async def custom_analysis():
    # Your custom logic here
    return {"status": "success"}
```

### Data Sources
Configure additional data sources:
- Player prop APIs
- Injury report feeds
- Weather services
- Public betting percentages
