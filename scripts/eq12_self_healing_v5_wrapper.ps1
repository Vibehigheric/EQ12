# EQ12 Self-Healing v5.0 PowerShell Wrapper with UTF-8 Hardening
# Proper UTF-8 encoding for PowerShell  Python  JSON integration
# Buffalo NY 14215 Content Empire Protection

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [string]$Action = "monitor",

    [Parameter()]
    [string]$Workspace = "C:\EQ12",

    [Parameter()]
    [switch]$Continuous,

    [Parameter()]
    [switch]$EmergencyMode,

    [Parameter()]
    [string]$AlertsJson,

    [Parameter()]
    [switch]$Verbose
)

# Force PowerShell UTF-8 encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

Write-Host ""
Write-Host " EQ12 SELF-HEALING v5.0 PowerShell Wrapper" -ForegroundColor Cyan
Write-Host " Buffalo NY 14215 Content Empire Protection" -ForegroundColor Yellow
Write-Host "=" * 60

# Validate Python script exists
$PythonScript = Join-Path $Workspace "scripts\eq12_self_healing_v5.py"
if (-not (Test-Path $PythonScript)) {
    Write-Host " EQ12 Self-Healing v5.0 script not found: $PythonScript" -ForegroundColor Red
    exit 1
}

# Build Python command with proper UTF-8 environment
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:LC_ALL = "C.UTF-8"
$env:LANG = "C.UTF-8"

$PythonArgs = @()

# Determine action
switch ($Action.ToLower()) {
    "monitor" {
        $PythonArgs += "monitor"
        $PythonArgs += "--workspace"
        $PythonArgs += $Workspace

        if ($Continuous) {
            $PythonArgs += "--continuous"
            $PythonArgs += "--interval"
            $PythonArgs += "300"  # 5 minutes
        }

        Write-Host " Starting resource monitoring..." -ForegroundColor Green
    }

    "heal" {
        $PythonArgs += "heal"
        $PythonArgs += "--workspace"
        $PythonArgs += $Workspace

        if ($AlertsJson) {
            # Properly escape JSON for Python
            $SafeJson = $AlertsJson -replace '"', '\"'
            $PythonArgs += "--alerts"
            $PythonArgs += $SafeJson
        } else {
            # Default test alert
            $TestAlert = '[{"type":"system_check","severity":"info","message":"PowerShell wrapper test","timestamp":"' + (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffK") + '"}]'
            $PythonArgs += "--alerts"
            $PythonArgs += $TestAlert
        }

        if ($EmergencyMode) {
            $PythonArgs += "--emergency-mode"
        }

        Write-Host " Starting emergency healing..." -ForegroundColor Yellow
    }

    "test" {
        # Test mode with sample alerts
        $PythonArgs += "heal"
        $PythonArgs += "--workspace"
        $PythonArgs += $Workspace

        $TestAlerts = @(
            @{
                type = "cpu_overload"
                severity = "critical"
                message = "CPU usage critical: 95.2%"
                value = 95.2
                threshold = 90.0
                timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffK")
            },
            @{
                type = "memory_overload"
                severity = "high"
                message = "Memory usage high: 87.5%"
                value = 87.5
                threshold = 85.0
                timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffK")
            }
        )

        $TestAlertsJson = $TestAlerts | ConvertTo-Json -Depth 5 -Compress
        $PythonArgs += "--alerts"
        $PythonArgs += $TestAlertsJson
        $PythonArgs += "--emergency-mode"

        Write-Host " Running test healing scenario..." -ForegroundColor Magenta
    }

    default {
        Write-Host " Unknown action: $Action" -ForegroundColor Red
        Write-Host "Valid actions: monitor, heal, test" -ForegroundColor Gray
        exit 1
    }
}

# Add verbose flag if requested
if ($Verbose) {
    $PythonArgs += "--verbose"
}

Write-Host " Executing Python command with UTF-8 encoding..." -ForegroundColor Green
Write-Host "Command: python `"$PythonScript`" $($PythonArgs -join ' ')" -ForegroundColor Gray

try {
    # Execute Python script with proper UTF-8 handling
    $Result = Start-Process -FilePath "python" -ArgumentList @($PythonScript) + $PythonArgs -Wait -PassThru -NoNewWindow

    if ($Result.ExitCode -eq 0) {
        Write-Host ""
        Write-Host " EQ12 Self-Healing v5.0 completed successfully" -ForegroundColor Green
        Write-Host " Exit code: $($Result.ExitCode)" -ForegroundColor Gray
    } else {
        Write-Host ""
        Write-Host " EQ12 Self-Healing v5.0 completed with warnings" -ForegroundColor Yellow
        Write-Host " Exit code: $($Result.ExitCode)" -ForegroundColor Gray
    }

    exit $Result.ExitCode

} catch {
    Write-Host ""
    Write-Host " EQ12 Self-Healing v5.0 execution failed" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Display next steps
Write-Host ""
Write-Host " EQ12 Self-Healing v5.0 Usage:" -ForegroundColor Cyan
Write-Host "Monitor: .\eq12_self_healing_v5_wrapper.ps1 -Action monitor [-Continuous]" -ForegroundColor Gray
Write-Host "Heal: .\eq12_self_healing_v5_wrapper.ps1 -Action heal -AlertsJson '[...]'" -ForegroundColor Gray
Write-Host "Test: .\eq12_self_healing_v5_wrapper.ps1 -Action test" -ForegroundColor Gray
Write-Host ""
Write-Host " Buffalo NY 14215 Content Empire: PROTECTED" -ForegroundColor Green

