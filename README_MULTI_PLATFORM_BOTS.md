# EQ12 Multi-Platform Bot Architecture

Complete automation control hub with visual input system and multi-channel distribution.

## System Overview

The EQ12 stack now includes a comprehensive multi-platform bot architecture that transforms your automation environment into a complete command and control system:

### 🏗️ **Architecture Components**

1. **Master Telegram Bot** (`eq12_telegram_master_bot.py`)
   - 67+ commands across 5 categories (sports, travel, finance, Apple TV, system)
   - Multi-channel support (command, public, premium)
   - Structured response system with inline keyboards
   - Cross-posting to Discord servers
   - Real-time EQ12 API integration

2. **Discord Integration** (`eq12_discord_bot.py`)
   - Dual server architecture:
     - **Ops Server**: Private mission control for admin/team coordination
     - **Community Server**: Public affiliate funnel with premium channels
   - Cross-platform messaging (Discord ↔ Telegram sync)
   - Role-based access control
   - Apple TV content streaming integration

3. **Visual Input System** (`eq12_snip_watcher.py`)
   - OCR-powered screenshot processing
   - Automatic content routing (betting/travel/finance)
   - Real-time visual data capture
   - Integration with all bot platforms

4. **Apple TV Command Center** (Previous delivery)
   - AirPlay content distribution
   - Real-time parlay/deal streaming
   - HomeKit integration
   - Cross-platform control interface

## 🎯 **Command Interface**

### Telegram Master Bot Commands

**Sports Betting Automation:**
```
/parlay [size] [sport]     # Generate parlay (default: 5-leg NFL)
/hrparlay                  # Heavy round parlay
/locks [count]             # Get lock picks
/odds [game]              # Live odds lookup
/bankroll                 # Bankroll management
```

**Travel Deal Monitoring:**
```
/deal [from] [to]         # Flight search (default: BUF→LAX)
/watchlist                # View/manage watchlist
/hotels [city]            # Hotel deals
/nextmove                 # Relocation analysis
```

**Finance Tracking:**
```
/finance                  # Portfolio snapshot
/credit                   # Credit monitoring
/income                   # Income analysis
/housing                  # Housing progress
```

**Apple TV Integration:**
```
/sendtv_parlay           # Stream parlay to Apple TV
/sendtv_deals           # Stream deals to Apple TV
/appletv_devices        # Device management
/homekit_lights         # Smart home control
```

**System Administration:**
```
/status                  # System health
/logs                   # View logs
/restart                # Restart services
/update                 # System updates
```

### Discord Bot Commands

**Mission Control (Ops Server):**
```
!eq12 status            # Bot status and integrations
!eq12 parlay 5 nfl      # Generate and distribute parlay
!eq12 deal BUF LAX      # Find and post travel deal
!eq12 sendtv parlay     # Stream content to Apple TV
!eq12 snip              # Snip watcher status
```

## 📱 **Multi-Channel Distribution**

### Content Flow Architecture

```
Visual Input (Screenshots)
    ↓ [OCR Processing]
EQ12 Snip Watcher
    ↓ [Content Routing]
EQ12 APIs (Betting/Travel/Finance)
    ↓ [Distribution]
┌─ Telegram Master Bot ←→ Discord Ops Server
└─ Apple TV Streaming    ←→ Discord Community Server
```

### Channel Configuration

**Telegram Channels:**
- **Command Channel**: Primary bot interface
- **Public Channel**: Open community content
- **Premium Channel**: Subscriber-only content

**Discord Servers:**
- **Ops Server** (Private):
  - #alerts - System notifications
  - #betting - Parlay generation and tracking
  - #travel - Deal monitoring and alerts
  - #finance - Portfolio and credit tracking
  - #appletv - Content streaming control
  - #snips - Visual input monitoring
  - #logs - System health and activity

- **Community Server** (Public):
  - #general - Community discussion
  - #betting - Public betting content
  - #travel - Public travel deals
  - #premium - Premium subscriber content
  - #affiliate - Affiliate program management

## 🔧 **Setup and Deployment**

### 1. Core Dependencies
```powershell
# Python packages
pip install python-telegram-bot discord.py pytesseract watchdog pillow aiohttp requests

# OCR Engine (Windows)
# Download: https://github.com/tesseract-ocr/tesseract
```

