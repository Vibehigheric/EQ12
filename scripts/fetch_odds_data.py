import os
import requests
import json
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("ODDS_API_KEY")
BASE_URL = "https://api.the-odds-api.com/v4/sports"

def fetch_sports():
    """Fetch available sports."""
    if not API_KEY:
        print("Error: ODDS_API_KEY not found in environment variables.")
        return

    url = f"{BASE_URL}/?apiKey={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        sports = response.json()
        print(f"Successfully fetched {len(sports)} sports.")
        
        # Save to a log file for inspection
        output_path = os.path.join("logs", "odds_api_sports.json")
        os.makedirs("logs", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(sports, f, indent=2)
        print(f"Sports list saved to {output_path}")
        
        # Print first 5 sports
        for sport in sports[:5]:
            print(f"- {sport['key']}: {sport['title']}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sports: {e}")

def fetch_odds(sport_key="upcoming", regions="us", markets="h2h"):
    """Fetch odds for a specific sport."""
    if not API_KEY:
        print("Error: ODDS_API_KEY not found.")
        return

    url = f"{BASE_URL}/{sport_key}/odds/?apiKey={API_KEY}&regions={regions}&markets={markets}"
    print(f"Fetching odds for {sport_key}...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        odds = response.json()
        print(f"Successfully fetched {len(odds)} events with odds.")
        
        output_path = os.path.join("logs", f"odds_{sport_key}.json")
        os.makedirs("logs", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(odds, f, indent=2)
        print(f"Odds saved to {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching odds: {e}")

def main():
    parser = argparse.ArgumentParser(description="Fetch data from The Odds API")
    parser.add_argument("--action", choices=["sports", "odds"], default="sports", help="Action to perform")
    parser.add_argument("--sport", default="upcoming", help="Sport key for odds (default: upcoming)")
    args = parser.parse_args()

    if args.action == "sports":
        fetch_sports()
    elif args.action == "odds":
        fetch_odds(sport_key=args.sport)

if __name__ == "__main__":
    main()
