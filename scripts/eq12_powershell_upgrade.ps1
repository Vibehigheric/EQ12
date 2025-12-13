# EQ12 PowerShell 7.x Upgrade & Optimization Script
# Purpose: Upgrade from Windows PowerShell 5.1 to PowerShell 7.5 (LTS)
#          Fix UTF-8 encoding, enable long paths, optimize for Python/AI dev
#
# Contract: AGENTS.md - EQ12 Project Standards
# Created: 2025-11-22
################################################################################

#Requires -RunAsAdministrator

[CmdletBinding()]
param(
    [switch]$SkipInstall,
    [switch]$SkipUTF8Fix,
    [switch]$SkipLongPaths,
    [switch]$SkipProfileSetup
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Colors
function Write-ColorOutput {
    param(
        [string]$Message,
        [ValidateSet('Info', 'Success', 'Warning', 'Error')]
        [string]$Type = 'Info'
    )

    switch ($Type) {
        'Info'    { Write-Host $Message -ForegroundColor Cyan }
        'Success' { Write-Host "✓ $Message" -ForegroundColor Green }
        'Warning' { Write-Host "⚠ $Message" -ForegroundColor Yellow }
        'Error'   { Write-Host "✗ $Message" -ForegroundColor Red }
    }
}

Write-ColorOutput "╔════════════════════════════════════════════════════════════╗" -Type Info
Write-ColorOutput "║     EQ12 POWERSHELL 7.5 UPGRADE & OPTIMIZATION             ║" -Type Info
Write-ColorOutput "║     Fixing UTF-8, Long Paths, Python Integration           ║" -Type Info
Write-ColorOutput "╚════════════════════════════════════════════════════════════╝" -Type Info
Write-Host ""

################################################################################
# STEP 1: Detect current PowerShell version
################################################################################
Write-ColorOutput "[1/8] Detecting PowerShell version..." -Type Info

$currentVersion = $PSVersionTable.PSVersion
Write-Host "  Current Version: $currentVersion"

if ($currentVersion.Major -ge 7) {
    Write-ColorOutput "Already running PowerShell 7.x" -Type Success
    if (-not $SkipInstall) {
        $response = Read-Host "Continue with optimization? (Y/N)"
        if ($response -ne 'Y') {
            Write-ColorOutput "Exiting..." -Type Warning
            exit 0
        }
    }
} else {
    Write-Host "  Running Windows PowerShell 5.1 - upgrade needed"
}

################################################################################
# STEP 2: Install PowerShell 7.5 (LTS)
################################################################################
if (-not $SkipInstall) {
    Write-ColorOutput "`n[2/8] Installing PowerShell 7.5 (LTS)..." -Type Info

    # Check if winget is available
    $wingetPath = Get-Command winget -ErrorAction SilentlyContinue

    if ($wingetPath) {
        Write-Host "  Using winget to install PowerShell 7.x..."
        try {
            winget install --id Microsoft.Powershell --source winget --silent --accept-package-agreements --accept-source-agreements
            Write-ColorOutput "PowerShell 7.x installed via winget" -Type Success
        } catch {
            Write-ColorOutput "Winget installation failed: $_" -Type Warning
            Write-Host "  Please install manually from: https://github.com/PowerShell/PowerShell/releases/latest"
        }
    } else {
        Write-ColorOutput "Winget not found - attempting MSI download..." -Type Warning

        $msiUrl = "https://github.com/PowerShell/PowerShell/releases/download/v7.4.6/PowerShell-7.4.6-win-x64.msi"
        $msiPath = "$env:TEMP\PowerShell-7.4.6-win-x64.msi"

        try {
            Write-Host "  Downloading PowerShell 7.4.6..."
            Invoke-WebRequest -Uri $msiUrl -OutFile $msiPath -UseBasicParsing

            Write-Host "  Installing PowerShell 7.4.6..."
            Start-Process msiexec.exe -ArgumentList "/i `"$msiPath`" /quiet /norestart ADD_EXPLORER_CONTEXT_MENU_OPENPOWERSHELL=1 ADD_FILE_CONTEXT_MENU_RUNPOWERSHELL=1 ADD_PATH=1" -Wait

            Remove-Item $msiPath -Force
            Write-ColorOutput "PowerShell 7.4.6 installed via MSI" -Type Success
        } catch {
            Write-ColorOutput "Auto-installation failed: $_" -Type Error
            Write-Host "  Please install manually from: https://github.com/PowerShell/PowerShell/releases/latest"
            exit 1
        }
    }
} else {
    Write-ColorOutput "`n[2/8] Skipping PowerShell installation..." -Type Warning
}

################################################################################
# STEP 3: Enable UTF-8 system-wide
################################################################################
if (-not $SkipUTF8Fix) {
    Write-ColorOutput "`n[3/8] Enabling UTF-8 encoding system-wide..." -Type Info

    try {
        # Set UTF-8 as Active Code Page
        Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Nls\CodePage' -Name ACP -Value 65001 -Force
        Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Nls\CodePage' -Name OEMCP -Value 65001 -Force

        # Enable Beta UTF-8 support for worldwide language support
        Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Nls\CodePage' -Name '1252' -Value 65001 -Force -ErrorAction SilentlyContinue

        Write-ColorOutput "UTF-8 encoding enabled (requires reboot to take full effect)" -Type Success
    } catch {
        Write-ColorOutput "Failed to set UTF-8: $_" -Type Error
    }
} else {
    Write-ColorOutput "`n[3/8] Skipping UTF-8 configuration..." -Type Warning
}

################################################################################
# STEP 4: Enable long path support
################################################################################
if (-not $SkipLongPaths) {
    Write-ColorOutput "`n[4/8] Enabling long path support (>260 chars)..." -Type Info

    try {
        Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name LongPathsEnabled -Type DWord -Value 1 -Force
        Write-ColorOutput "Long path support enabled" -Type Success
    } catch {
        Write-ColorOutput "Failed to enable long paths: $_" -Type Error
    }
} else {
    Write-ColorOutput "`n[4/8] Skipping long path configuration..." -Type Warning
}

################################################################################
# STEP 5: Set execution policy
################################################################################
Write-ColorOutput "`n[5/8] Setting execution policy..." -Type Info

try {
    Set-ExecutionPolicy RemoteSigned -Scope LocalMachine -Force
    Write-ColorOutput "Execution policy set to RemoteSigned" -Type Success
} catch {
    Write-ColorOutput "Failed to set execution policy: $_" -Type Warning
}

################################################################################
# STEP 6: Install essential PowerShell modules
################################################################################
Write-ColorOutput "`n[6/8] Installing essential PowerShell modules..." -Type Info

# Ensure PSGallery is trusted
try {
    Set-PSRepository -Name PSGallery -InstallationPolicy Trusted -ErrorAction SilentlyContinue
} catch {
    Register-PackageSource -Name PSGallery -ProviderName PowerShellGet -SourceLocation "https://www.powershellgallery.com/api/v2" -Force
}

$modulesToInstall = @(
    'PSReadLine',
    'PowerShellGet',
    'Pester'
)

foreach ($module in $modulesToInstall) {
    try {
        if (-not (Get-Module -ListAvailable -Name $module)) {
            Write-Host "  Installing $module..."
            Install-Module -Name $module -Scope CurrentUser -Force -AllowClobber -SkipPublisherCheck
            Write-ColorOutput "$module installed" -Type Success
        } else {
            Write-Host "  $module already installed"
        }
    } catch {
        Write-ColorOutput "Failed to install ${module}: $_" -Type Warning
    }
}

################################################################################
# STEP 7: Create optimized PowerShell profile
################################################################################
if (-not $SkipProfileSetup) {
    Write-ColorOutput "`n[7/8] Creating EQ12-optimized PowerShell profile..." -Type Info

    # Determine profile path for PowerShell 7
    $pwsh7ProfilePath = "$env:USERPROFILE\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"
    $pwsh7ProfileDir = Split-Path -Parent $pwsh7ProfilePath

    if (-not (Test-Path $pwsh7ProfileDir)) {
        New-Item -ItemType Directory -Path $pwsh7ProfileDir -Force | Out-Null
    }

    # Create backup if profile exists
    if (Test-Path $pwsh7ProfilePath) {
        $backupPath = "${pwsh7ProfilePath}.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item $pwsh7ProfilePath $backupPath
        Write-Host "  Existing profile backed up to: $backupPath"
    }

    # Create new profile
    $profileContent = @'
################################################################################
# EQ12 Optimized PowerShell 7.x Profile
# Created: 2025-11-22
################################################################################

# Import modules
Import-Module PSReadLine -ErrorAction SilentlyContinue

# PSReadLine configuration
if (Get-Module PSReadLine) {
    Set-PSReadLineOption -PredictionSource HistoryAndPlugin -ErrorAction SilentlyContinue
    Set-PSReadLineOption -PredictionViewStyle InlineView -ErrorAction SilentlyContinue
    Set-PSReadLineOption -EditMode Windows -ErrorAction SilentlyContinue
    Set-PSReadLineOption -BellStyle None -ErrorAction SilentlyContinue
}

# UTF-8 everywhere
$env:PYTHONUTF8 = "1"
$env:LC_ALL = "en_US.UTF-8"
$env:LANG = "en_US.UTF-8"
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::UTF8

# EQ12 Environment Variables
$env:EQ12_ROOT = "C:\EQ12"
$env:PYTHONPATH = "C:\EQ12"

# EQ12 Shortcuts
Set-Alias -Name activate -Value "C:\EQ12\.venv\Scripts\activate.ps1" -ErrorAction SilentlyContinue
Set-Alias -Name eq12test -Value "pytest C:\EQ12\tests\" -ErrorAction SilentlyContinue

# Enhanced prompt
function prompt {
    $location = Get-Location
    $venvName = if ($env:VIRTUAL_ENV) { " ($(Split-Path $env:VIRTUAL_ENV -Leaf))" } else { "" }
    "PS $location$venvName> "
}

# Better error handling
$ErrorActionPreference = "Continue"

# Welcome message
Write-Host "EQ12 PowerShell Environment Loaded" -ForegroundColor Green
Write-Host "Python UTF-8: $env:PYTHONUTF8 | Root: $env:EQ12_ROOT" -ForegroundColor Cyan

################################################################################
'@

    $profileContent | Out-File -FilePath $pwsh7ProfilePath -Encoding UTF8 -Force
    Write-ColorOutput "PowerShell profile created: $pwsh7ProfilePath" -Type Success

} else {
    Write-ColorOutput "`n[7/8] Skipping profile creation..." -Type Warning
}

################################################################################
# STEP 8: Generate summary & next steps
################################################################################
Write-ColorOutput "`n[8/8] Generating summary report..." -Type Info

$reportPath = "C:\EQ12\logs\powershell_upgrade_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

if (-not (Test-Path "C:\EQ12\logs")) {
    New-Item -ItemType Directory -Path "C:\EQ12\logs" -Force | Out-Null
}

$report = @{
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    original_version = $currentVersion.ToString()
    actions_completed = @{
        powershell_installed = -not $SkipInstall
        utf8_enabled = -not $SkipUTF8Fix
        long_paths_enabled = -not $SkipLongPaths
        profile_created = -not $SkipProfileSetup
    }
    next_steps = @(
        "Restart your computer to apply UTF-8 and long path changes",
        "Open PowerShell 7 from Start Menu or Windows Terminal",
        "In VS Code: Ctrl+Shift+P → Terminal: Select Default Profile → PowerShell 7",
        "Test UTF-8: `$OutputEncoding",
        "Activate EQ12 venv: C:\EQ12\.venv\Scripts\activate",
        "Run EQ12 tests: pytest C:\EQ12\tests\smoke_math_clean.py"
    )
}

$report | ConvertTo-Json -Depth 5 | Out-File -FilePath $reportPath -Encoding UTF8 -Force
Write-ColorOutput "Report saved: $reportPath" -Type Success

################################################################################
# Final Output
################################################################################
Write-Host ""
Write-ColorOutput "╔════════════════════════════════════════════════════════════╗" -Type Info
Write-ColorOutput "║              UPGRADE COMPLETE - REBOOT REQUIRED            ║" -Type Info
Write-ColorOutput "╚════════════════════════════════════════════════════════════╝" -Type Info
Write-Host ""
Write-ColorOutput "NEXT STEPS:" -Type Warning
Write-Host "  1. REBOOT your computer (required for UTF-8 & long paths)"
Write-Host "  2. Open PowerShell 7 from Start Menu"
Write-Host "  3. Set as default in VS Code:"
Write-Host "     Ctrl+Shift+P → Terminal: Select Default Profile → PowerShell 7"
Write-Host "  4. Verify installation:"
Write-Host "     pwsh -Command `$PSVersionTable.PSVersion"
Write-Host "  5. Test EQ12 environment:"
Write-Host "     cd C:\EQ12"
Write-Host "     .\.venv\Scripts\activate"
Write-Host "     pytest tests\smoke_math_clean.py"
Write-Host ""
Write-ColorOutput "Your EQ12 workspace will run SIGNIFICANTLY faster after reboot." -Type Success
Write-Host ""

# Offer to reboot now
$rebootNow = Read-Host "Reboot now? (Y/N)"
if ($rebootNow -eq 'Y') {
    Write-ColorOutput "Rebooting in 10 seconds..." -Type Warning
    shutdown /r /t 10 /c "EQ12 PowerShell upgrade complete - rebooting for UTF-8 and long path support"
}
