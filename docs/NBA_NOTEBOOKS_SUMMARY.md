# EQ12 NBA Notebooks - Complete Summary

**Generated:** 2025-11-27  
**Repository:** C:\EQ12_BROKEN_20251122_210342  
**JupyterLab Container:** eq12-jupyter-dataviz (Port 8889)  
**Total Notebooks:** 37 (3 existing + 34 generated)

---

## Quick Start

### 1. Start Jupyter Container

```powershell
docker-compose up -d jupyter
docker logs eq12-jupyter-dataviz
```

### 2. Access JupyterLab

- **URL:** http://localhost:8889/?token=eq12-dataviz-token
- **Token:** `eq12-dataviz-token`
- **Working Directory:** `/home/jovyan/work/notebooks/nba`

### 3. Verify Environment

Open `NBA_MASTER_INDEX.ipynb` and run the verification cells to check:
- Python packages installed
- API keys configured
- NBA API connectivity
- Notebook inventory

---

## Directory Structure

```
C:\EQ12_BROKEN_20251122_210342\notebooks\nba\
├── NBA_MASTER_INDEX.ipynb ..................... Central navigation hub
├── 01_data_ingestion\
│   ├── nba_data_ingestion.ipynb ............... Fetch game logs, team stats, odds (✅ Existing)
│   ├── nba_data_cleaning.ipynb ................ Normalize data, handle missing values
│   ├── nba_feature_engineering.ipynb .......... Generate PER, TS%, usage, advanced metrics
│   ├── nba_injury_updates.ipynb ............... Scrape daily injury reports
│   └── nba_schedule_sync.ipynb ................ Merge schedule with odds feed
├── 02_eda\
│   ├── nba_exploratory_analysis.ipynb ......... General EDA (✅ Existing)
│   ├── nba_team_trends.ipynb .................. Team performance, home/away splits
│   ├── nba_player_trends.ipynb ................ Player stats, efficiency trends
│   ├── nba_matchup_analytics.ipynb ............ Head-to-head, pace, defense
│   ├── nba_odds_vs_actuals.ipynb .............. Betting line vs outcome analysis
│   └── nba_referee_impact.ipynb ............... Referee tendencies on fouls/totals
├── 03_models\
│   ├── nba_ml_models.ipynb .................... General ML models (✅ Existing)
│   ├── nba_spread_model.ipynb ................. Point spread predictions (gradient boosting)
│   ├── nba_total_model.ipynb .................. Over/Under regression models
│   ├── nba_moneyline_model.ipynb .............. Win probability (logistic regression)
│   ├── nba_player_prop_model.ipynb ............ Props predictions (points/rebounds/assists)
│   ├── nba_simulation_engine.ipynb ............ Monte Carlo game simulations
│   └── nba_backtest.ipynb ..................... Historical validation, ROI analysis
├── 04_betting\
│   ├── nba_value_bets.ipynb ................... Edge detection (model vs market)
│   ├── nba_parlay_builder.ipynb ............... Correlated SGP builder with EV
│   ├── nba_bankroll_simulation.ipynb .......... Kelly Criterion, unit sizing, variance
│   ├── nba_live_betting.ipynb ................. In-game opportunities
│   └── nba_alert_system.ipynb ................. Telegram/Discord alerts for high-EV bets
├── 05_dashboards\
│   ├── nba_team_dashboard.ipynb ............... Team stats, form, schedule
│   ├── nba_player_dashboard.ipynb ............. Player metrics, prop trends
│   ├── nba_betting_dashboard.ipynb ............ Daily picks, bankroll, ROI charts
│   ├── nba_heatmaps.ipynb ..................... Shot charts, defensive zones, pace
│   └── nba_trend_tracker.ipynb ................ Rolling stats, streaks, trends
├── 06_automation\
│   ├── nba_daily_runner.ipynb ................. Master pipeline runner
│   ├── nba_odds_sync.ipynb .................... Odds fetcher (30-min intervals)
│   ├── nba_results_update.ipynb ............... Game results updater
│   ├── nba_telegram_integration.ipynb ......... Daily picks sender
│   └── nba_git_sync.ipynb ..................... Auto-commit outputs/snapshots
└── 07_experimental\
    ├── nba_quantum_model.ipynb ................ Quantum annealing portfolio optimization
    ├── nba_cluster_analysis.ipynb ............. K-means team/player archetypes
    ├── nba_market_efficiency.ipynb ............ EMH testing on betting markets
    └── nba_agent_training.ipynb ............... Reinforcement learning live betting agent
```

---

## Category Breakdown

### 01. Data Ingestion (5 notebooks)

**Purpose:** Fetch, clean, and prepare NBA data from multiple sources

