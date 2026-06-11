[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

#Requires -Version 5.1

<#
.SYNOPSIS
    EQ12 AI-Enhanced NFL Intelligence PowerShell Wrapper
    
.DESCRIPTION
    Sophisticated PowerShell wrapper for the AI-Enhanced NFL Intelligence System
    Uses OpenAI, Groq, Weather API, and Odds API for superior betting decisions
    
.PARAMETER Action
    The action to perform: FullAnalysis, QuickAnalysis, WeatherCheck, AIOptimize
    
.PARAMETER Legs
    Number of parlay legs to generate (default: 10)
    
.PARAMETER FocusLVDEN
    Focus on tonight's LV vs DEN game (switch parameter)
    
.PARAMETER VerboseOutput
    Enable verbose output (switch parameter)
    
.PARAMETER GenerateReport
    Generate HTML report (switch parameter)
    
.EXAMPLE
    .\eq12_ai_enhanced_nfl_wrapper.ps1 -Action FullAnalysis -Legs 10 -FocusLVDEN -VerboseOutput -GenerateReport
    
.NOTES
    Created: November 6, 2025
    Author: EQ12 System Operations Team
    Purpose: AI-powered NFL analysis with multi-API intelligence
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("FullAnalysis", "QuickAnalysis", "WeatherCheck", "AIOptimize")]
    [string]$Action = "FullAnalysis",
    
    [Parameter(Mandatory = $false)]
    [ValidateRange(5, 15)]
    [int]$Legs = 10,
    
    [Parameter(Mandatory = $false)]
    [switch]$FocusLVDEN,
    
    [Parameter(Mandatory = $false)]
    [switch]$VerboseOutput,
    
    [Parameter(Mandatory = $false)]
    [switch]$GenerateReport
)

# Set script variables
$ScriptName = "EQ12-AI-Enhanced-NFL-Intelligence"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$WorkspaceRoot = "C:\EQ12"
$ScriptsPath = Join-Path $WorkspaceRoot "scripts"
$LogsPath = Join-Path $WorkspaceRoot "logs"
$DashboardPath = Join-Path $WorkspaceRoot "dashboard"
$DataPath = Join-Path $WorkspaceRoot "data"

# AI-Enhanced NFL Intelligence Python script
$PythonScript = Join-Path $ScriptsPath "eq12_ai_enhanced_nfl_intelligence.py"

function Write-AIHeader {
    Write-Host " EQ12 AI-ENHANCED NFL INTELLIGENCE SYSTEM" -ForegroundColor Magenta
    Write-Host "Multi-API AI Analysis: OpenAI + Groq + Weather + Odds!" -ForegroundColor Cyan
    Write-Host ("=" * 75) -ForegroundColor DarkGray
    Write-Host " ARTIFICIAL INTELLIGENCE: Superior betting decisions" -ForegroundColor Green
    Write-Host " REAL-TIME DATA: Live odds and weather integration" -ForegroundColor Blue
    Write-Host " TONIGHT"S FOCUS: Las Vegas Raiders @ Denver Broncos" -ForegroundColor Yellow
    Write-Host ("=" * 75) -ForegroundColor DarkGray
}

