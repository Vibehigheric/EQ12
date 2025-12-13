"""
Configuration and Rules for the EQ12 Betting Engine.
"""

# Bankroll Management
BANKROLL = 1000.0  # Starting bankroll
UNIT_SIZE = 10.0   # 1 Unit = $10 (1% of bankroll)
MAX_UNITS_PER_BET = 5.0

# Strategy Filters
MIN_EDGE_PERCENT = 2.0  # Minimum 2% edge required
MIN_ODDS = 1.5          # Minimum decimal odds
MAX_ODDS = 5.0          # Maximum decimal odds (to prevent longshot bias)

# Banned Markets (Negative ROI or High Variance without Edge)
BANNED_MARKETS = [
    "First Basket Scorer",
    "Correct Score",
    "Parlay 4+ Legs"
]

# Sportsbooks
SPORTSBOOKS = [
    "DraftKings",
    "FanDuel",
    "BetMGM",
    "Caesars",
    "Pinnacle",
    "Circa"
]
