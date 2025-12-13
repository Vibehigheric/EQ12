import json
import requests
import argparse
import re
import os
from datetime import datetime

API_KEY = "c32c9644050b2240081428b43e7016ce"
MEMORY_FILE = "c:\\EQ12_BROKEN_20251122_210342\\config\\learning_memory.md"

class PostMortem:
    def __init__(self):
        self.scores_cache = None

    def fetch_scores(self):
        """Fetches recent scores from Odds API."""
        if self.scores_cache:
            return self.scores_cache
            
        url = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/scores/?daysFrom=3&apiKey={API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            self.scores_cache = response.json()
            return self.scores_cache
        except Exception as e:
            print(f"Error fetching scores: {e}")
            return []

    def find_game_result(self, home_team, away_team):
        """Finds the score for a specific matchup."""
        scores = self.fetch_scores()
        for game in scores:
            # Normalize names (simple check)
            if (home_team in game['home_team'] or game['home_team'] in home_team) and \
               (away_team in game['away_team'] or game['away_team'] in away_team):
                if game['completed']:
                    # Extract scores
                    home_score = 0
                    away_score = 0
                    if game['scores']:
                        for s in game['scores']:
                            if s['name'] == game['home_team']:
                                home_score = int(s['score'])
                            elif s['name'] == game['away_team']:
                                away_score = int(s['score'])
                    return {
                        "home_team": game['home_team'],
                        "away_team": game['away_team'],
                        "home_score": home_score,
                        "away_score": away_score
                    }
        return None

    def evaluate_pick(self, pick_text, result):
        """
        Evaluates a single pick string against the result.
        Returns: 'WIN', 'LOSS', 'PUSH', or 'UNKNOWN'
        """
        home_score = result['home_score']
        away_score = result['away_score']
        home_team = result['home_team']
        away_team = result['away_team']

        # 1. Spread Logic (e.g., "Detroit Lions -4.5")
        spread_match = re.search(r"(.+?)\s*([+-]?\d+\.?\d*)", pick_text)
        if spread_match:
            team_name = spread_match.group(1).strip()
            spread = float(spread_match.group(2))
            
            # Identify which team was picked
            picked_score = 0
            opponent_score = 0
            
            if team_name in home_team:
                picked_score = home_score
                opponent_score = away_score
            elif team_name in away_team:
                picked_score = away_score
                opponent_score = home_score
            else:
                return "UNKNOWN_TEAM"

            # Calculate cover
            if picked_score + spread > opponent_score:
                return "WIN"
            elif picked_score + spread < opponent_score:
                return "LOSS"
            else:
                return "PUSH"

        # 2. Moneyline Logic (e.g., "Dallas Cowboys Moneyline")
        if "Moneyline" in pick_text:
            if home_team in pick_text:
                return "WIN" if home_score > away_score else "LOSS"
            elif away_team in pick_text:
                return "WIN" if away_score > home_score else "LOSS"

        return "UNKNOWN_TYPE"

    def analyze_file(self, filepath):
        print(f"Analyzing {filepath}...")
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Extract teams from game_data
        home_team = data['game_data']['home_team']
        away_team = data['game_data']['away_team']
        
        print(f"Matchup: {away_team} @ {home_team}")
        
        result = self.find_game_result(home_team, away_team)
        if not result:
            print("Game result not found in recent history.")
            return

        print(f"Final Score: {result['away_team']} {result['away_score']} - {result['home_team']} {result['home_score']}")

        # Parse Report for Picks
        report = data.get('report', '')
        picks = []
        
        # Regex to find lines starting with bullet point
        for line in report.split('\n'):
            if "\u2022" in line: # Bullet point
                pick_text = line.split("\u2022")[1].split("-")[0].strip()
                picks.append(pick_text)

        lessons = []
        
        print("\n--- Evaluation ---")
        for pick in picks:
            outcome = self.evaluate_pick(pick, result)
            print(f"Pick: {pick} -> {outcome}")
            
            if outcome == "LOSS":
                lessons.append(f"Failed Pick: {pick}. Result: {result['away_team']} {result['away_score']} - {result['home_team']} {result['home_score']}")

        if lessons:
            self.update_memory(lessons, home_team, away_team)

    def update_memory(self, lessons, home_team, away_team):
        """Updates the persistent memory with lessons learned."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_entry = f"\n## Post-Mortem: {away_team} @ {home_team} ({timestamp})\n"
        for lesson in lessons:
            new_entry += f"- ❌ {lesson}\n"
            
        # Generate a strategic correction
        new_entry += f"- **Strategic Correction**: The model overestimated {away_team}. Adjust prompt to weight recent defensive performance higher.\n"

        # Ensure directory exists
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        
        with open(MEMORY_FILE, 'a') as f:
            f.write(new_entry)
        
        print(f"\n[SELF-LEARNING] Updated {MEMORY_FILE} with {len(lessons)} new lessons.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Path to the prediction JSON file")
    args = parser.parse_args()

    pm = PostMortem()
    pm.analyze_file(args.file)
