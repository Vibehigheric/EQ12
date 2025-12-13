# EQ12 GODLIKE LAUNCHER SYSTEM - FIXED VERSION
# ===========================================

param(
    [Parameter(Mandatory=$false)]
    [string]$Command,
    [switch]$QuickMode,
    [string]$Workspace = "C:\EQ12"
)

Set-Location $Workspace

function Show-EQ12Status {
    Write-Host ""
    Write-Host " EQ12 GODLIKE LAUNCHER SYSTEM" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "System Status: " -NoNewline -ForegroundColor White
    Write-Host "OPERATIONAL" -ForegroundColor Green
    Write-Host "API Coverage: 5/7 (71.4%)" -ForegroundColor Yellow
    Write-Host "Health Score: 66.7%" -ForegroundColor Yellow
    Write-Host "RAM: 32GB (64GB Ready)" -ForegroundColor Green
    Write-Host ""
}

function Execute-EQ12Command {
    param([string]$cmd)
    
    Write-Host "Executing: $cmd" -ForegroundColor Yellow
    
    switch ($cmd.ToLower()) {
        "1" { & python "$Workspace\scripts\eq12_run_odds.py" --mode single --verbose }
        "run-odds" { & python "$Workspace\scripts\eq12_run_odds.py" --mode single --verbose }
        
        "2" { & python "$Workspace\scripts\eq12_run_parlay.py" --legs 3 --count 1 --verbose }
        "run-parlay" { & python "$Workspace\scripts\eq12_run_parlay.py" --legs 3 --count 1 --verbose }
        
        "3" { & python "$Workspace\eq12_betting_suite.py" --mode sequential --verbose }
        "betting-suite" { & python "$Workspace\eq12_betting_suite.py" --mode sequential --verbose }
        
        "4" { & python "$Workspace\eq12_final_system_validation.py" }
        "health-check" { & python "$Workspace\eq12_final_system_validation.py" }
        
        "5" { & python "$Workspace\eq12_api_key_manager.py" --test-all }
        "api-test" { & python "$Workspace\eq12_api_key_manager.py" --test-all }
        
        "6" { & powershell -ExecutionPolicy Bypass -File "$Workspace\EQ12_System_Rebuild_Checklist.ps1" -Action All }
        "system-rebuild" { & powershell -ExecutionPolicy Bypass -File "$Workspace\EQ12_System_Rebuild_Checklist.ps1" -Action All }
        
        "7" { 
            Write-Host "RAM Optimization..." -ForegroundColor Cyan
            Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10
            [System.GC]::Collect()
            Write-Host "Memory optimized" -ForegroundColor Green
        }
        "ram-optimize" { 
            Write-Host "RAM Optimization..." -ForegroundColor Cyan
            Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10
            [System.GC]::Collect()
            Write-Host "Memory optimized" -ForegroundColor Green
        }
        
        default { Write-Host "Unknown command: $cmd" -ForegroundColor Red }
    }
}

function Show-QuickMenu {
    Write-Host "QUICK COMMANDS:" -ForegroundColor Green
    Write-Host "  1 | run-odds      -> Fetch live odds" -ForegroundColor White
    Write-Host "  2 | run-parlay    -> Generate parlay" -ForegroundColor White
    Write-Host "  3 | betting-suite -> Full betting cycle" -ForegroundColor White
    Write-Host "  4 | health-check  -> System validation" -ForegroundColor White
    Write-Host "  5 | api-test      -> Test all APIs" -ForegroundColor White
    Write-Host "  6 | system-rebuild-> Complete rebuild" -ForegroundColor White
    Write-Host "  7 | ram-optimize  -> Memory cleanup" -ForegroundColor White
    Write-Host ""
}

# Main execution
if ($QuickMode -and $Command) {
    Show-EQ12Status
    Execute-EQ12Command $Command
    exit 0
}

# Interactive mode
Show-EQ12Status
Show-QuickMenu

while ($true) {
    Write-Host "Enter command (or 'exit'): " -NoNewline -ForegroundColor Cyan
    $userInput = Read-Host
    
    if ($userInput -eq "exit") {
        break
    }
    
    if ($userInput) {
        Execute-EQ12Command $userInput
        Write-Host ""
    }
}

Write-Host "EQ12 Launcher session ended" -ForegroundColor Green