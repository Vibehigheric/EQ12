# NBA Props System Adaptation Plan

**Created**: 2025-01-22  
**Purpose**: Adapt existing VB.NET props infrastructure to new detailed specification  
**System**: EQ12 (12 cores, 31.77GB RAM, Pi @ 192.168.1.80)  
**Storage**: D:\EQ12Props\ (SQL Server), C:\ (code/execution)

---

## 1. System Scan Results ✅

**Hardware Validation** (Completed):
```
CPU Cores: 12
RAM: 31.77 GB
Pi Reachable: True (192.168.1.80)
Storage: C:\ (583 GB free), D:\ (399 GB free)
Database: D:\EQ12Props\ (ready for SQL Server)
```

**Assessment**: ✅ System exceeds NBA props workload requirements
- 12 cores sufficient for multi-threaded odds ingestion
- 31.77GB RAM handles large correlation matrices + feature engineering
- Pi confirmed reachable for TensorFlow Lite inference
- D:\ has 399GB for Props database growth

---

## 2. Current Infrastructure ✅

**Existing VB.NET Modules** (8 files, 1,640 lines):

1. **OddsIngestor.vb** (143 lines)
   - REST API odds fetching
   - JSON deserialization
   - Basic error handling
   - **NEEDS**: Retry/backoff logic, 100-source registry integration

2. **PricingUtils.vb** (100 lines)
   - Odds conversion (American ↔ Decimal ↔ Implied)
   - EV calculations
   - Poisson probability
   - **COMPLETE**: Meets new spec requirements

3. **KellyCalculator.vb** (120 lines)
   - Full/fractional Kelly sizing
   - Correlation adjustment
   - 5% risk cap
   - **COMPLETE**: Matches new spec patterns

4. **ParlayBuilder.vb** (250 lines)
   - Greedy parlay construction
   - Basic correlation lookup (ρ < 0.45)
   - Candidate filtering
   - **NEEDS**: Multi-dimensional correlation guard, explicit combiner logic

5. **PiClient.vb** (200 lines)
   - HTTP REST to Pi (/health, /predict, /predict/batch)
   - SSH file transfer (Renci.SshNet)
   - Model upload
   - **COMPLETE**: Ready for Pi service setup

6. **OptimizerApp.vb** (250 lines)
   - Main orchestrator
   - End-to-end workflow
   - Console output
   - **NEEDS**: VS Code task integration, 7-step runbook

7. **QuickStart.vb** (200 lines)
   - Standalone examples
   - Testing utilities
   - **COMPLETE**: Ready to use

8. **schema.sql** (400 lines)
   - 8 tables: PropLines, PropLinesSnapshot, Features, Predictions, Correlations, Parlays, ParlayLegs, SystemMetrics
   - 5 views: vw_BestLines, vw_LineMovements, vw_SharpAction, vw_CorrelationLookup, vw_TodayCandidates
   - 20+ indexes
   - **NEEDS**: Feature engineering columns (pace, on/off, DvP, whistle/FTA)

---

## 3. New Specification Requirements

**Key Differences from Original**:

### A. HttpClient Retry/Backoff Pattern
```vbnet
' NEW REQUIREMENT: Exponential backoff with 4 retry attempts
For attempt = 1 To 4
    Dim resp = Await _http.GetAsync(url)
    If resp.IsSuccessStatusCode Then Return ProcessResponse(resp)
    Await Task.Delay(CInt(Math.Pow(2, attempt) * 200)) ' 400ms, 800ms, 1600ms
Next
Throw New Exception($"GET failed after 4 attempts: {url}")
```

**Current State**: OddsIngestor.vb has basic try/catch, no retry  
**Action Required**: Add retry loop to `FetchBookLinesAsync()`

---

### B. 100-Source JSON Registry
```json
{
  "providers": [
    {
      "id": "odds_api_nba",
      "name": "The Odds API - NBA Props",
      "endpoint": "https://api.the-odds-api.com/v4/sports/basketball_nba/odds",
      "auth_type": "bearer",
      "rate_limit": 500,
      "reliability_score": 0.95,
      "markets": ["player_points", "player_assists", "player_rebounds"]
    },
    {
      "id": "prizepicks",
      "name": "PrizePicks",
      "endpoint": "https://api.prizepicks.com/projections",
      "auth_type": "none",
      "rate_limit": 100,
      "reliability_score": 0.88
    }
    // ... 98 more providers
  ]
}
```

