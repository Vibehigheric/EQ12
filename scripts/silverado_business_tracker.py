#!/usr/bin/env python3
"""
silverado_business_tracker.py - Business Intelligence & Profitability Tracker
For: 2026 Chevrolet Silverado 1500 TurboMax Multi-Business Operations

Tracks: Dropshipping, Deliveries, Snow Plow, Towing, Inventory, Maintenance, Fuel

Features:
- Transaction logging (income/expense with truck-use tracking)
- Monthly P&L summaries
- Truck usage analytics (miles, fuel, maintenance ROI)
- Seasonal profit forecasting (snow plow jobs)
- Expense breakdown visualizations
- CSV/Excel import with auto-categorization
- CLI for easy data entry and reporting

Author: EQ12 System (Copilot-Enhanced)
Created: 2025-11-27
"""

import pandas as pd
import sqlite3
import argparse
import json
import os
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

DB_FILENAME = "silverado_business.db"
LOGS_DIR = Path(__file__).parent.parent / "logs"
DB_PATH = LOGS_DIR / DB_FILENAME

# Categories & sub-types (extensible via JSON config)
CATEGORIES = {
    "income": ["plow_job", "delivery", "dropship_sale", "towing", "hauling", "other_income"],
    "expense": ["fuel", "maintenance", "plow_equipment", "dropship_cost", "inventory_purchase", "insurance", "registration", "loan_payment", "other_expense"],
    "inventory_sale": ["dropship_sale", "retail_sale", "wholesale"],
    "inventory_purchase": ["wholesale_buy", "supplier_cost"],
}

# Truck cost assumptions (user can override via config)
DEFAULT_TRUCK_COSTS = {
    "fuel_mpg": 18.0,  # 2026 Silverado 1500 TurboMax est. combined MPG
    "fuel_price_per_gallon": 3.50,
    "maintenance_per_mile": 0.15,  # oil, tires, brakes, etc.
    "plow_kit_cost": 5000.00,  # one-time plow mount + blade
    "plow_kit_life_seasons": 5,  # amortize over 5 winters
}

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def initialize_database():
    """Create SQLite database with transactions table if not exists."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            sub_type TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            miles REAL DEFAULT 0,
            truck_use INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS truck_config (
            key TEXT PRIMARY KEY,
            value REAL NOT NULL,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert default truck costs if not exist
    for key, value in DEFAULT_TRUCK_COSTS.items():
        cursor.execute("""
            INSERT OR IGNORE INTO truck_config (key, value) VALUES (?, ?)
        """, (key, value))
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized: {DB_PATH}")

# ============================================================================
# CORE FUNCTIONS - Transaction Management
# ============================================================================

def add_transaction(date, category, sub_type, description, amount, miles=0, truck_use=False):
    """
    Add a transaction to the database.
    
    Args:
        date (str): yyyy-mm-dd format
        category (str): income, expense, inventory_sale, inventory_purchase
        sub_type (str): plow_job, delivery, fuel, maintenance, etc.
        description (str): Free-text notes
        amount (float): Positive for income, negative for expense
        miles (float): Miles driven for this transaction
        truck_use (bool): True if uses Silverado
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO transactions (date, category, sub_type, description, amount, miles, truck_use)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (date, category, sub_type, description, amount, miles, int(truck_use)))
    
    conn.commit()
    transaction_id = cursor.lastrowid
    conn.close()
    
    print(f"✅ Transaction #{transaction_id} recorded: {category}/{sub_type} | ${amount:.2f} | {miles} mi | Truck: {truck_use}")
    return transaction_id

def load_transactions():
    """Load all transactions as pandas DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM transactions", conn, parse_dates=["date"])
    conn.close()
    return df

def get_truck_config():
    """Load truck configuration from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM truck_config")
    config = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return config

# ============================================================================
# ANALYTICS - Summaries & Reports
# ============================================================================

def summary_by_category(df):
    """Total income/expenses by category and sub-type."""
    return df.groupby(["category", "sub_type"])["amount"].sum().sort_values(ascending=False)

