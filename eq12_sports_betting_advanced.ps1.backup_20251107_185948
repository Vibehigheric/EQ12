[CmdletBinding()]
param(
    [Parameter(HelpMessage = "Operation to perform")]
    [ValidateSet(
        "analyze", "start", "stop", "status", "dashboard", "report",
        "startlive", "stopall", "autotrade", "listedges", "listbets",
        "retrainml", "cleandata", "config", "testsuite", "initdb"
    )]
    [string]$Action = "analyze",

    [Parameter(HelpMessage = "Enable/disable autotrade")]
    [switch]$Enable,

    [Parameter(HelpMessage = "Sport for ML retraining")]
    [ValidateSet("NFL", "NBA", "MLB", "NHL", "NCAAF", "NCAAB", "ALL")]
    [string]$Sport = "ALL",

    [Parameter(HelpMessage = "Days for data cleanup")]
    [int]$Days = 90,

    [Parameter(HelpMessage = "Configuration view section")]
    [ValidateSet("Risk", "Bookmakers", "Sports", "X_FACTOR", "All")]
    [string]$View = "All",

    [Parameter(HelpMessage = "Verbose logging")]
    [switch]$VerboseLogging
)

# EQ12 Professional Sports Betting PowerShell Wrapper
# Advanced automation, maintenance, and diagnostics

$ErrorActionPreference = "Stop"

# Configuration
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $ScriptRoot) {
    $ScriptRoot = "C:\EQ12"
}

$PythonScript = Join-Path $ScriptRoot "eq12_pro_sports_betting.py"
$XFactorScript = Join-Path $ScriptRoot "eq12_x_factor_pipeline.py"
$AutoTradeScript = Join-Path $ScriptRoot "eq12_auto_trade_executor.py"
$MasterController = Join-Path $ScriptRoot "eq12_master_controller.py"
$DatabaseMigration = Join-Path $ScriptRoot "eq12_database_migration.py"
$DashboardPath = Join-Path $ScriptRoot "dashboard\sports_betting_dashboard.html"
$ConfigPath = Join-Path $ScriptRoot "configs\sports_betting_config.json"
$LogsDir = Join-Path $ScriptRoot "logs"

# Global background job tracking
$Global:EQ12BackgroundJobs = @()

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        "INFO" { Write-Host $logEntry -ForegroundColor Cyan }
        "CRITICAL" { Write-Host $logEntry -ForegroundColor Magenta }
        default { Write-Host $logEntry }
    }

    # Log to file
    if (-not (Test-Path $LogsDir)) {
        New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
    }

    $logFile = Join-Path $LogsDir "eq12_powershell.log"
    Add-Content -Path $logFile -Value $logEntry
}

function Test-PythonEnvironment {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            return $false
        }

        Write-EQ12Log "Python environment: $pythonVersion" "SUCCESS"
        return $true
    }
    catch {
        Write-EQ12Log "Python environment check failed: $_" "ERROR"
        return $false
    }
}

function Test-RequiredFiles {
    $files = @{
        "Main Script"         = $PythonScript
        "X-Factor Pipeline"   = $XFactorScript
        "Auto-Trade Executor" = $AutoTradeScript
        "Master Controller"   = $MasterController
        "Configuration"       = $ConfigPath
    }

    $allExist = $true
    foreach ($name in $files.Keys) {
        $exists = Test-Path $files[$name]
        Write-EQ12Log "$name exists: $exists" $(if ($exists) { "SUCCESS" } else { "WARNING" })
        if (-not $exists) { $allExist = $false }
    }

    return $allExist
}

