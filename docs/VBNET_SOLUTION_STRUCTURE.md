# EQ12 Master Control Center - Visual Studio Solution Structure

**Auto-Generated:** November 27, 2025  
**Target Framework:** .NET 6.0+  
**IDE:** Visual Studio 2022 or later

---

## 📁 COMPLETE FOLDER STRUCTURE

```
C:\EQ12_BROKEN_20251122_210342\visual_studio_projects\
│
├── EQ12.MasterControlCenter.sln              # Main solution file
│
├── EQ12.Core\                                 # Shared utilities & models
│   ├── EQ12.Core.vbproj
│   ├── Models\
│   │   ├── ClusterNode.vb
│   │   ├── ApiConfig.vb
│   │   ├── BettingParlay.vb
│   │   └── SystemMetrics.vb
│   ├── Utilities\
│   │   ├── DatabaseHelper.vb
│   │   ├── ProcessHelper.vb
│   │   └── LogManager.vb
│   └── Config\
│       └── EQ12Config.vb
│
├── EQ12.Core.ApiClient\                       # ✅ ALREADY BUILT
│   ├── EQ12.Core.ApiClient.vbproj
│   ├── ApiCatalog.vb                          # 22 API integrations
│   └── ApiModels\
│       ├── OddsApiResponse.vb
│       ├── EspnScoreResponse.vb
│       └── StockQuoteResponse.vb
│
├── EQ12.SportsBetting.Orchestrator\          # ✅ ALREADY BUILT  
│   ├── EQ12.SportsBetting.Orchestrator.vbproj
│   ├── BettingOrchestrator.vb                 # CLI tool
│   └── ParlayEngine.vb
│
├── EQ12.FileScanner\                          # NEW - Code analysis module
│   ├── EQ12.FileScanner.vbproj
│   ├── CodeScanner.vb                         # Directory scanner
│   ├── IssueDetector.vb                       # Lint detection
│   ├── FixPlanGenerator.vb                    # Auto-fix JSON generation
│   └── GitHubIntegration.vb                   # PR creation via Octokit
│
├── EQ12.HardwareMonitor\                      # NEW - System metrics
│   ├── EQ12.HardwareMonitor.vbproj
│   ├── MetricsCollector.vb                    # CPU/RAM/Disk monitoring
│   ├── DockerManager.vb                       # Container detection
│   └── ClusterMonitor.vb                      # Multi-node tracking
│
├── EQ12.DatabaseManager\                      # NEW - SQLite integration
│   ├── EQ12.DatabaseManager.vbproj
│   ├── PromptDatabase.vb                      # prompt_execution.db
│   ├── BettingDatabase.vb                     # betting_data.db
│   ├── HardwareDatabase.vb                    # hardware_metrics.db
│   └── ReportGenerator.vb                     # Comprehensive reports
│
├── EQ12.RayCluster\                           # NEW - Distributed computing
│   ├── EQ12.RayCluster.vbproj
│   ├── ClusterManager.vb                      # Ray cluster orchestration
│   ├── WorkloadDistributor.vb                 # Task distribution
│   └── NodeHealthCheck.vb                     # Cluster monitoring
│
├── EQ12.PythonBridge\                         # NEW - Subprocess controller
│   ├── EQ12.PythonBridge.vbproj
│   ├── PythonExecutor.vb                      # Process.Start wrapper
│   ├── JsonParser.vb                          # Response parsing
│   └── BridgeHelper.vb                        # Utility functions
│
└── EQ12.UI.Desktop\                           # NEW - Main WPF application
    ├── EQ12.UI.Desktop.vbproj
    ├── MainWindow.xaml                        # Main UI window
    ├── MainWindow.xaml.vb                     # Code-behind
    ├── ViewModels\
    │   ├── DashboardViewModel.vb
    │   ├── BettingViewModel.vb
    │   ├── HardwareViewModel.vb
    │   └── ScannerViewModel.vb
    ├── Views\
    │   ├── DashboardView.xaml
    │   ├── BettingView.xaml
    │   ├── HardwareView.xaml
    │   ├── ScannerView.xaml
    │   └── GitHubView.xaml
    ├── Controls\
    │   ├── LiveChartControl.xaml             # Real-time graphs
    │   ├── ClusterStatusControl.xaml
    │   └── ParlayDisplayControl.xaml
    └── App.xaml                               # Application entry point
```

