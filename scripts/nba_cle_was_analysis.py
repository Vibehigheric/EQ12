import pandas as pd
import sys

# --- MOCK DATA FOR 12/12/2025 (CLE vs WAS) ---
# Scenario: CLE is a massive favorite (-13.5). Blowout expected.
# Strategy: Fade CLE Starters (Unders), Target WAS Bench (Overs).

def analyze_cle_was():
    print("\n=== EQ12 Strategy Engine: CLE vs WAS (12/12/2025) ===")
    
    # 1. Game Context
    spread = -13.5
    total = 238.5
    print(f"ℹ️  Spread: CLE {spread} | Total: {total}")
    
    if spread <= -10:
        print("🚨 BLOWOUT ALERT ACTIVE: CLE favored by double digits.")
        print("   -> Strategy: FADE CLE Starters (Minutes Risk).")
        print("   -> Strategy: TARGET WAS Bench (Garbage Time Usage).")
    
    # 2. Roster & Role Data
    cle_starters = [
        {"name": "Donovan Mitchell", "avg_min": 35.5, "avg_pts": 27.5, "role": "Star"},
        {"name": "Darius Garland", "avg_min": 34.0, "avg_pts": 20.1, "role": "Star"},
        {"name": "Evan Mobley", "avg_min": 33.5, "avg_reb": 10.2, "role": "Star"},
    ]
    
    was_bench = [
        {"name": "Corey Kispert", "role": "Bench Scorer", "trend": "High Usage in 4Q"},
        {"name": "Bilal Coulibaly", "role": "Young Core", "trend": "Development Minutes"},
        {"name": "Jordan Poole", "role": "Chaos Engine", "trend": "Green Light in Blowouts"}, # Sometimes starts, sometimes bench
    ]

    legs = []

    # 3. Logic Engine
    
    # Logic A: CLE Starters Unders
    for player in cle_starters:
        proj_min = player['avg_min'] * 0.85 # Reduce minutes by 15% due to blowout
        legs.append({
            "player": player['name'],
            "team": "CLE",
            "prop": "Points",
            "prediction": "UNDER",
            "reason": f"Blowout Risk. Proj Mins: {proj_min:.1f} (vs Avg {player['avg_min']})",
            "confidence": "High"
        })

    # Logic B: WAS Garbage Time Heroes
    legs.append({
        "player": "Corey Kispert",
        "team": "WAS",
        "prop": "Points",
        "prediction": "OVER",
        "reason": "Garbage Time Usage. 4Q Blowout Scorer.",
        "confidence": "Medium-High"
    })
    
    legs.append({
        "player": "Bilal Coulibaly",
        "team": "WAS",
        "prop": "Rebounds",
        "prediction": "OVER",
        "reason": "Development Minutes. Will play through blowout.",
        "confidence": "Medium"
    })

    # 4. Output
    df = pd.DataFrame(legs)
    print("\n=== 🎯 GENERATED LEGS (CLE vs WAS) ===")
    print(df[['player', 'team', 'prop', 'prediction', 'reason', 'confidence']].to_string(index=False))

if __name__ == "__main__":
    analyze_cle_was()
