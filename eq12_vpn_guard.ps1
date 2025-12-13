# EQ12 VPN Guard - Comprehensive WireGuard Integration for Betting System
# Ensures secure, reliable VPN connection for all betting operations
# Auto-reconnects on drops, logs all VPN activity, and protects betting pipeline

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$VpnConfig = "eq12-betting",

    [Parameter(Mandatory = $false)]
    [string]$DbPath = "C:\EQ12\eq12_bets.db",

    [Parameter(Mandatory = $false)]
    [string]$LogPath = "C:\EQ12\logs\vpn_guard.log",

    [Parameter(Mandatory = $false)]
    [string]$PipelineScript = "C:\EQ12\launch_production.py",

    [Parameter(Mandatory = $false)]
    [int]$MonitorIntervalSeconds = 30,

    [Parameter(Mandatory = $false)]
    [int]$MaxReconnectAttempts = 5,

    [Parameter(Mandatory = $false)]
    [switch]$RunPipeline,

    [Parameter(Mandatory = $false)]
    [switch]$MonitorOnly,

    [Parameter(Mandatory = $false)]
    [switch]$KillOnVpnDrop
)

# Import required modules
Import-Module -Name "Microsoft.PowerShell.Management" -Force

# Global variables
$script:LogFile = $LogPath
$script:DbPath = $DbPath
$script:VpnActive = $false
$script:LastKnownIp = ""
$script:PipelineProcess = $null
$script:ReconnectCount = 0

# Logging function
function Write-EQ12Log {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $false)]
        [ValidateSet("INFO", "WARN", "ERROR", "DEBUG")]
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"
    $logEntry = "[$timestamp] [$Level] EQ12_VPN_GUARD: $Message"

    # Write to console with color coding
    switch ($Level) {
        "INFO" { Write-Host $logEntry -ForegroundColor Green }
        "WARN" { Write-Host $logEntry -ForegroundColor Yellow }
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "DEBUG" { Write-Host $logEntry -ForegroundColor Cyan }
    }

    # Write to log file
    try {
        $logEntry | Out-File -FilePath $script:LogFile -Append -Encoding UTF8
    } catch {
        Write-Warning "Failed to write to log file: $_"
    }
}

# Initialize logging directory
function Initialize-Logging {
    $logDir = Split-Path -Parent $script:LogFile
    if (-not (Test-Path $logDir)) {
        New-Item -Path $logDir -ItemType Directory -Force | Out-Null
        Write-EQ12Log "Created log directory: $logDir"
    }
}

# Database initialization
function Initialize-VpnDatabase {
    Write-EQ12Log "Initializing VPN audit database..."

    $dbDir = Split-Path -Parent $script:DbPath
    if (-not (Test-Path $dbDir)) {
        New-Item -Path $dbDir -ItemType Directory -Force | Out-Null
    }

    # Create VPN logs table
    $createTableQuery = @"
CREATE TABLE IF NOT EXISTS vpn_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    vpn_config TEXT,
    ip_address TEXT,
    region TEXT,
    connection_status TEXT,
    reconnect_count INTEGER DEFAULT 0,
    pipeline_status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_vpn_timestamp ON vpn_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_vpn_session ON vpn_logs(session_id);
"@

    try {
        # Use sqlite3 if available, otherwise use .NET SQLite
        $sqlitePath = Get-Command sqlite3 -ErrorAction SilentlyContinue
        if ($sqlitePath) {
            $createTableQuery | & sqlite3 $script:DbPath
            Write-EQ12Log "VPN database initialized successfully with sqlite3"
        } else {
            # Fallback to PowerShell SQLite module or warn
            Write-EQ12Log "SQLite3 not found - database logging disabled" -Level "WARN"
            Write-EQ12Log "Install SQLite3 or use: winget install SQLite.SQLite" -Level "WARN"
        }
    } catch {
        Write-EQ12Log "Failed to initialize database: $_" -Level "ERROR"
    }
}

# Log VPN event to database
function Write-VpnAuditLog {
    param(
        [string]$EventType,
        [string]$IpAddress = "",
        [string]$Region = "",
        [string]$ConnectionStatus = "",
        [string]$PipelineStatus = ""
    )

    $sessionId = "eq12_vpn_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    $timestamp = [int][double]::Parse((Get-Date -UFormat %s))

    $insertQuery = @"
INSERT INTO vpn_logs (timestamp, session_id, event_type, vpn_config, ip_address, region, connection_status, reconnect_count, pipeline_status)
VALUES ($timestamp, '$sessionId', '$EventType', '$VpnConfig', '$IpAddress', '$Region', '$ConnectionStatus', $script:ReconnectCount, '$PipelineStatus');
"@

    try {
        $sqlitePath = Get-Command sqlite3 -ErrorAction SilentlyContinue
        if ($sqlitePath) {
            $insertQuery | & sqlite3 $script:DbPath
            Write-EQ12Log "Audit log written: $EventType"
        }
    } catch {
        Write-EQ12Log "Failed to write audit log: $_" -Level "ERROR"
    }
}

