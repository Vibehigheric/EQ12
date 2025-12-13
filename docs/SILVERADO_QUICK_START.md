# Silverado Business Tracker - Quick Start Guide

## 🎯 What This System Does

**Tracks profitability for your 2026 Chevrolet Silverado 1500 TurboMax multi-business operations:**
- ❄️ **Snow Plow Jobs** (seasonal income, per-job tracking)
- 📦 **Deliveries & Hauling** (package delivery, moving services)
- 🛒 **Dropshipping & Inventory** (e-commerce, retail sales)
- 🚗 **Towing Services** (roadside assistance, recovery)
- 💰 **Expense Tracking** (fuel, maintenance, insurance, equipment)
- 📊 **Truck Cost Analytics** (cost per mile, ROI, depreciation)
- 📈 **Forecasting** (seasonal profit predictions, break-even analysis)

---

## ⚡ Quick Start (5 Minutes)

### **1. Install Dependencies**

```powershell
# Navigate to scripts directory
cd C:\EQ12_BROKEN_20251122_210342\scripts

# Install required packages
pip install pandas matplotlib seaborn
```

### **2. Run Demo Mode**

```powershell
# Run without arguments to see demo with sample data
python silverado_business_tracker.py
```

**Expected Output:**
```
================================================================================
🚛 2026 Silverado TurboMax - Business Intelligence Tracker
================================================================================

📝 Adding sample transactions...
✅ Transaction #1 recorded: income/plow_job | $65.00 | 10 mi | Truck: True
✅ Transaction #2 recorded: expense/fuel | $-60.00 | 0 mi | Truck: True
✅ Transaction #3 recorded: income/delivery | $45.00 | 25 mi | Truck: True
✅ Transaction #4 recorded: expense/maintenance | $-120.00 | 0 mi | Truck: True

================================================================================
📊 ANALYTICS
================================================================================

💰 Summary by Category:
category  sub_type    
income    plow_job        65.00
          delivery        45.00
expense   fuel           -60.00
          maintenance   -120.00

📅 Monthly Summary:
        total_income  total_expense  net_income
month                                         
2025-11      110.00         180.00      -70.00

🚚 Truck Usage Stats:
  total_miles: 35.0
  fuel_cost: -60.0
  maintenance_cost: -120.0
  cost_per_mile: 5.14
  truck_income: 110.0
  net_truck_profit: -70.0

❄️  Plow Season Forecast (5 jobs/storm, 12 storms, $65/job):
  total_jobs: 60
  gross_income: 3900.0
  total_miles: 480.0
  fuel_cost: 93.33...
  ...

📈 Generating HTML report...
✅ Report generated: C:\EQ12_BROKEN_20251122_210342\logs\silverado_report_20251127_143025.html

================================================================================
✅ DEMO COMPLETE
================================================================================

Database: C:\EQ12_BROKEN_20251122_210342\logs\silverado_business.db
Report: C:\EQ12_BROKEN_20251122_210342\logs\silverado_report_20251127_143025.html
```

### **3. View Your First Report**

```powershell
# Open HTML report in browser
start C:\EQ12_BROKEN_20251122_210342\logs\silverado_report_*.html
```

**Report Includes:**
- 📊 Monthly net income trend (line chart)
- 🥧 Expense breakdown (pie chart)
- 📈 Truck income vs costs (bar chart)
- 💰 Income by source (bar chart)
- 📋 Category breakdown table
- 🚚 Truck usage metrics

---

## 📝 Real-World Usage Examples

### **Add Your First Plow Job**

```powershell
python silverado_business_tracker.py add `
  --date 2025-11-27 `
  --category income `
  --sub-type plow_job `
  --amount 65 `
  --description "123 Elm St driveway - 6 inches snow" `
  --miles 10 `
  --truck-use
```

### **Log Fuel Expense**

```powershell
python silverado_business_tracker.py add `
  --date 2025-11-27 `
  --category expense `
  --sub-type fuel `
  --amount -60.50 `
  --description "Shell - filled tank" `
  --truck-use
