<#
.SYNOPSIS
    EQ12 Deploy to Swarm
    Deploys the stack to the M70q Swarm Manager.

.DESCRIPTION
    1. Connects to M70q via SSH (assumes key-based auth or configured host).
    2. Updates the stack definition.
    3. Triggers a rolling update.

.EXAMPLE
    .\scripts\eq12_deploy_to_swarm.ps1 -Host "m70q"
#>

[CmdletBinding()]
param(
    [string]$SwarmHost = "192.168.100.3",
    [string]$User = "ricoj", # Adjust as needed
    [string]$StackName = "eq12"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 DEPLOYING TO SWARM ($SwarmHost)" -ForegroundColor Cyan

# 1. Check Connectivity
Write-Host "📡 Checking connectivity..." -ForegroundColor Yellow
if (-not (Test-Connection -ComputerName $SwarmHost -Count 1 -Quiet)) {
    Write-Error "❌ Cannot reach Swarm Host: $SwarmHost"
}

# 2. Copy Compose File
Write-Host "📄 Transferring stack definition..." -ForegroundColor Yellow
# Assuming we have a docker-compose.yml or stack file. If not, we need to create one.
# For now, let's assume we generate one or use an existing one.
$StackFile = "docker-compose.yml"
if (-not (Test-Path $StackFile)) {
    Write-Warning "⚠️ No docker-compose.yml found in root. Creating a basic one..."
    # Create a basic stack file for the demo
    $StackContent = @"
version: '3.8'
services:
  core:
    image: eq12/core:latest
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure
    environment:
      - EQ12_ENV=production
    volumes:
      - ./logs:/app/logs
"@
    $StackContent | Out-File -FilePath $StackFile -Encoding utf8
}

# SCP the file (requires scp in path)
try {
    scp $StackFile "${User}@${SwarmHost}:~/eq12_stack.yml"
    Write-Host "✅ Stack file transferred." -ForegroundColor Green
}
catch {
    Write-Error "❌ SCP Failed. Ensure SSH keys are set up. Error: $_"
}

# 3. Deploy Command
Write-Host "🔄 Triggering Swarm Update..." -ForegroundColor Cyan
$DeployCmd = "docker stack deploy -c eq12_stack.yml $StackName"

try {
    ssh "${User}@${SwarmHost}" $DeployCmd
    Write-Host "✅ Deployment Triggered Successfully!" -ForegroundColor Green
}
catch {
    Write-Error "❌ Deployment Failed: $_"
}
