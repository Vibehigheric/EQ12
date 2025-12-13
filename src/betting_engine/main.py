import sys
from . import database
from . import logger
from . import settlement
from . import analytics

def main():
    print("\n🧠 EQ12 200 IQ Betting System")
    print("=============================")
    print("1. Log New Bet")
    print("2. Settle Bets")
    print("3. View Analytics")
    print("4. Initialize Database")
    print("q. Quit")

    while True:
        choice = input("\nSelect Option: ").strip().lower()

        if choice == '1':
            logger.log_bet_interactive()
        elif choice == '2':
            settlement.settle_bets_interactive()
        elif choice == '3':
            analytics.generate_report()
        elif choice == '4':
            database.init_db()
        elif choice == 'q':
            print("Exiting.")
            sys.exit()
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
