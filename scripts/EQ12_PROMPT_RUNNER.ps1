<#
.SYNOPSIS
    EQ12 Prompt Runner - PowerShell wrapper for batch prompt execution

.DESCRIPTION
    Executes ChatGPT prompts in batches, learns from responses, and updates knowledge base
    
.EXAMPLE
    .\EQ12_PROMPT_RUNNER.ps1 -StartPrompt 1 -Count 50 -BatchSize 10
    
.EXAMPLE
    .\EQ12_PROMPT_RUNNER.ps1 -ReportOnly
#>

[CmdletBinding()]
param(
    [int]$StartPrompt = 1,
    [int]$Count = 100,
    [int]$BatchSize = 20,
    [double]$DelaySeconds = 1.0,
    [switch]$ReportOnly,
    [switch]$ContinuousMode,
    [switch]$Parallel,
    [int]$Workers = 0,
    [switch]$TurboMode,
    [string]$PromptsFile = "C:\EQ12_BROKEN_20251122_210342\prompts\chatgpt_prompts_20000_nov2025.txt",
    [string]$DatabasePath = "C:\EQ12_BROKEN_20251122_210342\logs\prompt_execution.db"
)

$ErrorActionPreference = 'Stop'

# Detect system capabilities
$cpuCount = (Get-WmiObject -Class Win32_Processor).NumberOfLogicalProcessors
$ramGB = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)

Write-Host "`n=== EQ12 Prompt Runner - FULL SYSTEM CAPABILITIES ===" -ForegroundColor Cyan
Write-Host "System: $cpuCount CPUs, $ramGB GB RAM" -ForegroundColor Green
Write-Host "Database: $DatabasePath" -ForegroundColor Yellow
Write-Host "Prompts: $PromptsFile" -ForegroundColor Yellow

# Enable TurboMode automatically for high-spec systems
if ($TurboMode -or ($cpuCount -ge 8 -and $ramGB -ge 16)) {
    $Parallel = $true
    if ($Workers -eq 0) {
        $Workers = [Math]::Min($cpuCount * 2, 16)
    }
    $DelaySeconds = 0.5
    Write-Host "TURBO MODE ENABLED: $Workers workers, parallel processing" -ForegroundColor Magenta
}

# Ensure Python script exists
$pythonScript = "C:\EQ12_BROKEN_20251122_210342\scripts\eq12_prompt_executor.py"
if (-not (Test-Path $pythonScript)) {
    Write-Host "Error: Python executor not found at $pythonScript" -ForegroundColor Red
    exit 1
}

# Build command with full capabilities
$cmd = "python `"$pythonScript`" --prompts `"$PromptsFile`" --db `"$DatabasePath`""

if ($ReportOnly) {
    $cmd += " --report-only"
}
else {
    $cmd += " --start $StartPrompt --count $Count --batch-size $BatchSize --delay $DelaySeconds"
    
    if ($Parallel) {
        $cmd += " --parallel"
    }
    
    if ($Workers -gt 0) {
        $cmd += " --workers $Workers"
    }
}

Write-Host "`nExecuting: $cmd" -ForegroundColor Green
Write-Host ""

if ($ContinuousMode) {
    Write-Host "CONTINUOUS MODE - Processing all 20,000 prompts in batches" -ForegroundColor Magenta
    $currentStart = $StartPrompt
    $totalPrompts = 20000
    
    while ($currentStart -lt $totalPrompts) {
        $remaining = $totalPrompts - $currentStart + 1
        $batchCount = [Math]::Min($Count, $remaining)
        
        Write-Host "`n=== BATCH: Prompts $currentStart to $($currentStart + $batchCount - 1) ===" -ForegroundColor Cyan
        
        $batchCmd = "python `"$pythonScript`" --prompts `"$PromptsFile`" --db `"$DatabasePath`" --start $currentStart --count $batchCount --batch-size $BatchSize --delay $DelaySeconds"
        
        if ($Parallel) {
            $batchCmd += " --parallel"
        }
        
        if ($Workers -gt 0) {
            $batchCmd += " --workers $Workers"
        }
        
        Invoke-Expression $batchCmd
        
        $currentStart += $batchCount
        
        # Generate interim report
        Write-Host "`n--- INTERIM REPORT ---" -ForegroundColor Yellow
        $reportCmd = "python `"$pythonScript`" --prompts `"$PromptsFile`" --db `"$DatabasePath`" --report-only"
        Invoke-Expression $reportCmd
        
        # Pause between large batches
        if ($currentStart -lt $totalPrompts) {
            Write-Host "`nPausing 30 seconds before next batch..." -ForegroundColor Yellow
            Start-Sleep -Seconds 30
        }
    }
    
    Write-Host "`n=== ALL PROMPTS PROCESSED ===" -ForegroundColor Green
}
else {
    # Single execution
    Invoke-Expression $cmd
}

# Open database for inspection (optional)
Write-Host "`nDatabase location: $DatabasePath" -ForegroundColor Cyan
Write-Host "To view: DB Browser for SQLite or any SQLite viewer" -ForegroundColor Gray
