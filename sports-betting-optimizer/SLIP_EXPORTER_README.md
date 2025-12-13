# 🎯 Extension Slip Exporter - Complete Integration

**Automatic parlay export** from your existing sports betting optimizer directly to the browser extension in real-time.

## ✅ What's Integrated

### **1. Optimizer Integration**
- ✅ **`extension_slip_exporter.py`** - Export module that converts optimizer results to extension format
- ✅ **`master_optimizer.py`** - Auto-patched to export slips after finding best parlay
- ✅ **Bridge directory structure** - Auto-created with proper JSON format

### **2. Extension Bridge**
- ✅ **FastAPI server** - Serves `/parlays/latest.json` and WebSocket `/ws` endpoint
- ✅ **Real-time updates** - Extension gets immediate notifications when optimizer runs
- ✅ **JSON format compatibility** - Exact format expected by extension

### **3. Automation**
- ✅ **Zero manual steps** - Run optimizer → extension gets parlay automatically
- ✅ **File watching** - Bridge server detects new parlays instantly
- ✅ **Cross-platform** - Works on Windows/Mac/Linux

## 🚀 Quick Start

```bash
# 1. Setup integration (one-time)
cd sports-betting-optimizer
python setup_extension_integration.py

# 2. Start bridge server
cd betting-bridge
python server.py

# 3. Load extension in browser
# Chrome: chrome://extensions/ → Load Unpacked
# Firefox: about:debugging → Load Temporary Add-on

# 4. Run your optimizer - parlays export automatically!
python -m src.promos.master_optimizer --sport nfl --promo mystery --token 25
```

## 📦 Files Created

```
sports-betting-optimizer/
├── src/extension_slip_exporter.py    # Export module
├── src/promos/master_optimizer.py    # Patched with auto-export
├── betting-bridge/                   # Bridge server directory
│   ├── server.py                     # FastAPI server
│   ├── config/credentials.json       # Bridge configuration
│   └── data/parlays/
│       ├── latest.json               # Current parlay (extension reads this)
│       └── 2025-10-03-nfl-mystery.json  # Timestamped history
├── test_extension_integration.py     # Integration tests
├── setup_extension_integration.py    # One-time setup
└── EXTENSION_USAGE.md               # Usage guide
```

## 🎯 How It Works

1. **Optimizer runs** → finds best parlay
2. **Auto-export** → saves to `betting-bridge/data/parlays/latest.json`
3. **Bridge server** → serves JSON at `http://localhost:8000/parlays/latest.json`
4. **Extension** → polls/WebSocket receives new parlay
5. **Notification** → browser shows new parlay available
6. **User** → clicks extension, reviews, applies to DraftKings

## 📄 JSON Format

Your optimizer now exports in this exact format:

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
  "promo_type": "mystery",
  "combined_odds": 264,
  "p_win": 37.85,
  "boosted_payout": 425.0,
  "boost_percentage": 25,
  "timestamp": "2025-10-03T10:30:00Z"
}
```

## 🔧 Integration Code Added

### **In `master_optimizer.py`:**
```python
# Auto-import extension exporter
try:
    from ..extension_slip_exporter import ExtensionSlipExporter
    EXTENSION_EXPORT = True
except ImportError:
    EXTENSION_EXPORT = False

# Auto-export after finding best parlay
if EXTENSION_EXPORT:
    try:
        exporter = ExtensionSlipExporter()
        exporter.export_from_args_and_result(args, best)
    except Exception as e:
        print(f"⚠️  Extension export failed: {e}")
```

### **Export Function:**
```python
def export_parlay(self, optimizer_result, sport, promo_type, promo_date):
    """Convert optimizer result to extension JSON format"""
    slip_data = {
        "id": f"{promo_date}-{sport}-{promo_type}",
        "sport": sport,
        "ev": round(optimizer_result.get("ev", 0), 2),
        "legs": [
            {
                "label": leg.label,
                "american": leg.american,
                "game": leg.game
            } for leg in optimizer_result.get("legs", [])
        ],
        # ... full format
    }

    # Write to latest.json (extension reads this)
    with open("betting-bridge/data/parlays/latest.json", 'w') as f:
        json.dump(slip_data, f, indent=2)
```

## 🎉 Results

**Before:** Manual parlay entry into extension
**After:** Run optimizer → extension gets parlay automatically

Your **sports betting optimizer** now has **direct real-time integration** with the **browser extension**. Every time you find a profitable parlay, it's **instantly available** in the extension with **one-click DraftKings application**.

**No more manual data transfer** - seamless automation from AI analysis to bet placement! 🚀
