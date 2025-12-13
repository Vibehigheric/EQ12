# EQ12 Master Control Panel - VB.NET Blueprint

## 🎯 **Project Overview**

**Name**: EQ12 Master Control Panel
**Language**: VB.NET (Windows Forms / WPF)
**Purpose**: Central GUI hub to control entire EQ12 automation empire
**Priority**: Phase 2 (after 20K prompts complete + SEC scraper operational)

---

## 🏗️ **Architecture**

### **Technology Stack**
- **Framework**: .NET 6.0+ (modern, cross-platform compatible)
- **UI**: Windows Forms (simpler, faster) OR WPF (modern, stylish)
- **Database**: SQLite (existing EQ12 databases)
- **Integration**: PowerShell subprocess calls + Python bridges
- **Charts**: LiveCharts2 (real-time visualization)
- **Icons**: FontAwesome or Material Design Icons

### **Project Structure**
```
EQ12MasterControlPanel\
├── EQ12.UI\                          # Main WPF/WinForms application
│   ├── MainWindow.xaml               # Main dashboard
│   ├── Modules\
│   │   ├── BettingModule.xaml        # Sports betting panel
│   │   ├── TradingModule.xaml        # Stock trading panel
│   │   ├── DataModule.xaml           # Data sources panel
│   │   ├── SystemModule.xaml         # System health panel
│   │   └── AutomationModule.xaml     # Script runner panel
│   └── Controls\
│       ├── LogViewer.xaml            # Real-time log display
│       ├── ChartWidget.xaml          # Live charts
│       └── StatusCard.xaml           # Metric cards
├── EQ12.Core\                        # Business logic
│   ├── Services\
│   │   ├── PowerShellService.vb      # Execute PS scripts
│   │   ├── PythonService.vb          # Execute Python scripts
│   │   ├── DatabaseService.vb        # SQLite connections
│   │   ├── APIService.vb             # Odds/Trading APIs
│   │   └── TelegramService.vb        # Telegram bot integration
│   └── Models\
│       ├── ParlayModel.vb            # Parlay data structures
│       ├── StockModel.vb             # Stock/holdings data
│       └── SystemMetrics.vb          # CPU/RAM/Disk metrics
└── EQ12.Tests\                       # Unit tests (NUnit)
    └── ServiceTests.vb
```

---

## 📱 **Main Dashboard Layout**

### **Top Bar**
```
┌─────────────────────────────────────────────────────────────┐
│ EQ12 Master Control Panel v1.0      [Minimize] [Close]      │
│ System Status: ✅ All Services Running    CPU: 45%  RAM: 12GB│
└─────────────────────────────────────────────────────────────┘
```

### **Left Sidebar (Module Navigation)**
```
┌──────────────────┐
│ 🏠 Dashboard     │
│ 🎲 Betting       │
│ 📈 Trading       │
│ 🌐 Data Sources  │
│ 🤖 Automation    │
│ 💰 Financial     │
│ 🛠️  System       │
│ 📊 Reports       │
│ ⚙️  Settings     │
└──────────────────┘
```

### **Center Panel (Dynamic Content)**
Switches based on selected module (see below)

### **Right Panel (Activity Feed)**
```
┌─────────────────────────┐
│ Recent Activity         │
├─────────────────────────┤
│ 15:32 Parlay generated  │
│ 15:30 Odds API updated  │
│ 15:25 13F filing scraped│
│ 15:20 Prompt executed   │
│ 15:15 System scan OK    │
└─────────────────────────┘
```

---

## 🎲 **Module 1: Betting Panel**

### **Quick Actions**
```
┌──────────────────────────────────────────────────┐
│ [Run 10-Leg Parlay Gen] [Run HR Parlay]         │
│ [Scan EV+ Opportunities] [Update Odds]          │
│ [Send to Telegram]       [Export to PDF]        │
└──────────────────────────────────────────────────┘
```

