<#
.SYNOPSIS
    Build script for Windows Data Sentinel VB.NET Data Collector

.DESCRIPTION
    Compiles the VB.NET data collector using dotnet CLI
    Outputs compiled executable to bin/Release folder

.PARAMETER Clean
    Clean build artifacts before compiling

.EXAMPLE
    .\build_collector.ps1
    .\build_collector.ps1 -Clean
#>

[CmdletBinding()]
param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

# Paths
$scriptRoot = Split-Path -Parent $PSCommandPath
$projectRoot = Split-Path -Parent $scriptRoot
$vbProjectPath = Join-Path $projectRoot "src\VBDataCollector\VBDataCollector.vbproj"
$outputDir = Join-Path $projectRoot "src\VBDataCollector\bin\Release\net8.0"

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Windows Data Sentinel - VB.NET Build Script" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Check if dotnet is installed
try {
    $dotnetVersion = dotnet --version
    Write-Host "[INFO] dotnet SDK version: $dotnetVersion" -ForegroundColor Green
} catch {
    Write-Error "dotnet SDK not found. Please install .NET 8.0 SDK from https://dotnet.microsoft.com/download"
    exit 1
}

# Check if project file exists
if (-not (Test-Path $vbProjectPath)) {
    Write-Error "Project file not found: $vbProjectPath"
    exit 1
}

Write-Host "[INFO] Project file: $vbProjectPath" -ForegroundColor Green

# Clean if requested
if ($Clean) {
    Write-Host "[INFO] Cleaning build artifacts..." -ForegroundColor Yellow
    try {
        dotnet clean $vbProjectPath --configuration Release
        Write-Host "[SUCCESS] Clean completed" -ForegroundColor Green
    } catch {
        Write-Warning "Clean failed: $_"
    }
}

# Restore NuGet packages
Write-Host "[INFO] Restoring NuGet packages..." -ForegroundColor Yellow
try {
    dotnet restore $vbProjectPath
    Write-Host "[SUCCESS] Restore completed" -ForegroundColor Green
} catch {
    Write-Error "Package restore failed: $_"
    exit 1
}

# Build project
Write-Host "[INFO] Building VB.NET project (Release configuration)..." -ForegroundColor Yellow
try {
    dotnet build $vbProjectPath --configuration Release --no-restore
    Write-Host "[SUCCESS] Build completed" -ForegroundColor Green
} catch {
    Write-Error "Build failed: $_"
    exit 1
}

# Check output
$exePath = Join-Path $outputDir "EQ12DataCollector.exe"
if (Test-Path $exePath) {
    $exeInfo = Get-Item $exePath
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host "[SUCCESS] Build complete!" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host "  Executable: $exePath" -ForegroundColor Cyan
    Write-Host "  Size: $($exeInfo.Length / 1KB) KB" -ForegroundColor Cyan
    Write-Host "  Modified: $($exeInfo.LastWriteTime)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To run the collector:" -ForegroundColor Yellow
    Write-Host "  $exePath" -ForegroundColor White
    Write-Host ""
} else {
    Write-Warning "Build succeeded but executable not found at expected location: $exePath"
    Write-Host "Output directory contents:" -ForegroundColor Yellow
    Get-ChildItem $outputDir -Recurse | Format-Table Name, Length, LastWriteTime
}
