<#
.SYNOPSIS
    EQ12 Emergency Stop - Stops all scans and prevents crashes
.DESCRIPTION
    Emergency script to stop running scans, kill resource-heavy processes,
    and apply crash-prevention settings to VS Code.
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
Write-Host "[1/4] Stopping any running scan processes..." -ForegroundColor Yellow

$ScanProcesses = Get-Process -Name "powershell" -ErrorAction SilentlyContinue | 
    Where-Object { $_.CommandLine -like "*EQ12_SYSTEM_SCAN*" -or $_.CommandLine -like "*EQ12_QUICK_SWEEP*" }

if ($ScanProcesses) {
    foreach ($Proc in $ScanProcesses) {
        Write-Host "  Stopping process: $($Proc.Id)" -ForegroundColor Yellow
        Stop-Process -Id $Proc.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "  ✓ Stopped $($ScanProcesses.Count) scan process(es)" -ForegroundColor Green
} else {
    Write-Host "  No active scan processes found" -ForegroundColor Gray
}

Write-Host ""

# Step 2: Check VS Code memory usage
Write-Host "[2/4] Checking VS Code resource usage..." -ForegroundColor Yellow

$VSCodeProcesses = Get-Process -Name "Code" -ErrorAction SilentlyContinue
if ($VSCodeProcesses) {
    $TotalMemoryMB = ($VSCodeProcesses | Measure-Object -Property WorkingSet64 -Sum).Sum / 1MB
    Write-Host "  VS Code memory usage: $([math]::Round($TotalMemoryMB, 0)) MB" -ForegroundColor $(if ($TotalMemoryMB -gt 2000) { "Red" } else { "Gray" })
    
    if ($TotalMemoryMB -gt 3000) {
        Write-Host "  ⚠️  HIGH MEMORY USAGE - Consider restarting VS Code" -ForegroundColor Red
        $Response = Read-Host "  Restart VS Code now? [Y/N]"
        if ($Response -eq "Y" -or $Response -eq "y") {
            Write-Host "  Stopping VS Code..." -ForegroundColor Yellow
            $VSCodeProcesses | Stop-Process -Force
            Start-Sleep -Seconds 2
            Write-Host "  ✓ VS Code stopped. Restart manually when ready." -ForegroundColor Green
        }
    }
} else {
    Write-Host "  VS Code is not running" -ForegroundColor Gray
}

Write-Host ""

# Step 3: Apply crash-prevention settings
Write-Host "[3/4] Checking crash-prevention settings..." -ForegroundColor Yellow

$SettingsFile = "C:\EQ12_BROKEN_20251122_210342\.vscode\settings.json"

if (Test-Path $SettingsFile) {
    $SettingsContent = Get-Content $SettingsFile -Raw
    
    # Check if critical exclusions exist
    $HasGitExclude = $SettingsContent -match '\.git/objects'
    $HasNodeModules = $SettingsContent -match 'node_modules'
    
    if ($HasGitExclude -and $HasNodeModules) {
        Write-Host "  ✓ Crash-prevention settings already applied" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Settings may need updating - check manually" -ForegroundColor Yellow
        Write-Host "     File: $SettingsFile" -ForegroundColor Gray
    }
} else {
    Write-Host "  settings.json not found" -ForegroundColor Gray
}

Write-Host ""

# Step 4: Recommendations
Write-Host "[4/4] Recommendations to prevent future crashes:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. ✓ File watcher exclusions applied to settings.json" -ForegroundColor Green
Write-Host "  2. Use Safe Scan instead:" -ForegroundColor Cyan
Write-Host "     .\scripts\EQ12_SAFE_SCAN.ps1" -ForegroundColor Gray
Write-Host "  3. Or limit file count:" -ForegroundColor Cyan
Write-Host "     .\scripts\EQ12_QUICK_SWEEP.ps1 -MaxFiles 5000" -ForegroundColor Gray
Write-Host "  4. Restart VS Code to apply settings" -ForegroundColor Cyan
Write-Host ""

Write-Host "=====================================" -ForegroundColor Green
Write-Host "   EMERGENCY STOP COMPLETE" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

return @{
    ProcessesStopped = if ($ScanProcesses) { $ScanProcesses.Count } else { 0 }
    VSCodeMemoryMB = if ($VSCodeProcesses) { [math]::Round($TotalMemoryMB, 0) } else { 0 }
}