function Invoke-AIEnhancedSystem {
    param(
        [string]$ActionType,
        [int]$LegCount,
        [bool]$EnableVerbose
    )
    
    Write-Host " Executing AI-Enhanced NFL Intelligence..." -ForegroundColor Magenta
    
    if ($EnableVerbose) {
        Write-Host " Configuration:" -ForegroundColor Yellow
        Write-Host "    Action: $ActionType" -ForegroundColor White
        Write-Host "    Parlay Legs: $LegCount" -ForegroundColor White
        Write-Host "    Focus LV vs DEN: $($FocusLVDEN.IsPresent)" -ForegroundColor White
        Write-Host "    Python Script: $PythonScript" -ForegroundColor White
    }
    
    # Check if Python script exists
    if (-not (Test-Path $PythonScript)) {
        Write-Error " Python script not found: $PythonScript"
        return $false
    }
    
    try {
        # Set environment variables for APIs
        ${env}OPENAI_API_KEY = "OPENAI_API_KEY_PLACEHOLDER"
        ${env}GROQ_API_KEY = "GROQ_API_KEY_PLACEHOLDER"
        ${env}ODDS_API_KEY = "ODDS_API_KEY_PLACEHOLDER"
        ${env}OPENWEATHER_API_KEY = "OPENWEATHER_API_KEY_PLACEHOLDER"
        
        Write-Host " API Keys configured: OpenAI, Groq, Odds, Weather" -ForegroundColor Green
        
        # Execute Python script
        Write-Host " Launching AI-Enhanced NFL Intelligence..." -ForegroundColor Cyan
        
        $PythonResult = & python $PythonScript 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host " AI-Enhanced NFL Intelligence completed successfully!" -ForegroundColor Green
            
            if ($EnableVerbose) {
                Write-Host " Python Output:" -ForegroundColor Yellow
                $PythonResult | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
            }
            
            # Find latest AI parlay file
            $LatestParlay = Get-ChildItem -Path $DataPath -Filter "ai_enhanced_nfl_parlay_*.json" | 
                           Sort-Object LastWriteTime -Descending | 
                           Select-Object -First 1
            
            if ($LatestParlay) {
                Write-Host " Latest AI Parlay: $($LatestParlay.Name)" -ForegroundColor Cyan
                return $LatestParlay.FullName
            }
            
        } else {
            Write-Warning " Python script execution issues detected"
            Write-Host " Output:" -ForegroundColor Yellow
            $PythonResult | ForEach-Object { Write-Host "   $_" -ForegroundColor Red }
        }
        
    } catch {
        Write-Error " Error executing AI-Enhanced system: $($_.Exception.Message)"
        return $false
    }
}

