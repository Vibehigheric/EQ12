#Requires -Version 5.1

<#
.SYNOPSIS
    EQ12 God Mode Commander - One-Click System Launcher

.DESCRIPTION
    PowerShell automation script to launch all EQ12 systems with a single command.
    Provides system orchestration, health monitoring, and comprehensive automation.

.PARAMETER Action
    Action to perform: Start, Stop, Status, or Interactive

.PARAMETER LaunchBrowser
    Whether to open the dashboard in browser

.PARAMETER Verbose
    Enable verbose logging

.EXAMPLE
    .\eq12_godmode_commander.ps1 -Action Start -LaunchBrowser -Verbose

.NOTES
    Author: EQ12 System
    Version: 2.0.0
    Requires: PowerShell 5.1+, Python 3.8+
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("Start", "Stop", "Status", "Interactive")]
    [string]$Action = "Interactive",

    [Parameter(Mandatory = $false)]
    [switch]$LaunchBrowser,

    [Parameter(Mandatory = $false)]
    [switch]$QuickMode
)

# Global configuration
$Script:EQ12Root = "C:\EQ12"
$Script:LogPath = Join-Path $EQ12Root "logs\godmode_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$Script:Processes = @{}
$Script:GodModeActive = $false

# Ensure logs directory exists
$LogDir = Split-Path $Script:LogPath -Parent
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-Log {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $false)]
        [ValidateSet("INFO", "WARNING", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )

    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"

    # Write to console with colors
    switch ($Level) {
        "INFO" { Write-Host $LogEntry -ForegroundColor Cyan }
        "WARNING" { Write-Host $LogEntry -ForegroundColor Yellow }
        "ERROR" { Write-Host $LogEntry -ForegroundColor Red }
        "SUCCESS" { Write-Host $LogEntry -ForegroundColor Green }
    }

    # Write to log file
    try {
        Add-Content -Path $Script:LogPath -Value $LogEntry -Encoding UTF8
    }
    catch {
        Write-Warning "Failed to write to log file: $_"
    }
}

function Show-EQ12Banner {
    Clear-Host
    Write-Host @"

████████████████████████████████████████████████████████████
█                                                          █
█    ███████  ███████  ████    ██████      ████████████   █
█    ██       ██    ██  ██      ██   ██    ██             █
█    █████    ███████   ██      ██████     ██  ████████   █
█    ██       ██   ██   ██      ██   ██    ██       ██    █
█    ███████  ██    ██ ████    ██    ██     ████████████   █
█                                                          █
█              GOD MODE COMMANDER v2.0                     █
█         Ultimate EQ12 System Orchestrator               █
█                                                          █
████████████████████████████████████████████████████████████

"@ -ForegroundColor Green

    Write-Host "🚀 EQ12 GOD MODE COMMANDER - System Status" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
}

