#!/usr/bin/env python3
"""
EQ12 Current College Football Games Finder
Find NCAAF games happening now/tonight with live betting opportunities
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CurrentNCAAFGamesFinder:
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.current_time = datetime.now(timezone.utc)
        
    def load_latest_games_data(self) -> Dict:
        """Load the most recent games data"""
        data_files = [
            "real_games_data_20251108_155841.json",
            "real_games_data_20251108_120857.json"
        ]
        
        for data_file in data_files:
            file_path = self.workspace_path / "logs" / data_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    logger.info(f" Loaded {len(data.get('games', []))} games from {data_file}")
                    return data
                except Exception as e:
                    logger.error(f"Error loading {data_file}: {e}")
        
        return {}
    
    def get_game_status(self, start_time_str: str) -> tuple[str, int]:
        """Determine game status and minutes since start"""
        try:
            game_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            time_diff_minutes = (self.current_time - game_time).total_seconds() / 60
            
            if time_diff_minutes < -60:
                return "UPCOMING", int(abs(time_diff_minutes))
            elif time_diff_minutes < -15:
                return "STARTING_SOON", int(abs(time_diff_minutes))
            elif time_diff_minutes < 0:
                return "PREGAME", int(abs(time_diff_minutes))
            elif time_diff_minutes < 210:  # 3.5 hours (typical game length)
                return "LIVE", int(time_diff_minutes)
            else:
                return "COMPLETED", int(time_diff_minutes)
        except:
            return "UNKNOWN", 0
    
    def find_current_ncaaf_games(self) -> List[Dict]:
        """Find NCAAF games that are live or starting soon"""
        data = self.load_latest_games_data()
        current_games = []
        
        for game in data.get('games', []):
            # Check if it's NCAAF
            if game.get('sport') == 'americanfootball_ncaaf' or game.get('league') == 'NCAAF':
                start_time = game.get('start_time', '')
                status, time_info = self.get_game_status(start_time)
                
                # Include live, starting soon, or upcoming games
                if status in ['LIVE', 'STARTING_SOON', 'UPCOMING']:
                    game_analysis = {
                        'home_team': game.get('home_team', ''),
                        'away_team': game.get('away_team', ''),
                        'start_time': start_time,
                        'status': status,
                        'time_info': time_info,
                        'markets': self.extract_betting_markets(game),
                        'raw_game_data': game
                    }
                    current_games.append(game_analysis)
        
        # Sort by game status priority (LIVE first, then STARTING_SOON, then UPCOMING)
        status_priority = {'LIVE': 1, 'STARTING_SOON': 2, 'UPCOMING': 3}
        current_games.sort(key=lambda x: (status_priority.get(x['status'], 999), x['time_info']))
        
        return current_games
    
    def extract_betting_markets(self, game: Dict) -> Dict:
        """Extract betting markets from game data"""
        markets = {
            'moneyline': {},
            'spreads': {},
            'totals': {}
        }
        
        for market in game.get('markets', []):
            market_key = market.get('key')
            
            if market_key == 'h2h':  # Moneyline
                for outcome in market.get('outcomes', []):
                    team = outcome.get('name', '')
                    odds = outcome.get('price', 0)
                    markets['moneyline'][team] = odds
            
            elif market_key == 'spreads':  # Point spreads
                for outcome in market.get('outcomes', []):
                    team = outcome.get('name', '')
                    odds = outcome.get('price', 0)
                    point = outcome.get('point', 0)
                    markets['spreads'][team] = {
                        'odds': odds,
                        'spread': point
                    }
            
            elif market_key == 'totals':  # Over/Under
                for outcome in market.get('outcomes', []):
                    bet_type = outcome.get('name', '')
                    odds = outcome.get('price', 0)
                    point = outcome.get('point', 0)
                    markets['totals'][bet_type] = {
                        'odds': odds,
                        'total': point
                    }
        
        return markets
    
    def analyze_betting_value(self, game: Dict) -> List[Dict]:
        """Analyze betting value for a game"""
        value_bets = []
        markets = game['markets']
        
        # Analyze spreads
        for team, data in markets['spreads'].items():
            odds = data['odds']
            spread = data['spread']
            
            # Simple value analysis
            implied_prob = self.calculate_implied_probability(odds)
            
            # Adjust fair probability based on spread and game status
            if game['status'] == 'LIVE':
                # Live games - more conservative
                fair_prob = 0.48
            else:
                # Pregame spreads tend to be efficient
                fair_prob = 0.50
            
            edge = fair_prob - implied_prob
            
            if edge > 0.01:  # 1% edge minimum
                value_bets.append({
                    'bet_type': 'spread',
                    'team': team,
                    'bet': f"{team} {spread:+.1f}",
                    'odds': odds,
                    'edge': edge,
                    'status_note': f"Game {game['status']}"
                })
        
        # Analyze totals
        for bet_type, data in markets['totals'].items():
            odds = data['odds']
            total = data['total']
            
            implied_prob = self.calculate_implied_probability(odds)
            
            # Totals analysis
            if game['status'] == 'LIVE':
                # Live totals can be more volatile
                fair_prob = 0.51 if bet_type == 'Under' else 0.49
            else:
                fair_prob = 0.50
            
            edge = fair_prob - implied_prob
            
            if edge > 0.005:  # 0.5% edge for totals
                value_bets.append({
                    'bet_type': 'total',
                    'team': bet_type,
                    'bet': f"{bet_type} {total}",
                    'odds': odds,
                    'edge': edge,
                    'status_note': f"Game {game['status']}"
                })
        
        return value_bets
    
    def calculate_implied_probability(self, odds: int) -> float:
        """Convert American odds to implied probability"""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)

def format_ncaaf_report(current_games: List[Dict]) -> str:
    """Format comprehensive NCAAF games report"""
    
    if not current_games:
        return """
 CURRENT NCAAF GAMES ANALYSIS 
{'='*60}

 No college football games currently live or starting soon.

 Check back later for evening games or weekend action!
{'='*60}
"""
    
    report = f"""
 CURRENT NCAAF GAMES ANALYSIS 
{'='*60}

 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}
 Found {len(current_games)} active/upcoming NCAAF games

