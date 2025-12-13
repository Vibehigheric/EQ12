# Complete EQ12 Apple TV Command Center Integration

## 📺 Overview

Transform your Apple TV into a real-time command center for the EQ12 automation stack. This system streams live betting slips, travel deals, sales dashboards, and triggers smart home automation - all controlled via Telegram and automated workflows.

---

## 🎯 What This System Does

### Real-Time Content Streaming
- **📺 Betting Slips**: Live parlay tickets with QR codes stream to your TV during games
- **✈️ Travel Deals**: Automated slideshow of flight deals with price alerts
- **📈 Sales Dashboards**: Live commerce stats from eBay, Etsy, Turo with real-time updates
- **🏠 Smart Home**: HomeKit lighting and automation triggers based on wins/losses

### Telegram Integration
- **/sendtv_parlay** - Stream latest betting parlay to Apple TV
- **/sendtv_deals** - Show travel deals slideshow
- **/sendtv_sales** - Display live sales dashboard
- **/appletv_devices** - Discover and manage Apple TVs
- **/homekit_lights <color>** - Control smart home lighting

### Automated Features
- **Auto-Discovery**: Finds Apple TVs on your network automatically
- **Real-Time Updates**: WebSocket connections for instant content refresh
- **Smart Scheduling**: Auto-streams content every 15 minutes
- **Health Monitoring**: System status and performance tracking

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Install required packages
pip install requests pystray pillow qrcode2 jinja2 websockets python-telegram-bot zeroconf netifaces

# Optional: Install for HomeKit integration
pip install homekit
```

### 2. Configure Telegram Bot
```bash
# Set environment variables or create key files
set TELEGRAM_BOT_TOKEN=your_bot_token_here
set TELEGRAM_CHAT_ID=your_chat_id_here

# Or save to files:
echo "your_bot_token" > C:\EQ12\keys\telegram_bot_token.txt
echo "your_chat_id" > C:\EQ12\keys\telegram_chat_id.txt
```

### 3. Launch Complete System
```bash
# Start everything with one command
cd C:\EQ12\appletv_system
python eq12_appletv_master_launcher.py

# System will auto-discover Apple TVs and start all services
```

### 4. Test Via Telegram
```
/start - Get welcome message
/sendtv_parlay - Stream demo betting slip
/appletv_devices - Check discovered Apple TVs
```

---

## 📁 System Architecture

```
C:\EQ12\appletv_system\
├── eq12_appletv_manager.py          # Apple TV content generation & management
├── eq12_streaming_engine.py         # Real-time AirPlay streaming protocol
├── eq12_telegram_appletv_bot.py     # Telegram bot integration
├── eq12_appletv_master_launcher.py  # Master orchestration system
├── templates/                       # HTML/CSS templates for Apple TV
│   ├── betting_slip.html           # Betting parlay display template
│   ├── travel_deals.html           # Travel deals slideshow template
│   └── sales_dashboard.html        # Sales metrics dashboard template
└── content/                        # Generated content and QR codes
```

### Service Components

1. **Apple TV Manager** (`eq12_appletv_manager.py`)
   - Content generation and templating
   - QR code creation for betting slips
   - HomeKit automation triggers
   - Device discovery and management

2. **Streaming Engine** (`eq12_streaming_engine.py`)
   - AirPlay protocol implementation
   - WebSocket real-time updates
   - Multi-device streaming coordination
   - Network discovery and health checks

3. **Telegram Bot** (`eq12_telegram_appletv_bot.py`)
   - Command processing and user interface
   - Real-time interaction with Apple TV system
   - Status monitoring and device management
   - Integration with EQ12 backend APIs

4. **Master Launcher** (`eq12_appletv_master_launcher.py`)
   - Complete system orchestration
   - Auto-streaming content loops
   - Health monitoring and performance tracking
   - Graceful startup and shutdown

---

## 🎨 Content Templates

### Betting Slip Template
- **Design**: Gradient background with glassmorphism effects
- **Features**: Live indicator, QR codes, team logos, odds display
- **Auto-refresh**: Every 30 seconds for live updates
- **HomeKit**: Triggers blue lights when parlay is generated

### Travel Deals Template
- **Design**: Dynamic gradient animation with card-based layout
- **Features**: Route maps, price alerts, urgency indicators
- **Auto-refresh**: Every 45 seconds for new deals
- **HomeKit**: Triggers green lights for new deal alerts

### Sales Dashboard Template
- **Design**: Professional dark theme with metric cards
- **Features**: Real-time revenue, conversion rates, live ticker
- **Auto-refresh**: Every 60 seconds for live stats
- **HomeKit**: Triggers purple lights for sales updates

---

## 🌐 API Endpoints

### Content Server (Port 8080)
- `http://localhost:8080/current` - Current displayed content
- `http://localhost:8080/betting_slip.html` - Betting slip template
- `http://localhost:8080/travel_deals.html` - Travel deals template
- `http://localhost:8080/sales_dashboard.html` - Sales dashboard template

