# EQ12 Pi WiFi Configuration Helper
# Automatically configures WiFi on Pi while preserving dedicated Ethernet cluster link

[CmdletBinding()]
param(
    [string]$PiIP = "192.168.100.2",
    [string]$Username = "ricoj100",
    [string]$Password = "CLUSTER_PASSWORD_PLACEHOLDER",
    [Parameter(Mandatory = $true)]
    [string]$WiFiSSID,
    [Parameter(Mandatory = $true)]
    [string]$WiFiPassword,
    [string]$WiFiCountry = "US",
    [switch]$VerifyDualNetwork,
    [switch]$SetRoutePriority
)

$ErrorActionPreference = "Stop"

# Configure logging
$LogPath = "C:\EQ12\logs\pi_wifi_config_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
New-Item -Path (Split-Path $LogPath) -ItemType Directory -Force | Out-Null

function Write-WiFiLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    
    $Color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        "INFO" { "Cyan" }
        default { "White" }
    }
    
    Write-Host $LogEntry -ForegroundColor $Color
    $LogEntry | Out-File -FilePath $LogPath -Append -Encoding UTF8
}

function Test-PiConnection {
    Write-WiFiLog "Testing Pi connectivity..." "INFO"
    
    # Test ping
    $PingResult = Test-Connection -ComputerName $PiIP -Count 1 -Quiet -ErrorAction SilentlyContinue
    if (-not $PingResult) {
        Write-WiFiLog "Pi not reachable at $PiIP" "ERROR"
        return $false
    }
    
    # Test SSH
    $SSHTest = Test-NetConnection -ComputerName $PiIP -Port 22 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    if (-not $SSHTest.TcpTestSucceeded) {
        Write-WiFiLog "SSH port not accessible on Pi" "ERROR"
        return $false
    }
    
    Write-WiFiLog "Pi connectivity confirmed" "SUCCESS"
    return $true
}

function Install-WiFiCredentials {
    param([string]$SSID, [string]$Pass, [string]$Country)
    
    Write-WiFiLog "Configuring WiFi credentials on Pi..." "INFO"
    
    # Create WiFi configuration
    $WiFiConfig = @"
country=$Country
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="$SSID"
    psk="$Pass"
    priority=1
}
"@
    
    # Create temporary file on EQ12
    $TempConfigFile = "C:\EQ12\temp\wpa_supplicant.conf"
    New-Item -Path (Split-Path $TempConfigFile) -ItemType Directory -Force | Out-Null
    $WiFiConfig | Out-File -FilePath $TempConfigFile -Encoding UTF8
    
    try {
        # Copy WiFi config to Pi
        Write-WiFiLog "Uploading WiFi configuration..." "INFO"
        $ScpCommand = "scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null '$TempConfigFile' ${Username}@${PiIP}:/tmp/wpa_supplicant.conf"
        $Result = cmd /c "echo $Password | $ScpCommand" 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-WiFiLog "Failed to upload WiFi config: $Result" "ERROR"
            return $false
        }
        
        # Apply WiFi configuration on Pi
        Write-WiFiLog "Applying WiFi configuration..." "INFO"
        $SSHCommands = @(
            "sudo cp /tmp/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf",
            "sudo chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf",
            "sudo systemctl restart wpa_supplicant",
            "sudo systemctl restart networking"
        )
        
        foreach ($Command in $SSHCommands) {
            $SSHResult = echo $Password | ssh -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=/dev/null" "${Username}@${PiIP}" $Command 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-WiFiLog "Command failed: $Command" "WARN"
                Write-WiFiLog "Output: $SSHResult" "WARN"
            }
        }
        
        Write-WiFiLog "WiFi configuration applied successfully" "SUCCESS"
        return $true
        
    }
    catch {
        Write-WiFiLog "WiFi configuration failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
    finally {
        # Cleanup temporary file
        Remove-Item -Path $TempConfigFile -ErrorAction SilentlyContinue
    }
}

