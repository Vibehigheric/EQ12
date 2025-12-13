#!/usr/bin/env pwsh
<#
.SYNOPSIS
    EQ12 R Path Detection and Configuration
    
.DESCRIPTION
    Automatically detects R installation and updates VS Code settings.
    Fixes "Cannot find R to use for help" error.
    
.EXAMPLE
    .\scripts\eq12_configure_r.ps1
    
.NOTES
    SPDX-License-Identifier: MIT
    SPDX-FileCopyrightText: 2025 EQ12 Project Contributors
#>

[CmdletBinding()]
param(
    [switch]$Force,
    [string]$CustomPath
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

function Find-RInstallation {
    [CmdletBinding()]
    param()
    
    Write-EQ12Log "Searching for R installations..."
    
    $commonPaths = @(
        "${env:ProgramFiles}\R\*\bin\R.exe",
        "${env:ProgramFiles(x86)}\R\*\bin\R.exe", 
        "$env:LOCALAPPDATA\Programs\R\*\bin\R.exe",
        "C:\R\*\bin\R.exe"
    )
    
    $rPaths = @()
    
    foreach ($pattern in $commonPaths) {
        try {
            $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | 
                     Sort-Object Name -Descending |
                     Select-Object -First 1
                     
            if ($found) {
                $rPaths += $found.FullName
            }
        }
        catch {
            # Ignore errors, continue searching
        }
    }
    
    # Also check PATH
    try {
        $pathR = Get-Command R.exe -ErrorAction SilentlyContinue
        if ($pathR) {
            $rPaths += $pathR.Source
        }
    }
    catch {
        # Ignore
    }
    
    # Test each installation
    $validInstallations = @()
    
    foreach ($rPath in $rPaths) {
        try {
            $version = & "$rPath" --version 2>$null | Select-Object -First 1
            if ($version -and $version -match "R version") {
                $validInstallations += @{
                    Path = $rPath
                    Version = $version.Trim()
                    Directory = Split-Path $rPath -Parent
                }
                Write-EQ12Log "✅ Found R: $rPath - $version"
            }
        }
        catch {
            Write-EQ12Log "❌ Invalid R installation: $rPath" -Level "WARN"
        }
    }
    
    return $validInstallations
}

function Update-VSCodeSettings {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [hashtable]$RInstallation
    )
    
    $settingsPath = ".vscode\settings.json"
    
    if (-not (Test-Path $settingsPath)) {
        Write-EQ12Log "❌ VS Code settings.json not found: $settingsPath" -Level "ERROR"
        return $false
    }
    
    try {
        Write-EQ12Log "📝 Updating VS Code settings..."
        
        # Read current settings
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
        
        # Update R paths
        $rExe = $RInstallation.Path
        $rTerm = Join-Path (Split-Path $rExe -Parent) "x64\Rterm.exe"
        
        # Handle both x64 and i386 architectures
        if (-not (Test-Path $rTerm)) {
            $rTerm = Join-Path (Split-Path $rExe -Parent) "Rterm.exe"
        }
        
        # Escape backslashes for JSON
        $rExeEscaped = $rExe -replace "\\", "\\"
        $rTermEscaped = $rTerm -replace "\\", "\\"
        
        # Update settings
        $settings | Add-Member -NotePropertyName "r.rpath.windows" -NotePropertyValue $rExeEscaped -Force
        $settings | Add-Member -NotePropertyName "r.rterm.windows" -NotePropertyValue $rTermEscaped -Force
        $settings | Add-Member -NotePropertyName "r.source.encoding" -NotePropertyValue "UTF-8" -Force
        $settings | Add-Member -NotePropertyName "r.source.focus" -NotePropertyValue "editor" -Force
        
        # Write back to file
        $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Encoding UTF8
        
        Write-EQ12Log "✅ Updated R configuration in VS Code settings"
        Write-EQ12Log "   R executable: $rExe"
        Write-EQ12Log "   R terminal: $rTerm"
        
        return $true
    }
    catch {
        Write-EQ12Log "❌ Failed to update VS Code settings: $_" -Level "ERROR"
        return $false
    }
}

function Test-RIntegration {
    [CmdletBinding()]
    param([string]$RPath)
    
    Write-EQ12Log "🧪 Testing R integration..."
    
    try {
        # Test basic R functionality
        $testScript = 'cat("R integration test successful\\n"); cat("Version:", R.version.string, "\\n")'
        $result = & "$RPath" --slave -e $testScript 2>$null
        
        if ($result -match "R integration test successful") {
            Write-EQ12Log "✅ R integration test passed"
            Write-EQ12Log "   Output: $($result -join ' ')"
            return $true
        }
        else {
            Write-EQ12Log "❌ R integration test failed" -Level "WARN"
            return $false
        }
    }
    catch {
        Write-EQ12Log "❌ R integration test error: $_" -Level "ERROR"
        return $false
    }
}

# Main execution
try {
    Write-EQ12Log "🚀 EQ12 R Configuration Starting..."
    
    # Handle custom path
    if ($CustomPath) {
        if (Test-Path $CustomPath) {
            Write-EQ12Log "📍 Using custom R path: $CustomPath"
            $rInstallation = @{
                Path = $CustomPath
                Version = "Custom Installation"
                Directory = Split-Path $CustomPath -Parent
            }
            $rInstallations = @($rInstallation)
        }
        else {
            Write-EQ12Log "❌ Custom R path not found: $CustomPath" -Level "ERROR"
            exit 1
        }
    }
    else {
        # Find R installations
        $rInstallations = Find-RInstallation
        
        if ($rInstallations.Count -eq 0) {
            Write-EQ12Log "❌ No R installations found!" -Level "ERROR"
            Write-EQ12Log "💡 Install R from: https://cran.r-project.org/bin/windows/base/"
            exit 1
        }
    }
    
    # Use the first (latest) installation
    $selectedR = $rInstallations[0]
    Write-EQ12Log "🎯 Selected R installation: $($selectedR.Path)"
    Write-EQ12Log "   Version: $($selectedR.Version)"
    
    # Test R before updating settings
    if (-not $Force) {
        $testResult = Test-RIntegration -RPath $selectedR.Path
        if (-not $testResult) {
            Write-EQ12Log "❌ R failed integration test. Use -Force to override." -Level "ERROR"
            exit 1
        }
    }
    
    # Update VS Code settings
    $updateResult = Update-VSCodeSettings -RInstallation $selectedR
    
    if ($updateResult) {
        Write-EQ12Log "✅ EQ12 R configuration complete!"
        Write-EQ12Log "💡 Restart VS Code to apply settings"
        Write-EQ12Log "📖 Test with: Ctrl+Shift+P → 'R: Create R Terminal'"
    }
    else {
        Write-EQ12Log "❌ Failed to update VS Code configuration" -Level "ERROR"
        exit 1
    }
}
catch {
    Write-EQ12Log "Configuration failed: $_" -Level "ERROR"
    Write-EQ12Log "Stack trace: $($_.ScriptStackTrace)" -Level "ERROR"
    exit 1
}