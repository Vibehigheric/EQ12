# EQ12 GODSTACK Ngrok Management Script
# =====================================
# Comprehensive PowerShell script for managing ngrok tunnels and integration
#
# Author: EQ12 GODSTACK
# Date: September 27, 2025
# Version: 2.0

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Start", "Stop", "Status", "Restart", "Install", "Configure", "Test", "Logs", "Cleanup")]
    [string]$Action,
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("development", "preview", "production")]
    [string]$Environment = "development",
    
    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = "C:\EQ12\ngrok.yml",
    
    [Parameter(Mandatory = $false)]
    [switch]$Force,
    
    [Parameter(Mandatory = $false)]
    [switch]$Silent,
    
    [Parameter(Mandatory = $false)]
    [int]$Timeout = 30
)

# === Configuration ===
$script:EQ12_DIR = "C:\EQ12"
$script:LOGS_DIR = "$EQ12_DIR\logs"
$script:CONFIG_DIR = "$EQ12_DIR\configs"
$script:NGROK_API = "http://127.0.0.1:4040/api/tunnels"
$script:LOGFILE = "$LOGS_DIR\ngrok_manager_$(Get-Date -Format 'yyyyMMdd').log"

# Ensure directories exist
@($LOGS_DIR, $CONFIG_DIR) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -Path $_ -ItemType Directory -Force | Out-Null
    }
}

# === Logging Functions ===
function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "DEBUG")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Write to log file
    Add-Content -Path $script:LOGFILE -Value $logEntry -Encoding UTF8
    
    # Write to console if not silent
    if (-not $Silent) {
        switch ($Level) {
            "INFO" { Write-Host $logEntry -ForegroundColor Green }
            "WARN" { Write-Host $logEntry -ForegroundColor Yellow }
            "ERROR" { Write-Host $logEntry -ForegroundColor Red }
            "DEBUG" { Write-Host $logEntry -ForegroundColor Cyan }
        }
    }
}

# === Utility Functions ===
function Test-NgrokInstalled {
    try {
        $version = & ngrok version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✅ Ngrok installed: $($version | Select-Object -First 1)" -Level INFO
            return $true
        }
    }
    catch {
        Write-Log "❌ Ngrok not found in PATH" -Level ERROR
        return $false
    }
    return $false
}

function Test-NgrokRunning {
    try {
        $response = Invoke-WebRequest -Uri $script:NGROK_API -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            return $true
        }
    }
    catch {
        return $false
    }
    return $false
}

function Get-NgrokTunnels {
    try {
        $response = Invoke-RestMethod -Uri $script:NGROK_API -TimeoutSec 10
        return $response.tunnels
    }
    catch {
        Write-Log "⚠️ Could not fetch ngrok tunnels: $($_.Exception.Message)" -Level WARN
        return @()
    }
}

function Test-EQ12Services {
    $services = @(
        @{ Name = "Dashboard"; Port = 8000; Path = "/health" },
        @{ Name = "API"; Port = 5000; Path = "/health" },
        @{ Name = "Metrics"; Port = 9100; Path = "/metrics" },
        @{ Name = "Webhook"; Port = 8080; Path = "/health" }
    )
    
    $results = @()
    foreach ($service in $services) {
        try {
            $uri = "http://localhost:$($service.Port)$($service.Path)"
            $response = Invoke-WebRequest -Uri $uri -TimeoutSec 5 -ErrorAction Stop
            $results += @{
                Name = $service.Name
                Status = "✅ Running"
                Port = $service.Port
                ResponseCode = $response.StatusCode
            }
        }
        catch {
            $results += @{
                Name = $service.Name
                Status = "❌ Not responding"
                Port = $service.Port
                Error = $_.Exception.Message
            }
        }
    }
    
    return $results
}

