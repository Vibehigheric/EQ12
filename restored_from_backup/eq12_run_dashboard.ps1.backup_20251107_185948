# EQ12 Dashboard Server Management Script
param(
    [Parameter(Position = 0)]
    [ValidateSet("start", "stop", "restart", "status")]
    [string]$Action = "start",

    [int]$Port = 3000,

    [switch]$Force
)

$ServerName = "EQ12 Dashboard Server"
$ServerScript = "eq12_dashboard_server.js"
$LogFile = "logs\dashboard_server.log"

function Write-Status($Message, $Color = "White") {
    Write-Host "[EQ12 Dashboard] $Message" -ForegroundColor $Color
}

function Get-ProcessOnPort($Port) {
    try {
        $netstat = netstat -ano | Select-String ":$Port\s"
        if ($netstat) {
            $pid = ($netstat -split '\s+')[-1]
            return Get-Process -Id $pid -ErrorAction SilentlyContinue
        }
    }
    catch {
        return $null
    }
    return $null
}

function Stop-DashboardServer {
    Write-Status "Stopping dashboard server..." "Yellow"

    $process = Get-ProcessOnPort $Port
    if ($process) {
        Write-Status "Found process $($process.Id) on port $Port" "Yellow"

        if ($Force) {
            Stop-Process -Id $process.Id -Force
            Write-Status "Forcefully stopped process $($process.Id)" "Green"
        }
        else {
            Stop-Process -Id $process.Id
            Write-Status "Gracefully stopped process $($process.Id)" "Green"
        }

        Start-Sleep -Seconds 2
    }
    else {
        Write-Status "No process found on port $Port" "Yellow"
    }
}

function Start-DashboardServer {
    Write-Status "Starting dashboard server on port $Port..." "Yellow"

    # Check if port is already in use
    $existingProcess = Get-ProcessOnPort $Port
    if ($existingProcess -and -not $Force) {
        Write-Status "Port $Port is already in use by process $($existingProcess.Id)" "Red"
        Write-Status "Use -Force to stop the existing process first" "Yellow"
        return
    }

    if ($existingProcess -and $Force) {
        Stop-DashboardServer
    }

    # Ensure logs directory exists
    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    }

    # Start the server
    Write-Status "Launching Node.js server..." "Yellow"

    $env:PORT = $Port
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = "node"
    $startInfo.Arguments = $ServerScript
    $startInfo.WorkingDirectory = $PWD
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.CreateNoWindow = $true

    $process = [System.Diagnostics.Process]::Start($startInfo)

    if ($process) {
        Write-Status "Started process $($process.Id)" "Green"

        # Wait a moment and test
        Start-Sleep -Seconds 3

        try {
            $response = Invoke-WebRequest "http://localhost:$Port/health" -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Status "Server is healthy! (HTTP $($response.StatusCode))" "Green"
                Write-Status "Dashboard URL: http://localhost:$Port/dashboard" "Cyan"
                Write-Status "Health URL: http://localhost:$Port/health" "Cyan"
            }
        }
        catch {
            Write-Status "Server started but health check failed: $($_.Exception.Message)" "Red"
        }
    }
    else {
        Write-Status "Failed to start server" "Red"
    }
}

function Get-DashboardStatus {
    Write-Status "Checking dashboard server status..." "Yellow"

    $process = Get-ProcessOnPort $Port
    if ($process) {
        Write-Status "Process: $($process.ProcessName) (PID: $($process.Id))" "Green"
        Write-Status "Port: $Port" "Green"

        try {
            $response = Invoke-WebRequest "http://localhost:$Port/health" -TimeoutSec 5
            $healthData = $response.Content | ConvertFrom-Json
            Write-Status "Health Status: $($healthData.status)" "Green"
            Write-Status "Service: $($healthData.service)" "Green"
            Write-Status "Last Check: $($healthData.timestamp)" "Green"
        }
        catch {
            Write-Status "Health check failed: $($_.Exception.Message)" "Red"
        }
    }
    else {
        Write-Status "No process found on port $Port" "Red"
    }
}

# Main execution
switch ($Action.ToLower()) {
    "start" {
        Start-DashboardServer
    }
    "stop" {
        Stop-DashboardServer
    }
    "restart" {
        Stop-DashboardServer
        Start-Sleep -Seconds 2
        Start-DashboardServer
    }
    "status" {
        Get-DashboardStatus
    }
    default {
        Write-Status "Usage: .\eq12_run_dashboard.ps1 [start|stop|restart|status] [-Port 3000] [-Force]" "Yellow"
    }
}
