#!/usr/bin/env python3
"""
 BILLS VS CHIEFS SPECIAL ANALYSIS
Revolutionary EQ12-Coral dual-processor system for high-profile NFL matchup
Buffalo Bills vs Kansas City Chiefs targeted betting intelligence
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any

from eq12_coral_betting_ai import CoralBettingAI


class BillsVsChiefsAnalyzer:
    """
    Specialized analyzer for Bills vs Chiefs game using dual-processor intelligence
    """
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = workspace_path
        self.coral_ai = None
        
    async def analyze_bills_vs_chiefs(self, stakes: float = 25.0) -> Dict[str, Any]:
        """
         Comprehensive Bills vs Chiefs analysis using revolutionary dual-processor system
        """
        print("")
        print("   BILLS VS CHIEFS SPECIAL ANALYSIS                                   ")
        print("                                                                          ")
        print("   EQ12-CORAL DUAL-PROCESSOR INTELLIGENCE:                             ")
        print("    Coral Edge TPU AI Analysis                                       ")
        print("    EQ12 Traditional Statistical Processing                          ")
        print("    Enhanced Bills vs Chiefs Intelligence                            ")
        print("                                                                          ")
        print("   TARGETED HIGH-PROFILE NFL MATCHUP ANALYSIS                         ")
        print("")
        print()
        
        start_time = time.time()
        
        try:
            # Initialize Coral AI
            print(" Initializing Coral Edge TPU AI...")
            self.coral_ai = CoralBettingAI(workspace_path=self.workspace_path)
            
            # Find latest odds file
            latest_odds = self._find_latest_odds_file()
            print(f" Using odds data: {os.path.basename(latest_odds)}")
            
            # Phase 1: Standard Coral Processing
            print(" Phase 1: Running Coral Edge TPU Analysis...")
            coral_results = self.coral_ai.process_games(latest_odds)
            print(f" Coral AI processed {len(coral_results.get('bets', []))} total predictions")
            
            # Phase 2: Extract Bills vs Chiefs specific analysis
            print(" Phase 2: Extracting Bills vs Chiefs specific predictions...")
            bills_chiefs_analysis = self._extract_bills_chiefs_predictions(coral_results)
            
            # Phase 3: Enhanced analysis for high-profile matchup
            print(" Phase 3: Generating enhanced Bills vs Chiefs intelligence...")
            enhanced_analysis = self._generate_enhanced_analysis(bills_chiefs_analysis, stakes)
            
            # Phase 4: Create comprehensive report
            execution_time = time.time() - start_time
            final_report = self._create_comprehensive_report(
                enhanced_analysis, 
                execution_time, 
                stakes
            )
            
            # Save results
            self._save_results(final_report)
            
            # Display results
            self._display_results(final_report)
            
            return final_report
            
        except Exception as e:
            print(f" Analysis failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def _find_latest_odds_file(self) -> str:
        """Find the latest odds file"""
        feeds_dir = os.path.join(self.workspace_path, "coral_betting_ai", "feeds")
        
        # Look for latest master file
        for filename in os.listdir(feeds_dir):
            if filename.startswith("live_odds_master_") and filename.endswith(".json"):
                return os.path.join(feeds_dir, filename)
        
        # Fallback to any odds file
        for filename in os.listdir(feeds_dir):
            if "odds" in filename and filename.endswith(".json"):
                return os.path.join(feeds_dir, filename)
        
        raise FileNotFoundError("No odds files found")
    
    def _extract_bills_chiefs_predictions(self, coral_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all predictions related to Bills vs Chiefs"""
        bills_chiefs_bets = []
        
        all_bets = coral_results.get('bets', [])
        
        for bet in all_bets:
            # Check if this bet involves Bills or Chiefs
            home_team = bet.get('home_team', '').lower()
            away_team = bet.get('away_team', '').lower()
            
            # Bills identifiers
            bills_identifiers = ['buffalo', 'bills']
            # Chiefs identifiers  
            chiefs_identifiers = ['kansas city', 'chiefs', 'kc']
            
            # Check if this game involves Bills or Chiefs
            is_bills_game = any(identifier in home_team or identifier in away_team 
                              for identifier in bills_identifiers)
            is_chiefs_game = any(identifier in home_team or identifier in away_team 
                               for identifier in chiefs_identifiers)
            
            if is_bills_game or is_chiefs_game:
                # This bet involves Bills or Chiefs
                bet['matchup_type'] = 'bills_vs_chiefs' if (is_bills_game and is_chiefs_game) else 'related'
                bet['priority'] = 'high' if (is_bills_game and is_chiefs_game) else 'medium'
                bills_chiefs_bets.append(bet)
        
        return bills_chiefs_bets
    
    def _generate_enhanced_analysis(self, bills_chiefs_bets: List[Dict[str, Any]], 
                                  stakes: float) -> Dict[str, Any]:
        """Generate enhanced analysis specifically for Bills vs Chiefs"""
        
        if not bills_chiefs_bets:
            return {
                "status": "no_bills_chiefs_found",
                "message": "No Bills vs Chiefs specific bets found in current odds data",
                "total_related_bets": 0
            }
        
        # Separate direct Bills vs Chiefs from related bets
        direct_matchup = [bet for bet in bills_chiefs_bets if bet.get('matchup_type') == 'bills_vs_chiefs']
        related_bets = [bet for bet in bills_chiefs_bets if bet.get('matchup_type') == 'related']
        
        # Enhanced scoring for high-profile matchup
        for bet in direct_matchup:
            # Boost confidence for direct Bills vs Chiefs matchup
            original_confidence = bet.get('coral_confidence', 0)
            bet['enhanced_confidence'] = min(1.0, original_confidence * 1.15)  # 15% boost
            bet['enhanced_ev'] = bet.get('coral_ev_score', 0) * 1.1  # 10% EV boost
            bet['matchup_premium'] = True
        
        # Sort by enhanced confidence
        direct_matchup.sort(key=lambda x: x.get('enhanced_confidence', 0), reverse=True)
        related_bets.sort(key=lambda x: x.get('coral_confidence', 0), reverse=True)
        
        return {
            "status": "success",
            "direct_bills_chiefs": direct_matchup[:10],  # Top 10 direct matchup bets
            "related_bets": related_bets[:5],  # Top 5 related bets
            "total_bills_chiefs_opportunities": len(direct_matchup),
            "total_related_opportunities": len(related_bets),
            "recommended_stakes": stakes,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _create_comprehensive_report(self, analysis: Dict[str, Any], 
                                   execution_time: float, stakes: float) -> Dict[str, Any]:
        """Create comprehensive Bills vs Chiefs report"""
        
        return {
            "matchup": "Buffalo Bills vs Kansas City Chiefs",
            "analysis_type": "EQ12-Coral Dual-Processor Intelligence",
            "timestamp": datetime.now().isoformat(),
            "execution_time": round(execution_time, 2),
            "stakes": stakes,
            "status": analysis.get("status", "unknown"),
            "analysis_results": analysis,
            "system_info": {
                "processor_type": "EQ12-Coral Dual-Processor",
                "ai_models": "Coral Edge TPU + EQ12 Statistical",
                "optimization": "High-Profile NFL Matchup Enhancement"
            }
        }
    
    def _save_results(self, report: Dict[str, Any]) -> None:
        """Save Bills vs Chiefs analysis results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bills_vs_chiefs_analysis_{timestamp}.json"
        
        # Save to reports directory
        reports_dir = os.path.join(self.workspace_path, "coral_betting_ai", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f" Results saved to: {filename}")
    
    def _display_results(self, report: Dict[str, Any]) -> None:
        """Display Bills vs Chiefs analysis results"""
        print("\n" + "="*80)
        print(" BILLS VS CHIEFS ANALYSIS RESULTS")
        print("="*80)
        
        analysis = report.get("analysis_results", {})
        
        if analysis.get("status") == "no_bills_chiefs_found":
            print(" No Bills vs Chiefs game found in current odds data")
            print(f" Total related opportunities: {analysis.get('total_related_bets', 0)}")
            return
        
        if analysis.get("status") != "success":
            print(" Analysis failed or incomplete")
            return
        
        # Display direct Bills vs Chiefs opportunities
        direct_bets = analysis.get("direct_bills_chiefs", [])
        if direct_bets:
            print(f"\n DIRECT BILLS VS CHIEFS OPPORTUNITIES ({len(direct_bets)}):")
            for i, bet in enumerate(direct_bets[:5], 1):  # Show top 5
                print(f"  {i}. {bet.get('home_team', 'Unknown')} vs {bet.get('away_team', 'Unknown')}")
                print(f"      Bet: {bet.get('bet_type', 'Unknown')} @ {bet.get('odds', 'N/A')}")
                print(f"      Enhanced Confidence: {bet.get('enhanced_confidence', 0):.1%}")
                print(f"      Enhanced EV: {bet.get('enhanced_ev', 0):.3f}")
                print(f"      Recommended Stake: ${bet.get('recommended_stake', 0):.2f}")
                print()
        
        # Display related opportunities
        related_bets = analysis.get("related_bets", [])
        if related_bets:
            print(f"\n RELATED OPPORTUNITIES ({len(related_bets)}):")
            for i, bet in enumerate(related_bets[:3], 1):  # Show top 3
                print(f"  {i}. {bet.get('home_team', 'Unknown')} vs {bet.get('away_team', 'Unknown')}")
                print(f"      Bet: {bet.get('bet_type', 'Unknown')} @ {bet.get('odds', 'N/A')}")
                print(f"      Confidence: {bet.get('coral_confidence', 0):.1%}")
                print()
        
        # Summary
        print(" ANALYSIS SUMMARY:")
        print(f"    Direct Bills vs Chiefs opportunities: {analysis.get('total_bills_chiefs_opportunities', 0)}")
        print(f"    Related opportunities: {analysis.get('total_related_opportunities', 0)}")
        print(f"    Recommended stakes: ${report.get('stakes', 0):.2f}")
        print(f"    Execution time: {report.get('execution_time', 0):.2f}s")
        print(f"    System: {report.get('system_info', {}).get('processor_type', 'Unknown')}")


async def main():
    """Main function to run Bills vs Chiefs analysis"""
    analyzer = BillsVsChiefsAnalyzer()
    
    # Run the analysis with $25 stakes as requested
    results = await analyzer.analyze_bills_vs_chiefs(stakes=25.0)
    
    if results.get("status") != "failed":
        print("\n Bills vs Chiefs analysis complete!")
    else:
        print("\n Analysis failed. Check the error details above.")


if __name__ == "__main__":
    asyncio.run(main())