# 📱 EQ12 Telegram Command Bundle — Master Control Center

Complete Telegram command map for remote control of your EQ12 automation stack.

---

## 🎯 Core Commands — Apple TV Integration

### `/sendtv_parlay`
**Purpose:** Send betting parlay to Apple TV
**Module:** `eq12_appletv_manager.py`
**Example Response:**
```
📺 PARLAY SENT TO APPLE TV

4-Leg MLB Mixed Parlay
• Braves ML (+150) | DraftKings
• Over 8.5 runs | FanDuel
• Yankees F5 ML (-110) | BetMGM
• Under 4.5 Ohtani Ks | Caesars

Combined Odds: 12.4x
Stake: $25 → Potential: $310
Edge: 8.2% | Confidence: 82%

📱 Apple TV Link: http://ngrok-url/tv/parlay
Tap to AirPlay from iPhone/iPad
```

### `/sendtv_deals`
**Purpose:** Send travel deals to Apple TV slideshow
**Module:** `eq12_appletv_manager.py`
**Example Response:**
```
✈️ DEALS SENT TO APPLE TV

Today's Top Travel Deals:
1. BUF → MCO: $49 RT (Spirit, Oct 15-22)
2. BUF → LAS: $89 RT (Frontier, Nov 2-9)
3. BUF → MIA: $67 RT (JetBlue, Dec 1-8)

🏨 Hotel Alert: Orlando $39/night (3-star)
🚗 Car Rental: $18/day (Economy)

📱 Apple TV Link: http://ngrok-url/tv/deals
QR codes included for instant booking
```

### `/sendtv_sales`
**Purpose:** Send finance/sales dashboard to Apple TV
**Module:** `eq12_appletv_manager.py`
**Example Response:**
```
📊 SALES DASHBOARD SENT TO APPLE TV

EQ12 Financial Overview:
💳 Credit Score: 572 (+8 this month)
🏦 Utilization: 12% (excellent)
💰 Savings: $2,847 (+$340 this month)
🚗 Turo Income: $520 this week

📈 Stack Performance:
• Betting ROI: +15.2% (30-day)
• Travel Savings: $1,240 YTD
• Cannabis Revenue: $890/month

📱 Apple TV Link: http://ngrok-url/tv/sales
Real-time financial tracking display
```

### `/appletv_devices`
**Purpose:** Discover and list Apple TV devices
**Module:** `eq12_streaming_engine.py`
**Example Response:**
```
📺 APPLE TV DEVICES DISCOVERED

Found 2 Devices:
1. Living Room Apple TV
   • IP: 192.168.1.150
   • Model: Apple TV 4K (3rd gen)
   • Status: Available for AirPlay

2. Bedroom Apple TV
   • IP: 192.168.1.151
   • Model: Apple TV HD
   • Status: Currently streaming

🌐 Network: 192.168.1.0/24
🔌 Streaming Server: Active (Port 8080)
📡 WebSocket: Active (Port 8081)
```

### `/appletv_status`
**Purpose:** Check Apple TV system health
**Module:** `eq12_appletv_master_launcher.py`
**Example Response:**
```
📊 APPLE TV COMMAND CENTER STATUS

🟢 Services Running:
✅ Content Server (Port 8080)
✅ WebSocket Server (Port 8081)
✅ Apple TV Manager
✅ Telegram Bot
❌ Streaming Engine (restarting...)

📈 Performance (24h):
• Content Streams: 47
• Telegram Commands: 23
• Apple TV Connections: 8
• Uptime: 23h 42m

🔄 Auto-Streaming: Active
⏰ Next Rotation: 2:34 PM (deals slideshow)
🏠 HomeKit Integration: Online
```

### `/homekit_lights`
**Purpose:** Trigger HomeKit lighting based on EQ12 events
**Module:** `eq12_appletv_manager.py`
**Example Response:**
```
🏠 HOMEKIT LIGHTS TRIGGERED

Parlay Mode Activated:
• Office Lights: Blue (betting focus)
• Accent Strip: Pulse blue
• Desk Lamp: Bright white

Event-Based Lighting:
🔵 Blue = Parlay/Betting mode
🟢 Green = Travel deals found
🟣 Purple = Sales milestone hit
🔴 Red = System alert/error

Current Scene: "EQ12 Betting Focus"
Duration: 30 minutes (auto-revert)
```

---

## ⚾ Sports Betting Commands

