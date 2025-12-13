# EQ12 Hard-Coded Loop Protection Rules

**Permanent rules for all EQ12 VB.NET development**

These rules are **MANDATORY** for all code in:
- CFB Analyzer
- Player Fetcher
- Coral TPU Health Monitor
- Parlay Builder
- Betting Slip Analyzer
- All adaptive Copilot logic modules

---

## 🚨 THE 5 MANDATORY RULES

### **RULE 1: Every loop must include LoopGuard()**

**No exceptions. All `While`, `Do`, `For` with potential for indefinite runtime.**

✅ **COMPLIANT:**
```vbnet
Dim guard = New LoopGuard(5000, 60, "MyLoop")
While guard.Check()
    ' Safe code
End While
```

❌ **VIOLATION:**
```vbnet
While True
    ' Dangerous code - NO GUARD!
End While
```

---

### **RULE 2: No `While True` without guard**

**All infinite loop conditions must be replaced with guard checks.**

✅ **COMPLIANT:**
```vbnet
Dim guard = New LoopGuard(3000, 30, "APIPoller")
While guard.TryCheck()
    Await FetchData()
End While
```

❌ **VIOLATION:**
```vbnet
While True
    Await FetchData()
End While
```

**Exception:** Heartbeat guards are allowed:
```vbnet
Dim heartbeat = New HeartbeatLoopGuard()
While heartbeat.IsRunning
    ' This is safe - can be stopped externally
End While
```

---

### **RULE 3: No recursion unless base case guaranteed**

**All recursive functions must either:**
1. Have mathematically guaranteed base case, OR
2. Use RecursionGuard

✅ **COMPLIANT (Guaranteed Base Case):**
```vbnet
Public Function Factorial(n As Integer) As Integer
    If n <= 1 Then Return 1 ' Guaranteed to hit
    Return n * Factorial(n - 1)
End Function
```

✅ **COMPLIANT (RecursionGuard):**
```vbnet
Private _guard = New RecursionGuard(20, "DataProcessor")

Public Function ProcessRecursive(data As String) As String
    _guard.Enter()
    Try
        If String.IsNullOrEmpty(data) Then Return ""
        Return ProcessRecursive(Transform(data))
    Finally
        _guard.Exit()
    End Try
End Function
```

❌ **VIOLATION:**
```vbnet
Public Function ValidatePlayer(name As String) As Boolean
    If Not PlayerExists(name) Then
        Return ValidatePlayer(name) ' NO GUARANTEED BASE CASE!
    End If
    Return True
End Function
```

---

### **RULE 4: Every polling loop must auto-stop on:**

**Required exit conditions:**
1. Timeout (time limit)
2. Error (exception or failure)
3. Empty data (null/empty response)
4. Volatile API response (error codes, rate limits)

✅ **COMPLIANT:**
```vbnet
Dim guard = New LoopGuard(2000, 45, "APIPoller")

While guard.TryCheck()
    Try
        Dim response = Await CallApi()
        
        ' Exit on empty data
        If response Is Nothing Then Exit While
        
        ' Exit on error status
        If response.StatusCode <> 200 Then Exit While
        
        ' Exit on empty result
        If response.Data.Count = 0 Then Exit While
        
        ProcessData(response.Data)
        Await Task.Delay(250)
        
    Catch ex As Exception
        ' Exit on error
        Console.WriteLine($"API error: {ex.Message}")
        Exit While
    End Try
End While
```

❌ **VIOLATION:**
```vbnet
While guard.Check()
    Dim response = Await CallApi()
    ProcessData(response) ' No exit conditions!
End While
```

---

### **RULE 5: Adaptive Learning must detect loop failures**

**All production loops must register failures with LoopGuardian.**

This enables:
- Pattern detection
- Automatic rewrite recommendations
- EQ12 dashboard monitoring
- Copilot-assisted fixes

✅ **COMPLIANT:**
```vbnet
' Create guardian (global/module-level)
Private Shared _guardian As New LoopGuardian(adaptiveThreshold:=2)

Public Function BuildParlay() As List(Of Leg)
    Dim guard = New LoopGuard(1000, 30, "ParlayBuilder")
    
    Try
        While guard.Check()
            ' Build parlay logic...
        End While
    Catch ex As InfiniteLoopException
        ' Register failure for adaptive learning
        _guardian.RegisterLoopFailure(
            "ParlayBuilder",
            ex.Message,
            guard.CurrentIteration)
        
        ' Check if rewrite recommended
        If _guardian.ShouldRewriteLoop Then
            LogToEQ12Dashboard("Parlay builder needs rewrite - event-driven recommended")
            _guardian.ApplyLoopRewrite()
        End If
        
        Throw ' Re-throw after logging
    End Try
End Function
```