"""
    
    live_games = [g for g in current_games if g['status'] == 'LIVE']
    starting_soon = [g for g in current_games if g['status'] == 'STARTING_SOON']
    upcoming = [g for g in current_games if g['status'] == 'UPCOMING']
    
    if live_games:
        report += f"""
 LIVE GAMES ({len(live_games)}):
{'='*60}
"""
        for i, game in enumerate(live_games, 1):
            report += format_game_details(game, i)
    
    if starting_soon:
        report += f"""
 STARTING SOON ({len(starting_soon)}):
{'='*60}
"""
        for i, game in enumerate(starting_soon, 1):
            report += format_game_details(game, i)
    
    if upcoming:
        report += f"""
 UPCOMING TONIGHT ({len(upcoming)}):
{'='*60}
"""
        for i, game in enumerate(upcoming, 1):
            report += format_game_details(game, i)
    
    report += """
 BETTING STRATEGY NOTES:
{'='*60}
 LIVE games: Look for momentum-based value
 STARTING SOON: Last chance for pregame lines
 UPCOMING: Monitor line movement before kickoff
 Consider same-game parlays for better odds

{'='*60}
"""
    
    return report

def format_game_details(game: Dict, index: int) -> str:
    """Format individual game details"""
    status_icons = {
        'LIVE': '',
        'STARTING_SOON': '', 
        'UPCOMING': ''
    }
    
    icon = status_icons.get(game['status'], '')
    
    details = f"""
{icon} #{index} {game['away_team']} @ {game['home_team']}
{''*50}
"""
    
    if game['status'] == 'LIVE':
        details += f"  LIVE - {game['time_info']} minutes elapsed\n"
    elif game['status'] == 'STARTING_SOON':
        details += f" Starting in {game['time_info']} minutes\n"
    else:
        details += f" Starts in {game['time_info']} minutes\n"
    
    markets = game['markets']
    
    # Moneyline
    if markets['moneyline']:
        details += " MONEYLINE:\n"
        for team, odds in markets['moneyline'].items():
            details += f"   {team}: {odds:+d}\n"
    
    # Spreads
    if markets['spreads']:
        details += " SPREADS:\n"
        for team, data in markets['spreads'].items():
            details += f"   {team} {data['spread']:+.1f}: {data['odds']:+d}\n"
    
    # Totals
    if markets['totals']:
        details += " TOTALS:\n"
        for bet_type, data in markets['totals'].items():
            details += f"   {bet_type} {data['total']}: {data['odds']:+d}\n"
    
    details += "\n"
    return details

def main():
    """Main execution function"""
    logger.info(" Searching for current NCAAF games...")
    
    finder = CurrentNCAAFGamesFinder()
    current_games = finder.find_current_ncaaf_games()
    
    logger.info(f" Found {len(current_games)} current/upcoming NCAAF games")
    
    # Analyze value bets for each game
    all_value_bets = []
    for game in current_games:
        value_bets = finder.analyze_betting_value(game)
        all_value_bets.extend(value_bets)
    
    logger.info(f" Identified {len(all_value_bets)} potential value bets")
    
    # Generate report
    report = format_ncaaf_report(current_games)
    print(report)
    
    if all_value_bets:
        print("\n TOP VALUE BETTING OPPORTUNITIES:")
        print("="*60)
        for i, bet in enumerate(all_value_bets[:5], 1):
            edge_pct = bet['edge'] * 100
            print(f"{i}. {bet['bet']} ({bet['odds']:+d}) - {edge_pct:+.1f}% edge - {bet['status_note']}")
        print("="*60)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results = {
        'timestamp': timestamp,
        'current_games': current_games,
        'value_bets': all_value_bets
    }
    
    results_file = finder.workspace_path / "logs" / f"current_ncaaf_games_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f" Results saved to: {results_file}")

if __name__ == "__main__":
    main()