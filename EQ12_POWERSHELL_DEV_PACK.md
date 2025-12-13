# EQ12 PowerShell Development Pack — Installation Guide

Complete professional PowerShell development environment for EQ12 workspace.

## ✅ What Was Installed

### 1. VS Code Settings (`.vscode/settings.json`)
- PowerShell 5.1 as default version
- Auto-formatting on save for `.ps1` files
- PSScriptAnalyzer integration
- Proper indentation (4 spaces, no tabs)
- Disabled focus-stealing console behavior

### 2. PSScriptAnalyzer Rules (`.vscode/PSScriptAnalyzerSettings.psd1`)
- **Consistent indentation** (4 spaces)
- **Consistent whitespace** around operators, pipes, braces
- **Correct casing** for cmdlets
- **No aliases** in production scripts
- **Comment-based help** enforcement
- **Open brace on same line** (K&R style)

### 3. Safe Extension List (`.vscode/extensions.json`)
**Recommended (5 extensions):**
- `ms-vscode.PowerShell` — PowerShell language support
- `ms-python.python` — Python support
- `ms-python.vscode-pylance` — Python IntelliSense
- `github.copilot` — AI coding assistant
- `github.copilot-chat` — AI chat interface

**Blocked (26 dangerous extensions):**
- TailwindCSS (tsconfig.json errors)
- Remote WSL (tikTokenizer crashes)
- Docker (scanning crashes)
- Black Formatter (conflicts)
- Jupyter (heap overflow)
- ESLint (scans entire C:\)
- GitLens (performance issues)
- And 19 others...

### 4. Extension Guard Script (`scripts/EQ12_EXTENSION_GUARD.ps1`)
Automated protection system that:
- Scans for dangerous extensions
- Removes crash-causing tools
- Installs only safe versions
- Prevents auto-reinstall
- Generates audit reports

### 5. Debug Configurations (Coming Next)
Pre-configured launch profiles for:
- PowerShell script debugging
- Python debugging with venv
- EQ12 system scripts (SAFE_SCAN, DRIFT_MONITOR, etc.)

---

## 🚀 Quick Start

### Step 1: Close VS Code Completely
```powershell
# Kill all VS Code processes
taskkill /F /IM Code.exe 2>$null
```

### Step 2: Run Extension Guard
```powershell
cd C:\EQ12_BROKEN_20251122_210342\scripts
.\EQ12_EXTENSION_GUARD.ps1
```

**What it does:**
- Detects dangerous extensions
- Asks permission before removing (unless `-Force`)
- Installs missing safe extensions
- Creates audit log

**Options:**
```powershell
# Dry run (preview only)
.\EQ12_EXTENSION_GUARD.ps1 -DryRun

# Auto-confirm (no prompts)
.\EQ12_EXTENSION_GUARD.ps1 -Force
```

### Step 3: Reopen VS Code
```powershell
# Open EQ12 workspace
code C:\EQ12_BROKEN_20251122_210342
```

### Step 4: Verify PowerShell Extension
Open any `.ps1` file (e.g., `scripts/EQ12_SAFE_SCAN.ps1`)

**Check status bar (bottom right):**
```
PowerShell 5.1  |  ✔ PSES Loaded
```

If you see `PowerShell 7.x` instead, that's also fine.

---

## 🧪 Test Your Setup

### Test 1: Auto-Formatting
1. Open `scripts/EQ12_SAFE_SCAN.ps1`
2. Add some messy code:
```powershell
Write-Host"test"| Out-Null
```
3. Save the file (`Ctrl+S`)
4. Auto-formatter should fix it to:
```powershell
Write-Host "test" | Out-Null
```

### Test 2: IntelliSense
1. Create new file: `test.ps1`
2. Type: `Get-Ch`
3. Should show autocomplete with `Get-ChildItem`, `Get-ChocolateyPath`, etc.

### Test 3: PSScriptAnalyzer
1. Create bad code:
```powershell
gci C:\ -Recurse  # Using alias 'gci'
```
2. Should see warning: "Avoid using aliases in scripts"

### Test 4: Debugging
1. Open `scripts/EQ12_SAFE_SCAN.ps1`
2. Set breakpoint (click left margin on line 20)
3. Press `F5` to debug
4. Should stop at breakpoint

---

## 🛡️ Extension Guard Details

### Safe Extensions (Always Keep)
| Extension ID | Purpose | Why Safe |
|--------------|---------|----------|
| `ms-vscode.PowerShell` | PowerShell language support | Official Microsoft, stable |
| `ms-python.python` | Python support | Required for EQ12 scripts |
| `ms-python.vscode-pylance` | Python IntelliSense | Memory-optimized |
| `github.copilot` | AI coding | Required for MCP |
| `github.copilot-chat` | AI chat | Required for MCP |

