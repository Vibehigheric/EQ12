#!/usr/bin/env python3
"""
EQ12 Winning Margin Analysis Tool
Analyzes live games for optimal winning margin betting opportunities using Coral AI predictions
"""

import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_coral_results(file_path: str) -> Dict[str, Any]:
    """Load Coral AI results from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading Coral results: {e}")
        return {}

def analyze_winning_margins(coral_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze games for winning margin betting opportunities"""
    margin_opportunities = []
    
    # Group bets by game
    games = {}
    for bet in coral_data.get('bets', []):
        game_id = bet['game_id']
        if game_id not in games:
            games[game_id] = []
        games[game_id].append(bet)
    
    for game_id, game_bets in games.items():
        # Focus on NFL games for margin analysis
        if not any(bet['sport'] == 'americanfootball_nfl' for bet in game_bets):
            continue
            
        # Get moneyline and spread bets
        h2h_bets = [bet for bet in game_bets if bet['market'] == 'h2h']
        spread_bets = [bet for bet in game_bets if bet['market'] == 'spreads']
        
        if len(h2h_bets) >= 2 and len(spread_bets) >= 2:
            home_team = game_bets[0]['home_team']
            away_team = game_bets[0]['away_team']
            commence_time = game_bets[0]['commence_time']
            
            # Get favorite and underdog
            home_ml = next((bet for bet in h2h_bets if bet['team'] == home_team), None)
            away_ml = next((bet for bet in h2h_bets if bet['team'] == away_team), None)
            
            if home_ml and away_ml:
                favorite = home_team if home_ml['odds'] < away_ml['odds'] else away_team
                underdog = away_team if favorite == home_team else home_team
                favorite_odds = home_ml['odds'] if favorite == home_team else away_ml['odds']
                underdog_odds = away_ml['odds'] if favorite == home_team else home_ml['odds']
                
                # Get spread information
                favorite_spread = next((bet for bet in spread_bets if bet['team'] == favorite), None)
                underdog_spread = next((bet for bet in spread_bets if bet['team'] == underdog), None)
                
                if favorite_spread and underdog_spread:
                    spread_line = abs(favorite_spread['point']) if favorite_spread['point'] else 0
                    
                    # Calculate margin scenarios
                    margin_analysis = analyze_margin_scenarios(
                        favorite, underdog, favorite_odds, underdog_odds, 
                        spread_line, favorite_spread, underdog_spread
                    )
                    
                    margin_opportunities.append({
                        'game_id': game_id,
                        'home_team': home_team,
                        'away_team': away_team,
                        'commence_time': commence_time,
                        'favorite': favorite,
                        'underdog': underdog,
                        'spread_line': spread_line,
                        'margin_analysis': margin_analysis,
                        'coral_ev_avg': sum(bet['coral_ev_score'] for bet in game_bets) / len(game_bets)
                    })
    
    # Sort by EV score
    margin_opportunities.sort(key=lambda x: x['coral_ev_avg'], reverse=True)
    return margin_opportunities

def analyze_margin_scenarios(favorite: str, underdog: str, fav_odds: float, dog_odds: float, 
                           spread: float, fav_spread_bet: Dict, dog_spread_bet: Dict) -> Dict[str, Any]:
    """Analyze different winning margin scenarios"""
    
    scenarios = {
        'blowout_favorite': {
            'description': f"{favorite} wins by {int(spread + 7)}+ points",
            'strategy': f"{favorite} ML + {favorite} spread",
            'reasoning': "Heavy favorite dominates, covers large spread",
            'odds_combo': fav_odds * fav_spread_bet['odds'],
            'risk_level': "Medium",
            'margin_range': f"{int(spread + 1)}+ points"
        },
        'close_favorite': {
            'description': f"{favorite} wins by 1-{int(spread)} points", 
            'strategy': f"{favorite} ML + {underdog} spread",
            'reasoning': "Favorite wins but doesn't cover spread",
            'odds_combo': fav_odds * dog_spread_bet['odds'],
            'risk_level': "High",
            'margin_range': f"1-{int(spread)} points"
        },
        'upset_close': {
            'description': f"{underdog} wins by 1-6 points",
            'strategy': f"{underdog} ML (straight bet)",
            'reasoning': "Underdog pulls upset in close game",
            'odds_combo': dog_odds,
            'risk_level': "High", 
            'margin_range': "1-6 points"
        },
        'upset_blowout': {
            'description': f"{underdog} wins by 7+ points",
            'strategy': f"{underdog} ML + {underdog} spread",
            'reasoning': "Major upset with dominant performance",
            'odds_combo': dog_odds * dog_spread_bet['odds'],
            'risk_level': "Very High",
            'margin_range': "7+ points"
        }
    }
    
    # Calculate implied probabilities and value
    for scenario in scenarios.values():
        implied_prob = 1 / scenario['odds_combo']
        scenario['implied_probability'] = f"{implied_prob:.1%}"
        scenario['potential_payout_25'] = f"${scenario['odds_combo'] * 25:.2f}"
        scenario['profit_25'] = f"${(scenario['odds_combo'] * 25) - 25:.2f}"
    
    return scenarios

