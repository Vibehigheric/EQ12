# EQ12 NBA JupyterLab Quick Launch
# Run this to start the Jupyter environment and open the master index

param(
    [switch]$SkipBrowser,
    [switch]$Rebuild
)

$ErrorActionPreference = "Stop"

Write-Host "EQ12 NBA JupyterLab Launcher" -ForegroundColor Cyan
Write-Host "============================`n" -ForegroundColor Cyan

# Check Docker is running
try {
    docker ps | Out-Null
}
catch {
    Write-Host "[ERROR] Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Rebuild if requested
if ($Rebuild) {
    Write-Host "[BUILD] Rebuilding Jupyter container..." -ForegroundColor Yellow
    docker-compose build jupyter
}

# Start Jupyter service
Write-Host "[START] Starting eq12-jupyter-dataviz container..." -ForegroundColor Green
docker-compose up -d jupyter

# Wait for container to be ready
Write-Host "[WAIT] Waiting for Jupyter to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check container status
$containerStatus = docker ps --filter "name=eq12-jupyter-dataviz" --format "{{.Status}}"
if ($containerStatus -match "Up") {
    Write-Host "[OK] Container is running: $containerStatus" -ForegroundColor Green
}
else {
    Write-Host "[ERROR] Container failed to start. Check logs with: docker logs eq12-jupyter-dataviz" -ForegroundColor Red
    exit 1
}

# Get server info
Write-Host "`n[INFO] Server Information:" -ForegroundColor Cyan
docker exec eq12-jupyter-dataviz jupyter server list

# Display connection details
$url = "http://localhost:8889/?token=eq12-dataviz-token"
Write-Host "`n[ACCESS] JupyterLab Connection:" -ForegroundColor Cyan
Write-Host "   URL: $url" -ForegroundColor White
Write-Host "   Token: eq12-dataviz-token" -ForegroundColor White

# Open browser unless skipped
if (-not $SkipBrowser) {
    Write-Host "`n[LAUNCH] Opening browser..." -ForegroundColor Green
    Start-Sleep -Seconds 2
    Start-Process $url
}

# Display quick commands
Write-Host "`n[COMMANDS] Quick Reference:" -ForegroundColor Cyan
Write-Host "   View logs:       docker logs -f eq12-jupyter-dataviz" -ForegroundColor Gray
Write-Host "   Stop container:  docker-compose stop jupyter" -ForegroundColor Gray
Write-Host "   Restart:         docker-compose restart jupyter" -ForegroundColor Gray
Write-Host "   Shell access:    docker exec -it eq12-jupyter-dataviz bash" -ForegroundColor GrayoundColor Gray

# Display notebook locations
Write-Host "`n[NOTEBOOKS] Key Locations:" -ForegroundColor CyanWrite-Host "`n[NOTEBOOKS] Key Locations:" -ForegroundColor Cyan
Write-Host "   Master Index: /home/jovyan/work/notebooks/nba/NBA_MASTER_INDEX.ipynb" -ForegroundColor Gray /home/jovyan/work/notebooks/nba/NBA_MASTER_INDEX.ipynb" -ForegroundColor Gray
Write-Host "   Data Ingestion: /home/jovyan/work/notebooks/nba/01_data_ingestion/" -ForegroundColor Graynba/01_data_ingestion/" -ForegroundColor Gray
Write-Host "   Models: /home/jovyan/work/notebooks/nba/03_models/" -ForegroundColor Gray
Write-Host "   Betting: /home/jovyan/work/notebooks/nba/04_betting/" -ForegroundColor Gray

# Verify environment
Write-Host "`n[ENV] Environment Check:" -ForegroundColor CyanWrite-Host "`n[ENV] Environment Check:" -ForegroundColor Cyan
$envFile = "C:\EQ12\.env".env"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Rawtent $envFile -Raw
    $oddsKeySet = $envContent -match "ODDS_API_KEY=(?!REPLACE_ME).+"tent -match "ODDS_API_KEY=(?!REPLACE_ME).+"
    $telegramSet = $envContent -match "TELEGRAM_BOT_TOKEN=(?!REPLACE_ME).+"GRAM_BOT_TOKEN=(?!REPLACE_ME).+"
    
Write-Host "   .env file: Found" -ForegroundColor Green
if ($oddsKeySet) {
    if ($oddsKeySet) {
        Write-Host "   ODDS_API_KEY: Configured" -ForegroundColor GreendColor Green
    }
    else {
        Write-Host "   ODDS_API_KEY: NOT SET (required for odds data)" -ForegroundColor Yellowdata)" -ForegroundColor Yellow
    }
    if ($telegramSet) {
        Write-Host "   TELEGRAM_BOT_TOKEN: Configured" -ForegroundColor Green   Write-Host "   TELEGRAM_BOT_TOKEN: Configured" -ForegroundColor Green
    } else {
        Write-Host "   TELEGRAM_BOT_TOKEN: Not set (optional)" -ForegroundColor GrayoundColor Gray
    }
} else {
    Write-Host "   .env file: NOT FOUND at $envFile" -ForegroundColor Yellowrite-Host "   .env file: NOT FOUND at $envFile" -ForegroundColor Yellow
    Write-Host "   Copy .env.example to .env and configure API keys" -ForegroundColor Yellow   Write-Host "   Copy .env.example to .env and configure API keys" -ForegroundColor Yellow
}

# Install dependencies reminder
Write-Host "`n[SETUP] Install NBA Dependencies (if first run):" -ForegroundColor Cyanrite-Host "`n[SETUP] Install NBA Dependencies (if first run):" -ForegroundColor Cyan
Write-Host "   docker exec -it eq12-jupyter-dataviz pip install nba-api xgboost lightgbm plotly beautifulsoup4" -ForegroundColor GrayWrite-Host "   docker exec -it eq12-jupyter-dataviz pip install nba-api xgboost lightgbm plotly beautifulsoup4" -ForegroundColor Gray

Write-Host "`n[READY] Jupyter environment ready!" -ForegroundColor Green
Write-Host "   Open NBA_MASTER_INDEX.ipynb in JupyterLab to begin analysis`n" -ForegroundColor White