❌ **VIOLATION:**
```vbnet
' No guardian, no failure tracking
Try
    Dim guard = New LoopGuard(1000, 30)
    While guard.Check()
        ' ...
    End While
Catch ex As InfiniteLoopException
    ' Just log and ignore - NO LEARNING!
    Console.WriteLine(ex.Message)
End Try
```

---

## 📋 Code Review Checklist

Use this checklist for **all code reviews**:

- [ ] Every `While` loop has LoopGuard or HeartbeatLoopGuard
- [ ] Every `Do` loop has LoopGuard
- [ ] Every `For` loop with uncertain bound has LoopGuard
- [ ] No `While True` without heartbeat guard
- [ ] All recursion has guaranteed base case OR RecursionGuard
- [ ] All API polling loops have 4 exit conditions (timeout/error/empty/volatile)
- [ ] All production loops register failures with LoopGuardian
- [ ] All timer events have re-entry protection
- [ ] Guard parameters appropriate for scenario (see parameter guide below)

---

## 📊 Guard Parameter Guidelines

### Required Parameters by Scenario

| Code Pattern | maxIterations | maxSeconds | guardName |
|--------------|---------------|------------|-----------|
| Fast API (< 100ms/call) | 3000 | 30 | "FastAPI" |
| Slow API (> 500ms/call) | 1000 | 60 | "SlowAPI" |
| CFB data fetch | 2000 | 60 | "CFB_Fetcher" |
| Player scraper | 10 | 30 | "PlayerScraper" |
| Odds line monitor | 5000 | 300 | "OddsMonitor" |
| Data validator | 100 | 5 | "Validator" |
| Parlay builder | 1000 | 20 | "ParlayBuilder" |
| Background monitor | 86400 | 86400 | "Monitor_24h" |
| Recursion depth | 50 | 5 | "RecursiveFunc" |

### How to Choose Parameters

**maxIterations:**
- Estimate: `(expected_runtime_seconds × calls_per_second) × 1.5`
- Example: 30 second runtime, 10 calls/sec → `(30 × 10) × 1.5 = 450`

**maxSeconds:**
- Set to `expected_runtime × 2` for safety margin
- Example: Expect 30s → set to 60s

**guardName:**
- Use descriptive name matching function/module
- Include context: `"CFB_API_Poller"` not just `"Loop1"`

---

## 🔧 Enforcement Mechanisms

### Level 1: Developer Responsibility
- Follow rules during development
- Use code review checklist

### Level 2: PSScriptAnalyzer Integration
- PowerShell scripts use `EQ12_LINT_CHECKER.ps1`
- Detects infinite loop patterns
- Auto-fix where possible

### Level 3: Copilot Instructions
- Copilot trained on these rules via `COPILOT_PROMPT.md`
- Auto-generates compliant code
- Suggests fixes for violations

### Level 4: Adaptive Learning
- LoopGuardian tracks failures across system
- Generates rewrite recommendations
- Integrates with EQ12 dashboard

---

## 🚫 Common Violations and Fixes

### Violation 1: Bare While True

❌ **WRONG:**
```vbnet
While True
    Await FetchData()
End While
```

✅ **FIX:**
```vbnet
Dim guard = New LoopGuard(3000, 30, "DataFetcher")
While guard.TryCheck()
    Dim data = Await FetchData()
    If data Is Nothing Then Exit While
    Await Task.Delay(250)
End While
```

### Violation 2: No Exit Conditions

❌ **WRONG:**
```vbnet
Dim guard = New LoopGuard(1000, 30)
While guard.Check()
    Dim result = ScrapeWebsite()
    Process(result)
End While
```

✅ **FIX:**
```vbnet
Dim guard = New LoopGuard(1000, 30, "Scraper")
While guard.TryCheck()
    Dim result = ScrapeWebsite()
    
    If result Is Nothing Then Exit While ' Exit on null
    If result.Count = 0 Then Exit While ' Exit on empty
    
    Process(result)
    Exit While ' Exit on success
End While
```

### Violation 3: Unguarded Recursion

❌ **WRONG:**
```vbnet
Public Function ValidateData(data As String) As Boolean
    If Not IsValid(data) Then
        Return ValidateData(Sanitize(data)) ' Could loop forever!
    End If
    Return True
End Function
```

