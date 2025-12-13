# === EQ12 Startup Launcher ===
# Runs updates, odds, parlay, and Telegram alert in one go

Write-Output "=== EQ12 Startup Launcher ==="

# 1. Trigger updates (admin shell required)
& "C:\EQ12\scripts\eq12_update.ps1"

# 2. Run odds parser
python "C:\EQ12\scripts\odds_parser.py"

# 3. Run parlay builder
python "C:\EQ12\scripts\parlay_builder.py"

# 4. Send Telegram alert
try {
    $Token  = Get-Content "C:\EQ12\keys\tg_token.txt"
    $ChatID = Get-Content "C:\EQ12\keys\tg_chatid.txt"
    $msg = "EQ12 Launcher executed: updates, odds, parlay complete."
    Invoke-RestMethod -Uri "https://api.telegram.org/bot$Token/sendMessage?chat_id=$ChatID&text=$msg"
    Write-Output "Telegram alert sent."
} catch {
    Write-Output "Telegram alert failed. Check keys in C:\EQ12\keys"
}

Write-Output "=== EQ12 Startup Completed ==="
