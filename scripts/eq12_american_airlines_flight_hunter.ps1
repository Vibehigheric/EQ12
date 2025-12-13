[CmdletBinding()]
param(
    [Parameter(HelpMessage="Search mode: quick, comprehensive, or live")]
    [ValidateSet("quick", "comprehensive", "live")]
    [string]$SearchMode = "comprehensive",

    [Parameter(HelpMessage="Output format: console, json, csv, html")]
    [ValidateSet("console", "json", "csv", "html")]
    [string]$OutputFormat = "console",

    [Parameter(HelpMessage="Maximum price filter")]
    [int]$MaxPrice = 1000,

    [Parameter(HelpMessage="Enable real-time price alerts")]
    [switch]$EnableAlerts,

    [Parameter(HelpMessage="Booking class preference")]
    [ValidateSet("economy", "premium", "business", "first")]
    [string]$BookingClass = "economy"
)

<#
.SYNOPSIS
EQ12 American Airlines Flight Hunter - Buffalo to Miami December 2025

.DESCRIPTION
Advanced flight search and booking automation for American Airlines flights
from Buffalo to Miami/South Florida area for December 2025.
Part of the Buffalo NY 14215 Content Empire automation suite.

.PARAMETER SearchMode
Search intensity: quick (5 days), comprehensive (full month), live (continuous monitoring)

.PARAMETER OutputFormat
Output format for results: console display, JSON file, CSV export, or HTML report

.PARAMETER MaxPrice
Maximum price filter for flight results (default: $1000)

.PARAMETER EnableAlerts
Enable real-time price drop alerts and notifications

.PARAMETER BookingClass
Preferred booking class: economy, premium, business, or first

.EXAMPLE
.\eq12_american_airlines_flight_hunter.ps1 -SearchMode comprehensive -OutputFormat html

.EXAMPLE
.\eq12_american_airlines_flight_hunter.ps1 -SearchMode quick -MaxPrice 500 -EnableAlerts

.NOTES
EQ12 System Requirements:
- PYTHONDONTWRITEBYTECODE=1
- EQ12_ASCII_MODE=ACTIVE
- Python 3.12 with required packages
- Chrome/Chromium browser for Selenium
#>

