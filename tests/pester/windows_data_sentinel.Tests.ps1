<#
.SYNOPSIS
    Pester tests for Windows Data Sentinel monitoring dashboard
.DESCRIPTION
    Comprehensive test suite validating:
    - System metrics collection (CPU, memory, disk, network)
    - Service status monitoring
    - Event log analysis
    - Threshold-based alerting
    - Snapshot generation
    - Dashboard rendering
.NOTES
    Run with: Invoke-Pester -Path .\windows_data_sentinel.Tests.ps1
#>

BeforeAll {
    # Import Windows Data Sentinel module
    $RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
    $ModulePath = Join-Path $RepoRoot "scripts\WindowsDataSentinel.psm1"

    if (-not (Test-Path $ModulePath)) {
        throw "SETUP ERROR: WindowsDataSentinel.psm1 not found at: $ModulePath"
    }

    Import-Module $ModulePath -Force

    # Mock environment variables for testing
    $env:TELEGRAM_BOT_TOKEN = "test_bot_token_123456"
    $env:TELEGRAM_CHAT_ID = "test_chat_id_789"

    # Test snapshot directory
    $Global:TestSnapshotDir = Join-Path $env:TEMP "sentinel_test_snapshots"
    if (Test-Path $Global:TestSnapshotDir) {
        Remove-Item -Path $Global:TestSnapshotDir -Recurse -Force
    }
    New-Item -Path $Global:TestSnapshotDir -ItemType Directory -Force | Out-Null

    # Configure module variables
    $Global:Thresholds = @{
        CPUPercent = 85
        MemoryPercent = 90
        DiskPercent = 90
        EventLogErrorsLast5Min = 10
        CriticalServicesDown = 1
    }

    $Global:CriticalServices = @(
        "Winmgmt", "EventLog", "W32Time", "Dhcp", "Dnscache",
        "LanmanServer", "LanmanWorkstation", "RpcSs", "SamSs",
        "Schedule", "Spooler", "WinDefend"
    )

    $Global:TelegramBotToken = $env:TELEGRAM_BOT_TOKEN
    $Global:TelegramChatId = $env:TELEGRAM_CHAT_ID
    $Global:EnableTelegram = $false
    $Global:SnapshotDir = $Global:TestSnapshotDir
}

Describe "Get-SystemMetrics" {
    It "Should return system metrics object" {
        $Result = Get-SystemMetrics
        
        $Result | Should -Not -BeNullOrEmpty
        $Result.Timestamp | Should -Not -BeNullOrEmpty
        $Result.CPU | Should -Not -BeNullOrEmpty
        $Result.Memory | Should -Not -BeNullOrEmpty
        $Result.Disks | Should -Not -BeNullOrEmpty
    }

    It "Should return valid CPU metrics" {
        $Result = Get-SystemMetrics
        
        $Result.CPU.LoadPercent | Should -BeOfType [double]
        $Result.CPU.LoadPercent | Should -BeGreaterOrEqual 0
        $Result.CPU.LoadPercent | Should -BeLessOrEqual 100
        $Result.CPU.Status | Should -Match "OK|CRITICAL"
    }

    It "Should return valid memory metrics" {
        $Result = Get-SystemMetrics
        
        $Result.Memory.TotalGB | Should -BeGreaterThan 0
        $Result.Memory.UsedGB | Should -BeGreaterOrEqual 0
        $Result.Memory.FreeGB | Should -BeGreaterOrEqual 0
        $Result.Memory.UsedPercent | Should -BeGreaterOrEqual 0
        $Result.Memory.UsedPercent | Should -BeLessOrEqual 100
        $Result.Memory.Status | Should -Match "OK|CRITICAL"
    }

    It "Should return disk information for all drives" {
        $Result = Get-SystemMetrics
        
        $Result.Disks | Should -Not -BeNullOrEmpty
        $Result.Disks.Count | Should -BeGreaterThan 0
        
        foreach ($Disk in $Result.Disks) {
            $Disk.Drive | Should -Not -BeNullOrEmpty
            $Disk.TotalGB | Should -BeGreaterThan 0
            $Disk.FreeGB | Should -BeGreaterOrEqual 0
            $Disk.UsedPercent | Should -BeGreaterOrEqual 0
            $Disk.UsedPercent | Should -BeLessOrEqual 100
        }
    }

    It "Should return network adapter statistics" {
        $Result = Get-SystemMetrics
        
        $Result.Network | Should -Not -BeNullOrEmpty
        
        foreach ($Adapter in $Result.Network) {
            $Adapter.Name | Should -Not -BeNullOrEmpty
            $Adapter.ReceivedMB | Should -BeGreaterOrEqual 0
            $Adapter.SentMB | Should -BeGreaterOrEqual 0
        }
    }

    It "Should return top processes by CPU" {
        $Result = Get-SystemMetrics
        
        $Result.TopProcesses.ByCPU | Should -Not -BeNullOrEmpty
        $Result.TopProcesses.ByCPU.Count | Should -BeGreaterOrEqual 1
        $Result.TopProcesses.ByCPU.Count | Should -BeLessOrEqual 5
        
        foreach ($Process in $Result.TopProcesses.ByCPU) {
            $Process.Name | Should -Not -BeNullOrEmpty
            $Process.CPU | Should -BeGreaterOrEqual 0
            $Process.MemoryMB | Should -BeGreaterOrEqual 0
        }
    }

    It "Should return top processes by memory" {
        $Result = Get-SystemMetrics
        
        $Result.TopProcesses.ByMemory | Should -Not -BeNullOrEmpty
        $Result.TopProcesses.ByMemory.Count | Should -BeGreaterOrEqual 1
        $Result.TopProcesses.ByMemory.Count | Should -BeLessOrEqual 5
        
        foreach ($Process in $Result.TopProcesses.ByMemory) {
            $Process.Name | Should -Not -BeNullOrEmpty
            $Process.MemoryMB | Should -BeGreaterThan 0
            $Process.CPU | Should -BeGreaterOrEqual 0
        }
    }

    It "Should include UTC timestamp in ISO 8601 format" {
        $Result = Get-SystemMetrics
        
        { [datetime]::Parse($Result.Timestamp) } | Should -Not -Throw
        $Result.Timestamp | Should -Match '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
    }
}