# === Main Action Functions ===
function Start-NgrokTunnels {
    Write-Log "🚀 Starting ngrok tunnels for EQ12 GODSTACK" -Level INFO
    
    # Check prerequisites
    if (-not (Test-NgrokInstalled)) {
        throw "Ngrok is not installed or not in PATH"
    }
    
    if (-not (Test-Path $ConfigPath)) {
        throw "Ngrok config file not found: $ConfigPath"
    }
    
    # Check if already running
    if (Test-NgrokRunning) {
        if (-not $Force) {
            Write-Log "⚠️ Ngrok is already running. Use -Force to restart." -Level WARN
            return
        } else {
            Write-Log "🔄 Force restart requested, stopping existing instance" -Level INFO
            Stop-NgrokTunnels
            Start-Sleep -Seconds 5
        }
    }
    
    # Test EQ12 services before starting tunnels
    Write-Log "🔍 Checking EQ12 services status..." -Level INFO
    $serviceResults = Test-EQ12Services
    $runningServices = $serviceResults | Where-Object { $_.Status -eq "✅ Running" }
    
    if ($runningServices.Count -eq 0) {
        Write-Log "⚠️ No EQ12 services are running. Starting tunnels anyway..." -Level WARN
    } else {
        Write-Log "✅ Found $($runningServices.Count) running EQ12 services" -Level INFO
    }
    
    # Start ngrok
    try {
        Write-Log "🌐 Starting ngrok with config: $ConfigPath" -Level INFO
        
        $ngrokArgs = @(
            "start",
            "--all",
            "--config", $ConfigPath,
            "--log", "stdout"
        )
        
        # Start ngrok in background
        $ngrokProcess = Start-Process -FilePath "ngrok" -ArgumentList $ngrokArgs -WindowStyle Hidden -PassThru
        
        Write-Log "⏳ Waiting for ngrok to initialize..." -Level INFO
        Start-Sleep -Seconds 10
        
        # Verify tunnels are up
        $retries = 0
        $maxRetries = 6
        
        while ($retries -lt $maxRetries) {
            if (Test-NgrokRunning) {
                $tunnels = Get-NgrokTunnels
                if ($tunnels.Count -gt 0) {
                    Write-Log "✅ Ngrok started successfully with $($tunnels.Count) tunnels" -Level INFO
                    
                    # Display tunnel information
                    foreach ($tunnel in $tunnels) {
                        Write-Log "🔗 $($tunnel.name): $($tunnel.public_url) → $($tunnel.config.addr)" -Level INFO
                    }
                    
                    # Save tunnel info for integration
                    $tunnelInfo = @{
                        timestamp = Get-Date -Format "o"
                        environment = $Environment
                        tunnels = $tunnels
                        process_id = $ngrokProcess.Id
                    }
                    
                    $tunnelInfoPath = "$LOGS_DIR\tunnel_info_$(Get-Date -Format 'yyyyMMddHHmmss').json"
                    $tunnelInfo | ConvertTo-Json -Depth 10 | Out-File -FilePath $tunnelInfoPath -Encoding UTF8
                    Write-Log "📄 Tunnel info saved: $tunnelInfoPath" -Level INFO
                    
                    return
                }
            }
            
            $retries++
            Write-Log "⏳ Retry $retries/$maxRetries - waiting for tunnels..." -Level INFO
            Start-Sleep -Seconds 5
        }
        
        throw "Failed to establish tunnels after $maxRetries attempts"
    }
    catch {
        Write-Log "❌ Failed to start ngrok: $($_.Exception.Message)" -Level ERROR
        throw
    }
}

function Stop-NgrokTunnels {
    Write-Log "🛑 Stopping ngrok tunnels" -Level INFO
    
    try {
        # Find ngrok processes
        $ngrokProcesses = Get-Process -Name "ngrok" -ErrorAction SilentlyContinue
        
        if ($ngrokProcesses) {
            foreach ($process in $ngrokProcesses) {
                Write-Log "🔻 Stopping ngrok process (PID: $($process.Id))" -Level INFO
                $process.Kill()
                $process.WaitForExit($Timeout * 1000)
            }
            
            Write-Log "✅ Ngrok processes stopped" -Level INFO
        } else {
            Write-Log "ℹ️ No ngrok processes found" -Level INFO
        }
        
        # Verify stopped
        Start-Sleep -Seconds 2
        if (-not (Test-NgrokRunning)) {
            Write-Log "✅ Ngrok successfully stopped" -Level INFO
        } else {
            Write-Log "⚠️ Ngrok may still be running" -Level WARN
        }
    }
    catch {
        Write-Log "❌ Error stopping ngrok: $($_.Exception.Message)" -Level ERROR
        throw
    }
}