### `/parlay [size] [sport]`
**Purpose:** Generate new parlay with custom parameters
**Module:** `eq12_extension_backend.py`
**Example:** `/parlay 5 mlb`
**Response:**
```
⚾ 5-LEG MLB PARLAY GENERATED

Today's Sharp Picks:
1. Dodgers ML (-135) | FanDuel | Edge: 6.2%
2. Over 8.5 runs LAD/ATL | DraftKings | Edge: 4.8%
3. Ohtani Over 1.5 Ks | BetMGM | Edge: 7.1%
4. Braves F5 ML (+120) | Caesars | Edge: 5.9%
5. Under 4.5 team HRs | FanDuel | Edge: 8.3%

Combined: 24.7x odds | $25 stake → $618 potential
Expected Value: +$41.20 (14.2% edge)
Kelly Fraction: 3.8% of bankroll

📱 Send to Apple TV: /sendtv_parlay
💾 Save parlay: Saved to parlays.json
```

### `/hrparlay`
**Purpose:** Generate home run focused parlay
**Module:** `eq12_extension_backend.py`
**Response:**
```
🏟️ HOME RUN PARLAY LOCKED

3-Leg Power Hitter Special:
• Aaron Judge Over 0.5 HRs (+180) | DraftKings
• Vladimir Guerrero Jr Over 0.5 HRs (+220) | FanDuel
• Kyle Tucker Over 0.5 HRs (+200) | BetMGM

Wind Analysis: 12 mph out to RF (favorable)
Ballpark Factor: Yankee Stadium (HR friendly)
Temperature: 78°F (ball carries well)

Combined Odds: 21.8x | Confidence: 73%
Weather Edge: High (wind-assisted)
```

### `/odds [team/game]`
**Purpose:** Get live odds for specific games
**Module:** `odds_parser.py`
**Example:** `/odds yankees`
**Response:**
```
⚾ YANKEES LIVE ODDS

Game: NYY @ BOS (7:10 PM EST)
Pitchers: Cole vs. Sale

Moneyline:
• Yankees ML: -145 (DraftKings) ⭐ BEST
• Yankees ML: -140 (FanDuel)
• Red Sox ML: +125 (BetMGM) ⭐ BEST

Run Total:
• Over 8.5: -110 (Caesars)
• Under 8.5: -105 (FanDuel) ⭐ BEST

Spread:
• Yankees -1.5: +135 (DraftKings) ⭐ BEST
• Red Sox +1.5: -160 (BetMGM)

🔄 Updated: 12:34 PM | Next update: 12:39 PM
```

---

## ✈️ Travel & Deals Commands

### `/deal [origin] [destination]`
**Purpose:** Find travel deals for specific routes
**Module:** `travel_intelligence_scraper.py`
**Example:** `/deal buf vegas`
**Response:**
```
✈️ BUF → LAS DEALS FOUND

Cheapest Flights (Next 30 Days):
1. Oct 15-22: $89 RT | Spirit Airlines
   • Depart: 6:00 AM BUF → 8:45 AM LAS
   • Return: 9:20 PM LAS → 5:30 AM+1 BUF
   • Baggage: $65 extra | Seats: $45 extra

2. Nov 2-9: $124 RT | Southwest Airlines
   • Depart: 12:30 PM BUF → 2:15 PM LAS
   • Return: 8:10 PM LAS → 1:45 AM+1 BUF
   • Bags Included | WiFi: $8

🏨 Hotel Combo Deals:
• Luxor: $142/night (flight + hotel package)
• MGM Grand: $189/night (includes $50 credit)

📱 Book now: Links sent to Apple TV slideshow
💾 Watchlist: Deal saved for price monitoring
```

### `/watchlist`
**Purpose:** Show active travel price alerts
**Module:** `travel_watchlist_manager.py`
**Response:**
```
👀 ACTIVE TRAVEL WATCHLIST

Price Drop Alerts:
1. BUF → MCO | Target: <$60 | Current: $78 ↓$12
2. BUF → LAX | Target: <$120 | Current: $145 ↑$5
3. BUF → MIA | Target: <$70 | Current: $89 ↓$8

Hotel Alerts:
• Orlando Resort <$50/night | Current: $67
• Vegas Strip Hotel <$80/night | Current: $120

🔔 Notifications: 3 alerts in last 24h
📊 Avg Savings: 32% below target prices
⏰ Next check: 2:15 PM (every 30 minutes)
```

