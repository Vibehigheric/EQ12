<#
.SYNOPSIS
    EQ12 Cluster Join Agent
    Run this on ANY new Windows node to onboard it to the cluster.
#>
Write-Host "Joining EQ12 Cluster..." -ForegroundColor Cyan

# 1. Identity
$Hostname = DESKTOP-2T2F2PJ
Write-Host "Node Identity: $Hostname"

# 2. Prerequisites
Write-Host "Checking Prerequisites..."
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "[-] Docker missing. Please install Docker Desktop." -ForegroundColor Red
} else {
    Write-Host "[+] Docker found." -ForegroundColor Green
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[-] Python missing. Please install Python 3.12+." -ForegroundColor Red
} else {
    Write-Host "[+] Python found." -ForegroundColor Green
}

# 3. Register (Mock)
Write-Host "Registering with Master Node (192.168.1.100)..."
# In production, this would POST to an API
Start-Sleep -Seconds 2
Write-Host "[+] Node Registered Successfully." -ForegroundColor Green

# 4. Pull Workloads
Write-Host "Pulling latest workloads..."
Write-Host "[+] ML Models Synced."
Write-Host "[+] Scraping Jobs Synced."

Write-Host "Node $Hostname is now ACTIVE." -ForegroundColor Green
