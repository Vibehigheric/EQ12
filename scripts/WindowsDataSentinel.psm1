<#
.SYNOPSIS
    Windows Data Sentinel - Helper Functions Module
.DESCRIPTION
    Extracted helper functions for testability. Import this module in tests.
#>

# Monitoring thresholds (can be overridden by calling scripts)
if (-not $Global:Thresholds) {
    $Global:Thresholds = @{
        CPUPercent = 85
        MemoryPercent = 90
        DiskPercent = 90
        EventLogErrorsLast5Min = 10
        CriticalServicesDown = 1
    }
}

# Critical services (can be overridden by calling scripts)
if (-not $Global:CriticalServices) {
    $Global:CriticalServices = @(
        "Winmgmt", "EventLog", "W32Time", "Dhcp", "Dnscache",
        "LanmanServer", "LanmanWorkstation", "RpcSs", "SamSs",
        "Schedule", "Spooler", "WinDefend"
    )
}

# Default snapshot directory
if (-not $Global:SnapshotDir) {
    $Global:SnapshotDir = "C:\EQ12\data\sentinel_snapshots"
}

# Telegram configuration
if (-not $Global:TelegramBotToken) {
    $Global:TelegramBotToken = $env:TELEGRAM_BOT_TOKEN
}
if (-not $Global:TelegramChatId) {
    $Global:TelegramChatId = $env:TELEGRAM_CHAT_ID
}
if (-not $Global:EnableTelegram) {
    $Global:EnableTelegram = $false
}

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
                Status = if ($CPULoad -ge $Global:Thresholds.CPUPercent) { "CRITICAL" } else { "OK" }
            }
            Memory = @{
                TotalGB = $TotalMemoryGB
                UsedGB = $UsedMemoryGB
                FreeGB = $FreeMemoryGB
                UsedPercent = $MemoryPercent
                Status = if ($MemoryPercent -ge $Global:Thresholds.MemoryPercent) { "CRITICAL" } else { "OK" }
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
        $ServiceStatus = foreach ($ServiceName in $Global:CriticalServices) {
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
            TotalMonitored = $Global:CriticalServices.Count
            Unhealthy = $UnhealthyCount
            Status = if ($UnhealthyCount -ge $Global:Thresholds.CriticalServicesDown) { "CRITICAL" } else { "OK" }
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
            Status = if ($TotalErrors -ge $Global:Thresholds.EventLogErrorsLast5Min) { "WARNING" } else { "OK" }
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

    if (-not $Global:EnableTelegram) {
        return
    }

    if (-not $Global:TelegramBotToken -or -not $Global:TelegramChatId) {
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

        $Uri = "https://api.telegram.org/bot$($Global:TelegramBotToken)/sendMessage"
        $Body = @{
            chat_id = $Global:TelegramChatId
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
        $SnapshotFile = Join-Path $Global:SnapshotDir "sentinel_snapshot_$Timestamp.json"

        # Ensure snapshot directory exists
        if (-not (Test-Path $Global:SnapshotDir)) {
            New-Item -Path $Global:SnapshotDir -ItemType Directory -Force | Out-Null
        }

        $Data | ConvertTo-Json -Depth 10 | Set-Content -Path $SnapshotFile -Encoding UTF8
        Write-Verbose "Snapshot saved: $SnapshotFile"

        # Cleanup old snapshots (keep last 100)
        $OldSnapshots = Get-ChildItem -Path $Global:SnapshotDir -Filter "sentinel_snapshot_*.json" | 
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

Export-ModuleMember -Function Get-SystemMetrics, Get-ServiceStatus, Get-EventLogSummary, Send-TelegramAlert, Save-Snapshot