### `/hotels [city]`
**Purpose:** Find hotel deals in specific city
**Module:** `hotel_scraper.py`
**Response:**
```
🏨 ORLANDO HOTEL DEALS

Top Value Picks:
1. Holiday Inn Express I-Drive
   • $39/night (Oct 15-17) | ⭐⭐⭐⭐
   • Free breakfast | Pool | Shuttle to parks
   • 0.5 mi to Universal Studios

2. Hampton Inn Convention Center
   • $52/night (Oct 15-17) | ⭐⭐⭐⭐
   • Free breakfast | Gym | Business center
   • 1.2 mi to Disney Springs

Luxury Steals:
• Four Points Sheraton: $78/night (was $140)
• Hilton Garden Inn: $89/night (includes $25 credit)

🎢 Theme Park Packages Available
🚗 Car Rental: +$18/day (economy)
```

---

## 💰 Finance & Business Commands

### `/finance`
**Purpose:** Get comprehensive financial overview
**Module:** `finance_tracker.py`
**Response:**
```
💰 EQ12 FINANCIAL DASHBOARD

Credit Profile:
📊 Current Score: 572 (Experian)
📈 30-Day Change: +8 points
💳 Utilization: 12% across 4 cards
🏦 Available Credit: $4,200 total

Income Streams (This Month):
🚗 Turo Fleet: $1,340 (3 vehicles active)
🌿 Cannabis Side Business: $890
⚾ Betting Profits: +$267 (15.2% ROI)
🏠 Housing Projects: $0 (planning phase)

Expenses & Savings:
💸 Monthly Expenses: $1,847
💰 Net Savings: $640 this month
🎯 Goal Progress: 78% to $3,000 emergency fund

📊 Next Credit Check: Oct 30
🔄 Auto-updates every morning at 8 AM
```

### `/credit`
**Purpose:** Detailed credit analysis and recommendations
**Module:** `credit_optimizer.py`
**Response:**
```
📊 CREDIT ANALYSIS & OPTIMIZATION

Current Status:
• Experian: 572 (Fair)
• Equifax: 568 (Fair)
• TransUnion: 575 (Fair)

Score Factors:
✅ Payment History: 100% on-time (24 months)
⚠️ Utilization: 12% (target: <10%)
⚠️ Credit Age: 2.1 years (building)
✅ Account Mix: Good (4 cards, 1 auto loan)
✅ Recent Inquiries: 0 (last 6 months)

Optimization Plan:
1. Pay down Discover card by $150 → +12 points
2. Request CLI on Chase Freedom → +8 points
3. Add authorized user account → +15 points
4. Wait 3 months → age factor improvement

🎯 Projected Score: 607 by January 2026
💳 Next card recommendation: Chase Sapphire (12+ months)
```

### `/income`
**Purpose:** Track income streams and performance
**Module:** `income_tracker.py`
**Response:**
```
💵 INCOME STREAM ANALYSIS

Turo Fleet Performance:
🚗 2018 Honda Civic: $420/month (83% utilization)
🚙 2020 Toyota RAV4: $580/month (91% utilization)
🚐 2019 Honda Pilot: $340/month (67% utilization)
📊 Total Fleet Income: $1,340/month

Side Business Revenue:
🌿 Cannabis Kits: $890/month (growing 15%)
📦 Inventory Value: $2,340
🎯 Target: $1,200/month by year-end

Stack Automation:
⚾ Betting Algorithm: +$267 this month (15.2% ROI)
✈️ Travel Arbitrage: $0 (opportunities tracked)
🏠 Real Estate: $0 (USDA loan prep phase)

💡 Growth Opportunities:
• Add 4th Turo vehicle → +$400-600/month
• Scale cannabis operation → +$300-500/month
• Launch affiliate funnels → +$200-800/month
```

---

## 🏠 Housing & Real Estate Commands

### `/housing`
**Purpose:** Track housing search and USDA loan progress
**Module:** `housing_tracker.py`
**Response:**
```
🏠 HOUSING SEARCH & LOAN PROGRESS

USDA Loan Status:
✅ Pre-qualification: Complete ($185K approved)
✅ Credit requirements: Met (572 score)
⏳ Income verification: In progress
⏳ Property search: Active (rural Buffalo area)
❌ Final approval: Pending above items

Property Watchlist:
1. 4BR/2BA Farmhouse | Clarence, NY
   • $178K | 2.1 acres | Built 1995
   • USDA eligible ✅ | Needs: Minor repairs

2. 3BR/2BA Ranch | Akron, NY
   • $165K | 1.8 acres | Built 1987
   • USDA eligible ✅ | Condition: Move-in ready

Market Analysis:
📊 Avg Price: $171K (target area)
📈 30-Day Trend: +2.1% (seasonal increase)
🎯 Budget: $160K-185K (USDA limits)

⏰ Next Steps: Complete income docs by Oct 30
📅 Target Closing: January 2026
```

