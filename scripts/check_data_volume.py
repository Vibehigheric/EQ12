from sportsbet.datasets import SoccerDataLoader
import pandas as pd

# Initialize to check available parameters
dataloader = SoccerDataLoader()
params = dataloader.get_all_params()

# params is a list of dicts, let's inspect the first one or iterate
print("Structure of params:", type(params))
if isinstance(params, list) and len(params) > 0:
    print("First item keys:", params[0].keys())
    
    # Assuming it returns a list of all available combinations or similar
    # Let's try to extract unique leagues and years from the list of dicts
    leagues = set()
    years = set()
    for p in params:
        if 'league' in p: leagues.add(p['league'])
        if 'year' in p: years.add(p['year'])
        
    print(f"Available Leagues: {len(leagues)}")
    print(f"Available Years: {len(years)}")
    print(f"Sample Leagues: {list(leagues)[:10]}")
    print(f"Years range: {min(years)} to {max(years)}")

    # Estimate total matches
    total_matches_est = len(leagues) * len(years) * 300
    print(f"Estimated Total Historical Matches available: {total_matches_est:,}")
