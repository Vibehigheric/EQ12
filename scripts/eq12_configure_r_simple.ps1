#!/usr/bin/env pwsh
<#
.SYNOPSIS
    EQ12 R Path Detection and Configuration
    
.DESCRIPTION
    Automatically detects R installation and updates VS Code settings.
    Fixes "Cannot find R to use for help" error.
    
.EXAMPLE
    .\scripts\eq12_configure_r_simple.ps1
#>

[CmdletBinding()]
param(
    [switch]$Force
)

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "INFO" { "Green" }
        "WARN" { "Yellow" }  
        "ERROR" { "Red" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

try {
    Write-EQ12Log "EQ12 R Configuration Starting..."
    
    # Common R installation paths
    $rPaths = @(
        "${env:ProgramFiles}\R\*\bin\R.exe",
        "${env:ProgramFiles(x86)}\R\*\bin\R.exe", 
        "$env:LOCALAPPDATA\Programs\R\*\bin\R.exe"
    )
    
    $foundR = $null
    
    foreach ($pattern in $rPaths) {
        $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | 
                 Sort-Object Name -Descending | 
                 Select-Object -First 1
                 
        if ($found) {
            Write-EQ12Log "Found R installation: $($found.FullName)"
            
            # Test if R works
            try {
                $version = & "$($found.FullName)" --version 2>$null | Select-Object -First 1
                if ($version -match "R version") {
                    $foundR = $found.FullName
                    Write-EQ12Log "Valid R installation: $version"
                    break
                }
            }
            catch {
                Write-EQ12Log "R test failed: $_" -Level "WARN"
            }
        }
    }
    
    if (-not $foundR) {
        Write-EQ12Log "No R installation found!" -Level "ERROR"
        Write-EQ12Log "Install R from: https://cran.r-project.org/bin/windows/base/" -Level "INFO"
        exit 1
    }
    
    # Update VS Code settings
    $settingsPath = ".vscode\settings.json"
    
    if (-not (Test-Path $settingsPath)) {
        Write-EQ12Log "VS Code settings.json not found: $settingsPath" -Level "ERROR"
        exit 1
    }
    
    # Read and update settings
    $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
    
    # Calculate paths
    $rExe = $foundR
    $rDir = Split-Path $rExe -Parent
    $rTerm = Join-Path $rDir "x64\Rterm.exe"
    
    if (-not (Test-Path $rTerm)) {
        $rTerm = Join-Path $rDir "Rterm.exe"
    }
    
    # Escape paths for JSON
    $rExeEscaped = $rExe -replace "\\", "\\"
    $rTermEscaped = $rTerm -replace "\\", "\\"
    
    # Update R settings
    $settings | Add-Member -NotePropertyName "r.rpath.windows" -NotePropertyValue $rExeEscaped -Force
    $settings | Add-Member -NotePropertyName "r.rterm.windows" -NotePropertyValue $rTermEscaped -Force
    
    # Write back to file
    $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding UTF8
    
    Write-EQ12Log "Updated R configuration in VS Code settings"
    Write-EQ12Log "R executable: $rExe"
    Write-EQ12Log "R terminal: $rTerm"
    Write-EQ12Log "Configuration complete! Restart VS Code to apply."
}
catch {
    Write-EQ12Log "Configuration failed: $_" -Level "ERROR"
    exit 1
}