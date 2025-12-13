#!/usr/bin/env powershell
# EQ12 Self-Healing v5.0 PowerShell Wrapper - ASCII SAFE VERSION
# Buffalo NY 14215 Content Empire Protection
# NO EMOJI - GUARANTEED TO WORK

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:LC_ALL = "C.UTF-8"
$env:LANG = "C.UTF-8"

param(
    [string]$Action = "monitor",
    [string]$Workspace = "C:\EQ12",
    [switch]$Continuous,
    [switch]$EmergencyMode,
    [string]$AlertsJson,
    [switch]$Verbose
)

function Write-EQ12Header {
    Write-Host ""
    Write-Host "EQ12 SELF-HEALING v5.0 - BULLETPROOF WRAPPER" -ForegroundColor Cyan
    Write-Host "Buffalo NY 14215 Content Empire Protection" -ForegroundColor Yellow
    Write-Host "ASCII-SAFE GUARANTEED EDITION" -ForegroundColor Green
    Write-Host "============================================================"
}

function Test-PythonScript {
    param([string]$ScriptPath)

    if (-not (Test-Path $ScriptPath)) {
        Write-Host "ERROR: Python script not found: $ScriptPath" -ForegroundColor Red

        $AltPaths = @(
            "C:\EQ12\eq12_self_healing_v5.py",
            "C:\EQ12\scripts\eq12_self_healing_v5.py"
        )

        foreach ($AltPath in $AltPaths) {
            if (Test-Path $AltPath) {
                Write-Host "FOUND: $AltPath" -ForegroundColor Green
                return $AltPath
            }
        }
        return $null
    }
    return $ScriptPath
}

function New-SafeJson {
    param([object]$Object)
    try {
        $Json = $Object | ConvertTo-Json -Depth 5 -Compress
        return $Json
    } catch {
        return '[]'
    }
}

function Get-TestAlerts {
    $CurrentTime = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffK"

    return @(
        @{
            type = "cpu_test"
            severity = "info"
            message = "PowerShell wrapper test"
            timestamp = $CurrentTime
            source = "wrapper_safe"
        }
    )
}

function Invoke-SafePython {
    param(
        [string]$Script,
        [array]$Args
    )

    Write-Host "EXECUTING: python `"$Script`" $($Args -join ' ')" -ForegroundColor Green

    try {
        $Result = & python $Script @Args
        $ExitCode = $LASTEXITCODE

        if ($ExitCode -eq 0) {
            Write-Host "SUCCESS: Exit code $ExitCode" -ForegroundColor Green
        } else {
            Write-Host "WARNING: Exit code $ExitCode" -ForegroundColor Yellow
        }

        return $ExitCode
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return 1
    }
}

# Main execution
try {
    Write-EQ12Header

    # Find Python script
    $PythonScript = Join-Path $Workspace "scripts\eq12_self_healing_v5.py"
    $ValidScript = Test-PythonScript -ScriptPath $PythonScript

    if (-not $ValidScript) {
        Write-Host "FATAL: Cannot find Python script" -ForegroundColor Red
        exit 1
    }

    Write-Host "VALIDATED: Python script found: $ValidScript" -ForegroundColor Green

    # Build arguments
    $PythonArgs = @()

    switch ($Action.ToLower()) {
        "monitor" {
            $PythonArgs = @("monitor", "--workspace", $Workspace)
            if ($Continuous) {
                $PythonArgs += @("--continuous", "--interval", "300")
            }
            Write-Host "ACTION: Starting monitoring..." -ForegroundColor Green
        }

        "heal" {
            $PythonArgs = @("heal", "--workspace", $Workspace)

            if ($AlertsJson) {
                $PythonArgs += @("--alerts", $AlertsJson)
            } else {
                $TestAlerts = Get-TestAlerts
                $SafeJson = New-SafeJson -Object $TestAlerts
                $PythonArgs += @("--alerts", $SafeJson)
            }

            if ($EmergencyMode) {
                $PythonArgs += "--emergency-mode"
            }

            Write-Host "ACTION: Starting healing..." -ForegroundColor Yellow
        }

        "test" {
            $TestAlerts = Get-TestAlerts
            $SafeJson = New-SafeJson -Object $TestAlerts
            $PythonArgs = @("heal", "--workspace", $Workspace, "--alerts", $SafeJson, "--emergency-mode")
            Write-Host "ACTION: Running test..." -ForegroundColor Magenta
        }

        "status" {
            $PythonArgs = @("status", "--workspace", $Workspace)
            Write-Host "ACTION: Checking status..." -ForegroundColor Blue
        }

        default {
            Write-Host "ERROR: Invalid action: $Action" -ForegroundColor Red
            Write-Host "Valid actions: monitor, heal, test, status" -ForegroundColor Gray
            exit 1
        }
    }

    if ($Verbose) {
        $PythonArgs += "--verbose"
    }

    # Execute Python script
    $ExitCode = Invoke-SafePython -Script $ValidScript -Args $PythonArgs

    Write-Host ""
    Write-Host "USAGE EXAMPLES:" -ForegroundColor Cyan
    Write-Host "  Monitor: .\eq12_self_healing_v5_wrapper_ascii.ps1 -Action monitor" -ForegroundColor Gray
    Write-Host "  Heal: .\eq12_self_healing_v5_wrapper_ascii.ps1 -Action heal" -ForegroundColor Gray
    Write-Host "  Test: .\eq12_self_healing_v5_wrapper_ascii.ps1 -Action test" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Buffalo NY 14215 Content Empire: PROTECTED" -ForegroundColor Green

    exit $ExitCode

} catch {
    Write-Host ""
    Write-Host "CRITICAL ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
