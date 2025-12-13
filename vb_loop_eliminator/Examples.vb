''' <summary>
''' EQ12 Loop Guard Usage Examples
''' Practical patterns for CFB analyzer, player fetcher, Coral TPU, parlay builder
''' </summary>
Imports System
Imports System.Threading.Tasks
Imports EQ12.Core.LoopProtection

Namespace EQ12.Examples

    Public Class LoopGuardExamples

        ' ==================== EXAMPLE 1: API Polling Loop ====================
        ''' <summary>
        ''' BEFORE: Infinite API polling
        ''' AFTER: Protected with LoopGuard
        ''' </summary>
        Public Async Function FetchCfbDataWithGuard() As Task
            Dim guard = New LoopGuard(3000, 30, "CFB_API_Polling")

            While guard.TryCheck() ' Soft check - no exception
                Try
                    Dim success = Await FetchCfbDataFromApi()

                    If Not success Then
                        Console.WriteLine("API returned no data - breaking loop")
                        Exit While
                    End If

                    ' Process data...
                    Await Task.Delay(250) ' Rate limiting

                Catch ex As Exception
                    Console.WriteLine($"API error: {ex.Message}")
                    Exit While
                End Try
            End While

            Console.WriteLine($"Loop ended: {guard.GetStats()}")
        End Function

        ' Stub for example
        Private Async Function FetchCfbDataFromApi() As Task(Of Boolean)
            Await Task.Delay(100)
            Return True
        End Function

        ' ==================== EXAMPLE 2: Player Validator (Recursion Fix) ====================
        ''' <summary>
        ''' BEFORE: Infinite recursion
        ''' Public Function ValidatePlayer(name As String) As Boolean
        '''     If Not PlayerExists(name) Then
        '''         Return ValidatePlayer(name)  ' INFINITE!
        '''     End If
        '''     Return True
        ''' End Function
        ''' 
        ''' AFTER: Iterative with LoopGuard
        ''' </summary>
        Public Function ValidatePlayerSafe(name As String) As Boolean
            Dim guard = New LoopGuard(5, 2, "PlayerValidator")

            While guard.TryCheck()
                If PlayerExists(name) Then
                    Return True
                End If

                ' Wait for cache refresh or retry
                System.Threading.Thread.Sleep(200)
            End While

            Return False ' Failed after max attempts
        End Function

        Private Function PlayerExists(name As String) As Boolean
            Return True ' Stub
        End Function

        ' ==================== EXAMPLE 3: Coral TPU Health Monitor ====================
        ''' <summary>
        ''' Heartbeat-based background monitoring
        ''' Can be stopped gracefully from any thread
        ''' </summary>
        Public Async Function MonitorCoralTpu(guard As HeartbeatLoopGuard) As Task
            While guard.IsRunning
                Try
                    Dim health = Await CheckCoralHealth()
                    Console.WriteLine($"Coral TPU Health: {health}%")

                    If health < 50 Then
                        Console.WriteLine("WARNING: Coral TPU degraded")
                        ' Trigger alert...
                    End If

                    Await Task.Delay(1000) ' Check every second

                Catch ex As Exception
                    Console.WriteLine($"Health check failed: {ex.Message}")
                    guard.StopLoop() ' Stop on critical error
                End Try
            End While

            Console.WriteLine($"Monitor stopped after {guard.ElapsedSeconds:F2}s")
        End Function

        Private Async Function CheckCoralHealth() As Task(Of Integer)
            Await Task.Delay(50)
            Return 85 ' Stub
        End Function

        ' ==================== EXAMPLE 4: Timer Event Protection ====================
        ''' <summary>
        ''' Prevents timer events from stacking and creating pseudo-infinite loop
        ''' </summary>
        Private timerGuard As Boolean = False

        Public Sub Timer1_Tick(sender As Object, e As EventArgs)
            ' Prevent re-entry
            If timerGuard Then
                Console.WriteLine("Timer still processing - skipping tick")
                Return
            End If

            timerGuard = True
            Try
                ' Heavy processing...
                Console.WriteLine("Processing timer event...")
                System.Threading.Thread.Sleep(500)

            Finally
                timerGuard = False
            End Try
        End Sub

        ' ==================== EXAMPLE 5: Scraper with Retry Logic ====================
        ''' <summary>
        ''' BEFORE: Do While Not success ... Loop (infinite if never succeeds)
        ''' AFTER: Protected with iteration limit
        ''' </summary>
        Public Async Function ScrapePlayersWithGuard() As Task(Of List(Of String))
            Dim guard = New LoopGuard(10, 15, "PlayerScraper")
            Dim players = New List(Of String)()

            While guard.TryCheck()
                players = Await ScrapePlayers()

                If players.Count > 0 Then
                    Exit While ' Success - break
                End If

                Console.WriteLine($"No players found - retry {guard.CurrentIteration}/10")
                Await Task.Delay(1000)
            End While

            Return players
        End Function

        Private Async Function ScrapePlayers() As Task(Of List(Of String))
            Await Task.Delay(200)
            Return New List(Of String) From {"Player1", "Player2"}
        End Function

        ' ==================== EXAMPLE 6: Parlay Builder with Adaptive Learning ====================
        ''' <summary>
        ''' Demonstrates LoopGuardian for adaptive learning
        ''' If parlay builder gets stuck, system learns and recommends rewrite
        ''' </summary>
        Public Function BuildParlayWithAdaptive(guardian As LoopGuardian) As List(Of String)
            Dim guard = New LoopGuard(5000, 10, "ParlayBuilder")
            Dim parlay = New List(Of String)()

            Try
                While guard.Check()
                    Dim leg = GetNextParlayLeg()
                    If leg Is Nothing Then Exit While

                    parlay.Add(leg)

                    If parlay.Count >= 10 Then Exit While ' Max legs
                End While

            Catch ex As InfiniteLoopException
                ' Register failure for adaptive learning
                guardian.RegisterLoopFailure(
                    "ParlayBuilder",
                    ex.Message,
                    guard.CurrentIteration)

                ' Check if system recommends rewrite
                If guardian.ShouldRewriteLoop Then
                    Console.WriteLine("ADAPTIVE SYSTEM: Parlay builder needs rewrite")
                    Console.WriteLine("Recommendation: Use event-driven leg selection")
                End If
            End Try

            Return parlay
        End Function

        Private Function GetNextParlayLeg() As String
            Return "Leg" ' Stub
        End Function

        ' ==================== EXAMPLE 7: Recursion with RecursionGuard ====================
        ''' <summary>
        ''' Safe recursion with depth protection
        ''' </summary>
        Private _recursionGuard As RecursionGuard

        Public Function ProcessDataRecursive(data As String, depth As Integer) As String
            If _recursionGuard Is Nothing Then
                _recursionGuard = New RecursionGuard(20, "DataProcessor")
            End If

            _recursionGuard.Enter()
            Try
                ' Base case
                If String.IsNullOrEmpty(data) OrElse depth = 0 Then
                    Return data
                End If

                ' Recursive case
                Dim processed = data.ToUpper()
                Return ProcessDataRecursive(processed, depth - 1)

            Finally
                _recursionGuard.Exit()
            End Try
        End Function

    End Class

    ' ==================== EXAMPLE 8: Complete Program with All Guards ====================
    ''' <summary>
    ''' Full example showing all guard types working together
    ''' </summary>
    Module Program
        Sub Main()
            Console.WriteLine("=== EQ12 Loop Guard Demonstration ===")
            Console.WriteLine()

            ' Example 1: Basic LoopGuard
            Console.WriteLine("--- Basic LoopGuard ---")
            Dim basicGuard = New LoopGuard(100, 5, "BasicLoop")
            Dim counter = 0
            While basicGuard.TryCheck()
                counter += 1
            End While
            Console.WriteLine($"Loop completed: {counter} iterations")
            Console.WriteLine()

            ' Example 2: HeartbeatLoopGuard
            Console.WriteLine("--- Heartbeat Guard (5 second demo) ---")
            Dim heartbeat = New HeartbeatLoopGuard("BackgroundTask")
            
            ' Simulate background task
            Task.Run(Async Function()
                         While heartbeat.IsRunning
                             Console.WriteLine($"Background task running... ({heartbeat.ElapsedSeconds:F1}s)")
                             Await Task.Delay(1000)
                         End While
                     End Function)

            ' Stop after 5 seconds
            System.Threading.Thread.Sleep(5000)
            heartbeat.StopLoop()
            System.Threading.Thread.Sleep(1000)
            Console.WriteLine()

            ' Example 3: Adaptive LoopGuardian
            Console.WriteLine("--- Adaptive LoopGuardian ---")
            Dim guardian = New LoopGuardian(adaptiveThreshold:=2)

            ' Simulate two loop failures
            guardian.RegisterLoopFailure("TestLoop1", "Timeout", 5000)
            guardian.RegisterLoopFailure("TestLoop2", "Max iterations", 10000)

            Console.WriteLine(guardian.GetFailureReport())
            Console.WriteLine()

            ' Example 4: RecursionGuard
            Console.WriteLine("--- RecursionGuard ---")
            Dim examples = New LoopGuardExamples()
            Dim result = examples.ProcessDataRecursive("test", 5)
            Console.WriteLine($"Recursion result: {result}")

            Console.WriteLine()
            Console.WriteLine("=== All guards tested successfully ===")
            Console.WriteLine("Press any key to exit...")
            Console.ReadKey()
        End Sub
    End Module

End Namespace
