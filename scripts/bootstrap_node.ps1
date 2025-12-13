<#
PowerShell bootstrap for new Windows node (run as Administrator)
- Enables PSRemoting
- Installs/starts OpenSSH.Server capability
- Enables firewall rules for WinRM/SSH/RDP (optional)
- Creates a local 'eq12' user if requested
#>
[CmdletBinding()]
param(
    [switch]$CreateEq12User,
    [string]$Eq12User = 'eq12',
    [string]$Eq12Password = 'ChangeMe!23',
    [switch]$EnableSSH
)

Write-Host "Starting EQ12 node bootstrap..." -ForegroundColor Cyan

# Enable PSRemoting
try {
    Enable-PSRemoting -Force -ErrorAction Stop
    Write-Host "PSRemoting enabled." -ForegroundColor Green
}
catch {
    Write-Warning "Failed to enable PSRemoting: $_"
}

# Configure firewall rules for WinRM
try {
    if (-not (Get-NetFirewallRule -DisplayName 'Windows Remote Management (HTTP-In)' -ErrorAction SilentlyContinue)) {
        Write-Host 'Enabling firewall rule for WinRM' -ForegroundColor Yellow
        Enable-NetFirewallRule -DisplayGroup 'Windows Remote Management' -ErrorAction SilentlyContinue
    }
}
catch {
    Write-Warning "Firewall config for WinRM failed: $_"
}

# Install/enable OpenSSH server
if ($EnableSSH) {
    Write-Host 'Installing/Enabling OpenSSH.Server capability' -ForegroundColor Yellow
    try {
        Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 -ErrorAction SilentlyContinue
        Start-Service sshd -ErrorAction SilentlyContinue
        Set-Service -Name sshd -StartupType 'Automatic' -ErrorAction SilentlyContinue
        if (-not (Get-NetFirewallRule -DisplayName 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue)) {
            New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH-Server-In-TCP' -Enabled True -Direction Inbound -Protocol TCP -LocalPort 22
        }
        Write-Host 'OpenSSH installed and started.' -ForegroundColor Green
    }
    catch {
        Write-Warning "OpenSSH install failed: $_"
    }
}

# Optionally create eq12 user
if ($CreateEq12User) {
    try {
        $securePass = ConvertTo-SecureString $Eq12Password -AsPlainText -Force
        New-LocalUser -Name $Eq12User -Password $securePass -FullName 'EQ12 Node User' -Description 'User for EQ12 automation' -ErrorAction SilentlyContinue
        Add-LocalGroupMember -Group 'Administrators' -Member $Eq12User -ErrorAction SilentlyContinue
        Write-Host "Created local user $Eq12User and added to Administrators." -ForegroundColor Green
    }
    catch {
        Write-Warning "Failed to create user: $_"
    }
}

Write-Host 'Bootstrap complete. Please verify network settings and domain/join preferences manually.' -ForegroundColor Cyan
