<#
.SYNOPSIS
    Deploys the EdgeGod scraper to the M70q node.
.DESCRIPTION
    1. Starts a local CONNECT-capable proxy on EQ12.
    2. Copies source files to M70q using SCP (user: ricoj100).
    3. Runs 'docker build' on M70q using the proxy for internet access.
#>
[CmdletBinding()]
param(
    [string]$M70q_IP = "192.168.100.3",
    [string]$User = "ricoj100",
    [string]$ProxyHost = "192.168.100.2",
    [int]$ProxyPort = 8888
)

$ErrorActionPreference = "Stop"

# 1. Start Proxy
Write-Host "Starting local CONNECT proxy..." -ForegroundColor Cyan
$ProxyScript = "$PSScriptRoot\proxy_server.py"
$ProxyJob = Get-Job -Name "EQ12_ConnectProxy" -ErrorAction SilentlyContinue
if ($ProxyJob) { Remove-Job $ProxyJob -Force }

Start-Job -Name "EQ12_ConnectProxy" -ScriptBlock {
    param($Path)
    python $Path
} -ArgumentList $ProxyScript | Out-Null

Start-Sleep -Seconds 2
if (Test-NetConnection -ComputerName 127.0.0.1 -Port $ProxyPort -InformationLevel Quiet) {
    Write-Host "Proxy is listening on port $ProxyPort." -ForegroundColor Green
}
else {
    Write-Warning "Proxy did not start correctly."
}

# 2. Copy Files
Write-Host "Copying files to M70q ($User@$M70q_IP)..." -ForegroundColor Cyan
$SourcePath = Resolve-Path "$PSScriptRoot\..\src\edgegod"
$RemotePath = "/home/$User/edgegod/src"

# Ensure remote dir exists
ssh $User@$M70q_IP "mkdir -p $RemotePath"

# SCP
scp -r "$($SourcePath.Path)\*" "$User@$($M70q_IP):$RemotePath/"
if ($LASTEXITCODE -eq 0) {
    Write-Host "Files copied successfully." -ForegroundColor Green
}
else {
    Write-Error "SCP failed. Check SSH keys/permissions."
}

# 3. Docker Build
Write-Host "Triggering Docker Build on M70q..." -ForegroundColor Cyan
$BuildCmd = "cd $RemotePath && sudo docker build " +
"--build-arg http_proxy=http://$($ProxyHost):$($ProxyPort) " +
"--build-arg https_proxy=http://$($ProxyHost):$($ProxyPort) " +
"--network host " +
"-t edgegod-scraper:latest ."

Write-Host "Command: $BuildCmd" -ForegroundColor DarkGray

# We use -t to allocate pseudo-tty if sudo needs password, but ideally sudo is passwordless or we pass it.
# If sudo needs password, this might hang. Assuming sudo works or user can type it.
# Actually, let's try without -t first to see output, or use -S for stdin password if needed.
# For now, assuming 'sudo' might prompt.
ssh -t $User@$M70q_IP $BuildCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build completed successfully!" -ForegroundColor Green
}
else {
    Write-Error "Docker build failed."
}

# 4. Restart Container
Write-Host "Restarting container on M70q..." -ForegroundColor Cyan
$RunCmd = "sudo docker rm -f edgegod-scraper 2>/dev/null || true && " +
"sudo docker run -d --name edgegod-scraper " +
"--network host " +
"--restart unless-stopped " +
"-e http_proxy=http://$($ProxyHost):$($ProxyPort) " +
"-e https_proxy=http://$($ProxyHost):$($ProxyPort) " +
"edgegod-scraper:latest"

ssh $User@$M70q_IP $RunCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment complete! Container 'edgegod-scraper' is running." -ForegroundColor Green
}
else {
    Write-Error "Failed to start container."
}
