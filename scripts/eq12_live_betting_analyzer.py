#!/usr/bin/env python3
"""
EQ12 Live Betting Opportunities Analyzer
Comprehensive analysis of live betting opportunities across all active games
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LiveBettingAnalyzer:
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.current_time = datetime.now(timezone.utc)
        
    def load_latest_data(self) -> Dict:
        """Load the most recent sports data"""
        data_files = [
            "real_games_data_20251108_155841.json",
            "real_games_data_20251108_120857.json"
        ]
        
        for data_file in data_files:
            file_path = self.workspace_path / "logs" / data_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    logger.info(f" Loaded {len(data.get('games', []))} games from {data_file}")
                    return data
                except Exception as e:
                    logger.error(f"Error loading {data_file}: {e}")
        return {}
    
    def get_game_status(self, start_time_str: str, sport: str) -> tuple[str, int, str]:
        """Determine game status with sport-specific timing"""
        try:
            game_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            time_diff_minutes = (self.current_time - game_time).total_seconds() / 60
            
            # Sport-specific game lengths
            game_lengths = {
                'NHL': 210,      # 3.5 hours (including intermissions/OT)
                'NCAAF': 210,    # 3.5 hours  
                'NCAAB': 150,    # 2.5 hours
                'NBA': 150       # 2.5 hours
            }
            
            max_length = game_lengths.get(sport, 180)
            
            if time_diff_minutes < -60:
                return "UPCOMING", int(abs(time_diff_minutes)), "Pre-game betting available"
            elif time_diff_minutes < -15:
                return "STARTING_SOON", int(abs(time_diff_minutes)), "Last chance for pre-game lines"
            elif time_diff_minutes < 0:
                return "PREGAME", int(abs(time_diff_minutes)), "Game about to start"
            elif time_diff_minutes < max_length:
                # Determine game phase for live games
                if time_diff_minutes < 30:
                    phase = "Early game"
                elif time_diff_minutes < 90:
                    phase = "Mid-game"
                elif time_diff_minutes < 150:
                    phase = "Late game"
                else:
                    phase = "Overtime/Final minutes"
                
                return "LIVE", int(time_diff_minutes), phase
            else:
                return "COMPLETED", int(time_diff_minutes), "Game finished"
        except:
            return "UNKNOWN", 0, "Status unknown"
    
    def find_live_opportunities(self) -> List[Dict]:
        """Find all live betting opportunities across sports"""
        data = self.load_latest_data()
        live_opportunities = []
        
        # Include live, starting soon, or upcoming games (exclude completed)
        for game in data.get('games', []):
            # Check if it's any sport
            sport = self.get_sport_name(game)
            start_time = game.get('start_time', '')
            status, time_info, phase = self.get_game_status(start_time, sport)
            
            # Only include games that are NOT completed
            if status in ['LIVE', 'STARTING_SOON', 'UPCOMING']:
                opportunity = {
                    'sport': sport,
                    'home_team': game.get('home_team', ''),
                    'away_team': game.get('away_team', ''),
                    'status': status,
                    'time_info': time_info,
                    'phase': phase,
                    'markets': self.extract_all_markets(game),
                    'live_value': self.calculate_live_value(game, status, time_info, sport),
                    'parlay_potential': self.assess_parlay_potential(game, status),
                    'urgency_score': self.calculate_urgency_score(status, time_info, sport)
                }
                live_opportunities.append(opportunity)
        
        # Sort by urgency score (highest first)
        live_opportunities.sort(key=lambda x: x['urgency_score'], reverse=True)
        
        return live_opportunities
    
    def get_sport_name(self, game: Dict) -> str:
        """Get standardized sport name"""
        sport_mapping = {
            'icehockey_nhl': 'NHL',
            'americanfootball_ncaaf': 'NCAAF',
            'basketball_ncaab': 'NCAAB',
            'basketball_nba': 'NBA'
        }
        
        sport_key = game.get('sport', '')
        league = game.get('league', '')
        
        return sport_mapping.get(sport_key, league if league else sport_key.upper())
    
    def extract_all_markets(self, game: Dict) -> Dict:
        """Extract all available betting markets"""
        markets = {
            'moneyline': {},
            'spreads': {},
            'totals': {},
            'props': []
        }
        
        for market in game.get('markets', []):
            market_key = market.get('key')
            
            if market_key == 'h2h':
                for outcome in market.get('outcomes', []):
                    team = outcome.get('name', '')
                    odds = outcome.get('price', 0)
                    markets['moneyline'][team] = odds
            
            elif market_key == 'spreads':
                for outcome in market.get('outcomes', []):
                    team = outcome.get('name', '')
                    odds = outcome.get('price', 0)
                    point = outcome.get('point', 0)
                    markets['spreads'][team] = {
                        'odds': odds,
                        'spread': point
                    }
            
            elif market_key == 'totals':
                for outcome in market.get('outcomes', []):
                    bet_type = outcome.get('name', '')
                    odds = outcome.get('price', 0)
                    point = outcome.get('point', 0)
                    markets['totals'][bet_type] = {
                        'odds': odds,
                        'total': point
                    }
        
        return markets
    
    def calculate_live_value(self, game: Dict, status: str, time_elapsed: int, sport: str) -> List[Dict]:
        """Calculate value for live betting based on game situation"""
        value_bets = []
        markets = self.extract_all_markets(game)
        
        # Live betting value factors
        live_factors = {
            'early_game': 0.95,    # Early game - lines still sharp
            'mid_game': 1.05,      # Mid-game - momentum factors
            'late_game': 1.15,     # Late game - high volatility
            'starting_soon': 0.90  # Pre-game - market efficient
        }
        
        if status == 'LIVE':
            if time_elapsed < 30:
                factor = live_factors['early_game']
                context = "Early game"
            elif time_elapsed < 90:
                factor = live_factors['mid_game'] 
                context = "Mid-game momentum"
            else:
                factor = live_factors['late_game']
                context = "Late game volatility"
        else:
            factor = live_factors['starting_soon']
            context = "Pre-game"
        
        # Analyze spreads
        for team, data in markets['spreads'].items():
            odds = data['odds']
            spread = data['spread']
            
            implied_prob = self.calculate_implied_probability(odds)
            base_fair_prob = 0.50
            adjusted_fair_prob = base_fair_prob * factor
            
            edge = adjusted_fair_prob - implied_prob
            
            if edge > 0.01:  # 1% minimum edge
                value_bets.append({
                    'bet_type': 'spread',
                    'bet': f"{team} {spread:+.1f}",
                    'odds': odds,
                    'edge': edge,
                    'context': context,
                    'urgency': 'HIGH' if status == 'LIVE' and time_elapsed > 60 else 'MEDIUM'
                })
        
        # Analyze totals with live context
        for bet_type, data in markets['totals'].items():
            odds = data['odds']
            total = data['total']
            
            implied_prob = self.calculate_implied_probability(odds)
            
            # Live totals adjustment based on game flow
            if status == 'LIVE':
                if sport in ['NCAAF', 'NCAAB'] and time_elapsed > 60:
                    # Late in game - scoring patterns more predictable
                    base_fair_prob = 0.52 if bet_type == 'Under' else 0.48
                else:
                    base_fair_prob = 0.50
            else:
                base_fair_prob = 0.50
            
            adjusted_fair_prob = base_fair_prob * factor
            edge = adjusted_fair_prob - implied_prob
            
            if edge > 0.005:  # 0.5% minimum for totals
                value_bets.append({
                    'bet_type': 'total',
                    'bet': f"{bet_type} {total}",
                    'odds': odds,
                    'edge': edge,
                    'context': context,
                    'urgency': 'HIGH' if status == 'LIVE' else 'MEDIUM'
                })
        
        return value_bets
    
    def assess_parlay_potential(self, game: Dict, status: str) -> Dict:
        """Assess same-game parlay potential"""
        markets = self.extract_all_markets(game)
        
        # Count available markets
        market_count = 0
        if markets['moneyline']:
            market_count += 1
        if markets['spreads']:
            market_count += 1  
        if markets['totals']:
            market_count += 1
        
        # Parlay viability
        if market_count >= 3:
            viability = "HIGH"
        elif market_count >= 2:
            viability = "MEDIUM"
        else:
            viability = "LOW"
        
        # Live parlay considerations
        if status == 'LIVE':
            considerations = [
                "Monitor momentum shifts",
                "Watch for scoring patterns",
                "Consider reduced correlation risk"
            ]
        else:
            considerations = [
                "Full market availability",
                "Pre-game line efficiency"
            ]
        
        return {
            'viability': viability,
            'available_markets': market_count,
            'considerations': considerations
        }
    
    def calculate_urgency_score(self, status: str, time_info: int, sport: str) -> float:
        """Calculate urgency score for prioritizing opportunities"""
        base_scores = {
            'LIVE': 100,
            'STARTING_SOON': 80,
            'UPCOMING': 60,
            'PREGAME': 70
        }
        
        base_score = base_scores.get(status, 0)
        
        if status == 'LIVE':
            # Higher urgency as game progresses
            time_multiplier = min(2.0, 1.0 + (time_info / 100))
            return base_score * time_multiplier
        elif status == 'STARTING_SOON':
            # Higher urgency as start approaches
            time_multiplier = max(0.5, 2.0 - (time_info / 30))
            return base_score * time_multiplier
        
        return base_score
    
    def calculate_implied_probability(self, odds: int) -> float:
        """Convert American odds to implied probability"""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    
    def get_sport_icon(self, sport: str) -> str:
        """Get emoji icon for sport"""
        sport_icons = {
            'NHL': '',
            'NCAAF': '', 
            'NCAAB': '',
            'NBA': '',
            'NFL': ''
        }
        return sport_icons.get(sport, '')

def get_sport_icon(sport: str) -> str:
    """Get emoji icon for sport"""
    sport_icons = {
        'NHL': '',
        'NCAAF': '', 
        'NCAAB': '',
        'NBA': '',
        'NFL': ''
    }
    return sport_icons.get(sport, '')

def format_live_opportunities_report(opportunities: List[Dict]) -> str:
    """Format comprehensive live betting opportunities report"""
    
    if not opportunities:
        return """
 LIVE BETTING OPPORTUNITIES ANALYSIS 
{'='*70}

 No live betting opportunities currently available.

 Check back during active game times!
{'='*70}
"""
    
    live_games = [opp for opp in opportunities if opp['status'] == 'LIVE']
    starting_soon = [opp for opp in opportunities if opp['status'] == 'STARTING_SOON']
    upcoming = [opp for opp in opportunities if opp['status'] == 'UPCOMING']
    
    report = f"""
 LIVE BETTING OPPORTUNITIES ANALYSIS (ACTIVE GAMES ONLY) 
{'='*70}

 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}
 Total Active Opportunities: {len(opportunities)}
 Live Games: {len(live_games)}
 Starting Soon: {len(starting_soon)}
 Upcoming: {len(upcoming)}
 EXCLUDED: All completed games

