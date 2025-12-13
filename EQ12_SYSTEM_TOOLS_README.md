# EQ12 System Repair Tools - Quick Start Guide

This repository now includes a complete suite of AI-assisted system repair and maintenance tools.

---

## 📋 What Was Just Created

### 1. **Permanent Copilot Instructions** 
**File:** `.github/copilot-instructions.md`

This file teaches GitHub Copilot to understand the EQ12 workspace structure and automatically:
- Scan for common issues (broken extensions, corrupted files, etc.)
- Suggest repairs using the tools below
- Follow EQ12 coding standards
- Never perform destructive operations without confirmation

### 2. **PowerShell Diagnostic Tools**

#### `EQ12_SYSTEM_SCAN.ps1`
**Location:** `scripts/EQ12_SYSTEM_SCAN.ps1`

Comprehensive workspace scanner that:
- ✅ Inventories all files in the EQ12 repo
- ✅ Optionally scans VS Code user directories (`-IncludeVSCode`)
- ✅ Outputs timestamped JSON reports to `reports/`
- ✅ 100% read-only - never modifies files

**Usage:**
```powershell
.\scripts\EQ12_SYSTEM_SCAN.ps1
.\scripts\EQ12_SYSTEM_SCAN.ps1 -IncludeVSCode -Verbose
```

#### `EQ12_REVERSE_ENGINEER.ps1`
**Location:** `scripts/EQ12_REVERSE_ENGINEER.ps1`

Analyzes scan results to detect:
- 🔍 Corrupted Copilot extension files (tiny tikTokenizerWorker.js)
- 🔍 Multiple conflicting VS Code settings
- 🔍 Broken Python virtual environments
- 🔍 Oversized cache directories
- 🔍 Missing critical configuration files

**Usage:**
```powershell
$ScanFile = Get-ChildItem .\reports\SCAN_RESULT_*.json | Sort LastWriteTime -Desc | Select -First 1
.\scripts\EQ12_REVERSE_ENGINEER.ps1 -ScanFile $ScanFile.FullName
```

#### `EQ12_GIT_SAFETY_TOOL.ps1`
**Location:** `scripts/EQ12_GIT_SAFETY_TOOL.ps1`

Git repository maintenance tool that:
- 🔧 Clears read-only flags blocking Git operations
- 🔧 Removes stale lock files (`.git\index.lock`, etc.)
- 🔧 Verifies `.git` directory integrity
- 🔧 Logs all actions to `logs/`
- ⚠️ NEVER deletes the `.git` directory

**Usage:**
```powershell
.\scripts\EQ12_GIT_SAFETY_TOOL.ps1
.\scripts\EQ12_GIT_SAFETY_TOOL.ps1 -DryRun    # Preview actions
.\scripts\EQ12_GIT_SAFETY_TOOL.ps1 -Force      # Skip confirmations
```

### 3. **Copilot Health Check Guide**
**File:** `EQ12_COPILOT_HEALTHCHECK.md`

Comprehensive troubleshooting documentation for:
- ✅ Diagnosing Copilot/Copilot Chat issues
- ✅ Repairing corrupted extension files
- ✅ Cleaning WSL Remote caches
- ✅ Preventive maintenance procedures
- ✅ Quick reference commands

### 4. **VS Code Tasks**

Three new tasks added to `.vscode/tasks.json`:

| Task Name | Keyboard Shortcut | Description |
|-----------|-------------------|-------------|
| **EQ12: Full System Sweep** | `Ctrl+Shift+P` → Run Task | Runs scan + analysis in one command |
| **EQ12: System Scan Only** | `Ctrl+Shift+P` → Run Task | Just the scan (no analysis) |
| **EQ12: Git Safety Check** | `Ctrl+Shift+P` → Run Task | Clean Git locks and read-only flags |

**To run a task:**
1. Press `Ctrl+Shift+P`
2. Type "Tasks: Run Task"
3. Select the task from the list

---

## 🚀 Quick Start Workflow

### First-Time Setup
```powershell
# Navigate to repo
cd C:\EQ12_BROKEN_20251122_210342

# Create required directories
New-Item -Path reports, logs -ItemType Directory -Force

# Run initial system scan
.\scripts\EQ12_SYSTEM_SCAN.ps1 -IncludeVSCode -Verbose
```

