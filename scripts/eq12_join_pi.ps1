param(
    [string]$ManagerIP = "192.168.100.3",
    [string]$PiIP = "192.168.1.80",
    [string]$PiClusterIP = "192.168.100.1",
    [string]$User = "ricoj100"
)

$ErrorActionPreference = "Stop"

Write-Host "=== [EQ12] Joining Pi to Swarm ===" -ForegroundColor Cyan

# 1. Get Worker Token from Manager (M70q)
Write-Host "[1/3] Fetching Swarm Worker Token from Manager ($ManagerIP)..." -ForegroundColor Yellow
try {
    $token = ssh -o BatchMode=yes "$User@$ManagerIP" "docker swarm join-token worker -q"
    if (-not $token) {
        throw "Failed to retrieve token. Is Docker running on $ManagerIP?"
    }
    Write-Host "Token: $token" -ForegroundColor Gray
} catch {
    Write-Error "Failed to connect to Manager ($ManagerIP). Ensure SSH keys are set."
    exit 1
}

# 2. Check if Pi is already in Swarm
Write-Host "[2/3] Checking Pi Swarm status..." -ForegroundColor Yellow
$swarmStatus = ssh -o BatchMode=yes "$User@$PiIP" "docker info --format '{{.Swarm.LocalNodeState}}'"
if ($swarmStatus -eq "active") {
    Write-Host "Pi is already in Swarm." -ForegroundColor Green
    exit 0
}

# 3. Join Pi to Swarm
Write-Host "[3/3] Joining Pi to Swarm (Advertise: $PiClusterIP)..." -ForegroundColor Yellow
$joinCmd = "docker swarm join --token $token --advertise-addr $PiClusterIP ${ManagerIP}:2377"
ssh -o BatchMode=yes "$User@$PiIP" $joinCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "Pi successfully joined the Swarm!" -ForegroundColor Green
} else {
    Write-Error "Failed to join Pi to Swarm."
    exit 1
}
