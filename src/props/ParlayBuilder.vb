' ParlayBuilder.vb - Greedy parlay construction with correlation constraints
Imports System
Imports System.Collections.Generic
Imports System.Linq
Imports System.Data.SqlClient

Namespace EQ12.Props

    ''' <summary>
    ''' Represents a single leg candidate for parlay building
    ''' </summary>
    Public Class LegCandidate
        Public Property PlayerId As String
        Public Property PlayerName As String
        Public Property GameId As String
        Public Property Market As String
        Public Property Line As Decimal
        Public Property Odds As Integer
        Public Property TrueProb As Double
        Public Property EdgePercent As Double
        Public Property Book As String
        Public Property GameDate As DateTime
        
        Public ReadOnly Property CorrelationKey As String
            Get
                Return $"{PlayerId}|{Market}"
            End Get
        End Property
        
        Public ReadOnly Property DecimalOdds As Double
            Get
                Return PricingUtils.AmericanToDecimal(Odds)
            End Get
        End Property
    End Class

    ''' <summary>
    ''' Builds optimal parlays with correlation constraints using greedy selection
    ''' </summary>
    Public Class ParlayBuilder
        Private ReadOnly _connStr As String
        Private ReadOnly _maxPairwiseRho As Double
        Private ReadOnly _minEdge As Double
        Private ReadOnly _minTrueProb As Double
        Private ReadOnly _maxTrueProb As Double
        
        Public Sub New(connectionString As String, 
                      Optional maxPairwiseRho As Double = 0.45, 
                      Optional minEdge As Double = 0.04, 
                      Optional minTrueProb As Double = 0.58, 
                      Optional maxTrueProb As Double = 0.64)
            _connStr = connectionString
            _maxPairwiseRho = maxPairwiseRho
            _minEdge = minEdge
            _minTrueProb = minTrueProb
            _maxTrueProb = maxTrueProb
        End Sub
        
        ''' <summary>
        ''' Fetch all eligible candidates for today's games
        ''' </summary>
        Public Function GetCandidates() As List(Of LegCandidate)
            Dim candidates As New List(Of LegCandidate)
            
            Using conn As New SqlConnection(_connStr)
                conn.Open()
                
                Dim sql = "
                    SELECT 
                        PlayerId, PlayerName, GameId, Market, Line, Odds, 
                        TrueProb, EdgePercent, Book, GameDate
                    FROM vw_TodayCandidates
                    WHERE EdgePercent >= @MinEdge * 100
                      AND TrueProb >= @MinProb
                      AND TrueProb <= @MaxProb
                    ORDER BY EdgePercent DESC
                "
                
                Using cmd As New SqlCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@MinEdge", _minEdge)
                    cmd.Parameters.AddWithValue("@MinProb", _minTrueProb)
                    cmd.Parameters.AddWithValue("@MaxProb", _maxTrueProb)
                    
                    Using reader = cmd.ExecuteReader()
                        While reader.Read()
                            candidates.Add(New LegCandidate With {
                                .PlayerId = reader("PlayerId").ToString(),
                                .PlayerName = reader("PlayerName").ToString(),
                                .GameId = reader("GameId").ToString(),
                                .Market = reader("Market").ToString(),
                                .Line = Convert.ToDecimal(reader("Line")),
                                .Odds = Convert.ToInt32(reader("Odds")),
                                .TrueProb = Convert.ToDouble(reader("TrueProb")),
                                .EdgePercent = Convert.ToDouble(reader("EdgePercent")),
                                .Book = reader("Book").ToString(),
                                .GameDate = Convert.ToDateTime(reader("GameDate"))
                            })
                        End While
                    End Using
                End Using
            End Using
            
            Console.WriteLine($"[ParlayBuilder] Found {candidates.Count} eligible candidates (edge >= {_minEdge*100:F1}%, prob {_minTrueProb*100:F0}-{_maxTrueProb*100:F0}%)")
            Return candidates
        End Function
        
        ''' <summary>
        ''' Lookup pairwise correlation between two legs
        ''' </summary>
        Private Function GetCorrelation(leg1 As LegCandidate, leg2 As LegCandidate) As Double
            If leg1.GameId = leg2.GameId AndAlso leg1.PlayerId = leg2.PlayerId Then
                ' Same player, same game → highly correlated (conservative estimate)
                Return 0.85
            End If
            
            If leg1.GameId <> leg2.GameId Then
                ' Different games → assume independent
                Return 0.0
            End If
            
            ' Same game, different players → check correlation table
            Using conn As New SqlConnection(_connStr)
                conn.Open()
                
                Dim sql = "
                    SELECT TOP 1 Rho
                    FROM dbo.Correlations
                    WHERE (
                        (Player1Id = @P1 AND Market1 = @M1 AND Player2Id = @P2 AND Market2 = @M2)
                        OR
                        (Player1Id = @P2 AND Market1 = @M2 AND Player2Id = @P1 AND Market2 = @M1)
                    )
                    AND SampleSize >= 30
                "
                
                Using cmd As New SqlCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@P1", leg1.PlayerId)
                    cmd.Parameters.AddWithValue("@M1", leg1.Market)
                    cmd.Parameters.AddWithValue("@P2", leg2.PlayerId)
                    cmd.Parameters.AddWithValue("@M2", leg2.Market)
                    
                    Dim result = cmd.ExecuteScalar()
                    If result IsNot Nothing Then
                        Return Convert.ToDouble(result)
                    End If
                End Using
            End Using
            
            ' No correlation data → conservative default for same-game props
            Return 0.3
        End Function
        
        ''' <summary>
        ''' Build a parlay using greedy selection with correlation constraints
        ''' </summary>
        Public Function BuildParlay(targetLegs As Integer) As List(Of LegCandidate)
            Dim candidates = GetCandidates()
            If candidates.Count = 0 Then
                Console.WriteLine("[ParlayBuilder] No candidates available")
                Return New List(Of LegCandidate)
            End If
            
            Dim selected As New List(Of LegCandidate)
            Dim correlations As New List(Of Double)
            
            ' Sort candidates by edge (descending)
            candidates = candidates.OrderByDescending(Function(c) c.EdgePercent).ToList()
            
            For Each candidate In candidates
                If selected.Count >= targetLegs Then Exit For
                
                ' Check correlation constraint with all existing legs
                Dim violatesConstraint = False
                For Each leg In selected
                    Dim rho = GetCorrelation(candidate, leg)
                    
                    If Math.Abs(rho) > _maxPairwiseRho Then
                        Console.WriteLine($"[ParlayBuilder] Skipping {candidate.PlayerName} {candidate.Market} (ρ={rho:F3} > {_maxPairwiseRho:F2} with {leg.PlayerName})")
                        violatesConstraint = True
                        Exit For
                    End If
                    
                    correlations.Add(rho)
                Next
                
                If Not violatesConstraint Then
                    selected.Add(candidate)
                    Console.WriteLine($"[ParlayBuilder] Added leg {selected.Count}: {candidate.PlayerName} {candidate.Market} {candidate.Line} @ {candidate.Odds} (edge={candidate.EdgePercent:F2}%, prob={candidate.TrueProb*100:F1}%)")
                End If
            Next
            
            If selected.Count > 0 Then
                Dim avgCorr = If(correlations.Count > 0, correlations.Average(), 0.0)
                Dim parlayProb = KellyCalculator.ParlayTrueProb(selected)
                Dim parlayOdds = KellyCalculator.ParlayDecimalOdds(selected)
                
                Console.WriteLine()
                Console.WriteLine($"[ParlayBuilder] Parlay complete: {selected.Count} legs")
                Console.WriteLine($"  - Combined true probability: {parlayProb*100:F2}%")
                Console.WriteLine($"  - Parlay odds: {KellyCalculator.ParlayAmericanOdds(selected):+0;-0;0}")
                Console.WriteLine($"  - Average correlation: {avgCorr:F3}")
            End If
            
            Return selected
        End Function
        
        ''' <summary>
        ''' Save parlay to database and return parlay ID
        ''' </summary>
        Public Function SaveParlay(legs As List(Of LegCandidate), 
                                  kellyStake As Decimal, 
                                  avgCorrelation As Double) As Long
            If legs.Count = 0 Then Return 0
            
            Dim parlayProb = KellyCalculator.ParlayTrueProb(legs)
            Dim parlayOdds = KellyCalculator.ParlayAmericanOdds(legs)
            Dim parlayDecOdds = KellyCalculator.ParlayDecimalOdds(legs)
            Dim ev = (parlayProb * (parlayDecOdds - 1)) - (1 - parlayProb)
            
            Dim parlayId As Long = 0
            
            Using conn As New SqlConnection(_connStr)
                conn.Open()
                
                Using txn = conn.BeginTransaction()
                    Try
                        ' Insert parlay header
                        Dim insertParlay = "
                            INSERT INTO dbo.Parlays (ParlayDate, NumLegs, TrueProb, ParlayOdds, ExpectedValue, KellyStake, AvgCorrelation, Status)
                            VALUES (CAST(GETDATE() AS DATE), @NumLegs, @TrueProb, @Odds, @EV, @Stake, @AvgRho, 'Pending');
                            SELECT CAST(SCOPE_IDENTITY() AS BIGINT);
                        "
                        
                        Using cmd As New SqlCommand(insertParlay, conn, txn)
                            cmd.Parameters.AddWithValue("@NumLegs", legs.Count)
                            cmd.Parameters.AddWithValue("@TrueProb", parlayProb)
                            cmd.Parameters.AddWithValue("@Odds", parlayOdds)
                            cmd.Parameters.AddWithValue("@EV", ev)
                            cmd.Parameters.AddWithValue("@Stake", kellyStake)
                            cmd.Parameters.AddWithValue("@AvgRho", avgCorrelation)
                            
                            parlayId = Convert.ToInt64(cmd.ExecuteScalar())
                        End Using
                        
                        ' Insert each leg
                        Dim insertLeg = "
                            INSERT INTO dbo.ParlayLegs (ParlayId, PlayerId, PlayerName, GameId, Market, Line, Odds, TrueProb, EdgePercent, Book)
                            VALUES (@ParlayId, @PlayerId, @PlayerName, @GameId, @Market, @Line, @Odds, @TrueProb, @EdgePct, @Book)
                        "
                        
                        For Each leg In legs
                            Using cmd As New SqlCommand(insertLeg, conn, txn)
                                cmd.Parameters.AddWithValue("@ParlayId", parlayId)
                                cmd.Parameters.AddWithValue("@PlayerId", leg.PlayerId)
                                cmd.Parameters.AddWithValue("@PlayerName", leg.PlayerName)
                                cmd.Parameters.AddWithValue("@GameId", leg.GameId)
                                cmd.Parameters.AddWithValue("@Market", leg.Market)
                                cmd.Parameters.AddWithValue("@Line", leg.Line)
                                cmd.Parameters.AddWithValue("@Odds", leg.Odds)
                                cmd.Parameters.AddWithValue("@TrueProb", leg.TrueProb)
                                cmd.Parameters.AddWithValue("@EdgePct", leg.EdgePercent)
                                cmd.Parameters.AddWithValue("@Book", leg.Book)
                                
                                cmd.ExecuteNonQuery()
                            End Using
                        Next
                        
                        txn.Commit()
                        Console.WriteLine($"[ParlayBuilder] Saved parlay #{parlayId} to database")
                        
                    Catch ex As Exception
                        txn.Rollback()
                        Console.WriteLine($"[ERROR] Failed to save parlay: {ex.Message}")
                        Return 0
                    End Try
                End Using
            End Using
            
            Return parlayId
        End Function
        
    End Class
    
End Namespace
