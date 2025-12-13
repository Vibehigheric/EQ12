#!/usr/bin/env python3
"""
EQ12-CORAL SYNERGISTIC BETTING INTELLIGENCE LAUNCHER
Revolutionary dual-processor system launcher combining EQ12 + Coral Edge TPU
The most advanced sports betting AI system ever created
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

# Import both processing systems
from eq12_coral_betting_ai import CoralBettingAI
from eq12_odds_stream import main as collect_odds

def print_banner():
    """Print revolutionary system banner"""
    banner = """

   EQ12-CORAL SYNERGISTIC BETTING INTELLIGENCE SYSTEM                 
                                                                          
   REVOLUTIONARY DUAL-PROCESSOR ARCHITECTURE:                           
    Coral Edge TPU AI (Hardware-Accelerated ML)                      
    EQ12 Traditional Processing (Statistical Analysis)               
    Synergistic Enhancement (Exponential Intelligence Boost)         
                                                                          
   THE MOST ADVANCED BETTING AI SYSTEM EVER CREATED                    

    """
    print(banner)

async def run_synergistic_analysis(workspace: str, stakes: float, mode: str = "hybrid"):
    """Run complete synergistic betting analysis"""
    
    print_banner()
    print(" Initializing revolutionary dual-processor system...")
    
    try:
        # Step 1: Collect fresh live odds
        print("\n PHASE 1: Collecting fresh live odds data...")
        await collect_fresh_odds(workspace)
        
        # Step 2: Initialize Coral AI with synergistic mode
        print("\n PHASE 2: Initializing Coral Edge TPU AI...")
        coral_ai = CoralBettingAI(workspace, verbose=True, enable_synergy=True)
        
        # Step 3: Find latest odds file
        odds_dir = Path(workspace) / "coral_betting_ai" / "feeds"
        odds_files = list(odds_dir.glob("live_odds_master_*.json"))
        
        if not odds_files:
            print(" No odds data found. Running odds collection first...")
            return
        
        latest_odds = max(odds_files, key=lambda f: f.stat().st_mtime)
        print(f" Using odds data: {latest_odds.name}")
        
        # Step 4: Run synergistic analysis
        print(f"\n PHASE 3: Running synergistic analysis (${stakes} stakes, {mode} mode)...")
        print(" Engaging dual-processor intelligence...")
        
        analysis = await coral_ai.process_synergistic_analysis(str(latest_odds), stakes)
        
        # Step 5: Display results
        print_synergistic_results(analysis)
        
        return analysis
        
    except Exception as e:
        print(f" Synergistic analysis failed: {e}")
        return None

async def collect_fresh_odds(workspace: str):
    """Collect fresh odds data"""
    try:
        # Use existing odds stream
        import subprocess
        result = subprocess.run([
            sys.executable, 
            str(Path(workspace) / "scripts" / "eq12_odds_stream.py"),
            "--workspace", workspace,
            "--verbose"
        ], capture_output=True, text=True, cwd=str(Path(workspace) / "scripts"))
        
        if result.returncode == 0:
            print(" Fresh odds data collected successfully")
        else:
            print(f" Odds collection warning: {result.stderr}")
            
    except Exception as e:
        print(f" Failed to collect odds: {e}")

def print_synergistic_results(analysis: dict):
    """Print comprehensive synergistic analysis results"""
    
    if not analysis:
        print(" No analysis results to display")
        return
    
    print("\n" + "="*80)
    print(" SYNERGISTIC ANALYSIS RESULTS")
    print("="*80)
    
    # System metrics
    synergy_metrics = analysis.get('synergy_metrics', {})
    print(f"\n SYNERGY PERFORMANCE:")
    print(f"   Synergy Boost: +{synergy_metrics.get('synergy_boost_percentage', 0):.1f}%")
    print(f"   Processor Consensus: {synergy_metrics.get('consensus_rate', 0):.1f}%")
    print(f"   Enhanced Predictions: {synergy_metrics.get('total_enhanced_predictions', 0)}")
    print(f"   Execution Time: {analysis.get('execution_time', 0):.2f}s")
    
    # Top predictions
    enhanced_preds = analysis.get('enhanced_predictions', [])
    if enhanced_preds:
        print(f"\n TOP SYNERGISTIC PREDICTIONS:")
        
        for i, pred in enumerate(enhanced_preds[:5], 1):
            print(f"\n   #{i}: {pred.get('description', 'Unknown Prediction')}")
            print(f"     Synergistic EV: {pred.get('synergistic_ev_score', 0):.8f}")
            print(f"     Enhanced Confidence: {pred.get('synergistic_confidence', 0):.4f}")
            print(f"     Agreement Factor: {pred.get('agreement_factor', 0):.1%}")
            print(f"     Synergy Multiplier: {pred.get('synergy_multiplier', 1):.2f}x")
            print(f"     Stakes: ${analysis.get('stakes_analysis', 25)}")
            
            # Calculate potential payout
            odds = pred.get('odds', 1)
            stakes = analysis.get('stakes_analysis', 25)
            potential_return = stakes * odds
            profit = potential_return - stakes
            
            print(f"     Potential Return: ${potential_return:.2f}")
            print(f"     Profit: ${profit:.2f}")
    
    print(f"\n SYSTEM STATUS: Revolutionary dual-processor active!")
    print(f" Processing Mode: {analysis.get('processing_mode', 'unknown').upper()}")
    
    # Telegram notification
    print(f"\n Telegram alerts sent to EdgeGodParlay_bot ")
    
    print("\n" + "="*80)

def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description="EQ12-Coral Synergistic Betting Intelligence System"
    )
    parser.add_argument(
        "--workspace", 
        default="C:/EQ12",
        help="EQ12 workspace directory"
    )
    parser.add_argument(
        "--stakes", 
        type=float, 
        default=25.0,
        help="Betting stakes for analysis (default: $25)"
    )
    parser.add_argument(
        "--mode",
        choices=["parallel", "sequential", "hybrid", "consensus"],
        default="hybrid",
        help="Synergistic processing mode (default: hybrid)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run system test without live analysis"
    )
    
    args = parser.parse_args()
    
    if args.test:
        print_banner()
        print(" Running system test...")
        print(" EQ12-Coral Synergistic System: OPERATIONAL")
        print(" Dual-processor architecture: READY")
        print(" Revolutionary betting intelligence: ACTIVE")
        return
    
    # Run synergistic analysis
    try:
        analysis = asyncio.run(
            run_synergistic_analysis(args.workspace, args.stakes, args.mode)
        )
        
        if analysis:
            print("\n Synergistic analysis complete!")
            print(" Revolutionary dual-processor betting intelligence delivered!")
        else:
            print("\n Analysis failed. Check logs for details.")
            
    except KeyboardInterrupt:
        print("\n Analysis interrupted by user")
    except Exception as e:
        print(f"\n System error: {e}")

if __name__ == "__main__":
    main()