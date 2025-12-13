<![CDATA[<#
.SYNOPSIS
EQ12 Resource Monitor & Auto-Scaler - PowerShell Integration
    
.DESCRIPTION
Conservative auto-scaling system with monitoring, stress testing, and safety nets
    
Key Features:
- Starts with 6 workers (not 10) for safety
- Continuous resource monitoring (CPU, memory, I/O)
- Auto-scaling based on metrics (conservative approach)
- Emergency throttling on critical thresholds
- Comprehensive stress testing
- Detailed logging and reporting
    
.PARAMETER Action
Action to perform:
- monitor: Start continuous monitoring with auto-scaling
- test: Run stress tests
- report: Generate resource usage report
- demo: Quick demonstration
    
.PARAMETER Duration
Duration in minutes for monitoring or testing (default: 30)
    
.PARAMETER Workers
Initial worker count (default: 6, conservative)
    
.PARAMETER StressTest
Type of stress test: sustained, spike, memory_leak, exhaustion, all
    
.EXAMPLE
.\EQ12_RESOURCE_MONITOR.ps1 -Action demo
Quick demonstration of monitoring capabilities
    
.EXAMPLE
.\EQ12_RESOURCE_MONITOR.ps1 -Action monitor -Duration 60
Start 60-minute monitoring session with auto-scaling
    
.EXAMPLE
.\EQ12_RESOURCE_MONITOR.ps1 -Action test -StressTest sustained
Run sustained load stress test
    
.EXAMPLE
.\EQ12_RESOURCE_MONITOR.ps1 -Action report
Generate current resource usage report
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('monitor', 'test', 'report', 'demo')]
    [string]$Action = 'demo',
    
    [Parameter(Mandatory = $false)]
    [int]$Duration = 30,
    
    [Parameter(Mandatory = $false)]
    [ValidateRange(2, 10)]
    [int]$Workers = 6,
    
    [Parameter(Mandatory = $false)]
    [ValidateSet('sustained', 'spike', 'memory_leak', 'exhaustion', 'all')]
    [string]$StressTest = 'sustained'
)

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

# Ensure logs directory exists
$LogDir = Join-Path $RepoRoot 'logs\resource_monitor'
if (-not (Test-Path $LogDir)) {
    New-Item -Path $LogDir -ItemType Directory -Force | Out-Null
}

Write-Host ''
Write-Host '='*80 -ForegroundColor Cyan
Write-Host 'EQ12 RESOURCE MONITOR & AUTO-SCALER' -ForegroundColor Cyan
Write-Host '='*80 -ForegroundColor Cyan
Write-Host ''

# Display current system state
Write-Host '[SYSTEM STATE]' -ForegroundColor Yellow
$cpu = Get-CimInstance Win32_Processor
$memory = Get-CimInstance Win32_PhysicalMemory | Measure-Object Capacity -Sum
$disk = Get-PSDrive C

$cores = $cpu.NumberOfLogicalProcessors
$memoryGB = [Math]::Round($memory.Sum / 1GB, 2)
$diskFreeGB = [Math]::Round($disk.Free / 1GB, 2)

Write-Host "  CPU: $cores threads" -ForegroundColor Gray
Write-Host "  RAM: $memoryGB GB" -ForegroundColor Gray
Write-Host "  Disk Free: $diskFreeGB GB" -ForegroundColor Gray
Write-Host ''

# Python check
Write-Host '[CHECKING PYTHON...]' -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Error 'Python not found. Please install Python 3.12+'
}

# Check required modules
Write-Host '[CHECKING PYTHON MODULES...]' -ForegroundColor Yellow
$requiredModules = @('psutil')
foreach ($module in $requiredModules) {
    $installed = python -c "import $module; print('OK')" 2>&1
    if ($installed -match 'OK') {
        Write-Host "  ✓ $module installed" -ForegroundColor Green
    }
    else {
        Write-Host "  ✗ $module missing - installing..." -ForegroundColor Yellow
        python -m pip install $module --quiet
        Write-Host "  ✓ $module installed" -ForegroundColor Green
    }
}
Write-Host ''

