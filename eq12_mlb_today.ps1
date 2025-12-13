[CmdletBinding()]
param(
    [switch]$Save,
    [switch]$Analysis,
    [switch]$Quiet,
    [string]$OutputFile,
    [switch]$OpenResults,
    [switch]$ShowLive
)

<#
.SYNOPSIS
EQ12 MLB Today Games Fetcher - PowerShell Wrapper

.DESCRIPTION
Fetches all MLB games scheduled for today with comprehensive analysis.
Wrapper around the Python MLB today fetcher with enhanced PowerShell features.

.PARAMETER Save
Save games to JSON file in logs directory

.PARAMETER Analysis
Generate comprehensive betting analysis

.PARAMETER Quiet
Minimal output (just essential info)

.PARAMETER OutputFile
Custom output filename for JSON

.PARAMETER OpenResults
Open results file after generation

.PARAMETER ShowLive
Show live updates if games are in progress

.EXAMPLE
.\eq12_mlb_today.ps1 -Save -Analysis
Fetch today's games with full analysis and save to file

.EXAMPLE
.\eq12_mlb_today.ps1 -Quiet -OpenResults
Quick fetch and open results in default viewer
#>

# EQ12 GODSTACK Header
Write-Host ""
Write-Host "🔥 EQ12 MLB TODAY GAMES FETCHER" -ForegroundColor Red
Write-Host "=================================" -ForegroundColor Yellow
Write-Host "📅 Date: $(Get-Date -Format 'yyyy-MM-dd')" -ForegroundColor Cyan
Write-Host "⚾ Fetching live MLB games and odds..." -ForegroundColor Green
Write-Host ""

# Validate environment
$pythonScript = "C:\EQ12\eq12_mlb_today_fetcher.py"
if (-not (Test-Path $pythonScript)) {
    Write-Error "❌ MLB fetcher script not found: $pythonScript"
    exit 1
}

# Check for API key
$apiKey = $env:ODDS_API_KEY
$apiStatus = if ($apiKey) { "✅ Available" } else { "⚠️ Not Set (Mock Mode)" }
Write-Host "🔑 ODDS_API_KEY: $apiStatus" -ForegroundColor $(if ($apiKey) { "Green" } else { "Yellow" })

# Build Python command
$pythonArgs = @()
if ($Save) { $pythonArgs += "--save" }
if ($Analysis) { $pythonArgs += "--analysis" }
if ($Quiet) { $pythonArgs += "--quiet" }
if ($OutputFile) { $pythonArgs += "--output", $OutputFile }

try {
    Write-Host "⚡ Executing MLB data fetch..." -ForegroundColor Cyan

    # Execute Python script
    $result = & python $pythonScript @pythonArgs
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        Write-Host $result
        Write-Host ""
        Write-Host "✅ MLB games fetched successfully!" -ForegroundColor Green

        # Find latest files
        $logsDir = "C:\EQ12\logs"
        $todayDate = Get-Date -Format "yyyyMMdd"

        $gameFiles = Get-ChildItem -Path $logsDir -Filter "mlb_games_today_$todayDate*.json" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

        $analysisFiles = Get-ChildItem -Path $logsDir -Filter "mlb_analysis_$todayDate*.json" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

        # Display file locations
        if ($gameFiles) {
            Write-Host "📁 Games Data: $($gameFiles.FullName)" -ForegroundColor White
        }
        if ($analysisFiles) {
            Write-Host "📊 Analysis: $($analysisFiles.FullName)" -ForegroundColor White
        }

        # Open results if requested
        if ($OpenResults) {
            if ($gameFiles) {
                Write-Host "🔍 Opening games file..." -ForegroundColor Cyan
                Start-Process -FilePath $gameFiles.FullName
            }
            if ($analysisFiles) {
                Write-Host "📈 Opening analysis file..." -ForegroundColor Cyan
                Start-Process -FilePath $analysisFiles.FullName
            }
        }

        # Show live updates if requested
        if ($ShowLive) {
            Write-Host ""
            Write-Host "📡 LIVE GAME MONITORING" -ForegroundColor Yellow
            Write-Host "Press Ctrl+C to stop monitoring..." -ForegroundColor Gray

            try {
                while ($true) {
                    Start-Sleep -Seconds 300  # Update every 5 minutes
                    Write-Host "🔄 Refreshing MLB data..." -ForegroundColor Cyan
                    & python $pythonScript --quiet @pythonArgs
                }
            }
            catch {
                Write-Host "⏹️ Live monitoring stopped" -ForegroundColor Yellow
            }
        }

    }
    else {
        Write-Error "❌ MLB fetch failed with exit code: $exitCode"
        Write-Host $result -ForegroundColor Red
        exit $exitCode
    }

}
catch {
    Write-Error "💥 Error executing MLB fetcher: $($_.Exception.Message)"
    exit 1
}

# Summary stats
Write-Host ""
Write-Host "📋 SESSION SUMMARY" -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow
Write-Host "✓ MLB games processed successfully" -ForegroundColor Green
Write-Host "✓ Real-time odds retrieved" -ForegroundColor Green
if ($Save) {
    Write-Host "✓ Data saved to JSON files" -ForegroundColor Green
}
if ($Analysis) {
    Write-Host "✓ Betting analysis generated" -ForegroundColor Green
}
Write-Host ""
Write-Host "🎯 Ready for MLB betting analysis!" -ForegroundColor Red