# Get current external IP address
function Get-ExternalIp {
    $ipServices = @(
        "https://ifconfig.me/ip",
        "https://ipinfo.io/ip",
        "https://api.ipify.org",
        "https://checkip.amazonaws.com"
    )

    foreach ($service in $ipServices) {
        try {
            $ip = (Invoke-RestMethod -Uri $service -TimeoutSec 10).Trim()
            if ($ip -match '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$') {
                return $ip
            }
        } catch {
            continue
        }
    }

    return "Unknown"
}

# Get VPN region/location info
function Get-VpnRegion {
    param([string]$IpAddress)

    if ($IpAddress -eq "Unknown") {
        return "Unknown"
    }

    try {
        $geoInfo = Invoke-RestMethod -Uri "http://ipinfo.io/$IpAddress/json" -TimeoutSec 10
        return "$($geoInfo.city), $($geoInfo.region), $($geoInfo.country)"
    } catch {
        return "Unknown"
    }
}

# Check if WireGuard tunnel is active
function Test-VpnConnection {
    try {
        # Check WireGuard service status
        $wgService = Get-Service -Name "WireGuardTunnel`$$VpnConfig" -ErrorAction SilentlyContinue
        if ($wgService -and $wgService.Status -eq "Running") {

            # Verify IP change by comparing with known non-VPN IP
            $currentIp = Get-ExternalIp
            if ($currentIp -ne "Unknown" -and $currentIp -ne $script:LastKnownIp) {
                $script:VpnActive = $true
                $script:LastKnownIp = $currentIp
                return $true
            }
        }

        $script:VpnActive = $false
        return $false
    } catch {
        Write-EQ12Log "VPN connection check failed: $_" -Level "ERROR"
        $script:VpnActive = $false
        return $false
    }
}

# Start WireGuard VPN connection
function Start-VpnConnection {
    Write-EQ12Log "Starting VPN connection: $VpnConfig"

    try {
        # Ensure WireGuard is installed
        $wgPath = "${env:ProgramFiles}\WireGuard\wireguard.exe"
        if (-not (Test-Path $wgPath)) {
            throw "WireGuard not found at $wgPath"
        }

        # Install tunnel service if not exists
        $configPath = "C:\EQ12\wireguard\$VpnConfig.conf"
        if (-not (Test-Path $configPath)) {
            throw "VPN config not found: $configPath"
        }

        # Install and start tunnel
        Start-Process -FilePath $wgPath -ArgumentList "/installtunnelservice", $configPath -Wait -WindowStyle Hidden

        # Wait for connection to establish
        Start-Sleep -Seconds 5

        # Verify connection
        if (Test-VpnConnection) {
            $ip = Get-ExternalIp
            $region = Get-VpnRegion -IpAddress $ip

            Write-EQ12Log "VPN connected successfully - IP: $ip, Region: $region"
            Write-VpnAuditLog -EventType "VPN_CONNECTED" -IpAddress $ip -Region $region -ConnectionStatus "ACTIVE"

            $script:ReconnectCount = 0
            return $true
        } else {
            throw "VPN connection verification failed"
        }
    } catch {
        Write-EQ12Log "Failed to start VPN: $_" -Level "ERROR"
        Write-VpnAuditLog -EventType "VPN_CONNECT_FAILED" -ConnectionStatus "FAILED"
        return $false
    }
}

# Stop VPN connection
function Stop-VpnConnection {
    Write-EQ12Log "Stopping VPN connection: $VpnConfig"

    try {
        $wgPath = "${env:ProgramFiles}\WireGuard\wireguard.exe"
        Start-Process -FilePath $wgPath -ArgumentList "/uninstalltunnelservice", $VpnConfig -Wait -WindowStyle Hidden

        Write-EQ12Log "VPN connection stopped"
        Write-VpnAuditLog -EventType "VPN_DISCONNECTED" -ConnectionStatus "STOPPED"

        $script:VpnActive = $false
        return $true
    } catch {
        Write-EQ12Log "Failed to stop VPN: $_" -Level "ERROR"
        return $false
    }
}

# Start betting pipeline
function Start-BettingPipeline {
    if (-not $script:VpnActive) {
        Write-EQ12Log "Cannot start pipeline - VPN not active" -Level "ERROR"
        return $false
    }

    Write-EQ12Log "Starting betting pipeline: $PipelineScript"

    try {
        # Find Python executable
        $pythonExe = "python"
        $condaPath = "${env:USERPROFILE}\miniconda3\Scripts\python.exe"
        $venvPath = "C:\EQ12\.venv\Scripts\python.exe"

        if (Test-Path $venvPath) {
            $pythonExe = $venvPath
        } elseif (Test-Path $condaPath) {
            $pythonExe = $condaPath
        }

        # Start pipeline process
        $script:PipelineProcess = Start-Process -FilePath $pythonExe -ArgumentList $PipelineScript -PassThru -WindowStyle Hidden

        Write-EQ12Log "Betting pipeline started - PID: $($script:PipelineProcess.Id)"
        Write-VpnAuditLog -EventType "PIPELINE_STARTED" -PipelineStatus "RUNNING"

        return $true
    } catch {
        Write-EQ12Log "Failed to start betting pipeline: $_" -Level "ERROR"
        Write-VpnAuditLog -EventType "PIPELINE_START_FAILED" -PipelineStatus "FAILED"
        return $false
    }
}

