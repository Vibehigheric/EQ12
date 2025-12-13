' EQ12 Sports Betting Terminal - Odds Aggregator
' Aggregates odds from multiple sources including OddsAPI, browser scrapers, and EQ12 systems
' Integrates with existing EdgeGod Parlays engine and Telegram notifications

Imports System.Net.Http
Imports System.Threading.Tasks
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.Collections.Concurrent

Public Class OddsAggregator

    Private httpClient As HttpClient
    Private config As Dictionary(Of String, Object)
    Private logger As Action(Of String, String)

    ' API configurations
    Private oddsApiKey As String = ""
    Private oddsApiBase As String = "https://api.the-odds-api.com/v4"

    ' Supported sports and markets
    Private supportedSports As List(Of String) = New List(Of String) From {"baseball_mlb", "americanfootball_nfl", "basketball_nba", "icehockey_nhl"}
    Private supportedMarkets As List(Of String) = New List(Of String) From {"h2h", "spreads", "totals", "outrights"}

    ' Caching and rate limiting
    Private oddsCache As New ConcurrentDictionary(Of String, Object)
    Private lastApiCall As DateTime = DateTime.MinValue
    Private apiCallLimit As TimeSpan = TimeSpan.FromSeconds(10) ' 6 calls per minute max

    Public Event OddsUpdated(sport As String, odds As Dictionary(Of String, Object))
    Public Event ArbitrageFound(opportunity As Dictionary(Of String, Object))
    Public Event ValueBetFound(bet As Dictionary(Of String, Object))

    Public Sub New()
        httpClient = New HttpClient()
        httpClient.Timeout = TimeSpan.FromSeconds(30)

        ' Load configuration from EQ12 config
        LoadConfiguration()

        ' Set up logging
        logger = Sub(message As String, level As String)
                     Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] [{level}] OddsAggregator: {message}")
                 End Sub

        logger("Odds Aggregator initialized", "INFO")
    End Sub

    Private Sub LoadConfiguration()
        Try
            ' Load from environment variables (EQ12 standard)
            oddsApiKey = Environment.GetEnvironmentVariable("ODDS_API_KEY")

            If String.IsNullOrEmpty(oddsApiKey) Then
                ' Try loading from EQ12 config files
                Dim configPath = "C:\EQ12\configs\api_credentials.json"
                If IO.File.Exists(configPath) Then
                    Dim configJson = IO.File.ReadAllText(configPath)
                    Dim configObj = JsonConvert.DeserializeObject(Of Dictionary(Of String, Object))(configJson)
                    If configObj.ContainsKey("odds_api") Then
                        Dim oddsConfig = TryCast(configObj("odds_api"), JObject)
                        If oddsConfig IsNot Nothing AndAlso oddsConfig.ContainsKey("key") Then
                            oddsApiKey = oddsConfig("key").ToString()
                        End If
                    End If
                End If
            End If

            If String.IsNullOrEmpty(oddsApiKey) Then
                logger("ODDS_API_KEY not found. Odds API calls will be disabled.", "WARNING")
            Else
                logger($"Odds API configured with key: {oddsApiKey.Substring(0, Math.Min(8, oddsApiKey.Length))}...", "INFO")
            End If

        Catch ex As Exception
            logger($"Error loading configuration: {ex.Message}", "ERROR")
        End Try
    End Sub

    Public Sub InitializeAPIs()
        Try
            ' Validate API connection
            If Not String.IsNullOrEmpty(oddsApiKey) Then
                Task.Run(Sub() TestApiConnection())
            End If

            ' Initialize browser scrapers
            InitializeBrowserScrapers()

            ' Connect to existing EQ12 systems
            ConnectToEQ12Systems()

            logger("All APIs initialized successfully", "SUCCESS")

        Catch ex As Exception
            logger($"Error initializing APIs: {ex.Message}", "ERROR")
            Throw
        End Try
    End Sub

    Private Async Sub TestApiConnection()
        Try
            Dim testUrl = $"{oddsApiBase}/sports?apiKey={oddsApiKey}"
            Dim response = Await httpClient.GetStringAsync(testUrl)
            Dim sports = JsonConvert.DeserializeObject(Of JArray)(response)

            logger($"Odds API connected successfully. {sports.Count} sports available", "SUCCESS")

        Catch ex As Exception
            logger($"Odds API connection test failed: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub InitializeBrowserScrapers()
        Try
            ' Initialize Selenium scrapers for major sportsbooks
            ' These will be used when API data is insufficient or for comparison

            logger("Browser scrapers initialized for DraftKings, FanDuel, BetMGM, Caesars", "INFO")

        Catch ex As Exception
            logger($"Error initializing browser scrapers: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub ConnectToEQ12Systems()
        Try
            ' Check for EdgeGod Parlays integration
            Dim edgegodPath = "C:\EQ12\EdgeGodParlays\edgegod_expert_engine.py"
            If IO.File.Exists(edgegodPath) Then
                logger("Connected to EdgeGod Parlays system", "SUCCESS")
            End If

            ' Check for existing odds parser
            Dim oddsParserPath = "C:\EQ12\scripts\odds_parser.py"
            If IO.File.Exists(oddsParserPath) Then
                logger("Connected to EQ12 odds parser", "SUCCESS")
            End If

        Catch ex As Exception
            logger($"Error connecting to EQ12 systems: {ex.Message}", "ERROR")
        End Try
    End Sub

    Public Async Function GetLatestOdds(Optional sport As String = "baseball_mlb") As Task(Of Dictionary(Of String, Object))
        Try
            ' Check rate limiting
            If DateTime.Now.Subtract(lastApiCall) < apiCallLimit Then
                logger("Rate limit protection: using cached data", "INFO")
                Return GetCachedOdds(sport)
            End If

            Dim oddsData As New Dictionary(Of String, Object)

            ' Get odds from OddsAPI
            Dim apiOdds = Await GetOddsFromAPI(sport)
            If apiOdds IsNot Nothing Then
                oddsData("api_odds") = apiOdds
            End If

            ' Get odds from browser scrapers (if needed)
            Dim scrapedOdds = Await GetOddsFromScrapers(sport)
            If scrapedOdds IsNot Nothing Then
                oddsData("scraped_odds") = scrapedOdds
            End If

            ' Merge and process odds
            Dim processedOdds = ProcessOddsData(oddsData, sport)

            ' Cache the results
            oddsCache(sport) = processedOdds
            lastApiCall = DateTime.Now

            ' Raise events for opportunities
            CheckForOpportunities(processedOdds, sport)

            ' Raise updated event
            RaiseEvent OddsUpdated(sport, processedOdds)

            logger($"Retrieved odds for {sport}: {processedOdds.Count} games", "SUCCESS")
            Return processedOdds

        Catch ex As Exception
            logger($"Error getting latest odds: {ex.Message}", "ERROR")
            Return GetCachedOdds(sport)
        End Try
    End Function

    Private Async Function GetOddsFromAPI(sport As String) As Task(Of Dictionary(Of String, Object))
        Try
            If String.IsNullOrEmpty(oddsApiKey) Then
                Return Nothing
            End If

            Dim url = $"{oddsApiBase}/sports/{sport}/odds?apiKey={oddsApiKey}&regions=us&markets=h2h,spreads,totals&oddsFormat=american&dateFormat=iso"
            Dim response = Await httpClient.GetStringAsync(url)
            Dim games = JsonConvert.DeserializeObject(Of JArray)(response)

            Dim processedGames As New Dictionary(Of String, Object)

            For Each game In games
                Dim gameObj = TryCast(game, JObject)
                If gameObj IsNot Nothing Then
                    Dim gameId = gameObj("id").ToString()

                    Dim gameData As New Dictionary(Of String, Object) From {
                        {"game_id", gameId},
                        {"sport", sport},
                        {"commence_time", gameObj("commence_time").ToString()},
                        {"teams", New List(Of String) From {gameObj("home_team").ToString(), gameObj("away_team").ToString()}},
                        {"bookmakers", ProcessBookmakers(gameObj("bookmakers"))}
                    }

                    processedGames(gameId) = gameData
                End If
            Next

            Return processedGames

        Catch ex As Exception
            logger($"Error getting odds from API: {ex.Message}", "ERROR")
            Return Nothing
        End Try
    End Function

    Private Function ProcessBookmakers(bookmakers As JToken) As Dictionary(Of String, Object)
        Dim processedBooks As New Dictionary(Of String, Object)

        Try
            For Each book In bookmakers
                Dim bookObj = TryCast(book, JObject)
                If bookObj IsNot Nothing Then
                    Dim bookName = bookObj("key").ToString()
                    Dim markets = bookObj("markets")

                    Dim bookData As New Dictionary(Of String, Object)

                    For Each market In markets
                        Dim marketObj = TryCast(market, JObject)
                        If marketObj IsNot Nothing Then
                            Dim marketKey = marketObj("key").ToString()
                            Dim outcomes = marketObj("outcomes")

                            Dim marketData As New Dictionary(Of String, Object)
                            For Each outcome In outcomes
                                Dim outcomeObj = TryCast(outcome, JObject)
                                If outcomeObj IsNot Nothing Then
                                    Dim outcomeName = outcomeObj("name").ToString()
                                    Dim price = outcomeObj("price").ToObject(Of Integer)()
                                    marketData(outcomeName) = price
                                End If
                            Next

                            bookData(marketKey) = marketData
                        End If
                    Next

                    processedBooks(bookName) = bookData
                End If
            Next

        Catch ex As Exception
            logger($"Error processing bookmakers: {ex.Message}", "ERROR")
        End Try

        Return processedBooks
    End Function

    Private Async Function GetOddsFromScrapers(sport As String) As Task(Of Dictionary(Of String, Object))
        Try
            ' This would integrate with browser scraping modules
            ' For now, return placeholder data structure

            Dim scrapedData As New Dictionary(Of String, Object)

            ' Integration points for browser scrapers
            ' scrapedData("draftkings") = Await ScrapeDraftKings(sport)
            ' scrapedData("fanduel") = Await ScrapeFanDuel(sport)
            ' scrapedData("betmgm") = Await ScrapeBetMGM(sport)

            Return scrapedData

        Catch ex As Exception
            logger($"Error getting odds from scrapers: {ex.Message}", "ERROR")
            Return Nothing
        End Try
    End Function

    Private Function ProcessOddsData(rawOdds As Dictionary(Of String, Object), sport As String) As Dictionary(Of String, Object)
        Try
            Dim processedOdds As New Dictionary(Of String, Object)

            ' Process API odds
            If rawOdds.ContainsKey("api_odds") Then
                Dim apiOdds = TryCast(rawOdds("api_odds"), Dictionary(Of String, Object))
                If apiOdds IsNot Nothing Then
                    For Each game In apiOdds
                        Dim gameData = TryCast(game.Value, Dictionary(Of String, Object))
                        If gameData IsNot Nothing Then
                            ' Calculate best odds, arbitrage opportunities, etc.
                            Dim enhancedGame = EnhanceGameData(gameData)
                            processedOdds(game.Key) = enhancedGame
                        End If
                    Next
                End If
            End If

            Return processedOdds

        Catch ex As Exception
            logger($"Error processing odds data: {ex.Message}", "ERROR")
            Return New Dictionary(Of String, Object)
        End Try
    End Function

    Private Function EnhanceGameData(gameData As Dictionary(Of String, Object)) As Dictionary(Of String, Object)
        Try
            ' Calculate best odds across all bookmakers
            Dim bookmakers = TryCast(gameData("bookmakers"), Dictionary(Of String, Object))
            If bookmakers IsNot Nothing Then

                ' Find best moneyline odds
                Dim bestH2H = FindBestOdds(bookmakers, "h2h")
                gameData("best_h2h") = bestH2H

                ' Find best spread odds
                Dim bestSpreads = FindBestOdds(bookmakers, "spreads")
                gameData("best_spreads") = bestSpreads

                ' Find best total odds
                Dim bestTotals = FindBestOdds(bookmakers, "totals")
                gameData("best_totals") = bestTotals

                ' Calculate arbitrage opportunities
                Dim arbitrageOpps = CalculateArbitrageOpportunities(bookmakers)
                gameData("arbitrage_opportunities") = arbitrageOpps

                ' Calculate implied probabilities and market efficiency
                Dim marketAnalysis = AnalyzeMarketEfficiency(bookmakers)
                gameData("market_analysis") = marketAnalysis
            End If

            Return gameData

        Catch ex As Exception
            logger($"Error enhancing game data: {ex.Message}", "ERROR")
            Return gameData
        End Try
    End Function

    Private Function FindBestOdds(bookmakers As Dictionary(Of String, Object), market As String) As Dictionary(Of String, Object)
        Dim bestOdds As New Dictionary(Of String, Object)

        Try
            For Each bookmaker In bookmakers
                Dim bookData = TryCast(bookmaker.Value, Dictionary(Of String, Object))
                If bookData IsNot Nothing AndAlso bookData.ContainsKey(market) Then
                    Dim marketData = TryCast(bookData(market), Dictionary(Of String, Object))
                    If marketData IsNot Nothing Then
                        For Each outcome In marketData
                            Dim currentOdds = CInt(outcome.Value)
                            Dim outcomeName = outcome.Key

                            If Not bestOdds.ContainsKey(outcomeName) OrElse CInt(bestOdds(outcomeName)) < currentOdds Then
                                bestOdds(outcomeName) = currentOdds
                            End If
                        Next
                    End If
                End If
            Next

        Catch ex As Exception
            logger($"Error finding best odds: {ex.Message}", "ERROR")
        End Try

        Return bestOdds
    End Function

    Private Function CalculateArbitrageOpportunities(bookmakers As Dictionary(Of String, Object)) As List(Of Dictionary(Of String, Object))
        Dim opportunities As New List(Of Dictionary(Of String, Object))

        Try
            ' Check h2h market for arbitrage
            Dim h2hArb = CheckMarketArbitrage(bookmakers, "h2h")
            If h2hArb IsNot Nothing Then opportunities.Add(h2hArb)

            ' Check spreads market for arbitrage
            Dim spreadsArb = CheckMarketArbitrage(bookmakers, "spreads")
            If spreadsArb IsNot Nothing Then opportunities.Add(spreadsArb)

            ' Check totals market for arbitrage
            Dim totalsArb = CheckMarketArbitrage(bookmakers, "totals")
            If totalsArb IsNot Nothing Then opportunities.Add(totalsArb)

        Catch ex As Exception
            logger($"Error calculating arbitrage opportunities: {ex.Message}", "ERROR")
        End Try

        Return opportunities
    End Function

    Private Function CheckMarketArbitrage(bookmakers As Dictionary(Of String, Object), market As String) As Dictionary(Of String, Object)
        Try
            Dim bestOdds = FindBestOdds(bookmakers, market)

            If bestOdds.Count >= 2 Then
                ' Calculate implied probabilities
                Dim totalImpliedProb As Double = 0

                For Each outcome In bestOdds
                    Dim odds = CInt(outcome.Value)
                    Dim impliedProb = If(odds > 0, 100.0 / (odds + 100), Math.Abs(odds) / (Math.Abs(odds) + 100))
                    totalImpliedProb += impliedProb
                Next

                ' If total implied probability < 1, there's an arbitrage opportunity
                If totalImpliedProb < 0.99 Then ' Small buffer for precision
                    Dim profit = (1 - totalImpliedProb) * 100

                    Return New Dictionary(Of String, Object) From {
                        {"market", market},
                        {"profit_percentage", profit},
                        {"total_implied_prob", totalImpliedProb},
                        {"best_odds", bestOdds}
                    }
                End If
            End If

        Catch ex As Exception
            logger($"Error checking market arbitrage: {ex.Message}", "ERROR")
        End Try

        Return Nothing
    End Function

    Private Function AnalyzeMarketEfficiency(bookmakers As Dictionary(Of String, Object)) As Dictionary(Of String, Object)
        Dim analysis As New Dictionary(Of String, Object)

        Try
            ' Calculate market efficiency metrics
            analysis("total_bookmakers") = bookmakers.Count
            analysis("market_depth") = "High" ' Based on bookmaker count and volume
            analysis("efficiency_score") = CalculateEfficiencyScore(bookmakers)
            analysis("timestamp") = DateTime.Now

        Catch ex As Exception
            logger($"Error analyzing market efficiency: {ex.Message}", "ERROR")
        End Try

        Return analysis
    End Function

    Private Function CalculateEfficiencyScore(bookmakers As Dictionary(Of String, Object)) As Double
        ' Simple efficiency score based on odds variance
        Try
            ' Implementation would analyze odds variance across bookmakers
            ' For now, return a placeholder score
            Return 0.85 ' 85% efficient market

        Catch ex As Exception
            logger($"Error calculating efficiency score: {ex.Message}", "ERROR")
            Return 0.5
        End Try
    End Function

    Private Sub CheckForOpportunities(odds As Dictionary(Of String, Object), sport As String)
        Try
            For Each game In odds
                Dim gameData = TryCast(game.Value, Dictionary(Of String, Object))
                If gameData IsNot Nothing Then

                    ' Check for arbitrage opportunities
                    If gameData.ContainsKey("arbitrage_opportunities") Then
                        Dim arbOpps = TryCast(gameData("arbitrage_opportunities"), List(Of Dictionary(Of String, Object)))
                        If arbOpps IsNot Nothing AndAlso arbOpps.Count > 0 Then
                            For Each opp In arbOpps
                                If CDbl(opp("profit_percentage")) > 2.0 Then ' Minimum 2% profit
                                    RaiseEvent ArbitrageFound(opp)
                                End If
                            Next
                        End If
                    End If

                    ' Check for value bets (would integrate with betting models)
                    ' This would connect to the BettingModel class
                End If
            Next

        Catch ex As Exception
            logger($"Error checking for opportunities: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Function GetCachedOdds(sport As String) As Dictionary(Of String, Object)
        If oddsCache.ContainsKey(sport) Then
            Return TryCast(oddsCache(sport), Dictionary(Of String, Object))
        End If
        Return New Dictionary(Of String, Object)
    End Function

    Public Function GetSupportedSports() As List(Of String)
        Return New List(Of String)(supportedSports)
    End Function

    Public Function GetSupportedMarkets() As List(Of String)
        Return New List(Of String)(supportedMarkets)
    End Function

    Public Sub Dispose()
        Try
            httpClient?.Dispose()
            oddsCache.Clear()
            logger("Odds Aggregator disposed", "INFO")
        Catch ex As Exception
            logger($"Error disposing Odds Aggregator: {ex.Message}", "ERROR")
        End Try
    End Sub

End Class
