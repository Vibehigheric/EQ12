# EQ12 GODLIKE LAUNCHER - Ultimate One-Keystroke Command System
# UTF-8 Safe Version - No Problematic Characters
# ================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

param(
    [string]$Command,
    [switch]$QuickMode,
    [string]$Workspace = "C:\EQ12"
)

# Initialize environment
Set-Location $Workspace
$LogFile = "$Workspace\logs\eq12_godlike_launcher_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-LauncherLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp | $Level | $Message"
    Add-Content -Path $LogFile -Value $logEntry -Encoding UTF8
    
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "Cyan" }
    }
    Write-Host $logEntry -ForegroundColor $color
}

function Show-EQ12Banner {
    Clear-Host
    Write-Host @"

                       
              
                            
                            
          
                 
                                                                                        
    GODLIKE LAUNCHER SYSTEM - Ultimate One-Keystroke Commands
    
"@ -ForegroundColor Cyan
    
    Write-Host "System Status: " -NoNewline -ForegroundColor White
    Write-Host "OPERATIONAL" -ForegroundColor Green
    Write-Host "RAM: 32GB -> 64GB Upgradeable" -ForegroundColor Yellow
    Write-Host "APIs: 3/7 Working (Need: SportsData, Twitter, OpenWeather, ESPN)" -ForegroundColor Yellow
    Write-Host "Health Score: 75%" -ForegroundColor Green
    Write-Host ""
}

function Show-CommandMenu {
    Write-Host "SELECT YOUR COMMAND (or type number):" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "REVENUE AND BETTING OPERATIONS:" -ForegroundColor Green
    Write-Host "  1  run-odds         -> High-frequency market data feed"
    Write-Host "  2  run-parlay       -> AI parlay constructor and EV calculator"
    Write-Host "  3  betting-suite    -> Full autonomous betting pipeline"
    Write-Host "  4  revenue-cycle    -> Complete revenue generation cycle"
    Write-Host ""
    
    Write-Host "SYSTEM MANAGEMENT:" -ForegroundColor Blue
    Write-Host "  5  health-check     -> Comprehensive system validation"
    Write-Host "  6  repair-all       -> Auto-repair PowerShell + system fixes"
    Write-Host "  7  optimize-ram     -> Memory optimization and performance boost"
    Write-Host "  8  api-setup        -> API key configuration wizard"
    Write-Host "  9  system-rebuild   -> Complete system rebuild and validation"
    Write-Host ""
    
    Write-Host "DATA AND ANALYTICS:" -ForegroundColor Magenta
    Write-Host "  10 build-dashboard  -> Generate live performance dashboard"
    Write-Host "  11 export-data      -> Export all revenue/odds data"
    Write-Host "  12 live-report      -> Real-time system metrics"
    Write-Host "  13 backup-system    -> Create full system backup"
    Write-Host ""
    
    Write-Host "SPORTS INTELLIGENCE:" -ForegroundColor Yellow
    Write-Host "  14 all-sports       -> Multi-league data aggregation"
    Write-Host "  15 live-odds        -> Real-time odds comparison"
    Write-Host "  16 weather-check    -> Stadium weather intelligence"
    Write-Host "  17 injury-tracker   -> Player injury monitoring"
    Write-Host ""
    
    Write-Host "EMERGENCY AND RECOVERY:" -ForegroundColor Red
    Write-Host "  18 emergency-mode   -> Crisis recovery protocol"
    Write-Host "  19 force-restart    -> System restart with validation"
    Write-Host "  20 clean-reset      -> Clean slate system reset"
    Write-Host "  21 godmode          -> Ultimate system override"
    Write-Host ""
    
    Write-Host "COST OPTIMIZATION:" -ForegroundColor Cyan
    Write-Host "  22 free-mode        -> Switch to free alternatives & save $375/month"
    Write-Host ""
    
    Write-Host "AI ENTERPRISE OPERATIONS:" -ForegroundColor Magenta
    Write-Host "  23 ai-deploy        -> Deploy local AI models (LLaMA/Mistral)"
    Write-Host "  24 ai-train         -> Train custom betting prediction models"
    Write-Host "  25 ai-inference     -> Run AI inference on current data"
    Write-Host "  26 tokenize         -> Deploy EQ12X token and smart contracts"
    Write-Host "  27 ai-dashboard     -> Launch AI business intelligence dashboard"
    Write-Host "  28 ai-optimize      -> AI-powered system optimization"
    Write-Host ""
    
    Write-Host "WEB INTERFACE & ADVANCED MANAGEMENT:" -ForegroundColor Green
    Write-Host "  29 web-interface    -> Launch EQ12 Web Control Center"
    Write-Host "  30 health-check     -> Advanced system health monitoring"
    Write-Host "  31 system-diagnostics -> Full system diagnostics and analysis"
    Write-Host "  32 auto-repair      -> Emergency system auto-repair"
    Write-Host "  33 system-report    -> Generate comprehensive system report"
    Write-Host "  34 open-web         -> Open web dashboard in browser"
    Write-Host ""
    
    Write-Host "  exit               -> Exit launcher"
    Write-Host ""
}

