Imports System.Net
Imports System.Text
Imports System.Threading
Imports System.IO
Imports Newtonsoft.Json.Linq
Imports System.Data.SQLite

''' <summary>
''' Local API Server for EQ12 Sports Betting Terminal
''' Provides REST endpoints for accessing bets, arbitrage data, and deliverables
''' </summary>
Public Class LocalApiServer
    Private Shared httpListener As HttpListener
    Private Shared isRunning As Boolean = False
    Private Shared listenerThread As Thread

    ''' <summary>
    ''' Start the API server on specified port
    ''' </summary>
    Public Shared Sub Start(Optional port As Integer = 5057)
        Try
            If isRunning Then
                Console.WriteLine("⚠️ API server is already running")
                Return
            End If

            httpListener = New HttpListener()
            httpListener.Prefixes.Add($"http://localhost:{port}/")
            httpListener.Start()
            isRunning = True

            Console.WriteLine($"🚀 EQ12 API Server started on http://localhost:{port}")

            listenerThread = New Thread(AddressOf HandleRequests)
            listenerThread.IsBackground = True
            listenerThread.Start()

        Catch ex As Exception
            Console.WriteLine($"❌ Failed to start API server: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Stop the API server
    ''' </summary>
    Public Shared Sub [Stop]()
        Try
            If Not isRunning Then Return

            isRunning = False
            httpListener?.Stop()
            httpListener?.Close()
            listenerThread?.Join(5000)

            Console.WriteLine("🛑 EQ12 API Server stopped")
        Catch ex As Exception
            Console.WriteLine($"⚠️ Error stopping API server: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Handle incoming HTTP requests
    ''' </summary>
    Private Shared Sub HandleRequests()
        While isRunning
            Try
                Dim context = httpListener.GetContext()
                Dim request = context.Request
                Dim response = context.Response

                ' Add CORS headers
                response.Headers.Add("Access-Control-Allow-Origin", "*")
                response.Headers.Add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                response.Headers.Add("Access-Control-Allow-Headers", "Content-Type")

                ' Handle preflight requests
                If request.HttpMethod = "OPTIONS" Then
                    response.StatusCode = 200
                    response.Close()
                    Continue While
                End If

                Dim responseText As String = ""
                Dim contentType As String = "application/json"

                ' Route requests
                Select Case request.Url.AbsolutePath.ToLower()
                    Case "/health"
                        responseText = GetHealthStatus()
                    Case "/content/latest"
                        responseText = GetLatestDeliverables()
                    Case "/content/stats"
                        responseText = GetContentStats()
                    Case "/bets/recent"
                        responseText = GetRecentBets()
                    Case "/arbitrage/latest"
                        responseText = GetLatestArbitrage()
                    Case "/bitly/analytics"
                        responseText = GetBitlyAnalytics()
                    Case Else
                        responseText = GetApiInfo()
                End Select

                ' Send response
                Dim buffer = Encoding.UTF8.GetBytes(responseText)
                response.ContentType = contentType
                response.ContentLength64 = buffer.Length
                response.StatusCode = 200
                response.OutputStream.Write(buffer, 0, buffer.Length)
                response.Close()

            Catch ex As Exception
                Console.WriteLine($"⚠️ API request error: {ex.Message}")
            End Try
        End While
    End Sub

    ''' <summary>
    ''' Get latest deliverables (content engine output)
    ''' </summary>
    Private Shared Function GetLatestDeliverables() As String
        Return ContentEngine.GetLatestDeliverables(50).ToString()
    End Function

    ''' <summary>
    ''' Get content generation statistics
    ''' </summary>
    Private Shared Function GetContentStats() As String
        Try
            Dim stats As New JObject()

            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()

                ' Total deliverables by type
                Using cmd As New SQLiteCommand("
                    SELECT kind, COUNT(*) as count
                    FROM deliverables
                    GROUP BY kind
                    ORDER BY count DESC", conn)
                    Using rdr = cmd.ExecuteReader()
                        Dim byType As New JObject()
                        While rdr.Read()
                            byType(rdr("kind").ToString()) = rdr("count")
                        End While
                        stats("by_type") = byType
                    End Using
                End Using

                ' Recent activity (last 30 days)
                Using cmd As New SQLiteCommand("
                    SELECT COUNT(*) as total,
                           COUNT(CASE WHEN ts >= datetime('now', '-7 days') THEN 1 END) as last_week,
                           COUNT(CASE WHEN ts >= datetime('now', '-1 day') THEN 1 END) as last_day
                    FROM deliverables", conn)
                    Using rdr = cmd.ExecuteReader()
                        If rdr.Read() Then
                            stats("total_deliverables") = rdr("total")
                            stats("last_week") = rdr("last_week")
                            stats("last_day") = rdr("last_day")
                        End If
                    End Using
                End Using
            End Using

            Return stats.ToString()

        Catch ex As Exception
            Return New JObject From {{"error", ex.Message}}.ToString()
        End Try
    End Function

    ''' <summary>
    ''' Get recent bets data
    ''' </summary>
    Private Shared Function GetRecentBets() As String
        Try
            Dim bets As New JArray()

            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()
                Using cmd As New SQLiteCommand("
                    SELECT bet_date, sport, market, selection, book, odds, stake, result, profit_loss
                    FROM bets
                    ORDER BY bet_date DESC
                    LIMIT 25", conn)
                    Using rdr = cmd.ExecuteReader()
                        While rdr.Read()
                            bets.Add(New JObject From {
                                {"date", rdr("bet_date").ToString()},
                                {"sport", rdr("sport").ToString()},
                                {"market", rdr("market").ToString()},
                                {"selection", rdr("selection").ToString()},
                                {"book", rdr("book").ToString()},
                                {"odds", rdr("odds")},
                                {"stake", rdr("stake")},
                                {"result", rdr("result").ToString()},
                                {"profit_loss", If(IsDBNull(rdr("profit_loss")), 0, rdr("profit_loss"))}
                            })
                        End While
                    End Using
                End Using
            End Using

            Return bets.ToString()

        Catch ex As Exception
            Return New JArray().ToString()
        End Try
    End Function

    ''' <summary>
    ''' Get latest arbitrage opportunities
    ''' </summary>
    Private Shared Function GetLatestArbitrage() As String
        Try
            Dim arbs As New JArray()

            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()
                Using cmd As New SQLiteCommand("
                    SELECT detected_at, event_id, side_a_selection, side_a_book, side_a_odds,
                           side_b_selection, side_b_book, side_b_odds, profit_percentage, guaranteed_profit
                    FROM arbitrage_opportunities
                    ORDER BY detected_at DESC
                    LIMIT 25", conn)
                    Using rdr = cmd.ExecuteReader()
                        While rdr.Read()
                            arbs.Add(New JObject From {
                                {"detected_at", rdr("detected_at").ToString()},
                                {"event_id", rdr("event_id").ToString()},
                                {"side_a", New JObject From {
                                    {"selection", rdr("side_a_selection").ToString()},
                                    {"book", rdr("side_a_book").ToString()},
                                    {"odds", rdr("side_a_odds")}
                                }},
                                {"side_b", New JObject From {
                                    {"selection", rdr("side_b_selection").ToString()},
                                    {"book", rdr("side_b_book").ToString()},
                                    {"odds", rdr("side_b_odds")}
                                }},
                                {"profit_percentage", rdr("profit_percentage")},
                                {"guaranteed_profit", If(IsDBNull(rdr("guaranteed_profit")), 0, rdr("guaranteed_profit"))}
                            })
                        End While
                    End Using
                End Using
            End Using

            Return arbs.ToString()

        Catch ex As Exception
            Return New JArray().ToString()
        End Try
    End Function

    ''' <summary>
    ''' Get Bitly analytics data
    ''' </summary>
    Private Shared Function GetBitlyAnalytics() As String
        Try
            Dim analytics As New JArray()

            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()
                Using cmd As New SQLiteCommand("
                    SELECT ts, source_type, long_url, short_url, clicks
                    FROM bitly_links
                    ORDER BY ts DESC
                    LIMIT 50", conn)
                    Using rdr = cmd.ExecuteReader()
                        While rdr.Read()
                            analytics.Add(New JObject From {
                                {"ts", rdr("ts").ToString()},
                                {"source_type", rdr("source_type").ToString()},
                                {"long_url", rdr("long_url").ToString()},
                                {"short_url", rdr("short_url").ToString()},
                                {"clicks", rdr("clicks")}
                            })
                        End While
                    End Using
                End Using
            End Using

            Return analytics.ToString()

        Catch ex As Exception
            Return New JArray().ToString()
        End Try
    End Function

    ''' <summary>
    ''' Get API health status
    ''' </summary>
    Private Shared Function GetHealthStatus() As String
        Dim health As New JObject From {
            {"status", "healthy"},
            {"timestamp", DateTime.UtcNow.ToString("o")},
            {"uptime", If(isRunning, "running", "stopped")},
            {"version", "1.0.0"},
            {"endpoints", New JArray From {
                "/health", "/content/latest", "/content/stats",
                "/bets/recent", "/arbitrage/latest", "/bitly/analytics"
            }}
        }
        Return health.ToString()
    End Function

    ''' <summary>
    ''' Get API information
    ''' </summary>
    Private Shared Function GetApiInfo() As String
        Dim info As New JObject From {
            {"name", "EQ12 Sports Betting Terminal API"},
            {"version", "1.0.0"},
            {"description", "REST API for accessing EQ12 data and content deliverables"},
            {"endpoints", New JObject From {
                {"/health", "API health status"},
                {"/content/latest", "Latest content deliverables"},
                {"/content/stats", "Content generation statistics"},
                {"/bets/recent", "Recent betting activity"},
                {"/arbitrage/latest", "Latest arbitrage opportunities"},
                {"/bitly/analytics", "URL shortening analytics"}
            }}
        }
        Return info.ToString()
    End Function
End Class
