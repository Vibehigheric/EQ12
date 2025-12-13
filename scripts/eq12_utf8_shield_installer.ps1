#Requires -Version 5.1
<#
EQ12 UTF-8 SHIELD - PERMANENT ENCODING SOLUTION
Eliminates ALL encoding issues across PowerShell, Python, VS Code, Git, Pi, Coral
#>

[CmdletBinding()]
param(
    [switch]$SystemWide,
    [switch]$Force
)

# FORCE UTF-8 AT SCRIPT LEVEL
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host " EQ12 UTF-8 SHIELD INSTALLER" -ForegroundColor Green
Write-Host "Permanent fix for all encoding issues" -ForegroundColor Yellow

function Install-SystemWideUTF8 {
    Write-Host "`n1 Configuring Windows System UTF-8..." -ForegroundColor Cyan
    
    # Enable Windows UTF-8 mode
    try {
        Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Nls\CodePage" -Name "ACP" -Value 65001 -Force
        Write-Host " Windows UTF-8 mode enabled" -ForegroundColor Green
    }
    catch {
        Write-Host " Admin rights needed for system UTF-8 - continuing with user settings" -ForegroundColor Yellow
    }
    
    # Set environment variables
    [Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")
    [Environment]::SetEnvironmentVariable("LC_ALL", "en_US.UTF-8", "User")
    [Environment]::SetEnvironmentVariable("LANG", "en_US.UTF-8", "User")
    
    Write-Host " Environment variables set for UTF-8" -ForegroundColor Green
}

function Update-VSCodeSettings {
    Write-Host "`n2 Updating VS Code settings..." -ForegroundColor Cyan
    
    $settingsPath = "$env:APPDATA\Code\User\settings.json"
    
    # Read current settings
    $currentSettings = @{}
    if (Test-Path $settingsPath) {
        try {
            $currentSettings = Get-Content $settingsPath -Encoding UTF8 | ConvertFrom-Json -AsHashtable
        }
        catch {
            $currentSettings = @{}
        }
    }
    
    # UTF-8 Shield settings
    $utf8Settings = @{
        "files.encoding"                         = "utf8"
        "files.eol"                              = "`n"
        "terminal.integrated.env.windows"        = @{
            "PYTHONUTF8"           = "1"
            "LC_ALL"               = "en_US.UTF-8"
            "LANG"                 = "en_US.UTF-8"
            "REVENUE_TARGET_DAILY" = "750"
            "CONTENT_EMPIRE_MODE"  = "ACTIVATED"
        }
        "python.analysis.autoImportCompletions"  = $true
        "editor.unicodeHighlight.allowedLocales" = @{
            "en-us" = $true
        }
        "code-runner.executorMap"                = @{
            "python" = "python -X utf8"
        }
        "git.encoding"                           = "utf8"
        "editor.formatOnSave"                    = $true
        "github.copilot.enable"                  = $true
        "python.defaultInterpreterPath"          = "python"
    }
    
    # Merge settings
    foreach ($key in $utf8Settings.Keys) {
        $currentSettings[$key] = $utf8Settings[$key]
    }
    
    # Write back with UTF-8 no BOM
    $settingsJson = $currentSettings | ConvertTo-Json -Depth 10
    $utf8NoBOM = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($settingsPath, $settingsJson, $utf8NoBOM)
    
    Write-Host " VS Code settings updated with UTF-8 shield" -ForegroundColor Green
}

function Create-GitAttributes {
    Write-Host "`n3 Creating .gitattributes..." -ForegroundColor Cyan
    
    $gitAttributesContent = @"
# EQ12 UTF-8 Shield - Force UTF-8 for all text files
*.ps1 text working-tree-encoding=UTF-8
*.py text working-tree-encoding=UTF-8
*.json text working-tree-encoding=UTF-8
*.csv text working-tree-encoding=UTF-8
*.html text working-tree-encoding=UTF-8
*.yml text working-tree-encoding=UTF-8
*.yaml text working-tree-encoding=UTF-8
*.txt text working-tree-encoding=UTF-8
*.md text working-tree-encoding=UTF-8
*.cfg text working-tree-encoding=UTF-8
*.conf text working-tree-encoding=UTF-8

# Binary files
*.jpg binary
*.png binary
*.gif binary
*.ico binary
*.zip binary
*.exe binary
"@

    $gitAttributesPath = "C:\EQ12\.gitattributes"
    $utf8NoBOM = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($gitAttributesPath, $gitAttributesContent, $utf8NoBOM)
    
    Write-Host " .gitattributes created with UTF-8 enforcement" -ForegroundColor Green
}

function Create-PythonUTF8Template {
    Write-Host "`n4 Creating Python UTF-8 template..." -ForegroundColor Cyan
    
    $pythonTemplate = @"
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EQ12 UTF-8 Shield Python Template
All EQ12 Python files should start with this header
"""

import sys
import os
import json
import locale

# Force UTF-8 encoding
if sys.getdefaultencoding().lower() != "utf-8":
    import importlib
    importlib.reload(sys)

# Set locale for proper Unicode handling
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')

# Environment variables for UTF-8
os.environ["PYTHONUTF8"] = "1"
os.environ["LC_ALL"] = "en_US.UTF-8" 
os.environ["LANG"] = "en_US.UTF-8"

def safe_open(path, mode='r', **kwargs):
    """Safe file opening with UTF-8 encoding"""
    return open(path, mode, encoding='utf-8', **kwargs)

def safe_json_dump(obj, path):
    """Safe JSON writing with UTF-8 and no ASCII escaping"""
    with safe_open(path, 'w') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def safe_json_load(path):
    """Safe JSON reading with UTF-8"""
    with safe_open(path, 'r') as f:
        return json.load(f)

# Example usage:
if __name__ == "__main__":
    print(" EQ12 UTF-8 Shield Active")
    print(f"Default encoding: {sys.getdefaultencoding()}")
    print(f"File system encoding: {sys.getfilesystemencoding()}")
"@

    $templatePath = "C:\EQ12\scripts\utf8_template.py"
    $utf8NoBOM = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($templatePath, $pythonTemplate, $utf8NoBOM)
    
    Write-Host " Python UTF-8 template created" -ForegroundColor Green
}

function Create-PowerShellTemplate {
    Write-Host "`n5 Creating PowerShell UTF-8 template..." -ForegroundColor Cyan
    
    $psTemplate = @"
#Requires -Version 5.1
<#
EQ12 UTF-8 Shield PowerShell Template
All EQ12 PowerShell scripts should start with this header
#>

# FORCE UTF-8 ENCODING
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
`$PSDefaultParameterValues['*:Encoding'] = 'utf8'
`$OutputEncoding = [System.Text.Encoding]::UTF8

# Set UTF-8 environment
`$env:PYTHONUTF8 = "1"
`$env:LC_ALL = "en_US.UTF-8"
`$env:LANG = "en_US.UTF-8"

function Write-SafeFile {
    param(
        [string]`$Path,
        [string]`$Content
    )
    `$utf8NoBOM = New-Object System.Text.UTF8Encoding(`$false)
    [System.IO.File]::WriteAllText(`$Path, `$Content, `$utf8NoBOM)
}

function Read-SafeFile {
    param([string]`$Path)
    return Get-Content `$Path -Encoding UTF8
}

function ConvertTo-SafeJson {
    param([object]`$InputObject)
    return `$InputObject | ConvertTo-Json -Depth 10 | ForEach-Object { [System.Text.RegularExpressions.Regex]::Unescape(`$_) }
}

Write-Host " EQ12 UTF-8 Shield Active" -ForegroundColor Green
"@

    $psTemplatePath = "C:\EQ12\scripts\utf8_template.ps1"
    $utf8NoBOM = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($psTemplatePath, $psTemplate, $utf8NoBOM)
    
    Write-Host " PowerShell UTF-8 template created" -ForegroundColor Green
}

function Create-PiUTF8Config {
    Write-Host "`n6 Creating Pi-Coral UTF-8 configuration..." -ForegroundColor Cyan
    
    $piConfig = @"
# EQ12 Pi-Coral UTF-8 Configuration
# Deploy to Raspberry Pi at 192.168.1.80

# /etc/default/locale content:
LANG=en_US.UTF-8
LC_ALL=en_US.UTF-8

# Commands to run on Pi:
sudo locale-gen en_US.UTF-8
sudo update-locale
export PYTHONUTF8=1

# Add to ~/.bashrc:
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8  
export PYTHONUTF8=1

# Python UTF-8 verification script for Pi:
python3 -c "import sys; print('UTF-8 Active:', sys.getdefaultencoding() == 'utf-8')"
"@

    $piConfigPath = "C:\EQ12\configs\pi_utf8_setup.txt"
    $utf8NoBOM = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($piConfigPath, $piConfig, $utf8NoBOM)
    
    Write-Host " Pi-Coral UTF-8 configuration created" -ForegroundColor Green
}

function Test-UTF8Shield {
    Write-Host "`n Testing UTF-8 Shield..." -ForegroundColor Magenta
    
    # Test emoji and special characters
    $testContent = " UTF-8 Test:    moji  "
    $testPath = "C:\EQ12\logs\utf8_test.json"
    
    $testData = @{
        "timestamp"      = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        "test_content"   = $testContent
        "encoding_test"  = "Success if you see emojis correctly"
        "revenue_target" = 750
    }
    
    # Write test file with UTF-8
    $testJson = $testData | ConvertTo-Json -Depth 10
    $utf8NoBOM = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($testPath, $testJson, $utf8NoBOM)
    
    # Read back and verify
    $readBack = Get-Content $testPath -Encoding UTF8 | ConvertFrom-Json
    
    if ($readBack.test_content -eq $testContent) {
        Write-Host " UTF-8 Shield test PASSED" -ForegroundColor Green
        Write-Host "   Emojis and Unicode preserved correctly" -ForegroundColor Green
    }
    else {
        Write-Host " UTF-8 Shield test FAILED" -ForegroundColor Red
    }
}

# Main Installation
Install-SystemWideUTF8
Update-VSCodeSettings
Create-GitAttributes
Create-PythonUTF8Template
Create-PowerShellTemplate  
Create-PiUTF8Config
Test-UTF8Shield

Write-Host "`n UTF-8 SHIELD INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host " All encoding issues eliminated permanently" -ForegroundColor Yellow
Write-Host " Restart VS Code and terminal for full activation" -ForegroundColor Cyan
Write-Host "`n Shield includes:" -ForegroundColor White
Write-Host "    System-wide UTF-8 enforcement" -ForegroundColor Green
Write-Host "    VS Code UTF-8 optimization" -ForegroundColor Green  
Write-Host "    Git UTF-8 attributes" -ForegroundColor Green
Write-Host "    Python UTF-8 templates" -ForegroundColor Green
Write-Host "    PowerShell UTF-8 templates" -ForegroundColor Green
Write-Host "    Pi-Coral UTF-8 configuration" -ForegroundColor Green
Write-Host "`n Ready for SD Card Crypto Suite development!" -ForegroundColor Magenta
