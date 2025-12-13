# 🚀 EQ12 EXPERT LIBRARY MASTERY ROADMAP
## 7-Week Intensive Training Plan for 18 Critical Libraries

**Your Success Path:** Week 1 → Week 7 = Expert-level proficiency in your entire ML/BI/automation stack

---

## 🎯 THE 18 LIBRARIES (In Mastery Order)

### **Tier 1: Foundation (Weeks 1-2)**
Essential for ALL downstream work.

1. **numpy** - numerical computing, arrays, matrices
2. **pandas** - data frames, time series, data manipulation
3. **scipy** - scientific computing, statistics, optimization

### **Tier 2: Machine Learning (Weeks 2-3)**
Core EV engine, drift detection, probability modeling.

4. **scikit-learn** - preprocessing, models, evaluation metrics
5. **xgboost** - gradient boosting (your primary EV model)
6. **lightgbm** - fast gradient boosting (alternative, comparison)

### **Tier 3: Automation & Infrastructure (Week 3-4)**
Daily loops, scheduling, multi-processing.

7. **asyncio** - async I/O, concurrent tasks
8. **schedule** - task scheduling (cron alternative)
9. **multiprocessing** - parallel workers for EV scanning
10. **subprocess** - spawning processes (Python ↔ VB.NET bridge)

### **Tier 4: APIs & Web (Week 4)**
Data pulling, Telegram alerts, REST servers.

11. **requests** - HTTP client (odds, stats, weather pulls)
12. **aiohttp** - async HTTP (for URL scanner)
13. **fastapi** - REST API framework (model serving)

### **Tier 5: Geospatial & Maps (Week 5)**
Food intelligence, travel routing, location scoring.

14. **osmnx** - OpenStreetMap data extraction
15. **geopy** - geocoding (address → lat/lon)
16. **folium** - interactive maps, visualization

### **Tier 6: Data Storage & Config (Week 5-6)**
Database interaction, secrets management.

17. **sqlite3** - SQLite queries (your database layer)
18. **python-dotenv** - environment variable loading

---

## 📅 WEEK-BY-WEEK CURRICULUM

### **WEEK 1: NUMPY + PANDAS FUNDAMENTALS**

#### Day 1-2: NumPy Deep Dive
**Goal:** Master arrays, vectorization, mathematical operations

**Topics:**
- Arrays vs lists (why faster)
- Broadcasting (key for EV calculations)
- Linear algebra (matrix ops for backtesting)
- Random number generation (Monte Carlo simulation)

**Code Exercises:**
```python
# Exercise 1: Create array for 100 MLB players' HR probabilities
import numpy as np
players = np.array([0.08, 0.12, 0.06, ...])  # 100 values
# Calculate expected HRs for 500 AB season
expected_hrs = players * 500
print(expected_hrs)

# Exercise 2: Broadcasting - odds adjustment
american_odds = np.array([-110, -120, +110])
# Convert all to implied probability
implied_probs = np.where(american_odds < 0, 
    abs(american_odds) / (abs(american_odds) + 100),
    100 / (american_odds + 100))

# Exercise 3: Monte Carlo - simulate season
np.random.seed(42)
at_bats = 600
hr_prob = 0.10
season_hrs = np.random.binomial(at_bats, hr_prob, size=10000)
print(f"Mean HRs: {season_hrs.mean()}, Std: {season_hrs.std()}")
```

**Why it matters for EQ12:**
- Expected value calculation = vectorized operations
- Backtesting speed comes from numpy
- Monte Carlo simulation requires broadcasting

---

#### Day 3-4: Pandas Master Class
**Goal:** Load, filter, join, aggregate data like a pro

**Topics:**
- DataFrames and Series
- Indexing and selection
- GroupBy and aggregation
- Merging multiple data sources
- Time series (for daily/weekly loops)

