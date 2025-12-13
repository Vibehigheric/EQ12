# Machine Learning & Predictive Modeling

## Model Overview

The EQ12 Predictive Engine uses supervised learning to forecast sports outcomes with high calibration accuracy.

## Architecture

### Training Pipeline

```
Raw Sports Data
       ↓
Feature Engineering
  - Team stats (offensive/defensive rating)
  - Player metrics (xwOBA, usage, impact)
  - Environmental factors (weather, venue, travel)
  - Market data (odds movement, implied probability)
       ↓
Data Validation & Normalization
       ↓
Cross-Validation (Rolling Window)
       ↓
Model Training (XGBoost / LightGBM)
       ↓
Hyperparameter Optimization (Bayesian Search)
       ↓
Model Evaluation (Brier Score, Log Loss, ROI)
       ↓
Calibration Check
       ↓
Azure ML Registration
       ↓
Staging Deployment → Production Deployment
```

### Prediction Flow

```
Live Match Data + Odds
       ↓
Load Trained Model
       ↓
Extract Features (Real-time)
       ↓
Predict p_true (True Win Probability)
       ↓
Calculate EV = p_true × payout - (1 - p_true)
       ↓
Kelly Fraction → Stake Size
       ↓
Return {p_true, EV, recommended_stake}
       ↓
Log Prediction + Execute (Paper Trading)
```

## Algorithms

### Primary Models
1. **XGBoost** (Gradient Boosting)
   - Excellent for mixed feature types
   - Handles categorical variables well
   - Fast inference time

2. **LightGBM** (Light Gradient Boosting)
   - Lower memory footprint
   - Faster training on large datasets
   - Similar performance to XGBoost

3. **Logistic Regression** (Baseline Calibration)
   - Reference model for calibration
   - Provides linear coefficients for interpretation
   - Fast training and inference

### Hyperparameters (Example)

```yaml
XGBoost:
  n_estimators: 500
  max_depth: 8
  learning_rate: 0.05
  subsample: 0.8
  colsample_bytree: 0.8
  reg_alpha: 1.0
  reg_lambda: 2.0

LightGBM:
  num_leaves: 31
  max_depth: 8
  learning_rate: 0.05
  n_estimators: 500
  subsample_for_bin: 200000
  feature_fraction: 0.8
```

## Feature Engineering

### Raw Features (Inputs)

#### Team Statistics
- Win/loss ratio (last 10 games)
- Points for / Points against (offensive/defensive rating)
- Strength of schedule
- Pace of play
- Home/away splits

#### Player Metrics
- Usage rate (% of touches)
- True shooting percentage
- Box plus/minus (individual impact rating)
- Player efficiency rating (PER)
- Return on investment (offensive rating contribution)

#### Environmental Factors
- Home/away designation
- Back-to-back games
- Travel distance
- Weather conditions (wind, temperature, humidity)
- Altitude
- Time zone differences
- Days of rest

#### Market Data
- Opening odds
- Current odds (live movement)
- Implied probability from bookmaker
- Market consensus (% backing)
- Line movement (indicator of sharp money)

### Derived Features (Engineering)

```python
# Form Index (weighted average of last 5 games)
form_index = np.average(recent_results, weights=[0.3, 0.25, 0.2, 0.15, 0.1])

# Market Edge (predictor vs bookmaker)
market_edge = predicted_prob - implied_prob

# Confidence Score (model certainty)
confidence = abs(0.5 - predicted_prob) * 2

# Expected Value (ROI per bet)
ev = (predicted_prob * decimal_odds) - 1

# Kelly Fraction (optimal stake size)
kelly = (confidence * edge) / odds_diff
```

## Model Evaluation Metrics