**Dependencies:**
- `nba-api` - Official NBA Stats API wrapper
- `requests` - HTTP client for OddsAPI
- `beautifulsoup4` - Web scraping for injury reports
- `pandas` - Data manipulation

**Key Outputs:**
- `C:/EQ12/data/nba/game_logs_YYYYMMDD.csv`
- `C:/EQ12/data/nba/odds_YYYYMMDD.json`
- `C:/EQ12/data/nba/injuries_YYYYMMDD.csv`
- `C:/EQ12/data/nba/schedule_YYYYMMDD.csv`

**Recommended Execution Order:**
1. `nba_data_ingestion.ipynb` - Fetch raw data
2. `nba_injury_updates.ipynb` - Get injury reports
3. `nba_schedule_sync.ipynb` - Merge schedule/odds
4. `nba_data_cleaning.ipynb` - Normalize data
5. `nba_feature_engineering.ipynb` - Generate advanced metrics

---

### 02. Exploratory Data Analysis (6 notebooks)

**Purpose:** Uncover trends, patterns, and insights

**Dependencies:**
- `matplotlib` - Static plotting
- `seaborn` - Statistical visualization
- `plotly` - Interactive charts
- `scipy` - Statistical tests

**Key Insights:**
- Team performance trends (home/away, vs conference)
- Player usage patterns and efficiency metrics
- Matchup analysis (pace, defensive rating, net rating)
- Betting line accuracy (closing line value)
- Referee impact on totals and foul calls

**Typical Workflow:**
1. Load cleaned data from 01_data_ingestion
2. Generate summary statistics
3. Create visualizations (trends, correlations, distributions)
4. Document findings in markdown cells
5. Export charts to `C:/EQ12/logs/charts/`

---

### 03. Machine Learning Models (7 notebooks)

**Purpose:** Build predictive models for spread, totals, moneyline, props

**Dependencies:**
- `scikit-learn` - ML algorithms (RandomForest, XGBoost, LogisticRegression)
- `xgboost` - Gradient boosting
- `lightgbm` - Fast gradient boosting
- `tensorflow` or `torch` - Deep learning (optional)

**Model Performance Tracking:**
- Accuracy, Precision, Recall, F1 (classification)
- MSE, RMSE, MAE, R² (regression)
- ROI, CLV (closing line value), Expected Value

**Backtesting Period:**
- Training: 2020-2023 seasons
- Validation: 2023-2024 season
- Test: 2024-2025 season (current)

**Output Format:**
```json
{
  "model_name": "XGBoost Spread Model",
  "training_date": "2025-11-27",
  "accuracy": 0.58,
  "roi": 7.2,
  "picks": [
    {"game": "LAL @ BOS", "prediction": "LAL +5.5", "confidence": 0.72}
  ]
}
```

---

### 04. Betting Strategies (5 notebooks)

**Purpose:** Identify value bets, build parlays, manage bankroll

**Dependencies:**
- Models from `03_models/`
- Odds data from `01_data_ingestion/nba_odds_sync.ipynb`
- `scipy.optimize` - Portfolio optimization

**Key Metrics:**
- **Expected Value (EV):** `(Prob_win * Payout) - (Prob_loss * Stake)`
- **Kelly Criterion:** `f* = (bp - q) / b` where b=odds, p=win probability, q=1-p
- **Sharpe Ratio:** `(Mean_return - Risk_free_rate) / Std_dev`

**Alert Triggers:**
- EV > 5% → Send to Telegram
- Model probability > Market probability by 10% → High-value alert
- Parlay EV > 15% → Premium alert

**Integration:**
- `nba_utils.send_telegram_alert()` for notifications
- `nba_utils.save_snapshot()` for bet tracking

---

### 05. Dashboards & Visualization (5 notebooks)

**Purpose:** Interactive dashboards for analysis and monitoring

**Dependencies:**
- `plotly` - Interactive charts
- `dash` or `streamlit` - Web dashboards (optional)
- `ipywidgets` - Jupyter widgets

**Dashboard Components:**
- **Team Dashboard:** Recent form table, upcoming games, injury impact
- **Player Dashboard:** Usage trends, prop bet odds, consistency metrics
- **Betting Dashboard:** Today's picks, P/L chart, ROI tracker, bankroll simulation
- **Heatmaps:** Shot charts, court zones, referee tendencies
- **Trend Tracker:** Rolling averages, streaks, season comparisons

**Refresh Schedule:**
- Team/Player dashboards: Daily (pre-games)
- Betting dashboard: Real-time (during games)
- Trend tracker: Weekly

---

### 06. Automation (5 notebooks)

**Purpose:** Scheduled execution of data pipelines and alerts

