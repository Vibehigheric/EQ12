# EQ12 2025 Master Orchestrator Wrapper
# PowerShell launcher for unified revenue automation

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet("all", "single", "health", "dashboard")]
    [string]$Mode = "all",
    
    [Parameter()]
    [ValidateSet("betting_intelligence", "prompt_monetization", "pacer_legal", "travel_automation", "content_empire")]
    [string]$Stream,
    
    [Parameter()]
    [switch]$Parallel,
    
    [Parameter()]
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$RepoRoot = "C:\EQ12_BROKEN_20251122_210342"
$OrchestratorScript = Join-Path $RepoRoot "EQ12_2025_MASTER_ORCHESTRATOR.py"
$ConfigFile = Join-Path $RepoRoot "config\master_config.json"

# Banner
Write-Host "`n" -NoNewline
Write-Host "╔═══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                   ║" -ForegroundColor Cyan
Write-Host "║      EQ12 2025 MASTER REVENUE ORCHESTRATOR                        ║" -ForegroundColor Cyan
Write-Host "║      Target: `$12M Annual Revenue                                  ║" -ForegroundColor Cyan
Write-Host "║      5 Revenue Streams | Unified Automation                       ║" -ForegroundColor Cyan
Write-Host "║                                                                   ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ Python not found in PATH" -ForegroundColor Red
    exit 1
}

# Check orchestrator script exists
if (-not (Test-Path $OrchestratorScript)) {
    Write-Host "✗ Orchestrator script not found: $OrchestratorScript" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Orchestrator: $OrchestratorScript" -ForegroundColor Green

# Check config exists
if (-not (Test-Path $ConfigFile)) {
    Write-Host "⚠ Config file not found, will be created: $ConfigFile" -ForegroundColor Yellow
}

# Build Python command
$pythonArgs = @($OrchestratorScript, "--mode", $Mode, "--config", $ConfigFile)

if ($Stream) {
    $pythonArgs += @("--stream", $Stream)
}

if ($Parallel) {
    $pythonArgs += "--parallel"
    Write-Host "⚡ Parallel execution enabled (faster but riskier)" -ForegroundColor Yellow
}

# Display execution plan
Write-Host "`n📋 EXECUTION PLAN:" -ForegroundColor Cyan
Write-Host "  Mode:     $Mode" -ForegroundColor White
if ($Stream) {
    Write-Host "  Stream:   $Stream" -ForegroundColor White
}
Write-Host "  Config:   $ConfigFile" -ForegroundColor White
Write-Host "  Parallel: $($Parallel.IsPresent)" -ForegroundColor White

Write-Host "`n🚀 Starting orchestrator..." -ForegroundColor Green
Write-Host ("=" * 80) -ForegroundColor Gray
Write-Host ""

# Execute Python orchestrator
try {
    $process = Start-Process `
        -FilePath "python" `
        -ArgumentList $pythonArgs `
        -NoNewWindow `
        -Wait `
        -PassThru
    
    $exitCode = $process.ExitCode
    
    Write-Host ""
    Write-Host ("=" * 80) -ForegroundColor Gray
    
    if ($exitCode -eq 0) {
        Write-Host "✅ Orchestrator completed successfully" -ForegroundColor Green
        
        # Display quick stats if config exists
        if (Test-Path $ConfigFile) {
            $config = Get-Content $ConfigFile | ConvertFrom-Json
            Write-Host "`n📊 QUICK STATS:" -ForegroundColor Cyan
            Write-Host "  Total Executions:  $($config.performance_metrics.total_executions)" -ForegroundColor White
            Write-Host "  Successful:        $($config.performance_metrics.successful_executions)" -ForegroundColor Green
            Write-Host "  Failed:            $($config.performance_metrics.failed_executions)" -ForegroundColor Red
            
            $successRate = if ($config.performance_metrics.total_executions -gt 0) {
                ($config.performance_metrics.successful_executions / $config.performance_metrics.total_executions * 100)
            }
            else { 0 }
            Write-Host "  Success Rate:      $($successRate.ToString('F1'))%" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "❌ Orchestrator failed with exit code: $exitCode" -ForegroundColor Red
    }
    
    exit $exitCode
    
}
catch {
    Write-Host "💥 Fatal error executing orchestrator:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