**Code Exercises:**
```python
# Exercise 1: Load player stats, calculate EV
import pandas as pd
stats = pd.read_csv("mlb_players.csv")
# Filter to eligible (600+ AB)
eligible = stats[stats['AB'] >= 600]
# Add EV column
eligible['EV'] = eligible['HR_prob'] * eligible['payout'] - eligible['cost']
print(eligible[['name', 'EV']].sort_values('EV', ascending=False))

# Exercise 2: Merge multiple data sources
players = pd.read_csv("players.csv")
weather = pd.read_csv("weather.csv", parse_dates=['date'])
combined = players.merge(weather, on='game_id')
# Filter to high wind (HRs fly further)
high_wind = combined[combined['wind_mph'] > 12]

# Exercise 3: GroupBy and rolling average
daily_stats = pd.read_csv("daily.csv", parse_dates=['date'])
weekly = daily_stats.groupby(pd.Grouper(key='date', freq='W')).agg({
    'revenue': 'sum',
    'roi': 'mean',
    'conversions': 'count'
})
print(weekly)
```

**Why it matters for EQ12:**
- BI-Core uses pandas for KPI aggregation
- Daily loops read data, transform, write results
- Multi-source data merging = your intelligence engine

---

#### Day 5: Integration Challenge
**Challenge:** Load sports data, aggregate by category, calculate daily EV

```python
# Load 3 CSV files (odds, stats, weather)
# Merge them
# Calculate expected value per bet type
# Group by sportsbook
# Rank by ROI
# Export results

# Should complete in < 30 lines of code
```

---

### **WEEK 2: SCIPY + STATSMODELS FOR PROBABILITY & DRIFT**

#### Day 1-2: SciPy Statistics
**Goal:** Understand distributions, probability tests, optimization

**Topics:**
- Normal distribution + cumulative probability
- Poisson (for rare events like HRs)
- Binomial (win/loss simulation)
- Chi-square test (drift detection prep)
- Kolmogorov-Smirnov test (PSI alternative)

**Code Exercises:**
```python
from scipy import stats
import numpy as np

# Exercise 1: Normal distribution - HR probabilities
mu, sigma = 0.10, 0.02  # Mean HR prob = 10%, std dev = 2%
# What's probability player hits >12% HR rate?
prob = 1 - stats.norm.cdf(0.12, mu, sigma)
print(f"P(HR% > 12%) = {prob:.4f}")

# Exercise 2: Poisson distribution - rare events
# Average 0.8 HRs per game
# Probability of 2+ HRs in a game?
hr_rate = 0.8
prob_2plus = 1 - stats.poisson.cdf(1, hr_rate)
print(f"P(2+ HRs) = {prob_2plus:.4f}")

# Exercise 3: Binomial - season simulation
n_at_bats = 600
p_hr = 0.10
# 95% confidence interval
ci = stats.binom.interval(0.95, n_at_bats, p_hr)
print(f"95% CI for HR count: {ci}")
```

**Why it matters for EQ12:**
- HR probabilities are Poisson/Binomial
- Drift detection = comparing distributions
- Confidence intervals = model reliability

---

#### Day 3-5: StatsModels Deep Dive
**Goal:** Regression, time series, model diagnostics

**Topics:**
- OLS regression (linear modeling)
- Statsmodels output interpretation
- Model diagnostics (residuals, normality tests)
- Time series (ARIMA for forecasting)

**Code Exercises:**
```python
import statsmodels.api as sm
import pandas as pd

# Exercise 1: Linear regression - predict HR from barrel%
data = pd.read_csv("mlb_data.csv")
X = sm.add_constant(data['barrel_percent'])
y = data['home_runs']
model = sm.OLS(y, X).fit()
print(model.summary())
# Interpret: p-values, R-squared, coefficients

# Exercise 2: Time series - daily revenue trend
daily_revenue = pd.read_csv("daily_revenue.csv", parse_dates=['date'])
model = sm.tsa.ARIMA(daily_revenue['revenue'], order=(1,1,1)).fit()
forecast = model.get_forecast(steps=7)
print(forecast.summary_frame())

# Exercise 3: Model diagnostics
fig = model.plot_diagnostics()
# Check: residuals normal? homoscedastic? no autocorrelation?
```

