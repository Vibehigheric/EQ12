# VB.NET Code Reference Index

**Purpose:** Quick reference to existing EQ12 VB.NET code patterns  
**Last Updated:** 2025-01-29  
**Total VB.NET Files:** 170+  
**Total Projects:** 8 Visual Studio solutions

---

## Why This Reference Instead of a Starter Kit?

The EQ12 system already has **8 production-grade VB.NET solutions** with 170+ files. These are **real-world, tested examples** that are superior to generic templates. This reference maps common development tasks to existing code you can copy and adapt.

---

## Quick Task → File Mapping

### API & HTTP Operations

**Need to call HTTP APIs?**
- **File:** `visual_studio_projects\EQ12SportsBettingOrchestrator\EQ12.Core.ApiClient\OddsApiClient.vb`
- **Features:**
  - `System.Net.Http.HttpClient` usage
  - Async/await patterns (`Task(Of T)`)
  - JSON deserialization with `System.Text.Json`
  - Error handling and retry logic
  - API key authentication

**Example Pattern:**
```vb
Imports System.Net.Http
Imports System.Text.Json
Imports System.Threading.Tasks

Public Class OddsApiClient
    Private ReadOnly _httpClient As HttpClient
    Private ReadOnly _apiKey As String

    Public Async Function GetDataAsync() As Task(Of MyData)
        Dim response = Await _httpClient.GetAsync($"https://api.example.com/endpoint?apiKey={_apiKey}")
        response.EnsureSuccessStatusCode()
        Dim json = Await response.Content.ReadAsStringAsync()
        Return JsonSerializer.Deserialize(Of MyData)(json)
    End Function
End Class
```

**Other API Examples:**
- `HuggingFaceClient.vb` - AI model API calls
- `WeatherApiClient.vb` - RESTful API consumption

---

### Database Operations (SQLite)

**Need to access SQLite databases?**
- **File:** `visual_studio_projects\EQ12ControlCenter\MainWindow.vb`
- **Features:**
  - `System.Data.SQLite` ADO.NET usage
  - Connection management
  - Parameterized queries (SQL injection prevention)
  - Transaction handling
  - Data binding to UI controls

**Example Pattern:**
```vb
Imports System.Data.SQLite

Public Sub SaveToDatabase(name As String, value As Decimal)
    Using conn As New SQLiteConnection("Data Source=C:\EQ12\data\mydb.db")
        conn.Open()
        Using cmd As New SQLiteCommand("INSERT INTO table (name, value) VALUES (@name, @value)", conn)
            cmd.Parameters.AddWithValue("@name", name)
            cmd.Parameters.AddWithValue("@value", value)
            cmd.ExecuteNonQuery()
        End Using
    End Using
End Sub
```

**Other Database Examples:**
- `visual_studio_projects\EQ12.SportsBetting.Orchestrator\BettingOrchestrator.vb`
- `src\props\OddsIngestor.vb`

---

### JSON Parsing & Serialization

**Need to parse JSON data?**
- **File:** `visual_studio_projects\EQ12SportsBettingOrchestrator\EQ12.Core.ApiClient\HuggingFaceClient.vb`
- **Features:**
  - `System.Text.Json.JsonSerializer`
  - Custom object deserialization
  - Property mapping

**Example Pattern:**
```vb
Imports System.Text.Json

Public Class MyData
    Public Property Name As String
    Public Property Value As Integer
End Class

' Deserialize JSON string to object
Dim jsonString = "{""name"":""test"",""value"":42}"
Dim data = JsonSerializer.Deserialize(Of MyData)(jsonString)

' Serialize object to JSON string
Dim obj As New MyData With {.Name = "test", .Value = 42}
Dim json = JsonSerializer.Serialize(obj)
```

---

### Infinite Loop Protection

**Need to prevent runaway loops?**
- **File:** `vb_loop_eliminator\LoopGuard.vb`
- **Features:**
  - Iteration counting with automatic termination
  - Heartbeat-based detection
  - Recursion depth tracking
  - Global loop guardian for multi-loop monitoring

**Example Pattern:**
```vb
' Create a loop guard that allows max 1000 iterations
Dim guard As New LoopGuard(maxIterations:=1000, "MyLoop")

While condition
    guard.Check() ' Throws InfiniteLoopException if max exceeded
    ' Your loop logic here
End While
```

**Full Implementation:**
- `LoopGuard` class - basic iteration counter
- `HeartbeatLoopGuard` class - time-based detection
- `RecursionGuard` class - recursive call depth tracking
- `LoopGuardian` class - multi-loop monitoring

---

### Web Scraping & Data Extraction

**Need to scrape web pages?**
- **File:** `visual_studio_projects\EQ12ControlCenter\PacerScraperModule.vb`
- **Features:**
  - HTTP GET/POST requests
  - HTML parsing
  - Cookie/session management
  - Rate limiting
  - Error handling for network failures

