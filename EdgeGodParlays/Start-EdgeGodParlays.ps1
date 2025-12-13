# ================= EdgeGodParlays Bot Launcher (with Auto-Recovery) =================
$ErrorActionPreference = "Stop"
chcp 65001 | Out-Null
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8

$ROOT  = "C:\EQ12\EdgeGodParlays"
$PY    = Join-Path $ROOT ".venv\Scripts\python.exe"
$BOT   = Join-Path $ROOT "ai_betting_bot_stealth_final_flask_pro.py"
$NG    = Join-Path $ROOT "ngrok.exe"
$LOGD  = Join-Path $ROOT "logs"
New-Item -ItemType Directory -Force -Path $LOGD | Out-Null

# --- Rotate logs ---
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$botOut   = Join-Path $LOGD ("bot_" + $timestamp + "_out.log")
$botErr   = Join-Path $LOGD ("bot_" + $timestamp + "_err.log")
$ngrokOut = Join-Path $LOGD ("ngrok_" + $timestamp + "_out.log")
$ngrokErr = Join-Path $LOGD ("ngrok_" + $timestamp + "_err.log")

# --- Kill strays ---
netstat -ano | findstr ":5005" | ForEach-Object {
    $procId = ($_ -split "\s+")[-1]
    if ($procId -match '^\d+$') { try { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue } catch {} }
}
Get-Process python,ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# --- Load .env ---
$ENVF = Join-Path $ROOT ".env"
if (Test-Path $ENVF) {
    Get-Content $ENVF | ForEach-Object {
        if (-not [string]::IsNullOrWhiteSpace($_) -and -not $_.StartsWith("#")) {
            $k,$v = $_.Split('=',2)
            [Environment]::SetEnvironmentVariable($k.Trim(), $v.Trim(), 'Process')
        }
    }
}

function Start-Bot {
    Write-Host "🚀 Starting EdgeGodParlays..." -ForegroundColor Cyan
    $proc = Start-Process -FilePath $PY `
        -ArgumentList "`"$BOT`"" `
        -WorkingDirectory $ROOT `
        -WindowStyle Hidden `
        -PassThru `
        -RedirectStandardOutput $botOut `
        -RedirectStandardError  $botErr
    return $proc
}

function Check-BotHealth {
    try {
        $resp = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5005/health -TimeoutSec 3
        return $true
    } catch { return $false }
}

# --- Auto-Recovery loop ---
$maxAttempts = 5
for ($i=1; $i -le $maxAttempts; $i++) {
    $botProc = Start-Bot
    Start-Sleep -Seconds 5

    if (Check-BotHealth) {
        Write-Host "✅ Bot healthy (attempt $i)" -ForegroundColor Green
        break
    } else {
        Write-Warning "⚠️ Bot failed health check (attempt $i). Restarting..."
        try { $botProc.Kill() } catch {}
        Start-Sleep -Seconds 3
    }

    if ($i -eq $maxAttempts) {
        Write-Error "❌ Bot could not start after $maxAttempts attempts. Check logs in $LOGD"
        exit 1
    }
}

# --- Telegram confirmation ---
if ($env:TELEGRAM_BOT_TOKEN -and $env:TELEGRAM_CHAT_ID) {
    try {
        $msg = "🚀 EdgeGodParlays bot started successfully ✅"
        Invoke-RestMethod -Uri "https://api.telegram.org/bot$($env:TELEGRAM_BOT_TOKEN)/sendMessage" `
            -Method Post -ContentType "application/json" `
            -Body (@{chat_id=$env:TELEGRAM_CHAT_ID; text=$msg} | ConvertTo-Json -Compress)
        Write-Host "🤖 Telegram confirmation sent." -ForegroundColor Cyan
    } catch { Write-Warning "⚠️ Could not send Telegram confirmation." }
} else {
    Write-Warning "⚠️ TELEGRAM_BOT_TOKEN or CHAT_ID not loaded."
}

# --- Ngrok ---
$DEFAULT_NGROK_TOKEN = "30ITsz6jMc0Ugg8RTQvBeGy05ag_7e8tLgn62naWMMtE1wmt"
$NGROK_TOKEN = if ($env:NGROK_AUTHTOKEN) { $env:NGROK_AUTHTOKEN } else { $DEFAULT_NGROK_TOKEN }

if (Test-Path $NG) {
    try { & $NG config add-authtoken $NGROK_TOKEN | Out-Null } catch {}
    # Hidden background
    $ngrokProc = Start-Process -FilePath $NG `
        -ArgumentList "http","5005" `
        -WorkingDirectory $ROOT `
        -WindowStyle Hidden `
        -PassThru `
        -RedirectStandardOutput $ngrokOut `
        -RedirectStandardError  $ngrokErr
    # Visible console window for monitoring
    Start-Process -FilePath $NG -ArgumentList "http","5005" -WorkingDirectory $ROOT

    Start-Sleep -Seconds 5
    try {
        $tunnels = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -TimeoutSec 3
        $publicUrl = ($tunnels.tunnels | Where-Object {$_.proto -eq "https"} | Select-Object -First 1).public_url
        if ($publicUrl) {
            Write-Host "🌐 ngrok URL: $publicUrl" -ForegroundColor Green
            $hookUrl = "$publicUrl/webhook"
            Invoke-WebRequest -UseBasicParsing -Uri "https://api.telegram.org/bot$($env:TELEGRAM_BOT_TOKEN)/setWebhook?url=$([uri]::EscapeDataString($hookUrl))" | Out-Null
            Write-Host "🤖 Telegram webhook set." -ForegroundColor Cyan
        }
    } catch { Write-Warning "⚠️ Ngrok tunnel not found yet; check ngrok console." }
} else {
    Write-Warning "❌ ngrok.exe not found in $ROOT"
}

Write-Host "Logs:" -ForegroundColor Cyan
Write-Host "  OUT: $botOut"
Write-Host "  ERR: $botErr"
# ============================================================================