Describe "Get-ServiceStatus" {
    It "Should return service status object" {
        $Result = Get-ServiceStatus
        
        $Result | Should -Not -BeNullOrEmpty
        $Result.Timestamp | Should -Not -BeNullOrEmpty
        $Result.Services | Should -Not -BeNullOrEmpty
        $Result.TotalMonitored | Should -BeGreaterThan 0
        $Result.Unhealthy | Should -BeGreaterOrEqual 0
        $Result.Status | Should -Match "OK|CRITICAL"
    }

    It "Should monitor critical Windows services" {
        $Result = Get-ServiceStatus
        
        $Result.Services.Count | Should -BeGreaterThan 0
        
        # Verify specific critical services are monitored
        $ServiceNames = $Result.Services | ForEach-Object { $_.Name }
        $ServiceNames | Should -Contain "Winmgmt"
        $ServiceNames | Should -Contain "EventLog"
    }

    It "Should report service health status correctly" {
        $Result = Get-ServiceStatus
        
        foreach ($Service in $Result.Services) {
            $Service.Name | Should -Not -BeNullOrEmpty
            $Service.DisplayName | Should -Not -BeNullOrEmpty
            $Service.Status | Should -Not -BeNullOrEmpty
            $Service.IsHealthy | Should -BeOfType [bool]
        }
    }

    It "Should count unhealthy services accurately" {
        $Result = Get-ServiceStatus
        
        $ManualCount = ($Result.Services | Where-Object { -not $_.IsHealthy }).Count
        $Result.Unhealthy | Should -Be $ManualCount
    }

    It "Should mark status as CRITICAL if threshold exceeded" {
        # This test validates the logic, even if all services are healthy
        $Result = Get-ServiceStatus
        
        if ($Result.Unhealthy -ge 1) {
            $Result.Status | Should -Be "CRITICAL"
        } else {
            $Result.Status | Should -Be "OK"
        }
    }
}

Describe "Get-EventLogSummary" {
    It "Should return event log summary object" {
        $Result = Get-EventLogSummary -Minutes 5
        
        $Result | Should -Not -BeNullOrEmpty
        $Result.Timestamp | Should -Not -BeNullOrEmpty
        $Result.TimeWindowMinutes | Should -Be 5
        $Result.Summary | Should -Not -BeNullOrEmpty
        $Result.TotalErrors | Should -BeGreaterOrEqual 0
        $Result.Status | Should -Match "OK|WARNING|CRITICAL"
    }

    It "Should analyze System event log" {
        $Result = Get-EventLogSummary -Minutes 5
        
        $Result.Summary.System | Should -Not -BeNullOrEmpty
        $Result.Summary.System.Errors | Should -BeGreaterOrEqual 0
        $Result.Summary.System.Warnings | Should -BeGreaterOrEqual 0
        $Result.Summary.System.Critical | Should -BeGreaterOrEqual 0
    }

    It "Should analyze Application event log" {
        $Result = Get-EventLogSummary -Minutes 5
        
        $Result.Summary.Application | Should -Not -BeNullOrEmpty
        $Result.Summary.Application.Errors | Should -BeGreaterOrEqual 0
        $Result.Summary.Application.Warnings | Should -BeGreaterOrEqual 0
        $Result.Summary.Application.Critical | Should -BeGreaterOrEqual 0
    }

    It "Should analyze Security event log for logins" {
        $Result = Get-EventLogSummary -Minutes 5
        
        $Result.Summary.Security | Should -Not -BeNullOrEmpty
        $Result.Summary.Security.SuccessfulLogins | Should -BeGreaterOrEqual 0
        $Result.Summary.Security.FailedLogins | Should -BeGreaterOrEqual 0
    }

    It "Should calculate total errors correctly" {
        $Result = Get-EventLogSummary -Minutes 5
        
        $ExpectedTotal = $Result.Summary.System.Errors + 
                        $Result.Summary.Application.Errors + 
                        $Result.Summary.System.Critical + 
                        $Result.Summary.Application.Critical
        
        $Result.TotalErrors | Should -Be $ExpectedTotal
    }

    It "Should support custom time windows" {
        $Result = Get-EventLogSummary -Minutes 10
        
        $Result.TimeWindowMinutes | Should -Be 10
        $Result.Summary | Should -Not -BeNullOrEmpty
    }
}

