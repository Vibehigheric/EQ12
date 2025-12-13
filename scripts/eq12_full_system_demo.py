import logging
import time
from eq12_player_eligibility_gate import EQ12EligibilityGate
from eq12_ev_calculator import EQ12EVCalculator
from eq12_bankroll_manager import EQ12KellyBankrollManager
from eq12_pre_tip_kill_switch import EQ12PreTipKillSwitch
from eq12_performance_tracker import EQ12PerformanceTracker

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EQ12_Full_System_Demo")

def run_full_system_demo():
    logger.info("🚀 STARTING EQ12 FULL SYSTEM DEMO")
    
    # 1. Initialize Components
    gate = EQ12EligibilityGate()
    ev_calc = EQ12EVCalculator()
    bankroll_mgr = EQ12KellyBankrollManager(total_bankroll=5000)
    kill_switch = EQ12PreTipKillSwitch()
    tracker = EQ12PerformanceTracker()
    
    # 2. Define Candidates (One Good, One Bad)
    candidates = [
        {'player': 'Luka Doncic', 'team': 'LAL', 'prop': 'Over 28.5 Points', 'odds': -110, 'model_prob': 58},
        {'player': 'Trae Young', 'team': 'ATL', 'prop': 'Over 24.5 Points', 'odds': -110, 'model_prob': 60}
    ]
    
    logger.info(f"📋 Processing {len(candidates)} candidates...")
    
    valid_bets = []
    
    for cand in candidates:
        player = cand['player']
        logger.info(f"\n--- Analyzing {player} ---")
        
        # 3. Gate Check
        is_eligible, reason = gate.check_eligibility(player, cand['team'])
        if not is_eligible:
            logger.warning(f"❌ GATE BLOCK: {player} -> {reason}")
            continue
        logger.info(f"✅ GATE PASS: {player}")
        
        # 4. EV Calculation
        ev = ev_calc.calculate_ev(cand['model_prob'], cand['odds'])
        if ev <= 0:
            logger.warning(f"❌ LOW EV: {ev:.2f}%")
            continue
        logger.info(f"✅ POSITIVE EV: {ev:.2f}%")
        
        # 5. Stake Calculation
        stake = bankroll_mgr.calculate_stake(ev, cand['odds'], cand['model_prob'])
        if stake <= 0:
            logger.warning("❌ ZERO STAKE RECOMMENDED")
            continue
        logger.info(f"💰 STAKE SIZED: ${stake:.2f}")
        
        # Add to valid bets
        cand['stake'] = stake
        cand['ev'] = ev
        valid_bets.append(cand)
        
    # 6. Pre-Tip Kill Switch (Simulate 15 mins before game)
    logger.info("\n⏳ Simulating T-15 Minute Kill Switch Check...")
    if valid_bets:
        is_valid, msg = kill_switch.validate_slip(valid_bets)
        if is_valid:
            logger.info("✅ SLIP CONFIRMED VALID")
            
            # 7. Log Bets
            for bet in valid_bets:
                tracker.log_bet(bet)
                logger.info(f"📝 BET LOGGED: {bet['player']} - ${bet['stake']}")
        else:
            logger.critical(f"🛑 SLIP KILLED: {msg}")
    else:
        logger.warning("⚠️ No valid bets to process.")
        
    logger.info("\n🏁 DEMO COMPLETE")

if __name__ == "__main__":
    run_full_system_demo()
