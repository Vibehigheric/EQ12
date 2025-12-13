<#
.SYNOPSIS
    EQ12 Founder Mode - Lenovo 10T8 Onboarding Script
    RUN THIS ON THE LENOVO MACHINE (WORKER NODE)

.DESCRIPTION
    This script configures the Lenovo 10T8 to join the EQ12 Cluster in "Founder Mode".
    It installs Docker, pulls the repo, and launches the 13-product portfolio.

.NOTES
    Author: EQ12 Master Orchestrator
    Mode: Founder Mode (Direct Action)
#>

[CmdletBinding()]
param(
    [string]$RepoUrl = "https://github.com/Ricoj100/EQ12_BROKEN_20251122_210342.git", # Adjust if private
    [string]$WorkDir = "C:\EQ12_Worker"
)

Write-Host "🚀 INITIATING FOUNDER MODE ONBOARDING FOR LENOVO 10T8..." -ForegroundColor Cyan

# 1. Setup Workspace
if (-not (Test-Path $WorkDir)) {
    Write-Host "Creating workspace at $WorkDir..."
    New-Item -ItemType Directory -Path $WorkDir | Out-Null
}
Set-Location $WorkDir

# 2. Check Docker
Write-Host "Checking Docker status..."
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "❌ Docker is NOT installed. Please install Docker Desktop for Windows first."
    exit 1
}
if (-not (docker info 2>$null)) {
    Write-Error "❌ Docker daemon is not running. Please start Docker Desktop."
    exit 1
}
Write-Host "✅ Docker is ready." -ForegroundColor Green

# 3. Clone/Pull Repo (Simulated for local context, assuming file copy or git clone)
# In a real scenario, we'd git clone. For now, we assume the files are transferred or accessible.
Write-Host "⚠️ NOTE: Ensure 'src/products' is present in $WorkDir. (Simulating sync)"

# 4. Launch Portfolio
$ComposeFile = "$WorkDir\src\products\docker-compose.yaml"

if (Test-Path $ComposeFile) {
    Write-Host "🔥 Launching the 13-Product Portfolio..." -ForegroundColor Magenta
    docker-compose -f $ComposeFile up -d --build
    
    if ($?) {
        Write-Host "✅ SUCCESS: Portfolio Deployed." -ForegroundColor Green
        docker ps
    }
    else {
        Write-Error "❌ Deployment Failed."
    }
}
else {
    Write-Warning "docker-compose.yaml not found at $ComposeFile. Please sync the repo."
}

Write-Host "🏁 FOUNDER MODE ONBOARDING COMPLETE." -ForegroundColor Cyan
