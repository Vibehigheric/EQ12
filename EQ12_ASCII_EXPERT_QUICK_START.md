# EQ12 ASC II Expert — Quick Start Guide

**Complete Automation & Systems Control Level II Environment — Ready in 5 Minutes**

---

## 🚀 Immediate Setup (3 Steps)

### Step 1: Load Master Profile
```powershell
# Add to your PowerShell profile
code $PROFILE

# Add this line at the end:
. "C:\EQ12_BROKEN_20251122_210342\EQ12_MASTER_PROFILE_ASCII_EXPERT.ps1"

# Reload PowerShell or source the profile:
. $PROFILE
```

### Step 2: Verify Environment
```powershell
# Run environment scan
eq12-env-scan

# Test API keys
eq12-api-test

# Check system status
eq12-status
```

### Step 3: Open VB.NET Solution
```powershell
# Open in Visual Studio
Start-Process "C:\EQ12_BROKEN_20251122_210342\EQ12.ASCIIExpert.sln"

# Or open in VS Code
code "C:\EQ12_BROKEN_20251122_210342"
```

---

## 📋 Core Commands Reference

### Essential Commands
```powershell
eq12-help           # Show all commands
eq12-status         # System health check
eq12-logs           # Tail live logs
eq12-config         # Edit .env configuration
eq12-env-scan       # Detect dev environment
```

### Sports Betting
```powershell
run-odds            # Fetch live odds (all sports)
run-parlay          # Generate EV+ parlays
eq12-live-odds      # Real-time streaming
eq12-weather        # Stadium weather
eq12-injuries       # Injury reports
```

### VB.NET ASC II Modules
```powershell
eq12-core-test      # Test credential manager
eq12-security-check # VPN monitor
eq12-telegram-send "Test message"  # Send Telegram alert
eq12-ai-diagnose "STO W8114"       # AI diagnostics
eq12-github-release "v1.0.0" "Release notes"  # Create GitHub release
eq12-dashboard      # Launch Command Center UI
```

### Docker & Containers
```powershell
eq12-docker-start   # Start all containers
eq12-docker-stop    # Stop all containers
eq12-docker-logs godstack  # View container logs
eq12-jupyter-start  # Start JupyterLab (NBA analysis)
```

### Data Management
```powershell
eq12-api-test       # Validate API keys
eq12-db-check       # Database health check
eq12-refresh-data   # Clear cache and refetch
eq12-export         # Export to CSV/JSON
```

### System Maintenance
```powershell
eq12-clean          # Deep clean temp files
eq12-backup         # Create encrypted backup
eq12-test           # Run test suite
eq12-recycle        # Quick cleanup
```

---

## 🧠 VB.NET Solution Structure

```
EQ12.ASCIIExpert.sln
├── EQ12.Core          → Credential manager + logging
├── EQ12.Security      → VPN monitoring + encryption
├── EQ12.TelegramBot   → Alert system
├── EQ12.StackAgent    → GPT-5/Hugging Face AI
├── EQ12.CI            → GitHub automation
├── EQ12.Diagnostics   → VFD/PLC diagnostics
└── EQ12.CommandCenter → Master UI dashboard
```

---

## 🔐 Your Pre-Configured API Keys

All keys are already loaded from `.env`:

- ✅ **OPENAI_API_KEY** — GPT-5 reasoning agent
- ✅ **ODDS_API_KEY** — Sports betting lines
- ✅ **TELEGRAM_BOT_TOKEN** — Alerts and notifications
- ✅ **GITHUB_TOKEN** — Automated releases
- ✅ **GROQ_API_KEY** — Fast inference
- ✅ **OPENROUTER_API_KEY** — Multi-model routing
- ✅ **GOOGLE_AI_API_KEY** — Gemini integration
- ✅ **HUGGINGFACE_TOKEN** — Model hub access

---

## 📊 Daily Workflow Example

