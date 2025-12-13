#!/usr/bin/env python3
"""
EQ12 Comprehensive Parlay Analysis System
Scans all parlay logs and analyzes performance metrics for betting slips

Analyzes:
- All parlay types (NFL, MLB, NCAA, SGP)
- Win/Loss rates by sport and bet type
- Performance trends over time
- Profitability analysis
- Optimal betting patterns
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
    logger = LoggingConfig.create_module_logger("parlay_analysis")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

class ParlayAnalysisEngine:
    """Comprehensive analysis engine for EQ12 parlay performance"""
    
    def __init__(self):
        self.eq12_root = Path("C:/EQ12")
        self.logs_path = self.eq12_root / "logs"
        self.analysis_results = {}
        self.parlay_data = {
            "nfl": [],
            "mlb": [],
            "ncaa": [], 
            "sgp": [],
            "mixed": [],
            "other": []
        }
        
        # Betting result patterns
        self.win_patterns = [
            r"WIN|WON|HIT|WINNER|SUCCESS",
            r"paid.*out|cashed|profit",
            r"final.*result.*win",
            r"status.*won"
        ]
        
        self.loss_patterns = [
            r"LOSS|LOST|MISS|LOSER|FAILED",
            r"busted|lost.*stake|no.*payout",
            r"final.*result.*loss",
            r"status.*lost"
        ]
        
    def scan_parlay_logs(self):
        """Scan all log files for parlay data"""
        logger.info("🔍 Starting comprehensive parlay log scan...")
        
        # Define file patterns to search
        file_patterns = [
            "nfl_parlay*.json",
            "nfl_parlay*.log",
            "mlb_*sgp*.json",
            "*parlay*.json", 
            "*sgp*.json",
            "daily_parlays*.json",
            "enhanced_parlay*.json",
            "eq12_optimal_parlays*.json",
            "*betting_slip*.txt",
            "NCAA_*.json"
        ]
        
        total_files_scanned = 0
        
        for pattern in file_patterns:
            files = list(self.logs_path.glob(pattern))
            for file_path in files:
                try:
                    self._process_parlay_file(file_path)
                    total_files_scanned += 1
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
        
        # Scan parlays subdirectory
        parlays_dir = self.logs_path / "parlays"
        if parlays_dir.exists():
            for file_path in parlays_dir.glob("*"):
                try:
                    self._process_parlay_file(file_path)
                    total_files_scanned += 1
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
        
        logger.info(f"✅ Scanned {total_files_scanned} parlay files")
        return total_files_scanned
    
    def _process_parlay_file(self, file_path: Path):
        """Process individual parlay file"""
        try:
            # Determine sport/type from filename
            sport_type = self._classify_parlay_type(file_path.name)
            
            if file_path.suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self._extract_json_parlays(data, sport_type, file_path)
            elif file_path.suffix in ['.log', '.txt']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    self._extract_text_parlays(content, sport_type, file_path)
                    
        except Exception as e:
            logger.warning(f"Could not process {file_path}: {e}")
    
    def _classify_parlay_type(self, filename: str) -> str:
        """Classify parlay type from filename"""
        filename_lower = filename.lower()
        
        if 'nfl' in filename_lower:
            return 'nfl'
        elif 'mlb' in filename_lower or 'baseball' in filename_lower:
            return 'mlb'
        elif 'ncaa' in filename_lower or 'college' in filename_lower:
            return 'ncaa'
        elif 'sgp' in filename_lower or 'same_game' in filename_lower:
            return 'sgp'
        elif 'mixed' in filename_lower or 'ultimate' in filename_lower:
            return 'mixed'
        else:
            return 'other'
    
    def _extract_json_parlays(self, data: Any, sport_type: str, file_path: Path):
        """Extract parlay data from JSON files"""
        timestamp = self._extract_timestamp_from_filename(file_path.name)
        
        if isinstance(data, dict):
            # Handle various JSON structures
            if 'parlays' in data:
                for parlay in data['parlays']:
                    self._process_single_parlay(parlay, sport_type, timestamp, file_path)
            elif 'recommendations' in data:
                for rec in data['recommendations']:
                    self._process_single_parlay(rec, sport_type, timestamp, file_path)
            elif 'legs' in data or 'bets' in data:
                # Single parlay structure
                self._process_single_parlay(data, sport_type, timestamp, file_path)
            elif isinstance(data, list):
                for item in data:
                    self._process_single_parlay(item, sport_type, timestamp, file_path)
        elif isinstance(data, list):
            for item in data:
                self._process_single_parlay(item, sport_type, timestamp, file_path)
    
    def _extract_text_parlays(self, content: str, sport_type: str, file_path: Path):
        """Extract parlay data from text/log files"""
        timestamp = self._extract_timestamp_from_filename(file_path.name)
        
        # Look for betting slip patterns
        slip_patterns = [
            r"Bet ID:\s*(\S+)",
            r"Parlay.*?Total Odds:\s*([-+]?\d+)",
            r"Wager:\s*\$?(\d+\.?\d*)",
            r"Potential Payout:\s*\$?(\d+\.?\d*)"
        ]
        
        # Extract potential win/loss indicators
        result_status = None
        for win_pattern in self.win_patterns:
            if re.search(win_pattern, content, re.IGNORECASE):
                result_status = "WIN"
                break
        
        if not result_status:
            for loss_pattern in self.loss_patterns:
                if re.search(loss_pattern, content, re.IGNORECASE):
                    result_status = "LOSS"
                    break
        
        # Create parlay record from text
        parlay_record = {
            "source_file": str(file_path),
            "timestamp": timestamp,
            "sport_type": sport_type,
            "result_status": result_status,
            "content_preview": content[:200] + "..." if len(content) > 200 else content
        }
        
        # Try to extract numerical data
        for pattern in slip_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                if "Odds" in pattern:
                    parlay_record["total_odds"] = matches[0]
                elif "Wager" in pattern:
                    parlay_record["wager_amount"] = float(matches[0])
                elif "Payout" in pattern:
                    parlay_record["potential_payout"] = float(matches[0])
        
        self.parlay_data[sport_type].append(parlay_record)
    
    def _process_single_parlay(self, parlay_data: Dict, sport_type: str, timestamp: str, file_path: Path):
        """Process individual parlay record"""
        try:
            parlay_record = {
                "source_file": str(file_path),
                "timestamp": timestamp,
                "sport_type": sport_type,
                "parlay_data": parlay_data
            }
            
            # Extract key metrics
            if isinstance(parlay_data, dict):
                parlay_record["legs"] = len(parlay_data.get("legs", parlay_data.get("bets", [])))
                parlay_record["total_odds"] = parlay_data.get("total_odds", parlay_data.get("odds"))
                parlay_record["wager_amount"] = parlay_data.get("wager", parlay_data.get("stake"))
                parlay_record["potential_payout"] = parlay_data.get("payout", parlay_data.get("potential_win"))
                parlay_record["confidence"] = parlay_data.get("confidence", parlay_data.get("ev_score"))
                parlay_record["result_status"] = parlay_data.get("status", parlay_data.get("result"))
                
                # Look for team names
                teams = []
                if "legs" in parlay_data:
                    for leg in parlay_data["legs"]:
                        if isinstance(leg, dict):
                            team = leg.get("team", leg.get("selection", ""))
                            if team:
                                teams.append(team)
                
                parlay_record["teams"] = teams
            
            self.parlay_data[sport_type].append(parlay_record)
            
        except Exception as e:
            logger.warning(f"Error processing parlay record: {e}")
    
    def _extract_timestamp_from_filename(self, filename: str) -> str:
        """Extract timestamp from filename"""
        # Look for timestamp patterns
        timestamp_patterns = [
            r"(\d{8}_\d{6})",  # YYYYMMDD_HHMMSS
            r"(\d{8})",        # YYYYMMDD
            r"(\d{4}-\d{2}-\d{2})" # YYYY-MM-DD
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1)
        
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze overall parlay performance"""
        logger.info("📊 Starting performance analysis...")
        
        analysis = {
            "summary": {},
            "by_sport": {},
            "trends": {},
            "profitability": {},
            "recommendations": []
        }
        
        # Overall summary
        total_parlays = sum(len(parlays) for parlays in self.parlay_data.values())
        analysis["summary"]["total_parlays_found"] = total_parlays
        
        wins = 0
        losses = 0
        pending = 0
        total_wagered = 0
        total_potential = 0
        
        # Analyze by sport
        for sport, parlays in self.parlay_data.items():
            if not parlays:
                continue
                
            sport_analysis = {
                "count": len(parlays),
                "wins": 0,
                "losses": 0,
                "pending": 0,
                "total_wagered": 0,
                "total_potential": 0,
                "avg_legs": 0,
                "recent_performance": []
            }
            
            leg_counts = []
            
            for parlay in parlays:
                # Count results
                status = parlay.get("result_status", "PENDING")
                if isinstance(status, str):
                    status = status.upper()
                    if any(win_word in status for win_word in ["WIN", "WON", "HIT", "SUCCESS"]):
                        sport_analysis["wins"] += 1
                        wins += 1
                    elif any(loss_word in status for loss_word in ["LOSS", "LOST", "MISS", "FAILED"]):
                        sport_analysis["losses"] += 1
                        losses += 1
                    else:
                        sport_analysis["pending"] += 1
                        pending += 1
                
                # Sum financials
                wager = parlay.get("wager_amount", 0)
                payout = parlay.get("potential_payout", 0)
                
                if isinstance(wager, (int, float)):
                    sport_analysis["total_wagered"] += wager
                    total_wagered += wager
                
                if isinstance(payout, (int, float)):
                    sport_analysis["total_potential"] += payout
                    total_potential += payout
                
                # Track leg counts
                legs = parlay.get("legs", 0)
                if isinstance(legs, int) and legs > 0:
                    leg_counts.append(legs)
            
            # Calculate averages
            if leg_counts:
                sport_analysis["avg_legs"] = sum(leg_counts) / len(leg_counts)
            
            # Calculate win rate
            total_decided = sport_analysis["wins"] + sport_analysis["losses"]
            if total_decided > 0:
                sport_analysis["win_rate"] = sport_analysis["wins"] / total_decided
                sport_analysis["loss_rate"] = sport_analysis["losses"] / total_decided
            
            # Calculate ROI if we have financial data
            if sport_analysis["total_wagered"] > 0:
                sport_analysis["potential_roi"] = (sport_analysis["total_potential"] / sport_analysis["total_wagered"]) - 1
            
            analysis["by_sport"][sport] = sport_analysis
        
        # Overall metrics
        analysis["summary"].update({
            "total_wins": wins,
            "total_losses": losses, 
            "pending": pending,
            "total_wagered": total_wagered,
            "total_potential": total_potential
        })
        
        # Calculate overall win rate
        total_decided = wins + losses
        if total_decided > 0:
            analysis["summary"]["overall_win_rate"] = wins / total_decided
            analysis["summary"]["overall_loss_rate"] = losses / total_decided
        
        # Generate recommendations
        recommendations = []
        
        # Find best performing sport
        best_sport = None
        best_win_rate = 0
        
        for sport, sport_data in analysis["by_sport"].items():
            win_rate = sport_data.get("win_rate", 0)
            if win_rate > best_win_rate and sport_data["count"] >= 5:  # Minimum sample size
                best_win_rate = win_rate
                best_sport = sport
        
        if best_sport:
            recommendations.append(f"Focus on {best_sport.upper()} parlays - highest win rate at {best_win_rate:.1%}")
        
        # Leg count analysis
        all_parlays = []
        for parlays in self.parlay_data.values():
            all_parlays.extend(parlays)
        
        if all_parlays:
            leg_performance = defaultdict(list)
            for parlay in all_parlays:
                legs = parlay.get("legs", 0)
                status = parlay.get("result_status", "")
                if legs and status:
                    won = any(win_word in str(status).upper() for win_word in ["WIN", "WON", "HIT"])
                    leg_performance[legs].append(won)
            
            # Find optimal leg count
            best_legs = None
            best_leg_rate = 0
            
            for leg_count, results in leg_performance.items():
                if len(results) >= 3:  # Minimum sample
                    win_rate = sum(results) / len(results)
                    if win_rate > best_leg_rate:
                        best_leg_rate = win_rate
                        best_legs = leg_count
            
            if best_legs:
                recommendations.append(f"Optimal parlay size: {best_legs} legs with {best_leg_rate:.1%} win rate")
        
        analysis["recommendations"] = recommendations
        
        logger.info(f"✅ Analysis complete: {total_parlays} parlays analyzed")
        return analysis
    
    def generate_detailed_report(self, analysis: Dict[str, Any]) -> str:
        """Generate detailed performance report"""
        report = []
        
        report.append("🏈 EQ12 COMPREHENSIVE PARLAY ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"📁 Log Directory: {self.logs_path}")
        report.append("")
        
        # Summary section
        summary = analysis["summary"]
        report.append("📊 OVERALL SUMMARY")
        report.append("-" * 30)
        report.append(f"Total Parlays Analyzed: {summary.get('total_parlays_found', 0)}")
        report.append(f"Wins: {summary.get('total_wins', 0)}")
        report.append(f"Losses: {summary.get('total_losses', 0)}")
        report.append(f"Pending: {summary.get('pending', 0)}")
        
        if "overall_win_rate" in summary:
            report.append(f"Overall Win Rate: {summary['overall_win_rate']:.2%}")
            report.append(f"Overall Loss Rate: {summary['overall_loss_rate']:.2%}")
        
        if summary.get('total_wagered', 0) > 0:
            report.append(f"Total Wagered: ${summary['total_wagered']:,.2f}")
            report.append(f"Total Potential: ${summary['total_potential']:,.2f}")
            roi = (summary['total_potential'] / summary['total_wagered']) - 1
            report.append(f"Potential ROI: {roi:.2%}")
        
        report.append("")
        
        # By sport analysis
        report.append("🏆 PERFORMANCE BY SPORT")
        report.append("-" * 30)
        
        for sport, data in analysis["by_sport"].items():
            if data["count"] == 0:
                continue
                
            report.append(f"\n{sport.upper()} PARLAYS:")
            report.append(f"  Count: {data['count']}")
            report.append(f"  Wins: {data['wins']}")
            report.append(f"  Losses: {data['losses']}")
            report.append(f"  Pending: {data['pending']}")
            
            if "win_rate" in data:
                report.append(f"  Win Rate: {data['win_rate']:.2%}")
            
            if data.get('avg_legs', 0) > 0:
                report.append(f"  Avg Legs: {data['avg_legs']:.1f}")
            
            if data.get('total_wagered', 0) > 0:
                report.append(f"  Total Wagered: ${data['total_wagered']:,.2f}")
                report.append(f"  Potential Return: ${data['total_potential']:,.2f}")
                
                if "potential_roi" in data:
                    report.append(f"  Potential ROI: {data['potential_roi']:.2%}")
        
        report.append("")
        
        # Recommendations
        if analysis["recommendations"]:
            report.append("💡 RECOMMENDATIONS")
            report.append("-" * 30)
            for i, rec in enumerate(analysis["recommendations"], 1):
                report.append(f"{i}. {rec}")
            report.append("")
        
        # Data quality notes
        report.append("📋 DATA QUALITY NOTES")
        report.append("-" * 30)
        report.append("• Analysis based on available log files in EQ12/logs directory")
        report.append("• Result status inferred from log content and file patterns")
        report.append("• Financial data extracted where available in structured logs")
        report.append("• Pending bets may include historical unresolved entries")
        report.append("")
        
        return "\n".join(report)
    
    def save_analysis_results(self, analysis: Dict[str, Any], detailed_report: str):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON analysis
        analysis_file = self.logs_path / f"parlay_analysis_{timestamp}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        # Save detailed report
        report_file = self.logs_path / f"parlay_analysis_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(detailed_report)
        
        logger.info(f"📄 Analysis saved to: {analysis_file}")
        logger.info(f"📄 Report saved to: {report_file}")
        
        return analysis_file, report_file

def main():
    """Main execution function"""
    print("🎰 EQ12 Parlay Performance Analysis")
    print("=" * 50)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Scanning: C:/EQ12/logs")
    print()
    
    # Initialize analyzer
    analyzer = ParlayAnalysisEngine()
    
    # Scan logs
    print("🔍 Scanning parlay logs...")
    files_scanned = analyzer.scan_parlay_logs()
    print(f"✅ Scanned {files_scanned} files")
    
    # Analyze performance
    print("\n📊 Analyzing performance...")
    analysis = analyzer.analyze_performance()
    
    # Generate report
    print("\n📝 Generating detailed report...")
    detailed_report = analyzer.generate_detailed_report(analysis)
    
    # Save results
    print("\n💾 Saving results...")
    analysis_file, report_file = analyzer.save_analysis_results(analysis, detailed_report)
    
    # Display summary
    print("\n🎯 QUICK SUMMARY")
    print("-" * 20)
    summary = analysis["summary"]
    print(f"Total Parlays: {summary.get('total_parlays_found', 0)}")
    print(f"Wins: {summary.get('total_wins', 0)}")
    print(f"Losses: {summary.get('total_losses', 0)}")
    
    if "overall_win_rate" in summary:
        print(f"Win Rate: {summary['overall_win_rate']:.2%}")
    
    # Show top recommendations
    if analysis["recommendations"]:
        print(f"\n💡 Top Recommendation: {analysis['recommendations'][0]}")
    
    print(f"\n📄 Full report: {report_file}")
    print("🏁 Analysis complete!")
    
    return analysis, detailed_report

if __name__ == "__main__":
    try:
        analysis, report = main()
    except KeyboardInterrupt:
        print("\n🛑 Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()