Imports System.Threading.Tasks
Imports System.Data
Imports System.Data.SQLite
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.Collections.Generic

''' <summary>
''' Injuries & Personnel Matchups Engine for EQ12
''' Tracks injuries, severity assessment, matchup analysis, and performance adjustments
''' Feeds monetization content and betting edge identification
''' </summary>
Public Class InjuriesEngine
    Private ReadOnly _dbPath As String
    Private ReadOnly _config As JObject

    ' Injury severity scale (1-5, where 5 = season-ending)
    Public Shared ReadOnly SEVERITY_SCALE As Dictionary(Of String, Integer) = New Dictionary(Of String, Integer) From {
        {"QUESTIONABLE", 2},
        {"DOUBTFUL", 3},
        {"OUT", 4},
        {"IR", 5},
        {"PUP", 5},
        {"SUSPENDED", 3},
        {"DAY_TO_DAY", 1},
        {"PROBABLE", 1},
        {"HEALTHY", 0}
    }

    ' Position importance weights by sport
    Public Shared ReadOnly NFL_POSITION_WEIGHTS As Dictionary(Of String, Double) = New Dictionary(Of String, Double) From {
        {"QB", 0.35}, {"RB", 0.15}, {"WR", 0.12}, {"TE", 0.08}, {"OL", 0.20},
        {"DE", 0.15}, {"LB", 0.12}, {"CB", 0.18}, {"S", 0.10}, {"DT", 0.08}
    }

    Public Shared ReadOnly NBA_POSITION_WEIGHTS As Dictionary(Of String, Double) = New Dictionary(Of String, Double) From {
        {"PG", 0.25}, {"SG", 0.20}, {"SF", 0.22}, {"PF", 0.18}, {"C", 0.15}
    }

    Public Sub New(Optional dbPath As String = "", Optional config As JObject = Nothing)
        _dbPath = If(String.IsNullOrEmpty(dbPath), "Data/eq12_terminal.db", dbPath)
        _config = config

        ' Initialize injury and matchup tables
        InitializeInjuryTables()
    End Sub

    ''' <summary>
    ''' Log injury information with severity and impact assessment
    ''' </summary>
    ''' <param name="sport">Sport identifier</param>
    ''' <param name="team">Team name</param>
    ''' <param name="player">Player name</param>
    ''' <param name="status">Injury status (OUT, QUESTIONABLE, etc.)</param>
    ''' <param name="severity">Severity score 1-5</param>
    ''' <param name="source">Data source</param>
    ''' <param name="notes">Additional notes</param>
    Public Sub LogInjury(sport As String, team As String, player As String, status As String,
                        severity As Integer, source As String, notes As String)
        Try
            If String.IsNullOrEmpty(sport) Or String.IsNullOrEmpty(team) Or String.IsNullOrEmpty(player) Then
                Throw New ArgumentException("Invalid input parameters")
            End If

            ' Validate severity
            If severity < 0 Or severity > 5 Then
                severity = If(SEVERITY_SCALE.ContainsKey(status.ToUpper()), SEVERITY_SCALE(status.ToUpper()), 2)
            End If

            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                ' Check if injury already exists (update vs insert)
                Using checkCmd As New SQLiteCommand("
                    SELECT id FROM injuries
                    WHERE sport = @sport AND team = @team AND player = @player
                    AND ts >= datetime('now', '-7 days')", conn)

                    checkCmd.Parameters.AddWithValue("@sport", sport.ToUpper())
                    checkCmd.Parameters.AddWithValue("@team", team)
                    checkCmd.Parameters.AddWithValue("@player", player)

                    Dim existingId = checkCmd.ExecuteScalar()

                    If existingId IsNot Nothing Then
                        ' Update existing injury
                        Using updateCmd As New SQLiteCommand("
                            UPDATE injuries
                            SET status = @status, severity = @severity, source = @source,
                                notes = @notes, ts = datetime('now')
                            WHERE id = @id", conn)

                            updateCmd.Parameters.AddWithValue("@status", status.ToUpper())
                            updateCmd.Parameters.AddWithValue("@severity", severity)
                            updateCmd.Parameters.AddWithValue("@source", source)
                            updateCmd.Parameters.AddWithValue("@notes", notes)
                            updateCmd.Parameters.AddWithValue("@id", existingId)

                            updateCmd.ExecuteNonQuery()
                        End Using
                    Else
                        ' Insert new injury
                        Using insertCmd As New SQLiteCommand("
                            INSERT INTO injuries (ts, sport, team, player, status, severity, source, notes)
                            VALUES (datetime('now'), @sport, @team, @player, @status, @severity, @source, @notes)", conn)

                            insertCmd.Parameters.AddWithValue("@sport", sport.ToUpper())
                            insertCmd.Parameters.AddWithValue("@team", team)
                            insertCmd.Parameters.AddWithValue("@player", player)
                            insertCmd.Parameters.AddWithValue("@status", status.ToUpper())
                            insertCmd.Parameters.AddWithValue("@severity", severity)
                            insertCmd.Parameters.AddWithValue("@source", source)
                            insertCmd.Parameters.AddWithValue("@notes", notes)

                            insertCmd.ExecuteNonQuery()
                        End Using
                    End If
                End Using
            End Using

            Console.WriteLine($"✅ Logged injury: {team} {player} - {status} (Severity: {severity})")

        Catch ex As Exception
            Console.WriteLine($"❌ Injury logging failed: {ex.Message}")
            LogError("LogInjury", ex.Message, $"{sport}_{team}_{player}")
        End Try
    End Sub

    ''' <summary>
    ''' Get current injuries for a team with impact assessment
    ''' </summary>
    ''' <param name="sport">Sport identifier</param>
    ''' <param name="team">Team name</param>
    ''' <param name="activeDays">Look for injuries in last N days</param>
    ''' <returns>DataTable with injury details and impact scores</returns>
    Public Function GetTeamInjuries(sport As String, team As String, Optional activeDays As Integer = 14) As DataTable
        Try
            Dim dt As New DataTable()
            dt.Columns.Add("Player", GetType(String))
            dt.Columns.Add("Status", GetType(String))
            dt.Columns.Add("Severity", GetType(Integer))
            dt.Columns.Add("Position", GetType(String))
            dt.Columns.Add("ImpactWeight", GetType(Double))
            dt.Columns.Add("AdjustmentFactor", GetType(Double))
            dt.Columns.Add("Notes", GetType(String))
            dt.Columns.Add("DaysOut", GetType(Integer))
            dt.Columns.Add("MonetizationSignal", GetType(String))

            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand($"
                    SELECT player, status, severity, notes,
                           julianday('now') - julianday(ts) as days_out
                    FROM injuries
                    WHERE sport = @sport AND team = @team
                    AND ts >= datetime('now', '-{activeDays} days')
                    AND severity > 0
                    ORDER BY severity DESC, ts DESC", conn)

                    cmd.Parameters.AddWithValue("@sport", sport.ToUpper())
                    cmd.Parameters.AddWithValue("@team", team)

                    Using reader = cmd.ExecuteReader()
                        While reader.Read()
                            Dim player = reader("player").ToString()
                            Dim status = reader("status").ToString()
                            Dim severity = Convert.ToInt32(reader("severity"))
                            Dim notes = reader("notes").ToString()
                            Dim daysOut = Convert.ToInt32(reader("days_out"))

                            ' Determine position and impact weight
                            Dim position = DeterminePosition(player, notes, sport)
                            Dim impactWeight = GetPositionWeight(position, sport)

                            ' Calculate adjustment factor
                            Dim adjustmentFactor = CalculateInjuryAdjustmentFactor(severity, impactWeight)

                            ' Generate monetization signal
                            Dim monetizationSignal = GenerateInjuryMonetizationSignal(severity, impactWeight, daysOut)

                            dt.Rows.Add(player, status, severity, position, impactWeight,
                                       adjustmentFactor, notes, daysOut, monetizationSignal)
                        End While
                    End Using
                End Using
            End Using

            Return dt

        Catch ex As Exception
            Console.WriteLine($"❌ Get team injuries failed: {ex.Message}")
            LogError("GetTeamInjuries", ex.Message, $"{sport}_{team}")
            Return New DataTable()
        End Try
    End Function

    ''' <summary>
    ''' Calculate injury adjustment factor for metrics
    ''' </summary>
    ''' <param name="baseMetric">Base metric value</param>
    ''' <param name="severityAvg">Average severity of team injuries</param>
    ''' <param name="depthScore">Team depth score (0-1)</param>
    ''' <returns>Adjusted metric value</returns>
    Public Function InjuryAdjustment(baseMetric As Double, severityAvg As Double, depthScore As Double) As Double
        Try
            ' Standard adjustment formula: adj = baseMetric * (1 - 0.02 * severityAvg) * (0.9 + 0.1 * depthScore)
            Dim severityImpact = Math.Max(0, 1 - (0.02 * severityAvg))
            Dim depthBonus = 0.9 + (0.1 * Math.Min(1, Math.Max(0, depthScore)))

            Dim adjustedMetric = baseMetric * severityImpact * depthBonus

            Return Math.Round(adjustedMetric, 4)

        Catch ex As Exception
            Console.WriteLine($"❌ Injury adjustment calculation failed: {ex.Message}")
            Return baseMetric ' Return original value on error
        End Try
    End Function

    ''' <summary>
    ''' Log matchup analysis between entities (players, units, teams)
    ''' </summary>
    ''' <param name="sport">Sport identifier</param>
    ''' <param name="entityA">First entity (e.g., "Patrick Mahomes")</param>
    ''' <param name="entityB">Second entity (e.g., "Bills Defense")</param>
    ''' <param name="matchupType">Type of matchup (player-vs-player, unit-vs-unit, etc.)</param>
    ''' <param name="factor">Matchup factor description</param>
    ''' <param name="weight">Model weight (-1 to 1, positive favors A)</param>
    ''' <param name="source">Data source</param>
    ''' <param name="notes">Analysis notes</param>
    Public Sub LogMatchup(sport As String, entityA As String, entityB As String, matchupType As String,
                         factor As String, weight As Double, source As String, notes As String)
        Try
            If String.IsNullOrEmpty(sport) Or String.IsNullOrEmpty(entityA) Or String.IsNullOrEmpty(entityB) Then
                Throw New ArgumentException("Invalid input parameters")
            End If

            ' Clamp weight to valid range
            weight = Math.Max(-1, Math.Min(1, weight))

            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand("
                    INSERT INTO matchups (ts, sport, entity_a, entity_b, type, factor, model_weight, source, notes)
                    VALUES (datetime('now'), @sport, @entityA, @entityB, @type, @factor, @weight, @source, @notes)", conn)

                    cmd.Parameters.AddWithValue("@sport", sport.ToUpper())
                    cmd.Parameters.AddWithValue("@entityA", entityA)
                    cmd.Parameters.AddWithValue("@entityB", entityB)
                    cmd.Parameters.AddWithValue("@type", matchupType)
                    cmd.Parameters.AddWithValue("@factor", factor)
                    cmd.Parameters.AddWithValue("@weight", weight)
                    cmd.Parameters.AddWithValue("@source", source)
                    cmd.Parameters.AddWithValue("@notes", notes)

                    cmd.ExecuteNonQuery()
                End Using
            End Using

            Console.WriteLine($"✅ Logged matchup: {entityA} vs {entityB} (Weight: {weight:F3})")

        Catch ex As Exception
            Console.WriteLine($"❌ Matchup logging failed: {ex.Message}")
            LogError("LogMatchup", ex.Message, $"{sport}_{entityA}_{entityB}")
        End Try
    End Sub

    ''' <summary>
    ''' Calculate matchup adjustment for metrics based on historical performance
    ''' </summary>
    ''' <param name="baseMetric">Base metric value</param>
    ''' <param name="weights">Collection of matchup weights</param>
    ''' <returns>Adjusted metric value</returns>
    Public Function MatchupAdjustment(baseMetric As Double, weights As IEnumerable(Of Double)) As Double
        Try
            If weights Is Nothing OrElse Not weights.Any() Then
                Return baseMetric
            End If

            ' Standard adjustment: adj = baseMetric * (1 + Sum(weights))
            Dim totalWeight = weights.Sum()
            Dim adjustedMetric = baseMetric * (1 + totalWeight)

            Return Math.Round(adjustedMetric, 4)

        Catch ex As Exception
            Console.WriteLine($"❌ Matchup adjustment calculation failed: {ex.Message}")
            Return baseMetric ' Return original value on error
        End Try
    End Function

    ''' <summary>
    ''' Build monetization-ready narrative for injuries and matchups
    ''' </summary>
    ''' <param name="sport">Sport identifier</param>
    ''' <param name="team">Team to analyze</param>
    ''' <param name="includeMatchups">Include matchup analysis</param>
    ''' <returns>Marketing-ready narrative text</returns>
    Public Function BuildInjuryMatchupNarrative(sport As String, team As String, Optional includeMatchups As Boolean = True) As String
        Try
            Dim narrative As New Text.StringBuilder()

            ' Get team injuries
            Dim injuries = GetTeamInjuries(sport, team)

            ' Header
            narrative.AppendLine($"🏥 **{team.ToUpper()} INJURY REPORT & MATCHUP ANALYSIS**")
            narrative.AppendLine()

            If injuries.Rows.Count = 0 Then
                narrative.AppendLine("✅ **CLEAN BILL OF HEALTH**")
                narrative.AppendLine("No significant injuries reported. Full strength roster provides betting edge.")
            Else
                ' Injury summary
                Dim severityAvg = injuries.AsEnumerable().Average(Function(r) Convert.ToInt32(r("Severity")))
                Dim keyInjuries = injuries.AsEnumerable().Where(Function(r) Convert.ToDouble(r("ImpactWeight")) > 0.15)

                narrative.AppendLine($"⚠️ **INJURY CONCERNS** (Avg Severity: {severityAvg:F1}/5)")

                For Each injury In keyInjuries.Take(3)
                    Dim player = injury("Player").ToString()
                    Dim status = injury("Status").ToString()
                    Dim position = injury("Position").ToString()
                    Dim signal = injury("MonetizationSignal").ToString()

                    narrative.AppendLine($"• **{player}** ({position}) - {status} 🚨 {signal}")
                Next

                ' Impact assessment
                Dim totalImpact = injuries.AsEnumerable().Sum(Function(r) Convert.ToDouble(r("AdjustmentFactor")))
                If Math.Abs(totalImpact) > 0.1 Then
                    narrative.AppendLine()
                    narrative.AppendLine($"📊 **BETTING IMPACT:** {If(totalImpact < 0, "NEGATIVE", "NEUTRAL")} ({totalImpact:F2})")
                    narrative.AppendLine("Consider injury-adjusted projections for value betting.")
                End If
            End If

            ' Matchups section (if requested)
            If includeMatchups Then
                Dim recentMatchups = GetRecentMatchups(sport, team, 7)
                If recentMatchups.Rows.Count > 0 Then
                    narrative.AppendLine()
                    narrative.AppendLine("🥊 **KEY MATCHUPS:**")

                    For Each matchup In recentMatchups.AsEnumerable().Take(3)
                        Dim entityA = matchup("EntityA").ToString()
                        Dim entityB = matchup("EntityB").ToString()
                        Dim factor = matchup("Factor").ToString()
                        Dim weight = Convert.ToDouble(matchup("Weight"))
                        Dim advantage = If(weight > 0, entityA, entityB)

                        narrative.AppendLine($"• {entityA} vs {entityB}")
                        narrative.AppendLine($"  Factor: {factor} | Edge: **{advantage}** ({Math.Abs(weight):F2})")
                    Next
                End If
            End If

            ' Monetization CTA
            narrative.AppendLine()
            narrative.AppendLine("💡 **SHARP INSIGHT:**")
            narrative.AppendLine("Injury reports and matchup edges are where smart money gets made.")
            narrative.AppendLine("[Get Full Analysis]({{premium_link}}) | [Track Updates]({{alerts_link}})")

            Return narrative.ToString()

        Catch ex As Exception
            Console.WriteLine($"❌ Narrative generation failed: {ex.Message}")
            Return $"Injury and matchup analysis available for {team}."
        End Try
    End Function

    ''' <summary>
    ''' Get team injury summary statistics for dashboard/reports
    ''' </summary>
    ''' <param name="sport">Sport identifier</param>
    ''' <param name="teams">List of teams to analyze</param>
    ''' <returns>DataTable with team injury summaries</returns>
    Public Function GetTeamInjurySummary(sport As String, teams As List(Of String)) As DataTable
        Try
            Dim dt As New DataTable()
            dt.Columns.Add("Team", GetType(String))
            dt.Columns.Add("ActiveInjuries", GetType(Integer))
            dt.Columns.Add("AvgSeverity", GetType(Double))
            dt.Columns.Add("KeyPlayersOut", GetType(Integer))
            dt.Columns.Add("ImpactScore", GetType(Double))
            dt.Columns.Add("HealthRank", GetType(String))
            dt.Columns.Add("BettingEdge", GetType(String))

            For Each team In teams
                Dim injuries = GetTeamInjuries(sport, team)

                If injuries.Rows.Count = 0 Then
                    dt.Rows.Add(team, 0, 0, 0, 0, "EXCELLENT", "FULL_STRENGTH")
                Else
                    Dim activeCount = injuries.Rows.Count
                    Dim avgSeverity = injuries.AsEnumerable().Average(Function(r) Convert.ToInt32(r("Severity")))
                    Dim keyPlayersOut = injuries.AsEnumerable().Count(Function(r) Convert.ToDouble(r("ImpactWeight")) > 0.15)
                    Dim impactScore = injuries.AsEnumerable().Sum(Function(r) Convert.ToDouble(r("AdjustmentFactor")))

                    Dim healthRank = GetHealthRank(avgSeverity, keyPlayersOut)
                    Dim bettingEdge = GetBettingEdge(impactScore, avgSeverity)

                    dt.Rows.Add(team, activeCount, Math.Round(avgSeverity, 2), keyPlayersOut,
                               Math.Round(impactScore, 3), healthRank, bettingEdge)
                End If
            Next

            Return dt

        Catch ex As Exception
            Console.WriteLine($"❌ Team injury summary failed: {ex.Message}")
            LogError("GetTeamInjurySummary", ex.Message, sport)
            Return New DataTable()
        End Try
    End Function

    ''' <summary>
    ''' Generate injury-based betting recommendations
    ''' </summary>
    ''' <param name="sport">Sport identifier</param>
    ''' <param name="gameDate">Date of games to analyze</param>
    ''' <returns>List of betting recommendations based on injuries</returns>
    Public Function GenerateInjuryBettingRecommendations(sport As String, gameDate As DateTime) As List(Of InjuryBettingRec)
        Try
            Dim recommendations As New List(Of InjuryBettingRec)()

            ' This would integrate with your odds/games data
            ' For now, return sample structure

            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                ' Get teams with significant injuries
                Using cmd As New SQLiteCommand("
                    SELECT team, COUNT(*) as injury_count, AVG(severity) as avg_severity
                    FROM injuries
                    WHERE sport = @sport
                    AND ts >= datetime('now', '-7 days')
                    AND severity >= 3
                    GROUP BY team
                    HAVING injury_count >= 2 OR avg_severity >= 3.5", conn)

                    cmd.Parameters.AddWithValue("@sport", sport.ToUpper())

                    Using reader = cmd.ExecuteReader()
                        While reader.Read()
                            Dim team = reader("team").ToString()
                            Dim injuryCount = Convert.ToInt32(reader("injury_count"))
                            Dim avgSeverity = Convert.ToDouble(reader("avg_severity"))

                            ' Generate recommendation
                            Dim rec As New InjuryBettingRec With {
                                .Team = team,
                                .RecommendationType = "FADE",
                                .Confidence = CalculateConfidence(injuryCount, avgSeverity),
                                .Reasoning = $"Significant injuries (Count: {injuryCount}, Severity: {avgSeverity:F1})",
                                .Edges = New List(Of String) From {"UNDER_TEAM_TOTAL", "OPPONENT_SPREAD"},
                                .Sport = sport
                            }

                            recommendations.Add(rec)
                        End While
                    End Using
                End Using
            End Using

            Return recommendations

        Catch ex As Exception
            Console.WriteLine($"❌ Injury betting recommendations failed: {ex.Message}")
            Return New List(Of InjuryBettingRec)()
        End Try
    End Function

    ' Helper methods
    Private Function DeterminePosition(player As String, notes As String, sport As String) As String
        ' Simple position detection based on notes or player name patterns
        ' In production, this would connect to roster/player databases

        Select Case sport.ToUpper()
            Case "NFL"
                If notes.Contains("QB") OrElse notes.Contains("quarterback") Then Return "QB"
                If notes.Contains("RB") OrElse notes.Contains("running back") Then Return "RB"
                If notes.Contains("WR") OrElse notes.Contains("wide receiver") Then Return "WR"
                If notes.Contains("TE") OrElse notes.Contains("tight end") Then Return "TE"
                Return "UNKNOWN"

            Case "NBA", "WNBA"
                If notes.Contains("PG") OrElse notes.Contains("point guard") Then Return "PG"
                If notes.Contains("SG") OrElse notes.Contains("shooting guard") Then Return "SG"
                If notes.Contains("SF") OrElse notes.Contains("small forward") Then Return "SF"
                If notes.Contains("PF") OrElse notes.Contains("power forward") Then Return "PF"
                If notes.Contains("C") OrElse notes.Contains("center") Then Return "C"
                Return "UNKNOWN"

            Case Else
                Return "UNKNOWN"
        End Select
    End Function

    Private Function GetPositionWeight(position As String, sport As String) As Double
        Select Case sport.ToUpper()
            Case "NFL"
                Return If(NFL_POSITION_WEIGHTS.ContainsKey(position), NFL_POSITION_WEIGHTS(position), 0.05)
            Case "NBA", "WNBA"
                Return If(NBA_POSITION_WEIGHTS.ContainsKey(position), NBA_POSITION_WEIGHTS(position), 0.15)
            Case Else
                Return 0.1 ' Default weight
        End Select
    End Function

    Private Function CalculateInjuryAdjustmentFactor(severity As Integer, impactWeight As Double) As Double
        ' Factor ranges from 0 (severe impact) to 0 (no impact)
        ' Negative values indicate negative impact on team performance
        Dim severityFactor = (5 - severity) / 5.0 ' Higher severity = more negative
        Dim weightedImpact = -(severity * impactWeight) / 5.0

        Return Math.Round(weightedImpact, 4)
    End Function

    Private Function GenerateInjuryMonetizationSignal(severity As Integer, impactWeight As Double, daysOut As Integer) As String
        If severity >= 4 AndAlso impactWeight > 0.2 Then
            Return "MAJOR_IMPACT"
        ElseIf severity >= 3 AndAlso impactWeight > 0.15 Then
            Return "SIGNIFICANT_CONCERN"
        ElseIf daysOut > 7 AndAlso severity >= 2 Then
            Return "EXTENDED_ABSENCE"
        ElseIf severity >= 2 Then
            Return "MONITOR_CLOSELY"
        Else
            Return "MINOR_ISSUE"
        End If
    End Function

    Private Function GetRecentMatchups(sport As String, team As String, days As Integer) As DataTable
        Dim dt As New DataTable()
        dt.Columns.Add("EntityA", GetType(String))
        dt.Columns.Add("EntityB", GetType(String))
        dt.Columns.Add("Factor", GetType(String))
        dt.Columns.Add("Weight", GetType(Double))

        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand($"
                    SELECT entity_a, entity_b, factor, model_weight
                    FROM matchups
                    WHERE sport = @sport
                    AND (entity_a LIKE '%{team}%' OR entity_b LIKE '%{team}%')
                    AND ts >= datetime('now', '-{days} days')
                    ORDER BY ABS(model_weight) DESC", conn)

                    cmd.Parameters.AddWithValue("@sport", sport.ToUpper())

                    Using reader = cmd.ExecuteReader()
                        While reader.Read()
                            dt.Rows.Add(
                                reader("entity_a").ToString(),
                                reader("entity_b").ToString(),
                                reader("factor").ToString(),
                                Convert.ToDouble(reader("model_weight"))
                            )
                        End While
                    End Using
                End Using
            End Using
        Catch ex As Exception
            Console.WriteLine($"❌ Get recent matchups failed: {ex.Message}")
        End Try

        Return dt
    End Function

    Private Function GetHealthRank(avgSeverity As Double, keyPlayersOut As Integer) As String
        If avgSeverity <= 1.5 AndAlso keyPlayersOut = 0 Then
            Return "EXCELLENT"
        ElseIf avgSeverity <= 2.5 AndAlso keyPlayersOut <= 1 Then
            Return "GOOD"
        ElseIf avgSeverity <= 3.5 AndAlso keyPlayersOut <= 2 Then
            Return "FAIR"
        Else
            Return "POOR"
        End If
    End Function

    Private Function GetBettingEdge(impactScore As Double, avgSeverity As Double) As String
        If impactScore < -0.15 Then
            Return "FADE_TEAM"
        ElseIf impactScore < -0.05 Then
            Return "CAUTION"
        ElseIf avgSeverity < 1.5 Then
            Return "FULL_STRENGTH"
        Else
            Return "NEUTRAL"
        End If
    End Function

    Private Function CalculateConfidence(injuryCount As Integer, avgSeverity As Double) As Double
        ' Confidence ranges from 0.5 to 0.95
        Dim baseConfidence = 0.5
        Dim severityBoost = (avgSeverity - 1) * 0.1
        Dim countBoost = Math.Min(injuryCount * 0.05, 0.25)

        Return Math.Min(0.95, baseConfidence + severityBoost + countBoost)
    End Function

    Private Sub InitializeInjuryTables()
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                ' Injuries table
                Using cmd As New SQLiteCommand("
                    CREATE TABLE IF NOT EXISTS injuries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts TEXT DEFAULT (datetime('now')),
                        sport TEXT,
                        team TEXT,
                        player TEXT,
                        status TEXT,
                        severity INTEGER,
                        source TEXT,
                        notes TEXT
                    )", conn)
                    cmd.ExecuteNonQuery()
                End Using

                ' Matchups table
                Using cmd As New SQLiteCommand("
                    CREATE TABLE IF NOT EXISTS matchups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts TEXT DEFAULT (datetime('now')),
                        sport TEXT,
                        entity_a TEXT,
                        entity_b TEXT,
                        type TEXT,
                        factor TEXT,
                        model_weight REAL,
                        source TEXT,
                        notes TEXT
                    )", conn)
                    cmd.ExecuteNonQuery()
                End Using

                ' Create indexes
                Using cmd As New SQLiteCommand("CREATE INDEX IF NOT EXISTS idx_injuries_sport_team ON injuries(sport, team)", conn)
                    cmd.ExecuteNonQuery()
                End Using

                Using cmd As New SQLiteCommand("CREATE INDEX IF NOT EXISTS idx_matchups_sport ON matchups(sport)", conn)
                    cmd.ExecuteNonQuery()
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"❌ Injury tables initialization failed: {ex.Message}")
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
                    cmd.Parameters.AddWithValue("@component", "InjuriesEngine")
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

''' <summary>
''' Injury-based betting recommendation structure
''' </summary>
Public Class InjuryBettingRec
    Public Property Team As String
    Public Property RecommendationType As String ' FADE, BACK, CAUTION
    Public Property Confidence As Double ' 0.0 to 1.0
    Public Property Reasoning As String
    Public Property Edges As List(Of String) ' Specific betting edges
    Public Property Sport As String
End Class