### Dangerous Extensions (Auto-Removed)
| Extension ID | Reason |
|--------------|--------|
| `ms-vscode-remote.remote-wsl` | Causes tikTokenizer errors, remote crashes |
| `bradlc.vscode-tailwindcss` | Parses all tsconfig.json, crashes on Web3 repos |
| `ms-azuretools.vscode-docker` | Scans entire workspace, memory overflow |
| `ms-python.black-formatter` | Conflicts with Pylance, format-on-save loops |
| `ms-toolsai.jupyter` | Heap overflow on repositories with 1000+ files |
| `dbaeumer.vscode-eslint` | Tries to scan C:\, causes hangs |
| `eamodio.gitlens` | Git blame slows down large repos |

---

## 📋 Troubleshooting

### Issue: "PowerShell extension not found"
**Fix:**
```powershell
.\scripts\EQ12_EXTENSION_GUARD.ps1 -Force
```

### Issue: "PSES failed to load"
**Fix:**
1. Close VS Code
2. Delete extension cache:
```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.vscode\extensions\ms-vscode.powershell-*"
```
3. Reopen VS Code
4. Extension will auto-reinstall

### Issue: "Extension Guard says extensions installed but they're not"
**Fix:**
```powershell
# Manually install
code --install-extension ms-vscode.PowerShell --force
code --install-extension ms-python.python --force
code --install-extension ms-python.vscode-pylance --force
code --install-extension github.copilot --force
code --install-extension github.copilot-chat --force
```

### Issue: "VS Code keeps recommending dangerous extensions"
**Fix:**
Your `.vscode/extensions.json` is now locked to safe extensions only. If VS Code ignores it:
```powershell
# Nuclear option: disable extension recommendations entirely
code --disable-extension-recommendations
```

---

## 🔧 Advanced Configuration

### Enable PowerShell 7 (Optional)
If you have PowerShell 7 installed:

Edit `.vscode/settings.json`:
```json
"powershell.powerShellDefaultVersion": "PowerShell 7"
```

### Disable Telemetry
Add to `.vscode/settings.json`:
```json
"powershell.developer.editorServicesLogLevel": "Warning",
"powershell.integratedConsole.suppressStartupBanner": true
```

### Custom Keyboard Shortcuts
**Run current script:**
- Press `F5` (debug mode)
- Press `Ctrl+F5` (run without debugging)

**Format document:**
- Press `Shift+Alt+F`

**Toggle terminal:**
- Press `` Ctrl+` ``

---

## 📊 Audit Reports

Extension Guard creates JSON reports in:
```
C:\EQ12_BROKEN_20251122_210342\logs\extension_guard_report_YYYYMMDD_HHmmss.json
```

**Report includes:**
- Timestamp
- Removed extensions
- Installed extensions
- Full safe/dangerous lists

**View latest report:**
```powershell
Get-ChildItem C:\EQ12_BROKEN_20251122_210342\logs\extension_guard_*.json |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1 |
  Get-Content |
  ConvertFrom-Json |
  Format-List
```

---

## ✅ Success Criteria

After setup, you should have:

### VS Code
- ✅ PowerShell extension active (status bar shows version)
- ✅ No "simplified workspace" warnings
- ✅ No tikTokenizer errors in Copilot Chat
- ✅ Auto-formatting works on `.ps1` files

### Extensions
- ✅ 5 safe extensions installed
- ✅ 0 dangerous extensions
- ✅ No auto-install prompts for unwanted tools

### Functionality
- ✅ IntelliSense works (type `Get-Ch` and see suggestions)
- ✅ Debugging works (F5 on `.ps1` file)
- ✅ PSScriptAnalyzer shows warnings for bad code
- ✅ Format-on-save fixes indentation/whitespace

---

## 🆘 Emergency Reset

If everything breaks:

```powershell
# 1. Remove all extensions
Remove-Item -Recurse -Force "$env:USERPROFILE\.vscode\extensions\*"

# 2. Clear VS Code cache
Remove-Item -Recurse -Force "$env:APPDATA\Code\Cache"
Remove-Item -Recurse -Force "$env:APPDATA\Code\CachedData"

# 3. Restart VS Code
taskkill /F /IM Code.exe
code C:\EQ12_BROKEN_20251122_210342

# 4. Run Extension Guard
cd C:\EQ12_BROKEN_20251122_210342\scripts
.\EQ12_EXTENSION_GUARD.ps1 -Force
```

---

**Next Step:** Run the Extension Guard to activate your safe environment:
```powershell
.\scripts\EQ12_EXTENSION_GUARD.ps1
```
