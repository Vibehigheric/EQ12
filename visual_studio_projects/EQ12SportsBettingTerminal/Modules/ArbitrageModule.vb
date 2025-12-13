' EQ12 Sports Betting Terminal - Arbitrage Detection Module
' Advanced arbitrage detection and opportunity analysis across multiple sportsbooks

Imports System.Collections.Generic
Imports System.Threading.Tasks
Imports System.Linq
Imports Newtonsoft.Json

Public Class ArbitrageModule

    Private logger As Action(Of String, String)
    Private config As Dictionary(Of String, Object)

    ' Arbitrage configuration
    Private Const MinProfitThreshold As Double = 0.01 ' 1% minimum profit
    Private Const MaxBookmakerCount As Integer = 10
    Private Const StakeRounding As Integer = 2

    ' Opportunity tracking
    Private opportunities As New List(Of ArbitrageOpportunity)
    Private lastScanTime As DateTime = DateTime.MinValue
    Private scanCount As Integer = 0

    Public Event ArbitrageFound(opportunity As ArbitrageOpportunity)
    Public Event ArbitrageExpired(opportunityId As String)
    Public Event ScanCompleted(opportunityCount As Integer, scanDuration As TimeSpan)

    Public Sub New()
        InitializeArbitrageModule()

        ' Set up logging
        logger = Sub(message As String, level As String)
                     Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] [{level}] ArbitrageModule: {message}")
                 End Sub

        logger("Arbitrage Module initialized", "INFO")
    End Sub

    Private Sub InitializeArbitrageModule()
        Try
            ' Load configuration
            config = New Dictionary(Of String, Object) From {
                {"min_profit_threshold", MinProfitThreshold},
                {"max_stake", 1000.0},
                {"min_stake", 10.0},
                {"scan_interval_seconds", 30},
                {"opportunity_expiry_minutes", 5},
                {"enabled_sportsbooks", New List(Of String) From {"draftkings", "fanduel", "betmgm", "caesars"}},
                {"market_types", New List(Of String) From {"h2h", "spreads", "totals"}}
            }

        Catch ex As Exception
            logger($"Error initializing arbitrage module: {ex.Message}", "ERROR")
            Throw
        End Try
    End Sub

    Public Function AnalyzeOpportunities(oddsData As List(Of Dictionary(Of String, Object))) As List(Of ArbitrageOpportunity)
        Try
            Dim stopwatch = System.Diagnostics.Stopwatch.StartNew()
            Dim newOpportunities As New List(Of ArbitrageOpportunity)

            ' Group odds by game and market type
            Dim groupedOdds = GroupOddsByGame(oddsData)

            For Each gameGroup In groupedOdds
                Dim gameOpportunities = AnalyzeGameOpportunities(gameGroup.Value)
                newOpportunities.AddRange(gameOpportunities)
            Next

            ' Filter by profit threshold
            Dim filteredOpportunities = newOpportunities.Where(Function(opp) opp.ProfitPercentage >= CDbl(config("min_profit_threshold"))).ToList()

            ' Update opportunities list
            UpdateOpportunities(filteredOpportunities)

            stopwatch.Stop()
            scanCount += 1
            lastScanTime = DateTime.Now

            RaiseEvent ScanCompleted(filteredOpportunities.Count, stopwatch.Elapsed)
            logger($"Arbitrage scan completed: {filteredOpportunities.Count} opportunities found in {stopwatch.ElapsedMilliseconds}ms", "SUCCESS")

            Return filteredOpportunities

        Catch ex As Exception
            logger($"Error analyzing arbitrage opportunities: {ex.Message}", "ERROR")
            Return New List(Of ArbitrageOpportunity)
        End Try
    End Function

    Private Function GroupOddsByGame(oddsData As List(Of Dictionary(Of String, Object))) As Dictionary(Of String, List(Of Dictionary(Of String, Object)))
        Try
            Dim grouped As New Dictionary(Of String, List(Of Dictionary(Of String, Object)))

            For Each odds In oddsData
                Dim gameKey = $"{odds("game_id")}_{odds("market_type")}"

                If Not grouped.ContainsKey(gameKey) Then
                    grouped(gameKey) = New List(Of Dictionary(Of String, Object))
                End If

                grouped(gameKey).Add(odds)
            Next

            Return grouped

        Catch ex As Exception
            logger($"Error grouping odds by game: {ex.Message}", "ERROR")
            Return New Dictionary(Of String, List(Of Dictionary(Of String, Object)))
        End Try
    End Function

    Private Function AnalyzeGameOpportunities(gameOdds As List(Of Dictionary(Of String, Object))) As List(Of ArbitrageOpportunity)
        Try
            Dim opportunities As New List(Of ArbitrageOpportunity)

            If gameOdds.Count < 2 Then
                Return opportunities
            End If

            Dim firstOdds = gameOdds.First()
            Dim gameId = firstOdds("game_id").ToString()
            Dim marketType = firstOdds("market_type").ToString()
            Dim homeTeam = firstOdds("home_team").ToString()
            Dim awayTeam = firstOdds("away_team").ToString()

            ' Group by outcome
            Dim outcomeGroups = gameOdds.GroupBy(Function(o) o("outcome_name").ToString()).
                ToDictionary(Function(g) g.Key, Function(g) g.ToList())

            ' For head-to-head markets (2 outcomes)
            If marketType = "h2h" AndAlso outcomeGroups.Count = 2 Then
                Dim opportunity = AnalyzeTwoOutcomeArbitrage(gameId, homeTeam, awayTeam, outcomeGroups)
                If opportunity IsNot Nothing Then
                    opportunities.Add(opportunity)
                End If
            End If

            ' For 3-way markets (win/draw/win)
            If outcomeGroups.Count = 3 Then
                Dim opportunity = AnalyzeThreeOutcomeArbitrage(gameId, homeTeam, awayTeam, outcomeGroups)
                If opportunity IsNot Nothing Then
                    opportunities.Add(opportunity)
                End If
            End If

            Return opportunities

        Catch ex As Exception
            logger($"Error analyzing game opportunities: {ex.Message}", "ERROR")
            Return New List(Of ArbitrageOpportunity)
        End Try
    End Function

    Private Function AnalyzeTwoOutcomeArbitrage(gameId As String, homeTeam As String, awayTeam As String, outcomeGroups As Dictionary(Of String, List(Of Dictionary(Of String, Object)))) As ArbitrageOpportunity
        Try
            Dim outcomes = outcomeGroups.Keys.ToList()

            If outcomes.Count <> 2 Then
                Return Nothing
            End If

            ' Find best odds for each outcome
            Dim bestOdds1 = FindBestOdds(outcomeGroups(outcomes(0)))
            Dim bestOdds2 = FindBestOdds(outcomeGroups(outcomes(1)))

            If bestOdds1 Is Nothing OrElse bestOdds2 Is Nothing Then
                Return Nothing
            End If

            ' Calculate implied probabilities
            Dim prob1 = 1.0 / CDbl(bestOdds1("odds_decimal"))
            Dim prob2 = 1.0 / CDbl(bestOdds2("odds_decimal"))
            Dim totalProb = prob1 + prob2

            ' Check for arbitrage (total probability < 1)
            If totalProb >= 1.0 Then
                Return Nothing
            End If

            ' Calculate profit percentage
            Dim profitPercentage = (1.0 - totalProb) / totalProb

            If profitPercentage < CDbl(config("min_profit_threshold")) Then
                Return Nothing
            End If

            ' Calculate optimal stakes
            Dim totalStake = 100.0 ' Base stake amount
            Dim stake1 = Math.Round(totalStake * prob1 / totalProb, StakeRounding)
            Dim stake2 = Math.Round(totalStake * prob2 / totalProb, StakeRounding)

            ' Calculate potential profits
            Dim payout1 = stake1 * CDbl(bestOdds1("odds_decimal"))
            Dim payout2 = stake2 * CDbl(bestOdds2("odds_decimal"))
            Dim profit = Math.Min(payout1, payout2) - totalStake

            Dim opportunity As New ArbitrageOpportunity With {
                .Id = Guid.NewGuid().ToString(),
                .GameId = gameId,
                .HomeTeam = homeTeam,
                .AwayTeam = awayTeam,
                .MarketType = bestOdds1("market_type").ToString(),
                .ProfitPercentage = profitPercentage,
                .ProfitAmount = profit,
                .TotalStake = totalStake,
                .Bets = New List(Of ArbitrageBet) From {
                    New ArbitrageBet With {
                        .Sportsbook = bestOdds1("sportsbook").ToString(),
                        .Outcome = outcomes(0),
                        .Odds = CDbl(bestOdds1("odds_decimal")),
                        .AmericanOdds = CInt(bestOdds1("odds_american")),
                        .Stake = stake1,
                        .Payout = payout1
                    },
                    New ArbitrageBet With {
                        .Sportsbook = bestOdds2("sportsbook").ToString(),
                        .Outcome = outcomes(1),
                        .Odds = CDbl(bestOdds2("odds_decimal")),
                        .AmericanOdds = CInt(bestOdds2("odds_american")),
                        .Stake = stake2,
                        .Payout = payout2
                    }
                },
                .DetectedAt = DateTime.Now,
                .ExpiresAt = DateTime.Now.AddMinutes(CInt(config("opportunity_expiry_minutes")))
            }

            Return opportunity

        Catch ex As Exception
            logger($"Error analyzing two-outcome arbitrage: {ex.Message}", "ERROR")
            Return Nothing
        End Try
    End Function

    Private Function AnalyzeThreeOutcomeArbitrage(gameId As String, homeTeam As String, awayTeam As String, outcomeGroups As Dictionary(Of String, List(Of Dictionary(Of String, Object)))) As ArbitrageOpportunity
        Try
            If outcomeGroups.Count <> 3 Then
                Return Nothing
            End If

            Dim outcomes = outcomeGroups.Keys.ToList()

            ' Find best odds for each outcome
            Dim bestOdds As New List(Of Dictionary(Of String, Object))

            For Each outcome In outcomes
                Dim best = FindBestOdds(outcomeGroups(outcome))
                If best Is Nothing Then
                    Return Nothing
                End If
                bestOdds.Add(best)
            Next

            ' Calculate implied probabilities
            Dim probs As New List(Of Double)
            For Each odds In bestOdds
                probs.Add(1.0 / CDbl(odds("odds_decimal")))
            Next

            Dim totalProb = probs.Sum()

            ' Check for arbitrage
            If totalProb >= 1.0 Then
                Return Nothing
            End If

            Dim profitPercentage = (1.0 - totalProb) / totalProb

            If profitPercentage < CDbl(config("min_profit_threshold")) Then
                Return Nothing
            End If

            ' Calculate optimal stakes for 3-way arbitrage
            Dim totalStake = 100.0
            Dim stakes As New List(Of Double)

            For i As Integer = 0 To 2
                stakes.Add(Math.Round(totalStake * probs(i) / totalProb, StakeRounding))
            Next

            ' Create arbitrage opportunity
            Dim opportunity As New ArbitrageOpportunity With {
                .Id = Guid.NewGuid().ToString(),
                .GameId = gameId,
                .HomeTeam = homeTeam,
                .AwayTeam = awayTeam,
                .MarketType = bestOdds(0)("market_type").ToString(),
                .ProfitPercentage = profitPercentage,
                .TotalStake = totalStake,
                .Bets = New List(Of ArbitrageBet),
                .DetectedAt = DateTime.Now,
                .ExpiresAt = DateTime.Now.AddMinutes(CInt(config("opportunity_expiry_minutes")))
            }

            For i As Integer = 0 To 2
                Dim payout = stakes(i) * CDbl(bestOdds(i)("odds_decimal"))

                opportunity.Bets.Add(New ArbitrageBet With {
                    .Sportsbook = bestOdds(i)("sportsbook").ToString(),
                    .Outcome = outcomes(i),
                    .Odds = CDbl(bestOdds(i)("odds_decimal")),
                    .AmericanOdds = CInt(bestOdds(i)("odds_american")),
                    .Stake = stakes(i),
                    .Payout = payout
                })
            Next

            opportunity.ProfitAmount = opportunity.Bets.Min(Function(b) b.Payout) - totalStake

            Return opportunity

        Catch ex As Exception
            logger($"Error analyzing three-outcome arbitrage: {ex.Message}", "ERROR")
            Return Nothing
        End Try
    End Function

    Private Function FindBestOdds(oddsGroup As List(Of Dictionary(Of String, Object))) As Dictionary(Of String, Object)
        Try
            Return oddsGroup.OrderByDescending(Function(o) CDbl(o("odds_decimal"))).FirstOrDefault()

        Catch ex As Exception
            logger($"Error finding best odds: {ex.Message}", "ERROR")
            Return Nothing
        End Try
    End Function

    Private Sub UpdateOpportunities(newOpportunities As List(Of ArbitrageOpportunity))
        Try
            ' Remove expired opportunities
            Dim currentTime = DateTime.Now
            Dim expiredOppIds As New List(Of String)

            For i = opportunities.Count - 1 To 0 Step -1
                If opportunities(i).ExpiresAt < currentTime Then
                    expiredOppIds.Add(opportunities(i).Id)
                    opportunities.RemoveAt(i)
                End If
            Next

            ' Raise expired events
            For Each expiredId In expiredOppIds
                RaiseEvent ArbitrageExpired(expiredId)
            Next

            ' Add new opportunities
            For Each newOpp In newOpportunities
                ' Check if similar opportunity already exists
                Dim exists = opportunities.Any(Function(o) o.GameId = newOpp.GameId AndAlso o.MarketType = newOpp.MarketType)

                If Not exists Then
                    opportunities.Add(newOpp)
                    RaiseEvent ArbitrageFound(newOpp)

                    logger($"New arbitrage opportunity: {newOpp.HomeTeam} vs {newOpp.AwayTeam} - {newOpp.ProfitPercentage:P2} profit", "SUCCESS")
                End If
            Next

        Catch ex As Exception
            logger($"Error updating opportunities: {ex.Message}", "ERROR")
        End Try
    End Sub

    Public Function GetActiveOpportunities() As List(Of ArbitrageOpportunity)
        Try
            ' Remove expired opportunities first
            UpdateOpportunities(New List(Of ArbitrageOpportunity))

            Return opportunities.OrderByDescending(Function(o) o.ProfitPercentage).ToList()

        Catch ex As Exception
            logger($"Error getting active opportunities: {ex.Message}", "ERROR")
            Return New List(Of ArbitrageOpportunity)
        End Try
    End Function

    Public Function CalculateOptimalStakes(opportunity As ArbitrageOpportunity, totalBankroll As Double) As Dictionary(Of String, Double)
        Try
            Dim stakes As New Dictionary(Of String, Double)
            Dim maxStake = Math.Min(totalBankroll * 0.1, CDbl(config("max_stake"))) ' Max 10% of bankroll

            Dim totalImpliedProb = opportunity.Bets.Sum(Function(b) 1.0 / b.Odds)

            For Each bet In opportunity.Bets
                Dim impliedProb = 1.0 / bet.Odds
                Dim optimalStake = Math.Round(maxStake * impliedProb / totalImpliedProb, StakeRounding)
                stakes(bet.Sportsbook) = Math.Max(optimalStake, CDbl(config("min_stake")))
            Next

            Return stakes

        Catch ex As Exception
            logger($"Error calculating optimal stakes: {ex.Message}", "ERROR")
            Return New Dictionary(Of String, Double)
        End Try
    End Function

    Public Function GetStatistics() As Dictionary(Of String, Object)
        Try
            Dim activeOpps = GetActiveOpportunities()

            Return New Dictionary(Of String, Object) From {
                {"total_scans", scanCount},
                {"last_scan_time", lastScanTime},
                {"active_opportunities", activeOpps.Count},
                {"best_profit_percentage", If(activeOpps.Any(), activeOpps.Max(Function(o) o.ProfitPercentage), 0)},
                {"average_profit_percentage", If(activeOpps.Any(), activeOpps.Average(Function(o) o.ProfitPercentage), 0)},
                {"min_profit_threshold", config("min_profit_threshold")},
                {"opportunity_expiry_minutes", config("opportunity_expiry_minutes")},
                {"enabled_sportsbooks", config("enabled_sportsbooks")}
            }

        Catch ex As Exception
            logger($"Error getting arbitrage statistics: {ex.Message}", "ERROR")
            Return New Dictionary(Of String, Object)
        End Try
    End Function

    Public Sub ClearOpportunities()
        Try
            opportunities.Clear()
            logger("All arbitrage opportunities cleared", "INFO")

        Catch ex As Exception
            logger($"Error clearing opportunities: {ex.Message}", "ERROR")
        End Try
    End Sub

