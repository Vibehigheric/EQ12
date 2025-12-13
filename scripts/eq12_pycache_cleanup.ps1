# EQ12 Pycache Cleanup Service
# Automatically removes all __pycache__ directories
# Prevents Pylance corruption and EPIPE errors
# Buffalo NY 14215 Content Empire
# Date: November 16, 2025

[CmdletBinding()]
param(
    [string]$WorkspacePath = "C:\EQ12",
    [switch]$Continuous,
    [int]$IntervalSeconds = 300,  # 5 minutes
    [switch]$ShowDetails
)

function Remove-AllPycache {
    param([string]$RootPath)

    $removed = 0

    try {
        Get-ChildItem -Path $RootPath -Include "__pycache__" -Recurse -Directory -ErrorAction SilentlyContinue |
        ForEach-Object {
            if ($ShowDetails) {
                Write-Host "Removing: $($_.FullName)" -ForegroundColor Gray
            }
            Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
            $removed++
        }

        # Also remove .pyc files
        Get-ChildItem -Path $RootPath -Include "*.pyc", "*.pyo" -Recurse -File -ErrorAction SilentlyContinue |
        ForEach-Object {
            if ($ShowDetails) {
                Write-Host "Removing: $($_.FullName)" -ForegroundColor Gray
            }
            Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
            $removed++
        }    } catch {
        Write-Host "Warning: Some pycache files could not be removed" -ForegroundColor Yellow
    }

    return $removed
}

function Set-PycacheEnvironment {
    Write-Host "Setting NO-PYCACHE environment variables..." -ForegroundColor Yellow

    $envVars = @{
        'PYTHONDONTWRITEBYTECODE' = '1'
        'PYTHONOPTIMIZE' = '0'
        'PYTHON_PYCACHE_PREFIX' = ''
        'EQ12_NO_PYCACHE' = 'ACTIVE'
    }

    foreach ($var in $envVars.GetEnumerator()) {
        [Environment]::SetEnvironmentVariable($var.Key, $var.Value, 'User')
        if ($ShowDetails) {
            Write-Host "  Set: $($var.Key)=$($var.Value)" -ForegroundColor Gray
        }
    }
}

Write-Host "================================================================" -ForegroundColor Green
Write-Host "EQ12 PYCACHE CLEANUP SERVICE" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Verify workspace exists
if (!(Test-Path $WorkspacePath)) {
    Write-Host "ERROR: Workspace path does not exist: $WorkspacePath" -ForegroundColor Red
    exit 1
}

# Set environment for no pycache
Set-PycacheEnvironment

if ($Continuous) {
    Write-Host "Starting continuous pycache cleanup..." -ForegroundColor Cyan
    Write-Host "Workspace: $WorkspacePath" -ForegroundColor White
    Write-Host "Interval: $IntervalSeconds seconds" -ForegroundColor White
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""

    $iteration = 0
    while ($true) {
        try {
            $iteration++
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

            if ($ShowDetails) {
                Write-Host "[$timestamp] Iteration $iteration - Scanning for pycache..." -ForegroundColor Gray
            }

            $removed = Remove-AllPycache -RootPath $WorkspacePath

            if ($removed -gt 0) {
                Write-Host "[$timestamp] Removed $removed pycache items" -ForegroundColor Green
            } elseif ($ShowDetails) {
                Write-Host "[$timestamp] No pycache found - workspace clean" -ForegroundColor DarkGreen
            }            Start-Sleep -Seconds $IntervalSeconds

        } catch {
            Write-Host "[$timestamp] Service error: $($_.Exception.Message)" -ForegroundColor Red
            Start-Sleep -Seconds 30  # Wait before retrying
        }
    }
} else {
    # One-time cleanup
    Write-Host "Performing one-time pycache cleanup..." -ForegroundColor Cyan
    Write-Host "Workspace: $WorkspacePath" -ForegroundColor White
    Write-Host ""

    $removed = Remove-AllPycache -RootPath $WorkspacePath

    if ($removed -gt 0) {
        Write-Host "SUCCESS: Removed $removed pycache items" -ForegroundColor Green
    } else {
        Write-Host "INFO: No pycache found - workspace already clean" -ForegroundColor DarkGreen
    }

    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor White
    Write-Host "1. Add 'from eq12_no_pycache import eq12_import_hook' to all scripts" -ForegroundColor Yellow
    Write-Host "2. Add 'eq12_import_hook()' as first line in scripts" -ForegroundColor Yellow
    Write-Host "3. Restart VS Code to refresh Pylance" -ForegroundColor Yellow
    Write-Host "4. Run continuous service if needed:" -ForegroundColor Yellow
    Write-Host "   powershell -File eq12_pycache_cleanup.ps1 -Continuous" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Buffalo NY 14215 Content Empire - PYCACHE ELIMINATION COMPLETE" -ForegroundColor Cyan
}
