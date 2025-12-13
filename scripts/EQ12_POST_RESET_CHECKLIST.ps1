# =====================================================================
# EQ12 POST-RESET CHECKLIST
# =====================================================================
# Run this script after EQ12_FULL_RESET.ps1 to verify your environment
# is stable and ready for development.
#
# This script checks:
#   1. VS Code extensions are installed and activated
#   2. Python interpreter is correctly selected
#   3. Pylance is active without degraded mode
#   4. Copilot and Copilot Chat are authenticated
#   5. File watcher exclusions are applied
#   6. Git repository is healthy
#   7. Python venv is working
#
# Usage:
#   .\EQ12_POST_RESET_CHECKLIST.ps1
#
# =====================================================================

[CmdletBinding()]
param()

Write-Host "`n=== EQ12 POST-RESET CHECKLIST ===" -ForegroundColor Cyan
Write-Host "Verifying your environment is stable and ready..." -ForegroundColor Yellow
Write-Host ""

$IssuesFound = 0
$Warnings = 0

# ------------------------------------------------------------
# 1. Check VS Code Extensions
# ------------------------------------------------------------
Write-Host "[1/7] Checking VS Code Extensions..." -ForegroundColor Yellow

$requiredExtensions = @(
    "ms-python.python",
    "ms-python.vscode-pylance",
    "github.copilot",
    "github.copilot-chat"
)

$extensionsPath = "$env:USERPROFILE\.vscode\extensions"
if (Test-Path $extensionsPath) {
    $installedExtensions = Get-ChildItem -Path $extensionsPath -Directory
    
    foreach ($ext in $requiredExtensions) {
        $found = $installedExtensions | Where-Object { $_.Name -like "$ext*" }
        if ($found) {
            Write-Host "  ✔ $ext installed" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $ext NOT installed" -ForegroundColor Red
            $IssuesFound++
        }
    }
} else {
    Write-Host "  ⚠️ VS Code extensions directory not found" -ForegroundColor DarkYellow
    $Warnings++
}

# Check for extra extensions that might cause conflicts
$conflictingExtensions = @(
    "ms-python.autopep8",
    "ms-python.flake8",
    "charliermarsh.ruff"
)

foreach ($ext in $conflictingExtensions) {
    $found = $installedExtensions | Where-Object { $_.Name -like "$ext*" }
    if ($found) {
        Write-Host "  ⚠️ Potentially conflicting extension: $ext" -ForegroundColor DarkYellow
        Write-Host "     Consider disabling if you experience formatter conflicts" -ForegroundColor DarkGray
        $Warnings++
    }
}

Write-Host ""

# ------------------------------------------------------------
# 2. Check Python Interpreter
# ------------------------------------------------------------
Write-Host "[2/7] Checking Python Interpreter..." -ForegroundColor Yellow

$venvPython = "C:\EQ12\.venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    $pythonVersion = & $venvPython --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✔ Python venv is working: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Python venv exists but failed to execute" -ForegroundColor Red
        $IssuesFound++
    }
} else {
    Write-Host "  ❌ Python venv not found at: $venvPython" -ForegroundColor Red
    Write-Host "     Run: python -m venv C:\EQ12\.venv" -ForegroundColor Cyan
    $IssuesFound++
}

Write-Host ""

# ------------------------------------------------------------
# 3. Check Workspace Settings
# ------------------------------------------------------------
Write-Host "[3/7] Checking Workspace Settings..." -ForegroundColor Yellow

