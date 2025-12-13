# EQ12 COMPLETE SETUP & RECOVERY GUIDE

**Complete toolkit for resetting, monitoring, and maintaining your EQ12 development environment**

Repository: `vibehigheric/edgegod-parlay` (Sports betting/odds analysis)

---

## 🚀 Quick Start

### For New Setup (Fresh Install)
```powershell
# 1. Install recommended MCP servers
.\scripts\EQ12_MCP_SELECTION_GUIDE.ps1

# 2. Run post-setup verification
.\scripts\EQ12_POST_RESET_CHECKLIST.ps1

# 3. Create first backup snapshot
.\scripts\EQ12_DAILY_SNAPSHOT.ps1

# 4. Start drift monitoring
.\scripts\EQ12_DRIFT_MONITOR.ps1 -ExportReport
```

### For Broken Environment (Emergency Reset)
```powershell
# WARNING: Destructive! Backs up automatically
cd C:\EQ12_BROKEN_20251122_210342\scripts
.\EQ12_FULL_RESET.ps1 -Force
```

---

## 📁 Script Inventory

### Core Reset & Recovery
| Script | Purpose | When to Use |
|--------|---------|-------------|
| `EQ12_FULL_RESET.ps1` | Complete environment rebuild | VS Code crashes, total corruption |
| `EQ12_POST_RESET_CHECKLIST.ps1` | Verify environment health | After reset or major changes |
| `EQ12_FULL_VSCODE_HARDENING.ps1` | Apply stability fixes | VS Code "simplified mode" warnings |

### Monitoring & Prevention
| Script | Purpose | When to Use |
|--------|---------|-------------|
| `EQ12_DRIFT_MONITOR.ps1` | Detect environment drift | Daily/weekly health checks |
| `EQ12_ENVIRONMENT_MONITOR.ps1` | Real-time system monitoring | Continuous stability tracking |
| `EQ12_SAFE_SCAN.ps1` | Crash-resistant file scanner | When full scan causes crashes |

### Backup & Restore
| Script | Purpose | When to Use |
|--------|---------|-------------|
| `EQ12_DAILY_SNAPSHOT.ps1` | Create ZIP backup | Daily automated backups |
| `EQ12_RESTORE_SNAPSHOT.ps1` | Restore from backup | Recover from bad changes |
| `EQ12_BACKUP_SNAPSHOT.ps1` | Advanced snapshots | Before risky changes (Docker, DevContainers) |

### Configuration & Setup
| Script | Purpose | When to Use |
|--------|---------|-------------|
| `EQ12_MCP_SELECTION_GUIDE.ps1` | Choose MCP servers | Initial MCP setup |
| `EQ12_REVERSE_ENGINEER_V2.ps1` | Deep issue analysis | Diagnose specific problems |

---

## 🛠️ MCP Server Recommendations

Based on EQ12 project analysis (`vibehigheric/edgegod-parlay`):

### ✅ CRITICAL (Install These)
1. **filesystem** - File operations (reading/writing code)
2. **git** - Repository management (commits, branches, status)

### ✅ HIGH PRIORITY
3. **fetch** - Web scraping, API calls (core EQ12 feature)
4. **GitHub** - Issue/PR management
5. **Playwright** - Browser automation for betting sites

### ⚠️ MEDIUM PRIORITY
6. **time** - Timestamp/timezone conversions

### ❌ SKIP
- **Netdata** - Not needed for development
- **Context7** - Redundant with filesystem + GitHub
- **ChromeDevTools** - Use Playwright instead
- **MongoDB/Elasticsearch/Supabase** - No database layer in EQ12

**Install Command**:
```powershell
pip install mcp-server-git mcp-server-fetch mcp-server-time
```

**Configuration**: Auto-generated in `C:\Users\<username>\AppData\Roaming\Code\User\mcp.json`

---

## 📋 Common Workflows

### Scenario 1: VS Code Crashes on Startup
```powershell
# 1. Emergency stop
.\scripts\EQ12_EMERGENCY_STOP_V2.ps1

# 2. Create backup before reset
.\scripts\EQ12_DAILY_SNAPSHOT.ps1

# 3. Full reset
.\scripts\EQ12_FULL_RESET.ps1 -Force

# 4. Verify health
.\scripts\EQ12_POST_RESET_CHECKLIST.ps1

# 5. Restart VS Code
```

### Scenario 2: Copilot Chat "tikTokenizer" Errors
```powershell
# 1. Backup current state
.\scripts\EQ12_BACKUP_SNAPSHOT.ps1 -Label "before_copilot_fix"

# 2. Run hardening (fixes WSL remote server)
.\scripts\EQ12_FULL_VSCODE_HARDENING.ps1 -Force

# 3. Restart VS Code

# 4. Test Copilot Chat
# Open Copilot Chat → Ask: "@workspace what files are in scripts/"
```

