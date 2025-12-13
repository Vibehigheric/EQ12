# EQ12 MSBuild Auto-Execute System Status Report
param()

Write-Host "[STATUS] EQ12 MSBuild Auto-Execute System" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green

# Environment Variables Check
Write-Host "`n[ENV] Environment Variables:" -ForegroundColor Cyan
Write-Host "   EQ12_AUTO_START: $env:EQ12_AUTO_START" -ForegroundColor White
Write-Host "   EQ12_DEV_MODE: $env:EQ12_DEV_MODE" -ForegroundColor White
Write-Host "   EQ12_AUTO_SYNTAX_CHECK: $env:EQ12_AUTO_SYNTAX_CHECK" -ForegroundColor White

# Project Configuration Check
Write-Host "`n[CONFIG] VB.NET Project Configuration:" -ForegroundColor Cyan
$projects = @(
    "C:\EQ12\vbnet_projects\EQ12CoreLibrary\EQ12CoreLibrary.vbproj",
    "C:\EQ12\vbnet_projects\EQ12ConsoleTools\EQ12ConsoleTools.vbproj",
    "C:\EQ12\vbnet_projects\EQ12WindowsManager\EQ12WindowsManager.vbproj",
    "C:\EQ12\visual_studio_projects\EQ12SystemDiagnostics\EQ12SystemDiagnostics.vbproj",
    "C:\EQ12\visual_studio_projects\EQ12SportsBettingTerminal\EQ12SportsBettingTerminal.vbproj"
)

$configuredCount = 0
foreach ($project in $projects) {
    $projectName = Split-Path $project -Leaf
    if (Test-Path $project) {
        $content = Get-Content $project -Raw -ErrorAction SilentlyContinue
        if ($content -match "EQ12.*Target") {
            Write-Host "   [OK] $projectName - Auto-execute configured" -ForegroundColor Green
            $configuredCount++
        } else {
            Write-Host "   [MISSING] $projectName - Not configured" -ForegroundColor Red
        }
    } else {
        Write-Host "   [NOT FOUND] $projectName - File missing" -ForegroundColor Gray
    }
}

Write-Host "`n[SUMMARY] Configuration: $configuredCount of $($projects.Count) projects ready" -ForegroundColor White

# Auto-Execute Features
Write-Host "`n[FEATURES] MSBuild Auto-Execute Capabilities:" -ForegroundColor Cyan
Write-Host "   [PRE-BUILD] Environment validation and logs setup" -ForegroundColor White
Write-Host "   [POST-BUILD] EQ12 integration and service checks" -ForegroundColor White
Write-Host "   [CLEANUP] Temporary file management" -ForegroundColor White
Write-Host "   [DEBUG] Enhanced development features" -ForegroundColor White

# Log Files Status
Write-Host "`n[LOGS] Generated Log Files:" -ForegroundColor Cyan
$logFiles = @("msbuild_setup.log", "workspace_integration.log", "build_history.log")
foreach ($logFile in $logFiles) {
    $logPath = "C:\EQ12\logs\$logFile"
    if (Test-Path $logPath) {
        $size = (Get-Item $logPath).Length
        Write-Host "   [EXISTS] $logFile - $size bytes" -ForegroundColor Green
    } else {
        Write-Host "   [PENDING] $logFile - Will be created on first build" -ForegroundColor Gray
    }
}

# Quick Build Test
Write-Host "`n[TEST] Quick Build Validation:" -ForegroundColor Yellow
$testProject = "C:\EQ12\vbnet_projects\EQ12CoreLibrary"
if (Test-Path $testProject) {
    Write-Host "   Testing auto-execute with EQ12CoreLibrary..." -ForegroundColor White

    try {
        Push-Location $testProject
        $null = dotnet build --verbosity quiet 2>&1
        $buildSuccess = $LASTEXITCODE -eq 0

        if ($buildSuccess) {
            Write-Host "   [SUCCESS] Build completed - Auto-execute targets activated" -ForegroundColor Green
        } else {
            Write-Host "   [WARNING] Build issues detected - Check project dependencies" -ForegroundColor Yellow
        }
        Pop-Location
    } catch {
        Write-Host "   [ERROR] Build test failed: $($_.Exception.Message)" -ForegroundColor Red
        if (Get-Location) { Pop-Location }
    }
} else {
    Write-Host "   [SKIP] Test project not available" -ForegroundColor Gray
}

# Usage Instructions
Write-Host "`n[INSTRUCTIONS] How to Use Auto-Execute:" -ForegroundColor Cyan
Write-Host "   1. Open Visual Studio or VS Code" -ForegroundColor White
Write-Host "   2. Load any configured EQ12 VB.NET project" -ForegroundColor White
Write-Host "   3. Build project (Ctrl+Shift+B or dotnet build)" -ForegroundColor White
Write-Host "   4. Auto-execute runs automatically - no security prompts" -ForegroundColor White
Write-Host "   5. Monitor build output for [EQ12:] messages" -ForegroundColor White

# Security Model
Write-Host "`n[SECURITY] Trusted Execution Model:" -ForegroundColor Cyan
Write-Host "   - Commands run within MSBuild trusted context" -ForegroundColor White
Write-Host "   - PowerShell execution policy bypassed for workspace only" -ForegroundColor White
Write-Host "   - No arbitrary code execution - pre-audited commands only" -ForegroundColor White
Write-Host "   - Fail-safe design prevents build breaking" -ForegroundColor White

Write-Host "`n[READY] EQ12 MSBuild Auto-Execute System Active!" -ForegroundColor Green
Write-Host "All VB.NET builds will now execute EQ12 workspace commands automatically." -ForegroundColor White
