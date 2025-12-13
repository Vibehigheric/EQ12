
# EQ12 UTF-8 Configuration Script
[CmdletBinding()]
param()

Write-Host "Configuring UTF-8 encoding for EQ12..." -ForegroundColor Cyan

# Set console code page
try {
    chcp 65001 | Out-Null
    Write-Host "Console code page set to UTF-8" -ForegroundColor Green
} catch {
    Write-Host "Warning: Could not set console code page" -ForegroundColor Yellow
}

# Set environment variables
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

Write-Host "Python UTF-8 environment configured" -ForegroundColor Green
Write-Host "UTF-8 configuration complete!" -ForegroundColor Cyan
