# EQ12 Complete Reset & Recovery Toolkit

This directory contains the complete set of scripts for resetting, monitoring, and maintaining a stable EQ12 development environment.

## 🚀 Quick Start: Full Reset

If your environment is corrupted or VS Code keeps crashing, run the **one-shot reset**:

```powershell
# WARNING: This deletes your current workspace and creates a fresh clone!
# Make sure all important work is committed and pushed first!

cd C:\EQ12_BROKEN_20251122_210342\scripts
.\EQ12_FULL_RESET.ps1 -Force
```

After reset completes, restart VS Code and run the post-reset checklist.

---

## 📋 Script Inventory

### 1. **EQ12_FULL_RESET.ps1** — Complete Environment Rebuild

**When to use**: Your environment is completely broken, VS Code crashes constantly, or you have accumulated corruption.

**What it does**:
- ✅ Deletes broken repository
- ✅ Clones fresh from GitHub (`vibehigheric/edgegod-parlay`)
- ✅ Rebuilds Python venv with clean dependencies
- ✅ Resets VS Code extensions
- ✅ Clears WSL remote server corruption
- ✅ Writes safe workspace settings

**Usage**:
```powershell
.\EQ12_FULL_RESET.ps1 -Force
```

**Time**: ~5-10 minutes depending on network speed

---

### 2. **EQ12_POST_RESET_CHECKLIST.ps1** — Verify Environment Health

**When to use**: After running `EQ12_FULL_RESET.ps1` or whenever you want to verify your setup is stable.

**What it checks**:
- ✅ VS Code extensions installed and working
- ✅ Python interpreter correctly selected
- ✅ Pylance active (not degraded mode)
- ✅ Copilot and Copilot Chat authenticated
- ✅ File watcher exclusions configured
- ✅ Git repository healthy
- ✅ Python dependency conflicts

**Usage**:
```powershell
.\EQ12_POST_RESET_CHECKLIST.ps1
```

**Output**: Detailed report with pass/fail for each check + manual verification steps

---

### 3. **EQ12_ENVIRONMENT_MONITOR.ps1** — Continuous Health Monitoring

**When to use**: Run periodically (or continuously) to catch problems before they escalate into crashes.

**What it monitors**:
- ✅ VS Code memory usage
- ✅ Extension health (corruption detection)
- ✅ Python venv status
- ✅ Git lock files
- ✅ File watcher configuration
- ✅ WSL health
- ✅ Disk space
- ✅ Recent error patterns in logs

**Usage**:

```powershell
# One-time health check:
.\EQ12_ENVIRONMENT_MONITOR.ps1

# Continuous monitoring (every 5 minutes):
.\EQ12_ENVIRONMENT_MONITOR.ps1 -Continuous -IntervalSeconds 300

# Export health report to JSON:
.\EQ12_ENVIRONMENT_MONITOR.ps1 -ExportReport
```

**Output**: Color-coded health report with overall status (OK/WARNING/ERROR)

---

### 4. **EQ12_BACKUP_SNAPSHOT.ps1** — Configuration Snapshots

**When to use**: Before making risky changes (enabling Docker, DevContainers, installing new extensions).

**What it backs up**:
- ✅ `.vscode/` directory (settings, tasks, launch configs)
- ✅ Python venv state (pip freeze + requirements.txt)
- ✅ Git repository state (branch, uncommitted changes)
- ✅ VS Code extension list
- ✅ Environment variables (secrets redacted)
- ✅ Key configuration files

**Usage**:

```powershell
# Create snapshot before risky change:
.\EQ12_BACKUP_SNAPSHOT.ps1 -Label "before_docker_enable"

# List all snapshots:
.\EQ12_BACKUP_SNAPSHOT.ps1 -ListSnapshots

# Restore a specific snapshot:
.\EQ12_BACKUP_SNAPSHOT.ps1 -Restore -SnapshotId "20251122_143000_before_docker"
```

**Storage**: Snapshots saved to `C:\EQ12\backups\`

---

### 5. **EQ12_FULL_VSCODE_HARDENING.ps1** — Apply Stability Fixes

**When to use**: After fresh install or when VS Code starts showing "simplified mode" warnings.

**What it fixes**:
- ✅ Cleans WSL `.vscode-server`
- ✅ Removes corrupted Copilot Chat extensions
- ✅ Fixes Git lock files
- ✅ Applies safe workspace settings template
- ✅ Verifies Python venv

**Usage**:
```powershell
.\EQ12_FULL_VSCODE_HARDENING.ps1 -Force
```

**Requirement**: Must restart VS Code after running

---

### 6. **EQ12_REVERSE_ENGINEER_V2.ps1** — Deep Issue Analysis

**When to use**: After running `EQ12_SYSTEM_SCAN.ps1` to analyze what's broken.

**What it analyzes**:
- ✅ Copilot / Copilot Chat health (tikTokenizerWorker.js checks)
- ✅ Pylance / Python tooling
- ✅ Workspace settings
- ✅ Git lock files
- ✅ NSIS installer corruption
- ✅ WSL health
- ✅ Docker health

**Usage**:
```powershell
# First, run a system scan:
.\EQ12_SYSTEM_SCAN.ps1

# Then analyze the results:
.\EQ12_REVERSE_ENGINEER_V2.ps1 -ScanFile "C:\EQ12\reports\SCAN_RESULT_20251122_210000.json"
```

**Output**: Concrete repair suggestions with copy-pasteable commands

---

## 🔄 Typical Workflow

### Scenario 1: "VS Code keeps crashing"

```powershell
# 1. Create emergency backup
.\EQ12_BACKUP_SNAPSHOT.ps1 -Label "before_emergency_reset"

