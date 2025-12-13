[CmdletBinding()]
param(
    [string]$Action = "HealthCheck",
    [string]$Workspace = "C:\EQ12"
)

$LogFile = Join-Path $Workspace "logs\system_mgmt_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Entry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] $Message"
    Write-Host $Entry -ForegroundColor $(if($Level -eq "ERROR"){"Red"}elseif($Level -eq "SUCCESS"){"Green"}elseif($Level -eq "WARNING"){"Yellow"}else{"Cyan"})
    $Entry | Out-File -FilePath $LogFile -Append
}

Write-Log " EQ12 System Management Wrapper Starting" "INFO"
Write-Log "Action: $Action | Workspace: $Workspace" "INFO"

# Test Python
try {
    $PythonVer = python --version 2>&1
    if ($PythonVer -match "Python") {
        Write-Log " Python: $PythonVer" "SUCCESS"
    } else {
        throw "Python not found"
    }
} catch {
    Write-Log " Python not available" "ERROR"
    exit 1
}

# Test system manager
$ManagerScript = Join-Path $Workspace "scripts\eq12_system_manager.py"
if (Test-Path $ManagerScript) {
    Write-Log " System manager found" "SUCCESS"
} else {
    Write-Log " System manager not found" "ERROR"
    exit 1
}

# Execute action
Write-Log " Executing: $Action" "INFO"

# Convert action to proper format
$ActionParam = switch ($Action) {
    "HealthCheck" { "health-check" }
    "AutoRepair" { "auto-repair" }
    default { $Action.ToLower() }
}

try {
    $Result = & python $ManagerScript --workspace $Workspace --action $ActionParam 2>&1
    $ExitCode = $LASTEXITCODE
    
    if ($ExitCode -eq 0) {
        Write-Log " System manager completed successfully" "SUCCESS"
        if ($Result) { Write-Host $Result }
    } else {
        Write-Log " System manager failed (exit code: $ExitCode)" "ERROR"
        if ($Result) { Write-Host $Result -ForegroundColor Red }
    }
} catch {
    Write-Log " Exception: $($_.Exception.Message)" "ERROR"
    exit 1
}

Write-Log " Wrapper completed" "SUCCESS"
