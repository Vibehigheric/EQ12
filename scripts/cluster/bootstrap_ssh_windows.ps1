# Bootstrap SSH on Windows nodes (EQ12, M70q if Windows)
# Run as Administrator

Write-Host "=== EQ12 Cluster Node Bootstrap (Windows) ===" -ForegroundColor Cyan
Write-Host "Target: Enable OpenSSH Server" -ForegroundColor Gray

# 1. Install OpenSSH Server
Write-Host "-> Checking OpenSSH Server capability..."
$capability = Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH.Server*'
if ($capability.State -ne 'Installed') {
    Write-Host "   Installing OpenSSH Server..."
    Add-WindowsCapability -Online -Name $capability.Name
}
else {
    Write-Host "   OpenSSH Server is already installed." -ForegroundColor Green
}

# 2. Configure Service
Write-Host "-> Configuring sshd service..."
Set-Service -Name sshd -StartupType Automatic
Start-Service sshd
$svc = Get-Service sshd
Write-Host "   Service Status: $($svc.Status)" -ForegroundColor Green

# 3. Configure Firewall
Write-Host "-> Configuring Firewall..."
$fw = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
if (-not $fw) {
    New-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -DisplayName "OpenSSH Server (TCP-In)" `
        -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
    Write-Host "   Firewall rule created." -ForegroundColor Green
}
else {
    Write-Host "   Firewall rule exists." -ForegroundColor Green
}

Write-Host "=== Bootstrap Complete ===" -ForegroundColor Cyan
Write-Host "Try connecting from another machine: ssh $env:USERNAME@$((Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp).IPAddress)"