---

## 📄 SOLUTION FILE (.sln)

**File:** `EQ12.MasterControlCenter.sln`

```sln
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1

Project("{F184B08F-C81C-45F6-A57F-5ABD9991F28F}") = "EQ12.Core", "EQ12.Core\EQ12.Core.vbproj", "{A1B2C3D4-E5F6-4789-A0B1-C2D3E4F56789}"
EndProject

Project("{F184B08F-C81C-45F6-A57F-5ABD9991F28F}") = "EQ12.Core.ApiClient", "EQ12.Core.ApiClient\EQ12.Core.ApiClient.vbproj", "{B2C3D4E5-F6A7-4890-B1C2-D3E4F5678901}"
EndProject

Project("{F184B08F-C81C-45F6-A57F-5ABD9991F28F}") = "EQ12.SportsBetting.Orchestrator", "EQ12.SportsBetting.Orchestrator\EQ12.SportsBetting.Orchestrator.vbproj", "{C3D4E5F6-A7B8-4901-C2D3-E4F567890123}"
EndProject

Project("{F184B08F-C81C-45F6-A57F-5ABD9991F28F}") = "EQ12.FileScanner", "EQ12.FileScanner\EQ12.FileScanner.vbproj", "{D4E5F6A7-B8C9-4012-D3E4-F56789012345}"
EndProject

Project("{F184B08F-C81C-45F6-A57F-5ABD9991F28F}") = "EQ12.HardwareMonitor", "EQ12.HardwareMonitor\EQ12.HardwareMonitor.vbproj", "{E5F6A7B8-C9D0-4123-E4F5-678901234567}"
EndProject

Project("{F184B08F-C81C-45F6-A57F-5ABD9991F28F}") = "EQ12.DatabaseManager", "EQ12.DatabaseManager\EQ12.DatabaseManager.vbproj", "{F6A7B8C9-D0E1-4234-F567-890123456789}"
EndProject

Project("{F184B08F-C81C-45F6-A57F-5ABD9991F28F}") = "EQ12.RayCluster", "EQ12.RayCluster\EQ12.RayCluster.vbproj", "{A7B8C9D0-E1F2-4345-6789-012345678901}"
EndProject

Project("{F184B08F-C81C-45F6-A57F-5ABD9991F28F}") = "EQ12.PythonBridge", "EQ12.PythonBridge\EQ12.PythonBridge.vbproj", "{B8C9D0E1-F2A3-4456-7890-123456789012}"
EndProject

Project("{F184B08F-C81C-45F6-A57F-5ABD9991F28F}") = "EQ12.UI.Desktop", "EQ12.UI.Desktop\EQ12.UI.Desktop.vbproj", "{C9D0E1F2-A3B4-4567-8901-234567890123}"
EndProject

Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Debug|Any CPU = Debug|Any CPU
		Release|Any CPU = Release|Any CPU
	EndGlobalSection
	GlobalSection(ProjectConfigurationPlatforms) = postSolution
		{A1B2C3D4-E5F6-4789-A0B1-C2D3E4F56789}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
		{A1B2C3D4-E5F6-4789-A0B1-C2D3E4F56789}.Debug|Any CPU.Build.0 = Debug|Any CPU
		{A1B2C3D4-E5F6-4789-A0B1-C2D3E4F56789}.Release|Any CPU.ActiveCfg = Release|Any CPU
		{A1B2C3D4-E5F6-4789-A0B1-C2D3E4F56789}.Release|Any CPU.Build.0 = Release|Any CPU
		
		{B2C3D4E5-F6A7-4890-B1C2-D3E4F5678901}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
		{B2C3D4E5-F6A7-4890-B1C2-D3E4F5678901}.Debug|Any CPU.Build.0 = Debug|Any CPU
		{B2C3D4E5-F6A7-4890-B1C2-D3E4F5678901}.Release|Any CPU.ActiveCfg = Release|Any CPU
		{B2C3D4E5-F6A7-4890-B1C2-D3E4F5678901}.Release|Any CPU.Build.0 = Release|Any CPU
		
		{C3D4E5F6-A7B8-4901-C2D3-E4F567890123}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
		{C3D4E5F6-A7B8-4901-C2D3-E4F567890123}.Debug|Any CPU.Build.0 = Debug|Any CPU
		{C3D4E5F6-A7B8-4901-C2D3-E4F567890123}.Release|Any CPU.ActiveCfg = Release|Any CPU
		{C3D4E5F6-A7B8-4901-C2D3-E4F567890123}.Release|Any CPU.Build.0 = Release|Any CPU
		
		{D4E5F6A7-B8C9-4012-D3E4-F56789012345}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
		{D4E5F6A7-B8C9-4012-D3E4-F56789012345}.Debug|Any CPU.Build.0 = Debug|Any CPU
		{D4E5F6A7-B8C9-4012-D3E4-F56789012345}.Release|Any CPU.ActiveCfg = Release|Any CPU
		{D4E5F6A7-B8C9-4012-D3E4-F56789012345}.Release|Any CPU.Build.0 = Release|Any CPU
		
		{E5F6A7B8-C9D0-4123-E4F5-678901234567}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
		{E5F6A7B8-C9D0-4123-E4F5-678901234567}.Debug|Any CPU.Build.0 = Debug|Any CPU
		{E5F6A7B8-C9D0-4123-E4F5-678901234567}.Release|Any CPU.ActiveCfg = Release|Any CPU
		{E5F6A7B8-C9D0-4123-E4F5-678901234567}.Release|Any CPU.Build.0 = Release|Any CPU
		
		{F6A7B8C9-D0E1-4234-F567-890123456789}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
		{F6A7B8C9-D0E1-4234-F567-890123456789}.Debug|Any CPU.Build.0 = Debug|Any CPU
		{F6A7B8C9-D0E1-4234-F567-890123456789}.Release|Any CPU.ActiveCfg = Release|Any CPU
		{F6A7B8C9-D0E1-4234-F567-890123456789}.Release|Any CPU.Build.0 = Release|Any CPU
		
		{A7B8C9D0-E1F2-4345-6789-012345678901}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
		{A7B8C9D0-E1F2-4345-6789-012345678901}.Debug|Any CPU.Build.0 = Debug|Any CPU
		{A7B8C9D0-E1F2-4345-6789-012345678901}.Release|Any CPU.ActiveCfg = Release|Any CPU
		{A7B8C9D0-E1F2-4345-6789-012345678901}.Release|Any CPU.Build.0 = Release|Any CPU
		
		{B8C9D0E1-F2A3-4456-7890-123456789012}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
		{B8C9D0E1-F2A3-4456-7890-123456789012}.Debug|Any CPU.Build.0 = Debug|Any CPU
		{B8C9D0E1-F2A3-4456-7890-123456789012}.Release|Any CPU.ActiveCfg = Release|Any CPU
		{B8C9D0E1-F2A3-4456-7890-123456789012}.Release|Any CPU.Build.0 = Release|Any CPU
		
		{C9D0E1F2-A3B4-4567-8901-234567890123}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
		{C9D0E1F2-A3B4-4567-8901-234567890123}.Debug|Any CPU.Build.0 = Debug|Any CPU
		{C9D0E1F2-A3B4-4567-8901-234567890123}.Release|Any CPU.ActiveCfg = Release|Any CPU
		{C9D0E1F2-A3B4-4567-8901-234567890123}.Release|Any CPU.Build.0 = Release|Any CPU
	EndGlobalSection
	GlobalSection(SolutionProperties) = preSolution
		HideSolutionNode = FALSE
	EndGlobalSection
EndGlobal
```

