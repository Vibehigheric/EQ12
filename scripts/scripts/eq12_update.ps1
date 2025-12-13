# Windows Update runner (admin shell)
Write-Host "[UPDATE] Starting Windows Update..." -ForegroundColor Cyan

# Ensure PSWindowsUpdate is available
if (-not (Get-Module -ListAvailable -Name PSWindowsUpdate)) {
    try {
        Write-Host "[UPDATE] Installing NuGet provider (CurrentUser)..." -ForegroundColor Yellow
        Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Scope CurrentUser -Force -ErrorAction SilentlyContinue
    } catch {}
    try {
        Write-Host "[UPDATE] Trusting PSGallery..." -ForegroundColor Yellow
        Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction SilentlyContinue
    } catch {}
    Write-Host "[UPDATE] Installing PSWindowsUpdate (CurrentUser)..." -ForegroundColor Yellow
    Install-Module -Name PSWindowsUpdate -Scope CurrentUser -Force -ErrorAction SilentlyContinue
}

Import-Module PSWindowsUpdate -ErrorAction SilentlyContinue
Write-Host "[UPDATE] Checking updates..." -ForegroundColor Cyan
Get-WindowsUpdate -ErrorAction SilentlyContinue | Out-Null
Write-Host "[UPDATE] Installing updates (will reboot if needed)..." -ForegroundColor Cyan
Install-WindowsUpdate -AcceptAll -AutoReboot -ErrorAction SilentlyContinue
Write-Host "[UPDATE] Windows Update step completed." -ForegroundColor Green
