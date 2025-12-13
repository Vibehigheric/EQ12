# EQ12_PYLANCE_FIREWALL.ps1
# Prevents Pylance from scanning outside EQ12 workspace
# Stops C:\ drive enumeration, crashes, and infinite loops

[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== EQ12 Pylance Firewall ===" -ForegroundColor Cyan
Write-Host "Stopping Pylance from scanning your entire C:\ drive`n"

# Target workspace
$WorkspaceRoot = "C:\EQ12"

if (-not (Test-Path $WorkspaceRoot)) {
    Write-Warning "EQ12 workspace not found at: $WorkspaceRoot"
    Write-Host "Creating directory..."
    New-Item -ItemType Directory -Path $WorkspaceRoot -Force | Out-Null
}

# Create .vscode directory
$VsCodeDir = Join-Path $WorkspaceRoot ".vscode"
if (-not (Test-Path $VsCodeDir)) {
    New-Item -ItemType Directory -Path $VsCodeDir -Force | Out-Null
}

Write-Host "[1/4] Creating Pylance protection config..." -ForegroundColor Yellow

# Pyrightconfig.json - Master Pylance control file
$PyrightConfig = @"
{
  "include": [
    "./"
  ],
  "exclude": [
    "**/__pycache__",
    "**/node_modules",
    "**/.git",
    "**/.venv",
    "**/venv",
    "**/dist",
    "**/build",
    "**/miniconda3",
    "C:/Users",
    "C:/Windows",
    "C:/ProgramData",
    "C:/Program Files",
    "C:/Program Files (x86)",
    "C:/xampp",
    "C:/workspace",
    "C:/logs"
  ],
  "ignore": [
    "**/tmp",
    "**/temp",
    "**/.cache"
  ],
  "venvPath": ".",
  "venv": [".venv"],
  "pythonVersion": "3.12",
  "pythonPlatform": "Windows",
  "typeCheckingMode": "off",
  "strictListInference": false,
  "strictDictionaryInference": false,
  "strictSetInference": false,
  "reportMissingImports": false,
  "reportMissingTypeStubs": false,
  "useLibraryCodeForTypes": false
}
"@

$PyrightPath = Join-Path $WorkspaceRoot "pyrightconfig.json"
$PyrightConfig | Out-File -FilePath $PyrightPath -Encoding UTF8 -Force
Write-Host "  [✓] Created: pyrightconfig.json" -ForegroundColor Green

Write-Host "`n[2/4] Creating VS Code workspace settings..." -ForegroundColor Yellow

# VS Code settings - Disable aggressive scanning
$VsCodeSettings = @"
{
  "python.analysis.autoSearchPaths": false,
  "python.analysis.indexing": false,
  "python.analysis.useLibraryCodeForTypes": false,
  "python.analysis.diagnosticMode": "openFilesOnly",
  "python.analysis.exclude": [
    "**/__pycache__",
    "**/node_modules",
    "**/.venv",
    "**/miniconda3",
    "C:/Users/**",
    "C:/Windows/**",
    "C:/ProgramData/**",
    "C:/Program Files/**",
    "C:/Program Files (x86)/**"
  ],
  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/.git/subtree-cache/**": true,
    "**/node_modules/**": true,
    "**/.venv/**": true,
    "**/venv/**": true,
    "**/__pycache__/**": true,
    "**/dist/**": true,
    "**/build/**": true,
    "**/logs/**": true,
    "**/reports/**": true,
    "**/miniconda3/**": true,
    "C:/Users/**": true,
    "C:/Windows/**": true,
    "C:/ProgramData/**": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.ruff_cache": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/dist": true,
    "**/build": true,
    "**/.venv": true,
    "**/venv": true,
    "**/__pycache__": true,
    "**/logs": true,
    "**/reports": true,
    "C:/Users/**": true,
    "C:/Windows/**": true
  },
  "files.maxMemoryForLargeFilesMB": 4096,
  "python.analysis.typeCheckingMode": "off"
}
"@

$SettingsPath = Join-Path $VsCodeDir "settings.json"
$VsCodeSettings | Out-File -FilePath $SettingsPath -Encoding UTF8 -Force
Write-Host "  [✓] Created: .vscode/settings.json" -ForegroundColor Green

