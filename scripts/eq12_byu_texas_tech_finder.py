#!/usr/bin/env python3
"""
EQ12 BYU vs Texas Tech Game Finder
Find and analyze the BYU vs Texas Tech game for today
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BYUTexasTechFinder:
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        
    def find_game(self) -> Optional[Dict]:
        """Find BYU vs Texas Tech game in latest data"""
        
        # Check both data files
        data_files = [
            "real_games_data_20251108_155841.json",
            "real_games_data_20251108_120857.json"
        ]
        
        for data_file in data_files:
            file_path = self.workspace_path / "logs" / data_file
            if file_path.exists():
                logger.info(f" Searching {data_file}...")
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Search for BYU vs Texas Tech
                    for game in data.get('games', []):
                        home_team = game.get('home_team', '').lower()
                        away_team = game.get('away_team', '').lower()
                        
                        # Check for various team name formats
                        byu_names = ['byu', 'brigham young', 'cougars']
                        tech_names = ['texas tech', 'red raiders', 'tech']
                        
                        is_byu_home = any(name in home_team for name in byu_names)
                        is_byu_away = any(name in away_team for name in byu_names)
                        is_tech_home = any(name in home_team for name in tech_names)
                        is_tech_away = any(name in away_team for name in tech_names)
                        
                        if (is_byu_home and is_tech_away) or (is_byu_away and is_tech_home):
                            logger.info(f" Found BYU vs Texas Tech game!")
                            return game
                    
                    logger.info(f" BYU vs Texas Tech not found in {data_file}")
                    
                except Exception as e:
                    logger.error(f"Error reading {data_file}: {e}")
        
        return None
    
    def list_all_ncaaf_games(self) -> List[Dict]:
        """List all NCAAF games available today"""
        
        data_file = self.workspace_path / "logs" / "real_games_data_20251108_155841.json"
        
        if not data_file.exists():
            logger.error("No recent data file found")
            return []
        
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
            
            ncaaf_games = []
            for game in data.get('games', []):
                if game.get('sport') == 'americanfootball_ncaaf' or game.get('league') == 'NCAAF':
                    ncaaf_games.append(game)
            
            logger.info(f" Found {len(ncaaf_games)} NCAAF games today:")
            for i, game in enumerate(ncaaf_games, 1):
                home = game.get('home_team', 'Unknown')
                away = game.get('away_team', 'Unknown')
                start_time = game.get('start_time', 'Unknown')
                logger.info(f"  {i}. {away} @ {home} ({start_time})")
            
            return ncaaf_games
            
        except Exception as e:
            logger.error(f"Error reading data: {e}")
            return []
    
    def analyze_game_odds(self, game: Dict) -> Dict:
        """Analyze betting odds for the game"""
        try:
            analysis = {
                'game_info': {
                    'home_team': game.get('home_team', ''),
                    'away_team': game.get('away_team', ''),
                    'start_time': game.get('start_time', ''),
                    'sport': game.get('sport', ''),
                    'league': game.get('league', '')
                },
                'betting_markets': {}
            }
            
            # Parse markets
            for market in game.get('markets', []):
                market_key = market.get('key')
                
                if market_key == 'h2h':  # Moneyline
                    analysis['betting_markets']['moneyline'] = {}
                    for outcome in market.get('outcomes', []):
                        team = outcome.get('name', '')
                        odds = outcome.get('price', 0)
                        analysis['betting_markets']['moneyline'][team] = odds
                
                elif market_key == 'spreads':  # Point spreads
                    analysis['betting_markets']['spreads'] = {}
                    for outcome in market.get('outcomes', []):
                        team = outcome.get('name', '')
                        odds = outcome.get('price', 0)
                        point = outcome.get('point', 0)
                        analysis['betting_markets']['spreads'][team] = {
                            'odds': odds,
                            'spread': point
                        }
                
                elif market_key == 'totals':  # Over/Under
                    analysis['betting_markets']['totals'] = {}
                    for outcome in market.get('outcomes', []):
                        bet_type = outcome.get('name', '')
                        odds = outcome.get('price', 0)
                        point = outcome.get('point', 0)
                        analysis['betting_markets']['totals'][bet_type] = {
                            'odds': odds,
                            'total': point
                        }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing game odds: {e}")
            return {}

def main():
    """Main execution function"""
    logger.info(" Searching for BYU vs Texas Tech game...")
    
    finder = BYUTexasTechFinder()
    
    # First, try to find the specific game
    game = finder.find_game()
    
    if game:
        logger.info(" BYU vs Texas Tech game found! Analyzing odds...")
        analysis = finder.analyze_game_odds(game)
        
        print("\n" + "="*60)
        print(" BYU vs TEXAS TECH GAME ANALYSIS")
        print("="*60)
        
        game_info = analysis.get('game_info', {})
        print(f" Game: {game_info.get('away_team')} @ {game_info.get('home_team')}")
        print(f" Start Time: {game_info.get('start_time')}")
        print(f" League: {game_info.get('league')}")
        
        markets = analysis.get('betting_markets', {})
        
        if 'moneyline' in markets:
            print(f"\n MONEYLINE:")
            for team, odds in markets['moneyline'].items():
                print(f"  {team}: {odds:+d}")
        
        if 'spreads' in markets:
            print(f"\n POINT SPREADS:")
            for team, data in markets['spreads'].items():
                print(f"  {team} {data['spread']:+.1f}: {data['odds']:+d}")
        
        if 'totals' in markets:
            print(f"\n TOTALS:")
            for bet_type, data in markets['totals'].items():
                print(f"  {bet_type} {data['total']}: {data['odds']:+d}")
        
        print("="*60)
        
        # Save analysis
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = finder.workspace_path / "logs" / f"byu_texas_tech_analysis_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        logger.info(f" Analysis saved to: {output_file}")
        
    else:
        logger.warning(" BYU vs Texas Tech game not found in today's data")
        logger.info(" Let me show you what NCAAF games are available today:")
        
        ncaaf_games = finder.list_all_ncaaf_games()
        
        if ncaaf_games:
            print("\n" + "="*60)
            print(" AVAILABLE NCAAF GAMES TODAY")
            print("="*60)
            
            for i, game in enumerate(ncaaf_games, 1):
                home = game.get('home_team', 'Unknown')
                away = game.get('away_team', 'Unknown')
                start_time = game.get('start_time', 'Unknown')
                print(f"{i:2d}. {away} @ {home}")
                print(f"    Start: {start_time}")
                print()
            
            print("="*60)
        else:
            print(" No NCAAF games found in today's data")

if __name__ == "__main__":
    main()