# EQ12 Node.js Sports Betting Integration

## 🟢 Complete Node.js Implementation for The Odds API

The EQ12 platform now includes a **complete Node.js implementation** that works alongside the existing Python platform, providing you with the most comprehensive multi-language sports betting automation system available.

---

## 📁 Node.js Files Added

### Core Components

1. **`eq12_node_odds_client.js`** (500+ lines)
   - Enhanced Node.js client for The Odds API
   - Real-time arbitrage detection
   - Professional logging and data persistence
   - Advanced usage tracking

2. **`eq12_node_betting_suite.js`** (800+ lines)
   - Complete betting automation suite
   - 5 comprehensive betting workflows
   - Cross-platform integration with Python
   - Portfolio performance tracking

3. **`package.json`** (Enhanced)
   - All necessary Node.js dependencies
   - Custom npm scripts for betting operations
   - Professional development setup

---

## 🚀 Quick Start Guide

### 1. Install Dependencies

```bash
# Install all Node.js packages
npm install

# Or use the VS Code task
# Ctrl+Shift+P → "Tasks: Run Task" → "EQ12: Install Node.js Dependencies"
```

### 2. Set Environment Variables

```bash
# Required for Node.js platform
set ODDS_API_KEY=your-odds-api-key-here

# Optional for enhanced features
set OPENAI_API_KEY=your-openai-key
set TELEGRAM_BOT_TOKEN=your-telegram-token
```

### 3. Test the Platform

```bash
# Run complete Node.js demo
node eq12_node_betting_suite.js

# Or use VS Code tasks:
# "EQ12: Node.js Complete Betting Suite"
# "EQ12: Node.js Odds Client Demo"
# "EQ12: Node.js NFL Analysis"
# "EQ12: Node.js Arbitrage Detection"
```

---

## 🎯 Node.js Platform Capabilities

### 1. Enhanced Odds API Client
- Real-time odds from 50+ sportsbooks
- Automatic arbitrage detection with profit calculations
- Professional error handling and retry logic
- Usage tracking and quota management
- Comprehensive logging to `C:/EQ12/logs/`

### 2. Advanced Betting Analytics
- **NFL Sunday Analysis** - Complete game analysis with value picks
- **NBA Props Builder** - Player props analysis and recommendations
- **Arbitrage Scanner** - Real-time opportunity detection
- **Portfolio Tracker** - Performance analytics and ROI tracking
- **Live Monitoring** - Continuous odds monitoring with alerts

### 3. Cross-Platform Integration
- Seamless integration with existing Python platform
- Shared data directories (`C:/EQ12/data/`, `C:/EQ12/logs/`)
- Compatible file formats for data exchange
- Unified configuration management

---

## 💻 Available npm Scripts

Run these commands from the EQ12 directory:

```bash
# Core demos
npm run odds:demo          # Complete platform demo
npm run odds:nfl          # NFL analysis only
npm run odds:arbitrage    # Arbitrage detection
npm run odds:sports       # Available sports list
npm run odds:props        # Player props analysis

# Development
npm install               # Install dependencies
npm test                  # Run tests (when available)
```

---

## 🎮 VS Code Tasks Integration

**New Node.js Tasks Available:**

### Core Tasks
- **EQ12: Install Node.js Dependencies** - Set up the Node.js environment
- **EQ12: Node.js Odds Client Demo** - Test the core odds client
- **EQ12: Node.js Complete Betting Suite** - Full platform demonstration

### Specialized Tasks
- **EQ12: Node.js NFL Analysis** - NFL-specific analysis
- **EQ12: Node.js Arbitrage Detection** - Real-time arbitrage scanning

### Master Task
- **EQ12: Complete Multi-Language Betting Platform** - Full Python + Node.js integration

---

## 📊 Node.js Betting Suite Features

### 1. NFL Sunday Analysis
```javascript
const suite = new EQ12NodeBettingSuite();
const analysis = await suite.nflSundayAnalysis();

// Returns:
// - Value picks against the spread
// - Totals betting opportunities
// - Moneyline value bets
// - Arbitrage opportunities
// - Comprehensive game analysis
```

### 2. NBA Props Builder
```javascript
const propsAnalysis = await suite.nbaPropsBuilder();

// Analyzes:
// - Player performance props
// - Value detection algorithms
// - Correlated betting opportunities
// - Cross-market analysis
```

### 3. Live Monitoring System
```javascript
// Monitor multiple sports for arbitrage
await suite.startLiveMonitoring(['americanfootball_nfl', 'basketball_nba']);

// Features:
// - Real-time odds monitoring
// - Arbitrage alerts
// - Usage tracking
// - Automated data persistence
```