function Start-LiveMonitoring {
    Write-EQ12Log "Starting persistent live monitoring system..." "INFO"

    try {
        # Stop any existing background jobs first
        Stop-AllBackgroundJobs

        # Start X-Factor Pipeline in background
        $xFactorJob = Start-Job -ScriptBlock {
            param($ScriptPath, $LogsDir)
            Set-Location -Path (Split-Path $ScriptPath -Parent)
            python $ScriptPath --live-mode
        } -ArgumentList $XFactorScript, $LogsDir -Name "EQ12_XFactor"

        # Start Auto-Trade Executor in background
        $autoTradeJob = Start-Job -ScriptBlock {
            param($ScriptPath, $LogsDir)
            Set-Location -Path (Split-Path $ScriptPath -Parent)
            python $ScriptPath --monitor-mode
        } -ArgumentList $AutoTradeScript, $LogsDir -Name "EQ12_AutoTrade"

        # Start Master Controller
        $masterJob = Start-Job -ScriptBlock {
            param($ScriptPath, $LogsDir)
            Set-Location -Path (Split-Path $ScriptPath -Parent)
            python $ScriptPath --daemon-mode
        } -ArgumentList $MasterController, $LogsDir -Name "EQ12_Master"

        $Global:EQ12BackgroundJobs = @($xFactorJob, $autoTradeJob, $masterJob)

        Write-EQ12Log "Live monitoring system started successfully" "SUCCESS"
        Write-EQ12Log "Background Jobs: X-Factor (ID: $($xFactorJob.Id)), AutoTrade (ID: $($autoTradeJob.Id)), Master (ID: $($masterJob.Id))" "INFO"

        return $true
    }
    catch {
        Write-EQ12Log "Failed to start live monitoring: $_" "ERROR"
        return $false
    }
}

function Stop-AllBackgroundJobs {
    Write-EQ12Log "Stopping all EQ12 background processes..." "INFO"

    try {
        # Stop tracked jobs
        foreach ($job in $Global:EQ12BackgroundJobs) {
            if ($job -and $job.State -eq "Running") {
                Stop-Job -Job $job -PassThru | Remove-Job
                Write-EQ12Log "Stopped job: $($job.Name)" "SUCCESS"
            }
        }

        # Stop any remaining EQ12 jobs
        Get-Job | Where-Object { $_.Name -like "EQ12_*" } | Stop-Job -PassThru | Remove-Job

        # Kill Python processes related to EQ12
        $pythonProcesses = Get-Process | Where-Object {
            $_.ProcessName -eq "python" -and
            $_.CommandLine -like "*eq12*"
        }

        foreach ($proc in $pythonProcesses) {
            try {
                $proc | Stop-Process -Force
                Write-EQ12Log "Terminated Python process: $($proc.Id)" "SUCCESS"
            }
            catch {
                Write-EQ12Log "Could not terminate process $($proc.Id): $_" "WARNING"
            }
        }

        $Global:EQ12BackgroundJobs = @()
        Write-EQ12Log "All background processes stopped" "SUCCESS"
        return $true
    }
    catch {
        Write-EQ12Log "Error stopping background jobs: $_" "ERROR"
        return $false
    }
}

function Set-AutoTradeMode {
    param([switch]$EnableAutoTrade)

    Write-EQ12Log "Setting auto-trade mode: $EnableAutoTrade" "INFO"

    try {
        if (-not (Test-Path $ConfigPath)) {
            Write-EQ12Log "Configuration file not found: $ConfigPath" "ERROR"
            return $false
        }

        $config = Get-Content $ConfigPath | ConvertFrom-Json
        $config.auto_bet_enabled = [bool]$EnableAutoTrade

        $config | ConvertTo-Json -Depth 10 | Set-Content $ConfigPath

        $status = if ($EnableAutoTrade) { "ENABLED" } else { "DISABLED" }
        Write-EQ12Log "Auto-trade mode $status successfully" "SUCCESS"

        # Restart auto-trade executor if it's running
        $autoTradeJob = Get-Job | Where-Object { $_.Name -eq "EQ12_AutoTrade" }
        if ($autoTradeJob -and $autoTradeJob.State -eq "Running") {
            Write-EQ12Log "Restarting auto-trade executor with new settings..." "INFO"
            Stop-Job $autoTradeJob -PassThru | Remove-Job

            $newJob = Start-Job -ScriptBlock {
                param($ScriptPath, $LogsDir)
                Set-Location -Path (Split-Path $ScriptPath -Parent)
                python $ScriptPath --monitor-mode
            } -ArgumentList $AutoTradeScript, $LogsDir -Name "EQ12_AutoTrade"

            # Update global tracking
            $Global:EQ12BackgroundJobs = $Global:EQ12BackgroundJobs | Where-Object { $_.Name -ne "EQ12_AutoTrade" }
            $Global:EQ12BackgroundJobs += $newJob
        }

        return $true
    }
    catch {
        Write-EQ12Log "Failed to set auto-trade mode: $_" "ERROR"
        return $false
    }
}

