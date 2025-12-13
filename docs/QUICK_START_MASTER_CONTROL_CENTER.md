# EQ12 Master Control Center - Quick Start Guide

**Notebook Location:** `notebooks/EQ12_Master_Control_Center.ipynb`

---

## ⚡ Quick Start (5 Minutes)

### 1. Open the Notebook
```bash
cd C:\EQ12_BROKEN_20251122_210342
code notebooks/EQ12_Master_Control_Center.ipynb
```

### 2. Install Dependencies (if needed)
```powershell
pip install psutil requests aiohttp
```

### 3. Run All Cells
- **VS Code:** Click "Run All" at the top of the notebook
- **Or:** Press Shift+Enter on each cell sequentially

### 4. Review Output
The notebook will:
- ✅ Validate your environment
- ✅ Load configuration for 22 APIs + cluster nodes
- ✅ Scan files for code issues
- ✅ Generate sample betting parlays
- ✅ Monitor hardware metrics
- ✅ Simulate GitHub automation
- ✅ Create comprehensive system report
- ✅ Simulate Ray cluster distribution

---

## 📊 What to Expect

### Cell 1: Title & Overview
- Displays architecture diagram
- Lists all integrated systems

### Cell 2-3: Environment Setup
- Checks Python version
- Verifies critical files exist
- Shows EQ12 directory structure

### Cell 4-5: Configuration
- Loads API keys (from environment variables)
- Configures cluster nodes (EQ12, HP EliteDesk, Orange Pi, Raspberry Pi)
- Displays 22 API catalog
- Validates all settings

### Cell 6-7: File Scanner
- Scans `scripts/` directory
- Detects code issues (lint errors, hardcoded secrets)
- Generates fix plan JSON
- Saves to `logs/fix_plan_YYYYMMDD_HHMMSS.json`

### Cell 8-9: Betting AI
- Initializes betting_data.db
- Generates sample 5-leg parlay
- Calculates EV + confidence scores
- Simulates Telegram notification
- Shows parlay details (teams, odds, payout)

### Cell 10-11: Hardware Monitoring
- Reads real-time system metrics (CPU, RAM, disk, network)
- Checks Docker containers
- Checks WSL2 instances
- Saves to hardware_metrics.db
- Shows status indicators (🟢 HEALTHY, 🟡 WARNING, 🔴 CRITICAL)

### Cell 12-13: GitHub Automation
- Simulates branch creation
- Generates commit message
- Creates pull request description
- Shows full automated workflow

### Cell 14-15: Database Integration
- Queries prompt_execution.db (if exists)
- Analyzes betting parlay stats
- Generates comprehensive system report
- Saves to `logs/eq12_system_report_YYYYMMDD_HHMMSS.txt`

### Cell 16-17: Ray Cluster
- Generates Ray cluster configuration (5 nodes)
- Simulates distributed workload (20K prompts)
- Shows speedup calculation (54h → 13h = 4x)
- Creates deployment script
- Saves to `scripts/EQ12_RAY_CLUSTER_DEPLOY.ps1`

### Cell 18: Comprehensive Summary
- Shows validation results
- Displays VB.NET build roadmap
- Presents hardware decision (hybrid cluster recommendation)
- Lists next action options

### Cell 19: Documentation
- Lists all generated files
- Shows integration points
- Provides usage examples

---

## 🎯 Key Outputs (Check These)

After running all cells, check these locations:

### 1. Logs Folder (`logs/`)
```
logs/
├── fix_plan_20251127_HHMMSS.json          # Code issue detection
├── eq12_system_report_20251127_HHMMSS.txt # Comprehensive report
├── betting_data.db                         # Betting parlays database
├── hardware_metrics.db                     # System monitoring database
└── prompt_execution.db                     # 20K prompts (if running)
```

### 2. Scripts Folder (`scripts/`)
```
scripts/
└── EQ12_RAY_CLUSTER_DEPLOY.ps1  # Ray cluster deployment automation
```