```

### **Record Delivery Income**

```powershell
python silverado_business_tracker.py add `
  --date 2025-11-27 `
  --category income `
  --sub-type delivery `
  --amount 45 `
  --description "Package delivery downtown" `
  --miles 25 `
  --truck-use
```

### **Track Maintenance Expense**

```powershell
python silverado_business_tracker.py add `
  --date 2025-11-28 `
  --category expense `
  --sub-type maintenance `
  --amount -120 `
  --description "Oil change + tire rotation" `
  --truck-use
```

### **Log Dropshipping Sale (No Truck)**

```powershell
python silverado_business_tracker.py add `
  --date 2025-11-28 `
  --category income `
  --sub-type dropship_sale `
  --amount 150 `
  --description "Amazon FBA - electronics"
# Note: No --truck-use flag (online business)
```

---

## 📊 Analytics Commands

### **Generate Latest Report**

```powershell
python silverado_business_tracker.py report
```

### **View Summary**

```powershell
python silverado_business_tracker.py summary
```

**Output:**
```
💰 Summary by Category:
category         sub_type    
income           plow_job           390.00
                 delivery           135.00
expense          fuel              -180.00
                 maintenance       -120.00

📅 Monthly Summary:
        total_income  total_expense  net_income
month                                         
2025-11      525.00         300.00      225.00
```

### **Check Truck Statistics**

```powershell
python silverado_business_tracker.py truck-stats
```

**Output:**
```
🚚 Truck Usage Statistics:
  Total Miles: 150
  Fuel Cost: $180.00
  Maintenance: $120.00
  Cost/Mile: $2.00
  Truck Income: $525.00
  Net Profit: $225.00
```

### **Forecast Plow Season Profit**

```powershell
# Default: 5 jobs/storm, 12 storms, $65/job, 8 mi/job
python silverado_business_tracker.py forecast

# Custom forecast
python silverado_business_tracker.py forecast `
  --jobs-per-storm 8 `
  --storms 15 `
  --fee 75 `
  --miles 12
```

**Output:**
```
❄️  Snow Plow Season Forecast:
  Total Jobs: 120
  Gross Income: $9000.00
  Total Costs: $1653.33
  Net Profit: $7346.67
  ROI: 444.5%
  Profit/Job: $61.22
```

---

## 📥 Import Bank Statements

### **CSV Import with Auto-Categorization**

```powershell
# Import bank statement (auto-categorizes transactions)
python silverado_business_tracker.py import `
  --csv C:\Downloads\bank_statement_nov2025.csv `
  --date-col "Date" `
  --desc-col "Description" `
  --amount-col "Amount"
```

**What Happens:**
1. Reads CSV file
2. Auto-categorizes each transaction using keywords:
   - "plow", "snow" → `income/plow_job`
   - "delivery" → `income/delivery`
   - "gas", "fuel", "Shell" → `expense/fuel`
   - "repair", "oil change" → `expense/maintenance`
3. Assigns confidence score (0.0 - 1.0)
4. Flags low-confidence transactions for review

**Preview Output:**
```
✅ Imported 45 transactions from bank_statement_nov2025.csv
⚠️  12 transactions flagged for review (low confidence)

📋 Preview (use --auto-commit to add to database):
        date category  sub_type           description  amount  confidence  needs_review
0 2025-11-01   income  plow_job   Snow removal - ...   65.00        0.85         False
1 2025-11-01  expense      fuel   SHELL #1234 - F...  -60.00        0.90         False
...
```

### **Auto-Commit High-Confidence Transactions**

```powershell
# Automatically add transactions with confidence >= 70%
python silverado_business_tracker.py import `
  --csv C:\Downloads\bank_statement_nov2025.csv `
  --auto-commit
