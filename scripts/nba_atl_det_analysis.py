import os
import sys
import requests
import pandas as pd
from datetime import datetime, timezone
from nba_api.stats.endpoints import scoreboardv2, commonteamroster, playergamelog, teamgamelog
from nba_api.stats.static import teams, players
import time

# Configuration
ODDS_API_KEY = "ODDS_API_KEY_PLACEHOLDER"
ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
TARGET_MATCHUP = {"ATL", "DET"}

def get_odds(api_key):
    """Fetch odds for NBA games."""
    params = {
        'apiKey': api_key,
        'regions': 'us',
        'markets': 'h2h,spreads,totals', # Fetching to ignore them as per instruction, but good to have context
        'oddsFormat': 'american'
    }
    try:
        response = requests.get(ODDS_API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching odds: {e}")
        return []

def get_game_info():
    """Find the ATL vs DET game ID for today."""
    # Note: ScoreboardV2 might need a specific date format
    today = datetime.now().strftime('%Y-%m-%d')
    # For simulation/demo purposes, if no game today, we might need to look at schedule
    # But user said "Today".
    board = scoreboardv2.ScoreboardV2(game_date=today)
    games = board.game_header.get_data_frame()
    
    target_game = None
    for index, row in games.iterrows():
        home_team_id = row['HOME_TEAM_ID']
        visitor_team_id = row['VISITOR_TEAM_ID']
        
        home_team = teams.find_team_name_by_id(home_team_id)
        visitor_team = teams.find_team_name_by_id(visitor_team_id)
        
        if home_team and visitor_team:
            teams_in_game = {home_team['abbreviation'], visitor_team['abbreviation']}
            if TARGET_MATCHUP.issubset(teams_in_game):
                target_game = row
                break
    
    return target_game

def analyze_roster_and_usage(team_id, team_abbrev):
    """Analyze roster for usage trends and potential 'Rotation Shock'."""
    print(f"\nAnalyzing {team_abbrev} Roster & Usage...")
    
    # Get Roster
    roster = commonteamroster.CommonTeamRoster(team_id=team_id).common_team_roster.get_data_frame()
    
    # We need to identify injuries. 
    # Since nba_api doesn't have a direct real-time injury endpoint easily accessible without parsing,
    # we will simulate "Rotation Shock" detection by looking at recent DNP (Did Not Play) in last game vs season.
    # Or we rely on the user's prompt implying we should look for "Who is OUT".
    # For this script, we'll look at the last game's active players.
    
    # Get Team Game Log to find last game ID
    # Current date is Dec 2025, so season is 2025-26
    season = '2025-26'
    try:
        gamelog = teamgamelog.TeamGameLog(team_id=team_id, season=season).team_game_log.get_data_frame()
    except Exception:
        gamelog = pd.DataFrame()

    if gamelog.empty:
        # Fallback to previous season if current is empty
        try:
            gamelog = teamgamelog.TeamGameLog(team_id=team_id, season='2024-25').team_game_log.get_data_frame()
        except Exception:
            gamelog = pd.DataFrame()
        
    if gamelog.empty:
        print("No game log found (API might be out of sync with 2025 date). Using SIMULATED data for demonstration.")
        # Return mock data for ATL/DET to demonstrate the logic
        if team_abbrev == 'ATL':
            return pd.DataFrame([
                {'name': 'Trae Young', 'id': 1, 'season_pts': 26.5, 'l5_pts': 28.0, 'season_min': 34.0, 'l5_min': 36.0, 'usage_delta': 2.5, 'role': 'Starter'},
                {'name': 'Jalen Johnson', 'id': 2, 'season_pts': 16.0, 'l5_pts': 18.5, 'season_min': 32.0, 'l5_min': 34.0, 'usage_delta': 1.2, 'role': 'Starter'},
                {'name': 'Bogdan Bogdanovic', 'id': 3, 'season_pts': 14.0, 'l5_pts': 12.0, 'season_min': 28.0, 'l5_min': 25.0, 'usage_delta': -0.5, 'role': 'Starter'},
                {'name': 'Onyeka Okongwu', 'id': 4, 'season_pts': 10.0, 'l5_pts': 14.0, 'season_min': 24.0, 'l5_min': 28.0, 'usage_delta': 1.8, 'role': 'Bench'}, # Bench promoted?
                {'name': 'Dyson Daniels', 'id': 5, 'season_pts': 8.0, 'l5_pts': 9.0, 'season_min': 20.0, 'l5_min': 22.0, 'usage_delta': 0.2, 'role': 'Bench'}
            ])
        elif team_abbrev == 'DET':
            return pd.DataFrame([
                {'name': 'Cade Cunningham', 'id': 10, 'season_pts': 22.5, 'l5_pts': 24.0, 'season_min': 35.0, 'l5_min': 36.0, 'usage_delta': 0.5, 'role': 'Starter'},
                {'name': 'Jaden Ivey', 'id': 11, 'season_pts': 18.0, 'l5_pts': 20.0, 'season_min': 30.0, 'l5_min': 32.0, 'usage_delta': 1.1, 'role': 'Starter'},
                {'name': 'Jalen Duren', 'id': 12, 'season_pts': 12.0, 'l5_pts': 10.0, 'season_min': 28.0, 'l5_min': 26.0, 'usage_delta': -0.8, 'role': 'Starter'},
                {'name': 'Ausar Thompson', 'id': 13, 'season_pts': 9.0, 'l5_pts': 11.0, 'season_min': 25.0, 'l5_min': 28.0, 'usage_delta': 1.5, 'role': 'Starter'},
                {'name': 'Isaiah Stewart', 'id': 14, 'season_pts': 8.0, 'l5_pts': 12.0, 'season_min': 20.0, 'l5_min': 24.0, 'usage_delta': 2.0, 'role': 'Bench'} # Bench usage spike
            ])
        return pd.DataFrame()

    last_game_id = gamelog.iloc[0]['Game_ID']
    
    # Get Player Stats for last 5 games vs Season
    # This is heavy, so we'll do it for top players
    
    analyzed_players = []
    
    for index, player in roster.iterrows():
        player_id = player['PLAYER_ID']
        player_name = player['PLAYER']
        
        # Get logs
        try:
            logs = playergamelog.PlayerGameLog(player_id=player_id, season=season).player_game_log.get_data_frame()
        except:
            logs = pd.DataFrame()

        if logs.empty:
             try:
                logs = playergamelog.PlayerGameLog(player_id=player_id, season='2024-25').player_game_log.get_data_frame()
             except:
                logs = pd.DataFrame()
        
        if logs.empty:
            continue
            
        # Calculate Season Avg
        season_pts = logs['PTS'].mean()
        season_min = logs['MIN'].apply(lambda x: int(str(x).split(':')[0]) if isinstance(x, str) else x).mean()
        season_usg_proxy = logs['FGA'].mean() + logs['FTA'].mean() * 0.44 + logs['TOV'].mean()
        
        # Calculate Last 5 Avg
        last_5 = logs.head(5)
        l5_pts = last_5['PTS'].mean()
        l5_min = last_5['MIN'].apply(lambda x: int(str(x).split(':')[0]) if isinstance(x, str) else x).mean()
        l5_usg_proxy = last_5['FGA'].mean() + last_5['FTA'].mean() * 0.44 + last_5['TOV'].mean()
        
        usage_delta = l5_usg_proxy - season_usg_proxy
        
        analyzed_players.append({
            'name': player_name,
            'id': player_id,
            'season_pts': season_pts,
            'l5_pts': l5_pts,
            'season_min': season_min,
            'l5_min': l5_min,
            'usage_delta': usage_delta,
            'role': 'Starter' if l5_min > 25 else 'Bench' # Simplified role detection
        })
        time.sleep(0.1) # Rate limit kindness
        
    return pd.DataFrame(analyzed_players)

def generate_bets(atl_df, det_df):
    """Generate bets based on the user's strategy."""
    print("\n=== 🧠 GENERATING BETS (Strategy: Injury + Rotation Shock) ===")
    
    bets = []
    
    # 1. Player Points: Secondary scorers / Bench promoted
    # Look for players with positive usage delta and increased minutes
    
    print("\n--- 🥇 Player Points (Usage Spikes) ---")
    for df, team in [(atl_df, "ATL"), (det_df, "DET")]:
        # Filter: Usage Delta > 1.0, Minutes > 20
        candidates = df[(df['usage_delta'] > 1.0) & (df['l5_min'] > 20)].sort_values(by='usage_delta', ascending=False)
        for _, row in candidates.iterrows():
            print(f"[{team}] {row['name']}: Usage Delta +{row['usage_delta']:.2f}, L5 Mins {row['l5_min']:.1f} (Season {row['season_min']:.1f})")
            bets.append({
                'type': 'Points',
                'player': row['name'],
                'team': team,
                'reason': f"Usage Spike (+{row['usage_delta']:.2f}) & Minutes Stability",
                'confidence': 'High' if row['l5_min'] > 28 else 'Medium'
            })

    # 2. Rebounds: Backup bigs / Forwards vs DET
    # DET allows rebounds. Look for ATL Forwards/Centers with good rebound rates per minute?
    # Simplified: Look for ATL bigs with stable minutes.
    print("\n--- 🥈 Rebounds (vs DET Weakness) ---")
    # Assuming we want ATL players here
    atl_bigs = atl_df[atl_df['name'].apply(lambda x: 'Capela' in x or 'Okongwu' in x or 'Johnson' in x)] # Heuristic
    for _, row in atl_bigs.iterrows():
        if row['l5_min'] > 18:
             print(f"[ATL] {row['name']}: Target Rebounds (DET Weakness). L5 Mins: {row['l5_min']:.1f}")
             bets.append({
                'type': 'Rebounds',
                'player': row['name'],
                'team': 'ATL',
                'reason': "DET Rebounding Weakness + Stable Role",
                'confidence': 'Medium'
            })

    # 3. Assists: Primary ball handlers
    print("\n--- 🥉 Assists (Primary Handlers) ---")
    # Look for high usage guards
    for df, team in [(atl_df, "ATL"), (det_df, "DET")]:
        handlers = df[(df['usage_delta'] > 0) & (df['l5_min'] > 25) & (df['name'].apply(lambda x: 'Young' in x or 'Cunningham' in x or 'Ivey' in x))]
        for _, row in handlers.iterrows():
             print(f"[{team}] {row['name']}: Target Assists. Usage Stable.")
             bets.append({
                'type': 'Assists',
                'player': row['name'],
                'team': team,
                'reason': "Primary Handler + Usage Check",
                'confidence': 'High'
            })

    return bets

def main():
    print("=== EQ12 NBA Strategy Engine: ATL vs DET ===")
    
    # 1. Odds Check
    odds = get_odds(ODDS_API_KEY)
    # Filter for ATL vs DET
    game_odds = [g for g in odds if 'Hawks' in g['home_team'] or 'Pistons' in g['home_team']]
    if game_odds:
        print(f"Found Odds for: {game_odds[0]['home_team']} vs {game_odds[0]['away_team']}")
    else:
        print("No specific odds found for ATL/DET today (might be off-board or API limit). Proceeding with Stats.")

    # 2. Game Info
    game = get_game_info()
    if game is None:
        print("⚠️ Game ATL vs DET not found in today's NBA API schedule.")
        print("Assuming simulation mode or date mismatch. Checking rosters anyway.")
        # Manually set IDs for ATL (1610612737) and DET (1610612765)
        atl_id = 1610612737
        det_id = 1610612765
    else:
        print(f"Game Found: {game['GAME_ID']}")
        atl_id = 1610612737 # Hawks
        det_id = 1610612765 # Pistons

    # 3. Analyze
    atl_stats = analyze_roster_and_usage(atl_id, "ATL")
    det_stats = analyze_roster_and_usage(det_id, "DET")
    
    if atl_stats.empty or det_stats.empty:
        print("Failed to fetch stats.")
        return

    # 4. Generate Bets
    bets = generate_bets(atl_stats, det_stats)
    
    # 5. Construct SGPs
    print("\n=== 🏗️ Micro-SGP Construction ===")
    # Simple logic: Pair Points + Assists for same player, or Points + Rebounds for Bigs
    
    sgps = []
    for bet in bets:
        if bet['type'] == 'Points':
            # Look for correlated bet
            partner = next((b for b in bets if b['player'] == bet['player'] and b['type'] == 'Assists'), None)
            if partner:
                sgps.append(f"SGP: {bet['player']} Points + {bet['player']} Assists")
    
    if not sgps:
        print("No perfect correlation found for SGPs. Suggest single props.")
        for bet in bets:
            print(f"Single: {bet['player']} {bet['type']} ({bet['reason']})")
    else:
        for sgp in set(sgps):
            print(sgp)

    print("\n=== 🛑 DETROIT EXPLOIT WARNING ===")
    print("Remember: DET games have high blowout risk.")
    print("Avoid 4Q-dependent overs for Stars (Trae Young, Cade Cunningham).")
    print("Prefer 1H lines or 'Minutes-Safe' players (Bench/Role players).")

if __name__ == "__main__":
    main()
