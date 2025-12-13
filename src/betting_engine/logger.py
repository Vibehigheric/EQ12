import argparse
import sys
from datetime import datetime
from .database import get_connection
from . import config

def validate_bet(stake, odds, market, edge):
    """Enforces the 200 IQ system rules."""
    
    # Rule 1: Bankroll Management
    units = stake / config.UNIT_SIZE
    if units > config.MAX_UNITS_PER_BET:
        print(f"❌ REJECTED: Stake {stake} ({units}u) exceeds max limit of {config.MAX_UNITS_PER_BET}u.")
        return False

    # Rule 2: Banned Markets
    if market in config.BANNED_MARKETS:
        print(f"❌ REJECTED: Market '{market}' is in the BANNED list.")
        return False

    # Rule 3: Minimum Edge
    if edge < config.MIN_EDGE_PERCENT:
        print(f"❌ REJECTED: Edge {edge}% is below minimum threshold of {config.MIN_EDGE_PERCENT}%.")
        return False

    # Rule 4: Odds Range
    if not (config.MIN_ODDS <= odds <= config.MAX_ODDS):
        print(f"⚠️ WARNING: Odds {odds} are outside recommended range ({config.MIN_ODDS}-{config.MAX_ODDS}). Proceed with caution.")
        # We allow it but warn, as sometimes value exists outside.
    
    return True

def log_bet_interactive():
    print("\n🧠 EQ12 200 IQ Bet Logger")
    print("==========================")

    try:
        sport = input("Sport/League (e.g., NBA): ").strip()
        market = input("Market (e.g., Moneyline): ").strip()
        selection = input("Selection (e.g., Lakers): ").strip()
        
        while True:
            try:
                odds = float(input("Decimal Odds: "))
                break
            except ValueError:
                print("Invalid number.")

        while True:
            try:
                stake = float(input(f"Stake ($) [Unit Size: ${config.UNIT_SIZE}]: "))
                break
            except ValueError:
                print("Invalid number.")

        sportsbook = input(f"Sportsbook ({', '.join(config.SPORTSBOOKS)}): ").strip()
        
        while True:
            try:
                edge = float(input("Expected Edge (%): "))
                break
            except ValueError:
                print("Invalid number.")

        model_name = input("Model Name: ").strip()
        reasoning = input("Reasoning/Notes: ").strip()
        tag = input("Tag (Optional): ").strip()

        # Validation
        if not validate_bet(stake, odds, market, edge):
            print("🚫 Bet Logging Aborted due to rule violation.")
            return

        # Calculate Implied Probability
        implied_prob = (1 / odds) * 100

        # Confirm
        print("\n--- Bet Summary ---")
        print(f"Selection: {selection} ({market})")
        print(f"Odds: {odds}")
        print(f"Stake: ${stake}")
        print(f"Edge: {edge}%")
        confirm = input("Log this bet? (y/n): ").lower()

        if confirm == 'y':
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bets (
                    date_placed, sport, league, market, selection, odds_decimal, 
                    stake, sportsbook, implied_prob, expected_edge, reasoning, 
                    model_name, tag
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                sport, sport, market, selection, odds, stake, sportsbook,
                implied_prob, edge, reasoning, model_name, tag
            ))
            conn.commit()
            conn.close()
            print("✅ Bet Logged Successfully.")
        else:
            print("❌ Bet Discarded.")

    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    log_bet_interactive()
