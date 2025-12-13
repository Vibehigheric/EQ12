# File: C:\EQ12\eq12_x_factor_service.ps1
# -----------------------------------------------------------------------------
# EQ12 X-Factor Master Service Installer & Manager
# Installs and manages the eq12_x_factor_master.py script as a Windows service.
# Requires: NSSM.exe (placed in C:\EQ12\bin or accessible via $env:Path)
# -----------------------------------------------------------------------------

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("install", "uninstall", "start", "stop", "status", "download-nssm")]
    [string]$Action,

    [string]$ServiceName = "EQ12_XFactorMaster",
    [string]$ScriptPath = "C:\EQ12\eq12_x_factor_pipeline.py",
    [string]$PythonExe = "python.exe",
    [string]$NssmPath = "C:\EQ12\bin\nssm.exe"
)

# === CONFIGURATION ===
$AppPath = $PythonExe
$AppParameters = $ScriptPath
$AppDirectory = "C:\EQ12"
$AppLogPath = "C:\EQ12\logs\$ServiceName.log"

# === UTILITIES ===

function Write-ServiceLog {
    param([string]$Message, [string]$Level = "INFO")

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        "INFO" { Write-Host $logEntry -ForegroundColor Cyan }
        default { Write-Host $logEntry }
    }
}

function Test-NssmDependency {
    if (-not (Test-Path $NssmPath)) {
        Write-ServiceLog "NSSM dependency not found at '$NssmPath'." "ERROR"
        Write-ServiceLog "Use -Action download-nssm to automatically download NSSM." "INFO"
        return $false
    }
    return $true
}

function Test-PythonScript {
    if (-not (Test-Path $ScriptPath)) {
        Write-ServiceLog "Python script not found at '$ScriptPath'." "ERROR"
        return $false
    }
    return $true
}

