# EQ12 NBA Analysis - Quick Start Card

## 🚀 One-Line Launch
```powershell
cd C:\EQ12_BROKEN_20251122_210342; .\scripts\EQ12_LAUNCH_NBA_JUPYTER.ps1
```

## 🔗 Access
- **URL:** http://localhost:8889/?token=eq12-dataviz-token
- **Token:** `eq12-dataviz-token`
- **Start:** `NBA_MASTER_INDEX.ipynb`

## 📦 First-Time Setup
```bash
# 1. Start Docker Desktop (manual)

# 2. Launch Jupyter
.\scripts\EQ12_LAUNCH_NBA_JUPYTER.ps1

# 3. Install dependencies (in JupyterLab terminal)
pip install nba-api xgboost lightgbm plotly beautifulsoup4

# 4. Configure .env
# Edit C:\EQ12\.env and add:
ODDS_API_KEY=your_key_here
```

## 📊 Notebook Categories

| Category | Count | Purpose |
|----------|-------|---------|
| 01_data_ingestion | 5 | Fetch/clean NBA data |
| 02_eda | 6 | Explore trends |
| 03_models | 7 | Build ML models |
| 04_betting | 5 | Find value bets |
| 05_dashboards | 5 | Interactive viz |
| 06_automation | 5 | Schedule tasks |
| 07_experimental | 4 | Advanced research |
| **TOTAL** | **37** | **Complete pipeline** |

## 🛠️ Utility Functions (nba_utils.py)

```python
# Import utilities
import sys
sys.path.append("C:/EQ12/scripts")
from nba_utils import *

# Fetch data
teams_df = fetch_nba_teams()
games_df = fetch_nba_games("LAL", "2024-25")
odds = fetch_nba_odds()

# Plot trends
fig = plot_team_trend(games_df, "PTS", "Lakers")
fig.show()

# Send alert
send_telegram_alert("High-EV bet found: LAL +5.5 (12% edge)")

# Cache data
cache_data(odds, "nba_odds")
cached = load_cached_data("nba_odds", max_age_hours=1)
```

## 📁 Key Files
```
C:\EQ12_BROKEN_20251122_210342\
├── scripts\nba_utils.py .............. Shared utilities
├── scripts\EQ12_LAUNCH_NBA_JUPYTER.ps1 Launcher
├── notebooks\nba\NBA_MASTER_INDEX.ipynb Central hub
├── docs\NBA_NOTEBOOKS_SUMMARY.md ..... Full docs
└── EQ12_NBA_SETUP_COMPLETE.md ........ This summary
```

## 🎯 Daily Workflow

**Morning (10 AM):**
1. Open `06_automation/nba_daily_runner.ipynb`
2. Run all cells → Fetches today's games + odds
3. Check `04_betting/nba_value_bets.ipynb` for picks

**Pre-Game (1 hour before tipoff):**
1. Review `05_dashboards/nba_betting_dashboard.ipynb`
2. Verify picks in Telegram alerts

**Post-Game (next morning):**
1. Run `06_automation/nba_results_update.ipynb`
2. Review ROI in `04_betting/nba_bankroll_simulation.ipynb`

## 📞 Support Commands

```powershell
# View logs
docker logs -f eq12-jupyter-dataviz

# Restart Jupyter
docker-compose restart jupyter

# Stop Jupyter
docker-compose stop jupyter

# Shell access
docker exec -it eq12-jupyter-dataviz bash

# Check container status
docker ps | Select-String "jupyter"
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8889 in use | Edit docker-compose.yml ports to 8890:8888 |
| API key error | Check C:\EQ12\.env has ODDS_API_KEY set |
| Container won't start | `docker-compose up -d --force-recreate jupyter` |
| Kernel crashes | Increase memory: `docker update --memory=4g eq12-jupyter-dataviz` |

## 📚 Documentation

- **Full Guide:** `docs/NBA_NOTEBOOKS_SUMMARY.md` (2500+ lines)
- **Master Index:** `notebooks/nba/NBA_MASTER_INDEX.ipynb`
- **Setup Summary:** `EQ12_NBA_SETUP_COMPLETE.md`
- **This Card:** `EQ12_NBA_QUICK_START.md`

---

**Status:** ✅ READY  
**Total Notebooks:** 37  
**Created:** 2025-11-27  
**Next:** Run launcher → Open Master Index → Start analyzing!
