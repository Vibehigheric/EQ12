#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Buffalo-Miami Flight Search PowerShell Wrapper
    Buffalo NY 14215 Content Empire - American Airlines December 2025

.DESCRIPTION
    Quick and reliable flight search wrapper for the Python search engine.
    Handles environment validation and provides clean PowerShell output.

.PARAMETER SearchType
    Type of search: Quick (default), Detailed, or PriceOnly

.PARAMETER OutputFormat
    Output format: Console (default), JSON, or CSV

.PARAMETER SaveResults
    Save results to logs directory (default: true)

.EXAMPLE
    .\eq12_buffalo_miami_quick_search.ps1

.EXAMPLE
    .\eq12_buffalo_miami_quick_search.ps1 -SearchType Detailed -OutputFormat JSON
#>

[CmdletBinding()]
param(
    [ValidateSet("Quick", "Detailed", "PriceOnly")]
    [string]$SearchType = "Quick",

    [ValidateSet("Console", "JSON", "CSV")]
    [string]$OutputFormat = "Console",

    [bool]$SaveResults = $true,

    [switch]$Verbose
)

# EQ12 Environment Setup
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# ASCII-safe environment
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:EQ12_ASCII_MODE = "ACTIVE"

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    switch ($Level) {
        "ERROR" { Write-Error $logEntry }
        "WARN"  { Write-Warning $logEntry }
        "INFO"  { Write-Host $logEntry -ForegroundColor Green }
        "DEBUG" { if ($Verbose) { Write-Host $logEntry -ForegroundColor Cyan } }
    }
}

function Test-PythonEnvironment {
    """Test Python environment and requirements"""

    Write-EQ12Log "Testing Python environment..." "INFO"

    try {
        # Check Python version
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found in PATH"
        }

        if ($pythonVersion -notmatch "Python 3\.[8-9]|Python 3\.1[0-9]") {
            throw "Python 3.8+ required. Found: $pythonVersion"
        }

        Write-EQ12Log "Python OK: $pythonVersion" "DEBUG"

        # Check required packages
        $requiredPackages = @("requests", "datetime")
        foreach ($package in $requiredPackages) {
            $result = python -c "import $package; print('OK')" 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-EQ12Log "Installing missing package: $package" "WARN"
                python -m pip install $package --quiet

                if ($LASTEXITCODE -ne 0) {
                    throw "Failed to install $package"
                }
            }
        }

        Write-EQ12Log "Python environment ready" "INFO"
        return $true

    } catch {
        Write-EQ12Log "Python environment error: $_" "ERROR"
        return $false
    }
}

function Test-NetworkConnectivity {
    """Test internet connectivity for flight search"""

    Write-EQ12Log "Testing network connectivity..." "DEBUG"

    $testUrls = @(
        "https://www.google.com",
        "https://www.aa.com"
    )

    foreach ($url in $testUrls) {
        try {
            $response = Invoke-WebRequest -Uri $url -TimeoutSec 10 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-EQ12Log "Network OK: $url" "DEBUG"
                return $true
            }
        } catch {
            Write-EQ12Log "Network test failed for $url" "DEBUG"
            continue
        }
    }

    Write-EQ12Log "Network connectivity issues detected" "WARN"
    return $false
}

function Invoke-FlightSearch {
    """Execute the Python flight search script"""

    Write-EQ12Log "Starting Buffalo-Miami flight search..." "INFO"

    $scriptPath = Join-Path $PSScriptRoot "eq12_buffalo_miami_quick_search.py"

    if (-not (Test-Path $scriptPath)) {
        throw "Python script not found: $scriptPath"
    }

    try {
        Write-Host "`n" -NoNewline
        Write-Host "🛫 " -ForegroundColor Blue -NoNewline
        Write-Host "EQ12 BUFFALO-MIAMI FLIGHT SEARCH" -ForegroundColor White
        Write-Host "   American Airlines • December 2025" -ForegroundColor Gray
        Write-Host "   Buffalo NY 14215 Content Empire`n" -ForegroundColor Gray

        # Execute Python script
        $pythonArgs = @($scriptPath)

        # Add arguments based on parameters
        if ($SearchType -eq "Detailed") {
            $pythonArgs += "--detailed"
        } elseif ($SearchType -eq "PriceOnly") {
            $pythonArgs += "--price-only"
        }

        if ($Verbose) {
            $pythonArgs += "--verbose"
        }

        Write-EQ12Log "Executing: python $($pythonArgs -join ' ')" "DEBUG"

        # Run the search
        python @pythonArgs

        if ($LASTEXITCODE -ne 0) {
            throw "Python script execution failed with exit code: $LASTEXITCODE"
        }

        Write-EQ12Log "Flight search completed successfully" "INFO"

        # Post-process results if needed
        if ($OutputFormat -ne "Console") {
            Convert-SearchResults -Format $OutputFormat
        }

    } catch {
        Write-EQ12Log "Flight search error: $_" "ERROR"
        throw
    }
}

