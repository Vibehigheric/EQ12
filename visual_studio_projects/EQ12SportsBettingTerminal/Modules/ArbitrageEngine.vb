
' ArbitrageBotEngine.vb
' Source: GitHub repo https://github.com/personal-coding/Live-Sports-Arbitrage-Bet-Finder, adapted for EQ12
' Original description: Automated bot that identifies live sports arbitrage opportunities across FanDuel, DraftKings, and William Hill (Caesars).
' Functions extracted:
    ' ArbFinder(object) from F & D - Arb_Website - Two Person.py
    ' ArbFinder(object) from F & D - Arb_Website.py
    ' ArbFinder(object) from F & W - Arb_Website - Two Person.py

Imports System
Imports System.Data
Imports System.Data.SQLite

Public Class ArbitrageBotEngine
    
    Private ReadOnly dbWriter As DBWriter
    Private ReadOnly logger As Logger
    
    Public Sub New()
        dbWriter = New DBWriter()
        logger = New Logger("ArbitrageBotEngine")
        logger.Info("ArbitrageBotEngine initialized from GitHub repo integration")
    End Sub
    
    Public Function DetectArbitrageOpportunities(oddsData As DataTable) As List(Of ArbitrageOpportunity)
        ' Core arbitrage detection logic adapted from Live-Sports-Arbitrage-Bet-Finder
        Dim opportunities As New List(Of ArbitrageOpportunity)()
        
        Try
            ' Group odds by event_id for comparison
            Dim eventGroups = oddsData.AsEnumerable().GroupBy(Function(row) row("event_id").ToString())
            
            For Each eventGroup In eventGroups
                Dim eventOdds = eventGroup.ToArray()
                
                ' Check for two-sided arbitrage (ML, Spread, Total)
                Dim arbOpp = CheckTwoSidedArbitrage(eventOdds)
                If arbOpp IsNot Nothing Then
                    opportunities.Add(arbOpp)
                End If
            Next
            
            ' Log opportunities to database
            For Each opp In opportunities
                LogArbitrageOpportunity(opp)
                SendArbitrageAlert(opp)
            Next
            
            logger.Info($"Detected {opportunities.Count} arbitrage opportunities")
            Return opportunities
            
        Catch ex As Exception
            logger.Error($"Error detecting arbitrage: {ex.Message}")
            Return opportunities
        End Try
    End Function
    
    Private Function CheckTwoSidedArbitrage(eventOdds As DataRow()) As ArbitrageOpportunity
        ' Implement arbitrage detection algorithm from GitHub repo
        ' Calculate implied probabilities and check if sum < 1.0
        
        Try
            ' Find best odds for each side
            Dim sideAOdds As Integer = Integer.MinValue
            Dim sideBOdds As Integer = Integer.MinValue
            Dim sideABook As String = ""
            Dim sideBBook As String = ""
            
            For Each row In eventOdds
                Dim odds As Integer = Convert.ToInt32(row("odds"))
                Dim book As String = row("book").ToString()
                Dim selection As String = row("selection").ToString()
                
                ' Logic to identify opposing sides and track best odds
                ' This would be adapted from the specific GitHub repo logic
            Next
            
            ' Calculate arbitrage percentage
            Dim impliedA As Double = ImpliedProbabilityFromAmerican(sideAOdds)
            Dim impliedB As Double = ImpliedProbabilityFromAmerican(sideBOdds)
            Dim totalImplied As Double = impliedA + impliedB
            
            If totalImplied < 1.0 Then
                Dim arbPct As Double = ((1.0 / totalImplied) - 1.0) * 100
                
                Return New ArbitrageOpportunity With {
                    .EventId = eventOdds(0)("event_id").ToString(),
                    .SideA = "Team A",
                    .BookA = sideABook,
                    .OddsA = sideAOdds,
                    .SideB = "Team B", 
                    .BookB = sideBBook,
                    .OddsB = sideBOdds,
                    .ArbPercent = arbPct,
                    .Timestamp = DateTime.Now
                }
            End If
            
        Catch ex As Exception
            logger.Error($"Error in arbitrage calculation: {ex.Message}")
        End Try
        
        Return Nothing
    End Function
    
    Private Function ImpliedProbabilityFromAmerican(americanOdds As Integer) As Double
        ' Convert American odds to implied probability
        If americanOdds > 0 Then
            Return 100.0 / (americanOdds + 100.0)
        Else
            Return Math.Abs(americanOdds) / (Math.Abs(americanOdds) + 100.0)
        End If
    End Function
    
    Private Sub LogArbitrageOpportunity(opp As ArbitrageOpportunity)
        ' Log to SQLite and BigQuery
        Try
            Dim sql As String = "INSERT INTO arb_opportunities (event_id, sideA, bookA, oddsA, sideB, bookB, oddsB, arb_pct) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            dbWriter.ExecuteNonQuery(sql, opp.EventId, opp.SideA, opp.BookA, opp.OddsA, opp.SideB, opp.BookB, opp.OddsB, opp.ArbPercent)
            
            ' Sync to BigQuery
            dbWriter.SyncToBigQuery("arb_opportunities")
            
        Catch ex As Exception
            logger.Error($"Error logging arbitrage opportunity: {ex.Message}")
        End Try
    End Sub
    
    Private Sub SendArbitrageAlert(opp As ArbitrageOpportunity)
        ' Send alert via Telegram/Discord with Bitly link
        Try
            Dim alertMessage As String = $"🚨 ARBITRAGE ALERT: {opp.ArbPercent:F2}% profit opportunity"
            Dim detailUrl As String = $"https://eq12.local/arb/{opp.EventId}"
            Dim bitlyUrl As String = BitlyHelper.ShortenUrl(detailUrl)
            
            ' Send via configured alert channels
            AlertsHelper.SendTelegramAlert(alertMessage & " " & bitlyUrl)
            AlertsHelper.SendDiscordAlert(alertMessage & " " & bitlyUrl)
            
        Catch ex As Exception
            logger.Error($"Error sending arbitrage alert: {ex.Message}")
        End Try
    End Sub
    
End Class

Public Class ArbitrageOpportunity
    Public Property EventId As String
    Public Property SideA As String
    Public Property BookA As String
    Public Property OddsA As Integer
    Public Property SideB As String
    Public Property BookB As String
    Public Property OddsB As Integer
    Public Property ArbPercent As Double
    Public Property Timestamp As DateTime
End Class