**Current State**: Hardcoded single endpoint in OddsIngestor  
**Action Required**: Create `data_sources_registry.json` + registry loader

---

### C. Feature Engineering Service
```vbnet
Public Class FeatureEngineer
    ' Pace adjustment: points_per_100_poss = player_pts * (league_avg_pace / team_pace)
    Public Function AdjustForPace(playerPts As Double, teamPace As Double) As Double
        Const LEAGUE_AVG_PACE = 100.0
        Return playerPts * (LEAGUE_AVG_PACE / teamPace)
    End Function
    
    ' On/Off court impact: net_rating_with_player - net_rating_without
    Public Function OnOffImpact(netRatingWith As Double, netRatingWithout As Double) As Double
        Return netRatingWith - netRatingWithout
    End Function
    
    ' Defense vs Position (DvP): opponent_defensive_rating_vs_position
    Public Function DvPFactor(oppDefRating As Double, leagueAvgDefRating As Double) As Double
        Return oppDefRating / leagueAvgDefRating ' >1.0 = favorable matchup
    End Function
    
    ' Whistle/FTA context: free_throw_attempts_per_game, foul_call_rate
    Public Function WhistleContext(ftaPerGame As Double, foulRate As Double) As Double
        Return ftaPerGame * foulRate
    End Function
End Class
```

**Current State**: No feature engineering module exists  
**Action Required**: Create `FeatureEngineer.vb` with 4 core functions

---

### D. Correlation Guard Combiner
```vbnet
' NEW REQUIREMENT: Multi-dimensional correlation guard
Public Function PassesCorrelationGuard(leg1 As PropLine, leg2 As PropLine) As Boolean
    ' Same player, different markets: check correlation matrix
    If leg1.PlayerId = leg2.PlayerId Then
        Dim corr = GetCorrelation(leg1.Market, leg2.Market)
        Return Math.Abs(corr) < 0.45 ' ρ < 0.45
    End If
    
    ' Same team: check team correlation
    If leg1.TeamId = leg2.TeamId Then
        Return GetTeamCorrelation(leg1, leg2) < 0.30 ' stricter threshold
    End If
    
    ' Same game: check game script correlation
    If leg1.GameId = leg2.GameId Then
        Return GetGameScriptCorrelation(leg1, leg2) < 0.35
    End If
    
    Return True ' No correlation risk
End Function
```

**Current State**: ParlayBuilder.vb has basic ρ < 0.45 check  
**Action Required**: Enhance with multi-dimensional correlation (player, team, game)

---

### E. VS Code Task Integration
```json
{
  "label": "EQ12 Props: Fetch Odds (All Sources)",
  "type": "shell",
  "command": "dotnet",
  "args": ["run", "--project", "${workspaceFolder}/src/props/PropsEngine.csproj", "--", "fetch-all"],
  "group": "build",
  "problemMatcher": []
}
```

**Current State**: No VS Code tasks for Props workflow  
**Action Required**: Create `.vscode/tasks_props_enhanced.json` with 10+ tasks

---

### F. 7-Step Runbook
```
1. DB Initialization    → sqlcmd -i schema.sql
2. Source Registry      → Load data_sources_registry.json
3. Feature Service      → Start FeatureEngineer on Pi
4. Odds Ingestion       → Parallel fetch from 100 sources
5. Pi Inference         → TensorFlow Lite predictions
6. Parlay Builder       → Correlation-guarded combiner
7. VS Code Monitoring   → Real-time dashboard task
```

**Current State**: Individual components exist, no orchestration  
**Action Required**: Create runbook script + VS Code task launcher

---

## 4. Adaptation Roadmap

### Phase 1: Core Enhancements (High Priority)

**Task 1.1**: Enhance OddsIngestor with Retry/Backoff  
**File**: `src/props/OddsIngestor.vb`  
**Changes**:
- Add `GetJsonAsync<T>(url)` with 4-attempt retry loop
- Exponential backoff: 200ms * 2^attempt
- Update `FetchBookLinesAsync()` to use new retry pattern
- **Estimate**: 30 minutes

**Task 1.2**: Create 100-Source JSON Registry  
**File**: `data/data_sources_registry.json`  
**Structure**:
- 100 providers (OddsAPI, PrizePicks, Underdog, DraftKings, FanDuel, etc.)
- Fields: id, name, endpoint, auth_type, rate_limit, reliability_score, markets
- **Estimate**: 2 hours (research + documentation)