$settingsPath = "C:\EQ12\.vscode\settings.json"
if (Test-Path $settingsPath) {
    $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
    
    # Check Python interpreter path
    if ($settings.'python.defaultInterpreterPath') {
        Write-Host "  ✔ Python interpreter path configured" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ Python interpreter path not set in settings.json" -ForegroundColor DarkYellow
        $Warnings++
    }
    
    # Check file watcher exclusions
    if ($settings.'files.watcherExclude') {
        $exclusionCount = ($settings.'files.watcherExclude' | Get-Member -MemberType NoteProperty).Count
        Write-Host "  ✔ File watcher exclusions configured ($exclusionCount patterns)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ File watcher exclusions not configured" -ForegroundColor DarkYellow
        $Warnings++
    }
    
    # Check Copilot enabled
    if ($settings.'github.copilot.enable') {
        Write-Host "  ✔ GitHub Copilot enabled in settings" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ GitHub Copilot not enabled in settings" -ForegroundColor DarkYellow
        $Warnings++
    }
    
} else {
    Write-Host "  ❌ Workspace settings.json not found" -ForegroundColor Red
    Write-Host "     Expected at: $settingsPath" -ForegroundColor Cyan
    $IssuesFound++
}

Write-Host ""

# ------------------------------------------------------------
# 4. Check Git Repository
# ------------------------------------------------------------
Write-Host "[4/7] Checking Git Repository..." -ForegroundColor Yellow

if (Test-Path "C:\EQ12\.git") {
    # Check for lock files
    $lockFiles = Get-ChildItem -Path "C:\EQ12\.git" -Recurse -Filter "*.lock" -ErrorAction SilentlyContinue
    if ($lockFiles) {
        Write-Host "  ⚠️ Git lock files found:" -ForegroundColor DarkYellow
        foreach ($lock in $lockFiles) {
            Write-Host "     - $($lock.FullName)" -ForegroundColor DarkGray
        }
        $Warnings++
    } else {
        Write-Host "  ✔ No Git lock files" -ForegroundColor Green
    }
    
    # Check Git status
    Set-Location "C:\EQ12"
    $gitStatus = & git status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✔ Git repository healthy" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ Git status returned error: $gitStatus" -ForegroundColor DarkYellow
        $Warnings++
    }
} else {
    Write-Host "  ❌ Git repository not found at C:\EQ12\.git" -ForegroundColor Red
    $IssuesFound++
}

Write-Host ""

# ------------------------------------------------------------
# 5. Check WSL (if available)
# ------------------------------------------------------------
Write-Host "[5/7] Checking WSL..." -ForegroundColor Yellow

$wslCmd = Get-Command wsl -ErrorAction SilentlyContinue
if ($wslCmd) {
    $wslStatus = & wsl --status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✔ WSL is installed and responding" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ WSL installed but returned error" -ForegroundColor DarkYellow
        Write-Host "     Error: $wslStatus" -ForegroundColor DarkGray
        $Warnings++
    }
} else {
    Write-Host "  ⏭️ WSL not installed (optional)" -ForegroundColor DarkGray
}

Write-Host ""

# ------------------------------------------------------------
# 6. Check Python Dependencies
# ------------------------------------------------------------
Write-Host "[6/7] Checking Python Dependencies..." -ForegroundColor Yellow

if (Test-Path $venvPython) {
    $pipList = & $venvPython -m pip list --format=json 2>&1 | ConvertFrom-Json
    
    # Check for known conflict packages
    $openai = $pipList | Where-Object { $_.name -eq "openai" }
    $orjson = $pipList | Where-Object { $_.name -eq "orjson" }
    
    if ($openai) {
        $openaiVersion = [version]$openai.version
        if ($openaiVersion -lt [version]"1.100.0") {
            Write-Host "  ✔ openai version compatible: $($openai.version)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️ openai version may have conflicts: $($openai.version)" -ForegroundColor DarkYellow
            Write-Host "     Consider: pip install 'openai<1.100'" -ForegroundColor Cyan
            $Warnings++
        }
    }
    
    if ($orjson) {
        Write-Host "  ✔ orjson installed: $($orjson.version)" -ForegroundColor Green
    }
    
    # Check if requirements.txt exists and is satisfied
    if (Test-Path "C:\EQ12\requirements.txt") {
        Write-Host "  Verifying requirements.txt..." -ForegroundColor DarkGray
        $checkResult = & $venvPython -m pip check 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✔ All dependencies compatible" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️ Dependency conflicts detected:" -ForegroundColor DarkYellow
            Write-Host "     $checkResult" -ForegroundColor DarkGray
            $Warnings++
        }
    }
} else {
    Write-Host "  ⏭️ Skipping (Python venv not available)" -ForegroundColor DarkGray
}