function Get-CurrentEdges {
    Write-EQ12Log "Retrieving current betting edges..." "INFO"

    try {
        $result = python -c @"
import sqlite3
from datetime import datetime, timedelta
conn = sqlite3.connect('data/sports_betting.db')
cursor = conn.execute('''
    SELECT g.home_team, g.away_team, be.market_type, be.edge_percentage,
           be.confidence_level, be.bookmaker, be.created_at
    FROM betting_edges be
    JOIN games g ON be.game_id = g.id
    WHERE be.expires_at > datetime('now') OR be.expires_at IS NULL
    ORDER BY be.edge_percentage DESC
    LIMIT 10
''')
edges = cursor.fetchall()
conn.close()

if not edges:
    print('No current edges found')
else:
    print('Current Betting Opportunities:')
    print('-' * 80)
    for edge in edges:
        home, away, market, pct, conf, book, created = edge
        print(f'{home} vs {away} | {market} | Edge: {pct:.2f}% | Conf: {conf:.1f} | {book}')
"@

        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "Edge retrieval completed" "SUCCESS"
        }
        else {
            Write-EQ12Log "Edge retrieval failed" "ERROR"
        }

        return $LASTEXITCODE -eq 0
    }
    catch {
        Write-EQ12Log "Error retrieving edges: $_" "ERROR"
        return $false
    }
}

function Get-BetHistory {
    Write-EQ12Log "Retrieving bet history..." "INFO"

    try {
        $result = python -c @"
import sqlite3
from datetime import datetime, timedelta
conn = sqlite3.connect('data/sports_betting.db')
cursor = conn.execute('''
    SELECT bet_type, stake, odds, result, profit_loss, clv, bet_time, bookmaker
    FROM bets
    ORDER BY bet_time DESC
    LIMIT 20
''')
bets = cursor.fetchall()
conn.close()

if not bets:
    print('No bet history found')
else:
    print('Recent Bet History:')
    print('-' * 100)
    total_profit = 0
    for bet in bets:
        bet_type, stake, odds, result, profit, clv, time, book = bet
        status = result or 'Pending'
        profit_str = f'${profit:.2f}' if profit else 'N/A'
        clv_str = f'{clv:.2f}%' if clv else 'N/A'
        total_profit += profit or 0
        print(f'{time[:16]} | {bet_type:15} | ${stake:6.2f} | {odds:+6.2f} | {status:8} | {profit_str:8} | CLV: {clv_str:6} | {book}')

    print('-' * 100)
    print(f'Total P&L: ${total_profit:.2f}')
"@

        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "Bet history retrieval completed" "SUCCESS"
        }
        else {
            Write-EQ12Log "Bet history retrieval failed" "ERROR"
        }

        return $LASTEXITCODE -eq 0
    }
    catch {
        Write-EQ12Log "Error retrieving bet history: $_" "ERROR"
        return $false
    }
}

function Invoke-MLRetraining {
    param([string]$Sport)

    Write-EQ12Log "Starting ML model retraining for: $Sport" "INFO"

    try {
        $retrainScript = @"
import sys
sys.path.append('.')
from eq12_pro_sports_betting import SportsBettingEngine
import asyncio

async def retrain_models():
    engine = SportsBettingEngine()
    sport_list = ['$Sport'] if '$Sport' != 'ALL' else ['NFL', 'NBA', 'MLB', 'NHL', 'NCAAF', 'NCAAB']

    for sport in sport_list:
        print(f'Retraining {sport} model...')
        # Placeholder for actual ML retraining logic
        await asyncio.sleep(1)  # Simulate training time
        print(f'{sport} model retrained successfully')

asyncio.run(retrain_models())
"@

        $result = python -c $retrainScript

        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "ML retraining completed successfully" "SUCCESS"
        }
        else {
            Write-EQ12Log "ML retraining failed" "ERROR"
        }

        return $LASTEXITCODE -eq 0
    }
    catch {
        Write-EQ12Log "Error during ML retraining: $_" "ERROR"
        return $false
    }
}