### WebSocket Server (Port 8081)
- `ws://localhost:8081` - Real-time updates and device control
- **Messages**: `stream_content`, `get_devices`, `ping/pong`
- **Broadcasts**: `stream_started`, `device_discovered`, `status_update`

---

## 📱 Telegram Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message and setup info | `/start` |
| `/sendtv_parlay` | Stream latest betting parlay to Apple TV | `/sendtv_parlay` |
| `/sendtv_deals` | Stream travel deals slideshow | `/sendtv_deals` |
| `/sendtv_sales` | Stream sales dashboard | `/sendtv_sales` |
| `/appletv_devices` | Show discovered Apple TV devices | `/appletv_devices` |
| `/appletv_status` | Check streaming status and metrics | `/appletv_status` |
| `/homekit_lights <color>` | Control HomeKit smart lights | `/homekit_lights green` |

### Advanced Commands (Planned)
- `/schedule_content <type> <time>` - Schedule automatic content streaming
- `/device_priority <device> <priority>` - Set preferred streaming device
- `/homekit_scene <scene>` - Trigger complex HomeKit scenes
- `/content_history` - View recent streaming history

---

## 🏠 HomeKit Integration

### Automatic Light Triggers
- **Parlay Generated**: Blue lights (80% brightness)
- **Travel Deal Alert**: Green lights (60% brightness)
- **Sales Update**: Purple lights (50% brightness)
- **Big Win**: Gold lights (100% brightness + flash)
- **Big Loss**: Red lights (30% brightness)

### Siri Shortcuts Integration (macOS)
```bash
# Create Siri shortcuts to trigger EQ12 actions
shortcuts run "EQ12 Send Parlay"
shortcuts run "EQ12 Travel Deals"
shortcuts run "EQ12 Sales Dashboard"
```

### Home Assistant Integration
```yaml
# Example Home Assistant automation
automation:
  - alias: "EQ12 Apple TV Parlay Alert"
    trigger:
      platform: webhook
      webhook_id: eq12_parlay_generated
    action:
      - service: light.turn_on
        entity_id: light.living_room
        data:
          color_name: blue
          brightness: 200
```

---

## ⚙️ Configuration Options

### Auto-Streaming Settings
```python
# Edit in eq12_appletv_master_launcher.py
auto_stream_config = {
    "parlay_notifications": True,      # Auto-stream new parlays
    "travel_deals_updates": True,      # Auto-stream travel deals
    "sales_dashboard_refresh": True,   # Auto-refresh sales dashboard
    "homekit_automation": True,        # Enable HomeKit triggers
    "stream_interval_minutes": 15      # Auto-stream every 15 minutes
}
```

### Network Configuration
```python
# Edit device discovery settings
default_appletv_ip = "192.168.1.100"  # Your Apple TV IP
dashboard_port = 8080                  # Content server port
websocket_port = 8081                  # WebSocket server port
```

### Content Styling
```css
/* Customize templates in templates/ directory */
/* Edit betting_slip.html, travel_deals.html, sales_dashboard.html */
/* Change colors, fonts, animations, layouts */
```

---

## 🔧 Troubleshooting

### Apple TV Not Discovered
1. **Check Network**: Ensure Apple TV and computer on same network
2. **Enable AirPlay**: Settings > AirPlay and HomeKit > Allow Access: Everyone
3. **Manual IP**: Set `default_appletv_ip` to your Apple TV's IP address
4. **Firewall**: Allow Python through Windows Firewall