def monthly_summary(df):
    """Monthly profit/loss summary."""
    df2 = df.copy()
    df2['month'] = df2['date'].dt.to_period('M')
    
    summary = df2.groupby(['month', 'category'])['amount'].sum().unstack(fill_value=0)
    
    # Calculate net income (all income - all expenses)
    income_cols = [c for c in summary.columns if c in ['income', 'inventory_sale']]
    expense_cols = [c for c in summary.columns if c in ['expense', 'inventory_purchase']]
    
    summary['total_income'] = summary[income_cols].sum(axis=1) if income_cols else 0
    summary['total_expense'] = summary[expense_cols].sum(axis=1).abs() if expense_cols else 0
    summary['net_income'] = summary['total_income'] - summary['total_expense']
    
    return summary

def truck_usage_stats(df):
    """
    Analyze truck-specific costs and usage.
    
    Returns:
        dict: total_miles, fuel_cost, maintenance_cost, cost_per_mile, truck_income
    """
    df_truck = df[df['truck_use'] == 1].copy()
    
    total_miles = df_truck['miles'].sum()
    fuel_cost = df_truck[df_truck['sub_type'] == 'fuel']['amount'].sum()
    maintenance = df_truck[df_truck['sub_type'] == 'maintenance']['amount'].sum()
    
    # Income generated using truck
    truck_income_categories = ['plow_job', 'delivery', 'towing', 'hauling']
    truck_income = df_truck[df_truck['sub_type'].isin(truck_income_categories)]['amount'].sum()
    
    # Cost per mile (actual)
    cost_per_mile = (abs(fuel_cost) + abs(maintenance)) / total_miles if total_miles > 0 else 0
    
    return {
        "total_miles": total_miles,
        "fuel_cost": fuel_cost,
        "maintenance_cost": maintenance,
        "cost_per_mile": cost_per_mile,
        "truck_income": truck_income,
        "net_truck_profit": truck_income + fuel_cost + maintenance  # fuel/maint are negative
    }

def plow_season_summary(df, season_start="2025-11-01", season_end="2026-03-31"):
    """
    Summary for snow plow season (Nov - March).
    
    Args:
        df (DataFrame): Transactions
        season_start (str): yyyy-mm-dd
        season_end (str): yyyy-mm-dd
    
    Returns:
        dict: plow_jobs, plow_income, plow_miles, season_profit
    """
    df_plow = df[(df['date'] >= season_start) & (df['date'] <= season_end) & 
                 (df['sub_type'] == 'plow_job')].copy()
    
    plow_jobs = len(df_plow)
    plow_income = df_plow['amount'].sum()
    plow_miles = df_plow['miles'].sum()
    
    # Estimate costs (fuel + maintenance for plow miles)
    config = get_truck_config()
    fuel_cost = -(plow_miles / config['fuel_mpg']) * config['fuel_price_per_gallon']
    maint_cost = -(plow_miles * config['maintenance_per_mile'])
    plow_kit_amortization = -(config['plow_kit_cost'] / config['plow_kit_life_seasons'])
    
    season_profit = plow_income + fuel_cost + maint_cost + plow_kit_amortization
    
    return {
        "season_start": season_start,
        "season_end": season_end,
        "plow_jobs": plow_jobs,
        "plow_income": plow_income,
        "plow_miles": plow_miles,
        "fuel_cost": fuel_cost,
        "maintenance_cost": maint_cost,
        "plow_kit_amortization": plow_kit_amortization,
        "net_profit": season_profit,
        "profit_per_job": season_profit / plow_jobs if plow_jobs > 0 else 0
    }

# ============================================================================
# FORECASTING - Seasonal Profit Predictions
# ============================================================================

def forecast_seasonal_plow_profit(avg_jobs_per_storm=5, storms_per_season=12, avg_fee_per_job=65, avg_miles_per_job=8):
    """
    Forecast snow plow season profitability.
    
    Args:
        avg_jobs_per_storm (int): Jobs completed per snowstorm
        storms_per_season (int): Expected storms (Nov-Mar)
        avg_fee_per_job (float): Average payment per plow job
        avg_miles_per_job (float): Avg miles driven per job
    
    Returns:
        dict: Forecast with gross_income, total_costs, net_profit, ROI
    """
    config = get_truck_config()
    
    total_jobs = avg_jobs_per_storm * storms_per_season
    gross_income = total_jobs * avg_fee_per_job
    total_miles = total_jobs * avg_miles_per_job
    
    # Costs
    fuel_cost = (total_miles / config['fuel_mpg']) * config['fuel_price_per_gallon']
    maintenance_cost = total_miles * config['maintenance_per_mile']
    plow_kit_amortization = config['plow_kit_cost'] / config['plow_kit_life_seasons']
    
    total_costs = fuel_cost + maintenance_cost + plow_kit_amortization
    net_profit = gross_income - total_costs
    roi = (net_profit / total_costs * 100) if total_costs > 0 else 0
    
    return {
        "total_jobs": total_jobs,
        "gross_income": gross_income,
        "total_miles": total_miles,
        "fuel_cost": fuel_cost,
        "maintenance_cost": maintenance_cost,
        "plow_kit_amortization": plow_kit_amortization,
        "total_costs": total_costs,
        "net_profit": net_profit,
        "roi_percentage": roi,
        "profit_per_job": net_profit / total_jobs if total_jobs > 0 else 0
    }

