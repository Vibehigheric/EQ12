<# =====================================================================
   EQ12 PowerShell Formatting Standard (ASCII-Only Safe)
   Author: EQ12 System Maintainer
   Purpose: Provide a consistent, stable formatting style for all PS1
            automation, logging, diagnostics, and scheduled tasks.
   ===================================================================== #>

# ---------------------------
# BASIC SCRIPT SETTINGS
# ---------------------------
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSDefaultParameterValues['Out-File:Encoding'] = 'ASCII'

# ---------------------------
# CONSTANTS
# ---------------------------
$DateStamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
$ScriptName = $MyInvocation.MyCommand.Name

# ---------------------------
# LOGGING HELPERS (ASCII ONLY)
# ---------------------------

function Write-Log {
    param (
        [Parameter(Mandatory = $true)][string]$Message,
        [ValidateSet("INFO", "ERROR", "WARN", "SUCCESS")] 
        [string]$Level = "INFO"
    )

    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[{0}] [{1}] {2}" -f $ts, $Level, $Message
    Write-Host $line
    
    # Also write to log file (same directory as script)
    $logFile = Join-Path -Path $PSScriptRoot -ChildPath "script.log"
    Add-Content -Path $logFile -Value $line -Encoding ASCII
}

# ---------------------------
# CLEAN SECTIONS FORMAT
# ---------------------------
function Start-Section {
    param([string]$Name)
    Write-Host ""
    Write-Host "==================================================================="
    Write-Host "SECTION: $Name"
    Write-Host "==================================================================="
}

function End-Section {
    Write-Host "==================================================================="
    Write-Host ""
}

# ---------------------------
# SAFE WRITE-HOST WRAPPER
# ---------------------------
function Banner {
    param([string]$Text)
    Write-Host ""
    Write-Host "-------------------------------------------------------------------"
    Write-Host $Text
    Write-Host "-------------------------------------------------------------------"
    Write-Host ""
}

# ---------------------------
# ERROR HANDLING TEMPLATE
# ---------------------------
function Safe-Block {
    param([scriptblock]$Action)

    try {
        & $Action
        Write-Log -Message "Block succeeded." -Level "SUCCESS"
    }
    catch {
        Write-Log -Message ("ERROR: " + $_.Exception.Message) -Level "ERROR"
    }
}

# ---------------------------
# SAMPLE FORMATTING USAGE
# ---------------------------

Banner "Starting EQ12 Diagnostic Task"

Start-Section "System Check"
Safe-Block {
    # Example test
    Get-Process | Out-Null
}
End-Section

Start-Section "Cleanup"
Safe-Block {
    # Example cleanup
    Write-Log "Cleanup complete."
}
End-Section

Write-Log "Script completed successfully." -Level "SUCCESS"
