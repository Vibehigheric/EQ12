# EQ12 Network Repair Tool (Run on M70q)
# Fixes connectivity issues on the Lenovo M70q

Write-Host "🔧 EQ12 Network Repair Tool" -ForegroundColor Cyan
Write-Host "----------------------------"

# 1. Reset Network Stack
Write-Host "1. Resetting Network Stack..." -ForegroundColor Yellow
netsh winsock reset | Out-Null
netsh int ip reset | Out-Null

# 2. Release/Renew DHCP
Write-Host "2. Refreshing IP Address..." -ForegroundColor Yellow
ipconfig /release | Out-Null
ipconfig /renew | Out-Null

# 3. Check Configuration
$ipConfig = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.InterfaceAlias -notlike "*vEthernet*" } | Select-Object -First 1

if ($ipConfig) {
    Write-Host "✅ IP Address Assigned: $($ipConfig.IPAddress)" -ForegroundColor Green
    
    # 4. Test Connectivity
    Write-Host "3. Testing Connectivity..." -ForegroundColor Yellow
    if (Test-Connection -ComputerName 192.168.100.1 -Count 1 -Quiet) {
        Write-Host "✅ Gateway (192.168.100.1) is REACHABLE!" -ForegroundColor Green
    }
    else {
        Write-Error "❌ Gateway (192.168.100.1) is UNREACHABLE."
        Write-Host "👉 Check the ethernet cable."
        Write-Host "👉 Ensure the switch is powered on."
    }
}
else {
    Write-Error "❌ No IP Address assigned. Check physical connection."
}

Write-Host "`nDone."
Start-Sleep -Seconds 5