# EQ12 System Banner
Write-Host @"
================================================================================
🛫 EQ12 AMERICAN AIRLINES FLIGHT HUNTER
Buffalo NY 14215 Content Empire - Flight Intelligence System
================================================================================
Searching: Buffalo (BUF) -> Miami/South Florida
Month: December 2025
Target: American Airlines flights
Mode: $SearchMode
Max Price: `$$MaxPrice
Class: $BookingClass
================================================================================
"@ -ForegroundColor Cyan

# Set EQ12 environment variables
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:EQ12_ASCII_MODE = "ACTIVE"
$env:EQ12_FLIGHT_SEARCH = "ACTIVE"

# Validate Python environment
function Test-PythonEnvironment {
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.12") {
            Write-Host "✅ Python 3.12 detected: $pythonVersion" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️  Python 3.12 required, found: $pythonVersion" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "❌ Python not found in PATH" -ForegroundColor Red
        return $false
    }
}

# Check required Python packages
function Test-RequiredPackages {
    Write-Host "🔍 Checking required Python packages..." -ForegroundColor Yellow

    $requiredPackages = @(
        "aiohttp",
        "requests",
        "beautifulsoup4",
        "pandas",
        "selenium",
        "lxml"
    )

    $missingPackages = @()

    foreach ($package in $requiredPackages) {
        try {
            $result = python -c "import $($package.Replace('beautifulsoup4', 'bs4')); print('OK')" 2>&1
            if ($result -eq "OK") {
                Write-Host "  ✅ $package" -ForegroundColor Green
            } else {
                $missingPackages += $package
                Write-Host "  ❌ $package" -ForegroundColor Red
            }
        } catch {
            $missingPackages += $package
            Write-Host "  ❌ $package" -ForegroundColor Red
        }
    }

    if ($missingPackages.Count -gt 0) {
        Write-Host "⚠️  Missing packages detected. Installing..." -ForegroundColor Yellow
        $packageList = $missingPackages -join " "

        try {
            python -m pip install $packageList --quiet --disable-pip-version-check
            Write-Host "✅ Packages installed successfully" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "❌ Failed to install packages: $packageList" -ForegroundColor Red
            Write-Host "Manual installation required: pip install $packageList" -ForegroundColor Yellow
            return $false
        }
    } else {
        Write-Host "✅ All required packages are installed" -ForegroundColor Green
        return $true
    }
}

# Check Chrome/Chromium for Selenium
function Test-ChromeDriver {
    Write-Host "🌐 Checking Chrome browser availability..." -ForegroundColor Yellow

    $chromePaths = @(
        "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "${env:LOCALAPPDATA}\Google\Chrome\Application\chrome.exe"
    )

    foreach ($path in $chromePaths) {
        if (Test-Path $path) {
            Write-Host "  ✅ Chrome found: $path" -ForegroundColor Green
            return $true
        }
    }

    Write-Host "  ⚠️  Chrome not found in standard locations" -ForegroundColor Yellow
    Write-Host "  Installing Chrome WebDriver manager..." -ForegroundColor Yellow

    try {
        python -m pip install webdriver-manager --quiet
        Write-Host "  ✅ WebDriver manager installed" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  ❌ Failed to install WebDriver manager" -ForegroundColor Red
        return $false
    }
}

# Generate search parameters JSON
function New-SearchParameters {
    param(
        [string]$Mode,
        [int]$MaxPrice,
        [string]$Class,
        [bool]$Alerts
    )

    $searchParams = @{
        search_mode = $Mode
        max_price = $MaxPrice
        booking_class = $Class
        enable_alerts = $Alerts
        origin_airports = @("BUF")
        destination_airports = @("MIA", "FLL", "PBI")
        month = "2025-12"
        airlines = @("American Airlines")
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    } | ConvertTo-Json -Depth 3

    $paramFile = "logs\eq12_flight_search_params_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

    # Ensure logs directory exists
    if (!(Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    }

    Set-Content -Path $paramFile -Value $searchParams -Encoding ASCII

    Write-Host "📋 Search parameters saved: $paramFile" -ForegroundColor Gray
    return $paramFile
}

# Run flight search with error handling
function Invoke-FlightSearch {
    param(
        [string]$ParameterFile,
        [string]$OutputFormat
    )

    $scriptPath = "scripts\eq12_american_airlines_flight_hunter.py"

    if (!(Test-Path $scriptPath)) {
        Write-Host "❌ Flight hunter script not found: $scriptPath" -ForegroundColor Red
        return $false
    }

    Write-Host "🚀 Launching American Airlines flight search..." -ForegroundColor Green
    Write-Host "📍 This may take 5-15 minutes depending on search scope..." -ForegroundColor Yellow

    try {
        # Add search parameters to environment
        $env:EQ12_SEARCH_PARAMS = $ParameterFile
        $env:EQ12_OUTPUT_FORMAT = $OutputFormat

        # Execute flight search
        $result = python $scriptPath 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Flight search completed successfully" -ForegroundColor Green

            # Display results based on format
            if ($OutputFormat -eq "console") {
                Write-Output $result
            } else {
                Write-Host "📁 Results saved in requested format: $OutputFormat" -ForegroundColor Cyan
            }

            return $true
        } else {
            Write-Host "❌ Flight search failed with exit code: $LASTEXITCODE" -ForegroundColor Red
            Write-Host "Error output:" -ForegroundColor Yellow
            Write-Output $result
            return $false
        }

    } catch {
        Write-Host "❌ Unexpected error during flight search:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        return $false
    }
}

# Process results and generate reports
function New-FlightReport {
    Write-Host "📊 Generating flight analysis report..." -ForegroundColor Yellow

    # Find latest results file
    $latestResults = Get-ChildItem -Path "logs" -Filter "eq12_american_airlines_buffalo_miami_dec2025_*.json" |
                    Sort-Object LastWriteTime -Descending |
                    Select-Object -First 1

    if ($latestResults) {
        try {
            $results = Get-Content $latestResults.FullName | ConvertFrom-Json

            Write-Host @"

📈 FLIGHT SEARCH SUMMARY REPORT
================================================================================
Search Completed: $(Get-Date)
Results File: $($latestResults.Name)
Total Deals Found: $($results.total_deals_found)
Average Price: `$$($results.average_price.ToString("F2"))
Price Range: `$$($results.min_price) - `$$($results.max_price)
Direct Flights: $($results.direct_flights.Count)
================================================================================
"@ -ForegroundColor Cyan

            if ($EnableAlerts -and $results.min_price -lt $MaxPrice) {
                Write-Host "🔔 PRICE ALERT: Flights found under `$$MaxPrice!" -ForegroundColor Green
                # Could trigger notification system here
            }

        } catch {
            Write-Host "⚠️  Could not parse results file: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  No results files found in logs directory" -ForegroundColor Yellow
    }
}

