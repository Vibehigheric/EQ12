# EQ12 Buffalo Stack Integration

🚀 **Complete automation stack for civil service job tracking, betting automation, and ChatGPT integration**

## 📋 What This Does

The Buffalo Stack is a comprehensive automation system that:

- **🏛️ Tracks Civil Service Jobs** - Monitors union-eligible positions (Code 14215)
- **🤖 ChatGPT Integration** - Prompts for API keys and enables code refactoring
- **⚡ EQ12 Automation** - Orchestrates betting bots, travel automation, and more
- **📅 Scheduled Tasks** - Runs automatically via Windows Task Scheduler
- **📱 Notifications** - Telegram alerts for new job postings
- **📊 Database Tracking** - SQLite database for job history and analytics

---

## 🚀 Quick Start

### 1️⃣ Installation

**Option A: Automated Install (Recommended)**
```powershell
# Run as Administrator
cd C:\EQ12\buffalo_stack\bin
.\install.ps1
```

**Option B: Manual Setup**
```powershell
# Create directories
mkdir C:\EQ12\buffalo_stack\logs
mkdir C:\EQ12\buffalo_stack\config

# Copy configuration templates
copy .env.example .env
copy config.example.yaml config\config.yaml

# Install Python dependencies
pip install -r requirements.txt
```

### 2️⃣ Configuration

Edit your API keys in `.env`:
```bash
OPENAI_API_KEY=your_openai_api_key_here
ODDS_API_KEY=your_odds_api_key_here  
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

### 3️⃣ First Run

```powershell
cd C:\EQ12\buffalo_stack
python eq12_godmode_runner_plus.py
```

**The system will:**
- ✅ Prompt for API keys if not configured
- ✅ Initialize the civil service job database  
- ✅ Run all enabled automation modules
- ✅ Log everything to `logs/` directory

---

## 🎯 What to Submit When Asked for "Refactor"

When the ChatGPT integration asks you what to refactor, here are good examples:

### **For Code Refactoring:**
- `"Make this function more efficient and add error handling"`
- `"Convert this to use async/await patterns"`  
- `"Add type hints and improve documentation"`
- `"Refactor this class to follow SOLID principles"`
- `"Optimize this database query and add logging"`

### **For Code Analysis:**
- `"Explain what this code does and suggest improvements"`
- `"Find potential security vulnerabilities"`
- `"Review for Python best practices"`
- `"Check for performance bottlenecks"`

### **For Bug Fixes:**
- `"Fix any syntax errors and logical issues"`
- `"Add proper exception handling"`
- `"Validate input parameters"`

---

## 📁 Directory Structure

```
C:\EQ12\buffalo_stack\
├── 📁 bin\                     # Executables & scripts
│   ├── install.ps1            # Automated installer
│   ├── uninstall.ps1          # Automated uninstaller  
│   └── run_eq12_combo.bat     # Task scheduler wrapper
├── 📁 civil\                  # Civil service tracker
│   └── civil_service_tracker.py
├── 📁 config\                 # Configuration files
│   └── config.yaml           # Main config (copy from example)
├── 📁 logs\                   # All log files
│   ├── civil_service_YYYY-MM-DD.log
│   ├── eq12_runner_YYYY-MM-DD.log
│   └── run_summary_YYYY-MM-DD.json
├── 📁 tasks\                  # Task Scheduler XML
│   ├── schedule_civil_tracker.xml
│   └── schedule_eq12_combo.xml
├── 📄 eq12_godmode_runner_plus.py  # Main orchestrator
├── 📄 requirements.txt        # Python dependencies
├── 📄 .env                   # API keys (copy from example)
├── 📄 .env.example          # Template for API keys
├── 📄 config.example.yaml   # Template for configuration
└── 📄 README.md             # This file
```

---

## ⚡ Command Line Options

```powershell
# Full run with API key prompting
python eq12_godmode_runner_plus.py

# Skip API key prompts (use environment only)
python eq12_godmode_runner_plus.py --skip-api-prompts

