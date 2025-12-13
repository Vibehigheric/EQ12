import pandas as pd
import time

def analyze_ind_phi_matchup():
    print("\n=== EQ12 Strategy Engine: IND vs PHI (12/12/2025) ===")
    
    # --- ROSTER CONTEXT ---
    # IND: Haliburton, Siakam, Mathurin, Turner (MISSING from roster output -> Check Injury/Trade?)
    # PHI: Embiid, Maxey, George, Drummond
    
    # CRITICAL NOTE: Myles Turner is NOT in the roster output above.
    # He is usually #33. The roster shows Jay Huff (#32), Isaiah Jackson (#22), Tony Bradley (#13).
    # This implies Myles Turner is OUT or TRADED.
    # This is a MASSIVE variable.
    
    print("\n🚨 CRITICAL ROSTER ALERT: Myles Turner NOT DETECTED.")
    print("   -> Implication: IND interior defense is compromised.")
    print("   -> Implication: Joel Embiid has no natural matchup.")
    
    # --- STRATEGY GENERATION ---
    
    bets = []
    
    # 1. Joel Embiid (PHI) - Points OVER
    # Logic: No Myles Turner. Isaiah Jackson/Jay Huff cannot guard Embiid without fouling.
    bets.append({
        'player': 'Joel Embiid',
        'team': 'PHI',
        'prop': 'Points',
        'prediction': 'OVER',
        'reason': 'No Myles Turner (Interior Defense Void). Foul trouble for IND bigs.',
        'confidence': 'MAX'
    })
    
    # 2. Tyrese Haliburton (IND) - Assists OVER
    # Logic: Pace up game. PHI defense (Embiid drop) allows mid-range/floaters or lobs.
    # Without Turner popping, Hali will look for Siakam/Mathurin cutting.
    bets.append({
        'player': 'Tyrese Haliburton',
        'team': 'IND',
        'prop': 'Assists',
        'prediction': 'OVER',
        'reason': 'High Pace. Embiid Drop Coverage opens passing lanes.',
        'confidence': 'High'
    })
    
    # 3. Pascal Siakam (IND) - Rebounds OVER
    # Logic: Without Turner, Siakam is the primary rebounder.
    bets.append({
        'player': 'Pascal Siakam',
        'team': 'IND',
        'prop': 'Rebounds',
        'prediction': 'OVER',
        'reason': 'Rebounding Vacuum (No Turner). Must crash glass vs Embiid/Drummond.',
        'confidence': 'High'
    })
    
    # 4. Tyrese Maxey (PHI) - Points OVER
    # Logic: IND perimeter defense (Haliburton/Mathurin) is weak. Maxey speed kills IND transition D.
    bets.append({
        'player': 'Tyrese Maxey',
        'team': 'PHI',
        'prop': 'Points',
        'prediction': 'OVER',
        'reason': 'Transition Scoring vs IND weak perimeter D.',
        'confidence': 'Medium-High'
    })
    
    # 5. Isaiah Jackson (IND) - Fouls OVER (if available) or Minutes UNDER (Foul Trouble)
    # Logic: He has to guard Embiid. He averages high fouls per minute.
    bets.append({
        'player': 'Isaiah Jackson',
        'team': 'IND',
        'prop': 'Fouls',
        'prediction': 'OVER (Risk of DQ)',
        'reason': 'Primary defender on Embiid. High foul rate.',
        'confidence': 'High'
    })

    # 6. Paul George (PHI) - 3PM OVER
    # Logic: Siakam will be busy helping on Embiid. PG13 gets open looks on kickouts.
    bets.append({
        'player': 'Paul George',
        'team': 'PHI',
        'prop': '3-Pointers',
        'prediction': 'OVER',
        'reason': 'Spacing from Embiid double-teams.',
        'confidence': 'Medium'
    })

    # 7. T.J. McConnell (IND) - Points + Assists OVER
    # Logic: Bench unit pace pusher. PHI bench (Lowry/Reggie Jackson?) can be exploited by TJ's energy.
    bets.append({
        'player': 'T.J. McConnell',
        'team': 'IND',
        'prop': 'Pts + Ast',
        'prediction': 'OVER',
        'reason': 'Bench Energy vs Older PHI Bench.',
        'confidence': 'Medium'
    })

    # 8. Andre Drummond (PHI) - Rebounds OVER
    # Logic: Backup minutes. He eats rebounds against IND backup bigs (Wiseman/Jackson).
    bets.append({
        'player': 'Andre Drummond',
        'team': 'PHI',
        'prop': 'Rebounds',
        'prediction': 'OVER',
        'reason': 'Elite Rebounder vs Weak IND Interior Depth.',
        'confidence': 'High'
    })

    # --- OUTPUT ---
    print("\n=== 🎯 GENERATED LEGS (IND vs PHI) ===")
    df = pd.DataFrame(bets)
    print(df.to_string(index=False))

if __name__ == "__main__":
    analyze_ind_phi_matchup()