### 2. Environment Variables
```powershell
$env:TELEGRAM_BOT_TOKEN = "your_telegram_token"
$env:DISCORD_BOT_TOKEN = "your_discord_token"
$env:ODDS_API_KEY = "your_odds_api_key"
$env:OPENAI_API_KEY = "your_openai_key"
```

### 3. Bot Configuration

**Telegram Bot Setup:**
```powershell
.\eq12_telegram_master_bot.ps1 -Start
```

**Discord Bot Setup:**
```powershell
.\eq12_discord_bot.ps1 -Setup    # Create configuration
.\eq12_discord_bot.ps1 -Config   # Edit server/channel IDs
.\eq12_discord_bot.ps1 -Start    # Launch bot
```

**Snip Watcher Setup:**
```powershell
.\eq12_snip_watcher.ps1 -Start   # Start visual monitoring
```

### 4. Apple TV Integration
```powershell
.\eq12_appletv_manager.ps1 -Start     # Start Apple TV system
.\eq12_appletv_streaming.ps1 -Start   # Start streaming engine
```

## 🎮 **Usage Examples**

### Complete Betting Workflow
```
1. Screenshot odds from sportsbook app
   → Saved to C:\EQ12\snips\

2. Snip Watcher processes image
   → OCR extracts game/odds data
   → Routes to /api/parlay endpoint

3. Telegram bot generates parlay
   /parlay 5 nfl
   → Creates 5-leg NFL parlay
   → Posts to Telegram + Discord

4. Stream to Apple TV
   /sendtv_parlay
   → Displays parlay on Apple TV
   → Shows on all connected devices
```

### Travel Deal Pipeline
```
1. Screenshot flight deal
   → Processed by Snip Watcher
   → Extracted price/route data

2. Discord command triggers search
   !eq12 deal BUF LAX
   → Searches flight APIs
   → Posts results to channels

3. Cross-platform distribution
   → Telegram premium channel
   → Discord community server
   → Apple TV dashboard display
```

## 📊 **Monitoring and Analytics**

### System Health Dashboard
```powershell
# Check all components
.\eq12_telegram_master_bot.ps1 -Status
.\eq12_discord_bot.ps1 -Status
.\eq12_snip_watcher.ps1 -Status
.\eq12_appletv_manager.ps1 -Status

# View processing stats
.\eq12_snip_watcher.ps1 -Stats
.\eq12_discord_bot.ps1 -Config
```

### Log Monitoring
- **Telegram Bot**: `C:\EQ12\logs\telegram_master\`
- **Discord Bot**: `C:\EQ12\logs\discord_bot\`
- **Snip Watcher**: `C:\EQ12\logs\snip_watcher\`
- **Apple TV**: `C:\EQ12\logs\appletv\`

## 🚀 **Advanced Features**

### Cross-Platform Synchronization
- Telegram ↔ Discord message sync
- Unified command processing
- Shared analytics and logging
- Multi-channel content distribution

### Visual Input Processing
- Screenshot → OCR → Structured data
- Automatic content type detection
- Real-time processing pipeline
- Integration with all platforms

### Premium Content Distribution
- Role-based access control
- Subscriber-only channels
- Affiliate link management
- Revenue tracking integration

### Smart Home Integration
- Apple TV content streaming
- HomeKit device control
- Automated lighting/display
- Voice command integration

## 🎯 **Next Phase: Enterprise Architecture**

The current multi-platform bot system provides the foundation for enterprise-scale deployment with:

- **Visual Studio Solution**: C#/.NET + Python hybrid architecture
- **Windows Service Integration**: Background processing services
- **Database Layer**: Structured data persistence
- **Web Dashboard**: Browser-based control interface
- **API Gateway**: Centralized endpoint management
- **Containerization**: Docker deployment ready

This creates a complete automation ecosystem where **Telegram becomes your command console**, **Discord becomes your mission control + community hub**, and **visual input captures data from any source** for processing through the entire EQ12 stack.

The architecture transforms your environment from individual scripts into a **unified automation command center** with multi-platform distribution, visual input processing, and comprehensive monitoring across all channels.
