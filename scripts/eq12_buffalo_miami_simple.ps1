#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Buffalo-Miami Flight Search PowerShell Wrapper
    Buffalo NY 14215 Content Empire - American Airlines December 2025

.DESCRIPTION
    Quick and reliable flight search wrapper for the Python search engine.

.EXAMPLE
    .\eq12_buffalo_miami_quick_search.ps1
#>

[CmdletBinding()]
param(
    [switch]$Debug
)

# EQ12 Environment Setup
$ErrorActionPreference = "Stop"
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:EQ12_ASCII_MODE = "ACTIVE"

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    switch ($Level) {
        "ERROR" { Write-Host "[$timestamp] [ERROR] $Message" -ForegroundColor Red }
        "WARN"  { Write-Host "[$timestamp] [WARN]  $Message" -ForegroundColor Yellow }
        "INFO"  { Write-Host "[$timestamp] [INFO]  $Message" -ForegroundColor Green }
        "DEBUG" { if ($Debug) { Write-Host "[$timestamp] [DEBUG] $Message" -ForegroundColor Cyan } }
    }
}

function Test-PythonEnvironment {
    Write-EQ12Log "Testing Python environment..." "INFO"

    try {
        # Check Python version
        $pythonCheck = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found in PATH"
        }

        Write-EQ12Log "Python OK: $pythonCheck" "DEBUG"

        # Check required packages
        python -c "import requests, datetime" 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-EQ12Log "Installing missing packages..." "WARN"
            python -m pip install requests --quiet
        }

        Write-EQ12Log "Python environment ready" "INFO"
        return $true

    } catch {
        Write-EQ12Log "Python environment error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Show-EQ12Banner {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Blue
    Write-Host "                    EQ12 FLIGHT FINDER                         " -ForegroundColor Blue
    Write-Host "              Buffalo NY 14215 Content Empire                 " -ForegroundColor Blue
    Write-Host "                                                               " -ForegroundColor Blue
    Write-Host "  Target: American Airlines Buffalo -> Miami Area             " -ForegroundColor White
    Write-Host "  Month:  December 2025                                       " -ForegroundColor White
    Write-Host "  Focus:  Best deals, direct flights, holiday travel         " -ForegroundColor White
    Write-Host "================================================================" -ForegroundColor Blue
    Write-Host ""
}

function Invoke-FlightSearch {
    Write-EQ12Log "Starting Buffalo-Miami flight search..." "INFO"

    $scriptPath = Join-Path $PSScriptRoot "eq12_buffalo_miami_quick_search.py"

    if (-not (Test-Path $scriptPath)) {
        throw "Python script not found: $scriptPath"
    }

    try {
        # Execute Python script
        python $scriptPath

        if ($LASTEXITCODE -ne 0) {
            throw "Python script execution failed"
        }

        Write-EQ12Log "Flight search completed successfully" "INFO"

    } catch {
        Write-EQ12Log "Flight search error: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Show-CompletionInfo {
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Review the deals above and choose your preferred flight" -ForegroundColor White
    Write-Host "   2. Visit the booking link to complete your reservation" -ForegroundColor White
    Write-Host "   3. Consider booking soon - December prices change frequently" -ForegroundColor White
    Write-Host "   4. Check American Airlines baggage policies" -ForegroundColor White
    Write-Host ""
    Write-Host "Support: EQ12 System - Buffalo NY 14215" -ForegroundColor Gray
    Write-Host ""
}

# MAIN EXECUTION
try {
    # Show system banner
    Show-EQ12Banner

    # Test Python environment
    if (-not (Test-PythonEnvironment)) {
        throw "Python environment check failed"
    }

    # Execute flight search
    Invoke-FlightSearch

    # Show completion info
    Show-CompletionInfo

    Write-EQ12Log "Flight search process completed successfully" "INFO"

} catch {
    $errorMessage = $_.Exception.Message
    Write-EQ12Log "Script execution failed: $errorMessage" "ERROR"
    exit 1
}