**Task 1.3**: Build Feature Engineering Service  
**File**: `src/props/FeatureEngineer.vb`  
**Functions**:
- `AdjustForPace()` - Normalize for team pace
- `OnOffImpact()` - Net rating differential
- `DvPFactor()` - Defense vs Position
- `WhistleContext()` - Foul rate adjustments
- **Estimate**: 1 hour

**Task 1.4**: Implement Correlation Guard Combiner  
**File**: `src/props/ParlayBuilder.vb`  
**Enhancement**:
- Add `PassesCorrelationGuard(leg1, leg2)` with 3 checks:
  - Same player: market correlation (ρ < 0.45)
  - Same team: team correlation (ρ < 0.30)
  - Same game: game script correlation (ρ < 0.35)
- **Estimate**: 45 minutes

---

### Phase 2: Workflow Integration (Medium Priority)

**Task 2.1**: Create VS Code Task Suite  
**File**: `.vscode/tasks_props_enhanced.json`  
**Tasks** (10 total):
1. Fetch Odds (All Sources)
2. Engineer Features
3. Run Pi Inference
4. Build Parlays
5. Size Bets (Kelly)
6. Save to Database
7. View Today's Candidates
8. Monitor Sharp Action
9. Performance Report
10. Full Pipeline (1→9)
- **Estimate**: 1.5 hours

**Task 2.2**: Implement 7-Step Runbook  
**File**: `scripts/eq12_props_runbook.ps1`  
**Workflow**:
```powershell
# Step 1: Initialize database
sqlcmd -S localhost -d EQ12Props -i "$PSScriptRoot\..\src\props\schema.sql"

# Step 2: Load source registry
dotnet run --project src/props/PropsEngine.csproj -- load-registry

# Step 3-7: Execute pipeline
dotnet run --project src/props/PropsEngine.csproj -- run-pipeline --full
```
- **Estimate**: 1 hour

---

### Phase 3: Database Schema Extensions (Low Priority)

**Task 3.1**: Add Feature Engineering Columns  
**File**: `src/props/schema.sql`  
**Changes**:
```sql
ALTER TABLE Features ADD pace_adjusted_value DECIMAL(10,4);
ALTER TABLE Features ADD on_off_impact DECIMAL(10,4);
ALTER TABLE Features ADD dvp_factor DECIMAL(10,4);
ALTER TABLE Features ADD whistle_context DECIMAL(10,4);
```
- **Estimate**: 30 minutes

**Task 3.2**: Create Correlation Matrix Tables  
**File**: `src/props/schema.sql`  
**New Tables**:
- `dim_player_market_corr` (player-level correlations)
- `dim_team_corr` (team-level correlations)
- `dim_game_script_corr` (game script correlations)
- **Estimate**: 1 hour

---

## 5. Amazon Echo Frames Evaluation

### Device Capabilities

**Echo Frames (3rd Generation)**:
- **Hands-free Alexa**: Voice commands without phone interaction
- **VIP Filter**: Priority notifications from selected apps
- **Open-ear Audio**: Private listening without blocking ambient sound
- **Battery Life**: 4 hours continuous use, 14 hours standby
- **Connectivity**: Bluetooth 5.0 to smartphone
- **Price**: ~$270

---

### EQ12 Betting System Integration Analysis

#### ✅ **Potential Value**

**1. Live Betting Alerts** (HIGH VALUE)
```
Scenario: Sharp line movement detected on Trae Young O25.5 points
Echo Frames: "Trae Young points line moved from 25.5 to 27.5 at DraftKings. 
              Sharp action detected. EV now 8.2%. Recommend 0.5% Kelly."

User Action: Immediate voice response "Alexa, place bet Trae Young over 27.5"
```

**2. Hands-Free Monitoring** (MEDIUM VALUE)
- Monitor EQ12 system while cooking, driving, working out
- Get parlay performance updates without checking phone
- Injury/lineup alerts during the day

**3. Discreet Notifications** (MEDIUM VALUE)
- Private alerts in public (open-ear audio)
- No phone checking in meetings/social situations
- VIP filter for high-EV opportunities only

---

#### ❌ **Limitations & Concerns**

**1. Limited Display** (CRITICAL ISSUE)
- No screen → can't show correlation matrices, odds tables, parlay slips
- Voice-only output → difficult for numerical data
- User must rely on smartphone for visual confirmation

**2. Battery Constraints** (MODERATE ISSUE)
- 4 hours continuous use → won't last full NBA slate (7+ hours)
- Need to remove/charge during games

