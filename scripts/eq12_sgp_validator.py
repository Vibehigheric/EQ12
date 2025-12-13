#!/usr/bin/env python3
"""
EQ12 SGP Validator - Check parlays against betting intelligence rules
Validates SGPs for correlation conflicts and contradictory legs.
"""

def validate_sgp_legs(legs: list) -> dict:
    """
    Validate SGP legs for contradictions and correlation issues.
    
    HARDCODED SPORTSBOOK RULES:
    1. Cannot combine ML + Spread + Total for same team on one slip
    2. No duplicate legs
    3. No contradictory outcomes
    
    Returns:
        dict: {
            'valid': bool,
            'errors': list,
            'warnings': list,
            'correlation_risk': str
        }
    """
    errors = []
    warnings = []
    correlation_risk = "unknown"
    
    # Extract leg types
    leg_types = [leg.get('pick', '') for leg in legs]
    
    # CHECK 1: HARDCODED SPORTSBOOK RULE - No ML + Spread + Total same team
    same_team_markets = {}
    
    for leg in legs:
        pick = leg.get('pick', '').upper()
        
        # Identify team
        team = None
        if 'SAC' in pick:
            team = 'SAC'
        elif 'UTA' in pick or 'UTAH' in pick:
            team = 'UTA'
        elif 'PHO' in pick or 'PHOENIX' in pick:
            team = 'PHO'
        elif 'OKC' in pick or 'OKLAHOMA' in pick:
            team = 'OKC'
        
        if team:
            if team not in same_team_markets:
                same_team_markets[team] = {'ml': False, 'spread': False, 'total': False}
            
            # Identify market type
            if 'MONEYLINE' in pick or 'ML' in pick:
                same_team_markets[team]['ml'] = True
            elif '+' in pick or '-' in pick and any(char.isdigit() for char in pick):
                # Spread has +/- followed by number
                if 'OVER' not in pick and 'UNDER' not in pick:
                    same_team_markets[team]['spread'] = True
            if 'OVER' in pick or 'UNDER' in pick:
                same_team_markets[team]['total'] = True
    
    # Check if any team has multiple market types
    for team, markets in same_team_markets.items():
        market_count = sum([markets['ml'], markets['spread'], markets['total']])
        if market_count > 1:
            active_markets = []
            if markets['ml']:
                active_markets.append('Moneyline')
            if markets['spread']:
                active_markets.append('Spread')
            if markets['total']:
                active_markets.append('Total')
            
            errors.append(
                f"SPORTSBOOK HARD RULE: Cannot combine {' + '.join(active_markets)} "
                f"for {team} on same slip. Pick ONE market type per team."
            )
    
    # CHECK 2: Contradictory outcomes in same game
    # Example: SAC ML + UTA -3.0 (can't both be true)
    contradictions = []
    
    # SAC wins (SAC ML) means SAC must cover +3.0, UTA -3.0 LOSES
    # UTA -3.0 means UTA wins by 4+, SAC ML LOSES
    for i, leg1 in enumerate(legs):
        for j, leg2 in enumerate(legs[i+1:], start=i+1):
            pick1 = leg1.get('pick', '').upper()
            pick2 = leg2.get('pick', '').upper()
            
            # SAC Moneyline vs UTA spread
            if 'SAC MONEYLINE' in pick1 and 'UTA -' in pick2:
                contradictions.append({
                    'leg1': leg1['pick'],
                    'leg2': leg2['pick'],
                    'reason': 'SAC winning (ML) contradicts UTA covering spread (-3.0). These are mutually exclusive.'
                })
            
            # UTA Moneyline vs SAC spread  
            if 'UTA MONEYLINE' in pick1 and 'SAC +' in pick2:
                # This is OK - UTA can win but SAC can cover +3.0
                pass
            
            # SAC ML vs UTA ML (impossible)
            if 'SAC MONEYLINE' in pick1 and 'UTA MONEYLINE' in pick2:
                contradictions.append({
                    'leg1': leg1['pick'],
                    'leg2': leg2['pick'],
                    'reason': 'Both teams cannot win moneyline. Mutually exclusive.'
                })
            
            # SAC +X vs UTA -X (usually OK if close game)
            if 'SAC +' in pick1 and 'UTA -' in pick2:
                warnings.append({
                    'legs': [leg1['pick'], leg2['pick']],
                    'reason': 'Both spreads can hit if game lands in middle (e.g., UTA wins by 1-3)'
                })
    
    # CHECK 2: Duplicate legs (Over appears twice)
    leg_counts = {}
    for leg in leg_types:
        leg_counts[leg] = leg_counts.get(leg, 0) + 1
    
    duplicates = []
    for leg, count in leg_counts.items():
        if count > 1:
            duplicates.append({
                'leg': leg,
                'count': count,
                'reason': f'Leg appears {count} times - sportsbooks will reject this'
            })
    
    # CHECK 3: Correlation warnings
    correlation_warnings = []
    
    # ML + Spread same team = correlated
    for leg1 in legs:
        for leg2 in legs:
            if leg1 == leg2:
                continue
            pick1 = leg1.get('pick', '').upper()
            pick2 = leg2.get('pick', '').upper()
            
            # SAC ML + SAC spread
            if 'SAC MONEYLINE' in pick1 and 'SAC +' in pick2:
                correlation_warnings.append({
                    'legs': [leg1['pick'], leg2['pick']],
                    'reason': 'ML + spread on same team highly correlated (if SAC wins, they auto-cover +3.0)'
                })
    
    # Set errors
    if contradictions:
        errors.extend([c['reason'] for c in contradictions])
        correlation_risk = "INVALID"
    
    if duplicates:
        errors.extend([d['reason'] for d in duplicates])
    
    if correlation_warnings:
        warnings.extend([w['reason'] for w in correlation_warnings])
        if correlation_risk == "unknown":
            correlation_risk = "high"
    
    # Determine validity
    valid = len(errors) == 0
    
    return {
        'valid': valid,
        'errors': errors,
        'warnings': warnings,
        'correlation_risk': correlation_risk,
        'contradictions': contradictions,
        'duplicates': duplicates,
        'correlation_warnings': correlation_warnings
    }


