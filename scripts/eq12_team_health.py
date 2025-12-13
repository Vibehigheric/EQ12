import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EQ12_TeamHealth")

class TeamHealthEngine:
    """
    EQ12 Team Health Engine.
    Calculates a 0-100 Health Score for each team based on injuries, fatigue, and rotation stress.
    Acts as the AUTHORITATIVE SOURCE for player availability.
    """

    def __init__(self):
        # MOCK DATABASE OF INJURIES (In prod, this comes from the PDF/API scraper)
        self.injury_report = {
            "ATL": ["Trae Young", "Clint Capela"],
            "WAS": ["Kyle Kuzma", "Corey Kispert", "Bilal Coulibaly", "Alex Sarr"], # Hospital Ward
            "IND": ["Myles Turner"],
            "PHI": [], # Healthy
            "CLE": [], # Healthy
            "DET": [], # Healthy
            "DAL": [], # Healthy
            "LAL": [], # Healthy (Luka's New Team)
            "BKN": ["Ben Simmons"] # Always
        }
        
        # MOCK SCHEDULE CONTEXT (Back-to-backs, travel)
        self.schedule_context = {
            "ATL": {"b2b": False, "travel_miles": 500},
            "WAS": {"b2b": True, "travel_miles": 800}, # Tired + Injured
            "IND": {"b2b": False, "travel_miles": 200},
            "PHI": {"b2b": False, "travel_miles": 0},
            "CLE": {"b2b": False, "travel_miles": 300},
            "DET": {"b2b": False, "travel_miles": 0},
            "DAL": {"b2b": False, "travel_miles": 0},
            "LAL": {"b2b": False, "travel_miles": 0},
            "BKN": {"b2b": True, "travel_miles": 1200}
        }

    def get_player_availability(self, player_name, team_slug):
        """
        Returns 'ACTIVE' or 'OUT' based on the injury report.
        """
        if player_name in self.injury_report.get(team_slug, []):
            return "OUT"
        return "ACTIVE"

    def calculate_health_score(self, team_slug):
        """
        Calculates the Team Health Score (0-100).
        Formula: 100 - (StarOut*15) - (RoleOut*8) - (B2B*7) - (Travel/300)
        """
        score = 100
        injuries = self.injury_report.get(team_slug, [])
        context = self.schedule_context.get(team_slug, {})
        
        # 1. Injury Penalties
        for player in injuries:
            # Simple heuristic for "Star" vs "Role"
            if player in ["Trae Young", "Kyle Kuzma", "Myles Turner", "Luka Doncic", "Donovan Mitchell"]:
                score -= 15 # Star Penalty
            else:
                score -= 8  # Role Player Penalty
                
        # 2. Fatigue Penalties
        if context.get("b2b"):
            score -= 7
            
        travel = context.get("travel_miles", 0)
        score -= (travel / 300)
        
        return max(0, round(score, 1))

    def get_betting_advice(self, team_slug):
        """
        Returns strategic advice based on Health Score.
        """
        score = self.calculate_health_score(team_slug)
        
        if score >= 80:
            return "GREEN: Full Props Allowed"
        elif score >= 60:
            return "YELLOW: Caution. Target Opponent Overs."
        else:
            return "RED: FADE TEAM. Only Unders or Opponent Overs."

if __name__ == "__main__":
    engine = TeamHealthEngine()
    teams = ["ATL", "WAS", "IND", "PHI", "CLE"]
    
    print("=== EQ12 TEAM HEALTH REPORT ===")
    for team in teams:
        score = engine.calculate_health_score(team)
        advice = engine.get_betting_advice(team)
        print(f"[{team}] Score: {score} | {advice}")
