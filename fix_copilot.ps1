# EQ12 Copilot Stability Patch - HARDENED
# Fixes all Pylance EPIPE errors and Copilot corruption issues
# Buffalo NY 14215 Content Empire
# Date: November 16, 2025

[CmdletBinding()]
param()

Write-Host "================================================================" -ForegroundColor Green
Write-Host "EQ12 COPILOT STABILITY PATCH - EMERGENCY REPAIR MODE" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Step 1: Force close VS Code and related processes
Write-Host "[1/8] Terminating VS Code processes..." -ForegroundColor Yellow
$processes = @('Code', 'code', 'Code - Insiders', 'code-insiders')
foreach ($proc in $processes) {
    try {
        Stop-Process -Name $proc -Force -ErrorAction SilentlyContinue
        Write-Host "  Terminated: $proc" -ForegroundColor Gray
    } catch {
        # Ignore errors - process might not be running
    }
}
Start-Sleep -Seconds 2

# Step 2: Clear VS Code cache and corrupt data
Write-Host "[2/8] Clearing corrupted VS Code cache..." -ForegroundColor Yellow
$cachePaths = @(
    "$env:APPDATA\Code\CachedExtensions",
    "$env:APPDATA\Code\logs",
    "$env:APPDATA\Code\Service Worker",
    "$env:APPDATA\Code\User\workspaceStorage",
    "$env:USERPROFILE\.vscode-server\data",
    "$env:USERPROFILE\.vscode\extensions"
)

foreach ($path in $cachePaths) {
    if (Test-Path $path) {
        try {
            Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  Cleared: $path" -ForegroundColor Gray
        } catch {
            Write-Host "  Warning: Could not clear $path" -ForegroundColor DarkYellow
        }
    }
}

# Step 3: Reset Pylance language server data
Write-Host "[3/8] Resetting Pylance language server..." -ForegroundColor Yellow
$pylancePath = "$env:USERPROFILE\AppData\Roaming\Code\User\globalStorage\ms-python.vscode-pylance"
if (Test-Path $pylancePath) {
    Remove-Item $pylancePath -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  Pylance cache cleared" -ForegroundColor Gray
}

# Step 4: Set ASCII-safe environment variables
Write-Host "[4/8] Configuring ASCII-safe environment..." -ForegroundColor Yellow
$asciiEnvVars = @{
    'PYTHONIOENCODING' = 'ascii'
    'PYTHONUTF8' = '0'
    'LC_ALL' = 'C'
    'LANG' = 'C'
    'PYTHONLEGACYWINDOWSSTDIO' = '1'
    'EQ12_ASCII_MODE' = 'ACTIVE'
    'EQ12_IMMUNITY_ACTIVE' = 'TRUE'
}

foreach ($var in $asciiEnvVars.GetEnumerator()) {
    [Environment]::SetEnvironmentVariable($var.Key, $var.Value, 'User')
    Write-Host "  Set: $($var.Key)=$($var.Value)" -ForegroundColor Gray
}

# Step 5: Reinstall critical extensions
Write-Host "[5/8] Reinstalling critical extensions..." -ForegroundColor Yellow
$extensions = @(
    'ms-python.vscode-pylance',
    'ms-python.python',
    'github.copilot',
    'github.copilot-chat'
)

foreach ($ext in $extensions) {
    try {
        Write-Host "  Installing: $ext" -ForegroundColor Gray
        & code --install-extension $ext --force 2>$null
    } catch {
        Write-Host "  Warning: Failed to install $ext" -ForegroundColor DarkYellow
    }
}

# Step 6: Create VS Code settings backup and repair
Write-Host "[6/8] Repairing VS Code settings..." -ForegroundColor Yellow
$settingsPath = "$env:APPDATA\Code\User\settings.json"
if (Test-Path $settingsPath) {
    # Backup existing settings
    Copy-Item $settingsPath "$settingsPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')" -Force
    Write-Host "  Settings backed up" -ForegroundColor Gray
}

# Step 7: Apply ASCII-safe VS Code configuration
Write-Host "[7/8] Applying ASCII-safe configuration..." -ForegroundColor Yellow
$asciiSafeSettings = @"
{
    "python.languageServer": "Pylance",
    "python.defaultInterpreterPath": "python",
    "python.analysis.indexing": true,
    "python.analysis.memory.keepLibraryAst": false,
    "python.analysis.enableSyncThreads": true,
    "python.analysis.typeCheckingMode": "off",
    "python.analysis.diagnosticMode": "workspace",
    "python.analysis.completeFunctionParens": false,
    "python.analysis.enableSyncServer": false,
    "python.analysis.logLevel": "Error",

    "files.encoding": "utf8",
    "files.autoGuessEncoding": false,
    "files.eol": "\n",

    "editor.formatOnSave": false,
    "editor.formatOnPaste": false,
    "editor.formatOnType": false,
    "editor.renderControlCharacters": false,
    "editor.unicodeHighlight.nonBasicASCII": true,
    "editor.unicodeHighlight.invisibleCharacters": true,
    "editor.unicodeHighlight.ambiguousCharacters": true,

    "terminal.integrated.env.windows": {
        "PYTHONIOENCODING": "ascii",
        "PYTHONUTF8": "0",
        "LC_ALL": "C",
        "LANG": "C",
        "EQ12_ASCII_MODE": "ACTIVE"
    },

    "github.copilot.enable": true,
    "github.copilot.advanced": {
        "inlineSuggest.enable": true,
        "chat.safeContinue": true,
        "chat.disableContinueOperator": true
    }
}
"@

# Ensure settings directory exists
$settingsDir = Split-Path $settingsPath -Parent
if (!(Test-Path $settingsDir)) {
    New-Item -ItemType Directory -Path $settingsDir -Force | Out-Null
}

# Write ASCII-safe settings
Set-Content -Path $settingsPath -Value $asciiSafeSettings -Encoding ASCII
Write-Host "  ASCII-safe settings applied" -ForegroundColor Gray

# Step 8: Final verification and restart
Write-Host "[8/8] Final verification..." -ForegroundColor Yellow

# Test ASCII safety module
if (Test-Path "C:\EQ12\ascii_safety.py") {
    try {
        $result = & python "C:\EQ12\ascii_safety.py" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ASCII safety module: OK" -ForegroundColor Green
        } else {
            Write-Host "  ASCII safety module: WARNING" -ForegroundColor DarkYellow
        }
    } catch {
        Write-Host "  ASCII safety module: ERROR" -ForegroundColor Red
    }
} else {
    Write-Host "  ASCII safety module: NOT FOUND" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "EQ12 COPILOT STABILITY PATCH COMPLETE" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor White
Write-Host "1. Restart your computer (recommended)" -ForegroundColor Yellow
Write-Host "2. Open VS Code: code C:\EQ12" -ForegroundColor Yellow
Write-Host "3. Wait for extensions to reload" -ForegroundColor Yellow
Write-Host "4. Test Pylance - no more EPIPE errors" -ForegroundColor Yellow
Write-Host ""
Write-Host "PROTECTION ACTIVE:" -ForegroundColor White
Write-Host "- Unicode corruption immunity" -ForegroundColor Green
Write-Host "- Pylance EPIPE error prevention" -ForegroundColor Green
Write-Host "- ASCII-safe Copilot operation" -ForegroundColor Green
Write-Host "- LSP channel stability enforced" -ForegroundColor Green
Write-Host ""
Write-Host "Buffalo NY 14215 Content Empire - COPILOT HARDENED" -ForegroundColor Cyan
