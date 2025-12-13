Write-Host "=== EdgeGodUnified Installer ==="
$base = "C:\EQ12_Automation\EdgeGodUnified"
if (!(Test-Path $base)) { New-Item -ItemType Directory -Force -Path $base | Out-Null }

Copy-Item -Path ".\*" -Destination $base -Recurse -Force

pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib requests

Write-Host "NEXT:"
Write-Host "1) Put credentials.json in $base"
Write-Host "2) Edit $base\config.json (email, Telegram, rules)"
Write-Host "3) Run once: python `"$base\runner.py`""
Write-Host "4) Schedule daily run in Task Scheduler"

pip install pandas openpyxl xlrd