# ============================================================================
# IMPORT - Bank Statement CSV/Excel Auto-Categorization
# ============================================================================

def auto_categorize(description):
    """
    Auto-categorize transaction based on description keywords.
    
    Args:
        description (str): Transaction description
    
    Returns:
        tuple: (category, sub_type, confidence)
    """
    desc_lower = description.lower()
    
    # Income keywords
    if any(word in desc_lower for word in ['plow', 'snow', 'driveway']):
        return ("income", "plow_job", 0.85)
    if any(word in desc_lower for word in ['delivery', 'deliver', 'ship']):
        return ("income", "delivery", 0.80)
    if any(word in desc_lower for word in ['tow', 'towing']):
        return ("income", "towing", 0.90)
    if any(word in desc_lower for word in ['sale', 'sold', 'revenue']):
        return ("income", "dropship_sale", 0.70)
    
    # Expense keywords
    if any(word in desc_lower for word in ['gas', 'fuel', 'shell', 'exxon', 'chevron', 'bp']):
        return ("expense", "fuel", 0.90)
    if any(word in desc_lower for word in ['repair', 'oil change', 'tire', 'brake', 'mechanic']):
        return ("expense", "maintenance", 0.85)
    if any(word in desc_lower for word in ['insurance', 'geico', 'progressive', 'state farm']):
        return ("expense", "insurance", 0.95)
    if any(word in desc_lower for word in ['plow', 'blade', 'mount', 'salt']):
        return ("expense", "plow_equipment", 0.80)
    if any(word in desc_lower for word in ['inventory', 'supplier', 'wholesale']):
        return ("expense", "inventory_purchase", 0.75)
    
    # Default: flag for review
    return ("expense", "other_expense", 0.30)  # Low confidence

def import_bank_statement(csv_path, date_col="Date", desc_col="Description", amount_col="Amount"):
    """
    Import bank statement CSV and auto-categorize transactions.
    
    Args:
        csv_path (str): Path to CSV file
        date_col (str): Column name for date
        desc_col (str): Column name for description
        amount_col (str): Column name for amount
    
    Returns:
        DataFrame: Imported transactions with suggested categories
    """
    df_import = pd.read_csv(csv_path, parse_dates=[date_col])
    
    results = []
    for _, row in df_import.iterrows():
        category, sub_type, confidence = auto_categorize(row[desc_col])
        
        # Determine if expense (negative) or income (positive)
        amount = row[amount_col]
        if amount < 0 and category == "income":
            category = "expense"  # Override if negative amount but detected as income keyword
        
        results.append({
            "date": row[date_col].strftime("%Y-%m-%d"),
            "category": category,
            "sub_type": sub_type,
            "description": row[desc_col],
            "amount": amount,
            "confidence": confidence,
            "needs_review": confidence < 0.70
        })
    
    df_result = pd.DataFrame(results)
    print(f"✅ Imported {len(df_result)} transactions from {csv_path}")
    print(f"⚠️  {df_result['needs_review'].sum()} transactions flagged for review (low confidence)")
    
    return df_result

# ============================================================================
# VISUALIZATION - HTML Report with Charts
# ============================================================================

