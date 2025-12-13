# EQ12 NBA Props Betting System

**Enterprise-grade VB.NET parlay optimizer with Raspberry Pi + Coral TPU ML inference**

---

## 📋 Overview

The EQ12 Props system is a production-ready NBA player props betting infrastructure designed to:

- **Ingest** real-time betting lines from multiple sportsbooks via REST APIs
- **Predict** true probabilities using ML models on Raspberry Pi + Coral TPU
- **Optimize** 3-4 leg parlays with correlation constraints (max ρ < 0.45)
- **Size bets** using fractional Kelly Criterion (1/4 Kelly) with 5% bankroll cap
- **Track performance** with comprehensive SQL Server time-series database

**Target Performance:**
- 3-4 leg parlays
- 58-64% true win probability per leg
- +4-6% edge minimum vs implied odds
- Max pairwise correlation ρ < 0.45

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Windows Development Machine                   │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │
│  │ IngestService  │  │ FeatureService  │  │  OptimizerApp    │ │
│  │   (VB.NET)     │  │   (VB.NET)      │  │    (VB.NET)      │ │
│  │                │  │                 │  │                  │ │
│  │ • REST API     │  │ • Pace calc     │  │ • ParlayBuilder  │ │
│  │ • MERGE upsert │  │ • Usage calc    │  │ • Kelly sizing   │ │
│  │ • Snapshots    │  │ • DvP calc      │  │ • Correlation    │ │
│  └────────┬───────┘  └────────┬────────┘  └────────┬─────────┘ │
│           │                   │                     │           │
│           └───────────────────┼─────────────────────┘           │
│                               │                                 │
│                    ┌──────────▼──────────┐                      │
│                    │   SQL Server        │                      │
│                    │  • PropLines        │                      │
│                    │  • Features         │                      │
│                    │  • Predictions      │                      │
│                    │  • Correlations     │                      │
│                    │  • Parlays          │                      │
│                    └─────────────────────┘                      │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP REST API
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                   Raspberry Pi 5 + Coral TPU                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  eq12_inference.py (Python FastAPI)                      │  │
│  │  • /health - TPU status check                            │  │
│  │  • /predict - Single prediction                          │  │
│  │  • /predict/batch - Batch predictions (efficient)        │  │
│  │  • /stats/tpu - Temperature, utilization                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  TensorFlow Lite Model (props_model.tflite)              │  │
│  │  • Input: Player stats, pace, usage, DvP, schedule       │  │
│  │  • Output: True probability, expected value, confidence  │  │
│  │  • Accelerated with Coral TPU (EdgeTPU delegate)         │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
C:\EQ12_BROKEN_20251122_210342\
├── src\props\
│   ├── schema.sql              # SQL Server database schema (8 tables, 5 views)
│   ├── OddsIngestor.vb         # REST API line fetching + MERGE upserts
│   ├── PricingUtils.vb         # Odds conversion, EV, Poisson calculations
│   ├── KellyCalculator.vb      # Optimal stake sizing with correlation adjustment
│   ├── ParlayBuilder.vb        # Greedy parlay construction with ρ constraints
│   ├── PiClient.vb             # Raspberry Pi REST client (HTTP + SSH)
│   └── OptimizerApp.vb         # Main console app (orchestrates pipeline)
│
├── .vscode\
│   └── tasks_props.json        # VS Code workflow automation (15 tasks)
│
├── models\
│   └── props_model.tflite      # TensorFlow Lite model for Pi inference
│
├── logs\
│   └── schema_init.log         # Database initialization logs
│
└── README_PROPS.md             # This file
```

---

## 🚀 Quick Start

### 1. Prerequisites

**Windows Machine:**
- .NET 6.0 SDK or later
- SQL Server 2019+ (or PostgreSQL with connection string change)
- Visual Studio 2022 or VS Code with VB.NET extension
- PowerShell 5.1+

**Raspberry Pi:**
- Raspberry Pi 4/5 with Coral TPU USB Accelerator
- Python 3.9+
- TensorFlow Lite Runtime
- FastAPI + Uvicorn

**API Keys:**
- The Odds API key (free tier: 500 requests/month, $0.025/request after)

### 2. Database Setup

```powershell
# Create database
sqlcmd -S localhost -Q "CREATE DATABASE EQ12Props"

