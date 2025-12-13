#requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('start', 'stop', 'restart', 'status', 'test')]
    [string]$Action,

    [int]$Port = 3000,

    # If node isn't on PATH, set $env:EQ12_NODE to the full node.exe path
    [string]$NodePath = $(if ($env:EQ12_NODE) { $env:EQ12_NODE } else { (Get-Command node -ErrorAction SilentlyContinue).Source }),

    # Adjust if your server file lives elsewhere
    [string]$ScriptPath = (Join-Path $PSScriptRoot 'eq12_dashboard_server.js'),

    [string]$LogPath = (Join-Path $PSScriptRoot 'logs\dashboard-server.log')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'# Ensure logs directory exists
$LogDir = Split-Path $LogFile -Parent
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
}

function Test-ServerHealth {
    param([int]$TestPort = $Port)

    try {
        $Response = Invoke-WebRequest -Uri "http://localhost:$TestPort/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        if ($Response.StatusCode -eq 200) {
            Write-Log "Server health check passed (Status: $($Response.StatusCode))" "SUCCESS"
            return $true
        }
        else {
            Write-Log "Server responded with unexpected status: $($Response.StatusCode)" "WARNING"
            return $false
        }
    }
    catch {
        Write-Log "Server health check failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-RedirectHandling {
    param([int]$TestPort = $Port)

    Write-Log "Testing redirect handling..." "INFO"

    try {
        # Test GET request to root (should redirect)
        $GetResponse = Invoke-WebRequest -Uri "http://localhost:$TestPort/" -Method GET -MaximumRedirection 0 -ErrorAction SilentlyContinue
        if ($GetResponse.StatusCode -eq 302) {
            $RedirectLocation = $GetResponse.Headers.Location
            Write-Log "Root redirect works: 302 -> $RedirectLocation" "SUCCESS"

            # Test the redirect target
            $DashboardResponse = Invoke-WebRequest -Uri "http://localhost:$TestPort/dashboard" -Method GET -TimeoutSec 5 -ErrorAction Stop
            if ($DashboardResponse.StatusCode -eq 200) {
                Write-Log "Dashboard endpoint accessible (Status: $($DashboardResponse.StatusCode))" "SUCCESS"
                return $true
            }
        }
        else {
            Write-Log "Expected 302 redirect, got: $($GetResponse.StatusCode)" "ERROR"
        }
    }
    catch {
        Write-Log "Redirect test failed: $($_.Exception.Message)" "ERROR"
    }

    return $false
}

function Start-DashboardServer {
    Write-Log "Starting EQ12 Dashboard Server..." "INFO"

    # Check if server script exists
    if (!(Test-Path $ServerScript)) {
        Write-Log "Server script not found: $ServerScript" "ERROR"
        return $false
    }

    # Stop any existing processes
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    # Set environment and start server
    $env:PORT = $Port
    $env:NODE_ENV = "production"
    $env:PATH = "$NodejsPath;$env:PATH"

    try {
        Write-Log "Starting Node.js server on port $Port..." "INFO"

        # Start the server as background process
        $ProcessArgs = @{
            FilePath         = "$NodejsPath\node.exe"
            ArgumentList     = @($ServerScript)
            WorkingDirectory = $PSScriptRoot
            WindowStyle      = "Hidden"
        }

        Start-Process @ProcessArgs
        Start-Sleep -Seconds 4

        # Test if server started successfully
        if (Test-ServerHealth -TestPort $Port) {
            Write-Log "Dashboard server started successfully" "SUCCESS"

            # Test redirect handling
            if (Test-RedirectHandling -TestPort $Port) {
                Write-Log "All server tests passed!" "SUCCESS"
                Write-Log "Access dashboard at: http://localhost:$Port/" "INFO"
                return $true
            }
            else {
                Write-Log "Server started but redirect tests failed" "WARNING"
                return $false
            }
        }
        else {
            Write-Log "Server failed to start properly" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Failed to start server: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Stop-DashboardServer {
    Write-Log "Stopping EQ12 Dashboard Server..." "INFO"

    try {
        Get-Process -Name "node" -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Log "Stopping Node.js process (PID: $($_.Id))" "INFO"
            Stop-Process -Id $_.Id -Force
        }
        Start-Sleep -Seconds 2
        Write-Log "Dashboard server stopped" "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Failed to stop server: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Main execution
Write-Log "=== EQ12 Dashboard Server Manager ===" "INFO"

switch ($Action.ToLower()) {
    "start" {
        if (Start-DashboardServer) {
            Write-Log "Server startup completed successfully" "SUCCESS"
            exit 0
        }
        else {
            Write-Log "Server startup failed" "ERROR"
            exit 1
        }
    }
    "stop" {
        if (Stop-DashboardServer) {
            exit 0
        }
        else {
            exit 1
        }
    }
    "restart" {
        Stop-DashboardServer
        Start-Sleep -Seconds 2
        if (Start-DashboardServer) {
            Write-Log "Server restart completed successfully" "SUCCESS"
            exit 0
        }
        else {
            Write-Log "Server restart failed" "ERROR"
            exit 1
        }
    }
    "test" {
        if (Test-ServerHealth -TestPort $Port) {
            Test-RedirectHandling -TestPort $Port
        }
    }
    default {
        Write-Host "Usage: .\Manage-DashboardServer.ps1 -Action [start|stop|restart|test] [-Port 3000]"
        exit 1
    }
}
