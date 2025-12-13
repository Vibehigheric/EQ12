#!/usr/bin/env python3
"""
EQ12 Financial Parlay Performance Tracker
Detailed winnings vs losses analysis with profit/loss calculations

Tracks:
- Actual cash winnings from successful bets
- Real money lost on failed bets  
- Net profit/loss by sport and strategy
- ROI analysis and break-even calculations
- Bankroll impact assessment
"""

import os
import json
import re
import logging
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import glob
import sys

# Add EQ12 paths
sys.path.append(str(Path(__file__).parent.parent / 'configs'))

try:
    from logging_eq12 import LoggingConfig
    logger = LoggingConfig.create_module_logger("financial_parlay_analysis")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

class FinancialParlayTracker:
    """Advanced financial tracking for EQ12 parlay performance"""
    
    def __init__(self):
        self.eq12_root = Path("C:/EQ12")
        self.logs_path = self.eq12_root / "logs"
        
        # Financial tracking containers
        self.financial_data = {
            "total_wagered": 0.0,
            "total_winnings": 0.0,
            "total_losses": 0.0,
            "net_profit_loss": 0.0,
            "by_sport": {},
            "by_date": {},
            "by_strategy": {}
        }
        
        # Bet tracking with outcomes
        self.bet_records = []
        
        # Outcome patterns for financial analysis
        self.win_indicators = [
            r"WIN|WON|HIT|WINNER|SUCCESS|PAID.*OUT|CASHED",
            r"profit.*\$(\d+\.?\d*)",
            r"won.*\$(\d+\.?\d*)",
            r"payout.*\$(\d+\.?\d*)",
            r"collected.*\$(\d+\.?\d*)"
        ]
        
        self.loss_indicators = [
            r"LOSS|LOST|MISS|LOSER|FAILED|BUSTED",
            r"lost.*stake|no.*payout|void",
            r"lost.*\$(\d+\.?\d*)",
            r"stake.*\$(\d+\.?\d*)"
        ]
        
    def scan_financial_records(self):
        """Scan logs for detailed financial performance data"""
        logger.info("💰 Starting comprehensive financial analysis...")
        
        # Define specific patterns for financial files
        financial_patterns = [
            "*parlay*.json",
            "*sgp*.json", 
            "*betting_slip*.txt",
            "*settlement*.json",
            "*winnings*.json",
            "*losses*.json",
            "daily_parlays*.json",
            "enhanced_parlay*.json"
        ]
        
        total_processed = 0
        
        for pattern in financial_patterns:
            files = list(self.logs_path.glob(pattern))
            for file_path in files:
                try:
                    self._extract_financial_data(file_path)
                    total_processed += 1
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
        
        logger.info(f"✅ Processed {total_processed} financial records")
        return total_processed
    
    def _extract_financial_data(self, file_path: Path):
        """Extract detailed financial information from betting records"""
        try:
            timestamp = self._extract_timestamp_from_filename(file_path.name)
            sport_type = self._classify_sport_type(file_path.name)
            
            if file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self._process_json_financial_data(data, sport_type, timestamp, file_path)
            elif file_path.suffix in ['.log', '.txt']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    self._process_text_financial_data(content, sport_type, timestamp, file_path)
                    
        except Exception as e:
            logger.warning(f"Could not process financial data from {file_path}: {e}")
    
    def _process_json_financial_data(self, data: Any, sport_type: str, timestamp: str, file_path: Path):
        """Process JSON files for financial data"""
        
        def extract_bet_record(bet_data, parent_data=None):
            """Extract individual bet financial record"""
            
            # Initialize bet record
            bet_record = {
                "source_file": str(file_path),
                "timestamp": timestamp,
                "sport_type": sport_type,
                "bet_id": None,
                "stake_amount": 0.0,
                "potential_payout": 0.0,
                "actual_payout": 0.0,
                "net_result": 0.0,
                "status": "PENDING",
                "odds": None,
                "legs": 0,
                "teams": [],
                "strategy": "standard"
            }
            
            # Extract from bet data
            if isinstance(bet_data, dict):
                # Financial amounts
                bet_record["stake_amount"] = self._extract_currency(
                    bet_data.get("wager", bet_data.get("stake", bet_data.get("bet_amount", 0)))
                )
                
                bet_record["potential_payout"] = self._extract_currency(
                    bet_data.get("potential_payout", bet_data.get("payout", bet_data.get("to_win", 0)))
                )
                
                bet_record["actual_payout"] = self._extract_currency(
                    bet_data.get("actual_payout", bet_data.get("winnings", bet_data.get("collected", 0)))
                )
                
                # Status and outcome
                status = bet_data.get("status", bet_data.get("result", bet_data.get("outcome", "PENDING")))
                if isinstance(status, str):
                    bet_record["status"] = status.upper()
                
                # Bet details
                bet_record["odds"] = bet_data.get("odds", bet_data.get("total_odds"))
                bet_record["legs"] = len(bet_data.get("legs", bet_data.get("bets", [])))
                bet_record["bet_id"] = bet_data.get("bet_id", bet_data.get("id"))
                
                # Strategy classification
                if "sgp" in str(file_path).lower() or "same_game" in str(bet_data).lower():
                    bet_record["strategy"] = "sgp"
                elif "mixed" in str(file_path).lower():
                    bet_record["strategy"] = "mixed"
                
                # Calculate net result
                if bet_record["status"] in ["WIN", "WON", "HIT", "SUCCESS"]:
                    bet_record["net_result"] = bet_record["actual_payout"] - bet_record["stake_amount"]
                elif bet_record["status"] in ["LOSS", "LOST", "MISS", "FAILED"]:
                    bet_record["net_result"] = -bet_record["stake_amount"]
                
                return bet_record
        
        # Process different JSON structures
        if isinstance(data, dict):
            if "parlays" in data:
                for parlay in data["parlays"]:
                    record = extract_bet_record(parlay, data)
                    if record:
                        self.bet_records.append(record)
            elif "bets" in data:
                for bet in data["bets"]:
                    record = extract_bet_record(bet, data)
                    if record:
                        self.bet_records.append(record)
            elif any(key in data for key in ["stake", "wager", "odds", "legs"]):
                # Single bet structure
                record = extract_bet_record(data)
                if record:
                    self.bet_records.append(record)
        elif isinstance(data, list):
            for item in data:
                record = extract_bet_record(item)
                if record:
                    self.bet_records.append(record)
    
    def _process_text_financial_data(self, content: str, sport_type: str, timestamp: str, file_path: Path):
        """Process text files for financial information"""
        
        # Extract financial amounts from text
        stake_patterns = [
            r"stake[:\s]*\$?(\d+\.?\d*)",
            r"wager[:\s]*\$?(\d+\.?\d*)",
            r"bet[:\s]*\$?(\d+\.?\d*)"
        ]
        
        payout_patterns = [
            r"payout[:\s]*\$?(\d+\.?\d*)",
            r"potential[:\s]*\$?(\d+\.?\d*)",
            r"to.*win[:\s]*\$?(\d+\.?\d*)"
        ]
        
        winnings_patterns = [
            r"won[:\s]*\$?(\d+\.?\d*)",
            r"collected[:\s]*\$?(\d+\.?\d*)",
            r"profit[:\s]*\$?(\d+\.?\d*)"
        ]
        
        # Extract amounts
        stake_amount = 0.0
        potential_payout = 0.0
        actual_winnings = 0.0
        
        for pattern in stake_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                stake_amount = max(float(match) for match in matches)
                break
        
        for pattern in payout_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                potential_payout = max(float(match) for match in matches)
                break
        
        for pattern in winnings_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                actual_winnings = max(float(match) for match in matches)
                break
        
        # Determine outcome
        status = "PENDING"
        for win_pattern in self.win_indicators:
            if re.search(win_pattern, content, re.IGNORECASE):
                status = "WIN"
                break
        
        if status == "PENDING":
            for loss_pattern in self.loss_indicators:
                if re.search(loss_pattern, content, re.IGNORECASE):
                    status = "LOSS"
                    break
        
        # Calculate net result
        net_result = 0.0
        if status == "WIN" and actual_winnings > 0:
            net_result = actual_winnings - stake_amount
        elif status == "LOSS" and stake_amount > 0:
            net_result = -stake_amount
        
        # Create bet record
        bet_record = {
            "source_file": str(file_path),
            "timestamp": timestamp,
            "sport_type": sport_type,
            "stake_amount": stake_amount,
            "potential_payout": potential_payout,
            "actual_payout": actual_winnings,
            "net_result": net_result,
            "status": status,
            "strategy": "sgp" if "sgp" in str(file_path).lower() else "standard"
        }
        
        if any([stake_amount, potential_payout, actual_winnings]):
            self.bet_records.append(bet_record)
    
    def _extract_currency(self, value) -> float:
        """Extract numeric value from currency strings"""
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            # Remove currency symbols and extract number
            clean_value = re.sub(r'[,$]', '', value)
            try:
                return float(clean_value)
            except ValueError:
                return 0.0
        return 0.0
    
    def _classify_sport_type(self, filename: str) -> str:
        """Classify sport from filename"""
        filename_lower = filename.lower()
        
        if 'nfl' in filename_lower:
            return 'nfl'
        elif 'mlb' in filename_lower or 'baseball' in filename_lower:
            return 'mlb'
        elif 'ncaa' in filename_lower or 'college' in filename_lower:
            return 'ncaa'
        elif 'sgp' in filename_lower:
            return 'sgp'
        elif 'nba' in filename_lower:
            return 'nba'
        else:
            return 'other'
    
    def _extract_timestamp_from_filename(self, filename: str) -> str:
        """Extract timestamp from filename"""
        timestamp_patterns = [
            r"(\d{8}_\d{6})",
            r"(\d{8})", 
            r"(\d{4}-\d{2}-\d{2})"
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1)
        
        return datetime.now().strftime("%Y%m%d")
    
    def calculate_financial_performance(self) -> Dict[str, Any]:
        """Calculate comprehensive financial performance metrics"""
        logger.info("📊 Calculating financial performance...")
        
        # Initialize totals
        total_stakes = 0.0
        total_winnings = 0.0
        total_losses = 0.0
        net_profit_loss = 0.0
        
        wins = 0
        losses = 0
        pending = 0
        
        # By sport tracking
        sport_performance = defaultdict(lambda: {
            "total_staked": 0.0,
            "total_winnings": 0.0,
            "total_losses": 0.0,
            "net_result": 0.0,
            "wins": 0,
            "losses": 0,
            "pending": 0,
            "avg_stake": 0.0,
            "avg_odds": 0.0,
            "roi": 0.0
        })
        
        # By strategy tracking
        strategy_performance = defaultdict(lambda: {
            "total_staked": 0.0,
            "total_winnings": 0.0, 
            "total_losses": 0.0,
            "net_result": 0.0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "roi": 0.0
        })
        
        # Process each bet record
        stakes_list = []
        
        for record in self.bet_records:
            sport = record["sport_type"]
            strategy = record["strategy"]
            stake = record["stake_amount"]
            net_result = record["net_result"]
            status = record["status"]
            
            if stake > 0:
                stakes_list.append(stake)
                total_stakes += stake
                sport_performance[sport]["total_staked"] += stake
                strategy_performance[strategy]["total_staked"] += stake
            
            if status in ["WIN", "WON", "HIT", "SUCCESS"]:
                wins += 1
                sport_performance[sport]["wins"] += 1
                strategy_performance[strategy]["wins"] += 1
                
                if net_result > 0:
                    total_winnings += net_result
                    sport_performance[sport]["total_winnings"] += net_result
                    strategy_performance[strategy]["total_winnings"] += net_result
                    
            elif status in ["LOSS", "LOST", "MISS", "FAILED"]:
                losses += 1
                sport_performance[sport]["losses"] += 1
                strategy_performance[strategy]["losses"] += 1
                
                if stake > 0:
                    total_losses += stake
                    sport_performance[sport]["total_losses"] += stake
                    strategy_performance[strategy]["total_losses"] += stake
                    
            else:
                pending += 1
                sport_performance[sport]["pending"] += 1
        
        # Calculate net result
        net_profit_loss = total_winnings - total_losses
        
        # Calculate rates and ROI
        total_decided = wins + losses
        overall_win_rate = wins / total_decided if total_decided > 0 else 0
        overall_roi = net_profit_loss / total_stakes if total_stakes > 0 else 0
        
        # Calculate sport-specific metrics
        for sport, perf in sport_performance.items():
            sport_decided = perf["wins"] + perf["losses"]
            perf["win_rate"] = perf["wins"] / sport_decided if sport_decided > 0 else 0
            perf["net_result"] = perf["total_winnings"] - perf["total_losses"]
            perf["roi"] = perf["net_result"] / perf["total_staked"] if perf["total_staked"] > 0 else 0
            
            # Average stake calculation
            sport_records = [r for r in self.bet_records if r["sport_type"] == sport and r["stake_amount"] > 0]
            if sport_records:
                perf["avg_stake"] = sum(r["stake_amount"] for r in sport_records) / len(sport_records)
        
        # Calculate strategy-specific metrics
        for strategy, perf in strategy_performance.items():
            strategy_decided = perf["wins"] + perf["losses"]
            perf["win_rate"] = perf["wins"] / strategy_decided if strategy_decided > 0 else 0
            perf["net_result"] = perf["total_winnings"] - perf["total_losses"]
            perf["roi"] = perf["net_result"] / perf["total_staked"] if perf["total_staked"] > 0 else 0
        
        # Compile results
        financial_analysis = {
            "overall": {
                "total_records": len(self.bet_records),
                "total_staked": total_stakes,
                "total_winnings": total_winnings,
                "total_losses": total_losses,
                "net_profit_loss": net_profit_loss,
                "wins": wins,
                "losses": losses,
                "pending": pending,
                "win_rate": overall_win_rate,
                "loss_rate": losses / total_decided if total_decided > 0 else 0,
                "roi": overall_roi,
                "avg_stake": sum(stakes_list) / len(stakes_list) if stakes_list else 0
            },
            "by_sport": dict(sport_performance),
            "by_strategy": dict(strategy_performance)
        }
        
        logger.info(f"✅ Financial analysis complete: {len(self.bet_records)} records processed")
        return financial_analysis
    
    def generate_financial_report(self, analysis: Dict[str, Any]) -> str:
        """Generate detailed financial performance report"""
        
        report = []
        overall = analysis["overall"]
        
        report.append("💰 EQ12 FINANCIAL PARLAY PERFORMANCE REPORT")
        report.append("=" * 60)
        report.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📊 Records Analyzed: {overall['total_records']}")
        report.append("")
        
        # Overall Financial Summary
        report.append("💵 OVERALL FINANCIAL PERFORMANCE")
        report.append("-" * 40)
        report.append(f"Total Staked: ${overall['total_staked']:,.2f}")
        report.append(f"Total Winnings: ${overall['total_winnings']:,.2f}")
        report.append(f"Total Losses: ${overall['total_losses']:,.2f}")
        report.append(f"Net Profit/Loss: ${overall['net_profit_loss']:,.2f}")
        
        # Performance metrics
        report.append(f"\nWin Rate: {overall['win_rate']:.2%}")
        report.append(f"Loss Rate: {overall['loss_rate']:.2%}")
        report.append(f"ROI: {overall['roi']:.2%}")
        report.append(f"Average Stake: ${overall['avg_stake']:,.2f}")
        
        # Profitability assessment
        if overall['net_profit_loss'] > 0:
            report.append(f"\n🏆 STATUS: PROFITABLE (+${overall['net_profit_loss']:,.2f})")
        else:
            report.append(f"\n🔴 STATUS: LOSING (${overall['net_profit_loss']:,.2f})")
        
        report.append("")
        
        # By Sport Analysis
        report.append("🏈 FINANCIAL PERFORMANCE BY SPORT")
        report.append("-" * 40)
        
        for sport, perf in analysis["by_sport"].items():
            if perf["total_staked"] == 0:
                continue
                
            report.append(f"\n{sport.upper()}:")
            report.append(f"  Total Staked: ${perf['total_staked']:,.2f}")
            report.append(f"  Winnings: ${perf['total_winnings']:,.2f}")
            report.append(f"  Losses: ${perf['total_losses']:,.2f}")
            report.append(f"  Net Result: ${perf['net_result']:,.2f}")
            report.append(f"  Win Rate: {perf['win_rate']:.2%}")
            report.append(f"  ROI: {perf['roi']:.2%}")
            
            # Profitability indicator
            if perf['net_result'] > 0:
                report.append(f"  Status: 🟢 PROFITABLE")
            elif perf['net_result'] < 0:
                report.append(f"  Status: 🔴 LOSING")
            else:
                report.append(f"  Status: 🟡 BREAK-EVEN")
        
        report.append("")
        
        # By Strategy Analysis  
        report.append("🎯 FINANCIAL PERFORMANCE BY STRATEGY")
        report.append("-" * 45)
        
        for strategy, perf in analysis["by_strategy"].items():
            if perf["total_staked"] == 0:
                continue
                
            report.append(f"\n{strategy.upper()} STRATEGY:")
            report.append(f"  Total Staked: ${perf['total_staked']:,.2f}")
            report.append(f"  Winnings: ${perf['total_winnings']:,.2f}")
            report.append(f"  Losses: ${perf['total_losses']:,.2f}")
            report.append(f"  Net Result: ${perf['net_result']:,.2f}")
            report.append(f"  Win Rate: {perf['win_rate']:.2%}")
            report.append(f"  ROI: {perf['roi']:.2%}")
        
        # Top Performers
        report.append("")
        report.append("🏆 TOP PERFORMERS")
        report.append("-" * 20)
        
        # Best sport by ROI
        best_sport = max(analysis["by_sport"].items(), 
                        key=lambda x: x[1]["roi"] if x[1]["total_staked"] > 0 else -999)
        if best_sport[1]["total_staked"] > 0:
            report.append(f"Best Sport: {best_sport[0].upper()} ({best_sport[1]['roi']:.2%} ROI)")
        
        # Best strategy by ROI
        best_strategy = max(analysis["by_strategy"].items(),
                          key=lambda x: x[1]["roi"] if x[1]["total_staked"] > 0 else -999)
        if best_strategy[1]["total_staked"] > 0:
            report.append(f"Best Strategy: {best_strategy[0].upper()} ({best_strategy[1]['roi']:.2%} ROI)")
        
        # Recommendations
        report.append("")
        report.append("💡 FINANCIAL RECOMMENDATIONS")
        report.append("-" * 30)
        
        if overall['roi'] < 0:
            report.append("⚠️  IMMEDIATE ACTIONS NEEDED:")
            report.append("   1. Reduce stake sizes on losing strategies")
            report.append("   2. Focus bankroll on profitable sports/strategies")
            report.append("   3. Implement strict bankroll management")
        
        # Identify most profitable approach
        profitable_sports = [(sport, data) for sport, data in analysis["by_sport"].items() 
                           if data["net_result"] > 0 and data["total_staked"] > 0]
        
        if profitable_sports:
            report.append("✅ PROFITABLE OPPORTUNITIES:")
            for sport, data in profitable_sports[:3]:
                report.append(f"   • {sport.upper()}: +${data['net_result']:.2f} ({data['roi']:.2%} ROI)")
        
        # Risk assessment
        report.append("")
        report.append("⚠️  RISK ASSESSMENT")
        report.append("-" * 20)
        
        if overall['avg_stake'] > 100:
            report.append("🔴 HIGH STAKES: Average bet size may be too large for bankroll")
        elif overall['avg_stake'] < 10:
            report.append("🟡 CONSERVATIVE: Very small stakes limiting profit potential")
        else:
            report.append("🟢 BALANCED: Stake sizes appear reasonable")
        
        if overall['win_rate'] < 0.1:
            report.append("🔴 LOW WIN RATE: Betting strategy needs significant improvement")
        elif overall['win_rate'] > 0.4:
            report.append("🟢 GOOD WIN RATE: Strategy showing promise")
        
        report.append("")
        report.append("📈 BANKROLL MANAGEMENT NOTES")
        report.append("-" * 30)
        report.append(f"• Current risk exposure: ${overall['total_staked']:,.2f}")
        report.append(f"• Break-even point: {(1/(1+abs(overall['roi']))):.2%} win rate needed")
        report.append(f"• Recommended max stake: {overall['avg_stake']*0.5:.2f} (50% reduction)")
        report.append("")
        
        return "\n".join(report)
    
    def save_financial_analysis(self, analysis: Dict[str, Any], report: str):
        """Save financial analysis results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON analysis
        json_file = self.logs_path / f"financial_analysis_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        # Save detailed report
        report_file = self.logs_path / f"financial_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save raw bet records for further analysis
        records_file = self.logs_path / f"bet_records_{timestamp}.json"
        with open(records_file, 'w') as f:
            json.dump(self.bet_records, f, indent=2, default=str)
        
        logger.info(f"💾 Financial analysis saved: {json_file}")
        logger.info(f"📄 Financial report saved: {report_file}")
        logger.info(f"📊 Bet records saved: {records_file}")
        
        return json_file, report_file, records_file

def main():
    """Main execution for financial analysis"""
    print("💰 EQ12 FINANCIAL PARLAY ANALYSIS")
    print("=" * 50)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("💵 Tracking: Winnings vs Losses with Comparative Analysis")
    print()
    
    # Initialize financial tracker
    tracker = FinancialParlayTracker()
    
    # Scan financial records
    print("🔍 Scanning financial records...")
    records_processed = tracker.scan_financial_records()
    print(f"✅ Processed {records_processed} financial files")
    
    # Calculate performance
    print("\n📊 Calculating financial performance...")
    analysis = tracker.calculate_financial_performance()
    
    # Generate report
    print("\n📝 Generating financial report...")
    report = tracker.generate_financial_report(analysis)
    
    # Save results
    print("\n💾 Saving financial analysis...")
    json_file, report_file, records_file = tracker.save_financial_analysis(analysis, report)
    
    # Display key metrics
    overall = analysis["overall"]
    print("\n💵 FINANCIAL SUMMARY")
    print("-" * 25)
    print(f"Total Staked: ${overall['total_staked']:,.2f}")
    print(f"Total Winnings: ${overall['total_winnings']:,.2f}")
    print(f"Total Losses: ${overall['total_losses']:,.2f}")
    print(f"Net Result: ${overall['net_profit_loss']:,.2f}")
    print(f"ROI: {overall['roi']:.2%}")
    print(f"Win Rate: {overall['win_rate']:.2%}")
    
    # Status indicator
    if overall['net_profit_loss'] > 0:
        print(f"\n🏆 STATUS: PROFITABLE (+${overall['net_profit_loss']:,.2f})")
    else:
        print(f"\n🔴 STATUS: LOSING (${overall['net_profit_loss']:,.2f})")
    
    # Top recommendation
    profitable_sports = [(sport, data) for sport, data in analysis["by_sport"].items() 
                        if data.get("net_result", 0) > 0]
    
    if profitable_sports:
        best_sport = max(profitable_sports, key=lambda x: x[1]["roi"])
        print(f"\n💡 BEST PERFORMER: {best_sport[0].upper()} (+${best_sport[1]['net_result']:.2f})")
    
    print(f"\n📄 Full report: {report_file}")
    print("💰 Financial analysis complete!")
    
    return analysis, report

if __name__ == "__main__":
    try:
        analysis, report = main()
    except KeyboardInterrupt:
        print("\n🛑 Financial analysis interrupted")
    except Exception as e:
        print(f"\n❌ Financial analysis failed: {e}")
        import traceback
        traceback.print_exc()