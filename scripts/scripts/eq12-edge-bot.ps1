# eq12-edge-bot.ps1
$Edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$ProfileDir = "C:\EQ12\profiles\edge-bot"
if (-not (Test-Path $ProfileDir)) { New-Item -ItemType Directory -Path $ProfileDir | Out-Null }
$flags = @(
  '--user-data-dir="{0}"' -f $ProfileDir,
  '--profile-directory="Default"',
  '--disable-features=AutomationControlled',
  '--no-first-run',
  '--no-default-browser-check'
)
& $Edge $flags