---

## 📦 NUGET PACKAGES (Required for All Projects)

Add to each `.vbproj` file:

```xml
<ItemGroup>
  <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
  <PackageReference Include="System.Data.SQLite.Core" Version="1.0.118" />
</ItemGroup>
```

**Additional packages by project:**

### EQ12.FileScanner
```xml
<PackageReference Include="Octokit" Version="9.0.0" />
<PackageReference Include="LibGit2Sharp" Version="0.27.2" />
```

### EQ12.UI.Desktop
```xml
<PackageReference Include="MaterialDesignThemes" Version="4.9.0" />
<PackageReference Include="MaterialDesignColors" Version="2.1.4" />
<PackageReference Include="LiveCharts.Wpf" Version="0.9.7" />
```

---

## 🏗️ BUILD INSTRUCTIONS

### Option 1: Visual Studio GUI
1. Open `EQ12.MasterControlCenter.sln` in Visual Studio 2022
2. Right-click solution → Restore NuGet Packages
3. Build → Build Solution (Ctrl+Shift+B)
4. Set `EQ12.UI.Desktop` as startup project
5. Press F5 to run

### Option 2: Command Line (MSBuild)
```powershell
# Navigate to solution directory
cd C:\EQ12_BROKEN_20251122_210342\visual_studio_projects

# Restore packages
dotnet restore EQ12.MasterControlCenter.sln

# Build solution
msbuild EQ12.MasterControlCenter.sln /p:Configuration=Release

# Run compiled executable
.\EQ12.UI.Desktop\bin\Release\net6.0-windows\EQ12.UI.Desktop.exe
```

