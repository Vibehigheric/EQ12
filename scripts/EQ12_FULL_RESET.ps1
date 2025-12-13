# =====================================================================
# EQ12 FULL RESET – GODMODE CLEAN REBUILD
# =====================================================================
# This script performs a complete teardown and rebuild of the EQ12 environment
# to eliminate all accumulated corruption and start fresh.
#
# What it does:
#   1. Verifies Administrator privileges
#   2. Stops all locking processes (VS Code, Git, Python, etc.)
#   3. Removes broken repository
#   4. Creates clean C:\EQ12 directory
#   5. Clones fresh repository from GitHub
#   6. Fixes Python environment and pip dependencies
#   7. Creates new .venv with clean dependencies
#   8. Resets VS Code extensions and WSL remote server
#   9. Writes safe workspace settings
#
# CRITICAL: This script is DESTRUCTIVE. It will delete C:\EQ12 and C:\EQ12_BROKEN_20251122_210342.
# Make sure you have committed and pushed any important work before running.
#
# Usage:
#   Run as Administrator:
#   powershell -ExecutionPolicy Bypass -File "C:\EQ12_BROKEN_20251122_210342\scripts\EQ12_FULL_RESET.ps1"
#
# =====================================================================

[CmdletBinding()]
param(
    [switch]$Force
)

Write-Host "`n=== EQ12 FULL RESET – GODMODE CLEAN REBUILD ===" -ForegroundColor Cyan
Write-Host "This script will perform a COMPLETE rebuild of your EQ12 environment." -ForegroundColor Yellow
Write-Host ""

# ------------------------------------------------------------
# SAFETY CHECK
# ------------------------------------------------------------
if (-not $Force) {
    Write-Host "⚠️ WARNING: This script will:" -ForegroundColor Red
    Write-Host "   - Delete C:\EQ12_BROKEN_20251122_210342" -ForegroundColor DarkYellow
    Write-Host "   - Delete C:\EQ12 (if exists)" -ForegroundColor DarkYellow
    Write-Host "   - Stop all VS Code, Git, Python processes" -ForegroundColor DarkYellow
    Write-Host "   - Reset VS Code extensions" -ForegroundColor DarkYellow
    Write-Host "   - Reset WSL .vscode-server" -ForegroundColor DarkYellow
    Write-Host "   - Clone fresh repository from GitHub" -ForegroundColor DarkYellow
    Write-Host ""
    Write-Host "Make sure you have committed and pushed all important work!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run with -Force to proceed:" -ForegroundColor Cyan
    Write-Host "   .\EQ12_FULL_RESET.ps1 -Force" -ForegroundColor White
    exit 0
}

Write-Host "✔ Running in FORCE mode. Beginning reset..." -ForegroundColor Green
Write-Host ""

# ------------------------------------------------------------
# 1. Verify Admin
# ------------------------------------------------------------
Write-Host "[1/9] Checking Administrator rights..." -ForegroundColor Yellow
$IsAdmin = ([Security.Principal.WindowsPrincipal]
    [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $IsAdmin) {
    Write-Host "  ❌ Not running as Administrator. Restart PowerShell as Admin." -ForegroundColor Red
    Write-Host "     Right-click PowerShell → Run as Administrator" -ForegroundColor Cyan
    exit 1
} else {
    Write-Host "  ✔ Running as Administrator" -ForegroundColor Green
}

# ------------------------------------------------------------
# 2. Kill processes that lock EQ12
# ------------------------------------------------------------
Write-Host "`n[2/9] Stopping locking processes..." -ForegroundColor Yellow

$procs = "Code","code","CodeHelper","git","node","python","SearchIndexer","ms-python-tools-service"
$killedCount = 0
foreach ($p in $procs) {
    $process = Get-Process -Name $p -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Name $p -Force -ErrorAction SilentlyContinue
        $killedCount++
    }
}

Write-Host "  ✔ Stopped $killedCount process(es)" -ForegroundColor Green

# Give processes time to release file handles
Start-Sleep -Seconds 3

# ------------------------------------------------------------
# 3. Delete broken repo safely
# ------------------------------------------------------------
$Broken = "C:\EQ12_BROKEN_20251122_210342"
if (Test-Path $Broken) {
    Write-Host "`n[3/9] Removing broken repository..." -ForegroundColor Yellow
    
    # Remove read-only attributes
    & attrib -r "$Broken\*" /S /D 2>$null
    
    # Take ownership
    & takeown /F $Broken /R /D Y 2>&1 | Out-Null
    
    # Grant full permissions
    & icacls $Broken /grant "${env:USERNAME}:(F)" /T 2>&1 | Out-Null
    
    # Remove the directory
    Remove-Item -Path $Broken -Recurse -Force -ErrorAction SilentlyContinue
    
    if (Test-Path $Broken) {
        Write-Host "  ⚠️ Failed to remove broken repo. Manual cleanup required." -ForegroundColor Red
        Write-Host "     Try running: Remove-Item -Path '$Broken' -Recurse -Force" -ForegroundColor Cyan
        exit 1
    }
    
    Write-Host "  ✔ Broken repo removed" -ForegroundColor Green
} else {
    Write-Host "`n[3/9] No broken repo found at $Broken" -ForegroundColor DarkGray
}