### 4. Portfolio Performance Tracker
```javascript
const performance = await suite.portfolioPerformanceTracker();

// Provides:
// - ROI and win rate analysis
// - Performance by bet type
// - Streak analysis
// - Actionable recommendations
```

### 5. Cross-Platform Integration
```javascript
const integration = await suite.crossPlatformDemo();

// Demonstrates:
// - Python module detection
// - Data sharing capabilities
// - Unified logging system
// - Configuration management
```

---

## 🔧 Advanced Configuration

### Custom Bookmakers
Edit `eq12_node_odds_client.js`:
```javascript
// Add your preferred bookmakers
const regions = 'us,uk,eu,au';  // Expand regions
const markets = 'h2h,spreads,totals,player_props';  // Add markets
```

### Arbitrage Sensitivity
Adjust profit thresholds:
```javascript
// In calculateArbitrage method
if (totalImpliedProb < 1.0 && profitMargin > 0.5) {  // Minimum 0.5% profit
    // Process arbitrage opportunity
}
```

### Monitoring Intervals
Customize live monitoring:
```javascript
// In startLiveMonitoring method
setInterval(async () => {
    // Your monitoring logic
}, 60000);  // Check every 60 seconds
```

---

## 📈 Data Integration

### Shared Data Structure
All Node.js components save data to `C:/EQ12/data/` in JSON format:

```
C:/EQ12/data/
├── sports.json                    # Available sports
├── odds_americanfootball_nfl_*.json  # NFL odds snapshots
├── arbitrage_opportunities.json    # Current arbitrages
├── nfl_analysis.json              # NFL analysis results
├── portfolio_performance.json      # Performance data
└── nodejs_platform_status.json    # Platform status
```

### Log Files
Comprehensive logging in `C:/EQ12/logs/`:

```
C:/EQ12/logs/
├── eq12_node_odds.log             # Odds client logs
├── eq12_node_betting_suite.log    # Suite operation logs
└── monitoring_*.json              # Live monitoring snapshots
```

---

## 🌐 Multi-Language Platform Benefits

### Python + Node.js Integration
- **Python**: Advanced AI analysis, Google Sheets integration, ML models
- **Node.js**: Real-time performance, efficient API handling, async operations
- **Combined**: Most comprehensive betting platform available

### Performance Advantages
- Node.js excels at real-time odds monitoring and API calls
- Python excels at data analysis and AI integration
- Choose the best tool for each specific task

### Development Flexibility
- Use Node.js for rapid prototyping and real-time features
- Use Python for complex analysis and AI integration
- Shared data formats enable seamless workflow integration

---

## 🚨 Important Notes

### API Usage
- Node.js platform shares the same Odds API quota with Python
- Monitor usage with `getUsageStats()` method
- Consider rate limiting for production use

### Development Best Practices
```javascript
// Always check for API key
if (!this.apiKey || this.apiKey === 'YOUR_API_KEY') {
    throw new Error('Valid API key required');
}

// Implement proper error handling
try {
    const odds = await this.makeRequest('/sports/nfl/odds');
} catch (error) {
    this.log(`API Error: ${error.message}`, 'ERROR');
}
```

### Production Deployment
- Use environment variables for all API keys
- Implement proper logging and monitoring
- Set up automated backups for data directory
- Consider Docker containerization for deployment

---

## 🎉 Next Steps

### Immediate Actions
1. **Install Dependencies**: Run `npm install` or VS Code task
2. **Set API Keys**: Configure ODDS_API_KEY environment variable
3. **Run Demo**: Execute "EQ12: Complete Multi-Language Betting Platform" task
4. **Explore Integration**: Test data sharing between Python and Node.js

### Advanced Development
- **Custom Strategies**: Implement your betting algorithms
- **Real-Time Alerts**: Add Telegram/Discord notifications
- **Database Integration**: Connect to PostgreSQL/MongoDB
- **Web Dashboard**: Build Express.js web interface
- **Mobile API**: Create REST API for mobile apps

---

## 🏆 Platform Status

✅ **Node.js Core**: Complete odds client with arbitrage detection
✅ **Betting Suite**: 5 comprehensive betting workflow examples
✅ **VS Code Integration**: Professional task automation
✅ **Cross-Platform**: Seamless Python integration
✅ **Documentation**: Complete setup and usage guides
✅ **Production Ready**: Error handling, logging, monitoring

**Your EQ12 platform now supports both Python and Node.js for the ultimate sports betting automation system!** 🚀

---

*Always gamble responsibly and comply with local laws and regulations.*
