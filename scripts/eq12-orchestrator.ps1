# PowerShell wrapper for eq12_orchestrator.py
param(
    [Switch]$Dry
)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$py = if (Test-Path 'C:\EQ12\.venv\Scripts\python.exe') { 'C:\EQ12\.venv\Scripts\python.exe' } else { 'python' }
$script = Join-Path $scriptDir 'eq12_orchestrator.py'
$args = @()
if ($Dry) { $args += '--dry' }
& $py $script $args