function Convert-SearchResults {
    param([string]$Format)

    Write-EQ12Log "Converting results to $Format format..." "DEBUG"

    # Find the latest results file
    $logsPath = Join-Path $PSScriptRoot "..\logs"

    if (Test-Path $logsPath) {
        $latestFile = Get-ChildItem -Path $logsPath -Filter "*buffalo_miami_aa_flights_*.json" |
                      Sort-Object LastWriteTime -Descending |
                      Select-Object -First 1

        if ($latestFile) {
            Write-EQ12Log "Found results: $($latestFile.Name)" "INFO"

            if ($Format -eq "CSV") {
                Convert-JSONToCSV -JsonFile $latestFile.FullName
            } elseif ($Format -eq "JSON") {
                Write-Host "`nJSON Results:" -ForegroundColor Yellow
                Get-Content $latestFile.FullName | Write-Host
            }
        } else {
            Write-EQ12Log "No results file found for conversion" "WARN"
        }
    }
}

function Convert-JSONToCSV {
    param([string]$JsonFile)

    try {
        $jsonData = Get-Content $JsonFile | ConvertFrom-Json
        $csvFile = $JsonFile.Replace('.json', '.csv')

        # Convert cheapest flights to CSV
        if ($jsonData.cheapest_five) {
            $jsonData.cheapest_five | Export-Csv -Path $csvFile -NoTypeInformation
            Write-EQ12Log "CSV results saved: $csvFile" "INFO"
        }
    } catch {
        Write-EQ12Log "CSV conversion error: $_" "WARN"
    }
}

function Show-EQ12Banner {
    """Display EQ12 system banner"""

    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Blue
    Write-Host "                    EQ12 FLIGHT FINDER                    " -ForegroundColor Blue
    Write-Host "              Buffalo NY 14215 Content Empire            " -ForegroundColor Blue
    Write-Host "                                                          " -ForegroundColor Blue
    Write-Host "  Target: American Airlines Buffalo -> Miami Area         " -ForegroundColor White
    Write-Host "  Month:  December 2025                                   " -ForegroundColor White
    Write-Host "  Focus:  Best deals, direct flights, holiday travel     " -ForegroundColor White
    Write-Host "================================================================" -ForegroundColor Blue
    Write-Host ""
}

function Test-Prerequisites {
    """Test all prerequisites before flight search"""

    Write-EQ12Log "Checking prerequisites..." "INFO"

    $checks = @(
        @{ Name = "Python Environment"; Test = { Test-PythonEnvironment } },
        @{ Name = "Network Connectivity"; Test = { Test-NetworkConnectivity } }
    )

    $allPassed = $true

    foreach ($check in $checks) {
        try {
            $result = & $check.Test
            if ($result) {
                Write-Host "✅ $($check.Name)" -ForegroundColor Green
            } else {
                Write-Host "❌ $($check.Name)" -ForegroundColor Red
                $allPassed = $false
            }
        } catch {
            Write-Host "❌ $($check.Name): $_" -ForegroundColor Red
            $allPassed = $false
        }
    }

    if (-not $allPassed) {
        throw "Prerequisites check failed. Please fix errors and try again."
    }

    Write-EQ12Log "All prerequisites passed" "INFO"
}

function Invoke-Cleanup {
    """Cleanup function for script completion"""

    Write-EQ12Log "Cleaning up..." "DEBUG"

    # Reset environment variables if needed
    if ($env:TEMP_EQ12_VARS) {
        Remove-Item env:TEMP_EQ12_VARS -ErrorAction SilentlyContinue
    }

    # Display completion info
    Write-Host "`n" -NoNewline
    Write-Host "🎯 NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "   1. Review the deals above and choose your preferred flight" -ForegroundColor White
    Write-Host "   2. Visit the booking link to complete your reservation" -ForegroundColor White
    Write-Host "   3. Consider booking soon - December prices change frequently" -ForegroundColor White
    Write-Host "   4. Check American Airlines baggage policies" -ForegroundColor White
    Write-Host ""
    Write-Host "📞 Support: EQ12 System - Buffalo NY 14215" -ForegroundColor Gray
    Write-Host ""
}

# MAIN EXECUTION
try {
    # Show system banner
    Show-EQ12Banner

    # Test prerequisites
    Test-Prerequisites

    # Execute flight search
    Invoke-FlightSearch

    # Show completion
    Write-EQ12Log "Flight search process completed successfully" "INFO"

} catch {
    Write-EQ12Log "Script execution failed: $($_.Exception.Message)" "ERROR"
    exit 1

} finally {
    # Cleanup
    Invoke-Cleanup
}
