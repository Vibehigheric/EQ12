<#
.SYNOPSIS
    EQ12 Environment Setup - Securely configure all API keys and credentials
.DESCRIPTION
    Reads .env file and sets Windows environment variables
    ALL KEYS ARE MASKED - NEVER LOGGED OR DISPLAYED
.NOTES
    Usage: .\scripts\setup_environment.ps1
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "🔒 EQ12 SECURE ENVIRONMENT SETUP" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check for .env file
$envFile = Join-Path $PSScriptRoot "..\\.env"
if (-not (Test-Path $envFile)) {
    Write-Host "❌ .env file not found" -ForegroundColor Red
    Write-Host "📝 Creating .env from template..." -ForegroundColor Yellow
    
    $templateFile = Join-Path $PSScriptRoot "..\\.env.template"
    if (Test-Path $templateFile) {
        Copy-Item $templateFile $envFile
        Write-Host "✅ Created .env - please fill in your API keys" -ForegroundColor Green
        Write-Host "📍 Location: $envFile" -ForegroundColor Gray
        exit 0
    }
    else {
        Write-Host "❌ Template file not found: $templateFile" -ForegroundColor Red
        exit 1
    }
}

# Read and parse .env file
$envVars = @{}
$maskedCount = 0
$setCount = 0

Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    
    # Skip comments and empty lines
    if ($line -match '^#' -or $line -eq '') {
        return
    }
    
    # Parse KEY=VALUE
    if ($line -match '^([^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        
        # Remove quotes if present
        $value = $value -replace '^["'']|["'']$', ''
        
        # Skip if value is placeholder
        if ($value -match '^\*+$' -or $value -eq '') {
            $maskedCount++
            return
        }
        
        # Set environment variable (USER scope, persistent)
        try {
            [System.Environment]::SetEnvironmentVariable($key, $value, [System.EnvironmentVariableTarget]::User)
            
            # Also set for current session
            Set-Item -Path "Env:$key" -Value $value -Force
            
            $setCount++
            Write-Host "✅ Set: $key" -ForegroundColor Green
        }
        catch {
            Write-Host "⚠️  Failed to set: $key" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "📊 SETUP SUMMARY" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "✅ Variables set:     $setCount" -ForegroundColor Green
Write-Host "⏭️  Skipped (masked):  $maskedCount" -ForegroundColor Gray
Write-Host ""
Write-Host "🔐 All keys are now stored securely in Windows environment" -ForegroundColor Cyan
Write-Host "📝 To update a key: Edit .env and re-run this script" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  SECURITY REMINDER:" -ForegroundColor Yellow
Write-Host "  • NEVER commit .env to git" -ForegroundColor Yellow
Write-Host "  • NEVER share .env file" -ForegroundColor Yellow
Write-Host "  • NEVER paste keys into chat/email" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
