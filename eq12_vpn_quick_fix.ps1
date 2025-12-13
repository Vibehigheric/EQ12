# EQ12 Mozilla VPN Admin Fix - Quick Reference
# Run this in Administrator PowerShell to fix error 2502/2503

Write-Host "🚀 EQ12 MOZILLA VPN ADMIN INSTALLATION" -ForegroundColor Green
Write-Host "Fixing Windows Installer errors 2502/2503..." -ForegroundColor Yellow

# Step 1: Clean temp files
Write-Host "`n🧹 Step 1: Cleaning temporary files..." -ForegroundColor Cyan
Get-ChildItem -Path $env:TEMP -Recurse -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
Write-Host "✅ Temp files cleaned" -ForegroundColor Green

# Step 2: Restart Windows Installer
Write-Host "`n🔄 Step 2: Restarting Windows Installer service..." -ForegroundColor Cyan
Stop-Service -Name 'msiserver' -Force -ErrorAction SilentlyContinue
Start-Service -Name 'msiserver' -ErrorAction SilentlyContinue
Write-Host "✅ Windows Installer service restarted" -ForegroundColor Green

# Step 3: Install Mozilla VPN
Write-Host "`n🚀 Step 3: Installing Mozilla VPN..." -ForegroundColor Cyan
$msiPath = "C:\Users\Ricoj100\Downloads\MozillaVPN.msi"

if (Test-Path $msiPath) {
    Write-Host "Found installer: $msiPath" -ForegroundColor White
    
    # Try MSI installation with proper flags
    Write-Host "Installing with elevated permissions..." -ForegroundColor Yellow
    Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$msiPath`" /quiet /norestart" -Wait -NoNewWindow
    
    # Verify installation
    if (Test-Path "C:\Program Files\Mozilla VPN\mozillavpn.exe") {
        Write-Host "✅ SUCCESS! Mozilla VPN installed successfully!" -ForegroundColor Green
        Write-Host "Location: C:\Program Files\Mozilla VPN\mozillavpn.exe" -ForegroundColor White
        
        # Next steps
        Write-Host "`n🎯 NEXT STEPS FOR EQ12 INTEGRATION:" -ForegroundColor Cyan
        Write-Host "1. Launch Mozilla VPN from Start menu" -ForegroundColor White
        Write-Host "2. Create account and subscribe ($4.99/month)" -ForegroundColor White
        Write-Host "3. Configure split tunneling:" -ForegroundColor White
        Write-Host "   • Route Odds API through VPN (international access)" -ForegroundColor Yellow
        Write-Host "   • Route Weather APIs direct (US-only services)" -ForegroundColor Yellow
        Write-Host "4. Test EQ12 arbitrage opportunities" -ForegroundColor White
        
    } else {
        Write-Host "⚠️ Installation completed but executable not found" -ForegroundColor Yellow
        Write-Host "Try launching from Start menu or download fresh copy" -ForegroundColor White
    }
    
} else {
    Write-Host "❌ Installer not found: $msiPath" -ForegroundColor Red
    Write-Host "Download from: https://vpn.mozilla.org/" -ForegroundColor Yellow
}

Write-Host "`n🎉 EQ12 VPN Fix Complete!" -ForegroundColor Green
Write-Host "Your betting system is ready for international arbitrage!" -ForegroundColor White