# EQ12 Sports Parlay Analyzer

## 🏒🏀 Automated NHL and NBA Parlay Analysis Tool

The EQ12 Sports Parlay Analyzer fetches today's NHL and NBA preseason games using The Odds API and creates intelligent parlay suggestions based on value analysis.

## ✨ Features

- **Real-time Data**: Fetches live odds from The Odds API
- **Multi-Sport Analysis**: Covers NHL and NBA preseason games
- **Smart Value Detection**: Analyzes moneyline, spread, and total bets
- **Parlay Generation**: Creates optimized 2-leg parlay suggestions
- **Confidence Scoring**: Rates each bet and parlay combination
- **Historical Logging**: Saves detailed analysis to JSON logs
- **Cross-platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### 1. Get API Key
Sign up for a free API key at [The Odds API](https://the-odds-api.com/#get-access)

### 2. Set Environment Variable (Recommended)
```powershell
# Windows PowerShell
$env:ODDS_API_KEY = "your_api_key_here"

# Windows Command Prompt
set ODDS_API_KEY=your_api_key_here

# Linux/macOS
export ODDS_API_KEY="your_api_key_here"
```

### 3. Run Analysis
```powershell
# PowerShell (Windows)
.\eq12_sports_parlay_analyzer.ps1

# Python (Cross-platform)
python eq12_sports_parlay_analyzer.py
```

## 📋 Usage Examples

### PowerShell Wrapper (Windows)
```powershell
# Basic analysis
.\eq12_sports_parlay_analyzer.ps1

# With API key parameter
.\eq12_sports_parlay_analyzer.ps1 -ApiKey "your_key_here"

# Verbose mode for debugging
.\eq12_sports_parlay_analyzer.ps1 -Verbose

# Save to logs only (no console output)
.\eq12_sports_parlay_analyzer.ps1 -SaveOnly

# Show help
.\eq12_sports_parlay_analyzer.ps1 -Help
```

### Python Script (Cross-platform)
```bash
# Basic analysis
python eq12_sports_parlay_analyzer.py

# With API key
python eq12_sports_parlay_analyzer.py --api-key "your_key_here"

# Verbose logging
python eq12_sports_parlay_analyzer.py --verbose

# Save only mode
python eq12_sports_parlay_analyzer.py --save-only
```

## 📊 Output Example

```
🏒🏀 EQ12 SPORTS PARLAY ANALYSIS - 2025-10-09
============================================================

📊 SUMMARY:
   • Total games analyzed: 8
   • High confidence games: 3
   • Parlay suggestions: 2
   • Sports with games: nhl, nba_preseason

🎯 GAMES FOUND:
   🏒 NHL: 6 games
   🏀 NBA_PRESEASON: 2 games

⭐ HIGH VALUE GAMES:
   🏒 Boston Bruins @ Toronto Maple Leafs (Confidence: 60%)
      └─ SPREAD: Boston Bruins +1.5 (+105)
         Close spread suggests competitive game
   🏀 Lakers @ Clippers (Confidence: 45%)
      └─ TOTAL: Over 215.5 (-110)
         NBA preseason total in reasonable range

💰 PARLAY SUGGESTIONS:

   PARLAY #1 (Confidence: 52.5%)
   LEG 1: Boston Bruins @ Toronto Maple Leafs
           SPREAD: Boston Bruins +1.5 (+105)
           Close spread suggests competitive game
   LEG 2: Lakers @ Clippers
           TOTAL: Over 215.5 (-110)
           NBA preseason total in reasonable range
```

## 📁 Log Files

Analysis results are automatically saved to:
- **Windows**: `C:\EQ12\logs\parlay_analysis_YYYY-MM-DD.json`
- **Linux/macOS**: `./logs/parlay_analysis_YYYY-MM-DD.json`

Log files contain:
- Detailed game analysis
- All betting options considered
- Confidence calculations
- API response metadata
- Timestamps for historical tracking

## 🔧 Requirements

- **Python 3.8+**
- **requests** library (`pip install requests`)
- **The Odds API key** (free tier available)

## ⚙️ Configuration

The analyzer supports these sports (automatically detected):
- `icehockey_nhl` - NHL regular season
- `basketball_nba_preseason_sg` - NBA preseason
- `basketball_nba` - NBA regular season (fallback)

### Betting Markets Analyzed:
- **h2h** (Head-to-head/Moneyline)
- **spreads** (Point spreads)
- **totals** (Over/Under)

### Confidence Scoring:
- **80-100%**: High confidence, multiple favorable indicators
- **60-79%**: Good value, solid reasoning
- **40-59%**: Moderate confidence, worth considering
- **20-39%**: Low confidence, proceed with caution
- **0-19%**: Very low confidence, avoid

## 🛡️ Responsible Gaming

**IMPORTANT DISCLAIMER**: This tool is for educational and analysis purposes only.

- Always gamble responsibly and within your means
- Never bet more than you can afford to lose
- Gambling can be addictive - seek help if needed
- Past performance does not guarantee future results
- This analysis is not financial advice

## 🔍 How It Works

1. **Data Collection**: Fetches live odds from The Odds API
2. **Value Analysis**: Calculates implied probabilities and identifies value
3. **Game Scoring**: Rates each game based on betting opportunities
4. **Parlay Creation**: Combines high-value bets into parlay suggestions
5. **Confidence Rating**: Assigns confidence scores based on analysis
6. **Logging**: Saves detailed results for historical analysis

## 🐛 Troubleshooting

### Common Issues:

**"No API key provided"**
- Set the `ODDS_API_KEY` environment variable
- Or use the `--api-key` parameter

**"Sport not available"**
- Some sports are seasonal - check available sports at [The Odds API](https://the-odds-api.com/sports-odds-data/sports-apis.html)
- The analyzer automatically falls back to regular season if preseason unavailable

**"No games found"**
- Games are fetched for today only
- Some days may have no scheduled games
- Try on game days for best results

**"requests module not found"**
```bash
pip install requests
```

### Debug Mode:
Add `--verbose` flag to see detailed API calls and analysis steps.

## 📈 Integration with EQ12

This analyzer integrates with the broader EQ12 automation stack:
- Uses existing Odds API infrastructure
- Follows EQ12 logging standards
- Compatible with EQ12 task scheduling
- Leverages EQ12 configuration management

## 🔄 Scheduling

For automated daily analysis, add to your scheduled tasks:
```powershell
# Windows Task Scheduler
schtasks /create /tn "EQ12 Daily Parlay Analysis" /tr "powershell.exe -File C:\EQ12\scripts\eq12_sports_parlay_analyzer.ps1" /sc daily /st 10:00
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review log files in `C:\EQ12\logs\`
3. Ensure your API key is valid and has remaining requests
4. Verify internet connection for API access

---

**Happy analyzing! 🎯🏒🏀**