# ------------------------------------------------------------
# 4. Recreate EQ12 folder
# ------------------------------------------------------------
Write-Host "`n[4/9] Creating clean EQ12 folder..." -ForegroundColor Yellow

if (Test-Path "C:\EQ12") {
    Write-Host "  Removing existing C:\EQ12..." -ForegroundColor DarkGray
    & attrib -r "C:\EQ12\*" /S /D 2>$null
    Remove-Item -Path "C:\EQ12" -Recurse -Force -ErrorAction SilentlyContinue
}

New-Item -ItemType Directory -Path "C:\EQ12" -Force | Out-Null

Write-Host "  ✔ C:\EQ12 ready" -ForegroundColor Green

# ------------------------------------------------------------
# 5. Clone the fresh repo
# ------------------------------------------------------------
Write-Host "`n[5/9] Cloning EQ12 repository..." -ForegroundColor Yellow

$RepoURL = "https://github.com/vibehigheric/edgegod-parlay.git"

# Verify git is available
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Write-Host "  ❌ Git not found in PATH. Install Git for Windows first." -ForegroundColor Red
    Write-Host "     Download from: https://git-scm.com/download/win" -ForegroundColor Cyan
    exit 1
}

# Clone the repository
Set-Location "C:\"
$cloneResult = & git clone $RepoURL "C:\EQ12" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Git clone failed. Check your network connection and GitHub access." -ForegroundColor Red
    Write-Host "     Error: $cloneResult" -ForegroundColor DarkGray
    exit 1
}

Write-Host "  ✔ Repository cloned successfully" -ForegroundColor Green

# ------------------------------------------------------------
# 6. Reset Python + Fix Dependencies
# ------------------------------------------------------------
Write-Host "`n[6/9] Rebuilding Python environment..." -ForegroundColor Yellow

# Check for Python 3.12
$pythonCmd = Get-Command py -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "  ⚠️ Python launcher 'py' not found. Trying 'python'..." -ForegroundColor DarkYellow
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        Write-Host "  ❌ Python not found. Install Python 3.12 first." -ForegroundColor Red
        Write-Host "     Download from: https://www.python.org/downloads/" -ForegroundColor Cyan
        exit 1
    }
    $pythonExe = "python"
} else {
    $pythonExe = "py"
    # Try to use Python 3.12 specifically
    $pythonVersion = & py -3.12 --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $pythonExe = "py -3.12"
        Write-Host "  Using Python 3.12" -ForegroundColor DarkGreen
    }
}

# Upgrade pip
Write-Host "  Upgrading pip..." -ForegroundColor DarkGray
& $pythonExe -m pip install --upgrade pip setuptools wheel --quiet 2>&1 | Out-Null

# Fix known dependency conflicts
Write-Host "  Fixing dependency conflicts..." -ForegroundColor DarkGray
& $pythonExe -m pip uninstall openai orjson -y 2>&1 | Out-Null
& $pythonExe -m pip install "openai<1.100" "orjson>=3.9.10" --quiet 2>&1 | Out-Null

Write-Host "  ✔ Python environment fixed" -ForegroundColor Green

# ------------------------------------------------------------
# 7. Create .venv
# ------------------------------------------------------------
Write-Host "`n[7/9] Creating fresh .venv..." -ForegroundColor Yellow

Set-Location "C:\EQ12"

# Create virtual environment
& $pythonExe -m venv .venv

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "  ❌ Failed to create .venv" -ForegroundColor Red
    exit 1
}

# Activate and install dependencies
$activateScript = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    
    # Upgrade pip in venv
    & .\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
    
    # Install requirements if they exist
    if (Test-Path "requirements.txt") {
        Write-Host "  Installing requirements.txt..." -ForegroundColor DarkGray
        & .\.venv\Scripts\pip.exe install -r requirements.txt --quiet
    }
    
    if (Test-Path "pyproject.toml") {
        Write-Host "  Installing from pyproject.toml..." -ForegroundColor DarkGray
        & .\.venv\Scripts\pip.exe install -e . --quiet
    }
}

Write-Host "  ✔ Virtual environment installed" -ForegroundColor Green