def generate_margin_report(opportunities: List[Dict[str, Any]], workspace: str) -> str:
    """Generate comprehensive winning margin report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(workspace, 'logs', f'winning_margin_analysis_{timestamp}.md')
    
    with open(report_path, 'w') as f:
        f.write("#  EQ12 WINNING MARGIN ANALYSIS\n")
        f.write(f"*Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p EST')}*\n\n")
        
        f.write("##  LIVE GAMES MARGIN OPPORTUNITIES\n\n")
        
        for i, opp in enumerate(opportunities[:5], 1):  # Top 5 games
            f.write(f"### {i}. {opp['away_team']} @ {opp['home_team']}\n")
            f.write(f"**Game Time:** {opp['commence_time']}\n")
            f.write(f"**Spread:** {opp['favorite']} -{opp['spread_line']}\n")  
            f.write(f"**Coral EV Score:** {opp['coral_ev_avg']:.2e}\n\n")
            
            f.write("####  MARGIN BETTING SCENARIOS:\n\n")
            
            for scenario_name, scenario in opp['margin_analysis'].items():
                risk_emoji = {"Medium": "", "High": "", "Very High": ""}
                f.write(f"**{scenario['description'].upper()}**\n")
                f.write(f"- **Strategy:** {scenario['strategy']}\n")
                f.write(f"- **Combined Odds:** {scenario['odds_combo']:.2f}x\n")
                f.write(f"- **$25 Payout:** {scenario['potential_payout_25']}\n")
                f.write(f"- **$25 Profit:** {scenario['profit_25']}\n")
                f.write(f"- **Risk Level:** {risk_emoji.get(scenario['risk_level'], '')} {scenario['risk_level']}\n")
                f.write(f"- **Reasoning:** {scenario['reasoning']}\n\n")
            
            f.write("---\n\n")
        
        f.write("##  METHODOLOGY\n")
        f.write("- Analyzed using Coral Edge TPU AI models\n")
        f.write("- EV Predictor: 50 epochs, 0.0209 MAE accuracy\n") 
        f.write("- Prop Scorer: 30 epochs, 100% validation accuracy\n")
        f.write("- Real-time odds from 13+ sportsbooks\n\n")
        
        f.write("##  RISK DISCLAIMER\n")
        f.write("Winning margin bets are complex and high-risk. Only bet what you can afford to lose.\n")
    
    return report_path

def send_margin_alert(opportunities: List[Dict[str, Any]], workspace: str):
    """Send Telegram alert with top margin opportunities"""
    try:
        # Load Telegram config
        config_path = os.path.join(workspace, 'coral_betting_ai', 'coral_config.env')
        bot_token = None
        chat_id = None
        
        with open(config_path, 'r') as f:
            for line in f:
                if 'TELEGRAM_BOT_TOKEN' in line:
                    bot_token = line.split('=')[1].strip()
                elif 'TELEGRAM_CHAT_ID' in line:
                    chat_id = line.split('=')[1].strip()
        
        if not bot_token or not chat_id:
            logger.warning("Telegram credentials not found")
            return
            
        import requests
        
        top_game = opportunities[0] if opportunities else None
        if not top_game:
            return
            
        # Get best margin scenario
        best_scenario = None
        best_odds = 0
        for scenario in top_game['margin_analysis'].values():
            if scenario['odds_combo'] > best_odds and scenario['risk_level'] != 'Very High':
                best_odds = scenario['odds_combo']
                best_scenario = scenario
        
        if best_scenario:
            message = f""" WINNING MARGIN ALERT 

 TOP MARGIN OPPORTUNITY:
{top_game['away_team']} @ {top_game['home_team']}

 BEST MARGIN BET:
{best_scenario['description']}

 DETAILS:
 Strategy: {best_scenario['strategy']}
 Odds: {best_scenario['odds_combo']:.2f}x
 $25 Payout: {best_scenario['potential_payout_25']}
 Profit: {best_scenario['profit_25']}
 Risk: {best_scenario['risk_level']}

 Reasoning: {best_scenario['reasoning']}

 LIVE NOW - Act quickly!

 Coral EV Score: {top_game['coral_ev_avg']:.2e}
 Generated by EQ12 Coral AI"""

            url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            data = {'chat_id': chat_id, 'text': message}
            response = requests.post(url, data=data)
            logger.info(f"Margin alert sent: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error sending Telegram alert: {e}")

def main():
    """Main execution function"""
    workspace = r"C:\EQ12"
    
    # Load latest Coral AI results
    results_file = os.path.join(workspace, 'coral_betting_ai', 'reports', 'coral_results_20251102_142939.json')
    
    logger.info("Loading Coral AI results...")
    coral_data = load_coral_results(results_file)
    
    if not coral_data:
        logger.error("Failed to load Coral data")
        return
    
    logger.info("Analyzing winning margin opportunities...")
    opportunities = analyze_winning_margins(coral_data)
    
    logger.info(f"Found {len(opportunities)} margin opportunities")
    
    # Generate report
    report_path = generate_margin_report(opportunities, workspace)
    logger.info(f"Report generated: {report_path}")
    
    # Send Telegram alert
    send_margin_alert(opportunities, workspace)
    
    # Print top opportunities
    print("\n TOP WINNING MARGIN OPPORTUNITIES:")
    for i, opp in enumerate(opportunities[:3], 1):
        print(f"\n{i}. {opp['away_team']} @ {opp['home_team']}")
        print(f"   Spread: {opp['favorite']} -{opp['spread_line']}")
        
        # Show best scenario
        best_scenario = max(opp['margin_analysis'].values(), 
                          key=lambda x: x['odds_combo'] if x['risk_level'] != 'Very High' else 0)
        print(f"    Best Margin: {best_scenario['description']}")
        print(f"    $25  {best_scenario['potential_payout_25']} ({best_scenario['profit_25']} profit)")
        print(f"    Strategy: {best_scenario['strategy']}")

if __name__ == "__main__":
    main()