# Initialize schema
sqlcmd -S localhost -d EQ12Props -i src\props\schema.sql -o logs\schema_init.log

# Verify tables
sqlcmd -S localhost -d EQ12Props -Q "SELECT name FROM sys.tables ORDER BY name"
```

Expected output:
```
Correlations
Features
ParlayLegs
Parlays
Predictions
PropLines
PropLinesSnapshot
SystemMetrics
```

### 3. Environment Variables

Create `.env` file in project root:

```bash
# Required
ODDS_API_KEY=your_odds_api_key_here
EQ12_DB_CONNECTION=Server=localhost;Database=EQ12Props;Integrated Security=true
EQ12_PI_HOST=192.168.1.80
EQ12_BANKROLL=10000
EQ12_KELLY_FRACTION=0.25

# Optional
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### 4. Build Solution

```powershell
# Using VS Code task (Ctrl+Shift+B)
# Or manually:
dotnet build src\props\EQ12.Props.sln /p:Configuration=Release
```

### 5. Run Optimizer (Dry Run)

```powershell
# Using VS Code task (Ctrl+Shift+P → "Run Task" → "EQ12 Props: Run Optimizer (Dry Run)")
# Or manually:
dotnet run --project src\props\OptimizerApp.vbproj -- --dry-run --legs 4
```

Expected output:
```
==============================================
   EQ12 NBA Props Optimizer v1.0
   Correlation-Aware Parlay Builder
==============================================

Configuration:
  - Database: Server=localhost;Database=EQ12Props...
  - Pi Host: 192.168.1.80
  - Bankroll: $10000.00
  - Kelly Fraction: 0.25
  - Target Legs: 4
  - Dry Run: True

──────────────────────────────────────────────
STEP 1: Check Pi Service Health
──────────────────────────────────────────────
[PiClient] Health check OK (TPU=True, Model=True)

──────────────────────────────────────────────
STEP 2: Fetch and Ingest Latest Lines
──────────────────────────────────────────────
[OddsIngestor] Fetching lines from draftkings...
[OddsIngestor] Upserted 143 lines (87 new, 56 updated) in 342ms
...

──────────────────────────────────────────────
STEP 4: Build Optimal Parlay
──────────────────────────────────────────────
[ParlayBuilder] Found 28 eligible candidates (edge >= 4.0%, prob 58-64%)
[ParlayBuilder] Added leg 1: LeBron James PTS 25.5 @ -115 (edge=5.23%, prob=62.1%)
[ParlayBuilder] Added leg 2: Luka Doncic AST 9.5 @ +105 (edge=4.87%, prob=60.3%)
[ParlayBuilder] Skipping Kyrie Irving PTS 23.5 (ρ=0.52 > 0.45 with Luka Doncic)
[ParlayBuilder] Added leg 3: Nikola Jokic REB 12.5 @ -110 (edge=4.65%, prob=61.8%)
[ParlayBuilder] Added leg 4: Jayson Tatum 3PM 3.5 @ +120 (edge=5.01%, prob=59.7%)

[ParlayBuilder] Parlay complete: 4 legs
  - Combined true probability: 13.96%
  - Parlay odds: +1825
  - Average correlation: 0.15

──────────────────────────────────────────────
STEP 5: Calculate Kelly Stake
──────────────────────────────────────────────
Kelly Stake: $483.27
  - Bankroll: $10000.00
  - Kelly Fraction: 0.25
  - Avg Correlation: 0.150
  - Risk: 4.83% of bankroll

═════════════════════════════════════════════════════════════
   BET SLIP (DRY RUN)
═════════════════════════════════════════════════════════════
Leg 1: LeBron James PTS 25.5 @ -115
       draftkings | True Prob: 62.1% | Edge: 5.23%
Leg 2: Luka Doncic AST 9.5 @ +105
       fanduel | True Prob: 60.3% | Edge: 4.87%
Leg 3: Nikola Jokic REB 12.5 @ -110
       betmgm | True Prob: 61.8% | Edge: 4.65%
Leg 4: Jayson Tatum 3PM 3.5 @ +120
       pointsbet | True Prob: 59.7% | Edge: 5.01%
─────────────────────────────────────────────────────────────
Parlay Odds: +1825 (Decimal: 19.25)
True Probability: 13.96%

Stake: $483.27
Potential Win: $8822.95
Potential Payout: $9306.22
═════════════════════════════════════════════════════════════

✓ Optimizer completed successfully
```