# Run only civil service tracker
python eq12_godmode_runner_plus.py --civil-only

# Run only betting automation 
python eq12_godmode_runner_plus.py --betting-only

# Preview what would run (no execution)
python eq12_godmode_runner_plus.py --dry-run

# Civil service tracker standalone
python civil\civil_service_tracker.py

# Show recent jobs (last 7 days)
python civil\civil_service_tracker.py --show-recent 7

# Show database statistics
python civil\civil_service_tracker.py --stats
```

---

## 🔧 Troubleshooting

### **"Another instance running as admin" Error**
```powershell
# Kill any stuck Python processes
Get-Process python | Where-Object {$_.Path -like "*buffalo*"} | Stop-Process -Force

# Or restart VS Code without admin privileges
```

### **Missing API Keys**
- The system will prompt you for keys on first run
- Edit `.env` file to persist keys between runs
- Use `--skip-api-prompts` flag to disable prompting

### **No Jobs Found**  
- Check `logs/civil_service_*.log` for details
- Customize job sources in `config.yaml`
- Mock data is used by default for testing

### **Task Scheduler Issues**
```powershell
# Check if tasks are registered
schtasks /query /tn "BuffaloStack\CivilServiceTracker"
schtasks /query /tn "BuffaloStack\EQ12ComboRunner"

# Manually run a task
schtasks /run /tn "BuffaloStack\CivilServiceTracker"
```

### **Permission Errors**
```powershell
# Run installer as Administrator
Right-click PowerShell → "Run as Administrator"
cd C:\EQ12\buffalo_stack\bin
.\install.ps1
```

---

## 📊 Monitoring & Logs

### **Log Files**
- `logs/eq12_runner_YYYY-MM-DD.log` - Main orchestrator logs
- `logs/civil_service_YYYY-MM-DD.log` - Job tracker logs  
- `logs/run_summary_YYYY-MM-DD.json` - Execution summaries

### **Database**
- `civil_service_jobs.db` - SQLite database with job history
- Use any SQLite browser to view data
- Automatic backups in Task Scheduler

### **Notifications**
- Telegram: New job alerts with details
- Logs: All activities recorded with timestamps
- Desktop: Shortcut created for easy access

---

## 🔄 Scheduled Automation

The system automatically runs via Windows Task Scheduler:

- **Civil Service Tracker**: Every 4 hours + at system logon
- **EQ12 Combo Runner**: Every 4 hours (all modules)
- **Automatic Restart**: Failed tasks retry 3 times with 10min delay
- **Log Cleanup**: Old logs automatically pruned

---

## 🆘 Support

### **View Recent Activity**
```powershell
# Last 24 hours of jobs
python civil\civil_service_tracker.py --show-recent 1

# System statistics  
python civil\civil_service_tracker.py --stats

# Check if everything is working
python eq12_godmode_runner_plus.py --dry-run
```

### **Reset Everything**
```powershell
# Uninstall completely
cd C:\EQ12\buffalo_stack\bin
.\uninstall.ps1 -RemoveFiles

# Reinstall fresh
.\install.ps1 -Force
```

---

## 🎯 Integration with EQ12

This Buffalo Stack integrates seamlessly with existing EQ12 components:

- **Betting Bots**: `EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro.py`
- **Travel Automation**: `travel/travel_bot.py`
- **Dropship Sync**: `dropship/sync.py`
- **Odds Parser**: `odds_parser.py`
- **Parlay Builder**: `parlay_builder.py`

The system will automatically detect and run any available EQ12 modules.

---

## ✅ Success Indicators

You'll know it's working when:

- ✅ Desktop shortcut created: "EQ12 Buffalo Stack"
- ✅ Task Scheduler shows: BuffaloStack tasks registered
- ✅ Database created: `civil_service_jobs.db`
- ✅ Logs directory populated with timestamped files
- ✅ API key prompts appear and save successfully
- ✅ Mock civil service jobs appear in database
- ✅ Telegram notifications sent (if configured)

**Ready to automate your civil service job search and EQ12 workflows! 🚀**