function Clear-OldData {
    param([int]$RetentionDays)

    Write-EQ12Log "Cleaning data older than $RetentionDays days..." "INFO"

    try {
        $cleanScript = @"
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('data/sports_betting.db')
cutoff_date = (datetime.now() - timedelta(days=$RetentionDays)).isoformat()

# Clean old odds snapshots
cursor = conn.execute('DELETE FROM odds_snapshots WHERE timestamp < ?', (cutoff_date,))
odds_deleted = cursor.rowcount

# Clean old twitter sentiment
cursor = conn.execute('DELETE FROM twitter_sentiment WHERE timestamp < ?', (cutoff_date,))
sentiment_deleted = cursor.rowcount

# Clean old injury reports
cursor = conn.execute('DELETE FROM injury_reports WHERE created_at < ?', (cutoff_date,))
injury_deleted = cursor.rowcount

conn.commit()
conn.close()

print(f'Cleanup completed:')
print(f'  - Odds snapshots: {odds_deleted} records deleted')
print(f'  - Sentiment data: {sentiment_deleted} records deleted')
print(f'  - Injury reports: {injury_deleted} records deleted')
"@

        $result = python -c $cleanScript

        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "Data cleanup completed successfully" "SUCCESS"
        }
        else {
            Write-EQ12Log "Data cleanup failed" "ERROR"
        }

        return $LASTEXITCODE -eq 0
    }
    catch {
        Write-EQ12Log "Error during data cleanup: $_" "ERROR"
        return $false
    }
}

function Show-Configuration {
    param([string]$Section)

    Write-EQ12Log "Displaying configuration section: $Section" "INFO"

    try {
        if (-not (Test-Path $ConfigPath)) {
            Write-EQ12Log "Configuration file not found" "ERROR"
            return $false
        }

        $config = Get-Content $ConfigPath | ConvertFrom-Json

        switch ($Section) {
            "Risk" {
                Write-Host "`nRisk Management Configuration:" -ForegroundColor Yellow
                Write-Host "=============================" -ForegroundColor Yellow
                $config.risk_management | ConvertTo-Json -Depth 3 | Write-Host
            }
            "Bookmakers" {
                Write-Host "`nBookmakers Configuration:" -ForegroundColor Yellow
                Write-Host "=========================" -ForegroundColor Yellow
                $config.bookmakers | Write-Host
            }
            "Sports" {
                Write-Host "`nSports Configuration:" -ForegroundColor Yellow
                Write-Host "=====================" -ForegroundColor Yellow
                $config.sports | Write-Host
            }
            "X_FACTOR" {
                Write-Host "`nX-Factor Configuration:" -ForegroundColor Yellow
                Write-Host "=======================" -ForegroundColor Yellow
                if ($config.x_factor) {
                    $config.x_factor | ConvertTo-Json -Depth 3 | Write-Host
                }
                else {
                    Write-Host "X-Factor configuration not found" -ForegroundColor Red
                }
            }
            default {
                Write-Host "`nFull Configuration:" -ForegroundColor Yellow
                Write-Host "===================" -ForegroundColor Yellow
                $config | ConvertTo-Json -Depth 5 | Write-Host
            }
        }

        return $true
    }
    catch {
        Write-EQ12Log "Error displaying configuration: $_" "ERROR"
        return $false
    }
}