### `/nextmove`
**Purpose:** Dynamic roadmap for financial and life goals
**Module:** `goal_tracker.py`
**Response:**
```
🎯 EQ12 DYNAMIC ROADMAP

Immediate Priorities (Next 30 Days):
1. 📊 Complete USDA income verification
2. 💳 Pay down Discover to <10% utilization
3. 🚗 Add 4th Turo vehicle to fleet
4. 🌿 Scale cannabis inventory by 25%
5. ⚾ Maintain 12%+ betting ROI

3-Month Targets (Jan 2026):
• 🏠 Close on rural property (USDA loan)
• 💰 Build $3,000 emergency fund
• 📊 Achieve 600+ credit score
• 🚗 Generate $1,800+ monthly Turo income
• 🌿 Hit $1,200+ monthly cannabis revenue

6-Month Vision (April 2026):
• 🏠 Move into new property + start renovations
• 🎓 Complete Stationary Engineer license
• 💼 Launch affiliate marketing funnels
• 📈 Diversify income to 6+ streams
• 🚀 EQ12 stack fully autonomous

Progress Score: 73/100 (on track)
Risk Factors: Housing market volatility, credit timing
```

---

## 🔧 System Administration Commands

### `/status`
**Purpose:** Overall EQ12 system health check
**Module:** `system_monitor.py`
**Response:**
```
🟢 EQ12 SYSTEM STATUS

Core Services:
✅ FastAPI Backend (Port 8000)
✅ Telegram Bot
✅ Apple TV Command Center
✅ Chrome Extension Bridge
✅ Firefox Automation Engine
❌ VPN Connection (reconnecting...)

Active Automations:
🤖 Betting Bot: Running (last parlay: 2:14 PM)
✈️ Travel Monitor: Scanning (15 watchlist items)
💰 Finance Tracker: Synced (last update: 12:30 PM)
🏠 Housing Alerts: Active (3 properties tracked)

Performance (24h):
📊 API Calls: 2,847
📱 Telegram Commands: 67
📺 Apple TV Streams: 23
💾 Data Points Collected: 15,420

🔧 System Load: 12% CPU | 34% RAM
⚡ Uptime: 4 days, 18 hours
🌐 Network: 45ms latency | VPN: Reconnecting
```

### `/logs [service]`
**Purpose:** Get recent logs from specific service
**Module:** `log_manager.py`
**Example:** `/logs betting`
**Response:**
```
📋 BETTING ENGINE LOGS (Last 10 Entries)

[2025-09-28 14:23] INFO | Generated 4-leg MLB parlay | Edge: 8.2%
[2025-09-28 14:18] INFO | Odds sync complete | 847 markets updated
[2025-09-28 14:15] WARN | DraftKings API rate limit reached
[2025-09-28 14:12] INFO | Home run parlay hit +$180 | ROI: 12.3%
[2025-09-28 14:05] INFO | Weather data updated | Wind: 8mph out
[2025-09-28 13:58] INFO | Sharp line movement detected | Yankees ML
[2025-09-28 13:45] INFO | Kelly sizing recommendation: 2.8% bankroll
[2025-09-28 13:30] INFO | Parlay evaluation complete | 3 of 5 legs profitable
[2025-09-28 13:15] ERROR | BetMGM scraping failed | Retrying in 5 min
[2025-09-28 13:00] INFO | Daily betting summary generated

📊 Error Rate: 2.1% (acceptable)
⚠️ Active Issues: 1 (BetMGM connection)
🔄 Next log rotation: 11:59 PM
```

### `/restart [service]`
**Purpose:** Restart specific EQ12 service
**Module:** `service_manager.py`
**Example:** `/restart appletv`
**Response:**
```
🔄 RESTARTING APPLE TV COMMAND CENTER

Shutdown sequence:
✅ Stopping WebSocket server (Port 8081)
✅ Stopping content server (Port 8080)
✅ Closing Apple TV connections
✅ Saving current state to disk

Startup sequence:
✅ Loading configuration files
✅ Starting content server (Port 8080)
✅ Starting WebSocket server (Port 8081)
✅ Discovering Apple TV devices
✅ Reconnecting Telegram integration

🟢 Apple TV Command Center: ONLINE
📺 Devices found: 2 Apple TVs available
⏰ Restart duration: 12 seconds
🔄 Auto-streaming resumed: Parlay mode active
```

