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
            Write-Log "$ActionName failed on attempt $i: $_"
            if ($i -lt $Retries) {
                Write-Log "Retrying in $Delay seconds..."
                Start-Sleep -Seconds $Delay
            } else {
                Write-Log "$ActionName failed after $Retries attempts."
            }
        }
    }
}

Write-Log "=== EQ12 Master Launcher BEGIN ==="

# --- System Updates ---
Retry-Command { & "C:\EQ12\scripts\eq12_update.ps1" } 3 10 "Windows Update"

# --- Core Betting Stack ---
Retry-Command { python "C:\EQ12\scripts\odds_parser.py" } 3 5 "Odds Parser"
Retry-Command { python "C:\EQ12\scripts\parlay_builder.py" } 3 5 "Parlay Builder"

# --- EdgeGodParlays ---
Retry-Command { python "C:\EQ12\EdgeGodParlays\main.py" } 3 5 "EdgeGodParlays"

# --- EdgeGodUnified ---
Retry-Command { python "C:\EQ12\EQ12_Automation\EdgeGodUnified\main.py" } 3 5 "EdgeGodUnified"

# --- JobSearchBot ---
Retry-Command { python "C:\EQ12\EQ12_Automation\JobSearchBot\main.py" } 3 5 "JobSearchBot"

# --- Telegram Alert ---
Retry-Command {
    $Token  = Get-Content "C:\EQ12\EQ12_Automation\keys\tg_token.txt"
    $ChatID = Get-Content "C:\EQ12\EQ12_Automation\keys\tg_chatid.txt"
    $msg = "✅ EQ12 Master Launcher executed successfully."
    Invoke-RestMethod -Uri "https://api.telegram.org/bot$Token/sendMessage?chat_id=$ChatID&text=$msg"
} 3 10 "Telegram Alert"

Write-Log "=== EQ12 Master Launcher END ==="
