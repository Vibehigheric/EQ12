# EQ12_EXTENSION_GUARD.ps1
# Automated extension safety system for EQ12 workspace
# Removes dangerous extensions, installs safe versions, prevents crashes

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== EQ12 Extension Guard ===" -ForegroundColor Cyan
Write-Host "Protecting your VS Code environment from dangerous extensions"
Write-Host ""

# Define safe extensions (exact versions we want)
$SafeExtensions = @{
    "ms-vscode.PowerShell"      = "PowerShell Language Support"
    "ms-python.python"          = "Python Extension"
    "ms-python.vscode-pylance"  = "Pylance (Python IntelliSense)"
    "github.copilot"            = "GitHub Copilot"
    "github.copilot-chat"       = "GitHub Copilot Chat"
}

# Define dangerous extensions to REMOVE
$DangerousExtensions = @(
    "ms-vscode-remote.remote-wsl"
    "ms-vscode-remote.remote-containers"
    "ms-azuretools.vscode-docker"
    "bradlc.vscode-tailwindcss"
    "ms-python.black-formatter"
    "ms-toolsai.jupyter"
    "dbaeumer.vscode-eslint"
    "esbenp.prettier-vscode"
    "redhat.vscode-yaml"
    "eamodio.gitlens"
    "WallabyJs.wallaby-vscode"
    "ms-vscode.test-adapter-converter"
)

# VS Code extensions directory
$ExtensionsDir = "$env:USERPROFILE\.vscode\extensions"

if (-not (Test-Path $ExtensionsDir)) {
    Write-Warning "VS Code extensions directory not found: $ExtensionsDir"
    exit 1
}

Write-Host "[1/5] Scanning installed extensions..." -ForegroundColor Yellow

# Get currently installed extensions
$InstalledExtensions = Get-ChildItem -Path $ExtensionsDir -Directory | ForEach-Object {
    $_.Name -replace '-\d+\.\d+\.\d+.*$', ''
}

Write-Host "Found $($InstalledExtensions.Count) installed extensions"
Write-Host ""

# Check for dangerous extensions
Write-Host "[2/5] Detecting dangerous extensions..." -ForegroundColor Yellow
$FoundDangerous = @()

foreach ($ext in $DangerousExtensions) {
    $matches = $InstalledExtensions | Where-Object { $_ -like "$ext*" }
    if ($matches) {
        $FoundDangerous += $ext
        Write-Host "  [!] DANGEROUS: $ext" -ForegroundColor Red
    }
}

if ($FoundDangerous.Count -eq 0) {
    Write-Host "  [OK] No dangerous extensions found" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "Found $($FoundDangerous.Count) dangerous extension(s)" -ForegroundColor Red
}

# Check for missing safe extensions
Write-Host ""
Write-Host "[3/5] Checking required extensions..." -ForegroundColor Yellow
$MissingExtensions = @()

foreach ($ext in $SafeExtensions.Keys) {
    $matches = $InstalledExtensions | Where-Object { $_ -like "$ext*" }
    if (-not $matches) {
        $MissingExtensions += $ext
        Write-Host "  [!] MISSING: $($SafeExtensions[$ext]) ($ext)" -ForegroundColor Yellow
    }
    else {
        Write-Host "  [OK] INSTALLED: $($SafeExtensions[$ext])" -ForegroundColor Green
    }
}

if ($MissingExtensions.Count -eq 0) {
    Write-Host ""
    Write-Host "All required extensions are installed" -ForegroundColor Green
}

# DRY RUN MODE
if ($DryRun) {
    Write-Host ""
    Write-Host "[DRY RUN MODE - No changes will be made]" -ForegroundColor Cyan
    
    if ($FoundDangerous.Count -gt 0) {
        Write-Host ""
        Write-Host "Would REMOVE these extensions:"
        $FoundDangerous | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    }
    
    if ($MissingExtensions.Count -gt 0) {
        Write-Host ""
        Write-Host "Would INSTALL these extensions:"
        $MissingExtensions | ForEach-Object { Write-Host "  - $_ ($($SafeExtensions[$_]))" -ForegroundColor Green }
    }
    
    Write-Host ""
    Write-Host "Run without -DryRun to apply changes" -ForegroundColor Cyan
    exit 0
}

# REMOVE DANGEROUS EXTENSIONS
if ($FoundDangerous.Count -gt 0) {
    Write-Host ""
    Write-Host "[4/5] Removing dangerous extensions..." -ForegroundColor Yellow
    
    if (-not $Force) {
        $confirm = Read-Host "Remove $($FoundDangerous.Count) dangerous extension(s)? (y/N)"
        if ($confirm -ne 'y') {
            Write-Host "Skipping removal" -ForegroundColor Yellow
        }
        else {
            foreach ($ext in $FoundDangerous) {
                Write-Host "  Uninstalling $ext..." -ForegroundColor Red
                & code --uninstall-extension $ext 2>&1 | Out-Null
            }
            Write-Host "  [OK] Removed dangerous extensions" -ForegroundColor Green
        }
    }
    else {
        foreach ($ext in $FoundDangerous) {
            Write-Host "  Uninstalling $ext..." -ForegroundColor Red
            & code --uninstall-extension $ext 2>&1 | Out-Null
        }
        Write-Host "  [OK] Removed dangerous extensions" -ForegroundColor Green
    }
}
else {
    Write-Host ""
    Write-Host "[4/5] No dangerous extensions to remove" -ForegroundColor Green
}

# INSTALL MISSING SAFE EXTENSIONS
if ($MissingExtensions.Count -gt 0) {
    Write-Host ""
    Write-Host "[5/5] Installing missing safe extensions..." -ForegroundColor Yellow
    
    foreach ($ext in $MissingExtensions) {
        Write-Host "  Installing $($SafeExtensions[$ext])..." -ForegroundColor Green
        & code --install-extension $ext --force 2>&1 | Out-Null
    }
    
    Write-Host "  [OK] Installed $($MissingExtensions.Count) extension(s)" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "[5/5] All safe extensions already installed" -ForegroundColor Green
}

# FINAL VERIFICATION
Write-Host ""
Write-Host "=== Extension Guard Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "[NEXT STEPS]" -ForegroundColor Yellow
Write-Host "1. Close ALL VS Code windows completely"
Write-Host "2. Reopen VS Code"
Write-Host "3. Open: C:\EQ12_BROKEN_20251122_210342"
Write-Host "4. Verify PowerShell extension loads (check status bar)"
Write-Host ""

# Export report
$LogsDir = "C:\EQ12_BROKEN_20251122_210342\logs"
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}

$ReportPath = Join-Path $LogsDir "extension_guard_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$Report = @{
    Timestamp           = (Get-Date).ToString('o')
    RemovedExtensions   = $FoundDangerous
    InstalledExtensions = $MissingExtensions
    SafeExtensions      = $SafeExtensions.Keys
    DangerousExtensions = $DangerousExtensions
}

$Report | ConvertTo-Json -Depth 3 | Out-File -FilePath $ReportPath -Encoding UTF8
Write-Host "Report saved: $ReportPath" -ForegroundColor Gray
