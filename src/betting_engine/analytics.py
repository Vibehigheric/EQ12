import sqlite3
import pandas as pd
from .database import get_connection

def generate_report():
    conn = get_connection()
    
    # Load settled bets into DataFrame
    query = "SELECT * FROM bets WHERE status != 'PENDING'"
    try:
        df = pd.read_sql_query(query, conn)
    except Exception:
        # Fallback if pandas not installed or other error
        print("Error loading data. Ensure pandas is installed.")
        conn.close()
        return

    if df.empty:
        print("No settled bets found for analysis.")
        conn.close()
        return

    print("\n📊 EQ12 Performance Analytics")
    print("============================")

    # 1. High Level Metrics
    total_bets = len(df)
    total_profit = df['profit'].sum()
    total_stake = df['stake'].sum()
    roi = (total_profit / total_stake) * 100 if total_stake > 0 else 0.0
    
    wins = len(df[df['status'] == 'WON'])
    win_rate = (wins / total_bets) * 100

    avg_clv = df['clv'].mean()

    print(f"Total Bets:   {total_bets}")
    print(f"Total Profit: ${total_profit:.2f}")
    print(f"ROI:          {roi:.2f}%")
    print(f"Win Rate:     {win_rate:.2f}%")
    print(f"Avg CLV:      {avg_clv:.2f}%")

    # 2. By Sport
    print("\n--- Performance by Sport ---")
    sport_stats = df.groupby('sport').agg({
        'profit': 'sum',
        'stake': 'sum',
        'clv': 'mean',
        'status': lambda x: (x == 'WON').mean() * 100
    }).rename(columns={'status': 'win_rate'})
    sport_stats['roi'] = (sport_stats['profit'] / sport_stats['stake']) * 100
    print(sport_stats[['profit', 'roi', 'win_rate', 'clv']])

    # 3. By Market
    print("\n--- Performance by Market ---")
    market_stats = df.groupby('market').agg({
        'profit': 'sum',
        'stake': 'sum',
        'clv': 'mean',
        'status': lambda x: (x == 'WON').mean() * 100
    }).rename(columns={'status': 'win_rate'})
    market_stats['roi'] = (market_stats['profit'] / market_stats['stake']) * 100
    print(market_stats[['profit', 'roi', 'win_rate', 'clv']])

    # 4. By Model
    if 'model_name' in df.columns:
        print("\n--- Performance by Model ---")
        model_stats = df.groupby('model_name').agg({
            'profit': 'sum',
            'stake': 'sum',
            'clv': 'mean',
            'status': lambda x: (x == 'WON').mean() * 100
        }).rename(columns={'status': 'win_rate'})
        model_stats['roi'] = (model_stats['profit'] / model_stats['stake']) * 100
        print(model_stats[['profit', 'roi', 'win_rate', 'clv']])

    conn.close()

if __name__ == "__main__":
    generate_report()