### **Live Parlay Display**
```
┌──────────────────────────────────────────────────┐
│ Latest Parlay (10-LEG) - Generated: 15:32        │
├──────────────────────────────────────────────────┤
│ 1. Aaron Judge OVER 0.5 HR (+140) **            │
│ 2. Shohei Ohtani OVER 1.5 H+R+RBI (-110)        │
│ 3. Yankees ML (-150)                             │
│ ...                                              │
│ Total Odds: +2500 | Risk: $100 | Win: $2,500   │
│ EV: +12.5% | Stars: 3 (**)                     │
└──────────────────────────────────────────────────┘
```

### **Integration Points**
- **PowerShell**: Call `run-parlay`, `run-odds`, `eq12-all-sports`
- **Python**: Execute `eq12_advanced_sports_betting_engine.py`
- **Database**: Read `prompt_execution.db` for AI-generated insights
- **Telegram**: Send formatted parlays via `TELEGRAM_BOT_TOKEN`

---

## 📈 **Module 2: Trading Panel**

### **Market Overview**
```
┌──────────────────────────────────────────────────┐
│ Citadel Holdings (Latest 13F)                    │
├──────────────────────────────────────────────────┤
│ Filing Date: 2025-08-14 | Period End: 2025-06-30│
│                                                   │
│ Top 10 Holdings:                                 │
│ 1. AAPL - Apple Inc.         $1.2B (+5%)        │
│ 2. MSFT - Microsoft Corp.    $980M (-2%)        │
│ 3. AMZN - Amazon.com Inc.    $850M (NEW)        │
│ ...                                              │
└──────────────────────────────────────────────────┘
```

### **Real-Time Charts** (LiveCharts2)
- Citadel portfolio allocation (pie chart)
- Position changes over time (line chart)
- Sector distribution (bar chart)

### **Integration Points**
- **Database**: Query `sec_13f_holdings.db`
- **Python**: Execute `eq12_sec_13f_scraper.py --scrape`
- **API**: Connect to Alpaca/IBKR for live prices (future)
- **PowerShell**: Run `EQ12_SEC_13F_SCRAPER.ps1 -Action report`

---

## 🌐 **Module 3: Data Sources Panel**

### **100-Source Registry Manager**
```
┌──────────────────────────────────────────────────┐
│ Active Data Sources: 54/100                      │
├──────────────────────────────────────────────────┤
│ Category: Odds API                               │
│ ✅ The Odds API (NBA)     Reliability: 0.98     │
│ ✅ Pinnacle (via RapidAPI) Reliability: 0.96     │
│ ⚠️  SportsData.io          Rate limit: 90%       │
│                                                   │
│ Category: Props                                  │
│ ✅ PrizePicks              Latency: 180ms        │
│ ✅ Underdog Fantasy        Latency: 200ms        │
│ ❌ Sleeper                 Status: DOWN          │
└──────────────────────────────────────────────────┘
```

### **Quick Actions**
```
[Test All Sources]  [Refresh Registry]  [Export Report]
[Enable Source]     [Disable Source]    [View Logs]
```

### **Integration Points**
- **JSON**: Load `data/data_sources_registry.json`
- **Python**: Execute health checks against each endpoint
- **Database**: Log source performance metrics
- **Alerts**: Notify via Telegram when sources go down

---

## 🤖 **Module 4: Automation Panel**

### **Script Runner**
```
┌──────────────────────────────────────────────────┐
│ Available Scripts (PowerShell)                   │
├──────────────────────────────────────────────────┤
│ [▶️] EQ12_PROMPT_RUNNER.ps1                      │
│ [▶️] EQ12_SEC_13F_SCRAPER.ps1                    │
│ [▶️] EQ12_SYSTEM_SCAN.ps1                        │
│ [▶️] run-parlay                                   │
│ [▶️] run-odds                                     │
│ [▶️] eq12-all-sports                              │
│                                                   │
│ Available Scripts (Python)                       │
├──────────────────────────────────────────────────┤
│ [▶️] eq12_sec_13f_scraper.py                     │
│ [▶️] eq12_prompt_executor.py                     │
│ [▶️] eq12_advanced_sports_betting_engine.py      │
└──────────────────────────────────────────────────┘
```

