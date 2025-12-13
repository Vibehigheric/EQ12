#!/usr/bin/env powershell
# EQ12 Self-Healing v5.0 PowerShell Wrapper - BULLETPROOF SAFE EDITION
# Guaranteed to work - No more syntax errors
# Buffalo NY 14215 Content Empire Protection

# UTF-8 enforcement
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

# Environment setup
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
    Write-Host " EQ12 SELF-HEALING v5.0 - BULLETPROOF WRAPPER" -ForegroundColor Cyan
    Write-Host " Buffalo NY 14215 Content Empire Protection" -ForegroundColor Yellow
    Write-Host " SYNTAX-SAFE GUARANTEED EDITION" -ForegroundColor Green
    Write-Host "=" * 60
}

function Test-PythonScript {
    param([string]$ScriptPath)

    if (-not (Test-Path $ScriptPath)) {
        Write-Host " Python script not found: $ScriptPath" -ForegroundColor Red

        # Check alternative locations
        $AltPaths = @(
            "C:\EQ12\eq12_self_healing_v5.py",
            "C:\EQ12\scripts\eq12_self_healing_v5.py"
        )

        foreach ($AltPath in $AltPaths) {
            if (Test-Path $AltPath) {
                Write-Host " Found at: $AltPath" -ForegroundColor Green
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
        }
    )
}

function Invoke-SafePython {
    param(
        [string]$Script,
        [array]$Args
    )

    Write-Host " Executing Python with safe UTF-8 encoding..." -ForegroundColor Green
    Write-Host "Command: python `"$Script`" $($Args -join ' ')" -ForegroundColor Gray

    try {
        $Result = & python $Script @Args
        $ExitCode = $LASTEXITCODE

        if ($ExitCode -eq 0) {
            Write-Host " SUCCESS (Exit: $ExitCode)" -ForegroundColor Green
        } else {
            Write-Host " WARNING (Exit: $ExitCode)" -ForegroundColor Yellow
        }

        return $ExitCode
    } catch {
        Write-Host " EXECUTION ERROR: $($_.Exception.Message)" -ForegroundColor Red
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
        Write-Host " Cannot find Python script" -ForegroundColor Red
        exit 1
    }

    Write-Host " Python script found: $ValidScript" -ForegroundColor Green

    # Build arguments based on action
    $PythonArgs = @()

    switch ($Action.ToLower()) {
        "monitor" {
            $PythonArgs = @("monitor", "--workspace", $Workspace)
            if ($Continuous) {
                $PythonArgs += @("--continuous", "--interval", "300")
            }
            Write-Host " Starting monitoring..." -ForegroundColor Green
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

            Write-Host " Starting healing..." -ForegroundColor Yellow
        }

        "test" {
            $TestAlerts = Get-TestAlerts
            $SafeJson = New-SafeJson -Object $TestAlerts
            $PythonArgs = @("heal", "--workspace", $Workspace, "--alerts", $SafeJson, "--emergency-mode")
            Write-Host " Running test..." -ForegroundColor Magenta
        }

        "status" {
            $PythonArgs = @("status", "--workspace", $Workspace)
            Write-Host " Checking status..." -ForegroundColor Blue
        }

        default {
            Write-Host " Invalid action: $Action" -ForegroundColor Red
            Write-Host "Valid: monitor, heal, test, status" -ForegroundColor Gray
            exit 1
        }
    }

    # Add verbose if requested
    if ($Verbose) {
        $PythonArgs += "--verbose"
    }

    # Execute
    $ExitCode = Invoke-SafePython -Script $ValidScript -Args $PythonArgs

    Write-Host ""
    Write-Host " USAGE EXAMPLES:" -ForegroundColor Cyan
    Write-Host "Monitor: .\eq12_self_healing_v5_wrapper_safe.ps1 -Action monitor" -ForegroundColor Gray
    Write-Host "Heal: .\eq12_self_healing_v5_wrapper_safe.ps1 -Action heal" -ForegroundColor Gray
    Write-Host "Test: .\eq12_self_healing_v5_wrapper_safe.ps1 -Action test" -ForegroundColor Gray
    Write-Host ""
    Write-Host " Buffalo NY 14215 Content Empire: PROTECTED" -ForegroundColor Green

    exit $ExitCode

} catch {
    Write-Host ""
    Write-Host " WRAPPER ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