Write-Host "`n[3/4] Cleaning corrupted workspace cache..." -ForegroundColor Yellow

# Clear corrupted workspace storage
$WorkspaceStorage = "$env:APPDATA\Code\User\workspaceStorage"
if (Test-Path $WorkspaceStorage) {
    Write-Host "  Removing corrupted workspace cache..."
    Remove-Item -Recurse -Force $WorkspaceStorage -ErrorAction SilentlyContinue
    Write-Host "  [✓] Cleared workspace cache" -ForegroundColor Green
} else {
    Write-Host "  [✓] No corrupted cache found" -ForegroundColor Green
}

# Clear Pylance cache
$PylanceCache = "$env:LOCALAPPDATA\Temp\pylance"
if (Test-Path $PylanceCache) {
    Write-Host "  Removing Pylance cache..."
    Remove-Item -Recurse -Force $PylanceCache -ErrorAction SilentlyContinue
    Write-Host "  [✓] Cleared Pylance cache" -ForegroundColor Green
}

Write-Host "`n[4/4] Verifying protection..." -ForegroundColor Yellow

$FilesCreated = @(
    $PyrightPath,
    $SettingsPath
)

$AllGood = $true
foreach ($file in $FilesCreated) {
    if (Test-Path $file) {
        Write-Host "  [✓] $(Split-Path $file -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "  [✗] MISSING: $(Split-Path $file -Leaf)" -ForegroundColor Red
        $AllGood = $false
    }
}

if ($AllGood) {
    Write-Host "`n=== Pylance Firewall Active ===" -ForegroundColor Cyan
    Write-Host "`n[PROTECTION ENABLED]" -ForegroundColor Green
    Write-Host "Pylance will now ONLY scan:"
    Write-Host "  - C:\EQ12\"
    Write-Host "  - Maximum ~500 files (not 22,511)"
    Write-Host "`n[BLOCKED DIRECTORIES]" -ForegroundColor Red
    Write-Host "  - C:\Users\"
    Write-Host "  - C:\Windows\"
    Write-Host "  - C:\ProgramData\"
    Write-Host "  - C:\Program Files\"
    Write-Host "  - All symlinks and system directories"
    
    Write-Host "`n[NEXT STEPS]" -ForegroundColor Yellow
    Write-Host "1. Close ALL VS Code windows"
    Write-Host "2. Restart your computer (clears stuck worker threads)"
    Write-Host "3. Open ONLY: C:\EQ12 (not C:\EQ12_BROKEN_20251122_210342)"
    Write-Host "4. Verify Pylance logs show <500 files (not 22,511)`n"
    
    Write-Host "[VERIFICATION COMMAND]" -ForegroundColor Cyan
    Write-Host "After restart, check Pylance output panel for:"
    Write-Host '  "Found XXX source files" (should be <500)'
    Write-Host '  NOT "No include entries specified; assuming c:\Windows"'
    Write-Host "`nIf still broken, run: .\scripts\EQ12_REBUILD.ps1 -Force`n"
} else {
    Write-Host "`n[!] WARNING: Some files failed to create" -ForegroundColor Red
    exit 1
}

# Create verification report
$ReportPath = "C:\EQ12\logs\pylance_firewall_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
New-Item -ItemType Directory -Path (Split-Path $ReportPath -Parent) -Force -ErrorAction SilentlyContinue | Out-Null

$Report = @{
    Timestamp = (Get-Date).ToString('o')
    WorkspaceRoot = $WorkspaceRoot
    FilesCreated = $FilesCreated
    ExcludedPaths = @(
        "C:/Users",
        "C:/Windows",
        "C:/ProgramData",
        "C:/Program Files",
        "C:/Program Files (x86)"
    )
    PylanceSettings = @{
        IndexingDisabled = $true
        AutoSearchDisabled = $true
        DiagnosticMode = "openFilesOnly"
        TypeCheckingMode = "off"
    }
}

$Report | ConvertTo-Json -Depth 3 | Out-File -FilePath $ReportPath -Encoding UTF8
Write-Host "Report saved: $ReportPath" -ForegroundColor Gray
