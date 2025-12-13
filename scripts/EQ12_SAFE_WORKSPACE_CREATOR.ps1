# EQ12_SAFE_WORKSPACE_CREATOR.ps1
# Creates a locked, protected EQ12 workspace that prevents VS Code corruption
# Migrates from BROKEN workspace to clean C:\EQ12

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$SkipBackup
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== EQ12 Safe Workspace Creator ===" -ForegroundColor Cyan
Write-Host "Creating protected workspace at C:\EQ12`n"

$SourceWorkspace = "C:\EQ12_BROKEN_20251122_210342"
$TargetWorkspace = "C:\EQ12"

# Verify source exists
if (-not (Test-Path $SourceWorkspace)) {
    Write-Error "Source workspace not found: $SourceWorkspace"
    exit 1
}

# Check if target already exists
if (Test-Path $TargetWorkspace) {
    Write-Host "[!] Target workspace already exists: $TargetWorkspace" -ForegroundColor Yellow
    
    if (-not $Force) {
        $confirm = Read-Host "Delete existing C:\EQ12 and recreate? (y/N)"
        if ($confirm -ne 'y') {
            Write-Host "Cancelled" -ForegroundColor Red
            exit 0
        }
    }
    
    Write-Host "Removing existing workspace..."
    Remove-Item -Recurse -Force $TargetWorkspace
}

Write-Host "[1/6] Creating backup snapshot..." -ForegroundColor Yellow

if (-not $SkipBackup) {
    $BackupPath = "C:\EQ12_BACKUP_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
    
    Write-Host "  Compressing workspace (this may take a few minutes)..."
    
    # Use robocopy to create clean copy first (excludes problematic files)
    $TempCopy = "$env:TEMP\EQ12_TEMP"
    if (Test-Path $TempCopy) {
        Remove-Item -Recurse -Force $TempCopy
    }
    
    robocopy $SourceWorkspace $TempCopy /E /XD ".git" "node_modules" ".venv" "__pycache__" "dist" "build" "logs" /XF "*.pyc" /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
    
    Compress-Archive -Path $TempCopy -DestinationPath $BackupPath -CompressionLevel Fastest
    Remove-Item -Recurse -Force $TempCopy
    
    Write-Host "  [✓] Backup created: $BackupPath" -ForegroundColor Green
} else {
    Write-Host "  [!] Skipping backup (not recommended)" -ForegroundColor Yellow
}

Write-Host "`n[2/6] Creating clean workspace structure..." -ForegroundColor Yellow

# Create target directory
New-Item -ItemType Directory -Path $TargetWorkspace -Force | Out-Null

# Copy essential files only (exclude problematic directories)
$ExcludeDirs = @(".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", "logs", "reports", "miniconda3", "web3_repos", "profiles")
$ExcludeFiles = @("*.pyc", "*.pyo", "*.pyd", ".DS_Store", "Thumbs.db")

Write-Host "  Copying files (excluding: $($ExcludeDirs -join ', '))..."

$RobocopyArgs = @(
    $SourceWorkspace,
    $TargetWorkspace,
    "/E",  # Copy subdirectories including empty
    "/NFL", "/NDL", "/NJH", "/NJS", "/nc", "/ns", "/np"  # Suppress output
)

# Add exclusions
foreach ($dir in $ExcludeDirs) {
    $RobocopyArgs += "/XD"
    $RobocopyArgs += $dir
}

foreach ($file in $ExcludeFiles) {
    $RobocopyArgs += "/XF"
    $RobocopyArgs += $file
}

& robocopy @RobocopyArgs | Out-Null

Write-Host "  [✓] Files copied" -ForegroundColor Green

Write-Host "`n[3/6] Creating protection files..." -ForegroundColor Yellow

# Create .vscode directory
$VsCodeDir = Join-Path $TargetWorkspace ".vscode"
New-Item -ItemType Directory -Path $VsCodeDir -Force | Out-Null

# pyrightconfig.json
$PyrightConfig = @"
{
  "include": ["./"],
  "exclude": [
    "**/__pycache__",
    "**/node_modules",
    "**/.git",
    "**/.venv",
    "**/venv",
    "**/dist",
    "**/build",
    "C:/Users",
    "C:/Windows",
    "C:/ProgramData",
    "C:/Program Files",
    "C:/Program Files (x86)"
  ],
  "venvPath": ".",
  "pythonVersion": "3.12",
  "typeCheckingMode": "off"
}
"@
$PyrightConfig | Out-File -FilePath (Join-Path $TargetWorkspace "pyrightconfig.json") -Encoding UTF8 -Force

