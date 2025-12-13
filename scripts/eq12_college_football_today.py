#!/usr/bin/env python3
"""
EQ12 College Football Games Fetcher - November 8, 2025
Fetch today's college football games from ESPN API (free, no key required)
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def fetch_college_football_games(date_str: str = "2025-11-08") -> List[Dict[str, Any]]:
    """
    Fetch college football games for the specified date using ESPN API
    
    Args:
        date_str: Date in YYYY-MM-DD format
    
    Returns:
        List of game dictionaries
    """
    try:
        # Try to import requests, if not available, use urllib
        try:
            import requests
            
            # ESPN College Football API endpoint
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            date_formatted = date_obj.strftime("%Y%m%d")
            
            # ESPN API endpoint for college football
            url = f"http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard"
            params = {
                'dates': date_formatted,
                'limit': 100
            }
            
            logger.info(f"Fetching college football games for {date_str} from ESPN API...")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
        except ImportError:
            # Fallback to urllib if requests not available
            import urllib.request
            import urllib.parse
            
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            date_formatted = date_obj.strftime("%Y%m%d")
            
            params = urllib.parse.urlencode({
                'dates': date_formatted,
                'limit': 100
            })
            
            url = f"http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?{params}"
            
            logger.info(f"Fetching college football games for {date_str} from ESPN API (urllib)...")
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
        
        # Parse and format the games
        games = []
        
        if 'events' in data:
            for event in data['events']:
                try:
                    # Extract game information
                    game_info = {
                        'game_id': event.get('id'),
                        'date': event.get('date'),
                        'status': event.get('status', {}).get('type', {}).get('description', 'Unknown'),
                        'venue': event.get('competitions', [{}])[0].get('venue', {}).get('fullName', 'TBD'),
                        'teams': [],
                        'score': {},
                        'odds': {},
                        'broadcast': []
                    }
                    
                    # Extract teams and scores
                    competition = event.get('competitions', [{}])[0]
                    competitors = competition.get('competitors', [])
                    
                    for competitor in competitors:
                        team = competitor.get('team', {})
                        team_info = {
                            'name': team.get('displayName'),
                            'abbreviation': team.get('abbreviation'),
                            'logo': team.get('logo'),
                            'color': team.get('color'),
                            'is_home': competitor.get('homeAway') == 'home',
                            'rank': competitor.get('curatedRank', {}).get('current')
                        }
                        
                        # Add score if available
                        score = competitor.get('score')
                        if score:
                            team_info['score'] = int(score)
                        
                        game_info['teams'].append(team_info)
                    
                    # Extract broadcast information
                    broadcasts = competition.get('broadcasts', [])
                    for broadcast in broadcasts:
                        for media in broadcast.get('media', []):
                            if media.get('shortName'):
                                game_info['broadcast'].append(media.get('shortName'))
                    
                    # Extract odds if available
                    odds = competition.get('odds', [])
                    if odds:
                        for odd in odds:
                            provider = odd.get('provider', {}).get('name')
                            if provider:
                                game_info['odds'][provider] = {
                                    'spread': odd.get('details'),
                                    'over_under': odd.get('overUnder')
                                }
                    
                    # Format display time
                    if game_info['date']:
                        try:
                            game_time = datetime.fromisoformat(game_info['date'].replace('Z', '+00:00'))
                            game_info['display_time'] = game_time.strftime("%I:%M %p ET")
                        except:
                            game_info['display_time'] = "TBD"
                    
                    games.append(game_info)
                    
                except Exception as e:
                    logger.warning(f"Error parsing game data: {e}")
                    continue
        
        logger.info(f"Found {len(games)} college football games for {date_str}")
        return games
        
    except Exception as e:
        logger.error(f"Error fetching college football games: {e}")
        return []

def display_games(games: List[Dict[str, Any]]) -> None:
    """Display games in a formatted output"""
    
    if not games:
        print(" No college football games found for today (November 8, 2025)")
        print("\nNote: College football typically plays on Saturdays.")
        print("Most games would be on November 9, 2025 (Saturday).")
        return
    
    print(f"\n COLLEGE FOOTBALL GAMES - {datetime.now().strftime('%B %d, %Y')}")
    print("=" * 80)
    
    for i, game in enumerate(games, 1):
        print(f"\n GAME {i}")
        print("-" * 40)
        
        # Team information
        if len(game['teams']) >= 2:
            away_team = game['teams'][0] if not game['teams'][0]['is_home'] else game['teams'][1]
            home_team = game['teams'][1] if game['teams'][1]['is_home'] else game['teams'][0]
            
            # Display rankings if available
            away_rank = f"#{away_team['rank']} " if away_team.get('rank') else ""
            home_rank = f"#{home_team['rank']} " if home_team.get('rank') else ""
            
            print(f" Away: {away_rank}{away_team['name']} ({away_team['abbreviation']})")
            print(f" Home: {home_rank}{home_team['name']} ({home_team['abbreviation']})")
            
            # Show scores if game has started
            if away_team.get('score') is not None and home_team.get('score') is not None:
                print(f" Score: {away_team['name']} {away_team['score']} - {home_team['score']} {home_team['name']}")
        
        # Game details
        print(f" Time: {game.get('display_time', 'TBD')}")
        print(f"  Venue: {game.get('venue', 'TBD')}")
        print(f" Status: {game.get('status', 'Unknown')}")
        
        # Broadcast information
        if game.get('broadcast'):
            print(f" TV: {', '.join(game['broadcast'])}")
        
        # Odds information
        if game.get('odds'):
            print(" Odds:")
            for provider, odds_info in game['odds'].items():
                if odds_info.get('spread'):
                    print(f"   {provider}: {odds_info['spread']}")
                if odds_info.get('over_under'):
                    print(f"   O/U: {odds_info['over_under']}")

def save_games_to_file(games: List[Dict[str, Any]], date_str: str) -> str:
    """Save games data to JSON file"""
    
    logs_dir = "C:\\EQ12\\logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cfb_games_{date_str.replace('-', '')}_{timestamp}.json"
    filepath = os.path.join(logs_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            'date': date_str,
            'fetch_time': datetime.now().isoformat(),
            'games_count': len(games),
            'games': games
        }, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Games data saved to: {filepath}")
    return filepath

def main():
    """Main execution function"""
    
    # Target date - November 8, 2025
    target_date = "2025-11-08"
    
    print(" EQ12 College Football Games Fetcher")
    print(f"Fetching games for: {target_date}")
    print("=" * 50)
    
    # Fetch games
    games = fetch_college_football_games(target_date)
    
    # Display results
    display_games(games)
    
    # Save to file
    if games:
        filepath = save_games_to_file(games, target_date)
        print(f"\n Games data saved to: {filepath}")
    
    # Also check Saturday (typical college football day)
    saturday_date = "2025-11-09"
    print(f"\n\n BONUS: Checking Saturday ({saturday_date}) for college football games...")
    print("=" * 60)
    
    saturday_games = fetch_college_football_games(saturday_date)
    display_games(saturday_games)
    
    if saturday_games:
        sat_filepath = save_games_to_file(saturday_games, saturday_date)
        print(f"\n Saturday games saved to: {sat_filepath}")
    
    print(f"\n College football data fetch complete!")
    print(f" Friday games: {len(games)}")
    print(f" Saturday games: {len(saturday_games)}")

if __name__ == "__main__":
    main()