**Why it matters for EQ12:**
- Drift detection = regression diagnostics
- Time series = forecasting next week's EV
- Model diagnostics = knowing when to retrain

---

### **WEEK 3: XGBOOST + LIGHTGBM FOR EV MODELING**

#### Day 1-2: XGBoost Expert Level
**Goal:** Build, tune, and explain your EV prediction model

**Topics:**
- Gradient boosting intuition
- Hyperparameter tuning (learning rate, tree depth, regularization)
- Feature importance
- Cross-validation strategy
- Custom loss functions (for EV optimization)

**Code Exercises:**
```python
import xgboost as xgb
from sklearn.model_selection import cross_val_score
import pandas as pd

# Exercise 1: Train HR probability model
data = pd.read_csv("mlb_training.csv")
X = data[['barrel_percent', 'exit_velocity', 'launch_angle', 'wind']]
y = data['home_run'].astype(int)

model = xgb.XGBClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
model.fit(X, y, eval_metric='logloss')

# Exercise 2: Evaluate with cross-validation
scores = cross_val_score(model, X, y, cv=5, scoring='roc_auc')
print(f"CV AUC: {scores.mean():.4f} ± {scores.std():.4f}")

# Exercise 3: Feature importance
import matplotlib.pyplot as plt
xgb.plot_importance(model)
plt.show()
# Which features matter most?
```

**Why it matters for EQ12:**
- HR/K/TB predictions = foundation of EV
- Tuning = squeeze 2-3% accuracy improvement
- Feature importance = understand model decisions

---

#### Day 3-5: LightGBM Comparison + Ensemble
**Goal:** Build faster models, compare with XGBoost, create ensemble

**Code Exercises:**
```python
import lightgbm as lgb

# Exercise 1: Train LightGBM (faster than XGBoost)
model_lgb = lgb.LGBMClassifier(
    n_estimators=100,
    learning_rate=0.1,
    num_leaves=31,
    max_depth=5
)
model_lgb.fit(X, y)

# Compare speed: LGBMs often 2-3x faster

# Exercise 2: Ensemble voting
from sklearn.ensemble import VotingClassifier
ensemble = VotingClassifier(
    estimators=[
        ('xgb', model),
        ('lgb', model_lgb)
    ],
    voting='soft'
)
ensemble.fit(X, y)

# Predict with ensemble
probs = ensemble.predict_proba(X_test)
# Often beats individual models
```

**Why it matters for EQ12:**
- LightGBM for fast daily retraining
- Ensemble = less overfitting
- Speed = scan 1000s of props every night

---

### **WEEK 4: ASYNCIO + FASTAPI + AIOHTTP**

#### Day 1-2: Asyncio Mastery
**Goal:** Write concurrent code for your URL scanner + EV scanner

**Topics:**
- async/await syntax
- Semaphores (rate limiting)
- Gathering tasks
- Exception handling in async

**Code Exercises:**
```python
import asyncio
import aiohttp

# Exercise 1: Fetch odds from 5 sportsbooks concurrently
async def fetch_odds(sportsbook_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(sportsbook_url) as resp:
            return await resp.json()

async def main():
    urls = [
        'https://api1.com/odds',
        'https://api2.com/odds',
        'https://api3.com/odds',
    ]
    results = await asyncio.gather(*[fetch_odds(url) for url in urls])
    return results

# Run it
odds = asyncio.run(main())

# Exercise 2: Rate limiting with semaphore
async def limited_scan(sem, url):
    async with sem:
        # Only N concurrent requests per host
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.read()

async def main_limited():
    sem = asyncio.Semaphore(5)  # Max 5 concurrent
    tasks = [limited_scan(sem, url) for url in urls]
    return await asyncio.gather(*tasks)
```