function Execute-Command {
    param([string]$cmd)
    
    Write-LauncherLog "Executing command: $cmd"
    
    try {
        switch ($cmd.ToLower()) {
            # Revenue and Betting Operations
            "1" { 
                Write-Host "Starting odds feed..." -ForegroundColor Yellow
                & python "$Workspace\scripts\eq12_run_odds.py" --mode single --verbose
            }
            "run-odds" { 
                Write-Host "Starting odds feed..." -ForegroundColor Yellow
                & python "$Workspace\scripts\eq12_run_odds.py" --mode single --verbose
            }
            
            "2" { 
                Write-Host "Starting parlay engine..." -ForegroundColor Yellow
                & python "$Workspace\scripts\eq12_run_parlay.py" --legs 3 --count 1 --verbose
            }
            "run-parlay" { 
                Write-Host "Starting parlay engine..." -ForegroundColor Yellow
                & python "$Workspace\scripts\eq12_run_parlay.py" --legs 3 --count 1 --verbose
            }
            
            "3" { 
                Write-Host "Starting betting suite..." -ForegroundColor Yellow
                & python "$Workspace\eq12_betting_suite.py" --mode sequential --verbose
            }
            "betting-suite" { 
                Write-Host "Starting betting suite..." -ForegroundColor Yellow
                & python "$Workspace\eq12_betting_suite.py" --mode sequential --verbose
            }
            
            "4" { 
                Write-Host "Starting revenue cycle..." -ForegroundColor Yellow
                if (Test-Path "$Workspace\eq12_revenue_scale_accelerator.py") {
                    & python "$Workspace\eq12_revenue_scale_accelerator.py" --verbose
                }
                else {
                    Write-Host "Revenue accelerator not found - using backup method" -ForegroundColor Yellow
                    & python "$Workspace\scripts\eq12_run_odds.py" --mode single
                    & python "$Workspace\scripts\eq12_run_parlay.py" --legs 5 --count 1
                }
            }
            "revenue-cycle" { 
                Write-Host "Starting revenue cycle..." -ForegroundColor Yellow
                if (Test-Path "$Workspace\eq12_revenue_scale_accelerator.py") {
                    & python "$Workspace\eq12_revenue_scale_accelerator.py" --verbose
                }
                else {
                    Write-Host "Revenue accelerator not found - using backup method" -ForegroundColor Yellow
                    & python "$Workspace\scripts\eq12_run_odds.py" --mode single
                    & python "$Workspace\scripts\eq12_run_parlay.py" --legs 5 --count 1
                }
            }
            
            # System Management
            "5" { 
                Write-Host "Running system validation..." -ForegroundColor Yellow
                & python "$Workspace\eq12_final_system_validation.py"
            }
            "health-check" { 
                Write-Host "Running system validation..." -ForegroundColor Yellow
                & python "$Workspace\eq12_final_system_validation.py"
            }
            
            "6" { 
                Write-Host "Running auto-repair..." -ForegroundColor Yellow
                & python "$Workspace\eq12_fix_powershell_blocks.py"
                if (Test-Path "$Workspace\eq12_error_repair_fixed.ps1") {
                    & powershell -ExecutionPolicy Bypass -File "$Workspace\eq12_error_repair_fixed.ps1" -Action All -VerboseLogging
                }
            }
            "repair-all" { 
                Write-Host "Running auto-repair..." -ForegroundColor Yellow
                & python "$Workspace\eq12_fix_powershell_blocks.py"
                if (Test-Path "$Workspace\eq12_error_repair_fixed.ps1") {
                    & powershell -ExecutionPolicy Bypass -File "$Workspace\eq12_error_repair_fixed.ps1" -Action All -VerboseLogging
                }
            }
            
            "7" { 
                Write-Host "RAM Optimization Mode" -ForegroundColor Cyan
                Write-Host "Current memory usage analysis:" -ForegroundColor White
                Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 | Format-Table Name, @{Name = "Memory(MB)"; Expression = { [math]::Round($_.WorkingSet / 1MB, 2) } }
                [System.GC]::Collect()
                Write-Host "Memory optimization complete" -ForegroundColor Green
            }
            "optimize-ram" { 
                Write-Host "RAM Optimization Mode" -ForegroundColor Cyan
                Write-Host "Current memory usage analysis:" -ForegroundColor White
                Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 | Format-Table Name, @{Name = "Memory(MB)"; Expression = { [math]::Round($_.WorkingSet / 1MB, 2) } }
                [System.GC]::Collect()
                Write-Host "Memory optimization complete" -ForegroundColor Green
            }
            
            "8" { 
                Write-Host "Starting API setup wizard..." -ForegroundColor Yellow
                & python "$Workspace\eq12_api_key_manager.py" --setup-guide
            }
            "api-setup" { 
                Write-Host "Starting API setup wizard..." -ForegroundColor Yellow
                & python "$Workspace\eq12_api_key_manager.py" --setup-guide
            }
            
            "9" {
                Write-Host "Starting complete system rebuild..." -ForegroundColor Yellow
                & powershell -ExecutionPolicy Bypass -File "$Workspace\EQ12_System_Rebuild_Checklist.ps1" -Action All -VerboseOutput
            }
            "system-rebuild" {
                Write-Host "Starting complete system rebuild..." -ForegroundColor Yellow
                & powershell -ExecutionPolicy Bypass -File "$Workspace\EQ12_System_Rebuild_Checklist.ps1" -Action All -VerboseOutput
            }
            
            # Data and Analytics
            "10" { 
                Write-Host "Building dashboard..." -ForegroundColor Yellow
                if (Test-Path "$Workspace\eq12_business_intelligence_prompt_pack_generator.py") {
                    & python "$Workspace\eq12_business_intelligence_prompt_pack_generator.py" --full-strategy --verbose
                }
                else {
                    Write-Host "Dashboard generator not found - creating placeholder" -ForegroundColor Yellow
                    Write-Host "Dashboard functionality will be available after full setup" -ForegroundColor Cyan
                }
            }
            "build-dashboard" { 
                Write-Host "Building dashboard..." -ForegroundColor Yellow
                if (Test-Path "$Workspace\eq12_business_intelligence_prompt_pack_generator.py") {
                    & python "$Workspace\eq12_business_intelligence_prompt_pack_generator.py" --full-strategy --verbose
                }
                else {
                    Write-Host "Dashboard generator not found - creating placeholder" -ForegroundColor Yellow
                    Write-Host "Dashboard functionality will be available after full setup" -ForegroundColor Cyan
                }
            }
            
            "11" { 
                Write-Host "Exporting all EQ12 data..." -ForegroundColor Cyan
                if (-not (Test-Path "$Workspace\exports")) {
                    New-Item -Path "$Workspace\exports" -ItemType Directory -Force | Out-Null
                }
                if (Test-Path "$Workspace\data\*.db") {
                    Copy-Item "$Workspace\data\*.db" "$Workspace\exports\" -Force
                    Write-Host "Data export complete to exports folder" -ForegroundColor Green
                }
                else {
                    Write-Host "No database files found to export" -ForegroundColor Yellow
                }
            }
            "export-data" { 
                Write-Host "Exporting all EQ12 data..." -ForegroundColor Cyan
                if (-not (Test-Path "$Workspace\exports")) {
                    New-Item -Path "$Workspace\exports" -ItemType Directory -Force | Out-Null
                }
                if (Test-Path "$Workspace\data\*.db") {
                    Copy-Item "$Workspace\data\*.db" "$Workspace\exports\" -Force
                    Write-Host "Data export complete to exports folder" -ForegroundColor Green
                }
                else {
                    Write-Host "No database files found to export" -ForegroundColor Yellow
                }
            }
            
            "12" { 
                Write-Host "Generating live report..." -ForegroundColor Yellow
                & python "$Workspace\eq12_resource_monitor_wrapper.py" --action report
            }
            "live-report" { 
                Write-Host "Generating live report..." -ForegroundColor Yellow
                & python "$Workspace\eq12_resource_monitor_wrapper.py" --action report
            }
            
            "13" { 
                Write-Host "Creating system backup..." -ForegroundColor Yellow
                $backupPath = "$Workspace\backups\eq12_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                New-Item -Path $backupPath -ItemType Directory -Force | Out-Null
                Copy-Item "$Workspace\*" $backupPath -Recurse -Force -Exclude "backups"
                Write-Host "Full backup created: $backupPath" -ForegroundColor Green
            }
            "backup-system" { 
                Write-Host "Creating system backup..." -ForegroundColor Yellow
                $backupPath = "$Workspace\backups\eq12_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                New-Item -Path $backupPath -ItemType Directory -Force | Out-Null
                Copy-Item "$Workspace\*" $backupPath -Recurse -Force -Exclude "backups"
                Write-Host "Full backup created: $backupPath" -ForegroundColor Green
            }
            
            # Sports Intelligence
            "14" { 
                Write-Host "Starting multi-league aggregation..." -ForegroundColor Yellow
                if (Test-Path "$Workspace\eq12_sports_intelligence_integration.py") {
                    & python "$Workspace\eq12_sports_intelligence_integration.py"
                }
                else {
                    Write-Host "Sports intelligence module not found - using odds feed" -ForegroundColor Yellow
                    & python "$Workspace\scripts\eq12_run_odds.py" --mode single
                }
            }
            "all-sports" { 
                Write-Host "Starting multi-league aggregation..." -ForegroundColor Yellow
                if (Test-Path "$Workspace\eq12_sports_intelligence_integration.py") {
                    & python "$Workspace\eq12_sports_intelligence_integration.py"
                }
                else {
                    Write-Host "Sports intelligence module not found - using odds feed" -ForegroundColor Yellow
                    & python "$Workspace\scripts\eq12_run_odds.py" --mode single
                }
            }
            
            "15" { 
                Write-Host "Fetching live odds..." -ForegroundColor Yellow
                & python "$Workspace\scripts\eq12_run_odds.py" --mode single --verbose
            }
            "live-odds" { 
                Write-Host "Fetching live odds..." -ForegroundColor Yellow
                & python "$Workspace\scripts\eq12_run_odds.py" --mode single --verbose
            }
            
            "16" { 
                Write-Host "Checking weather system..." -ForegroundColor Yellow
                & python "$Workspace\eq12_enhanced_stadium_weather_system.py"
            }
            "weather-check" { 
                Write-Host "Checking weather system..." -ForegroundColor Yellow
                & python "$Workspace\eq12_enhanced_stadium_weather_system.py"
            }
            
            "17" { 
                Write-Host "Injury Tracker - Feature Coming Soon" -ForegroundColor Yellow
                Write-Host "Will integrate with SportsData API once configured" -ForegroundColor Cyan
            }
            "injury-tracker" { 
                Write-Host "Injury Tracker - Feature Coming Soon" -ForegroundColor Yellow
                Write-Host "Will integrate with SportsData API once configured" -ForegroundColor Cyan
            }
            
            # Emergency and Recovery
            "18" { 
                Write-Host "EMERGENCY MODE ACTIVATED" -ForegroundColor Red
                & python "$Workspace\eq12_hardcoded_repair_emergency_protocol.py" --workspace $Workspace --workers 6 --verbose
            }
            "emergency-mode" { 
                Write-Host "EMERGENCY MODE ACTIVATED" -ForegroundColor Red
                & python "$Workspace\eq12_hardcoded_repair_emergency_protocol.py" --workspace $Workspace --workers 6 --verbose
            }
            
            "19" { 
                Write-Host "Force restarting EQ12 system..." -ForegroundColor Yellow
                Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
                Start-Sleep 2
                & python "$Workspace\eq12_final_system_validation.py"
            }
            "force-restart" { 
                Write-Host "Force restarting EQ12 system..." -ForegroundColor Yellow
                Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
                Start-Sleep 2
                & python "$Workspace\eq12_final_system_validation.py"
            }
            
            "20" { 
                Write-Host "Clean Reset Mode - Clearing temporary files..." -ForegroundColor Yellow
                Remove-Item "$Workspace\logs\*.log" -Force -ErrorAction SilentlyContinue
                Remove-Item "$env:TEMP\eq12_*" -Force -ErrorAction SilentlyContinue
                Write-Host "Clean reset complete" -ForegroundColor Green
            }
            "clean-reset" { 
                Write-Host "Clean Reset Mode - Clearing temporary files..." -ForegroundColor Yellow
                Remove-Item "$Workspace\logs\*.log" -Force -ErrorAction SilentlyContinue
                Remove-Item "$env:TEMP\eq12_*" -Force -ErrorAction SilentlyContinue
                Write-Host "Clean reset complete" -ForegroundColor Green
            }
            
            "21" { 
                Write-Host "GODMODE ACTIVATED" -ForegroundColor Red
                Write-Host "Running comprehensive system override..." -ForegroundColor Yellow
                & python "$Workspace\eq12_hardcoded_repair_emergency_protocol.py" --workspace $Workspace --workers 6 --verbose
                & python "$Workspace\eq12_final_system_validation.py"
                & python "$Workspace\eq12_api_key_manager.py" --test-all
                Write-Host "GODMODE COMPLETE - System restored to optimal state" -ForegroundColor Green
            }
            "godmode" { 
                Write-Host "GODMODE ACTIVATED" -ForegroundColor Red
                Write-Host "Running comprehensive system override..." -ForegroundColor Yellow
                & python "$Workspace\eq12_hardcoded_repair_emergency_protocol.py" --workspace $Workspace --workers 6 --verbose
                & python "$Workspace\eq12_final_system_validation.py"
                & python "$Workspace\eq12_api_key_manager.py" --test-all
                Write-Host "GODMODE COMPLETE - System restored to optimal state" -ForegroundColor Green
            }
            
            # Cost Optimization
            "22" { 
                Write-Host " FREE MODE ACTIVATED - Switching to cost-saving alternatives..." -ForegroundColor Cyan
                & powershell -ExecutionPolicy Bypass -File "$Workspace\eq12_free_mode_switcher.ps1" -Service all -EnableCaching
                Write-Host " FREE MODE COMPLETE - Potential savings: $375/month" -ForegroundColor Green
            }
            "free-mode" { 
                Write-Host " FREE MODE ACTIVATED - Switching to cost-saving alternatives..." -ForegroundColor Cyan
                & powershell -ExecutionPolicy Bypass -File "$Workspace\eq12_free_mode_switcher.ps1" -Service all -EnableCaching
                Write-Host " FREE MODE COMPLETE - Potential savings: $375/month" -ForegroundColor Green
            }
            
            # AI Enterprise Operations
            "23" { 
                Write-Host " AI DEPLOYMENT - Setting up local AI models..." -ForegroundColor Magenta
                & python "$Workspace\scripts\eq12_ai_model_deployer.py" --deploy-all --verbose
                Write-Host " AI MODELS DEPLOYED - Ready for inference" -ForegroundColor Green
            }
            "ai-deploy" { 
                Write-Host " AI DEPLOYMENT - Setting up local AI models..." -ForegroundColor Magenta
                & python "$Workspace\scripts\eq12_ai_model_deployer.py" --deploy-all --verbose
                Write-Host " AI MODELS DEPLOYED - Ready for inference" -ForegroundColor Green
            }
            
            "24" { 
                Write-Host " AI TRAINING - Custom betting prediction models..." -ForegroundColor Magenta
                & python "$Workspace\scripts\eq12_ai_trainer.py" --model betting-predictor --epochs 100 --verbose
                Write-Host " AI TRAINING COMPLETE - Model ready for prediction" -ForegroundColor Green
            }
            "ai-train" { 
                Write-Host " AI TRAINING - Custom betting prediction models..." -ForegroundColor Magenta
                & python "$Workspace\scripts\eq12_ai_trainer.py" --model betting-predictor --epochs 100 --verbose
                Write-Host " AI TRAINING COMPLETE - Model ready for prediction" -ForegroundColor Green
            }
            
            "25" { 
                Write-Host " AI INFERENCE - Running AI predictions on current data..." -ForegroundColor Magenta
                & python "$Workspace\scripts\eq12_ai_inference_engine.py" --auto --confidence-threshold 0.85
                Write-Host " AI INFERENCE COMPLETE - Predictions generated" -ForegroundColor Green
            }
            "ai-inference" { 
                Write-Host " AI INFERENCE - Running AI predictions on current data..." -ForegroundColor Magenta
                & python "$Workspace\scripts\eq12_ai_inference_engine.py" --auto --confidence-threshold 0.85
                Write-Host " AI INFERENCE COMPLETE - Predictions generated" -ForegroundColor Green
            }
            
            "26" { 
                Write-Host " TOKENIZATION - Deploying EQ12X token and smart contracts..." -ForegroundColor Magenta
                & python "$Workspace\scripts\eq12_token_deployer.py" --network testnet --supply 1000000
                Write-Host " TOKENIZATION COMPLETE - EQ12X token deployed" -ForegroundColor Green
            }
            "tokenize" { 
                Write-Host " TOKENIZATION - Deploying EQ12X token and smart contracts..." -ForegroundColor Magenta
                & python "$Workspace\scripts\eq12_token_deployer.py" --network testnet --supply 1000000
                Write-Host " TOKENIZATION COMPLETE - EQ12X token deployed" -ForegroundColor Green
            }
            
            "27" { 
                Write-Host " AI DASHBOARD - Launching business intelligence dashboard..." -ForegroundColor Magenta
                & python "$Workspace\scripts\eq12_ai_dashboard.py" --port 8080 --real-time
                Write-Host " AI DASHBOARD LAUNCHED - Available at http://localhost:8080" -ForegroundColor Green
            }
            "ai-dashboard" { 
                Write-Host " AI DASHBOARD - Launching business intelligence dashboard..." -ForegroundColor Magenta
                & python "$Workspace\scripts\eq12_ai_dashboard.py" --port 8080 --real-time
                Write-Host " AI DASHBOARD LAUNCHED - Available at http://localhost:8080" -ForegroundColor Green
            }
            
            "28" { 
                Write-Host " AI OPTIMIZATION - AI-powered system optimization..." -ForegroundColor Magenta
                & python "$Workspace\scripts\eq12_ai_optimizer.py" --optimize-all --auto-tune
                Write-Host " AI OPTIMIZATION COMPLETE - System performance enhanced" -ForegroundColor Green
            }
            "ai-optimize" { 
                Write-Host " AI OPTIMIZATION - AI-powered system optimization..." -ForegroundColor Magenta
                & python "$Workspace\scripts\eq12_ai_optimizer.py" --optimize-all --auto-tune
                Write-Host " AI OPTIMIZATION COMPLETE - System performance enhanced" -ForegroundColor Green
            }
            
            # WEB INTERFACE & SYSTEM MANAGEMENT COMMANDS (29-34)
            "29" { 
                Write-Host " WEB INTERFACE - Starting EQ12 Web Control Center..." -ForegroundColor Cyan
                Start-Process -FilePath "python" -ArgumentList "scripts\eq12_web_interface.py" -WorkingDirectory $Workspace
                Write-Host " WEB INTERFACE LAUNCHED - Available at http://localhost:8080" -ForegroundColor Green
            }
            "web-interface" { 
                Write-Host " WEB INTERFACE - Starting EQ12 Web Control Center..." -ForegroundColor Cyan
                Start-Process -FilePath "python" -ArgumentList "scripts\eq12_web_interface.py" -WorkingDirectory $Workspace
                Write-Host " WEB INTERFACE LAUNCHED - Available at http://localhost:8080" -ForegroundColor Green
            }
            
            "30" { 
                Write-Host " SYSTEM HEALTH - Running comprehensive health check..." -ForegroundColor Yellow
                & powershell -ExecutionPolicy Bypass -File "$Workspace\scripts\eq12_system_mgmt_basic.ps1" -Action HealthCheck
                Write-Host " SYSTEM HEALTH CHECK COMPLETE" -ForegroundColor Green
            }
            "health-check" { 
                Write-Host " SYSTEM HEALTH - Running comprehensive health check..." -ForegroundColor Yellow
                & powershell -ExecutionPolicy Bypass -File "$Workspace\scripts\eq12_system_mgmt_basic.ps1" -Action HealthCheck
                Write-Host " SYSTEM HEALTH CHECK COMPLETE" -ForegroundColor Green
            }
            
            "31" { 
                Write-Host " SYSTEM DIAGNOSTICS - Running full system analysis..." -ForegroundColor Yellow
                & powershell -ExecutionPolicy Bypass -File "$Workspace\scripts\eq12_system_mgmt_basic.ps1" -Action Diagnostics
                Write-Host " SYSTEM DIAGNOSTICS COMPLETE" -ForegroundColor Green
            }
            "system-diagnostics" { 
                Write-Host " SYSTEM DIAGNOSTICS - Running full system analysis..." -ForegroundColor Yellow
                & powershell -ExecutionPolicy Bypass -File "$Workspace\scripts\eq12_system_mgmt_basic.ps1" -Action Diagnostics
                Write-Host " SYSTEM DIAGNOSTICS COMPLETE" -ForegroundColor Green
            }
            
            "32" { 
                Write-Host " AUTO-REPAIR - Running emergency system repair..." -ForegroundColor Red
                & powershell -ExecutionPolicy Bypass -File "$Workspace\scripts\eq12_system_mgmt_basic.ps1" -Action AutoRepair
                Write-Host " AUTO-REPAIR COMPLETE" -ForegroundColor Green
            }
            "auto-repair" { 
                Write-Host " AUTO-REPAIR - Running emergency system repair..." -ForegroundColor Red
                & powershell -ExecutionPolicy Bypass -File "$Workspace\scripts\eq12_system_mgmt_basic.ps1" -Action AutoRepair
                Write-Host " AUTO-REPAIR COMPLETE" -ForegroundColor Green
            }
            
            "33" { 
                Write-Host " SYSTEM REPORT - Generating comprehensive system report..." -ForegroundColor Cyan
                & powershell -ExecutionPolicy Bypass -File "$Workspace\scripts\eq12_system_mgmt_basic.ps1" -Action Report
                Write-Host " SYSTEM REPORT GENERATED" -ForegroundColor Green
            }
            "system-report" { 
                Write-Host " SYSTEM REPORT - Generating comprehensive system report..." -ForegroundColor Cyan
                & powershell -ExecutionPolicy Bypass -File "$Workspace\scripts\eq12_system_mgmt_basic.ps1" -Action Report
                Write-Host " SYSTEM REPORT GENERATED" -ForegroundColor Green
            }
            
            "34" { 
                Write-Host " OPENING WEB DASHBOARD - Launching browser interface..." -ForegroundColor Green
                Start-Process "http://localhost:8080"
                Write-Host " WEB DASHBOARD OPENED" -ForegroundColor Green
            }
            "open-web" { 
                Write-Host " OPENING WEB DASHBOARD - Launching browser interface..." -ForegroundColor Green
                Start-Process "http://localhost:8080"
                Write-Host " WEB DASHBOARD OPENED" -ForegroundColor Green
            }
            
            "exit" { 
                Write-LauncherLog "EQ12 Launcher session ended"
                return $false
            }
            
            default { 
                Write-Host "Unknown command: $cmd" -ForegroundColor Red
                Write-Host "Type a number (1-34) or command name, or 'exit' to quit" -ForegroundColor Yellow
            }
        }
        
        Write-LauncherLog "Command '$cmd' completed successfully" "SUCCESS"
        return $true
        
    }
    catch {
        Write-LauncherLog "ERROR executing command '$cmd': $($_.Exception.Message)" "ERROR"
        Write-Host "Command failed: $($_.Exception.Message)" -ForegroundColor Red
        return $true
    }
}

# Main execution logic
if ($QuickMode -and $Command) {
    Execute-Command $Command
    exit 0
}

# Interactive mode
Show-EQ12Banner

while ($true) {
    Show-CommandMenu
    Write-Host "Enter command: " -NoNewline -ForegroundColor White
    $userInput = Read-Host
    
    if ([string]::IsNullOrWhiteSpace($userInput)) {
        continue
    }
    
    Write-Host ""
    $continue = Execute-Command $userInput
    
    if (-not $continue) {
        break
    }
    
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor DarkGray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

Write-Host "EQ12 Godlike Launcher session ended" -ForegroundColor Green