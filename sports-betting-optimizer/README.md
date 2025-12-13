# 🏈⚽🏀 DraftKings Sports Betting Optimizer

A comprehensive, automated sports betting analysis system designed specifically for **DraftKings Sportsbook** with sport-specific optimization, promo maximization, and EV calculation across all major sports.

## 🎯 **Core Features**

### **Multi-Sport Coverage**
- **🏈 College Football (CFB)** - Mystery Boost + Stepped Up optimizers
- **🏀 NFL** - Same Game Parlay (SGP) + Anytime TD strategies
- **🏀 NBA** - Player props + Triple-double parlays
- **⚾ MLB** - Dinger Tuesday + Pitcher strikeout combos
- **🏒 NHL** - Goal scorer + Shots on goal strategies
- **⚽ Soccer** - BTTS + Goal scorer specials across EPL/MLS/UCL
- **🥊 UFC/Boxing** - Method of victory + Round prop parlays
- **🎾 Tennis** - Match ML + Set betting combinations

### **Automated Promo Optimization**
- **Mystery Boost** (3+ legs, +300 min odds, 25/33/50% boost)
- **Stepped Up Boost** (4-11 legs, scaling 20-105% boost per leg ≥ -400)
- **Same Game Parlays** with correlation analysis
- **Daily Specials** (Dinger Tuesday, Goal Scorer boosts, etc.)

### **EV & Risk Management**
- **Monte Carlo simulations** (10,000+ trials per parlay)
- **True Win %** vs Sportsbook implied probability analysis
- **Kelly Criterion** stake sizing recommendations
- **Bankroll discipline** with automated tracking
- **Risk categorization**: Lock Ticket | High EV | Longshot

---

## 📂 **Repository Structure**

```
sports-betting-optimizer/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config/
│   ├── credentials.json         # API keys, tokens (template)
│   ├── settings.yaml           # Global betting settings
│   └── sport_configs/          # Sport-specific configurations
├── src/
│   ├── core/
│   │   ├── odds_fetcher.py     # OddsAPI integration
│   │   ├── ev_calculator.py    # Expected value calculations
│   │   ├── utils.py            # Shared utilities
│   │   └── database.py         # SQLite data persistence
│   ├── promos/
│   │   ├── mystery_boost.py    # 3+ leg Mystery Boost optimizer
│   │   ├── stepped_boost.py    # 4-11 leg Stepped Up optimizer
│   │   └── master_optimizer.py # Unified promo coordinator
│   ├── sports/
│   │   ├── cfb_optimizer.py    # College Football strategies
│   │   ├── nfl_optimizer.py    # NFL strategies
│   │   ├── nba_optimizer.py    # NBA strategies
│   │   ├── mlb_optimizer.py    # MLB strategies
│   │   ├── nhl_optimizer.py    # NHL strategies
│   │   ├── soccer_optimizer.py # Soccer strategies
│   │   ├── ufc_optimizer.py    # UFC/Boxing strategies
│   │   └── tennis_optimizer.py # Tennis strategies
│   └── notifications/
│       ├── telegram_bot.py     # Telegram alerts
│       └── discord_bot.py      # Discord notifications
├── data/
│   ├── odds_cache/            # Cached odds data with timestamps
│   ├── parlays/               # Generated parlay recommendations
│   └── results/               # Bet tracking and P&L analysis
├── tests/                     # Unit tests for all modules
└── .github/
    └── workflows/
        ├── daily.yml          # Daily odds fetching and analysis
        ├── friday_cfb.yml     # Friday CFB special runs
        └── weekend_sports.yml # Saturday/Sunday multi-sport
```

---

## 🚀 **Quick Start**

### **1. Installation**
```bash
git clone https://github.com/yourusername/sports-betting-optimizer
cd sports-betting-optimizer
pip install -r requirements.txt
```

### **2. Configuration**
```bash
# Copy template and add your API keys
cp config/credentials.json.template config/credentials.json

# Edit with your credentials:
# - OddsAPI key
# - Telegram bot token
# - Discord webhook (optional)
```

### **3. Run Analysis**
```bash
# Daily multi-sport analysis
python src/core/daily_runner.py

# Sport-specific optimization
python src/sports/cfb_optimizer.py --promo mystery_boost
python src/sports/nfl_optimizer.py --promo stepped_boost

# Master optimizer (all promos, all sports)
python src/promos/master_optimizer.py --day friday
```

---

## 📊 **Strategy Breakdown by Sport**

### **🏈 College Football (CFB)**
- **Markets**: Moneyline, Spread, Totals, Player Props (TD scorers, passing/rushing yards)
- **Promos**: Mystery Boost + Stepped Up Boost
- **Safe Strategy**: 3-5 leg parlays with correlated game totals + QB props
- **Lottery Strategy**: 8+ leg "Stepped Up" slips for maximum 105% boost
- **Key Metrics**: YPP, 3rd down %, Red Zone conversion rates

### **🏀 NFL**
- **Markets**: ML, Spread, Totals, Player Props (TD scorers, yards, receptions)
- **Promos**: SGP boost tokens, Sunday Stepped Up boosts
- **Safe Strategy**: TD scorer parlays (RB/WR mix) with game totals
- **Lottery Strategy**: Multi-game Anytime TD slips
- **Key Metrics**: Snap % usage, red zone targets, pass/run splits