**Example Pattern:**
```vb
Imports System.Net.Http
Imports System.Text.RegularExpressions

Public Class WebScraper
    Private ReadOnly _httpClient As HttpClient

    Public Async Function FetchPageAsync(url As String) As Task(Of String)
        Dim response = Await _httpClient.GetAsync(url)
        Return Await response.Content.ReadAsStringAsync()
    End Function

    Public Function ExtractData(html As String) As List(Of String)
        Dim regex As New Regex("<div class=""data"">(.*?)</div>")
        Dim matches = regex.Matches(html)
        Return matches.Cast(Of Match)().Select(Function(m) m.Groups(1).Value).ToList()
    End Function
End Class
```

---

### Docker Container Management

**Need to manage Docker containers?**
- **File:** `vbnet_projects\EQ12.DockerManager\DockerManager.vb`
- **Features:**
  - Docker CLI wrapper
  - Container start/stop/remove
  - Process execution and output capture
  - Error handling

**Example Pattern:**
```vb
Imports System.Diagnostics

Public Sub StartDockerContainer(containerName As String)
    Dim psi As New ProcessStartInfo With {
        .FileName = "docker",
        .Arguments = $"start {containerName}",
        .RedirectStandardOutput = True,
        .RedirectStandardError = True,
        .UseShellExecute = False,
        .CreateNoWindow = True
    }

    Using process = Process.Start(psi)
        process.WaitForExit()
        If process.ExitCode <> 0 Then
            Dim errorOutput = process.StandardError.ReadToEnd()
            Throw New Exception($"Docker start failed: {errorOutput}")
        End If
    End Using
End Sub
```

---

### File System Scanning & Analysis

**Need to scan directories and analyze files?**
- **File:** `visual_studio_projects\EQ12SportsBettingOrchestrator\EQ12.Core.FileScanner\Eq12Scanner.vb`
- **Features:**
  - Recursive directory traversal
  - File filtering (by extension, size, date)
  - JSON manifest generation
  - Pattern matching
  - Safe handling of access-denied errors

**Example Pattern:**
```vb
Imports System.IO

Public Function ScanDirectory(rootPath As String) As List(Of FileInfo)
    Dim results As New List(Of FileInfo)
    
    Try
        For Each file In Directory.EnumerateFiles(rootPath, "*.*", SearchOption.AllDirectories)
            Dim info As New FileInfo(file)
            If info.Extension = ".txt" AndAlso info.Length > 0 Then
                results.Add(info)
            End If
        Next
    Catch ex As UnauthorizedAccessException
        ' Log and continue - common for system directories
    End Try
    
    Return results
End Function
```

---

### Windows Forms UI Components

**Need to create WinForms GUIs?**
- **File:** `visual_studio_projects\EQ12ControlCenter\MainWindow.vb`
- **Features:**
  - Event-driven programming
  - DataGridView data binding
  - Timer components for periodic updates
  - Button click handlers
  - TextBox validation

**Example Pattern:**
```vb
Public Class MainWindow
    Private Sub btnSubmit_Click(sender As Object, e As EventArgs) Handles btnSubmit.Click
        If String.IsNullOrWhiteSpace(txtName.Text) Then
            MessageBox.Show("Please enter a name", "Validation Error", MessageBoxButtons.OK, MessageBoxIcon.Warning)
            Return
        End If
        
        ' Process data
        ProcessInput(txtName.Text)
    End Sub
    
    Private Sub LoadDataGrid()
        ' Bind data to DataGridView
        Dim data = GetDataFromDatabase()
        dgvResults.DataSource = data
    End Sub
End Class
```

---

### Background Task Orchestration

**Need to run Python scripts from VB.NET?**
- **File:** `visual_studio_projects\EQ12SportsBettingOrchestrator\EQ12.Core.Orchestrator\ScriptOrchestrator.vb`
- **Features:**
  - Process execution (Python, PowerShell, etc.)
  - Output capture (stdout/stderr)
  - Async execution
  - Exit code handling
  - Timeout management

**Example Pattern:**
```vb
Imports System.Diagnostics

Public Function RunPythonScript(scriptPath As String, args As String) As String
    Dim psi As New ProcessStartInfo With {
        .FileName = "python",
        .Arguments = $"""{scriptPath}"" {args}",
        .RedirectStandardOutput = True,
        .RedirectStandardError = True,
        .UseShellExecute = False,
        .CreateNoWindow = True
    }

    Using process = Process.Start(psi)
        Dim output = process.StandardOutput.ReadToEnd()
        Dim errors = process.StandardError.ReadToEnd()
        process.WaitForExit()
        
        If process.ExitCode <> 0 Then
            Throw New Exception($"Script failed: {errors}")
        End If
        
        Return output
    End Using
End Function
```

