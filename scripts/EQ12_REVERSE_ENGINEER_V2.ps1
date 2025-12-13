param(
    [string]$ScanFile
)

Write-Host "=== EQ12 REVERSE ENGINEERING ENGINE (v2) ===" -ForegroundColor Cyan

if (-not $ScanFile -or -not (Test-Path $ScanFile)) {
    Write-Host "❌ You must pass a valid scan JSON file path." -ForegroundColor Red
    Write-Host "   Example:" -ForegroundColor Yellow
    Write-Host "   .\EQ12_REVERSE_ENGINEER.ps1 -ScanFile 'C:\EQ12\SCAN_RESULT_20251122_210000.json'" -ForegroundColor Yellow
    exit 1
}

try {
    $Data = Get-Content $ScanFile -Raw | ConvertFrom-Json
} catch {
    Write-Host "❌ Failed to parse JSON: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# --------------------------------------------------------------------
# COLLECT PROBLEMS + SUGGESTIONS
# --------------------------------------------------------------------
$Problems    = New-Object System.Collections.Generic.List[string]
$Suggestions = New-Object System.Collections.Generic.List[string]

function Add-Problem {
    param(
        [string]$Message,
        [string]$Suggestion
    )
    if ($Message) {
        $Problems.Add($Message)
    }
    if ($Suggestion -and -not $Suggestions.Contains($Suggestion)) {
        $Suggestions.Add($Suggestion)
    }
}

# --------------------------------------------------------------------
# FLATTEN ALL FILES FROM SCAN
# --------------------------------------------------------------------
$allFiles = @()
foreach ($section in $Data) {
    if ($section.Files) {
        $allFiles += $section.Files
    }
}

# Helper: quick filter
function Find-Paths {
    param(
        [string]$Pattern
    )
    return $allFiles | Where-Object { $_.FullName -like $Pattern }
}

function Find-Match {
    param(
        [string]$Regex
    )
    return $allFiles | Where-Object { $_.FullName -match $Regex }
}

# ====================================================================
# CHECK 1 — Copilot / Copilot Chat health
# ====================================================================
$copilotExt     = Find-Match "\.vscode\\extensions\\github\.copilot-"
$copilotChatExt = Find-Match "\.vscode\\extensions\\github\.copilot-chat-"
$tikWorker      = Find-Match "tikTokenizerWorker\.js$"

if (-not $copilotExt) {
    Add-Problem "❌ GitHub Copilot extension not detected in VS Code extensions." `
        "Install 'GitHub Copilot' from the VS Code Extensions panel, then reload VS Code."
}

if (-not $copilotChatExt) {
    Add-Problem "❌ GitHub Copilot Chat extension not detected in VS Code extensions." `
        "Install 'GitHub Copilot Chat' from the VS Code Extensions panel, then reload VS Code."
} else {
    if (-not $tikWorker) {
        Add-Problem "⚠️ Copilot Chat extension found, but tikTokenizerWorker.js not seen in scan. Remote (WSL/DevContainer) Copilot Chat may be corrupted." `
            "From Windows: close VS Code, delete ~/.vscode-server inside WSL (wsl -e bash -lc 'rm -rf ~/.vscode-server') and remove any github.copilot-chat* folders under C:\Users\$env:USERNAME\.vscode\extensions, then reopen VS Code and let it reinstall the remote server + Copilot Chat."
    }
}

# ====================================================================
# CHECK 2 — Pylance / Python tooling
# ====================================================================
$pylanceExt = Find-Match "\.vscode\\extensions\\ms-python\.vscode-pylance"
$pythonExt  = Find-Match "\.vscode\\extensions\\ms-python\.python"

if (-not $pylanceExt) {
    Add-Problem "❌ Pylance (ms-python.vscode-pylance) extension not detected." `
        "Open VS Code → Extensions → install 'Pylance' (ms-python.vscode-pylance) and reload the window."
}

if (-not $pythonExt) {
    Add-Problem "⚠️ Python extension (ms-python.python) not detected in extensions scan." `
        "Install the official 'Python' extension (ms-python.python) in VS Code for best language support."
}

# Check for .venv / site-packages as sign of working Python env
$pythonEnvFiles = $allFiles | Where-Object {
    $_.FullName -match "\.venv\\" -or $_.FullName -match "site-packages"
}

if (-not $pythonEnvFiles -or $pythonEnvFiles.Count -eq 0) {
    Add-Problem "⚠️ No Python virtual environment (.venv / site-packages) detected in scanned paths." `
        "Create a venv inside your workspace:  python -m venv .venv  then activate it and install dependencies with:  .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt"
}

# ====================================================================
# CHECK 3 — Workspace .vscode/settings.json
# ====================================================================
$settingsFiles = Find-Paths "*\.vscode\settings.json"

if (-not $settingsFiles -or $settingsFiles.Count -eq 0) {
    Add-Problem "⚠️ No workspace .vscode/settings.json found. VS Code is likely using global defaults." `
        "Create C:\EQ12\.vscode\settings.json and define stable settings for Python, Pylance, Copilot, and formatting. Keep project-specific config in the workspace."
}

# ====================================================================
# CHECK 4 — Git lock files / unlink risk
# ====================================================================
$gitLockFiles = Find-Paths "*\.git\*.lock"

foreach ($lf in $gitLockFiles) {
    Add-Problem "⚠️ Git lock file present (can cause 'unlink' and 'file in use' errors): $($lf.FullName)" `
        "Close VS Code and terminals in this repo, then from elevated PowerShell run: attrib -r C:\EQ12 /S /D; Remove-Item -LiteralPath '$($lf.FullName)' -Force"
}

# ====================================================================
# CHECK 5 — NSIS / installer crumbs
# ====================================================================
$tempNsis = $allFiles | Where-Object {
    $_.FullName -match "nsis" -or $_.FullName -match "Temp\\ns"
}

if ($tempNsis -and $tempNsis.Count -gt 0) {
    Add-Problem "⚠️ Found NSIS-related TEMP/installer files in scan. These can correlate with 'NSIS Error' installer failures." `
        "Empty TEMP folders (Run:  del /q /s %TEMP%\* ) then re-download installers from the official source and run them again. If NSIS persists, run: DISM /Online /Cleanup-Image /RestoreHealth  and  sfc /scannow  in elevated PowerShell."
}

# ====================================================================
# CHECK 6 — WSL health
# ====================================================================
Write-Host "`n=== WSL HEALTH CHECK ===" -ForegroundColor Yellow

$wslCmd = Get-Command wsl -ErrorAction SilentlyContinue
if (-not $wslCmd) {
    Add-Problem "❌ WSL command not found on this system." `
        "Install 'Windows Subsystem for Linux' (WSL) from Microsoft Store or with:  wsl --install  then reboot."
    Write-Host "  WSL not detected (command not found)." -ForegroundColor Red
} else {
    try {
        $wslStatus = & wsl --status 2>&1
        if ($LASTEXITCODE -ne 0) {
            Add-Problem "⚠️ wsl --status returned a non-zero exit code." `
                "Open PowerShell as Admin and run:  wsl --shutdown  then reopen WSL. If warnings mention .wslconfig keys, remove or fix the invalid entries."
            Write-Host "  wsl --status reported an issue:" -ForegroundColor DarkYellow
            Write-Host "  $wslStatus" -ForegroundColor DarkGray
        } else {
            Write-Host "  WSL is installed and responding to wsl --status." -ForegroundColor Green
        }
    } catch {
        Add-Problem "⚠️ Exception while running wsl --status: $($_.Exception.Message)" `
            "Run wsl --status manually in PowerShell and correct any configuration issues (e.g., invalid .wslconfig keys)."
    }
}

# ====================================================================
# CHECK 7 — Docker health
# ====================================================================
Write-Host "`n=== DOCKER HEALTH CHECK ===" -ForegroundColor Yellow

$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCmd) {
    Add-Problem "❌ Docker CLI not detected in PATH." `
        "Install Docker Desktop for Windows, enable WSL2 integration for your distro, then restart Windows."
    Write-Host "  docker command not found in PATH." -ForegroundColor Red
} else {
    try {
        $dockerInfo = & docker info 2>&1
        if ($LASTEXITCODE -ne 0) {
            Add-Problem "⚠️ 'docker info' returned a non-zero exit code. Docker Engine may not be running." `
                "Start Docker Desktop, wait until it says 'Docker engine running', then run: docker info  again. If it still fails, open Docker Desktop → Troubleshoot."
            Write-Host "  docker info reported a problem:" -ForegroundColor DarkYellow
            Write-Host "  $dockerInfo" -ForegroundColor DarkGray
        } else {
            Write-Host "  Docker Engine responded successfully to docker info." -ForegroundColor Green
        }
    } catch {
        Add-Problem "⚠️ Exception while running docker info: $($_.Exception.Message)" `
            "Ensure Docker Desktop is installed and running, then retry: docker info"
    }
}

# ====================================================================
# SUMMARY: DETECTED PROBLEMS
# ====================================================================
Write-Host "`n=== ANALYSIS REPORT ===" -ForegroundColor Yellow

if ($Problems.Count -eq 0) {
    Write-Host "✅ No major issues detected based on the scan + health checks." -ForegroundColor Green
} else {
    foreach ($p in $Problems) {
        Write-Host $p -ForegroundColor Red
    }
}

# ====================================================================
# REPAIR SUGGESTIONS — CONCRETE COMMANDS TO RUN
# ====================================================================
Write-Host "`n=== REPAIR SUGGESTIONS (NEXT COMMANDS TO RUN) ===" -ForegroundColor Yellow

if ($Suggestions.Count -eq 0) {
    Write-Host "✅ No specific repairs suggested. System appears healthy." -ForegroundColor Green
} else {
    $i = 1
    foreach ($s in $Suggestions) {
        Write-Host (" {0}. {1}" -f $i, $s) -ForegroundColor Cyan
        $i++
    }
}

Write-Host "`n✔ Reverse engineering + health checks complete." -ForegroundColor Green