| Metric            | Definition                      | Good Range | Target   |
| --------------- | -------------------------------- | ---------- | -------- |
| **Brier Score**   | MSE of probability predictions  | 0.0 - 1.0  | < 0.20   |
| **Log Loss**      | Penalized probability error     | 0.0 - ∞    | < 0.70   |
| **Calibration Slope** | Regression of predicted vs actual | 0.8 - 1.2 | ≈ 1.0   |
| **ROI**           | Return on Investment            | -∞ to ∞    | > 10%    |
| **Sharpe Ratio**  | Risk-adjusted return            | -∞ to ∞    | > 1.2    |
| **Max Drawdown**  | Largest % drop from peak equity | 0% - 100%  | < 25%    |
| **Win Rate**      | Winning bets / Total bets       | 0% - 100%  | > 55%    |

## Training Process

### Step 1: Data Collection
```bash
python scripts/collect_historical_data.py \
  --sport nfl \
  --start-date 2023-01-01 \
  --end-date 2024-12-31 \
  --output data/training_data.csv
```

### Step 2: Feature Engineering
```bash
python scripts/feature_engineer.py \
  --input data/training_data.csv \
  --output data/features.csv \
  --lookback 10
```

### Step 3: Model Training
```bash
python scripts/train_model.py \
  --features data/features.csv \
  --targets data/outcomes.csv \
  --algorithm xgboost \
  --cv-folds 5 \
  --output models/eq12_optimizer.pkl
```

### Step 4: Evaluation
```bash
python scripts/evaluate_model.py \
  --model models/eq12_optimizer.pkl \
  --test-data data/test_set.csv \
  --metrics brier,logloss,roi,sharpe
```

### Step 5: Registration (Azure ML)
```bash
python scripts/register_model.py \
  --model models/eq12_optimizer.pkl \
  --name EQ12BettingOptimizer \
  --tags sport=nfl,version=v2
```

## Model Deployment

### Staging Environment
```bash
python scripts/deploy_model.py \
  --model-name EQ12BettingOptimizer \
  --environment staging \
  --compute Standard_D2s_v3
```

### Production Environment
```bash
python scripts/deploy_model.py \
  --model-name EQ12BettingOptimizer \
  --environment production \
  --compute Standard_NC6s_v3 \
  --replicas 3
```

## Inference API

### REST Endpoint
```
POST /predict
Content-Type: application/json

{
  "match_id": "nfl_2024_001",
  "home_team": "KC",
  "away_team": "DEN",
  "odds": {
    "moneyline": 1.53,
    "spread": -3.5
  }
}

Response:
{
  "predicted_probability": 0.68,
  "expected_value": 0.042,
  "recommended_stake": 50.00,
  "confidence": 0.85,
  "model_version": "v2.1"
}
```

## Retraining Schedule

- **Daily**: Quick recalibration with new outcomes
- **Weekly**: Feature importance analysis and drift detection
- **Monthly**: Full retrain with 90 days of new data
- **Quarterly**: Hyperparameter optimization

## Drift Detection

```python
# Brier Score deterioration
current_brier = evaluate_brier_score(predictions, actuals)
historical_brier = 0.18

if current_brier > (historical_brier * 1.15):
    logger.warning("Model drift detected! Brier increased 15%+")
    trigger_retraining()

# Accuracy by confidence percentile
if accuracy[90th_percentile] < 0.60:
    logger.warning("Low confidence predictions not performing")
    adjust_kelly_multiplier(0.8)
```

## Performance Baseline (Target)

```
Model: EQ12 Optimizer v2.1 (XGBoost)
Training Data: 2020-2023 (1,500 games)
Test Data: Jan-Dec 2024 (400 games)

Metrics:
├─ Brier Score: 0.184 ✅
├─ Log Loss: 0.654 ✅
├─ Calibration Slope: 0.97 ✅
├─ ROI (Paper Trading): +12.3% ✅
├─ Sharpe Ratio: 1.54 ✅
├─ Max Drawdown: 18.2% ✅
├─ Win Rate: 56.8% ✅
└─ Inference Time: 45ms ✅
```

## Next Steps

- [ ] Implement ensemble methods (stacking, blending)
- [ ] Add LSTM models for sequential betting data
- [ ] Integrate real-time feature updates
- [ ] Build active learning feedback loop
- [ ] Expand to more sports (NBA, NHL, MLS)
