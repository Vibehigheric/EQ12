<#
.SYNOPSIS
    EQ12 Emergency Stop - Stops all scans
.DESCRIPTION
    Stops running scans and checks VS Code status
.EXAMPLE
    .\EQ12_EMERGENCY_STOP.ps1
#>

[CmdletBinding()]
param()

Write-Host "=====================================" -ForegroundColor Red
Write-Host "   EQ12 EMERGENCY STOP" -ForegroundColor Red
Write-Host "=====================================" -ForegroundColor Red
Write-Host ""

# Step 1: Kill any running PowerShell scan processes
Write-Host "[1/3] Stopping any running scan processes..." -ForegroundColor Yellow

try {
    $ScanProcesses = Get-Process powershell -ErrorAction SilentlyContinue | Where-Object {
        $_.MainWindowTitle -like "*EQ12*SCAN*" -or
        $_.CommandLine -like "*EQ12_SYSTEM_SCAN*" -or
        $_.CommandLine -like "*EQ12_QUICK_SWEEP*"
    }

    if ($ScanProcesses) {
        foreach ($Proc in $ScanProcesses) {
            Write-Host "  Stopping process: $($Proc.Id)" -ForegroundColor Yellow
            Stop-Process -Id $Proc.Id -Force -ErrorAction SilentlyContinue
        }
        Write-Host "  Stopped $($ScanProcesses.Count) scan process(es)" -ForegroundColor Green
    } else {
        Write-Host "  No active scan processes found" -ForegroundColor Gray
    }
}
catch {
    Write-Host "  Error checking processes: $_" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Check VS Code memory usage
Write-Host "[2/3] Checking VS Code resource usage..." -ForegroundColor Yellow

try {
    $VSCodeProcesses = Get-Process Code -ErrorAction SilentlyContinue
    if ($VSCodeProcesses) {
        $TotalMemoryMB = ($VSCodeProcesses | Measure-Object -Property WorkingSet64 -Sum).Sum / 1MB
        Write-Host "  VS Code memory usage: $([math]::Round($TotalMemoryMB, 0)) MB" -ForegroundColor Gray
        
        if ($TotalMemoryMB -gt 3000) {
            Write-Host "  WARNING: HIGH MEMORY USAGE" -ForegroundColor Red
            Write-Host "  Consider restarting VS Code" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  VS Code is not running" -ForegroundColor Gray
    }
}
catch {
    Write-Host "  Could not check VS Code status" -ForegroundColor Yellow
}

Write-Host ""

# Step 3: Recommendations
Write-Host "[3/3] Recommendations to prevent future crashes:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Use Safe Scan instead:" -ForegroundColor Cyan
Write-Host "     .\scripts\EQ12_SAFE_SCAN.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Or limit file count:" -ForegroundColor Cyan
Write-Host "     .\scripts\EQ12_QUICK_SWEEP.ps1 -MaxFiles 5000" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Restart VS Code to clear memory" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. File watcher exclusions already applied in .vscode\settings.json" -ForegroundColor Green
Write-Host ""

Write-Host "=====================================" -ForegroundColor Green
Write-Host "   EMERGENCY STOP COMPLETE" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
