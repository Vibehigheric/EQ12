[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$SubnetMask = "192.168.1.0/24",
    
    [Parameter(Mandatory = $false)]
    [int]$TimeoutMs = 1000,
    
    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "$PSScriptRoot\..\logs\network_scan_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
)

Write-Verbose "Starting network device discovery..."
Write-Verbose "Subnet: $SubnetMask"

# Ensure logs directory exists
$LogDir = Split-Path $OutputPath
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Get local network adapters and their IPs
Write-Verbose "Retrieving local network configuration..."
$NetworkAdapters = @()
$LocalIPs = @()

Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object {
    $Adapter = $_
    $IpConfig = Get-NetIPAddress -InterfaceIndex $Adapter.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
    
    if ($IpConfig) {
        $LocalIPs += $IpConfig.IPAddress
        $NetworkAdapters += [PSCustomObject]@{
            Name        = $Adapter.Name
            Description = $Adapter.Description
            IPAddress   = $IpConfig.IPAddress
            Status      = $Adapter.Status
        }
    }
}

Write-Verbose "Found $($NetworkAdapters.Count) active network adapters"

# Discover devices via ARP cache and DHCP
Write-Verbose "Scanning ARP cache for known devices..."
$ArpDevices = @()
$ArpOutput = arp -a
$ArpDevices = $ArpOutput | Select-String '(\d+\.\d+\.\d+\.\d+)' | ForEach-Object {
    $Parts = $_.Line -split '\s+' | Where-Object { $_ }
    if ($Parts.Count -ge 2) {
        [PSCustomObject]@{
            IPAddress = $Parts[0]
            MAC       = $Parts[1]
            Type      = $Parts[2]
            Source    = "ARP"
        }
    }
}

Write-Verbose "Found $($ArpDevices.Count) devices in ARP cache"

# Attempt ping sweep on the subnet
Write-Verbose "Performing ping sweep on subnet $SubnetMask..."
$PingResults = @()

# Parse subnet
$SubnetParts = $SubnetMask -split '\/'
$NetworkAddress = $SubnetParts[0]
$CIDR = [int]$SubnetParts[1]

# Convert IP to integer
function Convert-IPToInt {
    param([string]$IP)
    $Octets = $IP -split '\.'
    return [UInt32]([UInt32]$Octets[0] -shl 24 -bor [UInt32]$Octets[1] -shl 16 -bor [UInt32]$Octets[2] -shl 8 -bor [UInt32]$Octets[3])
}

function Convert-IntToIP {
    param([UInt32]$Int)
    return "$([math]::Floor($Int / 16777216)).$([math]::Floor(($Int % 16777216) / 65536)).$([math]::Floor(($Int % 65536) / 256)).$($Int % 256)"
}

$NetworkInt = Convert-IPToInt $NetworkAddress
$HostBits = 32 - $CIDR
$HostCount = [math]::Pow(2, $HostBits) - 2

# Limit to reasonable number of hosts
$HostCount = [math]::Min($HostCount, 256)

Write-Verbose "Scanning $HostCount addresses in subnet..."

for ($i = 1; $i -le $HostCount; $i++) {
    $IPInt = $NetworkInt + $i
    $IP = Convert-IntToIP $IPInt
    
    # Skip local IPs
    if ($IP -notin $LocalIPs) {
        $PingReply = Test-Connection -ComputerName $IP -Count 1 -ErrorAction SilentlyContinue -Quiet
        
        if ($PingReply) {
            $PingResults += [PSCustomObject]@{
                IPAddress  = $IP
                Responsive = $true
                Source     = "Ping"
            }
        }
    }
}

Write-Verbose "Ping sweep complete. Found $($PingResults.Count) responsive devices"

# Get DNS hostnames
Write-Verbose "Resolving hostnames..."
$AllDevices = @($ArpDevices + $PingResults) | Sort-Object -Property IPAddress -Unique
$AllDevices | ForEach-Object {
    try {
        $HostName = [System.Net.Dns]::GetHostEntry($_.IPAddress).HostName
        $_ | Add-Member -NotePropertyName Hostname -NotePropertyValue $HostName -Force
    }
    catch {
        $_ | Add-Member -NotePropertyName Hostname -NotePropertyValue "Unknown" -Force
    }
}

# Compile final report
$Report = [PSCustomObject]@{
    ScanTime          = Get-Date -Format 'o'
    SubnetScanned     = $SubnetMask
    LocalAdapters     = $NetworkAdapters
    DevicesDiscovered = $AllDevices.Count
    Devices           = $AllDevices
}

# Output to console and file
Write-Host "=== NETWORK DEVICE DISCOVERY REPORT ===" -ForegroundColor Cyan
Write-Host "Scan Time: $($Report.ScanTime)" -ForegroundColor Cyan
Write-Host "Subnet: $SubnetMask" -ForegroundColor Cyan
Write-Host "Total Devices Found: $($Report.DevicesDiscovered)" -ForegroundColor Green
Write-Host ""
Write-Host "ACTIVE NETWORK ADAPTERS:" -ForegroundColor Yellow
$Report.LocalAdapters | Format-Table -AutoSize

Write-Host ""
Write-Host "DISCOVERED DEVICES:" -ForegroundColor Yellow
$Report.Devices | Format-Table -AutoSize IPAddress, Hostname, MAC, Source

# Save to JSON
$Report | ConvertTo-Json | Out-File -FilePath $OutputPath -Encoding UTF8
Write-Host ""
Write-Host "Full report saved to: $OutputPath" -ForegroundColor Green