### 3. Console Output
- Configuration validation results
- Scan statistics (files scanned, issues found)
- Betting parlay details (5-leg example)
- Hardware metrics (RAM usage, CPU %, disk space)
- Ray cluster workload distribution
- Comprehensive summary

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'psutil'"
**Solution:**
```powershell
pip install psutil
```

### Issue: "FileNotFoundError: prompt_execution.db not found"
**Expected:** Database created when EQ12_PROMPT_RUNNER.ps1 runs  
**Workaround:** Notebook shows error gracefully, won't crash

### Issue: "VB.NET projects not found"
**Expected:** Projects exist in `visual_studio_projects/`  
**Check:** Cell 2-3 shows which files are missing (❌ vs ✅)

### Issue: Docker/WSL errors
**Expected:** Only shows error if Docker Desktop or WSL2 not running  
**Workaround:** Notebook continues without Docker/WSL stats

---

## 💡 Usage Patterns

### Test Betting Parlay Generation
Find Cell 8-9 (Betting AI section) and modify:
```python
# Change leg count
parlay_10leg = betting_hub.generate_parlay(leg_count=10)

# Change sport
parlay_nba = betting_hub.generate_parlay(leg_count=5, sport="basketball_nba")
```

### Run File Scanner on Different Directory
Find Cell 6-7 (File Scanner section) and modify:
```python
# Scan different directory
scan_results = scanner.scan_directory(config.repo_root / "tests")
```

### Check Different Hardware Metrics
Find Cell 10-11 (Hardware Monitoring) and add:
```python
# Get metrics every 5 seconds
import time
for i in range(3):
    metrics = hw_monitor.get_system_metrics()
    print(f"Snapshot {i+1}: RAM {metrics['ram']['percent']:.1f}%")
    time.sleep(5)
```

### Simulate Different Cluster Sizes
Find Cell 16-17 (Ray Cluster) and modify:
```python
# Simulate larger workload
workload_100k = ray_manager.simulate_distributed_workload(100000)
print(f"100K prompts: {workload_100k['estimated_completion_hours']:.1f} hours")
```

---

## 📚 Learn More

### Related Documentation
- `docs/VBNET_API_INTEGRATION_GUIDE.md` - VB.NET setup instructions
- `docs/CLUSTER_EXPANSION_BUSINESS_INTELLIGENCE.md` - Hardware analysis
- `docs/STRATEGIC_BUILD_DECISION_RAY_CLUSTER.md` - Ray cluster decision
- `docs/PI_ALTERNATIVES_COST_ANALYSIS.md` - HP EliteDesk vs Orange Pi vs Pi 5

### Next Steps
1. **Review notebook output** - Validate all sections work
2. **Choose next action:**
   - A) Create hardware shopping cart
   - B) Generate VB.NET solution files
   - C) Deploy Ray cluster scripts
   - D) All of the above

---

## 🎉 Expected Results

After running all cells successfully, you'll see:

✅ **Environment validated** (Python 3.12, all files found)  
✅ **Configuration loaded** (22 APIs, 5 cluster nodes, 96GB total RAM)  
✅ **File scan complete** (e.g., "50 files scanned, 12 issues found")  
✅ **Betting parlay generated** (5-leg example with $XXX payout on $100)  
✅ **Hardware metrics recorded** (current RAM: XX%, CPU: XX%)  
✅ **GitHub workflow simulated** (branch created, PR generated)  
✅ **Database reports created** (20K prompts stats + betting summary)  
✅ **Ray cluster configured** (54h → 13h speedup calculated)  
✅ **Deployment scripts generated** (PowerShell + bash ready)  
✅ **Comprehensive summary displayed** (next action options)  

---

## 🚀 Time to Run It!

1. Open notebook in VS Code
2. Click "Run All" or Shift+Enter through cells
3. Review outputs
4. Check generated files in `logs/` and `scripts/`
5. Tell me which next action you want (A/B/C/D)

**Total runtime: ~2-5 minutes** (depends on file scan size)

---

**Let's validate your EQ12 Master Control Center architecture!** 🎯
