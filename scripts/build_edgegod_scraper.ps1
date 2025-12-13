<#
.SYNOPSIS
    Builds the EdgeGod scraper Docker image on the remote M70q node.
.DESCRIPTION
    This script automates the process of:
    1. Checking connectivity to the M70q (Island Node).
    2. Copying the updated Dockerfile (with proxy settings).
    3. Running 'docker build' remotely via SSH, using the SSH tunnel for internet access.
.EXAMPLE
    .\scripts\build_edgegod_scraper.ps1
#>
[CmdletBinding()]
param(
    [string]$M70q_IP = "192.168.100.3",
    [string]$User = "ricoj100",
    [int]$ProxyPort = 8888
)

$ErrorActionPreference = "Stop"

Write-Host "Checking connectivity to M70q at $M70q_IP..." -ForegroundColor Cyan
if (-not (Test-Connection -ComputerName $M70q_IP -Count 1 -Quiet)) {
    Write-Error "M70q ($M70q_IP) is not reachable. Please check power and network connection."
}

Write-Host "M70q is ONLINE." -ForegroundColor Green

# 0. Ensure Local Proxy is Running
$ProxyScript = "$PSScriptRoot\simple_proxy.py"
$ProxyJobName = "EQ12_SimpleProxy"

if (-not (Get-NetTCPConnection -LocalPort $ProxyPort -State Listen -ErrorAction SilentlyContinue)) {
    Write-Host "Starting local proxy on port $ProxyPort..." -ForegroundColor Yellow
    Start-Job -Name $ProxyJobName -ScriptBlock {
        param($ScriptPath)
        python $ScriptPath
    } -ArgumentList $ProxyScript | Out-Null
    
    # Wait a moment for it to start
    Start-Sleep -Seconds 2
    if (-not (Get-NetTCPConnection -LocalPort $ProxyPort -State Listen -ErrorAction SilentlyContinue)) {
        Write-Warning "Failed to start local proxy. Build may fail if internet is required."
    }
    else {
        Write-Host "Proxy started successfully." -ForegroundColor Green
    }
}
else {
    Write-Host "Local proxy already running on port $ProxyPort." -ForegroundColor Green
}

# Define paths
$LocalSourcePath = Resolve-Path "$PSScriptRoot\..\src\edgegod"
$LocalSourcePath = $LocalSourcePath.Path
Write-Host "Local Source Path: $LocalSourcePath" -ForegroundColor DarkGray

# Convert to WSL path for better SSH/SCP handling
# Escape backslashes for WSL argument parsing
$EscapedPath = $LocalSourcePath.Replace("\", "\\")
$WSLSourcePath = (wsl wslpath -a "$EscapedPath").Trim()
Write-Host "WSL Source Path: $WSLSourcePath" -ForegroundColor DarkGray

$RemotePath = "/opt/edgegod/src/"

Write-Host "`nIMPORTANT: You will be prompted for the password multiple times." -ForegroundColor Yellow
Write-Host "Password: Pny3737!!!" -ForegroundColor Green
Write-Host "User: $User`n" -ForegroundColor Green

# 1. Copy Source Files using WSL (interactive)
Write-Host "Copying source files to remote..." -ForegroundColor Cyan
try {
    # Use -r for recursive copy
    $ScpCmd = "scp -o StrictHostKeyChecking=no -r $WSLSourcePath/* $User@$($M70q_IP):$RemotePath/"
    wsl bash -c "$ScpCmd"
    
    if ($LASTEXITCODE -ne 0) { throw "SCP failed" }
}
catch {
    Write-Error "Failed to copy source files. $_"
}

# 2. Run Docker Build using WSL (interactive)
Write-Host "Starting Remote Docker Build..." -ForegroundColor Cyan
Write-Host "Using SSH Tunnel on port $ProxyPort for internet access..." -ForegroundColor Yellow

# We use -R to forward the proxy port
# We use -t to force pseudo-terminal allocation for sudo password prompt
$BuildCmd = "cd $RemotePath && sudo docker build --network host -t edgegod-scraper:latest ."
$SSHCmd = "ssh -t -o StrictHostKeyChecking=no -R $($ProxyPort):127.0.0.1:$ProxyPort $User@$M70q_IP `"$BuildCmd`""

Write-Host "Executing remote build..." -ForegroundColor DarkGray
wsl bash -c "$SSHCmd"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build SUCCESS!" -ForegroundColor Green
    Write-Host "You can now update the service with: sudo docker service update --force edgegod_odds-scraper" -ForegroundColor Cyan
}
else {
    Write-Error "Docker build failed."
}



