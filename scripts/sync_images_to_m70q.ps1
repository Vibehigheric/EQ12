<#
.SYNOPSIS
    Builds EQ12 GodStack images LOCALLY on Windows and syncs them to the M70q node.
.DESCRIPTION
    This script handles the full build pipeline:
    1. Sets up Docker Buildx environment (Local).
    2. Validates build context size.
    3. Builds multi-arch compatible images (targeting linux/amd64).
    4. Saves images to tarballs.
    5. Transfers images via SCP to M70q.
    6. Loads images on the remote node.
    
    NOTE: We are building LOCALLY because M70q currently lacks internet access to pull base images.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$TargetIP = "192.168.100.3"
$User = "ricoj100"

# --- 1. ENVIRONMENT SETUP ---
Write-Host "=== EQ12 GodStack Build Pipeline (Local Build -> Sync) ===" -ForegroundColor Cyan

# Force script to run from project root
$ProjectRoot = "$PSScriptRoot/.."
Set-Location -Path $ProjectRoot
Write-Host "Working Directory: $(Get-Location)" -ForegroundColor Gray

# Enable BuildKit
$env:DOCKER_BUILDKIT = "1"
$env:COMPOSE_DOCKER_CLI_BUILD = "1"

# --- 2. CONTEXT SIZE CHECK ---
Write-Host "Checking build context size..." -ForegroundColor Yellow
if (-not (Select-String -Path ".dockerignore" -Pattern "\.venv_wsl")) {
    Write-Warning ".dockerignore might be missing .venv_wsl exclusion!"
}

# --- 3. BUILDER SETUP ---
Write-Host "Setting up Docker Buildx..." -ForegroundColor Yellow
$BuilderName = "eq12-builder"
if (-not (docker buildx ls | Select-String $BuilderName)) {
    Write-Host "Creating builder: $BuilderName"
    docker buildx create --name $BuilderName --use --driver docker-container --bootstrap
}
else {
    Write-Host "Using builder: $BuilderName"
    docker buildx use $BuilderName
}

# --- 4. BUILD PROCESS ---
Write-Host "Building eq12/core:latest (AMD64)..." -ForegroundColor Cyan

# Build command using DOT (.) context
# --load imports to local docker daemon for 'docker save'
docker buildx build `
    --builder $BuilderName `
    --platform linux/amd64 `
    --progress plain `
    -t eq12/core:latest `
    --load `
    -f Dockerfile `
    .

if ($LASTEXITCODE -ne 0) { Write-Error "Build failed"; exit 1 }
Write-Host "Build complete." -ForegroundColor Green

# --- 5. TAGGING ---
$Eq12Images = @(
    "eq12/parlay-engine:latest",
    "eq12/risk-engine:latest",
    "eq12/prop-tensor:latest",
    "eq12/scraper:latest",
    "eq12/dashboard:latest"
)

foreach ($Img in $Eq12Images) {
    Write-Host "Tagging $Img..." -ForegroundColor Gray
    docker tag eq12/core:latest $Img
}

# --- 6. SAVE & TRANSFER ---
$ImagesToSync = @("eq12/core:latest") + $Eq12Images
$TarFile = "eq12_images.tar"

Write-Host "Saving images to $TarFile..." -ForegroundColor Yellow
docker save -o $TarFile $ImagesToSync

Write-Host "Transferring to M70q ($TargetIP)..." -ForegroundColor Cyan
scp $TarFile ${User}@${TargetIP}:/home/${User}/

Write-Host "Loading images on M70q..." -ForegroundColor Cyan
ssh ${User}@${TargetIP} "docker load -i /home/${User}/$TarFile && rm /home/${User}/$TarFile"

Write-Host "=== SYNC COMPLETE ===" -ForegroundColor Green