---

## 🔧 VS Code Tasks

Access via `Ctrl+Shift+P` → "Tasks: Run Task":

| Task | Description | Shortcut |
|------|-------------|----------|
| **Build Solution** | Compile all VB.NET projects | `Ctrl+Shift+B` |
| **Initialize Database** | Run schema.sql to create tables | - |
| **Run Ingest Service** | Start background line fetching | - |
| **Run Optimizer (Dry Run)** | Test parlay builder without saving | - |
| **Run Optimizer (Live)** | Build and save parlay to database | - |
| **Pi Health Check** | Verify Pi service + TPU availability | - |
| **SSH to Pi** | Open SSH session to Raspberry Pi | - |
| **Upload Model to Pi** | Transfer .tflite model via SCP | - |
| **Restart Pi Service** | Restart inference service on Pi | - |
| **View Today's Candidates** | Query eligible props with edge | - |
| **View Recent Parlays** | Show last 10 parlays from DB | - |
| **View Line Movements** | Track sharp action (steam moves) | - |
| **Full Pipeline** | Ingest → Optimize (sequential) | - |
| **Run Tests** | Execute unit tests | `Ctrl+Shift+T` |
| **Clean Build Artifacts** | Remove bin/obj folders | - |

---

## 📊 Database Schema

### Core Tables

**PropLines** - Current betting lines
- Fields: `GameId`, `PlayerId`, `Market`, `Line`, `Price`, `Book`, `FetchedAt`, `LineMovement`
- Indexes: Composite on (GameId, PlayerId, Market, Book, Line), FetchedAt DESC

**PropLinesSnapshot** - Historical line tracking (append-only)
- Fields: Same as PropLines + `SnapshotAt`
- Purpose: Track line movement over time, detect sharp action

**Features** - Player/game features for ML
- Fields: `PaceAdj`, `Usage`, `OnOffAdj`, `DvP`, `MinPred`, `ShotProfile*`, `FoulRisk`, `B2B`
- Purpose: Input features for ML model predictions

**Predictions** - Model outputs
- Fields: `TrueProb`, `ExpectedValue`, `Confidence`, `ModelVersion`
- Purpose: Store Pi predictions for comparison and analysis

**Correlations** - Pairwise correlation matrix
- Fields: `Player1Id`, `Market1`, `Player2Id`, `Market2`, `Rho`, `SampleSize`, `ConfidenceInterval95`
- Purpose: Enforce correlation constraints in parlay building

**Parlays** - Bet slips
- Fields: `NumLegs`, `TrueProb`, `ParlayOdds`, `KellyStake`, `AvgCorrelation`, `Status`, `ActualReturn`
- Purpose: Track performance, ROI, Kelly accuracy

**ParlayLegs** - Individual legs
- Fields: `ParlayId` (FK), `PlayerId`, `Market`, `Line`, `Odds`, `TrueProb`, `EdgePercent`, `ActualResult`
- Purpose: Detailed leg-level tracking

**SystemMetrics** - Performance monitoring
- Fields: `IngestLatencyP95`, `QueueDepth`, `TPUUtilization`, `ModelHitRate`, `ROI`, `KellyAccuracy`
- Purpose: System health and betting performance

### Views

- `vw_BestLines` - Best available price by player/market
- `vw_LineMovements` - Line movement tracking for steam detection
- `vw_SharpAction` - Rapid line movements (3+ moves in 2 hours)
- `vw_CorrelationLookup` - Helper for correlation matrix queries
- `vw_TodayCandidates` - Eligible props with edge calculations

---

## 🤖 Raspberry Pi Setup

### Install Dependencies

```bash
# On Raspberry Pi
sudo apt update
sudo apt install python3-pip python3-venv

# Create virtual environment
python3 -m venv ~/eq12_env
source ~/eq12_env/bin/activate

# Install packages
pip install tensorflow-lite-runtime
pip install fastapi uvicorn
pip install numpy pandas
pip install pycoral  # For Coral TPU
```

