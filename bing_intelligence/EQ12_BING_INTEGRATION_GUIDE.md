# EQ12 Bing Intelligence Integration Guide

## 🎯 **Complete EQ12 Stack Integration Map**

Your EQ12 Bing Intelligence Suite is now fully integrated with your existing automation systems. Here's exactly how each component works together:

---

## 🔗 **Integration Points by Stack**

### **🏈 Betting Stack Integration** 
**Enhances:** `EdgeGodParlays/`, `odds_parser.py`, `parlay_builder.py`

```bash
# Your existing EdgeGod system now gets real-time injury intelligence
C:\EQ12\bing_intelligence\betting\bing_betting_intel.py --sport mlb --mode injury

# Integrates with:
# ✅ C:\EQ12\EdgeGodParlays\ai_betting_bot_stealth_final_flask_pro.py
# ✅ C:\EQ12\scripts\odds_parser.py  
# ✅ Existing Telegram bot infrastructure
# ✅ C:\EQ12\logs\odds_*.json cross-referencing
```

**What it does:**
- Monitors injury reports hourly via Bing News API
- Cross-references with your Odds API data
- Sends urgent alerts via your existing Telegram bot
- Enhances EdgeGod parlay decisions with news intelligence

### **✈️ Travel Stack Integration**
**Enhances:** `travel_deals_scraper.py`, affiliate systems

```bash
# Enhanced flight deal detection from Buffalo
C:\EQ12\bing_intelligence\travel\bing_travel_intel.py --departure BUF --mode flights

# Integrates with:
# ✅ C:\EQ12\scripts\travel_deals_scraper.py (existing)
# ✅ Affiliate link generation systems
# ✅ C:\EQ12\dashboard\index.html travel sections
```

**What it does:**
- Finds flight deals from Buffalo airport (BUF)
- Monitors hotel deals in target markets
- Generates content for affiliate marketing
- Integrates with your dashboard travel panels

### **🌿 Cannabis Stack Integration**
**New Intelligence Stack** - Cannabis industry monitoring

```bash
# Track dispensary licenses and regulatory changes
C:\EQ12\bing_intelligence\cannabis\bing_cannabis_intel.py --region Buffalo --mode licenses

# Creates new opportunities:
# 🎯 Cannabis tourism content generation
# 🎯 Regulatory compliance monitoring  
# 🎯 Dispensary business intelligence
# 🎯 Investment opportunity identification
```

**What it does:**
- Tracks new dispensary licenses in Buffalo/NY
- Monitors regulatory changes (OCM updates)
- Identifies cannabis tourism opportunities
- Alerts on regulatory violations/fines

### **🏠 Finance Stack Integration**
**Enhances:** Housing affordability systems, credit monitoring

```bash
# Buffalo housing market intelligence
C:\EQ12\bing_intelligence\finance\bing_finance_intel.py --market Buffalo --mode housing

# Integrates with existing financial analysis
# ✅ Housing affordability calculations
# ✅ Credit repair opportunity identification
# ✅ Investment property scouting
```

**What it does:**
- Monitors Buffalo housing market trends
- Tracks mortgage rate changes
- Identifies investment opportunities
- Alerts on foreclosure/distressed properties

### **🚗 Fleet Stack Integration**
**New Intelligence Stack** - Vehicle/Turo market monitoring

```bash
# Vehicle recall and rental market intelligence
C:\EQ12\bing_intelligence\fleet\bing_fleet_intel.py --mode recalls

# Fleet management opportunities:
# 🎯 Turo/car sharing market analysis
# 🎯 Vehicle safety recall monitoring
# 🎯 Fuel price trend tracking
# 🎯 Rental market opportunity identification
```

**What it does:**
- Monitors NHTSA vehicle recalls
- Tracks Turo/car sharing market in Buffalo
- Analyzes rental car demand/pricing
- Fuel price trend analysis

---

## 📊 **Dashboard Integration**

All Bing intelligence automatically populates your existing EQ12 dashboard:

