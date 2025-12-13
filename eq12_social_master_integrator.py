#!/usr/bin/env python3
"""
 EQ12 SOCIAL INTELLIGENCE MASTER INTEGRATOR
=============================================

Master integration system that connects social intelligence with the EQ12 Business
Intelligence Tracker, Revenue Tracking, and automated betting decision engine.

This is the FINAL integration layer that:
- Connects social sentiment to BI metrics
- Generates actionable betting recommendations
- Updates revenue tracking with social-derived opportunities
- Creates dashboard-ready social intelligence panels
- Implements Kelly criterion with social sentiment adjustments

Real-Time Integration Features:
- Social sentiment  BI Tracker correlation analysis
- Cross-platform validation  confidence scoring
- Market divergence detection  arbitrage identification
- Automated stake sizing using Kelly criterion + social data
- Revenue impact tracking and performance optimization

Author: EQ12 Quantum Development Team  
Version: 1.0.0 - Master Social Integration
Date: November 7, 2025
"""

import asyncio
import json
import logging
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import statistics
import subprocess


@dataclass
class SocialBIIntegration:
    """Social intelligence + Business Intelligence integration."""
    sport: str
    social_sentiment: float
    market_confidence: float
    bi_correlation: float
    combined_score: float
    recommended_action: str
    stake_multiplier: float
    expected_roi: float
    risk_adjustment: float


@dataclass
class BettingOpportunity:
    """Final betting opportunity with social intelligence."""
    opportunity_id: str
    sport: str
    teams: List[str]
    opportunity_type: str
    social_sentiment: float
    market_edge: float
    confidence_score: float
    recommended_stake: float
    expected_value: float
    kelly_percentage: float
    social_boost: float
    timestamp: datetime


