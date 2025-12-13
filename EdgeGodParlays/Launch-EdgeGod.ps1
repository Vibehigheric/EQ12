# EdgeGod Expert Engine - PowerShell Launcher
# Production launcher with error handling and logging

[CmdletBinding()]
param(
    [string]$Action = "start",
    [switch]$Debug,
    [string]$Port = "8080",
    [string]$ConfigFile = ".env"
)

# Set strict mode and error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Initialize logging
$LogPath = "C:\EQ12\logs"
if (!(Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
}

$LogFile = Join-Path $LogPath "edgegod_launcher_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
}

function Test-Prerequisites {
    Write-Log "Checking prerequisites..."
    
    # Check Python
    try {
        $PythonVersion = & python --version 2>&1
        Write-Log "Found Python: $PythonVersion"
    }
    catch {
        Write-Log "Python not found in PATH" -Level "ERROR"
        return $false
    }
    
    # Check if we're in correct directory
    $EngineScript = Join-Path $PSScriptRoot "edgegod_expert_engine.py"
    if (!(Test-Path $EngineScript)) {
        Write-Log "EdgeGod engine script not found: $EngineScript" -Level "ERROR"
        return $false
    }
    
    # Check requirements file
    $RequirementsFile = Join-Path $PSScriptRoot "requirements_edgegod.txt"
    if (!(Test-Path $RequirementsFile)) {
        Write-Log "Requirements file not found: $RequirementsFile" -Level "ERROR"
        return $false
    }
    
    # Check configuration
    $ConfigPath = Join-Path $PSScriptRoot $ConfigFile
    if (!(Test-Path $ConfigPath)) {
        Write-Log "Configuration file not found: $ConfigPath" -Level "WARNING"
        Write-Log "Will use environment variables or defaults"
    }
    else {
        Write-Log "Configuration file found: $ConfigPath"
    }
    
    Write-Log "Prerequisites check passed"
    return $true
}

function Install-Dependencies {
    Write-Log "Installing Python dependencies..."
    
    try {
        Set-Location $PSScriptRoot
        & python -m pip install --upgrade pip
        & python -m pip install -r requirements_edgegod.txt
        Write-Log "Dependencies installed successfully"
    }
    catch {
        Write-Log "Failed to install dependencies: $_" -Level "ERROR"
        throw
    }
}

function Start-EdgeGodEngine {
    Write-Log "Starting EdgeGod Expert Engine..."
    
    try {
        # Set environment variables if Debug mode
        if ($Debug) {
            $env:DEBUG_MODE = "true"
            Write-Log "Debug mode enabled"
        }
        
        # Change to engine directory
        Set-Location $PSScriptRoot
        
        # Start the engine
        Write-Log "Launching engine on port $Port"
        & python launch_edgegod.py
    }
    catch {
        Write-Log "Failed to start engine: $_" -Level "ERROR"
        throw
    }
}

function Stop-EdgeGodEngine {
    Write-Log "Stopping EdgeGod Expert Engine..."
    
    try {
        # Find and stop Python processes running the engine
        $Processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
                    Where-Object { $_.CommandLine -like "*edgegod*" }
        
        if ($Processes) {
            foreach ($Process in $Processes) {
                Write-Log "Stopping process ID: $($Process.Id)"
                Stop-Process -Id $Process.Id -Force
            }
            Write-Log "Engine stopped successfully"
        }
        else {
            Write-Log "No EdgeGod engine processes found"
        }
    }
    catch {
        Write-Log "Failed to stop engine: $_" -Level "ERROR"
        throw
    }
}

function Test-EngineHealth {
    Write-Log "Testing engine health..."
    
    try {
        $HealthUrl = "http://localhost:$Port/health"
        $Response = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 10
        
        if ($Response.status -eq "healthy") {
            Write-Log "Engine is healthy"
            Write-Log "API Documentation: http://localhost:$Port/docs"
            return $true
        }
        else {
            Write-Log "Engine health check failed: $($Response.status)" -Level "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Engine health check failed: $_" -Level "ERROR"
        return $false
    }
}

function Show-Status {
    Write-Log "Checking EdgeGod Engine status..."
    
    # Check if processes are running
    $Processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
                Where-Object { $_.CommandLine -like "*edgegod*" }
    
    if ($Processes) {
        Write-Log "Engine processes found:"
        foreach ($Process in $Processes) {
            Write-Log "  PID: $($Process.Id), Started: $($Process.StartTime)"
        }
        
        # Test health if running
        if (Test-EngineHealth) {
            Write-Log "Engine is running and healthy"
        }
    }
    else {
        Write-Log "No EdgeGod engine processes found"
    }
}

function Show-Usage {
    Write-Host @"
EdgeGod Expert Engine Launcher

Usage: .\Launch-EdgeGod.ps1 -Action <action> [options]

Actions:
  start     Start the EdgeGod engine (default)
  stop      Stop the EdgeGod engine
  restart   Restart the EdgeGod engine
  status    Check engine status
  install   Install dependencies only
  test      Run health check
  help      Show this help

Options:
  -Debug           Enable debug mode
  -Port <port>     Specify port (default: 8080)
  -ConfigFile <f>  Specify config file (default: .env)

Examples:
  .\Launch-EdgeGod.ps1                        # Start engine
  .\Launch-EdgeGod.ps1 -Action stop           # Stop engine
  .\Launch-EdgeGod.ps1 -Action start -Debug   # Start with debug
  .\Launch-EdgeGod.ps1 -Action status         # Check status
"@
}

# Main execution
try {
    Write-Log "EdgeGod Expert Engine Launcher Started"
    Write-Log "Action: $Action, Port: $Port, Debug: $Debug"
    
    switch ($Action.ToLower()) {
        "start" {
            if (!(Test-Prerequisites)) {
                exit 1
            }
            Start-EdgeGodEngine
        }
        
        "stop" {
            Stop-EdgeGodEngine
        }
        
        "restart" {
            Stop-EdgeGodEngine
            Start-Sleep -Seconds 3
            if (!(Test-Prerequisites)) {
                exit 1
            }
            Start-EdgeGodEngine
        }
        
        "status" {
            Show-Status
        }
        
        "install" {
            if (!(Test-Prerequisites)) {
                exit 1
            }
            Install-Dependencies
        }
        
        "test" {
            if (Test-EngineHealth) {
                Write-Log "Health check passed"
                exit 0
            }
            else {
                Write-Log "Health check failed" -Level "ERROR"
                exit 1
            }
        }
        
        "help" {
            Show-Usage
        }
        
        default {
            Write-Log "Unknown action: $Action" -Level "ERROR"
            Show-Usage
            exit 1
        }
    }
    
    Write-Log "Operation completed successfully"
}
catch {
    Write-Log "Operation failed: $_" -Level "ERROR"
    exit 1
}
finally {
    Write-Log "EdgeGod Expert Engine Launcher Finished"
}