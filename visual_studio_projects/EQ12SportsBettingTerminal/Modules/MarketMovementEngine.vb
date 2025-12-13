Imports System.Threading.Tasks
Imports System.Data
Imports System.Data.SQLite
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.Collections.Generic

''' <summary>
''' Market Movement Engine for EQ12 - Beating the Public System
''' Detects reverse line moves, steam moves, and sharp vs public money indicators
''' Feeds monetization content and sharp betting edge identification
''' </summary>
Public Class MarketMovementEngine
    Private ReadOnly _dbPath As String
    Private ReadOnly _config As JObject

    ' Thresholds for market movement detection
    Public Shared ReadOnly REVERSE_LINE_MOVE_THRESHOLD As Double = 0.5 ' Points/percentage
    Public Shared ReadOnly PUBLIC_PERCENTAGE_THRESHOLD As Double = 60.0 ' % of public bets
    Public Shared ReadOnly STEAM_MOVE_THRESHOLD As Double = 1.0 ' Minimum line movement for steam
    Public Shared ReadOnly STEAM_TIME_WINDOW As Integer = 30 ' Minutes for steam detection

    ' Book weights for consensus calculations
    Public Shared ReadOnly SPORTSBOOK_WEIGHTS As Dictionary(Of String, Double) = New Dictionary(Of String, Double) From {
        {"pinnacle", 0.25}, {"bet365", 0.20}, {"draftkings", 0.15}, {"fanduel", 0.15},
        {"caesars", 0.10}, {"betmgm", 0.10}, {"pointsbet", 0.05}
    }

    Public Sub New(Optional dbPath As String = "", Optional config As JObject = Nothing)
        _dbPath = If(String.IsNullOrEmpty(dbPath), "Data/eq12_terminal.db", dbPath)
        _config = config

        ' Initialize market movement tables
        InitializeMarketTables()
    End Sub

    ''' <summary>
    ''' Log market snapshot with public betting percentages and line data
    ''' </summary>
    ''' <param name="sport">Sport identifier</param>
    ''' <param name="eventId">Unique event identifier</param>
    ''' <param name="side">Betting side (team name, over/under, etc.)</param>
    ''' <param name="book">Sportsbook name</param>
    ''' <param name="odds">Current odds (American format)</param>
    ''' <param name="publicPct">Percentage of public tickets (if available)</param>
    ''' <param name="handlePct">Percentage of handle (if available)</param>
    ''' <param name="consensus">Consensus line calculation</param>
    Public Sub LogSnapshot(sport As String, eventId As String, side As String, book As String,
                          odds As Integer, Optional publicPct As Double? = Nothing,
                          Optional handlePct As Double? = Nothing, Optional consensus As Double? = Nothing)
        Try
            If String.IsNullOrEmpty(sport) Or String.IsNullOrEmpty(eventId) Or String.IsNullOrEmpty(side) Then
                Throw New ArgumentException("Invalid input parameters")
            End If

            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand("
                    INSERT INTO market_snapshots (ts, sport, event_id, side, book, odds, public_pct, handle_pct, consensus_line)
                    VALUES (datetime('now'), @sport, @event_id, @side, @book, @odds, @public_pct, @handle_pct, @consensus)", conn)

                    cmd.Parameters.AddWithValue("@sport", sport.ToUpper())
                    cmd.Parameters.AddWithValue("@event_id", eventId)
                    cmd.Parameters.AddWithValue("@side", side)
                    cmd.Parameters.AddWithValue("@book", book.ToLower())
                    cmd.Parameters.AddWithValue("@odds", odds)
                    cmd.Parameters.AddWithValue("@public_pct", If(publicPct, DBNull.Value))
                    cmd.Parameters.AddWithValue("@handle_pct", If(handlePct, DBNull.Value))
                    cmd.Parameters.AddWithValue("@consensus", If(consensus, DBNull.Value))

                    cmd.ExecuteNonQuery()
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"❌ Market snapshot logging failed: {ex.Message}")
            LogError("LogSnapshot", ex.Message, $"{sport}_{eventId}_{side}")
        End Try
    End Sub

    ''' <summary>
    ''' Detect reverse line movement (public on one side, line moves opposite direction)
    ''' </summary>
    ''' <param name="eventId">Event to analyze</param>
    ''' <param name="side">Side to check for reverse movement</param>
    ''' <param name="lookbackHours">Hours to look back for line movement</param>
    ''' <returns>Tuple of (detected, magnitude, description)</returns>
    Public Function DetectReverseLineMove(eventId As String, side As String, Optional lookbackHours As Integer = 12) As (Boolean, Double, String)
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                ' Get latest public percentage and line movement
                Using cmd As New SQLiteCommand($"
                    WITH latest_public AS (
                        SELECT public_pct, consensus_line
                        FROM market_snapshots
                        WHERE event_id = @event_id AND side = @side
                        AND public_pct IS NOT NULL
                        AND ts >= datetime('now', '-{lookbackHours} hours')
                        ORDER BY ts DESC
                        LIMIT 1
                    ),
                    line_movement AS (
                        SELECT
                            MIN(consensus_line) as open_line,
                            MAX(consensus_line) as current_line
                        FROM market_snapshots
                        WHERE event_id = @event_id AND side = @side
                        AND consensus_line IS NOT NULL
                        AND ts >= datetime('now', '-{lookbackHours} hours')
                    )
                    SELECT
                        lp.public_pct,
                        lm.open_line,
                        lm.current_line,
                        (lm.current_line - lm.open_line) as line_move
                    FROM latest_public lp
                    CROSS JOIN line_movement lm", conn)

                    cmd.Parameters.AddWithValue("@event_id", eventId)
                    cmd.Parameters.AddWithValue("@side", side)

                    Using reader = cmd.ExecuteReader()
                        If reader.Read() Then
                            Dim publicPct = If(reader("public_pct") IsNot DBNull.Value, Convert.ToDouble(reader("public_pct")), 0)
                            Dim openLine = If(reader("open_line") IsNot DBNull.Value, Convert.ToDouble(reader("open_line")), 0)
                            Dim currentLine = If(reader("current_line") IsNot DBNull.Value, Convert.ToDouble(reader("current_line")), 0)
                            Dim lineMove = If(reader("line_move") IsNot DBNull.Value, Convert.ToDouble(reader("line_move")), 0)

                            ' Detect reverse line move
                            Dim isReverseMove = False
                            Dim description = ""

                            If publicPct >= PUBLIC_PERCENTAGE_THRESHOLD AndAlso Math.Abs(lineMove) >= REVERSE_LINE_MOVE_THRESHOLD Then
                                ' Public heavily on this side, but check if line moved against them
                                If (publicPct >= 60 AndAlso lineMove < -REVERSE_LINE_MOVE_THRESHOLD) Then
                                    isReverseMove = True
                                    description = $"Public {publicPct:F1}% on {side}, but line moved {Math.Abs(lineMove):F1} points AGAINST public"
                                ElseIf (publicPct <= 40 AndAlso lineMove > REVERSE_LINE_MOVE_THRESHOLD) Then
                                    isReverseMove = True
                                    description = $"Public only {publicPct:F1}% on {side}, line moved {lineMove:F1} points WITH the public (sharp money opposite)"
                                End If
                            End If

                            If isReverseMove Then
                                ' Log the reverse move detection
                                LogMarketMove(eventId, side, openLine, currentLine, lineMove, "reverse line move vs public")
                            End If

                            Return (isReverseMove, Math.Abs(lineMove), description)
                        End If
                    End Using
                End Using
            End Using

            Return (False, 0, "No reverse line move detected")

        Catch ex As Exception
            Console.WriteLine($"❌ Reverse line move detection failed: {ex.Message}")
            LogError("DetectReverseLineMove", ex.Message, $"{eventId}_{side}")
            Return (False, 0, "Detection failed")
        End Try
    End Function

    ''' <summary>
    ''' Detect steam moves (multiple books moving lines in same direction quickly)
    ''' </summary>
    ''' <param name="eventId">Event to analyze</param>
    ''' <param name="side">Side to check for steam</param>
    ''' <returns>Tuple of (detected, magnitude, description)</returns>
    Public Function SteamMove(eventId As String, side As String) As (Boolean, Double, String)
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                ' Get recent line movements across multiple books
                Using cmd As New SQLiteCommand($"
                    WITH book_moves AS (
                        SELECT
                            book,
                            MIN(consensus_line) as open_line,
                            MAX(consensus_line) as current_line,
                            (MAX(consensus_line) - MIN(consensus_line)) as move,
                            COUNT(*) as snapshots
                        FROM market_snapshots
                        WHERE event_id = @event_id AND side = @side
                        AND consensus_line IS NOT NULL
                        AND ts >= datetime('now', '-{STEAM_TIME_WINDOW} minutes')
                        GROUP BY book
                        HAVING snapshots >= 2
                    )
                    SELECT
                        COUNT(*) as books_moving,
                        AVG(ABS(move)) as avg_move,
                        SUM(CASE WHEN move > 0 THEN 1 ELSE 0 END) as books_up,
                        SUM(CASE WHEN move < 0 THEN 1 ELSE 0 END) as books_down,
                        MAX(ABS(move)) as max_move
                    FROM book_moves
                    WHERE ABS(move) >= {STEAM_MOVE_THRESHOLD}", conn)

                    cmd.Parameters.AddWithValue("@event_id", eventId)
                    cmd.Parameters.AddWithValue("@side", side)

                    Using reader = cmd.ExecuteReader()
                        If reader.Read() Then
                            Dim booksMoving = Convert.ToInt32(reader("books_moving"))
                            Dim avgMove = If(reader("avg_move") IsNot DBNull.Value, Convert.ToDouble(reader("avg_move")), 0)
                            Dim booksUp = Convert.ToInt32(reader("books_up"))
                            Dim booksDown = Convert.ToInt32(reader("books_down"))
                            Dim maxMove = If(reader("max_move") IsNot DBNull.Value, Convert.ToDouble(reader("max_move")), 0)

                            ' Detect steam (3+ books moving same direction with significant movement)
                            Dim isSteam = False
                            Dim direction = ""
                            Dim description = ""

                            If booksMoving >= 3 AndAlso avgMove >= STEAM_MOVE_THRESHOLD Then
                                If booksUp > booksDown AndAlso booksUp >= 3 Then
                                    isSteam = True
                                    direction = "UP"
                                    description = $"STEAM MOVE: {booksUp} books moved line UP avg {avgMove:F1} pts in {STEAM_TIME_WINDOW}min"
                                ElseIf booksDown > booksUp AndAlso booksDown >= 3 Then
                                    isSteam = True
                                    direction = "DOWN"
                                    description = $"STEAM MOVE: {booksDown} books moved line DOWN avg {avgMove:F1} pts in {STEAM_TIME_WINDOW}min"
                                End If
                            End If

                            If isSteam Then
                                ' Log the steam move
                                Dim currentLine = GetCurrentConsensusLine(eventId, side)
                                Dim openLine = currentLine - (If(direction = "UP", avgMove, -avgMove))
                                LogMarketMove(eventId, side, openLine, currentLine, If(direction = "UP", avgMove, -avgMove), $"steam on {side}")
                            End If

                            Return (isSteam, avgMove, description)
                        End If
                    End Using
                End Using
            End Using

            Return (False, 0, "No steam move detected")

        Catch ex As Exception
            Console.WriteLine($"❌ Steam move detection failed: {ex.Message}")
            LogError("SteamMove", ex.Message, $"{eventId}_{side}")
            Return (False, 0, "Detection failed")
        End Try
    End Function

    ''' <summary>
    ''' Generate monetization-ready market movement narrative
    ''' </summary>
    ''' <param name="eventId">Event to analyze</param>
    ''' <param name="includePublicData">Include public betting percentages</param>
    ''' <returns>Marketing-ready narrative text</returns>
    Public Function MarketNarrative(eventId As String, Optional includePublicData As Boolean = True) As String
        Try
            Dim narrative As New Text.StringBuilder()

            ' Get all sides for this event
            Dim sides = GetEventSides(eventId)

            If sides.Count = 0 Then
                Return "No market movement data available for this event."
            End If

            narrative.AppendLine($"📈 **MARKET MOVEMENT ANALYSIS**")
            narrative.AppendLine($"Event: {eventId}")
            narrative.AppendLine()

            Dim foundSignificantMove = False

            For Each side In sides
                ' Check for reverse line moves
                Dim (isReverse, reverseMag, reverseDesc) = DetectReverseLineMove(eventId, side)

                ' Check for steam moves
                Dim (isSteam, steamMag, steamDesc) = SteamMove(eventId, side)

                If isReverse Or isSteam Then
                    foundSignificantMove = True

                    narrative.AppendLine($"🚨 **{side.ToUpper()}**")

                    If isReverse Then
                        narrative.AppendLine($"   ⚠️  REVERSE MOVE: {reverseDesc}")
                        narrative.AppendLine($"   💡 Sharp money likely on opposite side")
                    End If

                    If isSteam Then
                        narrative.AppendLine($"   🔥 STEAM: {steamDesc}")
                        narrative.AppendLine($"   💡 Heavy professional action detected")
                    End If

                    narrative.AppendLine()
                End If
            Next

            If Not foundSignificantMove Then
                narrative.AppendLine("📊 **MARKET STATUS: STABLE**")
                narrative.AppendLine("No significant reverse moves or steam detected.")
                narrative.AppendLine("Lines moving with public sentiment.")
                narrative.AppendLine()
            End If

            ' Public vs Sharp summary (if data available)
            If includePublicData Then
                Dim publicSummary = GetPublicVsSharpSummary(eventId)
                If Not String.IsNullOrEmpty(publicSummary) Then
                    narrative.AppendLine("👥 **PUBLIC vs SHARP:**")
                    narrative.AppendLine(publicSummary)
                    narrative.AppendLine()
                End If
            End If

            ' Monetization CTA
            narrative.AppendLine("🎯 **BETTING INSIGHT:**")
            If foundSignificantMove Then
                narrative.AppendLine("Significant market movement detected → investigate contrarian value.")
                narrative.AppendLine("[Get Full Analysis]({{premium_link}}) | [Live Alerts]({{alerts_link}})")
            Else
                narrative.AppendLine("Market moving with public sentiment → monitor for value opportunities.")
                narrative.AppendLine("[Track Movement]({{tracking_link}}) | [Premium Analysis]({{premium_link}})")
            End If

            Return narrative.ToString()

        Catch ex As Exception
            Console.WriteLine($"❌ Market narrative generation failed: {ex.Message}")
            Return $"Market analysis available for event {eventId}."
        End Try
    End Function

    ''' <summary>
    ''' Get weekly "Beating the Public" summary for reports
    ''' </summary>
    ''' <param name="sport">Sport to analyze</param>
    ''' <param name="lookbackDays">Days to analyze</param>
    ''' <returns>Summary report of public vs sharp moves</returns>
    Public Function GetWeeklyPublicVsSharpSummary(sport As String, Optional lookbackDays As Integer = 7) As String
        Try
            Dim summary As New Text.StringBuilder()

            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                ' Get reverse line move statistics
                Using cmd As New SQLiteCommand($"
                    SELECT
                        COUNT(*) as total_reverse_moves,
                        AVG(ABS(move)) as avg_move_size,
                        MAX(ABS(move)) as max_move_size
                    FROM market_moves
                    WHERE sport = @sport
                    AND inference LIKE '%reverse%'
                    AND ts >= datetime('now', '-{lookbackDays} days')", conn)

                    cmd.Parameters.AddWithValue("@sport", sport.ToUpper())

                    Using reader = cmd.ExecuteReader()
                        If reader.Read() Then
                            Dim reverseMoves = Convert.ToInt32(reader("total_reverse_moves"))
                            Dim avgMove = If(reader("avg_move_size") IsNot DBNull.Value, Convert.ToDouble(reader("avg_move_size")), 0)
                            Dim maxMove = If(reader("max_move_size") IsNot DBNull.Value, Convert.ToDouble(reader("max_move_size")), 0)

                            summary.AppendLine($"📊 **{sport} SHARP vs PUBLIC ({lookbackDays} days)**")
                            summary.AppendLine()
                            summary.AppendLine($"🔄 **Reverse Line Moves:** {reverseMoves}")
                            summary.AppendLine($"📏 **Average Move Size:** {avgMove:F1} points")
                            summary.AppendLine($"📈 **Largest Move:** {maxMove:F1} points")
                        End If
                    End Using
                End Using

                ' Get steam move statistics
                Using cmd As New SQLiteCommand($"
                    SELECT
                        COUNT(*) as total_steam_moves,
                        AVG(ABS(move)) as avg_steam_size
                    FROM market_moves
                    WHERE sport = @sport
                    AND inference LIKE '%steam%'
                    AND ts >= datetime('now', '-{lookbackDays} days')", conn)

                    cmd.Parameters.AddWithValue("@sport", sport.ToUpper())

                    Using reader = cmd.ExecuteReader()
                        If reader.Read() Then
                            Dim steamMoves = Convert.ToInt32(reader("total_steam_moves"))
                            Dim avgSteam = If(reader("avg_steam_size") IsNot DBNull.Value, Convert.ToDouble(reader("avg_steam_size")), 0)

                            summary.AppendLine($"🔥 **Steam Moves:** {steamMoves}")
                            summary.AppendLine($"⚡ **Average Steam Size:** {avgSteam:F1} points")
                        End If
                    End Using
                End Using
            End Using

            summary.AppendLine()
            summary.AppendLine("💡 **Key Insight:** Look for reverse line moves as contrarian indicators.")
            summary.AppendLine("🎯 **Sharp Strategy:** Follow the steam, fade heavy public sides with reverse movement.")

            Return summary.ToString()

        Catch ex As Exception
            Console.WriteLine($"❌ Weekly public vs sharp summary failed: {ex.Message}")
            Return $"Public vs sharp analysis available for {sport}."
        End Try
    End Function

    ''' <summary>
    ''' Calculate market consensus line using weighted average of sportsbooks
    ''' </summary>
    ''' <param name="eventId">Event identifier</param>
    ''' <param name="side">Betting side</param>
    ''' <returns>Weighted consensus line</returns>
    Public Function CalculateConsensusLine(eventId As String, side As String) As Double
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                ' Get latest odds from each book with weights
                Using cmd As New SQLiteCommand("
                    SELECT DISTINCT book, odds
                    FROM (
                        SELECT book, odds,
                               ROW_NUMBER() OVER (PARTITION BY book ORDER BY ts DESC) as rn
                        FROM market_snapshots
                        WHERE event_id = @event_id AND side = @side
                        AND ts >= datetime('now', '-2 hours')
                    ) ranked
                    WHERE rn = 1", conn)

                    cmd.Parameters.AddWithValue("@event_id", eventId)
                    cmd.Parameters.AddWithValue("@side", side)

                    Dim totalWeight = 0.0
                    Dim weightedSum = 0.0

                    Using reader = cmd.ExecuteReader()
                        While reader.Read()
                            Dim book = reader("book").ToString().ToLower()
                            Dim odds = Convert.ToInt32(reader("odds"))

                            Dim weight = If(SPORTSBOOK_WEIGHTS.ContainsKey(book), SPORTSBOOK_WEIGHTS(book), 0.05)
                            Dim decimal_odds = ConvertAmericanToDecimal(odds)

                            weightedSum += decimal_odds * weight
                            totalWeight += weight
                        End While
                    End Using

                    If totalWeight > 0 Then
                        Return Math.Round(weightedSum / totalWeight, 3)
                    End If
                End Using
            End Using

            Return 0.0

        Catch ex As Exception
            Console.WriteLine($"❌ Consensus line calculation failed: {ex.Message}")
            Return 0.0
        End Try
    End Function

    ' Helper methods
    Private Sub LogMarketMove(eventId As String, side As String, openLine As Double, currentLine As Double,
                             move As Double, inference As String)
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand("
                    INSERT INTO market_moves (ts, sport, event_id, side, open_line, current_line, move, inference)
                    VALUES (datetime('now'), @sport, @event_id, @side, @open_line, @current_line, @move, @inference)", conn)

                    cmd.Parameters.AddWithValue("@sport", GetEventSport(eventId))
                    cmd.Parameters.AddWithValue("@event_id", eventId)
                    cmd.Parameters.AddWithValue("@side", side)
                    cmd.Parameters.AddWithValue("@open_line", openLine)
                    cmd.Parameters.AddWithValue("@current_line", currentLine)
                    cmd.Parameters.AddWithValue("@move", move)
                    cmd.Parameters.AddWithValue("@inference", inference)

                    cmd.ExecuteNonQuery()
                End Using
            End Using
        Catch
            ' Silent fail
        End Try
    End Sub

    Private Function GetCurrentConsensusLine(eventId As String, side As String) As Double
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand("
                    SELECT consensus_line
                    FROM market_snapshots
                    WHERE event_id = @event_id AND side = @side
                    AND consensus_line IS NOT NULL
                    ORDER BY ts DESC
                    LIMIT 1", conn)

                    cmd.Parameters.AddWithValue("@event_id", eventId)
                    cmd.Parameters.AddWithValue("@side", side)

                    Dim result = cmd.ExecuteScalar()
                    Return If(result IsNot Nothing AndAlso result IsNot DBNull.Value, Convert.ToDouble(result), 0.0)
                End Using
            End Using
        Catch
            Return 0.0
        End Try
    End Function

    Private Function GetEventSides(eventId As String) As List(Of String)
        Dim sides As New List(Of String)()

        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand("
                    SELECT DISTINCT side
                    FROM market_snapshots
                    WHERE event_id = @event_id", conn)

                    cmd.Parameters.AddWithValue("@event_id", eventId)

                    Using reader = cmd.ExecuteReader()
                        While reader.Read()
                            sides.Add(reader("side").ToString())
                        End While
                    End Using
                End Using
            End Using
        Catch
            ' Silent fail
        End Try

        Return sides
    End Function

    Private Function GetPublicVsSharpSummary(eventId As String) As String
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand("
                    SELECT side, AVG(public_pct) as avg_public, AVG(handle_pct) as avg_handle
                    FROM market_snapshots
                    WHERE event_id = @event_id
                    AND public_pct IS NOT NULL
                    GROUP BY side", conn)

                    cmd.Parameters.AddWithValue("@event_id", eventId)

                    Dim summary As New Text.StringBuilder()

                    Using reader = cmd.ExecuteReader()
                        While reader.Read()
                            Dim side = reader("side").ToString()
                            Dim publicPct = Convert.ToDouble(reader("avg_public"))
                            Dim handlePct = If(reader("avg_handle") IsNot DBNull.Value, Convert.ToDouble(reader("avg_handle")), Nothing)

                            summary.AppendLine($"   • {side}: {publicPct:F1}% tickets")
                            If handlePct.HasValue Then
                                summary.AppendLine($"     Handle: {handlePct.Value:F1}% (Sharp indicator)")
                            End If
                        End While
                    End Using

                    Return summary.ToString()
                End Using
            End Using
        Catch
            Return ""
        End Try
    End Function

    Private Function GetEventSport(eventId As String) As String
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand("
                    SELECT sport
                    FROM market_snapshots
                    WHERE event_id = @event_id
                    LIMIT 1", conn)

                    cmd.Parameters.AddWithValue("@event_id", eventId)

                    Dim result = cmd.ExecuteScalar()
                    Return If(result IsNot Nothing, result.ToString(), "UNKNOWN")
                End Using
            End Using
        Catch
            Return "UNKNOWN"
        End Try
    End Function

    Private Function ConvertAmericanToDecimal(americanOdds As Integer) As Double
        If americanOdds > 0 Then
            Return 1 + (americanOdds / 100.0)
        Else
            Return 1 + (100.0 / Math.Abs(americanOdds))
        End If
    End Function

    Private Sub InitializeMarketTables()
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                ' Market snapshots table
                Using cmd As New SQLiteCommand("
                    CREATE TABLE IF NOT EXISTS market_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts TEXT DEFAULT (datetime('now')),
                        sport TEXT,
                        event_id TEXT,
                        side TEXT,
                        book TEXT,
                        odds INTEGER,
                        public_pct REAL,
                        handle_pct REAL,
                        consensus_line REAL
                    )", conn)
                    cmd.ExecuteNonQuery()
                End Using

                ' Market moves table
                Using cmd As New SQLiteCommand("
                    CREATE TABLE IF NOT EXISTS market_moves (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts TEXT DEFAULT (datetime('now')),
                        sport TEXT,
                        event_id TEXT,
                        side TEXT,
                        open_line REAL,
                        current_line REAL,
                        move REAL,
                        inference TEXT
                    )", conn)
                    cmd.ExecuteNonQuery()
                End Using

                ' Create indexes for performance
                Using cmd As New SQLiteCommand("CREATE INDEX IF NOT EXISTS idx_snapshots_event ON market_snapshots(event_id)", conn)
                    cmd.ExecuteNonQuery()
                End Using

                Using cmd As New SQLiteCommand("CREATE INDEX IF NOT EXISTS idx_moves_event ON market_moves(event_id)", conn)
                    cmd.ExecuteNonQuery()
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"❌ Market tables initialization failed: {ex.Message}")
        End Try
    End Sub

    Private Sub LogError(method As String, errorMessage As String, context As String)
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand("
                    INSERT OR IGNORE INTO error_log (ts, component, method, error_message, context)
                    VALUES (@ts, @component, @method, @error, @context)", conn)

                    cmd.Parameters.AddWithValue("@ts", DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss"))
                    cmd.Parameters.AddWithValue("@component", "MarketMovementEngine")
                    cmd.Parameters.AddWithValue("@method", method)
                    cmd.Parameters.AddWithValue("@error", errorMessage)
                    cmd.Parameters.AddWithValue("@context", context)

                    cmd.ExecuteNonQuery()
                End Using
            End Using
        Catch
            ' Silent fail for logging errors
        End Try
    End Sub
End Class
