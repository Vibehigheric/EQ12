# EQ12 Smart Network Scanner
# Automatically detects local subnet and scans for devices.

$ErrorActionPreference = "SilentlyContinue"

function Get-LocalIPAddress {
    $ip = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { 
        $_.InterfaceAlias -notlike "*Loopback*" -and 
        $_.InterfaceAlias -notlike "*vEthernet*" -and 
        $_.IPAddress -notlike "169.254.*" 
    } | Select-Object -First 1
    return $ip
}

$localIP = Get-LocalIPAddress
if (-not $localIP) {
    Write-Error "Could not detect local IP address."
    exit 1
}

$ipParts = $localIP.IPAddress.Split('.')
$subnetPrefix = "$($ipParts[0]).$($ipParts[1]).$($ipParts[2])"
$myIP = $localIP.IPAddress

Write-Host "🚀 EQ12 Smart Network Scanner" -ForegroundColor Cyan
Write-Host "--------------------------------"
Write-Host "Local IP: $myIP" -ForegroundColor Green
Write-Host "Subnet:   $subnetPrefix.0/24" -ForegroundColor Green
Write-Host "--------------------------------"

$devices = @()

# 1. ARP Scan (Fastest for local segment)
Write-Host "`n📡 Reading ARP Table..." -ForegroundColor Yellow
$arpEntries = arp -a
$pattern = '\s+({0}\.\d+)\s+([0-9a-fA-F-]+)\s+(\w+)' -f $subnetPrefix
foreach ($line in $arpEntries) {
    if ($line -match $pattern) {
        $ip = $Matches[1]
        $mac = $Matches[2]
        $type = $Matches[3]
        
        if ($ip -eq $myIP) { continue } # Skip self in ARP (usually not there anyway)

        $status = "Online (ARP)"
        $hostname = "Unknown"
        
        try {
            $hostEntry = [System.Net.Dns]::GetHostEntry($ip)
            $hostname = $hostEntry.HostName
        }
        catch {}

        $devices += [PSCustomObject]@{
            IP       = $ip
            MAC      = $mac
            Hostname = $hostname
            Type     = "ARP Discovery"
        }
    }
}

# 2. Ping Sweep (for devices not in ARP yet)
Write-Host "📡 Performing Ping Sweep ($subnetPrefix.1-254)..." -ForegroundColor Yellow
$pingTasks = @()
1..254 | ForEach-Object {
    $target = "$subnetPrefix.$_"
    if ($target -eq $myIP) { return }
    
    # Skip if already found in ARP
    if ($devices.IP -contains $target) { return }

    $pingTasks += [PSCustomObject]@{ IP = $target; Job = Start-Job -ScriptBlock { Test-Connection -ComputerName $args[0] -Count 1 -Quiet } -ArgumentList $target }
}

# Wait for jobs
$pingTasks | ForEach-Object {
    $result = Receive-Job -Job $_.Job -Wait
    if ($result -eq $true) {
        $devices += [PSCustomObject]@{
            IP       = $_.IP
            MAC      = "Unknown"
            Hostname = "Unknown"
            Type     = "Ping Discovery"
        }
        try {
            $hostEntry = [System.Net.Dns]::GetHostEntry($_.IP)
            $devices[-1].Hostname = $hostEntry.HostName
        }
        catch {}
    }
    Remove-Job -Job $_.Job
}

# 3. Add Self
$devices += [PSCustomObject]@{
    IP       = $myIP
    MAC      = (Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1).MacAddress
    Hostname = [System.Net.Dns]::GetHostName()
    Type     = "This Device (Host)"
}

# 4. Display Results
Write-Host "`n📋 Network Scan Results:" -ForegroundColor Cyan
$devices | Sort-Object { [Version]$_.IP } | Format-Table -AutoSize

# 5. Check for 2.5G Switch Hints
# (Unmanaged switches are invisible, but we can check link speed of this device)
$netAdapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | Select-Object -First 1
Write-Host "`n🔌 Local Link Speed Check:" -ForegroundColor Yellow
Write-Host "Interface: $($netAdapter.Name)"
Write-Host "Description: $($netAdapter.InterfaceDescription)"
Write-Host "Link Speed: $($netAdapter.LinkSpeed)"

if ($netAdapter.LinkSpeed -like "*2.5*") {
    Write-Host "✅ 2.5G Link Detected! The switch appears to be working at 2.5Gbps." -ForegroundColor Green
}
elseif ($netAdapter.LinkSpeed -eq "1 Gbps") {
    Write-Host "⚠️ Link is 1 Gbps. Verify cables (Cat5e/Cat6) and NIC capabilities for 2.5G." -ForegroundColor Yellow
}

# 6. Save Log
$logPath = "logs\network_scan_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" | Out-Null }
$devices | ConvertTo-Json | Set-Content -Path $logPath
Write-Host "`n💾 Scan saved to $logPath" -ForegroundColor Gray
