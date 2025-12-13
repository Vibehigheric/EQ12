# EQ12 Unified Hub Launcher
# Starts the complete Reporting, Security & Communication system

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Start", "Stop", "Status", "Report", "SecurityAudit", "TestComms")]
    [string]$Action = "Start",
    
    [Parameter(Mandatory=$false)]
    [string]$Workspace = "C:\EQ12",
    
    [Parameter(Mandatory=$false)]
    [switch]$Daemon,
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput
)

# Set error handling
$ErrorActionPreference = "Stop"

# Configure logging
$LogPath = Join-Path $Workspace "logs\hub_launcher.log"
$null = New-Item -Path (Split-Path $LogPath) -ItemType Directory -Force -ErrorAction SilentlyContinue

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Output $LogEntry
    Add-Content -Path $LogPath -Value $LogEntry
}

function Start-EQ12Hub {
    Write-Log "Starting EQ12 Unified Hub..." "INFO"
    
    try {
        # Check if Python is available
        $PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
        if (-not $PythonPath) {
            throw "Python not found in PATH"
        }
        
        # Check if hub script exists
        $HubScript = Join-Path $Workspace "scripts\eq12_reporting_security_comms_hub.py"
        if (-not (Test-Path $HubScript)) {
            throw "Hub script not found: $HubScript"
        }
        
        # Build command arguments
        $Arguments = @(
            $HubScript,
            "--workspace", $Workspace
        )
        
        if ($Daemon) {
            $Arguments += "--daemon"
        }
        
        # Start the hub
        if ($Daemon) {
            Write-Log "Starting hub as background daemon..." "INFO"
            $Process = Start-Process -FilePath $PythonPath -ArgumentList $Arguments -WindowStyle Hidden -PassThru
            Write-Log "Hub started with PID: $($Process.Id)" "INFO"
            
            # Save PID for later management
            $PidFile = Join-Path $Workspace "logs\hub.pid"
            $Process.Id | Out-File -FilePath $PidFile -Encoding ASCII
            
            return $Process
        } else {
            Write-Log "Starting hub in foreground..." "INFO"
            & $PythonPath @Arguments
        }
        
    } catch {
        Write-Log "Failed to start EQ12 Hub: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Stop-EQ12Hub {
    Write-Log "Stopping EQ12 Hub..." "INFO"
    
    try {
        $PidFile = Join-Path $Workspace "logs\hub.pid"
        
        if (Test-Path $PidFile) {
            $Pid = Get-Content $PidFile -Raw
            $Pid = $Pid.Trim()
            
            if ($Pid -and $Pid -match '^\d+$') {
                $Process = Get-Process -Id $Pid -ErrorAction SilentlyContinue
                if ($Process) {
                    Write-Log "Stopping hub process (PID: $Pid)..." "INFO"
                    Stop-Process -Id $Pid -Force
                    Remove-Item $PidFile -Force
                    Write-Log "Hub stopped successfully" "INFO"
                } else {
                    Write-Log "Hub process not found (PID: $Pid)" "WARNING"
                    Remove-Item $PidFile -Force
                }
            }
        } else {
            Write-Log "No PID file found, checking for running hub processes..." "INFO"
            
            # Find and stop any hub processes
            $HubProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | 
                Where-Object { $_.CommandLine -and $_.CommandLine -like "*eq12_reporting_security_comms_hub*" }
            
            if ($HubProcesses) {
                foreach ($Process in $HubProcesses) {
                    Write-Log "Stopping hub process (PID: $($Process.Id))..." "INFO"
                    Stop-Process -Id $Process.Id -Force
                }
                Write-Log "$($HubProcesses.Count) hub process(es) stopped" "INFO"
            } else {
                Write-Log "No running hub processes found" "INFO"
            }
        }
        
    } catch {
        Write-Log "Failed to stop EQ12 Hub: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Get-EQ12HubStatus {
    Write-Log "Checking EQ12 Hub status..." "INFO"
    
    try {
        # Check PID file
        $PidFile = Join-Path $Workspace "logs\hub.pid"
        $Status = @{
            "PidFile" = Test-Path $PidFile
            "Process" = $false
            "WebInterface" = $false
            "LastReport" = $null
        }
        
        if ($Status.PidFile) {
            $Pid = Get-Content $PidFile -Raw | ForEach-Object { $_.Trim() }
            if ($Pid -match '^\d+$') {
                $Process = Get-Process -Id $Pid -ErrorAction SilentlyContinue
                $Status.Process = $null -ne $Process
            }
        }
        
        # Check web interface
        try {
            $Response = Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
            $Status.WebInterface = $Response.StatusCode -eq 200
        } catch {
            $Status.WebInterface = $false
        }
        
        # Check last report
        $ReportsPath = Join-Path $Workspace "reports"
        if (Test-Path $ReportsPath) {
            $LatestReport = Get-ChildItem -Path $ReportsPath -Filter "daily_report_*.json" | 
                Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($LatestReport) {
                $Status.LastReport = $LatestReport.LastWriteTime
            }
        }
        
        # Display status
        Write-Host " EQ12 Hub Status:" -ForegroundColor Green
        Write-Host "  PID File: $($Status.PidFile)" -ForegroundColor $(if ($Status.PidFile) { "Green" } else { "Red" })
        Write-Host "  Process Running: $($Status.Process)" -ForegroundColor $(if ($Status.Process) { "Green" } else { "Red" })
        Write-Host "  Web Interface: $($Status.WebInterface)" -ForegroundColor $(if ($Status.WebInterface) { "Green" } else { "Red" })
        
        if ($Status.LastReport) {
            Write-Host "  Last Report: $($Status.LastReport)" -ForegroundColor Green
        } else {
            Write-Host "  Last Report: None found" -ForegroundColor Yellow
        }
        
        return $Status
        
    } catch {
        Write-Log "Failed to get EQ12 Hub status: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Invoke-EQ12Report {
    Write-Log "Generating EQ12 report..." "INFO"
    
    try {
        $HubScript = Join-Path $Workspace "scripts\eq12_reporting_security_comms_hub.py"
        $Arguments = @($HubScript, "--workspace", $Workspace, "--report-only")
        
        $Output = & python @Arguments 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Report generated successfully" "INFO"
            Write-Output $Output
        } else {
            Write-Log "Report generation failed with exit code: $LASTEXITCODE" "ERROR"
            Write-Output $Output
        }
        
    } catch {
        Write-Log "Failed to generate report: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Invoke-EQ12SecurityAudit {
    Write-Log "Running EQ12 security audit..." "INFO"
    
    try {
        $HubScript = Join-Path $Workspace "scripts\eq12_reporting_security_comms_hub.py"
        $Arguments = @($HubScript, "--workspace", $Workspace, "--security-audit")
        
        $Output = & python @Arguments 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Security audit completed successfully" "INFO"
            Write-Output $Output
        } else {
            Write-Log "Security audit failed with exit code: $LASTEXITCODE" "ERROR"
            Write-Output $Output
        }
        
    } catch {
        Write-Log "Failed to run security audit: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Test-EQ12Communications {
    Write-Log "Testing EQ12 communication channels..." "INFO"
    
    try {
        $HubScript = Join-Path $Workspace "scripts\eq12_reporting_security_comms_hub.py"
        $Arguments = @($HubScript, "--workspace", $Workspace, "--test-comms")
        
        $Output = & python @Arguments 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Communication test completed successfully" "INFO"
            Write-Output $Output
        } else {
            Write-Log "Communication test failed with exit code: $LASTEXITCODE" "ERROR"
            Write-Output $Output
        }
        
    } catch {
        Write-Log "Failed to test communications: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# Main execution
try {
    Write-Log "EQ12 Hub Launcher started with action: $Action" "INFO"
    
    switch ($Action) {
        "Start" {
            Start-EQ12Hub
        }
        "Stop" {
            Stop-EQ12Hub
        }
        "Status" {
            Get-EQ12HubStatus
        }
        "Report" {
            Invoke-EQ12Report
        }
        "SecurityAudit" {
            Invoke-EQ12SecurityAudit
        }
        "TestComms" {
            Test-EQ12Communications
        }
        default {
            Write-Log "Unknown action: $Action" "ERROR"
            Write-Host "Available actions: Start, Stop, Status, Report, SecurityAudit, TestComms" -ForegroundColor Yellow
            exit 1
        }
    }
    
    Write-Log "EQ12 Hub Launcher completed successfully" "INFO"
    
} catch {
    Write-Log "EQ12 Hub Launcher failed: $($_.Exception.Message)" "ERROR"
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