# Execute action
switch ($Action) {
    'demo' {
        Write-Host '[RUNNING DEMO MODE]' -ForegroundColor Yellow
        Write-Host 'This will capture 5 resource snapshots and make a scaling decision' -ForegroundColor Gray
        Write-Host ''
        
        python (Join-Path $ScriptDir 'eq12_resource_monitor.py')
    }
    
    'monitor' {
        Write-Host '[STARTING CONTINUOUS MONITORING]' -ForegroundColor Yellow
        Write-Host "  Duration: $Duration minutes" -ForegroundColor Gray
        Write-Host "  Initial Workers: $Workers (conservative)" -ForegroundColor Gray
        Write-Host "  Log Directory: $LogDir" -ForegroundColor Gray
        Write-Host ''
        Write-Host 'Monitoring will auto-scale workers based on resource usage' -ForegroundColor Cyan
        Write-Host 'Press Ctrl+C to stop monitoring early' -ForegroundColor Cyan
        Write-Host ''
        
        # Create temporary monitoring script
        $monitorScript = @"
from eq12_resource_monitor import ResourceMonitor
import time

monitor = ResourceMonitor(log_dir=r'$LogDir')
monitor.current_workers = $Workers

print('[MONITORING STARTED]')
print(f'  Initial workers: {monitor.current_workers}')
print(f'  Duration: $Duration minutes')
print('')

try:
    monitor.start_monitoring(interval=30)
    
    # Run for specified duration
    end_time = time.time() + ($Duration * 60)
    while time.time() < end_time:
        time.sleep(60)
        
        # Status update every minute
        elapsed = int((time.time() - (end_time - ($Duration * 60))) / 60)
        metrics = monitor.metrics_history[-1] if monitor.metrics_history else None
        if metrics:
            print(f'[{elapsed}min] Workers: {monitor.current_workers}, '
                  f'CPU: {metrics.cpu_percent:.1f}%, '
                  f'Memory: {metrics.memory_percent:.1f}%')
    
    print('')
    print('[MONITORING COMPLETE]')
    monitor.stop_monitoring()
    
    # Generate final report
    report = monitor.export_metrics_report()
    print(report)
    
except KeyboardInterrupt:
    print('')
    print('[MONITORING STOPPED BY USER]')
    monitor.stop_monitoring()
    report = monitor.export_metrics_report()
    print(report)
"@
        
        $tempScript = Join-Path $env:TEMP 'eq12_monitor_temp.py'
        Set-Content -Path $tempScript -Value $monitorScript
        
        python $tempScript
        
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
    
    'test' {
        Write-Host '[RUNNING STRESS TESTS]' -ForegroundColor Yellow
        Write-Host "  Test Type: $StressTest" -ForegroundColor Gray
        Write-Host "  Workers: $Workers" -ForegroundColor Gray
        Write-Host ''
        Write-Host '⚠️  WARNING: Stress tests will consume significant resources' -ForegroundColor Yellow
        Write-Host 'Monitor system performance during tests' -ForegroundColor Yellow
        Write-Host ''
        
        $confirmation = Read-Host 'Continue with stress test? (y/N)'
        if ($confirmation -ne 'y') {
            Write-Host 'Stress test cancelled' -ForegroundColor Gray
            return
        }
        
        # Create stress test script
        $stressScript = @"
from eq12_stress_tester import *
import sys

print('')
print('='*80)
print('EQ12 STRESS TEST EXECUTION')
print('='*80)
print('')

test_type = '$StressTest'
workers = $Workers

if test_type == 'sustained':
    test = SustainedLoadTest(duration_minutes=10, workers=workers, tasks_per_sec=10)
elif test_type == 'spike':
    test = SpikeLoadTest(spike_workers=workers, spike_tasks=500, num_spikes=3)
elif test_type == 'memory_leak':
    test = MemoryLeakTest(workers=workers, iterations=50, leak_per_task_mb=2.0)
elif test_type == 'exhaustion':
    test = ResourceExhaustionTest(target_memory_percent=70.0)
elif test_type == 'all':
    print('Running comprehensive test suite...')
    run_all_stress_tests()
    sys.exit(0)

print(f'Running test: {test.name}')
print('')
result = test.run()

print('')
print('='*80)
print('TEST RESULTS')
print('='*80)
for key, value in result.items():
    if not isinstance(value, dict):
        print(f'  {key}: {value}')
"@
        
        $tempStressScript = Join-Path $env:TEMP 'eq12_stress_temp.py'
        Set-Content -Path $tempStressScript -Value $stressScript
        
        python $tempStressScript
        
        Remove-Item $tempStressScript -Force -ErrorAction SilentlyContinue
    }
    
    'report' {
        Write-Host '[GENERATING RESOURCE REPORT]' -ForegroundColor Yellow
        Write-Host ''
        
        # Quick resource snapshot
        $reportScript = @"
from eq12_resource_monitor import ResourceMonitor
import json

monitor = ResourceMonitor(log_dir=r'$LogDir')

# Capture 5 snapshots
print('[CAPTURING RESOURCE SNAPSHOTS...]')
for i in range(5):
    metrics = monitor.capture_metrics()
    print(f'  {i+1}. CPU: {metrics.cpu_percent:.1f}%, Memory: {metrics.memory_percent:.1f}%')
    import time
    time.sleep(2)

print('')
print('[GENERATING REPORT...]')
report = monitor.export_metrics_report()
print(report)

# Check for recent decision logs
import os
from pathlib import Path
log_files = list(Path(r'$LogDir').glob('scaling_decisions_*.jsonl'))
if log_files:
    print('')
    print('[RECENT SCALING DECISIONS]')
    latest = max(log_files, key=os.path.getmtime)
    with open(latest, 'r') as f:
        lines = f.readlines()
        for line in lines[-5:]:
            decision = json.loads(line)
            print(f'  {decision["timestamp"]}: {decision["action"].upper()} - {decision["reason"]}')
else:
    print('')
    print('[NO SCALING DECISIONS LOGGED YET]')
"@
        
        $tempReportScript = Join-Path $env:TEMP 'eq12_report_temp.py'
        Set-Content -Path $tempReportScript -Value $reportScript
        
        python $tempReportScript
        
        Remove-Item $tempReportScript -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ''
Write-Host '='*80 -ForegroundColor Cyan
Write-Host '✅ COMPLETE' -ForegroundColor Green
Write-Host '='*80 -ForegroundColor Cyan
Write-Host ''
Write-Host '[LOGS LOCATION]' -ForegroundColor Yellow
Write-Host "  $LogDir" -ForegroundColor Gray
Write-Host ''
]]>