# Stop betting pipeline
function Stop-BettingPipeline {
    param([string]$Reason = "Manual stop")

    if ($script:PipelineProcess -and -not $script:PipelineProcess.HasExited) {
        Write-EQ12Log "Stopping betting pipeline - Reason: $Reason"

        try {
            $script:PipelineProcess.Kill()
            $script:PipelineProcess.WaitForExit(10000)  # Wait up to 10 seconds

            Write-EQ12Log "Betting pipeline stopped"
            Write-VpnAuditLog -EventType "PIPELINE_STOPPED" -PipelineStatus "STOPPED"
        } catch {
            Write-EQ12Log "Failed to stop pipeline gracefully: $_" -Level "WARN"
        }
    }

    $script:PipelineProcess = $null
}

# Monitor VPN connection and handle drops
function Start-VpnMonitoring {
    Write-EQ12Log "Starting VPN monitoring (interval: ${MonitorIntervalSeconds}s)"

    while ($true) {
        try {
            $wasActive = $script:VpnActive
            $isActive = Test-VpnConnection

            if ($wasActive -and -not $isActive) {
                # VPN dropped
                Write-EQ12Log "VPN connection lost! Initiating recovery..." -Level "WARN"
                Write-VpnAuditLog -EventType "VPN_CONNECTION_LOST" -ConnectionStatus "DROPPED"

                if ($KillOnVpnDrop -and $script:PipelineProcess) {
                    Stop-BettingPipeline -Reason "VPN connection lost"
                }

                # Attempt reconnection
                $script:ReconnectCount++
                if ($script:ReconnectCount -le $MaxReconnectAttempts) {
                    Write-EQ12Log "Reconnection attempt $script:ReconnectCount of $MaxReconnectAttempts"

                    if (Start-VpnConnection) {
                        Write-EQ12Log "VPN reconnected successfully"

                        if ($RunPipeline -and -not $script:PipelineProcess) {
                            Start-BettingPipeline
                        }
                    }
                } else {
                    Write-EQ12Log "Max reconnection attempts exceeded - manual intervention required" -Level "ERROR"
                    Write-VpnAuditLog -EventType "VPN_RECONNECT_FAILED" -ConnectionStatus "FAILED"
                    break
                }
            } elseif (-not $wasActive -and $isActive) {
                # VPN restored
                Write-EQ12Log "VPN connection restored"
            }

            # Check pipeline health
            if ($script:PipelineProcess -and $script:PipelineProcess.HasExited) {
                Write-EQ12Log "Betting pipeline exited unexpectedly" -Level "WARN"
                Write-VpnAuditLog -EventType "PIPELINE_EXITED" -PipelineStatus "EXITED"
                $script:PipelineProcess = $null
            }

            Start-Sleep -Seconds $MonitorIntervalSeconds
        } catch {
            Write-EQ12Log "Monitoring error: $_" -Level "ERROR"
            Start-Sleep -Seconds $MonitorIntervalSeconds
        }
    }
}

# Main execution
function Main {
    Write-EQ12Log "EQ12 VPN Guard starting..."
    Write-EQ12Log "Config: $VpnConfig, Pipeline: $RunPipeline, Monitor: $MonitorOnly, KillSwitch: $KillOnVpnDrop"

    # Initialize components
    Initialize-Logging
    Initialize-VpnDatabase

    # Handle Ctrl+C gracefully
    $null = Register-ObjectEvent -InputObject ([Console]) -EventName CancelKeyPress -Action {
        Write-EQ12Log "Shutdown signal received - cleaning up..."
        Stop-BettingPipeline -Reason "Shutdown signal"
        if (-not $MonitorOnly) {
            Stop-VpnConnection
        }
        exit 0
    }

    try {
        if (-not $MonitorOnly) {
            # Start VPN connection
            if (-not (Start-VpnConnection)) {
                Write-EQ12Log "Failed to establish VPN connection - aborting" -Level "ERROR"
                exit 1
            }
        }

        # Start pipeline if requested
        if ($RunPipeline -and $script:VpnActive) {
            Start-BettingPipeline
        }

        # Start monitoring
        Start-VpnMonitoring
    } catch {
        Write-EQ12Log "Critical error: $_" -Level "ERROR"
        Stop-BettingPipeline -Reason "Critical error"
        exit 1
    }
}

# Execute main function
Main
