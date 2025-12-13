# EQ12 Safe Launcher v4.0 - ULTRA SIMPLE ASCII-SAFE VERSION
# No complex regex - just basic safety checks
# Buffalo NY 14215 - Content Empire Command Center

param(
    [string]$ScriptPath
)

Write-Host "=== EQ12 SAFE LAUNCHER v4.0 ===" -ForegroundColor Green

if (-not (Test-Path $ScriptPath)) {
    Write-Error "Script not found: $ScriptPath"
    exit 1
}

Write-Host "Executing: $ScriptPath" -ForegroundColor Cyan

try {
    # Simple execution with error handling
    & powershell -ExecutionPolicy Bypass -NoProfile -File $ScriptPath

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Script executed successfully" -ForegroundColor Green
    } else {
        Write-Host "Script failed with code: $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Error "Execution error: $_"
    exit 1
}

Write-Host "=== EXECUTION COMPLETE ===" -ForegroundColor Green