**Why it matters for EQ12:**
- URL scanner scans 50+ URLs concurrently
- Odds pulling from 10+ sportsbooks in parallel
- EV scanner evaluates 1000s of props per night

---

#### Day 3-4: FastAPI for Model Serving
**Goal:** Expose your ML models as a REST API

**Topics:**
- Route definition
- Request/response models
- Async endpoints
- Dependency injection
- OpenAPI docs auto-generation

**Code Exercises:**
```python
from fastapi import FastAPI
from pydantic import BaseModel
import xgboost as xgb

app = FastAPI()

class HRPredictionRequest(BaseModel):
    barrel_percent: float
    exit_velocity: float
    launch_angle: float
    wind_mph: float

class HRPredictionResponse(BaseModel):
    hr_probability: float
    expected_value: float

model = xgb.XGBClassifier()
model.load_model("hr_model.pkl")

@app.post("/predict/home-run")
async def predict_hr(request: HRPredictionRequest):
    prob = model.predict_proba([
        [request.barrel_percent, request.exit_velocity, request.launch_angle, request.wind_mph]
    ])[0][1]
    
    ev = prob * 2.0 - 1.0  # Payout = 2.0, cost = 1.0
    
    return HRPredictionResponse(
        hr_probability=prob,
        expected_value=ev
    )

# Run: uvicorn app:app --reload
```

**Why it matters for EQ12:**
- VB.NET calls Python models via FastAPI
- REST API = language agnostic
- Auto-docs = easy integration

---

#### Day 5: aiohttp + FastAPI Integration
**Challenge:** Build concurrent HTTP client that calls your FastAPI server

---

### **WEEK 5: OSMNX + GEOPY + FOLIUM FOR MAPS**

#### Day 1-2: OSMnx Deep Dive
**Goal:** Extract restaurant/location data from OpenStreetMap

**Code Exercises:**
```python
import osmnx as ox
import pandas as pd

# Exercise 1: Get restaurants in Buffalo
restaurants = ox.features_from_place(
    'Buffalo, New York',
    tags={'amenity': 'restaurant'}
)

# Convert to GeoDataFrame
restaurants_gdf = ox.features_from_point(
    (42.8864, -78.8784),  # Buffalo center
    {'amenity': 'restaurant'},
    dist=5000  # 5km radius
)

# Extract basic info
print(restaurants_gdf[['name', 'cuisine', 'opening_hours']])

# Exercise 2: Get streets and graph structure
G = ox.graph_from_place('Buffalo, New York', network_type='drive')
# Useful for routing, distances, connectivity analysis

# Exercise 3: Calculate distances between restaurants
from shapely.geometry import Point
restaurants_gdf['distance_to_center'] = restaurants_gdf.geometry.apply(
    lambda point: point.distance(Point(42.8864, -78.8784))
)
closest = restaurants_gdf.nsmallest(10, 'distance_to_center')
```

**Why it matters for EQ12:**
- "Where should I eat?" = OSM restaurant data
- Cannabis tourism = filter by nearby dispensaries
- Distance calculations = scoring function

---

#### Day 3-4: Geopy for Geocoding
**Goal:** Convert addresses ↔ coordinates

**Code Exercises:**
```python
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

geocoder = Nominatim(user_agent="eq12_app")

# Exercise 1: Address → coordinates
location = geocoder.geocode("123 Main St, Buffalo, NY")
print(f"Lat: {location.latitude}, Lon: {location.longitude}")

# Exercise 2: Coordinates → address
location = geocoder.reverse("42.8864, -78.8784")
print(f"Address: {location.address}")

# Exercise 3: Distance calculation
buffalo = (42.8864, -78.8784)
niagara = (43.0896, -79.0849)
distance_km = geodesic(buffalo, niagara).kilometers
print(f"Distance: {distance_km:.1f} km")
```

**Why it matters for EQ12:**
- Geopy bridge = user address → restaurant data
- Distance = core scoring factor
- Rate limited (1 req/sec) = respect API

