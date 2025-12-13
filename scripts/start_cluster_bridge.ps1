<#
.SYNOPSIS
    Starts the EQ12 Cluster Bridge (Proxy + SSH Tunnel).
.DESCRIPTION
    This script enables internet access for the "Island Node" (M70q) by:
    1. Starting a local HTTP proxy on port 8888.
    2. Establishing an SSH Reverse Tunnel to the M70q.
    
    This allows the M70q to access the internet via the Windows machine.
.EXAMPLE
    .\start_cluster_bridge.ps1
#>

[CmdletBinding()]
param()

$ProxyPort = 8888
$RemoteUser = "ricoj100"
$RemoteIP = "192.168.100.3"

# 1. Check/Start Proxy
Write-Host "Checking for Proxy Server..." -ForegroundColor Cyan
$ProxyJob = Get-Job | Where-Object { $_.Command -like "*proxy*" -and $_.State -eq "Running" }

if ($ProxyJob) {
    Write-Host "Proxy is already running (Job ID: $($ProxyJob.Id))." -ForegroundColor Green
}
else {
    Write-Host "Starting Proxy on port $ProxyPort..." -ForegroundColor Yellow
    # Ensure python is in path or use full path if needed. Assuming python is available.
    Start-Job -ScriptBlock { python -m proxy --hostname 0.0.0.0 --port 8888 } | Out-Null
    Start-Sleep -Seconds 2
    $NewJob = Get-Job | Where-Object { $_.Command -like "*proxy*" -and $_.State -eq "Running" }
    if ($NewJob) {
        Write-Host "Proxy started successfully." -ForegroundColor Green
    }
    else {
        Write-Error "Failed to start proxy. Check 'python -m proxy' manually."
        exit 1
    }
}

# 2. Start SSH Tunnel
Write-Host "Establishing SSH Reverse Tunnel to $RemoteIP..." -ForegroundColor Cyan
Write-Host "This will keep the terminal open. Press Ctrl+C to stop the bridge." -ForegroundColor Magenta

# We use -N (no command) to just hold the tunnel open.
# We use -R to reverse forward the port.
# We use -o ServerAliveInterval to keep it alive.

$SSHCommand = "ssh -N -R ${ProxyPort}:127.0.0.1:${ProxyPort} -o ServerAliveInterval=60 ${RemoteUser}@${RemoteIP}"

Write-Host "Running: $SSHCommand" -ForegroundColor DarkGray
Invoke-Expression $SSHCommand
