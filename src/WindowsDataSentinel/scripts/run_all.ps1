# Windows Data Sentinel - PowerShell Orchestrator
# Runs VB.NET data collector and manages logging

param(
    [string]$ConfigPath = "C:\EQ12\WindowsDataSentinel\config\feeds.json",
    [string]$CollectorExe = "C:\EQ12\WindowsDataSentinel\src\VBDataCollector\bin\Release\net8.0\EQ12DataCollector.exe",
    [string]$LogDir = "C:\EQ12\WindowsDataSentinel\logs",
    [switch]$Verbose
)

# Ensure log directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $LogDir "run_all_$timestamp.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] $Message"
    $line | Tee-Object -FilePath $logFile -Append
    
    if ($Verbose) {
        Write-Host $line -ForegroundColor $(
            switch ($Level) {
                "ERROR" { "Red" }
                "WARN" { "Yellow" }
                "SUCCESS" { "Green" }
                default { "White" }
            }
        )
    }
}

Write-Log "============================================" "INFO"
Write-Log "Windows Data Sentinel - Run Started" "INFO"
Write-Log "============================================" "INFO"

# Validate config file exists
if (-not (Test-Path $ConfigPath)) {
    Write-Log "Config file not found: $ConfigPath" "ERROR"
    exit 1
}

Write-Log "Config file: $ConfigPath" "INFO"

# Check if VB.NET collector exists
if (Test-Path $CollectorExe) {
    Write-Log "Using compiled VB.NET collector: $CollectorExe" "INFO"
    
    # Run VB.NET collector
    Write-Log "Starting VBDataCollector..." "INFO"
    try {
        $process = Start-Process -FilePath $CollectorExe `
                                 -ArgumentList "`"$ConfigPath`"" `
                                 -PassThru `
                                 -Wait `
                                 -NoNewWindow
        
        if ($process.ExitCode -eq 0) {
            Write-Log "VBDataCollector completed successfully (Exit Code: 0)" "SUCCESS"
        } else {
            Write-Log "VBDataCollector exited with code: $($process.ExitCode)" "WARN"
        }
    } catch {
        Write-Log "Error running VBDataCollector: $_" "ERROR"
        exit 1
    }
} else {
    Write-Log "VB.NET collector not found. Using Python fallback..." "WARN"
    
    # Python fallback collector
    $pythonCollector = "C:\EQ12\WindowsDataSentinel\src\PythonAnalytics\data_collector.py"
    
    if (Test-Path $pythonCollector) {
        Write-Log "Running Python collector: $pythonCollector" "INFO"
        try {
            python $pythonCollector --config $ConfigPath
            Write-Log "Python collector completed" "SUCCESS"
        } catch {
            Write-Log "Error running Python collector: $_" "ERROR"
            exit 1
        }
    } else {
        Write-Log "No collector found (neither VB.NET nor Python)" "ERROR"
        exit 1
    }
}

# Health check - verify database was updated
$dbPath = "C:\EQ12\WindowsDataSentinel\data\eq12_sentinel.db"
if (Test-Path $dbPath) {
    $dbInfo = Get-Item $dbPath
    $age = (Get-Date) - $dbInfo.LastWriteTime
    
    if ($age.TotalMinutes -lt 30) {
        Write-Log "Database updated successfully (Last modified: $($dbInfo.LastWriteTime))" "SUCCESS"
    } else {
        Write-Log "Database not recently updated (Last modified: $($dbInfo.LastWriteTime))" "WARN"
    }
    
    Write-Log "Database size: $([math]::Round($dbInfo.Length / 1MB, 2)) MB" "INFO"
} else {
    Write-Log "Database not found: $dbPath" "WARN"
}

Write-Log "============================================" "INFO"
Write-Log "Windows Data Sentinel - Run Completed" "INFO"
Write-Log "============================================" "INFO"

exit 0
