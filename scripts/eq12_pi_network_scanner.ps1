#Requires -Version 5.0
<#
.SYNOPSIS
    EQ12 Raspberry Pi Network Scanner
.DESCRIPTION
    Scans local networks to find Raspberry Pi devices and test SSH connectivity
.PARAMETER TargetNetworks
    Array of network ranges to scan (default: common ranges)
#>

[CmdletBinding()]
param(
    [string[]]$TargetNetworks = @("192.168.1.0/24", "192.168.0.0/24", "192.168.100.0/24", "10.0.0.0/24")
)

function Test-SSHConnection {
    param([string]$IPAddress)
    try {
        $ssh = Test-NetConnection -ComputerName $IPAddress -Port 22 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue -InformationLevel Quiet
        return $ssh.TcpTestSucceeded
    }
    catch {
        return $false
    }
}

function Get-NetworkHosts {
    param([string]$Network)
    
    # Parse network (e.g., "192.168.1.0/24")
    $parts = $Network -split "/"
    $baseIP = $parts[0]
    $prefix = [int]$parts[1]
    
    # For /24 networks, scan .1 to .254
    if ($prefix -eq 24) {
        $baseOctets = $baseIP -split "\."
        $networkBase = "$($baseOctets[0]).$($baseOctets[1]).$($baseOctets[2])"
        
        $hosts = @()
        for ($i = 1; $i -le 254; $i++) {
            $hosts += "$networkBase.$i"
        }
        return $hosts
    }
    
    return @()
}

Write-Host ""
Write-Host " EQ12 RASPBERRY PI NETWORK SCANNER" -ForegroundColor Cyan
Write-Host "Scanning for Pi devices with SSH enabled..." -ForegroundColor Yellow
Write-Host ""

$foundDevices = @()
$totalScanned = 0

foreach ($network in $TargetNetworks) {
    Write-Host "Scanning network: $network" -ForegroundColor Gray
    $hosts = Get-NetworkHosts -Network $network
    
    foreach ($ip in $hosts) {
        $totalScanned++
        
        # Quick ping test first
        if (Test-Connection -ComputerName $ip -Count 1 -Quiet -ErrorAction SilentlyContinue) {
            Write-Host "  Testing $ip..." -NoNewline -ForegroundColor White
            
            if (Test-SSHConnection -IPAddress $ip) {
                Write-Host "  SSH FOUND!" -ForegroundColor Green
                
                $device = [PSCustomObject]@{
                    IPAddress = $ip
                    Network = $network
                    SSHPort = 22
                    Status = "SSH Ready"
                }
                $foundDevices += $device
            }
            else {
                Write-Host "  Alive (no SSH)" -ForegroundColor Yellow
            }
        }
        
        # Progress indicator every 50 IPs
        if ($totalScanned % 50 -eq 0) {
            Write-Host "  Scanned $totalScanned hosts..." -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host " SCAN RESULTS" -ForegroundColor Cyan
Write-Host "Total hosts scanned: $totalScanned" -ForegroundColor Gray
Write-Host "Devices with SSH: $($foundDevices.Count)" -ForegroundColor Yellow

if ($foundDevices.Count -gt 0) {
    Write-Host ""
    Write-Host "SSH-enabled devices found:" -ForegroundColor Green
    $foundDevices | Format-Table IPAddress, Network, Status -AutoSize
    
    Write-Host ""
    Write-Host " NEXT STEPS:" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($device in $foundDevices) {
        Write-Host "Test connection to $($device.IPAddress):" -ForegroundColor Yellow
        Write-Host "ssh ricoj100@$($device.IPAddress)" -ForegroundColor Green
        Write-Host "Password: CLUSTER_PASSWORD_PLACEHOLDER" -ForegroundColor White
        Write-Host ""
    }
    
    Write-Host "Once connected, configure static IP:" -ForegroundColor Cyan
    Write-Host "sudo nano /etc/dhcpcd.conf" -ForegroundColor Green
    Write-Host ""
    Write-Host "Add these lines:" -ForegroundColor Yellow
    Write-Host "interface eth0" -ForegroundColor White
    Write-Host "static ip_address=192.168.100.2/24" -ForegroundColor White
    Write-Host "static routers=192.168.100.1" -ForegroundColor White
    Write-Host "static domain_name_servers=8.8.8.8 8.8.4.4" -ForegroundColor White
}
else {
    Write-Host ""
    Write-Host " No SSH-enabled devices found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "1. Verify Pi is powered on and booted" -ForegroundColor White
    Write-Host "2. Check if Pi is connected to different network" -ForegroundColor White
    Write-Host "3. Verify SSH was enabled in Pi Imager" -ForegroundColor White
    Write-Host "4. Try connecting Pi directly to EQ12 with Ethernet" -ForegroundColor White
}