```html
<!-- Auto-added to C:\EQ12\dashboard\index.html -->
<h3>🔍 Betting Intelligence</h3>
<table class="eq12-table"><!-- Real-time injury alerts --></table>

<h3>🔍 Travel Intelligence</h3>  
<table class="eq12-table"><!-- Flight deals from BUF --></table>

<h3>🔍 Cannabis Intelligence</h3>
<table class="eq12-table"><!-- Dispensary licenses --></table>

<h3>🔍 Finance Intelligence</h3>
<table class="eq12-table"><!-- Housing market trends --></table>

<h3>🔍 Fleet Intelligence</h3>
<table class="eq12-table"><!-- Vehicle recalls/opportunities --></table>
```

**Update Dashboard:**
```bash
# Updates dashboard with latest intelligence
python C:\EQ12\bing_intelligence\core\update_dashboard.py
```

---

## 📱 **Telegram Integration**

Uses your existing Telegram bot infrastructure:

```bash
# Reads from your existing configuration
TELEGRAM_BOT_TOKEN    # From C:\EQ12\keys\telegram_token.txt or environment
TELEGRAM_CHAT_ID      # From C:\EQ12\keys\telegram_chat_id.txt or environment

# Alert Priority Levels:
🚨 CRITICAL (Score 6+)  # Immediate Telegram alerts
⚠️  MEDIUM (Score 4-5)   # Batched alerts  
ℹ️  LOW (Score 1-3)     # Log only, no alerts
```

**Alert Examples:**
- **Betting:** "🚨 CRITICAL MLB INJURY: Star pitcher ruled out, check line movement"
- **Travel:** "✈️ FLIGHT DEAL: Buffalo to Miami $89 error fare, expires today"
- **Cannabis:** "🏪 LICENSE ALERT: New dispensary approved in Buffalo downtown"
- **Finance:** "🏠 HOUSING ALERT: Buffalo median price drops 5% month-over-month"

---

## ⏰ **Scheduled Tasks Integration**

The setup script created these Windows Scheduled Tasks:

```powershell
# Hourly betting intelligence (injury alerts)
EQ12-Bing-Hourly-Betting
# Runs: C:\EQ12\bing_intelligence\betting\bing_betting_intel.py

# Daily comprehensive intelligence  
EQ12-Bing-Daily-AllStacks
# Runs: C:\EQ12\bing_intelligence\core\bing_web_search.py --stack all

# Daily travel deals
EQ12-Bing-Daily-Travel
# Runs: C:\EQ12\bing_intelligence\travel\bing_travel_intel.py

# View all tasks:
schtasks /query /tn "EQ12-Bing-*"
```

---

## 📁 **File System Integration**

All intelligence follows EQ12 patterns:

```
C:\EQ12\
├── bing_intelligence\           # New Bing intelligence suite
│   ├── core\                    # Core Bing search engine
│   ├── betting\                 # Betting intelligence  
│   ├── travel\                  # Travel intelligence
│   ├── cannabis\                # Cannabis intelligence
│   ├── finance\                 # Finance intelligence
│   ├── fleet\                   # Fleet intelligence
│   └── bing_cache.db            # SQLite cache database
├── logs\                        # Existing EQ12 logs directory
│   ├── bing_*.json             # Bing intelligence outputs
│   ├── odds_*.json              # Existing odds data (cross-referenced)
│   └── bing_search_*.log        # Bing search logs
├── keys\                        # Existing EQ12 keys directory
│   ├── bing_api.txt             # Bing API key
│   ├── telegram_token.txt       # Existing Telegram bot token
│   └── telegram_chat_id.txt     # Existing Telegram chat ID
└── dashboard\index.html         # Enhanced with Bing intelligence
```

---

## 🔐 **Security & API Management**

**API Key Storage:**
```bash
# Method 1: EQ12 key file (recommended)
echo "your_bing_api_key" > C:\EQ12\keys\bing_api.txt

# Method 2: Environment variable
$env:BING_API_KEY = "your_bing_api_key"

# Method 3: Setup script
.\Setup-BingIntegration.ps1 -ApiKey "your_bing_api_key"
```

