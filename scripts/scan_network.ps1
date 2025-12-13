param(
    [string[]]$TargetIPs = @(
        "192.168.1.144", # EQ12
        "192.168.1.80",  # Pi
        "192.168.1.130", # M70q (Ubuntu)
        "192.168.1.94",  # VM A
        "192.168.1.116", # VM B
        "192.168.1.126", # VM C
        "192.168.1.249", # TCL TV
        "192.168.1.246", # LG TV (Should be excluded/offline)
        "192.168.100.1"  # Cluster Link
    )
)

$Results = @()

Write-Host "Starting Network Availability Scan..." -ForegroundColor Cyan

foreach ($IP in $TargetIPs) {
    $Status = "Offline"
    if (Test-Connection -ComputerName $IP -Count 1 -Quiet -ErrorAction SilentlyContinue) {
        $Status = "Online"
        Write-Host "  [+] $IP is ONLINE" -ForegroundColor Green
    }
    else {
        Write-Host "  [-] $IP is OFFLINE (or unreachable)" -ForegroundColor Red
    }

    $Results += [PSCustomObject]@{
        IP        = $IP
        Status    = $Status
        Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    }
}

# Save to JSON for the Orchestrator to read
$ReportPath = "logs/network_scan_report.json"
$Results | ConvertTo-Json | Set-Content -Path $ReportPath
Write-Host "Scan complete. Report saved to $ReportPath" -ForegroundColor Cyan
