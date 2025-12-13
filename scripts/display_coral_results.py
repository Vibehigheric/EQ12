#!/usr/bin/env python3
"""
EQ12 Coral AI Results Display - Show top betting recommendations from live analysis
"""

import json
from pathlib import Path

def display_coral_results():
    # Load the latest results
    results_dir = Path('C:/EQ12/coral_betting_ai/reports')
    latest_file = max(results_dir.glob('coral_results_*.json'), key=lambda f: f.stat().st_mtime)

    with open(latest_file) as f:
        data = json.load(f)

    print(' EQ12 CORAL EDGE TPU BETTING AI - LIVE ANALYSIS RESULTS')
    print('='*70)
    print(f' Analysis Complete: {data["total_games_analyzed"]} games processed')
    print(f' Total Predictions: {len(data["bets"])} betting opportunities')
    print(f' Processing Mode: {data["coral_tpu_status"]}')
    print(f' Analysis Time: {data["timestamp"]}')
    print()

    # Sort by EV score and show top 10
    bets = sorted(data['bets'], key=lambda x: x.get('coral_ev_score', 0), reverse=True)[:10]

    print(' TOP 10 CORAL AI BETTING RECOMMENDATIONS:')
    print('-'*70)

    for i, bet in enumerate(bets, 1):
        game_desc = f'{bet["away_team"]} @ {bet["home_team"]}'
        ev_score = bet.get('coral_ev_score', 0)
        confidence = bet.get('coral_confidence', 0)
        odds = bet.get('odds', 0)
        market = bet.get('market', '')
        team = bet.get('team', '')
        point = bet.get('point')
        
        print(f'{i:2d}. {game_desc}')
        print(f'     {team} ({market})')
        if point:
            print(f'     Spread: {point} @ {odds:.2f}')
        else:
            print(f'     Odds: {odds:.2f}')
        print(f'     Coral EV Score: {ev_score:.6f}')
        print(f'     AI Confidence: {confidence:.1%}')
        print()

    # Show unique games
    unique_games = {}
    for bet in data['bets']:
        game_key = f"{bet['away_team']} @ {bet['home_team']}"
        if game_key not in unique_games:
            unique_games[game_key] = bet

    print(f' GAMES ANALYZED ({len(unique_games)} unique matchups):')
    print('-'*50)
    for game_desc, bet in list(unique_games.items())[:10]:
        commence_time = bet.get('commence_time', '')
        sport = bet.get('sport', '').replace('americanfootball_', '').replace('basketball_', '').upper()
        print(f' {game_desc} ({sport}) - {commence_time[:10]}')

    print()
    print(' Coral Edge TPU Betting AI Status: ACTIVE & PROCESSING LIVE DATA')
    print(' Revolutionary dual-processor intelligence system operational!')

if __name__ == '__main__':
    display_coral_results()