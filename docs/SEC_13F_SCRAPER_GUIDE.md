# EQ12 SEC 13F Hedge Fund Scraper - User Guide

## 📊 **Overview**

Track Citadel and 9 other major hedge funds via SEC EDGAR API. Monitor quarterly holdings changes for market intelligence.

**Tracked Funds:**
1. Citadel Advisors LLC
2. Bridgewater Associates
3. Renaissance Technologies
4. Two Sigma Investments
5. Millennium Management
6. Point72 Asset Management
7. Elliott Management
8. DE Shaw & Co
9. Viking Global Investors
10. Tiger Global Management

---

## 🚀 **Quick Start**

### **1. Install Dependencies**

```powershell
# Install Python requests library
pip install requests
```

### **2. Scrape Latest Filings**

```powershell
# PowerShell (recommended)
.\EQ12_SEC_13F_SCRAPER.ps1 -Action scrape

# Python direct
python eq12_sec_13f_scraper.py --scrape
```

### **3. View Results**

```powershell
# List recent filings
.\EQ12_SEC_13F_SCRAPER.ps1 -Action list

# Export to JSON
.\EQ12_SEC_13F_SCRAPER.ps1 -Action export

# Full report
.\EQ12_SEC_13F_SCRAPER.ps1 -Action report
```

---

## 📁 **File Locations**

```
C:\EQ12_BROKEN_20251122_210342\
├── scripts\
│   ├── eq12_sec_13f_scraper.py          # Python scraper
│   └── EQ12_SEC_13F_SCRAPER.ps1         # PowerShell wrapper
├── logs\
│   └── sec_13f_holdings.db              # SQLite database (auto-created)
└── reports\
    └── sec_13f_export.json              # JSON export (when exported)
```

---

## 🗄️ **Database Schema**

### **Filings Table**
```sql
CREATE TABLE filings (
    id INTEGER PRIMARY KEY,
    fund_name TEXT,           -- "Citadel Advisors LLC"
    cik TEXT,                 -- "0001423053"
    filing_date DATE,         -- "2025-08-14"
    period_end DATE,          -- "2025-06-30" (quarter end)
    accession_number TEXT,    -- "0001193125-25-123456"
    form_type TEXT,           -- "13F-HR"
    total_value REAL,         -- Total AUM if parsed
    scraped_at TIMESTAMP
);
```

### **Holdings Table** (Coming Soon)
```sql
CREATE TABLE holdings (
    id INTEGER PRIMARY KEY,
    filing_id INTEGER,
    cusip TEXT,               -- Security identifier
    issuer_name TEXT,         -- "Apple Inc."
    ticker TEXT,              -- "AAPL"
    shares BIGINT,            -- 1,234,567
    market_value REAL,        -- Dollar value
    percentage REAL           -- % of portfolio
);
```

### **Position Changes Table** (Coming Soon)
```sql
CREATE TABLE position_changes (
    id INTEGER PRIMARY KEY,
    fund_name TEXT,
    ticker TEXT,
    shares_change BIGINT,     -- +/- shares
    shares_pct_change REAL,   -- % increase/decrease
    change_type TEXT,         -- "NEW", "INCREASED", "DECREASED", "SOLD"
    prev_filing_date DATE,
    new_filing_date DATE
);
```

---

## 💡 **Use Cases**

### **1. Track Citadel's Latest Moves**
```powershell
# Scrape latest filings
.\EQ12_SEC_13F_SCRAPER.ps1 -Action scrape -MaxFilings 3

# Query database
sqlite3 ..\logs\sec_13f_holdings.db "SELECT * FROM filings WHERE fund_name LIKE '%Citadel%' ORDER BY filing_date DESC LIMIT 5"
```

### **2. Monitor Quarter-Over-Quarter Changes**
```python
# Python analysis script (example)
import sqlite3
conn = sqlite3.connect('../logs/sec_13f_holdings.db')
cursor = conn.cursor()

# Get Citadel's latest 2 filings
cursor.execute("""
    SELECT filing_date, accession_number 
    FROM filings 
    WHERE fund_name = 'Citadel Advisors LLC' 
    ORDER BY filing_date DESC 
    LIMIT 2
""")

filings = cursor.fetchall()
print(f"Latest: {filings[0][0]} vs Previous: {filings[1][0]}")
```

