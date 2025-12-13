# EQ12 Sports Betting Orchestrator & Dashboard

## 🎯 **Overview**

The **EQ12 Sports Betting Orchestrator** is a Windows-native VB.NET application that provides a unified control panel for your entire betting automation stack. It scans, monitors, orchestrates, and visualizes all components of the EQ12 ecosystem.

---

## 🏗️ **Solution Structure**

```
EQ12SportsBettingOrchestrator.sln
│
├── EQ12.UI.Dashboard                # Main Windows Forms/WPF application
│   ├── Forms/
│   │   ├── MainDashboard.vb        # Primary UI with grids and controls
│   │   ├── OddsViewer.vb           # Live odds display
│   │   ├── ParlayBuilder.vb        # Parlay generation UI
│   │   └── SystemMonitor.vb        # System health dashboard
│   └── Controls/
│       ├── GameGrid.vb             # Reusable game display grid
│       └── ApiStatusCard.vb        # API health indicator
│
├── EQ12.Core.FileScanner            # Workspace scanning engine
│   ├── Eq12Scanner.vb              # Main scanner class
│   ├── Manifest models (embedded)  # ProjectInfo, ApiInfo, etc.
│   └── eq12_manifest.json (output) # Generated scan results
│
├── EQ12.Core.ApiClient              # API integration layer
│   ├── OddsApiClient.vb            # The Odds API client
│   ├── WeatherApiClient.vb         # Weather data client
│   └── TelegramClient.vb           # Telegram bot integration
│
└── EQ12.Core.Orchestrator           # Script execution engine
    ├── ScriptOrchestrator.vb       # Python/PowerShell runner
    └── ProcessMonitor.vb           # Background process tracking
```

---

## 🚀 **Quick Start**

### **1. Open Solution in Visual Studio**

```powershell
cd C:\EQ12_BROKEN_20251122_210342\visual_studio_projects\EQ12SportsBettingOrchestrator
start EQ12SportsBettingOrchestrator.sln
```

### **2. Build All Projects**

In Visual Studio:
- **Build → Build Solution** (Ctrl+Shift+B)
- Or: Right-click solution → **Build Solution**

### **3. Run File Scanner (Test Core Functionality)**

Create a console app or use this test code:

```vbnet
Imports EQ12.Core.FileScanner

Module TestScanner
    Sub Main()
        Dim scanner As New Eq12Scanner("C:\EQ12_BROKEN_20251122_210342")
        Dim manifest = scanner.Scan()
        
        scanner.SaveManifest(manifest, "C:\EQ12\reports\eq12_manifest.json")
        
        Console.WriteLine($"✅ Scanned {manifest.Projects.Count} projects")
        Console.WriteLine($"✅ Found {manifest.Apis.Count} APIs")
        Console.ReadLine()
    End Sub
End Module
```

### **4. Test Script Orchestrator**

```vbnet
Imports EQ12.Core.Orchestrator

Module TestOrchestrator
    Sub Main()
        Dim orch As New ScriptOrchestrator("C:\EQ12_BROKEN_20251122_210342")
        
        ' Run system scan
        Dim result = orch.RunSystemScan()
        
        If result.Success Then
            Console.WriteLine("✅ System scan completed")
            Console.WriteLine(result.Output)
        Else
            Console.WriteLine("❌ System scan failed")
            Console.WriteLine(result.ErrorOutput)
        End If
        
        Console.ReadLine()
    End Sub
End Module
```

---

## 📋 **Core Features**

### **1. File Scanner** (`EQ12.Core.FileScanner`)

**Scans for**:
- ✅ Python scripts (`.py`) - Classifies by purpose (parlay, odds, scraper, etc.)
- ✅ PowerShell scripts (`.ps1`) - Identifies automation wrappers
- ✅ VB.NET projects (`.vbproj`) - Catalogs existing projects
- ✅ Configuration files (`.json`, `.env`) - Maps API keys and settings
- ✅ Databases (`.db`) - Tracks SQLite databases with sizes
- ✅ Log files - Monitors log directory growth

**Outputs**:
- `eq12_manifest.json` - Comprehensive workspace inventory
- Categorized by type, tags, language, size, last modified

**Example Usage**:
```vbnet
Dim scanner As New Eq12Scanner("C:\EQ12_BROKEN_20251122_210342")
Dim manifest = scanner.Scan()

' Filter Python betting scripts
Dim bettingScripts = manifest.Projects _
    .Where(Function(p) p.Tags.Contains("betting")) _
    .ToList()

Console.WriteLine($"Found {bettingScripts.Count} betting scripts")
```

---

### **2. API Client** (`EQ12.Core.ApiClient`)

**Integrations**:
- **The Odds API** - Live sports odds (MLB, NBA, NFL, CFB, etc.)
- **Weather API** - Stadium weather conditions
- **Telegram Bot API** - Alert notifications

