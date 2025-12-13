<#
.SYNOPSIS
    EQ12 Build Pipeline - Windows to Ubuntu
    Stages a clean build context and runs docker buildx.

.DESCRIPTION
    This script enforces the "Windows Staging -> Ubuntu Runtime" contract.
    1. Creates a clean staging directory (C:\EQ12\build_context).
    2. Copies ONLY necessary files (allowlist approach).
    3. Runs docker buildx to build the image for linux/amd64.
    4. Pushes to the registry (optional) or saves as tar.

.EXAMPLE
    .\scripts\eq12_build_pipeline.ps1 -Push
#>

[CmdletBinding()]
param(
    [switch]$Push,
    [string]$ImageName = "eq12/core",
    [string]$Tag = "latest",
    [string]$StagingDir = "C:\EQ12\build_context"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 STARTING EQ12 BUILD PIPELINE" -ForegroundColor Cyan

# 1. Prepare Staging Directory
Write-Host "🧹 Preparing staging directory: $StagingDir" -ForegroundColor Yellow
if (Test-Path $StagingDir) {
    Remove-Item -Path $StagingDir -Recurse -Force
}
New-Item -Path $StagingDir -ItemType Directory | Out-Null

# 2. Define Allowlist (What goes into the container)
$AllowList = @(
    "src",
    "scripts",
    "requirements.txt",
    "requirements_patch.txt",
    "Dockerfile",
    ".env.example", # Do NOT copy .env
    "AGENTS.md"
)

# 3. Copy Files
Write-Host "📂 Copying artifacts..." -ForegroundColor Yellow
foreach ($Item in $AllowList) {
    $SourcePath = Join-Path -Path $PWD -ChildPath $Item
    if (Test-Path $SourcePath) {
        Write-Host "  + $Item" -ForegroundColor Green
        Copy-Item -Path $SourcePath -Destination $StagingDir -Recurse
    }
    else {
        Write-Warning "  ! Missing: $Item"
    }
}

# 4. Create .dockerignore in staging
Write-Host "🛡️ Generating .dockerignore..." -ForegroundColor Yellow
$DockerIgnoreContent = @(
    "**/__pycache__",
    "**/.venv",
    "**/.git",
    "**/*.pyc",
    "logs/",
    "data/",
    ".env"
)
$DockerIgnoreContent | Out-File -FilePath (Join-Path $StagingDir ".dockerignore") -Encoding utf8

# 5. Docker Buildx
Write-Host "🐳 Running Docker Buildx..." -ForegroundColor Cyan
$BuildCmd = "docker buildx build --platform linux/amd64 -t ${ImageName}:${Tag} ."

if ($Push) {
    $BuildCmd += " --push"
}
else {
    $BuildCmd += " --load" # Load into local docker daemon if not pushing
}

Write-Host "  > $BuildCmd" -ForegroundColor Gray

# Execute Build in Staging Dir
Push-Location $StagingDir
try {
    Write-Host "  > Executing build..." -ForegroundColor Gray
    # Use direct execution instead of Invoke-Expression for better error handling
    $process = Start-Process -FilePath "docker" -ArgumentList ($BuildCmd -replace "^docker ", "") -PassThru -Wait -NoNewWindow
    
    if ($process.ExitCode -eq 0) {
        Write-Host "✅ Build Complete!" -ForegroundColor Green
    }
    else {
        throw "Docker build failed with exit code $($process.ExitCode)"
    }
}
catch {
    Write-Error "❌ Build Failed: $_"
}
finally {
    Pop-Location
}

Write-Host "🏁 PIPELINE COMPLETE" -ForegroundColor Cyan