---

## 📊 PROJECT DEPENDENCIES

```
EQ12.UI.Desktop
├── References: EQ12.Core
├── References: EQ12.FileScanner
├── References: EQ12.HardwareMonitor
├── References: EQ12.DatabaseManager
├── References: EQ12.RayCluster
└── References: EQ12.PythonBridge

EQ12.FileScanner
└── References: EQ12.Core

EQ12.HardwareMonitor
└── References: EQ12.Core

EQ12.DatabaseManager
└── References: EQ12.Core

EQ12.RayCluster
├── References: EQ12.Core
└── References: EQ12.PythonBridge

EQ12.PythonBridge
└── References: EQ12.Core

EQ12.SportsBetting.Orchestrator
├── References: EQ12.Core
├── References: EQ12.Core.ApiClient
└── References: EQ12.DatabaseManager

EQ12.Core.ApiClient
└── References: EQ12.Core
```

---

## 🎯 NEXT STEPS AFTER STRUCTURE CREATION

1. **Copy existing VB.NET files:**
   - Move `ApiCatalog.vb` to `EQ12.Core.ApiClient\`
   - Move `BettingOrchestrator.vb` to `EQ12.SportsBetting.Orchestrator\`

2. **Create stub classes for new projects:**
   - Generate empty `.vb` files for each module
   - Implement basic interfaces
   - Add XML documentation comments

3. **Configure project references:**
   - Set up inter-project dependencies
   - Test compilation with `dotnet build`

4. **Implement WPF UI:**
   - Create XAML views for each module
   - Wire up ViewModels with data binding
   - Add MaterialDesign theming

5. **Test integration:**
   - Run UI.Desktop project
   - Verify Python bridge calls
   - Test database connections
   - Validate API integrations

---

**This structure is ready to be created.** Want me to generate all `.vbproj` files + stub code?
