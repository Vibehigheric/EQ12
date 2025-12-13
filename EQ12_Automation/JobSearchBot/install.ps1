Write-Host "=== EQ12 JobSearchBot Installer ==="

$base = "C:\EQ12_Automation\JobSearchBot"
if (!(Test-Path $base)) {
  New-Item -ItemType Directory -Force -Path $base | Out-Null
}

Write-Host "Copying files..."
Copy-Item -Path ".\*" -Destination $base -Recurse -Force

Write-Host "Installing Python dependencies..."
pip install -r "$base\requirements.txt"

Write-Host ""
Write-Host "NEXT STEPS:"
Write-Host "1) Place your Google 'credentials.json' into: $base"
Write-Host "2) Edit $base\config.json with your email, keywords, locations, and API keys."
Write-Host "3) Run once to authenticate Gmail:"
Write-Host "   python `"$base\job_alert_runner.py`""
Write-Host "4) Add a Windows Task Scheduler job to run daily at 7:00 AM:"
Write-Host "   Program/script: python"
Write-Host "   Arguments: `"$base\job_alert_runner.py`""
Write-Host "Done!"
