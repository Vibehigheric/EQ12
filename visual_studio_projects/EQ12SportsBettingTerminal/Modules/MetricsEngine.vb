Imports System.Threading.Tasks
Imports System.Data
Imports System.Data.SQLite
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.Collections.Generic

''' <summary>
''' Advanced Sports Betting Metrics System for EQ12
''' Comprehensive extraction, calculation, and reporting of all sports metrics
''' Feeds bankroll management, arbitrage detection, and monetization deliverables
''' </summary>
Public Class MetricsEngine
    Private ReadOnly _dbPath As String
    Private ReadOnly _config As JObject

    ' Sport-specific metrics constants for schema consistency
    Public Shared ReadOnly NFL_METRICS As String() = {
        "QB_PASS_YDS", "QB_PASS_TDS", "QB_INTERCEPTIONS", "QB_RUSH_YDS", "QB_SACK_RATE",
        "RB_RUSH_YDS", "RB_RUSH_TDS", "RB_RECEPTIONS", "RB_REC_YDS", "RB_FUMBLES",
        "WR_RECEPTIONS", "WR_REC_YDS", "WR_REC_TDS", "WR_TARGETS", "WR_YAC",
        "TEAM_RUSH_YDS", "TEAM_PASS_YDS", "TEAM_POINTS", "TEAM_TURNOVERS", "TEAM_REDZONE_EFF",
        "DEF_SACKS", "DEF_INTERCEPTIONS", "DEF_FUMBLES_REC", "DEF_POINTS_ALLOWED", "DEF_YDS_ALLOWED"
    }

    Public Shared ReadOnly NBA_METRICS As String() = {
        "PPG", "FG_PCT", "FG3_PCT", "FT_PCT", "REBOUNDS", "ASSISTS", "STEALS", "BLOCKS", "TURNOVERS",
        "MINUTES", "USAGE_RATE", "PLUS_MINUS", "OFF_RATING", "DEF_RATING", "TRUE_SHOOTING_PCT",
        "ASSIST_RATIO", "REBOUND_RATE", "STEAL_RATE", "BLOCK_RATE", "PACE"
    }

    Public Shared ReadOnly MLB_METRICS As String() = {
        "BAT_AVG", "BAT_OBP", "BAT_SLG", "BAT_OPS", "BAT_HR", "BAT_RBI", "BAT_K_PCT", "BAT_BB_PCT",
        "BAT_BABIP", "BAT_ISO", "BAT_WOBA", "BAT_WRC_PLUS", "PITCH_ERA", "PITCH_WHIP", "PITCH_FIP",
        "PITCH_K_9", "PITCH_BB_9", "PITCH_HR_9", "PITCH_BABIP", "PITCH_LOB_PCT", "PITCH_HARD_HIT_PCT"
    }

    Public Shared ReadOnly NHL_METRICS As String() = {
        "GOALS", "ASSISTS", "POINTS", "PLUS_MINUS", "SHOTS", "SHOT_PCT", "TOI_PER_GAME", "HITS",
        "BLOCKED_SHOTS", "FACEOFF_WIN_PCT", "GOALS_AGAINST_AVG", "SAVE_PCT", "SHUTOUTS",
        "POWER_PLAY_PCT", "PENALTY_KILL_PCT", "CORSI_FOR_PCT", "FENWICK_FOR_PCT"
    }

    Public Shared ReadOnly SOCCER_METRICS As String() = {
        "GOALS", "ASSISTS", "XG", "XA", "SHOTS", "SHOTS_ON_TARGET", "PASS_ACC", "PASS_COMP",
        "CROSSES", "DRIBBLES", "TACKLES", "INTERCEPTIONS", "CLEARANCES", "YELLOW_CARDS", "RED_CARDS",
        "CLEAN_SHEETS", "GOALS_CONCEDED", "POSSESSION_PCT", "DISTANCE_COVERED"
    }

    Public Shared ReadOnly GOLF_METRICS As String() = {
        "STROKES_GAINED_TOTAL", "STROKES_GAINED_OTT", "STROKES_GAINED_APP", "STROKES_GAINED_ARG",
        "STROKES_GAINED_PUTTING", "DRIVING_DISTANCE", "DRIVING_ACCURACY", "GIR_PCT", "SCRAMBLING_PCT",
        "PUTTS_PER_ROUND", "BIRDIE_RATE", "BOGEY_AVOIDANCE", "SCORING_AVG", "CUT_PERCENTAGE"
    }

    Public Sub New(Optional dbPath As String = "", Optional config As JObject = Nothing)
        _dbPath = If(String.IsNullOrEmpty(dbPath), "Data/eq12_terminal.db", dbPath)
        _config = config

        ' Initialize sports metrics table
        InitializeSportsMetricsTable()
    End Sub

    ''' <summary>
    ''' Ingest raw odds data from OddsAPI and extract basic betting metrics
    ''' </summary>
    ''' <param name="rawJson">Raw JSON response from OddsAPI</param>
    ''' <param name="sport">Sport identifier (NFL, NBA, MLB, etc.)</param>
    Public Sub IngestOddsAPI(rawJson As JObject, sport As String)
        Try
            If rawJson Is Nothing OrElse String.IsNullOrEmpty(sport) Then
                Throw New ArgumentException("Invalid input parameters")
            End If

            Dim events = rawJson("data")
            If events Is Nothing Then Return

            For Each eventObj As JObject In events
                Dim eventId = eventObj("id")?.ToString()
                Dim homeTeam = eventObj("home_team")?.ToString()
                Dim awayTeam = eventObj("away_team")?.ToString()
                Dim commenceTime = eventObj("commence_time")?.ToString()

                ' Extract bookmaker odds
                Dim bookmakers = eventObj("bookmakers")
                If bookmakers IsNot Nothing Then
                    For Each bookmaker As JObject In bookmakers
                        Dim bookName = bookmaker("key")?.ToString()
                        Dim markets = bookmaker("markets")

                        If markets IsNot Nothing Then
                            For Each market As JObject In markets
                                Dim marketKey = market("key")?.ToString()
                                Dim outcomes = market("outcomes")

                                If outcomes IsNot Nothing Then
                                    For Each outcome As JObject In outcomes
                                        Dim name = outcome("name")?.ToString()
                                        Dim price = outcome("price")?.ToObject(Of Integer?)()
                                        Dim point = outcome("point")?.ToObject(Of Double?)()

                                        ' Calculate implied probability
                                        Dim impliedProb = CalculateImpliedProbability(price)

                                        ' Store basic betting metrics
                                        IngestStatFeed(sport, name, New Dictionary(Of String, Double) From {
                                            {"ODDS_AMERICAN", If(price, 0)},
                                            {"IMPLIED_PROB", impliedProb},
                                            {"POINT_SPREAD", If(point, 0)},
                                            {"DECIMAL_ODDS", ConvertToDecimal(price)}
                                        }, $"odds_api_{bookName}_{marketKey}")
                                    Next
                                End If
                            Next
                        End If
                    Next
                End If
            Next

            Console.WriteLine($"✅ Ingested odds data for {sport}: {events.Count()} events processed")

        Catch ex As Exception
            Console.WriteLine($"❌ OddsAPI ingestion failed: {ex.Message}")
            LogError("IngestOddsAPI", ex.Message, sport)
        End Try
    End Sub

    ''' <summary>
    ''' Ingest advanced statistical data for teams or players
    ''' </summary>
    ''' <param name="sport">Sport identifier</param>
    ''' <param name="playerOrTeam">Player or team name</param>
    ''' <param name="metrics">Dictionary of metric name/value pairs</param>
    ''' <param name="source">Data source identifier</param>
    Public Sub IngestStatFeed(sport As String, playerOrTeam As String, metrics As Dictionary(Of String, Double), Optional source As String = "manual")
        Try
            If String.IsNullOrEmpty(sport) Or String.IsNullOrEmpty(playerOrTeam) Or metrics Is Nothing Then
                Throw New ArgumentException("Invalid input parameters")
            End If

            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand(conn)
                    cmd.CommandText = "INSERT INTO sports_metrics (ts, sport, team_or_player, metric_name, metric_value, source)
                                     VALUES (@ts, @sport, @entity, @metric, @value, @source)"

                    For Each metric In metrics
                        cmd.Parameters.Clear()
                        cmd.Parameters.AddWithValue("@ts", DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss"))
                        cmd.Parameters.AddWithValue("@sport", sport.ToUpper())
                        cmd.Parameters.AddWithValue("@entity", playerOrTeam)
                        cmd.Parameters.AddWithValue("@metric", metric.Key.ToUpper())
                        cmd.Parameters.AddWithValue("@value", metric.Value)
                        cmd.Parameters.AddWithValue("@source", source)

                        cmd.ExecuteNonQuery()
                    Next
                End Using
            End Using

            Console.WriteLine($"✅ Ingested {metrics.Count} metrics for {sport} {playerOrTeam}")

        Catch ex As Exception
            Console.WriteLine($"❌ Stat ingestion failed: {ex.Message}")
            LogError("IngestStatFeed", ex.Message, $"{sport}_{playerOrTeam}")
        End Try
    End Sub

    ''' <summary>
    ''' Compute advanced metrics for a specific sport with monetization hooks
    ''' </summary>
    ''' <param name="sport">Sport to compute metrics for</param>
    ''' <param name="lookbackDays">Number of days to look back for data</param>
    ''' <returns>DataTable with computed advanced metrics</returns>
    Public Function ComputeAdvancedMetrics(sport As String, Optional lookbackDays As Integer = 30) As DataTable
        Try
            Dim dt As New DataTable()
            dt.Columns.Add("Entity", GetType(String))
            dt.Columns.Add("MetricName", GetType(String))
            dt.Columns.Add("MetricValue", GetType(Double))
            dt.Columns.Add("AdvancedValue", GetType(Double))
            dt.Columns.Add("Percentile", GetType(Double))
            dt.Columns.Add("MonetizationTier", GetType(String))
            dt.Columns.Add("EdgeSignal", GetType(String))

            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                ' Get recent metrics for sport
                Using cmd As New SQLiteCommand($"
                    SELECT team_or_player, metric_name, AVG(metric_value) as avg_value, COUNT(*) as sample_size
                    FROM sports_metrics
                    WHERE sport = @sport
                    AND ts >= datetime('now', '-{lookbackDays} days')
                    GROUP BY team_or_player, metric_name
                    HAVING sample_size >= 3", conn)

                    cmd.Parameters.AddWithValue("@sport", sport.ToUpper())

                    Using reader = cmd.ExecuteReader()
                        Dim rawData As New List(Of (entity As String, metric As String, value As Double))

                        While reader.Read()
                            rawData.Add((
                                reader("team_or_player").ToString(),
                                reader("metric_name").ToString(),
                                Convert.ToDouble(reader("avg_value"))
                            ))
                        End While

                        ' Compute sport-specific advanced metrics
                        Select Case sport.ToUpper()
                            Case "NFL"
                                ComputeNFLAdvancedMetrics(rawData, dt)
                            Case "NBA", "WNBA"
                                ComputeNBAAdvancedMetrics(rawData, dt)
                            Case "MLB"
                                ComputeMLBAdvancedMetrics(rawData, dt)
                            Case "NHL"
                                ComputeNHLAdvancedMetrics(rawData, dt)
                            Case "SOCCER"
                                ComputeSoccerAdvancedMetrics(rawData, dt)
                            Case "GOLF"
                                ComputeGolfAdvancedMetrics(rawData, dt)
                        End Select
                    End Using
                End Using
            End Using

            ' Add monetization signals and edge detection
            AddMonetizationSignals(dt, sport)

            Console.WriteLine($"✅ Computed {dt.Rows.Count} advanced metrics for {sport}")
            Return dt

        Catch ex As Exception
            Console.WriteLine($"❌ Advanced metrics computation failed: {ex.Message}")
            LogError("ComputeAdvancedMetrics", ex.Message, sport)
            Return New DataTable()
        End Try
    End Function

    ''' <summary>
    ''' Compute NFL-specific advanced metrics
    ''' </summary>
    Private Sub ComputeNFLAdvancedMetrics(rawData As List(Of (entity As String, metric As String, value As Double)), dt As DataTable)
        Dim entities = rawData.GroupBy(Function(x) x.entity)

        For Each entityGroup In entities
            Dim entity = entityGroup.Key
            Dim metrics = entityGroup.ToDictionary(Function(x) x.metric, Function(x) x.value)

            ' QB Efficiency Rating
            If metrics.ContainsKey("QB_PASS_YDS") AndAlso metrics.ContainsKey("QB_PASS_TDS") AndAlso metrics.ContainsKey("QB_INTERCEPTIONS") Then
                Dim passingYds = metrics("QB_PASS_YDS")
                Dim passingTds = metrics("QB_PASS_TDS")
                Dim interceptions = metrics("QB_INTERCEPTIONS")
                Dim attempts = If(metrics.ContainsKey("QB_ATTEMPTS"), metrics("QB_ATTEMPTS"), 30) ' Default attempts

                Dim qbEfficiency = (passingYds + (passingTds * 20) - (interceptions * 45)) / attempts

                dt.Rows.Add(entity, "QB_EFFICIENCY", qbEfficiency, qbEfficiency, 0, "premium",
                           If(qbEfficiency > 8, "STRONG_QB", "WEAK_QB"))
            End If

            ' Offensive EPA (Expected Points Added)
            If metrics.ContainsKey("TEAM_POINTS") AndAlso metrics.ContainsKey("TEAM_RUSH_YDS") AndAlso metrics.ContainsKey("TEAM_PASS_YDS") Then
                Dim points = metrics("TEAM_POINTS")
                Dim rushYds = metrics("TEAM_RUSH_YDS")
                Dim passYds = metrics("TEAM_PASS_YDS")

                Dim offensiveEPA = (points * 1.0) + (passYds * 0.04) + (rushYds * 0.06)

                dt.Rows.Add(entity, "OFFENSIVE_EPA", offensiveEPA, offensiveEPA, 0, "standard",
                           If(offensiveEPA > 25, "HIGH_SCORING", "LOW_SCORING"))
            End If

            ' Red Zone Efficiency Score
            If metrics.ContainsKey("TEAM_REDZONE_EFF") Then
                Dim rzEff = metrics("TEAM_REDZONE_EFF")
                dt.Rows.Add(entity, "REDZONE_SCORE", rzEff, rzEff * 100, 0, "premium",
                           If(rzEff > 0.6, "REDZONE_ELITE", "REDZONE_STRUGGLE"))
            End If
        Next
    End Sub

    ''' <summary>
    ''' Compute NBA-specific advanced metrics
    ''' </summary>
    Private Sub ComputeNBAAdvancedMetrics(rawData As List(Of (entity As String, metric As String, value As Double)), dt As DataTable)
        Dim entities = rawData.GroupBy(Function(x) x.entity)

        For Each entityGroup In entities
            Dim entity = entityGroup.Key
            Dim metrics = entityGroup.ToDictionary(Function(x) x.metric, Function(x) x.value)

            ' True Shooting Percentage
            If metrics.ContainsKey("PPG") AndAlso metrics.ContainsKey("FG3_PCT") AndAlso metrics.ContainsKey("FT_PCT") Then
                Dim points = metrics("PPG")
                Dim fg3Pct = metrics("FG3_PCT")
                Dim ftPct = metrics("FT_PCT")
                Dim fgAttempts = If(metrics.ContainsKey("FG_ATTEMPTS"), metrics("FG_ATTEMPTS"), 15)
                Dim ftAttempts = If(metrics.ContainsKey("FT_ATTEMPTS"), metrics("FT_ATTEMPTS"), 5)

                Dim trueShootingPct = points / (2 * (fgAttempts + 0.44 * ftAttempts))

                dt.Rows.Add(entity, "TRUE_SHOOTING_PCT", trueShootingPct, trueShootingPct * 100, 0, "premium",
                           If(trueShootingPct > 0.58, "ELITE_SHOOTER", "POOR_SHOOTER"))
            End If

            ' Player Efficiency Rating (PER)
            If metrics.ContainsKey("PPG") AndAlso metrics.ContainsKey("REBOUNDS") AndAlso metrics.ContainsKey("ASSISTS") Then
                Dim points = metrics("PPG")
                Dim rebounds = metrics("REBOUNDS")
                Dim assists = metrics("ASSISTS")
                Dim turnovers = If(metrics.ContainsKey("TURNOVERS"), metrics("TURNOVERS"), 2)

                Dim per = ((points + rebounds + assists) - turnovers) * 1.5

                dt.Rows.Add(entity, "PLAYER_EFFICIENCY", per, per, 0, "standard",
                           If(per > 20, "ELITE_PLAYER", "AVERAGE_PLAYER"))
            End If
        Next
    End Sub

    ''' <summary>
    ''' Compute MLB-specific advanced metrics
    ''' </summary>
    Private Sub ComputeMLBAdvancedMetrics(rawData As List(Of (entity As String, metric As String, value As Double)), dt As DataTable)
        Dim entities = rawData.GroupBy(Function(x) x.entity)

        For Each entityGroup In entities
            Dim entity = entityGroup.Key
            Dim metrics = entityGroup.ToDictionary(Function(x) x.metric, Function(x) x.value)

            ' Weighted On-Base Average (wOBA)
            If metrics.ContainsKey("BAT_OBP") AndAlso metrics.ContainsKey("BAT_SLG") Then
                Dim obp = metrics("BAT_OBP")
                Dim slg = metrics("BAT_SLG")

                Dim woba = (0.69 * obp) + (0.72 * slg) - 0.09

                dt.Rows.Add(entity, "WOBA", woba, woba * 1000, 0, "premium",
                           If(woba > 0.36, "ELITE_HITTER", "POOR_HITTER"))
            End If

            ' Fielding Independent Pitching (FIP)
            If metrics.ContainsKey("PITCH_HR_9") AndAlso metrics.ContainsKey("PITCH_BB_9") AndAlso metrics.ContainsKey("PITCH_K_9") Then
                Dim hr9 = metrics("PITCH_HR_9")
                Dim bb9 = metrics("PITCH_BB_9")
                Dim k9 = metrics("PITCH_K_9")

                Dim fip = (13 * hr9) + (3 * bb9) - (2 * k9) + 3.2

                dt.Rows.Add(entity, "FIP_SCORE", fip, fip, 0, "premium",
                           If(fip < 3.2, "ELITE_PITCHER", "POOR_PITCHER"))
            End If
        Next
    End Sub

    ''' <summary>
    ''' Compute NHL-specific advanced metrics
    ''' </summary>
    Private Sub ComputeNHLAdvancedMetrics(rawData As List(Of (entity As String, metric As String, value As Double)), dt As DataTable)
        ' Implementation for NHL advanced metrics (Corsi, Fenwick, etc.)
        Dim entities = rawData.GroupBy(Function(x) x.entity)

        For Each entityGroup In entities
            Dim entity = entityGroup.Key
            Dim metrics = entityGroup.ToDictionary(Function(x) x.metric, Function(x) x.value)

            ' Points per 60 minutes
            If metrics.ContainsKey("POINTS") AndAlso metrics.ContainsKey("TOI_PER_GAME") Then
                Dim points = metrics("POINTS")
                Dim toi = metrics("TOI_PER_GAME")

                Dim pointsPer60 = If(toi > 0, (points / toi) * 60, 0)

                dt.Rows.Add(entity, "POINTS_PER_60", pointsPer60, pointsPer60, 0, "standard",
                           If(pointsPer60 > 2.0, "ELITE_SCORER", "LOW_SCORER"))
            End If
        Next
    End Sub

    ''' <summary>
    ''' Compute Soccer-specific advanced metrics
    ''' </summary>
    Private Sub ComputeSoccerAdvancedMetrics(rawData As List(Of (entity As String, metric As String, value As Double)), dt As DataTable)
        ' Implementation for Soccer advanced metrics (xG, xA, etc.)
        Dim entities = rawData.GroupBy(Function(x) x.entity)

        For Each entityGroup In entities
            Dim entity = entityGroup.Key
            Dim metrics = entityGroup.ToDictionary(Function(x) x.metric, Function(x) x.value)

            ' Goals vs Expected Goals differential
            If metrics.ContainsKey("GOALS") AndAlso metrics.ContainsKey("XG") Then
                Dim goals = metrics("GOALS")
                Dim xG = metrics("XG")

                Dim goalsVsXg = goals - xG

                dt.Rows.Add(entity, "GOALS_VS_XG", goalsVsXg, goalsVsXg, 0, "premium",
                           If(goalsVsXg > 2, "CLINICAL_FINISHER", "UNDERPERFORMING"))
            End If
        Next
    End Sub

    ''' <summary>
    ''' Compute Golf-specific advanced metrics
    ''' </summary>
    Private Sub ComputeGolfAdvancedMetrics(rawData As List(Of (entity As String, metric As String, value As Double)), dt As DataTable)
        ' Implementation for Golf advanced metrics
        Dim entities = rawData.GroupBy(Function(x) x.entity)

        For Each entityGroup In entities
            Dim entity = entityGroup.Key
            Dim metrics = entityGroup.ToDictionary(Function(x) x.metric, Function(x) x.value)

            ' Overall Strokes Gained
            If metrics.ContainsKey("STROKES_GAINED_TOTAL") Then
                Dim sg = metrics("STROKES_GAINED_TOTAL")

                dt.Rows.Add(entity, "STROKES_GAINED_RANK", sg, sg, 0, "premium",
                           If(sg > 1.5, "ELITE_GOLFER", "STRUGGLING_GOLFER"))
            End If
        Next
    End Sub

    ''' <summary>
    ''' Add monetization signals and tier classifications to metrics
    ''' </summary>
    Private Sub AddMonetizationSignals(dt As DataTable, sport As String)
        ' Calculate percentiles and assign monetization tiers
        For Each row As DataRow In dt.Rows
            Dim value = Convert.ToDouble(row("AdvancedValue"))
            Dim metricName = row("MetricName").ToString()

            ' Calculate percentile based on all values for this metric
            Dim allValues = dt.AsEnumerable().Where(Function(r) r("MetricName").ToString() = metricName).
                          Select(Function(r) Convert.ToDouble(r("AdvancedValue"))).ToArray()

            If allValues.Length > 1 Then
                Array.Sort(allValues)
                Dim percentile = (Array.IndexOf(allValues, value) + 1) / allValues.Length * 100
                row("Percentile") = Math.Round(percentile, 1)

                ' Assign monetization tier based on percentile
                If percentile >= 90 Then
                    row("MonetizationTier") = "elite"
                ElseIf percentile >= 70 Then
                    row("MonetizationTier") = "premium"
                Else
                    row("MonetizationTier") = "standard"
                End If
            End If
        Next
    End Sub

    ''' <summary>
    ''' Export metrics report for monetization (CSV, Excel, or blog content)
    ''' </summary>
    ''' <param name="period">Report period (daily, weekly, monthly)</param>
    ''' <param name="sport">Sport to report on</param>
    ''' <param name="format">Output format (csv, excel, blog)</param>
    ''' <returns>File path or content string</returns>
    Public Function ExportMetricsReport(period As String, sport As String, Optional format As String = "csv") As String
        Try
            Dim lookbackDays = GetLookbackDays(period)
            Dim metrics = ComputeAdvancedMetrics(sport, lookbackDays)

            Select Case format.ToLower()
                Case "csv"
                    Return ExportToCSV(metrics, sport, period)
                Case "excel"
                    Return ExportToExcel(metrics, sport, period)
                Case "blog"
                    Return GenerateBlogContent(metrics, sport, period)
                Case Else
                    Throw New ArgumentException($"Unsupported format: {format}")
            End Select

        Catch ex As Exception
            Console.WriteLine($"❌ Report export failed: {ex.Message}")
            Return ""
        End Try
    End Function

    ''' <summary>
    ''' Generate AI-enhanced narrative for metrics (monetization copy)
    ''' </summary>
    ''' <param name="sport">Sport to analyze</param>
    ''' <param name="topN">Number of top performers to highlight</param>
    ''' <returns>Marketing-ready narrative text</returns>
    Public Function GenerateMetricsNarrative(sport As String, Optional topN As Integer = 5) As String
        Try
            Dim metrics = ComputeAdvancedMetrics(sport)
            Dim narrative As New Text.StringBuilder()

            ' Header with monetization hook
            narrative.AppendLine($"🎯 **{sport.ToUpper()} ADVANCED METRICS INSIGHT**")
            narrative.AppendLine($"*Where the sharp money finds its edge...*")
            narrative.AppendLine()

            ' Top performers section
            Dim elitePerformers = metrics.AsEnumerable().
                                Where(Function(r) r("MonetizationTier").ToString() = "elite").
                                Take(topN).ToArray()

            If elitePerformers.Length > 0 Then
                narrative.AppendLine("🏆 **ELITE TIER PERFORMERS:**")
                For Each performer In elitePerformers
                    Dim entity = performer("Entity").ToString()
                    Dim metric = performer("MetricName").ToString()
                    Dim value = Convert.ToDouble(performer("AdvancedValue"))
                    Dim signal = performer("EdgeSignal").ToString()

                    narrative.AppendLine($"• **{entity}** - {metric}: {value:F2} ({signal})")
                Next
                narrative.AppendLine()
            End If

            ' Market insights
            narrative.AppendLine("💡 **BETTING INSIGHTS:**")
            narrative.AppendLine("Elite metrics often correlate with undervalued lines.")
            narrative.AppendLine("Track these performers for value opportunities.")
            narrative.AppendLine()

            ' Monetization CTA
            narrative.AppendLine("🚀 **Want the complete analysis?**")
            narrative.AppendLine("Premium subscribers get detailed breakdowns, projections, and alert notifications.")
            narrative.AppendLine("[Upgrade to Premium]({{upgrade_link}}) | [View Full Report]({{report_link}})")

            Return narrative.ToString()

        Catch ex As Exception
            Console.WriteLine($"❌ Narrative generation failed: {ex.Message}")
            Return $"Advanced {sport} metrics analysis available in premium reports."
        End Try
    End Function

    ' Helper methods
    Private Function CalculateImpliedProbability(americanOdds As Integer?) As Double
        If Not americanOdds.HasValue Then Return 0

        Dim odds = americanOdds.Value
        If odds > 0 Then
            Return 100.0 / (odds + 100.0)
        Else
            Return Math.Abs(odds) / (Math.Abs(odds) + 100.0)
        End If
    End Function

    Private Function ConvertToDecimal(americanOdds As Integer?) As Double
        If Not americanOdds.HasValue Then Return 1.0

        Dim odds = americanOdds.Value
        If odds > 0 Then
            Return 1 + (odds / 100.0)
        Else
            Return 1 + (100.0 / Math.Abs(odds))
        End If
    End Function

    Private Function GetLookbackDays(period As String) As Integer
        Select Case period.ToLower()
            Case "daily" : Return 1
            Case "weekly" : Return 7
            Case "monthly" : Return 30
            Case Else : Return 7
        End Select
    End Function

    Private Function ExportToCSV(metrics As DataTable, sport As String, period As String) As String
        Dim fileName = $"Exports\metrics_{sport}_{period}_{DateTime.Now:yyyyMMdd_HHmmss}.csv"
        Dim directory = Path.GetDirectoryName(fileName)
        If Not Directory.Exists(directory) Then Directory.CreateDirectory(directory)

        Using writer As New StreamWriter(fileName)
            ' Write header
            Dim headers = metrics.Columns.Cast(Of DataColumn)().Select(Function(c) c.ColumnName)
            writer.WriteLine(String.Join(",", headers))

            ' Write data
            For Each row As DataRow In metrics.Rows
                Dim values = row.ItemArray.Select(Function(field) $"""{field}""")
                writer.WriteLine(String.Join(",", values))
            Next
        End Using

        Return fileName
    End Function

    Private Function ExportToExcel(metrics As DataTable, sport As String, period As String) As String
        ' Implementation would use EPPlus or similar library
        Return ExportToCSV(metrics, sport, period) ' Fallback to CSV for now
    End Function

    Private Function GenerateBlogContent(metrics As DataTable, sport As String, period As String) As String
        Dim content As New Text.StringBuilder()

        content.AppendLine($"# {sport} Advanced Metrics Report - {period.ToTitleCase()}")
        content.AppendLine()
        content.AppendLine("## Executive Summary")
        content.AppendLine($"Analysis of {metrics.Rows.Count} advanced metrics covering key performance indicators.")
        content.AppendLine()

        ' Elite performers table
        Dim elites = metrics.AsEnumerable().Where(Function(r) r("MonetizationTier").ToString() = "elite")
        If elites.Any() Then
            content.AppendLine("## Elite Performers")
            content.AppendLine("| Entity | Metric | Value | Percentile |")
            content.AppendLine("|--------|--------|-------|------------|")

            For Each elite In elites.Take(10)
                content.AppendLine($"| {elite("Entity")} | {elite("MetricName")} | {elite("AdvancedValue"):F2} | {elite("Percentile")}% |")
            Next
            content.AppendLine()
        End If

        content.AppendLine("*Full analysis available to premium subscribers.*")

        Return content.ToString()
    End Function

    Private Sub InitializeSportsMetricsTable()
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand("
                    CREATE TABLE IF NOT EXISTS sports_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts TEXT DEFAULT (datetime('now')),
                        sport TEXT,
                        team_or_player TEXT,
                        metric_name TEXT,
                        metric_value REAL,
                        source TEXT
                    )", conn)
                    cmd.ExecuteNonQuery()
                End Using

                ' Create indexes for performance
                Using cmd As New SQLiteCommand("CREATE INDEX IF NOT EXISTS idx_sports_metrics_sport ON sports_metrics(sport)", conn)
                    cmd.ExecuteNonQuery()
                End Using

                Using cmd As New SQLiteCommand("CREATE INDEX IF NOT EXISTS idx_sports_metrics_entity ON sports_metrics(team_or_player)", conn)
                    cmd.ExecuteNonQuery()
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"❌ Database initialization failed: {ex.Message}")
        End Try
    End Sub

    Private Sub LogError(method As String, errorMessage As String, context As String)
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand("
                    INSERT INTO error_log (ts, component, method, error_message, context)
                    VALUES (@ts, @component, @method, @error, @context)", conn)

                    cmd.Parameters.AddWithValue("@ts", DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss"))
                    cmd.Parameters.AddWithValue("@component", "MetricsEngine")
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
