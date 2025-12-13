Imports System.Data.SQLite
Imports Newtonsoft.Json

Namespace EQ12.BICore

    Public Class BiCoreConfig
        Public Property MemoryConnectionString As String
        Public Property DatabaseRoot As String
        Public Property MinRoiThreshold As Double = 0.03
        Public Property DriftRetrainThreshold As Double = 0.25
    End Class

    Public Class NextMoveRecommendation
        Public Property GeneratedAt As DateTime
        Public Property Priority As Integer   ' 1 = highest
        Public Property Category As String    ' "Sports", "Revenue", "Infra", "ML"
        Public Property Title As String
        Public Property Description As String
        Public Property SuggestedActions As List(Of String)
        Public Property AutoExecutable As Boolean ' Can be auto-executed by StackAgent
    End Class

    Public Interface IBiCoreService
        Function GenerateDailyNextMoves() As List(Of NextMoveRecommendation)
    End Interface

    Public Class BiCoreService
        Implements IBiCoreService

        Private ReadOnly _config As BiCoreConfig
        Private ReadOnly _memoryRepo As ISystemMemoryRepository
        Private ReadOnly _kpiAnalyzer As IKpiAnalyzer
        Private ReadOnly _logger As Action(Of String)

        Public Sub New(
            config As BiCoreConfig,
            memoryRepo As ISystemMemoryRepository,
            kpiAnalyzer As IKpiAnalyzer,
            logger As Action(Of String)
        )
            _config = config
            _memoryRepo = memoryRepo
            _kpiAnalyzer = kpiAnalyzer
            _logger = logger
        End Sub

        Public Function GenerateDailyNextMoves() As List(Of NextMoveRecommendation) _
            Implements IBiCoreService.GenerateDailyNextMoves

            Dim now = DateTime.UtcNow
            _logger($"[BiCore] Generating Next Moves @ {now:O}")

            ' 1. Load current KPI state
            Dim kpiState = _kpiAnalyzer.GetCurrentKpiState()

            ' 2. Save KPI snapshot to memory
            _memoryRepo.SaveKpiSnapshot(kpiState)

            ' 3. Analyze and generate recommendations
            Dim recs As New List(Of NextMoveRecommendation)

            ' ML HEALTH CHECKS
            If kpiState.DriftDetected Then
                recs.Add(New NextMoveRecommendation With {
                    .GeneratedAt = now,
                    .Priority = 1,
                    .Category = "ML",
                    .Title = "Model drift detected - trigger immediate retrain",
                    .Description = "PSI threshold exceeded in production data. Model predictions may be degrading.",
                    .SuggestedActions = New List(Of String) From {
                        "Run: python scripts/train_model_production.py --config configs/model_moneyline_v1.yaml",
                        "Run: python scripts/promote_model.py --challenger v_new",
                        "Monitor: Check drift_monitor.py logs for feature breakdown"
                    },
                    .AutoExecutable = True
                })
            End If

            ' SPORTS BETTING PERFORMANCE
            If kpiState.SportsRoi7D < _config.MinRoiThreshold Then
                recs.Add(New NextMoveRecommendation With {
                    .GeneratedAt = now,
                    .Priority = If(kpiState.SportsRoi7D < 0, 1, 2),
                    .Category = "Sports",
                    .Title = $"Sports ROI below target ({kpiState.SportsRoi7D:P2} vs {_config.MinRoiThreshold:P2})",
                    .Description = "Recent 7-day ROI is underperforming. Consider model refresh, edge recalibration, or market selection adjustment.",
                    .SuggestedActions = New List(Of String) From {
                        "Run backtester on last 90 days: python scripts/backtester.py --days 90",
                        "Retrain model with updated data",
                        "Review edge thresholds (may need tighter filters)",
                        "Check for line movement timing issues"
                    },
                    .AutoExecutable = False
                })
            End If

            ' BANKROLL HEALTH
            If kpiState.BankrollMaxDrawdown > 0.15 Then
                recs.Add(New NextMoveRecommendation With {
                    .GeneratedAt = now,
                    .Priority = 1,
                    .Category = "Sports",
                    .Title = $"High drawdown alert ({kpiState.BankrollMaxDrawdown:P1})",
                    .Description = "Bankroll has experienced significant drawdown. Reduce bet sizing or pause trading.",
                    .SuggestedActions = New List(Of String) From {
                        "Reduce Kelly fraction to 0.5x (conservative)",
                        "Increase minimum edge threshold from 3% to 5%",
                        "Review recent losing streak for patterns",
                        "Consider temporary pause until model revalidated"
                    },
                    .AutoExecutable = False
                })
            End If

            ' REVENUE OPPORTUNITIES
            If kpiState.RevenueSpiked Then
                recs.Add(New NextMoveRecommendation With {
                    .GeneratedAt = now,
                    .Priority = 2,
                    .Category = "Revenue",
                    .Title = "Revenue spike detected - double down on winning channels",
                    .Description = $"7-day revenue ({kpiState.Revenue7D:C}) significantly above 30-day baseline. Investigate and scale top performers.",
                    .SuggestedActions = New List(Of String) From {
                        "Run: python scripts/analytics_report.py --metric all",
                        "Identify top 3 revenue sources from report",
                        "Increase traffic/budget allocation to top funnels by 30%",
                        "A/B test variations on winning landing pages"
                    },
                    .AutoExecutable = True
                })
            End If

            ' SYSTEM HEALTH
            If kpiState.SystemHealthScore < 0.6 Then
                recs.Add(New NextMoveRecommendation With {
                    .GeneratedAt = now,
                    .Priority = 2,
                    .Category = "Infra",
                    .Title = $"System health degraded (score: {kpiState.SystemHealthScore:F2}/1.0)",
                    .Description = "Multiple subsystems showing warning signs. Run diagnostics and repair.",
                    .SuggestedActions = New List(Of String) From {
                        "Run: powershell scripts/EQ12_SYSTEM_SCAN.ps1 -Verbose",
                        "Check logs/ directory for error patterns",
                        "Verify database integrity (120 databases)",
                        "Review GitHub Actions workflow failures"
                    },
                    .AutoExecutable = True
                })
            End If

            ' PROACTIVE OPTIMIZATION
            If kpiState.SportsWinRate > 0.55 AndAlso kpiState.SportsRoi7D > _config.MinRoiThreshold Then
                recs.Add(New NextMoveRecommendation With {
                    .GeneratedAt = now,
                    .Priority = 3,
                    .Category = "Sports",
                    .Title = "Strong performance - consider scaling bet sizes",
                    .Description = $"Win rate at {kpiState.SportsWinRate:P1} with positive ROI. System performing well.",
                    .SuggestedActions = New List(Of String) From {
                        "Increase Kelly fraction from 1.0x to 1.2x (aggressive)",
                        "Expand to additional markets (lower liquidity, similar edge)",
                        "Document what's working for future reference"
                    },
                    .AutoExecutable = False
                })
            End If

            ' 4. Save recommendations to memory
            _memoryRepo.SaveNextMoves(now, recs)

            Dim priority1Count = recs.Where(Function(r) r.Priority = 1).Count()
            _logger($"[BiCore] Generated {recs.Count} recommendations (Priority 1: {priority1Count})")

            Return recs.OrderBy(Function(r) r.Priority).ToList()
        End Function

    End Class

    Public Interface ISystemMemoryRepository
        Sub SaveKpiSnapshot(kpiState As KpiState)
        Sub SaveNextMoves(timestamp As DateTime, moves As IEnumerable(Of NextMoveRecommendation))
    End Interface

    Public Class SqliteSystemMemoryRepository
        Implements ISystemMemoryRepository

        Private ReadOnly _connectionString As String

        Public Sub New(connectionString As String)
            _connectionString = connectionString
            EnsureSchema()
        End Sub

        Private Sub EnsureSchema()
            Using conn As New SQLiteConnection(_connectionString)
                conn.Open()

                ' KPI snapshots table
                conn.ExecuteNonQuery("
                    CREATE TABLE IF NOT EXISTS kpi_snapshots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        captured_at_utc TEXT NOT NULL,
                        revenue_7d REAL,
                        revenue_30d REAL,
                        revenue_spiked INTEGER,
                        sports_roi_7d REAL,
                        sports_roi_target REAL,
                        sports_win_rate REAL,
                        bankroll_balance REAL,
                        bankroll_max_drawdown REAL,
                        system_health_score REAL,
                        active_models INTEGER,
                        drift_detected INTEGER
                    )
                ")

                ' Next moves table
                conn.ExecuteNonQuery("
                    CREATE TABLE IF NOT EXISTS next_moves (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        generated_at_utc TEXT NOT NULL,
                        priority INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        auto_executable INTEGER NOT NULL
                    )
                ")

                ' Next move actions table
                conn.ExecuteNonQuery("
                    CREATE TABLE IF NOT EXISTS next_move_actions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        next_move_id INTEGER NOT NULL,
                        action_text TEXT NOT NULL,
                        FOREIGN KEY(next_move_id) REFERENCES next_moves(id)
                    )
                ")

                conn.Close()
            End Using
        End Sub

        Public Sub SaveKpiSnapshot(kpiState As KpiState) Implements ISystemMemoryRepository.SaveKpiSnapshot
            Using conn As New SQLiteConnection(_connectionString)
                conn.Open()

                Using cmd As New SQLiteCommand("
                    INSERT INTO kpi_snapshots 
                    (captured_at_utc, revenue_7d, revenue_30d, revenue_spiked, sports_roi_7d, 
                     sports_roi_target, sports_win_rate, bankroll_balance, bankroll_max_drawdown, 
                     system_health_score, active_models, drift_detected)
                    VALUES (@ts, @r7, @r30, @rs, @roi7, @roit, @wr, @bb, @bmd, @shs, @am, @dd)
                ", conn)

                    cmd.Parameters.AddWithValue("@ts", kpiState.Timestamp.ToString("O"))
                    cmd.Parameters.AddWithValue("@r7", kpiState.Revenue7D)
                    cmd.Parameters.AddWithValue("@r30", kpiState.Revenue30D)
                    cmd.Parameters.AddWithValue("@rs", If(kpiState.RevenueSpiked, 1, 0))
                    cmd.Parameters.AddWithValue("@roi7", kpiState.SportsRoi7D)
                    cmd.Parameters.AddWithValue("@roit", kpiState.SportsRoiTarget)
                    cmd.Parameters.AddWithValue("@wr", kpiState.SportsWinRate)
                    cmd.Parameters.AddWithValue("@bb", kpiState.BankrollBalance)
                    cmd.Parameters.AddWithValue("@bmd", kpiState.BankrollMaxDrawdown)
                    cmd.Parameters.AddWithValue("@shs", kpiState.SystemHealthScore)
                    cmd.Parameters.AddWithValue("@am", kpiState.ActiveModels)
                    cmd.Parameters.AddWithValue("@dd", If(kpiState.DriftDetected, 1, 0))

                    cmd.ExecuteNonQuery()
                End Using

                conn.Close()
            End Using
        End Sub

        Public Sub SaveNextMoves(timestamp As DateTime, moves As IEnumerable(Of NextMoveRecommendation)) _
            Implements ISystemMemoryRepository.SaveNextMoves

            Using conn As New SQLiteConnection(_connectionString)
                conn.Open()

                Using tx = conn.BeginTransaction()
                    For Each move In moves
                        Using cmd As New SQLiteCommand("
                            INSERT INTO next_moves (generated_at_utc, priority, category, title, description, auto_executable)
                            VALUES (@ts, @p, @c, @t, @d, @ae);
                            SELECT last_insert_rowid();
                        ", conn, tx)

                            cmd.Parameters.AddWithValue("@ts", timestamp.ToString("O"))
                            cmd.Parameters.AddWithValue("@p", move.Priority)
                            cmd.Parameters.AddWithValue("@c", move.Category)
                            cmd.Parameters.AddWithValue("@t", move.Title)
                            cmd.Parameters.AddWithValue("@d", move.Description)
                            cmd.Parameters.AddWithValue("@ae", If(move.AutoExecutable, 1, 0))

                            Dim newId = CLng(cmd.ExecuteScalar())

                            If move.SuggestedActions IsNot Nothing Then
                                For Each action In move.SuggestedActions
                                    Using actCmd As New SQLiteCommand("
                                        INSERT INTO next_move_actions (next_move_id, action_text)
                                        VALUES (@id, @txt)
                                    ", conn, tx)
                                        actCmd.Parameters.AddWithValue("@id", newId)
                                        actCmd.Parameters.AddWithValue("@txt", action)
                                        actCmd.ExecuteNonQuery()
                                    End Using
                                Next
                            End If
                        End Using
                    Next

                    tx.Commit()
                End Using

                conn.Close()
            End Using
        End Sub

    End Class

    ' Extension method for SQLiteConnection
    Module SqliteExtensions
        <System.Runtime.CompilerServices.Extension>
        Public Sub ExecuteNonQuery(conn As SQLiteConnection, commandText As String)
            Using cmd As New SQLiteCommand(commandText, conn)
                cmd.ExecuteNonQuery()
            End Using
        End Sub
    End Module

End Namespace