def generate_report(output_format='html', output_path=None):
    """
    Generate comprehensive business report with charts.
    
    Args:
        output_format (str): 'html', 'pdf', 'json'
        output_path (str): Custom output path (default: logs/silverado_report_YYYYMMDD.html)
    
    Returns:
        str: Path to generated report
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        print("❌ matplotlib/seaborn not installed. Run: pip install matplotlib seaborn")
        return None
    
    df = load_transactions()
    
    if df.empty:
        print("⚠️  No transactions to report")
        return None
    
    # Generate charts
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('2026 Silverado TurboMax - Business Intelligence Report', fontsize=16, fontweight='bold')
    
    # 1. Monthly Net Income Trend
    monthly = monthly_summary(df)
    if 'net_income' in monthly.columns:
        monthly['net_income'].plot(ax=axes[0, 0], kind='line', marker='o', color='green', linewidth=2)
        axes[0, 0].set_title('Monthly Net Income Trend', fontweight='bold')
        axes[0, 0].set_ylabel('Net Income ($)')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].axhline(0, color='red', linestyle='--', alpha=0.5)
    
    # 2. Expense Breakdown (Pie Chart)
    expense_df = df[df['category'] == 'expense'].copy()
    if not expense_df.empty:
        expense_breakdown = expense_df.groupby('sub_type')['amount'].sum().abs()
        axes[0, 1].pie(expense_breakdown, labels=expense_breakdown.index, autopct='%1.1f%%', startangle=90)
        axes[0, 1].set_title('Expense Breakdown by Type', fontweight='bold')
    
    # 3. Truck Usage - Income vs Costs
    truck_stats = truck_usage_stats(df)
    categories_truck = ['Truck Income', 'Fuel Cost', 'Maintenance']
    values_truck = [truck_stats['truck_income'], abs(truck_stats['fuel_cost']), abs(truck_stats['maintenance_cost'])]
    axes[1, 0].bar(categories_truck, values_truck, color=['green', 'orange', 'red'])
    axes[1, 0].set_title('Truck Usage - Income vs Costs', fontweight='bold')
    axes[1, 0].set_ylabel('Amount ($)')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # 4. Income by Source (Bar Chart)
    income_df = df[df['category'] == 'income'].copy()
    if not income_df.empty:
        income_breakdown = income_df.groupby('sub_type')['amount'].sum().sort_values(ascending=False)
        income_breakdown.plot(ax=axes[1, 1], kind='barh', color='skyblue')
        axes[1, 1].set_title('Income by Source', fontweight='bold')
        axes[1, 1].set_xlabel('Amount ($)')
        axes[1, 1].grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    # Save chart
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chart_path = LOGS_DIR / f"silverado_charts_{timestamp}.png"
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    # Generate HTML report
    if output_path is None:
        output_path = LOGS_DIR / f"silverado_report_{timestamp}.html"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Silverado Business Tracker - Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: auto; background: white; padding: 30px; border-radius: 10px; }}
            h1 {{ color: #1e3a8a; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }}
            h2 {{ color: #1e40af; margin-top: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border: 1px solid #ddd; }}
            th {{ background-color: #3b82f6; color: white; }}
            tr:nth-child(even) {{ background-color: #f9fafb; }}
            .metric {{ display: inline-block; margin: 10px 20px; padding: 15px 25px; background: #dbeafe; border-radius: 8px; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #1e40af; }}
            .metric-label {{ font-size: 14px; color: #64748b; }}
            img {{ max-width: 100%; height: auto; margin: 20px 0; border: 1px solid #ddd; border-radius: 8px; }}
            .positive {{ color: green; font-weight: bold; }}
            .negative {{ color: red; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚛 2026 Silverado TurboMax - Business Intelligence Report</h1>
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <h2>📊 Key Metrics</h2>
            <div class="metric">
                <div class="metric-label">Total Transactions</div>
                <div class="metric-value">{len(df)}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Truck Miles</div>
                <div class="metric-value">{truck_stats['total_miles']:.0f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Net Truck Profit</div>
                <div class="metric-value {'positive' if truck_stats['net_truck_profit'] >= 0 else 'negative'}">${truck_stats['net_truck_profit']:.2f}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Cost per Mile</div>
                <div class="metric-value">${truck_stats['cost_per_mile']:.2f}</div>
            </div>
            
            <h2>📈 Visualizations</h2>
            <img src="{chart_path.name}" alt="Business Charts">
            
            <h2>💰 Monthly Summary</h2>
            {monthly[['total_income', 'total_expense', 'net_income']].to_html(classes='table')}
            
            <h2>🚚 Truck Usage Breakdown</h2>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Total Miles Driven</td><td>{truck_stats['total_miles']:.0f} mi</td></tr>
                <tr><td>Fuel Cost</td><td class="negative">${abs(truck_stats['fuel_cost']):.2f}</td></tr>
                <tr><td>Maintenance Cost</td><td class="negative">${abs(truck_stats['maintenance_cost']):.2f}</td></tr>
                <tr><td>Truck Income</td><td class="positive">${truck_stats['truck_income']:.2f}</td></tr>
                <tr><td>Net Truck Profit</td><td class="{'positive' if truck_stats['net_truck_profit'] >= 0 else 'negative'}">${truck_stats['net_truck_profit']:.2f}</td></tr>
                <tr><td>Cost per Mile</td><td>${truck_stats['cost_per_mile']:.2f}</td></tr>
            </table>
            
            <h2>📋 Category Breakdown</h2>
            {summary_by_category(df).to_frame('Total ($)').to_html(classes='table')}
            
            <hr style="margin: 40px 0;">
            <p style="text-align: center; color: #64748b; font-size: 12px;">
                Generated by silverado_business_tracker.py | EQ12 System
            </p>
        </div>
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Report generated: {output_path}")
    return str(output_path)

# ============================================================================
# CLI - Command-Line Interface
# ============================================================================

def cli_main():
    """Command-line interface for business tracker."""
    parser = argparse.ArgumentParser(
        description="2026 Silverado Business Tracker - Track profits, expenses, and truck usage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add plow job
  python silverado_business_tracker.py add --date 2025-11-27 --category income --sub-type plow_job --amount 65 --description "123 Elm St driveway" --miles 10 --truck-use
  
  # Add fuel expense
  python silverado_business_tracker.py add --date 2025-11-27 --category expense --sub-type fuel --amount -60 --truck-use
  
  # Generate report
  python silverado_business_tracker.py report
  
  # Show truck stats
  python silverado_business_tracker.py truck-stats
  
  # Forecast plow season
  python silverado_business_tracker.py forecast --jobs-per-storm 5 --storms 12 --fee 65
  
  # Import bank statement
  python silverado_business_tracker.py import --csv bank_statement.csv
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # ADD TRANSACTION
    add_parser = subparsers.add_parser('add', help='Add a transaction')
    add_parser.add_argument('--date', required=True, help='Date (YYYY-MM-DD)')
    add_parser.add_argument('--category', required=True, choices=['income', 'expense', 'inventory_sale', 'inventory_purchase'])
    add_parser.add_argument('--sub-type', required=True, help='Sub-type (plow_job, fuel, delivery, etc.)')
    add_parser.add_argument('--amount', required=True, type=float, help='Amount (positive=income, negative=expense)')
    add_parser.add_argument('--description', default='', help='Transaction description')
    add_parser.add_argument('--miles', type=float, default=0, help='Miles driven')
    add_parser.add_argument('--truck-use', action='store_true', help='Used Silverado for this transaction')
    
    # REPORT
    report_parser = subparsers.add_parser('report', help='Generate HTML report')
    report_parser.add_argument('--output', help='Custom output path')
    
    # TRUCK STATS
    subparsers.add_parser('truck-stats', help='Show truck usage statistics')
    
    # FORECAST
    forecast_parser = subparsers.add_parser('forecast', help='Forecast seasonal plow profit')
    forecast_parser.add_argument('--jobs-per-storm', type=int, default=5, help='Avg jobs per storm')
    forecast_parser.add_argument('--storms', type=int, default=12, help='Storms per season')
    forecast_parser.add_argument('--fee', type=float, default=65, help='Avg fee per job')
    forecast_parser.add_argument('--miles', type=float, default=8, help='Avg miles per job')
    
    # IMPORT
    import_parser = subparsers.add_parser('import', help='Import bank statement CSV')
    import_parser.add_argument('--csv', required=True, help='Path to CSV file')
    import_parser.add_argument('--date-col', default='Date', help='Date column name')
    import_parser.add_argument('--desc-col', default='Description', help='Description column name')
    import_parser.add_argument('--amount-col', default='Amount', help='Amount column name')
    import_parser.add_argument('--auto-commit', action='store_true', help='Auto-commit high-confidence transactions')
    
    # SUMMARY
    subparsers.add_parser('summary', help='Show summary by category')
    
    args = parser.parse_args()
    
    # Initialize database
    initialize_database()
    
    # Execute command
    if args.command == 'add':
        add_transaction(
            date=args.date,
            category=args.category,
            sub_type=args.sub_type,
            description=args.description,
            amount=args.amount,
            miles=args.miles,
            truck_use=args.truck_use
        )
    
    elif args.command == 'report':
        generate_report(output_path=args.output)
    
    elif args.command == 'truck-stats':
        df = load_transactions()
        stats = truck_usage_stats(df)
        print("\n🚚 Truck Usage Statistics:")
        print(f"  Total Miles: {stats['total_miles']:.0f}")
        print(f"  Fuel Cost: ${abs(stats['fuel_cost']):.2f}")
        print(f"  Maintenance: ${abs(stats['maintenance_cost']):.2f}")
        print(f"  Cost/Mile: ${stats['cost_per_mile']:.2f}")
        print(f"  Truck Income: ${stats['truck_income']:.2f}")
        print(f"  Net Profit: ${stats['net_truck_profit']:.2f}")
    
    elif args.command == 'forecast':
        forecast = forecast_seasonal_plow_profit(
            avg_jobs_per_storm=args.jobs_per_storm,
            storms_per_season=args.storms,
            avg_fee_per_job=args.fee,
            avg_miles_per_job=args.miles
        )
        print("\n❄️  Snow Plow Season Forecast:")
        print(f"  Total Jobs: {forecast['total_jobs']}")
        print(f"  Gross Income: ${forecast['gross_income']:.2f}")
        print(f"  Total Costs: ${forecast['total_costs']:.2f}")
        print(f"  Net Profit: ${forecast['net_profit']:.2f}")
        print(f"  ROI: {forecast['roi_percentage']:.1f}%")
        print(f"  Profit/Job: ${forecast['profit_per_job']:.2f}")
    
    elif args.command == 'import':
        df_import = import_bank_statement(
            csv_path=args.csv,
            date_col=args.date_col,
            desc_col=args.desc_col,
            amount_col=args.amount_col
        )
        
        if args.auto_commit:
            high_conf = df_import[df_import['confidence'] >= 0.70]
            for _, row in high_conf.iterrows():
                add_transaction(
                    date=row['date'],
                    category=row['category'],
                    sub_type=row['sub_type'],
                    description=row['description'],
                    amount=row['amount'],
                    miles=0,
                    truck_use=False
                )
            print(f"✅ Auto-committed {len(high_conf)} high-confidence transactions")
        else:
            print("\n📋 Preview (use --auto-commit to add to database):")
            print(df_import.to_string(index=False))
    
    elif args.command == 'summary':
        df = load_transactions()
        print("\n💰 Summary by Category:")
        print(summary_by_category(df).to_string())
        print("\n📅 Monthly Summary:")
        print(monthly_summary(df).to_string())
    
    else:
        parser.print_help()

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # CLI mode
        cli_main()
    else:
        # Interactive demo mode
        print("=" * 80)
        print("🚛 2026 Silverado TurboMax - Business Intelligence Tracker")
        print("=" * 80)
        
        initialize_database()
        
        # Example transactions
        print("\n📝 Adding sample transactions...")
        add_transaction("2025-11-27", "income", "plow_job", "123 Elm St driveway", 65.00, miles=10, truck_use=True)
        add_transaction("2025-11-27", "expense", "fuel", "Shell gas station", -60.00, miles=0, truck_use=True)
        add_transaction("2025-11-28", "income", "delivery", "Package delivery - downtown", 45.00, miles=25, truck_use=True)
        add_transaction("2025-11-28", "expense", "maintenance", "Oil change + tire rotation", -120.00, miles=0, truck_use=True)
        
        df = load_transactions()
        
        print("\n" + "=" * 80)
        print("📊 ANALYTICS")
        print("=" * 80)
        
        print("\n💰 Summary by Category:")
        print(summary_by_category(df))
        
        print("\n📅 Monthly Summary:")
        print(monthly_summary(df))
        
        print("\n🚚 Truck Usage Stats:")
        stats = truck_usage_stats(df)
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n❄️  Plow Season Forecast (5 jobs/storm, 12 storms, $65/job):")
        forecast = forecast_seasonal_plow_profit(5, 12, 65, 8)
        for key, value in forecast.items():
            print(f"  {key}: {value}")
        
        print("\n📈 Generating HTML report...")
        report_path = generate_report()
        
        print("\n" + "=" * 80)
        print("✅ DEMO COMPLETE")
        print("=" * 80)
        print(f"\nDatabase: {DB_PATH}")
        print(f"Report: {report_path}")
        print("\nNext steps:")
        print("  python silverado_business_tracker.py --help")
        print("  python silverado_business_tracker.py add --date 2025-11-27 --category income --sub-type plow_job --amount 65 --truck-use")
        print("  python silverado_business_tracker.py report")
