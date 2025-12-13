#!/usr/bin/env powershell
# EQ12 XAMPP Quick Setup Script
# This script downloads and sets up XAMPP for the EQ12 platform

param(
    [switch]$Install,
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status
)

$XAMPP_URL = "https://www.apachefriends.org/xampp-files/8.2.12/xampp-windows-x64-8.2.12-0-VS16-installer.exe"
$XAMPP_INSTALLER = "C:\EQ12\xampp-installer.exe"
$XAMPP_PATH = "C:\xampp"

function Write-ColoredOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Install-XAMPP {
    Write-ColoredOutput "🚀 EQ12 XAMPP Installation Starting..." "Green"

    if (Test-Path $XAMPP_PATH) {
        Write-ColoredOutput "✅ XAMPP already installed at $XAMPP_PATH" "Green"
        return
    }

    Write-ColoredOutput "📥 Downloading XAMPP installer..." "Yellow"
    try {
        Invoke-WebRequest -Uri $XAMPP_URL -OutFile $XAMPP_INSTALLER -UseBasicParsing
        Write-ColoredOutput "✅ Download completed" "Green"
    }
    catch {
        Write-ColoredOutput "❌ Failed to download XAMPP: $_" "Red"
        return
    }

    Write-ColoredOutput "🔧 Installing XAMPP (this may take a few minutes)..." "Yellow"
    try {
        # Silent installation
        Start-Process -FilePath $XAMPP_INSTALLER -ArgumentList "/S" -Wait -NoNewWindow
        Write-ColoredOutput "✅ XAMPP installation completed" "Green"

        # Cleanup installer
        Remove-Item $XAMPP_INSTALLER -Force -ErrorAction SilentlyContinue
    }
    catch {
        Write-ColoredOutput "❌ XAMPP installation failed: $_" "Red"
        return
    }
}

function Start-XAMPPServices {
    Write-ColoredOutput "🚀 Starting XAMPP Services..." "Green"

    if (-not (Test-Path "$XAMPP_PATH\xampp-control.exe")) {
        Write-ColoredOutput "❌ XAMPP not found. Run with -Install first." "Red"
        return
    }

    # Start Apache
    Write-ColoredOutput "🌐 Starting Apache..." "Yellow"
    & "$XAMPP_PATH\apache_start.bat"

    # Start MySQL
    Write-ColoredOutput "🗃️ Starting MySQL..." "Yellow"
    & "$XAMPP_PATH\mysql_start.bat"

    Start-Sleep 3
    Test-XAMPPStatus
}

function Stop-XAMPPServices {
    Write-ColoredOutput "🛑 Stopping XAMPP Services..." "Yellow"

    # Stop Apache
    & "$XAMPP_PATH\apache_stop.bat"

    # Stop MySQL
    & "$XAMPP_PATH\mysql_stop.bat"
}

function Test-XAMPPStatus {
    Write-ColoredOutput "🔍 Checking XAMPP Status..." "Cyan"

    # Check Apache
    $apacheProcess = Get-Process -Name "httpd" -ErrorAction SilentlyContinue
    if ($apacheProcess) {
        Write-ColoredOutput "✅ Apache is running (PID: $($apacheProcess.Id -join ', '))" "Green"
    }
    else {
        Write-ColoredOutput "❌ Apache is not running" "Red"
    }

    # Check MySQL
    $mysqlProcess = Get-Process -Name "mysqld" -ErrorAction SilentlyContinue
    if ($mysqlProcess) {
        Write-ColoredOutput "✅ MySQL is running (PID: $($mysqlProcess.Id -join ', '))" "Green"
    }
    else {
        Write-ColoredOutput "❌ MySQL is not running" "Red"
    }

    # Test HTTP connection
    try {
        $response = Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing -TimeoutSec 5
        Write-ColoredOutput "✅ HTTP server responding (Status: $($response.StatusCode))" "Green"
    }
    catch {
        Write-ColoredOutput "❌ HTTP server not responding" "Red"
    }
}

# Main execution
switch ($true) {
    $Install { Install-XAMPP }
    $Start { Start-XAMPPServices }
    $Stop { Stop-XAMPPServices }
    $Status { Test-XAMPPStatus }
    default {
        Write-ColoredOutput "🎯 EQ12 XAMPP Manager" "Green"
        Write-ColoredOutput "Usage:" "White"
        Write-ColoredOutput "  -Install    Download and install XAMPP" "Yellow"
        Write-ColoredOutput "  -Start      Start Apache and MySQL services" "Yellow"
        Write-ColoredOutput "  -Stop       Stop all XAMPP services" "Yellow"
        Write-ColoredOutput "  -Status     Check service status" "Yellow"
        Write-ColoredOutput "" "White"
        Write-ColoredOutput "Example: .\xampp-manager.ps1 -Install" "Cyan"
    }
}
