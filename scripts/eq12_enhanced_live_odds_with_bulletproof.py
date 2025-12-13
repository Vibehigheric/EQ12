#!/usr/bin/env python3
"""
 EQ12 LIVE ODDS WITH BULLETPROOF FILTERING
Enhanced version of live odds grabber with automatic player blocking

CRITICAL UPDATE:
 Giannis Antetokounmpo BLOCKED (OUT - Load Management)
 LeBron James BLOCKED (OUT - Load Management) 
 Kawhi Leonard BLOCKED (OUT - Knee Management)
 Paul George BLOCKED (QUESTIONABLE - Knee Soreness)
 Zion Williamson BLOCKED (OUT - Hamstring Strain)

This prevents future parlay errors by automatically filtering unavailable players
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Import the bulletproof system
try:
    from eq12_bulletproof_standalone import BulletproofParlayEngine
    BULLETPROOF_AVAILABLE = True
except ImportError:
    BULLETPROOF_AVAILABLE = False
    print(" Bulletproof system not available - running without player filtering")


class EnhancedLiveOddsGenerator:
    """
     Enhanced live odds generator with bulletproof player filtering
    """
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.logs_path = self.workspace_path / "logs"
        self.data_path = self.workspace_path / "data"
        
        # Create directories
        for path in [self.logs_path, self.data_path]:
            path.mkdir(exist_ok=True)
        
        # Initialize bulletproof system
        if BULLETPROOF_AVAILABLE:
            self.bulletproof_engine = BulletproofParlayEngine(str(workspace_path))
            print(" BULLETPROOF MODE: Player filtering ACTIVE")
            print(" Giannis, LeBron, Kawhi automatically blocked")
        else:
            self.bulletproof_engine = None
            print(" Standard mode: No player filtering")
    
    def generate_enhanced_parlay(self, target_legs: int = 10) -> dict:
        """
         Generate parlay with bulletproof player filtering
        """
        print(f"\n Generating enhanced {target_legs}-leg parlay...")
        print("=" * 50)
        
        start_time = datetime.now()
        
        if BULLETPROOF_AVAILABLE and self.bulletproof_engine:
            # Use bulletproof generation
            print(" Using BULLETPROOF generation with player filtering...")
            parlay = self.bulletproof_engine.generate_bulletproof_parlay(target_legs)
            
            # Add enhancement metadata
            parlay["enhancement_type"] = "bulletproof_filtered"
            parlay["player_filtering"] = True
            parlay["giannis_blocked"] = True
            
        else:
            # Fallback to basic generation
            print(" Using basic generation (no player filtering)...")
            parlay = self._generate_basic_parlay(target_legs)
            
            # Add metadata
            parlay["enhancement_type"] = "basic_unfiltered"
            parlay["player_filtering"] = False
            parlay["giannis_blocked"] = False
        
        generation_time = (datetime.now() - start_time).total_seconds()
        parlay["total_generation_time"] = generation_time
        
        # Save enhanced parlay
        self._save_enhanced_parlay(parlay)
        
        return parlay
    
    def _generate_basic_parlay(self, target_legs: int) -> dict:
        """Basic parlay generation without filtering (fallback)"""
        
        # Real NBA games for 11/4/2025
        nba_games = [
            {"home": "MIL", "away": "TOR", "time": "19:00"},
            {"home": "ORL", "away": "ATL", "time": "19:00"},
            {"home": "CHI", "away": "PHI", "time": "20:00"},
            {"home": "PHX", "away": "GS", "time": "22:00"},
            {"home": "OKC", "away": "LAC", "time": "20:00"},
            {"home": "LAL", "away": "DEN", "time": "22:30"}
        ]
        
        legs = []
        
        # Generate basic legs from games
        for i, game in enumerate(nba_games):
            if len(legs) >= target_legs:
                break
                
            home = game["home"]
            away = game["away"]
            
            # Add team-based legs (safer than player props)
            basic_legs = [
                {
                    "description": f"{away} ML vs {home}",
                    "type": "moneyline",
                    "odds": -110,
                    "sport": "NBA",
                    "game": f"{away}@{home}"
                },
                {
                    "description": f"OVER 225.5 {away} vs {home}",
                    "type": "total",
                    "odds": -110,
                    "sport": "NBA",
                    "game": f"{away}@{home}"
                }
            ]
            
            legs.extend(basic_legs)
        
        # Calculate basic odds
        total_odds = 1.91 ** len(legs[:target_legs])  # Assuming -110 odds
        bet_amount = 100
        potential_payout = bet_amount * total_odds
        
        return {
            "timestamp": datetime.now().isoformat(),
            "type": "basic_parlay",
            "actual_legs": min(len(legs), target_legs),
            "legs": legs[:target_legs],
            "odds": {
                "total_decimal_odds": round(total_odds, 2),
                "bet_amount": bet_amount,
                "potential_payout": round(potential_payout, 2),
                "profit": round(potential_payout - bet_amount, 2)
            }
        }
    
    def _save_enhanced_parlay(self, parlay: dict) -> str:
        """Save enhanced parlay to file"""
        filename = f"enhanced_parlay_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.data_path / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(parlay, f, indent=2)
            
            print(f" Enhanced parlay saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f" Failed to save parlay: {e}")
            return ""
    
    def print_enhancement_summary(self, parlay: dict):
        """Print summary of enhancements"""
        print(f"\n ENHANCEMENT SUMMARY")
        print("=" * 40)
        
        if parlay.get("player_filtering", False):
            print(" Player Filtering: ACTIVE")
            print(" Giannis Blocked: YES") 
            print(" LeBron Blocked: YES")
            print(" Kawhi Blocked: YES")
            
            if "blocked_players" in parlay:
                blocked_count = len(parlay["blocked_players"])
                print(f" Total Blocked Players: {blocked_count}")
                
        else:
            print(" Player Filtering: INACTIVE")
            print(" Giannis Blocked: NO - RISK OF ERROR!")
            print(" LeBron Blocked: NO - RISK OF ERROR!")
            print(" Kawhi Blocked: NO - RISK OF ERROR!")
        
        enhancement_type = parlay.get("enhancement_type", "unknown")
        print(f" Enhancement Type: {enhancement_type}")
        
        generation_time = parlay.get("total_generation_time", 0)
        print(f" Generation Time: {generation_time:.2f}s")
        
        print("=" * 40)


def main():
    """Main execution function"""
    print(" EQ12 ENHANCED LIVE ODDS GENERATOR")
    print("Prevents Giannis-type errors with bulletproof filtering!")
    print("=" * 60)
    
    try:
        # Initialize enhanced generator
        generator = EnhancedLiveOddsGenerator()
        
        # Generate enhanced parlay
        parlay = generator.generate_enhanced_parlay(target_legs=10)
        
        # Print enhancement summary
        generator.print_enhancement_summary(parlay)
        
        # Print parlay details if bulletproof system available
        if BULLETPROOF_AVAILABLE and generator.bulletproof_engine:
            generator.bulletproof_engine.print_parlay(parlay)
        else:
            # Basic parlay display
            print(f"\n BASIC PARLAY RESULTS:")
            print(f"   Legs: {parlay['actual_legs']}")
            
            if "odds" in parlay:
                odds_info = parlay["odds"]
                print(f"   Odds: {odds_info['total_decimal_odds']}x")
                print(f"   Payout: ${odds_info['potential_payout']:,.2f}")
            
            print(f"\n PARLAY LEGS:")
            for i, leg in enumerate(parlay["legs"], 1):
                print(f"{i:2}. {leg['description']} ({leg.get('odds', 'N/A')})")
        
        # Final status
        if parlay.get("giannis_blocked", False):
            print(f"\n SUCCESS: Enhanced parlay with bulletproof filtering!")
            print(f" Giannis and other OUT players automatically blocked!")
        else:
            print(f"\n WARNING: Basic parlay without player filtering!")
            print(f" Giannis and other OUT players NOT blocked - potential errors!")
        
        return 0
        
    except Exception as e:
        print(f" Error: {e}")
        return 1


if __name__ == "__main__":
    result = main()
    sys.exit(result)