**Example - Get MLB Odds**:
```vbnet
Dim apiKey = Environment.GetEnvironmentVariable("ODDS_API_KEY")
Dim client As New OddsApiClient(apiKey)

Dim mlbOdds = Await client.GetMlbOddsAsync()

For Each game In mlbOdds
    Console.WriteLine($"{game.AwayTeam} @ {game.HomeTeam}")
    Console.WriteLine($"  Start: {game.CommenceTime}")
    
    For Each bookmaker In game.Bookmakers
        Console.WriteLine($"  {bookmaker.Title}")
        For Each market In bookmaker.Markets
            For Each outcome In market.Outcomes
                Console.WriteLine($"    {outcome.Name}: {outcome.Price}")
            Next
        Next
    Next
Next
```

---

### **3. Script Orchestrator** (`EQ12.Core.Orchestrator`)

**Capabilities**:
- ✅ Execute Python scripts with arguments
- ✅ Execute PowerShell scripts
- ✅ Capture stdout/stderr
- ✅ Background process support
- ✅ Detect running processes (e.g., 20K prompt execution)

**Convenience Methods**:
- `RunHrParlayBuilder()` - Generate HR parlays
- `RunOddsUpdate()` - Refresh odds data
- `RunSec13FScraper(maxFilings)` - Scrape hedge fund filings
- `RunVBNETScan()` - Scan VB.NET codebase
- `RunSystemScan()` - System health check
- `IsPromptExecutionRunning()` - Detect background AI processing

**Example - Run Parlay Builder**:
```vbnet
Dim orch As New ScriptOrchestrator("C:\EQ12_BROKEN_20251122_210342")

Dim result = orch.RunHrParlayBuilder()

If result.Success Then
    Console.WriteLine("✅ Parlay generated successfully")
    Console.WriteLine(result.Output)
Else
    Console.WriteLine("❌ Parlay generation failed")
    Console.WriteLine(result.ErrorOutput)
End If

Console.WriteLine($"Execution time: {result.ExecutionTimeMs}ms")
```

---

## 🎨 **Main Dashboard Design** (To Be Implemented)

### **Top Navigation Bar**
```
╔═══════════════════════════════════════════════════════════════╗
║ EQ12 Sports Betting Orchestrator                              ║
║ Status: ✅ All Systems Online | CPU: 45% | RAM: 12/32 GB     ║
╚═══════════════════════════════════════════════════════════════╝
```

### **Left Sidebar (Module Tree)**
```
📁 Projects (147)
  ├── 🐍 Python Scripts (89)
  │   ├── Betting Engines (12)
  │   ├── Scrapers (8)
  │   └── API Connectors (15)
  ├── 💻 PowerShell Scripts (32)
  └── 🔷 VB.NET Projects (8)

📡 APIs (54 enabled)
  ├── Odds (10)
  ├── Props (13)
  └── News (25)

💾 Databases (4)
  ├── prompt_execution.db (580 MB)
  ├── sec_13f_holdings.db (12 MB)
  └── odds_cache.db (45 MB)
```

### **Center Panel - Upcoming Games Grid**
```
┌─────────────────────────────────────────────────────────────┐
│ League  │ Time    │ Matchup          │ Spread │ Total │ ML │
├─────────────────────────────────────────────────────────────┤
│ MLB     │ 7:05 PM │ NYY @ BOS        │ -1.5   │ 8.5   │-140│
│ NBA     │ 7:30 PM │ LAL @ BOS        │ +3.5   │ 225.5 │+125│
│ NFL     │ 8:20 PM │ BUF @ KC         │ -2.5   │ 49.5  │-130│
└─────────────────────────────────────────────────────────────┘
```

### **Right Panel - Edge Signals**
```
┌─────────────────────────────────────────────────────────────┐
│ 🔥 High-EV Opportunities                                    │
├─────────────────────────────────────────────────────────────┤
│ Aaron Judge OVER 0.5 HR (+140)                              │
│   Model: 58% | Book: 41% | Edge: +17% | ⭐⭐⭐             │
│                                                              │
│ Shohei Ohtani OVER 1.5 H+R+RBI (-110)                       │
│   Model: 62% | Book: 52% | Edge: +10% | ⭐⭐               │
└─────────────────────────────────────────────────────────────┘
```

### **Bottom Control Panel**
```
[🔄 Refresh Odds] [⚡ Run HR Parlay] [📊 Run Simulation] 
[📱 Send Telegram] [🔍 System Scan] [📈 View Reports]
```

---

## 🔧 **Build & Deployment**

### **Prerequisites**
- Visual Studio 2022 (or VS 2019)
- .NET Framework 4.8 or .NET 6.0+
- Python 3.12 (for script execution)
- PowerShell 5.1+

### **NuGet Packages Required**
```xml
<ItemGroup>
  <!-- Core Framework -->
  <PackageReference Include="System.Text.Json" Version="8.0.0" />
  
  <!-- UI (WinForms/WPF) -->
  <PackageReference Include="MaterialDesignThemes" Version="4.9.0" />
  <PackageReference Include="LiveChartsCore.SkiaSharpView.WinForms" Version="2.0.0-rc2" />
  
  <!-- HTTP Client -->
  <PackageReference Include="Microsoft.Extensions.Http" Version="8.0.0" />
</ItemGroup>
```