```

**Output:**
```
✅ Auto-committed 33 high-confidence transactions
⚠️  12 transactions need manual review (see preview above)
```

---

## 🎯 Common Workflows

### **Daily Routine (After Each Job)**

```powershell
# 1. Log plow job income
python silverado_business_tracker.py add --date 2025-11-27 --category income --sub-type plow_job --amount 65 --description "456 Oak Ave" --miles 8 --truck-use

# 2. Log fuel if filled up
python silverado_business_tracker.py add --date 2025-11-27 --category expense --sub-type fuel --amount -55 --truck-use

# 3. Check today's profit
python silverado_business_tracker.py summary
```

### **Weekly Review**

```powershell
# 1. Generate latest report
python silverado_business_tracker.py report

# 2. Check truck stats
python silverado_business_tracker.py truck-stats

# 3. Review expense breakdown (open HTML report)
start C:\EQ12_BROKEN_20251122_210342\logs\silverado_report_*.html
```

### **Monthly Close (End of Month)**

```powershell
# 1. Import bank statement to catch missed transactions
python silverado_business_tracker.py import --csv C:\Downloads\bank_nov2025.csv --auto-commit

# 2. Generate final report
python silverado_business_tracker.py report

# 3. View summary
python silverado_business_tracker.py summary

# 4. Export for accountant (future feature)
# python silverado_business_tracker.py export-powerbi
```

### **Pre-Season Planning (Before Winter)**

```powershell
# Forecast plow season profitability
python silverado_business_tracker.py forecast `
  --jobs-per-storm 6 `
  --storms 15 `
  --fee 70 `
  --miles 10

# Expected output: Net profit, ROI, profit per job
# Use this to decide: Is plow business worth it?
```

---

## 🗄️ Database & Files

### **Database Location**

```
C:\EQ12_BROKEN_20251122_210342\logs\silverado_business.db
```

**Tables:**
- `transactions` - All income/expense records
- `truck_config` - Truck cost assumptions (MPG, fuel price, etc.)

**View Database:**
- Use SQLite Viewer extension in VS Code
- Or: `sqlite3 logs\silverado_business.db` → `.tables` → `SELECT * FROM transactions;`

### **Reports Location**

```
C:\EQ12_BROKEN_20251122_210342\logs\silverado_report_YYYYMMDD_HHMMSS.html
C:\EQ12_BROKEN_20251122_210342\logs\silverado_charts_YYYYMMDD_HHMMSS.png
```

### **Backup Database**

```powershell
# Weekly backup
copy C:\EQ12_BROKEN_20251122_210342\logs\silverado_business.db `
     C:\EQ12_BROKEN_20251122_210342\logs\backups\silverado_business_$(Get-Date -Format 'yyyyMMdd').db
```

---

## 🔧 Customization

### **Update Truck Configuration**

**Edit fuel price, MPG, maintenance costs:**

```powershell
# Open database in VS Code (SQLite Viewer extension)
# Edit truck_config table:

# Example: Update fuel price to $3.75/gallon
sqlite3 logs\silverado_business.db "UPDATE truck_config SET value = 3.75 WHERE key = 'fuel_price_per_gallon';"

# Update estimated MPG to 20
sqlite3 logs\silverado_business.db "UPDATE truck_config SET value = 20 WHERE key = 'fuel_mpg';"
```

**Or edit in Python:**

```python
import sqlite3
conn = sqlite3.connect('logs/silverado_business.db')
cursor = conn.cursor()
cursor.execute("UPDATE truck_config SET value = 3.75 WHERE key = 'fuel_price_per_gallon'")
conn.commit()
conn.close()
```

### **Add Custom Categories**

**Edit `silverado_business_tracker.py`:**

```python
# Line ~30: Add new category
CATEGORIES = {
    "income": ["plow_job", "delivery", "dropship_sale", "towing", "hauling", "lawn_care", "other_income"],  # Added lawn_care
    "expense": ["fuel", "maintenance", "plow_equipment", "dropship_cost", "inventory_purchase", "insurance", "registration", "loan_payment", "equipment_rental", "other_expense"],  # Added equipment_rental
    # ...
}
```

