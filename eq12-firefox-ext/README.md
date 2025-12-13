# 🎯 EQ12 Browser Extensions

> **Firefox & Chrome extensions for EQ12 Betting Dashboard - Real-time parlay generation, EV analysis, and betting analytics**

## 🚀 Features

- **🎟️ Parlay Generation**: Generate 5-leg and 10-leg parlays with one click
- **🟢 EV Analysis**: Real-time expected value highlighting on major sportsbooks
- **📊 Audit Reports**: Track betting performance with win rates and ROI analytics
- **⚙️ API Integration**: Seamless connection to EQ12 FastAPI backend
- **🔐 Secure Settings**: Encrypted storage of API keys and configuration

## 📦 Installation

### Firefox
1. Download the latest `eq12-firefox-ext-vX.X.X.zip` from [Releases](../../releases)
2. Open Firefox and navigate to `about:debugging#/runtime/this-firefox`
3. Click "Load Temporary Add-on"
4. Select the downloaded zip file

### Chrome/Edge
1. Download the latest `eq12-chromium-ext-vX.X.X.zip` from [Releases](../../releases)
2. Extract the zip file to a folder
3. Open Chrome and navigate to `chrome://extensions/`
4. Enable "Developer mode"
5. Click "Load unpacked" and select the extracted folder

## ⚙️ Configuration

After installation, configure the extension:

1. Click the EQ12 extension icon
2. Click "Settings" (⚙️ icon)
3. Set your configuration:
   - **API Base**: `http://localhost:8000` (or your ngrok URL)
   - **API Key**: `eq12-test-key-2025` (or your custom key)
4. Click "Test Connection" to verify
5. Click "Save Settings"

## 🎮 Usage

### Generate Parlays
- Click the EQ12 extension icon
- Choose "5-Leg Parlay" or "10-Leg Parlay"
- View formatted results with odds and EV analysis

### View Analytics
- Click "Audit Report" for betting performance data
- Monitor win rates, ROI, and recent betting history
- Check system health and API connectivity

### EV Highlighting
- Visit supported sportsbooks (DraftKings, FanDuel, BetMGM, etc.)
- Extension automatically highlights positive EV bets
- Hover over highlights to see EV percentages

## 🛠 Development

### Prerequisites
```bash
# Node.js 18+ required
npm install
```

### Build Extensions
```bash
# Build Firefox version
npm run build:firefox

# Build Chromium version
npm run build:chromium

# Package for distribution
npm run package:firefox
npm run package:chromium
```

### Local Development
```bash
# Quick dev build (Windows)
npm run dev

# Start backend API server
cd ../scripts
python eq12_extension_backend.py

# Load extension in Firefox developer mode
# Navigate to about:debugging and load manifest.json
```

## 🌐 Supported Sportsbooks

The EV highlighting content script works on:
- **DraftKings** (`draftkings.com`)
- **FanDuel** (`fanduel.com`)
- **BetMGM** (`betmgm.com`)
- **Caesars** (`caesars.com`)
- **Barstool** (`barstoolsportsbook.com`)

## 📡 API Endpoints

The extension communicates with these EQ12 backend endpoints:

- `GET /api/ping` - Connection test
- `GET /api/health` - System health check
- `GET /api/parlay?size=N` - Generate N-leg parlay
- `GET /api/audit?last=N` - Recent betting audit
- `GET /api/check-ev?selection=X&odds=Y` - EV analysis

## 🔐 Security

- API keys stored in browser's encrypted storage
- CORS-protected communication with backend
- No sensitive data transmitted to external services
- Local-only operation (localhost/ngrok endpoints)

## 🚀 Automated Releases

This project uses GitHub Actions for automated building and releasing:

- **Development builds** on every push to `main`
- **Tagged releases** when you push a version tag (`v1.2.3`)
- **Cross-platform builds** for both Firefox and Chromium
- **Automatic changelog** generation from commit messages

### Creating a Release
```bash
# Tag a new version
git tag v1.2.3
git push origin v1.2.3

# GitHub Actions automatically:
# 1. Updates manifest.json versions
# 2. Builds both extension variants
# 3. Creates GitHub Release with zips
# 4. Generates changelog from commits
```

## 📋 Project Structure

```
eq12-firefox-ext/
├── src/
│   ├── background.js      # Service worker
│   ├── popup.html         # Extension popup UI
│   ├── popup.js          # Popup functionality
│   ├── options.html      # Settings page
│   ├── options.js        # Settings functionality
│   ├── content.js        # Sportsbook EV highlighting
│   └── styles.css        # UI styling
├── icons/                # Extension icons (16,32,48,128px)
├── manifest.firefox.json # Firefox Manifest V3
├── manifest.chromium.json# Chrome/Edge Manifest V3
└── package.json          # Build configuration
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](../../issues)
- **Documentation**: [EQ12 Docs](../README.md)
- **Backend API**: See `scripts/eq12_extension_backend.py`

---

**Built with ❤️ for the EQ12 betting automation ecosystem**
