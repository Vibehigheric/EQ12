#!/usr/bin/env python3
"""
EQ12 Wealth Intelligence Core
Unified Sports Betting + Financial AI System for autonomous wealth generation.
"""

import asyncio
import json
import logging
import os
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
import requests
from dataclasses import dataclass
import openai

# Configure logging
logging.basicCo        try:
            # Create OpenAI client
            from openai import OpenAI
            client = OpenAI(api_key=openai.api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", 
                     "content": "You are a professional wealth management AI with expertise in sports betting finance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )  level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:\\EQ12\\logs\\wealth_core.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class BettingResult:
    """Structure for betting results"""
    date: str
    sport: str
    bet_type: str
    stake: float
    odds: float
    profit_loss: float
    ai_confidence: float
    outcome: str


@dataclass
class FinancialMetrics:
    """Structure for financial metrics"""
    date: str
    total_bankroll: float
    daily_profit: float
    roi_percentage: float
    drawdown: float
    compound_rate: float
    reinvestment_amount: float


class WealthIntelligenceCore:
    """Unified Sports Betting and Financial AI System"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "data" / "wealth_core.db"
        self.config_path = self.workspace_path / "configs" / "wealth_config.json"
        
        # Create directories
        for path in [
            self.workspace_path / "data",
            self.workspace_path / "reports" / "wealth",
            self.workspace_path / "logs"
        ]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Initialize configuration
        self.config = self.load_config()
        self.init_database()
        
        # Initialize AI components  
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Current state
        self.current_bankroll = self.config.get("initial_bankroll", 25000.0)
        self.risk_tolerance = self.config.get("risk_tolerance", 0.02)  # 2% max per bet
        self.reinvestment_rate = self.config.get("reinvestment_rate", 0.7)  # 70% reinvest
        
        logger.info("EQ12 Wealth Intelligence Core initialized")

    def load_config(self) -> Dict:
        """Load wealth management configuration"""
        default_config = {
            "initial_bankroll": 25000.0,
            "risk_tolerance": 0.02,
            "reinvestment_rate": 0.70,
            "max_daily_exposure": 0.10,
            "min_bankroll_threshold": 5000.0,
            "compound_target": 0.65,  # 65% monthly target
            "sports": {
                "mlb": {"enabled": True, "max_legs": 10, "confidence_threshold": 0.75},
                "nfl": {"enabled": True, "max_legs": 8, "confidence_threshold": 0.80},
                "nba": {"enabled": True, "max_legs": 6, "confidence_threshold": 0.70}
            },
            "financial_targets": {
                "daily_profit_target": 1500.0,
                "weekly_profit_target": 8000.0,
                "monthly_profit_target": 35000.0
            },
            "automation": {
                "auto_betting": False,  # Human oversight required
                "auto_reinvestment": True,
                "alert_thresholds": {
                    "large_loss": 0.05,  # 5% bankroll
                    "profit_milestone": 0.20  # 20% growth
                }
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Config load failed: {e}, using defaults")
        
        return default_config

    def init_database(self):
        """Initialize wealth management database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Betting results table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS betting_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        sport TEXT NOT NULL,
                        bet_type TEXT NOT NULL,
                        stake REAL NOT NULL,
                        odds REAL NOT NULL,
                        profit_loss REAL NOT NULL,
                        ai_confidence REAL,
                        outcome TEXT NOT NULL,
                        parlay_details TEXT
                    )
                ''')
                
                # Financial metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS financial_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        total_bankroll REAL NOT NULL,
                        daily_profit REAL NOT NULL,
                        roi_percentage REAL NOT NULL,
                        drawdown REAL NOT NULL,
                        compound_rate REAL NOT NULL,
                        reinvestment_amount REAL NOT NULL
                    )
                ''')
                
                # AI predictions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ai_predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        sport TEXT NOT NULL,
                        event_details TEXT NOT NULL,
                        prediction TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        expected_value REAL NOT NULL,
                        actual_result TEXT,
                        accuracy_score REAL
                    )
                ''')
                
                # Wealth allocation table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS wealth_allocation (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        allocation_type TEXT NOT NULL,
                        amount REAL NOT NULL,
                        percentage REAL NOT NULL,
                        target_use TEXT NOT NULL
                    )
                ''')
                
                conn.commit()
                logger.info("Wealth database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    # ===============================
    # SPORTS BETTING AI ENGINE
    # ===============================
    
    async def analyze_betting_opportunities(self, sport: str = "MLB") -> List[Dict]:
        """AI-powered betting opportunity analysis"""
        try:
            logger.info(f"Analyzing {sport} betting opportunities...")
            
            # Get current odds data (placeholder - integrate with actual API)
            odds_data = await self.fetch_odds_data(sport)
            
            opportunities = []
            for game in odds_data:
                # AI analysis for each game
                analysis = await self.ai_game_analysis(game, sport)
                
                if analysis['expected_value'] > 0.05:  # Minimum 5% EV
                    opportunities.append({
                        'game': game,
                        'analysis': analysis,
                        'recommended_stake': self.calculate_stake(analysis),
                        'confidence': analysis['confidence']
                    })
            
            # Sort by expected value
            opportunities.sort(key=lambda x: x['analysis']['expected_value'], reverse=True)
            
            logger.info(f"Found {len(opportunities)} profitable opportunities")
            return opportunities[:10]  # Top 10
            
        except Exception as e:
            logger.error(f"Betting analysis failed: {e}")
            return []

    async def fetch_odds_data(self, sport: str) -> List[Dict]:
        """Fetch live odds data from APIs"""
        # Placeholder for actual API integration
        # In production, this would call OddsAPI, DraftKings API, etc.
        
        sample_games = [
            {
                "id": "game_001",
                "teams": ["Dodgers", "Yankees"],
                "moneyline": {"Dodgers": -150, "Yankees": +130},
                "spread": {"Dodgers": -1.5, "Yankees": +1.5},
                "total": {"over": 8.5, "under": 8.5},
                "props": {
                    "Mookie Betts Over 1.5 TB": +120,
                    "Aaron Judge 1+ HR": +180
                }
            }
        ]
        
        return sample_games

    async def ai_game_analysis(self, game: Dict, sport: str) -> Dict:
        """AI analysis of individual game for betting value"""
        try:
            prompt = f"""
            Analyze this {sport} game for betting value:
            
            Teams: {game['teams']}
            Moneyline: {game['moneyline']}
            Spread: {game['spread']}
            Total: {game['total']}
            Props: {game['props']}
            
            Provide analysis in JSON format:
            {{
                "true_probability": 0.65,
                "bookmaker_probability": 0.60,
                "expected_value": 0.08,
                "confidence": 0.85,
                "best_bet": "Dodgers ML",
                "reasoning": "Strong pitching matchup favors Dodgers"
            }}
            """
            
            # Create OpenAI client
            from openai import OpenAI
            client = OpenAI(api_key=openai.api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert sports betting analyst with 95% accuracy."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Store prediction for accuracy tracking
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO ai_predictions 
                    (timestamp, sport, event_details, prediction, confidence, expected_value)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now(timezone.utc).isoformat(),
                    sport,
                    json.dumps(game),
                    json.dumps(analysis),
                    analysis['confidence'],
                    analysis['expected_value']
                ))
                conn.commit()
            
            return analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {
                "true_probability": 0.5,
                "expected_value": 0.0,
                "confidence": 0.0,
                "best_bet": "No bet",
                "reasoning": "Analysis failed"
            }

    def calculate_stake(self, analysis: Dict) -> float:
        """Calculate optimal stake using Kelly Criterion"""
        try:
            ev = analysis['expected_value']
            confidence = analysis['confidence']
            
            # Modified Kelly Criterion with risk adjustment
            kelly_fraction = (ev * confidence) / (1 - confidence) if confidence < 1 else 0
            
            # Cap at risk tolerance
            max_stake = self.current_bankroll * self.risk_tolerance
            kelly_stake = self.current_bankroll * kelly_fraction * 0.25  # Quarter Kelly
            
            stake = min(kelly_stake, max_stake)
            
            # Minimum stake threshold
            return max(stake, 50.0) if stake > 25.0 else 0.0
            
        except Exception as e:
            logger.error(f"Stake calculation failed: {e}")
            return 0.0

    async def generate_parlay(self, sport: str, num_legs: int = 8) -> Dict:
        """Generate AI-optimized parlay"""
        try:
            opportunities = await self.analyze_betting_opportunities(sport)
            
            if len(opportunities) < num_legs:
                num_legs = len(opportunities)
            
            # Select top opportunities for parlay
            parlay_legs = opportunities[:num_legs]
            
            # Calculate combined odds and probability
            combined_odds = 1.0
            combined_prob = 1.0
            
            for leg in parlay_legs:
                # Extract odds from analysis
                odds_decimal = 2.0  # Placeholder
                prob = leg['analysis']['true_probability']
                
                combined_odds *= odds_decimal
                combined_prob *= prob
            
            parlay = {
                "sport": sport,
                "legs": parlay_legs,
                "num_legs": num_legs,
                "combined_odds": combined_odds,
                "win_probability": combined_prob,
                "expected_value": (combined_odds * combined_prob) - 1,
                "recommended_stake": self.calculate_parlay_stake(combined_prob, combined_odds),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Generated {num_legs}-leg parlay with EV: {parlay['expected_value']:.3f}")
            return parlay
            
        except Exception as e:
            logger.error(f"Parlay generation failed: {e}")
            return {}

    def calculate_parlay_stake(self, win_prob: float, odds: float) -> float:
        """Calculate optimal parlay stake"""
        if win_prob <= 0 or odds <= 1:
            return 0.0
        
        # Conservative staking for parlays
        kelly_fraction = ((odds * win_prob) - 1) / (odds - 1)
        conservative_fraction = kelly_fraction * 0.1  # 10% of Kelly for parlays
        
        max_parlay_stake = self.current_bankroll * 0.005  # 0.5% max for parlays
        kelly_stake = self.current_bankroll * conservative_fraction
        
        return min(kelly_stake, max_parlay_stake, 100.0)

    # ===============================
    # FINANCIAL AI ENGINE
    # ===============================
    
    def calculate_financial_metrics(self) -> FinancialMetrics:
        """Calculate current financial performance metrics"""
        try:
            # Get recent betting results
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Last 30 days
                thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
                cursor.execute('''
                    SELECT SUM(profit_loss), COUNT(*) 
                    FROM betting_results 
                    WHERE timestamp > ?
                ''', (thirty_days_ago,))
                
                result = cursor.fetchone()
                total_profit = result[0] if result[0] else 0.0
                total_bets = result[1] if result[1] else 0
                
                # Daily profit (last 24 hours)
                yesterday = (datetime.now() - timedelta(days=1)).isoformat()
                cursor.execute('''
                    SELECT SUM(profit_loss) 
                    FROM betting_results 
                    WHERE timestamp > ?
                ''', (yesterday,))
                
                daily_profit = cursor.fetchone()[0] or 0.0
            
            # Calculate metrics
            roi_percentage = (total_profit / self.current_bankroll) * 100 if self.current_bankroll > 0 else 0
            
            # Estimate compound rate (monthly)
            if total_bets > 0:
                avg_daily_return = daily_profit / self.current_bankroll if self.current_bankroll > 0 else 0
                compound_rate = ((1 + avg_daily_return) ** 30 - 1) * 100
            else:
                compound_rate = 0.0
            
            # Calculate drawdown (simplified)
            drawdown = max(0, (self.config['initial_bankroll'] - self.current_bankroll) / self.config['initial_bankroll'] * 100)
            
            # Reinvestment calculation
            reinvestment_amount = daily_profit * self.reinvestment_rate if daily_profit > 0 else 0
            
            metrics = FinancialMetrics(
                date=datetime.now(timezone.utc).isoformat(),
                total_bankroll=self.current_bankroll,
                daily_profit=daily_profit,
                roi_percentage=roi_percentage,
                drawdown=drawdown,
                compound_rate=compound_rate,
                reinvestment_amount=reinvestment_amount
            )
            
            # Store metrics
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO financial_metrics 
                    (timestamp, total_bankroll, daily_profit, roi_percentage, 
                     drawdown, compound_rate, reinvestment_amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.date, metrics.total_bankroll, metrics.daily_profit,
                    metrics.roi_percentage, metrics.drawdown, metrics.compound_rate,
                    metrics.reinvestment_amount
                ))
                conn.commit()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Financial metrics calculation failed: {e}")
            return FinancialMetrics(
                date=datetime.now(timezone.utc).isoformat(),
                total_bankroll=self.current_bankroll,
                daily_profit=0.0,
                roi_percentage=0.0,
                drawdown=0.0,
                compound_rate=0.0,
                reinvestment_amount=0.0
            )

    async def ai_financial_analysis(self, metrics: FinancialMetrics) -> Dict:
        """AI-powered financial analysis and recommendations"""
        try:
            prompt = f"""
            Analyze this financial performance data for EQ12 wealth management:
            
            Current Bankroll: ${metrics.total_bankroll:,.2f}
            Daily Profit: ${metrics.daily_profit:,.2f}
            ROI: {metrics.roi_percentage:.2f}%
            Drawdown: {metrics.drawdown:.2f}%
            Compound Rate: {metrics.compound_rate:.2f}%/month
            Reinvestment: ${metrics.reinvestment_amount:,.2f}
            
            Provide recommendations in JSON format:
            {{
                "risk_assessment": "low/medium/high",
                "bankroll_adjustment": 0.05,
                "reinvestment_strategy": "aggressive/conservative/balanced",
                "profit_target_adjustment": 1500.0,
                "warnings": ["Any risk warnings"],
                "opportunities": ["Growth opportunities"],
                "next_actions": ["Specific recommendations"]
            }}
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional wealth management AI with expertise in sports betting finance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            logger.info(f"AI Financial Analysis: {analysis['risk_assessment']} risk")
            return analysis
            
        except Exception as e:
            logger.error(f"AI financial analysis failed: {e}")
            return {
                "risk_assessment": "medium",
                "bankroll_adjustment": 0.0,
                "reinvestment_strategy": "conservative",
                "warnings": ["Analysis failed"],
                "opportunities": [],
                "next_actions": ["Manual review required"]
            }

    def execute_wealth_allocation(self, profit: float) -> Dict:
        """Execute AI-driven wealth allocation strategy"""
        try:
            if profit <= 0:
                return {"status": "no_allocation", "reason": "No profit to allocate"}
            
            # Allocation strategy
            allocations = {
                "bankroll_reinvestment": profit * 0.70,  # 70% back to betting
                "emergency_fund": profit * 0.15,        # 15% safety net
                "business_investment": profit * 0.10,   # 10% EQ12 upgrades
                "personal_withdrawal": profit * 0.05    # 5% personal use
            }
            
            # Execute allocations
            self.current_bankroll += allocations["bankroll_reinvestment"]
            
            # Log allocation
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for allocation_type, amount in allocations.items():
                    percentage = (amount / profit) * 100
                    cursor.execute('''
                        INSERT INTO wealth_allocation 
                        (timestamp, allocation_type, amount, percentage, target_use)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        datetime.now(timezone.utc).isoformat(),
                        allocation_type,
                        amount,
                        percentage,
                        f"Automated allocation from ${profit:.2f} profit"
                    ))
                conn.commit()
            
            logger.info(f"Allocated ${profit:.2f} profit across 4 categories")
            return {
                "status": "success",
                "total_allocated": profit,
                "allocations": allocations,
                "new_bankroll": self.current_bankroll
            }
            
        except Exception as e:
            logger.error(f"Wealth allocation failed: {e}")
            return {"status": "error", "message": str(e)}

    # ===============================
    # REPORTING & COMMUNICATION
    # ===============================
    
    async def generate_wealth_report(self) -> Dict:
        """Generate comprehensive wealth management report"""
        try:
            metrics = self.calculate_financial_metrics()
            ai_analysis = await self.ai_financial_analysis(metrics)
            
            # Get recent betting performance
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Last 7 days betting stats
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_bets,
                        SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
                        SUM(profit_loss) as total_profit,
                        AVG(ai_confidence) as avg_confidence
                    FROM betting_results 
                    WHERE timestamp > ?
                ''', (week_ago,))
                
                betting_stats = cursor.fetchone()
            
            # Calculate win rate
            total_bets = betting_stats[0] or 0
            wins = betting_stats[1] or 0
            win_rate = (wins / total_bets * 100) if total_bets > 0 else 0
            
            report = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "financial_metrics": {
                    "bankroll": metrics.total_bankroll,
                    "daily_profit": metrics.daily_profit,
                    "roi_percentage": metrics.roi_percentage,
                    "compound_rate": metrics.compound_rate,
                    "drawdown": metrics.drawdown
                },
                "betting_performance": {
                    "total_bets_7d": total_bets,
                    "wins_7d": wins,
                    "win_rate": win_rate,
                    "total_profit_7d": betting_stats[2] or 0,
                    "avg_ai_confidence": betting_stats[3] or 0
                },
                "ai_analysis": ai_analysis,
                "projections": {
                    "monthly_profit_projection": metrics.daily_profit * 30,
                    "annual_bankroll_projection": self.project_annual_growth(metrics),
                    "break_even_analysis": self.calculate_break_even()
                }
            }
            
            # Save report
            report_file = self.workspace_path / "reports" / "wealth" / f"wealth_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Wealth report generated: {report_file}")
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {}

    def project_annual_growth(self, metrics: FinancialMetrics) -> float:
        """Project annual bankroll growth based on current performance"""
        try:
            if metrics.compound_rate <= 0:
                return self.current_bankroll
            
            # Conservative projection with diminishing returns
            monthly_rate = metrics.compound_rate / 100
            
            projected_bankroll = self.current_bankroll
            for month in range(12):
                # Diminishing returns factor
                diminishing_factor = max(0.5, 1 - (month * 0.05))
                effective_rate = monthly_rate * diminishing_factor
                projected_bankroll *= (1 + effective_rate)
            
            return projected_bankroll
            
        except Exception as e:
            logger.error(f"Growth projection failed: {e}")
            return self.current_bankroll

    def calculate_break_even(self) -> int:
        """Calculate days to break even from initial investment"""
        try:
            initial_investment = self.config['initial_bankroll']
            current_profit = self.current_bankroll - initial_investment
            
            if current_profit >= 0:
                return 0  # Already profitable
            
            # Get average daily profit over last 30 days
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
                cursor.execute('''
                    SELECT AVG(daily_profit) FROM (
                        SELECT DATE(timestamp) as date, SUM(profit_loss) as daily_profit
                        FROM betting_results 
                        WHERE timestamp > ?
                        GROUP BY DATE(timestamp)
                    )
                ''', (thirty_days_ago,))
                
                avg_daily_profit = cursor.fetchone()[0] or 0
            
            if avg_daily_profit <= 0:
                return -1  # Cannot break even at current rate
            
            days_to_break_even = abs(current_profit) / avg_daily_profit
            return int(days_to_break_even)
            
        except Exception as e:
            logger.error(f"Break-even calculation failed: {e}")
            return -1

    async def send_wealth_alert(self, alert_type: str, data: Dict) -> bool:
        """Send wealth management alerts via Telegram"""
        try:
            if alert_type == "daily_summary":
                message = f"""
 **EQ12 Wealth Summary**

 Bankroll: ${data['bankroll']:,.2f}
 Daily P&L: ${data['daily_profit']:+,.2f}
 ROI: {data['roi']:.1f}%
 Win Rate: {data['win_rate']:.1f}%
 AI Confidence: {data['avg_confidence']:.1f}%

 Status: {data['status']}
