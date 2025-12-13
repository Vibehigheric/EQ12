[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [ValidateSet("continuous", "single", "report", "install-deps")]
    [string]$Action = "single",

    [Parameter()]
    [int]$Interval = 15,

    [Parameter()]
    [int]$ReportDays = 7,

    [Parameter()]
    [switch]$Verbose
)

# EQ12 OpenAI Community Forum Monitor - PowerShell Wrapper
$ErrorActionPreference = "Stop"
if ($Verbose) { $VerbosePreference = "Continue" }

# Paths
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptRoot "eq12_community_monitor.py"
$LogsDir = "C:\EQ12\logs"

Write-Verbose "EQ12 Community Monitor - Action: $Action"

# Ensure logs directory exists
if (!(Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
    Write-Verbose "Created logs directory: $LogsDir"
}

# Check if Python script exists
if (!(Test-Path $PythonScript)) {
    Write-Error "Python script not found: $PythonScript"
    exit 1
}

try {
    switch ($Action) {
        "install-deps" {
            Write-Host "Installing Python dependencies..." -ForegroundColor Green

            $packages = @("feedparser", "requests", "PyGithub")

            foreach ($package in $packages) {
                Write-Host "Installing $package..." -ForegroundColor Cyan
                python -m pip install $package
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✓ $package installed" -ForegroundColor Green
                } else {
                    Write-Warning "Failed to install $package"
                }
            }

            Write-Host "Dependencies installation complete!" -ForegroundColor Green
        }

        "continuous" {
            Write-Host "Starting continuous monitoring (interval: $Interval min)..." -ForegroundColor Green
            Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow

            $pythonArgs = @("--continuous", "--interval", $Interval)
            python $PythonScript @pythonArgs
        }

        "single" {
            Write-Host "Running single monitoring cycle..." -ForegroundColor Green

            python $PythonScript --single

            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Monitoring completed successfully" -ForegroundColor Green

                $LogFile = Join-Path $LogsDir "community_monitor.log"
                if (Test-Path $LogFile) {
                    Write-Host "`nRecent activity:" -ForegroundColor Cyan
                    Get-Content $LogFile -Tail 10 | ForEach-Object {
                        if ($_ -match "INFO") {
                            Write-Host $_ -ForegroundColor White
                        } elseif ($_ -match "WARNING") {
                            Write-Host $_ -ForegroundColor Yellow
                        } elseif ($_ -match "ERROR") {
                            Write-Host $_ -ForegroundColor Red
                        }
                    }
                }
            } else {
                Write-Warning "Monitoring completed with errors"
            }
        }

        "report" {
            Write-Host "Generating activity report (last $ReportDays days)..." -ForegroundColor Green

            $reportOutput = python $PythonScript --report $ReportDays

            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Report generated" -ForegroundColor Green
                Write-Host "`nCommunity Activity Report:" -ForegroundColor Cyan
                Write-Host "=========================" -ForegroundColor Cyan

                try {
                    $report = $reportOutput | ConvertFrom-Json

                    Write-Host "Period: Last $($report.period_days) days" -ForegroundColor White
                    Write-Host "Total Posts: $($report.total_posts)" -ForegroundColor White
                    Write-Host "High Priority: $($report.high_priority)" -ForegroundColor Yellow
                    Write-Host "Actionable: $($report.actionable)" -ForegroundColor Green

                    if ($report.categories.PSObject.Properties.Count -gt 0) {
                        Write-Host "`nTop Categories:" -ForegroundColor Cyan
                        $report.categories.PSObject.Properties | Sort-Object Value -Descending | Select-Object -First 5 | ForEach-Object {
                            Write-Host "  $($_.Name): $($_.Value)" -ForegroundColor White
                        }
                    }

                } catch {
                    Write-Host $reportOutput
                }
            } else {
                Write-Warning "Report generation failed"
            }
        }
    }

} catch {
    Write-Error "Community monitoring failed: $_"
    exit 1
}

# Configuration status
Write-Host "`nConfiguration Status:" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan

$envVars = @(
    @{Name="SLACK_WEBHOOK_URL"; Desc="Slack notifications"},
    @{Name="TEAMS_WEBHOOK_URL"; Desc="Teams notifications"},
    @{Name="GITHUB_TOKEN"; Desc="GitHub issues"},
    @{Name="GITHUB_REPO"; Desc="Issue repository"}
)

foreach ($var in $envVars) {
    $value = [Environment]::GetEnvironmentVariable($var.Name)
    $status = if ($value) { "✓ Set" } else { "✗ Not set" }
    $color = if ($value) { "Green" } else { "Yellow" }

    Write-Host "$($var.Name) ($($var.Desc)): " -NoNewline
    Write-Host $status -ForegroundColor $color
}

if ($Action -eq "single") {
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "• Use -Action continuous for ongoing monitoring" -ForegroundColor Gray
    Write-Host "• Use -Action report for activity summary" -ForegroundColor Gray
    Write-Host "• Check logs in: $LogsDir" -ForegroundColor Gray
}
