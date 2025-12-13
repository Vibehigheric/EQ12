# EQ12 Unified Dashboard System

## Overview

The EQ12 Unified Dashboard is a comprehensive, modern web-based control center that integrates all components of the EQ12 automation and betting platform into one centralized interface. It provides real-time monitoring, control, and analytics for all EQ12 systems.

## Features

### 🎯 Betting Hub
- **Active Parlays**: View and manage current betting parlays with EV calculations
- **Live Odds**: Real-time odds from multiple sportsbooks with edge detection
- **Performance Analytics**: Detailed betting performance metrics and ROI tracking
- **Kelly Sizing**: Automatic bet sizing using Kelly criterion
- **Sports Coverage**: NFL, NCAAF, NBA, MLB support

### 📊 System Status
- **Service Health**: Monitor all EQ12 microservices and their health status
- **VPN Management**: Control and monitor VPN connections
- **System Logs**: Real-time log viewing and filtering
- **Resource Monitoring**: CPU, memory, and API usage tracking

### 💰 Finance Dashboard
- **Portfolio Overview**: Real-time portfolio value and performance
- **Stock Tracking**: Monitor watchlisted stocks with buy/sell signals
- **Cryptocurrency**: Track crypto holdings and market data
- **Performance Metrics**: ROI, day changes, and trend analysis

### 🤖 Automation Center
- **Scraper Management**: Control web scrapers for sportsbooks and deals
- **Bot Control**: Manage Telegram and Discord bots
- **Apple TV Integration**: Stream parlay data to Apple TV displays
- **Task Scheduling**: View and control automated tasks

### 🧠 AI Control Panel
- **GPT-5 Integration**: Betting analysis and decision support
- **Cookbook Search**: AI-powered recipe and cooking assistance
- **Sora Video**: AI video generation for content creation
- **Model Performance**: Track AI model usage and accuracy

## Architecture

### Backend
- **FastAPI Framework**: High-performance async web framework
- **SQLite Database**: Lightweight data storage for logs and metrics
- **WebSocket Support**: Real-time data streaming to frontend
- **RESTful API**: Well-documented API endpoints for all functionality
- **Background Tasks**: Automated data collection and processing

### Frontend
- **Modern HTML5**: Responsive web interface
- **Alpine.js**: Reactive JavaScript framework
- **Chart.js**: Interactive charts and visualizations
- **CSS Grid/Flexbox**: Modern responsive layout
- **WebSocket Client**: Real-time updates without page refresh

### Integration Points
- **EQ12 Backend API**: Connects to main betting engine
- **Telegram Bot API**: Bot management and messaging
- **Discord Bot API**: Discord server integration
- **Apple TV Manager**: Streaming service integration
- **VPN Controls**: Network security management

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (primary platform)
- PowerShell 5.1 or PowerShell Core

### Quick Setup
```powershell
# Navigate to EQ12 directory
cd C:\EQ12

# Run the setup script
.\scripts\eq12_dashboard_simple_setup.ps1 -OpenBrowser
```

### Manual Installation
```powershell
# Install dependencies
pip install fastapi uvicorn pydantic requests websockets aiofiles

# Start the dashboard
python eq12_unified_dashboard_backend.py
```

## Usage

### Starting the Dashboard
```powershell
# Start with default settings (port 9000)
.\scripts\eq12_dashboard_simple_setup.ps1

# Start with custom port
.\scripts\eq12_dashboard_simple_setup.ps1 -Port 8080

# Start without installing dependencies
.\scripts\eq12_dashboard_simple_setup.ps1 -SkipInstall
```

### Managing the Service
```powershell
# Check status
.\scripts\eq12_unified_dashboard_manager.ps1 -Action status

# Stop the dashboard
.\scripts\eq12_unified_dashboard_manager.ps1 -Action stop

# Restart the dashboard
.\scripts\eq12_unified_dashboard_manager.ps1 -Action restart
```

### Accessing the Dashboard
- **Main Interface**: http://localhost:9000/
- **API Documentation**: http://localhost:9000/docs (auto-generated)
- **Health Check**: http://localhost:9000/api/health

## API Endpoints

### Core System
- `GET /api/health` - Service health check
- `GET /api/system/status` - Overall system status

### Betting Module
- `GET /api/betting/parlays` - Active parlays
- `GET /api/betting/odds` - Live odds data
- `GET /api/betting/performance` - Performance metrics

### Finance Module
- `GET /api/finance/portfolio` - Portfolio and holdings data

### Automation Module
- `GET /api/automation/status` - Scrapers and bots status
- `POST /api/scrapers/run/{scraper_name}` - Trigger scraper
- `POST /api/telegram/send` - Send Telegram message
- `POST /api/apple-tv/stream` - Stream to Apple TV

### AI Module
- `GET /api/ai/status` - AI models and services status

### Utilities
- `GET /api/vpn/status` - VPN connection status
- `POST /api/vpn/toggle` - Toggle VPN connection
- `GET /api/logs/recent` - Recent system logs

### WebSocket
- `WS /ws` - Real-time updates for dashboard components

## Configuration

