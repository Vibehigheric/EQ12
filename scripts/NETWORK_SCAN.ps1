[CmdletBinding()]
param(
    [string]$NetworkPrefix = "192.168.100",
    [int]$StartIP = 1,
    [int]$EndIP = 254,
    [string]$OutputPath = "c:\EQ12_BROKEN_20251122_210342\logs\network_scan.json"
)

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Network Device Scanner" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path "c:\EQ12_BROKEN_20251122_210342\logs")) {
    New-Item -ItemType Directory -Path "c:\EQ12_BROKEN_20251122_210342\logs" -Force | Out-Null
}

Write-Host "Scanning: $NetworkPrefix.0/24" -ForegroundColor Green
Write-Host ""

$DiscoveredDevices = @()
$ScanStart = Get-Date

for ($i = $StartIP; $i -le $EndIP; $i++) {
    $IP = "$NetworkPrefix.$i"
    $Percent = [math]::Round(($i - $StartIP) / ($EndIP - $StartIP) * 100)
    Write-Progress -Activity "Network Scan" -Status "Scanning $IP" -PercentComplete $Percent
    
    if (Test-Connection -ComputerName $IP -Count 1 -Quiet -ErrorAction SilentlyContinue) {
        Write-Host "FOUND: $IP" -ForegroundColor Green
        
        $Hostname = "N/A"
        try {
            $Hostname = [System.Net.Dns]::GetHostEntry($IP).HostName
        }
        catch {
            $Hostname = "Unable to resolve"
        }
        
        $MAC = "N/A"
        try {
            $ArpResult = arp -a | Select-String $IP
            if ($ArpResult) {
                $Parts = $ArpResult[0] -split '\s+'
                if ($Parts.Count -ge 2) {
                    $MAC = $Parts[1]
                }
            }
        }
        catch {
            $MAC = "Unable to retrieve"
        }
        
        $Device = [PSCustomObject]@{
            IPAddress  = $IP
            Hostname   = $Hostname
            MACAddress = $MAC
            Timestamp  = (Get-Date).ToString()
            Status     = "Active"
        }
        
        $DiscoveredDevices += $Device
    }
}

Write-Progress -Activity "Network Scan" -Completed

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "RESULTS" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

if ($DiscoveredDevices.Count -gt 0) {
    Write-Host "Found $($DiscoveredDevices.Count) active device(s)" -ForegroundColor Green
    Write-Host ""
    
    $DiscoveredDevices | Format-Table -AutoSize
    
    $DiscoveredDevices | ConvertTo-Json | Out-File -FilePath $OutputPath -Encoding UTF8
    Write-Host ""
    Write-Host "Results saved to: $OutputPath" -ForegroundColor Green
}
else {
    Write-Host "No devices found." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Network Adapters" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object {
    $IP = Get-NetIPAddress -InterfaceIndex $_.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
    Write-Host "Name: $($_.Name)" -ForegroundColor Yellow
    Write-Host "  Description: $($_.Description)"
    Write-Host "  IP: $($IP.IPAddress)"
    Write-Host "  Status: $($_.Status)"
    Write-Host ""
}

$ScanEnd = Get-Date
$Duration = $ScanEnd - $ScanStart
Write-Host "Scan completed in $($Duration.TotalSeconds) seconds" -ForegroundColor Cyan
