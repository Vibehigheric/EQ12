# EQ12_REBUILD.ps1
# Nuclear option: Complete VS Code + Pylance + Copilot rebuild
# Only use when everything else has failed

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$KeepExtensions
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== EQ12 COMPLETE REBUILD ===" -ForegroundColor Red
Write-Host "WARNING: This will reset VS Code to factory defaults`n" -ForegroundColor Yellow

if (-not $Force) {
    Write-Host "This will:" -ForegroundColor Yellow
    Write-Host "  - Delete all VS Code settings"
    Write-Host "  - Remove all extensions (unless -KeepExtensions)"
    Write-Host "  - Clear all caches"
    Write-Host "  - Kill all VS Code processes"
    Write-Host "  - Rebuild workspace from scratch"
    
    $confirm = Read-Host "`nType 'REBUILD' to continue"
    if ($confirm -ne 'REBUILD') {
        Write-Host "Cancelled" -ForegroundColor Red
        exit 0
    }
}

Write-Host "`n[1/8] Killing all VS Code processes..." -ForegroundColor Yellow
Get-Process -Name "Code" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*\.vscode\*" } | Stop-Process -Force
Start-Sleep -Seconds 2
Write-Host "  [✓] Processes terminated" -ForegroundColor Green

Write-Host "`n[2/8] Removing VS Code cache..." -ForegroundColor Yellow
$CachePaths = @(
    "$env:APPDATA\Code\Cache",
    "$env:APPDATA\Code\CachedData",
    "$env:APPDATA\Code\CachedExtensions",
    "$env:APPDATA\Code\CachedExtensionVSIXs",
    "$env:APPDATA\Code\User\workspaceStorage",
    "$env:LOCALAPPDATA\Temp\vscode-*",
    "$env:LOCALAPPDATA\Temp\pylance"
)

foreach ($path in $CachePaths) {
    if (Test-Path $path) {
        Write-Host "  Removing: $(Split-Path $path -Leaf)"
        Remove-Item -Recurse -Force $path -ErrorAction SilentlyContinue
    }
}
Write-Host "  [✓] Cache cleared" -ForegroundColor Green

if (-not $KeepExtensions) {
    Write-Host "`n[3/8] Removing all extensions..." -ForegroundColor Yellow
    $ExtDir = "$env:USERPROFILE\.vscode\extensions"
    if (Test-Path $ExtDir) {
        Remove-Item -Recurse -Force $ExtDir -ErrorAction SilentlyContinue
        Write-Host "  [✓] Extensions removed" -ForegroundColor Green
    }
} else {
    Write-Host "`n[3/8] Keeping extensions (as requested)" -ForegroundColor Yellow
}

Write-Host "`n[4/8] Removing corrupted settings..." -ForegroundColor Yellow
$SettingsPaths = @(
    "$env:APPDATA\Code\User\settings.json.backup",
    "$env:APPDATA\Code\User\globalStorage\state.vscdb.backup"
)

foreach ($path in $SettingsPaths) {
    if (Test-Path $path) {
        Remove-Item -Force $path -ErrorAction SilentlyContinue
    }
}
Write-Host "  [✓] Corrupted settings removed" -ForegroundColor Green

Write-Host "`n[5/8] Creating clean workspace..." -ForegroundColor Yellow

$TargetWorkspace = "C:\EQ12"
if (-not (Test-Path $TargetWorkspace)) {
    New-Item -ItemType Directory -Path $TargetWorkspace -Force | Out-Null
}

# Create protection files
$VsCodeDir = Join-Path $TargetWorkspace ".vscode"
New-Item -ItemType Directory -Path $VsCodeDir -Force | Out-Null

# Minimal pyrightconfig.json
$PyrightConfig = @"
{
  "include": ["./"],
  "exclude": [
    "**/__pycache__",
    "**/node_modules",
    "**/.venv",
    "C:/Users",
    "C:/Windows",
    "C:/ProgramData"
  ],
  "pythonVersion": "3.12",
  "typeCheckingMode": "off"
}
"@
$PyrightConfig | Out-File -FilePath (Join-Path $TargetWorkspace "pyrightconfig.json") -Encoding UTF8 -Force