### `/update`
**Purpose:** Check for and apply EQ12 system updates
**Module:** `update_manager.py`
**Response:**
```
📥 CHECKING FOR EQ12 UPDATES

Available Updates:
1. 🔧 Apple TV System v2.1.3
   • Fixed: Unicode encoding errors
   • Added: Multi-device streaming
   • Security: Updated dependencies

2. 📊 Betting Engine v1.8.7
   • Added: NCAA Football support
   • Fixed: Weather API integration
   • Performance: 15% faster odds parsing

3. ✈️ Travel Monitor v2.0.1
   • Added: Hotel price tracking
   • Fixed: Southwest Airlines scraping
   • Feature: Price drop notifications

🚀 Apply Updates? Send /update confirm
⏰ Estimated Time: 3-5 minutes
🔒 Backup: Auto-created before update
❓ Skip updates: /update skip
```

---

## 📚 Help & Information Commands

### `/help`
**Purpose:** Show available commands by category
**Response:**
```
📚 EQ12 TELEGRAM COMMAND REFERENCE

📺 APPLE TV COMMANDS:
/sendtv_parlay - Send betting slip to TV
/sendtv_deals - Send travel deals to TV
/sendtv_sales - Send finance dashboard to TV
/appletv_devices - List Apple TV devices
/appletv_status - Check Apple TV system health
/homekit_lights - Trigger smart home lighting

⚾ BETTING COMMANDS:
/parlay [size] [sport] - Generate new parlay
/hrparlay - Home run focused parlay
/odds [team] - Get live odds for games

✈️ TRAVEL COMMANDS:
/deal [from] [to] - Find flight deals
/watchlist - Show price alerts
/hotels [city] - Find hotel deals

💰 FINANCE COMMANDS:
/finance - Full financial overview
/credit - Credit analysis & tips
/income - Income stream tracking
/housing - USDA loan & property progress
/nextmove - Dynamic goal roadmap

🔧 SYSTEM COMMANDS:
/status - Overall system health
/logs [service] - View recent logs
/restart [service] - Restart services
/update - Check for updates

Type /help [category] for detailed commands
Example: /help betting
```

### `/about`
**Purpose:** EQ12 system information and stats
**Response:**
```
🚀 EQ12 AUTOMATION COMMAND CENTER

Version: 2.4.1 (September 2025)
Uptime: 4 days, 18 hours, 32 minutes
Location: Buffalo, NY | Timezone: EST

System Capabilities:
📺 Apple TV Integration (AirPlay streaming)
🤖 Multi-browser automation (Firefox, Chrome, Edge)
📱 Telegram remote control (67 commands)
⚾ Sports betting optimization (15.2% ROI)
✈️ Travel deal monitoring (32% avg savings)
💰 Financial tracking & credit optimization
🏠 Real estate & USDA loan management

Performance Stats (30-day):
• Betting Profit: +$847 (15.2% ROI)
• Travel Savings: $1,240
• Credit Score Gain: +23 points
• Automation Success Rate: 94.7%
• Apple TV Streams: 156
• Telegram Commands: 1,247

Built with: Python, FastAPI, Playwright, OpenAI
Hardware: Windows 11 | 16GB RAM | 1TB NVMe
```

---

## ⚡ Quick Action Shortcuts

### Single-Word Commands:
- `/parlay` → Generate 4-leg mixed sport parlay
- `/deals` → Send today's travel deals to Apple TV
- `/status` → Quick system health check
- `/finance` → Full financial dashboard
- `/housing` → USDA loan and property progress

### Emergency Commands:
- `/kill` → Emergency stop all services
- `/reboot` → Full system restart
- `/safe` → Enable safe mode (disable all automation)
- `/backup` → Create immediate system backup

---

## 🔧 Command Syntax & Examples

### Parameter Options:
```bash
/parlay 5 mlb           # 5-leg MLB parlay
/parlay 3 nfl           # 3-leg NFL parlay
/deal buf vegas         # Buffalo to Vegas flights
/odds yankees           # Yankees game odds
/logs betting           # Betting engine logs
/restart appletv        # Restart Apple TV service
```

### Flexible Aliases:
- `/tv` = `/sendtv_parlay`
- `/money` = `/finance`
- `/bets` = `/parlay`
- `/flights` = `/deal`
- `/sys` = `/status`

---

**💡 Pro Tips:**
- Commands work case-insensitive: `/PARLAY` = `/parlay`
- Use `/help [command]` for detailed usage
- Star ⭐ important messages to save them
- Commands auto-complete in Telegram
- System auto-suggests related commands

**🎯 Most Used Commands:** `/parlay`, `/sendtv_deals`, `/finance`, `/status`, `/nextmove`

---

This command bundle gives you **complete remote control** of your EQ12 automation stack through Telegram. Whether you're betting, traveling, managing finances, or monitoring Apple TV displays — everything is one `/command` away.
