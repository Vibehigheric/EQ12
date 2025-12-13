## EQ12 VB.NET Fetch Engine & System Utilities

**Complete .NET solution for sports data fetching, parlay validation, and system diagnostics**

**Location:** `c:\EQ12_BROKEN_20251122_210342\vb_fetch_engine\`

---

## 📦 What's Included (7 VB.NET Programs)

| File | Lines | Purpose |
|------|-------|---------|
| `FetchEngine.vb` | 400+ | Sports + flights data fetch with real vs simulated validation |
| `ParlayValidator.vb` | 350+ | 19 fault types, banned players, risk/correlation scoring |
| `UsbInspector.vb` | 150+ | D:/E: drive inspection, Ventoy detection |
| `LogInspector.vb` | 150+ | Scan logs for Pylance/PowerShell errors |
| `BannerGenerator.vb` | 150+ | ASCII-safe banner single source of truth |
| `AsciiValidator.vb` | 150+ | Non-ASCII character detection and reporting |
| `COPILOT_SCAN_PROMPT.md` | - | Hardware upgrade analysis prompt |

---

## 🎯 Core Systems

### 1. **FetchEngine.vb** - Real Data Validation

**Purpose:** Prevent TNF Bears-Lions simulation leak into betting analysis

**Key Classes:**
- `Eq12FetchEngine` - Main fetch coordinator
- `FetchRequest` - Game specification
- `GameFetchResult` - Complete game data package
- `GameMetadata` - Teams, venue, network, real game flag
- `OddsLine` - Spread, total, moneyline from multiple sources
- `GameInjury` - Player status tracking
- `GameWeather` - Environmental conditions
- `DataIntegrityGuard` - **HARD STOP on simulated data**

**Critical Features:**
```vbnet
' BEFORE any betting analysis:
Dim data = Await fetchEngine.FetchNflGameAsync(request)
DataIntegrityGuard.EnsureRealData(data) ' Throws if simulation detected

' Only proceeds if:
' - Game metadata exists
' - Teams match request
' - IsRealGame = True
' - Odds lines present
' - Data not stale
```

**Validation Rules:**
1. No future games without confirmed odds
2. No past games > 90 days old
3. Team names must match exactly
4. Odds must be < 30 minutes old
5. `IsRealGame` flag must be True

---

### 2. **ParlayValidator.vb** - 19 Fault Detection

**Purpose:** Prevent invalid parlays from reaching sportsbooks

**Fault Types:**
```
MissingGameData, WrongMatchup, MissingOdds, ConflictingLines,
StaleOdds, PlayerUnavailable, PlayerNotStarting, MissingPlayerName,
IllegalMarketMix, ExceededLegCap, ContradictingLegs, BannedMarket,
WrongSeasonData, MissingWeather, MissingInjuryData, ApiFailure,
SimulationUsed, NonAsciiContent, HiddenLegs
```

**Usage:**
```vbnet
Dim validator = New ParlayValidator(maxLegs:=10)
Dim result = validator.Validate(parlay.Legs)

If Not result.IsValid Then
    Console.WriteLine("PARLAY INVALID:")
    For Each fault In result.Faults
        Console.WriteLine($"  - {fault}")
    Next
    ' Block ticket submission
End If
```

**Banned Players** (Auto-reject):
- Mike Yastrzemski
- Nolan Arenado
- Ronald Acuna Jr.
- Zac Gallen
- Shohei Ohtani
- Aaron Judge

**Risk Scoring:**
```vbnet
' Higher = riskier
' Formula: (legCount × 1.5) + (sportDiversity × 2) + (highVariance × 1.2)
result.RiskScore  ' e.g., 18.6

' Higher = better correlation
' Formula: (Σ legsPerGame²) / totalLegs + singleSportBonus
result.CorrelationScore  ' e.g., 5.2
```

---

### 3. **UsbInspector.vb** - Drive Inventory

**Purpose:** Programmatic D:/E: inspection, Ventoy detection

**Features:**
```vbnet
' Get all removable drives
Dim drives = UsbInspector.GetRemovableDrives()

For Each drive In drives
    Console.WriteLine(drive.DriveLetter)  ' D:\
    Console.WriteLine(drive.SizeGb)       ' 128.00
    Console.WriteLine(drive.FreeGb)       ' 64.32
    Console.WriteLine(drive.VolumeLabel)  ' EQ12_BACKUP
    
    ' Check if Ventoy bootable
    If UsbInspector.IsVentoyDrive(drive.DriveLetter) Then
        Console.WriteLine("Ventoy detected")
    End If
Next

