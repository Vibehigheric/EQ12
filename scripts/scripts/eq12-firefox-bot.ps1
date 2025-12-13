# eq12-firefox-bot.ps1
$FF = "C:\Program Files\Mozilla Firefox\firefox.exe"
$ProfileDir = "C:\EQ12\profiles\firefox-bot"
if (-not (Test-Path $ProfileDir)) { New-Item -ItemType Directory -Path $ProfileDir | Out-Null }
& $FF -profile $ProfileDir