# 2. Stop all crashes
.\EQ12_EMERGENCY_STOP_V2.ps1

# 3. Full reset
.\EQ12_FULL_RESET.ps1 -Force

# 4. Verify health
.\EQ12_POST_RESET_CHECKLIST.ps1

# 5. Restart VS Code
```

---

### Scenario 2: "Copilot Chat broke after WSL update"

```powershell
# 1. Create snapshot
.\EQ12_BACKUP_SNAPSHOT.ps1 -Label "before_copilot_fix"

# 2. Run hardening (fixes WSL remote server + Copilot)
.\EQ12_FULL_VSCODE_HARDENING.ps1 -Force

# 3. Restart VS Code

# 4. Verify Copilot works
.\EQ12_POST_RESET_CHECKLIST.ps1
```

---

### Scenario 3: "About to enable Docker/DevContainers"

```powershell
# 1. Create snapshot BEFORE enabling risky features
.\EQ12_BACKUP_SNAPSHOT.ps1 -Label "before_docker_enable"

# 2. Enable Docker/DevContainer in VS Code

# 3. Monitor for issues
.\EQ12_ENVIRONMENT_MONITOR.ps1 -Continuous -IntervalSeconds 300

# 4. If things break, restore snapshot:
.\EQ12_BACKUP_SNAPSHOT.ps1 -Restore -SnapshotId "20251122_143000_before_docker_enable"
```

---

### Scenario 4: "Regular maintenance / drift prevention"

```powershell
# Run weekly health check:
.\EQ12_ENVIRONMENT_MONITOR.ps1 -ExportReport

# If warnings appear, run hardening:
.\EQ12_FULL_VSCODE_HARDENING.ps1 -Force

# Restart VS Code to apply fixes
```

---

## 📊 Success Criteria

After running any reset or hardening script, you should see:

✅ **VS Code**:
- No "simplified workspace" or "restricted mode" prompts
- No "Pylance (degraded)" status
- Python interpreter shows: `.venv\Scripts\python.exe`

✅ **Copilot Chat**:
- Opens without errors
- Responds to `@workspace` queries
- No tikTokenizer errors

✅ **Git**:
- Source Control panel shows branch and changes
- No "Git features limited" warning
- No lock files in `.git/` directory

✅ **Extensions**:
- All 4 core extensions installed and active:
  - Python (ms-python.python)
  - Pylance (ms-python.vscode-pylance)
  - GitHub Copilot (github.copilot)
  - GitHub Copilot Chat (github.copilot-chat)

---

## 🛡️ Safety Features

All destructive scripts require `-Force` flag to prevent accidental execution:

```powershell
# Safe (shows what would happen):
.\EQ12_FULL_RESET.ps1

# Destructive (actually executes):
.\EQ12_FULL_RESET.ps1 -Force
```

Before destructive operations, scripts:
- ✅ Warn you about what will be deleted
- ✅ List affected directories
- ✅ Require explicit confirmation
- ✅ Create automatic backups where possible

---

## 📁 File Locations

| Item | Location |
|------|----------|
| Scripts | `C:\EQ12_BROKEN_20251122_210342\scripts\` |
| Backups | `C:\EQ12\backups\` |
| Logs | `C:\EQ12\logs\` |
| Reports | `C:\EQ12\reports\` |
| Clean workspace (after reset) | `C:\EQ12\` |

---

## 🆘 Emergency Recovery

If everything is broken and scripts won't run:

1. **Open PowerShell as Administrator**
2. **Run emergency stop**:
   ```powershell
   taskkill /F /IM Code.exe
   taskkill /F /IM python.exe
   wsl --shutdown
   ```
3. **Manual cleanup**:
   ```powershell
   Remove-Item -Recurse -Force "C:\EQ12_BROKEN_20251122_210342"
   Remove-Item -Recurse -Force "$env:USERPROFILE\.vscode\extensions\github.copilot-chat*"
   ```
4. **Fresh start**:
   ```powershell
   git clone https://github.com/vibehigheric/edgegod-parlay.git C:\EQ12
   cd C:\EQ12
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. **Restart VS Code**, install 4 core extensions, open `C:\EQ12`

---

## 📚 Additional Documentation

- `EQ12_WHY_VSCODE_SIMPLIFIES.md` - Explains VS Code failsafe mode
- `.github/copilot-instructions.md` - AI agent instructions
- `AGENTS.md` - EQ12 project agent onboarding
- `.vscode/settings.SAFE_TEMPLATE.json` - Recommended VS Code settings

---

## 🔍 Debugging Tips

**VS Code crashes on startup?**
→ Run `EQ12_EMERGENCY_STOP_V2.ps1` then `EQ12_FULL_RESET.ps1 -Force`

**Copilot Chat "tikTokenizer" errors?**
→ Run `EQ12_FULL_VSCODE_HARDENING.ps1 -Force` (cleans WSL remote server)

**Python interpreter not found?**
→ `python -m venv C:\EQ12\.venv` then select in VS Code (Ctrl+Shift+P → Python: Select Interpreter)

**Git "file in use" errors?**
→ Check for lock files: `.\EQ12_GIT_SAFETY_TOOL.ps1`

**File watcher limit exceeded?**
→ Check `C:\EQ12\.vscode\settings.json` has proper `files.watcherExclude` patterns

---

**Last Updated**: 2025-11-22  
**Maintained By**: EQ12 System Architect (GitHub Copilot)
