<#
.SYNOPSIS
    Installs or updates Docker Buildx on Windows.
.DESCRIPTION
    Downloads the latest Docker Buildx binary and installs it into the Docker CLI plugins directory.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host "=== Setting up Docker Buildx for Windows ===" -ForegroundColor Cyan

# Define paths
$DockerConfigDir = "$env:USERPROFILE\.docker"
$CliPluginsDir = "$DockerConfigDir\cli-plugins"
$BuildxExe = "$CliPluginsDir\docker-buildx.exe"

# Create directory if it doesn't exist
if (-not (Test-Path $CliPluginsDir)) {
    Write-Host "Creating CLI plugins directory: $CliPluginsDir"
    New-Item -ItemType Directory -Path $CliPluginsDir -Force | Out-Null
}

# Check current version
if (Test-Path $BuildxExe) {
    Write-Host "Buildx binary found at $BuildxExe"
    try {
        $CurrentVersion = & $BuildxExe version
        Write-Host "Current version: $CurrentVersion"
    }
    catch {
        Write-Warning "Existing binary might be corrupted."
    }
}
else {
    Write-Host "Buildx binary not found."
}

# Download URL (latest release as of late 2024/early 2025 - adjust version if needed)
# Using v0.12.1 as a safe baseline, or we could query GitHub API. 
# For stability, let's use a known good version.
$BuildxVersion = "v0.12.1" 
$DownloadUrl = "https://github.com/docker/buildx/releases/download/$BuildxVersion/buildx-$BuildxVersion.windows-amd64.exe"

Write-Host "Downloading Buildx $BuildxVersion from GitHub..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $BuildxExe -UseBasicParsing
    Write-Host "Download complete." -ForegroundColor Green
}
catch {
    Write-Error "Failed to download Buildx: $_"
}

# Verify
if (Test-Path $BuildxExe) {
    Write-Host "Verifying installation..."
    & $BuildxExe version
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Buildx installed successfully!" -ForegroundColor Green
        Write-Host "You may need to restart your terminal or Docker Desktop."
    }
    else {
        Write-Error "Buildx binary is present but failed to run."
    }
}
