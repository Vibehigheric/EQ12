#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Update Visual Studio Code to the latest version
.DESCRIPTION
    Downloads and installs the latest VS Code version with proper handling
#>

[CmdletBinding()]
param()

Write-Host " Updating Visual Studio Code..." -ForegroundColor Cyan

try {
    # Method 1: Try winget first
    Write-Host "Attempting winget update..." -ForegroundColor Yellow
    $result = winget upgrade Microsoft.VisualStudioCode --accept-source-agreements --accept-package-agreements --silent
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " VS Code updated successfully via winget!" -ForegroundColor Green
        return
    }
    
    # Method 2: Direct download approach
    Write-Host "Winget failed, trying direct download..." -ForegroundColor Yellow
    
    $downloadUrl = "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user"
    $installerPath = "$env:TEMP\VSCodeUserSetup-x64.exe"
    
    Write-Host "Downloading VS Code installer..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
    
    Write-Host "Installing VS Code..." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -ArgumentList "/VERYSILENT", "/MERGETASKS=!runcode" -Wait
    
    # Clean up
    Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
    
    Write-Host " VS Code updated successfully!" -ForegroundColor Green
    
    # Verify installation
    $newVersion = & code --version 2>$null | Select-Object -First 1
    Write-Host "New VS Code version: $newVersion" -ForegroundColor Green
    
}
catch {
    Write-Error " Failed to update VS Code: $_"
    Write-Host "Please try updating manually from: https://code.visualstudio.com/Download" -ForegroundColor Red
}