**3. Integration Complexity** (HIGH EFFORT)
- Requires Alexa Skills Kit development
- EQ12 → AWS Lambda → Alexa Skill → Echo Frames pipeline
- Authentication, security, rate limits
- **Estimate**: 40+ hours development

**4. Voice Accuracy** (MODERATE ISSUE)
- Betting commands require 100% accuracy (player names, lines, amounts)
- Voice misinterpretation could place wrong bets
- High-risk for monetary transactions

---

### Alternative Solutions (Better ROI)

**1. Smartwatch (Apple Watch, Galaxy Watch)** - RECOMMENDED
- Visual display for odds tables, correlation matrices
- Haptic alerts for sharp action
- Lower integration complexity (native iOS/Android notifications)
- **Cost**: $200-400 (comparable to Echo Frames)
- **Development**: 10-15 hours (push notification service)

**2. Desktop Notifications (VS Code Extension)** - RECOMMENDED
- Zero hardware cost
- Rich visual displays (tables, charts, slips)
- Already have VS Code task infrastructure
- **Development**: 5-8 hours

**3. Telegram Bot** (EXISTING INFRASTRUCTURE)
- Already configured in EQ12: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- Rich formatting (Markdown tables)
- **Cost**: Free
- **Development**: 2-3 hours

---

### Final Recommendation: Echo Frames

**VERDICT**: ❌ **NOT RECOMMENDED** for EQ12 betting system

**Reasoning**:
1. **Poor data visualization**: Betting decisions require visual analysis (odds tables, correlation matrices, line movements). Voice-only output is insufficient.
2. **High integration complexity**: 40+ hours development for marginal benefit.
3. **Better alternatives exist**:
   - **Telegram Bot**: Already configured, free, rich formatting (2-3 hours)
   - **VS Code Extension**: Zero hardware cost, visual displays (5-8 hours)
   - **Smartwatch**: Better display + haptics, easier integration (10-15 hours)

**If hands-free is critical**: Use **Telegram voice notifications** (1 hour setup) instead of Echo Frames.

---

## 6. Execution Priority

### Immediate Actions (Next 4 Hours)

1. **Enhance OddsIngestor with Retry/Backoff** (30 min)
2. **Build Feature Engineering Service** (1 hour)
3. **Implement Correlation Guard Combiner** (45 min)
4. **Create VS Code Task Suite** (1.5 hours)

**Total**: ~3.75 hours to production-ready enhancement

---

### Next Steps (4-8 Hours)

5. **Create 100-Source JSON Registry** (2 hours)
6. **Implement 7-Step Runbook** (1 hour)
7. **Database Schema Extensions** (1.5 hours)
8. **Testing & Validation** (2 hours)

---

## 7. Success Criteria

**Functionality**:
- ✅ OddsIngestor retries failed requests with exponential backoff
- ✅ 100 sources registered in JSON config
- ✅ Feature engineering calculates pace, on/off, DvP, whistle context
- ✅ Correlation guard blocks high-ρ parlays (player, team, game)
- ✅ VS Code tasks automate full workflow
- ✅ 7-step runbook executes end-to-end

**Performance**:
- ✅ 58-64% win probability per leg (validated via backtesting)
- ✅ 1/4 Kelly sizing with max 0.75% risk per bet
- ✅ ρ < 0.45 for all parlay legs

**Operations**:
- ✅ Logs written to `C:\EQ12\logs` with UTC timestamps
- ✅ Database on D:\ (EQ12Props)
- ✅ Pi inference service running on 192.168.1.80
- ✅ VS Code tasks provide one-click execution

---

## 8. Resources Required

**Hardware**: ✅ Already confirmed sufficient (12 cores, 31.77GB RAM, Pi)  
**Storage**: ✅ D:\ ready for Props DB (399GB free)  
**Software**:
- VB.NET (Visual Studio or .NET CLI)
- SQL Server Express (free, sufficient for Props workload)
- Python 3.12 (Pi inference service)
- VS Code (task automation)

**External Dependencies**:
- OddsAPI account ($50/month for 500 requests/day)
- TensorFlow Lite models (train on Pi, ~2GB storage)

---

## 9. Next Steps

**Immediate** (Run now):
```powershell
# Navigate to workspace
cd C:\EQ12_BROKEN_20251122_210342

# Start with Task 1.1: Enhance OddsIngestor
code src\props\OddsIngestor.vb
```

**Confirm with user**:
- Priority order correct?
- Proceed with Phase 1 (Core Enhancements) first?
- Skip Echo Frames integration per recommendation?

---

**End of Adaptation Plan**
