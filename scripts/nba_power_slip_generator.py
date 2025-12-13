import json
import os
import sys
import pandas as pd

# Add current directory to path to find eq12_availability
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from eq12_player_eligibility_gate import PlayerEligibilityGate
from eq12_team_health import TeamHealthEngine

# Load Real Data Cache
# CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "nba_player_status.json")

def load_player_status(player_name):
    # ... existing code ...
    pass # We will use the Health Engine for status now

# --- HYBRID DATA FEED (Mock Props + Real Status Check) ---
candidates = [
    # ATL vs DET
    {"player": "Dyson Daniels", "team": "ATL", "prop": "Assists", "pick": "OVER", "minutes": 34, "confirmed": True, "reason": "Trae OUT -> Primary Ball Handler"},
    {"player": "Jalen Johnson", "team": "ATL", "prop": "Rebounds", "pick": "OVER", "minutes": 38, "confirmed": True, "reason": "Capela OUT -> Board Usage"},
    
    # IND vs PHI
    {"player": "Joel Embiid", "team": "PHI", "prop": "Points", "pick": "OVER", "minutes": 34, "confirmed": True, "reason": "No Turner -> Paint Feast"},
    {"player": "Pascal Siakam", "team": "IND", "prop": "Rebounds", "pick": "OVER", "minutes": 37, "confirmed": True, "reason": "No Turner -> Must Rebound"},
    
    # CLE vs WAS (Hospital Ward Check)
    # WAS has Kispert (OUT), Coulibaly (OUT), Sarr (OUT), Kuzma (GTD).
    # STRATEGY: If >2 Key Players OUT -> ABANDON GAME. PIVOT TO BACKUP.
    
    # PIVOT GAME: LAL @ DAL (Luka vs Kyrie)
    {"player": "Luka Doncic", "team": "LAL", "prop": "Points", "pick": "OVER", "minutes": 38, "confirmed": True, "reason": "Pivot from WAS. Heliocentric Usage (Lakers)."},
    {"player": "Kyrie Irving", "team": "DAL", "prop": "Assists", "pick": "OVER", "minutes": 36, "confirmed": True, "reason": "Pivot from WAS. Secondary Playmaking."},
    
    # Original WAS legs for audit (will be rejected by logic or manual exclusion)
    {"player": "Alex Sarr", "team": "WAS", "prop": "Rebounds", "pick": "OVER", "minutes": 34, "confirmed": True, "reason": "Rookie Usage"}, 
]

def generate_slip():
    # Initialize the new Gatekeeper
    gate = PlayerEligibilityGate()
    
    print("=== EQ12 POWER SLIP GENERATOR v5 (PLAYER ELIGIBILITY GATE) ===")
    
    # 1. CALCULATE TEAM HEALTH SCORES (Optional display, Gate handles logic)
    print("\n🏥 TEAM HEALTH REPORT (Managed by Gate):")
    # We can just let the gate handle it per candidate, or print a summary if the gate exposes it.
    # For now, we'll skip the explicit pre-calculation print to simplify, 
    # or we can instantiate the engine just for printing if we really want to.
    
    # 2. ENRICH & FILTER CANDIDATES
    print("\nℹ️  Applying Player Eligibility Gate Rules...")
    
    valid_legs = []
    for leg in candidates:
        player = leg['player']
        team = leg['team']
        
        # The Gate handles Availability, Health Score, and Conflicts
        result = gate.evaluate_candidate(leg)
        
        if not result['eligible']:
            print(f"⛔ REJECTED: {player} ({team}) -> {result['reason']}")
            continue
            
        # If eligible, we can add the enriched data
        leg['status'] = "ACTIVE" # Gate confirmed it
        valid_legs.append(leg)

    print(f"\n📉 FILTER REPORT: {len(candidates)} Candidates -> {len(valid_legs)} Approved.")
    
    # 3. FINAL SLIP
    df = pd.DataFrame(valid_legs)
    print("\n=== 🎫 FINAL APPROVED TICKET (GATE-VERIFIED) ===")
    if not df.empty:
        print(df[['player', 'team', 'prop', 'pick', 'status', 'reason']].to_string(index=False))
    else:
        print("No legs survived the Health Gate.")
    
    # Structure Check
    unique_games = set([x['team'] for x in valid_legs])
    print(f"\n✅ STRUCTURE CHECK: {len(unique_games)} Unique Teams")

if __name__ == "__main__":
    generate_slip()
