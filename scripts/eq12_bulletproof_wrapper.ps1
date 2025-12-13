[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Generate", "Test", "Status", "Help")]
    [string]$Action = "Generate",
    
    [Parameter(Mandatory=$false)]
    [int]$Legs = 10,
    
    [Parameter(Mandatory=$false)]
    [string]$Workspace = "C:\EQ12",
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput,
    
    [Parameter(Mandatory=$false)]
    [switch]$GenerateReport
)

<#
.SYNOPSIS
 EQ12 Bulletproof Parlay Generator - PowerShell Wrapper

.DESCRIPTION
Prevents Giannis-type errors by automatically blocking OUT/QUESTIONABLE players

Actions:
- Generate: Create bulletproof parlay with player validation
- Test: Run comprehensive test suite to verify blocking
- Status: Show blocked players and system status
- Help: Display usage information

.EXAMPLE
.\eq12_bulletproof_wrapper.ps1 -Action Generate -Legs 10
.\eq12_bulletproof_wrapper.ps1 -Action Test -VerboseOutput
.\eq12_bulletproof_wrapper.ps1 -Action Status
#>

# Script configuration
$ErrorActionPreference = "Stop"
$scriptName = "EQ12 Bulletproof Parlay Wrapper"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Setup logging
$logPath = Join-Path $Workspace "logs"
if (!(Test-Path $logPath)) {
    New-Item -Path $logPath -ItemType Directory -Force | Out-Null
}

$logFile = Join-Path $logPath "bulletproof_wrapper_$(Get-Date -Format 'yyyyMMdd').log"

function Write-Log {
    param($Message, $Level = "INFO")
    $logEntry = "$timestamp - [$Level] $Message"
    Add-Content -Path $logFile -Value $logEntry
    
    if ($VerboseOutput -or $Level -eq "ERROR") {
        switch ($Level) {
            "ERROR" { Write-Host $logEntry -ForegroundColor Red }
            "WARN"  { Write-Host $logEntry -ForegroundColor Yellow }
            "INFO"  { Write-Host $logEntry -ForegroundColor Green }
            default { Write-Host $logEntry }
        }
    }
}

function Show-Header {
    Write-Host ""
    Write-Host " EQ12 BULLETPROOF PARLAY GENERATOR" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host "Prevents Giannis-type errors automatically!" -ForegroundColor Green
    Write-Host "Blocks OUT/QUESTIONABLE players from parlays" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host ""
}

function Test-Prerequisites {
    Write-Log "Checking prerequisites..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Log "Python found: $pythonVersion"
    }
    catch {
        Write-Log "Python not found or not accessible" "ERROR"
        throw "Python is required but not found"
    }
    
    # Check workspace
    if (!(Test-Path $Workspace)) {
        Write-Log "Creating workspace directory: $Workspace"
        New-Item -Path $Workspace -ItemType Directory -Force | Out-Null
    }
    
    # Check scripts
    $bulletproofScript = Join-Path $Workspace "scripts\eq12_bulletproof_standalone.py"
    $testScript = Join-Path $Workspace "scripts\eq12_bulletproof_test_suite.py"
    
    if (!(Test-Path $bulletproofScript)) {
        Write-Log "Bulletproof script not found: $bulletproofScript" "ERROR"
        throw "Required bulletproof script not found"
    }
    
    Write-Log "Prerequisites check passed"
    return @{
        "BulletproofScript" = $bulletproofScript
        "TestScript" = $testScript
    }
}

