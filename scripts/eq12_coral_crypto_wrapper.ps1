[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

# EQ12 Coral Crypto Intelligence PowerShell Wrapper
# Easy Windows control for the complete crypto analysis stack

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("Start", "Stop", "Restart", "Status", "Monitor", "StartAll", "StopAll")]
    [string]$Action = "Status",
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("CoralAI", "DataStream", "Alerts", "ModelUpdater")]
    [string]$Component,
    
    [Parameter(Mandatory = $false)]
    [string]$ConfigPath,
    
    [Parameter(Mandatory = $false)]
    [switch]$Verbose,
    
    [Parameter(Mandatory = $false)]
    [switch]$AutoStart,
    
    [Parameter(Mandatory = $false)]
    [switch]$ShowLogs
)

# Initialize
$ErrorActionPreference = "Stop"
$WorkspacePath = "C:\EQ12"
$ScriptsPath = Join-Path $WorkspacePath "scripts"
$LogsPath = Join-Path $WorkspacePath "logs\crypto"

# Ensure directories exist
if (-not (Test-Path $LogsPath)) {
    New-Item -Path $LogsPath -ItemType Directory -Force | Out-Null
}

# Component mapping
$ComponentMap = @{
    "CoralAI" = "eq12_coral_crypto_ai.py"
    "DataStream" = "eq12_crypto_stream.py"
    "Alerts" = "eq12_alerts.py"
    "ModelUpdater" = "eq12_model_updater.py"
}

function Write-Banner {
    Write-Host ""
    Write-Host " EQ12 CORAL CRYPTO INTELLIGENCE STACK" -ForegroundColor Cyan
    Write-Host "Hardware-Accelerated Cryptocurrency Analysis" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Gray
}

function Start-Component {
    param([string]$ComponentName)
    
    if (-not $ComponentMap.ContainsKey($ComponentName)) {
        Write-Error "Unknown component: $ComponentName"
        return $false
    }
    
    $ScriptName = $ComponentMap[$ComponentName]
    $ScriptPath = Join-Path $ScriptsPath $ScriptName
    
    if (-not (Test-Path $ScriptPath)) {
        Write-Error "Script not found: $ScriptPath"
        return $false
    }
    
    Write-Host " Starting $ComponentName..." -ForegroundColor Green
    
    try {
        $ProcessArgs = @{
            FilePath = "python"
            ArgumentList = $ScriptPath
            WorkingDirectory = $ScriptsPath
            WindowStyle = "Minimized"
        }
        
        if ($ShowLogs) {
            $ProcessArgs.WindowStyle = "Normal"
        }
        
        Start-Process @ProcessArgs
        
        Write-Host " $ComponentName started successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error " Failed to start $ComponentName : $_"
        return $false
    }
}

function Stop-Component {
    param([string]$ComponentName)
    
    if (-not $ComponentMap.ContainsKey($ComponentName)) {
        Write-Error "Unknown component: $ComponentName"
        return $false
    }
    
    $ScriptName = $ComponentMap[$ComponentName]
    
    Write-Host " Stopping $ComponentName..." -ForegroundColor Yellow
    
    try {
        # Find and stop Python processes running this script
        $Processes = Get-Process python -ErrorAction SilentlyContinue | 
                    Where-Object { $_.CommandLine -like "*$ScriptName*" }
        
        if ($Processes) {
            $Processes | Stop-Process -Force
            Write-Host " $ComponentName stopped successfully" -ForegroundColor Green
        } else {
            Write-Host " $ComponentName was not running" -ForegroundColor Blue
        }
        
        return $true
    }
    catch {
        Write-Error " Failed to stop $ComponentName : $_"
        return $false
    }
}

function Get-ComponentStatus {
    Write-Host " COMPONENT STATUS" -ForegroundColor Cyan
    Write-Host "-" * 30 -ForegroundColor Gray
    
    foreach ($ComponentName in $ComponentMap.Keys) {
        $ScriptName = $ComponentMap[$ComponentName]
        $IsRunning = Get-Process python -ErrorAction SilentlyContinue | 
                    Where-Object { $_.CommandLine -like "*$ScriptName*" }
        
        $Status = if ($IsRunning) { " RUNNING" } else { " STOPPED" }
        $Color = if ($IsRunning) { "Green" } else { "Red" }
        
        Write-Host "$ComponentName : $Status" -ForegroundColor $Color
        
        if ($IsRunning) {
            $PID = $IsRunning.Id
            $StartTime = $IsRunning.StartTime
            $UpTime = (Get-Date) - $StartTime
            Write-Host "   PID: $PID | Uptime: $($UpTime.ToString("hh\:mm\:ss"))" -ForegroundColor Gray
        }
    }
}

