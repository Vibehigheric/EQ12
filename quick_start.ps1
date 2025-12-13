#!/usr/bin/env powershell
<#
.SYNOPSIS
    EQ12 Free Toolchain - Quick Start

.DESCRIPTION
    Immediate start guide for the EQ12 comprehensive development environment.
    Run this for instant setup with zero paid dependencies.

.EXAMPLE
    .\quick_start.ps1
    # Complete setup and validation in one command
#>

Write-Host "🚀 EQ12 FREE TOOLCHAIN - QUICK START" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host "Comprehensive Windows development environment with OpenAI Responses API" -ForegroundColor White
Write-Host "🛡️ 100% Free Mode - No API charges during development" -ForegroundColor Cyan
Write-Host ""

# Check if already set up
if (Test-Path ".\.venv\Scripts\python.exe") {
    Write-Host "✅ Environment already set up!" -ForegroundColor Green
    Write-Host "Testing current installation..." -ForegroundColor Yellow

    # Quick test
    $pythonExe = ".\.venv\Scripts\python.exe"
    $testResult = & $pythonExe -c "from eq12_free_guard import is_free_mode; from eq12_responses_client import get_responses_client; client = get_responses_client(); print(f'Free Mode: {is_free_mode()}')" 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host $testResult -ForegroundColor Green
        Write-Host ""
        Write-Host "🎯 Ready for development!" -ForegroundColor Green
        Write-Host "   • Test system: python eq12_responses_client.py" -ForegroundColor White
        Write-Host "   • VS Code: code ." -ForegroundColor White
        Write-Host "   • Update: .\scripts\eq12_toolchain_update.ps1" -ForegroundColor White
    }
    else {
        Write-Host "Environment needs refresh. Running bootstrap..." -ForegroundColor Yellow
        & ".\scripts\eq12_bootstrap.ps1" -Force
    }
}
else {
    Write-Host "Setting up new environment..." -ForegroundColor Yellow

    # Run bootstrap
    & ".\scripts\eq12_bootstrap.ps1"

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 Setup complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Next steps:" -ForegroundColor Cyan
        Write-Host "   1. Test: python eq12_responses_client.py" -ForegroundColor White
        Write-Host "   2. Develop: code ." -ForegroundColor White
        Write-Host "   3. Learn: cat EQ12_FREE_TOOLCHAIN_COMPLETE.md" -ForegroundColor White
        Write-Host ""
        Write-Host "🛡️ Free mode active - Safe for development!" -ForegroundColor Green
    }
    else {
        Write-Error "Setup failed. Check logs\bootstrap.log for details."
        exit 1
    }
}

Write-Host ""
Write-Host "=" * 50 -ForegroundColor Green
Write-Host "EQ12 Free Toolchain Ready! 🚀" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green
