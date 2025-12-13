# Sports Betting Extension - Installation Guide

## Prerequisites
- Chrome or Firefox browser
- Python 3.8+ installed
- Basic command line knowledge

## Step 1: Install Browser Extension

### Chrome Installation
1. **Open Chrome Extensions page**
   ```
   chrome://extensions/
   ```

2. **Enable Developer Mode**
   - Toggle the "Developer mode" switch in top-right corner

3. **Load Extension**
   - Click "Load unpacked"
   - Navigate to and select the `sports-betting-extension` folder
   - Extension should appear with 🎯 icon

4. **Pin Extension** (recommended)
   - Click puzzle icon in Chrome toolbar
   - Pin "Sports Betting Assistant" for easy access

### Firefox Installation
1. **Open Firefox Add-ons Debug page**
   ```
   about:debugging#/runtime/this-firefox
   ```

2. **Load Extension**
   - Click "Load Temporary Add-on..."
   - Navigate to extension folder
   - Select `manifest.json` file
   - Extension loads temporarily (until Firefox restart)

## Step 2: Start Python Backend

### Install Dependencies
```bash
# Navigate to extension directory
cd sports-betting-extension

# Install required Python packages
pip install websockets watchdog

# Optional: create virtual environment first
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
```

### Start Simple Bridge (Recommended for Testing)
```bash
python simple_bridge.py
```
**Output should show:**
```
🚀 Starting bridge on ws://localhost:8765
```

### Start Full Bridge (Production)
```bash
# Only if you have the full optimizer repo set up
python websocket_bridge.py --port 8765 --debug
```

## Step 3: Test Connection

### Verify WebSocket Connection
1. **Open extension popup** (click 🎯 icon)
2. **Check connection status** - should show green indicator
3. **Try requesting parlay** - click "Request New Parlay"

### Test DraftKings Integration
1. **Navigate to DraftKings**
   ```
   https://sportsbook.draftkings.com
   ```

2. **Open extension popup**
3. **Request a parlay** with your preferred sport
4. **Apply to bet slip** - should auto-fill selections

## Troubleshooting

### Extension Not Loading
- **Verify manifest.json** exists in extension folder
- **Check browser console** for error messages
- **Try reloading extension** in developer mode

### WebSocket Connection Failed
- **Ensure Python bridge is running** (`python simple_bridge.py`)
- **Check port 8765 is available** (no other services using it)
- **Verify firewall** allows localhost connections

### Bet Slip Not Filling
- **Confirm you're on DraftKings** sportsbook pages
- **Check browser console** for content script errors
- **Try different sport/market** combinations
- **Refresh page** and retry

### Permission Errors
- **Enable extension permissions** when prompted
- **Allow storage and scripting** access
- **Check site permissions** for DraftKings domain

## Quick Test Checklist

✅ **Extension appears in browser toolbar**
✅ **Python bridge shows connection logs**
✅ **Extension popup opens without errors**
✅ **Connection indicator is green**
✅ **Mock parlay request returns data**
✅ **DraftKings page loads extension overlay**
✅ **Bet slip fills automatically when testing**

## Next Steps

Once everything is working:

1. **Configure optimizer integration** (if using full bridge)
2. **Set up automated parlay generation**
3. **Customize sport/promo preferences**
4. **Test with real betting scenarios**
5. **Monitor performance and accuracy**

---

## Support Notes

- Extension works **locally only** - no data sent externally
- **Manual review required** before placing any real bets
- **Test with small stakes** initially
- **Verify odds** on DraftKings before confirmation
