# EQ12 Bing Intelligence Suite

**Comprehensive Bing API integration for all EQ12 automation stacks**

## 🎯 **Integration Overview**

This suite enhances your existing EQ12 automation with Bing intelligence across:
- **Betting Stack**: Real-time injury/news alerts for EdgeGod parlays
- **Travel Stack**: Flight deals and destination intelligence
- **Cannabis Stack**: Dispensary news and regulatory updates
- **Finance Stack**: Market intel and housing trends
- **Fleet Stack**: Vehicle recalls and rental market intelligence
- **Core Stack**: Cross-platform search and intelligence engine

## 🚀 **Quick Start**

1. **One-Click Setup**:
   ```powershell
   # Run as Administrator for Task Scheduler setup
   .\Setup-BingIntegration.ps1 -ApiKey "your_bing_api_key"
   ```

2. **Test Integration**:
   ```bash
   cd C:\EQ12\bing_intelligence\core
   .\.venv\Scripts\python bing_web_search.py --stack betting
   ```

3. **Check Results**:
   - View logs: `C:\EQ12\logs\bing_*.json`
   - Dashboard: Run `C:\EQ12\scripts\eq12-build-dashboard.ps1`

## 📁 **Directory Structure**

```
C:\EQ12\bing_intelligence\
├── core\                    # Core Bing search engine
│   ├── bing_web_search.py   # Main search intelligence
│   ├── bing_image_search.py # Image search & download
│   ├── bing_maps.py         # Maps & geocoding
│   └── update_dashboard.py  # Dashboard integration
├── betting\                 # Sports betting intelligence
│   ├── bing_betting_intel.py    # Injury/news alerts
│   ├── odds_cross_checker.py    # Cross-check with Odds API
│   └── telegram_alerts.py       # Urgent betting alerts
├── travel\                  # Travel deals intelligence
│   ├── bing_travel_intel.py     # Flight deals finder
│   ├── destination_scout.py     # Destination research
│   └── hotel_deals.py           # Hotel monitoring
├── cannabis\                # Cannabis industry intel
│   ├── dispensary_tracker.py    # License/location tracking
│   ├── regulation_monitor.py    # Legal updates
│   └── tourism_scout.py         # Cannabis tourism
├── finance\                 # Financial intelligence
│   ├── housing_tracker.py       # Buffalo housing market
│   ├── credit_intel.py          # Credit/finance news
│   └── macro_monitor.py         # Economic indicators
└── fleet\                   # Vehicle/fleet intelligence
    ├── recall_monitor.py         # Auto recalls
    ├── rental_market.py          # Turo/rental intel
    └── fuel_tracker.py           # Gas prices/trends
```

## 🔧 **EQ12 Integration Points**

### **Existing System Enhancement**:
- **EdgeGod Parlays**: Real-time injury alerts via Bing News API
- **Travel Scraper**: Enhanced with Bing flight deal detection
- **Telegram Bot**: Urgent alerts using existing bot infrastructure
- **Dashboard**: Intelligence sections added to `C:\EQ12\dashboard\index.html`
- **Logging**: Follows EQ12 patterns (`C:\EQ12\logs\bing_*.json`)
- **API Keys**: Uses EQ12 key management (`C:\EQ12\keys\bing_api.txt`)

### **Scheduled Tasks Created**:
- `EQ12-Bing-Hourly-Betting`: Injury/news monitoring (hourly)
- `EQ12-Bing-Daily-Travel`: Flight deals (06:00 daily)
- `EQ12-Bing-Daily-AllStacks`: Comprehensive intelligence (06:00 daily)

## 🎪 **Stack-Specific Usage**

### **Betting Stack**
```python
# Enhanced injury monitoring for EdgeGod system
python betting/bing_betting_intel.py
```
- Real-time injury alerts
- Cross-references with Odds API data
- Telegram notifications for urgent news

### **Travel Stack**
```python
# Flight deals from Buffalo (BUF)
python travel/bing_travel_intel.py --departure BUF
```
- Monitors cheap flight deals
- Destination research automation
- Hotel deal tracking

