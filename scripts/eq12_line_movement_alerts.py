import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EQ12_Line_Movement_Alerts")

class EQ12LineMovementDetector:
    """
    Detects significant line movement that might indicate sharp action or injury news.
    """
    
    def __init__(self, threshold_points=1.5, threshold_odds=20):
        self.threshold_points = threshold_points
        self.threshold_odds = threshold_odds
        logger.info("📉 Line Movement Detector Initialized")

    def check_movement(self, old_line, new_line, old_odds, new_odds):
        """
        Compare old and new lines.
        :return: (is_significant: bool, message: str)
        """
        # Check Spread/Total movement
        line_diff = abs(new_line - old_line)
        if line_diff >= self.threshold_points:
            direction = "Moved AGAINST" if new_line < old_line else "Moved WITH"
            return True, f"🚨 LINE MOVE: {old_line} -> {new_line} ({direction})"
            
        # Check Odds movement
        odds_diff = abs(new_odds - old_odds)
        if odds_diff >= self.threshold_odds:
            return True, f"🚨 ODDS SHIFT: {old_odds} -> {new_odds}"
            
        return False, "Stable"

if __name__ == "__main__":
    detector = EQ12LineMovementDetector()
    
    # Test: Significant line move
    print(detector.check_movement(212.5, 215.0, -110, -110))
    
    # Test: Significant odds move
    print(detector.check_movement(212.5, 212.5, -110, -140))
    
    # Test: Stable
    print(detector.check_movement(212.5, 212.5, -110, -115))
