<#
.SYNOPSIS
    Windows Data Sentinel - Real-time System Monitoring Dashboard
.DESCRIPTION
    Enterprise-grade PowerShell monitoring dashboard providing real-time visibility into:
    - System performance (CPU, Memory, Disk, Network)
    - Critical Windows services and processes
    - Event log analysis (System, Application, Security)
    - Threshold-based alerting with Telegram integration
    - Historical trend analysis with JSON snapshots
.PARAMETER AlertThresholds
    Enable threshold-based alerting
.PARAMETER RefreshInterval
    Dashboard refresh rate in seconds (default: 5)
.PARAMETER EnableTelegram
    Send critical alerts to Telegram
.EXAMPLE
    .\windows_data_sentinel.ps1
    .\windows_data_sentinel.ps1 -AlertThresholds -EnableTelegram
    .\windows_data_sentinel.ps1 -RefreshInterval 10
.NOTES
    Part of Windows Data Sentinel project (Strategic Project #1)
    Revenue target: +$7,500/month
    Deployment model: SaaS subscription + enterprise licensing
#>

[CmdletBinding()]
param(
    [Parameter()]
    [switch]$AlertThresholds,

    [Parameter()]
    [int]$RefreshInterval = 5,

    [Parameter()]
    [switch]$EnableTelegram,

    [Parameter()]
    [string]$SnapshotDir = "C:\EQ12\data\sentinel_snapshots"
)

$ErrorActionPreference = "Continue"
Set-StrictMode -Version Latest

#region Configuration

# Monitoring thresholds
$Thresholds = @{
    CPUPercent = 85
    MemoryPercent = 90
    DiskPercent = 90
    EventLogErrorsLast5Min = 10
    CriticalServicesDown = 1
}

# Critical services to monitor
$CriticalServices = @(
    "Winmgmt",        # Windows Management Instrumentation
    "EventLog",       # Windows Event Log
    "W32Time",        # Windows Time
    "Dhcp",           # DHCP Client
    "Dnscache",       # DNS Client
    "LanmanServer",   # Server
    "LanmanWorkstation", # Workstation
    "RpcSs",          # Remote Procedure Call
    "SamSs",          # Security Accounts Manager
    "Schedule",       # Task Scheduler
    "Spooler",        # Print Spooler
    "WinDefend"       # Windows Defender
)

# Telegram configuration (read from environment)
$TelegramBotToken = $env:TELEGRAM_BOT_TOKEN
$TelegramChatId = $env:TELEGRAM_CHAT_ID

# Initialize snapshot directory
if (-not (Test-Path $SnapshotDir)) {
    New-Item -Path $SnapshotDir -ItemType Directory -Force | Out-Null
}

#endregion

#region Helper Functions

function Get-SystemMetrics {
    <#
    .SYNOPSIS
        Collect comprehensive system performance metrics
    #>
    [CmdletBinding()]
    param()

    try {
        # CPU metrics
        $CPULoad = Get-CimInstance -ClassName Win32_Processor | 
            Measure-Object -Property LoadPercentage -Average | 
            Select-Object -ExpandProperty Average

        # Memory metrics
        $OS = Get-CimInstance -ClassName Win32_OperatingSystem
        $TotalMemoryGB = [math]::Round($OS.TotalVisibleMemorySize / 1MB, 2)
        $FreeMemoryGB = [math]::Round($OS.FreePhysicalMemory / 1MB, 2)
        $UsedMemoryGB = $TotalMemoryGB - $FreeMemoryGB
        $MemoryPercent = [math]::Round(($UsedMemoryGB / $TotalMemoryGB) * 100, 2)

        # Disk metrics
        $Disks = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DriveType=3" | 
            ForEach-Object {
                @{
                    Drive = $_.DeviceID
                    TotalGB = [math]::Round($_.Size / 1GB, 2)
                    FreeGB = [math]::Round($_.FreeSpace / 1GB, 2)
                    UsedPercent = [math]::Round((($_.Size - $_.FreeSpace) / $_.Size) * 100, 2)
                }
            }

        # Network metrics (current session)
        $NetworkAdapters = Get-NetAdapterStatistics | 
            Where-Object { $_.Name -notlike "*Bluetooth*" -and $_.Name -notlike "*Virtual*" } |
            Select-Object -First 3 |
            ForEach-Object {
                @{
                    Name = $_.Name
                    ReceivedMB = [math]::Round($_.ReceivedBytes / 1MB, 2)
                    SentMB = [math]::Round($_.SentBytes / 1MB, 2)
                }
            }

        # Process metrics
        $TopProcessesCPU = Get-Process | 
            Sort-Object CPU -Descending | 
            Select-Object -First 5 -Property Name, 
                @{Name="CPU"; Expression={[math]::Round($_.CPU, 2)}},
                @{Name="MemoryMB"; Expression={[math]::Round($_.WorkingSet64 / 1MB, 2)}}

        $TopProcessesMemory = Get-Process | 
            Sort-Object WorkingSet64 -Descending | 
            Select-Object -First 5 -Property Name, 
                @{Name="MemoryMB"; Expression={[math]::Round($_.WorkingSet64 / 1MB, 2)}},
                @{Name="CPU"; Expression={[math]::Round($_.CPU, 2)}}

        return @{
            Timestamp = (Get-Date).ToUniversalTime().ToString("o")
            CPU = @{
                LoadPercent = $CPULoad
                Status = if ($CPULoad -ge $Thresholds.CPUPercent) { "CRITICAL" } else { "OK" }
            }
            Memory = @{
                TotalGB = $TotalMemoryGB
                UsedGB = $UsedMemoryGB
                FreeGB = $FreeMemoryGB
                UsedPercent = $MemoryPercent
                Status = if ($MemoryPercent -ge $Thresholds.MemoryPercent) { "CRITICAL" } else { "OK" }
            }
            Disks = $Disks
            Network = $NetworkAdapters
            TopProcesses = @{
                ByCPU = $TopProcessesCPU
                ByMemory = $TopProcessesMemory
            }
        }
    }
    catch {
        Write-Error "Failed to collect system metrics: $_"
        return $null
    }
}

function Get-ServiceStatus {
    <#
    .SYNOPSIS
        Check status of critical Windows services
    #>
    [CmdletBinding()]
    param()

    try {
        $ServiceStatus = foreach ($ServiceName in $CriticalServices) {
            $Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
            
            if ($Service) {
                @{
                    Name = $ServiceName
                    DisplayName = $Service.DisplayName
                    Status = $Service.Status.ToString()
                    StartType = $Service.StartType.ToString()
                    IsHealthy = ($Service.Status -eq "Running")
                }
            }
            else {
                @{
                    Name = $ServiceName
                    DisplayName = "Service not found"
                    Status = "NotFound"
                    StartType = "Unknown"
                    IsHealthy = $false
                }
            }
        }

        $UnhealthyCount = ($ServiceStatus | Where-Object { -not $_.IsHealthy }).Count

        return @{
            Timestamp = (Get-Date).ToUniversalTime().ToString("o")
            Services = $ServiceStatus
            TotalMonitored = $CriticalServices.Count
            Unhealthy = $UnhealthyCount
            Status = if ($UnhealthyCount -ge $Thresholds.CriticalServicesDown) { "CRITICAL" } else { "OK" }
        }
    }
    catch {
        Write-Error "Failed to check service status: $_"
        return $null
    }
}

function Get-EventLogSummary {
    <#
    .SYNOPSIS
        Analyze recent event logs for errors and warnings
    #>
    [CmdletBinding()]
    param(
        [int]$Minutes = 5
    )

    try {
        $StartTime = (Get-Date).AddMinutes(-$Minutes)
        
        $LogSummary = @{
            System = @{
                Errors = 0
                Warnings = 0
                Critical = 0
            }
            Application = @{
                Errors = 0
                Warnings = 0
                Critical = 0
            }
            Security = @{
                FailedLogins = 0
                SuccessfulLogins = 0
            }
        }

        # System log
        $SystemEvents = Get-WinEvent -FilterHashtable @{
            LogName = "System"
            StartTime = $StartTime
        } -ErrorAction SilentlyContinue

        if ($SystemEvents) {
            $LogSummary.System.Errors = ($SystemEvents | Where-Object { $_.LevelDisplayName -eq "Error" }).Count
            $LogSummary.System.Warnings = ($SystemEvents | Where-Object { $_.LevelDisplayName -eq "Warning" }).Count
            $LogSummary.System.Critical = ($SystemEvents | Where-Object { $_.LevelDisplayName -eq "Critical" }).Count
        }

        # Application log
        $AppEvents = Get-WinEvent -FilterHashtable @{
            LogName = "Application"
            StartTime = $StartTime
        } -ErrorAction SilentlyContinue

        if ($AppEvents) {
            $LogSummary.Application.Errors = ($AppEvents | Where-Object { $_.LevelDisplayName -eq "Error" }).Count
            $LogSummary.Application.Warnings = ($AppEvents | Where-Object { $_.LevelDisplayName -eq "Warning" }).Count
            $LogSummary.Application.Critical = ($AppEvents | Where-Object { $_.LevelDisplayName -eq "Critical" }).Count
        }

        # Security log (login attempts)
        $SecurityEvents = Get-WinEvent -FilterHashtable @{
            LogName = "Security"
            StartTime = $StartTime
            ID = @(4624, 4625)  # 4624 = Success, 4625 = Failed
        } -ErrorAction SilentlyContinue

        if ($SecurityEvents) {
            $LogSummary.Security.SuccessfulLogins = ($SecurityEvents | Where-Object { $_.Id -eq 4624 }).Count
            $LogSummary.Security.FailedLogins = ($SecurityEvents | Where-Object { $_.Id -eq 4625 }).Count
        }

        $TotalErrors = $LogSummary.System.Errors + $LogSummary.Application.Errors + $LogSummary.System.Critical + $LogSummary.Application.Critical

        return @{
            Timestamp = (Get-Date).ToUniversalTime().ToString("o")
            TimeWindowMinutes = $Minutes
            Summary = $LogSummary
            TotalErrors = $TotalErrors
            Status = if ($TotalErrors -ge $Thresholds.EventLogErrorsLast5Min) { "WARNING" } else { "OK" }
        }
    }
    catch {
        Write-Error "Failed to analyze event logs: $_"
        return $null
    }
}

function Send-TelegramAlert {
    <#
    .SYNOPSIS
        Send alert to Telegram bot
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Message,

        [ValidateSet("INFO", "WARNING", "CRITICAL")]
        [string]$Severity = "INFO"
    )

    if (-not $EnableTelegram) {
        return
    }

    if (-not $TelegramBotToken -or -not $TelegramChatId) {
        Write-Warning "Telegram credentials not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables."
        return
    }

    try {
        $Icon = switch ($Severity) {
            "INFO" { "[INFO]" }
            "WARNING" { "[WARNING]" }
            "CRITICAL" { "[CRITICAL]" }
        }

        $FormattedMessage = "$Icon **Windows Data Sentinel Alert**`n`n$Message`n`nTimestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')"

        $Uri = "https://api.telegram.org/bot$TelegramBotToken/sendMessage"
        $Body = @{
            chat_id = $TelegramChatId
            text = $FormattedMessage
            parse_mode = "Markdown"
        } | ConvertTo-Json

        Invoke-RestMethod -Uri $Uri -Method Post -Body $Body -ContentType "application/json" | Out-Null
        Write-Verbose "Telegram alert sent: $Severity - $Message"
    }
    catch {
        Write-Error "Failed to send Telegram alert: $_"
    }
}