### Morning Routine
```powershell
# 1. Check system health
eq12-status

# 2. Verify VPN connection
eq12-security-check

# 3. Fetch latest odds
run-odds

# 4. Generate parlays
run-parlay

# 5. Send summary to Telegram
eq12-telegram-send "Morning report: System healthy, 5 EV+ parlays found"
```

### Sports Analysis
```powershell
# 1. Start Jupyter for NBA analysis
eq12-jupyter-start

# 2. Open master index
eq12-nba-master

# 3. Check weather for outdoor games
eq12-weather

# 4. Monitor injuries
eq12-injuries
```

### Industrial Diagnostics (ASC II)
```powershell
# 1. Parse VFD fault logs
eq12-ai-diagnose "Network Timeout STO W8114"

# 2. Check PLC network health
eq12-diagnostics-network

# 3. Send critical alert
eq12-telegram-send "VFD fault detected - Network timeout on Lenze 8400"
```

---

## 🔧 Build VB.NET Projects

```powershell
# Open solution in Visual Studio
Start-Process "EQ12.ASCIIExpert.sln"

# Or build from command line
msbuild EQ12.ASCIIExpert.sln /p:Configuration=Release

# Run Command Center
eq12-dashboard
```

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `EQ12.ASCIIExpert.sln` | Master VB.NET solution |
| `EQ12_MASTER_PROFILE_ASCII_EXPERT.ps1` | PowerShell profile with all commands |
| `.env` | API keys and credentials |
| `docs/EQ12_ASCII_EXPERT_COMPLETE_GUIDE.md` | Complete documentation |
| `docker-compose.yml` | Container orchestration |
| `requirements.txt` | Python dependencies |

---

## 🆘 Troubleshooting

### "Command not found: eq12-xxx"
**Solution**: 
```powershell
. "C:\EQ12_BROKEN_20251122_210342\EQ12_MASTER_PROFILE_ASCII_EXPERT.ps1"
```

### "API key not found"
**Solution**: 
```powershell
eq12-config  # Opens .env file for editing
```

### "Docker not running"
**Solution**: 
1. Start Docker Desktop manually
2. Run: `eq12-docker-start`

### "VPN disconnected"
**Solution**: 
```powershell
eq12-security-check  # Auto-reconnects VPN
```

---

## ✅ Success Checklist

After setup, verify:

- [ ] `eq12-help` shows all commands
- [ ] `eq12-env-scan` detects .NET SDK and Visual Studio
- [ ] `eq12-api-test` validates all API keys
- [ ] `eq12-status` shows Docker containers running
- [ ] `eq12-core-test` loads credentials successfully
- [ ] `eq12-telegram-send "Test"` sends alert
- [ ] `EQ12.ASCIIExpert.sln` opens in Visual Studio
- [ ] `eq12-dashboard` launches Command Center UI

---

## 🎯 Next Steps

1. **Build VB.NET Projects**: Open solution in Visual Studio, Build → Build Solution
2. **Explore Modules**: Test each module (Core, Security, TelegramBot, StackAgent, CI, Diagnostics)
3. **Customize UI**: Edit `EQ12.CommandCenter` WinForms/WPF dashboard
4. **Add Diagnostics**: Extend `EQ12.Diagnostics` with custom PLC/VFD parsers
5. **Automate Workflows**: Schedule PowerShell tasks for daily routines

---

## 📞 Support Resources

- **Complete Guide**: `docs/EQ12_ASCII_EXPERT_COMPLETE_GUIDE.md`
- **Logs**: `logs/` directory (tail with `eq12-logs`)
- **Test Suite**: `eq12-test` (runs pytest + Pester)
- **Environment Scan**: `eq12-env-scan`

---

**You're Ready!**

Run `eq12-help` to see all 50+ commands, or `eq12-env-scan` to validate your complete development environment.

**Version**: 1.0.0
**Created**: 2025-11-27
**EQ12 ASC II Expert System**
