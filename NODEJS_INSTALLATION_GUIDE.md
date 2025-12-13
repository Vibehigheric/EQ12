# Node.js Installation Guide for EQ12 Platform

## 🟢 Installing Node.js on Windows

Since Node.js is not currently installed on your system, follow these steps to enable the complete multi-language EQ12 platform:

---

## 📥 Installation Options

### Option 1: Official Node.js Installer (Recommended)

1. **Download Node.js**
   - Visit: https://nodejs.org/
   - Download the **LTS version** (Long Term Support)
   - Choose "Windows Installer (.msi)" for your system (x64)

2. **Run the Installer**
   - Double-click the downloaded `.msi` file
   - Follow the installation wizard
   - ✅ **IMPORTANT**: Check "Add to PATH" option
   - ✅ **IMPORTANT**: Check "Install additional tools" (includes npm)

3. **Verify Installation**
   ```powershell
   # Open new PowerShell window and test:
   node --version     # Should show v18.x.x or v20.x.x
   npm --version      # Should show 9.x.x or 10.x.x
   ```

### Option 2: Using Chocolatey (If Available)

```powershell
# If you have Chocolatey package manager:
choco install nodejs

# Verify installation
node --version
npm --version
```

### Option 3: Using winget (Windows Package Manager)

```powershell
# If you have winget:
winget install OpenJS.NodeJS

# Verify installation
node --version
npm --version
```

---

## ⚡ Quick Setup After Node.js Installation

### 1. Install EQ12 Node.js Dependencies

```powershell
# Navigate to EQ12 directory
cd C:\EQ12

# Install all required packages
npm install

# This will install:
# - axios (API requests)
# - dotenv (environment variables)
# - winston (logging)
# - moment (date handling)
# - lodash (utilities)
```

### 2. Test the Installation

```powershell
# Test basic Node.js functionality
node -e "console.log('Node.js working!', process.version)"

# Test EQ12 Node.js platform (without API key)
node eq12_node_odds_client.js

# Run complete demo (requires ODDS_API_KEY)
node eq12_node_betting_suite.js
```

### 3. Set Environment Variables

```powershell
# Set API key for Odds API
setx ODDS_API_KEY "your-odds-api-key-here"

# Optional: Set other API keys
setx OPENAI_API_KEY "your-openai-key"
setx TELEGRAM_BOT_TOKEN "your-telegram-token"

# Restart PowerShell after setting environment variables
```

---

## 🎮 VS Code Tasks (After Installation)

Once Node.js is installed, these tasks will be available:

### Setup Tasks
- **EQ12: Install Node.js Dependencies** - `npm install`

### Demo Tasks
- **EQ12: Node.js Odds Client Demo** - Basic odds client test
- **EQ12: Node.js Complete Betting Suite** - Full platform demo
- **EQ12: Node.js NFL Analysis** - NFL-specific analysis
- **EQ12: Node.js Arbitrage Detection** - Real-time arbitrage scanning

### Master Task
- **EQ12: Complete Multi-Language Betting Platform** - Python + Node.js integration

---

## 🔍 Troubleshooting

### "node is not recognized" Error
- **Solution**: Restart PowerShell/VS Code after Node.js installation
- **Alternative**: Add Node.js to PATH manually:
  - Default location: `C:\Program Files\nodejs\`
  - Add to system PATH environment variable

### npm Permission Issues
```powershell
# Fix npm permissions (run as Administrator if needed)
npm config set prefix C:\Users\%USERNAME%\AppData\Roaming\npm
```

### Package Installation Errors
```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -r node_modules
npm install
```

---

## 🚀 What You Get After Installation

### Complete Node.js Betting Platform
- ✅ Real-time odds API client (500+ lines)
- ✅ Complete betting suite (800+ lines)
- ✅ NFL/NBA analysis engines
- ✅ Arbitrage detection algorithms
- ✅ Live monitoring system
- ✅ Portfolio performance tracking
- ✅ Cross-platform Python integration

### Development Environment
- ✅ Professional npm scripts
- ✅ VS Code task integration
- ✅ Comprehensive logging system
- ✅ Error handling and recovery
- ✅ Usage tracking and monitoring

### Multi-Language Platform
- 🐍 **Python**: AI analysis, Google Sheets, ML models
- 🟢 **Node.js**: Real-time performance, efficient APIs
- 🔗 **Integration**: Shared data, unified workflows

---

## 📊 Platform Status Check

Run this after Node.js installation to verify everything works:

```powershell
cd C:\EQ12

# Check Node.js version
node --version

# Check npm version
npm --version

# Install dependencies
npm install

# Test EQ12 platform
node -e "
const EQ12Client = require('./eq12_node_odds_client.js');
console.log('🟢 EQ12 Node.js Platform: READY');
console.log('📦 Required modules: Available');
console.log('🔑 API Key: Set ODDS_API_KEY to activate');
console.log('🎯 Run: npm run odds:demo for full test');
"
```

---

## 💡 Immediate Next Steps

### 1. Install Node.js
- Download from https://nodejs.org/
- Choose LTS version for stability
- Ensure "Add to PATH" is checked

### 2. Install EQ12 Dependencies
```powershell
cd C:\EQ12
npm install
```

### 3. Set API Keys
```powershell
setx ODDS_API_KEY "your-key-here"
# Restart PowerShell
```

### 4. Run First Demo
```powershell
npm run odds:demo
# Or use VS Code task: "EQ12: Node.js Complete Betting Suite"
```

---

## 🏆 Benefits of Node.js Integration

### Performance Advantages
- **Async Operations**: Perfect for real-time odds monitoring
- **Fast API Calls**: Efficient HTTP request handling
- **Event-Driven**: Ideal for live betting applications
- **Memory Efficient**: Lower resource usage than Python for I/O

### Development Benefits
- **Rapid Prototyping**: Quick iteration and testing
- **Rich Ecosystem**: Vast npm package library
- **Cross-Platform**: Same code runs on Windows, Mac, Linux
- **Modern JavaScript**: Latest language features and tooling

### Integration Benefits
- **Complements Python**: Best of both worlds
- **Shared Data**: JSON-based data exchange
- **Unified Logging**: Consistent log formats
- **VS Code Integration**: Seamless development workflow

---

**Once Node.js is installed, your EQ12 platform will be the most comprehensive multi-language sports betting automation system available!** 🚀

---

*Node.js Installation: https://nodejs.org/ (Choose LTS version)*
