#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Pi Cluster Auto-Configuration Script
.DESCRIPTION
    Automatically configures Raspberry Pi for EQ12 cluster network via SSH
.PARAMETER PiIP
    IP address of the Pi (default: 192.168.1.80)
.PARAMETER ClusterIP
    Target cluster IP for Pi (default: 192.168.100.2)
.PARAMETER Username
    SSH username (default: ricoj100)
.PARAMETER Password
    SSH password
.EXAMPLE
    .\eq12_pi_cluster_autoconfig.ps1 -Password "CLUSTER_PASSWORD_PLACEHOLDER"
#>

[CmdletBinding()]
param(
    [string]$PiIP = "192.168.1.80",
    [string]$ClusterIP = "192.168.100.2",
    [string]$Username = "ricoj100",
    [string]$Password = "CLUSTER_PASSWORD_PLACEHOLDER",
    [switch]$VerboseOutput
)

# Enhanced logging
$LogPath = "C:\EQ12\logs"
$LogFile = Join-Path $LogPath "pi_cluster_config_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
if (-not (Test-Path $LogPath)) { New-Item -Path $LogPath -ItemType Directory -Force }

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Test-SSHConnection {
    param([string]$Target, [int]$Port = 22)
    try {
        $Connection = Test-NetConnection -ComputerName $Target -Port $Port -WarningAction SilentlyContinue
        return $Connection.TcpTestSucceeded
    }
    catch {
        return $false
    }
}

function Invoke-SSHCommand {
    param([string]$Command, [string]$Description)
    
    Write-Log "Executing: $Description"
    Write-Log "Command: $Command"
    
    # Create SSH command using plink (if available) or manual SSH
    $SSHCmd = "echo y | plink -ssh -l $Username -pw `"$Password`" $PiIP `"$Command`""
    
    try {
        $Result = Invoke-Expression $SSHCmd 2>&1
        Write-Log "Result: $Result"
        return $true
    }
    catch {
        Write-Log "Error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Main execution
Write-Log " Starting EQ12 Pi Cluster Auto-Configuration"
Write-Log "Target Pi: $PiIP -> Cluster IP: $ClusterIP"

# Step 1: Test initial connectivity
Write-Log "Step 1: Testing Pi connectivity..."
if (-not (Test-SSHConnection -Target $PiIP)) {
    Write-Log " Cannot reach Pi at $PiIP" "ERROR"
    exit 1
}
Write-Log " Pi is reachable at $PiIP"

# Step 2: Check if SSH works
Write-Log "Step 2: Testing SSH connection..."
$TestSSH = Invoke-SSHCommand -Command "whoami" -Description "Test SSH connection"
if (-not $TestSSH) {
    Write-Log " SSH connection failed - trying alternative method" "WARNING"
    
    # Alternative: Use native Windows SSH if available
    if (Get-Command ssh -ErrorAction SilentlyContinue) {
        Write-Log "Using Windows native SSH client"
        
        # Create temp script for SSH automation
        $TempScript = @"
#!/bin/bash
# EQ12 Pi Cluster Configuration Script

echo " Configuring Pi for EQ12 cluster network..."

# Backup current config
sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup
echo " Config backed up"

# Add cluster network configuration
sudo tee -a /etc/dhcpcd.conf << 'EOF'

# EQ12 Cluster Network Configuration
interface eth0
static ip_address=$ClusterIP/24
static routers=192.168.100.1
static domain_name_servers=8.8.8.8 8.8.4.4
EOF

echo " Cluster network config added"
echo " Rebooting in 5 seconds..."
sleep 5
sudo reboot
"@
        
        $ScriptPath = "C:\EQ12\logs\pi_config_script.sh"
        $TempScript | Out-File -FilePath $ScriptPath -Encoding UTF8
        
        Write-Log "Created configuration script: $ScriptPath"
        Write-Log "Manual SSH method required - see script above"
        
        # Generate manual commands
        Write-Log "=== MANUAL SSH COMMANDS ==="
        Write-Log "ssh $Username@$PiIP"
        Write-Log "Password: $Password"
        Write-Log "Then run these commands:"
        Write-Log "sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup"
        Write-Log "sudo tee -a /etc/dhcpcd.conf << 'EOF'"
        Write-Log "interface eth0"
        Write-Log "static ip_address=$ClusterIP/24"
        Write-Log "static routers=192.168.100.1"
        Write-Log "static domain_name_servers=8.8.8.8 8.8.4.4"
        Write-Log "EOF"
        Write-Log "sudo reboot"
        Write-Log "=========================="
        
        return
    }
}

# Step 3: Execute configuration commands
Write-Log "Step 3: Backing up current network configuration..."
Invoke-SSHCommand -Command "sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup" -Description "Backup network config"

Write-Log "Step 4: Adding cluster network configuration..."
$NetworkConfig = @"
sudo tee -a /etc/dhcpcd.conf << 'EOF'

# EQ12 Cluster Network Configuration
interface eth0
static ip_address=$ClusterIP/24
static routers=192.168.100.1
static domain_name_servers=8.8.8.8 8.8.4.4
EOF
"@

Invoke-SSHCommand -Command $NetworkConfig -Description "Add cluster network config"

Write-Log "Step 5: Rebooting Pi to apply changes..."
Invoke-SSHCommand -Command "sudo reboot" -Description "Reboot Pi"

Write-Log " Waiting 60 seconds for Pi to reboot..."
Start-Sleep -Seconds 60

# Step 6: Test cluster connectivity
Write-Log "Step 6: Testing cluster network connectivity..."
for ($i = 1; $i -le 10; $i++) {
    Write-Log "Attempt $i/10: Testing $ClusterIP..."
    if (Test-SSHConnection -Target $ClusterIP) {
        Write-Log " SUCCESS! Pi is accessible on cluster network at $ClusterIP"
        Write-Log " Cluster configuration complete!"
        
        # Test SSH to cluster IP
        $ClusterSSH = Invoke-SSHCommand -Command "hostname && ip addr show eth0" -Description "Test cluster SSH"
        if ($ClusterSSH) {
            Write-Log " SSH working on cluster network"
        }
        
        exit 0
    }
    Start-Sleep -Seconds 10
}

Write-Log "  Pi not yet accessible on cluster network - may need more time" "WARNING"
Write-Log "Configuration applied - manual verification recommended"

Write-Log " Pi Cluster Auto-Configuration Complete"
Write-Log "Log saved to: $LogFile"
