[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$NetworkPrefix = "192.168.100",
    
    [Parameter(Mandatory = $false)]
    [int]$StartIP = 1,
    
    [Parameter(Mandatory = $false)]
    [int]$EndIP = 254,
    
    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "$PSScriptRoot\..\logs\network_scan_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
)

Write-Host "=" * 60
Write-Host "EQ12 Network Device Scanner (PowerShell 5.1 Compatible)" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# Ensure logs directory exists
$LogDir = Split-Path $OutputPath
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

Write-Host "Network Prefix: $NetworkPrefix.x" -ForegroundColor Green
Write-Host "Scanning range: $NetworkPrefix.$StartIP - $NetworkPrefix.$EndIP" -ForegroundColor Green
Write-Host ""

$DiscoveredDevices = @()
$Timestamp = Get-Date

Write-Host "Scanning for active hosts..." -ForegroundColor Yellow

for ($i = $StartIP; $i -le $EndIP; $i++) {
    $IP = "$NetworkPrefix.$i"
    
    # Use Test-Connection with -Quiet for boolean result (PowerShell 5.1 compatible)
    if (Test-Connection -ComputerName $IP -Count 1 -Quiet -ErrorAction SilentlyContinue) {
        Write-Host "✓ Found: $IP" -ForegroundColor Green
        
        # Try to resolve hostname
        $Hostname = "N/A"
        try {
            $Hostname = [System.Net.Dns]::GetHostEntry($IP).HostName
        }
        catch {
            $Hostname = "Unable to resolve"
        }
        
        # Try to get MAC address from ARP cache
        $MAC = "N/A"
        try {
            $ArpResult = arp -a | Select-String $IP
            if ($ArpResult) {
                $MacMatch = $ArpResult[0] -match '([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})'
                if ($MacMatch) {
                    $MAC = $Matches[0]
                }
            }
        }
        catch {
            $MAC = "Unable to retrieve"
        }
        
        $Device = [PSCustomObject]@{
            IPAddress    = $IP
            Hostname     = $Hostname
            MACAddress   = $MAC
            Timestamp    = $Timestamp
            ResponseTime = "1 ms"
            Status       = "Active"
        }
        
        $DiscoveredDevices += $Device
    }
    else {
        Write-Host "✗ No response: $IP" -ForegroundColor Gray -NoNewline
        Write-Host " (skipped)" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "=" * 60
Write-Host "SCAN RESULTS" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

if ($DiscoveredDevices.Count -gt 0) {
    Write-Host "Found $($DiscoveredDevices.Count) active device(s):" -ForegroundColor Green
    Write-Host ""
    
    $DiscoveredDevices | Format-Table -AutoSize -Property @(
        @{Label = 'IP Address'; Expression = { $_.IPAddress } },
        @{Label = 'Hostname'; Expression = { $_.Hostname } },
        @{Label = 'MAC Address'; Expression = { $_.MACAddress } },
        @{Label = 'Status'; Expression = { $_.Status } }
    )
    
    Write-Host ""
    Write-Host "Detailed results saved to:" -ForegroundColor Green
    Write-Host $OutputPath
    
    # Save JSON output
    $DiscoveredDevices | ConvertTo-Json | Out-File -FilePath $OutputPath -Encoding UTF8
    Write-Host "JSON file created successfully"
}
else {
    Write-Host "No active devices found on network." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 60
Write-Host "Additional Network Info:" -ForegroundColor Cyan
Write-Host "=" * 60

Write-Host ""
Write-Host "Local Network Adapters:" -ForegroundColor Green
Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object {
    $IP = Get-NetIPAddress -InterfaceIndex $_.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
    Write-Host "  Name: $($_.Name)"
    Write-Host "  Description: $($_.Description)"
    Write-Host "  IP Address: $($IP.IPAddress)"
    Write-Host "  Status: $($_.Status)"
    Write-Host ""
}

Write-Host "ARP Cache (Known Devices):" -ForegroundColor Green
arp -a | Select-String "Internet Address" -Context 0, 20 | ForEach-Object {
    if ($_ -match "Interface: .* --- ") {
        Write-Host "  $($_.Line.Trim())"
    }
}

Write-Host ""
Write-Host "Scan completed at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
