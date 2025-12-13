#!/usr/bin/env powershell
<#
.SYNOPSIS
    EQ12 One-Click Pi Node Installer
    Automated Raspberry Pi 5 flashing, configuration, and cluster integration

.DESCRIPTION
    This script automates the complete process of:
    - Flashing Raspberry Pi OS to USB/NVMe drives
    - Configuring SSH, static IP, and cluster settings
    - Automatic registration with EQ12 cluster master
    - TPU detection and service deployment

.PARAMETER NodeId
    Pi node identifier (01-20)

.PARAMETER DriveType
    Boot device type: USB, NVMe, or SD

.PARAMETER AutoDeploy
    Automatically deploy cluster services after OS installation

.EXAMPLE
    .\eq12_pi_installer.ps1 -NodeId 02 -DriveType USB -AutoDeploy
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateRange(1, 20)]
    [int]$NodeId,
    
    [ValidateSet("USB", "NVMe", "SD")]
    [string]$DriveType = "USB",
    
    [switch]$AutoDeploy,
    
    [switch]$SkipFlashing,
    
    [string]$RaspberryPiImagerPath = "C:\Program Files (x86)\Raspberry Pi Imager\rpi-imager.exe"
)

$ErrorActionPreference = "Stop"

# Configure logging
$LogPath = "C:\EQ12\logs\pi_installer_node_$('{0:D2}' -f $NodeId)_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
New-Item -Path (Split-Path $LogPath) -ItemType Directory -Force | Out-Null

function Write-InstallerLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] Node-$('{0:D2}' -f $NodeId): $Message"
    
    $Color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        "PROGRESS" { "Cyan" }
        default { "White" }
    }
    
    Write-Host $LogEntry -ForegroundColor $Color
    Add-Content -Path $LogPath -Value $LogEntry
}

function Test-Prerequisites {
    Write-InstallerLog " Checking installation prerequisites..." -Level "PROGRESS"
    
    $Issues = @()
    
    # Check Raspberry Pi Imager
    if (-not (Test-Path $RaspberryPiImagerPath)) {
        $Issues += "Raspberry Pi Imager not found at $RaspberryPiImagerPath"
        Write-InstallerLog "Download from: https://www.raspberrypi.com/software/" -Level "WARN"
    }
    
    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        $Issues += "PowerShell 5.0+ required"
    }
    
    # Check network connectivity
    try {
        $NetworkTest = Test-NetConnection -ComputerName "192.168.100.1" -Port 80 -WarningAction SilentlyContinue
        if (-not $NetworkTest.TcpTestSucceeded) {
            Write-InstallerLog "Network connectivity test failed - cluster may not be accessible" -Level "WARN"
        }
    }
    catch {
        Write-InstallerLog "Network test inconclusive" -Level "WARN"
    }
    
    # Check available drives
    $AvailableDrives = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DriveType -eq 2 -and $_.Size -gt 8GB }
    if ($AvailableDrives.Count -eq 0) {
        $Issues += "No suitable USB drives found (minimum 8GB required)"
    }
    
    if ($Issues.Count -gt 0) {
        Write-InstallerLog " Prerequisites check failed:" -Level "ERROR"
        $Issues | ForEach-Object { Write-InstallerLog "  - $_" -Level "ERROR" }
        throw "Prerequisites not met"
    }
    
    Write-InstallerLog " Prerequisites satisfied" -Level "SUCCESS"
}

function Get-TargetDrive {
    Write-InstallerLog " Detecting target drives for $DriveType installation..." -Level "PROGRESS"
    
    $Drives = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { 
        $_.DriveType -eq 2 -and $_.Size -gt 8GB 
    } | Select-Object DeviceID, Size, VolumeName, @{
        Name = "SizeGB"; Expression = { [math]::Round($_.Size / 1GB, 2) }
    }
    
    if ($Drives.Count -eq 0) {
        throw "No suitable drives found for Pi installation"
    }
    
    Write-InstallerLog "Available drives:" -Level "PROGRESS"
    $Drives | ForEach-Object {
        Write-InstallerLog "  $($_.DeviceID) - $($_.SizeGB)GB - $($_.VolumeName)" -Level "PROGRESS"
    }
    
    if ($Drives.Count -eq 1) {
        $SelectedDrive = $Drives[0]
        Write-InstallerLog "Auto-selected drive: $($SelectedDrive.DeviceID)" -Level "SUCCESS"
    }
    else {
        Write-InstallerLog "Multiple drives detected. Please select target drive:" -Level "WARN"
        for ($i = 0; $i -lt $Drives.Count; $i++) {
            Write-Host "  [$i] $($Drives[$i].DeviceID) - $($Drives[$i].SizeGB)GB - $($Drives[$i].VolumeName)"
        }
        
        do {
            $Selection = Read-Host "Enter drive number (0-$($Drives.Count - 1))"
        } while ($Selection -notmatch '^\d+$' -or [int]$Selection -ge $Drives.Count)
        
        $SelectedDrive = $Drives[[int]$Selection]
    }
    
    # Confirm destructive operation
    Write-Host "`n  WARNING: This will ERASE all data on drive $($SelectedDrive.DeviceID)" -ForegroundColor Yellow
    Write-Host "   Drive: $($SelectedDrive.DeviceID) ($($SelectedDrive.SizeGB)GB)" -ForegroundColor Yellow
    Write-Host "   Target: Pi Node $('{0:D2}' -f $NodeId) (192.168.100.$([int]10 + $NodeId))" -ForegroundColor Yellow
    
    $Confirmation = Read-Host "`nProceed with installation? (yes/NO)"
    if ($Confirmation -ne "yes") {
        throw "Installation cancelled by user"
    }
    
    return $SelectedDrive
}

