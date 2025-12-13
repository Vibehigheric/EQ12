# Quick Start Guide - EQ12 Loop Eliminator

**Get infinite loop protection working in 3 minutes**

---

## Step 1: Create Visual Studio Project

### Option A: New Console Application

1. Open Visual Studio 2022
2. File → New → Project
3. Select **"Console App (.NET Framework)"** or **"Console App (.NET 6.0+)"**
4. Name: `EQ12LoopEliminator`
5. Click Create

### Option B: Add to Existing EQ12 Solution

1. Open your existing EQ12 solution
2. Right-click solution → Add → New Project
3. Select **"Class Library (.NET Framework)"**
4. Name: `EQ12.LoopProtection`
5. Click Create

---

## Step 2: Add the Code

### Method 1: Add Existing Files

1. Right-click project → Add → Existing Item
2. Navigate to `c:\EQ12_BROKEN_20251122_210342\vb_loop_eliminator\`
3. Select **LoopGuard.vb** and **Examples.vb**
4. Click Add

### Method 2: Copy/Paste

1. Right-click project → Add → Class
2. Name: `LoopGuard.vb`
3. Replace all code with contents of `LoopGuard.vb`
4. Repeat for `Examples.vb`

---

## Step 3: Test It

### Quick Test Program

Add this to your `Module1.vb` or `Program.vb`:

```vbnet
Imports EQ12.Core.LoopProtection

Module Program
    Sub Main()
        Console.WriteLine("=== Testing Loop Guard ===")
        
        ' Test 1: Basic iteration limit
        Dim guard = New LoopGuard(100, 10, "BasicTest")
        Dim counter = 0
        
        While guard.TryCheck()
            counter += 1
        End While
        
        Console.WriteLine($"Test 1: {counter} iterations (expected 100)")
        Console.WriteLine(guard.GetStats())
        Console.WriteLine()
        
        ' Test 2: Time limit
        Dim timeGuard = New LoopGuard(999999, 2, "TimeTest")
        Dim timeCounter = 0
        
        While timeGuard.TryCheck()
            timeCounter += 1
            System.Threading.Thread.Sleep(10)
        End While
        
        Console.WriteLine($"Test 2: {timeCounter} iterations (stopped by time)")
        Console.WriteLine(timeGuard.GetStats())
        Console.WriteLine()
        
        Console.WriteLine("=== All Tests Passed ===")
        Console.WriteLine("Press any key to exit...")
        Console.ReadKey()
    End Sub
End Module
```

### Run It

1. Press **F5** or click **Start**
2. You should see:

```
=== Testing Loop Guard ===
Test 1: 100 iterations (expected 100)
[BasicTest] Iterations: 100/100, Elapsed: 0.01s/10s

Test 2: 200 iterations (stopped by time)
[TimeTest] Iterations: 200/999999, Elapsed: 2.01s/2s

=== All Tests Passed ===
Press any key to exit...
```

---

## Step 4: Use in Your Code

### Replace Dangerous Loop

**BEFORE:**
```vbnet
While True
    Dim data = Await FetchData()
    ProcessData(data)
End While
```

**AFTER:**
```vbnet
Dim guard = New LoopGuard(5000, 60, "DataFetcher")

While guard.TryCheck()
    Dim data = Await FetchData()
    If data Is Nothing Then Exit While
    ProcessData(data)
    Await Task.Delay(100)
End While
```

### Common Patterns

#### API Polling
```vbnet
Dim guard = New LoopGuard(3000, 30, "API_Poll")
While guard.TryCheck()
    Dim response = Await CallApi()
    If Not response.Success Then Exit While
    Await Task.Delay(250)
End While
```

#### Scraper Retry
```vbnet
Dim guard = New LoopGuard(10, 20, "Scraper")
While guard.TryCheck()
    Dim data = ScrapeWebsite()
    If data.Count > 0 Then Exit While
    Thread.Sleep(2000)
End While
```

#### Background Task
```vbnet
Dim heartbeat = New HeartbeatLoopGuard("Monitor")

Task.Run(Sub()
             While heartbeat.IsRunning
                 DoMonitoring()
                 Thread.Sleep(1000)
             End While
         End Sub)

' Stop from anywhere:
heartbeat.StopLoop()
```

---

## Expected Output Examples

### Successful Loop Completion
```
[MyLoop] Iterations: 347/5000, Elapsed: 4.52s/60s
Loop completed successfully
```

### Iteration Limit Hit
```
InfiniteLoopException: LoopGuard [DataProcessor]: Max iterations exceeded (5000/5000)
```

### Time Limit Hit
```
InfiniteLoopException: LoopGuard [APIPoller]: Time limit exceeded (60.12s/60s after 2341 iterations)
```

### Soft Check (No Exception)
```vbnet
' Using TryCheck() returns False instead of throwing
While guard.TryCheck() ' Returns False when limit hit
    ' ...
End While
' No exception - graceful exit
```

---

## Score Interpretation

### Loop Health Indicators

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Iterations/sec | < 100 | 100-500 | > 500 |
| Total iterations | < 1000 | 1000-5000 | > 5000 |
| Runtime | < 10s | 10-60s | > 60s |
| Exit reason | Data empty | Time limit | Max iterations |

### When to Increase Limits

**Scenario:** Guard triggers too early
```vbnet
' If you see: "Max iterations exceeded (1000/1000)"
' But loop should run longer...

