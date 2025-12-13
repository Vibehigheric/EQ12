# [sanitized-ps] ﻿$ROOT = "C:\EQ12\EdgeGodParlays"
# [sanitized-ps] $BOT  = Join-Path $ROOT "ai_betting_bot_stealth_final_flask_pro.py"
# [sanitized-ps] Copy-Item $BOT "$BOT.bak" -Force

# Read, then replace the webhook + self_test sections and add the import + new helper
# [sanitized-ps] $code = Get-Content $BOT -Raw

# Ensure import line present
# [sanitized-ps] if ($code -notmatch 'from sports_live import context_for_command') {
# [sanitized-ps]   $code = $code -replace 'from flask import Flask, request',
# [sanitized-ps]     'from flask import Flask, request' + "`r`nfrom sports_live import context_for_command"
# [sanitized-ps] }

# Replace chatgpt() call site inside webhook to prepend context/guardrails
# [sanitized-ps] $code = $code -replace '(elif text.startswith\("/"\):)([\s\S]*?)return "OK", 200', @'
elif text.startswith("/"):
    key = text[1:]
    instruction = LOGIC.get(key, None)

    # Build sport-specific context and guardrails
    sport, ctx = context_for_command(key)
    guard = ""
    if sport == "mlb":
        guard = (
            "RULES: Only use MLB teams/players from TODAY. "
            "Reject colleges/soccer/hypotheticals. No NBA/NCAA/NHL. "
            "If player uncertain, pick from listed MLB games only.\n"
        )
    elif sport == "wnba":
        guard = (
            "RULES: Only use WNBA teams/players from TODAY. "
            "No NBA, NCAA, or men’s teams. Keep props strictly POINTS-only.\n"
        )
    elif sport == "ufc":
        guard = (
            "RULES: Only UFC fighters on active/scheduled cards. "
            "Picks must be Method of Victory (KO/TKO/SUB/DEC) with short rationale.\n"
        )
    elif sport == "boxing":
        guard = (
            "RULES: Only sanctioned boxing bouts; prefer distance/decision or KO props with compubox trends.\n"
        )

    if instruction:
        prompt = (
# [sanitized-ps]             f"{instruction}\n\n"
# [sanitized-ps]             f"{guard}"
# [sanitized-ps]             f"{ctx}\n"
            "Constrain picks exclusively to the teams/fighters above. "
            "If no valid games today, say so briefly."
        )
        ans = chatgpt(prompt, chat_id)
# [sanitized-ps]         tg_send(f"📊 *{key.upper()}*\n{ans}", chat_id)
    else:
        tg_send("⚠️ Unknown command. Try /commands.", chat_id)
    return "OK", 200
'@

# Make self_test prints ASCII-only & tolerant
# [sanitized-ps] $code = $code -replace 'print\(".*Local /health responded OK".*\)', 'print("Local /health responded OK")'
# [sanitized-ps] $code = $code -replace 'print\(f".*Self-test failed:.*"\)', 'print("Self-test failed")'

# [sanitized-ps] Set-Content -Path $BOT -Value $code -Encoding UTF8 -Force
# [sanitized-ps] Write-Host "✅ Patched $BOT (context + guardrails + ASCII self_test)"

# Restart cleanly and set webhook to current ngrok tunnel
# [sanitized-ps] netstat -ano | findstr ":5005" | ForEach-Object {
# [sanitized-ps]   $p = ($_ -split "\s+")[-1]; if ($p -match '^\d+$') { try { Stop-Process -Id $p -Force -EA SilentlyContinue } catch {} }
# [sanitized-ps] }
Get-Process python,ngrok -EA SilentlyContinue | Stop-Process -Force -EA SilentlyContinue
C:\EQ12\EdgeGodParlays\Start-EdgeGodParlays.ps1

# Wait and show health + current commands
Start-Sleep -Seconds 4
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5005/health | Select-Object -ExpandProperty Content