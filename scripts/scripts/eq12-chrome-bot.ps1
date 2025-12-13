# eq12-chrome-bot.ps1
$Chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$ProfileDir = "C:\EQ12\profiles\chrome-bot"
if (-not (Test-Path $ProfileDir)) { New-Item -ItemType Directory -Path $ProfileDir | Out-Null }
$flags = @(
  '--user-data-dir="{0}"' -f $ProfileDir,
  '--profile-directory="Default"',
  '--disable-features=AutomationControlled',
  '--no-first-run',
  '--no-default-browser-check'
)
& $Chrome $flags