' Increase limits:
New LoopGuard(10000, 120, "LongRunner") ' Was (1000, 60)
```

### When to Decrease Limits

**Scenario:** Loop runs too long before guard triggers
```vbnet
' If infinite loop takes 5 minutes to detect...

' Decrease limits:
New LoopGuard(500, 10, "QuickFail") ' Was (5000, 300)
```

---

## Troubleshooting

### Problem: "Type 'LoopGuard' is not defined"

**Solution:** Add import at top of file:
```vbnet
Imports EQ12.Core.LoopProtection
```

### Problem: "Namespace 'EQ12' is not defined"

**Solution:** Check namespace in LoopGuard.vb matches:
```vbnet
Namespace EQ12.Core.LoopProtection
    ' ... your classes
End Namespace
```

### Problem: Guard never triggers

**Solution:** Make sure Check() is in loop condition:
```vbnet
' WRONG:
While True
    guard.Check() ' Too late!
End While

' RIGHT:
While guard.Check() ' Guard controls loop
    ' ...
End While
```

### Problem: "Object reference not set" error

**Solution:** Create guard before loop:
```vbnet
' WRONG:
Dim guard As LoopGuard ' Not initialized!
While guard.Check() ' CRASH!

' RIGHT:
Dim guard = New LoopGuard(1000, 30)
While guard.Check() ' Works
```

---

## Next Steps

1. ✅ **Test basic loop guard** (you just did this!)
2. 📝 **Apply to one real loop** in your code
3. 🔍 **Monitor the results** - check console output
4. 🎯 **Tune the limits** based on actual behavior
5. 🚀 **Roll out to all loops** systematically
6. 📊 **Set up LoopGuardian** for adaptive learning

---

## Advanced Usage

### Recursion Protection

```vbnet
Private _recursionGuard As New RecursionGuard(20, "MyFunction")

Public Function RecursiveProcess(data As String) As String
    _recursionGuard.Enter()
    Try
        ' Recursive logic...
        If condition Then
            Return RecursiveProcess(newData)
        End If
        Return result
    Finally
        _recursionGuard.Exit()
    End Try
End Function
```

### Adaptive Learning

```vbnet
' Create guardian (persists across loops)
Dim guardian = New LoopGuardian(adaptiveThreshold:=2)

' In each loop:
Try
    Dim guard = New LoopGuard(1000, 30, "LoopName")
    While guard.Check()
        ' ...
    End While
Catch ex As InfiniteLoopException
    guardian.RegisterLoopFailure("LoopName", ex.Message, guard.CurrentIteration)
    
    If guardian.ShouldRewriteLoop Then
        Console.WriteLine("Adaptive system recommends code rewrite")
    End If
End Try
```

---

## Integration Examples

### With EQ12 CFB Analyzer

```vbnet
Public Async Function FetchCfbGames() As Task(Of List(Of Game))
    Dim guard = New LoopGuard(2000, 60, "CFB_Fetcher")
    Dim games = New List(Of Game)()
    
    While guard.TryCheck()
        games = Await ApiClient.GetGames()
        If games.Count > 0 Then Exit While
        
        Console.WriteLine($"No games - retry {guard.CurrentIteration}")
        Await Task.Delay(1000)
    End While
    
    Return games
End Function
```

### With Player Scraper

```vbnet
Public Function ScrapePlayersWithGuard() As List(Of Player)
    Dim guard = New LoopGuard(10, 30, "PlayerScraper")
    
    While guard.TryCheck()
        Dim players = ScrapeWebsite()
        If players.Count > 0 Then
            Return players
        End If
        Thread.Sleep(2000)
    End While
    
    Return New List(Of Player)() ' Empty if all retries failed
End Function
```

### With Coral TPU Monitor

```vbnet
Dim heartbeat = New HeartbeatLoopGuard("CoralMonitor")

' Background task
Task.Run(Sub()
             While heartbeat.IsRunning
                 Dim health = CheckCoralHealth()
                 Console.WriteLine($"TPU Health: {health}%")
                 Thread.Sleep(1000)
             End While
         End Sub)

' Stop from button click or error
Private Sub StopButton_Click(sender As Object, e As EventArgs)
    heartbeat.StopLoop()
End Sub
```

---

## Reference

### Constructor Parameters

```vbnet
New LoopGuard(maxIterations, maxSeconds, guardName)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| maxIterations | Integer | 5000 | Max loop iterations |
| maxSeconds | Integer | 10 | Max runtime in seconds |
| guardName | String | "UnnamedGuard" | Name for logging |

### Common Limits by Scenario

| Scenario | maxIterations | maxSeconds |
|----------|---------------|------------|
| Fast API (< 100ms) | 3000 | 30 |
| Slow API (> 500ms) | 1000 | 60 |
| Scraper with retries | 10 | 30 |
| Data validation | 100 | 5 |
| Background monitor | 86400 | 86400 |
| Recursion depth | 50 | 5 |

---

**You're ready to eliminate infinite loops!**

For more examples, see `Examples.vb` and `README.md`.