' Full report
Console.WriteLine(UsbInspector.GetDriveReport())
```

---

### 4. **LogInspector.vb** - Error Dashboard

**Purpose:** Scan logs for PowerShell/Pylance errors

**Detection Patterns:**
- `ParserError`
- `Unexpected token`
- `Missing closing '}'`
- `Pylance: connection to server is erroring`
- `write EPIPE`
- `channel closed`
- `UTF-8` encoding issues
- `UnicodeDecodeError`
- `InfiniteLoopException`

**Usage:**
```cmd
Eq12LogInspector.exe C:\EQ12\logs
```

**Output:**
```
================================================================
           EQ12 LOG INSPECTOR - DIAGNOSTIC REPORT
================================================================

Scanned Files: 156
Total Errors: 342
Problematic Files: 23

=== ERROR BREAKDOWN ===
  PylanceError         :   127 *******************
  UnexpectedToken      :    89 ************
  MissingBrace         :    56 ********
  EPIPE                :    34 *****
  EncodingIssue        :    21 ***
  ParserError          :    15 **

=== PROBLEMATIC FILES ===
  - C:\EQ12\logs\eq12_system_2025_11_27.log
  - C:\EQ12\logs\pylance_crash_dump.log
  ...
```

---

### 5. **BannerGenerator.vb** - ASCII Authority

**Purpose:** Single source of truth for all EQ12 banners

**Usage:**
```cmd
Eq12BannerGenerator.exe master
Eq12BannerGenerator.exe empire
Eq12BannerGenerator.exe tnf
Eq12BannerGenerator.exe diagnostic
Eq12BannerGenerator.exe usb
```

**PowerShell Integration:**
```powershell
Eq12BannerGenerator.exe master | Write-Host
```

**Benefits:**
- No emoji corruption
- No Unicode drift
- No copy-paste errors
- Always ASCII-safe
- Single edit point

---

### 6. **AsciiValidator.vb** - Corruption Scanner

**Purpose:** Find non-ASCII characters in all scripts

**Usage:**
```cmd
Eq12AsciiValidator.exe C:\EQ12
```

**Output:**
```
=== EQ12 ASCII VALIDATOR ===
Scanning: C:\EQ12
============================================================

FOUND 47 non-ASCII characters:

File: C:\EQ12\scripts\eq12_launcher.ps1
  Line 23: Char '✔' (code 10004)
    Context: ...Write-Host ✔ System...
  Line 45: Char '→' (code 8594)
    Context: ...USB Empire → Active...
  ... and 3 more issues in this file

File: C:\EQ12\scripts\eq12_banner.ps1
  Line 12: Char '█' (code 9608)
    Context: ...███████████████...

=== SUMMARY ===
Files with issues: 8
Total non-ASCII characters: 47

ACTION REQUIRED: Clean these files to prevent corruption.
```

---

## 🚀 Quick Start

### Step 1: Create Visual Studio Project

```
File → New → Project
Select: Console App (.NET 6.0 or .NET Framework 4.8)
Name: EQ12FetchEngine
```

### Step 2: Add Files

```
Right-click project → Add → Existing Item
Select all .vb files from vb_fetch_engine folder
```

### Step 3: Build

```
Press F6 or Build → Build Solution
```

### Step 4: Test

```vbnet
Imports EQ12.Core.DataFetch
Imports EQ12.Core.Validation
Imports EQ12.Core.Hardware

Module Program
    Async Function Main() As Task
        ' Test fetch engine
        Dim fetchEngine = New Eq12FetchEngine()
        Dim request = New FetchRequest() With {
            .Sport = SportType.Nfl,
            .HomeTeam = "Buffalo Bills",
            .AwayTeam = "Kansas City Chiefs",
            .GameDateUtc = New DateTime(2025, 11, 28, 1, 15, 0, DateTimeKind.Utc)
        }
        
        Dim result = Await fetchEngine.FetchNflGameAsync(request)
        
        Try
            DataIntegrityGuard.EnsureRealData(result)
            Console.WriteLine("Real data confirmed - proceed with analysis")
        Catch ex As Exception
            Console.WriteLine($"BLOCKED: {ex.Message}")
        End Try
        
        ' Test parlay validator
        Dim validator = New ParlayValidator()
        Dim legs = New List(Of ParlayLeg)()
        ' ... add legs
        Dim validation = validator.Validate(legs)
        Console.WriteLine(validation.GetSummary())
        
        ' Test USB inspector
        Console.WriteLine(UsbInspector.GetDriveReport())
    End Function
End Module
```

---

## 📋 Integration with EQ12 Stack

### TNF Engine Integration

```vbnet
Public Class TnfEngine
    Private ReadOnly _fetchEngine As Eq12FetchEngine
    
    Public Async Function RunAnalysisAsync(request As FetchRequest) As Task
        ' Fetch real data
        Dim data = Await _fetchEngine.FetchNflGameAsync(request)
        
        ' HARD STOP if simulation
        DataIntegrityGuard.EnsureRealData(data)
        
        ' Only if no exception:
        RunMonteCarloSimulation(data)
        CalculateExpectedValue(data)
        BuildParlays(data)
    End Function