**Then use new category:**

```powershell
python silverado_business_tracker.py add `
  --date 2025-11-27 `
  --category income `
  --sub-type lawn_care `
  --amount 80 `
  --description "Lawn mowing - 789 Maple Dr" `
  --miles 5 `
  --truck-use
```

---

## 🚀 Next Steps: Extend with Copilot

### **See 21 Ready-to-Use Prompts:**

Open: `docs\SILVERADO_COPILOT_ENHANCEMENT_GUIDE.md`

**Popular Extensions:**
1. **Telegram Alerts** - Daily profit summary via Telegram bot
2. **Receipt Scanning** - OCR to extract data from receipts
3. **Budget Alerts** - Warn when spending exceeds limits
4. **Tax Deduction Calculator** - IRS mileage deduction
5. **Plotly Dashboard** - Interactive web dashboard
6. **QuickBooks Sync** - Auto-sync to accounting software

**How to Use:**
1. Open VS Code
2. Open Copilot Chat (Ctrl+Shift+I)
3. Paste prompt from guide (e.g., "Add Telegram alerts...")
4. Review generated code → Accept → Test

---

## ❓ Troubleshooting

### **Error: `ModuleNotFoundError: No module named 'pandas'`**

**Fix:**
```powershell
pip install pandas matplotlib seaborn
```

### **Error: `OperationalError: no such table: transactions`**

**Fix:** Run once to initialize database
```powershell
python silverado_business_tracker.py
```

### **Charts Not Generating**

**Fix:** Install matplotlib
```powershell
pip install matplotlib seaborn
```

### **Database Location Wrong**

**Check:** Database is created at `logs/silverado_business.db` relative to script location.

**Fix:** Ensure you're in correct directory:
```powershell
cd C:\EQ12_BROKEN_20251122_210342\scripts
python silverado_business_tracker.py
```

---

## 📞 Support & Documentation

**Full Documentation:**
- `SILVERADO_COPILOT_ENHANCEMENT_GUIDE.md` - 21 Copilot prompts for extending system
- `silverado_business_tracker.py` - Source code (heavily commented)

**Help Command:**
```powershell
python silverado_business_tracker.py --help
python silverado_business_tracker.py add --help
python silverado_business_tracker.py report --help
```

**EQ12 System Documentation:**
- `AGENTS.md` - AI agent contract & standards
- `.github\copilot-instructions.md` - Copilot workspace instructions

---

## ✅ Quick Reference Card

| **Task** | **Command** |
|----------|------------|
| Run demo | `python silverado_business_tracker.py` |
| Add plow job | `python silverado_business_tracker.py add --date YYYY-MM-DD --category income --sub-type plow_job --amount 65 --miles 10 --truck-use` |
| Add fuel expense | `python silverado_business_tracker.py add --date YYYY-MM-DD --category expense --sub-type fuel --amount -60 --truck-use` |
| Generate report | `python silverado_business_tracker.py report` |
| View summary | `python silverado_business_tracker.py summary` |
| Truck stats | `python silverado_business_tracker.py truck-stats` |
| Forecast plow season | `python silverado_business_tracker.py forecast --jobs-per-storm 5 --storms 12 --fee 65` |
| Import bank CSV | `python silverado_business_tracker.py import --csv file.csv --auto-commit` |
| Help | `python silverado_business_tracker.py --help` |

---

**🚛 Your 2026 Silverado TurboMax is now a profit-tracking machine!**

**Next:** Open `SILVERADO_COPILOT_ENHANCEMENT_GUIDE.md` and pick your first extension (Telegram alerts, receipt scanning, or budget tracking recommended).

---

**Created:** 2025-11-27  
**Version:** 1.0  
**Author:** EQ12 System (Copilot-Enhanced)
