#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Advanced VB Debugging System - PowerShell Wrapper (Clean Version)
    
.DESCRIPTION
    Hardcoded VB debugging best practices with automation
    - Option Strict/Explicit enforcement
    - Debug.WriteLine automation  
    - Unit testing integration
    - Macro-based debugging automation
    
.PARAMETER Action
    The debugging action to perform:
    - EnforceAll: Apply all VB debugging improvements
    - ProcessFile: Process specific VB file
    - CreateTest: Create unit test template
    - CreateMacro: Generate debugging macro
    - AnalyzeQuality: Analyze code quality
    
.PARAMETER File
    Specific VB file to process
    
.PARAMETER Function
    Function name for unit test creation
    
.PARAMETER Verbose
    Enable verbose output
    
.EXAMPLE
    .\eq12_vb_debugging_wrapper_clean.ps1 -Action CreateMacro
    
.NOTES
    Author: EQ12 Team with GitHub Copilot
    Purpose: Advanced VB debugging with hardcoded best practices
    Requires: Python 3.12+, .NET tools
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("EnforceAll", "ProcessFile", "CreateTest", "CreateMacro", "AnalyzeQuality")]
    [string]$Action,
    
    [Parameter(Mandatory = $false)]
    [string]$File = "",
    
    [Parameter(Mandatory = $false)]
    [string]$Function = "",
    
    [Parameter(Mandatory = $false)]
    [string]$Workspace = "C:\EQ12"
)

# EQ12 logging setup
$LogsDir = Join-Path $Workspace "logs"
if (-not (Test-Path $LogsDir)) {
    New-Item -Path $LogsDir -ItemType Directory -Force | Out-Null
}

$Timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd_HHmmss")
$LogFile = Join-Path $LogsDir "vb_debugging_wrapper_clean_$Timestamp.log"

function Write-EQ12Log {
    param(
        [string]$Message, 
        [string]$Level = "INFO"
    )
    
    $LogEntry = "$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss.fffZ') - $Level - $Message"
    $LogEntry | Out-File -FilePath $LogFile -Append -Encoding utf8
    
    switch ($Level) {
        "ERROR" { Write-Host "❌ $Message" -ForegroundColor Red }
        "WARNING" { Write-Host "⚠️ $Message" -ForegroundColor Yellow }  
        "SUCCESS" { Write-Host "✅ $Message" -ForegroundColor Green }
        default { Write-Host "ℹ️ $Message" -ForegroundColor Cyan }
    }
}

function Test-Prerequisites {
    Write-EQ12Log "🔍 Checking VB debugging prerequisites"
    
    $Prerequisites = @()
    
    # Check Python
    try {
        $PythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "Python found: $PythonVersion" "SUCCESS"
        } else {
            $Prerequisites += "Python 3.12+ required"
        }
    } catch {
        $Prerequisites += "Python not found in PATH"
    }
    
    # Check VB debugging script
    $VBDebugScript = Join-Path $Workspace "scripts\eq12_vb_debugging_system.py"
    if (-not (Test-Path $VBDebugScript)) {
        $Prerequisites += "VB debugging script not found: $VBDebugScript"
    } else {
        Write-EQ12Log "VB debugging script found" "SUCCESS"
    }
    
    if ($Prerequisites.Count -gt 0) {
        Write-EQ12Log "Missing prerequisites:" "ERROR"
        foreach ($Prereq in $Prerequisites) {
            Write-EQ12Log "  - $Prereq" "ERROR"
        }
        throw "Prerequisites not met"
    }
    
    Write-EQ12Log "All prerequisites satisfied" "SUCCESS"
}

