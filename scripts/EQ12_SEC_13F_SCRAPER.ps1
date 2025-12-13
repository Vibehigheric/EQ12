<#
.SYNOPSIS
    PowerShell wrapper for SEC 13F hedge fund scraper

.DESCRIPTION
    Tracks Citadel and major hedge funds via SEC EDGAR API
    Stores holdings in SQLite database for market intelligence

.PARAMETER Action
    scrape - Download latest 13F filings
    export - Export to JSON
    list - Show recent filings
    report - Generate summary report

.PARAMETER MaxFilings
    Maximum filings per fund (default: 5)

.EXAMPLE
    .\EQ12_SEC_13F_SCRAPER.ps1 -Action scrape
    .\EQ12_SEC_13F_SCRAPER.ps1 -Action list
    .\EQ12_SEC_13F_SCRAPER.ps1 -Action export

.NOTES
    Author: EQ12 System
    Created: 2025-11-27
    Requires: Python 3.8+, requests library
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('scrape', 'export', 'list', 'report')]
    [string]$Action = 'list',
    
    [Parameter(Mandatory = $false)]
    [int]$MaxFilings = 5
)

$ErrorActionPreference = "Stop"

# Paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptDir "eq12_sec_13f_scraper.py"
$LogDir = Join-Path (Split-Path -Parent $ScriptDir) "logs"
$ReportsDir = Join-Path (Split-Path -Parent $ScriptDir) "reports"

# Ensure directories exist
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
New-Item -ItemType Directory -Force -Path $ReportsDir | Out-Null

Write-Host "=== EQ12 SEC 13F Hedge Fund Scraper ===" -ForegroundColor Cyan
Write-Host "Action: $Action" -ForegroundColor Yellow
Write-Host ""

# Build Python command
$PythonArgs = @()

switch ($Action) {
    'scrape' {
        $PythonArgs += "--scrape"
        $PythonArgs += "--max-filings", $MaxFilings
        Write-Host "Scraping latest 13F filings (max $MaxFilings per fund)..." -ForegroundColor Green
    }
    'export' {
        $PythonArgs += "--export"
        Write-Host "Exporting filings to JSON..." -ForegroundColor Green
    }
    'list' {
        $PythonArgs += "--list"
    }
    'report' {
        $PythonArgs += "--list"
        $PythonArgs += "--export"
        Write-Host "Generating comprehensive report..." -ForegroundColor Green
    }
}

try {
    # Execute Python scraper
    & python $PythonScript @PythonArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Success!" -ForegroundColor Green
        
        # Show database location
        $DbPath = Join-Path $LogDir "sec_13f_holdings.db"
        if (Test-Path $DbPath) {
            $DbSize = (Get-Item $DbPath).Length / 1KB
            Write-Host "Database: $DbPath ($([math]::Round($DbSize, 2)) KB)" -ForegroundColor Cyan
        }
        
        # Show export location if exported
        $ExportPath = Join-Path $ReportsDir "sec_13f_export.json"
        if ((Test-Path $ExportPath) -and ($Action -in @('export', 'report'))) {
            $ExportSize = (Get-Item $ExportPath).Length / 1KB
            Write-Host "Export: $ExportPath ($([math]::Round($ExportSize, 2)) KB)" -ForegroundColor Cyan
        }
    }
    else {
        Write-Error "Python script failed with exit code $LASTEXITCODE"
    }
}
catch {
    Write-Error "Failed to execute scraper: $_"
    exit 1
}