---

### USB Device Detection

**Need to detect USB drives or devices?**
- **File:** `vb_usb_scanner\UsbDeviceScanner.vb`
- **Features:**
  - `System.Management` WMI queries
  - USB device enumeration
  - Device property extraction (VID, PID, serial number)
  - Drive letter mapping

**Example Pattern:**
```vb
Imports System.Management

Public Function GetUsbDrives() As List(Of DriveInfo)
    Dim usbDrives As New List(Of DriveInfo)
    
    Dim searcher As New ManagementObjectSearcher("SELECT * FROM Win32_DiskDrive WHERE InterfaceType='USB'")
    For Each drive As ManagementObject In searcher.Get()
        Dim deviceId = drive("DeviceID").ToString()
        ' Map to drive letters
        Dim partitions As New ManagementObjectSearcher($"ASSOCIATORS OF {{Win32_DiskDrive.DeviceID='{deviceId}'}} WHERE AssocClass = Win32_DiskDriveToDiskPartition")
        For Each partition As ManagementObject In partitions.Get()
            Dim logical As New ManagementObjectSearcher($"ASSOCIATORS OF {{Win32_DiskPartition.DeviceID='{partition("DeviceID")}'}} WHERE AssocClass = Win32_LogicalDiskToPartition")
            For Each disk As ManagementObject In logical.Get()
                Dim driveLetter = disk("Name").ToString()
                usbDrives.Add(New DriveInfo(driveLetter))
            Next
        Next
    Next
    
    Return usbDrives
End Function
```

---

### Logging & Error Handling

**Need structured logging?**
- **File:** `vb_fetch_engine\LogInspector.vb`
- **Features:**
  - Console output with timestamps
  - File-based logging
  - Log parsing and analysis
  - Error categorization

**Example Pattern:**
```vb
Imports System.IO

Public Sub LogInfo(message As String)
    Dim timestamp = DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss")
    Dim logMessage = $"[{timestamp}] INFO: {message}"
    
    Console.WriteLine(logMessage)
    File.AppendAllText("C:\EQ12\logs\app.log", logMessage & Environment.NewLine)
End Sub

Public Sub LogError(ex As Exception)
    Dim timestamp = DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss")
    Dim logMessage = $"[{timestamp}] ERROR: {ex.Message}{Environment.NewLine}{ex.StackTrace}"
    
    Console.ForegroundColor = ConsoleColor.Red
    Console.WriteLine(logMessage)
    Console.ResetColor()
    
    File.AppendAllText("C:\EQ12\logs\errors.log", logMessage & Environment.NewLine)
End Sub
```

---

### Betting/Gaming Analysis

**Need to calculate odds, parlays, or probabilities?**
- **File:** `vb_betting_analyzer\BettingSlipAnalyzer.vb`
- **Features:**
  - Parlay odds calculation
  - Expected value (EV) computation
  - Kelly Criterion betting
  - Multi-leg bet validation

**Example Pattern:**
```vb
Public Class BetLeg
    Public Property Team As String
    Public Property Odds As Decimal ' American odds (-110, +150, etc.)
    Public Property Stake As Decimal
    
    Public Function ToDecimalOdds() As Decimal
        If Odds > 0 Then
            Return (Odds / 100) + 1
        Else
            Return (100 / Math.Abs(Odds)) + 1
        End If
    End Function
End Class

Public Function CalculateParlayPayout(legs As List(Of BetLeg), stake As Decimal) As Decimal
    Dim totalOdds As Decimal = 1
    For Each leg In legs
        totalOdds *= leg.ToDecimalOdds()
    Next
    Return stake * totalOdds
End Function
```

**Other Betting Files:**
- `src\props\ParlayBuilder.vb` - Advanced parlay construction
- `src\props\KellyCalculator.vb` - Kelly Criterion implementation
- `src\props\PricingUtils.vb` - Odds pricing utilities

---

## Project Templates by Use Case

### 1. Console Application (Data Processing)

**Best Example:** `vb_loop_eliminator\Examples.vb`

**Features:**
- `Module Program` with `Sub Main()`
- Command-line argument parsing
- Console output formatting
- Error handling

**Use For:**
- Batch processing scripts
- Data migration tools
- Scheduled tasks
- Utilities

---

### 2. Windows Forms Application (GUI)

**Best Example:** `visual_studio_projects\EQ12ControlCenter\MainWindow.vb`

**Features:**
- WinForms UI (buttons, text boxes, data grids)
- Event handlers
- Data binding
- Timer-based updates

**Use For:**
- Desktop dashboards
- System monitoring GUIs
- Admin panels
- Control centers

---

### 3. Class Library (Reusable Components)

