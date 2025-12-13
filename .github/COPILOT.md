# EQ12 COPILOT ML PARLAY IMPROVEMENT SYSTEM
# Mathematical + ML Learning Framework for Profitable Parlay Selection

## 🎯 PRIMARY MISSION
Transform EQ12 from a 2.98% parlay win rate to profitable betting through mathematical rigor + ML pattern recognition. Learn from 958 analyzed parlays to generate EV+ suggestions with risk controls.

## 📊 CURRENT PERFORMANCE BASELINE
- **Total Parlays Analyzed**: 958 slips
- **Overall Win Rate**: 2.98% (5 wins, 163 losses)
- **Strategy Performance**:
  - SGP Parlays: 100% win rate (2/2 decided)
  - MLB Parlays: 100% win rate (2/2)  
  - NFL Parlays: 0% win rate (0/163)
- **Financial Impact**: $5,220 wagered, need better outcome tracking

## 🧮 MATHEMATICAL FOUNDATIONS

### Expected Value (EV) Calculation
```
EV = (Probability_Win × Payout) - (Probability_Loss × Stake)
EV+ Required: EV > 0 for all suggestions
```

### Kelly Criterion Risk Management
```
Kelly_Fraction = (bp - q) / b
Where: b = odds-1, p = win_probability, q = 1-p
MAX_KELLY = 0.25 (hard cap for safety)
```

### Parlay Math (Cumulative Probability)
```
Parlay_Probability = P1 × P2 × P3 × ... × Pn
Minimum_Edge_Required = 15% above implied_probability
```

## 🤖 ML MODEL SPECIFICATIONS

### Feature Engineering Pipeline
**Location**: `eq12_learn/build_parlay_dataset.py`
**Input**: 958 parlay logs from `logs/` directory
**Features to Extract**:
```python
# Outcome Features
- win_loss_label (target)
- actual_payout_amount
- stake_amount
- net_profit_loss

# Temporal Features
- day_of_week
- month_season
- game_time_hour
- days_since_injury_report

# Team/Player Features
- team_recent_form (last_5_games)
- player_injury_status
- home_away_advantage
- rest_days_difference

# Market Features  
- closing_line_value
- bet_type_category
- parlay_leg_count
- correlation_score

# Historical Performance
- sport_specific_roi
- bet_type_success_rate
- team_vs_spread_history
```

### Model Training Pipeline
**Location**: `eq12_learn/train_parlay_model.py`
**Algorithm**: Calibrated Random Forest + XGBoost ensemble
**Cross-Validation**: TimeSeriesSplit (5 folds)
**Calibration**: Platt scaling for probability accuracy
```python
# Model Stack
primary_model = RandomForestClassifier(
    n_estimators=500,
    max_depth=15,
    class_weight='balanced_subsample'
)
secondary_model = XGBClassifier(
    learning_rate=0.05,
    max_depth=8,
    subsample=0.8
)
calibrator = CalibratedClassifierCV(method='sigmoid')
```

### Prediction Requirements
- **Minimum Confidence**: 65% win probability
- **EV Threshold**: +15% expected value required
- **Correlation Guards**: Max 2 correlated legs per parlay
- **Sample Size**: Minimum 50 historical samples per bet type

## ⚙️ SYSTEM ARCHITECTURE

### Data Pipeline Flow
```
Parlay Logs → Feature Extraction → Model Training → Calibration → API Endpoint
    ↓              ↓                   ↓              ↓            ↓
   958 slips    Features.pkl      Model.pkl    Calibrated.pkl   FastAPI
```

### API Integration
**Endpoint**: `/model/suggest`
**Input**: 
```json
{
  "sport": "NFL|NBA|MLB", 
  "max_legs": 4,
  "budget": 25.00,
  "risk_tolerance": "conservative|moderate|aggressive"
}
```
**Output**:
```json
{
  "suggestions": [
    {
      "legs": ["Team A +3.5", "Over 47.5"],
      "win_probability": 0.72,
      "expected_value": 1.15,
      "kelly_fraction": 0.08,
      "confidence_score": 0.85
    }
  ],
  "risk_analysis": {
    "correlation_warning": false,
    "sample_size_adequate": true,
    "kelly_cap_triggered": false
  }
}
```

## 🛡️ RISK MANAGEMENT GUARDRAILS

### Mandatory Safety Controls
1. **Kelly Criterion Capping**: Max 25% of bankroll per bet
2. **Correlation Limits**: No more than 2 correlated legs
3. **Minimum Sample Size**: 50+ historical examples required
4. **EV Floor**: Minimum +15% expected value
5. **Confidence Threshold**: 65% win probability minimum
6. **Cost Controls**: Max $50 per parlay suggestion
7. **Frequency Limits**: Max 3 parlays per day

