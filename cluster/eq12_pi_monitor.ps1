# EQ12 Pi Connection Monitor
# Real-time monitoring of Pi connectivity status

[CmdletBinding()]
param(
    [string]$PiIP = "192.168.100.2",
    [string]$HostIP = "192.168.100.1", 
    [int]$IntervalSeconds = 5,
    [switch]$Continuous,
    [switch]$ShowDetailedInfo
)

function Test-PiStatus {
    param([string]$IP)
    
    $Timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$Timestamp] " -NoNewline -ForegroundColor Gray
    
    # Test ping
    $PingResult = Test-Connection -ComputerName $IP -Count 1 -Quiet -ErrorAction SilentlyContinue
    if ($PingResult) {
        Write-Host "PING: OK " -NoNewline -ForegroundColor Green
        
        # Test SSH
        $SSHTest = Test-NetConnection -ComputerName $IP -Port 22 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        if ($SSHTest.TcpTestSucceeded) {
            Write-Host "SSH: OK " -NoNewline -ForegroundColor Green
            
            # Show ping time if available
            $PingTime = (Test-Connection -ComputerName $IP -Count 1 -ErrorAction SilentlyContinue).ResponseTime
            if ($PingTime) {
                Write-Host "($($PingTime)ms)" -ForegroundColor Cyan
            }
            else {
                Write-Host "(<1ms)" -ForegroundColor Cyan
            }
            
            return $true
        }
        else {
            Write-Host "SSH: FAIL" -ForegroundColor Red
            return $false
        }
    }
    else {
        Write-Host "PING: FAIL SSH: N/A" -ForegroundColor Red
        return $false
    }
}

function Show-NetworkInfo {
    Write-Host "`n=== EQ12 Network Status ===" -ForegroundColor Cyan
    
    # EQ12 adapter status
    $Adapter = Get-NetAdapter | Where-Object { $_.Name -eq "Ethernet 3" }
    if ($Adapter) {
        $IPConfig = Get-NetIPAddress -InterfaceAlias $Adapter.Name -AddressFamily IPv4 -ErrorAction SilentlyContinue
        Write-Host "EQ12 Adapter: $($Adapter.Name)" -ForegroundColor White
        Write-Host "  Status: $($Adapter.Status)" -ForegroundColor $(if ($Adapter.Status -eq "Up") { "Green" } else { "Red" })
        Write-Host "  Speed: $($Adapter.LinkSpeed)" -ForegroundColor White
        Write-Host "  IP: $($IPConfig.IPAddress -join ', ')" -ForegroundColor White
    }
    
    # Route info
    $Route = Get-NetRoute -DestinationPrefix "192.168.100.0/24" -ErrorAction SilentlyContinue
    if ($Route) {
        Write-Host "Route to Pi: $($Route.DestinationPrefix) via $($Route.InterfaceAlias)" -ForegroundColor White
    }
    
    # ARP entries
    $ARPEntries = & arp -a | Select-String "192.168.100"
    Write-Host "ARP Entries:" -ForegroundColor White
    if ($ARPEntries) {
        $ARPEntries | ForEach-Object { Write-Host "  $($_.Line)" -ForegroundColor Gray }
    }
    else {
        Write-Host "  No Pi devices found in ARP table" -ForegroundColor Yellow
    }
    
    Write-Host "=========================" -ForegroundColor Cyan
}

function Show-PiSetupReminder {
    Write-Host "`n Pi Configuration Reminder:" -ForegroundColor Yellow
    Write-Host "If Pi is not responding, ensure it's configured with:" -ForegroundColor White
    Write-Host "   Static IP: $PiIP/24" -ForegroundColor White
    Write-Host "   Gateway: $HostIP" -ForegroundColor White  
    Write-Host "   DNS: 8.8.8.8" -ForegroundColor White
    Write-Host "   SSH enabled" -ForegroundColor White
    Write-Host "`nConfiguration guide: C:\EQ12\cluster\PI_NETWORK_CONFIG_GUIDE.md" -ForegroundColor Cyan
}

# Show initial network info
if ($ShowDetailedInfo) {
    Show-NetworkInfo
}

Write-Host " Monitoring Pi connectivity at $PiIP..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Gray

$SuccessCount = 0
$FailCount = 0
$FirstSuccess = $false

do {
    $Result = Test-PiStatus -IP $PiIP
    
    if ($Result) {
        $SuccessCount++
        if (-not $FirstSuccess) {
            $FirstSuccess = $true
            Write-Host "`n SUCCESS! Pi is now accessible!" -ForegroundColor Green
            Write-Host " Ready for cluster integration" -ForegroundColor Green
            Write-Host "`nNext step:" -ForegroundColor Cyan
            Write-Host "python C:\EQ12\scripts\eq12_raspberry_pi_cluster_manager.py --action add-node --ip $PiIP --username ricoj100 --password 102120sRO1!" -ForegroundColor Yellow
            
            if (-not $Continuous) {
                Write-Host "`nConnection established! Exiting monitor..." -ForegroundColor Green
                break
            }
        }
    }
    else {
        $FailCount++
        
        # Show setup reminder after several failures
        if ($FailCount -eq 5 -and -not $FirstSuccess) {
            Show-PiSetupReminder
        }
    }
    
    if ($Continuous -or -not $FirstSuccess) {
        Start-Sleep -Seconds $IntervalSeconds
    }
    
} while ($Continuous -or -not $FirstSuccess)

Write-Host "`n Session Summary:" -ForegroundColor Cyan
Write-Host "Successful connections: $SuccessCount" -ForegroundColor Green
Write-Host "Failed attempts: $FailCount" -ForegroundColor Red

if ($FirstSuccess) {
    Write-Host "`n Pi is ready for EQ12 cluster integration!" -ForegroundColor Green
}
else {
    Write-Host "`n  Pi configuration needed. See setup guide." -ForegroundColor Yellow
}