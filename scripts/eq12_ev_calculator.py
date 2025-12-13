import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EQ12_EV_Calculator")

class EQ12EVCalculator:
    """
    Calculates Expected Value (EV) for bets.
    EV = (Probability of Winning * Amount Won) - (Probability of Losing * Amount Lost)
    """

    @staticmethod
    def american_to_decimal(american_odds):
        """Convert American odds to Decimal odds."""
        try:
            odds = float(american_odds)
            if odds > 0:
                return 1 + (odds / 100)
            else:
                return 1 + (100 / abs(odds))
        except ValueError:
            logger.error(f"Invalid odds format: {american_odds}")
            return 0.0

    @staticmethod
    def implied_probability(american_odds):
        """Calculate implied probability from American odds."""
        decimal = EQ12EVCalculator.american_to_decimal(american_odds)
        if decimal == 0: return 0.0
        return (1 / decimal) * 100

    def calculate_ev(self, model_probability_percent, american_odds):
        """
        Calculate EV percentage.
        :param model_probability_percent: The AI/Model's estimated win probability (0-100).
        :param american_odds: The market odds (e.g., -110, +150).
        :return: EV percentage (positive is good).
        """
        decimal_odds = self.american_to_decimal(american_odds)
        if decimal_odds == 0:
            return -100.0

        prob_win = model_probability_percent / 100.0
        prob_lose = 1.0 - prob_win

        # Amount won per unit wagered (Decimal Odds - 1)
        amount_won = decimal_odds - 1
        amount_lost = 1.0 # We lose our unit stake

        ev = (prob_win * amount_won) - (prob_lose * amount_lost)
        
        ev_percent = ev * 100
        
        logger.info(f"EV Calc: Model Prob {model_probability_percent}%, Odds {american_odds} -> EV: {ev_percent:.2f}%")
        return ev_percent

if __name__ == "__main__":
    calc = EQ12EVCalculator()
    # Test cases
    # 1. Coin flip (50%) at +100 (Even money) -> EV should be 0
    print(f"Test 1 (50% @ +100): {calc.calculate_ev(50, 100):.2f}%")
    
    # 2. Edge case: 55% win rate at -110 (Standard vig)
    # Decimal -110 is 1.909. Win 0.909. Lose 1.
    # (0.55 * 0.909) - (0.45 * 1) = 0.49995 - 0.45 = ~5% EV
    print(f"Test 2 (55% @ -110): {calc.calculate_ev(55, -110):.2f}%")
    
    # 3. Bad bet: 40% win rate at -110
    print(f"Test 3 (40% @ -110): {calc.calculate_ev(40, -110):.2f}%")
