[CmdletBinding()]
param(
    [Parameter(HelpMessage = "Skip browser automation setup")]
    [switch]$SkipBrowser,

    [Parameter(HelpMessage = "Skip AI governance components")]
    [switch]$SkipAI,

    [Parameter(HelpMessage = "Run in test mode (no actual services)")]
    [switch]$TestMode,

    [Parameter(HelpMessage = "Show system status only")]
    [switch]$Status,

    [Parameter(HelpMessage = "Restart specific component")]
    [string]$RestartComponent,

    [Parameter(HelpMessage = "EQ12 root directory")]
    [string]$EQ12Root = "C:\EQ12"
)

<#
.SYNOPSIS
EQ12 GODSTACK Complete System Startup - PowerShell Wrapper

.DESCRIPTION
PowerShell wrapper for the EQ12 System Manager that provides
convenient startup of all EQ12 GODSTACK components including:
- Expert Kelly Integration System
- Paper Trading Module
- Historical Backtesting Engine
- EdgeGod Parlay System
- Browser Automation
- AI Governance Suite

.EXAMPLE
.\Start-EQ12-GODSTACK.ps1
Start complete EQ12 system with all components

.EXAMPLE
.\Start-EQ12-GODSTACK.ps1 -SkipBrowser -SkipAI
Start system without browser automation and AI components

.EXAMPLE
.\Start-EQ12-GODSTACK.ps1 -TestMode
Run system startup in test mode (no actual services)

.EXAMPLE
.\Start-EQ12-GODSTACK.ps1 -Status
Show current system status

.EXAMPLE
.\Start-EQ12-GODSTACK.ps1 -RestartComponent kelly
Restart the Kelly bankroll management component
#>

# Set error action preference
$ErrorActionPreference = "Stop"

# EQ12 GODSTACK ASCII Banner
$Banner = @"
╔══════════════════════════════════════════════════════════════╗
║                      EQ12 GODSTACK                           ║
║                 COMPLETE SYSTEM STARTUP                      ║
║                                                              ║
║  🎯 Expert Kelly Integration System                          ║
║  📊 Paper Trading Module                                     ║
║  📈 Historical Backtesting Engine                            ║
║  🤖 EdgeGod Parlay System                                    ║
║  🌐 Browser Governance Automation                            ║
║  🧠 AI Governance Suite                                      ║
║                                                              ║
║  Ready for automated sports betting optimization!            ║
╚══════════════════════════════════════════════════════════════╝
"@

Write-Host $Banner -ForegroundColor Cyan

# Validate EQ12 root directory
if (!(Test-Path $EQ12Root)) {
    Write-Error "EQ12 root directory not found: $EQ12Root"
    exit 1
}

Write-Verbose "EQ12 Root Directory: $EQ12Root"

# Change to EQ12 directory
Push-Location $EQ12Root

try {
    # Build Python command arguments
    $PythonArgs = @("eq12_system_manager.py")

    if ($SkipBrowser) {
        $PythonArgs += "--skip-browser"
    }

    if ($SkipAI) {
        $PythonArgs += "--skip-ai"
    }

    if ($TestMode) {
        $PythonArgs += "--test-mode"
    }

    if ($Status) {
        $PythonArgs += "--status"
    }

    if ($RestartComponent) {
        $PythonArgs += "--restart-component", $RestartComponent
    }

    $PythonArgs += "--eq12-root", $EQ12Root

    Write-Host "🚀 Starting EQ12 System Manager..." -ForegroundColor Green
    Write-Verbose "Python command: python $($PythonArgs -join ' ')"

    # Execute Python system manager
    $StartTime = Get-Date

    & python @PythonArgs
    $ExitCode = $LASTEXITCODE

    $EndTime = Get-Date
    $Duration = $EndTime - $StartTime

    Write-Host "`n⏱️ Execution completed in $($Duration.TotalSeconds.ToString('F1')) seconds" -ForegroundColor Yellow

    if ($ExitCode -eq 0) {
        Write-Host "✅ EQ12 GODSTACK System startup successful!" -ForegroundColor Green

        # Show quick status summary
        if (!$Status -and !$RestartComponent) {
            Write-Host "`n📋 SYSTEM SUMMARY:" -ForegroundColor Cyan
            Write-Host "   💰 Kelly Bankroll Management: Ready"
            Write-Host "   📊 Paper Trading: Active"
            Write-Host "   📈 Backtesting Engine: Initialized"
            Write-Host "   🌐 Browser Automation: $(if ($SkipBrowser) { 'Skipped' } else { 'Ready' })"
            Write-Host "   🧠 AI Governance: $(if ($SkipAI) { 'Skipped' } else { 'Active' })"

            Write-Host "`n🎯 Next Steps:" -ForegroundColor Yellow
            Write-Host "   • Run paper trading: python sports-betting-optimizer/src/core/paper_trader.py"
            Write-Host "   • Start backtesting: python sports-betting-optimizer/src/core/backtester.py"
            Write-Host "   • Browser governance: python chrome_governance_automation.py --launch-browser"
            Write-Host "   • AI assistant: python eq12_streaming_assistant.py --interactive"
        }
    }
    else {
        Write-Warning "❌ EQ12 System startup completed with errors (Exit Code: $ExitCode)"
        Write-Host "Check logs in: $EQ12Root\logs\" -ForegroundColor Yellow
    }

}
catch {
    Write-Error "Failed to execute EQ12 System Manager: $_"
    exit 1
}
finally {
    # Return to original directory
    Pop-Location
}

# Additional PowerShell-specific functionality
if ($ExitCode -eq 0 -and !$Status -and !$RestartComponent -and !$TestMode) {
    Write-Host "`n🔧 PowerShell Integration Available:" -ForegroundColor Magenta
    Write-Host "   • Import-Module: Import-Module '$EQ12Root\scripts\eq12_powershell_module.psm1'"
    Write-Host "   • Quick Status: Get-EQ12Status"
    Write-Host "   • Restart Component: Restart-EQ12Component -Name 'kelly'"
    Write-Host "   • View Logs: Show-EQ12Logs"
}

exit $ExitCode
