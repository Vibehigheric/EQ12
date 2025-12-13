# EQ12 Prompt Generator Wrapper
# PowerShell wrapper for eq12_prompt_generator.py

[CmdletBinding()]
param(
    [Parameter(HelpMessage = "Number of prompts to generate")]
    [int]$Count = 100,
    
    [Parameter(HelpMessage = "Generate prompts for specific category")]
    [string]$Category,
    
    [Parameter(HelpMessage = "Output file path")]
    [string]$OutputFile = "$PSScriptRoot\..\prompts\generated_prompts.txt",
    
    [Parameter(HelpMessage = "Path to database")]
    [string]$Database = "$PSScriptRoot\..\logs\prompt_execution.db",
    
    [Parameter(HelpMessage = "Show quality metrics")]
    [switch]$Analyze,
    
    [Parameter(HelpMessage = "Show top N topics")]
    [int]$TopTopics
)

Write-Host "`n=== EQ12 Prompt Generator ===" -ForegroundColor Cyan
Write-Host "Intelligent prompt generation from learned patterns`n" -ForegroundColor Gray

# Build command
$pythonCmd = "python"
$scriptPath = "$PSScriptRoot\eq12_prompt_generator.py"

$arguments = @(
    $scriptPath,
    "--db", $Database,
    "--count", $Count,
    "--output", $OutputFile
)

if ($Category) {
    $arguments += @("--category", $Category)
}

if ($Analyze) {
    $arguments += "--analyze"
}

if ($TopTopics -gt 0) {
    $arguments += @("--top-topics", $TopTopics)
}

# Execute
Write-Verbose "Command: $pythonCmd $($arguments -join ' ')"
& $pythonCmd $arguments

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Prompt generation successful!" -ForegroundColor Green
    
    if (Test-Path $OutputFile) {
        $lines = (Get-Content $OutputFile | Measure-Object -Line).Lines
        Write-Host "Generated file: $OutputFile" -ForegroundColor Cyan
        Write-Host "Total lines: $lines" -ForegroundColor Gray
    }
}
else {
    Write-Error "Prompt generation failed with exit code: $LASTEXITCODE"
}
