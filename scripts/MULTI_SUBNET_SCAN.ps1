# Multi-subnet network scanner
Write-Host "===== MULTI-SUBNET NETWORK SCANNER =====" -ForegroundColor Cyan
Write-Host ""

# Define subnets to scan
$Subnets = @(
    @{Name = "Realtek USB 2.5GbE"; Prefix = "192.168.100"; Start = 1; End = 254 },
    @{Name = "Wi-Fi (192.168.1.x)"; Prefix = "192.168.1"; Start = 1; End = 254 },
    @{Name = "VPN (10.144.38.x)"; Prefix = "10.144.38"; Start = 1; End = 254 },
    @{Name = "Hyper-V (172.25.32.x)"; Prefix = "172.25.32"; Start = 1; End = 254 }
)

$AllDevices = @()

foreach ($Subnet in $Subnets) {
    Write-Host "Scanning $($Subnet.Name): $($Subnet.Prefix).0/24..." -ForegroundColor Yellow
    
    $SubnetDevices = @()
    
    for ($i = $Subnet.Start; $i -le $Subnet.End; $i++) {
        $IP = "$($Subnet.Prefix).$i"
        
        if (Test-Connection -ComputerName $IP -Count 1 -Quiet -ErrorAction SilentlyContinue) {
            Write-Host "  FOUND: $IP" -ForegroundColor Green
            
            $Hostname = "N/A"
            try {
                $Hostname = [System.Net.Dns]::GetHostEntry($IP).HostName
            }
            catch {
                $Hostname = "Unable to resolve"
            }
            
            $Device = [PSCustomObject]@{
                Subnet    = $Subnet.Name
                IPAddress = $IP
                Hostname  = $Hostname
                Timestamp = (Get-Date).ToString()
            }
            
            $SubnetDevices += $Device
            $AllDevices += $Device
        }
    }
    
    Write-Host "  Found $($SubnetDevices.Count) device(s) on this subnet" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "===== SCAN RESULTS =====" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total devices found: $($AllDevices.Count)" -ForegroundColor Green
Write-Host ""

if ($AllDevices.Count -gt 0) {
    $AllDevices | Format-Table -AutoSize -Property Subnet, IPAddress, Hostname
    
    Write-Host ""
    Write-Host "===== ACTIVE NETWORK INTERFACES =====" -ForegroundColor Cyan
    Write-Host ""
    Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object {
        $IP = Get-NetIPAddress -InterfaceIndex $_.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
        Write-Host "$($_.Description)" -ForegroundColor Yellow
        Write-Host "  Name: $($_.Name)"
        Write-Host "  Status: $($_.Status)"
        if ($IP) {
            Write-Host "  IP: $($IP.IPAddress)"
        }
        Write-Host ""
    }
}

Write-Host "Scan completed!" -ForegroundColor Cyan