✅ **FIX (Option 1: Iterative):**
```vbnet
Public Function ValidateData(data As String) As Boolean
    Dim guard = New LoopGuard(10, 5, "DataValidator")
    Dim current = data
    
    While guard.TryCheck()
        If IsValid(current) Then Return True
        current = Sanitize(current)
    End While
    
    Return False
End Function
```

✅ **FIX (Option 2: RecursionGuard):**
```vbnet
Private _recursionGuard = New RecursionGuard(10, "ValidateData")

Public Function ValidateData(data As String) As Boolean
    _recursionGuard.Enter()
    Try
        If IsValid(data) Then Return True
        Return ValidateData(Sanitize(data))
    Finally
        _recursionGuard.Exit()
    End Try
End Function
```

### Violation 4: No Adaptive Learning

❌ **WRONG:**
```vbnet
Try
    Dim guard = New LoopGuard(1000, 30)
    While guard.Check()
        ' ...
    End While
Catch ex As InfiniteLoopException
    Console.WriteLine("Loop failed")
End Try
```

✅ **FIX:**
```vbnet
Private Shared _guardian As New LoopGuardian(2)

Try
    Dim guard = New LoopGuard(1000, 30, "MyLoop")
    While guard.Check()
        ' ...
    End While
Catch ex As InfiniteLoopException
    _guardian.RegisterLoopFailure("MyLoop", ex.Message, guard.CurrentIteration)
    
    If _guardian.ShouldRewriteLoop Then
        Console.WriteLine("Adaptive system recommends rewrite")
        ' Log to EQ12 dashboard, notify via Telegram, etc.
    End If
    
    Throw
End Try
```

---

## 📈 Monitoring and Reporting

### Dashboard Integration

```vbnet
' In your loop exception handler:
Private Sub ReportToEQ12Dashboard(guardianReport As String)
    Dim logPath = "C:\EQ12\logs\loop_failures.json"
    File.WriteAllText(logPath, guardianReport)
    
    ' Optional: Send to Telegram
    If _telegramBot IsNot Nothing Then
        _telegramBot.SendMessage($"Loop guard triggered: {guardianReport}")
    End If
End Sub
```

### Metrics to Track

1. **Loop Failures Per Day** - from LoopGuardian
2. **Average Iterations Before Failure** - helps tune limits
3. **Most Common Failure Reason** - timeout vs max iterations
4. **Rewrite Recommendations** - tracks adaptive learning triggers

---

## 🎯 Exceptions to Rules

### When LoopGuard NOT Required

Only these scenarios are exempt:

1. **Simple For loops with literal bounds:**
   ```vbnet
   For i = 1 To 10 ' Known finite bound
       Console.WriteLine(i)
   Next
   ```

2. **Collection iteration:**
   ```vbnet
   For Each item In collection ' Finite collection
       Process(item)
   Next
   ```

3. **LINQ operations:**
   ```vbnet
   Dim results = data.Where(Function(x) x > 10).ToList()
   ```

### When HeartbeatLoopGuard Replaces LoopGuard

Background tasks, monitors, and long-running processes should use HeartbeatLoopGuard instead:

```vbnet
Dim heartbeat = New HeartbeatLoopGuard("LongRunner")

Task.Run(Sub()
             While heartbeat.IsRunning
                 ' Safe - can be stopped externally
             End While
         End Sub)
```

---

## 📚 Related Documentation

- `LoopGuard.vb` - Core implementation
- `Examples.vb` - Real-world usage patterns
- `README.md` - Complete feature documentation
- `QUICK_START.md` - 3-minute setup guide
- `AGENTS.md` - Adaptive learning integration
- `COPILOT_PROMPT.md` - AI-assisted enforcement

---

## ✅ Compliance Summary

To be compliant with EQ12 loop protection rules:

1. ✅ Import `EQ12.Core.LoopProtection` in all files
2. ✅ Replace all `While True` with guarded loops
3. ✅ Add exit conditions to all polling loops
4. ✅ Protect all recursion with guards or guaranteed base cases
5. ✅ Register failures with LoopGuardian
6. ✅ Use appropriate guard parameters for scenario
7. ✅ Monitor dashboard for rewrite recommendations
8. ✅ Apply adaptive learning fixes when triggered

---

**These rules are permanent and apply to ALL EQ12 VB.NET code.**

**No exceptions without documented approval.**

---

*Last updated: 2025-11-27*
*Enforced by: EQ12 VB.NET Expert System*
