# EQ12 Live Buffalo Bills Game Search
# Real-time NFL schedule and odds lookup

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class EQ12BillsGameSearch:
    def __init__(self):
        self.odds_api_key = os.getenv('ODDS_API_KEY', 'ODDS_API_KEY_PLACEHOLDER')
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'EQ12-Bills-Search/1.0'})

    def search_bills_games_today(self) -> Dict:
        """
        Search for Buffalo Bills games on current date using live NFL API
        """
        print("[INFO] Searching NFL API for Buffalo Bills games...")

        # The-Odds-API endpoint for NFL games
        url = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
        params = {
            'apiKey': self.odds_api_key,
            'regions': 'us',
            'markets': 'h2h,spreads,totals',
            'oddsFormat': 'american',
            'dateFormat': 'iso'
        }

        try:
            print("[API] Calling The-Odds-API for live NFL data...")
            response = self.session.get(url, params=params, timeout=15)

            if response.status_code == 401:
                print("[ERROR] API Key unauthorized - checking quota")
                return self._search_alternative_sources()
            elif response.status_code == 429:
                print("[ERROR] API rate limit exceeded")
                return self._search_alternative_sources()

            response.raise_for_status()
            games = response.json()

            # Filter for Buffalo Bills games
            bills_games = []
            today = datetime.now().strftime('%Y-%m-%d')

            for game in games:
                home_team = game.get('home_team', '')
                away_team = game.get('away_team', '')
                game_date = game.get('commence_time', '')

                if game_date:
                    game_day = datetime.fromisoformat(game_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')

                    if ('Buffalo Bills' in home_team or 'Buffalo Bills' in away_team or
                        'Bills' in home_team or 'Bills' in away_team):

                        if game_day == today:
                            bills_games.append({
                                'game': game,
                                'is_today': True,
                                'game_time': game_date,
                                'matchup': f"{away_team} @ {home_team}"
                            })
                        elif abs((datetime.fromisoformat(game_date.replace('Z', '+00:00')) - datetime.now()).days) <= 3:
                            bills_games.append({
                                'game': game,
                                'is_today': False,
                                'game_time': game_date,
                                'matchup': f"{away_team} @ {home_team}",
                                'days_away': (datetime.fromisoformat(game_date.replace('Z', '+00:00')) - datetime.now()).days
                            })

            if bills_games:
                print(f"[SUCCESS] Found {len(bills_games)} Buffalo Bills games")
                return {
                    'status': 'success',
                    'games_found': len(bills_games),
                    'bills_games': bills_games,
                    'search_date': today
                }
            else:
                print("[INFO] No Buffalo Bills games found for today")
                return self._check_weekly_schedule()

        except Exception as e:
            print(f"[ERROR] API Error: {e}")
            return self._search_alternative_sources()

    def _search_alternative_sources(self) -> Dict:
        """
        Search alternative sources when primary API is unavailable
        """
        print("[INFO] Searching alternative NFL schedule sources...")

        # ESPN API alternative (free tier)
        try:
            espn_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            response = self.session.get(espn_url, timeout=10)
            response.raise_for_status()

            data = response.json()
            events = data.get('events', [])

            bills_games = []
            today = datetime.now().strftime('%Y-%m-%d')

            for event in events:
                competitions = event.get('competitions', [])
                for comp in competitions:
                    competitors = comp.get('competitors', [])
                    game_date = comp.get('date', '')

                    home_team = ''
                    away_team = ''

                    for team in competitors:
                        if team.get('homeAway') == 'home':
                            home_team = team.get('team', {}).get('displayName', '')
                        else:
                            away_team = team.get('team', {}).get('displayName', '')

                    if game_date:
                        game_day = datetime.fromisoformat(game_date.replace('Z', '+00:00')).strftime('%Y-%m-%d')

                        if ('Buffalo Bills' in home_team or 'Buffalo Bills' in away_team):
                            bills_games.append({
                                'source': 'ESPN',
                                'matchup': f"{away_team} @ {home_team}",
                                'game_time': game_date,
                                'game_day': game_day,
                                'is_today': game_day == today,
                                'status': comp.get('status', {}).get('type', {}).get('description', 'Scheduled')
                            })

            if bills_games:
                return {
                    'status': 'success_alternative',
                    'source': 'ESPN API',
                    'games_found': len(bills_games),
                    'bills_games': bills_games
                }
            else:
                return self._no_games_found()

        except Exception as e:
            print(f"[ERROR] ESPN API Error: {e}")
            return self._no_games_found()

    def _check_weekly_schedule(self) -> Dict:
        """
        Check Bills weekly schedule when no games today
        """
        return {
            'status': 'no_games_today',
            'message': 'No Buffalo Bills games found for today',
            'recommendation': 'Check upcoming week schedule',
            'next_steps': [
                'Search for Bills games this week',
                'Check Monday Night Football',
                'Look for upcoming Sunday games'
            ]
        }

    def _no_games_found(self) -> Dict:
        """
        Handle case when no Bills games are found
        """
        return {
            'status': 'not_found',
            'message': 'No Buffalo Bills games found in available data sources',
            'possible_reasons': [
                'Bills may not be playing today',
                'Game may be on different date',
                'API data may be limited',
                'Season may be over'
            ],
            'recommendations': [
                'Check NFL official schedule',
                'Search for specific game date',
                'Verify current NFL season status'
            ]
        }

    def format_game_results(self, results: Dict) -> str:
        """
        Format search results for display
        """
        if results['status'] == 'success':
            output = "=== BUFFALO BILLS GAME SEARCH RESULTS ===\n\n"

            for game_info in results['bills_games']:
                if game_info['is_today']:
                    output += f"🏈 TODAY'S GAME:\n"
                    output += f"   Matchup: {game_info['matchup']}\n"
                    output += f"   Time: {game_info['game_time']}\n"

                    # Add betting lines if available
                    game = game_info.get('game', {})
                    bookmakers = game.get('bookmakers', [])
                    if bookmakers:
                        output += f"   Lines available: Yes ({len(bookmakers)} sportsbooks)\n"
                    output += "\n"
                else:
                    output += f"📅 UPCOMING GAME:\n"
                    output += f"   Matchup: {game_info['matchup']}\n"
                    output += f"   Time: {game_info['game_time']}\n"
                    output += f"   Days away: {game_info.get('days_away', 'TBD')}\n\n"

        elif results['status'] == 'success_alternative':
            output = f"=== BILLS GAMES (Source: {results['source']}) ===\n\n"

            for game_info in results['bills_games']:
                status = "🏈 TODAY" if game_info['is_today'] else "📅 UPCOMING"
                output += f"{status}: {game_info['matchup']}\n"
                output += f"   Time: {game_info['game_time']}\n"
                output += f"   Status: {game_info['status']}\n\n"

        elif results['status'] == 'no_games_today':
            output = "=== NO BILLS GAMES TODAY ===\n\n"
            output += f"{results['message']}\n\n"
            output += "Next steps:\n"
            for step in results['next_steps']:
                output += f"• {step}\n"

        else:
            output = "=== SEARCH UNSUCCESSFUL ===\n\n"
            output += f"{results['message']}\n\n"
            output += "Possible reasons:\n"
            for reason in results.get('possible_reasons', []):
                output += f"• {reason}\n"

        return output

def main():
    print("=== EQ12 BUFFALO BILLS GAME SEARCH ===")
    print("Searching for real-time game data...")

    searcher = EQ12BillsGameSearch()

    # Search for Bills games
    results = searcher.search_bills_games_today()

    # Format and display results
    formatted_results = searcher.format_game_results(results)
    print("\n" + formatted_results)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"C:/EQ12/logs/bills_game_search_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {filename}")

    return results

if __name__ == "__main__":
    main()
