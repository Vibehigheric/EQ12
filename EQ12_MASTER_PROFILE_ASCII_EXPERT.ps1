# ===================================================================
# EQ12 Master Profile — ASC II Expert Edition
# ===================================================================
# Automation & Systems Control Level II — Complete Command Suite
# Version: 2.0.0
# Last Updated: 2025-11-27
# ===================================================================

Write-Host ""
Write-Host "===== EQ12 Master Profile Loaded =====" -ForegroundColor Cyan
Write-Host ""

# ===================================================================
# SECTION 1: Core System Commands
# ===================================================================

function run-odds {
    <#
    .SYNOPSIS
        Fetch live odds from The Odds API
    .DESCRIPTION
        Retrieves current betting lines for all active sports
    #>
    python "C:\EQ12_BROKEN_20251122_210342\scripts\eq12_all_sports_fetcher.py"
}

function run-parlay {
    <#
    .SYNOPSIS
        Generate optimized parlay combinations
    .DESCRIPTION
        Runs parlay builder with EV+ filtering and correlation analysis
    #>
    python "C:\EQ12_BROKEN_20251122_210342\eq12_comprehensive_parlays.py"
}

function eq12-recycle {
    <#
    .SYNOPSIS
        Clean temp files and refresh system
    .DESCRIPTION
        Removes __pycache__, .pytest_cache, temp logs
    #>
    & "C:\EQ12_BROKEN_20251122_210342\scripts\eq12_recycle.ps1"
}

function eq12-report {
    <#
    .SYNOPSIS
        Generate system health report
    .DESCRIPTION
        Outputs JSON report with Docker, Redis, Prometheus status
    #>
    python "C:\EQ12_BROKEN_20251122_210342\eq12_system_health.py"
}

function eq12-launcher {
    <#
    .SYNOPSIS
        Open EQ12 Command Center dashboard
    .DESCRIPTION
        Launches VB.NET master UI (WinForms/WPF)
    #>
    Start-Process "C:\EQ12_BROKEN_20251122_210342\vbnet_projects\EQ12.CommandCenter\bin\Debug\EQ12.CommandCenter.exe"
}

function eq12-build-dashboard {
    <#
    .SYNOPSIS
        Build and launch web dashboard
    .DESCRIPTION
        Starts Node.js dashboard server on port 3000
    #>
    & "C:\EQ12_BROKEN_20251122_210342\eq12-build-dashboard.ps1"
}

# ===================================================================
# SECTION 2: Sports Betting & Analytics
# ===================================================================

function eq12-all-sports {
    <#
    .SYNOPSIS
        Fetch odds for ALL sports (NBA, NFL, MLB, NHL, NCAAF, NCAAB)
    .DESCRIPTION
        Comprehensive multi-sport odds aggregation
    #>
    python "C:\EQ12_BROKEN_20251122_210342\eq12_ultimate_5sport_integration.py"
}

function eq12-live-odds {
    <#
    .SYNOPSIS
        Real-time odds streaming
    .DESCRIPTION
        Continuous monitoring with auto-refresh every 60 seconds
    #>
    python "C:\EQ12_BROKEN_20251122_210342\eq12_live_parlay_scanner.py"
}

function eq12-weather {
    <#
    .SYNOPSIS
        Stadium weather conditions
    .DESCRIPTION
        OpenWeather API integration for outdoor games
    #>
    python "C:\EQ12_BROKEN_20251122_210342\eq12_enhanced_stadium_weather_system.py"
}

function eq12-injuries {
    <#
    .SYNOPSIS
        Injury report aggregator
    .DESCRIPTION
        Scrapes official team injury reports and lineup changes
    #>
    python "C:\EQ12_BROKEN_20251122_210342\eq12_lineup_watcher.py"
}

# ===================================================================
# SECTION 3: System Monitoring & Logs
# ===================================================================

function eq12-logs {
    <#
    .SYNOPSIS
        Tail live logs
    .DESCRIPTION
        Opens logs directory and tails most recent file
    #>
    $latestLog = Get-ChildItem "C:\EQ12_BROKEN_20251122_210342\logs\" -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    Get-Content $latestLog.FullName -Tail 50 -Wait
}

