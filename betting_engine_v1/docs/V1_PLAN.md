# Betting Engine V1 - 30 Day Execution Plan

## Mission
**Ship a working, daily betting pipeline that outputs actionable picks to Telegram.**

## Constraints (The "Tough Love" Rules)
1. **Single Project**: Only work on this. No travel bot, no cannabis bot.
2. **Single Source**: The Odds API (Live) + sports-betting lib (Historical).
3. **Single Output**: Telegram Bot.
4. **No Scope Creep**: No multi-node Swarm, no Coral, no complex MLOps until V1 runs daily.

## Architecture (Minimal)

### 1. Data Ingestion (`src/ingest.py`)
- **Input**: The Odds API (JSON).
- **Storage**: Local JSON/CSV in `data/`.
- **Frequency**: Daily (Cron/Task Scheduler).

### 2. Processing Core (`src/process.py`)
- **Logic**: 
    - Calculate Implied Probability from Odds.
    - Compare vs Historical Baseline (Dummy/Simple Model).
    - Identify Positive EV (Expected Value).
- **Output**: List of "Value Bets".

### 3. Alerting (`src/alert.py`)
- **Channel**: Telegram Bot.
- **Payload**: "Match: X vs Y | Bet: X | EV: +5% | Confidence: Low/Med/High".

## Folder Structure
```
/betting_engine_v1
   /data       # Raw JSON/CSV storage
   /src        # Python scripts (ingest, process, alert)
   /models     # Pickle files for scikit-learn models
   /docs       # Documentation
   /tests      # Pytest files
```

## Immediate Next Steps (Wednesday Prep)
1. [ ] `ping 192.168.1.1` (Network Verification)
2. [ ] Docker Install on M70q.
3. [ ] Deploy `betting_engine_v1` container.