function Get-NgrokStatus {
    Write-Log "📊 Getting ngrok status for EQ12 GODSTACK" -Level INFO
    
    $status = @{
        NgrokInstalled = Test-NgrokInstalled
        NgrokRunning = Test-NgrokRunning
        ConfigExists = Test-Path $ConfigPath
        Environment = $Environment
        Tunnels = @()
        EQ12Services = Test-EQ12Services
    }
    
    if ($status.NgrokRunning) {
        $status.Tunnels = Get-NgrokTunnels
    }
    
    # Display status
    Write-Host "`n🎯 EQ12 GODSTACK Ngrok Status" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    $installedText = if($status.NgrokInstalled) { '✅ Yes' } else { '❌ No' }
    Write-Host "📦 Ngrok Installed: $installedText" -ForegroundColor $(if($status.NgrokInstalled) { 'Green' } else { 'Red' })
    $runningText = if($status.NgrokRunning) { '✅ Yes' } else { '❌ No' }
    Write-Host "🔄 Ngrok Running: $runningText" -ForegroundColor $(if($status.NgrokRunning) { 'Green' } else { 'Red' })
    $configText = if($status.ConfigExists) { '✅ Yes' } else { '❌ No' }
    Write-Host "📄 Config Exists: $configText" -ForegroundColor $(if($status.ConfigExists) { 'Green' } else { 'Red' })
    Write-Host "🌍 Environment: $Environment" -ForegroundColor White
    Write-Host "📁 Config Path: $ConfigPath" -ForegroundColor White
    
    if ($status.Tunnels.Count -gt 0) {
        Write-Host "`n🌐 Active Tunnels ($($status.Tunnels.Count)):" -ForegroundColor Yellow
        foreach ($tunnel in $status.Tunnels) {
            Write-Host "  🔗 $($tunnel.name): $($tunnel.public_url) → $($tunnel.config.addr)" -ForegroundColor White
        }
    } else {
        Write-Host "`n🌐 Active Tunnels: None" -ForegroundColor Yellow
    }
    
    Write-Host "`n🔧 EQ12 Services:" -ForegroundColor Yellow
    foreach ($service in $status.EQ12Services) {
        $color = if ($service.Status -eq "✅ Running") { 'Green' } else { 'Red' }
        Write-Host "  $($service.Status) $($service.Name) (Port $($service.Port))" -ForegroundColor $color
    }
    
    Write-Host "=" * 50 -ForegroundColor Cyan
    
    return $status
}

function Restart-NgrokTunnels {
    Write-Log "🔄 Restarting ngrok tunnels" -Level INFO
    Stop-NgrokTunnels
    Start-Sleep -Seconds 3
    Start-NgrokTunnels
}

function Install-NgrokService {
    Write-Log "📦 Installing ngrok as Windows service" -Level INFO
    
    $taskXmlPath = "$EQ12_DIR\tasks\NgrokStart.xml"
    
    if (-not (Test-Path $taskXmlPath)) {
        Write-Log "❌ Task XML not found: $taskXmlPath" -Level ERROR
        throw "NgrokStart.xml not found. Please ensure the task definition exists."
    }
    
    try {
        # Register scheduled task
        $result = schtasks /create /tn "EQ12_NgrokAutoStart" /xml $taskXmlPath /f
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✅ Ngrok auto-start task registered successfully" -Level INFO
            
            # Test the task
            Write-Log "🧪 Testing scheduled task..." -Level INFO
            schtasks /run /tn "EQ12_NgrokAutoStart"
            
            Start-Sleep -Seconds 15
            
            if (Test-NgrokRunning) {
                Write-Log "✅ Auto-start task test successful" -Level INFO
            } else {
                Write-Log "⚠️ Auto-start task may need adjustment" -Level WARN
            }
        } else {
            throw "Failed to register scheduled task (exit code: $LASTEXITCODE)"
        }
    }
    catch {
        Write-Log "❌ Failed to install ngrok service: $($_.Exception.Message)" -Level ERROR
        throw
    }
}

