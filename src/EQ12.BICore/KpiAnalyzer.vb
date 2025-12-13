Imports System.Data.SQLite
Imports System.IO
Imports Newtonsoft.Json

Namespace EQ12.BICore

    ''' <summary>
    ''' KPI Analyzer - Reads 120 databases for comprehensive metrics
    ''' Feeds BI-Core decision engine with revenue, bankroll, performance trends
    ''' </summary>
    Public Class KpiAnalyzer
        Implements IKpiAnalyzer

        Private ReadOnly _databaseRoot As String
        Private ReadOnly _logger As Action(Of String)

        Public Sub New(databaseRoot As String, logger As Action(Of String))
            _databaseRoot = databaseRoot
            _logger = logger
        End Sub

        Public Function GetCurrentKpiState() As KpiState Implements IKpiAnalyzer.GetCurrentKpiState
            _logger("[KpiAnalyzer] Calculating current KPI state from 120 databases")

            Dim state As New KpiState With {
                .Timestamp = DateTime.UtcNow
            }

            ' Revenue metrics
            state.Revenue7D = GetRevenueMetric(7)
            state.Revenue30D = GetRevenueMetric(30)
            state.RevenueSpiked = DetectRevenueSpike(state.Revenue7D, state.Revenue30D)

            ' Sports betting metrics
            state.SportsRoi7D = GetSportsRoi(7)
            state.SportsRoiTarget = 0.05 ' 5% target ROI
            state.SportsWinRate = GetSportsWinRate()

            ' Bankroll health
            state.BankrollBalance = GetBankrollBalance()
            state.BankrollMaxDrawdown = GetBankrollMaxDrawdown()

            ' System health
            state.SystemHealthScore = CalculateSystemHealth()
            state.ActiveModels = GetActiveModelCount()
            state.DriftDetected = CheckForDrift()

            _logger($"[KpiAnalyzer] KPI state: Revenue7D=${state.Revenue7D:N2}, ROI7D={state.SportsRoi7D:P2}, Health={state.SystemHealthScore:F2}")

            Return state
        End Function

        Private Function GetRevenueMetric(days As Integer) As Decimal
            Try
                Dim revenueDbPath = Path.Combine(_databaseRoot, "revenue.db")
                If Not File.Exists(revenueDbPath) Then
                    _logger("[KpiAnalyzer] revenue.db not found")
                    Return 0D
                End If

                Using conn As New SQLiteConnection($"Data Source={revenueDbPath};Version=3;")
                    conn.Open()

                    Dim cutoffDate = DateTime.UtcNow.AddDays(-days).ToString("yyyy-MM-dd")

                    Dim query = $"
                        SELECT COALESCE(SUM(amount), 0) 
                        FROM revenue 
                        WHERE date >= '{cutoffDate}'
                    "

                    Using cmd As New SQLiteCommand(query, conn)
                        Dim result = cmd.ExecuteScalar()
                        Return If(result IsNot Nothing AndAlso Not IsDBNull(result), Convert.ToDecimal(result), 0D)
                    End Using
                End Using

            Catch ex As Exception
                _logger($"[KpiAnalyzer] Error reading revenue: {ex.Message}")
                Return 0D
            End Try
        End Function

        Private Function DetectRevenueSpike(revenue7d As Decimal, revenue30d As Decimal) As Boolean
            If revenue30d = 0 Then Return False

            Dim avgDaily30 = revenue30d / 30D
            Dim avgDaily7 = revenue7d / 7D

            ' Spike if 7-day average is >30% higher than 30-day average
            Return avgDaily7 > (avgDaily30 * 1.3D)
        End Function

        Private Function GetSportsRoi(days As Integer) As Double
            Try
                Dim betsDbPath = Path.Combine(_databaseRoot, "eq12_bets.db")
                If Not File.Exists(betsDbPath) Then Return 0.0

                Using conn As New SQLiteConnection($"Data Source={betsDbPath};Version=3;")
                    conn.Open()

                    Dim cutoffDate = DateTime.UtcNow.AddDays(-days).ToString("yyyy-MM-dd")

                    Dim query = $"
                        SELECT 
                            COALESCE(SUM(stake), 0) as total_stake,
                            COALESCE(SUM(profit), 0) as total_profit
                        FROM bets
                        WHERE placed_at >= '{cutoffDate}' AND status = 'settled'
                    "

                    Using cmd As New SQLiteCommand(query, conn)
                        Using reader = cmd.ExecuteReader()
                            If reader.Read() Then
                                Dim totalStake = reader.GetDouble(0)
                                Dim totalProfit = reader.GetDouble(1)

                                If totalStake > 0 Then
                                    Return totalProfit / totalStake
                                End If
                            End If
                        End Using
                    End Using
                End Using

            Catch ex As Exception
                _logger($"[KpiAnalyzer] Error reading sports ROI: {ex.Message}")
            End Try

            Return 0.0
        End Function

        Private Function GetSportsWinRate() As Double
            Try
                Dim betsDbPath = Path.Combine(_databaseRoot, "eq12_bets.db")
                If Not File.Exists(betsDbPath) Then Return 0.0

                Using conn As New SQLiteConnection($"Data Source={betsDbPath};Version=3;")
                    conn.Open()

                    Dim query = "
                        SELECT 
                            COUNT(*) as total,
                            SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins
                        FROM bets
                        WHERE status = 'settled'
                    "

                    Using cmd As New SQLiteCommand(query, conn)
                        Using reader = cmd.ExecuteReader()
                            If reader.Read() Then
                                Dim total = reader.GetInt32(0)
                                Dim wins = reader.GetInt32(1)

                                If total > 0 Then
                                    Return CDbl(wins) / CDbl(total)
                                End If
                            End If
                        End Using
                    End Using
                End Using

            Catch ex As Exception
                _logger($"[KpiAnalyzer] Error reading win rate: {ex.Message}")
            End Try

            Return 0.0
        End Function

        Private Function GetBankrollBalance() As Decimal
            Try
                Dim dashboardDbPath = Path.Combine(_databaseRoot, "dashboard.db")
                If Not File.Exists(dashboardDbPath) Then Return 0D

                Using conn As New SQLiteConnection($"Data Source={dashboardDbPath};Version=3;")
                    conn.Open()

                    Dim query = "SELECT COALESCE(balance, 0) FROM bankroll ORDER BY updated_at DESC LIMIT 1"

                    Using cmd As New SQLiteCommand(query, conn)
                        Dim result = cmd.ExecuteScalar()
                        Return If(result IsNot Nothing AndAlso Not IsDBNull(result), Convert.ToDecimal(result), 0D)
                    End Using
                End Using

            Catch ex As Exception
                _logger($"[KpiAnalyzer] Error reading bankroll: {ex.Message}")
                Return 0D
            End Try
        End Function

        Private Function GetBankrollMaxDrawdown() As Double
            Try
                Dim dashboardDbPath = Path.Combine(_databaseRoot, "dashboard.db")
                If Not File.Exists(dashboardDbPath) Then Return 0.0

                Using conn As New SQLiteConnection($"Data Source={dashboardDbPath};Version=3;")
                    conn.Open()

                    Dim query = "
                        WITH balance_history AS (
                            SELECT balance, ROW_NUMBER() OVER (ORDER BY updated_at) as rn
                            FROM bankroll
                        )
                        SELECT MAX(peak_balance - balance) / NULLIF(MAX(peak_balance), 0)
                        FROM (
                            SELECT 
                                balance,
                                MAX(balance) OVER (ORDER BY rn ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as peak_balance
                            FROM balance_history
                        )
                    "

                    Using cmd As New SQLiteCommand(query, conn)
                        Dim result = cmd.ExecuteScalar()
                        Return If(result IsNot Nothing AndAlso Not IsDBNull(result), Convert.ToDouble(result), 0.0)
                    End Using
                End Using

            Catch ex As Exception
                _logger($"[KpiAnalyzer] Error reading drawdown: {ex.Message}")
                Return 0.0
            End Try
        End Function

        Private Function CalculateSystemHealth() As Double
            ' Composite health score (0.0 to 1.0)
            Dim score As Double = 1.0

            ' Penalty for low ROI
            If GetSportsRoi(7) < 0.02 Then score -= 0.2

            ' Penalty for drift
            If CheckForDrift() Then score -= 0.3

            ' Penalty for high drawdown
            If GetBankrollMaxDrawdown() > 0.15 Then score -= 0.25

            ' Penalty for low win rate
            If GetSportsWinRate() < 0.50 Then score -= 0.15

            Return Math.Max(0.0, score)
        End Function

        Private Function GetActiveModelCount() As Integer
            Try
                Dim modelsPath = Path.Combine(_databaseRoot, "..", "models")
                If Not Directory.Exists(modelsPath) Then Return 0

                Return Directory.GetDirectories(modelsPath).Length

            Catch ex As Exception
                Return 0
            End Try
        End Function

        Private Function CheckForDrift() As Boolean
            Try
                Dim memoryDbPath = Path.Combine(_databaseRoot, "eq12_memory.db")
                If Not File.Exists(memoryDbPath) Then Return False

                Using conn As New SQLiteConnection($"Data Source={memoryDbPath};Version=3;")
                    conn.Open()

                    ' Check most recent drift snapshot
                    Dim query = "
                        SELECT drift_detected 
                        FROM drift_snapshots 
                        ORDER BY checked_at_utc DESC 
                        LIMIT 1
                    "

                    Using cmd As New SQLiteCommand(query, conn)
                        Dim result = cmd.ExecuteScalar()
                        Return If(result IsNot Nothing AndAlso Not IsDBNull(result), Convert.ToInt32(result) = 1, False)
                    End Using
                End Using

            Catch ex As Exception
                _logger($"[KpiAnalyzer] Error checking drift: {ex.Message}")
                Return False
            End Try
        End Function

    End Class

    Public Interface IKpiAnalyzer
        Function GetCurrentKpiState() As KpiState
    End Interface

    Public Class KpiState
        Public Property Timestamp As DateTime
        Public Property Revenue7D As Decimal
        Public Property Revenue30D As Decimal
        Public Property RevenueSpiked As Boolean
        Public Property SportsRoi7D As Double
        Public Property SportsRoiTarget As Double
        Public Property SportsWinRate As Double
        Public Property BankrollBalance As Decimal
        Public Property BankrollMaxDrawdown As Double
        Public Property SystemHealthScore As Double
        Public Property ActiveModels As Integer
        Public Property DriftDetected As Boolean
    End Class

End Namespace
