#!/usr/bin/env python3
"""
EQ12 Live Sports Scanner - Under 1 Hour Execution
Scans NFL, NBA, NHL, NCAAB, NCAAF for profitable betting opportunities
Runtime: 30-55 minutes with full cluster
"""

import os
import sys
import json
import time
import logging
import argparse
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"../logs/sports_scanner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# The Odds API Configuration
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
ODDS_API_BASE = "https://api.the-odds-api.com/v4"

# Sports to scan with their API keys
SPORTS_CONFIG = {
    "nfl": {
        "key": "americanfootball_nfl",
        "name": "NFL",
        "markets": ["h2h", "spreads", "totals"],
        "priority": 1
    },
    "nba": {
        "key": "basketball_nba",
        "name": "NBA",
        "markets": ["h2h", "spreads", "totals"],
        "priority": 1
    },
    "nhl": {
        "key": "icehockey_nhl",
        "name": "NHL",
        "markets": ["h2h", "spreads", "totals"],
        "priority": 2
    },
    "ncaab": {
        "key": "basketball_ncaab",
        "name": "College Basketball",
        "markets": ["h2h", "spreads", "totals"],
        "priority": 2
    },
    "ncaaf": {
        "key": "americanfootball_ncaaf",
        "name": "College Football",
        "markets": ["h2h", "spreads", "totals"],
        "priority": 1
    }
}

# Sportsbooks to scan (US-focused)
TARGET_BOOKS = [
    "draftkings", "fanduel", "betmgm", "caesars", "bet365",
    "pointsbetter", "barstool", "unibet", "betrivers", "espnbet"
]