### **Scheduler**
```
┌──────────────────────────────────────────────────┐
│ Scheduled Tasks                                  │
├──────────────────────────────────────────────────┤
│ Daily 8:00 AM  - Odds API Update                │
│ Daily 10:00 AM - Parlay Generation              │
│ Weekly Mon 8 AM - SEC 13F Scrape                │
│ Hourly         - System Health Check            │
└──────────────────────────────────────────────────┘
```

### **Integration Points**
- **PowerShell**: `Start-Process -FilePath "powershell.exe"`
- **Python**: `Process.Start("python.exe", "script.py")`
- **Logs**: Real-time log viewer with tail functionality
- **Scheduler**: Windows Task Scheduler integration

---

## 💰 **Module 5: Financial Panel**

### **Overview Cards**
```
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Bankroll        │ │ Today's P/L     │ │ Credit Score    │
│ $2,450          │ │ +$125 (+5.1%)   │ │ 680 (Fair)      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### **Credit Tracker**
```
┌──────────────────────────────────────────────────┐
│ Credit Stacking Plan ($250K)                     │
├──────────────────────────────────────────────────┤
│ Phase 1: Secured cards          ✅ Complete      │
│ Phase 2: Store cards            🔄 In Progress   │
│ Phase 3: Premium cards          ⏸️  Waiting      │
│ Phase 4: Business cards         ⏸️  Waiting      │
│                                                   │
│ Current Total: $15,000 / $250,000 (6%)          │
└──────────────────────────────────────────────────┘
```

### **Turo Fleet**
```
┌──────────────────────────────────────────────────┐
│ Vehicle ROI Dashboard                            │
├──────────────────────────────────────────────────┤
│ 2018 Honda Civic - 85% utilization - $450/mo    │
│ 2020 Toyota Camry - 72% utilization - $520/mo   │
│                                                   │
│ Total Monthly Revenue: $970                      │
│ Expenses: $320 (insurance + maintenance)         │
│ Net Profit: $650/mo                              │
└──────────────────────────────────────────────────┘
```

### **Integration Points**
- **Database**: Store financial metrics in SQLite
- **Python**: Calculate ROI, credit utilization, etc.
- **Excel**: Export to `.xlsx` for tax purposes
- **Alerts**: Notify on payment due dates

---

## 🛠️ **Module 6: System Panel**

### **Health Dashboard**
```
┌──────────────────────────────────────────────────┐
│ System Metrics                                   │
├──────────────────────────────────────────────────┤
│ CPU: 45% [████████░░] 12 cores @ 3.6 GHz       │
│ RAM: 12.4 / 31.77 GB [████░░░░░░]              │
│ C:\ 583 GB free / 1,906 GB total [██████░░░░]  │
│ D:\ 399 GB free / 476 GB total   [████████░░]  │
│ Temp: 62°C (CPU) | 55°C (GPU)                   │
│                                                   │
│ Raspberry Pi @ 192.168.1.80: ✅ Reachable       │
└──────────────────────────────────────────────────┘
```

### **Quick Actions**
```
[Run System Scan]  [Clean Logs]  [Backup DBs]  [Update Scripts]
```

### **Integration Points**
- **PowerShell**: `EQ12_SYSTEM_SCAN.ps1 -Verbose`
- **WMI**: Query CPU, RAM, disk usage via System.Management
- **Network**: Ping Raspberry Pi, check service availability
- **Logs**: Display `logs/` directory size + cleanup

---

## 📊 **Module 7: Reports Panel**

### **Available Reports**
```
┌──────────────────────────────────────────────────┐
│ 📄 Daily Betting Summary (PDF)                   │
│ 📄 Weekly Performance Report (Excel)             │
│ 📄 Monthly Financial Snapshot (PDF)              │
│ 📄 Quarterly Portfolio Analysis (PDF)            │
│ 📄 Annual Tax Summary (CSV + PDF)                │
└──────────────────────────────────────────────────┘
```

### **Generate Report**
```
[Select Report Type ▼] [Date Range: Last 7 Days ▼] [Generate]
```

### **Integration Points**
- **iTextSharp**: Generate PDFs
- **EPPlus**: Generate Excel `.xlsx` files
- **Database**: Query all EQ12 databases for metrics
- **Email**: Send reports via SMTP (optional)

---

## ⚙️ **Module 8: Settings Panel**

### **API Keys Manager**
```
┌──────────────────────────────────────────────────┐
│ API Keys Configuration                           │
├──────────────────────────────────────────────────┤
│ OPENROUTER_API_KEY    sk-or-v1-3a54... [Edit]   │
│ ODDS_API_KEY          8eb82261...      [Edit]   │
│ TELEGRAM_BOT_TOKEN    7913469072...    [Edit]   │
│ GROQ_API_KEY          gsk_fSidK5...    [Edit]   │
│ GITHUB_TOKEN          github_pat_...   [Edit]   │
│                                                   │
│ [Test All Keys] [Save] [Import from ENV]        │
└──────────────────────────────────────────────────┘
```

### **Preferences**
```
┌──────────────────────────────────────────────────┐
│ General Settings                                 │
├──────────────────────────────────────────────────┤
│ ☑ Start with Windows                            │
│ ☑ Minimize to system tray                       │
│ ☑ Enable Telegram notifications                 │
│ ☑ Auto-update odds hourly                       │
│ ☐ Dark mode                                      │
│                                                   │
│ Default Parlay Size: [10] legs                   │
│ Risk Per Bet: [$100]                             │
│ EV Threshold: [+5%]                              │
└──────────────────────────────────────────────────┘
```

### **Integration Points**
- **Registry**: Store settings in Windows Registry
- **Config File**: JSON config file in `C:\EQ12\config.json`
- **Environment**: Read/write environment variables
- **Validation**: Test API keys before saving

---

## 🔧 **Implementation Plan**

### **Phase 1: Foundation (8-12 hours)**
1. Create WPF project in Visual Studio 2022
2. Design main window layout + navigation
3. Implement PowerShell/Python subprocess execution
4. Build log viewer control
5. Test basic script execution (run-parlay)

### **Phase 2: Core Modules (20-30 hours)**
1. Betting Panel + parlay display
2. Trading Panel + 13F integration
3. Data Sources Panel + registry loader
4. System Panel + health metrics

### **Phase 3: Advanced Features (15-20 hours)**
1. Automation Panel + scheduler
2. Financial Panel + credit tracker
3. Reports Panel + PDF generation
4. Settings Panel + API key manager

### **Phase 4: Polish (5-10 hours)**
1. Icons + styling (MaterialDesign theme)
2. Error handling + logging
3. Installer (ClickOnce or NSIS)
4. Documentation + user guide

**Total Estimated Time**: 48-72 hours (6-9 full days)

---

## 📦 **Dependencies (NuGet)**

```xml
<ItemGroup>
  <!-- UI Framework -->
  <PackageReference Include="MaterialDesignThemes" Version="4.9.0" />
  <PackageReference Include="LiveChartsCore.SkiaSharpView.WPF" Version="2.0.0-rc2" />
  
  <!-- Database -->
  <PackageReference Include="System.Data.SQLite" Version="1.0.118" />
  
  <!-- Reports -->
  <PackageReference Include="iTextSharp" Version="5.5.13.3" />
  <PackageReference Include="EPPlus" Version="7.0.5" />
  
  <!-- Utilities -->
  <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
  <PackageReference Include="Serilog" Version="3.1.1" />
</ItemGroup>
```

---

## 🎯 **Success Criteria**

✅ All PowerShell/Python scripts executable from GUI
✅ Real-time log viewer shows script output
✅ Database queries display correctly (parlays, 13F holdings)
✅ System metrics update every 5 seconds
✅ Telegram integration sends test message
✅ Reports generate successfully (PDF + Excel)
✅ Settings persist across restarts
✅ Installer creates Start Menu shortcut

---

## 🚀 **Next Steps**

1. **Wait for 20K prompts completion** (~54 hours)
2. **Complete Task #18** (GitHub/HuggingFace/OpenRouter integration)
3. **Verify SEC scraper operational** (run `.\EQ12_SEC_13F_SCRAPER.ps1`)
4. **Begin VB.NET development** (Phase 1: Foundation)

---

**Status**: Blueprint Complete - Ready for Implementation
**Priority**: Phase 2 (after prompts + AI integration)
**ROI**: High (central hub for all EQ12 automation)
**Created**: 2025-11-27