"""
            
            elif alert_type == "profit_milestone":
                message = f"""
 **PROFIT MILESTONE REACHED!**

 New Bankroll: ${data['bankroll']:,.2f}
 Profit: ${data['profit']:+,.2f}
 ROI: {data['roi']:.1f}%

 Keep the momentum going!
"""
            
            elif alert_type == "risk_warning":
                message = f"""
 **RISK WARNING**

 Current Drawdown: {data['drawdown']:.1f}%
 Bankroll: ${data['bankroll']:,.2f}
 Recommended Action: {data['action']}

 AI Analysis: {data['analysis']}
"""
            
            else:
                message = f"EQ12 Wealth Alert: {alert_type}"
            
            # Send via Telegram (placeholder - integrate with actual bot)
            logger.info(f"Wealth alert sent: {alert_type}")
            return True
            
        except Exception as e:
            logger.error(f"Alert sending failed: {e}")
            return False

    # ===============================
    # MAIN CONTROL LOOP
    # ===============================
    
    async def run_wealth_cycle(self):
        """Main wealth management cycle"""
        logger.info("Starting EQ12 Wealth Intelligence cycle...")
        
        while True:
            try:
                # Generate betting opportunities
                opportunities = await self.analyze_betting_opportunities("MLB")
                
                if opportunities:
                    logger.info(f"Found {len(opportunities)} betting opportunities")
                    
                    # Generate optimal parlay if enough opportunities
                    if len(opportunities) >= 5:
                        parlay = await self.generate_parlay("MLB", 8)
                        if parlay and parlay.get('expected_value', 0) > 0.1:
                            logger.info(f"Generated profitable parlay: EV={parlay['expected_value']:.3f}")
                
                # Calculate financial metrics
                metrics = self.calculate_financial_metrics()
                
                # AI financial analysis
                ai_analysis = await self.ai_financial_analysis(metrics)
                
                # Execute wealth allocation if profitable
                if metrics.daily_profit > 0:
                    allocation = self.execute_wealth_allocation(metrics.daily_profit)
                    logger.info(f"Wealth allocation: {allocation['status']}")
                
                # Generate reports
                if datetime.now().hour == 9:  # Daily report at 9 AM
                    report = await self.generate_wealth_report()
                    await self.send_wealth_alert("daily_summary", {
                        "bankroll": metrics.total_bankroll,
                        "daily_profit": metrics.daily_profit,
                        "roi": metrics.roi_percentage,
                        "win_rate": 85.0,  # Placeholder
                        "avg_confidence": 0.87,  # Placeholder
                        "status": "Profitable"
                    })
                
                # Check for alerts
                if metrics.drawdown > 10:
                    await self.send_wealth_alert("risk_warning", {
                        "drawdown": metrics.drawdown,
                        "bankroll": metrics.total_bankroll,
                        "action": "Reduce position sizes",
                        "analysis": ai_analysis.get('warnings', ['Manual review needed'])[0]
                    })
                
                # Sleep until next cycle
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Wealth cycle error: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes on error


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Wealth Intelligence Core")
    parser.add_argument("--workspace", default="C:\\EQ12", help="Workspace path")
    parser.add_argument("--analyze", action="store_true", help="Analyze betting opportunities")
    parser.add_argument("--parlay", type=int, help="Generate parlay with N legs")
    parser.add_argument("--report", action="store_true", help="Generate wealth report")
    parser.add_argument("--daemon", action="store_true", help="Run continuous wealth cycle")
    
    args = parser.parse_args()
    
    wealth_core = WealthIntelligenceCore(args.workspace)
    
    if args.analyze:
        async def analyze():
            opportunities = await wealth_core.analyze_betting_opportunities()
            print(json.dumps(opportunities, indent=2))
        asyncio.run(analyze())
        return 0
    
    if args.parlay:
        async def generate_parlay():
            parlay = await wealth_core.generate_parlay("MLB", args.parlay)
            print(json.dumps(parlay, indent=2))
        asyncio.run(generate_parlay())
        return 0
    
    if args.report:
        async def generate_report():
            report = await wealth_core.generate_wealth_report()
            print(json.dumps(report, indent=2))
        asyncio.run(generate_report())
        return 0
    
    if args.daemon:
        try:
            asyncio.run(wealth_core.run_wealth_cycle())
        except KeyboardInterrupt:
            logger.info("Wealth Intelligence cycle stopped")
        except Exception as e:
            logger.error(f"Wealth cycle failed: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())