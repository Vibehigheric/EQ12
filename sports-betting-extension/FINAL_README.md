# 🎯 Sports Betting Extension - Complete Integration

**Real-time WebSocket bridge** connecting your Python sports betting optimizer directly to a **cross-browser extension** with **automatic DraftKings bet slip filling**.

## 🚀 Quick Start

```bash
# 1. Install extension dependencies
cd sports-betting-extension
pip install websockets watchdog

# 2. Test integration
python test_integration.py

# 3. Start complete system
python launch.py
```

**Then load extension in browser:**
- **Chrome:** `chrome://extensions/` → Developer Mode → Load Unpacked
- **Firefox:** `about:debugging` → Load Temporary Add-on → Select manifest.json

## 📦 What You Get

### **Extension Features**
- 🎯 **Real-time parlay notifications** via WebSocket
- 📱 **Professional popup interface** with parlay management
- 🤖 **One-click DraftKings bet slip automation**
- ⚙️ **Configurable sports/promos/stakes**
- 🔄 **Live connection status** and error handling
- 🌐 **Cross-browser compatibility** (Chrome + Firefox)

### **Python Integration**
- 🔌 **WebSocket bridge server** with auto-reconnection
- 🎰 **Direct optimizer integration** (auto-patches existing code)
- 📊 **Real-time parlay pushing** (no polling required)
- 🛠️ **Fallback modes** (mock data if optimizer unavailable)

## 📋 File Structure

```
sports-betting-extension/
├── 🎯 Extension Core
│   ├── manifest.json              # Cross-browser config (MV3)
│   ├── background.js              # WebSocket client + notifications
│   ├── content-draftkings.js      # DraftKings automation
│   └── popup/                     # Extension interface
│       ├── popup.html
│       └── popup.js
├── 🔧 Browser Compatibility
│   └── polyfill/
│       └── browser-polyfill.min.js # Chrome/Firefox API bridge
├── 🐍 Python Bridge
│   ├── simple_bridge.py           # Basic WebSocket server (mock data)
│   ├── enhanced_bridge.py         # Full optimizer integration
│   ├── optimizer_hook.py          # Direct optimizer patching
│   └── launch.py                  # Complete system launcher
└── 🧪 Testing & Setup
    ├── test_integration.py        # Full test suite
    ├── INSTALL.md                 # Step-by-step setup
    └── README.md                  # This file
```

## ⚡ Usage Workflow

1. **Python optimizer** finds profitable parlay
2. **WebSocket bridge** detects/receives new parlay
3. **Extension background** pushes browser notification
4. **User opens popup** to review parlay details
5. **One-click application** auto-fills DraftKings bet slip
6. **User reviews and places** bet manually

## 🔗 Integration Options

### **Option 1: Auto-Integration (Recommended)**
```bash
python launch.py
```
- Automatically finds and patches your existing optimizer
- Starts WebSocket bridge with full integration
- No manual code changes required

### **Option 2: Manual Integration**
Add to your `master_optimizer.py`:
```python
# At the top
try:
    from optimizer_hook import push_parlay
    EXTENSION_AVAILABLE = True
except ImportError:
    EXTENSION_AVAILABLE = False

# After generating parlay
if EXTENSION_AVAILABLE and best_parlay:
    asyncio.create_task(push_parlay(parlay_data))
```

### **Option 3: Mock Data Mode**
```bash
python simple_bridge.py
```
- Works without existing optimizer
- Generates mock parlays for testing
- Perfect for extension development

## 🎛️ DraftKings Automation

The extension uses **smart selectors** and **staggered timing** for reliable bet slip filling:

```javascript
// Multi-selector strategy for robust outcome finding
const selectors = [
    `[data-outcome-label*="${leg.label}"]`,
    `[data-sb-id*="${leg.market}"]`,
    `button[aria-label*="${leg.label}"]`,
    `button:contains("${leg.odds}")`
];

// Staggered clicking to avoid race conditions
parlay.legs.forEach((leg, index) => {
    setTimeout(() => {
        addBetSlipLeg(leg);
    }, index * 500);
});
```

## 🌐 Cross-Browser Support

### **Chrome (chrome.* APIs)**
- Callback-based APIs converted to promises
- Manifest V3 service worker
- `chrome.storage`, `chrome.notifications`, etc.

### **Firefox (browser.* APIs)**
- Native promise-based APIs
- WebExtension standard compliance
- `browser.storage`, `browser.notifications`, etc.

### **Polyfill Bridge**
```javascript
// Automatically handles Chrome → Firefox API conversion
if (!globalThis.browser) {
    globalThis.browser = {
        storage: {
            local: {
                get: promisify(chrome.storage.local.get),
                set: promisify(chrome.storage.local.set)
            }
        },
        notifications: {
            create: promisify(chrome.notifications.create)
        }
    };
}
```

## 🧪 Testing

**Run complete test suite:**
```bash
python test_integration.py
```

Tests:
- ✅ Extension files present and valid
- ✅ WebSocket connection functional
- ✅ Parlay generation working
- ✅ Optimizer integration status

**Manual testing:**
1. Load extension in browser
2. Navigate to `sportsbook.draftkings.com`
3. Click extension icon
4. Request new parlay
5. Verify auto-fill works

## 🔐 Security & Safety

- **Local-only communication** (WebSocket localhost:8765)
- **No external data transmission**
- **User-controlled betting** (review required before placing)
- **Transparent parlay details** (EV, legs, odds displayed)
- **Manual bet confirmation** (extension fills slip, user places bet)

## 🎯 Key Features

### **Real-Time Integration**
- **WebSocket connection** maintains live link to optimizer
- **Instant notifications** when profitable parlays found
- **Auto-reconnection** if connection drops
- **Background processing** doesn't interfere with browsing

### **Smart Bet Slip Filling**
- **Multiple selector strategies** for robust market finding
- **Automatic clearing** of existing selections
- **Proper timing delays** to avoid sportsbook rate limits
- **Error handling** with fallback approaches
- **Stake setting** with proper event simulation

### **Professional UI**
- **Modern gradient design** with dark theme
- **Real-time connection indicators**
- **Detailed parlay information** (EV, boost %, payout)
- **Configurable preferences** (sport, promo type, stakes)
- **Keyboard shortcuts** for power users

## 🚀 Ready to Use

This extension provides a **complete bridge** between your Python betting AI and real-time browser automation. The WebSocket architecture ensures **immediate delivery** of profitable opportunities with **one-click bet slip filling**.

**No more manual entry** - your AI finds the plays, the extension applies them instantly across **Chrome and Firefox** with full **promise/callback compatibility**.

Load the extension and run `python launch.py` to start the complete integrated system!
