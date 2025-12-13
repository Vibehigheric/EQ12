#!/usr/bin/env pwsh
# Connect to M70Q and add to cluster using stored credentials

$M70Q_IP = "192.168.1.52"
$M70Q_USER = "richj"

Write-Host "Connecting to M70Q at $M70Q_IP..." -ForegroundColor Cyan

# Use plink (PuTTY) if available for better password handling
if (Get-Command plink -ErrorAction SilentlyContinue) {
    Write-Host "Using PuTTY plink for connection..." -ForegroundColor Yellow
    echo "Pny3737!!!" | plink -ssh -l $M70Q_USER -pw "Pny3737!!!" $M70Q_IP "hostname; uname -a; ip addr show"
}
else {
    # Use native SSH with sshpass-equivalent
    Write-Host "Attempting SSH connection..." -ForegroundColor Yellow
    Write-Host "Enter password when prompted: Pny3737!!!" -ForegroundColor Green
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $M70Q_USER@$M70Q_IP "hostname; uname -a; ip addr show"
}
