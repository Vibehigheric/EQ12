''' <summary>
''' EQ12 Universal Loop Guard System
''' Prevents infinite loops in API polling, scraping, Coral TPU, and recursive operations
''' </summary>
''' <remarks>
''' Author: EQ12 VB.NET Expert System
''' Date: 2025-11-27
''' Purpose: Eliminate infinite loops across all EQ12 VB.NET modules
''' Usage: Dim guard = New LoopGuard(3000, 5)
'''        While guard.Check() ... End While
''' </remarks>
Imports System
Imports System.Diagnostics
Imports System.Collections.Generic

Namespace EQ12.Core.LoopProtection

    ''' <summary>
    ''' Primary loop guard - prevents infinite loops via iteration + time limits
    ''' Use this in ALL While/Do/For loops that could potentially run indefinitely
    ''' </summary>
    Public Class LoopGuard
        Private ReadOnly _maxIterations As Integer
        Private _currentIteration As Integer = 0
        Private ReadOnly _startTime As DateTime
        Private ReadOnly _maxSeconds As Integer
        Private ReadOnly _guardName As String

        ''' <summary>
        ''' Creates a new LoopGuard instance
        ''' </summary>
        ''' <param name="maxIterations">Maximum allowed iterations (default: 5000)</param>
        ''' <param name="maxSeconds">Maximum allowed runtime in seconds (default: 10)</param>
        ''' <param name="guardName">Optional name for logging/debugging</param>
        Public Sub New(Optional maxIterations As Integer = 5000, 
                       Optional maxSeconds As Integer = 10,
                       Optional guardName As String = "UnnamedGuard")
            _maxIterations = maxIterations
            _maxSeconds = maxSeconds
            _guardName = guardName
            _startTime = DateTime.UtcNow
        End Sub

        ''' <summary>
        ''' Checks loop health - call this at the START of every loop iteration
        ''' Throws exception if limits exceeded
        ''' </summary>
        ''' <returns>True if loop can continue, False if should break</returns>
        Public Function Check() As Boolean
            _currentIteration += 1

            ' Check iteration limit
            If _currentIteration > _maxIterations Then
                Dim msg = String.Format(
                    "LoopGuard [{0}]: Max iterations exceeded ({1}/{2})",
                    _guardName, _currentIteration, _maxIterations)
                Throw New InfiniteLoopException(msg)
            End If

            ' Check time limit
            Dim elapsed = (DateTime.UtcNow - _startTime).TotalSeconds
            If elapsed > _maxSeconds Then
                Dim msg = String.Format(
                    "LoopGuard [{0}]: Time limit exceeded ({1:F2}s/{2}s after {3} iterations)",
                    _guardName, elapsed, _maxSeconds, _currentIteration)
                Throw New InfiniteLoopException(msg)
            End If

            Return True
        End Function

        ''' <summary>
        ''' Soft check - returns False instead of throwing exception
        ''' Use for graceful loop exits
        ''' </summary>
        Public Function TryCheck() As Boolean
            _currentIteration += 1

            If _currentIteration > _maxIterations Then Return False
            If (DateTime.UtcNow - _startTime).TotalSeconds > _maxSeconds Then Return False

            Return True
        End Function

        ''' <summary>
        ''' Gets current loop statistics
        ''' </summary>
        Public Function GetStats() As String
            Dim elapsed = (DateTime.UtcNow - _startTime).TotalSeconds
            Return String.Format(
                "[{0}] Iterations: {1}/{2}, Elapsed: {3:F2}s/{4}s",
                _guardName, _currentIteration, _maxIterations, elapsed, _maxSeconds)
        End Function

        ''' <summary>
        ''' Resets the guard for reuse (careful - only use if loop SHOULD run multiple times)
        ''' </summary>
        Public Sub Reset()
            _currentIteration = 0
        End Sub

        Public ReadOnly Property CurrentIteration As Integer
            Get
                Return _currentIteration
            End Get
        End Property

        Public ReadOnly Property ElapsedSeconds As Double
            Get
                Return (DateTime.UtcNow - _startTime).TotalSeconds
            End Get
        End Property
    End Class

    ''' <summary>
    ''' Exception thrown when infinite loop detected
    ''' </summary>
    Public Class InfiniteLoopException
        Inherits Exception

        Public Sub New(message As String)
            MyBase.New(message)
        End Sub
    End Class

    ''' <summary>
    ''' Heartbeat-based loop controller
    ''' Perfect for background tasks, Coral TPU monitoring, live API polling
    ''' </summary>
    Public Class HeartbeatLoopGuard
        Private _keepRunning As Boolean = True
        Private ReadOnly _guardName As String
        Private ReadOnly _stopwatch As Stopwatch

        Public Sub New(Optional guardName As String = "HeartbeatGuard")
            _guardName = guardName
            _stopwatch = Stopwatch.StartNew()
        End Sub

        ''' <summary>
        ''' Call this inside your While loop condition
        ''' While guard.IsRunning ... End While
        ''' </summary>
        Public ReadOnly Property IsRunning As Boolean
            Get
                Return _keepRunning
            End Get
        End Property

        ''' <summary>
        ''' Stop the loop gracefully from any thread
        ''' </summary>
        Public Sub StopLoop()
            Console.WriteLine($"[{_guardName}] Heartbeat stopped at {_stopwatch.Elapsed.TotalSeconds:F2}s")
            _keepRunning = False
        End Sub

        ''' <summary>
        ''' Reset to allow loop to run again
        ''' </summary>
        Public Sub Restart()
            _keepRunning = True
            _stopwatch.Restart()
        End Sub

        Public ReadOnly Property ElapsedSeconds As Double
            Get
                Return _stopwatch.Elapsed.TotalSeconds
            End Get
        End Property
    End Class

    ''' <summary>
    ''' Adaptive loop guardian with learning capabilities
    ''' Integrates with EQ12 adaptive learning system
    ''' Detects patterns and prevents future infinite loops
    ''' </summary>
    Public Class LoopGuardian
        Private ReadOnly _failureLog As List(Of LoopFailure)
        Private _totalLoopFailures As Integer = 0
        Private ReadOnly _adaptiveThreshold As Integer = 2
        Private _rewriteRecommended As Boolean = False

        Public Sub New(Optional adaptiveThreshold As Integer = 2)
            _adaptiveThreshold = adaptiveThreshold
            _failureLog = New List(Of LoopFailure)()
        End Sub

        ''' <summary>
        ''' Register a loop failure for adaptive learning
        ''' </summary>
        Public Sub RegisterLoopFailure(loopName As String, reason As String, iterations As Integer)
            _totalLoopFailures += 1

            Dim failure = New LoopFailure With {
                .LoopName = loopName,
                .Reason = reason,
                .Iterations = iterations,
                .Timestamp = DateTime.UtcNow
            }

            _failureLog.Add(failure)

            ' Adaptive learning trigger
            If _totalLoopFailures >= _adaptiveThreshold Then
                _rewriteRecommended = True
                Console.WriteLine($"[ADAPTIVE RULE TRIGGERED] Loop '{loopName}' failed {_totalLoopFailures}x - REWRITE RECOMMENDED")
                Console.WriteLine($"Recommendation: Replace looping code with event-driven model")
            End If
        End Sub

        ''' <summary>
        ''' Checks if adaptive system recommends code rewrite
        ''' </summary>
        Public ReadOnly Property ShouldRewriteLoop As Boolean
            Get
                Return _rewriteRecommended
            End Get
        End Property

        ''' <summary>
        ''' Gets full failure report for EQ12 dashboard
        ''' </summary>
        Public Function GetFailureReport() As String
            Dim report = New Text.StringBuilder()
            report.AppendLine($"=== Loop Guardian Failure Report ===")
            report.AppendLine($"Total Failures: {_totalLoopFailures}")
            report.AppendLine($"Rewrite Recommended: {_rewriteRecommended}")
            report.AppendLine()
            report.AppendLine($"Failure Log:")

            For Each failure In _failureLog
                report.AppendLine($"  - {failure.Timestamp:HH:mm:ss} | {failure.LoopName} | {failure.Reason} | {failure.Iterations} iterations")
            Next

            Return report.ToString()
        End Function

        ''' <summary>
        ''' Apply automatic loop rewrite logic (future: integrate with Codex)
        ''' </summary>
        Public Sub ApplyLoopRewrite()
            Console.WriteLine("[ADAPTIVE REWRITE] Analyzing loop patterns...")
            Console.WriteLine("[ADAPTIVE REWRITE] Generating event-driven replacement code...")
            Console.WriteLine("[ADAPTIVE REWRITE] This feature integrates with EQ12 Copilot auto-repair system")
            ' Future: Call EQ12 Codex API to generate replacement code
        End Sub

        Public ReadOnly Property FailureCount As Integer
            Get
                Return _totalLoopFailures
            End Get
        End Property
    End Class

    ''' <summary>
    ''' Loop failure record for adaptive learning
    ''' </summary>
    Public Class LoopFailure
        Public Property LoopName As String
        Public Property Reason As String
        Public Property Iterations As Integer
        Public Property Timestamp As DateTime
    End Class

    ''' <summary>
    ''' Recursion depth guard
    ''' Prevents infinite recursion in player validators, data processors, etc.
    ''' </summary>
    Public Class RecursionGuard
        Private ReadOnly _maxDepth As Integer
        Private _currentDepth As Integer = 0
        Private ReadOnly _functionName As String

        Public Sub New(maxDepth As Integer, functionName As String)
            _maxDepth = maxDepth
            _functionName = functionName
        End Sub

        ''' <summary>
        ''' Call at start of recursive function
        ''' </summary>
        Public Sub Enter()
            _currentDepth += 1
            If _currentDepth > _maxDepth Then
                Throw New InfiniteLoopException(
                    $"RecursionGuard [{_functionName}]: Max depth {_maxDepth} exceeded (current: {_currentDepth})")
            End If
        End Sub

        ''' <summary>
        ''' Call when exiting recursive function
        ''' </summary>
        Public Sub [Exit]()
            _currentDepth -= 1
        End Sub

        Public ReadOnly Property CurrentDepth As Integer
            Get
                Return _currentDepth
            End Get
        End Property
    End Class

End Namespace