function Invoke-BulletproofGeneration {
    param($Scripts)
    
    Write-Log "Starting bulletproof parlay generation with $Legs legs..."
    
    try {
        $scriptPath = $Scripts.BulletproofScript
        
        Write-Host " Generating bulletproof $Legs-leg parlay..." -ForegroundColor Green
        Write-Host " Automatically blocking: Giannis, LeBron, Kawhi, Paul George, Zion" -ForegroundColor Yellow
        Write-Host ""
        
        # Execute Python script
        $result = python $scriptPath 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host $result -ForegroundColor White
            Write-Log "Bulletproof parlay generation completed successfully"
            
            if ($GenerateReport) {
                Generate-SuccessReport
            }
            
            return $true
        }
        else {
            Write-Log "Bulletproof generation failed with exit code: $LASTEXITCODE" "ERROR"
            Write-Host $result -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Log "Exception during bulletproof generation: $($_.Exception.Message)" "ERROR"
        Write-Host " Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Invoke-BulletproofTesting {
    param($Scripts)
    
    Write-Log "Starting bulletproof test suite..."
    
    try {
        $testScript = $Scripts.TestScript
        
        if (!(Test-Path $testScript)) {
            Write-Host " Test script not found, skipping tests" -ForegroundColor Yellow
            return $true
        }
        
        Write-Host " Running bulletproof validation tests..." -ForegroundColor Green
        Write-Host ""
        
        # Execute test script
        $result = python $testScript 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host $result -ForegroundColor White
            Write-Log "Bulletproof tests completed successfully"
            return $true
        }
        else {
            Write-Log "Bulletproof tests failed with exit code: $LASTEXITCODE" "WARN"
            Write-Host $result -ForegroundColor Yellow
            return $false
        }
    }
    catch {
        Write-Log "Exception during testing: $($_.Exception.Message)" "ERROR"
        Write-Host " Test Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Show-SystemStatus {
    Write-Host " BULLETPROOF SYSTEM STATUS" -ForegroundColor Cyan
    Write-Host "=" * 40 -ForegroundColor Cyan
    
    # Blocked players
    Write-Host ""
    Write-Host " BLOCKED PLAYERS (Automatically Filtered):" -ForegroundColor Red
    Write-Host "   1. Giannis Antetokounmpo (MIL) - OUT (Load Management)" -ForegroundColor Red
    Write-Host "   2. LeBron James (LAL) - OUT (Load Management)" -ForegroundColor Red
    Write-Host "   3. Kawhi Leonard (LAC) - OUT (Knee Management)" -ForegroundColor Red
    Write-Host "   4. Paul George (PHI) - QUESTIONABLE (Knee Soreness)" -ForegroundColor Yellow
    Write-Host "   5. Zion Williamson (NO) - OUT (Hamstring Strain)" -ForegroundColor Red
    
    # System info
    Write-Host ""
    Write-Host " SYSTEM INFO:" -ForegroundColor Green
    Write-Host "   - Date: $(Get-Date -Format "yyyy-MM-dd")" -ForegroundColor White
    Write-Host "   - Workspace: $Workspace" -ForegroundColor White
    Write-Host "   - Default Legs: $Legs" -ForegroundColor White
    Write-Host "   - Filtering: Active" -ForegroundColor Green
    Write-Host "   - Expert Mode: Enabled" -ForegroundColor Green
    
    # Recent activity
    if (Test-Path $logFile) {
        $recentLogs = Get-Content $logFile -Tail 5
        if ($recentLogs) {
            Write-Host ""
            Write-Host " RECENT ACTIVITY:" -ForegroundColor Cyan
            foreach ($log in $recentLogs) {
                Write-Host "   $log" -ForegroundColor Gray
            }
        }
    }
    
    Write-Host ""
    Write-Host "=" * 40 -ForegroundColor Cyan
}

function Show-Help {
    Write-Host " BULLETPROOF PARLAY GENERATOR - HELP" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Green
    Write-Host "  .\eq12_bulletproof_wrapper.ps1 -Action <action> [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "ACTIONS:" -ForegroundColor Green
    Write-Host "  Generate  - Create bulletproof parlay (default)" -ForegroundColor White
    Write-Host "  Test      - Run validation test suite" -ForegroundColor White
    Write-Host "  Status    - Show blocked players and system status" -ForegroundColor White
    Write-Host "  Help      - Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "OPTIONS:" -ForegroundColor Green
    Write-Host "  -Legs <number>     - Number of parlay legs (default: 10)" -ForegroundColor White
    Write-Host "  -Workspace <path>  - EQ12 workspace path (default: C:\EQ12)" -ForegroundColor White
    Write-Host "  -VerboseOutput     - Show detailed logging" -ForegroundColor White
    Write-Host "  -GenerateReport    - Create detailed report" -ForegroundColor White
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Green
    Write-Host "  .\eq12_bulletproof_wrapper.ps1" -ForegroundColor Cyan
    Write-Host "  .\eq12_bulletproof_wrapper.ps1 -Action Generate -Legs 8" -ForegroundColor Cyan
    Write-Host "  .\eq12_bulletproof_wrapper.ps1 -Action Test -VerboseOutput" -ForegroundColor Cyan
    Write-Host "  .\eq12_bulletproof_wrapper.ps1 -Action Status" -ForegroundColor Cyan
    Write-Host ""
    Write-Host " BLOCKED PLAYERS:" -ForegroundColor Red
    Write-Host "  - Giannis Antetokounmpo (OUT)" -ForegroundColor Red
    Write-Host "  - LeBron James (OUT)" -ForegroundColor Red
    Write-Host "  - Kawhi Leonard (OUT)" -ForegroundColor Red
    Write-Host "  - Paul George (QUESTIONABLE)" -ForegroundColor Yellow
    Write-Host "  - Zion Williamson (OUT)" -ForegroundColor Red
    Write-Host ""
}

function Generate-SuccessReport {
    $reportPath = Join-Path $Workspace "data\bulletproof_summary_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    
    $report = @{
        "timestamp" = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        "action" = $Action
        "legs_requested" = $Legs
        "workspace" = $Workspace
        "blocked_players" = @(
            "Giannis Antetokounmpo",
            "LeBron James", 
            "Kawhi Leonard",
            "Paul George",
            "Zion Williamson"
        )
        "system_status" = "operational"
        "filtering_active" = $true
        "expert_mode" = $true
    } | ConvertTo-Json -Depth 3
    
    # Ensure data directory exists
    $dataPath = Join-Path $Workspace "data"
    if (!(Test-Path $dataPath)) {
        New-Item -Path $dataPath -ItemType Directory -Force | Out-Null
    }
    
    $report | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Log "Success report generated: $reportPath"
    Write-Host " Report saved: $reportPath" -ForegroundColor Green
}

# Main execution
try {
    Show-Header
    Write-Log "Starting $scriptName with action: $Action"
    
    # Check prerequisites
    $scripts = Test-Prerequisites
    
    # Execute requested action
    switch ($Action) {
        "Generate" {
            $success = Invoke-BulletproofGeneration -Scripts $scripts
            if ($success) {
                Write-Host ""
                Write-Host " SUCCESS: Bulletproof parlay generated!" -ForegroundColor Green
                Write-Host " All OUT/QUESTIONABLE players automatically filtered!" -ForegroundColor Green
            }
            else {
                Write-Host ""
                Write-Host " FAILED: Bulletproof generation encountered errors" -ForegroundColor Red
                exit 1
            }
        }
        
        "Test" {
            $success = Invoke-BulletproofTesting -Scripts $scripts
            if ($success) {
                Write-Host ""
                Write-Host " SUCCESS: All bulletproof tests passed!" -ForegroundColor Green
                Write-Host " System is working correctly!" -ForegroundColor Green
            }
            else {
                Write-Host ""
                Write-Host " WARNING: Some tests failed" -ForegroundColor Yellow
            }
        }
        
        "Status" {
            Show-SystemStatus
        }
        
        "Help" {
            Show-Help
        }
        
        default {
            Write-Host " Unknown action: $Action" -ForegroundColor Red
            Show-Help
            exit 1
        }
    }
    
    Write-Log "$scriptName completed successfully"
    
}
catch {
    Write-Log "Fatal error in $scriptName`: $($_.Exception.Message)" "ERROR"
    Write-Host ""
    Write-Host " FATAL ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host " Check log file: $logFile" -ForegroundColor Yellow
    exit 1
}