"""
    
    if live_games:
        report += """
 PRIORITY LIVE OPPORTUNITIES:
{'='*70}
"""
        
        for i, opp in enumerate(live_games[:5], 1):
            sport_icon = get_sport_icon(opp['sport'])
            report += f"{sport_icon} " + format_opportunity_details(opp, i, priority=True)
    
    if starting_soon:
        report += """
 STARTING SOON - LAST CHANCE:
{'='*70}
"""
        
        for i, opp in enumerate(starting_soon[:3], 1):
            sport_icon = get_sport_icon(opp['sport'])
            report += f"{sport_icon} " + format_opportunity_details(opp, i, priority=False)
    
    if upcoming:
        report += """
 UPCOMING GAMES TONIGHT:
{'='*70}
"""
        
        for i, opp in enumerate(upcoming[:5], 1):
            sport_icon = get_sport_icon(opp['sport'])
            report += f"{sport_icon} " + format_opportunity_details(opp, i, priority=False)
    
    # Top value bets across all games
    all_value_bets = []
    for opp in opportunities:
        for bet in opp['live_value']:
            bet['game'] = f"{opp['away_team']} @ {opp['home_team']}"
            bet['sport'] = opp['sport']
            bet['status'] = opp['status']
            all_value_bets.append(bet)
    
    # Sort by edge
    all_value_bets.sort(key=lambda x: x['edge'], reverse=True)
    
    if all_value_bets:
        report += """
 TOP VALUE BETS RIGHT NOW:
{'='*70}
"""
        for i, bet in enumerate(all_value_bets[:8], 1):
            edge_pct = bet['edge'] * 100
            urgency_icon = "" if bet['urgency'] == 'HIGH' else ""
            sport_icon = get_sport_icon(bet['sport'])
            report += f"""
{urgency_icon} #{i} {bet['bet']} ({bet['odds']:+d})
   Edge: {edge_pct:+.1f}% | {bet['context']} | {sport_icon} {bet['sport']}: {bet['game']}
   Status: {bet['status']} | Urgency: {bet['urgency']}

