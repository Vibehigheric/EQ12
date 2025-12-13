# Windows Data Sentinel

**Windows-Native Business Intelligence Data Collection System**

A VB.NET + PowerShell + SQLite data aggregation platform that collects intelligence from RSS feeds and JSON APIs for legal, sports, weather, finance, and local news monitoring.

---

## 🎯 Project Overview

**Purpose:** Foundation for Windows Data Sentinel + Local Business Intelligence SaaS (Project 1 from EQ12 Strategic Plan)

**Revenue Target:** +$15,000/month (100 Buffalo/WNY businesses @ $49-$499/month)

**Architecture:** Windows-native VB.NET + PowerShell + SQLite (as explicitly requested)

**Current Status:** ✅ **OPERATIONAL** - 87 items collected from 6 data sources

---

## 📊 System Components

### 1. VB.NET Data Collector (`EQ12DataCollector.exe`)
- **Language:** Visual Basic .NET 8.0
- **Size:** 148 KB compiled executable
- **Features:**
  - RSS feed parsing using `System.ServiceModel.Syndication`
  - JSON API processing with `System.Text.Json`
  - SQLite database storage with upsert logic
  - Multi-source data aggregation
  - Error handling and logging
- **Dependencies:**
  - System.Data.SQLite.Core 1.0.118
  - System.ServiceModel.Syndication 8.0.0
  - System.Text.Json 9.0.0

### 2. PowerShell Orchestrator (`run_all.ps1`)
- **Language:** PowerShell 5.1
- **Features:**
  - Intelligent fallback (VB.NET → Python)
  - Structured logging with timestamps
  - Database health checks
  - Exit code management for scheduled tasks
  - Verbose mode for debugging

### 3. Python Fallback Collector (`data_collector.py`)
- **Language:** Python 3.12
- **Features:**
  - RSS parsing with `feedparser`
  - JSON API processing with `requests`
  - Date parsing with `python-dateutil`
  - Identical database schema to VB.NET
  - Automatic activation if VB.NET not compiled

### 4. SQLite Database (`eq12_sentinel.db`)
- **Schema:**
  ```sql
  Items (
    Id INTEGER PRIMARY KEY,
    SourceName TEXT NOT NULL,
    Category TEXT NOT NULL,
    ItemId TEXT NOT NULL,
    Title TEXT,
    Url TEXT,
    PublishedUtc TEXT,
    RawJson TEXT,
    InsertedUtc TEXT NOT NULL,
    UNIQUE(SourceName, ItemId)
  )
  ```
- **Indexes:** Category, SourceName, PublishedUtc
- **Current Size:** 56 KB (87 items)

---

## 📁 Directory Structure

```
C:\EQ12\WindowsDataSentinel\
├── config\
│   └── feeds.json              # Master data source configuration (12 feeds)
├── data\
│   └── eq12_sentinel.db        # SQLite database (auto-created)
├── logs\
│   └── run_all_*.log           # Execution logs with timestamps
├── src\
│   ├── VBDataCollector\
│   │   ├── Program.vb          # VB.NET source code (302 lines)
│   │   ├── VBDataCollector.vbproj
│   │   └── bin\Release\net8.0\
│   │       └── EQ12DataCollector.exe  # Compiled executable
│   └── PythonAnalytics\
│       ├── data_collector.py   # Python fallback (340 lines)
│       └── requirements.txt
└── scripts\
    ├── build_collector.ps1     # VB.NET build script
    ├── run_all.ps1             # Main orchestrator
    ├── register_scheduled_task.ps1  # Windows Task Scheduler setup
    └── database_summary.ps1    # Database statistics report
```

---

## 🚀 Quick Start

### Option 1: Run VB.NET Collector Directly
```powershell
C:\EQ12\WindowsDataSentinel\src\VBDataCollector\bin\Release\net8.0\EQ12DataCollector.exe
```

### Option 2: Run PowerShell Orchestrator
```powershell
cd C:\EQ12\WindowsDataSentinel\scripts
.\run_all.ps1 -Verbose
```

### Option 3: Run Python Fallback
```powershell
cd C:\EQ12\WindowsDataSentinel\src\PythonAnalytics
python data_collector.py --config ..\..\config\feeds.json
```

### View Database Summary
```powershell
cd C:\EQ12\WindowsDataSentinel\scripts
.\database_summary.ps1
```

---

## ⚙️ Configuration

### Data Sources (`config/feeds.json`)

**Current Configuration: 12 data sources (10 enabled)**

