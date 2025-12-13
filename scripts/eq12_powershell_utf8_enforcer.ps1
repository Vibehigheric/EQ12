# EQ12 PowerShell UTF-8 Enforcement Module
# Permanent UTF-8 protection for all PowerShell operations

[CmdletBinding()]
param(
    [switch]$Install,
    [switch]$Status
)

# Force UTF-8 for all PowerShell file operations
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
$PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'
$PSDefaultParameterValues['Export-Csv:Encoding'] = 'utf8'
$PSDefaultParameterValues['Select-String:Encoding'] = 'utf8'

# Set console to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

# Environment variables for UTF-8 safety
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:LC_ALL = "en_US.UTF-8"
$env:LANG = "en_US.UTF-8"
$env:EQ12_IMMUNITY_ACTIVE = "TRUE"

function Install-EQ12UTF8Enforcement {
    Write-Host " Installing EQ12 PowerShell UTF-8 Enforcement..." -ForegroundColor Green

    # Add to PowerShell profile for permanent activation
    $profilePath = $PROFILE.AllUsersAllHosts
    if (-not (Test-Path $profilePath)) {
        New-Item -Path $profilePath -ItemType File -Force | Out-Null
    }

    $enforcementCode = @"
# EQ12 UTF-8 Enforcement - Auto-loaded
`$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
`$PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
`$PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'
`$PSDefaultParameterValues['Export-Csv:Encoding'] = 'utf8'
`$PSDefaultParameterValues['Select-String:Encoding'] = 'utf8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
`$env:PYTHONUTF8 = "1"
`$env:PYTHONIOENCODING = "utf-8"
`$env:LC_ALL = "en_US.UTF-8"
`$env:LANG = "en_US.UTF-8"
`$env:EQ12_IMMUNITY_ACTIVE = "TRUE"
Write-Host " EQ12 UTF-8 Immunity Active" -ForegroundColor Green
"@

    # Check if already installed
    $currentContent = Get-Content -Path $profilePath -Raw -ErrorAction SilentlyContinue
    if ($currentContent -notlike "*EQ12 UTF-8 Enforcement*") {
        Add-Content -Path $profilePath -Value "`n$enforcementCode" -Encoding utf8
        Write-Host " UTF-8 enforcement installed to PowerShell profile" -ForegroundColor Green
    } else {
        Write-Host " UTF-8 enforcement already installed" -ForegroundColor Yellow
    }

    Write-Host " PowerShell UTF-8 enforcement active for this session" -ForegroundColor Green
}

function Get-EQ12UTF8Status {
    Write-Host " EQ12 UTF-8 Enforcement Status" -ForegroundColor Cyan
    Write-Host "=" * 40 -ForegroundColor Cyan

    # Check environment variables
    $status = @{
        "PYTHONUTF8" = $env:PYTHONUTF8
        "PYTHONIOENCODING" = $env:PYTHONIOENCODING
        "LC_ALL" = $env:LC_ALL
        "LANG" = $env:LANG
        "EQ12_IMMUNITY_ACTIVE" = $env:EQ12_IMMUNITY_ACTIVE
    }

    foreach ($var in $status.GetEnumerator()) {
        $color = if ($var.Value) { "Green" } else { "Red" }
        Write-Host "$($var.Key): $($var.Value)" -ForegroundColor $color
    }

    # Check PowerShell defaults
    Write-Host "`nPowerShell File Encoding Defaults:" -ForegroundColor Cyan
    $encodingDefaults = @(
        'Out-File:Encoding',
        'Set-Content:Encoding',
        'Add-Content:Encoding'
    )

    foreach ($default in $encodingDefaults) {
        $value = $PSDefaultParameterValues[$default]
        $color = if ($value -eq 'utf8') { "Green" } else { "Red" }
        Write-Host "$default = $value" -ForegroundColor $color
    }

    # Check console encoding
    Write-Host "`nConsole Encoding:" -ForegroundColor Cyan
    Write-Host "Output: $([Console]::OutputEncoding.EncodingName)" -ForegroundColor Green
    Write-Host "Input: $([Console]::InputEncoding.EncodingName)" -ForegroundColor Green
}

function Test-EQ12UTF8Protection {
    Write-Host " Testing EQ12 UTF-8 Protection..." -ForegroundColor Yellow

    $testFile = "C:\EQ12\logs\utf8_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
    $testContent = "EQ12 UTF-8 Test  Content Empire  Buffalo NY "

    try {
        # Test file writing
        $testContent | Out-File -FilePath $testFile
        $readBack = Get-Content -Path $testFile -Raw

        if ($readBack.Trim() -eq $testContent) {
            Write-Host " UTF-8 file operations working correctly" -ForegroundColor Green
        } else {
            Write-Host " UTF-8 file operations failed" -ForegroundColor Red
        }

        # Cleanup
        Remove-Item -Path $testFile -Force -ErrorAction SilentlyContinue

    } catch {
        Write-Host " UTF-8 test failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Main execution
if ($Install) {
    Install-EQ12UTF8Enforcement
} elseif ($Status) {
    Get-EQ12UTF8Status
    Test-EQ12UTF8Protection
} else {
    Write-Host " EQ12 PowerShell UTF-8 Enforcer Loaded" -ForegroundColor Green
    Write-Host "Use -Install to permanently install UTF-8 enforcement" -ForegroundColor Yellow
    Write-Host "Use -Status to check current UTF-8 protection status" -ForegroundColor Yellow

    # Auto-activate for this session
    Write-Host " Activating UTF-8 enforcement for current session..." -ForegroundColor Green
    Get-EQ12UTF8Status
}

