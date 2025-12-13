# Sports Betting Extension + Python Backend Integration

Complete **cross-browser WebExtension** with **real-time Python backend** for sports betting optimization.

## 🏗️ Architecture

```
Browser Extension (Chrome/Firefox)
    ↕️ WebSocket (ws://localhost:8765)
Python Backend Bridge
    ↕️ File System / API calls
Sports Betting Optimizer (existing repo)
```

## 📦 What's Included

### Extension Files
- `manifest.json` - Cross-browser extension manifest (MV3)
- `background.js` - Service worker with WebSocket client
- `content-draftkings.js` - DraftKings bet slip injection
- `content-fanduel.js` - FanDuel integration (basic)
- `popup/` - Extension popup interface
- `polyfill/browser-polyfill.min.js` - Chrome/Firefox compatibility
- `icons/` - Extension icons (add your own PNG files)

### Python Bridge
- `simple_bridge.py` - Lightweight WebSocket server
- `websocket_bridge.py` - Full-featured server with file watching

## 🚀 Quick Start

### 1. Install Extension

**Chrome:**
1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" → select `sports-betting-extension` folder

**Firefox:**
1. Open `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select `manifest.json` in the extension folder

### 2. Start Python Backend

```bash
cd sports-betting-extension

# Install WebSocket dependency
pip install websockets

# Start simple bridge (mock data)
python simple_bridge.py

# OR start full bridge (requires optimizer repo)
python websocket_bridge.py
```

### 3. Use Extension

1. **Navigate to DraftKings** sportsbook
2. **Click extension icon** in browser toolbar
3. **Request new parlay** with your preferences
4. **Apply to bet slip** automatically

## 🎛️ Extension Features

### Popup Interface
- **Current parlay display** with legs, EV, boost info
- **Quick parlay requests** by sport/promo type
- **Settings form** for stake, max legs, preferences
- **Real-time connection status** to Python backend

### Content Script (DraftKings)
- **Automatic bet slip filling** from optimized parlays
- **Odds monitoring** and backend sync
- **Keyboard shortcuts** (Ctrl+Shift+B to toggle overlay)
- **Smart selectors** for robust bet placement

### Background Service
- **WebSocket client** maintains connection to Python
- **Real-time notifications** for new parlays
- **Cross-tab communication** and state management
- **Auto-reconnection** on connection drops

## 🔧 Backend Integration

### Simple Bridge (`simple_bridge.py`)
- **Mock parlay generation** for testing
- **Basic WebSocket server** on port 8765
- **No dependencies** on optimizer repo
- **Perfect for development/testing**

### Full Bridge (`websocket_bridge.py`)
- **File system watching** for real parlay files
- **Integration** with existing optimizer repo
- **Async parlay generation** via master_optimizer
- **Production-ready** with logging and error handling

## 🌐 Cross-Browser Compatibility

### Chrome (chrome.* APIs)
- Uses **callback-based** APIs
- **Manifest V3** service worker
- **chrome.storage**, **chrome.tabs**, etc.

### Firefox (browser.* APIs)
- Uses **promise-based** APIs natively
- **WebExtension** standard compliance
- **browser.storage**, **browser.tabs**, etc.

### Polyfill Bridge
- **Automatic conversion** of Chrome callbacks to promises
- **Unified browser.* API** across both platforms
- **Single codebase** works everywhere

## 📱 Usage Workflow

1. **Background:** Python optimizer generates new parlays
2. **Bridge:** WebSocket server detects file changes
3. **Push:** Real-time parlay data sent to extension
4. **Notify:** Browser notification shows new parlay available
5. **Review:** User opens popup to see parlay details
6. **Apply:** One-click bet slip filling on DraftKings
7. **Track:** Extension monitors bet slip changes

## 🎯 DraftKings Integration

### Bet Slip Automation
- **Multi-selector strategy** for robust leg finding
- **Staggered clicking** to avoid race conditions
- **Automatic stake setting** with event simulation
- **Error handling** and fallback strategies

### Supported Markets
- **Spread bets** (team -3.5, etc.)
- **Totals** (Over/Under points)
- **Moneylines** (team to win)
- **Player props** (touchdowns, yards, etc.)

## 🔐 Security Notes

- **Local communication only** (WebSocket localhost)
- **No external data transmission**
- **User-controlled** bet placement (no auto-betting)
- **Transparent** parlay review before application

## 🛠️ Development

### Testing Extension
```bash
# Test WebSocket connection
node -e "const ws = new WebSocket('ws://localhost:8765'); ws.onopen = () => console.log('✅ Connected'); ws.onerror = (e) => console.log('❌', e);"

# Mock parlay request
curl -X POST localhost:8765 -d '{"type":"request_parlay","sport":"nfl"}'
```

### Debugging
- **Chrome DevTools:** Extensions tab → Background page → Console
- **Firefox DevTools:** about:debugging → Extension → Inspect
- **Python logs:** Check `websocket_bridge.log` for server activity

### Custom Sports Books
1. **Copy** `content-draftkings.js` → `content-newsportsbook.js`
2. **Update selectors** for new sportsbook's HTML structure
3. **Add manifest entry** for new domain
4. **Test** bet slip integration

## 📈 Enhancements

### Planned Features
- **Multi-sportsbook support** (FanDuel, BetMGM complete)
- **Parlay tracking** and results analysis
- **Kelly criterion staking** integration
- **Arbitrage opportunity** detection
- **Chrome extension store** publication

### Integration Opportunities
- **Telegram bot** notifications via existing system
- **CSV export** of placed bets for tracking
- **AI analysis** integration for bet evaluation
- **Live odds monitoring** across multiple books

## 🎉 Ready to Use

This extension bridges your **existing Python optimizer** with **real-time browser automation**. The WebSocket architecture ensures **immediate updates** when new +EV opportunities are found.

**No more manual bet slip entry** - let the AI find the plays, and the extension place them instantly.

---

## 📞 Support

For issues:
1. Check **browser console** for extension errors
2. Verify **WebSocket server** is running (`python simple_bridge.py`)
3. Test on **DraftKings sportsbook** pages only
4. Ensure **developer mode** enabled in browser