### Regular Maintenance
```powershell
# Option 1: Use VS Code Task (recommended)
# Ctrl+Shift+P → "Tasks: Run Task" → "EQ12: Full System Sweep"

# Option 2: Manual PowerShell
.\scripts\EQ12_SYSTEM_SCAN.ps1
$LatestScan = Get-ChildItem .\reports\SCAN_RESULT_*.json | Sort LastWriteTime -Desc | Select -First 1
.\scripts\EQ12_REVERSE_ENGINEER.ps1 -ScanFile $LatestScan.FullName
```

### When Git Issues Occur
```powershell
# Preview what would be fixed
.\scripts\EQ12_GIT_SAFETY_TOOL.ps1 -DryRun

# Apply fixes
.\scripts\EQ12_GIT_SAFETY_TOOL.ps1 -Verbose
```

### When Copilot Breaks
```powershell
# Follow the troubleshooting guide
code EQ12_COPILOT_HEALTHCHECK.md

# Or run diagnostics
.\scripts\EQ12_SYSTEM_SCAN.ps1 -IncludeVSCode
# Review REVERSE_REPORT_*.json for Copilot issues
```

---

## 📁 Output Directory Structure

After running the tools, you'll see:

```
C:\EQ12_BROKEN_20251122_210342\
├── reports\
│   ├── SCAN_RESULT_20251122_143000.json       # System inventory
│   └── REVERSE_REPORT_20251122_143015.json    # Issue analysis
├── logs\
│   ├── EQ12_SYSTEM_SCAN_LOG_20251122_143000.txt
│   ├── EQ12_REVERSE_ENGINEER_LOG_20251122_143015.txt
│   └── EQ12_GIT_SAFETY_TOOL_LOG_20251122_150000.txt
└── scripts\
    ├── EQ12_SYSTEM_SCAN.ps1
    ├── EQ12_REVERSE_ENGINEER.ps1
    └── EQ12_GIT_SAFETY_TOOL.ps1
```

---

## 🛡️ Safety Guarantees

All tools follow these principles:

1. **Non-Destructive by Default**
   - Scans never modify files
   - Repairs require explicit confirmation (unless `-Force` used)
   - Dry-run mode available for previews

2. **Comprehensive Logging**
   - All actions logged to `logs/` with UTC timestamps
   - Logs persisted even if scripts fail

3. **Repo-Scoped Only**
   - Tools only operate within `C:\EQ12_BROKEN_20251122_210342`
   - Never touch global Windows settings, registry, or other repos

4. **Git Protection**
   - `.git` directory is read-only
   - Only lock files and read-only flags can be cleared
   - Never deletes Git history or configuration

---

## 🤖 How Copilot Uses These Tools

With `.github/copilot-instructions.md` in place, Copilot now:

1. **Understands Context**
   - Knows repo root is `C:\EQ12_BROKEN_20251122_210342`
   - Recognizes EQ12-specific file patterns
   - Follows AGENTS.md coding standards

2. **Suggests Repairs Automatically**
   - When you report errors, Copilot may suggest running these scripts
   - Offers to create new diagnostic tools for new issue classes

3. **Respects Safety Rules**
   - Never suggests destructive operations without confirmation
   - Always proposes a plan before executing

4. **Learns from Conversations**
   - Logs root causes in `reports/` or `docs/`
   - Improves scripts based on recurring issues

---

## 📚 Additional Resources

- **AGENTS.md** - Full agent workflow and coding standards
- **EQ12_COPILOT_HEALTHCHECK.md** - Copilot troubleshooting guide
- **.github/copilot-instructions.md** - Copilot's permanent instructions

---

## 💡 Pro Tips

### Keyboard Shortcuts
Add to `.vscode/keybindings.json`:
```json
[
  {
    "key": "ctrl+shift+alt+s",
    "command": "workbench.action.tasks.runTask",
    "args": "EQ12: Full System Sweep"
  }
]
```

### Monthly Maintenance
Create a calendar reminder to:
1. Run `EQ12: Full System Sweep`
2. Review `REVERSE_REPORT_*.json`
3. Clean up `reports/` older than 30 days
4. Check for VS Code extension updates

### Integration with CI
Add to `.github/workflows/health-check.yml`:
```yaml
- name: EQ12 System Health Check
  run: |
    .\scripts\EQ12_SYSTEM_SCAN.ps1
    $Latest = Get-ChildItem .\reports\SCAN_RESULT_*.json | Sort LastWriteTime -Desc | Select -First 1
    .\scripts\EQ12_REVERSE_ENGINEER.ps1 -ScanFile $Latest.FullName
```

---

**Created:** 2025-11-22  
**Maintainer:** EQ12 System Repair AI  
**Status:** ✅ All tools operational
