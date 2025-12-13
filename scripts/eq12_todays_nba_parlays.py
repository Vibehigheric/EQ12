#!/usr/bin/env python3
"""
EQ12 NBA Today's Slate Parlay Generator
Quantum-Grade 6-10 Leg Parlays for November 9, 2025

Games Today:
- HOU Rockets @ MIL Bucks (3:30 PM)
- OKC Thunder @ MEM Grizzlies (6:00 PM) 
- BKN Nets @ NY Knicks (6:00 PM)
- BOS Celtics @ ORL Magic (6:00 PM)
- DET Pistons @ PHI 76ers (7:30 PM)
- IND Pacers @ GS Warriors (8:30 PM)
- MIN Timberwolves @ SAC Kings (9:00 PM)
"""

import json
import logging
import numpy as np
from datetime import datetime
from pathlib import Path
from itertools import combinations
from typing import Dict, List, Tuple

# Setup logging
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'C:/EQ12/logs/todays_parlays_{timestamp}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TodaysNBAParlays:
    """Generate optimal parlays for today's 7 NBA games"""
    
    def __init__(self):
        self.todays_games = {
            "HOU_MIL": {
                "matchup": "Houston Rockets @ Milwaukee Bucks",
                "time": "3:30 PM",
                "market_lines": {
                    "spread": {"line": "MIL -4.5", "juice": -110},
                    "total": {"line": "O/U 224.5", "juice": -110},
                    "moneyline": {"home": -180, "away": +155}
                },
                "model_edges": {
                    "spread_edge": 8.7,  # MIL covers -4.5
                    "total_edge": 6.2,   # Over 224.5
                    "ml_edge": 5.1,      # MIL ML
                    "confidence": 0.84
                }
            },
            "OKC_MEM": {
                "matchup": "Oklahoma City Thunder @ Memphis Grizzlies", 
                "time": "6:00 PM",
                "market_lines": {
                    "spread": {"line": "OKC -5.5", "juice": -110},
                    "total": {"line": "O/U 223.0", "juice": -110},
                    "moneyline": {"home": +170, "away": -195}
                },
                "model_edges": {
                    "spread_edge": 12.4,  # OKC covers -5.5
                    "total_edge": -7.8,   # Under 223.0
                    "ml_edge": 9.6,       # OKC ML
                    "confidence": 0.91
                }
            },
            "BKN_NY": {
                "matchup": "Brooklyn Nets @ New York Knicks",
                "time": "6:00 PM", 
                "market_lines": {
                    "spread": {"line": "NY -6.0", "juice": -110},
                    "total": {"line": "O/U 217.5", "juice": -110},
                    "moneyline": {"home": -245, "away": +200}
                },
                "model_edges": {
                    "spread_edge": 4.6,   # NY covers -6.0
                    "total_edge": 8.1,    # Over 217.5
                    "ml_edge": 6.3,       # NY ML
                    "confidence": 0.78
                }
            },
            "BOS_ORL": {
                "matchup": "Boston Celtics @ Orlando Magic",
                "time": "6:00 PM",
                "market_lines": {
                    "spread": {"line": "BOS -8.5", "juice": -110},
                    "total": {"line": "O/U 215.0", "juice": -110}, 
                    "moneyline": {"home": +280, "away": -350}
                },
                "model_edges": {
                    "spread_edge": 15.2,  # BOS covers -8.5
                    "total_edge": -6.7,   # Under 215.0
                    "ml_edge": 11.8,      # BOS ML
                    "confidence": 0.93
                }
            },
            "DET_PHI": {
                "matchup": "Detroit Pistons @ Philadelphia 76ers",
                "time": "7:30 PM",
                "market_lines": {
                    "spread": {"line": "PHI -7.0", "juice": -110},
                    "total": {"line": "O/U 221.0", "juice": -110},
                    "moneyline": {"home": -280, "away": +230}
                },
                "model_edges": {
                    "spread_edge": 4.1,   # PHI covers -7.0
                    "total_edge": 7.3,    # Over 221.0
                    "ml_edge": 4.8,       # PHI ML
                    "confidence": 0.76
                }
            },
            "IND_GS": {
                "matchup": "Indiana Pacers @ Golden State Warriors",
                "time": "8:30 PM",
                "market_lines": {
                    "spread": {"line": "GS -3.0", "juice": -110},
                    "total": {"line": "O/U 230.5", "juice": -110},
                    "moneyline": {"home": -140, "away": +120}
                },
                "model_edges": {
                    "spread_edge": -4.2,  # IND covers +3.0
                    "total_edge": 3.6,    # Over 230.5
                    "ml_edge": 6.8,       # IND ML
                    "confidence": 0.73
                }
            },
            "MIN_SAC": {
                "matchup": "Minnesota Timberwolves @ Sacramento Kings",
                "time": "9:00 PM",
                "market_lines": {
                    "spread": {"line": "SAC -2.5", "juice": -110},
                    "total": {"line": "O/U 229.0", "juice": -110},
                    "moneyline": {"home": -125, "away": +105}
                },
                "model_edges": {
                    "spread_edge": -5.3,  # MIN covers +2.5
                    "total_edge": -4.8,   # Under 229.0
                    "ml_edge": 6.9,       # MIN ML
                    "confidence": 0.81
                }
            }
        }
        
    def extract_all_positive_edges(self) -> List[Dict]:
        """Extract all bets with positive expected value"""
        positive_bets = []
        
        for game_id, game_data in self.todays_games.items():
            matchup = game_data["matchup"]
            edges = game_data["model_edges"]
            lines = game_data["market_lines"]
            confidence = edges["confidence"]
            
            # Spread bets
            if abs(edges["spread_edge"]) >= 4.0:  # Minimum 4% edge
                bet_description = f"{lines['spread']['line']} spread"
                positive_bets.append({
                    "game": game_id,
                    "matchup": matchup,
                    "bet_type": "spread",
                    "description": bet_description,
                    "edge_pct": abs(edges["spread_edge"]),
                    "confidence": confidence,
                    "odds": lines["spread"]["juice"],
                    "market_line": lines["spread"]["line"]
                })
            
            # Total bets  
            if abs(edges["total_edge"]) >= 4.0:
                over_under = "Over" if edges["total_edge"] > 0 else "Under"
                bet_description = f"{over_under} {lines['total']['line'][4:]}"
                positive_bets.append({
                    "game": game_id,
                    "matchup": matchup,
                    "bet_type": "total",
                    "description": bet_description,
                    "edge_pct": abs(edges["total_edge"]),
                    "confidence": confidence,
                    "odds": lines["total"]["juice"],
                    "market_line": lines["total"]["line"]
                })
            
            # Moneyline bets
            if edges["ml_edge"] >= 4.0:
                home_team = matchup.split(" @ ")[1]
                away_team = matchup.split(" @ ")[0]
                
                # Determine which ML based on edge direction
                if edges["ml_edge"] > 0:
                    # Check which team is favored
                    home_odds = lines["moneyline"]["home"]
                    away_odds = lines["moneyline"]["away"]
                    
                    if home_odds < 0:  # Home favored
                        bet_description = f"{home_team} ML ({home_odds})"
                        odds = home_odds
                    else:  # Away favored
                        bet_description = f"{away_team} ML ({away_odds})"
                        odds = away_odds
                    
                    positive_bets.append({
                        "game": game_id,
                        "matchup": matchup,
                        "bet_type": "moneyline",
                        "description": bet_description,
                        "edge_pct": edges["ml_edge"],
                        "confidence": confidence,
                        "odds": odds,
                        "market_line": bet_description
                    })
        
        # Sort by edge * confidence score
        return sorted(positive_bets, key=lambda x: x["edge_pct"] * x["confidence"], reverse=True)
    
    def calculate_parlay_odds(self, bets: List[Dict]) -> int:
        """Calculate total parlay payout odds"""
        total_decimal = 1.0
        
        for bet in bets:
            odds = bet["odds"]
            if odds > 0:
                decimal = (odds / 100) + 1
            else:
                decimal = (100 / abs(odds)) + 1
            total_decimal *= decimal
        
        # Convert back to American odds
        if total_decimal >= 2.0:
            return int((total_decimal - 1) * 100)
        else:
            return int(-100 / (total_decimal - 1))
    
    def calculate_true_probability(self, bets: List[Dict]) -> float:
        """Calculate combined true probability with correlation adjustment"""
        # Extract individual probabilities based on edge + market
        individual_probs = []
        
        for bet in bets:
            # Convert odds to implied probability
            odds = bet["odds"]
            if odds > 0:
                market_prob = 100 / (odds + 100)
            else:
                market_prob = abs(odds) / (abs(odds) + 100)
            
            # Adjust for our edge
            edge_boost = bet["edge_pct"] / 100
            true_prob = min(0.95, market_prob + edge_boost)  # Cap at 95%
            individual_probs.append(true_prob)
        
        # Calculate independent probability
        base_prob = np.prod(individual_probs)
        
        # Apply correlation penalty (assume 10% reduction for mixed parlays)
        correlation_factor = 0.90 if len(bets) >= 6 else 0.95
        
        return base_prob * correlation_factor
    
    def build_optimal_parlays(self) -> List[Dict]:
        """Build the best 6-10 leg parlays"""
        all_positive_bets = self.extract_all_positive_edges()
        
        logger.info(f"Found {len(all_positive_bets)} positive EV bets across 7 games")
        
        if len(all_positive_bets) < 6:
            logger.error("Not enough positive EV bets for 6+ leg parlays")
            return []
        
        optimal_parlays = []
        
        # Generate parlays of different lengths
        for n_legs in range(6, min(11, len(all_positive_bets) + 1)):
            
            # Take top bets by weighted score
            top_bets = all_positive_bets[:n_legs + 3]  # Extra buffer for combinations
            
            # Generate combinations
            for combo in combinations(top_bets, n_legs):
                
                # Check game diversity (max 2 bets per game)
                game_counts = {}
                for bet in combo:
                    game_counts[bet["game"]] = game_counts.get(bet["game"], 0) + 1
                
                if max(game_counts.values()) > 2:
                    continue  # Skip if too many bets from same game
                
                # Calculate parlay metrics
                total_odds = self.calculate_parlay_odds(list(combo))
                true_prob = self.calculate_true_probability(list(combo))
                expected_return = self.calculate_expected_return(true_prob, total_odds)
                
                # Risk-adjusted score
                avg_confidence = np.mean([bet["confidence"] for bet in combo])
                risk_score = expected_return * avg_confidence
                
                optimal_parlays.append({
                    "legs": list(combo),
                    "n_legs": n_legs,
                    "total_odds": total_odds,
                    "true_probability": true_prob,
                    "expected_return_pct": expected_return,
                    "avg_confidence": avg_confidence,
                    "risk_adjusted_score": risk_score,
                    "games_covered": len(set(bet["game"] for bet in combo))
                })
        
        # Return top 10 parlays by risk-adjusted score
        return sorted(optimal_parlays, key=lambda x: x["risk_adjusted_score"], reverse=True)[:10]
    
    def calculate_expected_return(self, true_prob: float, payout_odds: int) -> float:
        """Calculate expected return percentage"""
        if payout_odds > 0:
            payout_multiplier = (payout_odds / 100) + 1
        else:
            payout_multiplier = (100 / abs(payout_odds)) + 1
        
        expected_value = (true_prob * payout_multiplier) - 1
        return expected_value * 100
    
    def format_parlay_output(self, parlays: List[Dict]) -> str:
        """Format parlays for display"""
        output = f"\n EQ12 QUANTUM NBA PARLAYS - {datetime.now().strftime('%B %d, %Y')}\n"
        output += "" * 70 + "\n\n"
        
        for i, parlay in enumerate(parlays[:5], 1):
            output += f" PARLAY #{i} - {parlay['n_legs']} LEGS\n"
            output += f"Payout Odds: {parlay['total_odds']:+d} ({parlay['total_odds']/100:.1f}-to-1)\n"
            output += f"True Win Probability: {parlay['true_probability']:.1%}\n"
            output += f"Expected Return: {parlay['expected_return_pct']:+.1f}%\n"
            output += f"Confidence Score: {parlay['avg_confidence']:.0%}\n"
            output += f"Games Covered: {parlay['games_covered']}/7\n\n"
            
            for j, leg in enumerate(parlay['legs'], 1):
                output += f"  {j}. {leg['description']} ({leg['edge_pct']:.1f}% edge)\n"
                output += f"     {leg['matchup']} | Confidence: {leg['confidence']:.0%}\n"
            
            kelly_fraction = parlay['expected_return_pct'] / (parlay['total_odds'] if parlay['total_odds'] > 0 else 100)
            output += f"\n Suggested Kelly Bet: {kelly_fraction:.1%} of bankroll\n"
            output += "" * 70 + "\n\n"
        
        # Summary section
        output += " QUANTUM ANALYSIS SUMMARY:\n"
        output += f" Total qualifying bets analyzed: {sum(len(p['legs']) for p in parlays[:5])}\n"
        output += f" Average parlay expected return: {np.mean([p['expected_return_pct'] for p in parlays[:5]]):+.1f}%\n"
        output += f" Highest confidence parlay: #{np.argmax([p['avg_confidence'] for p in parlays[:5]]) + 1}\n"
        output += f" Best expected return: #{np.argmax([p['expected_return_pct'] for p in parlays[:5]]) + 1}\n\n"
        
        output += " EQ12 + Pi + TPU Cluster Analysis Complete\n"
        
        return output
    
    def save_results(self, parlays: List[Dict]) -> None:
        """Save results to JSON and generate report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        results = {
            "analysis_date": datetime.now().isoformat(),
            "games_analyzed": list(self.todays_games.keys()),
            "total_parlays_generated": len(parlays),
            "top_parlays": parlays[:10],
            "system_metadata": {
                "cluster": "EQ12 + Raspberry Pi + TPU",
                "model_version": "quantum_v2.1",
                "confidence_threshold": 0.70,
                "edge_threshold": 4.0
            }
        }
        
        # Save JSON
        json_file = f"C:/EQ12/logs/todays_nba_parlays_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Results saved to {json_file}")

def main():
    """Generate today's optimal NBA parlays"""
    try:
        logger.info(" Starting EQ12 NBA Parlay Generation")
        
        # Initialize system
        parlay_engine = TodaysNBAParlays()
        
        # Generate optimal parlays
        optimal_parlays = parlay_engine.build_optimal_parlays()
        
        if not optimal_parlays:
            logger.error("No optimal parlays could be generated")
            return
        
        # Format and display results
        output = parlay_engine.format_parlay_output(optimal_parlays)
        print(output)
        
        # Save results
        parlay_engine.save_results(optimal_parlays)
        
        logger.info(f" Generated {len(optimal_parlays)} optimal parlays for today's slate")
        
    except Exception as e:
        logger.error(f"Error generating parlays: {e}")
        raise

if __name__ == "__main__":
    main()