# EQ12 VS Code Performance & XML Fix Script
# Fixes LemMinX XML spam and VS Code memory issues

param(
    [switch]$IncreaseNodeMemory = $true,
    [switch]$ClearCaches = $true,
    [switch]$OptimizeVirtualMemory = $false
)

Write-Host "[TOOLS] EQ12 VS Code Performance & XML Fix Script" -ForegroundColor Cyan
Write-Host "=" * 50

# 1. Create schemas + catalog + stub XSD (already created above)
$schemaDir = "$PWD\schemas"
if (-not (Test-Path $schemaDir)) {
    New-Item -Force -ItemType Directory -Path $schemaDir | Out-Null
    Write-Host "✅ Created schemas directory" -ForegroundColor Green
} else {
    Write-Host "✅ Schemas directory exists" -ForegroundColor Green
}

# Verify XML files exist
$nunitXsd = "$schemaDir\nunit.xsd"
$catalogXml = "$schemaDir\catalog.xml"

if (Test-Path $nunitXsd) {
    Write-Host "✅ NUnit schema exists" -ForegroundColor Green
} else {
    Write-Host "❌ NUnit schema missing - should be created by previous step" -ForegroundColor Red
}

if (Test-Path $catalogXml) {
    Write-Host "✅ XML Catalog exists" -ForegroundColor Green
} else {
    Write-Host "❌ XML Catalog missing - should be created by previous step" -ForegroundColor Red
}

# 2. Increase VS Code/Node.js memory limit
if ($IncreaseNodeMemory) {
    Write-Host "[MEMORY] Setting Node.js memory limit to 4GB..." -ForegroundColor Yellow
    try {
        [Environment]::SetEnvironmentVariable("NODE_OPTIONS", "--max-old-space-size=4096", [EnvironmentVariableTarget]::User)
        Write-Host "✅ Node.js memory limit set to 4GB" -ForegroundColor Green
        Write-Host "   Restart VS Code to apply changes" -ForegroundColor Yellow
    } catch {
        Write-Host "❌ Failed to set NODE_OPTIONS: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 3. Clear VS Code and LemMinX caches
if ($ClearCaches) {
    Write-Host "[CLEANUP] Clearing VS Code and LemMinX caches..." -ForegroundColor Yellow
    
    # Clear LemMinX cache
    $lemminxCache = "$env:USERPROFILE\.lemminx\cache"
    if (Test-Path $lemminxCache) {
        try {
            Remove-Item -Recurse -Force $lemminxCache -ErrorAction SilentlyContinue
            Write-Host "✅ Cleared LemMinX cache" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Could not clear LemMinX cache: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    
    # Clear VS Code extension host cache
    $vscodeCache = "$env:APPDATA\Code\User\workspaceStorage"
    if (Test-Path $vscodeCache) {
        Write-Host "✅ VS Code workspace cache found (not clearing - too risky)" -ForegroundColor Green
    }
    
    # Clear temp files
    $tempPaths = @(
        "$env:TEMP\vscode-*",
        "$env:TEMP\Microsoft_*",
        "$PWD\.vscode\.ropeproject",
        "$PWD\**\__pycache__"
    )
    
    foreach ($tempPath in $tempPaths) {
        if (Test-Path $tempPath) {
            try {
                Remove-Item -Recurse -Force $tempPath -ErrorAction SilentlyContinue
                Write-Host "✅ Cleared temp files: $tempPath" -ForegroundColor Green
            } catch {
                Write-Host "⚠️  Could not clear: $tempPath" -ForegroundColor Yellow
            }
        }
    }
}

# 4. Virtual Memory optimization (optional)
if ($OptimizeVirtualMemory) {
    Write-Host "[VIRTUAL_MEMORY] Virtual Memory optimization..." -ForegroundColor Yellow
    Write-Host "[WARNING] This requires manual configuration:" -ForegroundColor Yellow
    Write-Host "   1. Control Panel → System → Advanced system settings" -ForegroundColor White
    Write-Host "   2. Performance → Settings → Advanced → Virtual Memory → Change" -ForegroundColor White
    Write-Host "   3. Uncheck 'Automatically manage'" -ForegroundColor White
    Write-Host "   4. Select C: drive → Custom size" -ForegroundColor White
    Write-Host "   5. Initial: 4096 MB, Maximum: 8192 MB" -ForegroundColor White
    Write-Host "   6. Click Apply and Restart" -ForegroundColor White
}

# 5. Verify VS Code settings
$vscodeSettings = "$PWD\.vscode\settings.json"
if (Test-Path $vscodeSettings) {
    $settings = Get-Content $vscodeSettings -Raw | ConvertFrom-Json
    
    # Check if XML settings are present
    if ($settings.'xml.catalogs') {
        Write-Host "✅ VS Code XML catalog configured" -ForegroundColor Green
    } else {
        Write-Host "⚠️  VS Code XML catalog not found in settings" -ForegroundColor Yellow
    }
    
    # Check if file exclusions are present
    if ($settings.'files.exclude' -and $settings.'files.exclude'.'**/.venv') {
        Write-Host "✅ VS Code file exclusions configured" -ForegroundColor Green
    } else {
        Write-Host "⚠️  VS Code file exclusions may need updating" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  VS Code settings.json not found" -ForegroundColor Yellow
}

# 6. System information
Write-Host ""
Write-Host "[INFO] System Information:" -ForegroundColor Cyan
$memory = Get-WmiObject -Class Win32_ComputerSystem
$totalRAM = [math]::Round($memory.TotalPhysicalMemory / 1GB, 2)
Write-Host "   Total RAM: $totalRAM GB" -ForegroundColor White

$pageFile = Get-WmiObject -Class Win32_PageFileUsage
if ($pageFile) {
    $pageFileSize = [math]::Round($pageFile.AllocatedBaseSize / 1024, 2)
    Write-Host "   Page file: $pageFileSize GB" -ForegroundColor White
}

# 7. Recommendations
Write-Host ""
Write-Host "[TIPS] Recommendations:" -ForegroundColor Cyan
Write-Host "   1. Restart VS Code to apply NODE_OPTIONS" -ForegroundColor White
Write-Host "   2. Close unnecessary browser tabs" -ForegroundColor White
Write-Host "   3. Use 'Developer: Reload Window' after long sessions" -ForegroundColor White
Write-Host "   4. Consider upgrading to 16GB+ RAM for heavy development" -ForegroundColor White

Write-Host ""
Write-Host "[SUCCESS] EQ12 VS Code optimization complete!" -ForegroundColor Green
Write-Host "   The LemMinX XML errors should stop after VS Code restart." -ForegroundColor Green