# ------------------------------------------------------------
# 8. Reset VS Code environment
# ------------------------------------------------------------
Write-Host "`n[8/9] Resetting VS Code extensions & remote server..." -ForegroundColor Yellow

# Clean WSL remote server
$wslCmd = Get-Command wsl -ErrorAction SilentlyContinue
if ($wslCmd) {
    Write-Host "  Cleaning WSL .vscode-server..." -ForegroundColor DarkGray
    & wsl --shutdown 2>&1 | Out-Null
    Start-Sleep -Seconds 2
    & wsl -e bash -lc "rm -rf ~/.vscode-server" 2>&1 | Out-Null
}

# Clean corrupted Copilot Chat extensions (but keep the extensions themselves)
$copilotChatExtensions = Get-ChildItem -Path "$env:USERPROFILE\.vscode\extensions" -Filter "github.copilot-chat*" -ErrorAction SilentlyContinue
foreach ($ext in $copilotChatExtensions) {
    $tikWorker = Get-ChildItem -Path $ext.FullName -Recurse -Filter "tikTokenizerWorker.js" -ErrorAction SilentlyContinue
    if ($tikWorker -and $tikWorker.Length -lt 1024) {
        Write-Host "  Removing corrupted Copilot Chat extension: $($ext.Name)" -ForegroundColor DarkGray
        Remove-Item -Path $ext.FullName -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "  ✔ VS Code environment reset" -ForegroundColor Green

# ------------------------------------------------------------
# 9. Write safe workspace settings
# ------------------------------------------------------------
Write-Host "`n[9/9] Writing safe .vscode/settings.json..." -ForegroundColor Yellow

$SettingsPath = "C:\EQ12\.vscode"
New-Item -ItemType Directory -Path $SettingsPath -Force | Out-Null

$SettingsContent = @"
{
  "python.defaultInterpreterPath": "`${workspaceFolder}/.venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,
  "python.analysis.indexing": true,
  "python.analysis.autoImportCompletions": true,
  "python.analysis.typeCheckingMode": "basic",
  
  "editor.formatOnSave": true,
  "editor.formatOnPaste": false,
  "editor.defaultFormatter": "ms-python.black-formatter",
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  
  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/.git/subtree-cache/**": true,
    "**/node_modules/**": true,
    "**/.venv/**": true,
    "**/__pycache__/**": true,
    "**/.pytest_cache/**": true,
    "**/.ruff_cache/**": true,
    "**/dist/**": true,
    "**/build/**": true,
    "**/.vscode-server/**": true,
    "**/logs/**": true,
    "**/reports/**": true
  },
  
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.ruff_cache": true,
    "**/*.pyc": true
  },
  
  "search.exclude": {
    "**/.git": true,
    "**/.venv": true,
    "**/node_modules": true,
    "**/dist": true,
    "**/build": true,
    "**/logs": true,
    "**/reports": true
  },
  
  "git.enabled": true,
  "git.autorefresh": true,
  "git.autofetch": false,
  "git.ignoreLimitWarning": true,
  
  "github.copilot.enable": {
    "*": true,
    "python": true,
    "markdown": true
  },
  
  "extensions.autoUpdate": false,
  "telemetry.telemetryLevel": "off",
  "window.restoreWindows": "none"
}
"@

$SettingsContent | Set-Content -Encoding UTF8 -Path "$SettingsPath\settings.json"

Write-Host "  ✔ Workspace settings created" -ForegroundColor Green

# ------------------------------------------------------------
# DONE
# ------------------------------------------------------------
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host " EQ12 FULL RESET COMPLETE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

Write-Host "`n✅ NEXT STEPS:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Open VS Code fresh (close all windows first)" -ForegroundColor White
Write-Host ""
Write-Host "2. Install ONLY these 4 extensions:" -ForegroundColor White
Write-Host "   - Python (ms-python.python)" -ForegroundColor Cyan
Write-Host "   - Pylance (ms-python.vscode-pylance)" -ForegroundColor Cyan
Write-Host "   - GitHub Copilot (github.copilot)" -ForegroundColor Cyan
Write-Host "   - GitHub Copilot Chat (github.copilot-chat)" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Open the folder: C:\EQ12" -ForegroundColor White
Write-Host ""
Write-Host "4. Select Python interpreter: .venv\Scripts\python.exe" -ForegroundColor White
Write-Host "   (Ctrl+Shift+P → Python: Select Interpreter)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "5. Verify Copilot Chat works without errors" -ForegroundColor White
Write-Host ""
Write-Host "6. Run post-reset checklist:" -ForegroundColor White
Write-Host "   .\scripts\EQ12_POST_RESET_CHECKLIST.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "✔ Everything should work cleanly now." -ForegroundColor Green
Write-Host ""
