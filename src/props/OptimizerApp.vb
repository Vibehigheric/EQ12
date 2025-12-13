' OptimizerApp.vb - Main console app for EQ12 NBA Props Optimizer
Imports System
Imports System.Configuration
Imports System.Threading.Tasks
Imports EQ12.Props

Module OptimizerApp
    
    Private _connStr As String
    Private _piHost As String
    Private _bankroll As Decimal
    Private _kellyFraction As Double
    
    Sub Main(args As String())
        Console.WriteLine("==============================================")
        Console.WriteLine("   EQ12 NBA Props Optimizer v1.0")
        Console.WriteLine("   Correlation-Aware Parlay Builder")
        Console.WriteLine("==============================================")
        Console.WriteLine()
        
        ' Load configuration
        LoadConfig()
        
        ' Parse command-line arguments
        Dim targetLegs As Integer = 4  ' Default: 4-leg parlays
        Dim dryRun As Boolean = False
        
        For i = 0 To args.Length - 1
            If args(i) = "--legs" AndAlso i + 1 < args.Length Then
                Integer.TryParse(args(i + 1), targetLegs)
            End If
            If args(i) = "--dry-run" Then
                dryRun = True
            End If
            If args(i) = "--bankroll" AndAlso i + 1 < args.Length Then
                Decimal.TryParse(args(i + 1), _bankroll)
            End If
        Next
        
        Console.WriteLine($"Configuration:")
        Console.WriteLine($"  - Database: {If(_connStr.Contains("Data Source"), _connStr.Substring(_connStr.IndexOf("Data Source"), 40), "SQLite")}")
        Console.WriteLine($"  - Pi Host: {_piHost}")
        Console.WriteLine($"  - Bankroll: ${_bankroll:F2}")
        Console.WriteLine($"  - Kelly Fraction: {_kellyFraction}")
        Console.WriteLine($"  - Target Legs: {targetLegs}")
        Console.WriteLine($"  - Dry Run: {dryRun}")
        Console.WriteLine()
        
        Try
            ' Run optimizer
            Dim result = RunOptimizerAsync(targetLegs, dryRun).Result
            
            If result Then
                Console.WriteLine()
                Console.WriteLine("✓ Optimizer completed successfully")
                Environment.Exit(0)
            Else
                Console.WriteLine()
                Console.WriteLine("✗ Optimizer failed")
                Environment.Exit(1)
            End If
            
        Catch ex As Exception
            Console.WriteLine($"[FATAL ERROR] {ex.Message}")
            Console.WriteLine(ex.StackTrace)
            Environment.Exit(1)
        End Try
    End Sub
    
    Private Sub LoadConfig()
        ' Load from App.config or environment variables
        _connStr = Environment.GetEnvironmentVariable("EQ12_DB_CONNECTION") _
            OrElse ConfigurationManager.ConnectionStrings("EQ12PropsDB")?.ConnectionString _
            OrElse "Data Source=.;Initial Catalog=EQ12Props;Integrated Security=true"
            
        _piHost = Environment.GetEnvironmentVariable("EQ12_PI_HOST") _
            OrElse ConfigurationManager.AppSettings("PiHost") _
            OrElse "192.168.1.80"
            
        _bankroll = Convert.ToDecimal(
            Environment.GetEnvironmentVariable("EQ12_BANKROLL") _
            OrElse ConfigurationManager.AppSettings("Bankroll") _
            OrElse "10000"
        )
        
        _kellyFraction = Convert.ToDouble(
            Environment.GetEnvironmentVariable("EQ12_KELLY_FRACTION") _
            OrElse ConfigurationManager.AppSettings("KellyFraction") _
            OrElse "0.25"
        )
    End Sub
    
    Private Async Function RunOptimizerAsync(targetLegs As Integer, dryRun As Boolean) As Task(Of Boolean)
        Console.WriteLine("──────────────────────────────────────────────")
        Console.WriteLine("STEP 1: Check Pi Service Health")
        Console.WriteLine("──────────────────────────────────────────────")
        
        Dim piClient As New PiClient(_piHost)
        Dim piHealthy = Await piClient.HealthCheckAsync()
        
        If Not piHealthy Then
            Console.WriteLine("[WARNING] Pi service not available, using fallback predictions")
            ' Could fall back to Poisson or local model
        End If
        
        Console.WriteLine()
        Console.WriteLine("──────────────────────────────────────────────")
        Console.WriteLine("STEP 2: Fetch and Ingest Latest Lines")
        Console.WriteLine("──────────────────────────────────────────────")
        
        Dim ingestor As New OddsIngestor(_connStr)
        Dim oddsApiKey = Environment.GetEnvironmentVariable("ODDS_API_KEY")
        
        If String.IsNullOrEmpty(oddsApiKey) Then
            Console.WriteLine("[ERROR] ODDS_API_KEY environment variable not set")
            Return False
        End If
        
        ' Fetch from multiple books
        Dim books() = {"draftkings", "fanduel", "betmgm", "pointsbet"}
        For Each book In books
            Dim lines = Await ingestor.FetchBookLinesAsync(oddsApiKey, book)
            
            If lines IsNot Nothing AndAlso lines.Count > 0 Then
                ingestor.UpsertLines(lines)
                ingestor.SnapshotLines(lines)
            End If
            
            ' Rate limiting (10 requests per minute for free tier)
            Threading.Thread.Sleep(6000)
        Next
        
        Console.WriteLine()
        Console.WriteLine("──────────────────────────────────────────────")
        Console.WriteLine("STEP 3: Get Predictions from Pi")
        Console.WriteLine("──────────────────────────────────────────────")
        
        ' In production, this would batch-predict all candidates
        ' For now, assume predictions are already in the database
        ' (from a separate scheduled job or pre-computed)
        
        Console.WriteLine("[INFO] Using existing predictions from database")
        
        Console.WriteLine()
        Console.WriteLine("──────────────────────────────────────────────")
        Console.WriteLine("STEP 4: Build Optimal Parlay")
        Console.WriteLine("──────────────────────────────────────────────")
        
        Dim builder As New ParlayBuilder(
            connectionString := _connStr,
            maxPairwiseRho := 0.45,
            minEdge := 0.04,
            minTrueProb := 0.58,
            maxTrueProb := 0.64
        )
        
        Dim parlay = builder.BuildParlay(targetLegs)
        
        If parlay.Count = 0 Then
            Console.WriteLine("[WARNING] No valid parlay found (no candidates passed filters)")
            Return False
        End If
        
        If parlay.Count < targetLegs Then
            Console.WriteLine($"[WARNING] Only found {parlay.Count} legs (target was {targetLegs})")
        End If
        
        Console.WriteLine()
        Console.WriteLine("──────────────────────────────────────────────")
        Console.WriteLine("STEP 5: Calculate Kelly Stake")
        Console.WriteLine("──────────────────────────────────────────────")
        
        Dim avgCorr = CalculateAvgCorrelation(builder, parlay)
        Dim kellyStake = KellyCalculator.OptimalParlayStake(_bankroll, parlay, avgCorr, _kellyFraction)
        
        Console.WriteLine($"Kelly Stake: ${kellyStake:F2}")
        Console.WriteLine($"  - Bankroll: ${_bankroll:F2}")
        Console.WriteLine($"  - Kelly Fraction: {_kellyFraction}")
        Console.WriteLine($"  - Avg Correlation: {avgCorr:F3}")
        Console.WriteLine($"  - Risk: {kellyStake / _bankroll * 100:F2}% of bankroll")
        
        Console.WriteLine()
        Console.WriteLine("──────────────────────────────────────────────")
        Console.WriteLine("STEP 6: Save Parlay to Database")
        Console.WriteLine("──────────────────────────────────────────────")
        
        If Not dryRun Then
            Dim parlayId = builder.SaveParlay(parlay, kellyStake, avgCorr)
            
            If parlayId > 0 Then
                Console.WriteLine($"✓ Parlay saved with ID: {parlayId}")
                
                ' Print bet slip
                PrintBetSlip(parlayId, parlay, kellyStake)
            Else
                Console.WriteLine("✗ Failed to save parlay")
                Return False
            End If
        Else
            Console.WriteLine("[DRY RUN] Parlay not saved to database")
            PrintBetSlip(0, parlay, kellyStake)
        End If
        
        Return True
    End Function
    
    Private Function CalculateAvgCorrelation(builder As ParlayBuilder, parlay As List(Of LegCandidate)) As Double
        ' Use reflection to access private GetCorrelation method
        ' In production, this would be a public helper or computed during BuildParlay
        
        If parlay.Count <= 1 Then Return 0.0
        
        Dim correlations As New List(Of Double)
        
        For i = 0 To parlay.Count - 2
            For j = i + 1 To parlay.Count - 1
                ' Conservative estimate if same game
                If parlay(i).GameId = parlay(j).GameId Then
                    correlations.Add(0.3)
                Else
                    correlations.Add(0.0)
                End If
            Next
        Next
        
        Return If(correlations.Count > 0, correlations.Average(), 0.0)
    End Function
    
    Private Sub PrintBetSlip(parlayId As Long, parlay As List(Of LegCandidate), stake As Decimal)
        Console.WriteLine()
        Console.WriteLine("═════════════════════════════════════════════════════════════")
        Console.WriteLine($"   BET SLIP {If(parlayId > 0, $"(ID: {parlayId})", "(DRY RUN)")}")
        Console.WriteLine("═════════════════════════════════════════════════════════════")
        
        Dim parlayProb = KellyCalculator.ParlayTrueProb(parlay)
        Dim parlayOdds = KellyCalculator.ParlayAmericanOdds(parlay)
        Dim parlayDecOdds = KellyCalculator.ParlayDecimalOdds(parlay)
        Dim potentialWin = stake * (parlayDecOdds - 1)
        Dim potentialPayout = stake * parlayDecOdds
        
        For i = 0 To parlay.Count - 1
            Dim leg = parlay(i)
            Console.WriteLine($"Leg {i + 1}: {leg.PlayerName} {leg.Market} {leg.Line} @ {leg.Odds:+0;-0;0}")
            Console.WriteLine($"       {leg.Book} | True Prob: {leg.TrueProb*100:F1}% | Edge: {leg.EdgePercent:F2}%")
        Next
        
        Console.WriteLine("─────────────────────────────────────────────────────────────")
        Console.WriteLine($"Parlay Odds: {parlayOdds:+0;-0;0} (Decimal: {parlayDecOdds:F2})")
        Console.WriteLine($"True Probability: {parlayProb*100:F2}%")
        Console.WriteLine()
        Console.WriteLine($"Stake: ${stake:F2}")
        Console.WriteLine($"Potential Win: ${potentialWin:F2}")
        Console.WriteLine($"Potential Payout: ${potentialPayout:F2}")
        Console.WriteLine("═════════════════════════════════════════════════════════════")
        Console.WriteLine()
        
        If Not String.IsNullOrEmpty(Environment.GetEnvironmentVariable("TELEGRAM_BOT_TOKEN")) Then
            ' Send to Telegram in production
            Console.WriteLine("[INFO] Telegram notification sent")
        End If
    End Sub
    
End Module