Describe "Save-Snapshot" {
    It "Should save snapshot to JSON file" {
        $TestData = @{
            Timestamp = (Get-Date).ToUniversalTime().ToString("o")
            TestValue = 123
            TestArray = @(1, 2, 3)
        }

        Save-Snapshot -Data $TestData

        $SnapshotFiles = Get-ChildItem -Path $Global:TestSnapshotDir -Filter "sentinel_snapshot_*.json"
        $SnapshotFiles.Count | Should -BeGreaterOrEqual 1
    }

    It "Should create valid JSON content" {
        $TestData = @{
            Timestamp = (Get-Date).ToUniversalTime().ToString("o")
            Metrics = @{
                CPU = 50
                Memory = 75
            }
        }

        Save-Snapshot -Data $TestData

        $SnapshotFile = Get-ChildItem -Path $Global:TestSnapshotDir -Filter "sentinel_snapshot_*.json" | 
            Sort-Object LastWriteTime -Descending | 
            Select-Object -First 1

        $Content = Get-Content -Path $SnapshotFile.FullName -Raw
        { $Content | ConvertFrom-Json } | Should -Not -Throw
    }

    It "Should clean up old snapshots (keep last 100)" {
        # Create 105 test snapshots
        for ($i = 1; $i -le 105; $i++) {
            $TestData = @{ Iteration = $i }
            Save-Snapshot -Data $TestData
            Start-Sleep -Milliseconds 10  # Ensure unique timestamps
        }

        $SnapshotFiles = Get-ChildItem -Path $Global:TestSnapshotDir -Filter "sentinel_snapshot_*.json"
        $SnapshotFiles.Count | Should -BeLessOrEqual 100
    }
}

Describe "Send-TelegramAlert" {
    It "Should not throw when Telegram is disabled" {
        Mock Invoke-RestMethod { return @{ ok = $true } }

        { Send-TelegramAlert -Message "Test alert" -Severity "INFO" } | Should -Not -Throw
    }

    It "Should format message correctly with severity icon" -Skip {
        # Skipped - requires network access and valid Telegram credentials
        # Manual test: Set $env:TELEGRAM_BOT_TOKEN and $env:TELEGRAM_CHAT_ID, then run:
        # Send-TelegramAlert -Message "Test alert from Pester" -Severity "INFO"
    }

    It "Should handle missing credentials gracefully" {
        $OriginalToken = $env:TELEGRAM_BOT_TOKEN
        $OriginalChatId = $env:TELEGRAM_CHAT_ID

        try {
            $env:TELEGRAM_BOT_TOKEN = $null
            $env:TELEGRAM_CHAT_ID = $null

            { Send-TelegramAlert -Message "Test" -Severity "INFO" } | Should -Not -Throw
        }
        finally {
            $env:TELEGRAM_BOT_TOKEN = $OriginalToken
            $env:TELEGRAM_CHAT_ID = $OriginalChatId
        }
    }
}

Describe "Integration Tests" {
    It "Should collect complete system state" {
        $Metrics = Get-SystemMetrics
        $Services = Get-ServiceStatus
        $EventLogs = Get-EventLogSummary -Minutes 5

        $Metrics | Should -Not -BeNullOrEmpty
        $Services | Should -Not -BeNullOrEmpty
        $EventLogs | Should -Not -BeNullOrEmpty

        # Validate complete data structure
        $Metrics.CPU.LoadPercent | Should -BeGreaterOrEqual 0
        $Services.TotalMonitored | Should -BeGreaterThan 0
        $EventLogs.TotalErrors | Should -BeGreaterOrEqual 0
    }

    It "Should save complete snapshot with all metrics" {
        $SnapshotData = @{
            Timestamp = (Get-Date).ToUniversalTime().ToString("o")
            Metrics = Get-SystemMetrics
            Services = Get-ServiceStatus
            EventLogs = Get-EventLogSummary -Minutes 5
        }

        Save-Snapshot -Data $SnapshotData

        $SnapshotFile = Get-ChildItem -Path $Global:TestSnapshotDir -Filter "sentinel_snapshot_*.json" | 
            Sort-Object LastWriteTime -Descending | 
            Select-Object -First 1

        $SnapshotFile | Should -Not -BeNullOrEmpty
        $SnapshotFile.Length | Should -BeGreaterThan 1KB
    }
}

AfterAll {
    # Cleanup test snapshots
    if (Test-Path $Global:TestSnapshotDir) {
        Remove-Item -Path $Global:TestSnapshotDir -Recurse -Force
    }

    # Restore environment
    Remove-Item Env:\TELEGRAM_BOT_TOKEN -ErrorAction SilentlyContinue
    Remove-Item Env:\TELEGRAM_CHAT_ID -ErrorAction SilentlyContinue
}
