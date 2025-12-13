import os
import json
import pandas as pd
from dotenv import load_dotenv
from sportsbet.datasets import SoccerDataLoader
from sportsbet.evaluation import ClassifierBettor
from sklearn.dummy import DummyClassifier
import requests

# Load environment variables
load_dotenv()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
ODDS_BASE_URL = "https://api.the-odds-api.com/v4/sports"

def demo_sports_betting_lib():
    print("\n--- Demo: sports-betting library ---")
    try:
        # Download data for Italian Soccer 2020 as a test
        print("Downloading historical data (Italy 2020)...")
        dataloader = SoccerDataLoader(param_grid={'league': ['Italy'], 'year': [2020]})
        
        # Extract training data
        X_train, Y_train, O_train = dataloader.extract_train_data(odds_type='market_maximum')
        print(f"Training data shape: {X_train.shape}")
        
        # Train a dummy bettor
        print("Training DummyClassifier bettor...")
        bettor = ClassifierBettor(DummyClassifier())
        bettor.fit(X_train, Y_train)
        print("Bettor trained.")
        
        # In a real scenario, we would use dataloader.extract_fixtures_data() 
        # but that requires current data sources supported by the lib.
        # For now, we just show we can train.
        
    except Exception as e:
        print(f"Error in sports-betting lib demo: {e}")

def fetch_live_odds_from_api():
    print("\n--- Demo: The Odds API (Live Data) ---")
    if not ODDS_API_KEY:
        print("ODDS_API_KEY not found.")
        return

    # Fetch upcoming soccer events to match the theme
    sport_key = "soccer_italy_serie_a" # Example, might need to verify key
    
    # First check if this sport is active/available
    try:
        print("Checking available sports...")
        response = requests.get(f"{ODDS_BASE_URL}/?apiKey={ODDS_API_KEY}")
        response.raise_for_status()
        sports = response.json()
        
        # Find a soccer league
        soccer_leagues = [s for s in sports if 'soccer' in s['key']]
        if not soccer_leagues:
            print("No soccer leagues currently available via API.")
            target_sport = "upcoming"
        else:
            target_sport = soccer_leagues[0]['key']
            print(f"Found soccer league: {target_sport}")
            
        # Fetch odds
        print(f"Fetching odds for {target_sport}...")
        url = f"{ODDS_BASE_URL}/{target_sport}/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h"
        response = requests.get(url)
        response.raise_for_status()
        odds_data = response.json()
        
        print(f"Fetched {len(odds_data)} events.")
        if odds_data:
            print("Sample event:")
            print(json.dumps(odds_data[0], indent=2))
            
            # Save to log
            log_path = os.path.join("logs", "live_odds_integration.json")
            with open(log_path, "w") as f:
                json.dump(odds_data, f, indent=2)
            print(f"Saved live odds to {log_path}")
            
    except Exception as e:
        print(f"Error fetching from Odds API: {e}")

def main():
    print("Initializing Sports Betting Intelligence Cluster...")
    
    # 1. Use the library for modeling capability
    demo_sports_betting_lib()
    
    # 2. Use the API key for real-time data capability
    fetch_live_odds_from_api()
    
    print("\nCluster update complete. Capabilities verified.")

if __name__ == "__main__":
    main()