| Category | Source | Type | Poll Interval | Status |
|----------|--------|------|---------------|--------|
| **Legal** | SCOTUS Opinions | RSS | 60 min | ⚠️ DTD Issue |
| **Legal** | CourtListener API | JSON | 30 min | ⚠️ Auth Required |
| **Legal** | FTC Consumer Alerts | RSS | 60 min | ⚠️ 404 Error |
| **Credit** | CFPB Blog | RSS | 60 min | ✅ **25 items** |
| **Credit** | CFPB Complaints | JSON | Disabled | - |
| **Sports** | ESPN MLB | RSS | 30 min | ✅ **14 items** |
| **Sports** | ESPN NFL | RSS | 30 min | ✅ **20 items** |
| **Sports** | ESPN NBA | RSS | 30 min | ✅ **17 items** |
| **Weather** | OpenWeather Buffalo | JSON | 15 min | ✅ **1 item** |
| **Local** | Buffalo News | RSS | 30 min | ✅ **10 items** |
| **Finance** | SEC Edgar | RSS | 60 min | ⚠️ 403 Forbidden |
| **Finance** | IRS Tax Updates | RSS | Disabled | - |

### Fixing Feed Issues

**CourtListener (401 Unauthorized):**
```json
"apiKey": "YOUR_COURTLISTENER_API_KEY_HERE"
```
Get free API key: https://www.courtlistener.com/api/

**SCOTUS (DTD Security):**
- VB.NET requires `DtdProcessing.Parse` in XmlReaderSettings
- Python's `feedparser` handles DTD automatically
- Not critical - SCOTUS opinions rare (only 60-80/year)

**SEC Edgar (403 Forbidden):**
- Requires User-Agent header: "CompanyName contact@email.com"
- SEC blocks generic HTTP clients
- Low priority - financial filings less relevant for local business intelligence

---

## 🤖 Automated Scheduling

### Setup Windows Scheduled Task (15-Minute Polling)
```powershell
cd C:\EQ12\WindowsDataSentinel\scripts
.\register_scheduled_task.ps1
```

**Task Configuration:**
- **Name:** EQ12_WindowsDataSentinel
- **Trigger:** Every 15 minutes, forever
- **Action:** PowerShell run_all.ps1
- **Settings:**
  - Run with highest privileges
  - Network required
  - Battery safe
  - Multiple instances ignored

### Verify Scheduled Task
```powershell
Get-ScheduledTask -TaskName "EQ12_WindowsDataSentinel"
Get-ScheduledTaskInfo -TaskName "EQ12_WindowsDataSentinel"
```

### Unregister Task
```powershell
.\register_scheduled_task.ps1 -Unregister
```

---

## 🛠️ Development

### Rebuild VB.NET Collector
```powershell
cd C:\EQ12\WindowsDataSentinel\scripts
.\build_collector.ps1 -Clean
```

**Requirements:**
- .NET 8.0 SDK (current: 9.0.306 installed)
- Visual Studio 2022 or VS Code with .NET extension (optional)

### Install Python Dependencies
```powershell
cd C:\EQ12\WindowsDataSentinel\src\PythonAnalytics
pip install -r requirements.txt
```

**Dependencies:**
- feedparser >= 6.0.10
- requests >= 2.31.0
- python-dateutil >= 2.8.2

### Database Queries (SQLite)
```powershell
# Total items by category
sqlite3 C:\EQ12\WindowsDataSentinel\data\eq12_sentinel.db "SELECT Category, COUNT(*) FROM Items GROUP BY Category"

# Recent items
sqlite3 C:\EQ12\WindowsDataSentinel\data\eq12_sentinel.db "SELECT SourceName, Title FROM Items ORDER BY InsertedUtc DESC LIMIT 10"

# Items from last hour
sqlite3 C:\EQ12\WindowsDataSentinel\data\eq12_sentinel.db "SELECT COUNT(*) FROM Items WHERE datetime(InsertedUtc) > datetime('now', '-1 hour')"
```

---

## 📈 Current Performance

**Database Statistics (as of 2025-11-29):**
- **Total Items:** 87
- **Categories:** 4 (sports, credit, local, weather)
- **Data Sources:** 6 active
- **Database Size:** 56 KB
- **Date Range:** 2024-08-09 to 2025-11-29

**Top Sources:**
1. CFPB Blog: 25 items (credit/consumer protection)
2. ESPN NFL: 20 items (sports intelligence)
3. ESPN NBA: 17 items (sports intelligence)
4. ESPN MLB: 14 items (sports intelligence)
5. Buffalo News: 10 items (local news)
6. OpenWeather Buffalo: 1 item (weather data)

**Collection Success Rate:** 60% (6/10 enabled feeds working)

---

## 🎯 Next Steps