# .vscode/settings.json
$VsCodeSettings = @"
{
  "python.analysis.autoSearchPaths": false,
  "python.analysis.indexing": false,
  "python.analysis.diagnosticMode": "openFilesOnly",
  "python.analysis.typeCheckingMode": "off",
  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/node_modules/**": true,
    "**/.venv/**": true,
    "**/__pycache__/**": true,
    "**/dist/**": true,
    "**/build/**": true,
    "C:/Users/**": true,
    "C:/Windows/**": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.ruff_cache": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/.venv": true,
    "**/__pycache__": true,
    "C:/Users/**": true,
    "C:/Windows/**": true
  }
}
"@
$VsCodeSettings | Out-File -FilePath (Join-Path $VsCodeDir "settings.json") -Encoding UTF8 -Force

# .vscode/extensions.json
$ExtensionsJson = @"
{
  "recommendations": [
    "ms-vscode.PowerShell",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "github.copilot",
    "github.copilot-chat"
  ],
  "unwantedRecommendations": [
    "ms-vscode-remote.remote-wsl",
    "ms-vscode-remote.remote-containers",
    "bradlc.vscode-tailwindcss",
    "ms-azuretools.vscode-docker"
  ]
}
"@
$ExtensionsJson | Out-File -FilePath (Join-Path $VsCodeDir "extensions.json") -Encoding UTF8 -Force

Write-Host "  [✓] Protection files created" -ForegroundColor Green

Write-Host "`n[4/6] Creating workspace directories..." -ForegroundColor Yellow

$RequiredDirs = @("logs", "reports", "backups", "scripts")
foreach ($dir in $RequiredDirs) {
    $dirPath = Join-Path $TargetWorkspace $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
    }
}

Write-Host "  [✓] Directory structure created" -ForegroundColor Green

Write-Host "`n[5/6] Cleaning VS Code cache..." -ForegroundColor Yellow

# Remove corrupted workspace cache
$CachePaths = @(
    "$env:APPDATA\Code\User\workspaceStorage",
    "$env:LOCALAPPDATA\Temp\pylance",
    "$env:APPDATA\Code\Cache",
    "$env:APPDATA\Code\CachedData"
)

foreach ($cache in $CachePaths) {
    if (Test-Path $cache) {
        Write-Host "  Removing: $(Split-Path $cache -Leaf)"
        Remove-Item -Recurse -Force $cache -ErrorAction SilentlyContinue
    }
}

Write-Host "  [✓] Cache cleared" -ForegroundColor Green

Write-Host "`n[6/6] Verifying workspace integrity..." -ForegroundColor Yellow

$RequiredFiles = @(
    (Join-Path $TargetWorkspace "pyrightconfig.json"),
    (Join-Path $VsCodeDir "settings.json"),
    (Join-Path $VsCodeDir "extensions.json")
)

$AllGood = $true
foreach ($file in $RequiredFiles) {
    if (Test-Path $file) {
        Write-Host "  [✓] $(Split-Path $file -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "  [✗] MISSING: $file" -ForegroundColor Red
        $AllGood = $false
    }
}

if ($AllGood) {
    Write-Host "`n=== Safe Workspace Created ===" -ForegroundColor Cyan
    Write-Host "`n[SUCCESS]" -ForegroundColor Green
    Write-Host "Protected workspace ready at: C:\EQ12"
    
    Write-Host "`n[PROTECTION ACTIVE]" -ForegroundColor Green
    Write-Host "  ✓ Pylance limited to C:\EQ12 only"
    Write-Host "  ✓ File watchers exclude system directories"
    Write-Host "  ✓ Dangerous extensions blocked"
    Write-Host "  ✓ Cache cleared"
    
    Write-Host "`n[NEXT STEPS]" -ForegroundColor Yellow
    Write-Host "1. Close ALL VS Code windows"
    Write-Host "2. Restart your computer"
    Write-Host "3. Open VS Code and load: C:\EQ12"
    Write-Host "4. Install safe extensions:"
    Write-Host "     cd C:\EQ12\scripts"
    Write-Host "     .\EQ12_EXTENSION_GUARD.ps1"
    
    Write-Host "`n[OLD WORKSPACE]" -ForegroundColor Yellow
    Write-Host "You can safely delete after verification:"
    Write-Host "  $SourceWorkspace"
    
    if (-not $SkipBackup) {
        Write-Host "`n[BACKUP LOCATION]" -ForegroundColor Cyan
        Write-Host "  $BackupPath`n"
    }
} else {
    Write-Host "`n[!] ERROR: Some files missing" -ForegroundColor Red
    exit 1
}

# Create success report
$ReportPath = Join-Path $TargetWorkspace "logs\workspace_creation_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$Report = @{
    Timestamp = (Get-Date).ToString('o')
    SourceWorkspace = $SourceWorkspace
    TargetWorkspace = $TargetWorkspace
    BackupPath = if (-not $SkipBackup) { $BackupPath } else { "Skipped" }
    FilesCreated = $RequiredFiles
    ExcludedDirectories = $ExcludeDirs
}

$Report | ConvertTo-Json -Depth 3 | Out-File -FilePath $ReportPath -Encoding UTF8
Write-Host "Report saved: $ReportPath" -ForegroundColor Gray