function eq12-status {
    <#
    .SYNOPSIS
        Full system status check
    .DESCRIPTION
        Docker, VPN, Redis, Prometheus, API keys validation
    #>
    & "C:\EQ12_BROKEN_20251122_210342\scripts\eq12_enhanced_status_check.ps1"
}

function eq12-backup {
    <#
    .SYNOPSIS
        Create encrypted system backup
    .DESCRIPTION
        AES-256 encrypted archive of configs, keys, scripts
    #>
    python "C:\EQ12_BROKEN_20251122_210342\eq12_resilience_core.py" --backup
}

function eq12-clean {
    <#
    .SYNOPSIS
        Deep clean temp files
    .DESCRIPTION
        Removes all __pycache__, .pytest_cache, .ruff_cache, logs older than 30 days
    #>
    python "C:\EQ12_BROKEN_20251122_210342\eq12_cleanup.py"
}

function eq12-test {
    <#
    .SYNOPSIS
        Run full test suite
    .DESCRIPTION
        Executes pytest + Pester tests with coverage
    #>
    & "C:\EQ12_BROKEN_20251122_210342\Run-EQ12TestsOptimized.ps1"
}

function eq12-go-check {
    <#
    .SYNOPSIS
        Pre-flight checklist
    .DESCRIPTION
        Validates all APIs, credentials, services before go-live
    #>
    python "C:\EQ12_BROKEN_20251122_210342\eq12_comprehensive_validation.py"
}

# ===================================================================
# SECTION 4: Data Management
# ===================================================================

function eq12-api-test {
    <#
    .SYNOPSIS
        Test all API endpoints
    .DESCRIPTION
        Validates Odds API, OpenAI, Telegram, GitHub tokens
    #>
    python "C:\EQ12_BROKEN_20251122_210342\validate_api_keys.py"
}

function eq12-db-check {
    <#
    .SYNOPSIS
        Database health check
    .DESCRIPTION
        Verifies SQLite databases (eq12_bets.db, dashboard.db, etc.)
    #>
    python "C:\EQ12_BROKEN_20251122_210342\check_db.py"
}

function eq12-refresh-data {
    <#
    .SYNOPSIS
        Refresh all cached data
    .DESCRIPTION
        Clears cache and re-fetches odds, weather, injury data
    #>
    Remove-Item "C:\EQ12_BROKEN_20251122_210342\cache\*" -Recurse -Force -ErrorAction SilentlyContinue
    eq12-all-sports
}

function eq12-export {
    <#
    .SYNOPSIS
        Export data to CSV/JSON
    .DESCRIPTION
        Generates snapshot files for analysis
    #>
    python "C:\EQ12_BROKEN_20251122_210342\eq12_export_all_data.py"
}

# ===================================================================
# SECTION 5: Utilities & Helpers
# ===================================================================

function eq12-config {
    <#
    .SYNOPSIS
        Edit .env configuration
    .DESCRIPTION
        Opens .env in VS Code
    #>
    code "C:\EQ12_BROKEN_20251122_210342\.env"
}

function eq12-help {
    <#
    .SYNOPSIS
        Show all EQ12 commands
    .DESCRIPTION
        Displays command reference with descriptions
    #>
    Get-Command -Name "eq12-*" | Format-Table Name, @{Label = "Description"; Expression = { (Get-Help $_.Name).Synopsis } }
}

function eq12-update {
    <#
    .SYNOPSIS
        Update EQ12 system
    .DESCRIPTION
        Git pull latest changes and reinstall dependencies
    #>
    Set-Location "C:\EQ12_BROKEN_20251122_210342"
    git pull origin main
    pip install -r requirements.txt --upgrade
}

function eq12-monitor {
    <#
    .SYNOPSIS
        Resource monitor dashboard
    .DESCRIPTION
        Real-time CPU, RAM, disk usage
    #>
    python "C:\EQ12_BROKEN_20251122_210342\eq12_resource_monitor_wrapper.py"
}

function eq12-usb {
    <#
    .SYNOPSIS
        USB device scanner
    .DESCRIPTION
        Detects connected USB devices (for Raspberry Pi, Coral TPU, etc.)
    #>
    Get-PnpDevice | Where-Object { $_.Class -eq "USB" } | Format-Table FriendlyName, Status
}

