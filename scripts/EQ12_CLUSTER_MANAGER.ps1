[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$PiUser = "ricoj100",
    
    [Parameter(Mandatory=$false)]
    [string]$PiIP = "192.168.1.80",
    
    [Parameter(Mandatory=$false)]
    [string]$ClusterNetwork = "192.168.100.1"
)

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "EQ12 Cluster Network Management" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Network Configuration:" -ForegroundColor Yellow
Write-Host "  Raspberry Pi (SSH): $PiIP" -ForegroundColor Green
Write-Host "  SSH User: $PiUser" -ForegroundColor Green
Write-Host "  EQ12 Cluster Network: $ClusterNetwork" -ForegroundColor Green
Write-Host "  Realtek USB 2.5GbE Adapter: 192.168.100.1, 192.168.100.10" -ForegroundColor Green
Write-Host "  Wi-Fi Network: 192.168.1.x" -ForegroundColor Green
Write-Host ""

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "SSH Connection Commands:" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Connect to Raspberry Pi:" -ForegroundColor Yellow
Write-Host "   ssh $PiUser@$PiIP" -ForegroundColor Cyan
Write-Host ""

Write-Host "2. Check Raspberry Pi Resources:" -ForegroundColor Yellow
Write-Host "   ssh $PiUser@$PiIP 'uname -a'" -ForegroundColor Cyan
Write-Host "   ssh $PiUser@$PiIP 'cat /proc/cpuinfo'" -ForegroundColor Cyan
Write-Host "   ssh $PiUser@$PiIP 'free -h'" -ForegroundColor Cyan
Write-Host ""

Write-Host "3. Check USB Devices on Pi:" -ForegroundColor Yellow
Write-Host "   ssh $PiUser@$PiIP 'lsusb'" -ForegroundColor Cyan
Write-Host ""

Write-Host "4. Check Storage Devices:" -ForegroundColor Yellow
Write-Host "   ssh $PiUser@$PiIP 'lsblk'" -ForegroundColor Cyan
Write-Host ""

Write-Host "5. Check Network Interfaces:" -ForegroundColor Yellow
Write-Host "   ssh $PiUser@$PiIP 'ifconfig'" -ForegroundColor Cyan
Write-Host ""

Write-Host "6. Scan EQ12 Cluster Network (192.168.100.0/24):" -ForegroundColor Yellow
Write-Host "   ssh $PiUser@$PiIP 'nmap -sn 192.168.100.0/24'" -ForegroundColor Cyan
Write-Host ""

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Network Scan Results:" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Scanning local network adapters..." -ForegroundColor Yellow
Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | ForEach-Object {
    $IP = Get-NetIPAddress -InterfaceIndex $_.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
    Write-Host "Adapter: $($_.Description)" -ForegroundColor Green
    Write-Host "  Name: $($_.Name)"
    Write-Host "  Status: $($_.Status)"
    Write-Host "  Speed: $($_.LinkSpeed)"
    if ($IP) {
        Write-Host "  IP: $($IP.IPAddress)"
    }
    Write-Host ""
}

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Device Summary:" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your EQ12 Cluster Network:" -ForegroundColor Yellow
Write-Host "  Main Server: 192.168.100.1 (Realtek USB 2.5GbE)" -ForegroundColor Green
Write-Host "  Gateway/Secondary: 192.168.100.10" -ForegroundColor Green
Write-Host "  Raspberry Pi: 192.168.1.80 (Wi-Fi)" -ForegroundColor Green
Write-Host "  Local Machine: 192.168.1.144 (Wi-Fi)" -ForegroundColor Green
Write-Host ""

Write-Host "Ready to manage EQ12 cluster!" -ForegroundColor Cyan
