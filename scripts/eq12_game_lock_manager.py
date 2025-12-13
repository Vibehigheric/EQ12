import logging
from datetime import datetime, timedelta
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EQ12_Game_Lock_Manager")

class EQ12GameLockManager:
    """
    Manages hard stops for betting based on game start times.
    Enforces a 'No Bet Zone' X minutes before tip-off.
    """
    
    def __init__(self, lock_minutes_before_tip=10):
        self.lock_minutes = lock_minutes_before_tip
        logger.info(f"🔒 Game Lock Manager Initialized (Lock: T-{self.lock_minutes}m)")

    def check_lock_status(self, game_start_iso):
        """
        Check if a game is locked for betting.
        :param game_start_iso: ISO format start time string (e.g., '2025-10-24T19:30:00Z')
        :return: (is_locked: bool, reason: str)
        """
        try:
            # Parse ISO time (handling Z for UTC)
            if game_start_iso.endswith('Z'):
                game_start_iso = game_start_iso[:-1]
            
            game_start = datetime.fromisoformat(game_start_iso)
            now = datetime.utcnow() # Assuming UTC for simplicity, ideally use timezone aware
            
            time_to_tip = (game_start - now).total_seconds() / 60.0
            
            if time_to_tip <= 0:
                return True, "LOCKED: Game In Progress / Started"
            
            if time_to_tip <= self.lock_minutes:
                return True, f"LOCKED: Within {self.lock_minutes}m Pre-Tip Window ({int(time_to_tip)}m left)"
            
            return False, f"OPEN: {int(time_to_tip)}m until tip"
            
        except Exception as e:
            logger.error(f"Error parsing game time: {e}")
            return True, "LOCKED: Error parsing time (Safety Lock)"

if __name__ == "__main__":
    locker = EQ12GameLockManager(lock_minutes_before_tip=15)
    
    # Test Cases
    future_game = (datetime.utcnow() + timedelta(minutes=60)).isoformat() + "Z"
    soon_game = (datetime.utcnow() + timedelta(minutes=10)).isoformat() + "Z"
    past_game = (datetime.utcnow() - timedelta(minutes=5)).isoformat() + "Z"
    
    print(f"Future: {locker.check_lock_status(future_game)}")
    print(f"Soon:   {locker.check_lock_status(soon_game)}")
    print(f"Past:   {locker.check_lock_status(past_game)}")
