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
# Provides easy access to community monitoring functionality

$ErrorActionPreference = "Stop"
if ($Verbose) { $VerbosePreference = "Continue" }

# Paths
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptRoot "eq12_community_monitor.py"
$LogsDir = "C:\EQ12\logs"

Write-Verbose "EQ12 Community Monitor - PowerShell Wrapper"
Write-Verbose "Action: $Action"

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
            Write-Host "Installing Python dependencies for Community Monitor..." -ForegroundColor Green

            $RequiredPackages = @(
                "feedparser",
                "requests",
                "PyGithub"
            )

            foreach ($package in $RequiredPackages) {
                Write-Host "Installing $package..." -ForegroundColor Cyan
                python -m pip install $package
                if ($LASTEXITCODE -ne 0) {
                    Write-Warning "Failed to install $package"
                } else {
                    Write-Host "✓ $package installed" -ForegroundColor Green
                }
            }

            Write-Host "Dependencies installation complete!" -ForegroundColor Green
        }

        "continuous" {
            Write-Host "Starting continuous community monitoring (interval: $Interval minutes)..." -ForegroundColor Green
            Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow

            $args = @("--continuous", "--interval", $Interval)
            if ($Verbose) { $args += "--verbose" }

            python $PythonScript @args
        }

        "single" {
            Write-Host "Running single community monitoring cycle..." -ForegroundColor Green

            $args = @("--single")
            if ($Verbose) { $args += "--verbose" }

            python $PythonScript @args

            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Monitoring cycle completed successfully" -ForegroundColor Green

                # Show recent log entries
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
                Write-Warning "Monitoring cycle completed with errors"
            }
        }

        "report" {
            Write-Host "Generating community activity report (last $ReportDays days)..." -ForegroundColor Green

            $args = @("--report", $ReportDays)

            $reportOutput = python $PythonScript @args

            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Report generated successfully" -ForegroundColor Green
                Write-Host "`nCommunity Activity Report:" -ForegroundColor Cyan
                Write-Host "=========================" -ForegroundColor Cyan

                # Parse and display JSON report nicely
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

                    if ($report.top_keywords.PSObject.Properties.Count -gt 0) {
                        Write-Host "`nTop Keywords:" -ForegroundColor Cyan
                        $report.top_keywords.PSObject.Properties | Sort-Object Value -Descending | Select-Object -First 5 | ForEach-Object {
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

# Show configuration status
Write-Host "`nConfiguration Status:" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan

$envVars = @(
    @{ Name = "SLACK_WEBHOOK_URL"; Description = "Slack notifications" },
    @{ Name = "TEAMS_WEBHOOK_URL"; Description = "Teams notifications" },
    @{ Name = "GITHUB_TOKEN"; Description = "GitHub issue creation" },
    @{ Name = "GITHUB_REPO"; Description = "GitHub repository" }
)

foreach ($var in $envVars) {
    $value = [Environment]::GetEnvironmentVariable($var.Name)
    $status = if ($value) { "✓ Configured" } else { "✗ Not set" }
    $color = if ($value) { "Green" } else { "Yellow" }

    Write-Host "$($var.Name) ($($var.Description)): " -NoNewline
    Write-Host $status -ForegroundColor $color
}

Write-Host "`nTo configure notifications:" -ForegroundColor Cyan
Write-Host "1. Set SLACK_WEBHOOK_URL for Slack notifications" -ForegroundColor Gray
Write-Host "2. Set GITHUB_TOKEN for automatic issue creation" -ForegroundColor Gray
Write-Host "3. Set GITHUB_REPO (format: owner/repo) for issue destination" -ForegroundColor Gray

if ($Action -eq "single") {
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "• Run with -Action continuous for ongoing monitoring" -ForegroundColor Gray
    Write-Host "• Run with -Action report to see activity summary" -ForegroundColor Gray
    Write-Host "• Check logs in: $LogsDir" -ForegroundColor Gray
}