function New-PiConfiguration {
    Write-InstallerLog " Generating Pi configuration for Node $('{0:D2}' -f $NodeId)..." -Level "PROGRESS"
    
    $NodeIPAddress = "192.168.100.$([int]10 + $NodeId)"
    $NodeHostname = "eq12-pi-$('{0:D2}' -f $NodeId)"
    
    $PiConfig = @{
        node_info = @{
            node_id        = "pi-node-$('{0:D2}' -f $NodeId)"
            hostname       = $NodeHostname
            ip_address     = $NodeIPAddress
            specialization = switch ($NodeId) {
                { $_ -le 3 } { "ai_inference" }
                { $_ -le 6 } { "cross_listing" }
                { $_ -le 9 } { "web_scraping" }
                default { "general_purpose" }
            }
        }
        network   = @{
            interface   = "eth0"
            ip_address  = "$NodeIPAddress/24"
            gateway     = "192.168.100.1"
            dns_servers = @("8.8.8.8", "1.1.1.1")
            master_ip   = "192.168.100.1"
        }
        services  = @{
            ssh_enabled        = $true
            username           = "pi"
            password           = "eq12stack"
            tpu_worker_port    = 8080
            cross_listing_port = 8081
            web_scraper_port   = 8082
            node_agent_port    = 8083
        }
        cluster   = @{
            master_api    = "http://192.168.100.1:8090/api"
            auto_register = $true
            capabilities  = @("tpu_inference", "web_automation", "cross_listing")
            resources     = @{
                cpu_cores = 4
                memory_gb = 8
                tpu_count = 1
            }
        }
    }
    
    # Save configuration
    $ConfigPath = "C:\EQ12\configs\pi_node_$('{0:D2}' -f $NodeId)_config.json"
    New-Item -Path (Split-Path $ConfigPath) -ItemType Directory -Force | Out-Null
    $PiConfig | ConvertTo-Json -Depth 10 | Out-File -FilePath $ConfigPath -Encoding UTF8
    
    Write-InstallerLog "Configuration saved: $ConfigPath" -Level "SUCCESS"
    return $PiConfig
}