### **Build Steps**
1. Restore NuGet packages: `nuget restore`
2. Build solution: `msbuild EQ12SportsBettingOrchestrator.sln /p:Configuration=Release`
3. Output: `bin\Release\EQ12.UI.Dashboard.exe`

---

## 🎯 **Integration with Existing EQ12 Stack**

### **Connects To**:
1. **100-Source Betting Registry** (`data/data_sources_registry.json`)
   - Loads enabled APIs automatically
   - Displays reliability scores
   
2. **Python Betting Scripts** (`scripts/`)
   - Executes via ScriptOrchestrator
   - Captures JSON output for display
   
3. **SEC 13F Scraper** (`scripts/eq12_sec_13f_scraper.py`)
   - Runs hedge fund data collection
   - Displays Citadel holdings
   
4. **VB.NET Scan Orchestrator** (`scripts/EQ12_VBNET_SCAN_ORCHESTRATOR.ps1`)
   - Generates code quality reports
   - Displays auto-fixable issues
   
5. **20K Prompt Execution** (background detection)
   - Monitors for running processes
   - Prevents resource conflicts

---

## 📊 **Usage Examples**

### **Scan Workspace on Startup**
```vbnet
' In Form_Load event
Private Sub MainDashboard_Load(sender As Object, e As EventArgs) Handles MyBase.Load
    Dim scanner As New Eq12Scanner(_workspaceRoot)
    Dim manifest = scanner.Scan()
    
    ' Populate UI
    PopulateProjectTree(manifest.Projects)
    PopulateApiList(manifest.Apis)
    PopulateDatabaseList(manifest.Databases)
    
    ' Check for background processes
    Dim orch As New ScriptOrchestrator(_workspaceRoot)
    If orch.IsPromptExecutionRunning() Then
        lblStatus.Text = "⚠️ Prompt execution running - LOW IMPACT MODE"
        lblStatus.ForeColor = Color.Orange
    End If
End Sub
```

### **Fetch Live Odds on Button Click**
```vbnet
Private Async Sub btnRefreshOdds_Click(sender As Object, e As EventArgs) Handles btnRefreshOdds.Click
    Dim apiKey = Environment.GetEnvironmentVariable("ODDS_API_KEY")
    Using client As New OddsApiClient(apiKey)
        Dim mlbOdds = Await client.GetMlbOddsAsync()
        
        ' Bind to DataGridView
        dgvGames.DataSource = mlbOdds _
            .Select(Function(g) New With {
                .League = "MLB",
                .Time = g.CommenceTime.ToLocalTime().ToString("h:mm tt"),
                .Matchup = $"{g.AwayTeam} @ {g.HomeTeam}",
                .Spread = GetBestSpread(g),
                .Total = GetBestTotal(g)
            }).ToList()
    End Using
End Sub
```

### **Run Parlay Builder**
```vbnet
Private Sub btnRunParlayBuilder_Click(sender As Object, e As EventArgs) Handles btnRunParlayBuilder.Click
    Dim orch As New ScriptOrchestrator(_workspaceRoot)
    
    Dim result = orch.RunHrParlayBuilder()
    
    If result.Success Then
        ' Parse JSON output and display in UI
        txtParlayOutput.Text = result.Output
        MessageBox.Show("✅ Parlay generated successfully!", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information)
    Else
        MessageBox.Show($"❌ Error: {result.ErrorOutput}", "Failed", MessageBoxButtons.OK, MessageBoxIcon.Error)
    End If
End Sub
```

---

## 🚀 **Next Steps**

### **Phase 1** (Current - Foundation Complete)
- ✅ File scanner implemented
- ✅ API client implemented  
- ✅ Script orchestrator implemented
- ⏳ Main dashboard UI (next)

### **Phase 2** (After 20K Prompts)
- Build Windows Forms dashboard
- Implement live odds grid
- Add parlay builder UI
- Integrate Telegram alerts

### **Phase 3** (Production)
- Add real-time charts (LiveCharts)
- Implement scheduler (auto-run scripts)
- Add system tray icon
- Create installer (ClickOnce/NSIS)

---

## 📚 **Additional Resources**

- **VB.NET Master Control Panel Blueprint**: `docs/VBNET_MASTER_CONTROL_PANEL_BLUEPRINT.md`
- **VB.NET Orchestrator Guide**: `docs/VBNET_ORCHESTRATOR_GUIDE.md`
- **SEC 13F Scraper Guide**: `docs/SEC_13F_SCRAPER_GUIDE.md`
- **100-Source Betting Registry**: `data/data_sources_registry.json`

---

**Status**: Core Infrastructure Complete ✅
**Priority**: Build Main Dashboard UI (Phase 2)
**ETA**: 8-12 hours after 20K prompts complete (~54 hours)
**ROI**: High - Unified control panel for entire EQ12 stack
