[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

#Requires -Version 5.1

<#
.SYNOPSIS
    EQ12 AI-Enhanced NFL Intelligence PowerShell Wrapper
    
.DESCRIPTION
    Sophisticated PowerShell wrapper for the AI-Enhanced NFL Intelligence System
    
.PARAMETER Action
    The action to perform: FullAnalysis, QuickAnalysis
    
.PARAMETER Legs
    Number of parlay legs to generate
    
.PARAMETER VerboseOutput
    Enable verbose output
    
.PARAMETER GenerateReport
    Generate HTML report
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("FullAnalysis", "QuickAnalysis")]
    [string]$Action = "FullAnalysis",
    
    [Parameter(Mandatory = $false)]
    [int]$Legs = 10,
    
    [Parameter(Mandatory = $false)]
    [switch]$VerboseOutput,
    
    [Parameter(Mandatory = $false)]
    [switch]$GenerateReport
)

# Set script variables
$WorkspaceRoot = "C:\EQ12"
$ScriptsPath = Join-Path $WorkspaceRoot "scripts"
$PythonScript = Join-Path $ScriptsPath "eq12_ai_enhanced_nfl_intelligence.py"

function Write-AIHeader {
    Write-Host " EQ12 AI-ENHANCED NFL INTELLIGENCE SYSTEM" -ForegroundColor Magenta
    Write-Host "Multi-API AI Analysis: OpenAI + Groq + Weather + Odds!" -ForegroundColor Cyan
    Write-Host ("=" * 75) -ForegroundColor DarkGray
}

# Main execution
try {
    Write-AIHeader
    
    Write-Host " Action: $Action | Legs: $Legs" -ForegroundColor White
    
    # Set API environment variables
    ${env}OPENAI_API_KEY = "OPENAI_API_KEY_PLACEHOLDER"
    ${env}GROQ_API_KEY = "GROQ_API_KEY_PLACEHOLDER"
    ${env}ODDS_API_KEY = "ODDS_API_KEY_PLACEHOLDER"
    ${env}OPENWEATHER_API_KEY = "OPENWEATHER_API_KEY_PLACEHOLDER"
    
    Write-Host " API Keys configured: OpenAI, Groq, Odds, Weather" -ForegroundColor Green
    
    # Execute Python script
    Write-Host " Launching AI-Enhanced NFL Intelligence..." -ForegroundColor Cyan
    
    if (Test-Path $PythonScript) {
        $PythonResult = & python $PythonScript 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host " AI-Enhanced NFL Intelligence completed successfully!" -ForegroundColor Green
            
            if ($VerboseOutput) {
                Write-Host " Python Output:" -ForegroundColor Yellow
                $PythonResult | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
            }
        } else {
            Write-Warning " Python script execution had issues"
            $PythonResult | ForEach-Object { Write-Host "   $_" -ForegroundColor Red }
        }
    } else {
        Write-Error " Python script not found: $PythonScript"
    }
    
    Write-Host ""
    Write-Host ("=" * 75) -ForegroundColor DarkGray
    Write-Host " AI-ENHANCED NFL INTELLIGENCE: Operation Complete!" -ForegroundColor Magenta
    Write-Host ("=" * 75) -ForegroundColor DarkGray

} catch {
    Write-Error " AI-Enhanced NFL Intelligence Error: $($_.Exception.Message)"
}
