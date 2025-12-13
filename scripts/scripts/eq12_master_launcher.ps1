# === EQ12 Unified Master Launcher (Ultra Fixed) ===

# --- Safety: try to unblock any downloaded files under C:\EQ12 so RemoteSigned won't block ---
try { Get-ChildItem 'C:\EQ12' -Recurse -Include *.ps1,*.psm1,*.psd1,*.xml | Unblock-File -ErrorAction SilentlyContinue } catch {}

# Ensure folders
$logDir = "C:\EQ12\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$logPath = Join-Path $logDir "eq12_master_launcher.log"

function Write-Log($msg) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $msg" | Out-File $logPath -Append
}

# --- Simple log rotation (keep current + 4 previous = 5 total) ---
function Rotate-Log {
    if (Test-Path $logPath) {
        for ($i = 4; $i -ge 1; $i--) {
            $src = "$logPath.$i"
            $dst = "$logPath." + ($i + 1)
            if (Test-Path $src) { Move-Item -Path $src -Destination $dst -Force }
        }
        Move-Item -Path $logPath -Destination "$logPath.1" -Force
    }
}
Rotate-Log

Write-Log "EQ12 Master Launcher initialized"
Write-Host "[INIT] EQ12 Master Launcher initialized" -ForegroundColor Cyan

# --- API Key Prompt (only if missing/empty) ---
$tokenPath  = "C:\EQ12\keys\tg_token.txt"
$chatIDPath = "C:\EQ12\keys\tg_chatid.txt"
if (-not (Test-Path (Split-Path $tokenPath))) { New-Item -ItemType Directory -Path (Split-Path $tokenPath) | Out-Null }

if (-not (Test-Path $tokenPath) -or -not (Get-Content $tokenPath -ErrorAction SilentlyContinue)) {
    $tgToken = Read-Host "Enter your Telegram Bot Token"
    Set-Content -Path $tokenPath -Value $tgToken
    Write-Log "Telegram token saved to keys folder"
}
if (-not (Test-Path $chatIDPath) -or -not (Get-Content $chatIDPath -ErrorAction SilentlyContinue)) {
    $tgChatID = Read-Host "Enter your Telegram Chat ID"
    Set-Content -Path $chatIDPath -Value $tgChatID
    Write-Log "Telegram chat id saved to keys folder"
}

# --- Counters for summary ---
$global:EQ12_Success = 0
$global:EQ12_Retry   = 0
$global:EQ12_Fail    = 0

function Retry-Command {
    param(
        [scriptblock]$ScriptBlock,
        [int]$Retries = 3,
        [int]$Delay = 5,
        [string]$ActionName = "Action"
    )
    for ($i = 1; $i -le $Retries; $i++) {
        try {
            & $ScriptBlock
            Write-Host ("[OK] {0} succeeded on attempt {1}" -f $ActionName,$i) -ForegroundColor Green
            Write-Log  ("{0} succeeded on attempt {1}" -f $ActionName,$i)
            $global:EQ12_Success++
            return
        } catch {
            Write-Host ("[FAIL] {0} failed on attempt {1}" -f $ActionName,$i) -ForegroundColor Red
            Write-Log  ("{0} failed on attempt {1}: " -f $ActionName,$i)
            Write-Log  (($_ | Out-String).Trim())
            if ($i -lt $Retries) {
                Write-Host ("[RETRY] Retrying in {0} seconds..." -f $Delay) -ForegroundColor Yellow
                Write-Log  ("Retrying in {0} seconds..." -f $Delay)
                $global:EQ12_Retry++
                Start-Sleep -Seconds $Delay
            } else {
                $global:EQ12_Fail++
                Write-Host ("[FAIL] {0} failed after {1} attempts" -f $ActionName,$Retries) -ForegroundColor Red
                Write-Log  ("{0} failed after {1} attempts" -f $ActionName,$Retries)
            }
        }
    }
}

# --- Actions ---

Write-Host "[STEP] Windows Update..." -ForegroundColor Cyan
Write-Log  "Running Windows Update..."
Retry-Command { & "C:\EQ12\scripts\eq12_update.ps1" } 3 10 "Windows Update"

Write-Host "[STEP] Odds Parser..." -ForegroundColor Cyan
Write-Log  "Running Odds Parser..."
Retry-Command { python "C:\EQ12\scripts\odds_parser.py" } 3 5 "Odds Parser"

Write-Host "[STEP] Parlay Builder..." -ForegroundColor Cyan
Write-Log  "Running Parlay Builder..."
Retry-Command { python "C:\EQ12\scripts\parlay_builder.py" } 3 5 "Parlay Builder"

Write-Host "[STEP] EdgeGodParlays..." -ForegroundColor Cyan
Write-Log  "Running EdgeGodParlays..."
Retry-Command { python "C:\EQ12\EdgeGodParlays\main.py" } 3 5 "EdgeGodParlays"

Write-Host "[STEP] EdgeGodUnified..." -ForegroundColor Cyan
Write-Log  "Running EdgeGodUnified..."
Retry-Command { python "C:\EQ12\EQ12_Automation\EdgeGodUnified\main.py" } 3 5 "EdgeGodUnified"

Write-Host "[STEP] JobSearchBot..." -ForegroundColor Cyan
Write-Log  "Running JobSearchBot..."
Retry-Command { python "C:\EQ12\EQ12_Automation\JobSearchBot\main.py" } 3 5 "JobSearchBot"

# --- Telegram Notify ---
try {
    $Token  = (Get-Content $tokenPath -ErrorAction Stop).Trim()
    $ChatID = (Get-Content $chatIDPath -ErrorAction Stop).Trim()
    if ($Token -and $ChatID) {
        $msg = "EQ12 Master Launcher executed."
        Write-Host "[STEP] Telegram alert..." -ForegroundColor Cyan
        Write-Log  "Sending Telegram alert..."
        # Escape & as `&
        $url = "https://api.telegram.org/bot{0}/sendMessage?chat_id={1}`&text={2}" -f $Token,$ChatID,[uri]::EscapeDataString($msg)
        Retry-Command { Invoke-RestMethod -Uri $url } 3 10 "Telegram Alert"
    } else {
        Write-Host "[WARN] Telegram keys empty; skipping alert." -ForegroundColor Yellow
        Write-Log  "Telegram keys empty; skipping alert."
    }
} catch {
    Write-Host "[WARN] Telegram keys missing or unreadable; skipping alert." -ForegroundColor Yellow
    Write-Log  "Telegram keys missing or unreadable; skipping alert."
}

# --- Summary ---
$summary = ("SUMMARY: {0} successes, {1} retries, {2} failures" -f $global:EQ12_Success,$global:EQ12_Retry,$global:EQ12_Fail)
Write-Host $summary -ForegroundColor Cyan
Write-Log  $summary
