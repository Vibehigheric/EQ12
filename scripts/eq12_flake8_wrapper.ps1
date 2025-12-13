# EQ12 Flake8 Auto-Fix PowerShell Wrapper
# Purpose: Comprehensive PowerShell integration for Flake8 Python automation system
# Agent: GitHub Copilot with EQ12 expertise
# Timestamp: 2025-01-03T19:30:00Z

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('Analyze', 'FixE02', 'FixF84', 'FixAll', 'GeneratePrompts')]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$Workspace = "C:\EQ12",
    
    [Parameter(Mandatory=$false)]
    [string[]]$Categories = @(),
    
    [Parameter(Mandatory=$false)]
    [switch]$GenerateReport,
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput
)

# Initialize EQ12 environment
$ErrorActionPreference = "Stop"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogDir = "$Workspace\logs"
$LogFile = "$LogDir\flake8_wrapper_$Timestamp.log"

# Ensure logs directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -Path $LogDir -ItemType Directory -Force | Out-Null
}

# EQ12 Logging Function
function Write-EQ12Log {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Level,
        
        [Parameter(Mandatory=$true)]
        [string]$Message
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
    $logEntry = @{
        timestamp = $timestamp
        level = $Level
        message = $Message
        component = "EQ12-Flake8-Wrapper"
        workspace = $Workspace
    }
    
    # Console output with color coding
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "INFO" { "White" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        "CRITICAL" { "Magenta" }
        default { "Gray" }
    }
    
    Write-Host "[$timestamp] $Level`: $Message" -ForegroundColor $color
    
    # Append to log file
    $logEntry | ConvertTo-Json -Compress | Add-Content -Path $LogFile
}

# Test Python Environment
function Test-PythonEnvironment {
    Write-EQ12Log "INFO" "Validating Python environment..."
    
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "SUCCESS" "Python found: $pythonVersion"
            return $true
        } else {
            Write-EQ12Log "ERROR" "Python validation failed"
            return $false
        }
    } catch {
        Write-EQ12Log "ERROR" "Python not found in PATH"
        return $false
    }
}

# Main Flake8 Auto-Fix Execution
function Invoke-Flake8AutoFix {
    param([string]$PythonAction, [string[]]$ErrorCategories = @())
    
    Write-EQ12Log "INFO" "Starting Flake8 auto-fix process..."
    
    # Build command arguments
    $pythonScript = "$Workspace\scripts\eq12_flake8_autofix.py"
    $args = @(
        $pythonScript,
        "--workspace", $Workspace,
        "--action", $PythonAction
    )
    
    if ($ErrorCategories.Count -gt 0) {
        $args += "--categories"
        $args += $ErrorCategories
    }
    
    if ($VerboseOutput) {
        $args += "--verbose"
    }
    
    try {
        Write-EQ12Log "INFO" "Executing: python $($args -join ' ')"
        
        $result = Start-Process -FilePath "python" -ArgumentList $args -NoNewWindow -Wait -PassThru -RedirectStandardOutput "$LogDir\flake8_output.log" -RedirectStandardError "$LogDir\flake8_error.log"
        
        if ($result.ExitCode -eq 0) {
            Write-EQ12Log "SUCCESS" "Flake8 auto-fix completed successfully"
            
            # Display output if available
            if (Test-Path "$LogDir\flake8_output.log") {
                $output = Get-Content "$LogDir\flake8_output.log" | Where-Object { $_ -ne "" }
                if ($output) {
                    Write-EQ12Log "INFO" "Results:"
                    $output | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
                }
            }
        } else {
            Write-EQ12Log "ERROR" "Flake8 auto-fix failed with exit code $($result.ExitCode)"
            
            # Display error if available
            if (Test-Path "$LogDir\flake8_error.log") {
                $errorOutput = Get-Content "$LogDir\flake8_error.log" | Where-Object { $_ -ne "" }
                if ($errorOutput) {
                    Write-EQ12Log "ERROR" "Error details:"
                    $errorOutput | ForEach-Object { Write-Host "   $_" -ForegroundColor Red }
                }
            }
        }
        
        return $result.ExitCode
        
    } catch {
        Write-EQ12Log "ERROR" "Failed to execute Flake8 auto-fix: $($_.Exception.Message)"
        return 1
    }
}

