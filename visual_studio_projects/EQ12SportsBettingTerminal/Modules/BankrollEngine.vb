Imports System.Threading.Tasks
Imports System.Data
Imports System.Data.SQLite
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.Collections.Generic

''' <summary>
''' Strict Bankroll Management & Staking Engine for EQ12
''' Implements Kelly Criterion, Unit System, and non-negotiable discipline rules
''' Prevents tilt betting and enforces professional staking protocols
''' </summary>
Public Class BankrollEngine
    Private ReadOnly _dbPath As String
    Private ReadOnly _config As JObject

    ' Discipline rules (non-negotiable)
    Public Shared ReadOnly MAX_DAILY_EXPOSURE_PCT As Double = 10.0 ' % of bankroll
    Public Shared ReadOnly MAX_SINGLE_STAKE_PCT As Double = 3.0 ' % of bankroll
    Public Shared ReadOnly CONSECUTIVE_LOSS_LOCKOUT As Integer = 5 ' Games
    Public Shared ReadOnly MIN_BANKROLL_FOR_BETTING As Double = 100.0 ' Minimum bankroll
    Public Shared ReadOnly KELLY_SAFETY_CAP As Double = 0.05 ' Max 5% even if Kelly suggests more

    ' Kelly fraction presets
    Public Shared ReadOnly KELLY_FRACTIONS As Dictionary(Of String, Double) = New Dictionary(Of String, Double) From {
        {"full", 1.0}, {"half", 0.5}, {"quarter", 0.25}, {"eighth", 0.125}, {"conservative", 0.1}
    }

    ' Unit system presets
    Public Shared ReadOnly UNIT_PERCENTAGES As Dictionary(Of String, Double) = New Dictionary(Of String, Double) From {
        {"conservative", 0.01}, {"standard", 0.02}, {"aggressive", 0.03}, {"degen", 0.05}
    }

    Public Sub New(Optional dbPath As String = "", Optional config As JObject = Nothing)
        _dbPath = If(String.IsNullOrEmpty(dbPath), "Data/eq12_terminal.db", dbPath)
        _config = config

        ' Initialize bankroll and staking tables
        InitializeBankrollTables()

        ' Ensure default bankroll exists
        EnsureDefaultBankroll()
    End Sub

    ''' <summary>
    ''' Convert American odds to decimal format
    ''' </summary>
    ''' <param name="americanOdds">American odds format (+100, -110, etc.)</param>
    ''' <returns>Decimal odds</returns>
    Public Function DecimalFromAmerican(americanOdds As Integer) As Double
        Try
            If americanOdds > 0 Then
                Return 1 + (americanOdds / 100.0)
            Else
                Return 1 + (100.0 / Math.Abs(americanOdds))
            End If
        Catch ex As Exception
            Console.WriteLine($"❌ Decimal conversion failed: {ex.Message}")
            Return 2.0 ' Default to even odds
        End Try
    End Function

    ''' <summary>
    ''' Calculate full Kelly Criterion percentage
    ''' </summary>
    ''' <param name="decimalOdds">Decimal odds (e.g., 2.1 for +110)</param>
    ''' <param name="winProbability">Model's estimated win probability (0-1)</param>
    ''' <returns>Kelly percentage (0-1)</returns>
    Public Function KellyFull(decimalOdds As Double, winProbability As Double) As Double
        Try
            If decimalOdds <= 1.0 Or winProbability <= 0 Or winProbability >= 1 Then
                Return 0.0 ' Invalid inputs
            End If

            Dim b = decimalOdds - 1 ' Net odds (profit per unit staked)
            Dim p = winProbability
            Dim q = 1 - winProbability

            ' Kelly formula: f* = (bp - q) / b
            Dim kellyFraction = (b * p - q) / b

            ' Return 0 if negative (no edge)
            Return Math.Max(0, kellyFraction)

        Catch ex As Exception
            Console.WriteLine($"❌ Kelly calculation failed: {ex.Message}")
            Return 0.0
        End Try
    End Function

    ''' <summary>
    ''' Calculate Kelly stake amount with safety caps and discipline rules
    ''' </summary>
    ''' <param name="balance">Current bankroll balance</param>
    ''' <param name="decimalOdds">Decimal odds</param>
    ''' <param name="winProbability">Model win probability</param>
    ''' <param name="fraction">Kelly fraction (0.25 for quarter-Kelly)</param>
    ''' <param name="bankrollName">Bankroll account name</param>
    ''' <returns>Recommended stake amount</returns>
    Public Function KellyStake(balance As Double, decimalOdds As Double, winProbability As Double,
                              fraction As Double, Optional bankrollName As String = "Main") As Double
        Try
            ' Discipline check: minimum bankroll
            If balance < MIN_BANKROLL_FOR_BETTING Then
                Console.WriteLine($"⚠️ Bankroll below minimum (${balance:F2} < ${MIN_BANKROLL_FOR_BETTING:F2})")
                Return 0.0
            End If

            ' Calculate full Kelly
            Dim kellyFull = Me.KellyFull(decimalOdds, winProbability)

            If kellyFull = 0 Then
                Console.WriteLine($"⚠️ No edge detected (Kelly = {kellyFull:F4})")
                Return 0.0
            End If

            ' Apply fraction
            Dim kellyFractional = kellyFull * fraction

            ' Apply safety cap (max 5% of bankroll regardless of Kelly)
            kellyFractional = Math.Min(kellyFractional, KELLY_SAFETY_CAP)

            ' Apply single stake limit
            kellyFractional = Math.Min(kellyFractional, MAX_SINGLE_STAKE_PCT / 100.0)

            ' Calculate stake
            Dim stake = balance * kellyFractional

            ' Check daily exposure limits
            If Not CheckDailyExposureLimit(stake, bankrollName) Then
                Console.WriteLine($"⚠️ Daily exposure limit exceeded - bet rejected")
                Return 0.0
            End If

            ' Check consecutive loss lockout
            If CheckConsecutiveLossLockout(bankrollName) Then
                Console.WriteLine($"⚠️ Consecutive loss lockout active - bet rejected")
                Return 0.0
            End If

            Return Math.Round(stake, 2)

        Catch ex As Exception
            Console.WriteLine($"❌ Kelly stake calculation failed: {ex.Message}")
            Return 0.0
        End Try
    End Function

    ''' <summary>
    ''' Calculate unit-based stake amount
    ''' </summary>
    ''' <param name="balance">Current bankroll balance</param>
    ''' <param name="unitPercentage">Unit size as percentage of bankroll</param>
    ''' <param name="units">Number of units to stake (1-5)</param>
    ''' <param name="bankrollName">Bankroll account name</param>
    ''' <returns>Stake amount</returns>
    Public Function UnitStake(balance As Double, unitPercentage As Double, units As Integer,
                             Optional bankrollName As String = "Main") As Double
        Try
            ' Validate inputs
            If balance < MIN_BANKROLL_FOR_BETTING Then
                Console.WriteLine($"⚠️ Bankroll below minimum (${balance:F2} < ${MIN_BANKROLL_FOR_BETTING:F2})")
                Return 0.0
            End If

            If units < 1 Or units > 5 Then
                Console.WriteLine($"⚠️ Invalid unit count ({units}). Must be 1-5.")
                Return 0.0
            End If

            If unitPercentage < 0.005 Or unitPercentage > 0.05 Then
                Console.WriteLine($"⚠️ Invalid unit percentage ({unitPercentage:F3}). Must be 0.5%-5%.")
                Return 0.0
            End If

            ' Calculate unit size
            Dim unitSize = balance * unitPercentage
            Dim totalStake = unitSize * units

            ' Apply safety caps
            Dim maxStake = balance * (MAX_SINGLE_STAKE_PCT / 100.0)
            totalStake = Math.Min(totalStake, maxStake)

            ' Check daily exposure limits
            If Not CheckDailyExposureLimit(totalStake, bankrollName) Then
                Console.WriteLine($"⚠️ Daily exposure limit exceeded - bet rejected")
                Return 0.0
            End If

            ' Check consecutive loss lockout
            If CheckConsecutiveLossLockout(bankrollName) Then
                Console.WriteLine($"⚠️ Consecutive loss lockout active - bet rejected")
                Return 0.0
            End If

            Return Math.Round(totalStake, 2)

        Catch ex As Exception
            Console.WriteLine($"❌ Unit stake calculation failed: {ex.Message}")
            Return 0.0
        End Try
    End Function

    ''' <summary>
    ''' Log staking decision with all parameters for analysis
    ''' </summary>
    ''' <param name="eventId">Event identifier</param>
    ''' <param name="market">Market type (moneyline, spread, total)</param>
    ''' <param name="selection">Specific selection</param>
    ''' <param name="decimalOdds">Decimal odds</param>
    ''' <param name="edge">Calculated edge/EV</param>
    ''' <param name="winProbability">Model win probability</param>
    ''' <param name="fraction">Kelly fraction used</param>
    ''' <param name="mode">Staking mode (kelly, units)</param>
    ''' <param name="units">Units staked (if using unit system)</param>
    ''' <param name="unitPercentage">Unit percentage (if using unit system)</param>
    ''' <param name="bankrollName">Bankroll account name</param>
    ''' <param name="notes">Additional notes</param>
    Public Sub LogStake(eventId As String, market As String, selection As String, decimalOdds As Double,
                       edge As Double, winProbability As Double, fraction As Double, mode As String,
                       units As Integer, unitPercentage As Double, bankrollName As String, notes As String)
        Try
            Dim currentBalance = GetCurrentBalance(bankrollName)
            Dim kellyFull = KellyFull(decimalOdds, winProbability)
            Dim kellyFractional = kellyFull * fraction

            Dim actualStake = If(mode.ToLower() = "kelly",
                                KellyStake(currentBalance, decimalOdds, winProbability, fraction, bankrollName),
                                UnitStake(currentBalance, unitPercentage, units, bankrollName))

            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand("
                    INSERT INTO staking_log (
                        ts, event_id, market, selection, decimal_odds, edge, p, q,
                        kelly_full, kelly_fraction, stake, mode, units, unit_size,
                        bankroll_name, notes
                    ) VALUES (
                        datetime('now'), @event_id, @market, @selection, @decimal_odds, @edge, @p, @q,
                        @kelly_full, @kelly_fraction, @stake, @mode, @units, @unit_size,
                        @bankroll_name, @notes
                    )", conn)

                    cmd.Parameters.AddWithValue("@event_id", eventId)
                    cmd.Parameters.AddWithValue("@market", market)
                    cmd.Parameters.AddWithValue("@selection", selection)
                    cmd.Parameters.AddWithValue("@decimal_odds", decimalOdds)
                    cmd.Parameters.AddWithValue("@edge", edge)
                    cmd.Parameters.AddWithValue("@p", winProbability)
                    cmd.Parameters.AddWithValue("@q", 1 - winProbability)
                    cmd.Parameters.AddWithValue("@kelly_full", kellyFull)
                    cmd.Parameters.AddWithValue("@kelly_fraction", kellyFractional)
                    cmd.Parameters.AddWithValue("@stake", actualStake)
                    cmd.Parameters.AddWithValue("@mode", mode)
                    cmd.Parameters.AddWithValue("@units", units)
                    cmd.Parameters.AddWithValue("@unit_size", currentBalance * unitPercentage)
                    cmd.Parameters.AddWithValue("@bankroll_name", bankrollName)
                    cmd.Parameters.AddWithValue("@notes", notes)

                    cmd.ExecuteNonQuery()
                End Using
            End Using

            Console.WriteLine($"✅ Logged stake: ${actualStake:F2} on {selection} ({mode})")

        Catch ex As Exception
            Console.WriteLine($"❌ Stake logging failed: {ex.Message}")
            LogError("LogStake", ex.Message, $"{eventId}_{selection}")
        End Try
    End Sub

    ''' <summary>
    ''' Get current bankroll balance
    ''' </summary>
    ''' <param name="bankrollName">Bankroll account name</param>
    ''' <returns>Current balance</returns>
    Public Function GetCurrentBalance(Optional bankrollName As String = "Main") As Double
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand("
                    SELECT balance
                    FROM bankroll
                    WHERE name = @name
                    ORDER BY ts DESC
                    LIMIT 1", conn)

                    cmd.Parameters.AddWithValue("@name", bankrollName)

                    Dim result = cmd.ExecuteScalar()
                    Return If(result IsNot Nothing, Convert.ToDouble(result), 0.0)
                End Using
            End Using
        Catch ex As Exception
            Console.WriteLine($"❌ Get balance failed: {ex.Message}")
            Return 0.0
        End Try
    End Function

    ''' <summary>
    ''' Update bankroll balance
    ''' </summary>
    ''' <param name="newBalance">New balance amount</param>
    ''' <param name="bankrollName">Bankroll account name</param>
    ''' <param name="reason">Reason for update</param>
    Public Sub UpdateBalance(newBalance As Double, Optional bankrollName As String = "Main", Optional reason As String = "Manual update")
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand("
                    INSERT INTO bankroll (ts, name, balance, notes)
                    VALUES (datetime('now'), @name, @balance, @reason)", conn)

                    cmd.Parameters.AddWithValue("@name", bankrollName)
                    cmd.Parameters.AddWithValue("@balance", newBalance)
                    cmd.Parameters.AddWithValue("@reason", reason)

                    cmd.ExecuteNonQuery()
                End Using
            End Using

            Console.WriteLine($"✅ Updated {bankrollName} bankroll: ${newBalance:F2} ({reason})")

        Catch ex As Exception
            Console.WriteLine($"❌ Balance update failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Get comprehensive bankroll status and discipline metrics
    ''' </summary>
    ''' <param name="bankrollName">Bankroll to analyze</param>
    ''' <param name="lookbackDays">Days to analyze</param>
    ''' <returns>Bankroll status report</returns>
    Public Function GetBankrollStatus(Optional bankrollName As String = "Main", Optional lookbackDays As Integer = 7) As BankrollStatus
        Try
            Dim status As New BankrollStatus()
            status.BankrollName = bankrollName
            status.LookbackDays = lookbackDays
            status.CurrentBalance = GetCurrentBalance(bankrollName)

            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                ' Get recent staking activity
                Using cmd As New SQLiteCommand($"
                    SELECT
                        COUNT(*) as total_stakes,
                        SUM(stake) as total_staked,
                        AVG(stake) as avg_stake,
                        MAX(stake) as max_stake,
                        AVG(kelly_full) as avg_kelly,
                        COUNT(CASE WHEN mode = 'kelly' THEN 1 END) as kelly_bets,
                        COUNT(CASE WHEN mode = 'units' THEN 1 END) as unit_bets
                    FROM staking_log
                    WHERE bankroll_name = @name
                    AND ts >= datetime('now', '-{lookbackDays} days')", conn)

                    cmd.Parameters.AddWithValue("@name", bankrollName)

                    Using reader = cmd.ExecuteReader()
                        If reader.Read() Then
                            status.TotalStakes = Convert.ToInt32(reader("total_stakes"))
                            status.TotalStaked = If(reader("total_staked") IsNot DBNull.Value, Convert.ToDouble(reader("total_staked")), 0)
                            status.AverageStake = If(reader("avg_stake") IsNot DBNull.Value, Convert.ToDouble(reader("avg_stake")), 0)
                            status.MaxStake = If(reader("max_stake") IsNot DBNull.Value, Convert.ToDouble(reader("max_stake")), 0)
                            status.AverageKelly = If(reader("avg_kelly") IsNot DBNull.Value, Convert.ToDouble(reader("avg_kelly")), 0)
                            status.KellyBets = Convert.ToInt32(reader("kelly_bets"))
                            status.UnitBets = Convert.ToInt32(reader("unit_bets"))
                        End If
                    End Using
                End Using

                ' Calculate exposure percentage
                status.DailyExposurePercentage = If(status.CurrentBalance > 0, (status.TotalStaked / status.CurrentBalance) * 100, 0)

                ' Check discipline violations
                status.DisciplineViolations = GetDisciplineViolations(bankrollName, lookbackDays)

                ' Get win/loss streak
                status.CurrentStreak = GetCurrentStreak(bankrollName)

                ' Calculate bankroll health score
                status.HealthScore = CalculateBankrollHealthScore(status)
            End Using

            Return status

        Catch ex As Exception
            Console.WriteLine($"❌ Bankroll status failed: {ex.Message}")
            Return New BankrollStatus() With {.BankrollName = bankrollName, .CurrentBalance = 0}
        End Try
    End Function

    ''' <summary>
    ''' Generate bankroll narrative for reports and content
    ''' </summary>
    ''' <param name="bankrollName">Bankroll to analyze</param>
    ''' <returns>Monetization-ready narrative</returns>
    Public Function GenerateBankrollNarrative(Optional bankrollName As String = "Main") As String
        Try
            Dim status = GetBankrollStatus(bankrollName)
            Dim narrative As New Text.StringBuilder()

            narrative.AppendLine($"💰 **BANKROLL DISCIPLINE REPORT**")
            narrative.AppendLine($"Account: {status.BankrollName}")
            narrative.AppendLine()

            ' Current status
            narrative.AppendLine($"💵 **Current Balance:** ${status.CurrentBalance:F2}")
            narrative.AppendLine($"📊 **{status.LookbackDays}d Exposure:** {status.DailyExposurePercentage:F1}% of bankroll")
            narrative.AppendLine($"🎯 **Avg Stake:** ${status.AverageStake:F2} | Max: ${status.MaxStake:F2}")
            narrative.AppendLine()

            ' Discipline assessment
            If status.DisciplineViolations.Count = 0 Then
                narrative.AppendLine("✅ **DISCIPLINE: EXCELLENT**")
                narrative.AppendLine("All staking rules followed. Professional money management.")
            Else
                narrative.AppendLine("⚠️ **DISCIPLINE VIOLATIONS:**")
                For Each violation In status.DisciplineViolations.Take(3)
                    narrative.AppendLine($"   • {violation}")
                Next
            End If

            ' Kelly vs Units breakdown
            If status.KellyBets > 0 OrElse status.UnitBets > 0 Then
                narrative.AppendLine()
                narrative.AppendLine($"📈 **STAKING METHOD:** {status.KellyBets} Kelly | {status.UnitBets} Units")
                narrative.AppendLine($"⚖️ **Avg Kelly:** {status.AverageKelly:F3} (Full Kelly)")
            End If

            ' Health score and advice
            narrative.AppendLine()
            Select Case status.HealthScore
                Case >= 90
                    narrative.AppendLine("🟢 **BANKROLL HEALTH: EXCELLENT** (90+)")
                    narrative.AppendLine("Perfect discipline and sustainable staking.")
                Case >= 70
                    narrative.AppendLine("🟡 **BANKROLL HEALTH: GOOD** (70-89)")
                    narrative.AppendLine("Solid management with room for improvement.")
                Case >= 50
                    narrative.AppendLine("🟠 **BANKROLL HEALTH: FAIR** (50-69)")
                    narrative.AppendLine("Some discipline issues. Review staking rules.")
                Case Else
                    narrative.AppendLine("🔴 **BANKROLL HEALTH: POOR** (<50)")
                    narrative.AppendLine("Serious discipline problems. Immediate intervention needed.")
            End Select

            ' Professional tip
            narrative.AppendLine()
            narrative.AppendLine("💡 **PRO TIP:**")
            narrative.AppendLine("Fractional Kelly + unit discipline = variance survival.")
            narrative.AppendLine("This is how pros stay profitable long-term.")
            narrative.AppendLine()
            narrative.AppendLine("[Learn More]({{education_link}}) | [Premium Analysis]({{premium_link}})")

            Return narrative.ToString()

        Catch ex As Exception
            Console.WriteLine($"❌ Bankroll narrative generation failed: {ex.Message}")
            Return $"Bankroll discipline analysis available for {bankrollName}."
        End Try
    End Function

    ' Helper methods for discipline enforcement
    Private Function CheckDailyExposureLimit(newStake As Double, bankrollName As String) As Boolean
        Try
            Dim currentBalance = GetCurrentBalance(bankrollName)
            Dim todayStaked = GetTodayTotalStaked(bankrollName)
            Dim totalExposure = (todayStaked + newStake) / currentBalance * 100

            Return totalExposure <= MAX_DAILY_EXPOSURE_PCT
        Catch
            Return False ' Err on side of caution
        End Try
    End Function

    Private Function CheckConsecutiveLossLockout(bankrollName As String) As Boolean
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                ' This would require bet result tracking (win/loss)
                ' For now, return False (no lockout)
                ' In production, integrate with bet result tracking
                Return False
            End Using
        Catch
            Return True ' Err on side of caution
        End Try
    End Function

    Private Function GetTodayTotalStaked(bankrollName As String) As Double
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Using cmd As New SQLiteCommand("
                    SELECT COALESCE(SUM(stake), 0) as total
                    FROM staking_log
                    WHERE bankroll_name = @name
                    AND DATE(ts) = DATE('now')", conn)

                    cmd.Parameters.AddWithValue("@name", bankrollName)

                    Dim result = cmd.ExecuteScalar()
                    Return If(result IsNot Nothing, Convert.ToDouble(result), 0.0)
                End Using
            End Using
        Catch
            Return 0.0
        End Try
    End Function

    Private Function GetDisciplineViolations(bankrollName As String, lookbackDays As Integer) As List(Of String)
        Dim violations As New List(Of String)()

        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                ' Check for stakes exceeding single stake limit
                Using cmd As New SQLiteCommand($"
                    SELECT COUNT(*) as violation_count
                    FROM staking_log s
                    JOIN bankroll b ON b.name = s.bankroll_name
                    WHERE s.bankroll_name = @name
                    AND s.ts >= datetime('now', '-{lookbackDays} days')
                    AND s.stake > (b.balance * {MAX_SINGLE_STAKE_PCT / 100.0})
                    AND ABS(julianday(s.ts) - julianday(b.ts)) < 1", conn)

                    cmd.Parameters.AddWithValue("@name", bankrollName)

                    Dim violationCount = Convert.ToInt32(cmd.ExecuteScalar())
                    If violationCount > 0 Then
                        violations.Add($"Exceeded single stake limit {violationCount} times")
                    End If
                End Using

                ' Check for days exceeding daily exposure limit
                Using cmd As New SQLiteCommand($"
                    SELECT COUNT(*) as violation_days
                    FROM (
                        SELECT DATE(ts) as bet_date, SUM(stake) as daily_total
                        FROM staking_log
                        WHERE bankroll_name = @name
                        AND ts >= datetime('now', '-{lookbackDays} days')
                        GROUP BY DATE(ts)
                    ) daily
                    WHERE daily_total > ({GetCurrentBalance(bankrollName)} * {MAX_DAILY_EXPOSURE_PCT / 100.0})", conn)

                    cmd.Parameters.AddWithValue("@name", bankrollName)

                    Dim violationDays = Convert.ToInt32(cmd.ExecuteScalar())
                    If violationDays > 0 Then
                        violations.Add($"Exceeded daily exposure limit on {violationDays} days")
                    End If
                End Using
            End Using
        Catch ex As Exception
            violations.Add($"Unable to check violations: {ex.Message}")
        End Try

        Return violations
    End Function

    Private Function GetCurrentStreak(bankrollName As String) As String
        ' This would require bet result tracking
        ' Placeholder for now
        Return "N/A (requires bet result tracking)"
    End Function

    Private Function CalculateBankrollHealthScore(status As BankrollStatus) As Double
        Dim score = 100.0

        ' Deduct for discipline violations
        score -= status.DisciplineViolations.Count * 15

        ' Deduct for excessive exposure
        If status.DailyExposurePercentage > MAX_DAILY_EXPOSURE_PCT Then
            score -= (status.DailyExposurePercentage - MAX_DAILY_EXPOSURE_PCT) * 2
        End If

        ' Deduct for excessive average stake
        Dim avgStakePct = If(status.CurrentBalance > 0, (status.AverageStake / status.CurrentBalance) * 100, 0)
        If avgStakePct > MAX_SINGLE_STAKE_PCT Then
            score -= (avgStakePct - MAX_SINGLE_STAKE_PCT) * 5
        End If

        ' Bonus for using Kelly (disciplined approach)
        If status.KellyBets > status.UnitBets AndAlso status.AverageKelly > 0 AndAlso status.AverageKelly < 0.05 Then
            score += 10 ' Bonus for conservative Kelly usage
        End If

        Return Math.Max(0, Math.Min(100, score))
    End Function

    Private Sub EnsureDefaultBankroll()
        Try
            Dim currentBalance = GetCurrentBalance("Main")
            If currentBalance = 0 Then
                UpdateBalance(1000.0, "Main", "Initial default bankroll")
            End If
        Catch
            ' Silent fail
        End Try
    End Sub

    Private Sub InitializeBankrollTables()
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                ' Bankroll table
                Using cmd As New SQLiteCommand("
                    CREATE TABLE IF NOT EXISTS bankroll (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts TEXT DEFAULT (datetime('now')),
                        name TEXT DEFAULT 'Main',
                        balance REAL,
                        notes TEXT
                    )", conn)
                    cmd.ExecuteNonQuery()
                End Using

                ' Staking log table
                Using cmd As New SQLiteCommand("
                    CREATE TABLE IF NOT EXISTS staking_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts TEXT DEFAULT (datetime('now')),
                        event_id TEXT,
                        market TEXT,
                        selection TEXT,
                        decimal_odds REAL,
                        edge REAL,
                        p REAL,
                        q REAL,
                        kelly_full REAL,
                        kelly_fraction REAL,
                        stake REAL,
                        mode TEXT,
                        units REAL,
                        unit_size REAL,
                        bankroll_name TEXT,
                        notes TEXT
                    )", conn)
                    cmd.ExecuteNonQuery()
                End Using

                ' Create indexes
                Using cmd As New SQLiteCommand("CREATE INDEX IF NOT EXISTS idx_bankroll_name ON bankroll(name)", conn)
                    cmd.ExecuteNonQuery()
                End Using

                Using cmd As New SQLiteCommand("CREATE INDEX IF NOT EXISTS idx_staking_bankroll ON staking_log(bankroll_name)", conn)
                    cmd.ExecuteNonQuery()
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"❌ Bankroll tables initialization failed: {ex.Message}")
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
                    cmd.Parameters.AddWithValue("@component", "BankrollEngine")
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
''' Comprehensive bankroll status structure
''' </summary>
Public Class BankrollStatus
    Public Property BankrollName As String
    Public Property CurrentBalance As Double
    Public Property LookbackDays As Integer
    Public Property TotalStakes As Integer
    Public Property TotalStaked As Double
    Public Property AverageStake As Double
    Public Property MaxStake As Double
    Public Property AverageKelly As Double
    Public Property KellyBets As Integer
    Public Property UnitBets As Integer
    Public Property DailyExposurePercentage As Double
    Public Property DisciplineViolations As List(Of String) = New List(Of String)()
    Public Property CurrentStreak As String
    Public Property HealthScore As Double
End Class