### Scenario 3: Before Enabling Docker/DevContainers
```powershell
# 1. Create pre-change snapshot
.\scripts\EQ12_BACKUP_SNAPSHOT.ps1 -Label "before_docker_enable"

# 2. Run drift check to establish baseline
.\scripts\EQ12_DRIFT_MONITOR.ps1 -ExportReport

# 3. Enable Docker/DevContainer in VS Code

# 4. Monitor for issues
.\scripts\EQ12_ENVIRONMENT_MONITOR.ps1 -Continuous -IntervalSeconds 300

# 5. If problems occur, restore snapshot:
.\scripts\EQ12_RESTORE_SNAPSHOT.ps1 -BackupZip "C:\EQ12\backups\EQ12_SNAPSHOT_<timestamp>.zip"
```

### Scenario 4: Weekly Maintenance
```powershell
# Run every Monday:
.\scripts\EQ12_DRIFT_MONITOR.ps1 -ExportReport
.\scripts\EQ12_DAILY_SNAPSHOT.ps1
.\scripts\EQ12_ENVIRONMENT_MONITOR.ps1 -ExportReport

# Review reports in C:\EQ12\logs\
```

---

## ✅ Success Criteria

After reset/hardening, you should have:

### VS Code
- ✅ No "simplified workspace" or "restricted mode" prompts
- ✅ Python interpreter: `.venv\Scripts\python.exe`
- ✅ Pylance status: "Pylance" (not "Pylance (degraded)")
- ✅ All 4 core extensions active (Python, Pylance, Copilot, Copilot Chat)

### Copilot Chat
- ✅ Opens without errors
- ✅ Responds to `@workspace` queries
- ✅ No tikTokenizer errors
- ✅ MCP servers active (test with file/git queries)

### Git
- ✅ Source Control panel shows branch + changes
- ✅ No "Git features limited" warning
- ✅ No lock files in `.git/` directory

### System Health
- ✅ No Git lock files
- ✅ Single `.venv` directory
- ✅ Logs folder < 250 MB
- ✅ Disk space > 20 GB free

---

## 🔧 Automation Setup

### Daily Backup (Recommended)
```powershell
# Run as Administrator:
schtasks /create /sc daily /tn "EQ12 Daily Snapshot" `
  /tr "powershell -ExecutionPolicy Bypass -File C:\EQ12\scripts\EQ12_DAILY_SNAPSHOT.ps1" `
  /st 09:00
```

### Hourly Drift Monitor (Optional)
```powershell
# Run as Administrator:
schtasks /create /sc hourly /tn "EQ12 Drift Monitor" `
  /tr "powershell -ExecutionPolicy Bypass -File C:\EQ12\scripts\EQ12_DRIFT_MONITOR.ps1 -ExportReport" `
  /st 00:00
```

---

## 🆘 Emergency Recovery

If scripts won't run or VS Code is completely broken:

```powershell
# 1. Manual process termination
taskkill /F /IM Code.exe
taskkill /F /IM python.exe
wsl --shutdown

# 2. Manual cleanup
Remove-Item -Recurse -Force "C:\EQ12_BROKEN_20251122_210342"
Remove-Item -Recurse -Force "$env:USERPROFILE\.vscode\extensions\github.copilot-chat*"

# 3. Fresh clone
git clone https://github.com/vibehigheric/edgegod-parlay.git C:\EQ12
cd C:\EQ12

# 4. Rebuild Python environment
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# 5. Restart VS Code and install 4 core extensions
```

---

## 📚 Additional Documentation

- `EQ12_WHY_VSCODE_SIMPLIFIES.md` - Why VS Code enters failsafe mode
- `EQ12_TOOLKIT_README.md` - Detailed script documentation
- `.github/copilot-instructions.md` - AI agent instructions for this repo
- `AGENTS.md` - Agent onboarding guide
- `.vscode/settings.SAFE_TEMPLATE.json` - Recommended VS Code settings

---

## 🔍 Troubleshooting

### "Property 'Count' cannot be found"
**Fixed!** `EQ12_SAFE_SCAN.ps1` now wraps `Get-ChildItem` in `@()` to ensure Count property exists.

### "Unexpected token" in PowerShell Scripts
**Fixed!** All scripts now use proper encoding without Unicode characters that cause parsing errors.

### MCP Servers Not Loading
1. Verify `mcp.json` exists: `C:\Users\<username>\AppData\Roaming\Code\User\mcp.json`
2. Check Python packages installed: `pip list | findstr mcp`
3. Restart VS Code completely (close all windows)
4. Check Copilot Chat output panel for errors

### Python Dependency Conflicts
**Known Issue**: `openai` and `orjson` version conflicts are non-blocking for MCP functionality. If needed:
```powershell
pip install "openai<1.100" "orjson>=3.9.10" --force-reinstall
```

---

## 📊 File Locations

| Item | Location |
|------|----------|
| Scripts | `C:\EQ12_BROKEN_20251122_210342\scripts\` |
| Daily Backups | `C:\EQ12\backups\` |
| Logs & Reports | `C:\EQ12\logs\` |
| MCP Configuration | `C:\Users\<username>\AppData\Roaming\Code\User\mcp.json` |
| VS Code Settings | `C:\EQ12\.vscode\settings.json` |

---

**Last Updated**: 2025-11-22  
**Total Scripts**: 14  
**Recommended MCPs**: 6 (filesystem, git, fetch, time, github, playwright)  
**Estimated Setup Time**: 10-15 minutes

---

**Ready to start?** Run `.\scripts\EQ12_MCP_SELECTION_GUIDE.ps1` to begin!