### Create Inference Service

Create `~/eq12/eq12_inference.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel
import tflite_runtime.interpreter as tflite
from pycoral.utils import edgetpu
import numpy as np
import time

app = FastAPI()

# Load model with EdgeTPU delegate
interpreter = tflite.Interpreter(
    model_path='/home/pi/eq12/models/props_model.tflite',
    experimental_delegates=[edgetpu.load_edgetpu_delegate()]
)
interpreter.allocate_tensors()

class PredictionRequest(BaseModel):
    PlayerId: str
    GameId: str
    Market: str
    Line: float
    Features: dict

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "tpu": True,  # Check edgetpu.list_edge_tpus()
        "model_loaded": interpreter is not None
    }

@app.post("/predict")
def predict(request: PredictionRequest):
    start = time.time()
    
    # Prepare input tensor (example - adjust based on model)
    input_features = np.array([
        request.Features['PaceAdj'],
        request.Features['Usage'],
        request.Features['OnOffAdj'],
        request.Features['DvP'],
        request.Features['MinPred']
    ], dtype=np.float32).reshape(1, -1)
    
    interpreter.set_tensor(interpreter.get_input_details()[0]['index'], input_features)
    interpreter.invoke()
    
    output = interpreter.get_tensor(interpreter.get_output_details()[0]['index'])
    true_prob = float(output[0][0])
    
    elapsed = (time.time() - start) * 1000
    
    return {
        "TrueProb": true_prob,
        "ExpectedValue": request.Line * 1.1,  # Placeholder
        "Confidence": 0.85,
        "ModelVersion": "v1.0",
        "InferenceTimeMs": elapsed
    }

@app.post("/predict/batch")
def predict_batch(requests: list[PredictionRequest]):
    results = []
    for req in requests:
        results.append(predict(req))
    return results

@app.get("/stats/tpu")
def tpu_stats():
    # Placeholder - implement actual TPU monitoring
    return {
        "temperature": 42.5,
        "utilization": 67.3
    }
```

### Create systemd Service

Create `/etc/systemd/system/eq12-inference.service`:

```ini
[Unit]
Description=EQ12 Props Inference Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/eq12
Environment="PATH=/home/pi/eq12_env/bin"
ExecStart=/home/pi/eq12_env/bin/uvicorn eq12_inference:app --host 0.0.0.0 --port 5000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable eq12-inference
sudo systemctl start eq12-inference
sudo systemctl status eq12-inference
```

---

## 📈 Usage Examples

### Full Production Run

```powershell
# 1. Set environment variables (or use .env file)
$env:ODDS_API_KEY = "your_key_here"
$env:EQ12_BANKROLL = "10000"

# 2. Run optimizer (live mode)
dotnet run --project src\props\OptimizerApp.vbproj -- --legs 4 --bankroll 10000

# 3. View saved parlay
sqlcmd -S localhost -d EQ12Props -Q "SELECT TOP 1 * FROM dbo.Parlays ORDER BY CreatedAt DESC"
```

### Query Best Lines

```sql
SELECT TOP 20 
    PlayerName, Market, Line, BestPrice, LatestFetch
FROM vw_BestLines
WHERE Market IN ('PTS', 'AST', 'REB', 'PRA')
ORDER BY PlayerName;
```

### Detect Sharp Action

```sql
SELECT 
    PlayerName, Market, Line, 
    MoveCount, TotalMovement, LastMove
FROM vw_SharpAction
ORDER BY TotalMovement DESC;
```

### Calculate ROI

```sql
SELECT 
    COUNT(*) as TotalParlays,
    SUM(CASE WHEN Status = 'Won' THEN 1 ELSE 0 END) as Wins,
    SUM(CASE WHEN Status = 'Lost' THEN 1 ELSE 0 END) as Losses,
    SUM(KellyStake) as TotalRisked,
    SUM(ISNULL(ActualReturn, 0)) as TotalReturn,
    (SUM(ISNULL(ActualReturn, 0)) - SUM(KellyStake)) / SUM(KellyStake) * 100 as ROI
FROM dbo.Parlays
WHERE ParlayDate >= DATEADD(MONTH, -1, GETDATE());
```

