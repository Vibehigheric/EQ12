[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("analyze", "betting", "nhl", "arbitrage", "test")]
    [string]$Action = "analyze",
    
    [Parameter(Mandatory=$false)]
    [string]$GameData = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Question = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput = $false
)

# EQ12 Groq AI Wrapper - Ultra-Fast Sports Analysis
# Part of EQ12 GODSTACK enhancement with free/freemium APIs
# Integrates Groq Llama models for 3-5x faster betting analysis

$ErrorActionPreference = "Stop"
$GroqPythonScript = Join-Path $PSScriptRoot "groq_ai_client.py"

# Ensure Python script exists
if (-not (Test-Path $GroqPythonScript)) {
    Write-Error "Groq client not found at: $GroqPythonScript"
    exit 1
}

# Check for GROQ_API_KEY
if (-not $env:GROQ_API_KEY) {
    Write-Warning "GROQ_API_KEY environment variable not set"
    Write-Host "Get your free API key from: https://console.groq.com/keys" -ForegroundColor Yellow
    Write-Host "14,400 requests/day free tier available" -ForegroundColor Green
    exit 1
}

# Log directory for EQ12 compliance
$LogDir = "C:\EQ12\logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $LogDir "groq_wrapper_$timestamp.log"

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")
    $logEntry = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
        level = $Level
        component = "EQ12-Groq-Wrapper"
        message = $Message
        action = $Action
        session_id = $timestamp
    }
    $logEntry | ConvertTo-Json -Compress | Out-File -FilePath $logFile -Append -Encoding UTF8
    
    if ($VerboseOutput -or $Level -eq "ERROR") {
        Write-Host "[$Level] $Message" -ForegroundColor $(if($Level -eq "ERROR") {"Red"} else {"Green"})
    }
}

try {
    Write-EQ12Log "Starting Groq AI analysis with action: $Action"
    
    # Build Python command based on action
    $pythonArgs = @()
    
    switch ($Action) {
        "analyze" {
            if ($Question) {
                $pythonArgs += @("--analyze", $Question)
            } else {
                $pythonArgs += @("--analyze", "Provide quick sports betting analysis for today's games")
            }
        }
        "betting" {
            if ($GameData) {
                $pythonArgs += @("--betting-analysis", $GameData)
            } else {
                Write-EQ12Log "Betting analysis requires --GameData parameter" "ERROR"
                exit 1
            }
        }
        "nhl" {
            $pythonArgs += @("--nhl-analysis")
            if ($GameData) {
                $pythonArgs += $GameData
            }
        }
        "arbitrage" {
            $pythonArgs += @("--arbitrage-scan")
        }
        "test" {
            $pythonArgs += @("--test-connection")
        }
    }
    
    if ($VerboseOutput) {
        $pythonArgs += "--verbose"
    }
    
    Write-EQ12Log "Executing: python $GroqPythonScript $($pythonArgs -join ' ')"
    
    # Execute Python script
    $result = & python $GroqPythonScript @pythonArgs
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-EQ12Log "Groq analysis completed successfully"
        Write-Output $result
    } else {
        Write-EQ12Log "Groq analysis failed with exit code: $exitCode" "ERROR"
        Write-Error "Analysis failed: $result"
    }
    
} catch {
    Write-EQ12Log "Exception in Groq wrapper: $($_.Exception.Message)" "ERROR"
    throw
}

# Usage Examples:
# .\eq12_groq_wrapper.ps1 -Action analyze -Question "What are the best NHL bets tonight?"
# .\eq12_groq_wrapper.ps1 -Action nhl -GameData "BOS @ TOR, COL @ VGK"
# .\eq12_groq_wrapper.ps1 -Action arbitrage -Verbose
# .\eq12_groq_wrapper.ps1 -Action test