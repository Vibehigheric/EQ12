# EQ12 Loop Eliminator - Universal Infinite Loop Prevention System

**VB.NET Expert System for CFB Analyzer, Player Fetcher, Coral TPU, Parlay Builder**

---

## 🎯 What This Solves

Prevents infinite loops in:

- ✅ API polling loops (CFB data, odds APIs, live lines)
- ✅ Recursive functions (player validators, data processors)
- ✅ "Retry until success" patterns (scrapers, fetchers)
- ✅ Timer events (stacking, overlap, pseudo-infinite loops)
- ✅ Background tasks (Coral TPU monitoring, health checks)
- ✅ Adaptive learning loops (parlay builders, bet analyzers)

---

## 📦 What's Included

### **1. LoopGuard.vb** - Core Classes

| Class | Purpose | Use Case |
|-------|---------|----------|
| `LoopGuard` | Iteration + time limits | All While/Do/For loops |
| `HeartbeatLoopGuard` | Graceful stop control | Background tasks, TPU monitoring |
| `LoopGuardian` | Adaptive learning | Detects patterns, recommends rewrites |
| `RecursionGuard` | Recursion depth limit | Recursive validators, processors |
| `InfiniteLoopException` | Custom exception | Thrown when limits exceeded |

### **2. Examples.vb** - Real-World Patterns

- API polling with timeout
- Player validator (recursion → iteration)
- Coral TPU health monitor
- Timer event protection
- Scraper retry logic
- Parlay builder with adaptive learning
- Safe recursion with depth guard
- Complete demo program

---

## 🚀 Quick Start

### **Step 1: Add to Visual Studio Project**

1. Open your EQ12 VB.NET solution
2. Right-click solution → Add → Existing Item
3. Select `LoopGuard.vb` and `Examples.vb`
4. Build solution (Ctrl+Shift+B)

### **Step 2: Basic Usage**

```vbnet
Imports EQ12.Core.LoopProtection

' Replace:
While True
    ' dangerous code
End While

' With:
Dim guard = New LoopGuard(5000, 10, "MyLoop")
While guard.Check()
    ' protected code
End While
```

### **Step 3: Run Examples**

```vbnet
' In Module1.vb or your main entry point:
Sub Main()
    Dim examples = New EQ12.Examples.LoopGuardExamples()
    
    ' Test API polling
    examples.FetchCfbDataWithGuard().Wait()
    
    ' Test player validator
    Dim valid = examples.ValidatePlayerSafe("Player Name")
    Console.WriteLine($"Player valid: {valid}")
End Sub
```

---

## 📚 Usage Patterns

### **Pattern 1: API Polling Loop**

**Problem:** Infinite API calls when server down

```vbnet
' BEFORE (DANGEROUS):
While True
    Await FetchFromApi()
End While

' AFTER (SAFE):
Dim guard = New LoopGuard(3000, 30, "API_Polling")
While guard.TryCheck() ' Returns False instead of throwing
    Dim success = Await FetchFromApi()
    If Not success Then Exit While
    Await Task.Delay(250)
End While
```

### **Pattern 2: Recursion Fix**

**Problem:** Infinite recursion in player validator

```vbnet
' BEFORE (DANGEROUS):
Public Function ValidatePlayer(name As String) As Boolean
    If Not PlayerExists(name) Then
        Return ValidatePlayer(name) ' INFINITE!
    End If
    Return True
End Function

' AFTER (SAFE - Method 1: Iteration):
Public Function ValidatePlayerSafe(name As String) As Boolean
    Dim guard = New LoopGuard(5, 2, "PlayerValidator")
    While guard.TryCheck()
        If PlayerExists(name) Then Return True
        Thread.Sleep(200)
    End While
    Return False
End Function

' AFTER (SAFE - Method 2: Recursion Guard):
Private _recursionGuard = New RecursionGuard(10, "ValidatePlayer")

Public Function ValidatePlayerRecursive(name As String) As Boolean
    _recursionGuard.Enter()
    Try
        If PlayerExists(name) Then Return True
        Return ValidatePlayerRecursive(name) ' Safe now
    Finally
        _recursionGuard.Exit()
    End Try
End Function
```

### **Pattern 3: Background Task with Heartbeat**

**Problem:** Background Coral TPU monitor can't be stopped

```vbnet
' Create guard
Dim heartbeat = New HeartbeatLoopGuard("CoralMonitor")

' Start background task
Task.Run(Async Function()
             While heartbeat.IsRunning
                 Dim health = Await CheckCoralHealth()
                 Console.WriteLine($"Health: {health}%")
                 Await Task.Delay(1000)
             End While
         End Function)

' Stop gracefully from any thread
heartbeat.StopLoop()
```

### **Pattern 4: Timer Event Protection**

**Problem:** Timer events stack and create pseudo-infinite loop