End Class

' Supporting classes
Public Class ArbitrageOpportunity
    Public Property Id As String
    Public Property GameId As String
    Public Property HomeTeam As String
    Public Property AwayTeam As String
    Public Property MarketType As String
    Public Property ProfitPercentage As Double
    Public Property ProfitAmount As Double
    Public Property TotalStake As Double
    Public Property Bets As List(Of ArbitrageBet)
    Public Property DetectedAt As DateTime
    Public Property ExpiresAt As DateTime

    Public ReadOnly Property IsExpired As Boolean
        Get
            Return DateTime.Now > ExpiresAt
        End Get
    End Property

    Public ReadOnly Property TimeRemaining As TimeSpan
        Get
            Return ExpiresAt.Subtract(DateTime.Now)
        End Get
    End Property

    Public Function GetSummary() As String
        Return $"{HomeTeam} vs {AwayTeam} - {ProfitPercentage:P2} profit ({Bets.Count} bets)"
    End Function
End Class

Public Class ArbitrageBet
    Public Property Sportsbook As String
    Public Property Outcome As String
    Public Property Odds As Double
    Public Property AmericanOdds As Integer
    Public Property Stake As Double
    Public Property Payout As Double

    Public ReadOnly Property Profit As Double
        Get
            Return Payout - Stake
        End Get
    End Property
End Class
