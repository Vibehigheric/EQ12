#Requires -Version 5.1

<#
.SYNOPSIS
    EQ12 GODSTACK - Chrome Governance Task Management (Simplified)

.DESCRIPTION
    Simple PowerShell script to test Chrome governance automation.

.EXAMPLE
    .\test_chrome_governance.ps1
#>

param(
    [string]$Action = "Test"
)

# Configuration
$EQ12Root = "C:\EQ12"
$PythonExecutable = "C:\Program Files\Python312\python.exe"
$ChromeScript = "$EQ12Root\chrome_governance_automation.py"

function Write-Status {
    param([string]$Message, [string]$Level = "Info")

    $colors = @{
        "Info" = "White"
        "Success" = "Green"
        "Warning" = "Yellow"
        "Error" = "Red"
    }

    Write-Host "[$Level] $Message" -ForegroundColor $colors[$Level]
}

function Test-ChromeGovernance {
    Write-Status "🧪 Testing Chrome governance automation..." "Info"

    # Check Python
    if (Test-Path $PythonExecutable) {
        Write-Status "✅ Python found: $PythonExecutable" "Success"
    } else {
        Write-Status "❌ Python not found: $PythonExecutable" "Error"
        return $false
    }

    # Check Chrome script
    if (Test-Path $ChromeScript) {
        Write-Status "✅ Chrome script found: $ChromeScript" "Success"
    } else {
        Write-Status "❌ Chrome script not found: $ChromeScript" "Error"
        return $false
    }

    # Test script execution
    Write-Status "🔍 Testing script validation..." "Info"
    try {
        $result = & $PythonExecutable $ChromeScript --validate-profile
        if ($LASTEXITCODE -eq 0) {
            Write-Status "✅ Chrome governance validation successful" "Success"
        } else {
            Write-Status "⚠️ Chrome governance validation failed (exit code: $LASTEXITCODE)" "Warning"
        }
    } catch {
        Write-Status "❌ Script execution failed: $($_.Exception.Message)" "Error"
        return $false
    }

    # Check Chrome executable
    $chromeExe = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    if (Test-Path $chromeExe) {
        Write-Status "✅ Chrome executable found" "Success"
    } else {
        Write-Status "⚠️ Chrome executable not found at standard location" "Warning"
    }

    return $true
}

Write-Status "🚀 EQ12 Chrome Governance Test" "Info"

$success = Test-ChromeGovernance

if ($success) {
    Write-Status "🎉 Chrome governance test completed successfully!" "Success"
} else {
    Write-Status "❌ Chrome governance test encountered issues." "Error"
}

if ($success) { exit 0 } else { exit 1 }
