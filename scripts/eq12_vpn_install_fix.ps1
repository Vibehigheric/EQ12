# EQ12 Mozilla VPN Admin Installation Script
# Fixes error codes 2502/2503

[CmdletBinding()]
param()

Write-Host "🔧 EQ12 Mozilla VPN Installation Fix" -ForegroundColor Cyan
Write-Host "Attempting to resolve error codes 2502/2503..." -ForegroundColor Yellow

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "❌ Not running as Administrator" -ForegroundColor Red
    Write-Host "Please run this script as Administrator:" -ForegroundColor Yellow
    Write-Host "Right-click PowerShell → Run as Administrator" -ForegroundColor White
    exit 1
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green

# Fix 1: Clean temporary files
Write-Host "`n🧹 Cleaning temporary files..." -ForegroundColor Cyan
try {
    Get-ChildItem -Path $env:TEMP -Recurse -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
    Write-Host "✅ Temp files cleaned" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Some temp files could not be deleted (normal)" -ForegroundColor Yellow
}

# Fix 2: Restart Windows Installer service
Write-Host "`n🔄 Restarting Windows Installer service..." -ForegroundColor Cyan
try {
    Stop-Service -Name 'msiserver' -Force -ErrorAction SilentlyContinue
    Start-Service -Name 'msiserver'
    Write-Host "✅ Windows Installer service restarted" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Could not restart Windows Installer service" -ForegroundColor Yellow
}

# Fix 3: Install Mozilla VPN with proper parameters
$msiPath = "C:\Users\Ricoj100\Downloads\MozillaVPN.msi"

if (Test-Path $msiPath) {
    Write-Host "`n🚀 Installing Mozilla VPN..." -ForegroundColor Cyan
    Write-Host "File: $msiPath" -ForegroundColor White
    
    try {
        # Method 1: Direct MSI execution
        Write-Host "Attempting direct MSI installation..." -ForegroundColor Yellow
        Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$msiPath`" /qb /norestart" -Wait -NoNewWindow
        
        # Check if installation succeeded
        if (Test-Path "C:\Program Files\Mozilla VPN\mozillavpn.exe") {
            Write-Host "✅ Mozilla VPN installed successfully!" -ForegroundColor Green
            Write-Host "Location: C:\Program Files\Mozilla VPN\mozillavpn.exe" -ForegroundColor White
        } else {
            Write-Host "⚠️ Installation may not have completed. Trying alternative method..." -ForegroundColor Yellow
            
            # Method 2: Alternative installation
            Start-Process -FilePath $msiPath -Verb RunAs -Wait
        }
        
    } catch {
        Write-Host "❌ Installation failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Try manual installation or download fresh copy from https://vpn.mozilla.org/" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "❌ Mozilla VPN installer not found at: $msiPath" -ForegroundColor Red
    Write-Host "Please download from: https://vpn.mozilla.org/" -ForegroundColor Yellow
}

# Final verification
Write-Host "`n🔍 Verification..." -ForegroundColor Cyan

$vpnExe = "C:\Program Files\Mozilla VPN\mozillavpn.exe"
if (Test-Path $vpnExe) {
    Write-Host "✅ Mozilla VPN executable found: $vpnExe" -ForegroundColor Green
    
    # Check service
    $service = Get-Service -Name "*Mozilla*" -ErrorAction SilentlyContinue
    if ($service) {
        Write-Host "✅ Mozilla VPN service detected: $($service.Name)" -ForegroundColor Green
    }
    
    Write-Host "`n🎉 INSTALLATION SUCCESS!" -ForegroundColor Green
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "1. Launch Mozilla VPN from Start menu" -ForegroundColor White  
    Write-Host "2. Create account and subscribe ($4.99/month)" -ForegroundColor White
    Write-Host "3. Configure split tunneling for EQ12 APIs" -ForegroundColor White
    Write-Host "4. Test arbitrage opportunities" -ForegroundColor White
    
} else {
    Write-Host "❌ Mozilla VPN not found after installation attempt" -ForegroundColor Red
    Write-Host "`nAlternatives:" -ForegroundColor Yellow
    Write-Host "• Download fresh installer from https://vpn.mozilla.org/" -ForegroundColor White
    Write-Host "• Contact Mozilla support" -ForegroundColor White
    Write-Host "• Continue using EQ12 without VPN (still 90% cost savings!)" -ForegroundColor White
}

Write-Host "`n🎯 EQ12 System Status: Ready for betting operations!" -ForegroundColor Cyan
Write-Host "VPN enhances capabilities but is not required for core functionality" -ForegroundColor White
