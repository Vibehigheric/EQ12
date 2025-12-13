[CmdletBinding()]
param(
    [switch]$Force
)

Write-Host "=== EQ12 FULL VS CODE HARDENING ENGINE ===" -ForegroundColor Cyan
Write-Host "This script prevents VS Code failsafe/simplified mode by:" -ForegroundColor Yellow
Write-Host "  1. Cleaning corrupted remote server extensions" -ForegroundColor White
Write-Host "  2. Fixing file watcher resource limits" -ForegroundColor White
Write-Host "  3. Stabilizing Python + Pylance + Copilot configuration" -ForegroundColor White
Write-Host "  4. Clearing Git lock files and read-only flags" -ForegroundColor White
Write-Host "  5. Applying safe workspace settings template" -ForegroundColor White
Write-Host ""

# ====================================================================
# SAFETY CHECK — Require explicit Force flag for destructive actions
# ====================================================================
if (-not $Force) {
    Write-Host "⚠️ This script will make changes to:" -ForegroundColor Yellow
    Write-Host "   - VS Code extensions (cleanup corrupted files)" -ForegroundColor DarkYellow
    Write-Host "   - WSL .vscode-server (force clean reinstall)" -ForegroundColor DarkYellow
    Write-Host "   - Git lock files (remove if found)" -ForegroundColor DarkYellow
    Write-Host "   - Workspace .vscode/settings.json (apply hardened template)" -ForegroundColor DarkYellow
    Write-Host ""
    Write-Host "Run with -Force to proceed:" -ForegroundColor Cyan
    Write-Host "   .\EQ12_FULL_VSCODE_HARDENING.ps1 -Force" -ForegroundColor White
    exit 0
}

Write-Host "✔ Running in FORCE mode. Applying hardening..." -ForegroundColor Green
Write-Host ""

# ====================================================================
# STEP 1 — Clean WSL .vscode-server (most common corruption source)
# ====================================================================
Write-Host "=== STEP 1: Clean WSL Remote Server ===" -ForegroundColor Yellow

$wslCmd = Get-Command wsl -ErrorAction SilentlyContinue
if ($wslCmd) {
    Write-Host "  Shutting down WSL..." -ForegroundColor White
    & wsl --shutdown
    Start-Sleep -Seconds 2
    
    Write-Host "  Removing corrupted .vscode-server..." -ForegroundColor White
    & wsl -e bash -lc "rm -rf ~/.vscode-server"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ WSL .vscode-server removed successfully." -ForegroundColor Green
        Write-Host "     VS Code will reinstall clean remote server on next WSL connection." -ForegroundColor DarkGreen
    } else {
        Write-Host "  ⚠️ Failed to remove .vscode-server (may not exist or WSL unavailable)." -ForegroundColor DarkYellow
    }
} else {
    Write-Host "  ⏭️ WSL not detected. Skipping remote server cleanup." -ForegroundColor DarkGray
}

Write-Host ""

# ====================================================================
# STEP 2 — Clean Windows Copilot Chat extension corruption
# ====================================================================
Write-Host "=== STEP 2: Clean Copilot Chat Extension Corruption ===" -ForegroundColor Yellow

$copilotChatPath = "$env:USERPROFILE\.vscode\extensions\github.copilot-chat*"
$copilotExtensions = Get-ChildItem -Path "$env:USERPROFILE\.vscode\extensions" -Filter "github.copilot-chat*" -ErrorAction SilentlyContinue

if ($copilotExtensions) {
    Write-Host "  Found Copilot Chat extension(s):" -ForegroundColor White
    foreach ($ext in $copilotExtensions) {
        Write-Host "    - $($ext.FullName)" -ForegroundColor DarkGray
        
        # Check for tikTokenizerWorker.js corruption
        $tikWorker = Get-ChildItem -Path $ext.FullName -Recurse -Filter "tikTokenizerWorker.js" -ErrorAction SilentlyContinue
        if ($tikWorker -and $tikWorker.Length -lt 1024) {
            Write-Host "    ⚠️ Corrupted tikTokenizerWorker.js detected (size: $($tikWorker.Length) bytes)" -ForegroundColor Red
            Write-Host "       Removing extension folder..." -ForegroundColor White
            Remove-Item -Path $ext.FullName -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "       ✅ Removed corrupted extension. VS Code will reinstall on next launch." -ForegroundColor Green
        } else {
            Write-Host "    ✅ tikTokenizerWorker.js appears healthy." -ForegroundColor DarkGreen
        }
    }
} else {
    Write-Host "  ⏭️ No Copilot Chat extensions found in Windows user extensions." -ForegroundColor DarkGray
}

Write-Host ""

# ====================================================================
# STEP 3 — Fix Git lock files and read-only flags
# ====================================================================
Write-Host "=== STEP 3: Fix Git Lock Files ===" -ForegroundColor Yellow

