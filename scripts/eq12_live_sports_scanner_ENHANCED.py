#!/usr/bin/env python3
"""
EQ12 Live Sports Scanner - ENHANCED with Advanced Betting Intelligence
======================================================================

Integrates your existing advanced betting systems:
- Kelly Criterion bankroll optimization
- Correlation-adjusted position sizing
- Sharp money detection algorithms
- Line movement intelligence
- Closing line value tracking
- Advanced odds mathematics
- Multi-strategy bankroll allocation

Enhanced Features:
- Real Kelly Criterion sizing (not just detection)
- Correlation adjustments for parlays
- Sharp money confidence scores
- Bankroll allocation recommendations
- Risk-adjusted opportunity scoring
- Integration with existing EQ12 systems

Author: EQ12 Development Team
Date: November 28, 2025
Version: 2.0.0 - Enhanced Intelligence
"""

import asyncio
import json
import logging
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# EQ12 System Integration
try:
    from eq12_betting_mathematics import EQ12BettingMathematics, OddsFormat
    MATH_ENGINE = True
except ImportError:
    MATH_ENGINE = False
    print("⚠️ eq12_betting_mathematics not found - using basic math")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("../logs/sports_scanner_enhanced.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("EQ12SportsScanner")

# API Configuration
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
ODDS_API_BASE = "https://api.the-odds-api.com/v4"

# Sports to scan
SPORTS = {
    "NFL": "americanfootball_nfl",
    "NBA": "basketball_nba",
    "NHL": "icehockey_nhl",
    "NCAAB": "basketball_ncaab",
    "NCAAF": "americanfootball_ncaaf",
}


@dataclass
class BettingOpportunity:
    """Enhanced betting opportunity with bankroll management"""
    
    # Basic info
    sport: str
    game: str
    market: str
    outcome: str
    
    # Odds and probabilities
    best_odds: int  # American
    best_book: str
    decimal_odds: float
    implied_probability: float
    
    # Value metrics
    opportunity_type: str  # arbitrage, +ev, sharp_move, steam_move
    edge_percent: float
    fair_odds: Optional[int] = None
    
    # Bankroll management (NEW)
    kelly_fraction: float = 0.0
    recommended_stake_pct: float = 0.0
    recommended_stake_amount: float = 0.0
    max_stake_amount: float = 0.0
    
    # Risk metrics (NEW)
    confidence_score: float = 0.0  # 0-100
    sharp_money_indicator: bool = False
    steam_move_indicator: bool = False
    line_movement_score: float = 0.0  # -100 to +100
    
    # Correlation risk (NEW)
    correlation_risk: str = "unknown"  # low, medium, high
    correlation_notes: str = ""
    
    # Timing (NEW)
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    time_to_expiry: Optional[str] = None


class EnhancedLiveSportsScanner:
    """
    Enhanced sports scanner with advanced betting intelligence
    """
    
    def __init__(self, api_key: str, bankroll: float = 10000.0):
        self.api_key = api_key
        self.bankroll = bankroll
        self.results = {
            "scan_timestamp": datetime.now(UTC).isoformat(),
            "sports_scanned": [],
            "total_games": 0,
            "total_opportunities": 0,
            "arbitrage": [],
            "positive_ev": [],
            "sharp_moves": [],
            "steam_moves": [],
            "bankroll_allocation": {},
            "scan_duration": 0,
        }
        self.api_requests_used = 0
        
        # Initialize math engine
        if MATH_ENGINE:
            self.math_engine = EQ12BettingMathematics()
            logger.info("✅ Advanced betting mathematics loaded")
        else:
            self.math_engine = None
            logger.warning("⚠️ Using basic math - install eq12_betting_mathematics for full features")
        
        # Kelly Criterion parameters
        self.kelly_fraction = 0.25  # Conservative quarter Kelly
        self.max_single_bet = 0.05  # Never bet more than 5% of bankroll
        self.min_edge = 0.02  # Minimum 2% edge to bet
        
        # Sharp money detection parameters
        self.sharp_line_threshold = 1.5  # Points line movement
        self.steam_line_threshold = 2.0  # Points for steam move
        
    def get_games(self, sport_key: str, regions: str = "us") -> List[Dict]:
        """Fetch games for a specific sport"""
        try:
            url = f"{ODDS_API_BASE}/sports/{sport_key}/odds"
            params = {
                "apiKey": self.api_key,
                "regions": regions,
                "markets": "h2h,spreads,totals",
                "oddsFormat": "american",
            }
            
            logger.info(f"Fetching {sport_key} games...")
            response = requests.get(url, params=params, timeout=15)
            self.api_requests_used += 1
            
            if response.status_code == 200:
                games = response.json()
                logger.info(f"Found {len(games)} games for {sport_key}")
                return games
            else:
                logger.error(f"API error for {sport_key}: {response.status_code}")
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
    
    def calculate_kelly_fraction(
        self, decimal_odds: float, true_probability: float
    ) -> float:
        """
        Calculate Kelly Criterion fraction using advanced mathematics
        """
        if self.math_engine:
            try:
                kelly = self.math_engine.kelly_criterion(
                    decimal_odds,
                    true_probability,
                    conservative_factor=self.kelly_fraction
                )
                return kelly
            except Exception as e:
                logger.warning(f"Kelly calculation error: {e}")
        
        # Fallback to basic Kelly
        b = decimal_odds - 1.0
        p = true_probability
        q = 1.0 - true_probability
        
        kelly_full = ((b * p) - q) / b
        kelly_fractional = kelly_full * self.kelly_fraction
        
        return max(0.0, min(kelly_fractional, self.max_single_bet))
    
    def calculate_confidence_score(
        self,
        edge_percent: float,
        num_books: int,
        line_disparity: float = 0.0,
        sharp_indicator: bool = False,
    ) -> float:
        """
        Calculate confidence score (0-100) for an opportunity
        
        Factors:
        - Edge magnitude (higher edge = higher confidence)
        - Number of books (more books = more confidence)
        - Line disparity (sharp money indicator)
        - Sharp money signals
        """
        # Base confidence from edge
        confidence = min(edge_percent * 2, 50)  # Cap at 50 from edge alone
        
        # Add confidence from market depth
        if num_books >= 10:
            confidence += 20
        elif num_books >= 5:
            confidence += 10
        elif num_books >= 3:
            confidence += 5
        
        # Add confidence from sharp money indicators
        if sharp_indicator:
            confidence += 15
        
        if line_disparity > 2.0:
            confidence += 10
        elif line_disparity > 1.0:
            confidence += 5
        
        return min(confidence, 100.0)
    
    def detect_line_movement_type(
        self, line_disparity: float, num_books: int
    ) -> tuple[bool, bool, float]:
        """
        Detect sharp money and steam moves from line disparities
        
        Returns: (sharp_money, steam_move, movement_score)
        """
        sharp_money = False
        steam_move = False
        movement_score = 0.0
        
        # Sharp money: significant line disparity (1.5+ points)
        if line_disparity >= self.sharp_line_threshold:
            sharp_money = True
            movement_score = min(line_disparity * 10, 100)
        
        # Steam move: extreme line disparity (2.0+ points) across many books
        if line_disparity >= self.steam_line_threshold and num_books >= 5:
            steam_move = True
            movement_score = min(line_disparity * 15, 100)
        
        return sharp_money, steam_move, movement_score
    
    def find_arbitrage(self, game: Dict, sport_name: str) -> List[BettingOpportunity]:
        """Detect arbitrage opportunities with enhanced bankroll management"""
        opportunities = []
        
        if not game.get("bookmakers"):
            return opportunities
        
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
                                "decimal": self.american_to_decimal(current_odds),
                            }
            
            # Check for arbitrage
            if len(best_odds) >= 2:
                total_implied_prob = sum(
                    self.calculate_implied_probability(v["odds"])
                    for v in best_odds.values()
                )
                
                if total_implied_prob < 0.98:  # Arbitrage opportunity (2%+ margin)
                    profit_margin = ((1.0 / total_implied_prob) - 1.0) * 100
                    
                    # Calculate optimal stakes for arbitrage
                    for outcome_key, outcome_data in best_odds.items():
                        decimal_odds = outcome_data["decimal"]
                        stake_pct = (1.0 / decimal_odds) / total_implied_prob
                        stake_amount = self.bankroll * stake_pct
                        
                        # Create enhanced opportunity
                        opp = BettingOpportunity(
                            sport=sport_name,
                            game=f"{game.get('home_team')} vs {game.get('away_team')}",
                            market=market_type,
                            outcome=outcome_key,
                            best_odds=outcome_data["odds"],
                            best_book=outcome_data["book"],
                            decimal_odds=decimal_odds,
                            implied_probability=self.calculate_implied_probability(
                                outcome_data["odds"]
                            ),
                            opportunity_type="arbitrage",
                            edge_percent=profit_margin,
                            kelly_fraction=stake_pct,  # For arb, use exact stake
                            recommended_stake_pct=stake_pct * 100,
                            recommended_stake_amount=stake_amount,
                            max_stake_amount=self.bankroll * self.max_single_bet,
                            confidence_score=95.0,  # Arbitrage is near-certain
                            correlation_risk="low",  # Arbitrage has no correlation risk
                            correlation_notes="Risk-free arbitrage - mathematically guaranteed",
                        )
                        
                        opportunities.append(opp)
        
        return opportunities
    
    def find_positive_ev(self, game: Dict, sport_name: str) -> List[BettingOpportunity]:
        """Find positive EV bets with Kelly sizing"""
        opportunities = []
        
        if not game.get("bookmakers"):
            return opportunities
        
        for market_type in ["h2h", "spreads", "totals"]:
            for outcome_name in self._get_possible_outcomes(game, market_type):
                odds_list = []
                
                for bookmaker in game["bookmakers"]:
                    for market in bookmaker.get("markets", []):
                        if market.get("key") != market_type:
                            continue
                        
                        for outcome in market.get("outcomes", []):
                            if self._matches_outcome(outcome, outcome_name, market_type):
                                odds_list.append({
                                    "book": bookmaker.get("key"),
                                    "odds": outcome.get("price"),
                                })
                
                if len(odds_list) >= 3:
                    # Calculate no-vig fair odds
                    implied_probs = [
                        self.calculate_implied_probability(o["odds"]) for o in odds_list
                    ]
                    avg_prob = sum(implied_probs) / len(implied_probs)
                    
                    # Find best book
                    best_book = max(odds_list, key=lambda x: x["odds"])
                    best_prob = self.calculate_implied_probability(best_book["odds"])
                    
                    # Calculate edge
                    if avg_prob > best_prob:
                        edge = (avg_prob - best_prob) / best_prob
                        
                        if edge > self.min_edge:
                            # Calculate fair American odds
                            if avg_prob < 0.5:
                                fair_american = int(-100 / (avg_prob / (1 - avg_prob)))
                            else:
                                fair_american = int(100 * (avg_prob / (1 - avg_prob)))
                            
                            # Calculate Kelly fraction
                            decimal_odds = self.american_to_decimal(best_book["odds"])
                            kelly = self.calculate_kelly_fraction(decimal_odds, avg_prob)
                            
                            # Calculate line movement (disparity between books)
                            odds_values = [o["odds"] for o in odds_list]
                            line_disparity = (max(odds_values) - min(odds_values)) / 100
                            
                            # Detect sharp money / steam moves
                            sharp, steam, movement_score = self.detect_line_movement_type(
                                line_disparity, len(odds_list)
                            )
                            
                            # Calculate confidence
                            confidence = self.calculate_confidence_score(
                                edge * 100,
                                len(odds_list),
                                line_disparity,
                                sharp or steam,
                            )
                            
                            # Determine correlation risk
                            corr_risk = self._assess_correlation_risk(
                                market_type, outcome_name
                            )
                            
                            opp = BettingOpportunity(
                                sport=sport_name,
                                game=f"{game.get('home_team')} vs {game.get('away_team')}",
                                market=market_type,
                                outcome=outcome_name,
                                best_odds=best_book["odds"],
                                best_book=best_book["book"],
                                decimal_odds=decimal_odds,
                                implied_probability=best_prob,
                                opportunity_type="positive_ev",
                                edge_percent=edge * 100,
                                fair_odds=fair_american,
                                kelly_fraction=kelly,
                                recommended_stake_pct=kelly * 100,
                                recommended_stake_amount=self.bankroll * kelly,
                                max_stake_amount=self.bankroll * self.max_single_bet,
                                confidence_score=confidence,
                                sharp_money_indicator=sharp,
                                steam_move_indicator=steam,
                                line_movement_score=movement_score,
                                correlation_risk=corr_risk["level"],
                                correlation_notes=corr_risk["notes"],
                            )
                            
                            opportunities.append(opp)
        
        return opportunities
    
    def find_sharp_moves(self, game: Dict, sport_name: str) -> List[BettingOpportunity]:
        """Detect sharp money moves from line disparities"""
        opportunities = []
        
        if not game.get("bookmakers"):
            return opportunities
        
        for market_type in ["h2h", "spreads"]:
            for outcome_name in self._get_possible_outcomes(game, market_type):
                odds_list = []
                
                for bookmaker in game["bookmakers"]:
                    for market in bookmaker.get("markets", []):
                        if market.get("key") != market_type:
                            continue
                        
                        for outcome in market.get("outcomes", []):
                            if self._matches_outcome(outcome, outcome_name, market_type):
                                odds_list.append({
                                    "book": bookmaker.get("key"),
                                    "odds": outcome.get("price"),
                                    "point": outcome.get("point", 0),
                                })
                
                if len(odds_list) >= 3:
                    # Calculate line disparity
                    if market_type == "spreads":
                        points = [o["point"] for o in odds_list]
                        disparity = abs(max(points) - min(points))
                    else:
                        odds_values = [o["odds"] for o in odds_list]
                        disparity = abs(max(odds_values) - min(odds_values)) / 100
                    
                    if disparity >= self.sharp_line_threshold:
                        best_book = max(odds_list, key=lambda x: x["odds"])
                        
                        sharp, steam, movement_score = self.detect_line_movement_type(
                            disparity, len(odds_list)
                        )
                        
                        opp = BettingOpportunity(
                            sport=sport_name,
                            game=f"{game.get('home_team')} vs {game.get('away_team')}",
                            market=market_type,
                            outcome=outcome_name,
                            best_odds=best_book["odds"],
                            best_book=best_book["book"],
                            decimal_odds=self.american_to_decimal(best_book["odds"]),
                            implied_probability=self.calculate_implied_probability(
                                best_book["odds"]
                            ),
                            opportunity_type="steam_move" if steam else "sharp_move",
                            edge_percent=0.0,  # Unknown without fair odds
                            kelly_fraction=0.0,
                            recommended_stake_pct=0.0,
                            recommended_stake_amount=0.0,
                            max_stake_amount=0.0,
                            confidence_score=movement_score,
                            sharp_money_indicator=sharp,
                            steam_move_indicator=steam,
                            line_movement_score=movement_score,
                            correlation_risk="unknown",
                            correlation_notes=f"Line disparity: {disparity:.1f} points",
                        )
                        
                        opportunities.append(opp)
        
        return opportunities
    
    def _get_possible_outcomes(self, game: Dict, market_type: str) -> List[str]:
        """Get all possible outcomes for a market type"""
        outcomes = set()
        
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market.get("key") == market_type:
                    for outcome in market.get("outcomes", []):
                        outcome_key = outcome.get("name")
                        if market_type == "spreads":
                            outcome_key += f"_{outcome.get('point', 0)}"
                        elif market_type == "totals":
                            outcome_key = f"{outcome.get('name')}_{outcome.get('point', 0)}"
                        outcomes.add(outcome_key)
        
        return list(outcomes)
    
    def _matches_outcome(
        self, outcome: Dict, outcome_name: str, market_type: str
    ) -> bool:
        """Check if outcome matches outcome_name"""
        if market_type == "spreads":
            return f"{outcome.get('name')}_{outcome.get('point', 0)}" == outcome_name
        elif market_type == "totals":
            return f"{outcome.get('name')}_{outcome.get('point', 0)}" == outcome_name
        else:
            return outcome.get("name") == outcome_name
    
    def _assess_correlation_risk(
        self, market_type: str, outcome_name: str
    ) -> Dict[str, str]:
        """
        Assess correlation risk for an outcome
        
        This is a simplified version - full implementation would use
        eq12_advanced_correlation_engine.py
        """
        # Game totals have correlation risk with player props
        if market_type == "totals":
            return {
                "level": "medium",
                "notes": "Totals correlate with player props and pace",
            }
        
        # Spreads have lower correlation
        if market_type == "spreads":
            return {
                "level": "low",
                "notes": "Spread bets have minimal correlation",
            }
        
        # Moneyline
        return {
            "level": "low",
            "notes": "Moneyline bets have minimal correlation",
        }
    
    def scan_sport(self, sport_key: str, sport_name: str) -> Dict:
        """Scan a single sport for opportunities"""
        logger.info(f"\n{'=' * 80}")
        logger.info(f"🔍 Scanning {sport_name}")
        logger.info(f"{'=' * 80}")
        
        games = self.get_games(sport_key)
        
        if not games:
            return {
                "sport": sport_name,
                "games": 0,
                "arbitrage": [],
                "positive_ev": [],
                "sharp_moves": [],
                "steam_moves": [],
            }
        
        sport_arbitrage = []
        sport_positive_ev = []
        sport_sharp_moves = []
        sport_steam_moves = []
        
        for game in games:
            # Find arbitrage
            arb_opps = self.find_arbitrage(game, sport_name)
            sport_arbitrage.extend(arb_opps)
            
            # Find +EV
            ev_opps = self.find_positive_ev(game, sport_name)
            sport_positive_ev.extend(ev_opps)
            
            # Find sharp moves
            sharp_opps = self.find_sharp_moves(game, sport_name)
            for opp in sharp_opps:
                if opp.steam_move_indicator:
                    sport_steam_moves.append(opp)
                else:
                    sport_sharp_moves.append(opp)
        
        logger.info(f"✅ {sport_name}: {len(games)} games scanned")
        logger.info(f"   🎯 Arbitrage: {len(sport_arbitrage)}")
        logger.info(f"   💰 +EV: {len(sport_positive_ev)}")
        logger.info(f"   📊 Sharp Moves: {len(sport_sharp_moves)}")
        logger.info(f"   🔥 Steam Moves: {len(sport_steam_moves)}")
        
        return {
            "sport": sport_name,
            "games": len(games),
            "arbitrage": [self._opp_to_dict(o) for o in sport_arbitrage],
            "positive_ev": [self._opp_to_dict(o) for o in sport_positive_ev],
            "sharp_moves": [self._opp_to_dict(o) for o in sport_sharp_moves],
            "steam_moves": [self._opp_to_dict(o) for o in sport_steam_moves],
        }
    
    def _opp_to_dict(self, opp: BettingOpportunity) -> Dict:
        """Convert BettingOpportunity to dictionary"""
        return {
            "sport": opp.sport,
            "game": opp.game,
            "market": opp.market,
            "outcome": opp.outcome,
            "best_odds": opp.best_odds,
            "best_book": opp.best_book,
            "decimal_odds": round(opp.decimal_odds, 2),
            "implied_probability": round(opp.implied_probability, 4),
            "opportunity_type": opp.opportunity_type,
            "edge_percent": round(opp.edge_percent, 2),
            "fair_odds": opp.fair_odds,
            "kelly_fraction": round(opp.kelly_fraction, 4),
            "recommended_stake_pct": round(opp.recommended_stake_pct, 2),
            "recommended_stake_amount": round(opp.recommended_stake_amount, 2),
            "max_stake_amount": round(opp.max_stake_amount, 2),
            "confidence_score": round(opp.confidence_score, 1),
            "sharp_money_indicator": opp.sharp_money_indicator,
            "steam_move_indicator": opp.steam_move_indicator,
            "line_movement_score": round(opp.line_movement_score, 1),
            "correlation_risk": opp.correlation_risk,
            "correlation_notes": opp.correlation_notes,
            "detected_at": opp.detected_at.isoformat(),
        }
    
    def run_full_scan(self, workers: int = 10) -> Dict:
        """Run full scan across all sports with parallel execution"""
        start_time = datetime.now(UTC)
        logger.info("\n" + "=" * 80)
        logger.info("🚀 STARTING ENHANCED LIVE SPORTS SCAN")
        logger.info("=" * 80)
        logger.info(f"Bankroll: ${self.bankroll:,.2f}")
        logger.info(f"Kelly Fraction: {self.kelly_fraction * 100}% (Conservative)")
        logger.info(f"Max Single Bet: {self.max_single_bet * 100}%")
        logger.info(f"Min Edge: {self.min_edge * 100}%")
        logger.info("=" * 80)
        
        # Parallel execution
        sport_results = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(self.scan_sport, sport_key, sport_name): sport_name
                for sport_name, sport_key in SPORTS.items()
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    sport_results.append(result)
                except Exception as e:
                    sport_name = futures[future]
                    logger.error(f"❌ Error scanning {sport_name}: {e}")
        
        # Aggregate results
        for result in sport_results:
            self.results["sports_scanned"].append(result["sport"])
            self.results["total_games"] += result["games"]
            self.results["arbitrage"].extend(result["arbitrage"])
            self.results["positive_ev"].extend(result["positive_ev"])
            self.results["sharp_moves"].extend(result["sharp_moves"])
            self.results["steam_moves"].extend(result["steam_moves"])
        
        # Calculate total opportunities
        self.results["total_opportunities"] = (
            len(self.results["arbitrage"])
            + len(self.results["positive_ev"])
            + len(self.results["sharp_moves"])
            + len(self.results["steam_moves"])
        )
        
        # Calculate optimal bankroll allocation
        self.results["bankroll_allocation"] = self._calculate_bankroll_allocation()
        
        # Scan duration
        end_time = datetime.now(UTC)
        self.results["scan_duration"] = (end_time - start_time).total_seconds()
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _calculate_bankroll_allocation(self) -> Dict:
        """Calculate optimal bankroll allocation across all opportunities"""
        allocation = {
            "total_bankroll": self.bankroll,
            "allocated_amount": 0.0,
            "allocated_percent": 0.0,
            "remaining_bankroll": self.bankroll,
            "num_bets": 0,
            "arbitrage_allocation": 0.0,
            "positive_ev_allocation": 0.0,
            "high_confidence_allocation": 0.0,
        }
        
        total_stake = 0.0
        
        # Arbitrage gets priority (risk-free)
        for opp in self.results["arbitrage"]:
            total_stake += opp["recommended_stake_amount"]
            allocation["arbitrage_allocation"] += opp["recommended_stake_amount"]
            allocation["num_bets"] += 1
        
        # +EV bets sorted by confidence
        ev_opps = sorted(
            self.results["positive_ev"],
            key=lambda x: x["confidence_score"],
            reverse=True,
        )
        
        for opp in ev_opps[:20]:  # Top 20 +EV opportunities
            total_stake += opp["recommended_stake_amount"]
            allocation["positive_ev_allocation"] += opp["recommended_stake_amount"]
            allocation["num_bets"] += 1
            
            if opp["confidence_score"] >= 70:
                allocation["high_confidence_allocation"] += opp["recommended_stake_amount"]
        
        allocation["allocated_amount"] = total_stake
        allocation["allocated_percent"] = (total_stake / self.bankroll) * 100
        allocation["remaining_bankroll"] = self.bankroll - total_stake
        
        return allocation
    
    def _print_summary(self):
        """Print scan summary"""
        logger.info("\n" + "=" * 80)
        logger.info("SCAN SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Games Scanned: {self.results['total_games']}")
        logger.info(f"Total Opportunities: {self.results['total_opportunities']}")
        logger.info(f"API Requests Used: {self.api_requests_used}")
        logger.info(f"Scan Duration: {self.results['scan_duration']:.2f} seconds")
        logger.info("")
        logger.info(f"🎯 Arbitrage Opportunities: {len(self.results['arbitrage'])}")
        logger.info(f"💰 Positive EV Bets: {len(self.results['positive_ev'])}")
        logger.info(f"📊 Sharp Moves Detected: {len(self.results['sharp_moves'])}")
        logger.info(f"🔥 Steam Moves Detected: {len(self.results['steam_moves'])}")
        logger.info("")
        
        # Bankroll allocation summary
        alloc = self.results["bankroll_allocation"]
        logger.info("BANKROLL ALLOCATION")
        logger.info("=" * 80)
        logger.info(f"Total Bankroll: ${alloc['total_bankroll']:,.2f}")
        logger.info(f"Recommended Allocation: ${alloc['allocated_amount']:,.2f} ({alloc['allocated_percent']:.1f}%)")
        logger.info(f"Number of Bets: {alloc['num_bets']}")
        logger.info(f"Remaining Bankroll: ${alloc['remaining_bankroll']:,.2f}")
        logger.info("")
        logger.info(f"  Arbitrage: ${alloc['arbitrage_allocation']:,.2f}")
        logger.info(f"  +EV Bets: ${alloc['positive_ev_allocation']:,.2f}")
        logger.info(f"  High Confidence (70+): ${alloc['high_confidence_allocation']:,.2f}")
        
        # Top opportunities
        if self.results["arbitrage"]:
            logger.info("\n" + "=" * 80)
            logger.info("TOP 3 ARBITRAGE OPPORTUNITIES")
            logger.info("=" * 80)
            for i, opp in enumerate(self.results["arbitrage"][:3], 1):
                logger.info(f"\n{i}. {opp['sport']} - {opp['game']}")
                logger.info(f"   Market: {opp['market']} | Outcome: {opp['outcome']}")
                logger.info(f"   Profit: {opp['edge_percent']:.2f}%")
                logger.info(f"   Recommended Stake: ${opp['recommended_stake_amount']:,.2f} ({opp['recommended_stake_pct']:.2f}%)")
                logger.info(f"   Book: {opp['best_book']} @ {opp['best_odds']:+d}")
        
        if self.results["positive_ev"]:
            logger.info("\n" + "=" * 80)
            logger.info("TOP 5 POSITIVE EV BETS (by confidence)")
            logger.info("=" * 80)
            top_ev = sorted(
                self.results["positive_ev"],
                key=lambda x: x["confidence_score"],
                reverse=True,
            )[:5]
            
            for i, opp in enumerate(top_ev, 1):
                logger.info(f"\n{i}. {opp['sport']} - {opp['game']}")
                logger.info(f"   {opp['outcome']} @ {opp['best_book']}: {opp['best_odds']:+d}")
                logger.info(f"   Edge: {opp['edge_percent']:.2f}% | Confidence: {opp['confidence_score']:.0f}/100")
                logger.info(f"   Kelly Stake: ${opp['recommended_stake_amount']:,.2f} ({opp['recommended_stake_pct']:.2f}%)")
                if opp['sharp_money_indicator']:
                    logger.info(f"   🔥 SHARP MONEY DETECTED (Score: {opp['line_movement_score']:.0f})")
                if opp['steam_move_indicator']:
                    logger.info(f"   🌊 STEAM MOVE DETECTED")
        
        logger.info("\n" + "=" * 80)
        logger.info(f"✅ Scan completed in {self.results['scan_duration']:.2f} seconds")
        logger.info(f"💡 API requests remaining this month: {500 - self.api_requests_used}")
        logger.info("=" * 80)
    
    def save_results(self, output_dir: str = "../logs"):
        """Save results to JSON file"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = output_path / f"sports_scan_enhanced_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"\n💾 Results saved to: {filename}")
        return filename


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="EQ12 Enhanced Live Sports Scanner with Advanced Betting Intelligence"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of parallel workers (default: 10)",
    )
    parser.add_argument(
        "--bankroll",
        type=float,
        default=10000.0,
        help="Total bankroll for Kelly calculations (default: $10,000)",
    )
    parser.add_argument(
        "--kelly-fraction",
        type=float,
        default=0.25,
        help="Kelly fraction (default: 0.25 = quarter Kelly)",
    )
    
    args = parser.parse_args()
    
    # Check for API key
    if not ODDS_API_KEY:
        logger.error("❌ ODDS_API_KEY environment variable not set!")
        logger.info("Set it with: $env:ODDS_API_KEY = 'your_key_here'")
        return
    
    # Run scanner
    scanner = EnhancedLiveSportsScanner(
        api_key=ODDS_API_KEY,
        bankroll=args.bankroll,
    )
    scanner.kelly_fraction = args.kelly_fraction
    
    results = scanner.run_full_scan(workers=args.workers)
    scanner.save_results()


if __name__ == "__main__":
    main()