### **3. Export for Analysis**
```powershell
# Export to JSON
.\EQ12_SEC_13F_SCRAPER.ps1 -Action export

# Import to Excel/PowerBI/Tableau
# File: C:\EQ12_BROKEN_20251122_210342\reports\sec_13f_export.json
```

---

## 🔧 **Advanced Usage**

### **Custom Database Path**
```powershell
python eq12_sec_13f_scraper.py --scrape --db "D:\EQ12\hedge_funds.db"
```

### **Scrape More Filings Per Fund**
```powershell
.\EQ12_SEC_13F_SCRAPER.ps1 -Action scrape -MaxFilings 10
```

### **Scheduled Automation**
```powershell
# Windows Task Scheduler (weekly scrape every Monday 8 AM)
# Action: PowerShell.exe
# Arguments: -NoProfile -ExecutionPolicy Bypass -File "C:\EQ12_BROKEN_20251122_210342\scripts\EQ12_SEC_13F_SCRAPER.ps1" -Action scrape
```

---

## 📊 **Example Output**

### **List Command**
```
=== Latest 13F Filings ===

2025-08-14 | Citadel Advisors LLC         | 0001193125-25-234567
2025-08-14 | Bridgewater Associates       | 0001193125-25-234568
2025-08-13 | Renaissance Technologies     | 0001193125-25-234569
2025-08-12 | Two Sigma Investments        | 0001193125-25-234570
2025-08-11 | Millennium Management        | 0001193125-25-234571
```

### **Scrape Command**
```
=== EQ12 SEC 13F Hedge Fund Scraper ===
Action: scrape

Fetching filings for Citadel Advisors LLC (CIK: 0001423053)...
Found 5 13F-HR filings for Citadel Advisors LLC
Saved filing 0001193125-25-234567 for Citadel Advisors LLC
Saved filing 0001193125-25-234566 for Citadel Advisors LLC
...
Scrape complete!

✅ Success!
Database: C:\EQ12_BROKEN_20251122_210342\logs\sec_13f_holdings.db (45.2 KB)
```

---

## 🚧 **Roadmap (Phase 2)**

1. **Holdings Parsing**: Extract detailed stock positions from 13F XML files
2. **Change Detection**: Automatic quarter-over-quarter comparisons
3. **Telegram Alerts**: Notify when Citadel makes major moves (>$100M position changes)
4. **VB.NET GUI**: Real-time dashboard in Master Control Panel
5. **Correlation Analysis**: Compare hedge fund moves with your sports betting predictions

---

## 🔗 **Integration Points**

### **With VB.NET Master Control Panel** (Phase 2)
- Display Citadel's top 10 holdings
- Show recent position changes
- Alert on new filings

### **With Trading Module** (Future)
- Correlate hedge fund moves with stock price predictions
- Generate sentiment scores based on institutional activity

### **With Prompt Execution System** (Current)
- Use 13F data as input for AI-generated market analysis prompts
- Feed holdings into prompt: "Analyze Citadel's Q3 2025 portfolio changes"

---

## 📝 **Notes**

- **SEC Rate Limits**: 10 requests/second (scraper includes 0.5s delays)
- **13F Filing Schedule**: Quarterly, due 45 days after quarter end
- **Data Freshness**: Latest Q3 2025 filings available ~mid-November 2025
- **Incomplete**: Holdings parsing (Phase 2) not yet implemented

---

## ❓ **Troubleshooting**

### **Error: "HTTP 403 - Forbidden"**
```powershell
# SEC requires valid User-Agent header
# Update USER_AGENT in eq12_sec_13f_scraper.py with your email
USER_AGENT = "EQ12Bot/1.0 (your_email@example.com)"
```

### **Error: "Module 'requests' not found"**
```powershell
pip install requests
```

### **Database Locked**
```powershell
# Close any open SQLite connections
# Windows: Close DB Browser for SQLite or similar tools
```

---

## 🎯 **Next Steps**

1. **Run initial scrape**: `.\EQ12_SEC_13F_SCRAPER.ps1 -Action scrape`
2. **Verify database**: Check `C:\EQ12_BROKEN_20251122_210342\logs\sec_13f_holdings.db`
3. **Schedule weekly scrapes**: Windows Task Scheduler (Mondays 8 AM)
4. **Wait for Phase 2**: Holdings parsing + change detection

---

**Created**: 2025-11-27
**Status**: Production-ready (metadata only, holdings parsing in Phase 2)
**Priority**: High ROI (market intelligence for trading decisions)
