#!/usr/bin/env python3
"""
Educational Cryptocurrency Trading Bot Demonstration
This is for EDUCATIONAL PURPOSES ONLY - NOT for live trading!

Buffalo NY Crypto Education Kit
"""

import json
import time
import random
from datetime import datetime

class EducationalTradingBot:
    def __init__(self):
        self.balance_usd = 1000.0  # Demo balance
        self.balance_btc = 0.0
        self.btc_price = 45000.0  # Demo price
        self.trades = []
        
        print(" Educational Trading Bot Initialized")
        print("  This is for DEMONSTRATION ONLY")
        print(" Demo balance: $1000 USD")
    
    def simulate_market_data(self):
        """Simulate cryptocurrency price movements"""
        # Random price movement (demo only)
        change_percent = random.uniform(-0.02, 0.02)  # 2% movement
        self.btc_price *= (1 + change_percent)
        return self.btc_price
    
    def simple_strategy(self):
        """Demo trading strategy: Buy low, sell high"""
        current_price = self.simulate_market_data()
        
        # Simple moving average simulation
        price_history = [current_price * random.uniform(0.98, 1.02) for _ in range(10)]
        avg_price = sum(price_history) / len(price_history)
        
        decision = "HOLD"
        
        # Buy if price is below average and we have USD
        if current_price < avg_price * 0.98 and self.balance_usd > 100:
            buy_amount = min(self.balance_usd * 0.1, 200)  # Buy 10% or $200 max
            btc_bought = buy_amount / current_price
            
            self.balance_usd -= buy_amount
            self.balance_btc += btc_bought
            decision = f"BUY ${buy_amount:.2f} worth of BTC"
            
            self.trades.append({
                "timestamp": datetime.now().isoformat(),
                "action": "BUY",
                "amount_usd": buy_amount,
                "btc_amount": btc_bought,
                "price": current_price
            })
        
        # Sell if price is above average and we have BTC
        elif current_price > avg_price * 1.02 and self.balance_btc > 0.001:
            btc_to_sell = self.balance_btc * 0.2  # Sell 20%
            usd_received = btc_to_sell * current_price
            
            self.balance_btc -= btc_to_sell
            self.balance_usd += usd_received
            decision = f"SELL {btc_to_sell:.6f} BTC for ${usd_received:.2f}"
            
            self.trades.append({
                "timestamp": datetime.now().isoformat(),
                "action": "SELL",
                "amount_usd": usd_received,
                "btc_amount": btc_to_sell,
                "price": current_price
            })
        
        return decision, current_price
    
    def run_demo(self, cycles=20):
        """Run trading bot demonstration"""
        print(f"\n Running {cycles} trading cycles...")
        print(" Strategy: Simple mean reversion demo")
        print("=" * 50)
        
        for i in range(cycles):
            decision, price = self.simple_strategy()
            total_value = self.balance_usd + (self.balance_btc * price)
            
            print(f"Cycle {i+1:2d}: BTC ${price:,.2f} | {decision}")
            print(f"         Balance: ${self.balance_usd:.2f} USD + {self.balance_btc:.6f} BTC")
            print(f"         Total Value: ${total_value:.2f}")
            print("-" * 40)
            
            time.sleep(0.5)  # Demo delay
        
        # Final summary
        final_value = self.balance_usd + (self.balance_btc * price)
        profit_loss = final_value - 1000
        
        print("\n DEMO COMPLETE")
        print(f"Starting Value: $1000.00")
        print(f"Final Value: ${final_value:.2f}")
        print(f"Profit/Loss: ${profit_loss:+.2f} ({profit_loss/1000*100:+.1f}%)")
        print(f"Total Trades: {len(self.trades)}")
        
        # Save trade log
        with open("demo_trade_log.json", "w") as f:
            json.dump(self.trades, f, indent=2)
        print(" Trade log saved to demo_trade_log.json")
        
        print("\n  REMEMBER: This is educational demonstration only!")
        print(" Learn more about real trading strategies before investing")

if __name__ == "__main__":
    print(" Cryptocurrency Trading Bot Education")
    print("Created for Buffalo NY Crypto Education Kit\n")
    
    bot = EducationalTradingBot()
    bot.run_demo()
    
    print("\n Questions? Contact your local Buffalo crypto education provider!")