# Show Available Copilot Prompts
function Show-AvailablePrompts {
    Write-EQ12Log "INFO" "Displaying available Copilot prompts..."
    
    $promptsFile = "C:\EQ12\configs\flake8_copilot_prompts.json"
    
    if (Test-Path $promptsFile) {
        try {
            $prompts = Get-Content $promptsFile | ConvertFrom-Json
            
            Write-Host "`nAvailable Copilot Expert Prompts:" -ForegroundColor Cyan
            Write-Host "================================================" -ForegroundColor Cyan
            
            foreach ($promptName in $prompts.PSObject.Properties.Name) {
                $prompt = $prompts.$promptName
                Write-Host "`n$promptName" -ForegroundColor Yellow
                Write-Host "   Copy the following into GitHub Copilot Chat:" -ForegroundColor Gray
                Write-Host "`n$($prompt.Substring(0, [Math]::Min(200, $prompt.Length)))..." -ForegroundColor White
                Write-Host "`n   [Full prompt available in $promptsFile]" -ForegroundColor Gray
            }
            
        } catch {
            Write-EQ12Log "ERROR" "Failed to read prompts file: $($_.Exception.Message)"
        }
    } else {
        Write-EQ12Log "WARN" "Prompts file not found. Run with -Action GeneratePrompts first."
    }
}

# Main execution logic
Write-EQ12Log "INFO" "EQ12 Flake8 Auto-Fix Wrapper starting..."
Write-EQ12Log "INFO" "Action: $Action | Workspace: $Workspace"

try {
    # Check Python environment
    if (-not (Test-PythonEnvironment)) {
        Write-EQ12Log "ERROR" "Python environment check failed"
        exit 1
    }
    
    # Execute based on action
    $exitCode = 0
    
    switch ($Action) {
        'Analyze' {
            Write-EQ12Log "INFO" "Running Flake8 analysis only..."
            $exitCode = Invoke-Flake8AutoFix -PythonAction "analyze"
        }
        
        'FixE02' {
            Write-EQ12Log "INFO" "Fixing E02* spacing and indentation issues..."
            $exitCode = Invoke-Flake8AutoFix -PythonAction "fix-e02"
        }
        
        'FixF84' {
            Write-EQ12Log "INFO" "Fixing F841 unused local variable issues..."
            $exitCode = Invoke-Flake8AutoFix -PythonAction "fix-f84"
        }
        
        'FixAll' {
            Write-EQ12Log "INFO" "Running comprehensive Flake8 fixes..."
            $exitCode = Invoke-Flake8AutoFix -PythonAction "fix-comprehensive"
        }
        
        'GeneratePrompts' {
            Write-EQ12Log "INFO" "Generating Copilot expert prompts..."
            $exitCode = Invoke-Flake8AutoFix -PythonAction "generate-prompts"
            
            if ($exitCode -eq 0) {
                Show-AvailablePrompts
            }
        }
    }
    
    # Generate report summary if requested
    if ($GenerateReport -and $exitCode -eq 0) {
        Write-EQ12Log "INFO" "Generating summary report..."
        
        $reportSummary = @{
            Timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
            Action = $Action
            Workspace = $Workspace
            Categories = $Categories
            ExitCode = $exitCode
            LogFile = $LogFile
        }
        
        $reportFile = "$LogDir\flake8_summary_$Timestamp.json"
        $reportSummary | ConvertTo-Json | Set-Content -Path $reportFile
        Write-EQ12Log "SUCCESS" "Report saved: $reportFile"
    }
    
    # Final status
    if ($exitCode -eq 0) {
        Write-EQ12Log "SUCCESS" "EQ12 Flake8 operation completed successfully!"
    } else {
        Write-EQ12Log "ERROR" "EQ12 Flake8 operation completed with errors"
    }
    
    Write-EQ12Log "INFO" "Logs saved to: $LogFile"
    exit $exitCode
    
} catch {
    Write-EQ12Log "ERROR" "Fatal error: $($_.Exception.Message)"
    exit 1
}