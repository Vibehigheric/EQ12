# EQ12 Daily Maintenance Test
Import-Module "C:\EQ12\scripts\eq12_recycle.ps1" -Force
Write-Host "Running recycle report + browser cleanup (test run)" -ForegroundColor Cyan
eq12-report -Format json
eq12-clear-browser -Chrome -Edge -Confirm
Write-Host "Test run completed." -ForegroundColor Green