function Save-Snapshot {
    <#
    .SYNOPSIS
        Save system state snapshot to JSON
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [hashtable]$Data
    )

    try {
        $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $SnapshotFile = Join-Path $SnapshotDir "sentinel_snapshot_$Timestamp.json"

        $Data | ConvertTo-Json -Depth 10 | Set-Content -Path $SnapshotFile -Encoding UTF8
        Write-Verbose "Snapshot saved: $SnapshotFile"

        # Cleanup old snapshots (keep last 100)
        $OldSnapshots = Get-ChildItem -Path $SnapshotDir -Filter "sentinel_snapshot_*.json" | 
            Sort-Object LastWriteTime -Descending | 
            Select-Object -Skip 100

        if ($OldSnapshots) {
            $OldSnapshots | Remove-Item -Force
            Write-Verbose "Cleaned up $($OldSnapshots.Count) old snapshots"
        }
    }
    catch {
        Write-Error "Failed to save snapshot: $_"
    }
}

function Show-Dashboard {
    <#
    .SYNOPSIS
        Render real-time dashboard to console
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [hashtable]$Metrics,

        [Parameter(Mandatory)]
        [hashtable]$Services,

        [Parameter(Mandatory)]
        [hashtable]$EventLogs
    )

    Clear-Host

    # Header
    Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "                    WINDOWS DATA SENTINEL - REAL-TIME DASHBOARD                 " -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')  |  Refresh: ${RefreshInterval}s" -ForegroundColor Gray
    Write-Host ""

    # System Performance
    Write-Host "┌─ SYSTEM PERFORMANCE ────────────────────────────────────────────────────────┐" -ForegroundColor White
    
    $CPUColor = if ($Metrics.CPU.Status -eq "CRITICAL") { "Red" } else { "Green" }
    Write-Host "  CPU Load:        " -NoNewline
    Write-Host "$($Metrics.CPU.LoadPercent)`%" -ForegroundColor $CPUColor -NoNewline
    Write-Host " [$($Metrics.CPU.Status)]" -ForegroundColor $CPUColor

    $MemColor = if ($Metrics.Memory.Status -eq "CRITICAL") { "Red" } else { "Green" }
    Write-Host "  Memory Usage:    " -NoNewline
    Write-Host "$($Metrics.Memory.UsedGB) GB / $($Metrics.Memory.TotalGB) GB ($($Metrics.Memory.UsedPercent)`%)" -ForegroundColor $MemColor -NoNewline
    Write-Host " [$($Metrics.Memory.Status)]" -ForegroundColor $MemColor

    Write-Host ""
    Write-Host "  Disk Usage:" -ForegroundColor Yellow
    foreach ($Disk in $Metrics.Disks) {
        $DiskColor = if ($Disk.UsedPercent -ge $Thresholds.DiskPercent) { "Red" } else { "Green" }
        Write-Host "    $($Disk.Drive) - $($Disk.UsedPercent)`% used ($($Disk.FreeGB) GB free)" -ForegroundColor $DiskColor
    }

    Write-Host ""
    Write-Host "  Network Activity (Session Total):" -ForegroundColor Yellow
    foreach ($Adapter in $Metrics.Network) {
        Write-Host "    $($Adapter.Name) - ↓ $($Adapter.ReceivedMB) MB | ↑ $($Adapter.SentMB) MB" -ForegroundColor Cyan
    }

    Write-Host "└─────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor White
    Write-Host ""

    # Critical Services
    Write-Host "┌─ CRITICAL SERVICES ─────────────────────────────────────────────────────────┐" -ForegroundColor White
    
    $ServiceColor = if ($Services.Status -eq "CRITICAL") { "Red" } else { "Green" }
    Write-Host "  Status: " -NoNewline
    Write-Host "$($Services.TotalMonitored - $Services.Unhealthy)/$($Services.TotalMonitored) services healthy" -ForegroundColor $ServiceColor -NoNewline
    Write-Host " [$($Services.Status)]" -ForegroundColor $ServiceColor

    if ($Services.Unhealthy -gt 0) {
        Write-Host ""
        Write-Host "  Unhealthy Services:" -ForegroundColor Red
        $UnhealthyServices = $Services.Services | Where-Object { -not $_.IsHealthy }
        foreach ($Service in $UnhealthyServices) {
            Write-Host "    - $($Service.DisplayName) ($($Service.Name)) - Status: $($Service.Status)" -ForegroundColor Red
        }
    }

    Write-Host "└─────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor White
    Write-Host ""

    # Event Logs
    Write-Host "┌─ EVENT LOG SUMMARY (Last $($EventLogs.TimeWindowMinutes) minutes) ───────────────────────────────┐" -ForegroundColor White
    
    $EventColor = if ($EventLogs.Status -eq "WARNING") { "Yellow" } elseif ($EventLogs.Status -eq "CRITICAL") { "Red" } else { "Green" }
    Write-Host "  Total Errors: " -NoNewline
    Write-Host "$($EventLogs.TotalErrors)" -ForegroundColor $EventColor -NoNewline
    Write-Host " [$($EventLogs.Status)]" -ForegroundColor $EventColor

    Write-Host ""
    Write-Host "  System Log:       Errors: $($EventLogs.Summary.System.Errors) | Warnings: $($EventLogs.Summary.System.Warnings) | Critical: $($EventLogs.Summary.System.Critical)" -ForegroundColor Cyan
    Write-Host "  Application Log:  Errors: $($EventLogs.Summary.Application.Errors) | Warnings: $($EventLogs.Summary.Application.Warnings) | Critical: $($EventLogs.Summary.Application.Critical)" -ForegroundColor Cyan
    Write-Host "  Security Log:     Failed Logins: $($EventLogs.Summary.Security.FailedLogins) | Successful: $($EventLogs.Summary.Security.SuccessfulLogins)" -ForegroundColor Cyan

    Write-Host "└─────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor White
    Write-Host ""

    # Top Processes
    Write-Host "┌─ TOP PROCESSES ─────────────────────────────────────────────────────────────┐" -ForegroundColor White
    Write-Host "  By CPU:" -ForegroundColor Yellow
    foreach ($Process in $Metrics.TopProcesses.ByCPU) {
        Write-Host "    $($Process.Name.PadRight(30)) CPU: $($Process.CPU)s  Memory: $($Process.MemoryMB) MB" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "  By Memory:" -ForegroundColor Yellow
    foreach ($Process in $Metrics.TopProcesses.ByMemory) {
        Write-Host "    $($Process.Name.PadRight(30)) Memory: $($Process.MemoryMB) MB  CPU: $($Process.CPU)s" -ForegroundColor Gray
    }
    Write-Host "└─────────────────────────────────────────────────────────────────────────────┘" -ForegroundColor White
    Write-Host ""

    # Footer
    Write-Host "  Press CTRL+C to exit  |  Next refresh in ${RefreshInterval} seconds..." -ForegroundColor DarkGray
}

