# [sanitized] $ROOT = "C:\EQ12\EdgeGodParlays"
# [sanitized] $BOT  = Join-Path $ROOT "ai_betting_bot_stealth_final_flask_pro.py"
# [sanitized] Copy-Item $BOT "$BOT.bak" -Force

# Read, then replace the webhook + self_test sections and add the import + new helper
# [sanitized] $code = Get-Content $BOT -Raw

# Ensure import line present
if ($code -notmatch 'from sports_live import context_for_command') {
# [sanitized]   $code = $code -replace 'from flask import Flask, request',
# [sanitized]     'from flask import Flask, request' + "`r`nfrom sports_live import context_for_command"
# [sanitized] }

# Replace chatgpt() call site inside webhook to prepend context/guardrails
# [sanitized] $code = $code -replace '(elif text.startswith\("/"\):)([\s\S]*?)return "OK", 200', @'
elif text.startswith("/"):
    key = text[1:]
    instruction = LOGIC.get(key, None)

    # Build sport-specific context and guardrails
# [sanitized]     sport, ctx = context_for_command(key)
    guard = ""
    if sport == "mlb":
        guard = (
# [sanitized]             "RULES: Only use MLB teams/players from TODAY. "
# [sanitized]             "Reject colleges/soccer/hypotheticals. No NBA/NCAA/NHL. "
# [sanitized]             "If player uncertain, pick from listed MLB games only.\n"
# [sanitized]         )
    elif sport == "wnba":
        guard = (
# [sanitized]             "RULES: Only use WNBA teams/players from TODAY. "
# [sanitized]             "No NBA, NCAA, or men’s teams. Keep props strictly POINTS-only.\n"
# [sanitized]         )
    elif sport == "ufc":
        guard = (
# [sanitized]             "RULES: Only UFC fighters on active/scheduled cards. "
# [sanitized]             "Picks must be Method of Victory (KO/TKO/SUB/DEC) with short rationale.\n"
# [sanitized]         )
    elif sport == "boxing":
        guard = (
# [sanitized]             "RULES: Only sanctioned boxing bouts; prefer distance/decision or KO props with compubox trends.\n"
# [sanitized]         )

    if instruction:
        prompt = (
# [sanitized]             f"{instruction}\n\n"
# [sanitized]             f"{guard}"
# [sanitized]             f"{ctx}\n"
# [sanitized]             "Constrain picks exclusively to the teams/fighters above. "
# [sanitized]             "If no valid games today, say so briefly."
# [sanitized]         )
        ans = chatgpt(prompt, chat_id)
# [sanitized]         tg_send(f"📊 *{key.upper()}*\n{ans}", chat_id)
    else:
# [sanitized]         tg_send("⚠️ Unknown command. Try /commands.", chat_id)
    return "OK", 200
# [sanitized] '@

# Make self_test prints ASCII-only & tolerant
# [sanitized] $code = $code -replace 'print\(".*Local /health responded OK".*\)', 'print("Local /health responded OK")'
# [sanitized] $code = $code -replace 'print\(f".*Self-test failed:.*"\)', 'print("Self-test failed")'

# [sanitized] Set-Content -Path $BOT -Value $code -Encoding UTF8 -Force
# [sanitized] Write-Host "✅ Patched $BOT (context + guardrails + ASCII self_test)"

# Restart cleanly and set webhook to current ngrok tunnel
# [sanitized] netstat -ano | findstr ":5005" | ForEach-Object {
# [sanitized]   $p = ($_ -split "\s+")[-1]; if ($p -match '^\d+$') { try { Stop-Process -Id $p -Force -EA SilentlyContinue } catch {} }
# [sanitized] }
# [sanitized] Get-Process python,ngrok -EA SilentlyContinue | Stop-Process -Force -EA SilentlyContinue
# [sanitized] C:\EQ12\EdgeGodParlays\Start-EdgeGodParlays.ps1

# Wait and show health + current commands
# [sanitized] Start-Sleep -Seconds 4
# [sanitized] Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5005/health | Select-Object -ExpandProperty Content