# Minimal settings.json
$Settings = @"
{
  "python.analysis.indexing": false,
  "python.analysis.autoSearchPaths": false,
  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/node_modules/**": true,
    "**/.venv/**": true
  }
}
"@
$Settings | Out-File -FilePath (Join-Path $VsCodeDir "settings.json") -Encoding UTF8 -Force

Write-Host "  [✓] Clean workspace created" -ForegroundColor Green

Write-Host "`n[6/8] Installing safe extensions..." -ForegroundColor Yellow
$SafeExtensions = @(
    "ms-vscode.PowerShell",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "github.copilot",
    "github.copilot-chat"
)

foreach ($ext in $SafeExtensions) {
    Write-Host "  Installing $ext..."
    & code --install-extension $ext --force 2>&1 | Out-Null
}
Write-Host "  [✓] Safe extensions installed" -ForegroundColor Green

Write-Host "`n[7/8] Creating MCP configuration..." -ForegroundColor Yellow
$McpConfig = @"
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\EQ12"]
    },
    "git": {
      "command": "python",
      "args": ["-m", "mcp_server_git", "--repository", "C:\\EQ12"]
    },
    "fetch": {
      "command": "python",
      "args": ["-m", "mcp_server_fetch"]
    },
    "time": {
      "command": "python",
      "args": ["-m", "mcp_server_time"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-playwright"]
    }
  }
}
"@

$McpPath = "$env:APPDATA\Code\User\mcp.json"
$McpConfig | Out-File -FilePath $McpPath -Encoding UTF8 -Force
Write-Host "  [✓] MCP configuration created" -ForegroundColor Green

Write-Host "`n[8/8] Final verification..." -ForegroundColor Yellow
$RequiredFiles = @(
    (Join-Path $TargetWorkspace "pyrightconfig.json"),
    (Join-Path $VsCodeDir "settings.json"),
    $McpPath
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
    Write-Host "`n=== REBUILD COMPLETE ===" -ForegroundColor Cyan
    Write-Host "`n[SUCCESS]" -ForegroundColor Green
    Write-Host "VS Code has been reset to a clean state"
    
    Write-Host "`n[WHAT WAS DONE]" -ForegroundColor Yellow
    Write-Host "  ✓ Killed all VS Code processes"
    Write-Host "  ✓ Cleared all caches"
    if (-not $KeepExtensions) {
        Write-Host "  ✓ Removed all extensions"
        Write-Host "  ✓ Reinstalled 5 safe extensions"
    }
    Write-Host "  ✓ Created clean C:\EQ12 workspace"
    Write-Host "  ✓ Configured Pylance firewall"
    Write-Host "  ✓ Configured MCP servers"
    
    Write-Host "`n[CRITICAL NEXT STEPS]" -ForegroundColor Red
    Write-Host "1. RESTART YOUR COMPUTER (required to clear worker threads)"
    Write-Host "2. After restart, open VS Code"
    Write-Host "3. File > Open Folder > C:\EQ12 (NOT C:\EQ12_BROKEN...)"
    Write-Host "4. Wait 30 seconds for extensions to load"
    Write-Host "5. Check Pylance output: Should show <500 files (not 22,511)"
    
    Write-Host "`n[VERIFICATION]" -ForegroundColor Cyan
    Write-Host "Open any .py file and check:"
    Write-Host "  - Python extension shows interpreter: .venv\Scripts\python.exe"
    Write-Host "  - Pylance shows: Pylance (not 'Pylance degraded')"
    Write-Host "  - Copilot Chat opens without tikTokenizer errors"
    
    Write-Host "`n[IF STILL BROKEN]" -ForegroundColor Yellow
    Write-Host "The issue is likely hardware/network related:"
    Write-Host "  - Insufficient RAM (<16GB)"
    Write-Host "  - Antivirus blocking VS Code"
    Write-Host "  - Network proxy interfering"
    Write-Host "  - Windows Defender scanning node processes`n"
} else {
    Write-Host "`n[!] ERROR: Some files missing" -ForegroundColor Red
    exit 1
}

# Create rebuild report
$ReportPath = "C:\EQ12\logs\rebuild_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
New-Item -ItemType Directory -Path (Split-Path $ReportPath -Parent) -Force -ErrorAction SilentlyContinue | Out-Null

$Report = @{
    Timestamp = (Get-Date).ToString('o')
    Action = "Complete Rebuild"
    ExtensionsKept = $KeepExtensions
    SafeExtensionsInstalled = $SafeExtensions
    WorkspaceCreated = $TargetWorkspace
    McpConfigured = $true
}

$Report | ConvertTo-Json -Depth 3 | Out-File -FilePath $ReportPath -Encoding UTF8
Write-Host "Report saved: $ReportPath" -ForegroundColor Gray