#endregion

#region Main Monitoring Loop

Write-Host "Windows Data Sentinel starting..." -ForegroundColor Green
Write-Host "Monitoring interval: ${RefreshInterval}s" -ForegroundColor Yellow
Write-Host "Alert thresholds: $(if ($AlertThresholds) { 'ENABLED' } else { 'DISABLED' })" -ForegroundColor Yellow
Write-Host "Telegram alerts: $(if ($EnableTelegram) { 'ENABLED' } else { 'DISABLED' })" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press CTRL+C to stop monitoring..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

$IterationCount = 0
$LastAlertTime = @{}

try {
    while ($true) {
        $IterationCount++

        # Collect metrics
        $SystemMetrics = Get-SystemMetrics
        $ServiceStatus = Get-ServiceStatus
        $EventLogSummary = Get-EventLogSummary -Minutes 5

        if (-not $SystemMetrics -or -not $ServiceStatus -or -not $EventLogSummary) {
            Write-Warning "Failed to collect complete metrics. Retrying in ${RefreshInterval}s..."
            Start-Sleep -Seconds $RefreshInterval
            continue
        }

        # Display dashboard
        Show-Dashboard -Metrics $SystemMetrics -Services $ServiceStatus -EventLogs $EventLogSummary

        # Save snapshot every 10 iterations (reduces I/O)
        if ($IterationCount % 10 -eq 0) {
            $SnapshotData = @{
                Timestamp = (Get-Date).ToUniversalTime().ToString("o")
                Metrics = $SystemMetrics
                Services = $ServiceStatus
                EventLogs = $EventLogSummary
            }
            Save-Snapshot -Data $SnapshotData
        }

        # Threshold-based alerting
        if ($AlertThresholds) {
            $CurrentTime = Get-Date

            # CPU alert (max once per 5 minutes)
            if ($SystemMetrics.CPU.Status -eq "CRITICAL") {
                $AlertKey = "CPU"
                if (-not $LastAlertTime.ContainsKey($AlertKey) -or ($CurrentTime - $LastAlertTime[$AlertKey]).TotalMinutes -ge 5) {
                    Send-TelegramAlert -Message "CPU load critical: $($SystemMetrics.CPU.LoadPercent)`% (threshold: $($Thresholds.CPUPercent)`%)" -Severity "CRITICAL"
                    $LastAlertTime[$AlertKey] = $CurrentTime
                }
            }

            # Memory alert
            if ($SystemMetrics.Memory.Status -eq "CRITICAL") {
                $AlertKey = "Memory"
                if (-not $LastAlertTime.ContainsKey($AlertKey) -or ($CurrentTime - $LastAlertTime[$AlertKey]).TotalMinutes -ge 5) {
                    Send-TelegramAlert -Message "Memory usage critical: $($SystemMetrics.Memory.UsedPercent)`% (threshold: $($Thresholds.MemoryPercent)`%)" -Severity "CRITICAL"
                    $LastAlertTime[$AlertKey] = $CurrentTime
                }
            }

            # Service alert
            if ($ServiceStatus.Status -eq "CRITICAL") {
                $AlertKey = "Services"
                if (-not $LastAlertTime.ContainsKey($AlertKey) -or ($CurrentTime - $LastAlertTime[$AlertKey]).TotalMinutes -ge 5) {
                    $UnhealthyList = ($ServiceStatus.Services | Where-Object { -not $_.IsHealthy } | ForEach-Object { $_.Name }) -join ", "
                    Send-TelegramAlert -Message "Critical services down: $UnhealthyList" -Severity "CRITICAL"
                    $LastAlertTime[$AlertKey] = $CurrentTime
                }
            }

            # Event log alert
            if ($EventLogSummary.Status -eq "WARNING") {
                $AlertKey = "EventLogs"
                if (-not $LastAlertTime.ContainsKey($AlertKey) -or ($CurrentTime - $LastAlertTime[$AlertKey]).TotalMinutes -ge 10) {
                    Send-TelegramAlert -Message "High error rate in event logs: $($EventLogSummary.TotalErrors) errors in last $($EventLogSummary.TimeWindowMinutes) minutes" -Severity "WARNING"
                    $LastAlertTime[$AlertKey] = $CurrentTime
                }
            }
        }

        # Wait for next refresh
        Start-Sleep -Seconds $RefreshInterval
    }
}
catch {
    Write-Error "Monitoring loop error: $_"
    throw
}
finally {
    Write-Host "`nWindows Data Sentinel stopped." -ForegroundColor Yellow
}

#endregion
