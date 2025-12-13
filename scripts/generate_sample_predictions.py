#!/usr/bin/env python3
"""
Generate Sample Coral AI Predictions for Demo
"""

import json
import random
from datetime import datetime
from pathlib import Path

def generate_sample_predictions():
    """Generate sample predictions from odds data for demonstration"""
    
    # Load the odds data
    try:
        with open('C:/EQ12/coral_betting_ai/feeds/live_odds_latest.json') as f:
            odds_data = json.load(f)
    except Exception as e:
        print(f"Error loading odds data: {e}")
        return
    
    # Extract games from the dictionary structure
    games = odds_data.get('api_odds', [])
    
    print(f"Found {len(games)} games to process")
    
    # Create sample predictions
    predictions = {
        'timestamp': datetime.now().isoformat(),
        'total_games_analyzed': len(games),
        'bets': []
    }
    
    # Generate synthetic predictions for demonstration
    random.seed(42)  # For reproducible results
    
    for i, game in enumerate(games[:10]):  # Limit to 10 for demo
        if game.get('bookmakers'):
            bookmaker = game['bookmakers'][0]  # Use first bookmaker
            if bookmaker.get('markets'):
                # Process h2h (head-to-head) market
                h2h_market = bookmaker['markets'].get('h2h', [])
                for j, outcome in enumerate(h2h_market[:2]):
                    bet = {
                        'game_id': game.get('game_id', f'game_{i}'),
                        'sport': game.get('sport', 'americanfootball_nfl'),
                        'description': f"{outcome.get('name', 'Team')} ML",
                        'team': outcome.get('name', f'Team {j+1}'),
                        'market': 'h2h',
                        'odds': outcome.get('price', 2.0),
                        'coral_ev_score': round(random.uniform(0.05, 0.25), 3),
                        'coral_confidence': round(random.uniform(0.6, 0.9), 3),
                        'predicted_probability': round(random.uniform(0.4, 0.6), 3),
                        'bookmaker_probability': round(1 / outcome.get('price', 2.0), 3),
                        'commence_time': game.get('commence_time', ''),
                        'home_team': game.get('home_team', ''),
                        'away_team': game.get('away_team', '')
                    }
                    predictions['bets'].append(bet)
                
                # Process spreads market
                spreads_market = bookmaker['markets'].get('spreads', [])
                for j, outcome in enumerate(spreads_market[:2]):
                    bet = {
                        'game_id': game.get('game_id', f'game_{i}'),
                        'sport': game.get('sport', 'americanfootball_nfl'),
                        'description': f"{outcome.get('name', 'Team')} {outcome.get('point', 0):+.1f}",
                        'team': outcome.get('name', f'Team {j+1}'),
                        'market': 'spreads',
                        'odds': outcome.get('price', 2.0),
                        'point': outcome.get('point', 0),
                        'coral_ev_score': round(random.uniform(0.05, 0.20), 3),
                        'coral_confidence': round(random.uniform(0.65, 0.85), 3),
                        'predicted_probability': round(random.uniform(0.45, 0.55), 3),
                        'bookmaker_probability': round(1 / outcome.get('price', 2.0), 3),
                        'commence_time': game.get('commence_time', ''),
                        'home_team': game.get('home_team', ''),
                        'away_team': game.get('away_team', '')
                    }
                    predictions['bets'].append(bet)
    
    # Save predictions
    reports_path = Path('C:/EQ12/coral_betting_ai/reports')
    reports_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    predictions_file = reports_path / f'coral_results_{timestamp}.json'
    
    with open(predictions_file, 'w') as f:
        json.dump(predictions, f, indent=2)
    
    print(f'Generated {len(predictions["bets"])} sample predictions')
    print(f'Saved to: {predictions_file}')
    return str(predictions_file)

if __name__ == "__main__":
    generate_sample_predictions()