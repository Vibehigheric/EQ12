# extracted Python blocks from merged-candidate
# Source: ai_betting_bot_stealth_final_flask_pro.py.merged-candidate.py



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
            f"{instruction}\n\n"
            f"{guard}"
            f"{ctx}\n"
            "Constrain picks exclusively to the teams/fighters above. "
            "If no valid games today, say so briefly."
        )
        ans = chatgpt(prompt, chat_id)
        tg_send(f"📊 *{key.upper()}*\n{ans}", chat_id)
    else:
        tg_send("⚠️ Unknown command. Try /commands.", chat_id)
    return "OK", 200