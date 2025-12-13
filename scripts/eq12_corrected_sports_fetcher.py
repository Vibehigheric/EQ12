#!/usr/bin/env python3
"""
 EQ12 CORRECTED Complete Sports Data Fetcher
Fixes all errors and captures ALL games for November 8, 2025
"""

import json
import logging
import os
import urllib.request
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
log_dir = "C:\\EQ12\\logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %        print(f"\n FULLY CORRECTED TOTAL GAMES TODAY: {total_games}")
        print(f" College Basketball: {all_sports_data['cbb']['count']} (CORRECTED)")
        print(f" College Football: {all_sports_data['cfb']['count']} (CORRECTED)")
        print(f" NBA: {all_sports_data['nba']['count']} (CORRECTED)")
        print(f" NHL: {all_sports_data['nhl']['count']} (CORRECTED)")  lname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, f'corrected_sports_fetcher_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EQ12CorrectedSportsDataFetcher:
    def __init__(self):
        """Initialize the Corrected Sports Data Fetcher"""
        self.date_target = "2025-11-08"
        
        # Manual game list from user's correction - College Basketball
        self.manual_cbb_games = [
            {"away": "Princeton", "home": "Akron", "time": "12:00 PM"},
            {"away": "Alcorn", "home": "Minnesota", "time": "12:00 PM"},
            {"away": "Penn State", "home": "New Haven", "time": "1:00 PM"},
            {"away": "Kennesaw State", "home": "Florida A&M", "time": "1:00 PM"},
            {"away": "Drexel", "home": "Saint Josephs", "time": "1:00 PM"},
            {"away": "FIU", "home": "Nebraska", "time": "1:00 PM"},
            {"away": "Western Carolina", "home": "Duke (#6)", "time": "1:30 PM"},
            {"away": "South Florida", "home": "George Washington", "time": "1:30 PM"},
            {"away": "Texas State", "home": "Tulane", "time": "2:00 PM"},
            {"away": "Milwaukee", "home": "Wofford", "time": "2:00 PM"},
            {"away": "Marshall", "home": "Toledo", "time": "2:00 PM"},
            {"away": "UMBC", "home": "Dayton", "time": "2:00 PM"},
            {"away": "Fairfield", "home": "NJIT", "time": "2:00 PM"},
            {"away": "Fairleigh Dickinson", "home": "Saint Peters", "time": "2:00 PM"},
            {"away": "Towson", "home": "Houston (#2)", "time": "3:00 PM"},
            {"away": "San Francisco", "home": "Memphis", "time": "3:00 PM"},
            {"away": "Northern Kentucky", "home": "Tennessee (#18)", "time": "3:00 PM"},
            {"away": "Lafayette", "home": "Texas", "time": "3:00 PM"},
            {"away": "UNC Asheville", "home": "Georgia Southern", "time": "3:00 PM"},
            {"away": "Monmouth", "home": "La Salle", "time": "3:30 PM"},
            {"away": "Utah Valley", "home": "Boise State", "time": "4:00 PM"},
            {"away": "Vanderbilt", "home": "UCF", "time": "4:00 PM"},
            {"away": "UT Arlington", "home": "New Mexico", "time": "4:00 PM"},
            {"away": "San Jose State", "home": "UC Santa Barbara", "time": "4:00 PM"},
            {"away": "Providence", "home": "Virginia Tech", "time": "4:00 PM"},
            {"away": "Montana", "home": "Stanford", "time": "4:00 PM"},
            {"away": "Eastern Washington", "home": "Colorado", "time": "4:00 PM"},
            {"away": "Cal State Fullerton", "home": "Wyoming", "time": "4:00 PM"},
            {"away": "Elon", "home": "UNC Greensboro", "time": "4:00 PM"},
            {"away": "William & Mary", "home": "Norfolk State", "time": "4:00 PM"},
            {"away": "Austin Peay", "home": "Air Force", "time": "4:00 PM"},
            {"away": "IU Indianapolis", "home": "Butler", "time": "5:00 PM"},
            {"away": "Long Beach State", "home": "Fresno State", "time": "5:00 PM"},
            {"away": "East Carolina", "home": "Richmond", "time": "6:00 PM"},
            {"away": "Charleston", "home": "Florida Atlantic", "time": "6:00 PM"},
            {"away": "ETSU", "home": "Presbyterian", "time": "6:00 PM"},
            {"away": "Arkansas (#14)", "home": "Michigan State (#22)", "time": "7:00 PM"},
            {"away": "Prairie View", "home": "Wichita State", "time": "7:00 PM"},
            {"away": "Weber State", "home": "Utah", "time": "7:00 PM"},
            {"away": "Queens NC", "home": "Villanova", "time": "7:00 PM"},
            {"away": "A&M-Corpus Christi", "home": "Tarleton State", "time": "7:00 PM"},
            {"away": "Bellarmine", "home": "Kansas State", "time": "8:00 PM"},
            {"away": "Central Michigan", "home": "Bradley", "time": "8:00 PM"},
            {"away": "Tennessee State", "home": "Belmont", "time": "8:00 PM"},
            {"away": "UT Rio Grande Valley", "home": "Southern Utah", "time": "8:30 PM"},
            {"away": "Chattanooga", "home": "UNLV", "time": "9:00 PM"},
            {"away": "Holy Cross", "home": "BYU (#8)", "time": "9:00 PM"},
            {"away": "Arkansas-Pine Bluff", "home": "Loyola Marymount", "time": "9:00 PM"},
            {"away": "Pacific", "home": "Nevada", "time": "10:00 PM"},
            {"away": "Cal Poly", "home": "Seattle", "time": "10:00 PM"},
            {"away": "Houston Christian", "home": "UC San Diego", "time": "10:00 PM"},
            {"away": "Oklahoma", "home": "Gonzaga (#21)", "time": "10:30 PM"}
        ]
        
        # Manual game list from user's correction - College Football
        self.manual_cfb_games = [
            {"away": "Indiana (#2)", "home": "Penn State", "time": "12:00 PM"},
            {"away": "BYU (#7)", "home": "Texas Tech (#8)", "time": "12:00 PM"},
            {"away": "Georgia (#5)", "home": "Mississippi State", "time": "12:00 PM"},
            {"away": "SMU", "home": "Boston College", "time": "12:00 PM"},
            {"away": "James Madison", "home": "Marshall", "time": "12:00 PM"},
            {"away": "Colorado", "home": "West Virginia", "time": "12:00 PM"},
            {"away": "Southern Miss", "home": "Arkansas State", "time": "12:00 PM"},
            {"away": "Ohio State (#1)", "home": "Purdue", "time": "1:00 PM"},
            {"away": "The Citadel", "home": "Ole Miss (#6)", "time": "1:00 PM"},
            {"away": "Missouri State", "home": "Liberty", "time": "1:00 PM"},
            {"away": "Bowling Green", "home": "Eastern Michigan", "time": "1:00 PM"},
            {"away": "UAB", "home": "Rice", "time": "2:00 PM"},
            {"away": "Maryland", "home": "Rutgers", "time": "2:30 PM"},
            {"away": "Charlotte", "home": "East Carolina", "time": "3:00 PM"},
            {"away": "Louisiana Tech", "home": "Delaware", "time": "3:00 PM"},
            {"away": "Tulsa", "home": "Florida Atlantic", "time": "3:00 PM"},
            {"away": "Jacksonville State", "home": "UTEP", "time": "3:00 PM"},
            {"away": "FIU", "home": "Middle Tennessee", "time": "3:00 PM"},
            {"away": "Texas A&M (#3)", "home": "Missouri (#22)", "time": "3:30 PM"},
            {"away": "Oregon (#9)", "home": "Iowa (#20)", "time": "3:30 PM"},
            {"away": "Duke", "home": "UConn", "time": "3:30 PM"},
            {"away": "Iowa State", "home": "TCU", "time": "3:30 PM"},
            {"away": "Kansas", "home": "Arizona", "time": "3:30 PM"},
            {"away": "Auburn", "home": "Vanderbilt (#16)", "time": "4:00 PM"},
            {"away": "Kennesaw State", "home": "New Mexico State", "time": "4:00 PM"},
            {"away": "Georgia State", "home": "Coastal Carolina", "time": "4:00 PM"},
            {"away": "Washington (#23)", "home": "Wisconsin", "time": "4:30 PM"},
            {"away": "Stanford", "home": "North Carolina", "time": "4:30 PM"},
            {"away": "Texas State", "home": "Louisiana", "time": "5:00 PM"},
            {"away": "Air Force", "home": "San Jose State", "time": "6:00 PM"},
            {"away": "Wake Forest", "home": "Virginia (#14)", "time": "7:00 PM"},
            {"away": "California", "home": "Louisville (#15)", "time": "7:00 PM"},
            {"away": "Florida State", "home": "Clemson", "time": "7:00 PM"},
            {"away": "LSU", "home": "Alabama (#4)", "time": "7:30 PM"},
            {"away": "Navy", "home": "Notre Dame (#10)", "time": "7:30 PM"},
            {"away": "Florida", "home": "Kentucky", "time": "7:30 PM"},
            {"away": "Nevada", "home": "Utah State", "time": "7:30 PM"},
            {"away": "Nebraska", "home": "UCLA", "time": "9:00 PM"},
            {"away": "UNLV", "home": "Colorado State", "time": "9:30 PM"},
            {"away": "Sam Houston", "home": "Oregon State", "time": "10:00 PM"},
            {"away": "San Diego State", "home": "Hawaii", "time": "11:00 PM"}
        ]
        
        # Manual game list from user's correction - NBA
        self.manual_nba_games = [
            {"away": "DAL Mavericks", "home": "WAS Wizards", "time": "7:00 PM"},
            {"away": "TOR Raptors", "home": "PHI 76ers", "time": "7:30 PM"},
            {"away": "NO Pelicans", "home": "SA Spurs", "time": "8:00 PM"},
            {"away": "LA Lakers", "home": "ATL Hawks", "time": "8:00 PM"},
            {"away": "CHI Bulls", "home": "CLE Cavaliers", "time": "8:00 PM"},
            {"away": "POR Trail Blazers", "home": "MIA Heat", "time": "8:00 PM"},
            {"away": "IND Pacers", "home": "DEN Nuggets", "time": "9:00 PM"},
            {"away": "PHO Suns", "home": "LA Clippers", "time": "10:30 PM"}
        ]
        
        # Manual game list from user's correction - NHL
        self.manual_nhl_games = [
            {"away": "PIT Penguins", "home": "NJ Devils", "time": "12:40 PM"},
            {"away": "OTT Senators", "home": "PHI Flyers", "time": "1:10 PM"},
            {"away": "DAL Stars", "home": "NSH Predators", "time": "3:40 PM"},
            {"away": "BUF Sabres", "home": "CAR Hurricanes", "time": "7:10 PM"},
            {"away": "WAS Capitals", "home": "TB Lightning", "time": "7:10 PM"},
            {"away": "BOS Bruins", "home": "TOR Maple Leafs", "time": "7:10 PM"},
            {"away": "NY Islanders", "home": "NY Rangers", "time": "7:10 PM"},
            {"away": "UTA Mammoth", "home": "MTL Canadiens", "time": "7:10 PM"},
            {"away": "SEA Kraken", "home": "STL Blues", "time": "7:10 PM"},
            {"away": "ANA Ducks", "home": "VGK Golden Knights", "time": "10:10 PM"},
            {"away": "FLA Panthers", "home": "SJ Sharks", "time": "10:10 PM"},
            {"away": "COL Avalanche", "home": "EDM Oilers", "time": "10:10 PM"},
            {"away": "CBJ Blue Jackets", "home": "VAN Canucks", "time": "10:10 PM"}
        ]
        
        # Enhanced API configuration
        self.sports_apis = {
            'nhl': {
                'name': 'NHL',
                'emoji': '',
                'endpoints': [
                    'http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard'
                ]
            },
            'nba': {
                'name': 'NBA', 
                'emoji': '',
                'endpoints': [
                    'http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard'
                ]
            },
            'cfb': {
                'name': 'College Football',
                'emoji': '',
                'endpoints': [
                    'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard'
                ]
            }
        }
        
        # Coral USB Accelerator
        self.coral_connected = True  # User confirmed
        
        logger.info(" EQ12 CORRECTED Sports Data Fetcher initialized")
        logger.info(f" Coral USB Accelerator: Connected ")

    def fetch_api_games(self, sport: str) -> List[Dict[str, Any]]:
        """Fetch games from API for NHL, NBA, CFB"""
        if sport not in self.sports_apis:
            return []
            
        sport_config = self.sports_apis[sport]
        all_games = []
        
        date_formatted = "20251108"  # ESPN format
        
        logger.info(f" Fetching {sport_config['name']} games...")
        
        for endpoint in sport_config['endpoints']:
            try:
                url = f"{endpoint}?dates={date_formatted}&limit=300"
                
                with urllib.request.urlopen(url, timeout=20) as response:
                    data = json.loads(response.read().decode())
                
                games = data.get('events', [])
                all_games.extend(games)
                
                logger.info(f" Found {len(games)} {sport_config['name']} games")
                
            except Exception as e:
                logger.warning(f" API fetch failed for {sport}: {e}")
                continue
        
        return all_games

    def format_manual_cfb_games(self) -> List[Dict[str, Any]]:
        """Format the manually corrected college football games"""
        formatted_games = []
        
        for i, game in enumerate(self.manual_cfb_games, 1):
            formatted_game = {
                'id': f'cfb_manual_{i}',
                'name': f"{game['away']} @ {game['home']}",
                'shortName': f"{game['away']} @ {game['home']}",
                'date': self.date_target,
                'time': game['time'],
                'status': {'type': {'description': 'Scheduled'}},
                'competitions': [{
                    'competitors': [
                        {
                            'team': {'displayName': game['away']},
                            'homeAway': 'away'
                        },
                        {
                            'team': {'displayName': game['home']},
                            'homeAway': 'home'
                        }
                    ],
                    'venue': {'fullName': 'Various Venues'}
                }]
            }
            formatted_games.append(formatted_game)
        
        return formatted_games

    def format_manual_nba_games(self) -> List[Dict[str, Any]]:
        """Format the manually corrected NBA games"""
        formatted_games = []
        
        for i, game in enumerate(self.manual_nba_games, 1):
            formatted_game = {
                'id': f'nba_manual_{i}',
                'name': f"{game['away']} @ {game['home']}",
                'shortName': f"{game['away']} @ {game['home']}",
                'date': self.date_target,
                'time': game['time'],
                'status': {'type': {'description': 'Scheduled'}},
                'competitions': [{
                    'competitors': [
                        {
                            'team': {'displayName': game['away']},
                            'homeAway': 'away'
                        },
                        {
                            'team': {'displayName': game['home']},
                            'homeAway': 'home'
                        }
                    ],
                    'venue': {'fullName': 'Various Venues'}
                }]
            }
            formatted_games.append(formatted_game)
        
        return formatted_games

    def format_manual_nhl_games(self) -> List[Dict[str, Any]]:
        """Format the manually corrected NHL games"""
        formatted_games = []
        
        for i, game in enumerate(self.manual_nhl_games, 1):
            formatted_game = {
                'id': f'nhl_manual_{i}',
                'name': f"{game['away']} @ {game['home']}",
                'shortName': f"{game['away']} @ {game['home']}",
                'date': self.date_target,
                'time': game['time'],
                'status': {'type': {'description': 'Scheduled'}},
                'competitions': [{
                    'competitors': [
                        {
                            'team': {'displayName': game['away']},
                            'homeAway': 'away'
                        },
                        {
                            'team': {'displayName': game['home']},
                            'homeAway': 'home'
                        }
                    ],
                    'venue': {'fullName': 'Various Venues'}
                }]
            }
            formatted_games.append(formatted_game)
        
        return formatted_games

    def format_manual_cbb_games(self) -> List[Dict[str, Any]]:
        """Format the manually corrected college basketball games"""
        formatted_games = []
        
        for i, game in enumerate(self.manual_cbb_games, 1):
            formatted_game = {
                'id': f'cbb_manual_{i}',
                'name': f"{game['away']} @ {game['home']}",
                'shortName': f"{game['away']} @ {game['home']}",
                'date': self.date_target,
                'time': game['time'],
                'status': {'type': {'description': 'Scheduled'}},
                'competitions': [{
                    'competitors': [
                        {
                            'team': {'displayName': game['away']},
                            'homeAway': 'away'
                        },
                        {
                            'team': {'displayName': game['home']},
                            'homeAway': 'home'
                        }
                    ],
                    'venue': {'fullName': 'Various Venues'}
                }]
            }
            formatted_games.append(formatted_game)
        
        return formatted_games

    def format_game_display(self, game: Dict[str, Any]) -> str:
        """Format game for display"""
        try:
            if 'competitions' in game:
                competitors = game['competitions'][0].get('competitors', [])
                if len(competitors) >= 2:
                    away = competitors[0] if competitors[0].get('homeAway') == 'away' else competitors[1]
                    home = competitors[1] if competitors[1].get('homeAway') == 'home' else competitors[0]
                    
                    away_name = away.get('team', {}).get('displayName', 'Unknown')
                    home_name = home.get('team', {}).get('displayName', 'Unknown')
                else:
                    away_name = "Unknown"
                    home_name = "Unknown"
            else:
                # Manual format
                away_name = game.get('name', '').split(' @ ')[0] if ' @ ' in game.get('name', '') else 'Unknown'
                home_name = game.get('name', '').split(' @ ')[1] if ' @ ' in game.get('name', '') else 'Unknown'
            
            time_info = game.get('time', game.get('status', {}).get('type', {}).get('description', 'TBD'))
            venue = game.get('competitions', [{}])[0].get('venue', {}).get('fullName', 'Various Venues')
            
            return f"""
 {away_name} @ {home_name}
 Time: {time_info}
  Venue: {venue}
"""
        except Exception as e:
            logger.debug(f"Error formatting game: {e}")
            return " Game formatting error"

    def run_corrected_fetch(self):
        """Run CORRECTED complete sports data fetch"""
        print(" EQ12 CORRECTED Complete Sports Data Fetcher")
        print(" FIXED COMPREHENSIVE SPORTS SCHEDULE - November 8, 2025")
        print("=" * 80)
        
        all_sports_data = {}
        total_games = 0
        
        # Get College Basketball (CORRECTED with manual list)
        cbb_games = self.format_manual_cbb_games()
        logger.info(f" Using CORRECTED College Basketball game list: {len(cbb_games)} games")
        
        all_sports_data['cbb'] = {
            'name': 'College Basketball',
            'emoji': '',
            'games': cbb_games,
            'count': len(cbb_games)
        }
        total_games += len(cbb_games)
        
        # Get College Football (CORRECTED with manual list)
        cfb_games = self.format_manual_cfb_games()
        logger.info(f" Using CORRECTED College Football game list: {len(cfb_games)} games")
        
        all_sports_data['cfb'] = {
            'name': 'College Football',
            'emoji': '',
            'games': cfb_games,
            'count': len(cfb_games)
        }
        total_games += len(cfb_games)
        
        # Get NBA (CORRECTED with manual list)
        nba_games = self.format_manual_nba_games()
        logger.info(f" Using CORRECTED NBA game list: {len(nba_games)} games")
        
        all_sports_data['nba'] = {
            'name': 'NBA',
            'emoji': '',
            'games': nba_games,
            'count': len(nba_games)
        }
        total_games += len(nba_games)
        
        # Get NHL (CORRECTED with manual list)
        nhl_games = self.format_manual_nhl_games()
        logger.info(f" Using CORRECTED NHL game list: {len(nhl_games)} games")
        
        all_sports_data['nhl'] = {
            'name': 'NHL',
            'emoji': '',
            'games': nhl_games,
            'count': len(nhl_games)
        }
        total_games += len(nhl_games)
        
        print(f"\n COLLEGE BASKETBALL (CORRECTED) - {len(cbb_games)} Games")
        print("-" * 60)
        for i, game in enumerate(cbb_games[:10], 1):  # Show first 10
            print(f"Game {i}:{self.format_game_display(game)}")
        
        if len(cbb_games) > 10:
            print(f"... and {len(cbb_games) - 10} more games")
        
        print(f"\n COLLEGE FOOTBALL (CORRECTED) - {len(cfb_games)} Games")
        print("-" * 60)
        for i, game in enumerate(cfb_games[:10], 1):  # Show first 10
            print(f"Game {i}:{self.format_game_display(game)}")
        
        if len(cfb_games) > 10:
            print(f"... and {len(cfb_games) - 10} more games")
        
        print(f"\n NBA (CORRECTED) - {len(nba_games)} Games")
        print("-" * 60)
        for i, game in enumerate(nba_games, 1):  # Show all NBA games
            print(f"Game {i}:{self.format_game_display(game)}")
        
        print(f"\n NHL (CORRECTED) - {len(nhl_games)} Games")
        print("-" * 60)
        for i, game in enumerate(nhl_games[:10], 1):  # Show first 10
            print(f"Game {i}:{self.format_game_display(game)}")
        
        if len(nhl_games) > 10:
            print(f"... and {len(nhl_games) - 10} more games")
        
        print(f"\n CORRECTED TOTAL GAMES TODAY: {total_games}")
        print(f" College Basketball: {all_sports_data['cbb']['count']} (CORRECTED)")
        print(f" College Football: {all_sports_data['cfb']['count']} (CORRECTED)")
        print(f" NHL: {all_sports_data['nhl']['count']}")
        print(f" NBA: {all_sports_data['nba']['count']}")  
        
        # Save corrected data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(log_dir, f"corrected_all_sports_complete_{timestamp}.json")
        
        with open(output_file, 'w') as f:
            json.dump(all_sports_data, f, indent=2, default=str)
        
        print(f"\n CORRECTED data saved to: {output_file}")
        logger.info(f"CORRECTED sports data fetch complete - {total_games} total games")
        
        # Key games highlight
        print("\n KEY COLLEGE BASKETBALL GAMES TODAY:")
        key_cbb_games = [
            "Arkansas (#14) @ Michigan State (#22) - 7:00 PM",
            "Western Carolina @ Duke (#6) - 1:30 PM", 
            "Towson @ Houston (#2) - 3:00 PM",
            "Northern Kentucky @ Tennessee (#18) - 3:00 PM",
            "Holy Cross @ BYU (#8) - 9:00 PM",
            "Oklahoma @ Gonzaga (#21) - 10:30 PM"
        ]
        for game in key_cbb_games:
            print(f" {game}")
        
        print("\n KEY COLLEGE FOOTBALL GAMES TODAY:")
        key_cfb_games = [
            "Ohio State (#1) @ Purdue - 1:00 PM",
            "Indiana (#2) @ Penn State - 12:00 PM",
            "Texas A&M (#3) @ Missouri (#22) - 3:30 PM",
            "LSU @ Alabama (#4) - 7:30 PM",
            "Georgia (#5) @ Mississippi State - 12:00 PM",
            "BYU (#7) @ Texas Tech (#8) - 12:00 PM",
            "Oregon (#9) @ Iowa (#20) - 3:30 PM",
            "Navy @ Notre Dame (#10) - 7:30 PM"
        ]
        for game in key_cfb_games:
            print(f" {game}")

if __name__ == "__main__":
    fetcher = EQ12CorrectedSportsDataFetcher()
    fetcher.run_corrected_fetch()