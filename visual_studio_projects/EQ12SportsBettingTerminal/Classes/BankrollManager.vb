' EQ12 Sports Betting Terminal - Bankroll Manager
' Advanced bankroll management with Kelly Criterion, risk assessment, and EQ12 integration

Imports System.Collections.Generic
Imports System.Data.SQLite
Imports System.Threading.Tasks
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.IO

Public Class BankrollManager

    Private config As Dictionary(Of String, Object)
    Private logger As Action(Of String, String)
    Private dbConnection As SQLiteConnection

    ' Bankroll settings
    Private currentBankroll As Decimal = 0
    Private initialBankroll As Decimal = 0
    Private dailyBudget As Decimal = 0
    Private maxBetPercentage As Double = 0.05 ' 5% max per bet
    Private kellyFraction As Double = 0.25 ' Conservative Kelly
    Private riskTolerance As String = "moderate"

    ' Statistics tracking
    Private totalBets As Integer = 0
    Private winningBets As Integer = 0
    Private totalProfit As Decimal = 0
    Private dailyBets As Integer = 0
    Private dailyProfit As Decimal = 0

    ' Risk management
    Private dailyLossLimit As Decimal = 0
    Private weeklyLossLimit As Decimal = 0
    Private consecutiveLosses As Integer = 0
    Private maxConsecutiveLosses As Integer = 5

    Public Event BankrollUpdated(bankrollData As Dictionary(Of String, Decimal))
    Public Event RiskLimitReached(limitType As String, currentValue As Decimal)
    Public Event KellySizeCalculated(betSize As Decimal, edge As Double, probability As Double)

    Public Sub New()
        InitializeBankrollManager()

        ' Set up logging
        logger = Sub(message As String, level As String)
                     Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] [{level}] BankrollManager: {message}")
                 End Sub

        logger("Bankroll Manager initialized", "INFO")
    End Sub

    Private Sub InitializeBankrollManager()
        Try
            ' Initialize database connection
            InitializeDatabase()

            ' Load bankroll configuration
            LoadBankrollConfig()

            ' Load current bankroll state
            LoadCurrentBankroll()

            ' Connect to EQ12 systems
            ConnectToEQ12Systems()

        Catch ex As Exception
            logger($"Error initializing bankroll manager: {ex.Message}", "ERROR")
            Throw
        End Try
    End Sub

    Private Sub InitializeDatabase()
        Try
            Dim dbPath = "C:\EQ12\data\bankroll.db"
            Dim dbDirectory = Path.GetDirectoryName(dbPath)

            ' Create directory if it doesn't exist
            If Not Directory.Exists(dbDirectory) Then
                Directory.CreateDirectory(dbDirectory)
            End If

            ' Initialize database connection
            Dim connectionString = $"Data Source={dbPath};Version=3;"
            dbConnection = New SQLiteConnection(connectionString)
            dbConnection.Open()

            ' Create tables if they don't exist
            CreateTables()

            logger($"Database initialized: {dbPath}", "SUCCESS")

        Catch ex As Exception
            logger($"Error initializing database: {ex.Message}", "ERROR")
            Throw
        End Try
    End Sub

    Private Sub CreateTables()
        Try
            Dim createBetsTable = "
                CREATE TABLE IF NOT EXISTS bets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bet_date TEXT NOT NULL,
                    sport TEXT NOT NULL,
                    market_type TEXT NOT NULL,
                    selection TEXT NOT NULL,
                    odds INTEGER NOT NULL,
                    american_odds TEXT,
                    stake REAL NOT NULL,
                    potential_win REAL NOT NULL,
                    result TEXT DEFAULT 'Pending',
                    actual_profit REAL DEFAULT 0,
                    confidence REAL DEFAULT 0,
                    expected_value REAL DEFAULT 0,
                    kelly_size REAL DEFAULT 0,
                    source TEXT DEFAULT 'Manual',
                    bet_type TEXT DEFAULT 'Single',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    settled_at DATETIME,
                    notes TEXT
                )"

            Dim createBankrollTable = "
                CREATE TABLE IF NOT EXISTS bankroll_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    starting_balance REAL NOT NULL,
                    ending_balance REAL NOT NULL,
                    daily_profit REAL NOT NULL,
                    total_bets INTEGER NOT NULL,
                    winning_bets INTEGER NOT NULL,
                    daily_roi REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )"

            Dim createConfigTable = "
                CREATE TABLE IF NOT EXISTS bankroll_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT UNIQUE NOT NULL,
                    config_value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )"

            Using cmd As New SQLiteCommand(createBetsTable, dbConnection)
                cmd.ExecuteNonQuery()
            End Using

            Using cmd As New SQLiteCommand(createBankrollTable, dbConnection)
                cmd.ExecuteNonQuery()
            End Using

            Using cmd As New SQLiteCommand(createConfigTable, dbConnection)
                cmd.ExecuteNonQuery()
            End Using

            logger("Database tables created successfully", "SUCCESS")

        Catch ex As Exception
            logger($"Error creating database tables: {ex.Message}", "ERROR")
            Throw
        End Try
    End Sub

    Private Sub LoadBankrollConfig()
        Try
            ' Load from database first
            LoadConfigFromDB()

            ' Load from EQ12 config files if available
            Dim configPath = "C:\EQ12\configs\bankroll_config.json"
            If File.Exists(configPath) Then
                Dim configJson = File.ReadAllText(configPath)
                Dim configData = JsonConvert.DeserializeObject(Of Dictionary(Of String, Object))(configJson)

                If configData.ContainsKey("initial_bankroll") Then
                    initialBankroll = CDec(configData("initial_bankroll"))
                End If

                If configData.ContainsKey("daily_budget") Then
                    dailyBudget = CDec(configData("daily_budget"))
                End If

                If configData.ContainsKey("max_bet_percentage") Then
                    maxBetPercentage = CDbl(configData("max_bet_percentage"))
                End If

                If configData.ContainsKey("kelly_fraction") Then
                    kellyFraction = CDbl(configData("kelly_fraction"))
                End If

                If configData.ContainsKey("risk_tolerance") Then
                    riskTolerance = configData("risk_tolerance").ToString()
                End If

                ' Save to database
                SaveConfigToDB()
            Else
                ' Create default config
                CreateDefaultConfig()
            End If

            ' Calculate risk limits
            CalculateRiskLimits()

            logger("Bankroll configuration loaded successfully", "SUCCESS")

        Catch ex As Exception
            logger($"Error loading bankroll config: {ex.Message}", "ERROR")
            ' Set default values
            SetDefaultConfig()
        End Try
    End Sub

    Private Sub LoadConfigFromDB()
        Try
            Dim sql = "SELECT config_key, config_value FROM bankroll_config"
            Using cmd As New SQLiteCommand(sql, dbConnection)
                Using reader = cmd.ExecuteReader()
                    While reader.Read()
                        Dim key = reader("config_key").ToString()
                        Dim value = reader("config_value").ToString()

                        Select Case key
                            Case "initial_bankroll"
                                Decimal.TryParse(value, initialBankroll)
                            Case "current_bankroll"
                                Decimal.TryParse(value, currentBankroll)
                            Case "daily_budget"
                                Decimal.TryParse(value, dailyBudget)
                            Case "max_bet_percentage"
                                Double.TryParse(value, maxBetPercentage)
                            Case "kelly_fraction"
                                Double.TryParse(value, kellyFraction)
                            Case "risk_tolerance"
                                riskTolerance = value
                        End Select
                    End While
                End Using
            End Using

        Catch ex As Exception
            logger($"Error loading config from DB: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub SaveConfigToDB()
        Try
            Dim configs = New Dictionary(Of String, String) From {
                {"initial_bankroll", initialBankroll.ToString()},
                {"current_bankroll", currentBankroll.ToString()},
                {"daily_budget", dailyBudget.ToString()},
                {"max_bet_percentage", maxBetPercentage.ToString()},
                {"kelly_fraction", kellyFraction.ToString()},
                {"risk_tolerance", riskTolerance}
            }

            For Each config In configs
                Dim sql = "INSERT OR REPLACE INTO bankroll_config (config_key, config_value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)"
                Using cmd As New SQLiteCommand(sql, dbConnection)
                    cmd.Parameters.AddWithValue("@key", config.Key)
                    cmd.Parameters.AddWithValue("@value", config.Value)
                    cmd.ExecuteNonQuery()
                End Using
            Next

        Catch ex As Exception
            logger($"Error saving config to DB: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub CreateDefaultConfig()
        Try
            initialBankroll = 1000D ' $1000 default
            currentBankroll = initialBankroll
            dailyBudget = initialBankroll * 0.1D ' 10% daily budget
            maxBetPercentage = 0.05 ' 5% max per bet
            kellyFraction = 0.25 ' Conservative Kelly
            riskTolerance = "moderate"

            ' Save default config
            Dim defaultConfig = New Dictionary(Of String, Object) From {
                {"initial_bankroll", initialBankroll},
                {"current_bankroll", currentBankroll},
                {"daily_budget", dailyBudget},
                {"max_bet_percentage", maxBetPercentage},
                {"kelly_fraction", kellyFraction},
                {"risk_tolerance", riskTolerance}
            }

            Dim configJson = JsonConvert.SerializeObject(defaultConfig, Formatting.Indented)
            File.WriteAllText("C:\EQ12\configs\bankroll_config.json", configJson)

            SaveConfigToDB()

            logger("Default bankroll configuration created", "INFO")

        Catch ex As Exception
            logger($"Error creating default config: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub SetDefaultConfig()
        initialBankroll = 1000D
        currentBankroll = initialBankroll
        dailyBudget = 100D
        maxBetPercentage = 0.05
        kellyFraction = 0.25
        riskTolerance = "moderate"
    End Sub

    Private Sub CalculateRiskLimits()
        Try
            ' Calculate daily loss limit (percentage of bankroll)
            Dim dailyLossPercent As Double = Select Case riskTolerance.ToLower()
                                                 Case "conservative"
                                                     0.02 ' 2%
                                                 Case "moderate"
                                                     0.05 ' 5%
                                                 Case "aggressive"
                                                     0.1 ' 10%
                                                 Case Else
                                                     0.05 ' Default
                                             End Select

            dailyLossLimit = currentBankroll * CDec(dailyLossPercent)
            weeklyLossLimit = dailyLossLimit * 5 ' 5 trading days

            logger($"Risk limits calculated: Daily=${dailyLossLimit:F2}, Weekly=${weeklyLossLimit:F2}", "INFO")

        Catch ex As Exception
            logger($"Error calculating risk limits: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub LoadCurrentBankroll()
        Try
            ' Load current statistics
            LoadBankrollStats()

            ' If no current bankroll in DB, use initial
            If currentBankroll = 0 Then
                currentBankroll = initialBankroll
            End If

            logger($"Current bankroll loaded: ${currentBankroll:F2}", "INFO")

        Catch ex As Exception
            logger($"Error loading current bankroll: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub LoadBankrollStats()
        Try
            ' Load total statistics
            Dim totalSql = "SELECT COUNT(*) as total_bets, SUM(CASE WHEN result = 'Won' THEN 1 ELSE 0 END) as winning_bets, SUM(actual_profit) as total_profit FROM bets WHERE result != 'Pending'"
            Using cmd As New SQLiteCommand(totalSql, dbConnection)
                Using reader = cmd.ExecuteReader()
                    If reader.Read() Then
                        totalBets = Convert.ToInt32(reader("total_bets"))
                        winningBets = Convert.ToInt32(reader("winning_bets"))
                        totalProfit = Convert.ToDecimal(reader("total_profit"))
                    End If
                End Using
            End Using

            ' Load daily statistics
            Dim today = DateTime.Today.ToString("yyyy-MM-dd")
            Dim dailySql = "SELECT COUNT(*) as daily_bets, SUM(actual_profit) as daily_profit FROM bets WHERE DATE(bet_date) = ? AND result != 'Pending'"
            Using cmd As New SQLiteCommand(dailySql, dbConnection)
                cmd.Parameters.AddWithValue("@date", today)
                Using reader = cmd.ExecuteReader()
                    If reader.Read() Then
                        dailyBets = Convert.ToInt32(reader("daily_bets"))
                        dailyProfit = Convert.ToDecimal(reader("daily_profit"))
                    End If
                End Using
            End Using

            ' Update current bankroll
            currentBankroll = initialBankroll + totalProfit

        Catch ex As Exception
            logger($"Error loading bankroll stats: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub ConnectToEQ12Systems()
        Try
            ' Check for EQ12 backtester integration
            Dim backtesterPath = "C:\EQ12\eq12_backtester"
            If Directory.Exists(backtesterPath) Then
                logger("Connected to EQ12 backtester system", "SUCCESS")
            End If

            ' Check for EdgeGod integration
            Dim edgegodPath = "C:\EQ12\EdgeGodParlays"
            If Directory.Exists(edgegodPath) Then
                logger("Connected to EdgeGod Parlays system", "SUCCESS")
            End If

        Catch ex As Exception
            logger($"Error connecting to EQ12 systems: {ex.Message}", "ERROR")
        End Try
    End Sub

    Public Function GetCurrentBankroll() As Dictionary(Of String, Decimal)
        Try
            ' Refresh stats
            LoadBankrollStats()

            ' Calculate metrics
            Dim winRate = If(totalBets > 0, CDec(winningBets) / CDec(totalBets), 0D)
            Dim roi = If(initialBankroll > 0, totalProfit / initialBankroll, 0D)
            Dim sharpeRatio = CalculateSharpeRatio()
            Dim riskLevel = CalculateRiskLevel()

            Dim bankrollData = New Dictionary(Of String, Decimal) From {
                {"current_bankroll", currentBankroll},
                {"initial_bankroll", initialBankroll},
                {"total_profit", totalProfit},
                {"daily_profit", dailyProfit},
                {"win_rate", winRate},
                {"roi", roi},
                {"total_bets", totalBets},
                {"winning_bets", winningBets},
                {"daily_bets", dailyBets},
                {"sharpe_ratio", CDec(sharpeRatio)},
                {"risk_level", CDec(riskLevel)},
                {"daily_budget_remaining", dailyBudget - GetDailyWagered()},
                {"consecutive_losses", consecutiveLosses}
            }

            ' Raise event
            RaiseEvent BankrollUpdated(bankrollData)

            Return bankrollData

        Catch ex As Exception
            logger($"Error getting current bankroll: {ex.Message}", "ERROR")
            Return New Dictionary(Of String, Decimal)
        End Try
    End Function

    Private Function CalculateSharpeRatio() As Double
        Try
            ' Simple Sharpe ratio calculation
            ' Would need daily returns for proper calculation
            If totalBets < 10 Then Return 0.0

            Dim averageReturn = CDbl(totalProfit) / totalBets
            Dim standardDeviation = CalculateReturnStandardDeviation()

            If standardDeviation > 0 Then
                Return averageReturn / standardDeviation
            End If

            Return 0.0

        Catch ex As Exception
            logger($"Error calculating Sharpe ratio: {ex.Message}", "ERROR")
            Return 0.0
        End Try
    End Function

    Private Function CalculateReturnStandardDeviation() As Double
        Try
            ' Calculate standard deviation of bet returns
            Dim sql = "SELECT actual_profit / stake as return_rate FROM bets WHERE result != 'Pending' AND stake > 0"
            Dim returns As New List(Of Double)

            Using cmd As New SQLiteCommand(sql, dbConnection)
                Using reader = cmd.ExecuteReader()
                    While reader.Read()
                        returns.Add(Convert.ToDouble(reader("return_rate")))
                    End While
                End Using
            End Using

            If returns.Count < 2 Then Return 0.0

            Dim mean = returns.Average()
            Dim variance = returns.Select(Function(x) Math.Pow(x - mean, 2)).Average()

            Return Math.Sqrt(variance)

        Catch ex As Exception
            logger($"Error calculating standard deviation: {ex.Message}", "ERROR")
            Return 0.0
        End Try
    End Function

    Private Function CalculateRiskLevel() As Double
        Try
            ' Risk level based on various factors
            Dim riskScore As Double = 0

            ' Factor 1: Daily loss percentage
            If dailyProfit < 0 Then
                riskScore += Math.Abs(CDbl(dailyProfit)) / CDbl(currentBankroll) * 0.3
            End If

            ' Factor 2: Consecutive losses
            riskScore += (consecutiveLosses / 10.0) * 0.2

            ' Factor 3: Bet size relative to bankroll
            Dim avgBetSize = GetAverageBetSize()
            riskScore += (CDbl(avgBetSize) / CDbl(currentBankroll)) * 0.25

            ' Factor 4: Win rate deviation from expected
            Dim winRate = If(totalBets > 0, CDbl(winningBets) / CDbl(totalBets), 0.5)
            If winRate < 0.5 Then
                riskScore += (0.5 - winRate) * 0.25
            End If

            Return Math.Min(1.0, riskScore)

        Catch ex As Exception
            logger($"Error calculating risk level: {ex.Message}", "ERROR")
            Return 0.5
        End Try
    End Function

    Private Function GetDailyWagered() As Decimal
        Try
            Dim today = DateTime.Today.ToString("yyyy-MM-dd")
            Dim sql = "SELECT SUM(stake) as total_wagered FROM bets WHERE DATE(bet_date) = ?"

            Using cmd As New SQLiteCommand(sql, dbConnection)
                cmd.Parameters.AddWithValue("@date", today)
                Dim result = cmd.ExecuteScalar()
                If result IsNot Nothing AndAlso Not IsDBNull(result) Then
                    Return Convert.ToDecimal(result)
                End If
            End Using

            Return 0D

        Catch ex As Exception
            logger($"Error getting daily wagered amount: {ex.Message}", "ERROR")
            Return 0D
        End Try
    End Function

    Private Function GetAverageBetSize() As Decimal
        Try
            Dim sql = "SELECT AVG(stake) as avg_stake FROM bets WHERE result != 'Pending'"
            Using cmd As New SQLiteCommand(sql, dbConnection)
                Dim result = cmd.ExecuteScalar()
                If result IsNot Nothing AndAlso Not IsDBNull(result) Then
                    Return Convert.ToDecimal(result)
                End If
            End Using

            Return 0D

        Catch ex As Exception
            logger($"Error getting average bet size: {ex.Message}", "ERROR")
            Return 0D
        End Try
    End Function

    Public Function CalculateKellyBetSize(expectedValue As Decimal, probability As Double, odds As Decimal) As Decimal
        Try
            If expectedValue <= 0 OrElse probability <= 0 OrElse probability >= 1 Then
                Return 0D ' No bet if no edge or invalid probability
            End If

            ' Convert American odds to decimal odds
            Dim decimalOdds As Double
            If odds > 0 Then
                decimalOdds = (CDbl(odds) / 100.0) + 1
            Else
                decimalOdds = (100.0 / Math.Abs(CDbl(odds))) + 1
            End If

            ' Kelly formula: f = (bp - q) / b
            ' Where: b = odds received, p = probability of winning, q = probability of losing
            Dim b = decimalOdds - 1
            Dim p = probability
            Dim q = 1 - probability

            Dim kellyFraction = (b * p - q) / b

            ' Apply conservative fraction
            kellyFraction = kellyFraction * Me.kellyFraction

            ' Calculate bet size
            Dim betSize = currentBankroll * CDec(kellyFraction)

            ' Apply maximum bet size limit
            Dim maxBet = currentBankroll * CDec(maxBetPercentage)
            betSize = Math.Min(betSize, maxBet)

            ' Ensure positive and not zero
            betSize = Math.Max(0D, betSize)

            ' Round to nearest dollar
            betSize = Math.Round(betSize, 0)

            ' Raise event
            RaiseEvent KellySizeCalculated(betSize, CDbl(expectedValue), probability)

            logger($"Kelly bet size calculated: ${betSize:F2} (EV: {expectedValue:P2}, Prob: {probability:P2})", "INFO")

            Return betSize

        Catch ex As Exception
            logger($"Error calculating Kelly bet size: {ex.Message}", "ERROR")
            Return 0D
        End Try
    End Function

    Public Sub RecordBet(betSize As Decimal, gameData As Dictionary(Of String, Object))
        Try
            Dim betDate = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
            Dim sport = If(gameData.ContainsKey("sport"), gameData("sport").ToString(), "Unknown")
            Dim teams = If(gameData.ContainsKey("teams"), gameData("teams").ToString(), "Unknown vs Unknown")

            Dim sql = "INSERT INTO bets (bet_date, sport, market_type, selection, odds, stake, potential_win, source, bet_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

            Using cmd As New SQLiteCommand(sql, dbConnection)
                cmd.Parameters.AddWithValue("@bet_date", betDate)
                cmd.Parameters.AddWithValue("@sport", sport)
                cmd.Parameters.AddWithValue("@market_type", "Moneyline") ' Default
                cmd.Parameters.AddWithValue("@selection", teams)
                cmd.Parameters.AddWithValue("@odds", 100) ' Placeholder
                cmd.Parameters.AddWithValue("@stake", betSize)
                cmd.Parameters.AddWithValue("@potential_win", betSize * 2D) ' Placeholder
                cmd.Parameters.AddWithValue("@source", "Auto")
                cmd.Parameters.AddWithValue("@bet_type", "Single")

                cmd.ExecuteNonQuery()
            End Using

            ' Update daily bets
            dailyBets += 1

            logger($"Bet recorded: ${betSize:F2} on {teams}", "SUCCESS")

        Catch ex As Exception
            logger($"Error recording bet: {ex.Message}", "ERROR")
        End Try
    End Sub

    Public Function CheckRiskLimits(proposedBetSize As Decimal) As Dictionary(Of String, Object)
        Try
            Dim riskCheck = New Dictionary(Of String, Object) From {
                {"approved", True},
                {"warnings", New List(Of String)},
                {"risk_level", "Low"}
            }

            ' Check daily loss limit
            If Math.Abs(dailyProfit) >= dailyLossLimit Then
                riskCheck("approved") = False
                CType(riskCheck("warnings"), List(Of String)).Add("Daily loss limit reached")
                RaiseEvent RiskLimitReached("Daily Loss", Math.Abs(dailyProfit))
            End If

            ' Check daily budget
            Dim dailyWagered = GetDailyWagered()
            If dailyWagered + proposedBetSize > dailyBudget Then
                riskCheck("approved") = False
                CType(riskCheck("warnings"), List(Of String)).Add("Daily budget exceeded")
            End If

            ' Check maximum bet size
            Dim maxBet = currentBankroll * CDec(maxBetPercentage)
            If proposedBetSize > maxBet Then
                riskCheck("approved") = False
                CType(riskCheck("warnings"), List(Of String)).Add($"Bet size exceeds {maxBetPercentage:P0} limit")
            End If

            ' Check consecutive losses
            If consecutiveLosses >= maxConsecutiveLosses Then
                riskCheck("approved") = False
                CType(riskCheck("warnings"), List(Of String)).Add("Maximum consecutive losses reached")
            End If

            ' Determine risk level
            Dim warningCount = CType(riskCheck("warnings"), List(Of String)).Count
            riskCheck("risk_level") = If(warningCount = 0, "Low", If(warningCount <= 2, "Medium", "High"))

            Return riskCheck

        Catch ex As Exception
            logger($"Error checking risk limits: {ex.Message}", "ERROR")
            Return New Dictionary(Of String, Object) From {
                {"approved", False},
                {"warnings", New List(Of String) From {"Risk check failed"}},
                {"risk_level", "High"}
            }
        End Try
    End Function

    Public Sub Dispose()
        Try
            ' Save final state
            SaveConfigToDB()

            ' Close database connection
            dbConnection?.Close()
            dbConnection?.Dispose()

            logger("Bankroll Manager disposed", "INFO")

        Catch ex As Exception
            logger($"Error disposing Bankroll Manager: {ex.Message}", "ERROR")
        End Try
    End Sub

End Class