function Invoke-VBDebugging {
    param([string[]]$Arguments)
    
    $VBDebugScript = Join-Path $Workspace "scripts\eq12_vb_debugging_system.py"
    
    Write-EQ12Log "🔧 Executing VB debugging with args: $($Arguments -join ' ')"
    
    try {
        $ProcessArgs = @("python", $VBDebugScript) + $Arguments
        $Result = & $ProcessArgs[0] $ProcessArgs[1..($ProcessArgs.Length-1)] 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "VB debugging completed successfully" "SUCCESS"
            Write-Output $Result
        } else {
            Write-EQ12Log "VB debugging failed with exit code: $LASTEXITCODE" "ERROR"
            Write-Error $Result
        }
    } catch {
        Write-EQ12Log "Exception during VB debugging: $_" "ERROR"
        throw
    }
}

function Show-VBDebuggingTips {
    Write-EQ12Log "💡 EQ12 Advanced VB Debugging Tips" "SUCCESS"
    
    $Tips = @(
        "🔒 Always use 'Option Strict On' and 'Option Explicit On' for type safety",
        "📝 Add Debug.WriteLine statements at function entry/exit for flow tracking",
        "🧪 Create isolated unit tests for complex functions", 
        "🤖 Use VBA macros to automate repetitive debugging tasks",
        "📊 Leverage variable watch expressions for runtime state monitoring",
        "⚡ Profile function performance with DateTime.Now measurements",
        "🔍 Combine Roslyn analyzers with custom debugging automation",
        "📋 Log all debugging sessions to structured JSON for analysis"
    )
    
    foreach ($Tip in $Tips) {
        Write-Host $Tip -ForegroundColor Cyan
    }
}

# Main execution
try {
    Write-EQ12Log "🚀 EQ12 Advanced VB Debugging System Starting"
    Write-EQ12Log "Action: $Action | Workspace: $Workspace"
    
    # Test prerequisites
    Test-Prerequisites
    
    # Execute based on action
    switch ($Action) {
        "EnforceAll" {
            Write-EQ12Log "🔧 Enforcing all VB debugging best practices"
            $Arguments = @("--workspace", $Workspace, "--enforce-all")
            if ($VerbosePreference -eq "Continue") { $Arguments += "--verbose" }
            Invoke-VBDebugging -Arguments $Arguments
        }
        
        "ProcessFile" {
            if ([string]::IsNullOrEmpty($File)) {
                throw "File parameter required for ProcessFile action"
            }
            Write-EQ12Log "📄 Processing VB file: $File"
            $Arguments = @("--workspace", $Workspace, "--file", $File)
            if ($VerbosePreference -eq "Continue") { $Arguments += "--verbose" }
            Invoke-VBDebugging -Arguments $Arguments
        }
        
        "CreateTest" {
            if ([string]::IsNullOrEmpty($Function)) {
                throw "Function parameter required for CreateTest action"
            }
            Write-EQ12Log "🧪 Creating unit test for function: $Function"
            $Arguments = @("--workspace", $Workspace, "--create-test", $Function)
            if ($VerbosePreference -eq "Continue") { $Arguments += "--verbose" }
            Invoke-VBDebugging -Arguments $Arguments
        }
        
        "CreateMacro" {
            Write-EQ12Log "🤖 Creating VB debugging automation macro"
            $Arguments = @("--workspace", $Workspace, "--create-macro")
            if ($VerbosePreference -eq "Continue") { $Arguments += "--verbose" }
            Invoke-VBDebugging -Arguments $Arguments
        }
        
        "AnalyzeQuality" {
            Write-EQ12Log "📊 Analyzing VB code quality"
            $Arguments = @("--workspace", $Workspace, "--analyze-quality")
            if ($VerbosePreference -eq "Continue") { $Arguments += "--verbose" }
            Invoke-VBDebugging -Arguments $Arguments
        }
        
        default {
            throw "Unknown action: $Action"
        }
    }
    
    # Show helpful tips
    Show-VBDebuggingTips
    
    Write-EQ12Log "🎉 EQ12 VB Debugging completed successfully!" "SUCCESS"
    Write-EQ12Log "📄 Full log available at: $LogFile"
    
} catch {
    Write-EQ12Log "❌ Fatal error in VB debugging: $_" "ERROR"
    exit 1
}