# ===================================================================
# SECTION 6: VB.NET Module Launchers (ASC II Expert)
# ===================================================================

function eq12-core-test {
    <#
    .SYNOPSIS
        Test EQ12.Core credential manager
    .DESCRIPTION
        Validates .env loading and API key retrieval
    #>
    & "C:\EQ12_BROKEN_20251122_210342\vbnet_projects\EQ12.Core\bin\Debug\EQ12.Core.exe"
}

function eq12-security-check {
    <#
    .SYNOPSIS
        Run EQ12.Security VPN monitor
    .DESCRIPTION
        Checks VPN status and auto-reconnects if needed
    #>
    & "C:\EQ12_BROKEN_20251122_210342\vbnet_projects\EQ12.Security\bin\Debug\EQ12.Security.exe"
}

function eq12-telegram-send {
    <#
    .SYNOPSIS
        Send Telegram alert
    .DESCRIPTION
        Quick message send via VB.NET Telegram bot
    .PARAMETER Message
        Alert message to send
    #>
    param([Parameter(Mandatory = $true)][string]$Message)
    & "C:\EQ12_BROKEN_20251122_210342\vbnet_projects\EQ12.TelegramBot\bin\Debug\EQ12.TelegramBot.exe" "send" $Message
}

function eq12-ai-diagnose {
    <#
    .SYNOPSIS
        AI-powered diagnostics
    .DESCRIPTION
        Use GPT-5 to diagnose VFD faults or system errors
    .PARAMETER FaultCode
        Fault code to diagnose (e.g., "STO W8114")
    #>
    param([Parameter(Mandatory = $true)][string]$FaultCode)
    & "C:\EQ12_BROKEN_20251122_210342\vbnet_projects\EQ12.Diagnostics\bin\Debug\EQ12.Diagnostics.exe" "diagnose" $FaultCode
}

function eq12-github-release {
    <#
    .SYNOPSIS
        Create GitHub release
    .DESCRIPTION
        Automated release via VB.NET GitHub API wrapper
    .PARAMETER Tag
        Version tag (e.g., "v1.2.3")
    .PARAMETER Body
        Release notes
    #>
    param(
        [Parameter(Mandatory = $true)][string]$Tag,
        [Parameter(Mandatory = $true)][string]$Body
    )
    & "C:\EQ12_BROKEN_20251122_210342\vbnet_projects\EQ12.CI\bin\Debug\EQ12.CI.exe" "release" $Tag $Body
}

function eq12-dashboard {
    <#
    .SYNOPSIS
        Launch ASC II Expert Command Center
    .DESCRIPTION
        Opens VB.NET master UI with all modules
    #>
    Start-Process "C:\EQ12_BROKEN_20251122_210342\vbnet_projects\EQ12.CommandCenter\bin\Debug\EQ12.CommandCenter.exe"
}

# ===================================================================
# SECTION 7: Docker & Container Management
# ===================================================================

function eq12-docker-start {
    <#
    .SYNOPSIS
        Start all EQ12 Docker containers
    .DESCRIPTION
        docker-compose up -d for godstack, redis, grafana, prometheus, jupyter
    #>
    Set-Location "C:\EQ12_BROKEN_20251122_210342"
    docker-compose up -d
}

function eq12-docker-stop {
    <#
    .SYNOPSIS
        Stop all EQ12 Docker containers
    #>
    Set-Location "C:\EQ12_BROKEN_20251122_210342"
    docker-compose down
}

function eq12-docker-logs {
    <#
    .SYNOPSIS
        View Docker container logs
    .PARAMETER Container
        Container name (godstack, redis, grafana, prometheus, jupyter)
    #>
    param([Parameter(Mandatory = $false)][string]$Container = "godstack")
    docker logs -f $Container
}

function eq12-docker-restart {
    <#
    .SYNOPSIS
        Restart specific Docker container
    .PARAMETER Container
        Container name to restart
    #>
    param([Parameter(Mandatory = $true)][string]$Container)
    docker restart $Container
}

# ===================================================================
# SECTION 8: Jupyter & NBA Analysis (from previous session)
# ===================================================================

