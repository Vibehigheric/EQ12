# === EQ12 Master PowerShell Profile ===
Write-Output "`n=== EQ12 Master Profile Loaded ==="
Write-Output "Shortcuts: eq12-master | eq12-update | run-odds | run-parlay | backup-ai | netcheck | tg-alert | top-proc"

function eq12-master { & "C:\EQ12\scripts\eq12_master_launcher.ps1" }
function eq12-update { & "C:\EQ12\scripts\eq12_update.ps1" }
function run-odds { python "C:\EQ12\scripts\odds_parser.py" }
function run-parlay { python "C:\EQ12\scripts\parlay_builder.py" }

function netcheck {
    Test-Connection oddsapi.com -Count 4 | Out-File "C:\EQ12\logs\netcheck.txt" -Append
    Write-Output "Netcheck logged → C:\EQ12\logs\netcheck.txt"
}

function backup-ai {
    robocopy "C:\AI_Projects" "D:\Backups\AI_Projects" /MIR /LOG:"C:\EQ12\logs\backup.log"
    Write-Output "Backup complete → C:\EQ12\logs\backup.log"
}

function tg-alert {
    param([string]$msg)
    $Token  = Get-Content "C:\EQ12\EQ12_Automation\keys\tg_token.txt"
    $ChatID = Get-Content "C:\EQ12\EQ12_Automation\keys\tg_chatid.txt"
    Invoke-RestMethod -Uri "https://api.telegram.org/bot$Token/sendMessage?chat_id=$ChatID&text=$msg"
}

function top-proc {
    Get-Process | Sort CPU -Desc | Select -First 15
}

Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