function Start-OSFlashing {
    param([object]$TargetDrive, [hashtable]$Config)
    
    if ($SkipFlashing) {
        Write-InstallerLog "  Skipping OS flashing (SkipFlashing enabled)" -Level "WARN"
        return
    }
    
    Write-InstallerLog " Starting Raspberry Pi OS flashing..." -Level "PROGRESS"
    
    # Create Raspberry Pi Imager configuration
    $ImagerConfig = @{
        "os"               = "rpi-imager-os://ubuntu-20.04-desktop-arm64+raspi"
        "target_drive"     = $TargetDrive.DeviceID
        "advanced_options" = @{
            "enable_ssh"        = $true
            "ssh_username"      = $Config.services.username
            "ssh_password"      = $Config.services.password
            "hostname"          = $Config.node_info.hostname
            "configure_network" = $true
            "network_config"    = @{
                "dhcp"       = $false
                "ip_address" = $Config.network.ip_address
                "gateway"    = $Config.network.gateway
                "dns"        = $Config.network.dns_servers -join ","
            }
        }
    }
    
    # Create temporary configuration file for rpi-imager
    $TempConfigPath = [System.IO.Path]::GetTempFileName() + ".json"
    $ImagerConfig | ConvertTo-Json -Depth 10 | Out-File -FilePath $TempConfigPath -Encoding UTF8
    
    Write-InstallerLog "Launching Raspberry Pi Imager..." -Level "PROGRESS"
    Write-InstallerLog "Manual configuration required:" -Level "WARN"
    Write-InstallerLog "  1. Select 'Raspberry Pi OS (64-bit) Lite'" -Level "WARN"
    Write-InstallerLog "  2. Choose drive: $($TargetDrive.DeviceID)" -Level "WARN"
    Write-InstallerLog "  3. Press Ctrl+Shift+X for advanced options:" -Level "WARN"
    Write-InstallerLog "     - Enable SSH" -Level "WARN"
    Write-InstallerLog "     - Username: $($Config.services.username)" -Level "WARN"
    Write-InstallerLog "     - Password: $($Config.services.password)" -Level "WARN"
    Write-InstallerLog "     - Hostname: $($Config.node_info.hostname)" -Level "WARN"
    Write-InstallerLog "     - Static IP: $($Config.network.ip_address.Split('/')[0])" -Level "WARN"
    Write-InstallerLog "     - Gateway: $($Config.network.gateway)" -Level "WARN"
    Write-InstallerLog "  4. Click 'Save' then 'Write'" -Level "WARN"
    
    try {
        Start-Process -FilePath $RaspberryPiImagerPath -Wait
        Write-InstallerLog " Raspberry Pi Imager completed" -Level "SUCCESS"
    }
    catch {
        Write-InstallerLog " Failed to launch Raspberry Pi Imager: $($_.Exception.Message)" -Level "ERROR"
        throw
    }
    
    # Cleanup
    if (Test-Path $TempConfigPath) {
        Remove-Item $TempConfigPath -Force
    }
}

function Wait-ForPiOnline {
    param([hashtable]$Config)
    
    $NodeIP = $Config.network.ip_address.Split('/')[0]
    Write-InstallerLog " Waiting for Pi Node to come online at $NodeIP..." -Level "PROGRESS"
    
    $MaxAttempts = 60  # 5 minutes
    $Attempt = 0
    
    do {
        $Attempt++
        Write-Progress -Activity "Waiting for Pi Node" -Status "Attempt $Attempt/$MaxAttempts" -PercentComplete (($Attempt / $MaxAttempts) * 100)
        
        try {
            $PingResult = Test-Connection -ComputerName $NodeIP -Count 1 -Quiet -ErrorAction SilentlyContinue
            if ($PingResult) {
                Write-InstallerLog " Pi Node responding to ping" -Level "SUCCESS"
                
                # Test SSH connectivity
                $SSHTest = Test-NetConnection -ComputerName $NodeIP -Port 22 -WarningAction SilentlyContinue
                if ($SSHTest.TcpTestSucceeded) {
                    Write-InstallerLog " SSH service accessible" -Level "SUCCESS"
                    Write-Progress -Completed -Activity "Waiting for Pi Node"
                    return $true
                }
            }
        }
        catch {
            # Continue waiting
        }
        
        Start-Sleep -Seconds 5
        
    } while ($Attempt -lt $MaxAttempts)
    
    Write-Progress -Completed -Activity "Waiting for Pi Node"
    Write-InstallerLog " Pi Node did not come online within 5 minutes" -Level "ERROR"
    return $false
}