function eq12-jupyter-start {
    <#
    .SYNOPSIS
        Start JupyterLab for NBA analysis
    .DESCRIPTION
        Launches eq12-jupyter-dataviz container on port 8889
    #>
    & "C:\EQ12_BROKEN_20251122_210342\scripts\EQ12_LAUNCH_NBA_JUPYTER.ps1"
}

function eq12-nba-master {
    <#
    .SYNOPSIS
        Open NBA master index notebook
    .DESCRIPTION
        Opens NBA_MASTER_INDEX.ipynb in browser
    #>
    Start-Process "http://localhost:8889/lab/tree/notebooks/nba/NBA_MASTER_INDEX.ipynb?token=eq12-dataviz-token"
}

function eq12-nba-utils {
    <#
    .SYNOPSIS
        Test NBA utilities module
    .DESCRIPTION
        Runs Python script to verify nba_utils.py functions
    #>
    python -c "from scripts.nba_utils import *; print('NBA utilities loaded successfully')"
}

# ===================================================================
# SECTION 9: Git & Version Control
# ===================================================================

function eq12-git-status {
    <#
    .SYNOPSIS
        Enhanced git status with branch info
    #>
    Set-Location "C:\EQ12_BROKEN_20251122_210342"
    Write-Host "`nBranch: " -NoNewline -ForegroundColor Yellow
    git branch --show-current
    Write-Host "`nStatus:" -ForegroundColor Yellow
    git status -s
    Write-Host "`nRecent Commits:" -ForegroundColor Yellow
    git log --oneline -5
}

function eq12-git-commit {
    <#
    .SYNOPSIS
        Signed commit with conventional format
    .DESCRIPTION
        GPG-signed commit following COMMIT_CONVENTIONS.md
    .PARAMETER Message
        Commit message (e.g., "feat(betting): add parlay optimizer")
    #>
    param([Parameter(Mandatory = $true)][string]$Message)
    Set-Location "C:\EQ12_BROKEN_20251122_210342"
    git add .
    git commit -S -m $Message
}

function eq12-git-push {
    <#
    .SYNOPSIS
        Push to main branch
    #>
    Set-Location "C:\EQ12_BROKEN_20251122_210342"
    git push origin main
}

# ===================================================================
# SECTION 10: Environment Detection (as requested)
# ===================================================================

function eq12-env-scan {
    <#
    .SYNOPSIS
        Detect and recommend optimal development environment
    .DESCRIPTION
        Scans for .NET SDKs, Visual Studio, Docker, WSL, Python
    #>
    Write-Host "`n[SCAN] EQ12 Environment Detection`n" -ForegroundColor Cyan
    Write-Host "====================================="
    
    # .NET SDKs
    $dotnetVersions = & dotnet --list-sdks 2>$null
    if ($dotnetVersions) {
        Write-Host "`n[OK] Detected .NET SDKs:" -ForegroundColor Green
        $dotnetVersions | ForEach-Object { Write-Host "  - $_" }
    }
    else {
        Write-Host "`n[WARNING] No .NET SDK found. Recommend installing .NET 8.0 SDK." -ForegroundColor Yellow
    }
    
    # Visual Studio
    $vswhere = "$env:ProgramFiles(x86)\Microsoft Visual Studio\Installer\vswhere.exe"
    if (Test-Path $vswhere) {
        Write-Host "`n[OK] Installed Visual Studio Editions:" -ForegroundColor Green
        & $vswhere -all -prerelease -products * -property displayName | ForEach-Object { Write-Host "  - $_" }
    }
    else {
        Write-Host "`n[WARNING] Visual Studio not detected. Recommend VS 2022 Community or higher." -ForegroundColor Yellow
    }
    
    # Docker
    if (Get-Command docker -ErrorAction SilentlyContinue) {
        Write-Host "`n[OK] Docker detected — container build option available." -ForegroundColor Green
        docker --version
    }
    else {
        Write-Host "`n[WARNING] Docker not found. Install Docker Desktop for containerized builds." -ForegroundColor Yellow
    }
    
    # WSL
    $wslList = & wsl --list --verbose 2>$null
    if ($wslList) {
        Write-Host "`n[OK] WSL Environments Detected:" -ForegroundColor Green
        $wslList | ForEach-Object { Write-Host "  $_" }
    }
    else {
        Write-Host "`n[INFO] No WSL distributions found." -ForegroundColor Cyan
    }
    
    # Python
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Host "`n[OK] Python detected:" -ForegroundColor Green
        python --version
    }
    else {
        Write-Host "`n[WARNING] Python not found in PATH." -ForegroundColor Yellow
    }
    
    # Recommendation
    Write-Host "`n[RECOMMEND] Environment Recommendation:" -ForegroundColor Magenta
    if ($dotnetVersions -match "8.0" -and (Test-Path $vswhere)) {
        Write-Host "  Use Visual Studio 2022 with .NET 8.0 SDK for full VB.NET solution development." -ForegroundColor Green
    }
    elseif ($dotnetVersions -match "8.0" -and (Get-Command code -ErrorAction SilentlyContinue)) {
        Write-Host "  Use VS Code + .NET 8 SDK + Dev Containers for modular or remote VB.NET dev." -ForegroundColor Green
    }
    elseif ($wslList) {
        Write-Host "  WSL environment viable for lightweight CLI-based builds." -ForegroundColor Green
    }
    else {
        Write-Host "  Limited environment — install Visual Studio or .NET SDK 8.0." -ForegroundColor Yellow
    }
    
    Write-Host "`n=====================================" -ForegroundColor Cyan
}