### **🏀 NBA**
- **Markets**: ML, Spread, Totals, Player Props (PTS, REB, AST, 3PM)
- **Promos**: SGP boosts (25-50%), weekly parlay insurance
- **Safe Strategy**: Points + Assists combos for high-usage stars
- **Lottery Strategy**: Triple-double parlays
- **Key Metrics**: Usage rate, pace, minutes projections

### **⚾ MLB**
- **Markets**: ML, Run Line, Totals, Player Props (Hits, TB, HR, Strikeouts)
- **Promos**: Dinger Tuesday HR boosts, seasonal Stepped Up parlays
- **Safe Strategy**: Pitcher strikeouts + team ML combos
- **Lottery Strategy**: 3-leg HR parlays, TB + Hits + HR combos
- **Key Metrics**: Exit velocity, launch angle, K/9 rates

### **🏒 NHL**
- **Markets**: ML, Puck Line, Totals, Player Props (Goals, Assists, Shots)
- **Promos**: Goal Scorer Parlays boosts
- **Safe Strategy**: Shots on goal + team ML combos
- **Lottery Strategy**: Anytime goalscorer parlays
- **Key Metrics**: xGF (expected goals for), power play %

### **⚽ Soccer (EPL/MLS/UCL)**
- **Markets**: 3-way ML, Totals, Both Teams to Score, Player Props
- **Promos**: Parlay boosts, Goal Scorer specials
- **Safe Strategy**: BTTS + Over 2.5 goals
- **Lottery Strategy**: Anytime goalscorer slips with big odds
- **Key Metrics**: xG, possession %, form streaks

### **🥊 UFC/Boxing**
- **Markets**: ML, Method of Victory, Round Props, Significant Strikes
- **Promos**: Fight Night parlays, KO/TKO insurance
- **Safe Strategy**: Heavy favorites with decision props
- **Lottery Strategy**: Exact round + method parlays
- **Key Metrics**: Strikes absorbed/min, takedown defense, reach

### **🎾 Tennis**
- **Markets**: Match ML, Set Betting, Total Games
- **Promos**: Grand Slam boosts, parlay insurance
- **Safe Strategy**: Favorite ML + over games combos
- **Lottery Strategy**: Exact set score parlays
- **Key Metrics**: First serve %, break point conversion, surface record

---

## 🤖 **Automated Workflow**

### **Daily GitHub Actions**
1. **Morning (8 AM)**: Fetch fresh odds for all sports via OddsAPI
2. **Midday (12 PM)**: Run Monte Carlo simulations → output best EV parlays
3. **Afternoon (3 PM)**: Telegram bot pushes "✅ Lock Tickets" to your phone
4. **Evening (8 PM)**: Log bet results and update bankroll tracking

### **Friday CFB Special**
- Extra focus on college football with Mystery Boost optimization
- 10+ parlay recommendations across different risk levels
- Correlation analysis for same-game parlays

### **Weekend Multi-Sport**
- Saturday: CFB + Soccer + UFC analysis
- Sunday: NFL + NBA + NHL comprehensive coverage
- Export ready-to-bet CSV files with stake recommendations

---

## 📈 **EV Calculation & Risk Management**

### **Expected Value Formula**
```
EV = (True_Win_Probability × Payout) - (1 - True_Win_Probability) × Stake
EV% = EV / Stake × 100
```

### **Risk Categories**
- **🔒 Lock Ticket**: EV > 5%, Win Probability > 60%
- **💰 High EV**: EV > 2%, moderate risk-reward
- **🎰 Longshot**: EV > 1%, high variance for entertainment

### **Bankroll Management**
- **Kelly Criterion**: Optimal stake sizing based on EV and bankroll
- **Flat Betting**: Conservative fixed-amount approach
- **Martingale Protection**: Loss limits and cool-down periods

---

## 🔔 **Notifications & Alerts**

### **Telegram Integration**
- Real-time alerts when high EV opportunities are found
- Daily summary of recommended bets
- Results tracking with profit/loss updates
- Customizable alert thresholds

### **Discord Integration** (Optional)
- Community sharing of best bets
- Group discussions on strategies
- Automated posting of daily recommendations

---

## 🛠️ **Development & Testing**

### **Running Tests**
```bash
pytest tests/ -v
python -m pytest tests/test_ev_calculator.py
```

### **Adding New Sports**
1. Create new optimizer in `src/sports/`
2. Add sport configuration to `config/sport_configs/`
3. Update master optimizer to include new sport
4. Add tests for new functionality

### **Contributing**
- Fork the repository
- Create feature branch (`git checkout -b feature/new-sport`)
- Add tests and documentation
- Submit pull request

---

## ⚠️ **Disclaimer**

This software is for **educational and analytical purposes only**. Users are responsible for:
- Complying with local gambling laws and regulations
- Using the software responsibly and within their means
- Understanding that all betting involves risk of loss
- Verifying odds and bet details before placing any wagers

**The creators are not responsible for any losses incurred through use of this software.**

---

## 📄 **License**

MIT License - See LICENSE file for details

---

## 🤝 **Support & Community**

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join our Discord for strategy talks
- **Updates**: Follow development progress
- **Contributions**: PRs welcome for new features and improvements

---

*Built by bettors, for bettors. May the odds be ever in your favor! 🍀*