function Set-NgrokConfiguration {
    Write-Log "⚙️ Configuring ngrok for EQ12 GODSTACK" -Level INFO
    
    # Check for authtoken
    $authToken = $env:NGROK_AUTH_TOKEN
    if (-not $authToken) {
        Write-Log "⚠️ NGROK_AUTH_TOKEN environment variable not set" -Level WARN
        $authToken = Read-Host -Prompt "Enter your ngrok auth token"
    }
    
    if ($authToken) {
        try {
            Write-Log "🔐 Setting ngrok auth token..." -Level INFO
            & ngrok config add-authtoken $authToken
            
            if ($LASTEXITCODE -eq 0) {
                Write-Log "✅ Auth token configured successfully" -Level INFO
            } else {
                throw "Failed to set auth token"
            }
        }
        catch {
            Write-Log "❌ Failed to configure auth token: $($_.Exception.Message)" -Level ERROR
            throw
        }
    }
    
    # Create/update ngrok.yml if needed
    if (-not (Test-Path $ConfigPath) -or $Force) {
        Write-Log "📝 Creating ngrok configuration file..." -Level INFO
        
        $ngrokConfig = @"
version: "2"
authtoken: $authToken
region: us
log_level: info
log_format: json

tunnels:
  dashboard:
    proto: http
    addr: 8000
    subdomain: eq12-dashboard-$Environment
    bind_tls: true
    schemes: [https]
    
  api:
    proto: http
    addr: 5000
    subdomain: eq12-api-$Environment
    bind_tls: true
    schemes: [https]
    
  metrics:
    proto: http
    addr: 9100
    subdomain: eq12-metrics-$Environment
    bind_tls: true
    schemes: [https]
    
  webhook:
    proto: http
    addr: 8080
    subdomain: eq12-webhook-$Environment
    bind_tls: true
    schemes: [https]
"@
        
        $ngrokConfig | Out-File -FilePath $ConfigPath -Encoding UTF8
        Write-Log "✅ Ngrok configuration saved: $ConfigPath" -Level INFO
    }
}

function Test-NgrokSetup {
    Write-Log "🧪 Testing ngrok setup for EQ12 GODSTACK" -Level INFO
    
    $testResults = @{
        Installation = Test-NgrokInstalled
        Configuration = Test-Path $ConfigPath
        Services = @()
        Connectivity = $false
        OverallStatus = "FAIL"
    }
    
    # Test EQ12 services
    $testResults.Services = Test-EQ12Services
    
    # Test ngrok connectivity if running
    if (Test-NgrokRunning) {
        $tunnels = Get-NgrokTunnels
        if ($tunnels.Count -gt 0) {
            $testResults.Connectivity = $true
            
            # Test actual tunnel connectivity
            foreach ($tunnel in $tunnels) {
                try {
                    $response = Invoke-WebRequest -Uri $tunnel.public_url -TimeoutSec 10 -ErrorAction Stop
                    Write-Log "✅ Tunnel test passed: $($tunnel.name) ($($tunnel.public_url))" -Level INFO
                }
                catch {
                    Write-Log "❌ Tunnel test failed: $($tunnel.name) - $($_.Exception.Message)" -Level ERROR
                }
            }
        }
    }
    
    # Determine overall status
    $runningServices = ($testResults.Services | Where-Object { $_.Status -eq "✅ Running" }).Count
    if ($testResults.Installation -and $testResults.Configuration -and $runningServices -gt 0) {
        $testResults.OverallStatus = "PASS"
    }
    
    # Display test results
    Write-Host "`n🧪 EQ12 Ngrok Test Results" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    $installText = if($testResults.Installation) { '✅ PASS' } else { '❌ FAIL' }
    Write-Host "📦 Installation: $installText" -ForegroundColor $(if($testResults.Installation) { 'Green' } else { 'Red' })
    $configTestText = if($testResults.Configuration) { '✅ PASS' } else { '❌ FAIL' }
    Write-Host "📄 Configuration: $configTestText" -ForegroundColor $(if($testResults.Configuration) { 'Green' } else { 'Red' })
    Write-Host "🔧 EQ12 Services: $runningServices/$($testResults.Services.Count) running" -ForegroundColor $(if($runningServices -gt 0) { 'Green' } else { 'Red' })
    $connectText = if($testResults.Connectivity) { '✅ PASS' } else { '❌ FAIL' }
    Write-Host "🌐 Connectivity: $connectText" -ForegroundColor $(if($testResults.Connectivity) { 'Green' } else { 'Red' })
    Write-Host "📊 Overall: $($testResults.OverallStatus)" -ForegroundColor $(if($testResults.OverallStatus -eq 'PASS') { 'Green' } else { 'Red' })
    Write-Host "=" * 50 -ForegroundColor Cyan
    
    return $testResults
}

