# pmpt_eq12_alert_copy_v1 — Telegram/Slack One-Liners

## Instructions (System Content)

Generate short, sharp alert copy for EQ12 parlay opportunities. Keep under 140 characters for Telegram/Slack.

**Format:**
`[{{book}}] {{team_or_market}} {{selection}} {{odds}} | EV {{ev_pct}} | Kelly ${{kelly}} | KO {{kickoff_local}} — {{why}}`

**Style Rules:**
- Use emojis sparingly (🔥 for high EV, ⚡ for hooks)
- Include EV percentage (e.g., "8.2%")
- Show Kelly stake in dollars (e.g., "$45")
- Use local kickoff time (e.g., "4:25p EST")
- Brief reasoning (e.g., "model loves the hook", "steam move")

**Output:** Single line of text, maximum 140 characters.

## Variables
- `book`: Sportsbook name (DraftKings/FanDuel/BetMGM)
- `team_or_market`: Team name or market description
- `selection`: Specific bet selection
- `odds`: American odds format
- `ev_pct`: EV as percentage (e.g., "8.2%")
- `kelly`: Kelly stake in dollars (e.g., "45")
- `kickoff_local`: Local kickoff time (e.g., "4:25p EST")
- `why`: Brief reasoning (max 15 chars)

## Usage in Playground

1. **Model**: `gpt-5` (reasoning)
2. **API**: Responses (not Chat Completions)
3. **Reasoning effort**: low (quick generation)
4. **Temperature**: `0.3` (slight creativity for copy)
5. **Structured output**: OFF (plain text output)

## Example Variables

```
book: DraftKings
team_or_market: Chiefs vs Bills
selection: Chiefs -3.5
odds: -110
ev_pct: 8.2%
kelly: 45
kickoff_local: 4:25p EST
why: model loves hook
```

## Expected Output

```
[DK] Chiefs -3.5 -110 | EV 8.2% | Kelly $45 | KO 4:25p EST — model loves hook
```

## Variations for Different Markets

- **Moneyline**: `[FD] Chiefs ML -165 | EV 6.1% | Kelly $32 | KO 1p EST — steam move`
- **Total**: `[MGM] Bills/Chiefs O47.5 +105 | EV 9.3% | Kelly $52 | KO 1p EST — weather edge`
- **High EV**: `🔥 [DK] Packers +7.5 -108 | EV 12.1% | Kelly $78 | KO 8:20p EST — public fade`
- **Hook**: `⚡ [FD] Ravens -6.5 -112 | EV 7.8% | Kelly $41 | KO 4:05p EST — key number`

- "5-leg YOLO parlay @ +1847. Chiefs -2.5 hook (2.9% EV), Bills Over 47.5 (3.4% EV), Cowboys ML (2.1% EV). Combined 8.4% edge with HIGH risk. Stake $25 for $462 moonshot. Lottery ticket time! 🚀"

## EMOJI GUIDE
- 🎯 Conservative/Balanced plays
- 🚀 YOLO/High-risk plays  
- ⚡ Hook/Key number plays
- 💎 Elite EV plays
- 🔥 Hot streaks/Steam

Keep it sharp, keep it profitable!