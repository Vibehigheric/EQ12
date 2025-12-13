' ================================================================================
' EQ12 Sports Betting Orchestrator - VB.NET API Client for Python Integration
' ================================================================================
' Purpose: Fetch real-time odds, scores, player stats from multiple sources
'          Feed data to Python betting automation and SQLite databases
' ================================================================================

Imports EQ12.Core.ApiClient
Imports Newtonsoft.Json.Linq
Imports System.Data.SQLite

Module BettingOrchestrator

    Private ReadOnly apiClient As New ApiCatalog()
    Private dbPath As String = "C:\EQ12_BROKEN_20251122_210342\logs\betting_data.db"

    Sub Main(args As String())
        Console.WriteLine("=== EQ12 Sports Betting Data Orchestrator ===")
        Console.WriteLine($"Database: {dbPath}")
        Console.WriteLine()

        ' Initialize SQLite database
        InitializeDatabase()

        If args.Length = 0 Then
            ShowUsage()
            Return
        End If

        ' Parse command
        Dim command = args(0).ToLower()

        Select Case command
            Case "odds"
                FetchOddsData(args)
            Case "scores"
                FetchScores(args)
            Case "stocks"
                FetchStockData(args)
            Case "crypto"
                FetchCryptoData(args)
            Case "flights"
                FetchFlightDeals(args)
            Case "news"
                FetchNews(args)
            Case "all"
                RunFullPipeline()
            Case "test"
                TestAllApis()
            Case Else
                Console.WriteLine($"Unknown command: {command}")
                ShowUsage()
        End Select

    End Sub

    ' ========================================
    ' COMMAND HANDLERS
    ' ========================================

    Sub FetchOddsData(args As String())
        Console.WriteLine("[ODDS] Fetching betting odds...")
        
        Dim sport = If(args.Length > 1, args(1), "upcoming")
        Dim region = If(args.Length > 2, args(2), "us")

        Try
            Dim oddsData = apiClient.GetOddsDataAsync(sport, region).Result
            
            ' Save to database
            SaveOddsToDatabase(oddsData)
            
            ' Export to JSON for Python
            Dim outputPath = "C:\EQ12_BROKEN_20251122_210342\logs\latest_odds.json"
            apiClient.SaveToJson(oddsData, outputPath)
            
            Console.WriteLine($"[SUCCESS] Odds data saved to {outputPath}")
            Console.WriteLine($"[EVENTS] Found {oddsData("length")} betting events")
            
        Catch ex As Exception
            Console.WriteLine($"[ERROR] {ex.Message}")
        End Try
    End Sub

    Sub FetchScores(args As String())
        Console.WriteLine("[SCORES] Fetching live scores...")
        
        Dim sport = If(args.Length > 1, args(1), "football")
        Dim league = If(args.Length > 2, args(2), "nfl")

        Try
            Dim scoresData = apiClient.GetEspnScoresAsync(sport, league).Result
            
            ' Save to JSON
            Dim outputPath = $"C:\EQ12_BROKEN_20251122_210342\logs\{league}_scores.json"
            apiClient.SaveToJson(scoresData, outputPath)
            
            Console.WriteLine($"[SUCCESS] Scores saved to {outputPath}")
            
            ' Display summary
            If scoresData("events") IsNot Nothing Then
                Console.WriteLine($"[GAMES] {scoresData("events").Count()} games in progress")
            End If
            
        Catch ex As Exception
            Console.WriteLine($"[ERROR] {ex.Message}")
        End Try
    End Sub

    Sub FetchStockData(args As String())
        Console.WriteLine("[STOCKS] Fetching stock data...")
        
        Dim symbol = If(args.Length > 1, args(1), "SPY")

        Try
            Dim stockData = apiClient.GetStockDataAsync(symbol).Result
            
            ' Save to database
            SaveStockToDatabase(stockData, symbol)
            
            ' Display quote
            If stockData("Global Quote") IsNot Nothing Then
                Dim quote = stockData("Global Quote")
                Console.WriteLine($"[{symbol}] Price: {quote("05. price")} | Change: {quote("09. change")} ({quote("10. change percent")})")
            End If
            
        Catch ex As Exception
            Console.WriteLine($"[ERROR] {ex.Message}")
        End Try
    End Sub

    Sub FetchCryptoData(args As String())
        Console.WriteLine("[CRYPTO] Fetching cryptocurrency data...")
        
        Dim coinId = If(args.Length > 1, args(1), "bitcoin")

        Try
            Dim cryptoData = apiClient.GetCryptoDataAsync(coinId).Result
            
            ' Save to JSON
            Dim outputPath = $"C:\EQ12_BROKEN_20251122_210342\logs\crypto_{coinId}.json"
            apiClient.SaveToJson(cryptoData, outputPath)
            
            ' Display market data
            If cryptoData("market_data") IsNot Nothing Then
                Dim marketData = cryptoData("market_data")
                Console.WriteLine($"[{coinId.ToUpper()}] Price: ${marketData("current_price")("usd")} | 24h Change: {marketData("price_change_percentage_24h")}%")
            End If
            
        Catch ex As Exception
            Console.WriteLine($"[ERROR] {ex.Message}")
        End Try
    End Sub

    Sub FetchFlightDeals(args As String())
        Console.WriteLine("[FLIGHTS] Fetching flight deals...")
        
        Dim departure = If(args.Length > 1, args(1), "BUF") ' Buffalo
        Dim arrival = If(args.Length > 2, args(2), "LAX")   ' Los Angeles

        Try
            Dim flightData = apiClient.GetFlightDealsAsync(departure, arrival).Result
            
            ' Save to JSON
            Dim outputPath = $"C:\EQ12_BROKEN_20251122_210342\logs\flights_{departure}_{arrival}.json"
            apiClient.SaveToJson(flightData, outputPath)
            
            Console.WriteLine($"[SUCCESS] Flight data saved to {outputPath}")
            Console.WriteLine($"[ROUTES] {departure} → {arrival}")
            
        Catch ex As Exception
            Console.WriteLine($"[ERROR] {ex.Message}")
        End Try
    End Sub

    Sub FetchNews(args As String())
        Console.WriteLine("[NEWS] Fetching latest headlines...")
        
        Dim category = If(args.Length > 1, args(1), "business")
        Dim country = If(args.Length > 2, args(2), "us")

        Try
            Dim newsData = apiClient.GetNewsAsync(category, country).Result
            
            ' Save to JSON
            Dim outputPath = $"C:\EQ12_BROKEN_20251122_210342\logs\news_{category}.json"
            apiClient.SaveToJson(newsData, outputPath)
            
            ' Display headlines
            If newsData("articles") IsNot Nothing Then
                Console.WriteLine($"[HEADLINES] Found {newsData("articles").Count()} articles")
                For Each article In newsData("articles").Take(5)
                    Console.WriteLine($"  • {article("title")}")
                Next
            End If
            
        Catch ex As Exception
            Console.WriteLine($"[ERROR] {ex.Message}")
        End Try
    End Sub

    Sub RunFullPipeline()
        Console.WriteLine("=== RUNNING FULL DATA PIPELINE ===")
        Console.WriteLine()
        
        ' Fetch all data sources
        FetchOddsData({"odds"})
        FetchScores({"scores", "football", "nfl"})
        FetchStockData({"stocks", "SPY"})
        FetchCryptoData({"crypto", "bitcoin"})
        FetchNews({"news", "sports"})
        
        ' Display cache stats
        Console.WriteLine()
        Console.WriteLine("=== CACHE STATISTICS ===")
        Dim cacheStats = apiClient.GetCacheStats()
        Console.WriteLine($"Total cached responses: {cacheStats("total_cached")}")
        Console.WriteLine($"APIs called: {cacheStats("apis_called")}")
    End Sub

    Sub TestAllApis()
        Console.WriteLine("=== TESTING ALL API ENDPOINTS ===")
        Console.WriteLine()

        Dim tests = New List(Of (String, Func(Of Task(Of JObject)))) From {
            ("ESPN Scores", Function() apiClient.GetEspnScoresAsync("football", "nfl")),
            ("Yahoo Finance", Function() apiClient.GetYahooFinanceAsync("AAPL")),
            ("CoinGecko", Function() apiClient.GetCryptoDataAsync("bitcoin")),
            ("OpenSky Flights", Function() apiClient.GetOpenSkyFlightsAsync()),
            ("Reddit Posts", Function() apiClient.GetRedditPostsAsync("investing", 10)),
            ("Exchange Rate", Function() apiClient.GetExchangeRateAsync("USD", "EUR"))
        }

        For Each test In tests
            Try
                Console.Write($"Testing {test.Item1}... ")
                Dim result = test.Item2().Result
                Console.WriteLine("✓ SUCCESS")
            Catch ex As Exception
                Console.WriteLine($"✗ FAILED: {ex.Message}")
            End Try
        Next

        Console.WriteLine()
        Console.WriteLine("=== TEST COMPLETE ===")
    End Sub

    ' ========================================
    ' DATABASE OPERATIONS
    ' ========================================

    Sub InitializeDatabase()
        If Not System.IO.File.Exists(dbPath) Then
            SQLiteConnection.CreateFile(dbPath)
        End If

        Using conn As New SQLiteConnection($"Data Source={dbPath};Version=3;")
            conn.Open()

            ' Odds table
            Dim createOddsTable = "
                CREATE TABLE IF NOT EXISTS odds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sport TEXT,
                    event_id TEXT,
                    home_team TEXT,
                    away_team TEXT,
                    commence_time TEXT,
                    bookmaker TEXT,
                    market TEXT,
                    odds TEXT,
                    fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
                )"

            ' Stocks table
            Dim createStocksTable = "
                CREATE TABLE IF NOT EXISTS stocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    price REAL,
                    change_percent TEXT,
                    volume TEXT,
                    fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
                )"

            Using cmd As New SQLiteCommand(createOddsTable, conn)
                cmd.ExecuteNonQuery()
            End Using

            Using cmd As New SQLiteCommand(createStocksTable, conn)
                cmd.ExecuteNonQuery()
            End Using

            conn.Close()
        End Using

        Console.WriteLine($"[DATABASE] Initialized at {dbPath}")
    End Sub

    Sub SaveOddsToDatabase(oddsData As JObject)
        Using conn As New SQLiteConnection($"Data Source={dbPath};Version=3;")
            conn.Open()

            For Each game In oddsData
                ' Parse JSON and insert into database
                ' (Simplified - full implementation would parse bookmaker odds)
                
                Dim insertSql = "INSERT INTO odds (sport, event_id, home_team, away_team, commence_time) 
                                VALUES (@sport, @event_id, @home_team, @away_team, @commence_time)"
                
                Using cmd As New SQLiteCommand(insertSql, conn)
                    cmd.Parameters.AddWithValue("@sport", "upcoming")
                    cmd.Parameters.AddWithValue("@event_id", Guid.NewGuid().ToString())
                    cmd.Parameters.AddWithValue("@home_team", "TBD")
                    cmd.Parameters.AddWithValue("@away_team", "TBD")
                    cmd.Parameters.AddWithValue("@commence_time", DateTime.UtcNow.ToString("o"))
                    
                    cmd.ExecuteNonQuery()
                End Using
            Next

            conn.Close()
        End Using
    End Sub

    Sub SaveStockToDatabase(stockData As JObject, symbol As String)
        Using conn As New SQLiteConnection($"Data Source={dbPath};Version=3;")
            conn.Open()

            If stockData("Global Quote") IsNot Nothing Then
                Dim quote = stockData("Global Quote")
                
                Dim insertSql = "INSERT INTO stocks (symbol, price, change_percent, volume) 
                                VALUES (@symbol, @price, @change_percent, @volume)"
                
                Using cmd As New SQLiteCommand(insertSql, conn)
                    cmd.Parameters.AddWithValue("@symbol", symbol)
                    cmd.Parameters.AddWithValue("@price", CDbl(quote("05. price")))
                    cmd.Parameters.AddWithValue("@change_percent", quote("10. change percent").ToString())
                    cmd.Parameters.AddWithValue("@volume", quote("06. volume").ToString())
                    
                    cmd.ExecuteNonQuery()
                End Using
            End If

            conn.Close()
        End Using
    End Sub

    ' ========================================
    ' UTILITY
    ' ========================================

    Sub ShowUsage()
        Console.WriteLine("Usage: BettingOrchestrator.exe <command> [options]")
        Console.WriteLine()
        Console.WriteLine("Commands:")
        Console.WriteLine("  odds <sport> <region>     Fetch betting odds (default: upcoming, us)")
        Console.WriteLine("  scores <sport> <league>   Fetch live scores (default: football, nfl)")
        Console.WriteLine("  stocks <symbol>           Fetch stock data (default: SPY)")
        Console.WriteLine("  crypto <coinId>           Fetch crypto data (default: bitcoin)")
        Console.WriteLine("  flights <from> <to>       Fetch flight deals (default: BUF, LAX)")
        Console.WriteLine("  news <category> <country> Fetch news headlines (default: business, us)")
        Console.WriteLine("  all                       Run full data pipeline")
        Console.WriteLine("  test                      Test all API endpoints")
        Console.WriteLine()
        Console.WriteLine("Examples:")
        Console.WriteLine("  BettingOrchestrator.exe odds americanfootball_nfl us")
        Console.WriteLine("  BettingOrchestrator.exe scores basketball nba")
        Console.WriteLine("  BettingOrchestrator.exe stocks TSLA")
        Console.WriteLine("  BettingOrchestrator.exe all")
    End Sub

End Module