**Best Example:** `visual_studio_projects\EQ12SportsBettingOrchestrator\EQ12.Core.ApiClient\`

**Features:**
- Modular classes
- Public interfaces
- Dependency injection patterns
- XML documentation comments

**Use For:**
- Shared utilities
- API client libraries
- Data models
- Business logic layers

---

### 4. Background Service (Long-Running Tasks)

**Best Example:** `visual_studio_projects\EQ12_System_Health_Monitor\EQ12_System_Health_Monitor.vb`

**Features:**
- Infinite loops with sleep intervals
- Resource monitoring
- File watching
- Graceful shutdown handling

**Use For:**
- System monitors
- File watchers
- Log processors
- Health checkers

---

## VB.NET Project Creation Commands

### New Console App
```powershell
dotnet new console -lang VB -n MyConsoleApp
cd MyConsoleApp
dotnet build
dotnet run
```

### New Class Library
```powershell
dotnet new classlib -lang VB -n MyLibrary
cd MyLibrary
dotnet build
```

### Reference an Existing Project
```powershell
dotnet add reference ..\MyLibrary\MyLibrary.vbproj
```

---

## Common VB.NET Patterns (Cheat Sheet)

### Import Common Namespaces
```vb
Imports System
Imports System.IO
Imports System.Collections.Generic
Imports System.Linq
Imports System.Threading.Tasks
Imports System.Net.Http
Imports System.Text.Json
```

### Define a Class with Properties
```vb
Public Class Product
    Public Property Id As Integer
    Public Property Name As String
    Public Property Price As Decimal
    
    Public Sub New(id As Integer, name As String, price As Decimal)
        Me.Id = id
        Me.Name = name
        Me.Price = price
    End Sub
End Class
```

### LINQ Queries
```vb
Dim products As New List(Of Product)
Dim expensive = products.Where(Function(p) p.Price > 100).OrderBy(Function(p) p.Name).ToList()
```

### Async/Await
```vb
Public Async Function FetchDataAsync() As Task(Of String)
    Using client As New HttpClient()
        Return Await client.GetStringAsync("https://api.example.com/data")
    End Using
End Function
```

### Error Handling
```vb
Try
    ' Risky operation
    Dim result = DoSomething()
Catch ex As IOException
    Console.WriteLine($"File error: {ex.Message}")
Catch ex As Exception
    Console.WriteLine($"Unexpected error: {ex.Message}")
Finally
    ' Cleanup code
End Try
```

---

## VS Code Tasks for VB.NET

**Existing tasks (from `.vscode/tasks.json`):**

### Build VB.NET Project
```json
{
  "label": "build",
  "command": "dotnet",
  "type": "process",
  "args": ["build", "${workspaceFolder}/MyProject.vbproj"],
  "problemMatcher": "$msCompile"
}
```

### Run VB.NET Project
```json
{
  "label": "run",
  "command": "dotnet",
  "type": "process",
  "args": ["run", "--project", "${workspaceFolder}/MyProject.vbproj"]
}
```

---

## Testing VB.NET Code

### Unit Testing Framework

**Not in current codebase, but recommended:**
```powershell
# Install xUnit for VB.NET
dotnet new xunit -lang VB -n MyTests
cd MyTests
dotnet add reference ..\MyProject\MyProject.vbproj
```

**Example Test:**
```vb
Imports Xunit

Public Class ProductTests
    <Fact>
    Public Sub TestPriceCalculation()
        Dim product As New Product(1, "Widget", 99.99D)
        Assert.Equal(99.99D, product.Price)
    End Sub
End Class
```

---

## Additional Resources

### EQ12-Specific Documentation
- `COPILOT_PROMPT.md` - Copilot instructions for EQ12 project
- `AGENTS.md` - Agent onboarding and coding standards
- `README.md` files in individual projects

### Microsoft Documentation
- [VB.NET Language Reference](https://learn.microsoft.com/en-us/dotnet/visual-basic/)
- [.NET API Browser](https://learn.microsoft.com/en-us/dotnet/api/)
- [Visual Studio Code VB.NET](https://code.visualstudio.com/docs/languages/dotnet)

---

## Quick Decision Tree: Which File to Reference?

```
Start Here
├─ Need HTTP API calls? → OddsApiClient.vb
├─ Need database access? → MainWindow.vb (SQLite examples)
├─ Need web scraping? → PacerScraperModule.vb
├─ Need loop protection? → LoopGuard.vb
├─ Need Docker control? → DockerManager.vb
├─ Need file scanning? → Eq12Scanner.vb
├─ Need USB detection? → UsbDeviceScanner.vb
├─ Need betting calculations? → BettingSlipAnalyzer.vb
├─ Need background tasks? → ScriptOrchestrator.vb
└─ Need UI controls? → MainWindow.vb (WinForms)
```

---

**Last Updated:** 2025-01-29  
**Maintained By:** EQ12 System (GitHub Copilot + Autonomous Agents)  
**Version:** 1.0