### **Cannabis Stack**
```python
# Buffalo dispensary intelligence
python cannabis/dispensary_tracker.py --location Buffalo
```
- New license tracking
- Regulatory update monitoring
- Cannabis tourism opportunities

## 🔑 **API Key Setup**

1. **Get Bing Search API Key**:
   - Sign up at: [Azure Portal](https://portal.azure.com)
   - Create "Bing Search v7" resource
   - Copy API key

2. **Store Securely**:
   ```powershell
   # Method 1: Setup script
   .\Setup-BingIntegration.ps1 -ApiKey "your_key_here"

   # Method 2: Manual
   echo "your_bing_api_key" > C:\EQ12\keys\bing_api.txt

   # Method 3: Environment variable
   $env:BING_API_KEY = "your_bing_api_key"
   ```

## 📊 **Dashboard Integration**

The Bing intelligence automatically integrates with your existing EQ12 dashboard:

```html
<!-- Added to C:\EQ12\dashboard\index.html -->
<h3>🔍 Betting Intelligence</h3>
<table class="eq12-table">
  <tr><th>Title</th><th>Summary</th><th>Time</th></tr>
  <!-- Real-time injury alerts here -->
</table>

<h3>🔍 Travel Intelligence</h3>
<table class="eq12-table">
  <tr><th>Title</th><th>Summary</th><th>Time</th></tr>
  <!-- Flight deals here -->
</table>
```

## 🤖 **Advanced Automation**

### **Cross-Stack Intelligence**
```python
# Run comprehensive intelligence across all stacks
python core/bing_web_search.py --stack all --export json

# Custom queries for specific needs
python core/bing_web_search.py --custom-query "Buffalo dispensary grand opening December 2025"
```

### **Telegram Integration**
The system uses your existing EQ12 Telegram infrastructure:
- Reads `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from environment
- Sends urgent alerts (injuries, deals, breaking news)
- Integrates with EdgeGod parlay system alerts

### **Database Caching**
All searches are cached in SQLite for performance:
```sql
-- Located at: C:\EQ12\bing_intelligence\bing_cache.db
SELECT * FROM search_results WHERE stack = 'betting' ORDER BY timestamp DESC;
```

## 🛡️ **Legal & Best Practices**

- **Rate Limiting**: Built-in 1-second delays between requests
- **Official APIs**: Uses Bing Search API (not web scraping)
- **Caching**: 15-minute intelligent cache to minimize API calls
- **Error Handling**: Robust retry logic with exponential backoff
- **TOS Compliance**: Respects Bing API usage guidelines

## 📈 **Performance & Monitoring**

- **Logs**: All activity logged to `C:\EQ12\logs\bing_search_YYYYMMDD.log`
- **Metrics**: Search counts, API response times, cache hit rates
- **Alerts**: Failed API calls trigger Telegram notifications
- **Cleanup**: Automatic log rotation and database pruning

## 🔧 **Customization**

Edit search queries in `core/bing_web_search.py`:

```python
STACK_QUERIES = {
    "betting": [
        "Buffalo sports betting news injury reports",
        "MLB player injury betting impact latest",
        # Add your custom queries here
    ],
    "travel": [
        "Buffalo airport cheap flights December 2025",
        # Add your routes here
    ]
}
```

## 🆘 **Troubleshooting**

**Common Issues**:
1. **403 API Error**: Check API key in `C:\EQ12\keys\bing_api.txt`
2. **No Results**: Verify internet connection and API quotas
3. **Task Scheduler**: Run setup as Administrator
4. **Dependencies**: Re-run `.\Setup-BingIntegration.ps1 --SkipInstall`

**Debug Mode**:
```python
python core/bing_web_search.py --stack betting --verbose
```

## 📞 **Support**

- **EQ12 Integration**: Follows existing patterns in `C:\EQ12\scripts\`
- **Bing API Documentation**: [Microsoft Bing Search APIs](https://docs.microsoft.com/en-us/bing/search-apis/)
- **Task Scheduler**: Use `schtasks /query /tn "EQ12-Bing-*"` to verify jobs

---

**Ready to supercharge your EQ12 automation with Bing intelligence? Run the setup script and start getting actionable intelligence across all your stacks! 🚀**