function Download-NSSM {
    Write-ServiceLog "Downloading NSSM (Non-Sucking Service Manager)..." "INFO"

    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $tempZip = "$env:TEMP\nssm.zip"
    $extractPath = "$env:TEMP\nssm"
    $binDir = Split-Path $NssmPath -Parent

    try {
        # Create bin directory if it doesn't exist
        if (-not (Test-Path $binDir)) {
            New-Item -ItemType Directory -Path $binDir -Force | Out-Null
            Write-ServiceLog "Created directory: $binDir" "SUCCESS"
        }

        # Download NSSM
        Write-ServiceLog "Downloading from: $nssmUrl" "INFO"
        Invoke-WebRequest -Uri $nssmUrl -OutFile $tempZip -UseBasicParsing

        # Extract NSSM
        Write-ServiceLog "Extracting NSSM..." "INFO"
        Expand-Archive -Path $tempZip -DestinationPath $extractPath -Force

        # Copy the appropriate architecture version
        $arch = if ([Environment]::Is64BitOperatingSystem) { "win64" } else { "win32" }
        $nssmExe = Get-ChildItem -Path $extractPath -Recurse -Name "nssm.exe" | Where-Object { $_ -like "*$arch*" } | Select-Object -First 1

        if ($nssmExe) {
            $sourcePath = Get-ChildItem -Path $extractPath -Recurse -Filter "nssm.exe" | Where-Object { $_.FullName -like "*$arch*" } | Select-Object -First 1
            Copy-Item -Path $sourcePath.FullName -Destination $NssmPath -Force
            Write-ServiceLog "NSSM installed successfully to: $NssmPath" "SUCCESS"
        } else {
            throw "Could not find nssm.exe in downloaded archive"
        }

        # Cleanup
        Remove-Item $tempZip -Force -ErrorAction SilentlyContinue
        Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue

        return $true
    }
    catch {
        Write-ServiceLog "Failed to download/install NSSM: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# === CORE FUNCTIONS ===

function Install-Service {
    Write-ServiceLog "Installing Windows Service: $ServiceName..." "INFO"

    try {
        # Use NSSM to install the service
        & $NssmPath install $ServiceName $AppPath $AppParameters
        if ($LASTEXITCODE -ne 0) {
            throw "NSSM install failed with exit code: $LASTEXITCODE"
        }

        # Configure service properties
        Write-ServiceLog "Configuring service properties..." "INFO"

        # Basic configuration
        & $NssmPath set $ServiceName DisplayName "EQ12 X-Factor Trade Engine"
        & $NssmPath set $ServiceName Description "Real-time X/Twitter sentiment pipeline with auto-trade execution and CLV tracking."

        # Working directory and logging
        & $NssmPath set $ServiceName AppDirectory $AppDirectory
        & $NssmPath set $ServiceName AppStdout $AppLogPath
        & $NssmPath set $ServiceName AppStderr $AppLogPath

        # Log rotation (10MB limit)
        & $NssmPath set $ServiceName AppRotateFiles 1
        & $NssmPath set $ServiceName AppRotateBytes 10485760
        & $NssmPath set $ServiceName AppRotateOnline 1

        # Auto-restart configuration (critical for 24/7 operation)
        & $NssmPath set $ServiceName AppThrottle 1500  # Wait 1.5 seconds before restart
        & $NssmPath set $ServiceName AppExit Default Restart
        & $NssmPath set $ServiceName AppRestartDelay 10000  # 10 second delay between restarts

        # Set startup type to Automatic (Delayed Start)
        Set-Service -Name $ServiceName -StartupType Automatic

        Write-ServiceLog "Service installed and configured for auto-restart." "SUCCESS"
        Write-ServiceLog "Log rotation enabled at $AppLogPath" "SUCCESS"

        # Start the service immediately
        Start-Service -Name $ServiceName
        Write-ServiceLog "Service started successfully." "SUCCESS"

        # Display service status
        Get-Service -Name $ServiceName | Format-Table Name, Status, StartType, DisplayName -AutoSize

    }
    catch {
        Write-ServiceLog "Failed to install service: $($_.Exception.Message)" "ERROR"
        return $false
    }

    return $true
}

function Uninstall-Service {
    Write-ServiceLog "Uninstalling Windows Service: $ServiceName..." "INFO"

    try {
        # Stop the service if it's running
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
        if ($service -and $service.Status -eq 'Running') {
            Write-ServiceLog "Stopping service..." "INFO"
            Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 3
        }

        # Remove the service
        & $NssmPath remove $ServiceName confirm

        if ($LASTEXITCODE -eq 0) {
            Write-ServiceLog "Service uninstalled successfully." "SUCCESS"
        } else {
            Write-ServiceLog "Service removal may have failed. Check manually." "WARNING"
        }
    }
    catch {
        Write-ServiceLog "Error during uninstall: $($_.Exception.Message)" "ERROR"
        return $false
    }

    return $true
}

function Start-EQ12Service {
    Write-ServiceLog "Starting service: $ServiceName..." "INFO"

    try {
        Start-Service -Name $ServiceName
        Start-Sleep -Seconds 2

        $service = Get-Service -Name $ServiceName
        if ($service.Status -eq 'Running') {
            Write-ServiceLog "Service started successfully." "SUCCESS"
            return $true
        } else {
            Write-ServiceLog "Service failed to start. Current status: $($service.Status)" "ERROR"
            return $false
        }
    }
    catch {
        Write-ServiceLog "Failed to start service: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Stop-EQ12Service {
    Write-ServiceLog "Stopping service: $ServiceName..." "INFO"

    try {
        Stop-Service -Name $ServiceName -Force
        Start-Sleep -Seconds 2

        $service = Get-Service -Name $ServiceName
        if ($service.Status -eq 'Stopped') {
            Write-ServiceLog "Service stopped successfully." "SUCCESS"
            return $true
        } else {
            Write-ServiceLog "Service may still be running. Current status: $($service.Status)" "WARNING"
            return $false
        }
    }
    catch {
        Write-ServiceLog "Failed to stop service: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Get-ServiceStatus {
    Write-ServiceLog "Checking service status..." "INFO"

    try {
        $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue

        if ($service) {
            Write-ServiceLog "Service found: $ServiceName" "SUCCESS"

            # Display detailed service information
            $service | Format-Table Name, Status, StartType, DisplayName -AutoSize

            # Check if log file exists and show recent entries
            if (Test-Path $AppLogPath) {
                Write-ServiceLog "Recent log entries:" "INFO"
                Get-Content $AppLogPath -Tail 10 | ForEach-Object { Write-Host "  $_" }
            }

            # Show process information if running
            if ($service.Status -eq 'Running') {
                $processes = Get-WmiObject -Class Win32_Service | Where-Object { $_.Name -eq $ServiceName }
                if ($processes) {
                    Write-ServiceLog "Process ID: $($processes.ProcessId)" "INFO"
                }
            }

            return $true
        } else {
            Write-ServiceLog "Service not found: $ServiceName" "ERROR"
            return $false
        }
    }
    catch {
        Write-ServiceLog "Error checking service status: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# === MAIN EXECUTION ===

Write-Host ""
Write-Host "EQ12 X-Factor Master Service Manager" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

switch ($Action.ToLower()) {
    "download-nssm" {
        $success = Download-NSSM
        exit $(if ($success) { 0 } else { 1 })
    }

    "install" {
        # Check dependencies
        if (-not (Test-NssmDependency)) {
            Write-ServiceLog "Run with -Action download-nssm first to install NSSM." "INFO"
            exit 1
        }

        if (-not (Test-PythonScript)) {
            exit 1
        }

        $success = Install-Service
        exit $(if ($success) { 0 } else { 1 })
    }

    "uninstall" {
        if (-not (Test-NssmDependency)) {
            exit 1
        }

        $success = Uninstall-Service
        exit $(if ($success) { 0 } else { 1 })
    }

    "start" {
        $success = Start-EQ12Service
        exit $(if ($success) { 0 } else { 1 })
    }

    "stop" {
        $success = Stop-EQ12Service
        exit $(if ($success) { 0 } else { 1 })
    }

    "status" {
        $success = Get-ServiceStatus
        exit $(if ($success) { 0 } else { 1 })
    }

    default {
        Write-ServiceLog "Unknown action: $Action" "ERROR"
        Write-Host "Usage: .\eq12_x_factor_service.ps1 -Action <install|uninstall|start|stop|status|download-nssm>"
        exit 1
    }
}
