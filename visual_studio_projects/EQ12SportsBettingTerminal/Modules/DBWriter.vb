Imports System.Data.SQLite
Imports System.IO
Imports Newtonsoft.Json.Linq

''' <summary>
''' Centralized database operations with event-driven updates and comprehensive error handling
''' </summary>
Public Class DBWriter
    Public Shared Event DbChanged()
    Public Shared Event BetAdded(betId As Integer)
    Public Shared Event ArbitrageDetected(arbId As Integer)
    Public Shared Event LineMovement(eventId As String, market As String, book As String, oldOdds As Integer, newOdds As Integer)

    Private Shared ReadOnly dbPath As String = "Data\bankroll.db"
    Private Shared ReadOnly connectionString As String = $"Data Source={dbPath};Version=3;Pooling=true;Max Pool Size=10;Connection Timeout=30;"

    Shared Sub New()
        ' Ensure database and tables exist on first load
        InitializeDatabase()
    End Sub

    ''' <summary>
    ''' Initialize database and create tables if they don't exist
    ''' </summary>
    Private Shared Sub InitializeDatabase()
        Try
            Dim dataDir = Path.GetDirectoryName(dbPath)
            If Not Directory.Exists(dataDir) Then
                Directory.CreateDirectory(dataDir)
            End If

            If Not File.Exists(dbPath) Then
                SQLiteConnection.CreateFile(dbPath)
            End If

            ' Execute schema if needed
            Dim schemaPath = "Data\schema.sql"
            If File.Exists(schemaPath) Then
                Dim schema = File.ReadAllText(schemaPath)
                ExecuteNonQuery(schema)
            End If
        Catch ex As Exception
            Throw New Exception($"Failed to initialize database: {ex.Message}", ex)
        End Try
    End Sub

    ''' <summary>
    ''' Insert or update event data
    ''' </summary>
    Public Shared Function UpsertEvent(eventId As String, sport As String, league As String, startTs As String, homeTeam As String, awayTeam As String) As Boolean
        Try
            Dim sql = "INSERT OR REPLACE INTO events (event_id, sport, league, start_ts, home_team, away_team, updated_at) VALUES (@id, @sport, @league, @start, @home, @away, datetime('now'))"
            Dim parameters = New Dictionary(Of String, Object) From {
                {"@id", eventId},
                {"@sport", sport},
                {"@league", league},
                {"@start", startTs},
                {"@home", homeTeam},
                {"@away", awayTeam}
            }

            Dim result = ExecuteNonQuery(sql, parameters) > 0
            If result Then RaiseEvent DbChanged()
            Return result
        Catch ex As Exception
            LogError("UpsertEvent", ex, $"EventId: {eventId}")
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Log odds line with duplicate detection and line movement tracking
    ''' </summary>
    Public Shared Function LogLine(ts As String, eventId As String, sport As String, league As String, market As String, selection As String, book As String, odds As Integer, Optional lineValue As Double? = Nothing, Optional source As String = "api") As Boolean
        Try
            ' Check for existing line to detect movement
            Dim existingOdds = GetLatestOdds(eventId, market, selection, book)

            Dim sql = "INSERT OR IGNORE INTO lines (ts, event_id, sport, league, market, selection, book, odds, line_value, source) VALUES (@ts, @event, @sport, @league, @market, @selection, @book, @odds, @line_value, @source)"
            Dim parameters = New Dictionary(Of String, Object) From {
                {"@ts", ts},
                {"@event", eventId},
                {"@sport", sport},
                {"@league", league},
                {"@market", market},
                {"@selection", selection},
                {"@book", book},
                {"@odds", odds},
                {"@line_value", If(lineValue.HasValue, lineValue.Value, DBNull.Value)},
                {"@source", source}
            }

            Dim rowsAffected = ExecuteNonQuery(sql, parameters)

            ' Trigger line movement event if odds changed significantly
            If existingOdds.HasValue AndAlso Math.Abs(existingOdds.Value - odds) >= 10 Then
                RaiseEvent LineMovement(eventId, market, book, existingOdds.Value, odds)
            End If

            If rowsAffected > 0 Then
                RaiseEvent DbChanged()
                Return True
            End If

            Return False
        Catch ex As Exception
            LogError("LogLine", ex, $"Event: {eventId}, Book: {book}")
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Log placed bet with comprehensive metadata
    ''' </summary>
    Public Shared Function LogBet(betDate As String, sport As String, league As String, market As String, eventId As String, selection As String, book As String, odds As Integer, stake As Double, Optional edge As Double? = Nothing, Optional kelly As Double? = Nothing, Optional confidence As Double? = Nothing, Optional source As String = "manual", Optional notes As String = "") As Integer
        Try
            Dim potentialPayout = CalculatePayout(stake, odds)

            Dim sql = "INSERT INTO bets (bet_date, sport, league, market, event_id, selection, book, odds, stake, potential_payout, edge_percentage, kelly_fraction, confidence_score, source, notes) VALUES (@date, @sport, @league, @market, @event, @selection, @book, @odds, @stake, @payout, @edge, @kelly, @confidence, @source, @notes)"
            Dim parameters = New Dictionary(Of String, Object) From {
                {"@date", betDate},
                {"@sport", sport},
                {"@league", league},
                {"@market", market},
                {"@event", eventId},
                {"@selection", selection},
                {"@book", book},
                {"@odds", odds},
                {"@stake", stake},
                {"@payout", potentialPayout},
                {"@edge", If(edge.HasValue, edge.Value, DBNull.Value)},
                {"@kelly", If(kelly.HasValue, kelly.Value, DBNull.Value)},
                {"@confidence", If(confidence.HasValue, confidence.Value, DBNull.Value)},
                {"@source", source},
                {"@notes", notes}
            }

            Dim betId = ExecuteInsertAndGetId(sql, parameters)

            If betId > 0 Then
                RaiseEvent DbChanged()
                RaiseEvent BetAdded(betId)
                UpdateBankrollSnapshot()
            End If

            Return betId
        Catch ex As Exception
            LogError("LogBet", ex, $"Event: {eventId}, Stake: {stake}")
            Return -1
        End Try
    End Function

    ''' <summary>
    ''' Log detected arbitrage opportunity
    ''' </summary>
    Public Shared Function LogArbitrage(eventId As String, sport As String, market As String, sideASelection As String, sideABook As String, sideAOdds As Integer, sideBSelection As String, sideBBook As String, sideBOdds As Integer, profitPct As Double, stakeA As Double, stakeB As Double, guaranteedProfit As Double) As Integer
        Try
            Dim sql = "INSERT INTO arbitrage_opportunities (event_id, sport, market, side_a_selection, side_a_book, side_a_odds, side_b_selection, side_b_book, side_b_odds, profit_percentage, stake_a, stake_b, guaranteed_profit, expires_at) VALUES (@event, @sport, @market, @selA, @bookA, @oddsA, @selB, @bookB, @oddsB, @profit, @stakeA, @stakeB, @guaranteed, datetime('now', '+30 minutes'))"
            Dim parameters = New Dictionary(Of String, Object) From {
                {"@event", eventId},
                {"@sport", sport},
                {"@market", market},
                {"@selA", sideASelection},
                {"@bookA", sideABook},
                {"@oddsA", sideAOdds},
                {"@selB", sideBSelection},
                {"@bookB", sideBBook},
                {"@oddsB", sideBOdds},
                {"@profit", profitPct},
                {"@stakeA", stakeA},
                {"@stakeB", stakeB},
                {"@guaranteed", guaranteedProfit}
            }

            Dim arbId = ExecuteInsertAndGetId(sql, parameters)

            If arbId > 0 Then
                RaiseEvent DbChanged()
                RaiseEvent ArbitrageDetected(arbId)
            End If

            Return arbId
        Catch ex As Exception
            LogError("LogArbitrage", ex, $"Event: {eventId}")
            Return -1
        End Try
    End Function

    ''' <summary>
    ''' Update bet result and calculate profit/loss
    ''' </summary>
    Public Shared Function SettleBet(betId As Integer, result As String, Optional actualPayout As Double = 0) As Boolean
        Try
            Dim sql = "UPDATE bets SET result = @result, actual_payout = @payout, settled_at = datetime('now') WHERE id = @id"
            Dim parameters = New Dictionary(Of String, Object) From {
                {"@result", result},
                {"@payout", actualPayout},
                {"@id", betId}
            }

            Dim success = ExecuteNonQuery(sql, parameters) > 0

            If success Then
                RaiseEvent DbChanged()
                UpdateBankrollSnapshot()
            End If

            Return success
        Catch ex As Exception
            LogError("SettleBet", ex, $"BetId: {betId}")
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Log system alert
    ''' </summary>
    Public Shared Function LogAlert(alertType As String, title As String, message As String, Optional priority As String = "medium", Optional channels As String = "telegram", Optional eventId As String = Nothing, Optional betId As Integer? = Nothing) As Integer
        Try
            Dim sql = "INSERT INTO alert_history (alert_type, title, message, priority, channels, event_id, related_bet_id) VALUES (@type, @title, @msg, @priority, @channels, @event, @bet)"
            Dim parameters = New Dictionary(Of String, Object) From {
                {"@type", alertType},
                {"@title", title},
                {"@msg", message},
                {"@priority", priority},
                {"@channels", channels},
                {"@event", If(String.IsNullOrEmpty(eventId), DBNull.Value, eventId)},
                {"@bet", If(betId.HasValue, betId.Value, DBNull.Value)}
            }

            Return ExecuteInsertAndGetId(sql, parameters)
        Catch ex As Exception
            LogError("LogAlert", ex)
            Return -1
        End Try
    End Function

    ''' <summary>
    ''' Record performance metric
    ''' </summary>
    Public Shared Sub LogPerformanceMetric(metricType As String, metricName As String, value As Double, Optional unit As String = "", Optional source As String = "")
        Try
            Dim sql = "INSERT INTO performance_metrics (metric_type, metric_name, value, unit, source) VALUES (@type, @name, @value, @unit, @source)"
            Dim parameters = New Dictionary(Of String, Object) From {
                {"@type", metricType},
                {"@name", metricName},
                {"@value", value},
                {"@unit", unit},
                {"@source", source}
            }

            ExecuteNonQuery(sql, parameters)
        Catch ex As Exception
            LogError("LogPerformanceMetric", ex)
        End Try
    End Sub

    ''' <summary>
    ''' Get current bankroll balance
    ''' </summary>
    Public Shared Function GetCurrentBankroll() As Double
        Try
            Dim sql = "SELECT ending_balance FROM bankroll_history ORDER BY date DESC LIMIT 1"
            Dim result = ExecuteScalar(sql)

            If result IsNot Nothing AndAlso IsNumeric(result) Then
                Return CDbl(result)
            End If

            ' Fallback to config if no history
            Return GetConfigValue("bankroll_starting", 1000.0)
        Catch ex As Exception
            LogError("GetCurrentBankroll", ex)
            Return 1000.0 ' Default fallback
        End Try
    End Function

    ''' <summary>
    ''' Update daily bankroll snapshot
    ''' </summary>
    Private Shared Sub UpdateBankrollSnapshot()
        Try
            Dim today = DateTime.Now.ToString("yyyy-MM-dd")
            Dim currentBalance = CalculateCurrentBalance()

            Dim sql = "INSERT OR REPLACE INTO bankroll_history (date, starting_balance, ending_balance, total_wagered, total_won, total_lost, net_profit, roi_percentage, win_rate, total_bets, avg_odds, max_win, max_loss) SELECT @date, COALESCE((SELECT ending_balance FROM bankroll_history WHERE date = date(@date, '-1 day')), @current), @current, COALESCE(SUM(stake), 0), COALESCE(SUM(CASE WHEN result = 'Won' THEN actual_payout ELSE 0 END), 0), COALESCE(SUM(CASE WHEN result = 'Lost' THEN stake ELSE 0 END), 0), COALESCE(SUM(profit_loss), 0), CASE WHEN SUM(stake) > 0 THEN ROUND(SUM(profit_loss) / SUM(stake) * 100, 2) ELSE 0 END, CASE WHEN COUNT(CASE WHEN result IN ('Won', 'Lost') THEN 1 END) > 0 THEN ROUND(COUNT(CASE WHEN result = 'Won' THEN 1 END) * 100.0 / COUNT(CASE WHEN result IN ('Won', 'Lost') THEN 1 END), 2) ELSE 0 END, COUNT(*), COALESCE(AVG(odds), 0), COALESCE(MAX(CASE WHEN result = 'Won' THEN profit_loss END), 0), COALESCE(MIN(CASE WHEN result = 'Lost' THEN profit_loss END), 0) FROM bets WHERE bet_date = @date"

            Dim parameters = New Dictionary(Of String, Object) From {
                {"@date", today},
                {"@current", currentBalance}
            }

            ExecuteNonQuery(sql, parameters)
        Catch ex As Exception
            LogError("UpdateBankrollSnapshot", ex)
        End Try
    End Sub

    ''' <summary>
    ''' Calculate current balance including pending bets
    ''' </summary>
    Private Shared Function CalculateCurrentBalance() As Double
        Try
            Dim sql = "SELECT COALESCE(SUM(profit_loss), 0) as total_pl FROM bets WHERE result IN ('Won', 'Lost', 'Push')"
            Dim totalPL = CDbl(ExecuteScalar(sql))
            Dim startingBalance = GetConfigValue("bankroll_starting", 1000.0)

            Return startingBalance + totalPL
        Catch ex As Exception
            LogError("CalculateCurrentBalance", ex)
            Return GetConfigValue("bankroll_starting", 1000.0)
        End Try
    End Function

    ''' <summary>
    ''' Get latest odds for line movement detection
    ''' </summary>
    Private Shared Function GetLatestOdds(eventId As String, market As String, selection As String, book As String) As Integer?
        Try
            Dim sql = "SELECT odds FROM lines WHERE event_id = @event AND market = @market AND selection = @selection AND book = @book ORDER BY ts DESC LIMIT 1"
            Dim parameters = New Dictionary(Of String, Object) From {
                {"@event", eventId},
                {"@market", market},
                {"@selection", selection},
                {"@book", book}
            }

            Dim result = ExecuteScalar(sql, parameters)
            If result IsNot Nothing AndAlso IsNumeric(result) Then
                Return CInt(result)
            End If

            Return Nothing
        Catch ex As Exception
            LogError("GetLatestOdds", ex)
            Return Nothing
        End Try
    End Function

    ''' <summary>
    ''' Calculate potential payout from American odds
    ''' </summary>
    Private Shared Function CalculatePayout(stake As Double, americanOdds As Integer) As Double
        If americanOdds > 0 Then
            Return stake * (americanOdds / 100.0) + stake
        Else
            Return stake * (100.0 / Math.Abs(americanOdds)) + stake
        End If
    End Function

    ''' <summary>
    ''' Log arbitrage opportunity with Kelly Criterion stakes (Legacy method)
    ''' </summary>
    Public Shared Function LogArbitrage(eventId As String, sport As String, market As String,
                                       sideASelection As String, sideABook As String, sideAOdds As Integer,
                                       sideBSelection As String, sideBBook As String, sideBOdds As Integer,
                                       profitPercentage As Double, stakeA As Double, stakeB As Double,
                                       guaranteedProfit As Double) As Integer
        ' Call the comprehensive version with default values
        Return LogArbFull(eventId, sport, market, sideASelection, sideABook, sideAOdds,
                         sideBSelection, sideBBook, sideBOdds, profitPercentage,
                         2500.0, 0.02, 0.25, stakeA, stakeB, 0.0, 0.0,
                         stakeA + stakeB, guaranteedProfit, "hedge", 0.0)
    End Function

    ''' <summary>
    ''' Log arbitrage opportunity with comprehensive Final Form data (all stake modes)
    ''' </summary>
    Public Shared Function LogArbFull(eventId As String, sport As String, market As String,
                                     sideASelection As String, sideABook As String, sideAOdds As Integer,
                                     sideBSelection As String, sideBBook As String, sideBOdds As Integer,
                                     arbPct As Double, bankroll As Double, riskPerArb As Double, kellyFraction As Double,
                                     hedgeA As Double, hedgeB As Double, kellyA As Double, kellyB As Double,
                                     totalStake As Double, lockProfit As Double, mode As String, fixedStake As Double) As Integer
        Try
            Dim sql = "INSERT OR IGNORE INTO arbitrage_opportunities
                      (event_id, sport, market, side_a_selection, side_a_book, side_a_odds,
                       side_b_selection, side_b_book, side_b_odds, profit_percentage,
                       bankroll, risk_per_arb, kelly_fraction,
                       hedge_stakeA, hedge_stakeB, kelly_stakeA, kelly_stakeB,
                       total_stake, guaranteed_profit, mode, fixed_stake, status, detected_at)
                      VALUES (@event_id, @sport, @market, @side_a_sel, @side_a_book, @side_a_odds,
                              @side_b_sel, @side_b_book, @side_b_odds, @arb_pct,
                              @bankroll, @risk_per_arb, @kelly_fraction,
                              @hedge_a, @hedge_b, @kelly_a, @kelly_b,
                              @total_stake, @lock_profit, @mode, @fixed_stake, 'detected', datetime('now'))"

            Dim parameters As New Dictionary(Of String, Object) From {
                {"@event_id", eventId},
                {"@sport", sport},
                {"@market", market},
                {"@side_a_sel", sideASelection},
                {"@side_a_book", sideABook},
                {"@side_a_odds", sideAOdds},
                {"@side_b_sel", sideBSelection},
                {"@side_b_book", sideBBook},
                {"@side_b_odds", sideBOdds},
                {"@arb_pct", arbPct},
                {"@bankroll", bankroll},
                {"@risk_per_arb", riskPerArb},
                {"@kelly_fraction", kellyFraction},
                {"@hedge_a", hedgeA},
                {"@hedge_b", hedgeB},
                {"@kelly_a", kellyA},
                {"@kelly_b", kellyB},
                {"@total_stake", totalStake},
                {"@lock_profit", lockProfit},
                {"@mode", mode},
                {"@fixed_stake", fixedStake}
            }

            Dim arbId = ExecuteInsertAndGetId(sql, parameters)

            ' Raise events for real-time updates
            RaiseEvent ArbitrageDetected(arbId)
            RaiseEvent DbChanged()

            ' Log performance metric
            LogPerformanceMetric("arbitrage_detected", "LogArbFull", 1, "count", eventId)

            Return arbId

        Catch ex As Exception
            LogError("LogArbFull", ex, $"Event: {eventId}, Profit: {arbPct}%, Mode: {mode}")
            Return -1
        End Try
    End Function

    ''' <summary>
    ''' Get configuration value with type conversion
    ''' </summary>
    Public Shared Function GetConfigValue(Of T)(key As String, defaultValue As T) As T
        Try
            Dim sql = "SELECT value, data_type FROM system_config WHERE key = @key"
            Using conn As New SQLiteConnection(connectionString)
                conn.Open()
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@key", key)
                    Using reader = cmd.ExecuteReader()
                        If reader.Read() Then
                            Dim value = reader("value").ToString()
                            Dim dataType = reader("data_type").ToString()

                            Select Case dataType.ToLower()
                                Case "integer"
                                    Return CType(CObj(Integer.Parse(value)), T)
                                Case "float"
                                    Return CType(CObj(Double.Parse(value)), T)
                                Case "boolean"
                                    Return CType(CObj(Boolean.Parse(value)), T)
                                Case "json"
                                    Return CType(CObj(JObject.Parse(value)), T)
                                Case Else
                                    Return CType(CObj(value), T)
                            End Select
                        End If
                    End Using
                End Using
            End Using
        Catch ex As Exception
            LogError("GetConfigValue", ex, $"Key: {key}")
        End Try

        Return defaultValue
    End Function

    ''' <summary>
    ''' Execute non-query SQL with parameters
    ''' </summary>
    Private Shared Function ExecuteNonQuery(sql As String, Optional parameters As Dictionary(Of String, Object) = Nothing) As Integer
        Using conn As New SQLiteConnection(connectionString)
            conn.Open()
            Using cmd As New SQLiteCommand(sql, conn)
                If parameters IsNot Nothing Then
                    For Each param In parameters
                        cmd.Parameters.AddWithValue(param.Key, param.Value)
                    Next
                End If
                Return cmd.ExecuteNonQuery()
            End Using
        End Using
    End Function

    ''' <summary>
    ''' Execute INSERT and return new ID
    ''' </summary>
    Private Shared Function ExecuteInsertAndGetId(sql As String, Optional parameters As Dictionary(Of String, Object) = Nothing) As Integer
        Using conn As New SQLiteConnection(connectionString)
            conn.Open()
            Using cmd As New SQLiteCommand(sql, conn)
                If parameters IsNot Nothing Then
                    For Each param In parameters
                        cmd.Parameters.AddWithValue(param.Key, param.Value)
                    Next
                End If
                cmd.ExecuteNonQuery()
                cmd.CommandText = "SELECT last_insert_rowid()"
                Return CInt(cmd.ExecuteScalar())
            End Using
        End Using
    End Function

    ''' <summary>
    ''' Execute scalar query with parameters
    ''' </summary>
    Private Shared Function ExecuteScalar(sql As String, Optional parameters As Dictionary(Of String, Object) = Nothing) As Object
        Using conn As New SQLiteConnection(connectionString)
            conn.Open()
            Using cmd As New SQLiteCommand(sql, conn)
                If parameters IsNot Nothing Then
                    For Each param In parameters
                        cmd.Parameters.AddWithValue(param.Key, param.Value)
                    Next
                End If
                Return cmd.ExecuteScalar()
            End Using
        End Using
    End Function

    ''' <summary>
    ''' Log error to performance metrics table
    ''' </summary>
    Private Shared Sub LogError(methodName As String, ex As Exception, Optional context As String = "")
        Try
            Console.WriteLine($"DBWriter Error in {methodName}: {ex.Message}")
            If Not String.IsNullOrEmpty(context) Then
                Console.WriteLine($"Context: {context}")
            End If

            ' Log to performance metrics for monitoring
            LogPerformanceMetric("error", methodName, 1, "count", "DBWriter")
        Catch
            ' Avoid recursive errors
        End Try
    End Sub

    ''' <summary>
    ''' Log Bitly URL shortening for analytics tracking
    ''' </summary>
    ''' <param name="sourceType">Type of source (deliverable, report, alert)</param>
    ''' <param name="longUrl">Original long URL</param>
    ''' <param name="shortUrl">Shortened Bitly URL</param>
    Public Shared Function LogBitly(sourceType As String, longUrl As String, shortUrl As String) As Boolean
        Try
            Dim sql = "INSERT INTO bitly_links (source_type, long_url, short_url) VALUES (@type, @long, @short)"
            Using conn As New SQLiteConnection(connectionString)
                conn.Open()
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@type", sourceType)
                    cmd.Parameters.AddWithValue("@long", longUrl)
                    cmd.Parameters.AddWithValue("@short", shortUrl)
                    cmd.ExecuteNonQuery()
                End Using
            End Using
            Return True
        Catch ex As Exception
            LogError("LogBitly", ex)
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Log Bitly analytics statistics from API
    ''' </summary>
    Public Shared Function LogBitlyStats(linkId As String, clicks As Integer, country As String, referrer As String, Optional platform As String = "") As Boolean
        Try
            Dim sql = "INSERT INTO bitly_stats (link_id, clicks, country, referrer, platform) VALUES (@linkId, @clicks, @country, @referrer, @platform)"
            Using conn As New SQLiteConnection(connectionString)
                conn.Open()
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@linkId", linkId)
                    cmd.Parameters.AddWithValue("@clicks", clicks)
                    cmd.Parameters.AddWithValue("@country", If(String.IsNullOrEmpty(country), "unknown", country))
                    cmd.Parameters.AddWithValue("@referrer", If(String.IsNullOrEmpty(referrer), "direct", referrer))
                    cmd.Parameters.AddWithValue("@platform", If(String.IsNullOrEmpty(platform), "unknown", platform))
                    cmd.ExecuteNonQuery()
                End Using
            End Using
            Return True
        Catch ex As Exception
            LogError("LogBitlyStats", ex)
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Log link safety check results for cybersecurity tracking
    ''' </summary>
    Public Shared Function LogLinkCheck(shortUrl As String, resolvedUrl As String, verdict As String, Optional riskFactors As String = "", Optional senderContext As String = "") As Boolean
        Try
            Dim sql = "INSERT INTO link_safety_checks (short_url, resolved_url, verdict, risk_factors, sender_context) VALUES (@short, @resolved, @verdict, @risks, @sender)"
            Using conn As New SQLiteConnection(connectionString)
                conn.Open()
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@short", shortUrl)
                    cmd.Parameters.AddWithValue("@resolved", If(String.IsNullOrEmpty(resolvedUrl), "unknown", resolvedUrl))
                    cmd.Parameters.AddWithValue("@verdict", verdict)
                    cmd.Parameters.AddWithValue("@risks", If(String.IsNullOrEmpty(riskFactors), "[]", riskFactors))
                    cmd.Parameters.AddWithValue("@sender", If(String.IsNullOrEmpty(senderContext), "unknown", senderContext))
                    cmd.ExecuteNonQuery()
                End Using
            End Using
            Return True
        Catch ex As Exception
            LogError("LogLinkCheck", ex)
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Log integration events for GitHub, X API, and other system integrations
    ''' </summary>
    Public Shared Function LogIntegration(module As String, source As String, details As String, action As String, status As String, Optional metadata As String = "") As Boolean
        Try
            Dim sql = "INSERT INTO integration_log (module, source, details, action, status, metadata, timestamp) VALUES (@module, @source, @details, @action, @status, @metadata, @timestamp)"
            Using conn As New SQLiteConnection(connectionString)
                conn.Open()

                ' Create integration_log table if it doesn't exist
                Dim createTableSql = "CREATE TABLE IF NOT EXISTS integration_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module TEXT NOT NULL,
                    source TEXT NOT NULL,
                    details TEXT,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )"
                Using createCmd As New SQLiteCommand(createTableSql, conn)
                    createCmd.ExecuteNonQuery()
                End Using

                ' Insert integration log entry
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@module", If(String.IsNullOrEmpty(module), "unknown", module))
                    cmd.Parameters.AddWithValue("@source", If(String.IsNullOrEmpty(source), "unknown", source))
                    cmd.Parameters.AddWithValue("@details", If(String.IsNullOrEmpty(details), "", details))
                    cmd.Parameters.AddWithValue("@action", If(String.IsNullOrEmpty(action), "unknown", action))
                    cmd.Parameters.AddWithValue("@status", If(String.IsNullOrEmpty(status), "unknown", status))
                    cmd.Parameters.AddWithValue("@metadata", If(String.IsNullOrEmpty(metadata), "{}", metadata))
                    cmd.Parameters.AddWithValue("@timestamp", DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss"))
                    cmd.ExecuteNonQuery()
                End Using
            End Using
            Return True
        Catch ex As Exception
            LogError("LogIntegration", ex)
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Log X/Twitter API specific operations with enhanced tracking
    ''' </summary>
    Public Shared Function LogXApiOperation(operation As String, endpoint As String, success As Boolean, responseMetadata As String, Optional engagementData As String = "") As Boolean
        Try
            Dim sql = "INSERT INTO x_api_operations_log (operation, endpoint, success, response_metadata, engagement_data, timestamp) VALUES (@operation, @endpoint, @success, @response_metadata, @engagement_data, @timestamp)"
            Using conn As New SQLiteConnection(connectionString)
                conn.Open()

                ' Create x_api_operations_log table if it doesn't exist
                Dim createTableSql = "CREATE TABLE IF NOT EXISTS x_api_operations_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    response_metadata TEXT,
                    engagement_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )"
                Using createCmd As New SQLiteCommand(createTableSql, conn)
                    createCmd.ExecuteNonQuery()
                End Using

                ' Insert X API operation log entry
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@operation", operation)
                    cmd.Parameters.AddWithValue("@endpoint", endpoint)
                    cmd.Parameters.AddWithValue("@success", success)
                    cmd.Parameters.AddWithValue("@response_metadata", If(String.IsNullOrEmpty(responseMetadata), "{}", responseMetadata))
                    cmd.Parameters.AddWithValue("@engagement_data", If(String.IsNullOrEmpty(engagementData), "{}", engagementData))
                    cmd.Parameters.AddWithValue("@timestamp", DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss"))
                    cmd.ExecuteNonQuery()
                End Using
            End Using
            Return True
        Catch ex As Exception
            LogError("LogXApiOperation", ex)
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Log repository analysis and classification results
    ''' </summary>
    Public Shared Function LogRepositoryAnalysis(repoFullName As String, category As String, analysisScore As Double, monetizationPotential As Double, extractedPatterns As String) As Boolean
        Try
            Dim sql = "INSERT OR REPLACE INTO repo_analysis_cache (repo_full_name, category, analysis_score, monetization_potential, extracted_patterns, last_analyzed) VALUES (@repo, @category, @score, @monetization, @patterns, @timestamp)"
            Using conn As New SQLiteConnection(connectionString)
                conn.Open()

                ' Create repo_analysis_cache table if it doesn't exist
                Dim createTableSql = "CREATE TABLE IF NOT EXISTS repo_analysis_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo_full_name TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    analysis_score REAL NOT NULL,
                    monetization_potential REAL NOT NULL,
                    extracted_patterns TEXT,
                    last_analyzed DATETIME DEFAULT CURRENT_TIMESTAMP
                )"
                Using createCmd As New SQLiteCommand(createTableSql, conn)
                    createCmd.ExecuteNonQuery()
                End Using

                ' Insert repository analysis entry
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@repo", repoFullName)
                    cmd.Parameters.AddWithValue("@category", category)
                    cmd.Parameters.AddWithValue("@score", analysisScore)
                    cmd.Parameters.AddWithValue("@monetization", monetizationPotential)
                    cmd.Parameters.AddWithValue("@patterns", If(String.IsNullOrEmpty(extractedPatterns), "[]", extractedPatterns))
                    cmd.Parameters.AddWithValue("@timestamp", DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss"))
                    cmd.ExecuteNonQuery()
                End Using
            End Using
            Return True
        Catch ex As Exception
            LogError("LogRepositoryAnalysis", ex)
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Log X/Twitter actions with SQLite + BigQuery sync integration
    ''' </summary>
    Public Shared Sub LogXAction(action As String, refId As String, payload As String, cnt As Integer, status As String, details As String, Optional metadata As String = "{}")
        Try
            ' SQLite logging
            Using conn As New SQLiteConnection(connectionString)
                conn.Open()

                ' Ensure x_actions table exists
                Dim createTableSql = "CREATE TABLE IF NOT EXISTS x_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT DEFAULT (datetime('now')),
                    action TEXT NOT NULL,
                    ref_id TEXT,
                    payload TEXT,
                    count INTEGER DEFAULT 0,
                    status TEXT NOT NULL,
                    details TEXT,
                    metadata TEXT
                )"
                Using createCmd As New SQLiteCommand(createTableSql, conn)
                    createCmd.ExecuteNonQuery()
                End Using

                ' Insert X action log
                Dim sql = "INSERT INTO x_actions (action, ref_id, payload, count, status, details, metadata) VALUES (@a, @r, @p, @c, @s, @d, @m)"
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@a", If(String.IsNullOrEmpty(action), "unknown", action))
                    cmd.Parameters.AddWithValue("@r", If(String.IsNullOrEmpty(refId), "", refId))
                    cmd.Parameters.AddWithValue("@p", If(String.IsNullOrEmpty(payload), "", payload))
                    cmd.Parameters.AddWithValue("@c", cnt)
                    cmd.Parameters.AddWithValue("@s", If(String.IsNullOrEmpty(status), "unknown", status))
                    cmd.Parameters.AddWithValue("@d", If(String.IsNullOrEmpty(details), "", details))
                    cmd.Parameters.AddWithValue("@m", If(String.IsNullOrEmpty(metadata), "{}", metadata))
                    cmd.ExecuteNonQuery()
                End Using
            End Using

            ' BigQuery sync (if available)
            Try
                Dim dt As New DataTable()
                dt.Columns.Add("ts", GetType(DateTime))
                dt.Columns.Add("action", GetType(String))
                dt.Columns.Add("ref_id", GetType(String))
                dt.Columns.Add("payload", GetType(String))
                dt.Columns.Add("count", GetType(Integer))
                dt.Columns.Add("status", GetType(String))
                dt.Columns.Add("details", GetType(String))
                dt.Columns.Add("metadata", GetType(String))

                dt.Rows.Add(DateTime.UtcNow, action, refId, payload, cnt, status, details, metadata)

                ' Attempt BigQuery sync (non-blocking)
                Task.Run(Sub()
                    Try
                        If BigQueryClientEx.Singleton IsNot Nothing Then
                            BigQueryClientEx.Singleton.UpsertFromDataTable("x_actions", dt)
                        End If
                    Catch
                        ' Silent fail for BigQuery sync - not critical
                    End Try
                End Sub)
            Catch
                ' Silent fail for BigQuery setup - not critical
            End Try

        Catch ex As Exception
            LogError("LogXAction", ex)
        End Try
    End Sub

    ''' <summary>
    ''' Log X/Twitter monetization tracking with ROI calculations
    ''' </summary>
    Public Shared Function LogXMonetization(actionType As String, refId As String, revenueGenerated As Double, affiliateClicks As Integer, conversionRate As Double, cost As Double, bitlyUrl As String, source As String) As Boolean
        Try
            Using conn As New SQLiteConnection(connectionString)
                conn.Open()

                ' Ensure x_monetization_tracking table exists
                Dim createTableSql = "CREATE TABLE IF NOT EXISTS x_monetization_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_date TEXT DEFAULT (datetime('now')),
                    action_type TEXT NOT NULL,
                    ref_id TEXT,
                    revenue_generated REAL DEFAULT 0.0,
                    affiliate_clicks INTEGER DEFAULT 0,
                    conversion_rate REAL DEFAULT 0.0,
                    cost REAL DEFAULT 0.0,
                    roi REAL DEFAULT 0.0,
                    bitly_url TEXT,
                    source TEXT
                )"
                Using createCmd As New SQLiteCommand(createTableSql, conn)
                    createCmd.ExecuteNonQuery()
                End Using

                ' Calculate ROI
                Dim roi = If(cost > 0, ((revenueGenerated - cost) / cost) * 100, 0.0)

                ' Insert monetization tracking
                Dim sql = "INSERT INTO x_monetization_tracking (action_type, ref_id, revenue_generated, affiliate_clicks, conversion_rate, cost, roi, bitly_url, source) VALUES (@type, @ref, @revenue, @clicks, @conversion, @cost, @roi, @bitly, @source)"
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@type", actionType)
                    cmd.Parameters.AddWithValue("@ref", If(String.IsNullOrEmpty(refId), "", refId))
                    cmd.Parameters.AddWithValue("@revenue", revenueGenerated)
                    cmd.Parameters.AddWithValue("@clicks", affiliateClicks)
                    cmd.Parameters.AddWithValue("@conversion", conversionRate)
                    cmd.Parameters.AddWithValue("@cost", cost)
                    cmd.Parameters.AddWithValue("@roi", roi)
                    cmd.Parameters.AddWithValue("@bitly", If(String.IsNullOrEmpty(bitlyUrl), "", bitlyUrl))
                    cmd.Parameters.AddWithValue("@source", If(String.IsNullOrEmpty(source), "unknown", source))
                    cmd.ExecuteNonQuery()
                End Using
            End Using
            Return True
        Catch ex As Exception
            LogError("LogXMonetization", ex)
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Log deliverable generation for tracking reports and content
    ''' </summary>
    Public Shared Function LogDeliverable(kind As String, title As String, bitlyUrl As String, gistUrl As String, window As String, filePath As String, Optional metadata As String = "{}") As Boolean
        Try
            Using conn As New SQLiteConnection(connectionString)
                conn.Open()

                ' Ensure deliverables table exists
                Dim createTableSql = "CREATE TABLE IF NOT EXISTS deliverables (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT DEFAULT (datetime('now')),
                    kind TEXT NOT NULL,
                    title TEXT NOT NULL,
                    bitly_url TEXT,
                    gist_url TEXT,
                    window TEXT,
                    file_path TEXT,
                    metadata TEXT
                )"
                Using createCmd As New SQLiteCommand(createTableSql, conn)
                    createCmd.ExecuteNonQuery()
                End Using

                ' Insert deliverable log
                Dim sql = "INSERT INTO deliverables (kind, title, bitly_url, gist_url, window, file_path, metadata) VALUES (@kind, @title, @bitly, @gist, @window, @path, @metadata)"
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@kind", kind)
                    cmd.Parameters.AddWithValue("@title", title)
                    cmd.Parameters.AddWithValue("@bitly", If(String.IsNullOrEmpty(bitlyUrl), "", bitlyUrl))
                    cmd.Parameters.AddWithValue("@gist", If(String.IsNullOrEmpty(gistUrl), "", gistUrl))
                    cmd.Parameters.AddWithValue("@window", If(String.IsNullOrEmpty(window), "", window))
                    cmd.Parameters.AddWithValue("@path", If(String.IsNullOrEmpty(filePath), "", filePath))
                    cmd.Parameters.AddWithValue("@metadata", If(String.IsNullOrEmpty(metadata), "{}", metadata))
                    cmd.ExecuteNonQuery()
                End Using
            End Using
            Return True
        Catch ex As Exception
            LogError("LogDeliverable", ex)
            Return False
        End Try
    End Function
End Class