**Dependencies:**
- Windows Task Scheduler or cron jobs
- `papermill` - Parameterized notebook execution
- `nbconvert` - Notebook to HTML/PDF conversion

**Automation Schedule:**

| Notebook | Frequency | Time (EST) | Purpose |
|----------|-----------|------------|---------|
| `nba_odds_sync.ipynb` | Every 30 min | 09:00-00:00 | Fetch latest odds |
| `nba_injury_updates.ipynb` | Daily | 08:00 | Morning injury reports |
| `nba_daily_runner.ipynb` | Daily | 10:00 | Run full pipeline |
| `nba_results_update.ipynb` | Daily | 02:00 | Update completed games |
| `nba_telegram_integration.ipynb` | Daily | 11:00 | Send today's picks |
| `nba_git_sync.ipynb` | Daily | 03:00 | Commit snapshots |

**Task Scheduler Example:**
```powershell
# Create scheduled task for daily runner
$action = New-ScheduledTaskAction -Execute "jupyter" -Argument "nbconvert --execute --to html C:\EQ12_BROKEN_20251122_210342\notebooks\nba\06_automation\nba_daily_runner.ipynb"
$trigger = New-ScheduledTaskTrigger -Daily -At 10:00AM
Register-ScheduledTask -TaskName "EQ12_NBA_Daily_Runner" -Action $action -Trigger $trigger
```

---

### 07. Experimental (4 notebooks)

**Purpose:** Cutting-edge research and advanced techniques

**Dependencies:**
- `qiskit` or `dwave-ocean-sdk` - Quantum computing
- `sklearn.cluster` - Clustering algorithms
- `stable-baselines3` - Reinforcement learning
- `arch` - Time series models (GARCH, ARCH)

**Research Topics:**

**Quantum Model:**
- Use quantum annealing to optimize parlay portfolios
- Constraint: Total correlation < threshold
- Objective: Maximize expected value

**Cluster Analysis:**
- K-means clustering of teams by playstyle
- Identify archetypes: "High pace offense", "Elite defense", "Balanced"
- Use for matchup analysis

**Market Efficiency:**
- Test weak-form EMH on NBA betting markets
- Autocorrelation in line movements
- Arbitrage opportunity detection

**Agent Training:**
- RL agent for live betting (Q-learning, DQN)
- State: Current score, time remaining, possession
- Action: Bet spread/total/moneyline or wait
- Reward: Profit/loss from bet

---

## Shared Utilities (`nba_utils.py`)

**Location:** `C:\EQ12\scripts\nba_utils.py`

**Key Functions:**

### Data Fetchers
- `fetch_nba_odds()` - Get current odds from The Odds API
- `fetch_nba_teams()` - Team information from nba-api
- `fetch_nba_games()` - Team game logs
- `fetch_player_stats()` - Player game logs

### Plotting Templates
- `plot_team_trend()` - Interactive line chart with rolling average
- `plot_correlation_heatmap()` - Feature correlation matrix
- `plot_betting_performance()` - Daily P/L + cumulative profit

### Model Evaluation
- `evaluate_classification_model()` - Accuracy, Precision, Recall, F1, AUC
- `evaluate_regression_model()` - MSE, RMSE, MAE, R²
- `calculate_betting_roi()` - Win rate, total profit, ROI%

### Alert Systems
- `send_telegram_alert()` - Send message to Telegram
- `send_discord_alert()` - Send message to Discord webhook

### Data Caching
- `cache_data()` - Save JSON snapshot with timestamp
- `load_cached_data()` - Load recent cache if not expired

### Utilities
- `setup_logging()` - Configure structured logging
- `save_snapshot()` - Export DataFrame to CSV
- `format_currency()` - Format dollar amounts
- `format_percentage()` - Format percentages

---

## Environment Configuration

### Required API Keys (`.env`)

```bash
# Odds Data
ODDS_API_KEY=your_odds_api_key_here

# Alerts
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
DISCORD_WEBHOOK_URL=your_discord_webhook_url

# Optional
OPENAI_API_KEY=your_openai_key_for_llm_analysis
```

### Python Dependencies

```bash
# Core
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0

# NBA Data
nba-api>=1.3.0
requests>=2.31.0
beautifulsoup4>=4.12.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.14.0

# Machine Learning
scikit-learn>=1.3.0
xgboost>=2.0.0
lightgbm>=4.0.0

# Automation
papermill>=2.4.0
nbconvert>=7.6.0
python-dotenv>=1.0.0

# Optional (Experimental)
tensorflow>=2.13.0  # or torch>=2.0.0
qiskit>=0.44.0
dwave-ocean-sdk>=6.6.0
stable-baselines3>=2.1.0
```

### Docker Installation