```vbnet
Private timerGuard As Boolean = False

Private Sub Timer1_Tick(sender As Object, e As EventArgs) Handles Timer1.Tick
    If timerGuard Then Return ' Already processing
    
    timerGuard = True
    Try
        ' Heavy work here...
    Finally
        timerGuard = False
    End Try
End Sub
```

### **Pattern 5: Adaptive Learning (LoopGuardian)**

**Problem:** Parlay builder keeps getting stuck

```vbnet
' Create guardian (tracks failures across app lifetime)
Dim guardian = New LoopGuardian(adaptiveThreshold:=2)

' In your loop:
Dim guard = New LoopGuard(5000, 10, "ParlayBuilder")
Try
    While guard.Check()
        ' Build parlay...
    End While
Catch ex As InfiniteLoopException
    ' Register failure
    guardian.RegisterLoopFailure("ParlayBuilder", ex.Message, guard.CurrentIteration)
    
    ' Check if rewrite recommended
    If guardian.ShouldRewriteLoop Then
        Console.WriteLine("ADAPTIVE: Rewrite recommended - use event-driven model")
        guardian.ApplyLoopRewrite() ' Future: auto-generate fixed code
    End If
End Try
```

---

## 🛡️ The 5 Hard Rules

### **RULE 1: Every loop must include LoopGuard**

No exceptions. All `While`, `Do`, `For` with potential for indefinite runtime.

### **RULE 2: No `While True` without guard**

Replace:
```vbnet
While True
```

With:
```vbnet
Dim guard = New LoopGuard(5000, 10)
While guard.Check()
```

### **RULE 3: No recursion unless base case guaranteed**

Use `RecursionGuard` if base case could fail.

### **RULE 4: Every polling loop must auto-stop on:**

- Timeout
- Error
- Empty data
- Volatile API response

### **RULE 5: Adaptive Learning must detect loop failures**

Use `LoopGuardian` to track patterns and auto-rewrite problematic code.

---

## 🔧 Integration with Existing EQ12 Modules

### **CFB Analyzer**

```vbnet
' In CFB data fetcher:
Dim guard = New LoopGuard(2000, 60, "CFB_Fetcher")
While guard.TryCheck()
    Dim games = Await FetchCfbGames()
    If games.Count = 0 Then Exit While
    ProcessGames(games)
    Await Task.Delay(500)
End While
```

### **Player Aggregator**

```vbnet
' In player scraper:
Dim guard = New LoopGuard(10, 30, "PlayerScraper")
Dim players = New List(Of Player)()

While guard.TryCheck()
    players = Await ScrapePlayersFromSource()
    If players.Count > 0 Then Exit While
    Console.WriteLine($"Retry {guard.CurrentIteration}/10")
    Await Task.Delay(2000)
End While
```

### **Coral TPU Health Monitor**

```vbnet
' Background monitoring:
Dim heartbeat = New HeartbeatLoopGuard("CoralTPU")
_monitorTask = Task.Run(Async Function()
                            While heartbeat.IsRunning
                                Await MonitorCoralHealth()
                                Await Task.Delay(1000)
                            End While
                        End Function)

' Stop from UI or error handler:
heartbeat.StopLoop()
```

### **Parlay Builder**

```vbnet
' With adaptive learning:
Dim guardian = New LoopGuardian(2) ' Global instance
Dim guard = New LoopGuard(1000, 20, "ParlayBuilder")

Try
    While guard.Check()
        Dim leg = SelectNextLeg()
        If leg Is Nothing Then Exit While
        parlay.Add(leg)
    End While
Catch ex As InfiniteLoopException
    guardian.RegisterLoopFailure("ParlayBuilder", ex.Message, guard.CurrentIteration)
End Try
```

---

## 📊 LoopGuard Parameters Guide

| Scenario | MaxIterations | MaxSeconds | Notes |
|----------|---------------|------------|-------|
| API polling (fast) | 3000 | 30 | 10 calls/sec for 30s |
| API polling (slow) | 1000 | 60 | 16 calls/sec for 60s |
| Player scraper | 10 | 30 | Max 10 retries |
| Data validator | 100 | 5 | Quick validation |
| Background monitor | 86400 | 86400 | 1 day runtime |
| Parlay builder | 1000 | 20 | Max 1000 legs |
| Recursion | 50 | 5 | Shallow recursion |

---

## 🧪 Testing

### **Test 1: Basic Guard**

```vbnet
Dim guard = New LoopGuard(100, 5, "Test")
Dim counter = 0
While guard.TryCheck()
    counter += 1
End While
Console.WriteLine($"Completed {counter} iterations") ' Should be 100
```

### **Test 2: Time Limit**

```vbnet
Dim guard = New LoopGuard(999999, 2, "TimeTest") ' 2 second limit
Dim counter = 0
While guard.TryCheck()
    counter += 1
    Thread.Sleep(100) ' Slow iterations
End While
Console.WriteLine($"Stopped at {counter} iterations (time limit reached)")
```

