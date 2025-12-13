# 🔗 EQ12 Sports Betting Optimizer → Extension Integration

Complete automatic integration between the Python sports betting optimizer and browser extension via WebSocket bridge.

## 🎯 What This Does

Your **Python optimizer** now automatically:
1. 📊 Computes best EV parlays (as before)
2. 📤 **Exports to JSON** in extension-compatible format
3. 🌉 **Drops into bridge directory** for real-time pickup
4. 🔄 **Triggers WebSocket broadcast** to browser extension
5. 📱 **Notifies extension users** of new optimal parlays

**Result**: Zero copy-paste. Every optimizer run instantly updates your browser extension.

---

## 🚀 Quick Start

### 1️⃣ Setup (One Time)
```bash
python setup_complete_integration.py
```

### 2️⃣ Test Integration
```bash
python test_integration_complete.py
```

### 3️⃣ Run Optimizer (Now Auto-Exports)
```bash
python -m src.promos.master_optimizer --sport nfl --promo mystery
```

### 4️⃣ Start Bridge Server (In Extension Folder)
```bash
cd ../sports-betting-extension
python bridge.py
```

### 5️⃣ Load Browser Extension
- Open Chrome/Firefox
- Load extension from `sports-betting-extension` folder
- Watch for automatic parlay notifications!

---

## 🔧 How It Works

### Integration Files Added:

#### `src/core/slip_export.py`
- **Purpose**: Simple helper to convert optimizer results to extension JSON format
- **Key Functions**:
  - `export_slip(slip, bridge_dir)` - Saves JSON to bridge
  - `build_slip_from_optimizer_result(args, best)` - Converts optimizer format
  - `export_optimizer_result(args, best)` - One-step export

#### Updated `src/promos/master_optimizer.py`
- **Added**: Auto-import of `slip_export`
- **Added**: Export call after best parlay computation
- **Added**: Graceful fallback if export fails

### Data Flow:
```
Optimizer → slip_export.py → betting-bridge/data/parlays/latest.json → WebSocket → Extension
```

---

## 📊 JSON Format

The optimizer exports parlays in this extension-ready format:

```json
{
  "id": "2025-10-03-nfl-mystery",
  "sport": "nfl",
  "ev": 12.34,
  "stake": 100,
  "legs": [
    {
      "label": "Chiefs -3.5",
      "american": -110,
      "game": "KC @ DEN"
    },
    {
      "label": "Over 45.5",
      "american": -105,
      "game": "KC @ DEN"
    }
  ],
  "combined_odds": 264,
  "p_win": 37.85,
  "boosted_payout": 425.0,
  "promo_type": "mystery",
  "promo_date": "2025-10-03",
  "timestamp": "2025-10-03T15:30:45"
}
```

---

## 🔍 Files Created/Modified

### New Files:
- ✅ `src/core/slip_export.py` - Export helper
- ✅ `setup_complete_integration.py` - One-command setup
- ✅ `test_integration_complete.py` - Integration testing
- ✅ `INTEGRATION_README.md` - This file

### Modified Files:
- ✅ `src/promos/master_optimizer.py` - Added auto-export calls

### Directory Structure Created:
```
sports-betting-optimizer/
├── betting-bridge/          # Bridge directory for extension
│   └── data/
│       └── parlays/
│           ├── latest.json      # Extension watches this
│           └── parlay_*.json    # Timestamped history
└── src/
    └── core/
        └── slip_export.py   # New export helper
```

---

## 🧪 Testing

### Test the Export:
```bash
python test_integration_complete.py
```

### Test Full Integration:
```bash
# Terminal 1: Run optimizer
python -m src.promos.master_optimizer --sport nfl --promo mystery

# Terminal 2: Start bridge (different directory)
cd ../sports-betting-extension
python bridge.py

# Browser: Load extension and wait for notification
```

---

## 🔗 Extension Bridge Server

The bridge server (in `sports-betting-extension` folder) provides:

- **HTTP Endpoint**: `GET /parlays/latest.json`
- **WebSocket**: `ws://localhost:8000/ws` for real-time updates
- **File Watching**: Monitors `betting-bridge/data/parlays/` for changes
- **Auto-Broadcast**: Pushes new parlays to all connected extensions

---

## ⚡ Workflow After Integration

1. **Run Optimizer**: `python -m src.promos.master_optimizer --sport cfb --promo stepped`
2. **Automatic Export**: Slip saved to `betting-bridge/data/parlays/latest.json`
3. **Bridge Detection**: Server detects file change
4. **WebSocket Broadcast**: New parlay pushed to extensions
5. **Extension Alert**: Browser notification with "Apply to Sportsbook" button
6. **One-Click Betting**: Extension fills DraftKings/FanDuel bet slip

**No manual steps. No copy-paste. Fully automated.**

---

## 🛠️ Customization

### Change Bridge Directory:
```python
from src.core.slip_export import export_optimizer_result

# Custom bridge location
export_optimizer_result(args, best, bridge_dir="/custom/path/to/bridge")
```

### Add Custom Slip Data:
Edit `build_slip_from_optimizer_result()` in `src/core/slip_export.py`:

```python
slip = {
    "id": f"{args.promo_date}-{args.sport}-{args.promo}",
    "sport": args.sport,
    "ev": float(best_result.get("ev", 0)),
    "stake": best_result.get("stake", getattr(args, "stake", 100)),
    "legs": legs,
    # Add your custom fields here:
    "confidence": best_result.get("confidence", 0),
    "kelly_bet": best_result.get("kelly_size", 0),
    "custom_metric": your_calculation(best_result)
}
```

---

## 🐛 Troubleshooting

### Export Not Working?
```bash
# Check if slip_export is imported
grep -n "slip_export" src/promos/master_optimizer.py

# Test export directly
python -c "from src.core.slip_export import export_slip; print('✅ Import works')"
```

### Bridge Directory Issues?
```bash
# Check bridge directory exists
ls -la betting-bridge/data/parlays/

# Check latest.json is being written
python -m src.promos.master_optimizer --sport nfl --promo mystery
cat betting-bridge/data/parlays/latest.json
```

### Extension Not Receiving?
- Ensure bridge server is running: `python bridge.py`
- Check WebSocket connection in browser console
- Verify extension has correct WebSocket URL (`ws://localhost:8000/ws`)

---

## 🎉 Success Indicators

When everything is working, you'll see:

1. **Optimizer Output**:
   ```
   ✅ Best NFL parlay for mystery on 2025-10-03
   📤 Slip exported to betting-bridge/data/parlays/latest.json
   ```

2. **Bridge Server Output**:
   ```
   📁 File change detected: latest.json
   🔄 Broadcasting to 1 WebSocket clients
   ```

3. **Browser Extension**:
   ```
   🎯 New parlay received!
   EV: $12.34 | 3 legs | Click to apply
   ```

**You now have a fully automated sports betting optimization workflow!**