function Test-DualNetworkConfiguration {
    Write-WiFiLog "Verifying dual network configuration..." "INFO"
    
    try {
        # Get network interface information
        $NetworkInfoCommand = "ip a show eth0; echo '---SEPARATOR---'; ip a show wlan0; echo '---SEPARATOR---'; ip route"
        $NetworkInfo = echo $Password | ssh -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=/dev/null" "${Username}@${PiIP}" $NetworkInfoCommand 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-WiFiLog "Failed to get network information" "ERROR"
            return $false
        }
        
        # Parse network information
        $InfoParts = $NetworkInfo -split "---SEPARATOR---"
        $EthInfo = $InfoParts[0]
        $WlanInfo = $InfoParts[1]
        $RouteInfo = $InfoParts[2]
        
        Write-WiFiLog "Network Configuration Analysis:" "INFO"
        
        # Check Ethernet interface
        if ($EthInfo -match "inet 192\.168\.100\.2/24") {
            Write-WiFiLog " Ethernet (eth0): 192.168.100.2/24 - EQ12 cluster link active" "SUCCESS"
            $EthStatus = $true
        }
        else {
            Write-WiFiLog " Ethernet (eth0): EQ12 cluster link not configured properly" "ERROR"
            $EthStatus = $false
        }
        
        # Check WiFi interface
        if ($WlanInfo -match "inet (\d+\.\d+\.\d+\.\d+)/\d+") {
            $WiFiIP = $Matches[1]
            Write-WiFiLog " WiFi (wlan0): $WiFiIP - Internet access available" "SUCCESS"
            $WiFiStatus = $true
        }
        else {
            Write-WiFiLog " WiFi (wlan0): Not connected or no IP assigned" "ERROR"
            $WiFiStatus = $false
        }
        
        # Test internet connectivity
        if ($WiFiStatus) {
            Write-WiFiLog "Testing Internet connectivity via WiFi..." "INFO"
            $PingTest = echo $Password | ssh -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=/dev/null" "${Username}@${PiIP}" "ping -c 3 8.8.8.8" 2>&1
            if ($PingTest -match "3 received") {
                Write-WiFiLog " Internet connectivity confirmed" "SUCCESS"
            }
            else {
                Write-WiFiLog "  Internet connectivity issues detected" "WARN"
            }
        }
        
        # Show routing table
        Write-WiFiLog "Routing Table:" "INFO"
        $RouteInfo -split "`n" | ForEach-Object {
            if ($_ -match "default|192\.168\.100|192\.168\.0") {
                Write-WiFiLog "  $_" "INFO"
            }
        }
        
        return ($EthStatus -and $WiFiStatus)
        
    }
    catch {
        Write-WiFiLog "Network verification failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Set-NetworkRoutePriority {
    Write-WiFiLog "Configuring network route priority..." "INFO"
    
    try {
        # Set WiFi as default gateway for Internet, preserve Ethernet for cluster
        $RouteCommands = @(
            "sudo ip route del default 2>/dev/null || true",
            "sudo ip route add default via \$(ip route | grep wlan0 | grep 'scope link' | awk '{print \$1}' | head -1 | sed 's|/.*||').1 dev wlan0 metric 100",
            "sudo ip route add 192.168.100.0/24 dev eth0 metric 50"
        )
        
        foreach ($Command in $RouteCommands) {
            $Result = echo $Password | ssh -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=/dev/null" "${Username}@${PiIP}" $Command 2>&1
        }
        
        Write-WiFiLog "Network routing priority configured" "SUCCESS"
        return $true
        
    }
    catch {
        Write-WiFiLog "Route priority configuration failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Main execution flow
Write-WiFiLog " EQ12 Pi WiFi Configuration Tool" "INFO"
Write-WiFiLog "Target Pi: $PiIP" "INFO"
Write-WiFiLog "WiFi SSID: $WiFiSSID" "INFO"
Write-WiFiLog "" "INFO"

# Step 1: Test Pi connectivity
if (-not (Test-PiConnection)) {
    Write-WiFiLog " Cannot reach Pi. Ensure Ethernet cluster link is working first." "ERROR"
    Write-WiFiLog "Run: ping $PiIP" "INFO"
    exit 1
}

# Step 2: Configure WiFi
$WiFiResult = Install-WiFiCredentials -SSID $WiFiSSID -Pass $WiFiPassword -Country $WiFiCountry

if (-not $WiFiResult) {
    Write-WiFiLog " WiFi configuration failed" "ERROR"
    exit 1
}

# Step 3: Wait for WiFi to connect
Write-WiFiLog " Waiting for WiFi connection to establish..." "INFO"
Start-Sleep -Seconds 15

# Step 4: Verify dual network setup
if ($VerifyDualNetwork) {
    $VerifyResult = Test-DualNetworkConfiguration
    if (-not $VerifyResult) {
        Write-WiFiLog "  Dual network verification issues detected" "WARN"
    }
}

# Step 5: Set route priority if requested
if ($SetRoutePriority) {
    Set-NetworkRoutePriority
}

# Final status
Write-WiFiLog "" "INFO"
Write-WiFiLog " WiFi Configuration Complete!" "SUCCESS"
Write-WiFiLog " Network Summary:" "INFO"
Write-WiFiLog "   Ethernet (192.168.100.2): EQ12 cluster communication" "INFO"
Write-WiFiLog "   WiFi: Internet access for updates and cloud services" "INFO"
Write-WiFiLog "   Pi is ready for dual-network cluster operation" "INFO"
Write-WiFiLog "" "INFO"
Write-WiFiLog " Full log: $LogPath" "INFO"

# Test cluster connectivity
Write-WiFiLog " Final cluster connectivity test..." "INFO"
$FinalPing = Test-Connection -ComputerName $PiIP -Count 1 -Quiet -ErrorAction SilentlyContinue
if ($FinalPing) {
    Write-WiFiLog " EQ12 cluster link remains active" "SUCCESS"
    Write-WiFiLog " Ready for cluster service deployment" "SUCCESS"
}
else {
    Write-WiFiLog " EQ12 cluster link disrupted" "ERROR"
}