### **Test 3: Exception Handling**

```vbnet
Dim guard = New LoopGuard(10, 5, "ExceptionTest")
Try
    While guard.Check() ' Will throw after 10 iterations
        ' Work...
    End While
Catch ex As InfiniteLoopException
    Console.WriteLine($"Caught: {ex.Message}")
End Try
```

---

## 🎯 Advanced Features

### **1. Soft Check vs Hard Check**

```vbnet
' Soft (returns False, no exception):
While guard.TryCheck()
    ' ...
End While

' Hard (throws exception):
While guard.Check()
    ' ...
End While
```

### **2. Loop Statistics**

```vbnet
Console.WriteLine(guard.GetStats())
' Output: [MyLoop] Iterations: 234/5000, Elapsed: 3.45s/10s
```

### **3. Guard Reset (Use Carefully)**

```vbnet
' Only use if loop SHOULD run multiple times
guard.Reset()
```

### **4. Adaptive Rewrite (Future)**

```vbnet
' When LoopGuardian.ShouldRewriteLoop = True:
guardian.ApplyLoopRewrite()
' Future: Calls EQ12 Copilot/Codex to generate event-driven replacement
```

---

## 🔗 Integration with EQ12 Ecosystem

### **PowerShell Wrapper**

```powershell
# Call VB.NET loop guard from PowerShell:
$vb = Add-Type -Path "LoopGuard.vb" -PassThru
$guard = New-Object EQ12.Core.LoopProtection.LoopGuard(1000, 30, "PS_Loop")

while ($guard.TryCheck()) {
    # PowerShell work...
}

Write-Host $guard.GetStats()
```

### **Telegram Bot Integration**

```vbnet
' Send alert when loop guard triggers:
Catch ex As InfiniteLoopException
    Await SendTelegramAlert($"Loop guard triggered: {ex.Message}")
End Try
```

### **EQ12 Dashboard**

```vbnet
' Export guardian report to JSON:
Dim report = guardian.GetFailureReport()
File.WriteAllText("C:\EQ12\logs\loop_failures.json", JsonConvert.SerializeObject(guardian))
```

### **Raspberry Pi Deployment**

```bash
# Run on Pi with Mono:
mono EQ12LoopEliminator.exe
```

---

## 📝 Customization Examples

### **Custom Loop Guard for Specific API**

```vbnet
Public Class OddsApiGuard
    Inherits LoopGuard
    
    Public Sub New()
        MyBase.New(500, 60, "OddsAPI") ' 500 calls max, 60s timeout
    End Sub
    
    Public Function CheckWithRateLimit() As Boolean
        If Not MyBase.TryCheck() Then Return False
        
        ' Custom: Enforce 10 calls/sec rate limit
        If CurrentIteration Mod 10 = 0 Then
            Thread.Sleep(1000)
        End If
        
        Return True
    End Function
End Class
```

---

## 🚨 Troubleshooting

### **Problem: Guard triggers too early**

**Solution:** Increase limits
```vbnet
' Before:
New LoopGuard(100, 5) ' Too restrictive

' After:
New LoopGuard(5000, 60) ' More permissive
```

### **Problem: Guard doesn't trigger**

**Solution:** Ensure `Check()` or `TryCheck()` called in loop
```vbnet
' WRONG:
While True
    guard.Check() ' Never reached if loop condition is True
End While

' RIGHT:
While guard.Check() ' Guard IS the loop condition
    ' ...
End While
```

### **Problem: RecursionGuard depth exceeded**

**Solution:** Increase max depth or rewrite as iteration
```vbnet
' Quick fix:
New RecursionGuard(100, "MyFunc") ' Was 10, now 100

' Better fix: Convert to loop (see Examples.vb)
```

---

## 🎓 Next Steps

1. **Copy `LoopGuard.vb` and `Examples.vb` to your project**
2. **Build and test with examples**
3. **Apply to your existing loops** (start with API polling)
4. **Set up LoopGuardian** for adaptive learning
5. **Monitor loop failures** via EQ12 dashboard
6. **Let adaptive system recommend rewrites**

---

## 📚 Related EQ12 Documentation

- `EQ12_FORMATTING_STANDARD.ps1` - PowerShell loop guards
- `BettingSlipAnalyzer.vb` - Risk scoring (uses loop guards internally)
- `AGENTS.md` - Adaptive learning system integration
- `COPILOT_PROMPT.md` - AI-assisted loop rewriting

---

## 📧 Support

For issues or questions:
- Check `Examples.vb` for patterns
- Review EQ12 dashboard logs: `C:\EQ12\logs\loop_failures.json`
- Enable verbose logging: `Console.WriteLine(guard.GetStats())`

---

**Built for EQ12 by VB.NET Expert System | 2025-11-27**