### Environment Variables
```powershell
# Set custom port
$env:EQ12_DASHBOARD_PORT = "9000"

# Set log level
$env:EQ12_LOG_LEVEL = "INFO"  # DEBUG, INFO, WARN, ERROR

# API Keys (if connecting to live services)
$env:ODDS_API_KEY = "your_odds_api_key"
$env:TELEGRAM_BOT_TOKEN = "your_telegram_token"
$env:OPENAI_API_KEY = "your_openai_key"
```

### Database Configuration
The dashboard automatically creates a SQLite database at `C:\EQ12\dashboard.db` for:
- System metrics and performance data
- Dashboard access logs
- Configuration settings

### Log Files
- **Setup Log**: `C:\EQ12\logs\dashboard_setup.log`
- **Manager Log**: `C:\EQ12\logs\dashboard_manager.log`
- **Runtime Log**: `C:\EQ12\logs\unified_dashboard.log`
- **Output Log**: `C:\EQ12\logs\dashboard_output.log`
- **Error Log**: `C:\EQ12\logs\dashboard_error.log`

## Development

### Adding New Features
1. **Backend**: Add new endpoints in `eq12_unified_dashboard_backend.py`
2. **Frontend**: Update the dashboard HTML with new sections
3. **API**: Follow FastAPI patterns for new routes
4. **Database**: Add new tables/columns as needed

### Testing
```powershell
# Test API endpoints
Invoke-RestMethod -Uri "http://localhost:9000/api/health"

# Test WebSocket connection
# Use browser developer tools or WebSocket testing tools

# Check logs for errors
Get-Content "C:\EQ12\logs\unified_dashboard.log" -Tail 50
```

### Debugging
```powershell
# Start in debug mode (visible console)
python eq12_unified_dashboard_backend.py --log-level debug

# View real-time logs
Get-Content "C:\EQ12\logs\unified_dashboard.log" -Wait

# Check process status
Get-Process | Where-Object { $_.ProcessName -eq "python" }
```

## Security Considerations

### Authentication
- Currently operates on localhost only
- No authentication required for local access
- For remote access, implement proper authentication

### API Security
- CORS enabled for local development
- Rate limiting should be added for production
- API keys stored as environment variables

### Network Security
- VPN integration for secure connections
- Local firewall rules recommended
- HTTPS can be configured for production use

## Troubleshooting

### Common Issues

#### Dashboard Won't Start
```powershell
# Check Python installation
python --version

# Verify dependencies
pip list | findstr "fastapi uvicorn"

# Check port availability
netstat -an | findstr "9000"
```

#### API Endpoints Not Responding
```powershell
# Check process is running
Get-Process | Where-Object { $_.CommandLine -like "*dashboard_backend*" }

# Test health endpoint
Invoke-RestMethod -Uri "http://localhost:9000/api/health"

# Check logs
Get-Content "C:\EQ12\logs\unified_dashboard.log" -Tail 20
```

#### WebSocket Connection Issues
- Ensure firewall allows connections on dashboard port
- Check browser console for WebSocket errors
- Verify no proxy interference

### Performance Optimization
- Increase update intervals for less frequent data refresh
- Disable unused dashboard sections
- Use SQLite WAL mode for better concurrent access
- Consider Redis for high-frequency data caching

## Integration with Existing EQ12 Systems

### Betting Engine Integration
The dashboard connects to the main EQ12 betting backend to pull:
- Active parlays and bet tracking
- Live odds from multiple sportsbooks
- Edge detection and EV calculations
- Kelly sizing recommendations

### Bot Integration
Manages and displays status for:
- **Telegram Bot**: Message statistics and command handling
- **Discord Bot**: Server activity and user interactions
- **Apple TV Bot**: Streaming status and content management

### Scraper Integration
Monitors and controls:
- **Sportsbook Scrapers**: DraftKings, FanDuel, etc.
- **Deal Scrapers**: Travel, shopping, and other opportunities
- **Job Alert Scrapers**: Employment opportunity monitoring

## Future Enhancements

### Planned Features
- **Mobile App**: Native iOS/Android companion app
- **Advanced Analytics**: Machine learning insights
- **Multi-User Support**: Role-based access control
- **Cloud Deployment**: AWS/Azure hosting options
- **Real-Time Notifications**: Push notifications for key events

### API Improvements
- **GraphQL Support**: More efficient data fetching
- **Webhook System**: Event-driven integrations
- **Batch Operations**: Bulk data processing
- **Caching Layer**: Redis integration for performance

### UI/UX Enhancements
- **Dark Mode**: Alternative color scheme
- **Customizable Layout**: Drag-and-drop dashboard components
- **Advanced Filtering**: More granular data views
- **Export Features**: PDF reports and data exports

## Support and Contributing

### Documentation
- **API Docs**: Auto-generated at `/docs` endpoint
- **Code Comments**: Inline documentation in source
- **Architecture Diagrams**: Visual system overview

### Issue Reporting
- Check logs first: `C:\EQ12\logs\`
- Include error messages and steps to reproduce
- Provide system information (Python version, OS, etc.)

### Development Guidelines
- Follow FastAPI best practices
- Use type hints for Python code
- Add logging for all operations
- Test endpoints before committing
- Update documentation for new features

---

**EQ12 Unified Dashboard v2.0.0**
*Comprehensive automation and betting platform interface*

For additional support, check the logs directory or review the API documentation at `/docs` when the dashboard is running.