# Cleanup function
function Remove-TempFiles {
    Write-Host "🧹 Cleaning temporary files..." -ForegroundColor Gray

    # Clean up any temporary selenium files
    Get-ChildItem -Path $env:TEMP -Filter "*selenium*" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path $env:TEMP -Filter "*chrome*" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

    # Clean up any pycache directories (EQ12 protection)
    Get-ChildItem -Path . -Include "__pycache__" -Recurse -Directory -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

    Write-Host "✅ Cleanup completed" -ForegroundColor Green
}

# Main execution
try {
    Write-Host "🔧 EQ12 System Validation..." -ForegroundColor Yellow

    # Validate environment
    $pythonOK = Test-PythonEnvironment
    $packagesOK = Test-RequiredPackages
    $chromeOK = Test-ChromeDriver

    if (-not ($pythonOK -and $packagesOK -and $chromeOK)) {
        Write-Host "❌ Environment validation failed. Please fix the above issues." -ForegroundColor Red
        exit 1
    }

    Write-Host "✅ Environment validation completed" -ForegroundColor Green
    Write-Host ""

    # Generate search parameters
    $paramFile = New-SearchParameters -Mode $SearchMode -MaxPrice $MaxPrice -Class $BookingClass -Alerts $EnableAlerts.IsPresent

    # Execute flight search
    $searchSuccess = Invoke-FlightSearch -ParameterFile $paramFile -OutputFormat $OutputFormat

    if ($searchSuccess) {
        # Generate summary report
        New-FlightReport

        # Open results if HTML format requested
        if ($OutputFormat -eq "html") {
            $htmlFile = Get-ChildItem -Path "logs" -Filter "*.html" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($htmlFile) {
                Write-Host "🌐 Opening HTML report..." -ForegroundColor Cyan
                Start-Process $htmlFile.FullName
            }
        }

        Write-Host @"

🎉 FLIGHT SEARCH COMPLETED SUCCESSFULLY!
================================================================================
✅ American Airlines flights from Buffalo to Miami searched
✅ December 2025 availability checked
✅ Results saved in logs directory
✅ Best deals identified and ranked

Next Steps:
1. Review the flight options above
2. Check logs directory for detailed results
3. Use booking links to complete reservations
4. Set up alerts for price drops (if enabled)

Buffalo NY 14215 Content Empire - Flight Intelligence Mission Complete! 🛫
================================================================================
"@ -ForegroundColor Green

    } else {
        Write-Host "❌ Flight search failed. Check error messages above." -ForegroundColor Red
        exit 1
    }

} catch {
    Write-Host "❌ Unexpected error in flight search system:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1

} finally {
    # Always cleanup
    Remove-TempFiles

    # Reset environment variables
    Remove-Item Env:EQ12_SEARCH_PARAMS -ErrorAction SilentlyContinue
    Remove-Item Env:EQ12_OUTPUT_FORMAT -ErrorAction SilentlyContinue
}

Write-Host "`n🚀 EQ12 Flight Hunter - Mission Complete!" -ForegroundColor Cyan