### Implementation Locations
- **Kelly Calculator**: `eq12_learn/risk_manager.py`
- **Correlation Detector**: `eq12_learn/correlation_analyzer.py`
- **Cost Guards**: FastAPI middleware validation
- **Frequency Limits**: Redis-based rate limiting

## 🔄 CI/CD WORKFLOW

### Nightly Model Retraining
**File**: `.github/workflows/retrain_parlay_model.yml`
**Schedule**: 2 AM EST daily
**Triggers**:
1. New parlay data in logs/ directory
2. Model performance degradation (accuracy < 60%)
3. Manual trigger via GitHub Actions

**Steps**:
```yaml
- Extract new parlay data since last training
- Validate data quality and completeness
- Retrain model with updated dataset
- Perform backtesting validation
- Deploy new model if performance improved
- Send performance report to Telegram
```

### Performance Monitoring
- **Accuracy Tracking**: Rolling 30-day win rate
- **EV Validation**: Track actual vs predicted returns
- **Risk Control Verification**: Kelly fraction adherence
- **Alert Thresholds**: <60% accuracy triggers retraining

## 📋 COPILOT DEVELOPMENT TASKS

### Phase 1: Foundation (Week 1)
- [ ] Create `eq12_learn/` directory structure
- [ ] Implement feature extraction from 958 parlay logs
- [ ] Build calibrated ML model with cross-validation
- [ ] Add comprehensive unit tests (>90% coverage)

### Phase 2: Integration (Week 2)  
- [ ] Create FastAPI `/model/suggest` endpoint
- [ ] Implement all risk management guardrails
- [ ] Add EV calculation and Kelly criterion safety
- [ ] Build correlation detection system

### Phase 3: Automation (Week 3)
- [ ] Setup GitHub Actions nightly retraining
- [ ] Create performance monitoring dashboard
- [ ] Add Telegram alerts for model updates
- [ ] Implement backtesting validation pipeline

### Phase 4: Optimization (Week 4)
- [ ] Fine-tune model hyperparameters
- [ ] Add sport-specific model variants
- [ ] Implement ensemble model stacking
- [ ] Create profit maximization algorithms

## 🧪 TESTING REQUIREMENTS

### Unit Tests (pytest)
**Coverage Target**: >90%
**Test Files**:
- `tests/test_feature_extraction.py`
- `tests/test_model_training.py`
- `tests/test_risk_management.py`
- `tests/test_api_endpoints.py`

### Integration Tests
- End-to-end parlay suggestion pipeline
- Model retraining automation
- Risk guardrail validation
- Performance monitoring alerts

### Backtesting Validation
- Historical performance simulation
- Out-of-sample testing (20% holdout)
- Walk-forward analysis validation
- Stress testing with extreme scenarios

## 📈 SUCCESS METRICS

### Primary KPIs
1. **Win Rate Improvement**: Target >35% (from 2.98%)
2. **ROI Positive**: Sustained profitable returns
3. **EV Accuracy**: Predicted vs actual returns within 10%
4. **Risk Adherence**: 100% compliance with Kelly caps

### Secondary Metrics
- Model calibration score (Brier score)
- Suggestion adoption rate by users
- System uptime and response latency
- False positive rate on EV+ predictions

## 🔧 COPILOT IMPLEMENTATION GUIDELINES

### Code Quality Standards
- Type hints for all functions
- Docstrings with mathematical formulas
- Error handling with graceful degradation
- Logging with structured JSON output

### Security Requirements  
- No hardcoded API keys or credentials
- Input validation on all user parameters
- Rate limiting on suggestion endpoints
- Audit logging for all model decisions

### Performance Targets
- Model training: <10 minutes on standard hardware
- Suggestion generation: <2 seconds response time
- Memory usage: <1GB for model inference
- Storage efficiency: Compressed model artifacts

---

## 🎲 MATHEMATICAL BETTING PHILOSOPHY

**"Math First, Gut Never"** - Every suggestion must pass quantitative validation before human consideration. The system prioritizes:

1. **Positive Expected Value**: Never suggest negative EV bets
2. **Proper Bankroll Management**: Kelly criterion compliance always
3. **Statistical Significance**: Adequate sample sizes required
4. **Risk-Adjusted Returns**: Sharpe ratio optimization over raw returns
5. **Correlation Awareness**: Independence validation for parlay legs

The goal is sustainable profitability through mathematical edge, not gambling psychology or intuition.