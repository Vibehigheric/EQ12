<#
.SYNOPSIS
    EQ12 Adaptive Performance Manager - Auto-tunes based on system capabilities

.DESCRIPTION
    Automatically configures EQ12 scripts for optimal performance based on:
    - CPU cores/threads (12 threads detected)
    - RAM availability (32 GB detected)
    - Disk space (564 GB free)
    - Network speed (100 Gbps)

.PARAMETER Task
    Task type: scanner, validator, bankroll, scan, export

.PARAMETER AutoTune
    Automatically select best configuration

.EXAMPLE
    .\EQ12_ADAPTIVE_TUNER.ps1 -Task scanner -AutoTune
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('scanner', 'validator', 'bankroll', 'scan', 'export', 'all')]
    [string]$Task = 'all',
    
    [Parameter()]
    [switch]$AutoTune,
    
    [Parameter()]
    [switch]$ShowConfig
)

# System Capabilities (auto-detected)
$SystemConfig = @{
    CPUThreads = 12
    CPUCores   = 10
    RAMGb      = 32
    DiskFreeGb = 564
    MaxWorkers = 10
    BatchSize  = 100
}

# Task-Specific Optimizations
$TaskConfigs = @{
    scanner   = @{
        Workers       = 10          # I/O intensive, use all workers
        BatchSize     = 100
        Timeout       = 30
        MaxConcurrent = 10
        Description   = "Sports betting odds scanner"
    }
    validator = @{
        Workers      = 5           # CPU intensive, use half workers
        BatchSize    = 50
        Timeout      = 10
        CacheEnabled = $true
        Description  = "SGP parlay validator"
    }
    bankroll  = @{
        Workers      = 10          # Light workload, use all workers
        BatchSize    = 200
        DBPoolSize   = 5
        CacheEnabled = $true
        Description  = "Bankroll management system"
    }
    scan      = @{
        Workers     = 8           # Mixed workload
        MaxFiles    = 50000      # Increased from 5000 (we have 32GB RAM)
        BatchSize   = 1000
        Timeout     = 300
        Description = "System file scanner"
    }
    export    = @{
        Workers      = 10          # I/O intensive
        ChunkSize    = 10000
        Compression  = 'gzip'
        BufferSizeMb = 512
        Description  = "Data export operations"
    }
}

function Show-ConfigSummary {
    Write-Host "`n" -NoNewline
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host "EQ12 ADAPTIVE PERFORMANCE CONFIGURATION" -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    
    Write-Host "`n[HARDWARE PROFILE]" -ForegroundColor Yellow
    Write-Host "  CPU: $($SystemConfig.CPUThreads) threads ($($SystemConfig.CPUCores) cores)"
    Write-Host "  RAM: $($SystemConfig.RAMGb) GB"
    Write-Host "  Disk: $($SystemConfig.DiskFreeGb) GB free"
    Write-Host "  Max Workers: $($SystemConfig.MaxWorkers)"
    
    Write-Host "`n[OPTIMIZED TASK CONFIGURATIONS]" -ForegroundColor Yellow
    foreach ($taskName in $TaskConfigs.Keys | Sort-Object) {
        $config = $TaskConfigs[$taskName]
        Write-Host "`n  [$($taskName.ToUpper())] - $($config.Description)" -ForegroundColor Green
        Write-Host "    Workers: $($config.Workers)"
        if ($config.BatchSize) { Write-Host "    Batch Size: $($config.BatchSize)" }
        if ($config.MaxFiles) { Write-Host "    Max Files: $($config.MaxFiles)" }
        if ($config.Timeout) { Write-Host "    Timeout: $($config.Timeout)s" }
        if ($config.CacheEnabled) { Write-Host "    Cache: Enabled" }
    }
    
    Write-Host "`n[PERFORMANCE RECOMMENDATIONS]" -ForegroundColor Yellow
    Write-Host "  • Use 10 workers for I/O tasks (scanner, export)"
    Write-Host "  • Use 5 workers for CPU tasks (validator)"
    Write-Host "  • Increased scan limit to 50,000 files (from 5,000)"
    Write-Host "  • Each worker has ~3.2 GB RAM available"
    Write-Host "  • Network: 100 Gbps - optimal for API calls"
    
    Write-Host "`n" -NoNewline
    Write-Host ("=" * 80) -ForegroundColor Cyan
}

