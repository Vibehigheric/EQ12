# EdgeGodUnified — EV + Monte Carlo + Rule Builder + Gmail/Telegram (EQ12)

Everything in one runner:
- EV% ranking vs book odds
- Monte Carlo parlay true win probabilities
- Rule-based construction (your caps + IL/HR rules + star TB/Hits)
- Auto email + Telegram

## Setup
1. Unzip to `C:\EQ12_Automation\EdgeGodUnified`
2. Add Google `credentials.json` (Gmail API enabled)
3. Edit `config.json` for recipients, Telegram, and rules
4. Run once to authorize:
   ```powershell
   python C:\EQ12_Automation\EdgeGodUnifiedunner.py
   ```
5. Schedule daily.

## Input
Replace `data\sample_lines.csv` with your real lines:
`game_id,market,side,player,display_name,odds,true_prob,proj_over_2_prob`

© 2025