function Test-Prerequisites {
    [CmdletBinding()]
    param()

    Write-Log "Testing system prerequisites..." -Level INFO

    $Prerequisites = @{
        "Python"    = { python --version 2>$null }
        "EQ12 Root" = { Test-Path $Script:EQ12Root }
        "Chrome"    = { Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe" }
        "Firefox"   = { Test-Path "C:\Program Files\Mozilla Firefox\firefox.exe" }
        "Java"      = { java -version 2>$null }
    }

    $Results = @{}
    foreach ($Name in $Prerequisites.Keys) {
        try {
            $Result = & $Prerequisites[$Name]
            $Results[$Name] = if ($Result -or $?) { "Available" } else { "Missing" }
        }
        catch {
            $Results[$Name] = "Missing"
        }
    }

    Write-Host "`n📋 System Prerequisites Check:" -ForegroundColor Yellow
    foreach ($Item in $Results.GetEnumerator()) {
        $Color = if ($Item.Value.StartsWith("Available")) { "Green" } else { "Red" }
        Write-Host "   $($Item.Key): $($Item.Value)" -ForegroundColor $Color
    }

    return $Results
}

function Get-EQ12SystemStatus {
    [CmdletBinding()]
    param()

    Write-Log "Getting comprehensive system status..." -Level INFO

    # System health metrics
    $CpuUsage = (Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 1).CounterSamples.CookedValue
    $Memory = Get-CimInstance Win32_OperatingSystem
    $MemoryUsage = [math]::Round((($Memory.TotalVisibleMemorySize - $Memory.FreePhysicalMemory) / $Memory.TotalVisibleMemorySize) * 100, 2)
    $DiskSpace = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
    $DiskUsage = [math]::Round((($DiskSpace.Size - $DiskSpace.FreeSpace) / $DiskSpace.Size) * 100, 2)

    # EQ12 processes
    $EQ12Processes = Get-Process | Where-Object {
        $_.ProcessName -match "python|chrome|firefox|java" -or
        $_.MainWindowTitle -match "EQ12"
    }

    # Module status
    $Modules = @{
        "Backtester"         = Test-Path (Join-Path $Script:EQ12Root "eq12_backtester\run.py")
        "Chrome Automation"  = Test-Path (Join-Path $Script:EQ12Root "chrome_governance_automation.py")
        "Firefox Automation" = Test-Path (Join-Path $Script:EQ12Root "scripts\firefox_governance_automation.py")
        "AI Assistant"       = Test-Path (Join-Path $Script:EQ12Root "eq12_streaming_assistant.py")
        "System Scanner"     = Test-Path (Join-Path $Script:EQ12Root "eq12_system_scanner.py")
        "Unified Dashboard"  = Test-Path (Join-Path $Script:EQ12Root "eq12_unified_dashboard.py")
        "Java Integration"   = Test-Path (Join-Path $Script:EQ12Root "eq12_java_integration\pom.xml")
    }

    $Status = [PSCustomObject]@{
        Timestamp       = Get-Date
        SystemHealth    = [PSCustomObject]@{
            CpuUsage    = $CpuUsage
            MemoryUsage = $MemoryUsage
            DiskUsage   = $DiskUsage
            HealthScore = [math]::Max(0, 100 - ($CpuUsage * 0.3) - ($MemoryUsage * 0.4) - ($DiskUsage * 0.3))
        }
        ActiveProcesses = $EQ12Processes.Count
        Modules         = $Modules
        GodModeActive   = $Script:GodModeActive
        EQ12Size        = if (Test-Path $Script:EQ12Root) {
            [math]::Round((Get-ChildItem $Script:EQ12Root -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
        }
        else { 0 }
    }

    return $Status
}

function Show-SystemStatus {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [PSCustomObject]$Status
    )

    Write-Host "`n📊 EQ12 System Status Dashboard" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

    # System Health
    $HealthColor = switch ($Status.SystemHealth.HealthScore) {
        { $_ -ge 80 } { "Green" }
        { $_ -ge 60 } { "Yellow" }
        default { "Red" }
    }

    Write-Host "🏥 System Health: " -NoNewline -ForegroundColor White
    Write-Host "$([math]::Round($Status.SystemHealth.HealthScore, 1))%" -ForegroundColor $HealthColor
    Write-Host "   CPU Usage: $([math]::Round($Status.SystemHealth.CpuUsage, 1))%" -ForegroundColor Gray
    Write-Host "   Memory Usage: $($Status.SystemHealth.MemoryUsage)%" -ForegroundColor Gray
    Write-Host "   Disk Usage: $($Status.SystemHealth.DiskUsage)%" -ForegroundColor Gray

    # Module Status
    Write-Host "`n🔧 EQ12 Modules:" -ForegroundColor Yellow
    foreach ($Module in $Status.Modules.GetEnumerator()) {
        $StatusText = if ($Module.Value) { "Ready" } else { "Missing" }
        $Color = if ($Module.Value) { "Green" } else { "Red" }
        Write-Host "   $($Module.Key): $StatusText" -ForegroundColor $Color
    }

    # System Resources
    Write-Host "`n💾 Resources:" -ForegroundColor Magenta
    Write-Host "   Active Processes: $($Status.ActiveProcesses)" -ForegroundColor Gray
    Write-Host "   EQ12 Size: $($Status.EQ12Size) MB" -ForegroundColor Gray
    Write-Host "   God Mode: $(if ($Status.GodModeActive) { '🟢 ACTIVE' } else { '⚫ INACTIVE' })" -ForegroundColor Gray
}

function Start-EQ12GodMode {
    [CmdletBinding()]
    param()

    Write-Log "🚀 INITIATING EQ12 GOD MODE SEQUENCE" -Level SUCCESS
    $Script:GodModeActive = $true

    # Define all systems to launch in God Mode
    $GodModeSystems = @(
        @{
            Name       = "Chrome Governance Automation"
            Command    = "python"
            Arguments  = @((Join-Path $Script:EQ12Root "chrome_governance_automation.py"), "--refresh-daily", "--launch-browser")
            WorkingDir = $Script:EQ12Root
            Background = $true
        },
        @{
            Name       = "Firefox Governance Setup"
            Command    = "python"
            Arguments  = @((Join-Path $Script:EQ12Root "scripts\firefox_governance_automation.py"))
            WorkingDir = $Script:EQ12Root
            Background = $true
        },
        @{
            Name       = "AI Streaming Assistant"
            Command    = "python"
            Arguments  = @((Join-Path $Script:EQ12Root "eq12_streaming_assistant.py"), "--demo")
            WorkingDir = $Script:EQ12Root
            Background = $true
        },
        @{
            Name       = "System Health Monitor"
            Command    = "python"
            Arguments  = @((Join-Path $Script:EQ12Root "eq12_system_health.py"))
            WorkingDir = $Script:EQ12Root
            Background = $true
        },
        @{
            Name       = "Unified Dashboard"
            Command    = "python"
            Arguments  = @((Join-Path $Script:EQ12Root "eq12_unified_dashboard.py"), "--port", "8080")
            WorkingDir = $Script:EQ12Root
            Background = $true
        }
    )

    $LaunchedSystems = @()
    $FailedSystems = @()

    Write-Host "`n🚀 Launching God Mode Systems..." -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

    foreach ($System in $GodModeSystems) {
        try {
            Write-Host "   Launching $($System.Name)... " -NoNewline -ForegroundColor Cyan

            if (Test-Path $System.Arguments[0]) {
                $ProcessParams = @{
                    FilePath         = $System.Command
                    ArgumentList     = $System.Arguments
                    WorkingDirectory = $System.WorkingDir
                    WindowStyle      = "Hidden"
                    PassThru         = $true
                }

                if ($System.Background) {
                    $Process = Start-Process @ProcessParams
                    $Script:Processes[$System.Name] = $Process
                    Write-Host "Started (PID: $($Process.Id))" -ForegroundColor Green
                    $LaunchedSystems += $System.Name
                }
                else {
                    $Process = Start-Process @ProcessParams -Wait
                    Write-Host "Completed" -ForegroundColor Green
                    $LaunchedSystems += $System.Name
                }

                Write-Log "Successfully launched $($System.Name)" -Level SUCCESS
                Start-Sleep -Seconds 2
            }
            else {
                Write-Host "File not found" -ForegroundColor Red
                $FailedSystems += "$($System.Name) - File not found"
                Write-Log "Failed to launch $($System.Name) - File not found: $($System.Arguments[0])" -Level ERROR
            }
        }
        catch {
            Write-Host "✗ Error: $_" -ForegroundColor Red
            $FailedSystems += "$($System.Name) - $_"
            Write-Log "Failed to launch $($System.Name): $_" -Level ERROR
        }
    }

    # Summary
    Write-Host "`n✅ God Mode Launch Summary:" -ForegroundColor Green
    Write-Host "   Successfully Launched: $($LaunchedSystems.Count) systems" -ForegroundColor Green
    Write-Host "   Failed Launches: $($FailedSystems.Count) systems" -ForegroundColor $(if ($FailedSystems.Count -eq 0) { "Green" } else { "Red" })

    if ($FailedSystems.Count -gt 0) {
        Write-Host "`n❌ Failed Systems:" -ForegroundColor Red
        foreach ($Failed in $FailedSystems) {
            Write-Host "   • $Failed" -ForegroundColor Red
        }
    }

    # Launch browser if requested
    if ($LaunchBrowser) {
        Write-Host "`n🌐 Opening EQ12 Dashboard in browser..." -ForegroundColor Cyan
        Start-Process "http://localhost:8080"
        Start-Sleep -Seconds 3
    }

    Write-Host "`n🎉 EQ12 GOD MODE ACTIVATED!" -ForegroundColor Green
    Write-Host "   Monitor systems at: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "   Press Ctrl+C to deactivate God Mode" -ForegroundColor Yellow

    return @{
        LaunchedSystems = $LaunchedSystems
        FailedSystems   = $FailedSystems
        ProcessCount    = $Script:Processes.Count
    }
}

function Stop-EQ12GodMode {
    [CmdletBinding()]
    param()

    Write-Log "🛑 DEACTIVATING EQ12 GOD MODE" -Level WARNING
    $Script:GodModeActive = $false

    $StoppedProcesses = @()
    $FailedStops = @()

    Write-Host "`n🛑 Stopping God Mode Systems..." -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

    foreach ($ProcessName in $Script:Processes.Keys) {
        try {
            $Process = $Script:Processes[$ProcessName]
            if ($Process -and -not $Process.HasExited) {
                Write-Host "   Stopping $ProcessName... " -NoNewline -ForegroundColor Cyan
                $Process.CloseMainWindow()

                if (-not $Process.WaitForExit(5000)) {
                    $Process.Kill()
                    Write-Host "Terminated" -ForegroundColor Yellow
                }
                else {
                    Write-Host "Stopped" -ForegroundColor Green
                }

                $StoppedProcesses += $ProcessName
                Write-Log "Stopped $ProcessName" -Level SUCCESS
            }
        }
        catch {
            Write-Host "✗ Error: $_" -ForegroundColor Red
            $FailedStops += "$ProcessName - $_"
            Write-Log "Failed to stop $ProcessName: $_" -Level ERROR
        }
    }

    $Script:Processes.Clear()

    # Kill any remaining EQ12 processes
    try {
        Get-Process | Where-Object { $_.ProcessName -match "python" -and $_.MainWindowTitle -match "EQ12|eq12" } | Stop-Process -Force -ErrorAction SilentlyContinue
    }
    catch {
        Write-Log "Error cleaning up processes: $_" -Level WARNING
    }

    Write-Host "`n✅ God Mode Deactivation Summary:" -ForegroundColor Green
    Write-Host "   Stopped Processes: $($StoppedProcesses.Count)" -ForegroundColor Green
    Write-Host "   Failed Stops: $($FailedStops.Count)" -ForegroundColor $(if ($FailedStops.Count -eq 0) { "Green" } else { "Red" })

    Write-Host "`n🔴 EQ12 GOD MODE DEACTIVATED" -ForegroundColor Red

    return @{
        StoppedProcesses = $StoppedProcesses
        FailedStops      = $FailedStops
    }
}

function Show-InteractiveMenu {
    [CmdletBinding()]
    param()

    do {
        Show-EQ12Banner
        $Status = Get-EQ12SystemStatus
        Show-SystemStatus -Status $Status

        Write-Host "`n🎮 EQ12 God Mode Commander" -ForegroundColor White
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
        Write-Host "1. 🚀 Activate God Mode (Launch All Systems)" -ForegroundColor Green
        Write-Host "2. 🛑 Deactivate God Mode (Stop All Systems)" -ForegroundColor Red
        Write-Host "3. 📊 Refresh System Status" -ForegroundColor Cyan
        Write-Host "4. 🔧 Test Prerequisites" -ForegroundColor Yellow
        Write-Host "5. 🌐 Open Dashboard (http://localhost:8080)" -ForegroundColor Magenta
        Write-Host "6. 📝 View Logs" -ForegroundColor Blue
        Write-Host "7. 🔄 Quick System Scan" -ForegroundColor White
        Write-Host "0. ❌ Exit" -ForegroundColor Gray

        Write-Host "`nSelect option (0-7): " -NoNewline -ForegroundColor White
        $Choice = Read-Host

        switch ($Choice) {
            "1" {
                Write-Host "`n🚨 WARNING: This will launch all EQ12 systems!" -ForegroundColor Yellow
                Write-Host "Continue? (Y/N): " -NoNewline -ForegroundColor White
                $Confirm = Read-Host
                if ($Confirm -eq "Y" -or $Confirm -eq "y") {
                    Start-EQ12GodMode
                    Write-Host "`nPress any key to continue..." -ForegroundColor Gray
                    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
                }
            }
            "2" {
                if ($Script:GodModeActive -or $Script:Processes.Count -gt 0) {
                    Stop-EQ12GodMode
                    Write-Host "`nPress any key to continue..." -ForegroundColor Gray
                    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
                }
                else {
                    Write-Host "`n⚠️ God Mode is not currently active." -ForegroundColor Yellow
                    Start-Sleep -Seconds 2
                }
            }
            "3" {
                Write-Host "`n🔄 Refreshing system status..." -ForegroundColor Cyan
                Start-Sleep -Seconds 1
            }
            "4" {
                Test-Prerequisites
                Write-Host "`nPress any key to continue..." -ForegroundColor Gray
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            }
            "5" {
                Write-Host "`n🌐 Opening dashboard..." -ForegroundColor Magenta
                Start-Process "http://localhost:8080"
                Start-Sleep -Seconds 2
            }
            "6" {
                if (Test-Path $Script:LogPath) {
                    Write-Host "`n📝 Recent log entries:" -ForegroundColor Blue
                    Get-Content $Script:LogPath -Tail 20 | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
                }
                else {
                    Write-Host "`n📝 No log file found." -ForegroundColor Yellow
                }
                Write-Host "`nPress any key to continue..." -ForegroundColor Gray
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            }
            "7" {
                Write-Host "`n🔄 Running quick system scan..." -ForegroundColor White
                if (Test-Path (Join-Path $Script:EQ12Root "eq12_system_scanner.py")) {
                    try {
                        & python (Join-Path $Script:EQ12Root "eq12_system_scanner.py") | Out-Host
                    }
                    catch {
                        Write-Host "Error running system scanner: $_" -ForegroundColor Red
                    }
                }
                else {
                    Write-Host "System scanner not found." -ForegroundColor Red
                }
                Write-Host "`nPress any key to continue..." -ForegroundColor Gray
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            }
            "0" {
                if ($Script:GodModeActive -or $Script:Processes.Count -gt 0) {
                    Write-Host "`n🛑 God Mode is active. Stop all processes before exiting? (Y/N): " -NoNewline -ForegroundColor Yellow
                    $Confirm = Read-Host
                    if ($Confirm -eq "Y" -or $Confirm -eq "y") {
                        Stop-EQ12GodMode
                    }
                }
                Write-Host "`n👋 Goodbye! EQ12 God Mode Commander shutting down..." -ForegroundColor Green
                return
            }
            default {
                Write-Host "`n❌ Invalid option. Please select 0-7." -ForegroundColor Red
                Start-Sleep -Seconds 2
            }
        }
    } while ($true)
}

# Main execution logic
try {
    Write-Log "EQ12 God Mode Commander v2.0 started" -Level SUCCESS
    Write-Log "Command line arguments: Action=$Action LaunchBrowser=$LaunchBrowser QuickMode=$QuickMode" -Level INFO

    # Ensure EQ12 root exists
    if (-not (Test-Path $Script:EQ12Root)) {
        Write-Error "EQ12 root directory not found: $Script:EQ12Root"
        exit 1
    }

    switch ($Action) {
        "Start" {
            Show-EQ12Banner
            Start-EQ12GodMode
            if ($LaunchBrowser) {
                Write-Host "`n🌐 Opening dashboard..." -ForegroundColor Cyan
                Start-Process "http://localhost:8080"
            }
        }
        "Stop" {
            Show-EQ12Banner
            Stop-EQ12GodMode
        }
        "Status" {
            Show-EQ12Banner
            $Status = Get-EQ12SystemStatus
            Show-SystemStatus -Status $Status
            Test-Prerequisites
        }
        "Interactive" {
            Show-InteractiveMenu
        }
    }
}
catch {
    Write-Log "Fatal error in God Mode Commander: $_" -Level ERROR
    Write-Error "Fatal error: $_"
    exit 1
}
finally {
    Write-Log "EQ12 God Mode Commander session ended" -Level INFO
}