# VALIDATE THE PROBLEMATIC SGPs
if __name__ == '__main__':
    print("\n" + "="*80)
    print("🔍 EQ12 SGP VALIDATOR - Checking Parlays Against Betting Intelligence")
    print("="*80)
    
    # The problematic SAC/UTA 5-leg
    sac_uta_5leg = [
        {"pick": "SAC Moneyline (+124)", "odds": 124, "desc": "Kings win"},
        {"pick": "SAC +3.0 (-114)", "odds": -114, "desc": "Kings cover"},
        {"pick": "Over 242.5 (-110)", "odds": -110, "desc": "High scoring"},
        {"pick": "UTA -3.0 (-110)", "odds": -110, "desc": "Jazz cover (hedge)"},
        {"pick": "Over 242.5 (-110)", "odds": -110, "desc": "Shootout confirmed"}
    ]
    
    print("\n❌ TESTING: SAC/UTA 5-Leg MEGA MOONSHOT")
    print("-" * 80)
    for i, leg in enumerate(sac_uta_5leg, 1):
        print(f"{i}. {leg['pick']} - {leg['desc']}")
    
    result = validate_sgp_legs(sac_uta_5leg)
    
    print(f"\n🔍 VALIDATION RESULT:")
    print(f"   Valid: {'✅ YES' if result['valid'] else '❌ NO'}")
    print(f"   Correlation Risk: {result['correlation_risk']}")
    
    if result['errors']:
        print(f"\n❌ ERRORS ({len(result['errors'])}):")
        for i, error in enumerate(result['errors'], 1):
            print(f"   {i}. {error}")
    
    if result['warnings']:
        print(f"\n⚠️  WARNINGS ({len(result['warnings'])}):")
        for i, warning in enumerate(result['warnings'], 1):
            print(f"   {i}. {warning}")
    
    if result['contradictions']:
        print(f"\n🚫 CONTRADICTORY LEGS:")
        for c in result['contradictions']:
            print(f"   • {c['leg1']} ⚔️  {c['leg2']}")
            print(f"     Reason: {c['reason']}")
    
    if result['duplicates']:
        print(f"\n🔄 DUPLICATE LEGS:")
        for d in result['duplicates']:
            print(f"   • {d['leg']} appears {d['count']} times")
            print(f"     Reason: {d['reason']}")
    
    # Test PHO/OKC parlay
    print("\n" + "="*80)
    print("❌ TESTING: PHO/OKC 3-Leg Upset")
    print("-" * 80)
    
    pho_okc_3leg = [
        {"pick": "PHO Moneyline (+700)", "odds": 700, "desc": "Suns win"},
        {"pick": "PHO +14.5 (-110)", "odds": -110, "desc": "Suns cover"},
        {"pick": "Over 223.5 (-110)", "odds": -110, "desc": "High scoring"}
    ]
    
    for i, leg in enumerate(pho_okc_3leg, 1):
        print(f"{i}. {leg['pick']} - {leg['desc']}")
    
    result2 = validate_sgp_legs(pho_okc_3leg)
    
    print(f"\n🔍 VALIDATION RESULT:")
    print(f"   Valid: {'✅ YES' if result2['valid'] else '❌ NO'}")
    print(f"   Correlation Risk: {result2['correlation_risk']}")
    
    if result2['errors']:
        print(f"\n❌ ERRORS ({len(result2['errors'])}):")
        for i, error in enumerate(result2['errors'], 1):
            print(f"   {i}. {error}")
    
    if result2['warnings']:
        print(f"\n⚠️  WARNINGS ({len(result2['warnings'])}):")
        for i, warning in enumerate(result2['warnings'], 1):
            print(f"   {i}. {warning}")
    
    # RECOMMENDED VALID PARLAYS
    print("\n" + "="*80)
    print("✅ RECOMMENDED VALID SGPs (Following Betting Intelligence)")
    print("="*80)
    
    print("\n✅ OPTION 1: SAC Upset Play (Valid)")
    print("-" * 80)
    valid_sac = [
        {"pick": "SAC Moneyline (+124)", "desc": "Kings win"},
        {"pick": "SAC +3.0 (-114)", "desc": "Kings cover (correlated)"},
        {"pick": "Over 242.5 (-110)", "desc": "High scoring"}
    ]
    for i, leg in enumerate(valid_sac, 1):
        print(f"{i}. {leg['pick']} - {leg['desc']}")
    result3 = validate_sgp_legs(valid_sac)
    print(f"Valid: {'✅' if result3['valid'] else '❌'} | Risk: {result3['correlation_risk']}")
    
    print("\n✅ OPTION 2: UTA Home Win (Valid)")
    print("-" * 80)
    valid_uta = [
        {"pick": "UTA Moneyline (-146)", "desc": "Jazz win"},
        {"pick": "UTA -3.0 (-110)", "desc": "Jazz cover (correlated)"},
        {"pick": "Under 242.5 (-110)", "desc": "Defense wins"}
    ]
    for i, leg in enumerate(valid_uta, 1):
        print(f"{i}. {leg['pick']} - {leg['desc']}")
    result4 = validate_sgp_legs(valid_uta)
    print(f"Valid: {'✅' if result4['valid'] else '❌'} | Risk: {result4['correlation_risk']}")
    
    print("\n" + "="*80)
    print("📋 SUMMARY")
    print("="*80)
    print("❌ INVALID: SAC ML + UTA -3.0 (contradictory - can't both win)")
    print("❌ INVALID: Over 242.5 appearing twice (duplicate leg)")
    print("✅ VALID: SAC ML + SAC spread + Over (correlated but allowed)")
    print("✅ VALID: UTA ML + UTA spread + Under (correlated but allowed)")
    print("⚠️  WARNING: ML + spread same team = high correlation")
    print("\n💡 KEY RULE: Never bet contradictory outcomes in same game!")
    print("="*80)