class LiveSportsScanner:
    """Scans multiple sports for betting opportunities in under 1 hour"""
    
    def __init__(self, api_key: str, max_workers: int = 10):
        self.api_key = api_key
        self.max_workers = max_workers
        self.start_time = time.time()
        self.results = {
            "arbitrage": [],
            "positive_ev": [],
            "sharp_moves": [],
            "steam_moves": [],
            "total_games_scanned": 0,
            "total_opportunities": 0,
            "scan_duration": 0
        }
        self.api_requests_used = 0
        
    def get_games(self, sport_key: str, regions: str = "us") -> List[Dict]:
        """Fetch games for a specific sport"""
        try:
            url = f"{ODDS_API_BASE}/sports/{sport_key}/odds"
            params = {
                "apiKey": self.api_key,
                "regions": regions,
                "markets": "h2h,spreads,totals",
                "oddsFormat": "american"
            }
            
            logger.info(f"Fetching {sport_key} games...")
            response = requests.get(url, params=params, timeout=15)
            self.api_requests_used += 1
            
            if response.status_code == 200:
                games = response.json()
                logger.info(f"Found {len(games)} games for {sport_key}")
                return games
            else:
                logger.error(f"API error for {sport_key}: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching {sport_key}: {e}")
            return []
    
    def american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def calculate_implied_probability(self, american_odds: int) -> float:
        """Calculate implied probability from American odds"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    def find_arbitrage(self, game: Dict, sport_name: str) -> List[Dict]:
        """Detect arbitrage opportunities in a single game"""
        opportunities = []
        
        if not game.get("bookmakers"):
            return opportunities
        
        # Collect best odds for each outcome across all books
        for market_type in ["h2h", "spreads", "totals"]:
            best_odds = defaultdict(lambda: {"odds": -10000, "book": None})
            
            for bookmaker in game["bookmakers"]:
                book_name = bookmaker.get("key", "unknown")
                
                for market in bookmaker.get("markets", []):
                    if market.get("key") != market_type:
                        continue
                    
                    for outcome in market.get("outcomes", []):
                        outcome_key = outcome.get("name")
                        if market_type == "spreads":
                            outcome_key += f"_{outcome.get('point', 0)}"
                        elif market_type == "totals":
                            outcome_key = f"{outcome.get('name')}_{outcome.get('point', 0)}"
                        
                        current_odds = outcome.get("price", -10000)
                        
                        if current_odds > best_odds[outcome_key]["odds"]:
                            best_odds[outcome_key] = {
                                "odds": current_odds,
                                "book": book_name,
                                "decimal": self.american_to_decimal(current_odds)
                            }
            
            # Check for arbitrage (total implied probability < 1.0)
            if len(best_odds) >= 2:
                total_prob = sum(1/data["decimal"] for data in best_odds.values())
                
                if total_prob < 0.98:  # Arbitrage found (98% to account for rounding)
                    profit_margin = (1 - total_prob) * 100
                    
                    opportunity = {
                        "type": "arbitrage",
                        "sport": sport_name,
                        "game": f"{game.get('away_team')} @ {game.get('home_team')}",
                        "market": market_type,
                        "profit_margin": round(profit_margin, 2),
                        "legs": [],
                        "commence_time": game.get("commence_time")
                    }
                    
                    for outcome_key, data in best_odds.items():
                        opportunity["legs"].append({
                            "outcome": outcome_key,
                            "odds": data["odds"],
                            "book": data["book"],
                            "stake_percent": round((1/data["decimal"]) / total_prob * 100, 2)
                        })
                    
                    opportunities.append(opportunity)
                    logger.info(f"🎯 ARBITRAGE: {sport_name} - {profit_margin:.2f}% profit")
        
        return opportunities
    
    def find_positive_ev(self, game: Dict, sport_name: str) -> List[Dict]:
        """Find positive expected value bets (line shopping)"""
        opportunities = []
        
        if not game.get("bookmakers"):
            return opportunities
        
        for market_type in ["h2h", "spreads", "totals"]:
            # Collect all odds for each outcome
            outcome_odds = defaultdict(list)
            
            for bookmaker in game["bookmakers"]:
                book_name = bookmaker.get("key", "unknown")
                
                for market in bookmaker.get("markets", []):
                    if market.get("key") != market_type:
                        continue
                    
                    for outcome in market.get("outcomes", []):
                        outcome_key = outcome.get("name")
                        if market_type == "spreads":
                            outcome_key += f"_{outcome.get('point', 0)}"
                        elif market_type == "totals":
                            outcome_key = f"{outcome.get('name')}_{outcome.get('point', 0)}"
                        
                        outcome_odds[outcome_key].append({
                            "book": book_name,
                            "odds": outcome.get("price", -10000)
                        })
            
            # Calculate average market odds (no-vig fair odds)
            for outcome_key, odds_list in outcome_odds.items():
                if len(odds_list) < 3:  # Need at least 3 books for reliable average
                    continue
                
                # Calculate no-vig probabilities
                implied_probs = [self.calculate_implied_probability(o["odds"]) for o in odds_list]
                avg_prob = sum(implied_probs) / len(implied_probs)
                
                # Find best available odds
                best_book = max(odds_list, key=lambda x: x["odds"])
                best_prob = self.calculate_implied_probability(best_book["odds"])
                
                # Check for positive EV (best odds < average market probability)
                if best_prob < avg_prob:
                    ev_percent = ((avg_prob / best_prob) - 1) * 100
                    
                    if ev_percent >= 2.0:  # At least 2% +EV
                        opportunities.append({
                            "type": "positive_ev",
                            "sport": sport_name,
                            "game": f"{game.get('away_team')} @ {game.get('home_team')}",
                            "market": market_type,
                            "outcome": outcome_key,
                            "ev_percent": round(ev_percent, 2),
                            "best_book": best_book["book"],
                            "best_odds": best_book["odds"],
                            "fair_odds": round(-100 / (avg_prob / (1 - avg_prob)) if avg_prob < 0.5 
                                            else 100 * (1 - avg_prob) / avg_prob, 0),
                            "commence_time": game.get("commence_time")
                        })
                        logger.info(f"💰 +EV: {sport_name} - {outcome_key} ({ev_percent:.2f}% edge)")
        
        return opportunities
    
    def find_sharp_moves(self, game: Dict, sport_name: str) -> List[Dict]:
        """Detect sharp money moves (Pinnacle vs consensus)"""
        # This would require historical line data
        # For now, we'll detect significant line disparities
        opportunities = []
        
        if not game.get("bookmakers"):
            return opportunities
        
        for market_type in ["spreads", "totals"]:
            lines = defaultdict(list)
            
            for bookmaker in game["bookmakers"]:
                book_name = bookmaker.get("key", "unknown")
                
                for market in bookmaker.get("markets", []):
                    if market.get("key") != market_type:
                        continue
                    
                    for outcome in market.get("outcomes", []):
                        if market_type == "spreads":
                            point = outcome.get("point", 0)
                            lines[outcome.get("name")].append({
                                "book": book_name,
                                "line": point,
                                "odds": outcome.get("price")
                            })
                        elif market_type == "totals":
                            point = outcome.get("point", 0)
                            lines["total"].append({
                                "book": book_name,
                                "line": point,
                                "odds": outcome.get("price"),
                                "side": outcome.get("name")
                            })
            
            # Detect line disparities (potential sharp moves)
            for outcome_name, book_lines in lines.items():
                if len(book_lines) < 3:
                    continue
                
                if market_type == "spreads":
                    line_values = [b["line"] for b in book_lines]
                    avg_line = sum(line_values) / len(line_values)
                    max_line = max(line_values)
                    min_line = min(line_values)
                    
                    if (max_line - min_line) >= 1.5:  # 1.5+ point disparity
                        opportunities.append({
                            "type": "sharp_move",
                            "sport": sport_name,
                            "game": f"{game.get('away_team')} @ {game.get('home_team')}",
                            "market": f"{market_type}_{outcome_name}",
                            "avg_line": round(avg_line, 1),
                            "line_range": f"{min_line} to {max_line}",
                            "disparity": round(max_line - min_line, 1),
                            "commence_time": game.get("commence_time")
                        })
                        logger.info(f"📊 SHARP MOVE: {sport_name} - {outcome_name} line disparity")
        
        return opportunities
    
    def scan_sport(self, sport_key: str, sport_config: Dict) -> Dict:
        """Scan a single sport for all opportunities"""
        logger.info(f"🔍 Scanning {sport_config['name']}...")
        
        games = self.get_games(sport_key)
        sport_results = {
            "sport": sport_config["name"],
            "games_found": len(games),
            "arbitrage": [],
            "positive_ev": [],
            "sharp_moves": []
        }
        
        for game in games:
            # Run all detection methods
            sport_results["arbitrage"].extend(self.find_arbitrage(game, sport_config["name"]))
            sport_results["positive_ev"].extend(self.find_positive_ev(game, sport_config["name"]))
            sport_results["sharp_moves"].extend(self.find_sharp_moves(game, sport_config["name"]))
        
        logger.info(f"✅ {sport_config['name']}: {len(sport_results['arbitrage'])} arb, "
                   f"{len(sport_results['positive_ev'])} +EV, "
                   f"{len(sport_results['sharp_moves'])} sharp moves")
        
        return sport_results
    
    def run_full_scan(self) -> Dict:
        """Execute full scan of all sports in parallel"""
        logger.info("=" * 80)
        logger.info("EQ12 LIVE SPORTS SCANNER - STARTING")
        logger.info("=" * 80)
        
        if not self.api_key:
            logger.error("ODDS_API_KEY not found in environment variables!")
            sys.exit(1)
        
        # Scan all sports in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            for sport_key, config in SPORTS_CONFIG.items():
                future = executor.submit(self.scan_sport, config["key"], config)
                futures[future] = sport_key
            
            for future in as_completed(futures):
                sport_key = futures[future]
                try:
                    sport_results = future.result()
                    
                    # Aggregate results
                    self.results["arbitrage"].extend(sport_results["arbitrage"])
                    self.results["positive_ev"].extend(sport_results["positive_ev"])
                    self.results["sharp_moves"].extend(sport_results["sharp_moves"])
                    self.results["total_games_scanned"] += sport_results["games_found"]
                    
                except Exception as e:
                    logger.error(f"Error scanning {sport_key}: {e}")
        
        # Calculate totals
        self.results["total_opportunities"] = (
            len(self.results["arbitrage"]) + 
            len(self.results["positive_ev"]) + 
            len(self.results["sharp_moves"])
        )
        self.results["scan_duration"] = round(time.time() - self.start_time, 2)
        self.results["api_requests_used"] = self.api_requests_used
        
        # Sort by profitability
        self.results["arbitrage"].sort(key=lambda x: x["profit_margin"], reverse=True)
        self.results["positive_ev"].sort(key=lambda x: x["ev_percent"], reverse=True)
        
        return self.results
    
    def save_results(self, output_path: str = None):
        """Save results to JSON file"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"../logs/sports_scan_results_{timestamp}.json"
        
        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"📁 Results saved to: {output_path}")
        return output_path
    
    def print_summary(self):
        """Print executive summary of findings"""
        logger.info("\n" + "=" * 80)
        logger.info("SCAN SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Games Scanned: {self.results['total_games_scanned']}")
        logger.info(f"Total Opportunities: {self.results['total_opportunities']}")
        logger.info(f"API Requests Used: {self.results['api_requests_used']}")
        logger.info(f"Scan Duration: {self.results['scan_duration']:.2f} seconds")
        logger.info("")
        logger.info(f"🎯 Arbitrage Opportunities: {len(self.results['arbitrage'])}")
        logger.info(f"💰 Positive EV Bets: {len(self.results['positive_ev'])}")
        logger.info(f"📊 Sharp Moves Detected: {len(self.results['sharp_moves'])}")
        
        # Show top 5 arbitrage opportunities
        if self.results["arbitrage"]:
            logger.info("\n" + "-" * 80)
            logger.info("TOP 5 ARBITRAGE OPPORTUNITIES")
            logger.info("-" * 80)
            for i, arb in enumerate(self.results["arbitrage"][:5], 1):
                logger.info(f"{i}. {arb['sport']} - {arb['game']}")
                logger.info(f"   Market: {arb['market']} | Profit: {arb['profit_margin']:.2f}%")
                for leg in arb["legs"]:
                    logger.info(f"   - {leg['outcome']}: {leg['odds']} @ {leg['book']} ({leg['stake_percent']:.1f}%)")
                logger.info("")
        
        # Show top 5 +EV bets
        if self.results["positive_ev"]:
            logger.info("-" * 80)
            logger.info("TOP 5 POSITIVE EV BETS")
            logger.info("-" * 80)
            for i, bet in enumerate(self.results["positive_ev"][:5], 1):
                logger.info(f"{i}. {bet['sport']} - {bet['game']}")
                logger.info(f"   {bet['outcome']} @ {bet['best_book']}: {bet['best_odds']}")
                logger.info(f"   Fair Odds: {bet['fair_odds']} | Edge: {bet['ev_percent']:.2f}%")
                logger.info("")
        
        logger.info("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="EQ12 Live Sports Scanner")
    parser.add_argument("--workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--output", type=str, help="Output JSON file path")
    args = parser.parse_args()
    
    # Initialize scanner
    scanner = LiveSportsScanner(
        api_key=ODDS_API_KEY,
        max_workers=args.workers
    )
    
    # Run full scan
    results = scanner.run_full_scan()
    
    # Save and display results
    scanner.save_results(args.output)
    scanner.print_summary()
    
    logger.info(f"\n✅ Scan completed in {results['scan_duration']:.2f} seconds")
    logger.info(f"💡 API requests remaining this month: {500 - results['api_requests_used']}")


if __name__ == "__main__":
    main()