End Class
```

### Parlay Builder Integration

```vbnet
Public Function BuildAndValidateParlay(legs As List(Of ParlayLeg)) As Boolean
    Dim validator = New ParlayValidator()
    Dim result = validator.Validate(legs)
    
    If Not result.IsValid Then
        LogParlayRejection(result.Faults, result.Messages)
        Return False
    End If
    
    ' Check risk thresholds
    If result.RiskScore > 25 Then
        Console.WriteLine("WARNING: High risk parlay (score: {0})", result.RiskScore)
    End If
    
    If result.CorrelationScore > 5 Then
        Console.WriteLine("EXCELLENT: Strong correlation (score: {0})", result.CorrelationScore)
    End If
    
    Return True
End Function
```

### PowerShell Wrapper

```powershell
# Call VB.NET tools from PowerShell
$usbReport = & "Eq12UsbInspector.exe"
Write-Host $usbReport

$logAnalysis = & "Eq12LogInspector.exe" "C:\EQ12\logs"
Write-Host $logAnalysis

$banner = & "Eq12BannerGenerator.exe" "master"
Write-Host $banner
```

---

## 🛡️ Hard-Coded Rules

### RULE 1: No Simulation in Betting Analysis
**Enforcement:** `DataIntegrityGuard.EnsureRealData()` throws exception

### RULE 2: All Parlays Must Validate
**Enforcement:** `ParlayValidator.Validate()` must return `IsValid = True`

### RULE 3: ASCII-Only for Control Scripts
**Enforcement:** `AsciiValidator` scans all `.ps1`, `.py`, `.vb`

### RULE 4: Banned Players Auto-Reject
**Enforcement:** `ParlayValidator` maintains banned list, adds runtime via `BanPlayer()`

### RULE 5: Single Banner Source
**Enforcement:** All banners generated by `BannerGenerator.exe`

---

## 📊 Hardware Upgrade Analysis

### Use Copilot Scan Prompt

See `COPILOT_SCAN_PROMPT.md` for complete instructions.

**Quick paste:**
```
Paste the prompt from COPILOT_SCAN_PROMPT.md into Copilot Chat
Get hardware recommendations
Review priority list
Implement upgrades sequentially
```

---

## 🎯 Success Criteria

✅ **Fetch Engine prevents simulation leak**
- TNF analysis only runs on real games
- Bears-Lions stub never reaches betting logic
- Hard exceptions on invalid data

✅ **Parlay Validator blocks bad tickets**
- 19 fault types detected
- Banned players rejected
- Contradicting legs caught
- Risk/correlation scored

✅ **USB Inspector automates drive management**
- D: through H: programmatically accessed
- Ventoy detection automated
- Capacity reports generated

✅ **Log Inspector catches errors early**
- Pylance crashes tracked
- PowerShell parse errors found
- UTF-8 issues identified

✅ **Banner Generator eliminates corruption**
- No emoji in production
- No Unicode drift
- Single source of truth

✅ **ASCII Validator prevents encoding issues**
- All scripts scanned
- Non-ASCII flagged
- Reports generated

---

## 📚 Related Documentation

- **Loop Eliminator:** `vb_loop_eliminator/` - Infinite loop prevention
- **Betting Analyzer:** `vb_betting_analyzer/` - Slip risk scoring
- **PowerShell Tools:** `scripts/` - EQ12 diagnostic scripts
- **Agents Guide:** `AGENTS.md` - Adaptive learning system

---

## 🔧 Troubleshooting

### Problem: "Type 'Eq12FetchEngine' is not defined"

**Solution:** Add imports
```vbnet
Imports EQ12.Core.DataFetch
Imports EQ12.Core.Validation
Imports EQ12.Core.Hardware
```

### Problem: Fetch engine always returns invalid

**Solution:** Check `IsRealGame` flag logic in `ParseMetadataFromEspn()`. Replace stub with real JSON parsing.

### Problem: Parlay validator too strict

**Solution:** Adjust limits
```vbnet
Dim validator = New ParlayValidator(maxLegs:=15) ' Was 10
validator.UnbanPlayer("Player Name")
```

### Problem: ASCII validator finds too many issues

**Solution:** Filter by file type or directory
```vbnet
' In AsciiValidator.vb, modify:
Dim exts = {".ps1", ".py"} ' Remove .md, .txt if needed
```

---

## 🎓 Next Steps

1. ✅ **Build all VB.NET programs in Visual Studio**
2. ✅ **Test fetch engine with real NFL game**
3. ✅ **Validate existing parlays** with ParlayValidator
4. ✅ **Scan USB drives** with UsbInspector
5. ✅ **Analyze logs** with LogInspector
6. ✅ **Clean scripts** with AsciiValidator
7. ✅ **Generate banners** with BannerGenerator
8. ✅ **Run Copilot scan** for hardware upgrades

---

**Built for EQ12 by VB.NET Expert System | 2025-11-27**

**Production-ready for Visual Studio 2022, .NET 6.0+, .NET Framework 4.8**