function Start-AllComponents {
    Write-Host " Starting all components..." -ForegroundColor Cyan
    
    $Results = @{}
    
    # Start in priority order
    $StartOrder = @("DataStream", "CoralAI", "Alerts")
    
    foreach ($ComponentName in $StartOrder) {
        $Success = Start-Component -ComponentName $ComponentName
        $Results[$ComponentName] = $Success
        
        if ($Success) {
            Start-Sleep -Seconds 3  # Delay between starts
        }
    }
    
    # Summary
    $Successful = ($Results.Values | Where-Object { $_ }).Count
    $Total = $Results.Count
    
    Write-Host ""
    Write-Host " STARTUP SUMMARY: $Successful/$Total components started" -ForegroundColor Cyan
    
    foreach ($ComponentName in $Results.Keys) {
        $Status = if ($Results[$ComponentName]) { " SUCCESS" } else { " FAILED" }
        $Color = if ($Results[$ComponentName]) { "Green" } else { "Red" }
        Write-Host "$ComponentName : $Status" -ForegroundColor $Color
    }
}

function Stop-AllComponents {
    Write-Host " Stopping all components..." -ForegroundColor Yellow
    
    foreach ($ComponentName in $ComponentMap.Keys) {
        Stop-Component -ComponentName $ComponentName
        Start-Sleep -Seconds 1
    }
    
    Write-Host " All components stopped" -ForegroundColor Green
}

function Show-SystemInfo {
    Write-Host " SYSTEM INFORMATION" -ForegroundColor Cyan
    Write-Host "-" * 30 -ForegroundColor Gray
    
    Write-Host "Workspace: $WorkspacePath" -ForegroundColor White
    Write-Host "Scripts: $ScriptsPath" -ForegroundColor White
    Write-Host "Logs: $LogsPath" -ForegroundColor White
    
    # Check Python
    try {
        $PythonVersion = python --version 2>&1
        Write-Host "Python: $PythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "Python:  Not installed or not in PATH" -ForegroundColor Red
    }
    
    # Check Coral TPU libraries
    try {
        python -c "import tflite_runtime; print('TFLite Runtime:  Available')" 2>$null
        Write-Host "TFLite Runtime:  Available" -ForegroundColor Green
    }
    catch {
        Write-Host "TFLite Runtime:  Not available" -ForegroundColor Yellow
    }
    
    try {
        python -c "from pycoral.utils import edgetpu; print('Coral TPU:  Available')" 2>$null
        Write-Host "Coral TPU:  Available" -ForegroundColor Green
    }
    catch {
        Write-Host "Coral TPU:  Not available (simulation mode)" -ForegroundColor Yellow
    }
}

function Start-MonitorMode {
    Write-Host " Starting monitoring mode..." -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
    
    if ($AutoStart) {
        Start-AllComponents
        Start-Sleep -Seconds 5
    }
    
    try {
        while ($true) {
            Clear-Host
            Write-Banner
            Get-ComponentStatus
            Show-SystemInfo
            
            Write-Host ""
            Write-Host " Refreshing in 30 seconds... (Ctrl+C to stop)" -ForegroundColor Gray
            Start-Sleep -Seconds 30
        }
    }
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
    catch [System.Management.Automation.BreakException] {
        Write-Host ""
        Write-Host " Monitoring stopped by user" -ForegroundColor Yellow
    }
}

function Invoke-MasterController {
    $MasterScript = Join-Path $ScriptsPath "eq12_coral_crypto_master.py"
    
    if (-not (Test-Path $MasterScript)) {
        Write-Warning "Master controller not found: $MasterScript"
        return
    }
    
    $Args = @("--action", $Action.ToLower())
    
    if ($Component) {
        $Args += @("--component", $Component.ToLower())
    }
    
    if ($ConfigPath) {
        $Args += @("--config", $ConfigPath)
    }
    
    if ($Verbose) {
        $Args += "--verbose"
    }
    
    Write-Host " Invoking master controller..." -ForegroundColor Cyan
    
    try {
        & python $MasterScript @Args
    }
    catch {
        Write-Error " Master controller failed: $_"
    }
}

# Main execution
Write-Banner

switch ($Action) {
    "Start" {
        if ($Component) {
            Start-Component -ComponentName $Component
        } else {
            Write-Error "Component required for Start action. Use -Component parameter or StartAll action."
        }
    }
    
    "Stop" {
        if ($Component) {
            Stop-Component -ComponentName $Component
        } else {
            Write-Error "Component required for Stop action. Use -Component parameter or StopAll action."
        }
    }
    
    "Restart" {
        if ($Component) {
            Stop-Component -ComponentName $Component
            Start-Sleep -Seconds 3
            Start-Component -ComponentName $Component
        } else {
            Write-Error "Component required for Restart action"
        }
    }
    
    "Status" {
        Get-ComponentStatus
        Write-Host ""
        Show-SystemInfo
    }
    
    "StartAll" {
        Start-AllComponents
    }
    
    "StopAll" {
        Stop-AllComponents
    }
    
    "Monitor" {
        Start-MonitorMode
    }
    
    default {
        Write-Error "Unknown action: $Action"
    }
}

Write-Host ""
Write-Host " EQ12 Coral Crypto Stack Ready" -ForegroundColor Green
Write-Host "Use -Action parameter to control components" -ForegroundColor Gray
