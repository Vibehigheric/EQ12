import logging
import time
import requests
import json
from datetime import datetime
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EQ12_Live_Score_Daemon")

class EQ12LiveScoreDaemon:
    """
    Continuously polls ESPN API for live game states.
    Acts as the 'Heartbeat' of the system.
    """
    
    ESPN_NBA_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    
    def __init__(self, interval_seconds=60):
        self.interval = interval_seconds
        self.running = False
        self.game_states = {} # Cache game states
        logger.info(f"📡 Live Score Daemon Initialized (Interval: {self.interval}s)")

    def fetch_live_scores(self):
        """Fetch current scoreboard from ESPN."""
        try:
            response = requests.get(self.ESPN_NBA_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_espn_data(data)
            else:
                logger.error(f"Failed to fetch scores: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Exception fetching scores: {e}")
            return []

    def _parse_espn_data(self, data):
        """Parse raw ESPN JSON into structured game objects."""
        games = []
        events = data.get('events', [])
        
        for event in events:
            competition = event['competitions'][0]
            status = event['status']['type']['name'] # STATUS_SCHEDULED, STATUS_IN_PROGRESS, STATUS_FINAL
            clock = event['status'].get('displayClock', '0:00')
            period = event['status'].get('period', 0)
            
            home_team = competition['competitors'][0]['team']['abbreviation']
            away_team = competition['competitors'][1]['team']['abbreviation']
            
            home_score = competition['competitors'][0].get('score', '0')
            away_score = competition['competitors'][1].get('score', '0')
            
            game_info = {
                'id': event['id'],
                'matchup': f"{away_team} @ {home_team}",
                'status': status,
                'clock': clock,
                'period': period,
                'score': f"{away_team} {away_score} - {home_team} {home_score}",
                'start_time': event['date']
            }
            games.append(game_info)
            
        return games

    def run_once(self):
        """Run a single poll cycle."""
        logger.info("🔄 Polling Live Scores...")
        games = self.fetch_live_scores()
        
        active_games = [g for g in games if g['status'] == 'STATUS_IN_PROGRESS']
        scheduled_games = [g for g in games if g['status'] == 'STATUS_SCHEDULED']
        final_games = [g for g in games if g['status'] == 'STATUS_FINAL']
        
        logger.info(f"📊 Status: {len(active_games)} Live | {len(scheduled_games)} Scheduled | {len(final_games)} Final")
        
        for game in active_games:
            logger.info(f"🏀 LIVE: {game['matchup']} | {game['score']} | Q{game['period']} {game['clock']}")
            
        return games

    def start(self):
        """Start the daemon loop."""
        self.running = True
        logger.info("🚀 Daemon Started")
        try:
            while self.running:
                self.run_once()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            logger.info("🛑 Daemon Stopped by User")

if __name__ == "__main__":
    daemon = EQ12LiveScoreDaemon(interval_seconds=10) # Fast poll for demo
    daemon.run_once()
