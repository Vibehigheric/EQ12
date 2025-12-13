# === EQ12 Unified Master Launcher with Retry + Logging ===
$logPath = "C:\EQ12\logs\eq12_master_launcher.log"

function Write-Log($msg) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $msg" | Out-File $logPath -Append
}

function Retry-Command($ScriptBlock, $Retries = 3, $Delay = 5, $ActionName = "Action") {
    for ($i = 1; $i -le $Retries; $i++) {
        try {
            & $ScriptBlock
            Write-Log "$ActionName succeeded on attempt $i."
            return
        } catch {
            Write-Log ("$ActionName failed on attempt $i`: " + $_.Exception.Message)
            if ($i -lt $Retries) {
                Write-Log "Retrying in $Delay seconds..."
                Start-Sleep -Seconds $Delay
            } else {
                Write-Log "$ActionName failed after $Retries attempts."
            }
        }
    }
}

function Ensure-OddsAPIKey {
    $keyPath = "C:\EQ12\keys\oddsapi.txt"
    if (-not (Test-Path $keyPath)) {
        $key = Read-Host "Enter your Odds API Key"
        $key | Out-File $keyPath -Encoding UTF8
        Write-Host "Odds API key saved to $keyPath"
    }
    $env:ODDS_API_KEY = Get-Content $keyPath | Select-Object -First 1
}
Ensure-OddsAPIKey

Write-Log "=== EQ12 Master Launcher BEGIN ==="

# --- System Updates ---
Retry-Command -ScriptBlock { & "C:\EQ12\scripts\eq12_update.ps1" } -Retries 3 -Delay 10 -ActionName "Windows Update"

# --- Core Betting Stack ---
Retry-Command -ScriptBlock { python "C:\EQ12\scripts\odds_parser.py" } -Retries 3 -Delay 5 -ActionName "Odds Parser"
Retry-Command -ScriptBlock { python "C:\EQ12\scripts\parlay_builder.py" } -Retries 3 -Delay 5 -ActionName "Parlay Builder"

# --- EdgeGodParlays ---
Retry-Command -ScriptBlock { python "C:\EQ12\EdgeGodParlays\main.py" } -Retries 3 -Delay 5 -ActionName "EdgeGodParlays"

# --- EdgeGodUnified ---
Retry-Command -ScriptBlock { python "C:\EQ12\EQ12_Automation\EdgeGodUnified\main.py" } -Retries 3 -Delay 5 -ActionName "EdgeGodUnified"

# --- JobSearchBot ---
Retry-Command -ScriptBlock { python "C:\EQ12\EQ12_Automation\JobSearchBot\main.py" } -Retries 3 -Delay 5 -ActionName "JobSearchBot"

# --- Telegram Alert ---
Retry-Command -ScriptBlock {
    $Token = Get-Content "C:\EQ12\EQ12_Automation\keys\tg_token.txt"
    $ChatID = Get-Content "C:\EQ12\EQ12_Automation\keys\tg_chatid.txt"
    $msg = "✅ EQ12 Master Launcher executed successfully."
    Invoke-RestMethod -Uri "https://api.telegram.org/bot$Token/sendMessage?chat_id=$ChatID&text=$msg"
} -Retries 3 -Delay 10 -ActionName "Telegram Alert"

Write-Log "=== EQ12 Master Launcher END ==="
