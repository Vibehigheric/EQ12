# EQ12 Self-Healing v5.0 PowerShell Wrapper - MINIMAL SAFE VERSION
# Buffalo NY 14215 Content Empire Protection
# GUARANTEED TO WORK - NO COMPLEX SYNTAX

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# Get command line arguments
$Action = if ($args[0]) { $args[0] } else { "test" }
$Workspace = if ($args[1]) { $args[1] } else { "C:\EQ12" }

Write-Host ""
Write-Host "EQ12 SELF-HEALING v5.0 - MINIMAL WRAPPER" -ForegroundColor Cyan
Write-Host "Buffalo NY 14215 Content Empire Protection" -ForegroundColor Yellow
Write-Host "============================================"
Write-Host "Action: $Action | Workspace: $Workspace" -ForegroundColor Green

# Find Python script
$PythonScript = Join-Path $Workspace "scripts\eq12_self_healing_v5.py"

if (-not (Test-Path $PythonScript)) {
    Write-Host "ERROR: Python script not found: $PythonScript" -ForegroundColor Red

    # Try alternative locations
    $Alt1 = Join-Path $Workspace "eq12_self_healing_v5.py"
    $Alt2 = "C:\EQ12\eq12_self_healing_v5.py"

    if (Test-Path $Alt1) {
        $PythonScript = $Alt1
        Write-Host "FOUND: Using $PythonScript" -ForegroundColor Green
    } elseif (Test-Path $Alt2) {
        $PythonScript = $Alt2
        Write-Host "FOUND: Using $PythonScript" -ForegroundColor Green
    } else {
        Write-Host "FATAL: Cannot find Python script anywhere" -ForegroundColor Red
        exit 1
    }
}

Write-Host "VALIDATED: Python script: $PythonScript" -ForegroundColor Green

# Build command arguments
$PythonArgs = @()

switch ($Action.ToLower()) {
    "monitor" {
        $PythonArgs = @("monitor", "--workspace", $Workspace)
        Write-Host "ACTION: Starting monitoring mode" -ForegroundColor Green
    }

    "heal" {
        $TestAlert = '[{"type":"system_check","severity":"info","message":"PowerShell wrapper test","timestamp":"' + (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffK") + '"}]'
        $PythonArgs = @("heal", "--workspace", $Workspace, "--alerts", $TestAlert)
        Write-Host "ACTION: Starting healing mode" -ForegroundColor Yellow
    }

    "test" {
        $TestAlert = '[{"type":"test_alert","severity":"info","message":"Wrapper connectivity test","timestamp":"' + (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffK") + '"}]'
        $PythonArgs = @("heal", "--workspace", $Workspace, "--alerts", $TestAlert, "--emergency-mode")
        Write-Host "ACTION: Running test mode" -ForegroundColor Magenta
    }

    default {
        Write-Host "ERROR: Invalid action '$Action'" -ForegroundColor Red
        Write-Host "Valid actions: monitor, heal, test" -ForegroundColor Gray
        exit 1
    }
}

Write-Host "COMMAND: python `"$PythonScript`" $($PythonArgs -join ' ')" -ForegroundColor Gray

# Execute Python script
try {
    $Result = & python $PythonScript @PythonArgs
    $ExitCode = $LASTEXITCODE

    Write-Host ""
    if ($ExitCode -eq 0) {
        Write-Host "SUCCESS: Self-healing completed (Exit: $ExitCode)" -ForegroundColor Green
    } elseif ($ExitCode -eq 2) {
        Write-Host "WARNING: Self-healing completed with warnings (Exit: $ExitCode)" -ForegroundColor Yellow
    } else {
        Write-Host "ERROR: Self-healing failed (Exit: $ExitCode)" -ForegroundColor Red
    }

} catch {
    Write-Host ""
    Write-Host "EXECUTION ERROR: $($_.Exception.Message)" -ForegroundColor Red
    $ExitCode = 1
}

Write-Host ""
Write-Host "USAGE:" -ForegroundColor Cyan
Write-Host "  .\eq12_self_healing_wrapper_minimal.ps1 test" -ForegroundColor Gray
Write-Host "  .\eq12_self_healing_wrapper_minimal.ps1 monitor" -ForegroundColor Gray
Write-Host "  .\eq12_self_healing_wrapper_minimal.ps1 heal" -ForegroundColor Gray
Write-Host ""
Write-Host "Buffalo NY 14215 Content Empire: PROTECTED" -ForegroundColor Green

exit $ExitCode