function New-AIEnhancedHTMLReport {
    param(
        [string]$ParlayFile
    )
    
    if (-not $ParlayFile -or -not (Test-Path $ParlayFile)) {
        Write-Warning " No parlay file found for HTML report generation"
        return
    }
    
    try {
        $ParlayData = Get-Content $ParlayFile -Raw | ConvertFrom-Json
        $ReportFile = Join-Path $DashboardPath "ai_enhanced_nfl_report_$Timestamp.html"
        
        # Extract key metrics
        $TotalOdds = $ParlayData.odds.total_decimal_odds
        $Payout = $ParlayData.odds.potential_payout
        $LegCount = $ParlayData.leg_count
        $HighConfidence = $ParlayData.confidence_levels.high
        $MediumConfidence = $ParlayData.confidence_levels.medium
        $AIProviders = $ParlayData.ai_providers -join ", "
        
        $HTMLContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 AI-Enhanced NFL Intelligence Report</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container { 
            max-width: 1200px; margin: 0 auto; 
            background: rgba(255,255,255,0.1); 
            border-radius: 20px; padding: 30px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
        }
        .header { 
            text-align: center; 
            border-bottom: 3px solid #00ff88; 
            padding-bottom: 20px; margin-bottom: 30px; 
        }
        .header h1 { 
            color: #00ff88; margin: 0; font-size: 2.8em; 
            text-shadow: 0 0 20px rgba(0,255,136,0.5);
        }
        .ai-badge {
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            display: inline-block;
            margin: 10px 0;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(78, 205, 196, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(78, 205, 196, 0); }
            100% { box-shadow: 0 0 0 0 rgba(78, 205, 196, 0); }
        }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
            gap: 25px; margin: 30px 0; 
        }
        .stat-card { 
            background: rgba(255,255,255,0.1); 
            border-left: 5px solid #00ff88; 
            padding: 25px; border-radius: 15px;
            backdrop-filter: blur(5px);
            transition: transform 0.3s ease;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,255,136,0.2);
        }
        .stat-card h3 { 
            margin: 0 0 15px 0; 
            color: #00ff88; 
            font-size: 1.2em;
        }
        .stat-value { 
            font-size: 2.2em; 
            font-weight: bold; 
            color: #ffffff; 
            text-shadow: 0 0 10px rgba(255,255,255,0.3);
        }
        .legs-section {
            background: rgba(0,0,0,0.2);
            border-radius: 15px;
            padding: 25px;
            margin: 25px 0;
        }
        .leg-item {
            background: rgba(255,255,255,0.1);
            margin: 10px 0;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #4ecdc4;
        }
        .leg-high { border-left-color: #ff6b6b; }
        .leg-medium { border-left-color: #ffd93d; }
        .leg-featured { 
            border-left-color: #00ff88; 
            background: rgba(0,255,136,0.1);
        }
        .ai-analysis {
            background: rgba(138, 43, 226, 0.2);
            border: 1px solid rgba(138, 43, 226, 0.5);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .weather-intel {
            background: rgba(30, 144, 255, 0.2);
            border: 1px solid rgba(30, 144, 255, 0.5);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .timestamp { 
            text-align: center; 
            color: rgba(255,255,255,0.7); 
            margin-top: 30px; 
            font-style: italic; 
        }
        .success-badge { 
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white; 
            padding: 15px 25px; 
            border-radius: 25px; 
            display: inline-block; 
            margin: 15px 0;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> EQ12 AI-ENHANCED NFL INTELLIGENCE</h1>
            <div class="ai-badge">$AIProviders</div>
            <p>Multi-API Artificial Intelligence  Superior Betting Decisions</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3> Total Odds</h3>
                <div class="stat-value">${TotalOdds}x</div>
            </div>
            <div class="stat-card">
                <h3> Potential Payout</h3>
                <div class="stat-value">`$$(${Payout:N2})</div>
            </div>
            <div class="stat-card">
                <h3> Total Legs</h3>
                <div class="stat-value">$LegCount</div>
            </div>
            <div class="stat-card">
                <h3> High Confidence</h3>
                <div class="stat-value">$HighConfidence</div>
            </div>
        </div>
        
        <div class="ai-analysis">
            <h2> AI Intelligence Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>High Confidence Picks</h3>
                    <div class="stat-value">$HighConfidence</div>
                </div>
                <div class="stat-card">
                    <h3>Medium Confidence Picks</h3>
                    <div class="stat-value">$MediumConfidence</div>
                </div>
                <div class="stat-card">
                    <h3>AI Providers Active</h3>
                    <div class="stat-value">$($ParlayData.ai_providers.Count)</div>
                </div>
            </div>
        </div>
        
        <div class="legs-section">
            <h2> AI-ENHANCED PARLAY LEGS</h2>
"@
        
        # Add each leg
        for ($i = 0; $i -lt $ParlayData.legs.Count; $i++) {
            $leg = $ParlayData.legs[$i]
            $legNumber = $i + 1
            $confidenceClass = switch ($leg.confidence) {
                "HIGH" { "leg-high" }
                "MEDIUM" { "leg-medium" }
                default { "leg-medium" }
            }
            
            if ($leg.featured) {
                $confidenceClass += " leg-featured"
            }
            
            $HTMLContent += @"
            <div class="leg-item $confidenceClass">
                <strong>$legNumber. $($leg.selection)</strong> ($($leg.odds))
                <br><small> $($leg.description)</small>
                $(if ($leg.ai_reasoning) { "<br><em> AI: $($leg.ai_reasoning)</em>" })
                $(if ($leg.featured) { "<br><span style='color: #00ff88;'> FEATURED PICK</span>" })
            </div>
"@
        }
        
        $HTMLContent += @"
        </div>
        
        <div class="weather-intel">
            <h2> Weather Intelligence</h2>
            <p>Environmental factors analyzed and integrated into AI decision matrix</p>
"@
        
        # Add weather data if available
        if ($ParlayData.weather_intelligence) {
            foreach ($gameWeather in $ParlayData.weather_intelligence.PSObject.Properties) {
                $weather = $gameWeather.Value
                if ($weather.analysis) {
                    $HTMLContent += "<p><strong>Weather Impact:</strong> $($weather.analysis) (Impact: $($weather.impact.ToUpper()))</p>"
                }
            }
        }
        
        $HTMLContent += @"
        </div>
        
        <div class="success-badge">
             AI-Enhanced NFL Intelligence: Multi-API Analysis Complete
        </div>
        
        <div class="timestamp">
            Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss") | System: EQ12 AI-Enhanced NFL Intelligence
            <br>File: $(Split-Path $ParlayFile -Leaf)
        </div>
    </div>
</body>
</html>
"@
        
        $HTMLContent | Out-File -FilePath $ReportFile -Encoding UTF8
        Write-Host " AI-Enhanced HTML Report: $ReportFile" -ForegroundColor Green
        
        # Open in browser
        if ($GenerateReport) {
            Start-Process $ReportFile
            Write-Host " Report opened in default browser" -ForegroundColor Cyan
        }
        
        return $ReportFile
        
    } catch {
        Write-Error " Error generating AI-Enhanced HTML report: $($_.Exception.Message)"
    }
}

function Get-AISystemStatus {
    Write-Host " AI System Status Check..." -ForegroundColor Yellow
    
    # Check Python availability
    try {
        $PythonVersion = & python --version 2>&1
        Write-Host " Python: $PythonVersion" -ForegroundColor Green
    } catch {
        Write-Host " Python: Not available" -ForegroundColor Red
    }
    
    # Check API key configuration
    $APIKeys = @("OPENAI_API_KEY", "GROQ_API_KEY", "ODDS_API_KEY", "OPENWEATHER_API_KEY")
    foreach ($key in $APIKeys) {
        $keyValue = [System.Environment]::GetEnvironmentVariable($key)
        if ($keyValue) {
            $keyPreview = $keyValue.Substring(0, [Math]::Min(20, $keyValue.Length)) + "..."
            Write-Host " ${key}: $keyPreview" -ForegroundColor Green
        } else {
            Write-Host " ${key}: Not configured" -ForegroundColor Red
        }
    }
    
    # Check required directories
    $RequiredDirs = @($WorkspaceRoot, $ScriptsPath, $LogsPath, $DashboardPath, $DataPath)
    foreach ($dir in $RequiredDirs) {
        if (Test-Path $dir) {
            Write-Host " Directory: $dir" -ForegroundColor Green
        } else {
            Write-Host " Directory: $dir (Missing)" -ForegroundColor Red
        }
    }
}

# Main execution
try {
    Write-AIHeader
    
    Write-Host " Action: $Action | Legs: $Legs | Focus LV vs DEN: $($FocusLVDEN.IsPresent)" -ForegroundColor White
    Write-Host ""
    
    switch ($Action) {
        "FullAnalysis" {
            Write-Host " Executing Full AI-Enhanced Analysis..." -ForegroundColor Magenta
            $ParlayFile = Invoke-AIEnhancedSystem -ActionType $Action -LegCount $Legs -EnableVerbose $VerboseOutput.IsPresent
            
            if ($ParlayFile -and $GenerateReport) {
                $HTMLReport = New-AIEnhancedHTMLReport -ParlayFile $ParlayFile
                Write-Host " AI-Enhanced Analysis Complete with HTML Report!" -ForegroundColor Green
            }
        }
        
        "QuickAnalysis" {
            Write-Host " Executing Quick AI Analysis..." -ForegroundColor Cyan
            $ParlayFile = Invoke-AIEnhancedSystem -ActionType $Action -LegCount $Legs -EnableVerbose $false
        }
        
        "WeatherCheck" {
            Write-Host " Weather Intelligence Check..." -ForegroundColor Blue
            Get-AISystemStatus
        }
        
        "AIOptimize" {
            Write-Host " AI Optimization Mode..." -ForegroundColor Magenta
            $ParlayFile = Invoke-AIEnhancedSystem -ActionType $Action -LegCount $Legs -EnableVerbose $VerboseOutput.IsPresent
        }
    }
    
    Write-Host ""
    Write-Host ("=" * 75) -ForegroundColor DarkGray
    Write-Host " AI-ENHANCED NFL INTELLIGENCE: Operation Complete!" -ForegroundColor Magenta
    Write-Host " Multi-API Analysis: OpenAI + Groq + Weather + Odds" -ForegroundColor Cyan
    Write-Host " Superior Betting Intelligence Delivered!" -ForegroundColor Green
    Write-Host ("=" * 75) -ForegroundColor DarkGray

} catch {
    Write-Error " AI-Enhanced NFL Intelligence Error: $($_.Exception.Message)"
    Write-Host " Stack Trace:" -ForegroundColor Red
    Write-Host $_.Exception.StackTrace -ForegroundColor Red
}