function Get-NgrokLogs {
    Write-Log "📋 Retrieving ngrok logs" -Level INFO
    
    $logFiles = @(
        "$LOGS_DIR\ngrok_startup.log",
        "$LOGS_DIR\ngrok_manager_$(Get-Date -Format 'yyyyMMdd').log",
        "$env:USERPROFILE\.ngrok2\ngrok.log"
    )
    
    foreach ($logFile in $logFiles) {
        if (Test-Path $logFile) {
            Write-Host "`n📄 Log file: $logFile" -ForegroundColor Yellow
            Write-Host "=" * 80 -ForegroundColor Yellow
            Get-Content $logFile -Tail 20 | ForEach-Object {
                Write-Host $_ -ForegroundColor White
            }
            Write-Host "=" * 80 -ForegroundColor Yellow
        } else {
            Write-Log "⚠️ Log file not found: $logFile" -Level WARN
        }
    }
    
    # Show ngrok process info
    $ngrokProcesses = Get-Process -Name "ngrok" -ErrorAction SilentlyContinue
    if ($ngrokProcesses) {
        Write-Host "`n🔍 Ngrok Processes:" -ForegroundColor Yellow
        foreach ($process in $ngrokProcesses) {
            Write-Host "  PID: $($process.Id), CPU: $($process.CPU), Memory: $([math]::Round($process.WorkingSet/1MB, 2))MB" -ForegroundColor White
        }
    }
}

function Clear-NgrokData {
    Write-Log "🧹 Cleaning up ngrok data" -Level INFO
    
    if (-not $Force) {
        $confirmation = Read-Host "This will stop ngrok and clean up logs. Continue? (y/N)"
        if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
            Write-Log "ℹ️ Cleanup cancelled by user" -Level INFO
            return
        }
    }
    
    # Stop ngrok
    Stop-NgrokTunnels
    
    # Clean up log files
    $cleanupItems = @(
        "$LOGS_DIR\ngrok_*.log",
        "$LOGS_DIR\tunnel_*.json",
        "$LOGS_DIR\discussion_*.md"
    )
    
    $cleanedCount = 0
    foreach ($pattern in $cleanupItems) {
        $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            try {
                Remove-Item $file.FullName -Force
                $cleanedCount++
                Write-Log "🗑️ Removed: $($file.Name)" -Level INFO
            }
            catch {
                Write-Log "⚠️ Could not remove: $($file.Name) - $($_.Exception.Message)" -Level WARN
            }
        }
    }
    
    Write-Log "✅ Cleanup completed. Removed $cleanedCount files." -Level INFO
}

# === Main Script Execution ===
try {
    Write-Log "🎯 EQ12 Ngrok Manager - Action: $Action, Environment: $Environment" -Level INFO
    
    switch ($Action) {
        "Start" { Start-NgrokTunnels }
        "Stop" { Stop-NgrokTunnels }
        "Status" { Get-NgrokStatus }
        "Restart" { Restart-NgrokTunnels }
        "Install" { Install-NgrokService }
        "Configure" { Set-NgrokConfiguration }
        "Test" { Test-NgrokSetup }
        "Logs" { Get-NgrokLogs }
        "Cleanup" { Clear-NgrokData }
    }
    
    Write-Log "✅ Action '$Action' completed successfully" -Level INFO
}
catch {
    Write-Log "❌ Action '$Action' failed: $($_.Exception.Message)" -Level ERROR
    exit 1
}

# === Usage Examples ===
<#
.SYNOPSIS
EQ12 GODSTACK Ngrok Management Script

.DESCRIPTION
Comprehensive PowerShell script for managing ngrok tunnels integrated with EQ12 GODSTACK

.PARAMETER Action
The action to perform: Start, Stop, Status, Restart, Install, Configure, Test, Logs, Cleanup

.PARAMETER Environment
The environment configuration: development, preview, production

.PARAMETER ConfigPath
Path to ngrok configuration file (default: C:\EQ12\ngrok.yml)

.PARAMETER Force
Force the action without prompts

.PARAMETER Silent
Suppress console output (logging only)

.PARAMETER Timeout
Timeout in seconds for operations (default: 30)

.EXAMPLE
.\eq12_ngrok_manager.ps1 -Action Start
Start ngrok tunnels with default configuration

.EXAMPLE
.\eq12_ngrok_manager.ps1 -Action Status
Show current status of ngrok and EQ12 services

.EXAMPLE
.\eq12_ngrok_manager.ps1 -Action Install
Install ngrok as a Windows service

.EXAMPLE
.\eq12_ngrok_manager.ps1 -Action Configure -Environment production
Configure ngrok for production environment

.EXAMPLE
.\eq12_ngrok_manager.ps1 -Action Test
Run comprehensive tests of the ngrok setup

.NOTES
Author: EQ12 GODSTACK
Version: 2.0
Requires: PowerShell 5.1+, ngrok CLI
#>