class EQ12SocialMasterIntegrator:
    """Master social intelligence integration system."""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.scripts_path = self.workspace_path / "scripts"
        self.data_path = self.workspace_path / "data"
        self.logs_path = self.workspace_path / "logs"
        
        # Setup logging
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_path / f"social_master_integrator_{self.timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Database paths
        self.revenue_db_path = self.data_path / "revenue.db"
        self.social_db_path = self.data_path / "social_intelligence.db"
        
        # Integration metrics
        self.master_metrics = {
            "total_opportunities": 0,
            "high_confidence_bets": 0,
            "social_edge_identified": 0,
            "total_recommended_stake": 0.0,
            "expected_portfolio_roi": 0.0,
            "integration_success_rate": 0.0
        }
    
    def get_bi_tracker_data(self) -> Dict[str, Any]:
        """Get latest data from BI tracker (simulated for demo)."""
        # In real implementation, this would query the actual BI tracker database
        return {
            "nfl": {
                "market_confidence": 0.78,
                "recent_roi": 0.12,
                "win_rate": 0.65,
                "volume_trend": "increasing",
                "sharp_money_indicator": 0.82
            },
            "nhl": {
                "market_confidence": 0.71,
                "recent_roi": 0.08,
                "win_rate": 0.58,
                "volume_trend": "stable",
                "sharp_money_indicator": 0.69
            },
            "nba": {
                "market_confidence": 0.75,
                "recent_roi": 0.15,
                "win_rate": 0.62,
                "volume_trend": "decreasing",
                "sharp_money_indicator": 0.74
            }
        }
    
    def get_social_intelligence_summary(self) -> Dict[str, Any]:
        """Get social intelligence summary from latest data."""
        if not self.social_db_path.exists():
            return {}
        
        conn = sqlite3.connect(self.social_db_path)
        
        try:
            # Get recent sentiment by sport
            cursor = conn.execute('''
                SELECT sport, 
                       AVG(sentiment_score) as avg_sentiment,
                       AVG(confidence) as avg_confidence,
                       AVG(betting_relevance) as avg_relevance,
                       COUNT(*) as sample_size
                FROM social_data 
                WHERE timestamp > datetime('now', '-2 hours')
                GROUP BY sport
            ''')
            
            social_summary = {}
            for row in cursor.fetchall():
                sport, avg_sentiment, avg_confidence, avg_relevance, sample_size = row
                social_summary[sport] = {
                    "avg_sentiment": avg_sentiment,
                    "avg_confidence": avg_confidence,
                    "avg_relevance": avg_relevance,
                    "sample_size": sample_size,
                    "data_quality": min(1.0, sample_size / 10.0)  # Quality score based on sample size
                }
            
            return social_summary
            
        except Exception as e:
            self.logger.error(f"Error getting social intelligence summary: {e}")
            return {}
        finally:
            conn.close()
    
    def calculate_social_bi_correlation(self, social_data: Dict[str, Any], 
                                       bi_data: Dict[str, Any]) -> List[SocialBIIntegration]:
        """Calculate correlation between social intelligence and BI metrics."""
        integrations = []
        
        for sport in social_data.keys():
            if sport not in bi_data:
                continue
            
            social_info = social_data[sport]
            bi_info = bi_data[sport]
            
            # Calculate correlation score
            social_sentiment = social_info["avg_sentiment"]
            market_confidence = bi_info["market_confidence"]
            
            # Correlation based on directional alignment
            sentiment_direction = 1 if social_sentiment > 0 else -1 if social_sentiment < 0 else 0
            market_direction = 1 if market_confidence > 0.5 else -1
            
            directional_correlation = 1.0 if sentiment_direction == market_direction else 0.3
            
            # Adjust for data quality
            data_quality_factor = social_info["data_quality"]
            bi_correlation = directional_correlation * data_quality_factor
            
            # Combined score (weighted average)
            social_weight = 0.4  # 40% social
            market_weight = 0.6  # 60% market/BI
            
            combined_score = (abs(social_sentiment) * social_weight) + (market_confidence * market_weight)
            
            # Determine recommended action
            if combined_score > 0.7 and social_sentiment > 0.2:
                recommended_action = "STRONG_BUY"
                stake_multiplier = 1.5
            elif combined_score > 0.6 and social_sentiment > 0.1:
                recommended_action = "BUY"
                stake_multiplier = 1.2
            elif combined_score > 0.6 and social_sentiment < -0.1:
                recommended_action = "SELL"
                stake_multiplier = 1.2
            elif combined_score > 0.7 and social_sentiment < -0.2:
                recommended_action = "STRONG_SELL"
                stake_multiplier = 1.5
            else:
                recommended_action = "HOLD"
                stake_multiplier = 0.8
            
            # Calculate expected ROI
            base_roi = bi_info["recent_roi"]
            social_boost = abs(social_sentiment) * 0.1  # Up to 10% boost
            expected_roi = base_roi + social_boost
            
            # Risk adjustment
            risk_adjustment = 1.0 - (abs(social_sentiment - (market_confidence - 0.5)) * 0.2)
            
            integration = SocialBIIntegration(
                sport=sport,
                social_sentiment=social_sentiment,
                market_confidence=market_confidence,
                bi_correlation=bi_correlation,
                combined_score=combined_score,
                recommended_action=recommended_action,
                stake_multiplier=stake_multiplier,
                expected_roi=expected_roi,
                risk_adjustment=risk_adjustment
            )
            
            integrations.append(integration)
        
        return integrations
    
    def generate_final_betting_opportunities(self, integrations: List[SocialBIIntegration]) -> List[BettingOpportunity]:
        """Generate final betting opportunities with Kelly criterion."""
        opportunities = []
        
        for integration in integrations:
            # Skip low-confidence opportunities
            if integration.combined_score < 0.5:
                continue
            
            # Calculate Kelly criterion percentage
            win_probability = min(0.95, integration.combined_score)  # Cap at 95%
            payout_odds = 2.0  # Assume 2:1 odds (simplified)
            
            # Kelly = (bp - q) / b where b=odds-1, p=win_prob, q=lose_prob
            kelly_percentage = ((payout_odds * win_probability) - (1 - win_probability)) / payout_odds
            kelly_percentage = max(0, min(0.25, kelly_percentage))  # Cap at 25%
            
            # Social sentiment boost
            social_boost = abs(integration.social_sentiment) * 0.02  # Up to 2% boost
            
            # Final recommended stake
            recommended_stake = kelly_percentage * integration.stake_multiplier
            recommended_stake = max(0.01, min(0.1, recommended_stake))  # Between 1% and 10%
            
            # Expected value calculation
            expected_value = (win_probability * payout_odds - 1) * recommended_stake
            
            # Create opportunity
            opportunity = BettingOpportunity(
                opportunity_id=f"{integration.sport}_social_{self.timestamp}",
                sport=integration.sport,
                teams=[f"{integration.sport.upper()} Teams"],  # Simplified for demo
                opportunity_type="social_bi_integration",
                social_sentiment=integration.social_sentiment,
                market_edge=integration.combined_score - 0.5,  # Edge over 50/50
                confidence_score=integration.combined_score,
                recommended_stake=recommended_stake,
                expected_value=expected_value,
                kelly_percentage=kelly_percentage,
                social_boost=social_boost,
                timestamp=datetime.now(timezone.utc)
            )
            
            opportunities.append(opportunity)
            
            # Update metrics
            self.master_metrics["total_opportunities"] += 1
            if integration.combined_score > 0.7:
                self.master_metrics["high_confidence_bets"] += 1
            if abs(integration.social_sentiment) > 0.3:
                self.master_metrics["social_edge_identified"] += 1
            self.master_metrics["total_recommended_stake"] += recommended_stake
        
        return opportunities
    
    def save_opportunities_to_revenue_db(self, opportunities: List[BettingOpportunity]):
        """Save opportunities to revenue database."""
        conn = sqlite3.connect(self.revenue_db_path)
        
        # Ensure master opportunities table exists
        conn.execute('''
            CREATE TABLE IF NOT EXISTS master_betting_opportunities (
                opportunity_id TEXT PRIMARY KEY,
                sport TEXT NOT NULL,
                teams TEXT NOT NULL,
                opportunity_type TEXT NOT NULL,
                social_sentiment REAL NOT NULL,
                market_edge REAL NOT NULL,
                confidence_score REAL NOT NULL,
                recommended_stake REAL NOT NULL,
                expected_value REAL NOT NULL,
                kelly_percentage REAL NOT NULL,
                social_boost REAL NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        for opportunity in opportunities:
            conn.execute('''
                INSERT OR REPLACE INTO master_betting_opportunities 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', CURRENT_TIMESTAMP)
            ''', (
                opportunity.opportunity_id,
                opportunity.sport,
                json.dumps(opportunity.teams),
                opportunity.opportunity_type,
                opportunity.social_sentiment,
                opportunity.market_edge,
                opportunity.confidence_score,
                opportunity.recommended_stake,
                opportunity.expected_value,
                opportunity.kelly_percentage,
                opportunity.social_boost,
                opportunity.timestamp.isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def update_bi_tracker_with_social_data(self, integrations: List[SocialBIIntegration]):
        """Update BI tracker with social intelligence enhancements."""
        # Create BI enhancement table if it doesn't exist
        conn = sqlite3.connect(self.revenue_db_path)
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS bi_social_enhancements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sport TEXT NOT NULL,
                social_sentiment REAL NOT NULL,
                bi_correlation REAL NOT NULL,
                combined_score REAL NOT NULL,
                recommended_action TEXT NOT NULL,
                stake_multiplier REAL NOT NULL,
                expected_roi REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        for integration in integrations:
            conn.execute('''
                INSERT INTO bi_social_enhancements 
                (sport, social_sentiment, bi_correlation, combined_score, 
                 recommended_action, stake_multiplier, expected_roi)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                integration.sport,
                integration.social_sentiment,
                integration.bi_correlation,
                integration.combined_score,
                integration.recommended_action,
                integration.stake_multiplier,
                integration.expected_roi
            ))
        
        conn.commit()
        conn.close()
    
    async def execute_master_integration(self) -> Dict[str, Any]:
        """Execute master social intelligence integration."""
        print(" EQ12 SOCIAL INTELLIGENCE MASTER INTEGRATOR")
        print("=" * 47)
        print("Final integration: Social Intelligence + BI Tracker + Revenue Engine")
        print()
        
        start_time = time.time()
        
        master_results = {
            "start_timestamp": datetime.now(timezone.utc).isoformat(),
            "bi_data": {},
            "social_data": {},
            "integrations": [],
            "betting_opportunities": [],
            "master_metrics": {},
            "execution_time": 0.0
        }
        
        # Step 1: Get BI Tracker Data
        print("1 BUSINESS INTELLIGENCE DATA RETRIEVAL")
        print("-" * 42)
        
        bi_data = self.get_bi_tracker_data()
        master_results["bi_data"] = bi_data
        
        print(f" BI Metrics loaded for {len(bi_data)} sports:")
        for sport, metrics in bi_data.items():
            print(f"    {sport.upper()}: Confidence {metrics['market_confidence']:.1%} | ROI {metrics['recent_roi']:.1%} | Win Rate {metrics['win_rate']:.1%}")
        
        # Step 2: Get Social Intelligence Data
        print(f"\n2 SOCIAL INTELLIGENCE DATA RETRIEVAL")
        print("-" * 41)
        
        social_data = self.get_social_intelligence_summary()
        master_results["social_data"] = social_data
        
        if social_data:
            print(f" Social data loaded for {len(social_data)} sports:")
            for sport, metrics in social_data.items():
                print(f"    {sport.upper()}: Sentiment {metrics['avg_sentiment']:+.2f} | Confidence {metrics['avg_confidence']:.1%} | Sample: {metrics['sample_size']}")
        else:
            print(" No social intelligence data available")
        
        # Step 3: Calculate Social-BI Correlation
        print(f"\n3 SOCIAL-BI CORRELATION ANALYSIS")
        print("-" * 36)
        
        if social_data and bi_data:
            integrations = self.calculate_social_bi_correlation(social_data, bi_data)
            master_results["integrations"] = [asdict(i) for i in integrations]
            
            print(f" Correlation analysis for {len(integrations)} sports:")
            for integration in integrations:
                action_icon = "" if "STRONG" in integration.recommended_action else "" if "BUY" in integration.recommended_action else "" if "SELL" in integration.recommended_action else ""
                print(f"   {action_icon} {integration.sport.upper()}: {integration.recommended_action} | Score: {integration.combined_score:.2f} | Correlation: {integration.bi_correlation:.2f}")
                print(f"      Social: {integration.social_sentiment:+.2f} | Market: {integration.market_confidence:.2f} | ROI: {integration.expected_roi:.1%}")
        else:
            integrations = []
            print(" Insufficient data for correlation analysis")
        
        # Step 4: Generate Final Betting Opportunities
        print(f"\n4 FINAL BETTING OPPORTUNITY GENERATION")
        print("-" * 42)
        
        if integrations:
            opportunities = self.generate_final_betting_opportunities(integrations)
            master_results["betting_opportunities"] = [asdict(o) for o in opportunities]
            
            print(f" Generated {len(opportunities)} betting opportunities:")
            for opportunity in opportunities:
                print(f"    {opportunity.sport.upper()}: {opportunity.opportunity_type}")
                print(f"       Stake: {opportunity.recommended_stake:.1%} | Kelly: {opportunity.kelly_percentage:.1%}")
                print(f"       Expected Value: {opportunity.expected_value:.3f} | Confidence: {opportunity.confidence_score:.1%}")
                print(f"       Social Boost: +{opportunity.social_boost:.1%} | Market Edge: {opportunity.market_edge:.2f}")
            
            # Save opportunities
            self.save_opportunities_to_revenue_db(opportunities)
            self.update_bi_tracker_with_social_data(integrations)
            print(f"\n Opportunities saved to revenue database")
            
            # Calculate portfolio metrics
            total_expected_value = sum(o.expected_value for o in opportunities)
            total_stake = sum(o.recommended_stake for o in opportunities)
            portfolio_roi = (total_expected_value / total_stake) if total_stake > 0 else 0
            
            self.master_metrics["expected_portfolio_roi"] = portfolio_roi
            self.master_metrics["integration_success_rate"] = len(opportunities) / len(integrations) if integrations else 0
            
        else:
            opportunities = []
            print(" No betting opportunities generated")
        
        # Final Results
        execution_time = time.time() - start_time
        master_results["execution_time"] = execution_time
        master_results["master_metrics"] = self.master_metrics
        
        print(f"\n MASTER INTEGRATION COMPLETE!")
        print("=" * 35)
        print(f" Execution time: {execution_time:.2f} seconds")
        print(f" Total opportunities: {self.master_metrics['total_opportunities']}")
        print(f" High confidence bets: {self.master_metrics['high_confidence_bets']}")
        print(f" Social edge identified: {self.master_metrics['social_edge_identified']}")
        print(f" Total recommended stake: {self.master_metrics['total_recommended_stake']:.1%}")
        print(f" Expected portfolio ROI: {self.master_metrics['expected_portfolio_roi']:.1%}")
        print(f" Integration success rate: {self.master_metrics['integration_success_rate']:.1%}")
        
        # Save comprehensive report
        report_file = self.logs_path / f"social_master_integration_{self.timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(master_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f" Master report: {report_file}")
        
        return master_results


async def main():
    """Main execution function for master integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Social Intelligence Master Integrator")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    args = parser.parse_args()
    
    try:
        # Initialize master integrator
        master_integrator = EQ12SocialMasterIntegrator(args.workspace)
        
        # Execute master integration
        results = await master_integrator.execute_master_integration()
        
        return 0
        
    except Exception as e:
        print(f" MASTER INTEGRATION ERROR: {e}")
        logging.error(f"Master integration error: {e}")
        return 1


if __name__ == "__main__":
    # Ensure proper event loop for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)