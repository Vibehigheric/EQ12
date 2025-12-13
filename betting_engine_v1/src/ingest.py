import os
import json
import pandas as pd
from sportsbet.datasets import SoccerDataLoader
from sportsbet.evaluation import ClassifierBettor
from sklearn.dummy import DummyClassifier
import requests
from datetime import datetime

# Configuration
DATA_DIR = "data"
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
ODDS_BASE_URL = "https://api.the-odds-api.com/v4/sports"

def ingest_historical_data():
    """
    Ingest historical data using sports-betting library.
    For V1, we focus on a single league to prove the pipeline.
    """
    print(f"[{datetime.now()}] Ingesting historical data (Italy 2020)...")
    try:
        dataloader = SoccerDataLoader(param_grid={'league': ['Italy'], 'year': [2020]})
        X_train, Y_train, O_train = dataloader.extract_train_data(odds_type='market_maximum')
        
        # Save to disk
        os.makedirs(DATA_DIR, exist_ok=True)
        X_train.to_csv(os.path.join(DATA_DIR, "X_train_italy_2020.csv"), index=False)
        Y_train.to_csv(os.path.join(DATA_DIR, "Y_train_italy_2020.csv"), index=False)
        O_train.to_csv(os.path.join(DATA_DIR, "O_train_italy_2020.csv"), index=False)
        
        print(f"[{datetime.now()}] Historical data saved to {DATA_DIR}")
        return X_train, Y_train, O_train
    except Exception as e:
        print(f"Error ingesting historical data: {e}")
        return None, None, None

def ingest_live_odds(sport_key="soccer_italy_serie_a"):
    """
    Ingest live odds from The Odds API.
    """
    print(f"[{datetime.now()}] Fetching live odds for {sport_key}...")
    if not ODDS_API_KEY:
        print("Error: ODDS_API_KEY not found.")
        return None

    url = f"{ODDS_BASE_URL}/{sport_key}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h"
    try:
        response = requests.get(url)
        response.raise_for_status()
        odds_data = response.json()
        
        # Save raw JSON
        filename = f"odds_{sport_key}_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "w") as f:
            json.dump(odds_data, f, indent=2)
            
        print(f"[{datetime.now()}] Live odds saved to {filepath}")
        return odds_data
    except Exception as e:
        print(f"Error fetching live odds: {e}")
        return None

if __name__ == "__main__":
    # Test run
    ingest_historical_data()
    # ingest_live_odds() # Uncomment to test API usage