```bash
# Install in Jupyter container
docker exec -it eq12-jupyter-dataviz bash
conda install -c conda-forge nba-api xgboost lightgbm
pip install plotly beautifulsoup4 python-dotenv papermill
```

---

## Workflow Examples

### Daily Analysis Workflow

1. **Morning (08:00 AM):**
   - Run `nba_injury_updates.ipynb` - Check injury reports
   - Run `nba_schedule_sync.ipynb` - Get today's games

2. **Pre-Game (10:00 AM):**
   - Run `nba_daily_runner.ipynb` - Execute full pipeline
   - Review `nba_betting_dashboard.ipynb` - See today's picks
   - Check Telegram alerts for high-EV bets

3. **During Games (Live):**
   - Monitor `nba_live_betting.ipynb` - In-game opportunities
   - Track `nba_odds_sync.ipynb` - Line movements

4. **Post-Game (02:00 AM):**
   - Run `nba_results_update.ipynb` - Update database
   - Run `nba_git_sync.ipynb` - Commit snapshots

### Model Development Workflow

1. **Data Preparation:**
   - `01_data_ingestion/nba_data_cleaning.ipynb`
   - `01_data_ingestion/nba_feature_engineering.ipynb`

2. **EDA:**
   - `02_eda/nba_team_trends.ipynb`
   - `02_eda/nba_matchup_analytics.ipynb`

3. **Model Building:**
   - `03_models/nba_spread_model.ipynb` - Train model
   - `03_models/nba_backtest.ipynb` - Validate performance

4. **Production Deployment:**
   - `04_betting/nba_value_bets.ipynb` - Generate picks
   - `06_automation/nba_daily_runner.ipynb` - Automate

---

## Git Workflow

### Auto-Commit Strategy

`nba_git_sync.ipynb` automatically commits:
- Notebook outputs (executed .ipynb files)
- Data snapshots (CSV/JSON in `C:/EQ12/logs/`)
- Model artifacts (pickled models in `C:/EQ12/models/`)

**Git LFS for Large Files:**
```bash
git lfs track "*.csv"
git lfs track "*.pkl"
git lfs track "*.h5"
```

**Commit Message Format:**
```
Auto-commit: NBA analysis YYYY-MM-DD

- Executed notebooks: nba_daily_runner, nba_spread_model
- Snapshots: game_logs_20251127.csv, odds_20251127.json
- Models: spread_model_v3.pkl (Accuracy: 58.2%)
- Picks: 5 bets (EV: 12.3%)
```

---

## Troubleshooting

### Jupyter Container Not Starting

```powershell
# Check container status
docker ps -a | Select-String "eq12-jupyter-dataviz"

# View logs
docker logs eq12-jupyter-dataviz

# Restart
docker-compose restart jupyter
```

### NBA API Rate Limits

```python
# Add delay between requests
import time
time.sleep(1)  # 1 second delay

# Cache responses
from nba_utils import cache_data, load_cached_data
cached = load_cached_data("team_logs_LAL", max_age_hours=24)
if cached is None:
    data = fetch_nba_games("LAL")
    cache_data(data, "team_logs_LAL")
```

### Missing Python Packages

```bash
# Install in Jupyter container
docker exec -it eq12-jupyter-dataviz pip install nba-api xgboost
```

### Odds API Quota Exceeded

```python
# Check remaining requests
response = requests.get("https://api.the-odds-api.com/v4/sports/basketball_nba/odds", 
                        params={"apiKey": api_key})
print(f"Remaining requests: {response.headers.get('X-Requests-Remaining')}")

# Use cached data when quota low
if int(response.headers.get('X-Requests-Remaining', 0)) < 10:
    data = load_cached_data("nba_odds", max_age_hours=1)
```

---

## Next Steps

1. **Start Jupyter:**
   ```powershell
   docker-compose up -d jupyter
   ```

2. **Open Master Index:**
   - Navigate to http://localhost:8889/?token=eq12-dataviz-token
   - Open `notebooks/nba/NBA_MASTER_INDEX.ipynb`

3. **Configure API Keys:**
   - Edit `C:/EQ12/.env`
   - Add ODDS_API_KEY, TELEGRAM_BOT_TOKEN, etc.

4. **Run First Analysis:**
   - Execute `01_data_ingestion/nba_data_ingestion.ipynb`
   - Verify data fetched successfully

5. **Schedule Automation:**
   - Create Windows Task for `nba_daily_runner.ipynb`
   - Test with `papermill` execution

6. **Deploy Models:**
   - Train initial models in `03_models/`
   - Generate first picks in `04_betting/nba_value_bets.ipynb`

---

**Last Updated:** 2025-11-27  
**Maintainer:** EQ12 Expert Quantum System  
**Documentation:** This file + `NBA_MASTER_INDEX.ipynb`