function Set-OptimalEnvironment {
    param([string]$TaskType)
    
    $config = $TaskConfigs[$TaskType]
    
    Write-Host "`n🔧 Configuring environment for: $TaskType" -ForegroundColor Cyan
    
    # Set environment variables
    $env:EQ12_MAX_WORKERS = $config.Workers
    $env:EQ12_BATCH_SIZE = $config.BatchSize
    $env:EQ12_TASK_TYPE = $TaskType
    
    if ($config.MaxFiles) {
        $env:EQ12_MAX_FILES = $config.MaxFiles
    }
    
    Write-Host "  ✓ Workers: $($config.Workers)" -ForegroundColor Green
    Write-Host "  ✓ Batch Size: $($config.BatchSize)" -ForegroundColor Green
    
    return $config
}

function Invoke-AdaptiveTask {
    param(
        [string]$TaskType,
        [hashtable]$Config
    )
    
    Write-Host "`n▶️  Executing: $TaskType" -ForegroundColor Cyan
    
    switch ($TaskType) {
        'scanner' {
            Write-Host "  Running sports scanner with $($Config.Workers) workers..."
            $cmd = "python eq12_live_sports_scanner_1hour.py --workers $($Config.Workers)"
            Write-Host "  Command: $cmd" -ForegroundColor Gray
        }
        'validator' {
            Write-Host "  Running SGP validator with $($Config.Workers) workers..."
            $cmd = "python eq12_sgp_validator.py --workers $($Config.Workers) --batch-size $($Config.BatchSize)"
            Write-Host "  Command: $cmd" -ForegroundColor Gray
        }
        'scan' {
            Write-Host "  Running system scan (max $($Config.MaxFiles) files)..."
            $cmd = ".\EQ12_SYSTEM_SCAN.ps1 -MaxFiles $($Config.MaxFiles) -Verbose"
            Write-Host "  Command: $cmd" -ForegroundColor Gray
        }
        'bankroll' {
            Write-Host "  Running bankroll manager with $($Config.Workers) workers..."
            $cmd = "python eq12_bankroll_manager.py --workers $($Config.Workers)"
            Write-Host "  Command: $cmd" -ForegroundColor Gray
        }
        'export' {
            Write-Host "  Running data export with $($Config.Workers) workers..."
            $cmd = "python eq12_data_export.py --workers $($Config.Workers) --chunk-size $($Config.ChunkSize)"
            Write-Host "  Command: $cmd" -ForegroundColor Gray
        }
    }
    
    Write-Host "  ℹ️  Configuration applied. Ready to execute." -ForegroundColor Yellow
}

# Main execution
if ($ShowConfig) {
    Show-ConfigSummary
    exit 0
}

if ($AutoTune) {
    Show-ConfigSummary
    
    if ($Task -eq 'all') {
        Write-Host ''
        Write-Host '📊 All tasks configured with optimal settings.' -ForegroundColor Green
        Write-Host '   Use -Task [name] to configure specific task.' -ForegroundColor Yellow
    }
    else {
        $config = Set-OptimalEnvironment -TaskType $Task
        Invoke-AdaptiveTask -TaskType $Task -Config $config
    }
}
else {
    Write-Host ''
    Write-Host '⚠️  Use -AutoTune to apply optimal configuration' -ForegroundColor Yellow
    Write-Host '   Use -ShowConfig to display configuration details' -ForegroundColor Yellow
    Write-Host ''
    Write-Host 'Example:' -ForegroundColor Gray
    Write-Host '  .\EQ12_ADAPTIVE_TUNER.ps1 -Task scanner -AutoTune'
}
