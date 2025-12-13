[CmdletBinding()]
param(
    [string]$ApiKey = $env:ODDS_API_KEY,
    [int[]]$Legs = @(6, 10, 15, 20),
    [switch]$Demo,
    [switch]$Help
)

function Show-Help {
    Write-Host "🏒🏀 EQ12 Advanced Parlay Generator" -ForegroundColor Green
    Write-Host "="*50 -ForegroundColor Green
    Write-Host ""
    Write-Host "Generates 6, 10, 15, and 20-leg parlays including Same Game Parlays (SGP)" -ForegroundColor Yellow
    Write-Host "for tonight's NHL games using live odds from The Odds API." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Cyan
    Write-Host "  .\eq12_advanced_parlay_generator.ps1                    # Run with live data"
    Write-Host "  .\eq12_advanced_parlay_generator.ps1 -Demo             # Run demo mode"
    Write-Host "  .\eq12_advanced_parlay_generator.ps1 -Legs 6,10        # Custom leg counts"
    Write-Host "  .\eq12_advanced_parlay_generator.ps1 -Help             # Show this help"
    Write-Host ""
    Write-Host "PARAMETERS:" -ForegroundColor Cyan
    Write-Host "  -ApiKey    : The Odds API key (uses ODDS_API_KEY env var if not specified)"
    Write-Host "  -Legs      : Array of leg counts for parlays (default: 6,10,15,20)"
    Write-Host "  -Demo      : Run in demo mode with mock data (no API key required)"
    Write-Host "  -Help      : Show this help message"
    Write-Host ""
    Write-Host "FEATURES:" -ForegroundColor Cyan
    Write-Host "  • 6, 10, 15, and 20-leg parlay combinations"
    Write-Host "  • Same Game Parlays (SGP) - multiple bets from one game"
    Write-Host "  • Multi-SGP slips - combine SGPs from different games"
    Write-Host "  • Intelligent bet selection and conflict avoidance"
    Write-Host "  • Probability calculations and value analysis"
    Write-Host "  • JSON logging for historical tracking"
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Cyan
    Write-Host "  # Generate standard 6,10,15,20-leg parlays with live data"
    Write-Host "  `$env:ODDS_API_KEY = 'your_api_key'"
    Write-Host "  .\eq12_advanced_parlay_generator.ps1"
    Write-Host ""
    Write-Host "  # Test with demo data (no API key needed)"
    Write-Host "  .\eq12_advanced_parlay_generator.ps1 -Demo"
    Write-Host ""
    Write-Host "  # Generate only 6 and 10-leg parlays"
    Write-Host "  .\eq12_advanced_parlay_generator.ps1 -Legs 6,10"
    Write-Host ""
    Write-Host "API SETUP:" -ForegroundColor Cyan
    Write-Host "  1. Get free API key from https://the-odds-api.com"
    Write-Host "  2. Set environment variable: `$env:ODDS_API_KEY = 'your_key'"
    Write-Host "  3. Or pass directly: -ApiKey 'your_key'"
    Write-Host ""
    Write-Host "OUTPUT:" -ForegroundColor Cyan
    Write-Host "  • Console display of all parlay combinations"
    Write-Host "  • JSON log saved to C:\EQ12\logs\"
    Write-Host "  • Same Game Parlay (SGP) combinations highlighted"
    Write-Host "  • Probability percentages and odds calculations"
    Write-Host ""
}

if ($Help) {
    Show-Help
    return
}

Write-Host "🏒🏀 EQ12 Advanced Parlay Generator - Starting..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Python not found. Please install Python 3.8+ and add it to PATH."
    return
}

# Check for required packages
Write-Host "Checking Python dependencies..." -ForegroundColor Yellow
$requiredPackages = @("requests")

foreach ($package in $requiredPackages) {
    try {
        python -c "import $package" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $package is available" -ForegroundColor Green
        } else {
            Write-Host "Installing $package..." -ForegroundColor Yellow
            python -m pip install $package --quiet
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ $package installed successfully" -ForegroundColor Green
            } else {
                Write-Error "Failed to install $package. Please install manually: pip install $package"
                return
            }
        }
    } catch {
        Write-Host "Installing $package..." -ForegroundColor Yellow
        python -m pip install $package --quiet
    }
}

# Prepare arguments for Python script
$pythonArgs = @()

if ($Demo) {
    $pythonArgs += "--demo"
    Write-Host "Running in DEMO mode (no API key required)" -ForegroundColor Yellow
} elseif ($ApiKey) {
    $pythonArgs += "--api-key", $ApiKey
    Write-Host "Using provided API key for live data" -ForegroundColor Green
} elseif ($env:ODDS_API_KEY) {
    Write-Host "Using ODDS_API_KEY environment variable for live data" -ForegroundColor Green
} else {
    Write-Host "No API key found - running in DEMO mode" -ForegroundColor Yellow
    $pythonArgs += "--demo"
}

if ($Legs) {
    $pythonArgs += "--legs"
    $pythonArgs += $Legs
    Write-Host "Generating parlays with $($Legs -join ', ') legs" -ForegroundColor Cyan
}

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Construct path to Python script
$pythonScript = Join-Path $scriptDir "eq12_advanced_parlay_generator.py"

if (-not (Test-Path $pythonScript)) {
    Write-Error "Python script not found: $pythonScript"
    return
}

Write-Host ""
Write-Host "🚀 Launching Advanced Parlay Generator..." -ForegroundColor Green
Write-Host "Arguments: $($pythonArgs -join ' ')" -ForegroundColor Gray

# Execute Python script
try {
    & python $pythonScript @pythonArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Advanced parlay generation completed successfully!" -ForegroundColor Green
        Write-Host "Check C:\EQ12\logs\ for detailed JSON analysis files." -ForegroundColor Cyan
    } else {
        Write-Error "Advanced parlay generator failed with exit code $LASTEXITCODE"
    }
} catch {
    Write-Error "Error running advanced parlay generator: $_"
}

Write-Host ""
Write-Host "💡 TIP: Use -Help to see all available options and examples" -ForegroundColor Yellow