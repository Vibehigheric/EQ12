import random

def generate_recommendations(scanner_results=None):
    """
    Generates betting recommendations based on scanner results and internal logic.
    """
    print("\n🧩 EQ12 Recommendation Engine")
    print("============================")
    
    recommendations = []

    # 1. Arbitrage / Sure Bets (from Scanner)
    if scanner_results:
        for arb in scanner_results:
            recommendations.append({
                "type": "ARBITRAGE",
                "desc": f"Guaranteed Profit: {arb['event']}",
                "confidence": 100.0,
                "edge": arb['profit_margin']
            })

    # 2. Value Bets (Mock Logic for now - would come from ML Engine)
    # In a real system, this would query ml_engine.predict()
    recommendations.append({
        "type": "VALUE",
        "desc": "NBA: Lakers ML @ 2.05 (Model Prob: 55%)",
        "confidence": 55.0,
        "edge": 12.75 # (2.05 * 0.55) - 1 = 12.75%
    })
    
    recommendations.append({
        "type": "PROP",
        "desc": "MLB: Ohtani Over 6.5 Ks (Coral TPU Projection: 8.2)",
        "confidence": 65.0,
        "edge": 15.0
    })

    # 3. Parlay Builder (Cross-Sport)
    parlay_legs = [
        "Lakers ML",
        "Chiefs -3.5",
        "Man City ML"
    ]
    recommendations.append({
        "type": "PARLAY",
        "desc": f"3-Leg Cross-Sport: {', '.join(parlay_legs)}",
        "confidence": 40.0,
        "edge": 8.5
    })

    # Output
    print(f"Generated {len(recommendations)} Recommendations:\n")
    for rec in recommendations:
        print(f"[{rec['type']}] {rec['desc']}")
        print(f"   Confidence: {rec['confidence']}% | Edge: {rec['edge']}%")
        print("-" * 40)

if __name__ == "__main__":
    # Test with mock scanner data
    mock_arbs = [{
        "event": "Warriors @ Lakers",
        "profit_margin": 2.5,
        "bet_home": {"team": "Lakers", "odds": 2.05, "book": "FanDuel"},
        "bet_away": {"team": "Warriors", "odds": 2.05, "book": "DraftKings"} # Impossible odds but for testing
    }]
    generate_recommendations(mock_arbs)
