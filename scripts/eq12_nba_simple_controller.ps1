[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Status", "Pipeline", "Collect", "Train", "Predict", "Dashboard", "Telegram", "Test")]
    [string]$Action = "Status",
    
    [Parameter(Mandatory=$false)]
    [string]$GameDate = (Get-Date -Format "yyyy-MM-dd"),
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput
)

Write-Host "EQ12 NBA Betting Cluster Controller" -ForegroundColor Cyan
Write-Host "Action: $Action | Date: $GameDate" -ForegroundColor White
Write-Host "=" * 50

$PythonExe = "C:\Program Files\Python312\python.exe"
$ScriptsDir = "C:\EQ12\scripts"

function Write-Status {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

switch ($Action) {
    "Status" {
        Write-Status "Checking NBA cluster status..." "Yellow"
        
        # Check if databases exist
        $DataDir = "C:\EQ12\data"
        $databases = @("nba_odds.db", "nba_props.db", "nba_ai_insights.db")
        
        foreach ($db in $databases) {
            $dbPath = Join-Path $DataDir $db
            if (Test-Path $dbPath) {
                $size = (Get-Item $dbPath).Length / 1KB
                Write-Status "  $db : EXISTS ($([math]::Round($size, 1)) KB)" "Green"
            } else {
                Write-Status "  $db : NOT FOUND" "Red"
            }
        }
        
        # Check latest export
        $exportFile = Join-Path $DataDir "latest_tpu_export.json"
        if (Test-Path $exportFile) {
            $exportTime = (Get-Item $exportFile).LastWriteTime
            Write-Status "  Latest TPU Export: $exportTime" "Green"
        } else {
            Write-Status "  Latest TPU Export: NOT FOUND" "Red"
        }
    }
    
    "Collect" {
        Write-Status "Starting NBA data collection..." "Yellow"
        
        $params = @(
            "$ScriptsDir\eq12_nba_production_collector.py",
            "--workspace", "C:\EQ12"
        )
        if ($VerboseOutput) { $params += "--verbose" }
        
        & $PythonExe @params
        
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Data collection completed successfully!" "Green"
        } else {
            Write-Status "Data collection failed!" "Red"
        }
    }
    
    "Dashboard" {
        Write-Status "Generating NBA dashboard..." "Yellow"
        
        $params = @(
            "$ScriptsDir\eq12_nba_dashboard_generator.py",
            "--workspace", "C:\EQ12"
        )
        if ($VerboseOutput) { $params += "--verbose" }
        
        & $PythonExe @params
        
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Dashboard generated successfully!" "Green"
            $dashboardFile = "C:\EQ12\dashboard\nba_betting_dashboard_latest.html"
            if (Test-Path $dashboardFile) {
                Write-Status "Dashboard location: $dashboardFile" "Cyan"
            }
        } else {
            Write-Status "Dashboard generation failed!" "Red"
        }
    }
    
    "Telegram" {
        Write-Status "Generating Telegram report..." "Yellow"
        
        $params = @(
            "$ScriptsDir\eq12_nba_telegram_bot.py",
            "--workspace", "C:\EQ12",
            "--action", "daily"
        )
        if ($VerboseOutput) { $params += "--verbose" }
        
        & $PythonExe @params
        
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Telegram report sent successfully!" "Green"
        } else {
            Write-Status "Telegram report failed!" "Red"
        }
    }
    
    "Pipeline" {
        Write-Status "Running complete NBA pipeline..." "Yellow"
        
        # Step 1: Data Collection
        Write-Status "Step 1: Data Collection" "Cyan"
        & $PythonExe "$ScriptsDir\eq12_nba_production_collector.py" --workspace "C:\EQ12"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Status "  Data collection: SUCCESS" "Green"
            
            # Step 2: Dashboard
            Write-Status "Step 2: Dashboard Generation" "Cyan"
            & $PythonExe "$ScriptsDir\eq12_nba_dashboard_generator.py" --workspace "C:\EQ12"
            
            if ($LASTEXITCODE -eq 0) {
                Write-Status "  Dashboard: SUCCESS" "Green"
                
                # Step 3: Telegram
                Write-Status "Step 3: Telegram Report" "Cyan"
                & $PythonExe "$ScriptsDir\eq12_nba_telegram_bot.py" --workspace "C:\EQ12" --action "daily"
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Status "  Telegram: SUCCESS" "Green"
                    Write-Status "Complete pipeline executed successfully!" "Green"
                } else {
                    Write-Status "  Telegram: FAILED" "Red"
                }
            } else {
                Write-Status "  Dashboard: FAILED" "Red"
            }
        } else {
            Write-Status "  Data collection: FAILED" "Red"
        }
    }
    
    "Test" {
        Write-Status "Running NBA cluster tests..." "Yellow"
        
        # Test 1: Data Collection
        Write-Status "Test 1: Data Collection (test mode)" "Cyan"
        & $PythonExe "$ScriptsDir\eq12_nba_production_collector.py" --workspace "C:\EQ12" --test-mode
        $test1 = ($LASTEXITCODE -eq 0)
        
        # Test 2: Dashboard
        Write-Status "Test 2: Dashboard Generation" "Cyan"
        & $PythonExe "$ScriptsDir\eq12_nba_dashboard_generator.py" --workspace "C:\EQ12"
        $test2 = ($LASTEXITCODE -eq 0)
        
        # Test 3: Telegram
        Write-Status "Test 3: Telegram Bot" "Cyan"
        & $PythonExe "$ScriptsDir\eq12_nba_telegram_bot.py" --workspace "C:\EQ12" --action "report"
        $test3 = ($LASTEXITCODE -eq 0)
        
        # Results
        Write-Host "`n" + "=" * 40
        Write-Host "NBA CLUSTER TEST RESULTS" -ForegroundColor Cyan
        Write-Host "=" * 40
        
        Write-Status "Data Collection: $(if ($test1) { 'PASS' } else { 'FAIL' })" $(if ($test1) { "Green" } else { "Red" })
        Write-Status "Dashboard:       $(if ($test2) { 'PASS' } else { 'FAIL' })" $(if ($test2) { "Green" } else { "Red" })
        Write-Status "Telegram Bot:    $(if ($test3) { 'PASS' } else { 'FAIL' })" $(if ($test3) { "Green" } else { "Red" })
        
        $totalPassed = @($test1, $test2, $test3) | Where-Object { $_ -eq $true } | Measure-Object | Select-Object -ExpandProperty Count
        Write-Status "Overall: $totalPassed/3 tests passed" $(if ($totalPassed -eq 3) { "Green" } else { "Yellow" })
    }
    
    default {
        Write-Status "Unknown action: $Action" "Red"
        Write-Status "Available actions: Status, Pipeline, Collect, Dashboard, Telegram, Test" "Yellow"
    }
}

Write-Host "`n" + "=" * 50
Write-Status "EQ12 NBA Cluster Controller finished" "Cyan"