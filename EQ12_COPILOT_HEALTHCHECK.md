# EQ12 Copilot Health Check Guide

This document provides step-by-step procedures to diagnose and repair GitHub Copilot and Copilot Chat extension issues in the EQ12 workspace.

---

## Table of Contents

1. [Common Symptoms](#common-symptoms)
2. [Diagnostic Procedures](#diagnostic-procedures)
3. [Repair Procedures](#repair-procedures)
4. [Prevention & Maintenance](#prevention--maintenance)

---

## Common Symptoms

### Copilot Not Working
- ✗ Copilot icon shows but no suggestions appear
- ✗ "Copilot not available" or "Service unavailable" errors
- ✗ Chat panel opens but shows errors or blank content
- ✗ Extensions listed but show "(Disabled)" or warning icons

### Extension Corruption Indicators
- ✗ `tikTokenizerWorker.js` missing or < 1KB in size
- ✗ Extension folders in `.vscode\extensions` incomplete
- ✗ Multiple versions of the same extension installed
- ✗ Extension crashes or hangs VS Code on startup

### WSL-Specific Issues
- ✗ Copilot works on Windows but not in WSL Remote
- ✗ "Module not found" errors in WSL environment
- ✗ `.vscode-server` folder corrupted or incomplete

---

## Diagnostic Procedures

### 1. Check Extension Status

**PowerShell:**
```powershell
# List installed Copilot extensions
$ExtDir = "$env:USERPROFILE\.vscode\extensions"
Get-ChildItem -Path $ExtDir -Directory | Where-Object { $_.Name -match "copilot" }

# Check for tiny tikTokenizerWorker.js files
Get-ChildItem -Path $ExtDir -Recurse -Filter "tikTokenizerWorker.js" | 
    Select-Object FullName, Length |
    Where-Object { $_.Length -lt 1000 }
```

**VS Code Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type: `Extensions: Show Installed Extensions`
3. Search for: `copilot`
4. Check status indicators

### 2. Check Extension Logs

**View Copilot Logs:**
1. `Ctrl+Shift+P` → `Developer: Show Logs`
2. Select `Extension Host`
3. Filter for `copilot` or error messages

**View Output Panel:**
1. `View` → `Output` (or `Ctrl+Shift+U`)
2. Dropdown: Select `GitHub Copilot`
3. Look for error messages or stack traces

### 3. Run EQ12 System Scan

Use the EQ12 diagnostic tools to detect corruption:

```powershell
# Run full system scan
cd C:\EQ12_BROKEN_20251122_210342
.\scripts\EQ12_SYSTEM_SCAN.ps1 -IncludeVSCode

# Analyze results
$ScanFile = Get-ChildItem .\reports\SCAN_RESULT_*.json | Sort-Object LastWriteTime -Descending | Select-Object -First 1
.\scripts\EQ12_REVERSE_ENGINEER.ps1 -ScanFile $ScanFile.FullName
```

Check the `REVERSE_REPORT_*.json` for Copilot-related issues.

---

## Repair Procedures

### Procedure A: Reinstall Copilot Extensions (Clean)

**Step 1: Uninstall Current Extensions**

```powershell
# PowerShell - Uninstall Copilot extensions
code --uninstall-extension GitHub.copilot
code --uninstall-extension GitHub.copilot-chat

# Verify removal
code --list-extensions | Select-String "copilot"
```

**Step 2: Clean Extension Folders**

```powershell
# Manually remove extension folders
$ExtDir = "$env:USERPROFILE\.vscode\extensions"
Get-ChildItem -Path $ExtDir -Directory | 
    Where-Object { $_.Name -match "github\.copilot" } |
    Remove-Item -Recurse -Force

# Verify cleanup
Get-ChildItem -Path $ExtDir -Directory | Where-Object { $_.Name -match "copilot" }
```

**Step 3: Reinstall Extensions**

```powershell
# Reinstall from marketplace
code --install-extension GitHub.copilot
code --install-extension GitHub.copilot-chat

# OR: Use VS Code UI
# Ctrl+Shift+X → Search "GitHub Copilot" → Install
```

**Step 4: Restart VS Code**

Close ALL VS Code windows and reopen to initialize extensions.

---

### Procedure B: Repair Corrupted tikTokenizerWorker.js

**Identify Corrupted File:**

```powershell
$ExtDir = "$env:USERPROFILE\.vscode\extensions"
$CorruptedFiles = Get-ChildItem -Path $ExtDir -Recurse -Filter "tikTokenizerWorker.js" |
    Where-Object { $_.Length -lt 1000 } |
    Select-Object FullName, Length

$CorruptedFiles | Format-Table -AutoSize
```

**Option 1: Reinstall Specific Extension Version**

```powershell
# Find current version
$CopilotDir = Get-ChildItem -Path $ExtDir -Directory | 
    Where-Object { $_.Name -match "github\.copilot-chat" } |
    Select-Object -First 1

Write-Host "Current version: $($CopilotDir.Name)"

# Uninstall
code --uninstall-extension GitHub.copilot-chat

# Remove folder
Remove-Item -Path $CopilotDir.FullName -Recurse -Force

# Reinstall latest
code --install-extension GitHub.copilot-chat
```

**Option 2: Manual File Replacement (Advanced)**

⚠️ **Not recommended** - prefer full reinstall. Only if desperate:

1. Download matching extension version `.vsix` from marketplace
2. Extract `.vsix` (it's a ZIP file)
3. Locate `dist/tikTokenizerWorker.js` in extracted files
4. Copy to corrupted extension's `dist/` folder
5. Restart VS Code

---

### Procedure C: Clean WSL Remote Extension Cache

For WSL-specific Copilot issues:

**Step 1: Remove WSL Server Cache**

In **WSL terminal**:
```bash
# Remove VS Code server cache
rm -rf ~/.vscode-server/extensions/github.copilot*
rm -rf ~/.vscode-server/extensions/github.copilot-chat*

# Optional: Full server reset (will reinstall all extensions)
# rm -rf ~/.vscode-server
```

**Step 2: Reconnect to WSL**

1. Close VS Code
2. Reopen and connect to WSL: `Ctrl+Shift+P` → `WSL: Connect to WSL`
3. Wait for extensions to reinstall automatically
4. Check Copilot status

---

### Procedure D: Clear Extension Storage/Cache

**Clear Global Storage:**

```powershell
# Clear Copilot storage data
$StorageDir = "$env:APPDATA\Code\User\globalStorage\github.copilot"
if (Test-Path $StorageDir) {
    Remove-Item -Path $StorageDir -Recurse -Force
    Write-Host "Cleared Copilot global storage"
}

$ChatStorageDir = "$env:APPDATA\Code\User\globalStorage\github.copilot-chat"
if (Test-Path $ChatStorageDir) {
    Remove-Item -Path $ChatStorageDir -Recurse -Force
    Write-Host "Cleared Copilot Chat global storage"
}
```

**Clear Workspace Storage:**

```powershell
$WorkspaceStorageDir = "$env:APPDATA\Code\User\workspaceStorage"
# Manually inspect and remove suspicious workspace caches
explorer $WorkspaceStorageDir
```

Restart VS Code after clearing storage.

---

### Procedure E: Verify Authentication

**Check Copilot Account Status:**

1. `Ctrl+Shift+P` → `GitHub Copilot: Sign In`
2. Verify your GitHub account is shown
3. Check subscription status at: https://github.com/settings/copilot

**Re-authenticate:**

```powershell
# Sign out and back in
# In VS Code Command Palette:
# 1. "GitHub Copilot: Sign Out"
# 2. "GitHub Copilot: Sign In"
```

---

## Prevention & Maintenance

### Regular Health Checks

**Monthly Maintenance Script:**

```powershell
# Save as: scripts\EQ12_COPILOT_MAINTENANCE.ps1

[CmdletBinding()]
param()

Write-Host "===== EQ12 Copilot Monthly Maintenance ====="

# 1. List current versions
Write-Host "`n1. Current Copilot Extensions:"
code --list-extensions --show-versions | Select-String "copilot"

# 2. Check for updates
Write-Host "`n2. Checking for updates..."
code --list-extensions --show-versions | Select-String "copilot" | ForEach-Object {
    Write-Host "  $_"
}

# 3. Verify critical files
Write-Host "`n3. Verifying tikTokenizerWorker.js integrity..."
$ExtDir = "$env:USERPROFILE\.vscode\extensions"
$Workers = Get-ChildItem -Path $ExtDir -Recurse -Filter "tikTokenizerWorker.js" -ErrorAction SilentlyContinue

foreach ($Worker in $Workers) {
    $SizeKB = [math]::Round($Worker.Length / 1KB, 2)
    $Status = if ($Worker.Length -lt 1000) { "⚠️ CORRUPT" } else { "✓ OK" }
    Write-Host "  $Status - $SizeKB KB - $($Worker.FullName)"
}

# 4. Check storage size
Write-Host "`n4. Storage usage:"
$GlobalStorage = "$env:APPDATA\Code\User\globalStorage"
if (Test-Path $GlobalStorage) {
    $CopilotStorage = Get-ChildItem -Path $GlobalStorage -Directory | 
        Where-Object { $_.Name -match "copilot" }
    foreach ($Dir in $CopilotStorage) {
        $Size = (Get-ChildItem -Path $Dir.FullName -Recurse -File -ErrorAction SilentlyContinue |
            Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "  $($Dir.Name): $([math]::Round($Size, 2)) MB"
    }
}

Write-Host "`n===== Maintenance Complete ====="
```

### Best Practices

1. **Keep Extensions Updated**
   - Enable auto-update in VS Code settings
   - Check for updates monthly: `Ctrl+Shift+P` → `Extensions: Check for Extension Updates`

2. **Monitor Extension Size**
   - Run `EQ12_SYSTEM_SCAN.ps1 -IncludeVSCode` monthly
   - Alert on tikTokenizerWorker.js < 1KB

3. **Backup Settings**
   - Export settings: `Ctrl+Shift+P` → `Settings: Export Settings`
   - Store in repo: `.vscode/settings.json.backup`

4. **Clean Workspace Storage**
   - Quarterly cleanup of `$env:APPDATA\Code\User\workspaceStorage`
   - Remove old workspace caches for deleted projects

5. **Use Settings Sync**
   - Enable: `Ctrl+Shift+P` → `Settings Sync: Turn On`
   - Ensures consistent config across machines/WSL

---

## Troubleshooting Decision Tree

```
Copilot not working?
│
├─ Is extension installed?
│  ├─ No  → Install via Extensions panel (Ctrl+Shift+X)
│  └─ Yes → Continue
│
├─ Check Output panel for errors
│  ├─ "Module not found" → Run Procedure C (WSL) or Procedure A (Windows)
│  ├─ "Authentication failed" → Run Procedure E
│  └─ Other errors → Continue
│
├─ Run diagnostic scan
│  └─ .\scripts\EQ12_SYSTEM_SCAN.ps1 -IncludeVSCode
│     └─ .\scripts\EQ12_REVERSE_ENGINEER.ps1 -ScanFile <scan_file>
│
├─ Found corrupted tikTokenizerWorker.js?
│  ├─ Yes → Run Procedure B
│  └─ No  → Continue
│
├─ Multiple extension versions?
│  ├─ Yes → Run Procedure A (clean reinstall)
│  └─ No  → Continue
│
└─ Still broken?
   └─ Run Procedure D (clear cache) + Procedure A (reinstall)
```

---

## Quick Reference Commands

```powershell
# List installed Copilot extensions
code --list-extensions | Select-String "copilot"

# Uninstall all Copilot extensions
code --uninstall-extension GitHub.copilot
code --uninstall-extension GitHub.copilot-chat

# Reinstall
code --install-extension GitHub.copilot
code --install-extension GitHub.copilot-chat

# Find corrupted worker files
$ExtDir = "$env:USERPROFILE\.vscode\extensions"
Get-ChildItem -Path $ExtDir -Recurse -Filter "tikTokenizerWorker.js" |
    Where-Object { $_.Length -lt 1000 } |
    Select-Object FullName, Length

# Clear Copilot storage
Remove-Item -Path "$env:APPDATA\Code\User\globalStorage\github.copilot*" -Recurse -Force

# Run EQ12 diagnostics
.\scripts\EQ12_SYSTEM_SCAN.ps1 -IncludeVSCode
.\scripts\EQ12_REVERSE_ENGINEER.ps1 -ScanFile .\reports\SCAN_RESULT_*.json
```

---

## Support Resources

- **GitHub Copilot Docs:** https://docs.github.com/copilot
- **VS Code Extension Docs:** https://code.visualstudio.com/docs/editor/extension-marketplace
- **EQ12 Issue Tracker:** File issues in this repo's GitHub Issues
- **Extension Logs:** `Ctrl+Shift+P` → `Developer: Show Logs` → `Extension Host`

---

**Last Updated:** 2025-11-22  
**Maintainer:** EQ12 System Repair AI
