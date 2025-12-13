$Subnets = @("192.168.1.", "192.168.100.")
$Start = 1
$End = 254

Write-Host "Starting Device Discovery..." -ForegroundColor Cyan

$FoundDevices = @()

foreach ($Subnet in $Subnets) {
    Write-Host "Scanning subnet ${Subnet}0/24..." -ForegroundColor Yellow
    $PingTasks = @()
    
    # Launch async pings
    for ($i = $Start; $i -le $End; $i++) {
        $IP = "${Subnet}${i}"
        $PingTasks += [PSCustomObject]@{ IP = $IP; Task = [System.Net.NetworkInformation.Ping]::new().SendPingAsync($IP, 100) }
    }

    # Process results
    foreach ($Item in $PingTasks) {
        try {
            $Result = $Item.Task.Result
            if ($Result.Status -eq "Success") {
                # Filter out non-LAN IPs (just in case)
                if ($Item.IP -notmatch "^(192\.168|10\.|172\.(1[6-9]|2[0-9]|3[0-1]))") {
                    continue
                }

                $Hostname = "Unknown"
                try {
                    $HostEntry = [System.Net.Dns]::GetHostEntry($Item.IP)
                    $Hostname = $HostEntry.HostName
                }
                catch {
                    # Hostname resolution failed
                }

                Write-Host "  [+] Found: $($Item.IP) ($Hostname)" -ForegroundColor Green
                $FoundDevices += [PSCustomObject]@{ IP = $Item.IP; Hostname = $Hostname }
            }
        }
        catch {
            # Ping failed or timeout
        }
    }
}

# Also grab ARP table and filter it
Write-Host "Scanning ARP table for cached devices..." -ForegroundColor Yellow
$ArpEntries = arp -a | Select-String -Pattern "\s+([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\s+"
foreach ($Entry in $ArpEntries) {
    if ($Entry -match "([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})") {
        $IP = $matches[1]
        # Filter for RFC1918 only
        if ($IP -match "^(192\.168|10\.|172\.(1[6-9]|2[0-9]|3[0-1]))") {
            if (-not ($FoundDevices | Where-Object { $_.IP -eq $IP })) {
                Write-Host "  [+] Found via ARP: $IP" -ForegroundColor Green
                $FoundDevices += [PSCustomObject]@{ IP = $IP; Hostname = "ARP-Cached" }
            }
        }
    }
}

$FoundDevices | ConvertTo-Json | Set-Content "logs/discovery_report.json"
Write-Host "Discovery complete. Saved to logs/discovery_report.json" -ForegroundColor Cyan