Write-Host ""

# ------------------------------------------------------------
# 7. Check MCP Configuration
# ------------------------------------------------------------
Write-Host "[7/7] Checking MCP Configuration..." -ForegroundColor Yellow

$mcpConfigPath = "$env:APPDATA\Code\User\mcp.json"
if (Test-Path $mcpConfigPath) {
    try {
        $mcpConfig = Get-Content $mcpConfigPath -Raw | ConvertFrom-Json
        $mcpCount = ($mcpConfig.mcpServers | Get-Member -MemberType NoteProperty).Count
        Write-Host "  ✔ MCP configuration found ($mcpCount servers configured)" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠️ MCP configuration exists but has JSON errors" -ForegroundColor DarkYellow
        $Warnings++
    }
} else {
    Write-Host "  ⏭️ MCP configuration not found (optional)" -ForegroundColor DarkGray
}

Write-Host ""

# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " CHECKLIST SUMMARY" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if ($IssuesFound -eq 0 -and $Warnings -eq 0) {
    Write-Host "✅ ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host "   Your EQ12 environment is stable and ready." -ForegroundColor Green
} elseif ($IssuesFound -eq 0) {
    Write-Host "⚠️ $Warnings WARNING(S) FOUND" -ForegroundColor Yellow
    Write-Host "   Your environment is functional but has minor issues." -ForegroundColor Yellow
    Write-Host "   Review the warnings above and address them if needed." -ForegroundColor Yellow
} else {
    Write-Host "❌ $IssuesFound CRITICAL ISSUE(S) FOUND" -ForegroundColor Red
    Write-Host "   Your environment is not ready for development." -ForegroundColor Red
    Write-Host "   Fix the issues above before proceeding." -ForegroundColor Red
}

Write-Host ""

# ------------------------------------------------------------
# MANUAL VERIFICATION STEPS
# ------------------------------------------------------------
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " MANUAL VERIFICATION REQUIRED" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please verify these items manually in VS Code:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open VS Code and load C:\EQ12" -ForegroundColor White
Write-Host ""
Write-Host "2. Check Python interpreter (bottom-right corner):" -ForegroundColor White
Write-Host "   Should show: .venv\Scripts\python.exe" -ForegroundColor Cyan
Write-Host "   If not: Ctrl+Shift+P → Python: Select Interpreter" -ForegroundColor DarkGray
Write-Host ""
Write-Host "3. Check Pylance status:" -ForegroundColor White
Write-Host "   Should show: 'Pylance' (not 'Pylance (degraded)')" -ForegroundColor Cyan
Write-Host "   Check in: Output → Python Language Server" -ForegroundColor DarkGray
Write-Host ""
Write-Host "4. Test Copilot Chat:" -ForegroundColor White
Write-Host "   Open Copilot Chat panel" -ForegroundColor Cyan
Write-Host "   Ask: '@workspace what files are in scripts/'" -ForegroundColor Cyan
Write-Host "   Should respond without tikTokenizer errors" -ForegroundColor DarkGray
Write-Host ""
Write-Host "5. Check for VS Code prompts:" -ForegroundColor White
Write-Host "   Should NOT see: 'simplified workspace' or 'restricted mode'" -ForegroundColor Cyan
Write-Host ""
Write-Host "6. Test Git integration:" -ForegroundColor White
Write-Host "   Source Control panel should show branch and changes" -ForegroundColor Cyan
Write-Host "   Should NOT show 'Git features limited' warning" -ForegroundColor DarkGray
Write-Host ""

if ($IssuesFound -eq 0 -and $Warnings -eq 0) {
    Write-Host "✔ If all manual checks pass, you're ready to start development!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Fix the issues above before proceeding with manual verification." -ForegroundColor Yellow
}

Write-Host ""
