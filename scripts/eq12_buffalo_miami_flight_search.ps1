#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Buffalo-Miami Flight Search PowerShell Wrapper
    Buffalo NY 14215 Content Empire - American Airlines December 2025

.DESCRIPTION
    ASCII-safe, syntax-perfect flight search wrapper.

.EXAMPLE
    .\eq12_buffalo_miami_flight_search.ps1

.EXAMPLE
    .\eq12_buffalo_miami_flight_search.ps1 -Verbose
#>

[CmdletBinding()]
param()

# EQ12 ASCII Environment Setup
$ErrorActionPreference = "Stop"
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:EQ12_ASCII_MODE = "ACTIVE"

function Write-EQ12Log {
    param(
        [Parameter(Mandatory)]
        [string]$Message,

        [ValidateSet("INFO", "WARN", "ERROR")]
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    switch ($Level) {
        "ERROR" {
            $logMessage = "[$timestamp] [ERROR] $Message"
            Write-Host $logMessage -ForegroundColor Red
        }
        "WARN"  {
            $logMessage = "[$timestamp] [WARN]  $Message"
            Write-Host $logMessage -ForegroundColor Yellow
        }
        "INFO"  {
            $logMessage = "[$timestamp] [INFO]  $Message"
            Write-Host $logMessage -ForegroundColor Green
        }
    }

    if ($VerbosePreference -eq "Continue") {
        Write-Verbose $logMessage
    }
}

function Test-PythonEnvironment {
    Write-EQ12Log -Message "Testing Python environment..." -Level "INFO"

    try {
        # Check if Python exists
        $pythonCheck = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found in PATH. Please install Python 3.8+ or activate virtual environment."
        }

        Write-Verbose "Python found: $pythonCheck"

        # Test required packages
        $testImports = "import requests, datetime, json, os, sys"
        python -c $testImports 2>&1 | Out-Null

        if ($LASTEXITCODE -ne 0) {
            Write-EQ12Log -Message "Installing missing Python packages..." -Level "WARN"
            python -m pip install requests --quiet

            if ($LASTEXITCODE -ne 0) {
                throw "Failed to install required packages. Please run: pip install requests"
            }
        }

        Write-EQ12Log -Message "Python environment ready" -Level "INFO"
        return $true

    }
    catch {
        $errorMsg = $_.Exception.Message
        Write-EQ12Log -Message "Python environment error: $errorMsg" -Level "ERROR"
        return $false
    }
}

function Show-EQ12Header {
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
    Write-EQ12Log -Message "Starting Buffalo-Miami flight search..." -Level "INFO"

    $scriptPath = Join-Path $PSScriptRoot "eq12_buffalo_miami_quick_search.py"

    if (-not (Test-Path $scriptPath)) {
        $errorMsg = "Python script not found: $scriptPath"
        Write-EQ12Log -Message $errorMsg -Level "ERROR"
        throw $errorMsg
    }

    try {
        Write-Verbose "Executing Python script: $scriptPath"

        # Execute the Python flight search
        python $scriptPath

        if ($LASTEXITCODE -ne 0) {
            throw "Python script execution failed with exit code: $LASTEXITCODE"
        }

        Write-EQ12Log -Message "Flight search completed successfully" -Level "INFO"

    }
    catch {
        $errorMsg = $_.Exception.Message
        Write-EQ12Log -Message "Flight search error: $errorMsg" -Level "ERROR"
        throw
    }
}

function Show-NextSteps {
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Review the flight deals above" -ForegroundColor White
    Write-Host "   2. Visit American Airlines to book your preferred flight" -ForegroundColor White
    Write-Host "   3. Book soon - December holiday prices change daily" -ForegroundColor White
    Write-Host "   4. Consider travel insurance for holiday trips" -ForegroundColor White
    Write-Host ""
    Write-Host "Booking Links:" -ForegroundColor Cyan
    Write-Host "   - American Airlines: https://www.aa.com" -ForegroundColor White
    Write-Host "   - Kayak: https://www.kayak.com/flights/BUF-MIA" -ForegroundColor White
    Write-Host "   - Google Flights: https://www.google.com/travel/flights" -ForegroundColor White
    Write-Host ""
    Write-Host "Support: EQ12 System - Buffalo NY 14215 Content Empire" -ForegroundColor Gray
    Write-Host ""
}

# ===== MAIN EXECUTION =====
try {
    # Display header
    Show-EQ12Header

    # Validate Python environment
    $pythonReady = Test-PythonEnvironment
    if (-not $pythonReady) {
        throw "Python environment validation failed. Please fix Python setup and try again."
    }

    # Execute flight search
    Invoke-FlightSearch

    # Show next steps
    Show-NextSteps

    # Success message
    Write-EQ12Log -Message "EQ12 Flight Search completed successfully" -Level "INFO"

}
catch {
    # Error handling - ASCII-safe error message
    $errorMessage = $_.Exception.Message
    Write-EQ12Log -Message "Script execution failed: $errorMessage" -Level "ERROR"

    Write-Host ""
    Write-Host "Troubleshooting Tips:" -ForegroundColor Yellow
    Write-Host "   1. Ensure Python 3.8+ is installed and in PATH" -ForegroundColor White
    Write-Host "   2. Install required packages: pip install requests" -ForegroundColor White
    Write-Host "   3. Check internet connectivity" -ForegroundColor White
    Write-Host "   4. Run with -Verbose for detailed debugging" -ForegroundColor White
    Write-Host ""

    exit 1
}