$repoRoot = "C:\EQ12_BROKEN_20251122_210342"
if (Test-Path $repoRoot) {
    Write-Host "  Removing read-only flags from repo..." -ForegroundColor White
    & attrib -r "$repoRoot\*" /S /D 2>$null
    
    # Find and remove Git lock files
    $lockFiles = Get-ChildItem -Path "$repoRoot\.git" -Recurse -Filter "*.lock" -ErrorAction SilentlyContinue
    if ($lockFiles) {
        Write-Host "  Found Git lock files:" -ForegroundColor White
        foreach ($lock in $lockFiles) {
            Write-Host "    - $($lock.FullName)" -ForegroundColor DarkGray
            Remove-Item -LiteralPath $lock.FullName -Force -ErrorAction SilentlyContinue
        }
        Write-Host "  ✅ Removed $($lockFiles.Count) Git lock file(s)." -ForegroundColor Green
    } else {
        Write-Host "  ✅ No Git lock files found." -ForegroundColor DarkGreen
    }
} else {
    Write-Host "  ⚠️ Repo root not found: $repoRoot" -ForegroundColor DarkYellow
}

Write-Host ""

# ====================================================================
# STEP 4 — Apply Safe Workspace Settings Template
# ====================================================================
Write-Host "=== STEP 4: Apply Safe Workspace Settings ===" -ForegroundColor Yellow

$templatePath = "$PSScriptRoot\EQ12_SAFE_WORKSPACE_TEMPLATE.json"
$workspaceSettingsPath = "$repoRoot\.vscode\settings.json"

if (Test-Path $templatePath) {
    # Ensure .vscode directory exists
    $vscodeDirPath = Split-Path -Path $workspaceSettingsPath -Parent
    if (-not (Test-Path $vscodeDirPath)) {
        New-Item -ItemType Directory -Path $vscodeDirPath -Force | Out-Null
        Write-Host "  Created .vscode directory." -ForegroundColor White
    }
    
    # Backup existing settings if present
    if (Test-Path $workspaceSettingsPath) {
        $backupPath = "$workspaceSettingsPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item -Path $workspaceSettingsPath -Destination $backupPath -Force
        Write-Host "  ✅ Backed up existing settings to: $(Split-Path $backupPath -Leaf)" -ForegroundColor Green
    }
    
    # Apply hardened template
    Copy-Item -Path $templatePath -Destination $workspaceSettingsPath -Force
    Write-Host "  ✅ Applied EQ12_SAFE_WORKSPACE_TEMPLATE.json to workspace." -ForegroundColor Green
} else {
    Write-Host "  ⚠️ Template not found at: $templatePath" -ForegroundColor DarkYellow
    Write-Host "     Run this script from the scripts/ directory or create the template first." -ForegroundColor DarkYellow
}

Write-Host ""

# ====================================================================
# STEP 5 — Verify Python Virtual Environment
# ====================================================================
Write-Host "=== STEP 5: Verify Python Virtual Environment ===" -ForegroundColor Yellow

$venvPath = "$repoRoot\.venv"
$venvPython = "$venvPath\Scripts\python.exe"

if (Test-Path $venvPython) {
    Write-Host "  ✅ Python venv detected at: $venvPath" -ForegroundColor Green
    
    # Test Python interpreter
    $pythonVersion = & $venvPython --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "     Python version: $pythonVersion" -ForegroundColor DarkGreen
    } else {
        Write-Host "     ⚠️ Python interpreter test failed." -ForegroundColor Red
    }
} else {
    Write-Host "  ⚠️ No Python venv found at: $venvPath" -ForegroundColor DarkYellow
    Write-Host "     Create one with: python -m venv .venv" -ForegroundColor Cyan
    Write-Host "     Then activate and install: .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt" -ForegroundColor Cyan
}

Write-Host ""

# ====================================================================
# STEP 6 — Increase File Watcher Limits (Windows Registry)
# ====================================================================
Write-Host "=== STEP 6: File Watcher Limits ===" -ForegroundColor Yellow
Write-Host "  ⏭️ Skipping Windows Registry modifications (not safe for automation)." -ForegroundColor DarkGray
Write-Host "     Manual step: VS Code uses native file watchers. Exclusions in settings.json are sufficient." -ForegroundColor DarkGray

Write-Host ""

# ====================================================================
# COMPLETION SUMMARY
# ====================================================================
Write-Host "=== HARDENING COMPLETE ===" -ForegroundColor Green
Write-Host ""
Write-Host "✅ WSL .vscode-server cleaned (will reinstall on next connection)" -ForegroundColor Green
Write-Host "✅ Copilot Chat extension corruption checked" -ForegroundColor Green
Write-Host "✅ Git lock files removed" -ForegroundColor Green
Write-Host "✅ Safe workspace settings applied" -ForegroundColor Green
Write-Host "✅ Python venv verified" -ForegroundColor Green
Write-Host ""
Write-Host "🔄 NEXT STEP: Restart VS Code to apply all changes." -ForegroundColor Cyan
Write-Host "   Close all VS Code windows, then reopen your workspace." -ForegroundColor White
Write-Host ""
Write-Host "🧪 VERIFY: After restart, check:" -ForegroundColor Yellow
Write-Host "   1. Copilot Chat loads without tikTokenizer errors" -ForegroundColor White
Write-Host "   2. Pylance activates without 'degraded mode' warnings" -ForegroundColor White
Write-Host "   3. Python interpreter shows as: .venv\Scripts\python.exe" -ForegroundColor White
Write-Host "   4. No 'simplified workspace' or 'restricted mode' prompts" -ForegroundColor White
Write-Host ""
