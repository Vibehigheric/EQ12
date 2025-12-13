' EQ12 Sports Betting Terminal - Database Manager
' Comprehensive database management for bets, bankroll, odds, and system data

Imports System.Data.SQLite
Imports System.Collections.Generic
Imports System.Threading.Tasks
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.IO

Public Class DatabaseManager

    Private dbConnection As SQLiteConnection
    Private config As Dictionary(Of String, Object)
    Private logger As Action(Of String, String)

    ' Database configuration
    Private dbPath As String = "C:\EQ12\data\eq12_terminal.db"
    Private backupPath As String = "C:\EQ12\data\backups"
    Private connectionString As String = ""

    ' Performance tracking
    Private queryCount As Integer = 0
    Private lastBackup As DateTime = DateTime.MinValue
    Private backupInterval As TimeSpan = TimeSpan.FromHours(6)

    Public Event DatabaseUpdated(table As String, operation As String, recordCount As Integer)
    Public Event BackupCompleted(backupFile As String, success As Boolean)

    Public Sub New()
        InitializeDatabase()

        ' Set up logging
        logger = Sub(message As String, level As String)
                     Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] [{level}] DatabaseManager: {message}")
                 End Sub

        logger("Database Manager initialized", "INFO")
    End Sub

    Private Sub InitializeDatabase()
        Try
            ' Create data directory structure
            CreateDirectories()

            ' Set up connection string
            connectionString = $"Data Source={dbPath};Version=3;Journal Mode=WAL;Synchronous=NORMAL;"

            ' Initialize connection
            dbConnection = New SQLiteConnection(connectionString)
            dbConnection.Open()

            ' Create all tables
            CreateAllTables()

            ' Create indexes for performance
            CreateIndexes()

            ' Initialize with default data
            InitializeDefaultData()

            logger($"Database initialized: {dbPath}", "SUCCESS")

        Catch ex As Exception
            logger($"Error initializing database: {ex.Message}", "ERROR")
            Throw
        End Try
    End Sub

    Private Sub CreateDirectories()
        Try
            Dim directories = New String() {
                Path.GetDirectoryName(dbPath),
                backupPath,
                "C:\EQ12\logs",
                "C:\EQ12\configs",
                "C:\EQ12\data\exports"
            }

            For Each dir In directories
                If Not Directory.Exists(dir) Then
                    Directory.CreateDirectory(dir)
                End If
            Next

        Catch ex As Exception
            logger($"Error creating directories: {ex.Message}", "ERROR")
            Throw
        End Try
    End Sub

    Private Sub CreateAllTables()
        Try
            ' Bets table - comprehensive betting records
            CreateBetsTable()

            ' Bankroll history table
            CreateBankrollTable()

            ' Odds data table
            CreateOddsTable()

            ' System configuration table
            CreateConfigTable()

            ' User preferences table
            CreatePreferencesTable()

            ' Alert history table
            CreateAlertsTable()

            ' Model predictions table
            CreatePredictionsTable()

            ' Performance metrics table
            CreateMetricsTable()

            logger("All database tables created successfully", "SUCCESS")

        Catch ex As Exception
            logger($"Error creating tables: {ex.Message}", "ERROR")
            Throw
        End Try
    End Sub

    Private Sub CreateBetsTable()
        Dim sql = "
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bet_id TEXT UNIQUE NOT NULL,
                bet_date DATETIME NOT NULL,
                sport TEXT NOT NULL,
                league TEXT,
                market_type TEXT NOT NULL,
                selection TEXT NOT NULL,
                home_team TEXT,
                away_team TEXT,
                odds_decimal REAL,
                odds_american INTEGER,
                odds_fractional TEXT,
                stake REAL NOT NULL,
                potential_win REAL NOT NULL,
                actual_profit REAL DEFAULT 0,
                result TEXT DEFAULT 'Pending',
                confidence REAL DEFAULT 0,
                expected_value REAL DEFAULT 0,
                kelly_percentage REAL DEFAULT 0,
                source TEXT DEFAULT 'Manual',
                sportsbook TEXT,
                bet_type TEXT DEFAULT 'Single',
                parlay_id TEXT,
                settled_date DATETIME,
                void_reason TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"

        ExecuteNonQuery(sql)
    End Sub

    Private Sub CreateBankrollTable()
        Dim sql = "
            CREATE TABLE IF NOT EXISTS bankroll_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                starting_balance REAL NOT NULL,
                ending_balance REAL NOT NULL,
                daily_profit REAL NOT NULL,
                total_wagered REAL DEFAULT 0,
                total_bets INTEGER NOT NULL,
                winning_bets INTEGER NOT NULL,
                losing_bets INTEGER DEFAULT 0,
                void_bets INTEGER DEFAULT 0,
                daily_roi REAL DEFAULT 0,
                running_roi REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0,
                sharpe_ratio REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                avg_bet_size REAL DEFAULT 0,
                largest_win REAL DEFAULT 0,
                largest_loss REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"

        ExecuteNonQuery(sql)
    End Sub

    Private Sub CreateOddsTable()
        Dim sql = "
            CREATE TABLE IF NOT EXISTS odds_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                sport TEXT NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                commence_time DATETIME NOT NULL,
                sportsbook TEXT NOT NULL,
                market_type TEXT NOT NULL,
                outcome_name TEXT NOT NULL,
                odds_decimal REAL NOT NULL,
                odds_american INTEGER NOT NULL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                source TEXT DEFAULT 'API'
            )"

        ExecuteNonQuery(sql)
    End Sub

    Private Sub CreateConfigTable()
        Dim sql = "
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_section TEXT NOT NULL,
                config_key TEXT NOT NULL,
                config_value TEXT NOT NULL,
                data_type TEXT DEFAULT 'string',
                description TEXT,
                is_encrypted BOOLEAN DEFAULT 0,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(config_section, config_key)
            )"

        ExecuteNonQuery(sql)
    End Sub

    Private Sub CreatePreferencesTable()
        Dim sql = "
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_key TEXT UNIQUE NOT NULL,
                preference_value TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"

        ExecuteNonQuery(sql)
    End Sub

    Private Sub CreateAlertsTable()
        Dim sql = "
            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT DEFAULT 'INFO',
                source_module TEXT,
                related_bet_id TEXT,
                telegram_sent BOOLEAN DEFAULT 0,
                discord_sent BOOLEAN DEFAULT 0,
                email_sent BOOLEAN DEFAULT 0,
                is_read BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"

        ExecuteNonQuery(sql)
    End Sub

    Private Sub CreatePredictionsTable()
        Dim sql = "
            CREATE TABLE IF NOT EXISTS model_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT NOT NULL,
                sport TEXT NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                home_probability REAL NOT NULL,
                away_probability REAL NOT NULL,
                confidence REAL NOT NULL,
                expected_value REAL DEFAULT 0,
                model_version TEXT DEFAULT '1.0',
                model_accuracy REAL DEFAULT 0,
                prediction_features TEXT,
                actual_result TEXT,
                prediction_correct BOOLEAN,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"

        ExecuteNonQuery(sql)
    End Sub

    Private Sub CreateMetricsTable()
        Dim sql = "
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE NOT NULL,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                source_module TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"

        ExecuteNonQuery(sql)
    End Sub

    Private Sub CreateIndexes()
        Try
            Dim indexes = New String() {
                "CREATE INDEX IF NOT EXISTS idx_bets_date ON bets(bet_date)",
                "CREATE INDEX IF NOT EXISTS idx_bets_sport ON bets(sport)",
                "CREATE INDEX IF NOT EXISTS idx_bets_result ON bets(result)",
                "CREATE INDEX IF NOT EXISTS idx_bets_source ON bets(source)",
                "CREATE INDEX IF NOT EXISTS idx_odds_game ON odds_data(game_id)",
                "CREATE INDEX IF NOT EXISTS idx_odds_sportsbook ON odds_data(sportsbook)",
                "CREATE INDEX IF NOT EXISTS idx_odds_updated ON odds_data(last_updated)",
                "CREATE INDEX IF NOT EXISTS idx_bankroll_date ON bankroll_history(date)",
                "CREATE INDEX IF NOT EXISTS idx_alerts_type ON alert_history(alert_type)",
                "CREATE INDEX IF NOT EXISTS idx_alerts_created ON alert_history(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_predictions_game ON model_predictions(game_id)",
                "CREATE INDEX IF NOT EXISTS idx_metrics_date ON performance_metrics(metric_date)"
            }

            For Each indexSql In indexes
                ExecuteNonQuery(indexSql)
            Next

            logger("Database indexes created successfully", "SUCCESS")

        Catch ex As Exception
            logger($"Error creating indexes: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub InitializeDefaultData()
        Try
            ' Initialize system configuration
            InitializeDefaultConfig()

            ' Initialize user preferences
            InitializeDefaultPreferences()

            logger("Default data initialized successfully", "SUCCESS")

        Catch ex As Exception
            logger($"Error initializing default data: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub InitializeDefaultConfig()
        Try
            Dim defaultConfigs = New Dictionary(Of String, Dictionary(Of String, String)) From {
                {"bankroll", New Dictionary(Of String, String) From {
                    {"initial_bankroll", "1000.00"},
                    {"daily_budget", "100.00"},
                    {"max_bet_percentage", "0.05"},
                    {"kelly_fraction", "0.25"},
                    {"risk_tolerance", "moderate"}
                }},
                {"alerts", New Dictionary(Of String, String) From {
                    {"telegram_enabled", "true"},
                    {"discord_enabled", "false"},
                    {"email_enabled", "false"},
                    {"min_arbitrage_profit", "0.02"},
                    {"min_value_bet_edge", "0.05"}
                }},
                {"model", New Dictionary(Of String, String) From {
                    {"confidence_threshold", "0.6"},
                    {"edge_threshold", "0.02"},
                    {"auto_bet_enabled", "false"},
                    {"model_version", "1.0"}
                }}
            }

            For Each section In defaultConfigs
                For Each config In section.Value
                    Dim sql = "INSERT OR IGNORE INTO system_config (config_section, config_key, config_value) VALUES (?, ?, ?)"
                    ExecuteNonQuery(sql, section.Key, config.Key, config.Value)
                Next
            Next

        Catch ex As Exception
            logger($"Error initializing default config: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub InitializeDefaultPreferences()
        Try
            Dim defaultPreferences = New Dictionary(Of String, String) From {
                {"theme", "dark"},
                {"auto_refresh_interval", "5"},
                {"default_sport", "baseball_mlb"},
                {"currency_symbol", "$"},
                {"date_format", "MM/dd/yyyy"},
                {"time_format", "HH:mm:ss"},
                {"notifications_sound", "true"},
                {"auto_backup", "true"}
            }

            For Each pref In defaultPreferences
                Dim sql = "INSERT OR IGNORE INTO user_preferences (preference_key, preference_value) VALUES (?, ?)"
                ExecuteNonQuery(sql, pref.Key, pref.Value)
            Next

        Catch ex As Exception
            logger($"Error initializing default preferences: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub ExecuteNonQuery(sql As String, ParamArray parameters() As Object)
        Try
            Using cmd As New SQLiteCommand(sql, dbConnection)
                For i As Integer = 0 To parameters.Length - 1
                    cmd.Parameters.Add(New SQLiteParameter($"@param{i}", parameters(i)))
                Next
                cmd.ExecuteNonQuery()
            End Using

            queryCount += 1

        Catch ex As Exception
            logger($"Error executing SQL: {ex.Message}", "ERROR")
            logger($"SQL: {sql}", "DEBUG")
            Throw
        End Try
    End Sub

    Public Function GetRecentBets(count As Integer) As List(Of Dictionary(Of String, Object))
        Try
            Dim bets As New List(Of Dictionary(Of String, Object))

            Dim sql = "SELECT * FROM bets ORDER BY bet_date DESC LIMIT ?"
            Using cmd As New SQLiteCommand(sql, dbConnection)
                cmd.Parameters.AddWithValue("@count", count)

                Using reader = cmd.ExecuteReader()
                    While reader.Read()
                        Dim bet As New Dictionary(Of String, Object)

                        For i As Integer = 0 To reader.FieldCount - 1
                            bet(reader.GetName(i)) = If(IsDBNull(reader(i)), Nothing, reader(i))
                        Next

                        bets.Add(bet)
                    End While
                End Using
            End Using

            RaiseEvent DatabaseUpdated("bets", "SELECT", bets.Count)
            Return bets

        Catch ex As Exception
            logger($"Error getting recent bets: {ex.Message}", "ERROR")
            Return New List(Of Dictionary(Of String, Object))
        End Try
    End Function

    Public Function InsertBet(betData As Dictionary(Of String, Object)) As Boolean
        Try
            Dim sql = "
                INSERT INTO bets (
                    bet_id, bet_date, sport, market_type, selection,
                    odds_decimal, odds_american, stake, potential_win,
                    confidence, expected_value, source, sportsbook
                ) VALUES (
                    @bet_id, @bet_date, @sport, @market_type, @selection,
                    @odds_decimal, @odds_american, @stake, @potential_win,
                    @confidence, @expected_value, @source, @sportsbook
                )"

            Using cmd As New SQLiteCommand(sql, dbConnection)
                cmd.Parameters.AddWithValue("@bet_id", If(betData.ContainsKey("bet_id"), betData("bet_id"), Guid.NewGuid().ToString()))
                cmd.Parameters.AddWithValue("@bet_date", If(betData.ContainsKey("bet_date"), betData("bet_date"), DateTime.Now))
                cmd.Parameters.AddWithValue("@sport", If(betData.ContainsKey("sport"), betData("sport"), "Unknown"))
                cmd.Parameters.AddWithValue("@market_type", If(betData.ContainsKey("market_type"), betData("market_type"), "Moneyline"))
                cmd.Parameters.AddWithValue("@selection", If(betData.ContainsKey("selection"), betData("selection"), ""))
                cmd.Parameters.AddWithValue("@odds_decimal", If(betData.ContainsKey("odds_decimal"), betData("odds_decimal"), 2.0))
                cmd.Parameters.AddWithValue("@odds_american", If(betData.ContainsKey("odds_american"), betData("odds_american"), 100))
                cmd.Parameters.AddWithValue("@stake", If(betData.ContainsKey("stake"), betData("stake"), 0))
                cmd.Parameters.AddWithValue("@potential_win", If(betData.ContainsKey("potential_win"), betData("potential_win"), 0))
                cmd.Parameters.AddWithValue("@confidence", If(betData.ContainsKey("confidence"), betData("confidence"), 0))
                cmd.Parameters.AddWithValue("@expected_value", If(betData.ContainsKey("expected_value"), betData("expected_value"), 0))
                cmd.Parameters.AddWithValue("@source", If(betData.ContainsKey("source"), betData("source"), "Terminal"))
                cmd.Parameters.AddWithValue("@sportsbook", If(betData.ContainsKey("sportsbook"), betData("sportsbook"), ""))

                cmd.ExecuteNonQuery()
            End Using

            RaiseEvent DatabaseUpdated("bets", "INSERT", 1)
            logger("Bet inserted successfully", "SUCCESS")
            Return True

        Catch ex As Exception
            logger($"Error inserting bet: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Public Function UpdateBetResult(betId As String, result As String, actualProfit As Decimal) As Boolean
        Try
            Dim sql = "UPDATE bets SET result = @result, actual_profit = @profit, settled_date = @settled_date, updated_at = CURRENT_TIMESTAMP WHERE bet_id = @bet_id"

            Using cmd As New SQLiteCommand(sql, dbConnection)
                cmd.Parameters.AddWithValue("@result", result)
                cmd.Parameters.AddWithValue("@profit", actualProfit)
                cmd.Parameters.AddWithValue("@settled_date", DateTime.Now)
                cmd.Parameters.AddWithValue("@bet_id", betId)

                Dim rowsAffected = cmd.ExecuteNonQuery()

                RaiseEvent DatabaseUpdated("bets", "UPDATE", rowsAffected)
                logger($"Bet result updated: {betId} -> {result}", "SUCCESS")
                Return rowsAffected > 0
            End Using

        Catch ex As Exception
            logger($"Error updating bet result: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Public Function InsertOddsData(oddsData As List(Of Dictionary(Of String, Object))) As Integer
        Try
            Dim insertedCount = 0

            Using transaction = dbConnection.BeginTransaction()
                Try
                    For Each odds In oddsData
                        Dim sql = "
                            INSERT OR REPLACE INTO odds_data (
                                game_id, sport, home_team, away_team, commence_time,
                                sportsbook, market_type, outcome_name, odds_decimal, odds_american
                            ) VALUES (
                                @game_id, @sport, @home_team, @away_team, @commence_time,
                                @sportsbook, @market_type, @outcome_name, @odds_decimal, @odds_american
                            )"

                        Using cmd As New SQLiteCommand(sql, dbConnection, transaction)
                            cmd.Parameters.AddWithValue("@game_id", If(odds.ContainsKey("game_id"), odds("game_id"), ""))
                            cmd.Parameters.AddWithValue("@sport", If(odds.ContainsKey("sport"), odds("sport"), ""))
                            cmd.Parameters.AddWithValue("@home_team", If(odds.ContainsKey("home_team"), odds("home_team"), ""))
                            cmd.Parameters.AddWithValue("@away_team", If(odds.ContainsKey("away_team"), odds("away_team"), ""))
                            cmd.Parameters.AddWithValue("@commence_time", If(odds.ContainsKey("commence_time"), odds("commence_time"), DateTime.Now))
                            cmd.Parameters.AddWithValue("@sportsbook", If(odds.ContainsKey("sportsbook"), odds("sportsbook"), ""))
                            cmd.Parameters.AddWithValue("@market_type", If(odds.ContainsKey("market_type"), odds("market_type"), ""))
                            cmd.Parameters.AddWithValue("@outcome_name", If(odds.ContainsKey("outcome_name"), odds("outcome_name"), ""))
                            cmd.Parameters.AddWithValue("@odds_decimal", If(odds.ContainsKey("odds_decimal"), odds("odds_decimal"), 0))
                            cmd.Parameters.AddWithValue("@odds_american", If(odds.ContainsKey("odds_american"), odds("odds_american"), 0))

                            cmd.ExecuteNonQuery()
                            insertedCount += 1
                        End Using
                    Next

                    transaction.Commit()

                Catch ex As Exception
                    transaction.Rollback()
                    Throw
                End Try
            End Using

            RaiseEvent DatabaseUpdated("odds_data", "INSERT", insertedCount)
            logger($"Inserted {insertedCount} odds records", "SUCCESS")
            Return insertedCount

        Catch ex As Exception
            logger($"Error inserting odds data: {ex.Message}", "ERROR")
            Return 0
        End Try
    End Function

    Public Function GetBankrollSummary() As Dictionary(Of String, Object)
        Try
            Dim summary As New Dictionary(Of String, Object)

            ' Get basic stats
            Dim sql = "
                SELECT
                    COUNT(*) as total_bets,
                    SUM(CASE WHEN result = 'Won' THEN 1 ELSE 0 END) as winning_bets,
                    SUM(actual_profit) as total_profit,
                    AVG(stake) as avg_stake,
                    MAX(actual_profit) as largest_win,
                    MIN(actual_profit) as largest_loss
                FROM bets
                WHERE result != 'Pending'"

            Using cmd As New SQLiteCommand(sql, dbConnection)
                Using reader = cmd.ExecuteReader()
                    If reader.Read() Then
                        summary("total_bets") = Convert.ToInt32(reader("total_bets"))
                        summary("winning_bets") = Convert.ToInt32(reader("winning_bets"))
                        summary("total_profit") = Convert.ToDecimal(reader("total_profit"))
                        summary("avg_stake") = Convert.ToDecimal(reader("avg_stake"))
                        summary("largest_win") = Convert.ToDecimal(reader("largest_win"))
                        summary("largest_loss") = Convert.ToDecimal(reader("largest_loss"))
                    End If
                End Using
            End Using

            ' Calculate additional metrics
            Dim totalBets = CInt(summary("total_bets"))
            If totalBets > 0 Then
                summary("win_rate") = CDec(summary("winning_bets")) / totalBets
                summary("roi") = CDec(summary("total_profit")) / (CDec(summary("avg_stake")) * totalBets)
            Else
                summary("win_rate") = 0D
                summary("roi") = 0D
            End If

            Return summary

        Catch ex As Exception
            logger($"Error getting bankroll summary: {ex.Message}", "ERROR")
            Return New Dictionary(Of String, Object)
        End Try
    End Function

    Public Function BackupDatabase() As Boolean
        Try
            If DateTime.Now.Subtract(lastBackup) < backupInterval Then
                logger("Backup skipped: too recent", "INFO")
                Return True
            End If

            Dim backupFile = Path.Combine(backupPath, $"eq12_terminal_backup_{DateTime.Now:yyyyMMdd_HHmmss}.db")

            ' Simple file copy backup
            File.Copy(dbPath, backupFile, True)

            ' Cleanup old backups (keep last 10)
            CleanupOldBackups()

            lastBackup = DateTime.Now
            RaiseEvent BackupCompleted(backupFile, True)
            logger($"Database backed up to: {backupFile}", "SUCCESS")

            Return True

        Catch ex As Exception
            logger($"Error backing up database: {ex.Message}", "ERROR")
            RaiseEvent BackupCompleted("", False)
            Return False
        End Try
    End Function

    Private Sub CleanupOldBackups()
        Try
            Dim backupFiles = Directory.GetFiles(backupPath, "eq12_terminal_backup_*.db").
                OrderByDescending(Function(f) File.GetCreationTime(f)).
                Skip(10).
                ToList()

            For Each file In backupFiles
                File.Delete(file)
            Next

            If backupFiles.Count > 0 Then
                logger($"Cleaned up {backupFiles.Count} old backup files", "INFO")
            End If

        Catch ex As Exception
            logger($"Error cleaning up old backups: {ex.Message}", "ERROR")
        End Try
    End Sub

    Public Sub InitializeDatabase()
        ' Re-initialize if needed
        If dbConnection Is Nothing OrElse dbConnection.State <> ConnectionState.Open Then
            InitializeDatabase()
        End If
    End Sub

    Public Sub Dispose()
        Try
            ' Perform final backup
            BackupDatabase()

            ' Close connection
            dbConnection?.Close()
            dbConnection?.Dispose()

            logger($"Database Manager disposed. Total queries: {queryCount}", "INFO")

        Catch ex As Exception
            logger($"Error disposing Database Manager: {ex.Message}", "ERROR")
        End Try
    End Sub

End Class