"""
    
    report += """
 LIVE BETTING STRATEGY:
{'='*70}
 Monitor game momentum for value shifts
 Higher edges available during live play
 Same-game parlays reduce correlation risk
 Act quickly on high-urgency opportunities

 RISK MANAGEMENT:
 Limit live bets to 1-2% of bankroll per opportunity
 Set stop-loss limits before betting
 Monitor multiple games simultaneously
 Don't chase losses with larger stakes

{'='*70}
"""
    
    return report

def format_opportunity_details(opp: Dict, index: int, priority: bool = False) -> str:
    """Format individual opportunity details"""
    
    urgency_icons = {
        'LIVE': '',
        'STARTING_SOON': ''
    }
    
    icon = urgency_icons.get(opp['status'], '')
    priority_flag = "  HIGH PRIORITY" if priority and opp['urgency_score'] > 150 else ""
    
    details = f"""
{icon} #{index} {opp['sport']}: {opp['away_team']} @ {opp['home_team']}{priority_flag}
{''*60}
"""
    
    if opp['status'] == 'LIVE':
        details += f"  LIVE - {opp['phase']} ({opp['time_info']} min elapsed)\n"
    else:
        details += f" Starting in {opp['time_info']} minutes\n"
    
    details += f" Urgency Score: {opp['urgency_score']:.1f}/200\n"
    
    # Show markets
    markets = opp['markets']
    
    if markets['spreads']:
        details += " SPREADS:\n"
        for team, data in list(markets['spreads'].items())[:2]:
            details += f"   {team} {data['spread']:+.1f}: {data['odds']:+d}\n"
    
    if markets['totals']:
        details += " TOTALS:\n"
        for bet_type, data in list(markets['totals'].items())[:2]:
            details += f"   {bet_type} {data['total']}: {data['odds']:+d}\n"
    
    # Value bets
    if opp['live_value']:
        details += " VALUE OPPORTUNITIES:\n"
        for bet in opp['live_value'][:2]:
            edge_pct = bet['edge'] * 100
            details += f"   {bet['bet']} ({bet['odds']:+d}) - {edge_pct:+.1f}% edge\n"
    
    # Parlay potential
    parlay = opp['parlay_potential']
    details += f" Parlay Potential: {parlay['viability']} ({parlay['available_markets']} markets)\n"
    
    details += "\n"
    return details

def main():
    """Main execution function"""
    logger.info(" Analyzing live betting opportunities...")
    
    analyzer = LiveBettingAnalyzer()
    opportunities = analyzer.find_live_opportunities()
    
    logger.info(f" Found {len(opportunities)} live betting opportunities")
    
    # Generate comprehensive report
    report = format_live_opportunities_report(opportunities)
    print(report)
    
    # Save detailed analysis
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results = {
        'timestamp': timestamp,
        'analysis_time': datetime.now().isoformat(),
        'total_opportunities': len(opportunities),
        'live_opportunities': opportunities
    }
    
    results_file = analyzer.workspace_path / "logs" / f"live_betting_opportunities_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f" Analysis saved to: {results_file}")

if __name__ == "__main__":
    main()