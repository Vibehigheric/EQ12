#!/usr/bin/env python3
"""
EQ12 SD Card Cryptocurrency Suite Generator
Automated system for generating crypto trading suite contents targeting $130 profit per unit
Buffalo 14215 local SEO optimization and multi-platform marketplace automation
"""

import argparse
import json
import logging
import os
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Force UTF-8 encoding (hardened)
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Set UTF-8 environment
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LC_ALL"] = "en_US.UTF-8"
os.environ["LANG"] = "en_US.UTF-8"

class CryptoSDCardGenerator:
    def __init__(self):
        self.base_path = Path("C:/EQ12")
        self.output_path = self.base_path / "data" / "sdcard_packages"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Revenue targets
        self.unit_cost = 19.00  # SD card + packaging
        self.selling_price = 149.00
        self.profit_per_unit = self.selling_price - self.unit_cost  # $130 profit
        self.daily_target_units = 5  # $650/day revenue
        
        # Buffalo 14215 local advantage
        self.location = "Buffalo, NY 14215"
        self.shipping_zone = "Northeast US"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8',
            handlers=[
                logging.FileHandler(self.base_path / "logs" / "sdcard_generator.log", encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def safe_filename(self, name: str) -> str:
        """Generate safe filename without problematic characters"""
        name = re.sub(r'[^\w\s\-\.]', '_', name)
        return name[:100]  # Limit length
    
    def safe_json_dump(self, data: Dict, path: Path) -> None:
        """UTF-8 safe JSON writing with no BOM"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def generate_crypto_guide_html(self) -> str:
        """Generate cryptocurrency beginner guide HTML"""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cryptocurrency Trading Starter Kit - Buffalo NY</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; }}
        .highlight {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
        .warning {{ background: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 20px 0; }}
        .success {{ background: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0; }}
        code {{ background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }}
        .buffalo-local {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1> Cryptocurrency Trading Starter Kit</h1>
        
        <div class="buffalo-local">
            <h3> Local Buffalo, NY Support Available</h3>
            <p><strong>Fast 2-day shipping from {self.location}</strong></p>
            <p>Local pickup available for Buffalo area customers</p>
        </div>
        
        <div class="highlight">
            <h3> What's Included in Your Kit</h3>
            <ul>
                <li>Complete cryptocurrency education guide</li>
                <li>Portfolio tracking spreadsheet</li>
                <li>Risk management calculator</li>
                <li>Trading strategy templates</li>
                <li>Security best practices checklist</li>
                <li>Bonus: AI trading bot demonstration script</li>
            </ul>
        </div>
        
        <h2> Getting Started</h2>
        
        <h3>Step 1: Understand the Basics</h3>
        <p>Cryptocurrency is digital money secured by cryptography. The most popular cryptocurrencies include:</p>
        <ul>
            <li><strong>Bitcoin (BTC)</strong> - The original cryptocurrency</li>
            <li><strong>Ethereum (ETH)</strong> - Platform for smart contracts</li>
            <li><strong>Other altcoins</strong> - Various specialized cryptocurrencies</li>
        </ul>
        
        <h3>Step 2: Set Up Your Portfolio Tracker</h3>
        <p>Use the included Excel spreadsheet to track your investments:</p>
        <ol>
            <li>Open <code>portfolio_tracker.xlsx</code></li>
            <li>Enter your cryptocurrency purchases</li>
            <li>Monitor gains/losses automatically</li>
            <li>Set price alerts for key levels</li>
        </ol>
        
        <div class="warning">
            <h3> Important Risk Warning</h3>
            <p>Cryptocurrency trading involves significant risk. Never invest more than you can afford to lose. Always do your own research before making any investment decisions.</p>
        </div>
        
        <h3>Step 3: Security Best Practices</h3>
        <ul>
            <li>Use hardware wallets for large amounts</li>
            <li>Enable 2FA on all exchanges</li>
            <li>Keep private keys offline and secure</li>
            <li>Never share your seed phrases</li>
        </ul>
        
        <h3>Step 4: Trading Strategies</h3>
        <p>Review the included strategy templates:</p>
        <ul>
            <li><strong>DCA (Dollar Cost Averaging)</strong> - Steady, regular purchases</li>
            <li><strong>HODLing</strong> - Long-term holding strategy</li>
            <li><strong>Swing Trading</strong> - Medium-term position trading</li>
            <li><strong>Technical Analysis</strong> - Chart-based trading decisions</li>
        </ul>
        
        <div class="success">
            <h3> Bonus: AI Trading Bot Demo</h3>
            <p>Your kit includes a Python demonstration script showing how automated trading bots work. This is for educational purposes only.</p>
            <p>File: <code>auto_trading_bot_demo.py</code></p>
        </div>
        
        <h2> Additional Resources</h2>
        <ul>
            <li>CoinGecko - Cryptocurrency market data</li>
            <li>TradingView - Technical analysis charts</li>
            <li>Reddit r/cryptocurrency - Community discussions</li>
            <li>YouTube crypto education channels</li>
        </ul>
        
        <h2> Support</h2>
        <p>Questions about your cryptocurrency starter kit? We're here to help!</p>
        <p><strong>Local Buffalo, NY pickup and support available</strong></p>
        <p>Email: support@eq12crypto.local</p>
        
        <div class="highlight">
            <p><strong>This kit was created in Buffalo, NY and shipped with  from the 14215 area</strong></p>
            <p>Supporting local entrepreneurship and cryptocurrency education</p>
        </div>
    </div>
</body>
</html>"""
        return html_content
    
    def generate_trading_bot_demo(self) -> str:
        """Generate educational trading bot demonstration"""
        bot_code = '''#!/usr/bin/env python3
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
        print(f"\\n Running {cycles} trading cycles...")
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
        
        print("\\n DEMO COMPLETE")
        print(f"Starting Value: $1000.00")
        print(f"Final Value: ${final_value:.2f}")
        print(f"Profit/Loss: ${profit_loss:+.2f} ({profit_loss/1000*100:+.1f}%)")
        print(f"Total Trades: {len(self.trades)}")
        
        # Save trade log
        with open("demo_trade_log.json", "w") as f:
            json.dump(self.trades, f, indent=2)
        print(" Trade log saved to demo_trade_log.json")
        
        print("\\n  REMEMBER: This is educational demonstration only!")
        print(" Learn more about real trading strategies before investing")

if __name__ == "__main__":
    print(" Cryptocurrency Trading Bot Education")
    print("Created for Buffalo NY Crypto Education Kit\\n")
    
    bot = EducationalTradingBot()
    bot.run_demo()
    
    print("\\n Questions? Contact your local Buffalo crypto education provider!")
'''
        return bot_code
    
    def generate_portfolio_tracker_data(self) -> Dict:
        """Generate portfolio tracking spreadsheet data"""
        return {
            "portfolio_template": {
                "columns": ["Date", "Cryptocurrency", "Amount", "Purchase_Price", "Current_Price", "Value_USD", "Profit_Loss", "Percentage_Change"],
                "sample_data": [
                    ["2024-01-01", "Bitcoin", 0.025, 45000, 47000, 1175, 50, 4.4],
                    ["2024-01-15", "Ethereum", 1.5, 2800, 3000, 4500, 300, 7.1],
                    ["2024-02-01", "Cardano", 1000, 0.55, 0.48, 480, -70, -12.7]
                ],
                "formulas": {
                    "Value_USD": "=Amount * Current_Price", 
                    "Profit_Loss": "=Value_USD - (Amount * Purchase_Price)",
                    "Percentage_Change": "=(Current_Price - Purchase_Price) / Purchase_Price * 100"
                },
                "risk_levels": {
                    "Conservative": "5-15% crypto allocation",
                    "Moderate": "15-25% crypto allocation", 
                    "Aggressive": "25%+ crypto allocation"
                }
            }
        }
    
    def generate_risk_management_guide(self) -> str:
        """Generate risk management documentation"""
        return """# Cryptocurrency Risk Management Guide

##  Essential Risk Management Rules

### 1. Position Sizing
- Never risk more than 2-5% of your total portfolio on a single trade
- Allocate only what you can afford to lose completely
- Start with small amounts while learning

### 2. Diversification
- Don't put all money in one cryptocurrency
- Spread investments across different types of crypto
- Consider traditional investments alongside crypto

### 3. Stop-Loss Orders
- Set stop-loss at 10-20% below purchase price
- Stick to your stop-loss - don't move it lower
- Take profits at predetermined levels

### 4. Dollar-Cost Averaging (DCA)
- Buy fixed dollar amounts regularly
- Reduces impact of volatility
- Builds position over time

### 5. Security Measures
- Use hardware wallets for large amounts
- Enable 2-factor authentication everywhere
- Never share private keys or seed phrases
- Keep backups in secure, separate locations

### 6. Emotional Discipline
- Don't trade based on emotions
- Have a plan before you trade
- Don't FOMO (Fear of Missing Out)
- Take breaks from watching prices

### 7. Tax Considerations
- Keep detailed records of all trades
- Understand crypto tax laws in your area
- Consider tax implications of trading strategies
- Consult with tax professional if needed

##  Portfolio Allocation Examples

### Conservative (5-10% crypto)
- 80% Traditional investments
- 15% Cash/Bonds
- 5% Cryptocurrency

### Moderate (15-20% crypto)
- 70% Traditional investments
- 10% Cash/Bonds
- 20% Cryptocurrency

### Aggressive (25%+ crypto)
- 60% Traditional investments
- 15% Cash/Bonds
- 25% Cryptocurrency

##  Red Flags to Avoid
- Promises of guaranteed returns
- "Get rich quick" schemes
- Pressure to invest immediately
- Unlicensed investment advisors
- Requests for private keys or passwords

Remember: This kit is for educational purposes. Always do your own research and consider consulting with financial advisors before making investment decisions.

Created with  in Buffalo, NY 14215
"""
    
    def create_sdcard_package(self, package_name: str = "crypto_trading_suite") -> Path:
        """Create complete SD card package"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_dir = self.output_path / f"{package_name}_{timestamp}"
        package_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Creating SD card package: {package_name}")
        
        # Generate all content files
        files_created = []
        
        # 1. Main HTML guide
        html_path = package_dir / "crypto_starter_guide.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_crypto_guide_html())
        files_created.append(html_path.name)
        
        # 2. Trading bot demo
        bot_path = package_dir / "auto_trading_bot_demo.py"
        with open(bot_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_trading_bot_demo())
        files_created.append(bot_path.name)
        
        # 3. Portfolio tracker data
        portfolio_path = package_dir / "portfolio_tracker_data.json"
        self.safe_json_dump(self.generate_portfolio_tracker_data(), portfolio_path)
        files_created.append(portfolio_path.name)
        
        # 4. Risk management guide
        risk_path = package_dir / "risk_management_guide.md"
        with open(risk_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_risk_management_guide())
        files_created.append(risk_path.name)
        
        # 5. README with setup instructions
        readme_content = f"""# Cryptocurrency Trading Starter Kit
## Buffalo, NY Local Crypto Education

###  Package Contents:
- crypto_starter_guide.html - Complete beginner guide (open in web browser)
- auto_trading_bot_demo.py - Educational trading bot demonstration
- portfolio_tracker_data.json - Portfolio tracking template data
- risk_management_guide.md - Essential risk management strategies

###  Quick Start:
1. Open crypto_starter_guide.html in your web browser
2. Follow the step-by-step instructions
3. Use portfolio_tracker_data.json to set up your tracking spreadsheet
4. Review risk_management_guide.md before investing

###  Important:
This kit is for educational purposes only. Always do your own research and never invest more than you can afford to lose.

###  Support:
Local Buffalo, NY support available
Created with  in Buffalo 14215

Package generated: {timestamp}
Retail value: ${self.selling_price}
Your investment in crypto education: Priceless!
"""
        
        readme_path = package_dir / "README.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        files_created.append(readme_path.name)
        
        # Create package info for tracking
        package_info = {
            "package_name": package_name,
            "creation_date": timestamp,
            "location": self.location,
            "files_included": files_created,
            "target_market": "Cryptocurrency beginners",
            "pricing": {
                "cost": self.unit_cost,
                "retail_price": self.selling_price,
                "profit_margin": self.profit_per_unit,
                "roi_percentage": (self.profit_per_unit / self.unit_cost) * 100
            },
            "local_advantage": {
                "location": self.location,
                "shipping_zone": self.shipping_zone,
                "two_day_shipping": True,
                "local_pickup": True
            }
        }
        
        info_path = package_dir / "package_info.json"
        self.safe_json_dump(package_info, info_path)
        
        self.logger.info(f"SD card package created successfully: {package_dir}")
        self.logger.info(f"Files created: {len(files_created)}")
        self.logger.info(f"Target profit per unit: ${self.profit_per_unit}")
        
        return package_dir
    
    def generate_marketplace_listings(self, package_path: Path) -> Dict:
        """Generate optimized marketplace listings for eBay, Etsy, Facebook"""
        listings = {}
        
        # eBay listing
        listings["ebay"] = {
            "title": "Cryptocurrency Trading Starter Kit - Complete Beginner Guide - Fast Buffalo NY Shipping",
            "description": f"""
 COMPLETE CRYPTOCURRENCY TRADING STARTER KIT

Perfect for beginners wanting to learn cryptocurrency trading safely and systematically!

 WHAT'S INCLUDED:
 Complete beginner-friendly guide (HTML format)
 Portfolio tracking templates and data
 Risk management strategies guide
 Educational trading bot demonstration (Python)
 Security best practices checklist
 Ready-to-use on any computer

 FAST LOCAL SHIPPING FROM BUFFALO, NY 14215
 2-day Priority shipping within Northeast US
 Local pickup available for Buffalo area

 PERFECT FOR:
- Crypto beginners wanting structured learning
- Investors seeking risk management education  
- Anyone interested in automated trading concepts
- Students learning about digital assets

 EDUCATIONAL PURPOSE: All content is for learning only. Not financial advice.

 WHY CHOOSE OUR KIT:
- Created by local Buffalo crypto educators
- Comprehensive yet beginner-friendly
- Includes practical tools and templates
- Focus on safety and risk management

 SHIPS ON SD CARD - Works on any computer
 Money-back guarantee if not satisfied

#cryptocurrency #bitcoin #trading #education #buffalo #startup
            """,
            "price": self.selling_price,
            "shipping": "FREE 2-day Priority from Buffalo NY",
            "tags": ["cryptocurrency", "bitcoin", "trading", "education", "buffalo", "beginner", "kit", "guide"]
        }
        
        # Etsy listing (more personal/educational focus)
        listings["etsy"] = {
            "title": "Handcrafted Crypto Education Kit - Buffalo NY Local Business - Digital Trading Guide",
            "description": f"""
 Handcrafted Cryptocurrency Education Package

Created with  by local Buffalo entrepreneurs for beginners wanting to learn crypto safely!

 THIS UNIQUE KIT INCLUDES:
 Beautifully designed HTML guide you can open in any browser
 Personal portfolio tracking system with templates
 Educational Python trading bot for learning (not live trading!)
 Comprehensive risk management guide
 All content created locally in Buffalo, NY

 SUPPORTING LOCAL BUFFALO BUSINESS
 Fast shipping from 14215 zip code
 Personal customer support from creators

PERFECT GIFT for:
- College students learning about digital assets
- Friends interested in cryptocurrency
- Anyone wanting structured crypto education
- Tech enthusiasts exploring automation

 WHAT MAKES US SPECIAL:
- Not a mass-produced course - personally crafted content
- Focus on safety and education over "get rich quick" 
- Real local Buffalo business supporting community
- Genuine educational value with practical tools

 Delivered on quality SD card - works on Mac, PC, Linux
 Educational content only - not financial advice
 Personal guarantee from Buffalo creators

Supporting local entrepreneurship one crypto education at a time! 
            """,
            "price": self.selling_price,
            "category": "Digital Education",
            "tags": ["crypto education", "buffalo ny", "local business", "digital guide", "trading education", "handmade", "small business"]
        }
        
        # Facebook Marketplace (local focus)
        listings["facebook"] = {
            "title": "Cryptocurrency Education Kit - Local Buffalo Creator - $149",
            "description": f"""
 Complete Cryptocurrency Trading Education Kit
Created locally in Buffalo, NY 14215

Perfect for beginners! Includes everything you need to learn crypto trading safely:
 Complete step-by-step guide
 Portfolio tracking tools  
 Risk management strategies
 Educational trading bot demo
 Security best practices

 LOCAL ADVANTAGE:
- Made in Buffalo by local entrepreneurs
- Fast local delivery or pickup available
- Personal support from creators
- Support local 14215 business!

 Price: ${self.selling_price}
 Includes everything on SD card
 Perfect for crypto beginners

Can meet anywhere in Buffalo area or ship fast within WNY.

Local pickup locations:
- Downtown Buffalo
- Elmwood Village  
- University area
- Suburbs by arrangement

Message me for questions or to arrange pickup!

#BuffaloNY #CryptocurrencyEducation #LocalBusiness #TradingKit #WNY #BuffaloSmallBusiness
            """,
            "price": self.selling_price,
            "location": "Buffalo, NY 14215",
            "category": "Electronics & Tech > Software"
        }
        
        return listings

def main():
    parser = argparse.ArgumentParser(description='EQ12 SD Card Cryptocurrency Suite Generator')
    parser.add_argument('--package-name', default='crypto_trading_suite', help='Package name')
    parser.add_argument('--generate-listings', action='store_true', help='Generate marketplace listings')
    parser.add_argument('--output-dir', help='Custom output directory')
    
    args = parser.parse_args()
    
    generator = CryptoSDCardGenerator()
    
    # Override output directory if specified
    if args.output_dir:
        generator.output_path = Path(args.output_dir)
        generator.output_path.mkdir(parents=True, exist_ok=True)
    
    print(" EQ12 SD Card Cryptocurrency Suite Generator")
    print("=" * 50)
    print(f"Target location: {generator.location}")
    print(f"Profit per unit: ${generator.profit_per_unit}")
    print(f"Daily target: {generator.daily_target_units} units (${generator.daily_target_units * generator.profit_per_unit}/day)")
    print()
    
    # Create package
    package_path = generator.create_sdcard_package(args.package_name)
    print(f" Package created: {package_path}")
    
    # Generate marketplace listings
    if args.generate_listings:
        listings = generator.generate_marketplace_listings(package_path)
        
        listings_path = package_path / "marketplace_listings.json"
        generator.safe_json_dump(listings, listings_path)
        
        print(f" Marketplace listings generated: {listings_path}")
        print(f"   - eBay listing optimized for search")
        print(f"   - Etsy listing for handmade/educational market")
        print(f"   - Facebook Marketplace for local Buffalo sales")
    
    # Log to revenue tracker
    try:
        import subprocess
        revenue_cmd = [
            "python", "revenue_tracker_hardened.py",
            "--platform", "sdcard_generation",
            "--amount", str(generator.profit_per_unit),
            "--content-type", "crypto_education_kit"
        ]
        subprocess.run(revenue_cmd, cwd="C:/EQ12/scripts")
        print(" Revenue potential logged to tracking system")
    except:
        print(" Could not log to revenue tracker")
    
    print(f"\n Ready for production:")
    print(f"   1. Burn package to 32GB+ SD cards")
    print(f"   2. List on marketplaces using generated listings")
    print(f"   3. Target: {generator.daily_target_units} sales/day = ${generator.daily_target_units * generator.profit_per_unit}/day revenue")
    print(f"   4. Buffalo 14215 local SEO advantage activated!")

if __name__ == "__main__":
    main()