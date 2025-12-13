# EQ12 Betting Slip Analyzer - VB.NET Console Application

## Overview

This VB.NET console application analyzes DraftKings/FanDuel Same Game Parlay (SGP) betting slips for risk and correlation using automated scoring algorithms.

## Features

- **Risk Scoring**: Calculates risk based on leg count × variance × sport mixing penalty
- **Correlation Scoring**: Rewards same-game stacking (multiple legs from one game)
- **Variance Tagging**: Each leg rated 1.0 (safe) → 3.0 (high risk)
- **Automated Recommendations**: Tells you which slip to play or avoid
- **Multi-Slip Comparison**: Compare multiple slips side-by-side

## How to Use in Visual Studio

### Option 1: Visual Studio 2022 (Recommended)

1. Open **Visual Studio 2022**
2. Create **New Project** → **Visual Basic** → **Console App (.NET Framework)** or **Console App (.NET)**
3. Name it `EQ12BettingAnalyzer`
4. Delete all default code in `Module1.vb` or `Program.vb`
5. Paste the entire contents of `BettingSlipAnalyzer.vb`
6. Press **F5** to run

### Option 2: Command Line Compilation

```powershell
# Navigate to directory
cd C:\EQ12_BROKEN_20251122_210342\vb_betting_analyzer

# Compile with VB.NET compiler (requires .NET Framework SDK or Visual Studio)
vbc.exe /out:BettingAnalyzer.exe BettingSlipAnalyzer.vb

# Run the compiled executable
.\BettingAnalyzer.exe
```

### Option 3: .NET SDK (cross-platform)

If you have .NET SDK installed:

```powershell
# Create new VB console project
dotnet new console -lang VB -o EQ12BettingAnalyzer

# Replace Program.vb with BettingSlipAnalyzer.vb content

# Run
dotnet run
```

## Example Output

```
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
  [!] BYU Moneyline (Variance: 2.6)
  [!] Santa Clara Moneyline (Variance: 2.8)
  [!] Arkansas +10.5 Spread (Variance: 2.9)
  [!] Dayton Moneyline (Variance: 2.5)
  [!] Jameson Williams 60+ Receiving Yards (Variance: 2.5)

LEG BREAKDOWN:
  - Noah Fant 2+ Receptions  [CIN@BAL 8:20PM] [MEDIUM]
  - George Pickens 7+ Receptions  [KC@DAL 4:30PM] [MEDIUM]
  - Navy +14.5 Alternate Spread  [NAVY@MEM 7:30PM] [HIGH RISK]
  ...

=============================================================================
RECOMMENDED SLIP TO PLAY TODAY:
>>> Slip 2 - NFL Correlated SGP

WHY THIS SLIP?
  - Risk Score: 16.00 (lower is better)
  - Correlation Score: 5.00 (higher is better)
  - Sport Mix Penalty: 0.00

[VERDICT] GOOD BET - Well-correlated, acceptable risk profile.
```

## Scoring System Explained

### Risk Score (Lower = Better)

```
Risk = (Leg Count × Average Variance) + (Sport Mix Penalty)
```

- **Leg Count**: More legs = higher risk
- **Average Variance**: Calculated from each leg's BaseVariance (1.0 - 3.0)
- **Sport Mix Penalty**: +2 points for each additional sport beyond the first

### Correlation Score (Higher = Better)

```
Correlation = (Σ Legs per Game²) / Total Legs + Single Sport Bonus
```

- **Same-Game Stacking**: Rewards having multiple legs from one game
- **Single Sport Bonus**: +1.0 if all legs are from one sport (e.g., NFL-only)

### Variance Guidelines

| Variance | Risk Level | Examples |
|----------|-----------|----------|
| 1.0 - 1.6 | **Safe** | Low reception floors (2+ rec), heavy favorite ML |
| 1.7 - 2.4 | **Medium** | Standard spreads, moderate reception totals, rushing attempts |
| 2.5 - 3.0 | **High** | Alternate spreads, underdog MLs, receiving yard totals, mid-major college games |

## Customization

### Adding New Slips

To add your own betting slips, follow this pattern:

```vbnet
Dim mySlip As New BetSlip("My Custom Slip Name")

mySlip.Legs.Add(New BetLeg(
    "Player Name Action",           ' Description
    SportType.NFL,                  ' Sport (NFL, NCAAF, NCAAB)
    MarketType.Receptions,          ' Market type
    "TEAM1@TEAM2 TIME",            ' Game key
    2.0                            ' Variance (1.0-3.0)
))
```

### Adjusting Variance

Edit the `BaseVariance` parameter for each leg:

- **1.0** = safest bets (e.g., Patrick Mahomes 1+ passing yards)
- **1.5** = low floors (e.g., Travis Kelce 2+ receptions)
- **2.0** = standard props (e.g., receiver 50+ yards)
- **2.5** = risky (e.g., tight end 60+ yards, underdog ML)
- **3.0** = very risky (e.g., alternate spreads, mid-major college games)

### Changing Recommendation Logic

Modify the `Main()` function's winner selection:

```vbnet
' Current logic: Correlation - (Risk / 10)
Dim bestSlip As BetSlip = slips _
    .OrderByDescending(Function(s) s.CorrelationScore() - (s.RiskScore() / 10.0)) _
    .First()

' Example alternative: Prefer lowest risk regardless of correlation
Dim bestSlip As BetSlip = slips _
    .OrderBy(Function(s) s.RiskScore()) _
    .First()
```

## Integration with EQ12 Ecosystem

This VB.NET analyzer can be integrated with:

- **PowerShell Scripts**: Call VB executable from PowerShell automation
- **Python Backend**: Convert to Python using same scoring logic
- **Telegram Bot**: Send slip analysis via bot notifications
- **Web Dashboard**: Wrap in ASP.NET web service
- **Raspberry Pi**: Compile to .NET Core for Pi deployment

### Example PowerShell Integration

```powershell
# Run analyzer and capture output
$result = & "C:\EQ12_BROKEN_20251122_210342\vb_betting_analyzer\BettingAnalyzer.exe"

# Parse output and send to Telegram
if ($result -match "RECOMMENDED SLIP TO PLAY") {
    Send-TelegramMessage -Message $result
}
```

## Next Steps (Advanced Features)

These features can be added:

1. **CSV Import**: Load slips from DraftKings CSV exports
2. **Windows Forms GUI**: Visual slip builder with drag-and-drop
3. **API Integration**: Pull real-time odds from DraftKings API
4. **Machine Learning**: Train model on historical slip outcomes
5. **Injury/News Feed**: Auto-adjust variance based on breaking news
6. **Database Storage**: Save and track slip performance over time

## License

MIT License - Part of EQ12 project ecosystem

## Author

EQ12 Copilot Workspace Architect
Date: 2025-11-27