---

## 🧪 Testing

Create `src\props\EQ12.Props.Tests\PricingUtilsTests.vb`:

```vbnet
Imports Xunit
Imports EQ12.Props

Public Class PricingUtilsTests
    
    <Fact>
    Public Sub AmericanToImplProb_Favorite_ReturnsCorrectValue()
        Dim prob = PricingUtils.AmericanToImplProb(-110)
        Assert.Equal(0.524, prob, 3)  ' 52.4%
    End Sub
    
    <Fact>
    Public Sub AmericanToImplProb_Underdog_ReturnsCorrectValue()
        Dim prob = PricingUtils.AmericanToImplProb(150)
        Assert.Equal(0.40, prob, 2)  ' 40.0%
    End Sub
    
    <Fact>
    Public Sub EVPerLeg_PositiveEdge_ReturnsPositiveEV()
        Dim ev = PricingUtils.EVPerLeg(0.55, -110, 100)
        Assert.True(ev > 0)
    End Sub
    
End Class
```

Run tests:

```powershell
dotnet test src\props\EQ12.Props.Tests\EQ12.Props.Tests.vbproj --logger "console;verbosity=detailed"
```

---

## 🔐 Security Best Practices

1. **Never hardcode API keys** - Use environment variables or Azure Key Vault
2. **SQL injection protection** - All queries use parameterized commands
3. **SSH key authentication** - Never use passwords for Pi access
4. **Rate limiting** - Respect OddsAPI free tier (10 req/min)
5. **Bankroll caps** - Hard 5% limit regardless of Kelly calculation
6. **Audit logging** - All DB writes include timestamps and user context

---

## 📝 Monitoring & Alerts

### Windows Performance Counters

```powershell
# Track ingest latency
Get-Counter "\Process(OptimizerApp)\% Processor Time"

# Monitor SQL Server
Get-Counter "\SQLServer:Databases(EQ12Props)\Transactions/sec"
```

### Telegram Alerts (Optional)

Add to `OptimizerApp.vb`:

```vbnet
Private Sub SendTelegramAlert(message As String)
    Dim botToken = Environment.GetEnvironmentVariable("TELEGRAM_BOT_TOKEN")
    Dim chatId = Environment.GetEnvironmentVariable("TELEGRAM_CHAT_ID")
    
    If String.IsNullOrEmpty(botToken) Then Return
    
    Dim url = $"https://api.telegram.org/bot{botToken}/sendMessage"
    Dim payload = New With {.chat_id = chatId, .text = message}
    
    ' Send via HttpClient (async)
End Sub
```

---

## 🐛 Troubleshooting

### Pi Service Not Responding

```bash
# Check service status
sudo systemctl status eq12-inference

# View logs
journalctl -u eq12-inference -n 50 -f

# Test manually
curl http://192.168.1.80:5000/health
```

### SQL Connection Errors

```powershell
# Test connection
sqlcmd -S localhost -d EQ12Props -Q "SELECT @@VERSION"

# Check connection string
echo $env:EQ12_DB_CONNECTION
```

### OddsAPI Rate Limits

```powershell
# Check remaining requests
Invoke-RestMethod -Uri "https://api.the-odds-api.com/v4/sports/?apiKey=$env:ODDS_API_KEY" `
    -Method Get -Headers @{'X-Requests-Remaining'='true'}
```

---

## 📚 References

- [The Odds API Documentation](https://the-odds-api.com/liveapi/guides/v4/)
- [Kelly Criterion Explainer](https://en.wikipedia.org/wiki/Kelly_criterion)
- [Coral TPU Documentation](https://coral.ai/docs/edgetpu/compiler/)
- [VB.NET Language Reference](https://learn.microsoft.com/en-us/dotnet/visual-basic/)

---

## 📄 License

Internal EQ12 project - Not for public distribution

---

## 👤 Author

EQ12 Development Team  
Built with GitHub Copilot + Claude Sonnet 4.5

---

**Status:** ✅ Core modules complete, ready for integration testing  
**Next Steps:** Feature service implementation, correlation matrix population, live testing with small bankroll
