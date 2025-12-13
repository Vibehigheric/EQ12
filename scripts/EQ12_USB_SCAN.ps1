<#
.SYNOPSIS
    EQ12 USB Scanner - PowerShell Wrapper

.DESCRIPTION
    Runs the VB.NET USB device scanner and processes results
    Can run in scan, monitor, or JSON logging mode

.PARAMETER Mode
    scan     - One-time scan with console output
    monitor  - Continuous monitoring mode
    json     - Output JSON to logs folder

.PARAMETER LogPath
    Override default log path (default: C:\EQ12\logs)

.EXAMPLE
    .\EQ12_USB_SCAN.ps1 -Mode scan
    .\EQ12_USB_SCAN.ps1 -Mode monitor
    .\EQ12_USB_SCAN.ps1 -Mode json

.NOTES
    Author: EQ12 Copilot Workspace Architect
    Date: 2025-11-27
    Requires: Compiled Eq12UsbScanner.exe
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("scan", "monitor", "json")]
    [string]$Mode = "scan",

    [Parameter(Mandatory = $false)]
    [string]$LogPath = "C:\EQ12\logs"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ==================== CONFIGURATION ====================
$script:RepoRoot = "C:\EQ12_BROKEN_20251122_210342"
$script:ScannerExe = Join-Path $RepoRoot "vb_usb_scanner\bin\Release\net8.0\Eq12UsbScanner.exe"
$script:LogsDir = $LogPath

# ==================== BANNER ====================
function Write-Banner {
    Write-Host ""
    Write-Host "=== EQ12 USB DEVICE SCANNER ===" -ForegroundColor Cyan
    Write-Host "Mode: $Mode" -ForegroundColor Yellow
    Write-Host ""
}

# ==================== VALIDATE SCANNER ====================
function Test-Scanner {
    if (-not (Test-Path $script:ScannerExe)) {
        Write-Host "[ERROR] USB Scanner not found at:" -ForegroundColor Red
        Write-Host "  $script:ScannerExe" -ForegroundColor Red
        Write-Host ""
        Write-Host "Build instructions:" -ForegroundColor Yellow
        Write-Host "  1. Open Visual Studio 2022" -ForegroundColor White
        Write-Host "  2. Create new Console App (.NET 8.0)" -ForegroundColor White
        Write-Host "  3. Add UsbDeviceScanner.vb + Program.vb" -ForegroundColor White
        Write-Host "  4. Build solution (Ctrl+Shift+B)" -ForegroundColor White
        Write-Host ""
        exit 1
    }

    Write-Host "[OK] Scanner found: $script:ScannerExe" -ForegroundColor Green
}

# ==================== SCAN MODE ====================
function Invoke-UsbScan {
    Write-Host "[SCAN] Running USB device detection..." -ForegroundColor Cyan
    Write-Host ""

    try {
        & $script:ScannerExe

        Write-Host ""
        Write-Host "[OK] Scan complete" -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] Scan failed: $_" -ForegroundColor Red
        exit 1
    }
}

# ==================== MONITOR MODE ====================
function Invoke-UsbMonitor {
    Write-Host "[MONITOR] Starting USB event monitoring..." -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""

    try {
        & $script:ScannerExe --monitor
    }
    catch {
        Write-Host "[ERROR] Monitor failed: $_" -ForegroundColor Red
        exit 1
    }
}

# ==================== JSON MODE ====================
function Invoke-UsbJsonLog {
    Write-Host "[JSON] Logging USB devices to file..." -ForegroundColor Cyan

    # Ensure logs directory exists
    if (-not (Test-Path $script:LogsDir)) {
        New-Item -Path $script:LogsDir -ItemType Directory -Force | Out-Null
    }

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $logFile = Join-Path $script:LogsDir "usb_scan_$timestamp.json"

    try {
        $jsonOutput = & $script:ScannerExe --json
        $jsonOutput | Out-File -FilePath $logFile -Encoding UTF8

        Write-Host ""
        Write-Host "[OK] Saved to: $logFile" -ForegroundColor Green
        Write-Host ""

        # Display summary
        $devices = $jsonOutput | ConvertFrom-Json
        Write-Host "Devices detected: $($devices.Count)" -ForegroundColor Cyan

        foreach ($dev in $devices) {
            $name = if ($dev.productName) { $dev.productName } else { "Unknown Device" }
            Write-Host "  - $name ($($dev.vendorId):$($dev.productId))" -ForegroundColor White
        }
    }
    catch {
        Write-Host "[ERROR] JSON logging failed: $_" -ForegroundColor Red
        exit 1
    }
}

# ==================== MAIN EXECUTION ====================
Write-Banner
Test-Scanner

switch ($Mode) {
    "scan" {
        Invoke-UsbScan
    }

    "monitor" {
        Invoke-UsbMonitor
    }

    "json" {
        Invoke-UsbJsonLog
    }
}

Write-Host ""
Write-Host "[OK] USB Scanner completed" -ForegroundColor Green
