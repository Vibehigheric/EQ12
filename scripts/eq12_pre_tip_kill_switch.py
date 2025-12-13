import logging
import time
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EQ12_PreTip_KillSwitch")

try:
    from eq12_player_eligibility_gate import EQ12EligibilityGate
except ImportError:
    logger.error("Could not import EQ12EligibilityGate. Kill switch disabled.")
    EQ12EligibilityGate = None

class EQ12PreTipKillSwitch:
    """
    Final safety check before bet submission.
    Re-validates all players in a slip 15 minutes before tip-off.
    """

    def __init__(self):
        self.gate = EQ12EligibilityGate() if EQ12EligibilityGate else None
        logger.info("🛑 Pre-Tip Kill Switch Initialized")

    def validate_slip(self, slip_data):
        """
        Validate a full betting slip.
        :param slip_data: List of bet dictionaries. Each dict must have 'player', 'team', 'sport'.
        :return: (is_valid: bool, reason: str)
        """
        if not self.gate:
            return True, "WARNING: Gate not available, passing by default."

        logger.info(f"🔍 Re-validating slip with {len(slip_data)} legs...")
        
        for leg in slip_data:
            player = leg.get('player')
            team = leg.get('team')
            sport = leg.get('sport', 'nba')
            
            is_eligible, reason = self.gate.check_eligibility(player, team, sport=sport)
            
            if not is_eligible:
                logger.critical(f"❌ KILL SWITCH ACTIVATED: {player} ({team}) is NO LONGER ELIGIBLE. Reason: {reason}")
                return False, f"Slip KILLED: {player} ineligible ({reason})"

        logger.info("✅ Slip passed final pre-tip validation.")
        return True, "VALID"

if __name__ == "__main__":
    ks = EQ12PreTipKillSwitch()
    
    # Test Slip
    test_slip = [
        {'player': 'Luka Doncic', 'team': 'LAL', 'sport': 'nba'},
        {'player': 'Trae Young', 'team': 'ATL', 'sport': 'nba'} # Should fail
    ]
    
    is_valid, msg = ks.validate_slip(test_slip)
    print(f"Result: {is_valid} | {msg}")
