# VB.NET Betting Analyzer - Quick Start Guide

## Visual Studio Users (3 Steps)

### Step 1: Create New Project

1. Open **Visual Studio 2022** (or Visual Studio 2019+)
2. Click **Create a new project**
3. Search for **"Visual Basic Console"**
4. Select **Console App (.NET Framework)** or **Console App (.NET)**
5. Name: `EQ12BettingAnalyzer`
6. Click **Create**

### Step 2: Replace Code

1. Visual Studio will create `Module1.vb` or `Program.vb`
2. **Delete all the default code** in that file
3. Open `BettingSlipAnalyzer.vb` from this folder
4. **Copy the entire contents**
5. **Paste into Module1.vb**

### Step 3: Run

1. Press **F5** (or click the green **Start** button)
2. Console window will appear showing slip analysis
3. Read the **RECOMMENDED SLIP** at the bottom
4. Press any key to exit

---

## Output You'll See

```
=============================================================================
EQ12 BETTING SLIP ANALYZER - VB.NET Edition
=============================================================================

=============================================================================
Slip 1 - Mixed Multi-Sport SGPx
=============================================================================
Total Legs: 10
Risk Score (lower is better): 28.20
Correlation Score (higher is better): 1.80
Sport Mix Penalty: 4.00

HIGH VARIANCE LEGS (>= 2.5):
  [!] Navy +14.5 Alternate Spread (Variance: 3)
  [!] Michigan State Moneyline (Variance: 2.6)
  ...

LEG BREAKDOWN:
  - Noah Fant 2+ Receptions  [CIN@BAL 8:20PM] [MEDIUM]
  - George Pickens 7+ Receptions  [KC@DAL 4:30PM] [MEDIUM]
  ...

=============================================================================
Slip 2 - NFL Correlated SGP
=============================================================================
Total Legs: 8
Risk Score (lower is better): 16.00
Correlation Score (higher is better): 5.00
Sport Mix Penalty: 0.00

LEG BREAKDOWN:
  - Andrei Iosivas 3+ Receptions  [CIN@BAL 8:20PM] [MEDIUM]
  ...

=============================================================================
RECOMMENDATION ENGINE
=============================================================================

RECOMMENDED SLIP TO PLAY TODAY:
>>> Slip 2 - NFL Correlated SGP

WHY THIS SLIP?
  - Risk Score: 16.00 (lower is better)
  - Correlation Score: 5.00 (higher is better)
  - Sport Mix Penalty: 0.00

[VERDICT] GOOD BET - Well-correlated, acceptable risk profile.

Press any key to exit...
```

---

## What the Scores Mean

### Risk Score (Want LOW)
- **Below 15** = Safe bet
- **15-20** = Moderate risk
- **20-25** = Risky
- **Above 25** = Avoid or remove high-variance legs

### Correlation Score (Want HIGH)
- **Below 2.0** = Weak correlation (spread across many games)
- **2.0-3.5** = Moderate correlation
- **3.5-5.0** = Strong correlation (good same-game stacking)
- **Above 5.0** = Excellent correlation

### Verdict Guide
- **GOOD BET** = Play as-is
- **RISKY** = Remove 2+ high-variance legs before playing
- **DO NOT PLAY** = Too dangerous, start over with different slip

---

## Customizing for Your Own Slips

### Find This Section in the Code:

```vbnet
Dim slip1 As New BetSlip("My Slip Name")

slip1.Legs.Add(New BetLeg("Player Action",
                          SportType.NFL,
                          MarketType.Receptions,
                          "TEAM@TEAM TIME",
                          2.0))  ' <- Variance number
```

### Change These:
1. **"My Slip Name"** → Your DraftKings slip name
2. **"Player Action"** → Exact bet description (e.g., "Travis Kelce 3+ Receptions")
3. **SportType** → NFL / NCAAF / NCAAB
4. **MarketType** → Moneyline / Spread / Receptions / etc.
5. **"TEAM@TEAM TIME"** → Game identifier
6. **Variance** → Set risk level:
   - `1.5` = Safe (low floor props)
   - `2.0` = Medium (standard props)
   - `2.5+` = High (alternate spreads, underdog MLs)

---

## Troubleshooting

### Error: "Namespace or type 'List' is not defined"
**Fix**: Add this at the top of the file:
```vbnet
Imports System.Collections.Generic
Imports System.Linq
```

### Error: "Sub Main was not found"
**Fix**: Make sure the code starts with:
```vbnet
Module Program
    Sub Main()
```

### Can't Find Visual Studio?
**Option 1**: Download Visual Studio Community (free):
- https://visualstudio.microsoft.com/downloads/
- Install **VB.NET** workload

**Option 2**: Use command-line compiler:
```powershell
vbc.exe /out:Analyzer.exe BettingSlipAnalyzer.vb
```

---

## Next Steps

Once you understand the basics:

1. **Add your own slips** using the pattern above
2. **Adjust variance numbers** based on your research
3. **Change recommendation logic** to match your betting strategy
4. **Export to CSV** or integrate with Telegram bot
5. **Request advanced features** (Windows Forms GUI, API integration, etc.)

---

**Questions? Check `README.md` for full documentation.**
