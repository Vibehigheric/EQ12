#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Visual Studio Code Troubleshooter - Professional-Level Diagnostics
    
.DESCRIPTION
    VS Code troubleshooting script that automatically diagnoses and fixes common issues
    
.PARAMETER Action
    Troubleshooting action: Quick, Clean, Dependencies, Test, Full
    
.EXAMPLE
    .\eq12_vscode_troubleshooter_simple.ps1 -Action Quick
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('Quick', 'Clean', 'Dependencies', 'Test', 'Full')]
    [string]$Action = 'Quick',
    
    [Parameter(Mandatory = $false)]
    [string]$Workspace = $PWD.Path
)

# Initialize logging
$LogDir = "C:\EQ12\logs"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = "$LogDir\vscode_troubleshooter_$Timestamp.log"

if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-EQ12Log {
    param([string]$Level, [string]$Message)
    
    $LogEntry = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
        level = $Level
        message = $Message
        workspace = $Workspace
        action = $Action
    } | ConvertTo-Json -Compress
    
    Add-Content -Path $LogFile -Value $LogEntry
    
    $Color = switch ($Level) {
        'ERROR' { 'Red' }
        'WARN' { 'Yellow' }
        'SUCCESS' { 'Green' }
        default { 'Cyan' }
    }
    
    Write-Host "[$Level] $Message" -ForegroundColor $Color
}

function Test-Prerequisites {
    Write-EQ12Log "INFO" "Checking VS Code prerequisites..."
    
    $issues = @()
    
    # Check VS Code
    $vscode = Get-Command "code" -ErrorAction SilentlyContinue
    if ($vscode) {
        Write-EQ12Log "SUCCESS" "VS Code CLI available"
    } else {
        $issues += "VS Code CLI not in PATH"
        Write-EQ12Log "ERROR" "VS Code CLI not found"
    }
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            Write-EQ12Log "SUCCESS" "Node.js version: $nodeVersion"
        } else {
            $issues += "Node.js not available"
        }
    } catch {
        $issues += "Node.js not installed"
    }
    
    return $issues
}

function Clear-VSCodeCache {
    Write-EQ12Log "INFO" "Clearing VS Code cache..."
    
    $cacheLocations = @(
        "$env:APPDATA\Code\User\workspaceStorage",
        "$env:APPDATA\Code\logs",
        "$Workspace\.vscode"
    )
    
    $cleared = @()
    
    foreach ($location in $cacheLocations) {
        if (Test-Path $location) {
            try {
                Remove-Item -Path "$location\*" -Recurse -Force -ErrorAction SilentlyContinue
                $cleared += $location
                Write-EQ12Log "SUCCESS" "Cleared: $location"
            } catch {
                Write-EQ12Log "WARN" "Could not clear: $location"
            }
        }
    }
    
    return $cleared
}

function Repair-Dependencies {
    Write-EQ12Log "INFO" "Repairing project dependencies..."
    
    Push-Location $Workspace
    $repairs = @()
    
    try {
        # Node.js projects
        if (Test-Path "package.json") {
            Write-EQ12Log "INFO" "Found Node.js project, repairing dependencies..."
            
            if (Test-Path "node_modules") {
                Remove-Item "node_modules" -Recurse -Force
                $repairs += "Removed node_modules"
            }
            
            npm install 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-EQ12Log "SUCCESS" "npm install completed"
                $repairs += "Fresh npm install"
            }
        }
        
    } finally {
        Pop-Location
    }
    
    return $repairs
}

function Run-ProjectTests {
    Write-EQ12Log "INFO" "Running project tests..."
    
    Push-Location $Workspace
    $results = @()
    
    try {
        if (Test-Path "package.json") {
            npm test 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $results += "npm test: PASSED"
            } else {
                $results += "npm test: FAILED"
            }
        }
    } finally {
        Pop-Location
    }
    
    return $results
}

# Main execution
Write-EQ12Log "INFO" "EQ12 VS Code Troubleshooter starting..."
Write-EQ12Log "INFO" "Action: $Action | Workspace: $Workspace"

$allIssues = @()
$allRepairs = @()
$testResults = @()

switch ($Action) {
    'Quick' {
        Write-EQ12Log "INFO" "Running quick diagnostic..."
        $allIssues += Test-Prerequisites
    }
    
    'Clean' {
        Write-EQ12Log "INFO" "Deep cleaning VS Code..."
        $cleared = Clear-VSCodeCache
        $allRepairs += $cleared
    }
    
    'Dependencies' {
        Write-EQ12Log "INFO" "Repairing dependencies..."
        $repairs = Repair-Dependencies
        $allRepairs += $repairs
    }
    
    'Test' {
        $testResults = Run-ProjectTests
    }
    
    'Full' {
        Write-EQ12Log "INFO" "Running complete troubleshooting cycle..."
        $allIssues += Test-Prerequisites
        $cleared = Clear-VSCodeCache
        $allRepairs += $cleared
        $repairs = Repair-Dependencies
        $allRepairs += $repairs
        $testResults = Run-ProjectTests
    }
}

# Summary
$criticalIssues = $allIssues | Where-Object { $_ -like "*not found*" -or $_ -like "*failed*" }

if ($criticalIssues) {
    Write-EQ12Log "WARN" "$($criticalIssues.Count) critical issues found"
} else {
    Write-EQ12Log "SUCCESS" "No critical issues detected"
}

Write-EQ12Log "INFO" "Applied $($allRepairs.Count) repairs"
Write-EQ12Log "INFO" "Logs saved to: $LogFile"

if ($criticalIssues.Count -eq 0) { 
    Write-EQ12Log "SUCCESS" "Troubleshooting completed successfully!"
    exit 0 
} else { 
    exit 1 
}