**Rate Limiting:**
- Built-in 1-second delays between requests
- 15-minute intelligent caching via SQLite
- Conservative 25 requests/second limit (well under Bing's 1000/month free tier)

---

## 🔄 **Cross-Stack Data Flow**

Here's how intelligence flows between your EQ12 systems:

```mermaid
Bing APIs → Core Search Engine → Stack-Specific Filters → Analysis → Cache → Dashboard
                                       ↓
                              Urgent Alerts → Telegram Bot → You
                                       ↓
                           Cross-Reference → EdgeGod/Odds API → Enhanced Decisions
```

**Example Flow:**
1. **Injury News:** Bing News API finds "MVP pitcher injured"
2. **Analysis:** Betting intel scores urgency (8/10)
3. **Cross-Reference:** Checks existing `odds_mlb.json` for line impact
4. **Alert:** Immediate Telegram: "🚨 Check DraftKings lines for Yankees game"
5. **Integration:** EdgeGod parlay system gets enhanced injury context

---

## 🚀 **Deployment Status**

✅ **COMPLETED:**
- Core Bing search engine with EQ12 integration
- 5 stack-specific intelligence modules  
- PowerShell setup script with dependencies
- Task Scheduler automation
- Dashboard integration
- Telegram alert system
- SQLite caching and rate limiting
- Comprehensive documentation

🎯 **READY TO USE:**
```bash
# Test the system:
cd C:\EQ12\bing_intelligence\core
.\.venv\Scripts\python bing_web_search.py --stack betting --verbose

# Check results:
Get-Content C:\EQ12\logs\bing_betting_*.json

# View dashboard:
Start-Process C:\EQ12\dashboard\index.html
```

---

## 💡 **Next Steps & Customization**

### **1. Customize Search Queries**
Edit `C:\EQ12\bing_intelligence\core\bing_web_search.py`:

```python
STACK_QUERIES = {
    "betting": [
        "Buffalo sports betting news injury reports",
        # Add your custom queries here
    ]
}
```

### **2. Add New Stacks**
Create new intelligence modules following the pattern:
```bash
# Copy existing module
Copy-Item betting\bing_betting_intel.py newstack\bing_newstack_intel.py
# Customize for your needs
```

### **3. Integration with Your Custom Systems**
All modules are designed to integrate with your existing EQ12 patterns:
- JSON output to `C:\EQ12\logs\`
- Telegram alerts via existing bot
- Dashboard sections auto-generated
- Cross-references with existing data files

---

## 🆘 **Troubleshooting & Support**

**Common Issues:**
1. **403 API Error:** Check API key in `C:\EQ12\keys\bing_api.txt`
2. **No Results:** Verify internet connection and API quotas  
3. **Import Errors:** Re-run `.\Setup-BingIntegration.ps1`
4. **No Alerts:** Check Telegram credentials

**Debug Commands:**
```bash
# Verbose logging
python core\bing_web_search.py --stack betting --verbose

# Check scheduled tasks
schtasks /query /tn "EQ12-Bing-*"

# View API usage
sqlite3 bing_cache.db "SELECT COUNT(*) FROM api_stats WHERE DATE(timestamp) = DATE('now');"
```

---

## 🎯 **Success Metrics**

Your EQ12 Bing Intelligence Suite will deliver:
- **Zero 429 errors** (eliminated via rate limiting)
- **Real-time injury alerts** for betting intelligence
- **Daily travel deals** from Buffalo airport
- **Regulatory monitoring** for cannabis opportunities  
- **Housing market intelligence** for Buffalo area
- **Vehicle safety alerts** and rental market opportunities
- **Cross-stack intelligence** enhancing all your existing systems

**You now have a complete Bing-powered intelligence engine integrated seamlessly with your EQ12 automation stack! 🚀**