### Phase 1: Core Data Collection (✅ COMPLETE)
- [x] VB.NET RSS feed parser
- [x] VB.NET JSON API processor
- [x] SQLite database with indexes
- [x] PowerShell orchestrator
- [x] Python fallback collector
- [x] Windows Scheduled Task setup
- [x] Database summary reporting

### Phase 2: VB.NET Dashboard (NEXT - Week 1)
- [ ] WinForms or WPF application
- [ ] Data grid with filtering (category, source, date range)
- [ ] "Open URL in browser" functionality
- [ ] Real-time database query
- [ ] Auto-refresh every 5 minutes

### Phase 3: Python Analytics Layer (Week 2)
- [ ] Trend detection algorithms
- [ ] Alert generation (keyword matching)
- [ ] Telegram notifications
- [ ] Email digest generation
- [ ] API endpoint for dashboard

### Phase 4: B2B SaaS Packaging (Week 3-4)
- [ ] Multi-tenant database architecture
- [ ] Custom feed configuration per customer
- [ ] Alert customization per customer
- [ ] Billing integration (Stripe)
- [ ] Customer dashboard (web)

### Phase 5: Buffalo Market Launch (Week 5-8)
- [ ] Beta test with 10 local businesses
- [ ] Pricing tiers: $49 (basic), $149 (pro), $499 (enterprise)
- [ ] Local marketing campaign
- [ ] Sales automation (CRM integration)
- [ ] Target: 100 customers = $15K/month revenue

---

## 🔧 Troubleshooting

### "VB.NET collector not found"
**Solution:** Rebuild the VB.NET project:
```powershell
cd C:\EQ12\WindowsDataSentinel\scripts
.\build_collector.ps1
```

### "Database locked" error
**Solution:** Only one collector can run at a time. Check for running processes:
```powershell
Get-Process | Where-Object {$_.Name -like "*DataCollector*"}
```

### "401 Unauthorized" for CourtListener
**Solution:** Add API key to `feeds.json`:
```json
{
  "name": "CourtListener New Opinions",
  "apiKey": "YOUR_KEY_HERE"
}
```

### "429 Too Many Requests"
**Solution:** Increase poll interval in `feeds.json`:
```json
"pollMinutes": 60  // Change from 30 to 60
```

### Python dependencies missing
**Solution:**
```powershell
cd C:\EQ12\WindowsDataSentinel\src\PythonAnalytics
pip install -r requirements.txt
```

---

## 📞 Integration with EQ12 Ecosystem

**Related Projects:**
- **Legal Shield SaaS** (Project 2) - Uses legal feed data for case alerts
- **Sports Betting AI** (Existing) - Can consume ESPN feeds for real-time odds
- **Business Intelligence Tracker** (Existing) - Dashboard integration

**Shared Infrastructure:**
- **Telegram Bot:** 7913469072:AAHlN0XQyZG1G... (for alerts)
- **OpenWeather API:** 229507bc0f5ea7d23bd26958... (Buffalo weather)
- **SQLite Databases:** Common pattern across all EQ12 projects

**Revenue Synergy:**
- Local businesses get data sentinel + legal shield bundle (upsell)
- Sports intelligence adds value for sports bars/betting lounges
- Weather data valuable for outdoor event businesses

---

## 📄 License & Credits

**Project:** EQ12 Windows Data Sentinel  
**Owner:** Ricoj100  
**Status:** Proprietary - Part of EQ12 Business Intelligence Suite  
**Created:** 2025-11-29  
**Architecture:** Windows + VB.NET + PowerShell + SQLite (user-requested)  

**Part of:** EQ12 Strategic Project 1  
**Revenue Target:** $15K/month by Q2 2026  
**Market:** Buffalo/WNY small businesses (5,000 potential customers)  

---

## 🚀 Quick Reference

**Most Common Commands:**
```powershell
# Run data collection
.\scripts\run_all.ps1 -Verbose

# View database summary
.\scripts\database_summary.ps1

# Rebuild VB.NET collector
.\scripts\build_collector.ps1

# Register scheduled task
.\scripts\register_scheduled_task.ps1

# Query database
sqlite3 .\data\eq12_sentinel.db "SELECT * FROM Items LIMIT 10"
```

**File Locations:**
- Config: `C:\EQ12\WindowsDataSentinel\config\feeds.json`
- Database: `C:\EQ12\WindowsDataSentinel\data\eq12_sentinel.db`
- Logs: `C:\EQ12\WindowsDataSentinel\logs\run_all_*.log`
- VB.NET Exe: `C:\EQ12\WindowsDataSentinel\src\VBDataCollector\bin\Release\net8.0\EQ12DataCollector.exe`

---

**Status:** ✅ Foundation Complete - Ready for Dashboard Development
