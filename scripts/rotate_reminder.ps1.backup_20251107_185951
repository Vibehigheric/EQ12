<#
rotate_reminder.ps1
Reminder helper that prompts the user to rotate API keys and launches the interactive secret storage helper.
If a Telegram bot token and chat id are present in C:\EQ12\keys, it will attempt to send a Telegram message before opening the prompt.
#>
[CmdletBinding()]
param()

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$keysDir = Join-Path (Split-Path -Parent $scriptDir) 'keys'

# Try to send Telegram reminder if possible
$telegramTokenPath = Join-Path $keysDir 'telegram.txt'
$telegramIdPath = Join-Path $keysDir 'telegram_id.txt'
if (Test-Path $telegramTokenPath -and Test-Path $telegramIdPath) {
    try {
        $token = Get-Content $telegramTokenPath -Raw
        $chatId = Get-Content $telegramIdPath -Raw
        $message = "Reminder: Please rotate your API keys and secrets for EQ12. You can run the local helper to update keys now."
        $uri = "https://api.telegram.org/bot$token/sendMessage"
        $body = @{ chat_id = $chatId; text = $message }
        Invoke-RestMethod -Uri $uri -Method Post -Body $body -ErrorAction Stop | Out-Null
        Write-Host "Telegram reminder sent to chat id $chatId"
    } catch {
        Write-Host "Failed to send Telegram reminder: $($_.Exception.Message)"
    }
}

Write-Host "\n=== EQ12 Secret Rotation Reminder ===\n"
Write-Host "It's time to rotate your API keys and secrets."
Write-Host "Press Enter to open the interactive helper and update keys now, or Ctrl+C to skip."

# Wait for Enter key
[void][System.Console]::ReadLine()

# Launch the interactive store_secrets.ps1 in a new PowerShell window so the scheduled task (if any) doesn't run headless
$storeScript = Join-Path $scriptDir 'store_secrets.ps1'
if (-not (Test-Path $storeScript)) {
    Write-Host "Could not find $storeScript. Please run it manually from the repo scripts folder."
    exit 1
}

$pwshExe = Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
$arg = "-NoExit -ExecutionPolicy Bypass -File `"$storeScript`""
Start-Process -FilePath $pwshExe -ArgumentList $arg
Write-Host "Launched interactive helper in a new PowerShell window."
""