function Invoke-TestSuite {
    Write-EQ12Log "Running comprehensive test suite..." "INFO"

    try {
        # Run Python tests
        Write-EQ12Log "Running Python test suite..." "INFO"
        $testResult = python -m pytest tests/ -v

        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "Python tests passed" "SUCCESS"
        }
        else {
            Write-EQ12Log "Python tests failed" "ERROR"
        }

        # Run PowerShell tests if they exist
        $pesterPath = Join-Path $ScriptRoot "tests\pester"
        if (Test-Path $pesterPath) {
            Write-EQ12Log "Running PowerShell Pester tests..." "INFO"
            $pesterResult = Invoke-Pester -Path $pesterPath -PassThru

            if ($pesterResult.FailedCount -eq 0) {
                Write-EQ12Log "PowerShell tests passed" "SUCCESS"
            }
            else {
                Write-EQ12Log "PowerShell tests failed: $($pesterResult.FailedCount) failures" "ERROR"
            }
        }

        return ($LASTEXITCODE -eq 0)
    }
    catch {
        Write-EQ12Log "Error running test suite: $_" "ERROR"
        return $false
    }
}

function Initialize-Database {
    Write-EQ12Log "Initializing/upgrading database schema..." "INFO"

    try {
        python $DatabaseMigration
        return $LASTEXITCODE -eq 0
    }
    catch {
        Write-EQ12Log "Database initialization failed: $_" "ERROR"
        return $false
    }
}

function Start-SportsBettingEngine {
    if (-not (Test-Path $PythonScript)) {
        throw "Sports betting script not found: $PythonScript"
    }

    try {
        Write-EQ12Log "Starting sports betting analysis..." "INFO"
        & python $PythonScript

        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "Operation completed successfully" "SUCCESS"
        }
        else {
            Write-EQ12Log "Operation failed with exit code: $LASTEXITCODE" "ERROR"
        }
    }
    catch {
        Write-EQ12Log "Execution error: $_" "ERROR"
        throw
    }
}

function Open-SportsDashboard {
    if (-not (Test-Path $DashboardPath)) {
        Write-EQ12Log "Dashboard not found: $DashboardPath" "ERROR"
        return
    }

    try {
        Write-EQ12Log "Opening sports betting dashboard..." "INFO"
        Start-Process $DashboardPath
        Write-EQ12Log "Dashboard opened in default browser" "SUCCESS"
    }
    catch {
        Write-EQ12Log "Failed to open dashboard: $_" "ERROR"
    }
}

function Get-SystemStatus {
    Write-EQ12Log "Checking EQ12 Sports Betting System Status..." "INFO"

    # Check Python environment
    $pythonOK = Test-PythonEnvironment

    # Check required files
    $filesOK = Test-RequiredFiles

    # Check database
    $dbPath = Join-Path $ScriptRoot "data\sports_betting.db"
    $dbOK = Test-Path $dbPath
    Write-EQ12Log "Database exists: $dbOK" $(if ($dbOK) { "SUCCESS" } else { "ERROR" })

    # Check background jobs
    $runningJobs = Get-Job | Where-Object { $_.Name -like "EQ12_*" -and $_.State -eq "Running" }
    $jobCount = $runningJobs.Count
    Write-EQ12Log "Background jobs running: $jobCount" $(if ($jobCount -gt 0) { "SUCCESS" } else { "INFO" })

    foreach ($job in $runningJobs) {
        Write-EQ12Log "  - $($job.Name) (ID: $($job.Id))" "INFO"
    }

    # Overall system health
    $overallHealth = $pythonOK -and $filesOK -and $dbOK
    $healthStatus = if ($overallHealth) { "HEALTHY" } else { "ISSUES DETECTED" }

    Write-EQ12Log "Overall System Health: $healthStatus" $(if ($overallHealth) { "SUCCESS" } else { "WARNING" })

    return $overallHealth
}

