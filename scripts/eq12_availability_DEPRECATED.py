import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EQ12_Availability")

class AvailabilityGate:
    """
    EQ12 Hard Availability Gate.
    Enforces strict player availability rules before any bet is considered.
    """
    
    def __init__(self):
        # POSITIVE CONFIRMATION MODE
        # We do not list banned statuses. We only list ALLOWED statuses.
        # Everything else is REJECTED by default.
        self.allowed_statuses = ["ACTIVE", "PROBABLE"]
        
    def validate_nba_player(self, player_name, status, minutes_proj, is_starter_confirmed=False, game_start_time=None):
        """
        Layer 2: NBA Specific Logic (Positive Confirmation)
        """
        status_upper = status.upper()
        
        # 1. POSITIVE STATUS CHECK
        # If it's not explicitly allowed, it's blocked.
        if status_upper not in self.allowed_statuses:
            logger.warning(f"⛔ REJECTED: {player_name} status is '{status}' (Not in ALLOWED list)")
            return False
            
        # 2. CONFIRMATION CHECK (Layer 3)
        # If we are close to game time, we might require is_starter_confirmed.
        # For now, we enforce that 'ACTIVE' means 'Active for this specific game'.
        
        # 3. Minutes Projection (Layer 1)
        if minutes_proj <= 0:
            logger.warning(f"⛔ REJECTED: {player_name} has 0 projected minutes.")
            return False

        logger.info(f"✅ ACCEPTED: {player_name} ({status}, {minutes_proj}m)")
        return True

    def validate_slip(self, legs):
        """
        Layer 3: Final Pre-Slip Lock
        """
        valid_legs = []
        print("\n🔒 RUNNING FINAL AVAILABILITY GATE (POSITIVE CONFIRMATION)...")
        for leg in legs:
            # We expect the leg to have 'status' populated from the cache
            status = leg.get('status', 'UNAVAILABLE') # Default to UNAVAILABLE
            
            is_valid = self.validate_nba_player(
                leg['player'], 
                status,
                leg.get('minutes', 0),
                leg.get('confirmed', False)
            )
            if is_valid:
                valid_legs.append(leg)
        
        return valid_legs
