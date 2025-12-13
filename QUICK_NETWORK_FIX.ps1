param([switch]$AsAdmin)

if (-not $AsAdmin) {
    Write-Host "Restarting as Administrator..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`" -AsAdmin" -Verb RunAs
    exit
}

Write-Host "=== EQ12 Quick Network Fix ===" -ForegroundColor Cyan
Write-Host "Fixing DHCP and static IP configuration..." -ForegroundColor Yellow

try {
    # Disable DHCP on IPv4
    Write-Host "1. Disabling DHCP..." -ForegroundColor Green
    Set-NetIPInterface -InterfaceAlias "Ethernet 3" -AddressFamily IPv4 -Dhcp Disabled -ErrorAction Stop
    
    # Remove any existing IP
    Write-Host "2. Clearing existing IP..." -ForegroundColor Green
    Remove-NetIPAddress -InterfaceAlias "Ethernet 3" -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
    
    # Set static IP
    Write-Host "3. Setting static IP (192.168.100.1/24)..." -ForegroundColor Green
    New-NetIPAddress -InterfaceAlias "Ethernet 3" -IPAddress "192.168.100.1" -PrefixLength 24 -ErrorAction Stop
    
    # Enable adapter
    Write-Host "4. Enabling adapter..." -ForegroundColor Green
    Enable-NetAdapter -Name "Ethernet 3" -ErrorAction SilentlyContinue
    
    Write-Host "`n Configuration successful!" -ForegroundColor Green
    
    # Test configuration
    Write-Host "`n5. Testing configuration..." -ForegroundColor Green
    $ip = Get-NetIPAddress -InterfaceAlias "Ethernet 3" -AddressFamily IPv4 -ErrorAction SilentlyContinue
    if ($ip) {
        Write-Host "   Host IP: $($ip.IPAddress)/$($ip.PrefixLength)" -ForegroundColor Green
    }
    
    # Test Pi
    Write-Host "`n6. Testing Pi connectivity..." -ForegroundColor Green
    $ping = Test-Connection -ComputerName "192.168.100.2" -Count 1 -Quiet -ErrorAction SilentlyContinue
    if ($ping) {
        Write-Host "    Pi responds!" -ForegroundColor Green
    }
    else {
        Write-Host "    Pi not responding (needs configuration)" -ForegroundColor Yellow
    }
    
}
catch {
    Write-Host " Error: $($_.Exception.Message)" -ForegroundColor Red
    
    # Try netsh fallback
    Write-Host "`nTrying netsh fallback..." -ForegroundColor Yellow
    $result = netsh interface ip set address "Ethernet 3" static 192.168.100.1 255.255.255.0
    if ($LASTEXITCODE -eq 0) {
        Write-Host " Netsh configuration successful!" -ForegroundColor Green
    }
    else {
        Write-Host " Netsh also failed" -ForegroundColor Red
    }
}

Write-Host "`nPress any key to close..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")