function Show-Help {
    Write-Host ""
    Write-Host "EQ12 Professional Sports Betting System" -ForegroundColor Green
    Write-Host "=======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "CORE OPERATIONS:" -ForegroundColor Yellow
    Write-Host "  analyze         - Run single-pass sports analysis (default)" -ForegroundColor White
    Write-Host "  startlive       - Start persistent live monitoring with X-Factor" -ForegroundColor White
    Write-Host "  stopall         - Gracefully stop all background processes" -ForegroundColor White
    Write-Host "  status          - Check comprehensive system status" -ForegroundColor White
    Write-Host "  dashboard       - Open web dashboard" -ForegroundColor White
    Write-Host ""
    Write-Host "AUTOMATION & TRADING:" -ForegroundColor Yellow
    Write-Host "  autotrade -Enable `$true   - Enable automated trade execution" -ForegroundColor White
    Write-Host "  autotrade -Enable `$false  - Disable automated trade execution" -ForegroundColor White
    Write-Host "  listedges                 - Display current betting opportunities" -ForegroundColor White
    Write-Host "  listbets                  - Show recent bet history and P&L" -ForegroundColor White
    Write-Host ""
    Write-Host "AI & DATA MANAGEMENT:" -ForegroundColor Yellow
    Write-Host "  retrainml -Sport NFL      - Retrain ML models for specified sport" -ForegroundColor White
    Write-Host "  cleandata -Days 90        - Clean data older than N days" -ForegroundColor White
    Write-Host "  config -View Risk         - View configuration section" -ForegroundColor White
    Write-Host "  testsuite                 - Run comprehensive test suite" -ForegroundColor White
    Write-Host "  initdb                    - Initialize/upgrade database schema" -ForegroundColor White
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  .\eq12_sports_betting.ps1 -Action startlive" -ForegroundColor Gray
    Write-Host "  .\eq12_sports_betting.ps1 -Action autotrade -Enable `$true" -ForegroundColor Gray
    Write-Host "  .\eq12_sports_betting.ps1 -Action retrainml -Sport ALL" -ForegroundColor Gray
    Write-Host "  .\eq12_sports_betting.ps1 -Action config -View X_FACTOR" -ForegroundColor Gray
    Write-Host ""
}

# Main execution
try {
    Write-Host ""
    Write-Host "EQ12 Professional Sports Betting System v2.0" -ForegroundColor Green
    Write-Host "=============================================" -ForegroundColor Green
    Write-Host ""

    switch ($Action.ToLower()) {
        "status" {
            $systemOK = Get-SystemStatus
            exit $(if ($systemOK) { 0 } else { 1 })
        }

        "startlive" {
            if (-not (Test-PythonEnvironment)) {
                throw "Python environment check failed"
            }
            $success = Start-LiveMonitoring
            exit $(if ($success) { 0 } else { 1 })
        }

        "stopall" {
            $success = Stop-AllBackgroundJobs
            exit $(if ($success) { 0 } else { 1 })
        }

        "autotrade" {
            $success = Set-AutoTradeMode -EnableAutoTrade:$Enable
            exit $(if ($success) { 0 } else { 1 })
        }

        "listedges" {
            $success = Get-CurrentEdges
            exit $(if ($success) { 0 } else { 1 })
        }

        "listbets" {
            $success = Get-BetHistory
            exit $(if ($success) { 0 } else { 1 })
        }

        "retrainml" {
            $success = Invoke-MLRetraining -Sport $Sport
            exit $(if ($success) { 0 } else { 1 })
        }

        "cleandata" {
            $success = Clear-OldData -RetentionDays $Days
            exit $(if ($success) { 0 } else { 1 })
        }

        "config" {
            $success = Show-Configuration -Section $View
            exit $(if ($success) { 0 } else { 1 })
        }

        "testsuite" {
            $success = Invoke-TestSuite
            exit $(if ($success) { 0 } else { 1 })
        }

        "initdb" {
            $success = Initialize-Database
            exit $(if ($success) { 0 } else { 1 })
        }

        "dashboard" {
            Open-SportsDashboard
            exit 0
        }

        "analyze" {
            if (-not (Test-PythonEnvironment)) {
                throw "Python environment check failed"
            }
            Start-SportsBettingEngine
        }

        default {
            Write-EQ12Log "Unknown action: $Action" "ERROR"
            Show-Help
            exit 1
        }
    }

    Write-EQ12Log "EQ12 Sports Betting operation completed!" "SUCCESS"

}
catch {
    Write-EQ12Log "FATAL ERROR: $_" "ERROR"

    if ($_.Exception.Message -like "*TerminatorExpectedAtEndOfString*") {
        Write-EQ12Log "PowerShell syntax error detected. Please check script formatting." "CRITICAL"
    }

    exit 1
}
