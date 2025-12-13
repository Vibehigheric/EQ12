#!/usr/bin/env python3
"""
EQ12 Sports Betting Scanner - DEMO MODE
Shows what you CAN do with working API key in under 1 hour
Uses simulated realistic data for demonstration
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DemoSportsScanner:
    """Demo version showing capabilities with simulated data"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = {
            "arbitrage": [],
            "positive_ev": [],
            "sharp_moves": [],
            "steam_moves": [],
            "total_games_scanned": 0,
            "total_opportunities": 0
        }
    
    def generate_realistic_nfl_games(self) -> List[Dict]:
        """Generate realistic NFL games with odds from multiple books"""
        games = [
            {
                "home_team": "Buffalo Bills",
                "away_team": "Kansas City Chiefs",
                "commence_time": (datetime.now() + timedelta(days=2)).isoformat(),
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Buffalo Bills", "price": -115},
                                    {"name": "Kansas City Chiefs", "price": -105}
                                ]
                            },
                            {
                                "key": "spreads",
                                "outcomes": [
                                    {"name": "Buffalo Bills", "price": -110, "point": -2.5},
                                    {"name": "Kansas City Chiefs", "price": -110, "point": 2.5}
                                ]
                            },
                            {
                                "key": "totals",
                                "outcomes": [
                                    {"name": "Over", "price": -110, "point": 50.5},
                                    {"name": "Under", "price": -110, "point": 50.5}
                                ]
                            }
                        ]
                    },
                    {
                        "key": "fanduel",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Buffalo Bills", "price": -118},
                                    {"name": "Kansas City Chiefs", "price": -102}
                                ]
                            },
                            {
                                "key": "spreads",
                                "outcomes": [
                                    {"name": "Buffalo Bills", "price": -112, "point": -2.5},
                                    {"name": "Kansas City Chiefs", "price": -108, "point": 2.5}
                                ]
                            },
                            {
                                "key": "totals",
                                "outcomes": [
                                    {"name": "Over", "price": -115, "point": 50.5},
                                    {"name": "Under", "price": -105, "point": 50.5}
                                ]
                            }
                        ]
                    },
                    {
                        "key": "betmgm",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Buffalo Bills", "price": -110},
                                    {"name": "Kansas City Chiefs", "price": -110}
                                ]
                            },
                            {
                                "key": "spreads",
                                "outcomes": [
                                    {"name": "Buffalo Bills", "price": -108, "point": -2.0},  # Sharp move - different line
                                    {"name": "Kansas City Chiefs", "price": -112, "point": 2.0}
                                ]
                            },
                            {
                                "key": "totals",
                                "outcomes": [
                                    {"name": "Over", "price": -108, "point": 51.0},  # Different total
                                    {"name": "Under", "price": -112, "point": 51.0}
                                ]
                            }
                        ]
                    },
                    {
                        "key": "caesars",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Buffalo Bills", "price": -120},
                                    {"name": "Kansas City Chiefs", "price": +100}
                                ]
                            },
                            {
                                "key": "spreads",
                                "outcomes": [
                                    {"name": "Buffalo Bills", "price": -115, "point": -2.5},
                                    {"name": "Kansas City Chiefs", "price": -105, "point": 2.5}
                                ]
                            },
                            {
                                "key": "totals",
                                "outcomes": [
                                    {"name": "Over", "price": -112, "point": 50.5},
                                    {"name": "Under", "price": -108, "point": 50.5}
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "home_team": "Detroit Lions",
                "away_team": "Green Bay Packers",
                "commence_time": (datetime.now() + timedelta(days=1)).isoformat(),
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Detroit Lions", "price": -145},
                                    {"name": "Green Bay Packers", "price": +125}
                                ]
                            },
                            {
                                "key": "spreads",
                                "outcomes": [
                                    {"name": "Detroit Lions", "price": -110, "point": -3.5},
                                    {"name": "Green Bay Packers", "price": -110, "point": 3.5}
                                ]
                            }
                        ]
                    },
                    {
                        "key": "fanduel",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Detroit Lions", "price": -140},
                                    {"name": "Green Bay Packers", "price": +120}
                                ]
                            },
                            {
                                "key": "spreads",
                                "outcomes": [
                                    {"name": "Detroit Lions", "price": -112, "point": -3.5},
                                    {"name": "Green Bay Packers", "price": -108, "point": 3.5}
                                ]
                            }
                        ]
                    },
                    {
                        "key": "betmgm",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Detroit Lions", "price": -150},
                                    {"name": "Green Bay Packers", "price": +130}  # Better underdog odds
                                ]
                            }
                        ]
                    }
                ]
            },
            # Add arbitrage opportunity game
            {
                "home_team": "Miami Dolphins",
                "away_team": "New York Jets",
                "commence_time": (datetime.now() + timedelta(days=3)).isoformat(),
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Miami Dolphins", "price": +150},  # Great underdog odds
                                    {"name": "New York Jets", "price": -165}
                                ]
                            }
                        ]
                    },
                    {
                        "key": "fanduel",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Miami Dolphins", "price": +140},
                                    {"name": "New York Jets", "price": -155}  # Better favorite odds
                                ]
                            }
                        ]
                    },
                    {
                        "key": "betmgm",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Miami Dolphins", "price": +145},
                                    {"name": "New York Jets", "price": -150}  # Even better favorite
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
        return games
    
    def generate_realistic_nba_games(self) -> List[Dict]:
        """Generate realistic NBA games"""
        games = [
            {
                "home_team": "Los Angeles Lakers",
                "away_team": "Boston Celtics",
                "commence_time": (datetime.now() + timedelta(hours=8)).isoformat(),
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Los Angeles Lakers", "price": +110},
                                    {"name": "Boston Celtics", "price": -130}
                                ]
                            },
                            {
                                "key": "totals",
                                "outcomes": [
                                    {"name": "Over", "price": -108, "point": 228.5},
                                    {"name": "Under", "price": -112, "point": 228.5}
                                ]
                            }
                        ]
                    },
                    {
                        "key": "fanduel",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Los Angeles Lakers", "price": +115},  # Better dog odds
                                    {"name": "Boston Celtics", "price": -135}
                                ]
                            },
                            {
                                "key": "totals",
                                "outcomes": [
                                    {"name": "Over", "price": -105, "point": 228.5},  # Sharp move to Over
                                    {"name": "Under", "price": -115, "point": 228.5}
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "home_team": "Milwaukee Bucks",
                "away_team": "Philadelphia 76ers",
                "commence_time": (datetime.now() + timedelta(hours=10)).isoformat(),
                "bookmakers": [
                    {
                        "key": "draftkings",
                        "markets": [
                            {
                                "key": "spreads",
                                "outcomes": [
                                    {"name": "Milwaukee Bucks", "price": -110, "point": -5.5},
                                    {"name": "Philadelphia 76ers", "price": -110, "point": 5.5}
                                ]
                            }
                        ]
                    },
                    {
                        "key": "betmgm",
                        "markets": [
                            {
                                "key": "spreads",
                                "outcomes": [
                                    {"name": "Milwaukee Bucks", "price": -108, "point": -4.5},  # Line move
                                    {"name": "Philadelphia 76ers", "price": -112, "point": 4.5}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
        return games
    
    def american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def calculate_implied_probability(self, american_odds: int) -> float:
        """Calculate implied probability"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    def find_opportunities(self, games: List[Dict], sport_name: str):
        """Find arbitrage and +EV opportunities"""
        
        for game in games:
            game_str = f"{game['away_team']} @ {game['home_team']}"
            
            # Check for arbitrage
            for market_type in ["h2h", "spreads", "totals"]:
                best_odds = {}
                
                for bookmaker in game.get("bookmakers", []):
                    book_name = bookmaker.get("key")
                    
                    for market in bookmaker.get("markets", []):
                        if market.get("key") != market_type:
                            continue
                        
                        for outcome in market.get("outcomes", []):
                            outcome_key = outcome.get("name")
                            if market_type in ["spreads", "totals"]:
                                outcome_key += f"_{outcome.get('point', 0)}"
                            
                            current_odds = outcome.get("price")
                            
                            if outcome_key not in best_odds or current_odds > best_odds[outcome_key]["odds"]:
                                best_odds[outcome_key] = {
                                    "odds": current_odds,
                                    "book": book_name,
                                    "decimal": self.american_to_decimal(current_odds)
                                }
                
                # Check for arbitrage
                if len(best_odds) >= 2:
                    total_prob = sum(1/data["decimal"] for data in best_odds.values())
                    
                    if total_prob < 0.98:  # Arbitrage found
                        profit_margin = (1 - total_prob) * 100
                        
                        self.results["arbitrage"].append({
                            "type": "arbitrage",
                            "sport": sport_name,
                            "game": game_str,
                            "market": market_type,
                            "profit_margin": round(profit_margin, 2),
                            "legs": [
                                {
                                    "outcome": k,
                                    "odds": v["odds"],
                                    "book": v["book"],
                                    "stake_percent": round((1/v["decimal"]) / total_prob * 100, 2)
                                }
                                for k, v in best_odds.items()
                            ]
                        })
                        logger.info(f"🎯 ARBITRAGE: {sport_name} {game_str} - {profit_margin:.2f}% profit")
                
                # Check for +EV (positive expected value)
                if len(best_odds) >= 2:
                    for outcome_key, data in best_odds.items():
                        # Simulate market average (for demo purposes)
                        market_avg_prob = self.calculate_implied_probability(data["odds"]) * 1.05
                        best_prob = self.calculate_implied_probability(data["odds"])
                        
                        if best_prob < market_avg_prob * 0.95:  # 5% or more edge
                            ev_percent = ((market_avg_prob / best_prob) - 1) * 100
                            
                            if ev_percent >= 3.0:
                                self.results["positive_ev"].append({
                                    "type": "positive_ev",
                                    "sport": sport_name,
                                    "game": game_str,
                                    "outcome": outcome_key,
                                    "ev_percent": round(ev_percent, 2),
                                    "best_book": data["book"],
                                    "best_odds": data["odds"]
                                })
                                logger.info(f"💰 +EV: {sport_name} {game_str} - {outcome_key} ({ev_percent:.2f}% edge)")
            
            # Check for sharp moves (line disparities)
            for market_type in ["spreads", "totals"]:
                lines = []
                
                for bookmaker in game.get("bookmakers", []):
                    for market in bookmaker.get("markets", []):
                        if market.get("key") != market_type:
                            continue
                        
                        for outcome in market.get("outcomes", []):
                            if "point" in outcome:
                                lines.append(outcome.get("point"))
                
                if len(lines) >= 2:
                    line_range = max(lines) - min(lines)
                    
                    if line_range >= 1.0:  # 1+ point disparity
                        self.results["sharp_moves"].append({
                            "type": "sharp_move",
                            "sport": sport_name,
                            "game": game_str,
                            "market": market_type,
                            "line_range": f"{min(lines)} to {max(lines)}",
                            "disparity": round(line_range, 1)
                        })
                        logger.info(f"📊 SHARP MOVE: {sport_name} {game_str} - {market_type} disparity")
    
    def run_demo_scan(self):
        """Run demonstration scan"""
        logger.info("=" * 80)
        logger.info("EQ12 SPORTS BETTING SCANNER - DEMO MODE")
        logger.info("Simulating what you CAN do with active ODDS_API_KEY")
        logger.info("=" * 80)
        
        # Simulate NFL scan
        logger.info("\n🏈 Scanning NFL...")
        time.sleep(0.5)  # Simulate API delay
        nfl_games = self.generate_realistic_nfl_games()
        self.find_opportunities(nfl_games, "NFL")
        self.results["total_games_scanned"] += len(nfl_games)
        
        # Simulate NBA scan
        logger.info("\n🏀 Scanning NBA...")
        time.sleep(0.5)
        nba_games = self.generate_realistic_nba_games()
        self.find_opportunities(nba_games, "NBA")
        self.results["total_games_scanned"] += len(nba_games)
        
        # Simulate other sports
        logger.info("\n🏒 Scanning NHL...")
        time.sleep(0.3)
        self.results["total_games_scanned"] += 4
        
        logger.info("\n🏀 Scanning College Basketball...")
        time.sleep(0.3)
        self.results["total_games_scanned"] += 8
        
        logger.info("\n🏈 Scanning College Football...")
        time.sleep(0.3)
        self.results["total_games_scanned"] += 6
        
        # Calculate totals
        self.results["total_opportunities"] = (
            len(self.results["arbitrage"]) +
            len(self.results["positive_ev"]) +
            len(self.results["sharp_moves"])
        )
        self.results["scan_duration"] = round(time.time() - self.start_time, 2)
        
        # Print summary
        self.print_summary()
        
        return self.results
    
    def print_summary(self):
        """Print results summary"""
        logger.info("\n" + "=" * 80)
        logger.info("DEMO SCAN RESULTS")
        logger.info("=" * 80)
        logger.info(f"Total Games Scanned: {self.results['total_games_scanned']}")
        logger.info(f"Total Opportunities Found: {self.results['total_opportunities']}")
        logger.info(f"Scan Duration: {self.results['scan_duration']:.2f} seconds")
        logger.info("")
        logger.info(f"🎯 Arbitrage Opportunities: {len(self.results['arbitrage'])}")
        logger.info(f"💰 Positive EV Bets: {len(self.results['positive_ev'])}")
        logger.info(f"📊 Sharp Moves Detected: {len(self.results['sharp_moves'])}")
        
        # Show arbitrage opportunities
        if self.results["arbitrage"]:
            logger.info("\n" + "-" * 80)
            logger.info("ARBITRAGE OPPORTUNITIES (GUARANTEED PROFIT)")
            logger.info("-" * 80)
            for arb in self.results["arbitrage"]:
                logger.info(f"\n{arb['sport']} - {arb['game']}")
                logger.info(f"Market: {arb['market']} | Profit: {arb['profit_margin']:.2f}%")
                logger.info("How to bet:")
                for leg in arb["legs"]:
                    logger.info(f"  - Bet {leg['stake_percent']:.1f}% on {leg['outcome']}: {leg['odds']} @ {leg['book']}")
                logger.info(f"  → Example with $1000: Guaranteed profit ${arb['profit_margin']*10:.2f}")
        
        # Show +EV bets
        if self.results["positive_ev"]:
            logger.info("\n" + "-" * 80)
            logger.info("POSITIVE EXPECTED VALUE BETS")
            logger.info("-" * 80)
            for bet in self.results["positive_ev"]:
                logger.info(f"\n{bet['sport']} - {bet['game']}")
                logger.info(f"Bet: {bet['outcome']} @ {bet['best_book']}: {bet['best_odds']}")
                logger.info(f"Edge: {bet['ev_percent']:.2f}% (Market is undervaluing this outcome)")
        
        # Show sharp moves
        if self.results["sharp_moves"]:
            logger.info("\n" + "-" * 80)
            logger.info("SHARP MONEY INDICATORS (Line Disparities)")
            logger.info("-" * 80)
            for move in self.results["sharp_moves"]:
                logger.info(f"\n{move['sport']} - {move['game']}")
                logger.info(f"{move['market']}: Line range {move['line_range']} ({move['disparity']} point disparity)")
                logger.info("→ Different books have different opinions - potential sharp action")
        
        logger.info("\n" + "=" * 80)
        logger.info("TO USE THIS FOR REAL:")
        logger.info("1. Get active ODDS_API_KEY from https://the-odds-api.com")
        logger.info("2. Sign up for free tier (500 requests/month)")
        logger.info("3. Set environment variable: setx ODDS_API_KEY \"your_key_here\"")
        logger.info("4. Run: python eq12_live_sports_scanner_1hour.py")
        logger.info("=" * 80)


if __name__ == "__main__":
    scanner = DemoSportsScanner()
    scanner.run_demo_scan()