### Streaming Issues
1. **Check Ports**: Ensure ports 8080, 8081, 7000 are not blocked
2. **Content Server**: Verify `http://localhost:8080/current` works
3. **WebSocket**: Test WebSocket connection at `ws://localhost:8081`
4. **Logs**: Check logs in `C:\EQ12\logs\appletv\` for errors

### Telegram Bot Issues
1. **Token**: Verify `TELEGRAM_BOT_TOKEN` is correct
2. **Chat ID**: Get your chat ID with `/start` command first
3. **Permissions**: Bot needs message permissions in your chat
4. **API Limits**: Check Telegram API rate limits

### HomeKit Issues
1. **Platform**: HomeKit integration works best on macOS
2. **Shortcuts**: Install Shortcuts app and create EQ12 shortcuts
3. **Home App**: Add devices to Home app first
4. **Permissions**: Grant Home access to shortcuts

---

## 📊 Performance Monitoring

### System Metrics Tracked
- **Devices Discovered**: Number of Apple TVs found on network
- **Content Streams**: Total streaming sessions initiated
- **Telegram Commands**: Commands processed via bot
- **HomeKit Triggers**: Smart home automations executed
- **Uptime**: System availability and reliability
- **Response Times**: Content generation and streaming performance

### Health Reports
```bash
# View health reports
cat C:\EQ12\logs\appletv\health_report_20251028.json

# Monitor in real-time
tail -f C:\EQ12\logs\appletv\master_controller.log
```

---

## 🔮 Future Enhancements

### Advanced Features (Planned)
- **Multi-Room Streaming**: Stream different content to multiple Apple TVs
- **Voice Control**: "Hey Siri, stream EQ12 parlay to living room TV"
- **Interactive Content**: Touch controls on Apple TV remote
- **Custom Widgets**: tvOS app for native EQ12 integration
- **Analytics Dashboard**: Web-based monitoring and control panel

### Integration Expansion
- **Spotify Integration**: Background music for content streams
- **Weather Integration**: Include weather in travel deal displays
- **News Feeds**: Real-time sports news and betting insights
- **Social Features**: Share winning parlays to social media
- **Cloud Sync**: Sync content across multiple locations

---

## 🎉 Success Stories

### Real-World Usage Examples

**Scenario 1: Game Day Experience**
- EQ12 generates 3-leg NFL parlay at 12 PM
- Parlay streams to living room Apple TV with blue lighting
- During games, travel deals slideshow plays during commercial breaks
- Win triggers gold lights + victory fanfare + social media share

**Scenario 2: Commerce Automation Hub**
- Sales dashboard auto-refreshes every hour on office Apple TV
- eBay sale notifications trigger green lights + Telegram alerts
- Travel deals stream during lunch break for team motivation
- End-of-day revenue summary with HomeKit scene changes

**Scenario 3: Multi-Location Management**
- Stream betting content to sports bar Apple TVs
- Travel deals to travel agency waiting room displays
- Sales dashboards to e-commerce office displays
- Centralized control via Telegram from anywhere

---

## 🤝 Support & Development

### Getting Help
- **Logs**: Check `C:\EQ12\logs\appletv\` for detailed error information
- **Status**: Use `/appletv_status` Telegram command for system health
- **Testing**: Run individual components to isolate issues
- **Documentation**: Refer to inline code comments for technical details

### Contributing
- **Code Style**: Follow existing patterns and logging standards
- **Testing**: Test all Telegram commands and Apple TV streaming
- **Documentation**: Update this guide for any new features
- **Performance**: Monitor system resources and optimize for efficiency

---

## 📋 Complete Installation Checklist

- [ ] Install Python dependencies (`pip install` command above)
- [ ] Configure Telegram bot token and chat ID
- [ ] Ensure Apple TV on same network with AirPlay enabled
- [ ] Test basic streaming with `/sendtv_parlay` command
- [ ] Configure HomeKit devices and shortcuts (optional)
- [ ] Setup auto-streaming schedule preferences
- [ ] Test all Telegram commands functionality
- [ ] Monitor system logs for any issues
- [ ] Configure firewall exceptions for ports 7000, 8080, 8081
- [ ] Verify WebSocket connections and real-time updates

**🎯 Result**: Your Apple TV becomes a real-time visual dashboard for the entire EQ12 automation ecosystem, controllable via Telegram with smart home integration and automated content streaming!

---

*This system transforms Apple TV from a simple streaming device into a powerful command center display for your entire EQ12 automation stack. Every betting slip, travel deal, and sales update becomes a visual experience that enhances your automation workflow.*
