import sqlite3
from datetime import datetime
from .database import get_connection

def calculate_clv(odds_taken, closing_odds):
    """Calculates Closing Line Value percentage."""
    if closing_odds <= 0: return 0.0
    # Formula: (Odds Taken / Closing Odds) - 1
    # Example: Taken 2.0, Closed 1.8 -> (2.0/1.8) - 1 = +11.1%
    return ((odds_taken / closing_odds) - 1) * 100

def settle_bets_interactive():
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch pending bets
    cursor.execute("SELECT id, date_placed, selection, market, odds_decimal, stake FROM bets WHERE status = 'PENDING'")
    pending_bets = cursor.fetchall()

    if not pending_bets:
        print("No pending bets to settle.")
        conn.close()
        return

    print("\n📝 Pending Bets:")
    print(f"{'ID':<5} {'Date':<20} {'Selection':<20} {'Odds':<6} {'Stake':<6}")
    print("-" * 60)
    for bet in pending_bets:
        print(f"{bet[0]:<5} {bet[1]:<20} {bet[2]:<20} {bet[4]:<6} ${bet[5]:<6}")

    try:
        bet_id = input("\nEnter Bet ID to settle (or 'q' to quit): ")
        if bet_id.lower() == 'q': return

        # Verify ID
        cursor.execute("SELECT * FROM bets WHERE id = ?", (bet_id,))
        bet = cursor.fetchone()
        if not bet:
            print("Invalid Bet ID.")
            return

        # Input Result
        print("\nResult Options: [W]in, [L]oss, [P]ush, [V]oid")
        result_code = input("Result: ").upper()
        
        status_map = {'W': 'WON', 'L': 'LOST', 'P': 'PUSH', 'V': 'VOID'}
        if result_code not in status_map:
            print("Invalid result code.")
            return
        
        status = status_map[result_code]
        
        # Input Closing Odds
        while True:
            try:
                closing_odds = float(input("Closing Odds (Decimal): "))
                break
            except ValueError:
                print("Invalid number.")

        # Calculate Metrics
        odds_taken = bet[6] # odds_decimal
        stake = bet[7]      # stake
        
        profit = 0.0
        if status == 'WON':
            profit = stake * (odds_taken - 1)
        elif status == 'LOST':
            profit = -stake
        
        clv = calculate_clv(odds_taken, closing_odds)

        # Update DB
        cursor.execute('''
            UPDATE bets 
            SET status = ?, profit = ?, closing_odds = ?, clv = ?, date_settled = ?
            WHERE id = ?
        ''', (
            status, profit, closing_odds, clv, 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            bet_id
        ))
        conn.commit()
        print(f"\n✅ Bet {bet_id} settled as {status}.")
        print(f"Profit: ${profit:.2f}")
        print(f"CLV: {clv:.2f}%")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    settle_bets_interactive()
