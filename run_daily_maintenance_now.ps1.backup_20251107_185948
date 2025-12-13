# EQ12 Manual Maintenance Runner
# Location: C:\EQ12\run_daily_maintenance_now.ps1

# Import the recycle/hygiene module
Import-Module "C:\EQ12\scripts\eq12_recycle.ps1" -Force

# EQ12 Manual Maintenance Runner
# Location: C:\EQ12\run_daily_maintenance_now.ps1

# Force import of the recycle/hygiene module so functions are available
Import-Module "C:\EQ12\scripts\eq12_recycle.ps1" -Force

# Ensure Telegram keys (prompts only if missing)
try { Ensure-TelegramKeys } catch {}

# Run recycle report (JSON export into C:\EQ12\data)
$report = Export-RecycleReport -Format json
Write-Output "Recycle report created: $report"

# Clear browser data (Chrome + Edge). Add -Firefox if you want that too.
Clear-BrowserData -Chrome -Edge -Confirm

# Send Telegram notification
try {
    $msg = "✅ EQ12 Daily Maintenance (manual run) completed.`nRecycle report: $report"
    Send-Telegram $msg
    Write-Output "Telegram sent: $msg"
} catch {
    Write-Output "Telegram send failed: $($_.Exception.Message)"
}

Write-Output "=== EQ12 Maintenance Done ==="

# Ensure Telegram keys (prompts only if missing)
try { Ensure-TelegramKeys } catch {}

# Run recycle report (JSON export into C:\EQ12\data)
$report = Export-RecycleReport -Format json
Write-Output "Recycle report created: $report"

# Clear browser data (Chrome + Edge). Add -Firefox if you want that too.
Clear-BrowserData -Chrome -Edge -Confirm

# Send Telegram notification
try {
    $msg = "✅ EQ12 Daily Maintenance (manual run) completed.`nRecycle report: $report"
    Send-Telegram $msg
    Write-Output "Telegram sent: $msg"
} catch {
    Write-Output "Telegram send failed: $($_.Exception.Message)"
}

Write-Output "=== EQ12 Maintenance Done ==="