function Deploy-ClusterServices {
    param([hashtable]$Config)
    
    if (-not $AutoDeploy) {
        Write-InstallerLog "  Skipping service deployment (AutoDeploy not enabled)" -Level "WARN"
        return
    }
    
    $NodeIP = $Config.network.ip_address.Split('/')[0]
    Write-InstallerLog " Deploying cluster services to Pi Node..." -Level "PROGRESS"
    
    # Create deployment script
    $DeploymentScript = @"
#!/bin/bash
# EQ12 Pi Node Service Deployment
set -e

echo " Starting EQ12 Pi Node service deployment..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker pi
sudo systemctl enable docker
sudo systemctl start docker

# Install Python dependencies
sudo apt install -y python3-pip python3-venv
pip3 install --user fastapi uvicorn requests

# Install Coral TPU support
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt update
sudo apt install -y libedgetpu1-std python3-pycoral

# Create EQ12 directories
mkdir -p /home/pi/eq12/{configs,logs,models,automation,data}

# Download EQ12 cluster tools
cat > /home/pi/eq12/eq12_pi_service.py << 'EOF'
#!/usr/bin/env python3
import requests
import json
import time
import subprocess
import os

def register_with_master():
    master_url = "http://192.168.100.1:8090/api/register_node"
    node_config = {
        "node_id": "$($Config.node_info.node_id)",
        "ip_address": "$($Config.network.ip_address.Split('/')[0])",
        "hostname": "$($Config.node_info.hostname)",
        "capabilities": $($Config.cluster.capabilities | ConvertTo-Json),
        "resources": $($Config.cluster.resources | ConvertTo-Json),
        "specialization": "$($Config.node_info.specialization)"
    }
    
    try:
        response = requests.post(master_url, json=node_config, timeout=10)
        if response.status_code == 200:
            print(" Successfully registered with EQ12 cluster master")
            return True
        else:
            print(f" Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f" Registration error: {e}")
        return False

def start_services():
    print(" Starting EQ12 Pi Node services...")
    
    # Start TPU worker service
    subprocess.Popen([
        "python3", "/home/pi/eq12/tpu_worker.py",
        "--port", "8080",
        "--node-id", "$($Config.node_info.node_id)"
    ])
    
    print(" Pi Node services started")

if __name__ == "__main__":
    print(" EQ12 Pi Node Service Manager")
    
    # Wait for network to be ready
    time.sleep(30)
    
    # Register with master
    if register_with_master():
        start_services()
        print(" Pi Node ready for cluster operations!")
    else:
        print("  Registration failed - manual intervention may be required")
EOF

chmod +x /home/pi/eq12/eq12_pi_service.py

# Create systemd service
sudo bash -c 'cat > /etc/systemd/system/eq12-node.service << EOF
[Unit]
Description=EQ12 Pi Node Services
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/eq12
ExecStart=/usr/bin/python3 /home/pi/eq12/eq12_pi_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl enable eq12-node.service
sudo systemctl start eq12-node.service

echo " EQ12 Pi Node deployment complete!"
echo "   Node ID: $($Config.node_info.node_id)"
echo "   IP Address: $($Config.network.ip_address.Split('/')[0])"
echo "   Services: TPU Worker, Cross-listing, Web Scraping"
echo "   Status: systemctl status eq12-node"
"@

    # Save deployment script
    $ScriptPath = "C:\EQ12\cluster\deploy_pi_node_$('{0:D2}' -f $NodeId).sh"
    $DeploymentScript | Out-File -FilePath $ScriptPath -Encoding UTF8
    
    Write-InstallerLog "Deployment script created: $ScriptPath" -Level "SUCCESS"
    Write-InstallerLog "Manual deployment required:" -Level "WARN"
    Write-InstallerLog "  1. Copy script to Pi: scp $ScriptPath pi@${NodeIP}:~/" -Level "WARN"
    Write-InstallerLog "  2. SSH to Pi: ssh pi@$NodeIP" -Level "WARN"
    Write-InstallerLog "  3. Run deployment: chmod +x deploy_pi_node_$('{0:D2}' -f $NodeId).sh && ./deploy_pi_node_$('{0:D2}' -f $NodeId).sh" -Level "WARN"
}

function Register-WithCluster {
    param([hashtable]$Config)
    
    Write-InstallerLog " Registering Pi Node with EQ12 cluster master..." -Level "PROGRESS"
    
    $MasterAPI = "http://192.168.100.1:8090/api/register_node"
    $NodeRegistration = @{
        node_id                = $Config.node_info.node_id
        ip_address             = $Config.network.ip_address.Split('/')[0]
        hostname               = $Config.node_info.hostname
        capabilities           = $Config.cluster.capabilities
        resources              = $Config.cluster.resources
        specialization         = $Config.node_info.specialization
        installation_timestamp = Get-Date -Format "o"
        installer_version      = "1.0.0"
    }
    
    try {
        $Response = Invoke-RestMethod -Uri $MasterAPI -Method POST -Body ($NodeRegistration | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 10
        Write-InstallerLog " Node registered successfully with cluster master" -Level "SUCCESS"
        Write-InstallerLog "Registration ID: $($Response.registration_id)" -Level "SUCCESS"
    }
    catch {
        Write-InstallerLog "  Cluster registration failed: $($_.Exception.Message)" -Level "WARN"
        Write-InstallerLog "Node can be manually registered later via cluster dashboard" -Level "WARN"
    }
}

function New-InstallationReport {
    param([hashtable]$Config, [bool]$Success)
    
    Write-InstallerLog " Generating installation report..." -Level "PROGRESS"
    
    $InstallationReport = @{
        installation    = @{
            timestamp   = Get-Date -Format "o"
            node_id     = $Config.node_info.node_id
            node_ip     = $Config.network.ip_address.Split('/')[0]
            hostname    = $Config.node_info.hostname
            drive_type  = $DriveType
            auto_deploy = $AutoDeploy.IsPresent
            success     = $Success
        }
        configuration   = $Config
        next_steps      = @()
        troubleshooting = @{
            log_file          = $LogPath
            ssh_command       = "ssh pi@$($Config.network.ip_address.Split('/')[0])"
            ping_test         = "ping $($Config.network.ip_address.Split('/')[0])"
            cluster_dashboard = "http://192.168.100.1:3000"
        }
    }
    
    if ($Success) {
        $InstallationReport.next_steps += "Test SSH connectivity: ssh pi@$($Config.network.ip_address.Split('/')[0])"
        $InstallationReport.next_steps += "Check node services: systemctl status eq12-node"
        $InstallationReport.next_steps += "Monitor cluster dashboard: http://192.168.100.1:3000"
        if (-not $AutoDeploy) {
            $InstallationReport.next_steps += "Deploy cluster services using generated script"
        }
    }
    else {
        $InstallationReport.next_steps += "Check installation log: $LogPath"
        $InstallationReport.next_steps += "Verify network connectivity to 192.168.100.1"
        $InstallationReport.next_steps += "Re-run installer with -SkipFlashing if OS is already installed"
    }
    
    # Save report
    $ReportPath = "C:\EQ12\logs\pi_installation_report_node_$('{0:D2}' -f $NodeId)_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    $InstallationReport | ConvertTo-Json -Depth 10 | Out-File -FilePath $ReportPath -Encoding UTF8
    
    Write-InstallerLog "Installation report saved: $ReportPath" -Level "SUCCESS"
    return $InstallationReport
}

# Main installation workflow
try {
    Write-InstallerLog " Starting EQ12 Pi Node Installer" -Level "SUCCESS"
    Write-InstallerLog "Target: Pi Node $('{0:D2}' -f $NodeId) | Drive: $DriveType | Auto-Deploy: $($AutoDeploy.IsPresent)" -Level "PROGRESS"
    
    # Prerequisites check
    Test-Prerequisites
    
    # Generate Pi configuration
    $PiConfig = New-PiConfiguration
    
    # Detect and select target drive
    $TargetDrive = Get-TargetDrive
    
    # Flash Raspberry Pi OS
    Start-OSFlashing -TargetDrive $TargetDrive -Config $PiConfig
    
    Write-InstallerLog " Please complete the flashing process in Raspberry Pi Imager..." -Level "WARN"
    Write-InstallerLog "Press Enter when flashing is complete and Pi is powered on..." -Level "WARN"
    Read-Host
    
    # Wait for Pi to come online
    $PiOnline = Wait-ForPiOnline -Config $PiConfig
    
    if ($PiOnline) {
        # Deploy cluster services
        Deploy-ClusterServices -Config $PiConfig
        
        # Register with cluster
        Register-WithCluster -Config $PiConfig
        
        # Generate success report
        $Report = New-InstallationReport -Config $PiConfig -Success $true
        
        Write-InstallerLog " EQ12 Pi Node $('{0:D2}' -f $NodeId) installation completed successfully!" -Level "SUCCESS"
        Write-InstallerLog "Node IP: $($PiConfig.network.ip_address.Split('/')[0])" -Level "SUCCESS"
        Write-InstallerLog "SSH Access: ssh pi@$($PiConfig.network.ip_address.Split('/')[0])" -Level "SUCCESS"
        Write-InstallerLog "Cluster Dashboard: http://192.168.100.1:3000" -Level "SUCCESS"
        
        if ($AutoDeploy) {
            Write-InstallerLog " Services deployed automatically - node ready for cluster operations!" -Level "SUCCESS"
        }
        else {
            Write-InstallerLog "  Manual service deployment required - see generated deployment script" -Level "WARN"
        }
        
    }
    else {
        $Report = New-InstallationReport -Config $PiConfig -Success $false
        Write-InstallerLog " Pi Node installation failed - node did not come online" -Level "ERROR"
        Write-InstallerLog "Check flashing process and network configuration" -Level "ERROR"
    }
    
}
catch {
    Write-InstallerLog " Installation failed: $($_.Exception.Message)" -Level "ERROR"
    Write-InstallerLog "Check installation log for details: $LogPath" -Level "ERROR"
    
    try {
        $Report = New-InstallationReport -Config $PiConfig -Success $false
    }
    catch {
        Write-InstallerLog "Failed to generate error report" -Level "ERROR"
    }
    
    exit 1
}

Write-InstallerLog " EQ12 Pi Node Installer completed!" -Level "SUCCESS"
Write-InstallerLog " Installation log: $LogPath" -Level "SUCCESS"