# ===================================================================
# SECTION 11: Quick Aliases
# ===================================================================

Set-Alias eq12 eq12-help
Set-Alias odds run-odds
Set-Alias parlay run-parlay
Set-Alias logs eq12-logs
Set-Alias clean eq12-clean
Set-Alias test eq12-test

# ===================================================================
# SECTION 12: Environment Variables Display (Masked)
# ===================================================================

Write-Host "Core: run-odds | run-parlay | eq12-recycle | eq12-report | eq12-launcher | eq12-build-dashboard" -ForegroundColor White
Write-Host "Sports: eq12-all-sports | eq12-live-odds | eq12-weather | eq12-injuries" -ForegroundColor White
Write-Host "System: eq12-logs | eq12-status | eq12-backup | eq12-clean | eq12-test | eq12-go-check" -ForegroundColor White
Write-Host "Data: eq12-api-test | eq12-db-check | eq12-refresh-data | eq12-export" -ForegroundColor White
Write-Host "Utils: eq12-config | eq12-help | eq12-update | eq12-monitor | eq12-usb" -ForegroundColor White
Write-Host ""

# Display loaded API keys (masked for security)
$envKeys = @(
    "CHATGPT_API_KEY",
    "GITHUB_TOKEN",
    "GROQ_API_KEY",
    "ODDS_API_KEY",
    "OPENAI_API_KEY",
    "OPENROUTER_API_KEY",
    "OPENWEATHER_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "THE_ODDS_API_KEY"
)

$envPath = "C:\EQ12_BROKEN_20251122_210342\.env"
if (Test-Path $envPath) {
    $envContent = Get-Content $envPath | Where-Object { $_ -match "^[A-Z_]+=" }
    $loadedKeys = @{}
    
    foreach ($line in $envContent) {
        $parts = $line -split "=", 2
        if ($parts.Length -eq 2) {
            $key = $parts[0].Trim()
            $value = $parts[1].Trim()
            if ($value.Length -gt 10) {
                $masked = $value.Substring(0, 10) + "..."
            }
            else {
                $masked = "***"
            }
            $loadedKeys[$key] = $masked
        }
    }
    
    foreach ($key in $envKeys) {
        if ($loadedKeys.ContainsKey($key)) {
            Write-Host ("{0,-25} {1}" -f $key, $loadedKeys[$key]) -ForegroundColor DarkGray
        }
    }
}

Write-Host ""
Write-Host "[TIP] Run 'eq12-env-scan' to detect your complete development environment" -ForegroundColor Yellow
Write-Host "[TIP] Run 'eq12-help' to see all available commands" -ForegroundColor Yellow
Write-Host ""

# ===================================================================
# Load ChatGPT Integration Commands
# ===================================================================
$chatgptCommands = "$PSScriptRoot\EQ12_CHATGPT_COMMANDS.ps1"
if (Test-Path $chatgptCommands) {
    . $chatgptCommands
}
else {
    Write-Host "⚠️ ChatGPT commands not found at: $chatgptCommands" -ForegroundColor Yellow
}