---

#### Day 5: Folium Maps
**Goal:** Visualize food/travel recommendations

**Code Exercises:**
```python
import folium

# Exercise 1: Create base map
m = folium.Map(
    location=[42.8864, -78.8784],
    zoom_start=13
)

# Exercise 2: Add restaurant markers
for idx, row in restaurants_gdf.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=5,
        popup=row['name'],
        color='red' if row['rating'] > 4.0 else 'blue'
    ).add_to(m)

# Exercise 3: Add heatmap
from folium.plugins import HeatMap
heat_data = [[point.y, point.x] for point in restaurants_gdf.geometry]
HeatMap(heat_data).add_to(m)

m.save('restaurants_map.html')
```

**Why it matters for EQ12:**
- Visualization = operator dashboard
- Heatmaps = identify best restaurant clusters
- Interactive HTML = shareable reports

---

### **WEEKS 6-7: SQLITE3 + DOTENV + INTEGRATION**

#### Day 1-2: SQLite3 Expert Level
**Goal:** Master your database layer

**Code Exercises:**
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('eq12.db')

# Exercise 1: Complex queries with joins
query = """
SELECT 
    conv.conversion_date,
    funnel.name,
    COUNT(*) as conversions,
    SUM(conv.revenue) as total_revenue
FROM conversions_daily conv
JOIN funnels funnel ON conv.funnel_id = funnel.id
WHERE conv.conversion_date >= date('now', '-30 days')
GROUP BY conv.conversion_date, funnel.id
ORDER BY total_revenue DESC
"""
df = pd.read_sql(query, conn)

# Exercise 2: Transactions + error handling
try:
    cur = conn.cursor()
    cur.execute("BEGIN")
    cur.execute("INSERT INTO orchestration_logs ...")
    cur.execute("UPDATE model_registry ...")
    conn.commit()
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
```

**Why it matters for EQ12:**
- SQLite = your system of record
- Complex queries = BI-Core intelligence
- Transactions = data integrity

---

#### Day 3-5: Integration Challenge
**Build the complete pipeline:**

1. Load data from 10 URLs (URL scanner)
2. Process with pandas
3. Feature engineer with numpy/scipy
4. Predict with XGBoost
5. Store results in SQLite
6. Serve via FastAPI
7. Visualize with folium

**Should complete in < 200 lines of code**

---

## 📊 SUCCESS METRICS

After 7 weeks, you should be able to:

- ✅ Write async code that scans 50+ URLs in 30 seconds
- ✅ Build ML models with 3-5% accuracy improvement through tuning
- ✅ Query your databases in your sleep
- ✅ Create beautiful maps showing your food/travel intelligence
- ✅ Serve models via REST API
- ✅ Load/transform/aggregate gigabytes of data in seconds
- ✅ Understand probability distributions and statistical tests
- ✅ Explain every decision your models make

---

## 📚 RESOURCE LINKS

| Library | Official Docs | Cheat Sheet |
|---------|---------------|------------|
| NumPy | https://numpy.org/doc/ | [Array Cheat Sheet](https://github.com/rougier/numpy-cheatsheet) |
| Pandas | https://pandas.pydata.org/docs/ | [Pandas Cheat Sheet](https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf) |
| SciPy | https://docs.scipy.org/doc/ | |
| scikit-learn | https://scikit-learn.org/ | [ML Cheat Sheet](https://cheatsheets.readthedocs.io/en/latest/scikit-learn.html) |
| XGBoost | https://xgboost.readthedocs.io/ | |
| AsyncIO | https://docs.python.org/3/library/asyncio.html | |
| FastAPI | https://fastapi.tiangolo.com/ | |
| OSMnx | https://osmnx.readthedocs.io/ | |
| Folium | https://python-visualization.github.io/folium/ | |

---

**Your Path to Expert Status:** Commit 2 hours/day for 7 weeks = 98 hours of focused mastery.

This is the roadmap. Execute it.
