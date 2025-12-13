' EQ12 Sports Betting Quant Terminal - Main Form
' Professional sports betting terminal with real-time odds, model predictions,
' bankroll management, and automated trading capabilities
'
' Features:
' - Multi-sportsbook odds aggregation
' - AI-powered prediction models
' - Kelly Criterion bet sizing
' - Real-time P&L tracking
' - Telegram/Discord alerts
' - Twitter sentiment analysis
' - Automated bet placement

Imports System.ComponentModel
Imports System.Drawing
Imports System.Net.Http
Imports System.Threading.Tasks
Imports System.Windows.Forms
Imports Newtonsoft.Json

Public Class MainForm

    ' Core Components
    Private WithEvents oddsAggregator As New OddsAggregator()
    Private WithEvents bettingModel As New BettingModel()
    Private WithEvents bankrollManager As New BankrollManager()
    Private WithEvents telegramBot As New TelegramBot()
    Private WithEvents twitterAPI As New TwitterAPI()
    Private WithEvents apiManager As New APIManager()
    Private WithEvents dbManager As New DatabaseManager()

    ' UI Update Timer
    Private WithEvents updateTimer As New Timer()

    ' Current Data
    Private currentOdds As New Dictionary(Of String, Object)
    Private currentBets As New List(Of Object)
    Private bankrollData As New Dictionary(Of String, Decimal)

    Public Sub New()
        InitializeComponent()
        InitializeEQ12Terminal()
    End Sub

    Private Sub InitializeEQ12Terminal()
        ' Initialize terminal components
        Try
            Me.Text = "EQ12 Sports Betting Quant Terminal v2.0"
            Me.WindowState = FormWindowState.Maximized

            ' Initialize database connection
            dbManager.InitializeDatabase()

            ' Load configuration
            LoadConfiguration()

            ' Initialize APIs
            InitializeAPIs()

            ' Setup UI update timer (every 5 seconds)
            updateTimer.Interval = 5000
            updateTimer.Enabled = True

            ' Load initial data
            LoadInitialData()

            AddHandler Me.FormClosing, AddressOf MainForm_FormClosing

            ' Log startup
            LogMessage("EQ12 Terminal initialized successfully", "SUCCESS")

        Catch ex As Exception
            LogMessage($"Error initializing EQ12 Terminal: {ex.Message}", "ERROR")
            MessageBox.Show($"Initialization Error: {ex.Message}", "EQ12 Terminal Error",
                          MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    Private Sub LoadConfiguration()
        ' Load API credentials and settings from EQ12 config
        Dim configPath As String = "C:\EQ12\configs\api_credentials.json"

        If IO.File.Exists(configPath) Then
            Try
                Dim configJson As String = IO.File.ReadAllText(configPath)
                Dim config = JsonConvert.DeserializeObject(Of Dictionary(Of String, Object))(configJson)

                ' Configure API managers
                apiManager.LoadConfiguration(config)
                telegramBot.LoadConfiguration(config)
                twitterAPI.LoadConfiguration(config)

                LogMessage("Configuration loaded successfully", "INFO")
            Catch ex As Exception
                LogMessage($"Error loading configuration: {ex.Message}", "ERROR")
            End Try
        Else
            LogMessage("Configuration file not found, using defaults", "WARNING")
        End If
    End Sub

    Private Sub InitializeAPIs()
        ' Initialize all API connections
        Task.Run(Sub()
                     Try
                         ' Initialize odds APIs
                         oddsAggregator.InitializeAPIs()

                         ' Initialize social media APIs
                         telegramBot.Initialize()
                         twitterAPI.Initialize()

                         ' Initialize betting model
                         bettingModel.LoadModel()

                         Me.BeginInvoke(Sub()
                                            LogMessage("All APIs initialized", "SUCCESS")
                                            UpdateStatusBar("Connected to all services")
                                        End Sub)

                     Catch ex As Exception
                         Me.BeginInvoke(Sub()
                                            LogMessage($"API initialization error: {ex.Message}", "ERROR")
                                        End Sub)
                     End Try
                 End Sub)
    End Sub

    Private Sub LoadInitialData()
        ' Load bankroll data
        bankrollData = bankrollManager.GetCurrentBankroll()
        UpdateBankrollDisplay()

        ' Load recent bets
        currentBets = dbManager.GetRecentBets(50)
        UpdateBetsGrid()

        ' Start odds feed
        StartOddsFeed()
    End Sub

    Private Sub StartOddsFeed()
        ' Start real-time odds aggregation
        Task.Run(Sub()
                     While True
                         Try
                             Dim odds = oddsAggregator.GetLatestOdds()

                             Me.BeginInvoke(Sub()
                                                currentOdds = odds
                                                UpdateOddsDisplay()
                                                CheckArbitrageOpportunities()
                                                CheckValueBets()
                                            End Sub)

                             Threading.Thread.Sleep(10000) ' Update every 10 seconds

                         Catch ex As Exception
                             Me.BeginInvoke(Sub()
                                                LogMessage($"Odds feed error: {ex.Message}", "ERROR")
                                            End Sub)
                         End Try
                     End While
                 End Sub)
    End Sub

    Private Sub UpdateOddsDisplay()
        ' Update the odds display grid
        Try
            oddsDataGridView.Rows.Clear()

            For Each game In currentOdds
                Dim gameData = TryCast(game.Value, Dictionary(Of String, Object))
                If gameData IsNot Nothing Then

                    ' Calculate best odds and arbitrage opportunities
                    Dim bestOdds = CalculateBestOdds(gameData)
                    Dim arbOpportunity = CalculateArbitrageOpportunity(gameData)

                    ' Get model prediction
                    Dim prediction = bettingModel.GetPrediction(gameData)

                    ' Add row to grid
                    Dim row As New DataGridViewRow()
                    row.CreateCells(oddsDataGridView)

                    row.Cells(0).Value = gameData("game_id")
                    row.Cells(1).Value = gameData("teams")
                    row.Cells(2).Value = gameData("sport")
                    row.Cells(3).Value = bestOdds("team1")
                    row.Cells(4).Value = bestOdds("team2")
                    row.Cells(5).Value = prediction("probability")
                    row.Cells(6).Value = prediction("expected_value")
                    row.Cells(7).Value = If(arbOpportunity > 0, arbOpportunity.ToString("P2"), "")

                    ' Color coding for value bets and arbitrage
                    If prediction("expected_value") > 0.05 Then
                        row.DefaultCellStyle.BackColor = Color.LightGreen ' Value bet
                    ElseIf arbOpportunity > 0 Then
                        row.DefaultCellStyle.BackColor = Color.LightBlue ' Arbitrage opportunity
                    End If

                    oddsDataGridView.Rows.Add(row)
                End If
            Next

        Catch ex As Exception
            LogMessage($"Error updating odds display: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub CheckArbitrageOpportunities()
        ' Scan for arbitrage opportunities and alert
        Try
            For Each game In currentOdds
                Dim gameData = TryCast(game.Value, Dictionary(Of String, Object))
                If gameData IsNot Nothing Then
                    Dim arbProfit = CalculateArbitrageOpportunity(gameData)

                    If arbProfit > 0.02 Then ' 2% minimum profit
                        Dim message = $"🔥 ARBITRAGE ALERT: {gameData("teams")} - {arbProfit:P2} profit opportunity!"

                        ' Send Telegram alert
                        telegramBot.SendAlert(message)

                        ' Log alert
                        LogMessage(message, "ALERT")

                        ' Update UI
                        ShowAlert(message, Color.Orange)
                    End If
                End If
            Next

        Catch ex As Exception
            LogMessage($"Error checking arbitrage: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub CheckValueBets()
        ' Check for value betting opportunities
        Try
            For Each game In currentOdds
                Dim gameData = TryCast(game.Value, Dictionary(Of String, Object))
                If gameData IsNot Nothing Then
                    Dim prediction = bettingModel.GetPrediction(gameData)
                    Dim expectedValue = CDec(prediction("expected_value"))

                    If expectedValue > 0.05 Then ' 5% minimum edge
                        Dim kellyBetSize = bankrollManager.CalculateKellyBetSize(
                            expectedValue,
                            CDec(prediction("probability")),
                            CDec(gameData("best_odds"))
                        )

                        Dim message = $"💰 VALUE BET: {gameData("teams")} - EV: {expectedValue:P2}, Kelly: {kellyBetSize:C}"

                        ' Send alert
                        telegramBot.SendAlert(message)

                        ' Log
                        LogMessage(message, "VALUE")

                        ' Update UI
                        ShowAlert(message, Color.Green)

                        ' Auto-bet if enabled
                        If chkAutoBet.Checked Then
                            PlaceAutomaticBet(gameData, kellyBetSize, expectedValue)
                        End If
                    End If
                End If
            Next

        Catch ex As Exception
            LogMessage($"Error checking value bets: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub PlaceAutomaticBet(gameData As Dictionary(Of String, Object), betSize As Decimal, expectedValue As Decimal)
        ' Place automatic bet through API
        Try
            ' Risk management checks
            If betSize > bankrollData("current_bankroll") * 0.05 Then ' Max 5% of bankroll
                LogMessage($"Bet size {betSize:C} exceeds 5% limit, reducing", "WARNING")
                betSize = bankrollData("current_bankroll") * 0.05
            End If

            If bankrollData("daily_bets") >= 10 Then ' Max 10 bets per day
                LogMessage("Daily bet limit reached, skipping auto-bet", "WARNING")
                Return
            End If

            ' Place bet via API
            Dim betResult = apiManager.PlaceBet(gameData, betSize)

            If betResult("success") Then
                ' Update bankroll
                bankrollManager.RecordBet(betSize, gameData)

                ' Send confirmation
                Dim confirmMsg = $"✅ AUTO-BET PLACED: {gameData("teams")} - {betSize:C} (EV: {expectedValue:P2})"
                telegramBot.SendAlert(confirmMsg)
                LogMessage(confirmMsg, "SUCCESS")

                ' Update UI
                UpdateBankrollDisplay()
                LoadRecentBets()
            Else
                LogMessage($"Auto-bet failed: {betResult("error")}", "ERROR")
            End If

        Catch ex As Exception
            LogMessage($"Error placing automatic bet: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub UpdateBankrollDisplay()
        ' Update bankroll information display
        Try
            bankrollData = bankrollManager.GetCurrentBankroll()

            lblCurrentBankroll.Text = bankrollData("current_bankroll").ToString("C")
            lblTotalProfit.Text = bankrollData("total_profit").ToString("C")
            lblROI.Text = bankrollData("roi").ToString("P2")
            lblWinRate.Text = bankrollData("win_rate").ToString("P1")
            lblSharpeRatio.Text = bankrollData("sharpe_ratio").ToString("F2")

            ' Update progress bars
            pbBankrollGrowth.Value = Math.Min(100, Math.Max(0, CInt(bankrollData("roi") * 100 + 50)))
            pbRiskLevel.Value = Math.Min(100, CInt(bankrollData("risk_level") * 100))

            ' Color coding for performance
            If bankrollData("roi") > 0 Then
                lblTotalProfit.ForeColor = Color.Green
                lblROI.ForeColor = Color.Green
            Else
                lblTotalProfit.ForeColor = Color.Red
                lblROI.ForeColor = Color.Red
            End If

        Catch ex As Exception
            LogMessage($"Error updating bankroll display: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub UpdateBetsGrid()
        ' Update recent bets grid
        Try
            betsDataGridView.Rows.Clear()

            For Each bet In currentBets
                Dim betData = TryCast(bet, Dictionary(Of String, Object))
                If betData IsNot Nothing Then
                    Dim row As New DataGridViewRow()
                    row.CreateCells(betsDataGridView)

                    row.Cells(0).Value = betData("date")
                    row.Cells(1).Value = betData("game")
                    row.Cells(2).Value = betData("bet_type")
                    row.Cells(3).Value = CDec(betData("amount")).ToString("C")
                    row.Cells(4).Value = betData("odds")
                    row.Cells(5).Value = betData("status")
                    row.Cells(6).Value = CDec(betData("profit")).ToString("C")

                    ' Color coding for wins/losses
                    If betData("status").ToString() = "Won" Then
                        row.DefaultCellStyle.ForeColor = Color.Green
                    ElseIf betData("status").ToString() = "Lost" Then
                        row.DefaultCellStyle.ForeColor = Color.Red
                    End If

                    betsDataGridView.Rows.Add(row)
                End If
            Next

        Catch ex As Exception
            LogMessage($"Error updating bets grid: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub LoadRecentBets()
        ' Reload recent bets from database
        currentBets = dbManager.GetRecentBets(50)
        UpdateBetsGrid()
    End Sub

    Private Function CalculateBestOdds(gameData As Dictionary(Of String, Object)) As Dictionary(Of String, Decimal)
        ' Calculate best available odds from all sportsbooks
        Dim bestOdds As New Dictionary(Of String, Decimal)

        Try
            Dim sportsbooks = TryCast(gameData("sportsbooks"), Dictionary(Of String, Object))
            If sportsbooks IsNot Nothing Then
                Dim maxTeam1 As Decimal = 0
                Dim maxTeam2 As Decimal = 0

                For Each book In sportsbooks
                    Dim bookData = TryCast(book.Value, Dictionary(Of String, Object))
                    If bookData IsNot Nothing Then
                        maxTeam1 = Math.Max(maxTeam1, CDec(bookData("team1_odds")))
                        maxTeam2 = Math.Max(maxTeam2, CDec(bookData("team2_odds")))
                    End If
                Next

                bestOdds("team1") = maxTeam1
                bestOdds("team2") = maxTeam2
            End If

        Catch ex As Exception
            LogMessage($"Error calculating best odds: {ex.Message}", "ERROR")
        End Try

        Return bestOdds
    End Function

    Private Function CalculateArbitrageOpportunity(gameData As Dictionary(Of String, Object)) As Decimal
        ' Calculate arbitrage profit percentage
        Try
            Dim bestOdds = CalculateBestOdds(gameData)

            If bestOdds.Count = 2 Then
                Dim impliedProb1 As Decimal = 1 / bestOdds("team1")
                Dim impliedProb2 As Decimal = 1 / bestOdds("team2")
                Dim totalImplied As Decimal = impliedProb1 + impliedProb2

                If totalImplied < 1 Then
                    Return (1 - totalImplied) ' Arbitrage profit percentage
                End If
            End If

        Catch ex As Exception
            LogMessage($"Error calculating arbitrage: {ex.Message}", "ERROR")
        End Try

        Return 0
    End Function

    Private Sub ShowAlert(message As String, color As Color)
        ' Show alert in UI
        Try
            Dim alertLabel As New Label()
            alertLabel.Text = message
            alertLabel.BackColor = color
            alertLabel.ForeColor = Color.White
            alertLabel.Dock = DockStyle.Top
            alertLabel.Height = 30
            alertLabel.TextAlign = ContentAlignment.MiddleLeft

            pnlAlerts.Controls.Add(alertLabel)

            ' Auto-remove after 30 seconds
            Dim removeTimer As New Timer()
            removeTimer.Interval = 30000
            AddHandler removeTimer.Tick, Sub()
                                             pnlAlerts.Controls.Remove(alertLabel)
                                             removeTimer.Dispose()
                                         End Sub
            removeTimer.Start()

        Catch ex As Exception
            LogMessage($"Error showing alert: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub LogMessage(message As String, level As String)
        ' Log message to file and display
        Try
            Dim timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
            Dim logEntry = $"[{timestamp}] [{level}] {message}"

            ' Add to log display
            If lstLog.InvokeRequired Then
                lstLog.BeginInvoke(Sub()
                                       lstLog.Items.Insert(0, logEntry)
                                       If lstLog.Items.Count > 1000 Then
                                           lstLog.Items.RemoveAt(lstLog.Items.Count - 1)
                                       End If
                                   End Sub)
            Else
                lstLog.Items.Insert(0, logEntry)
                If lstLog.Items.Count > 1000 Then
                    lstLog.Items.RemoveAt(lstLog.Items.Count - 1)
                End If
            End If

            ' Write to log file
            Dim logFile = "C:\EQ12\logs\terminal_log.txt"
            IO.File.AppendAllText(logFile, logEntry + Environment.NewLine)

        Catch ex As Exception
            ' Silent fail to prevent infinite loop
        End Try
    End Sub

    Private Sub UpdateStatusBar(message As String)
        ' Update status bar
        Try
            If statusStrip.InvokeRequired Then
                statusStrip.BeginInvoke(Sub()
                                            toolStripStatusLabel.Text = $"{DateTime.Now:HH:mm:ss} - {message}"
                                        End Sub)
            Else
                toolStripStatusLabel.Text = $"{DateTime.Now:HH:mm:ss} - {message}"
            End If
        Catch
            ' Silent fail
        End Try
    End Sub

    ' Event Handlers
    Private Sub updateTimer_Tick(sender As Object, e As EventArgs) Handles updateTimer.Tick
        ' Periodic UI updates
        UpdateBankrollDisplay()
        UpdateStatusBar("System running normally")
    End Sub

    Private Sub btnRefreshOdds_Click(sender As Object, e As EventArgs) Handles btnRefreshOdds.Click
        ' Manual odds refresh
        Task.Run(Sub()
                     Try
                         currentOdds = oddsAggregator.GetLatestOdds()
                         Me.BeginInvoke(Sub()
                                            UpdateOddsDisplay()
                                            LogMessage("Odds refreshed manually", "INFO")
                                        End Sub)
                     Catch ex As Exception
                         Me.BeginInvoke(Sub()
                                            LogMessage($"Manual refresh error: {ex.Message}", "ERROR")
                                        End Sub)
                     End Try
                 End Sub)
    End Sub

    Private Sub btnPlaceBet_Click(sender As Object, e As EventArgs) Handles btnPlaceBet.Click
        ' Manual bet placement
        If oddsDataGridView.SelectedRows.Count > 0 Then
            Dim selectedRow = oddsDataGridView.SelectedRows(0)
            Dim gameId = selectedRow.Cells(0).Value.ToString()

            ' Open bet placement dialog
            Dim betForm As New BetPlacementForm(gameId, currentOdds, bankrollData)
            If betForm.ShowDialog() = DialogResult.OK Then
                ' Refresh displays
                UpdateBankrollDisplay()
                LoadRecentBets()
                LogMessage($"Manual bet placed for game {gameId}", "INFO")
            End If
        Else
            MessageBox.Show("Please select a game to bet on.", "No Selection",
                          MessageBoxButtons.OK, MessageBoxIcon.Information)
        End If
    End Sub

    Private Sub btnSendTelegramTest_Click(sender As Object, e As EventArgs) Handles btnSendTelegramTest.Click
        ' Test Telegram integration
        Task.Run(Sub()
                     Try
                         telegramBot.SendAlert("🧪 EQ12 Terminal Test Message - All systems operational!")
                         Me.BeginInvoke(Sub()
                                            LogMessage("Test Telegram message sent", "INFO")
                                        End Sub)
                     Catch ex As Exception
                         Me.BeginInvoke(Sub()
                                            LogMessage($"Telegram test failed: {ex.Message}", "ERROR")
                                        End Sub)
                     End Try
                 End Sub)
    End Sub

    Private Sub MainForm_FormClosing(sender As Object, e As FormClosingEventArgs)
        ' Cleanup on close
        Try
            updateTimer.Stop()
            telegramBot.Dispose()
            twitterAPI.Dispose()
            dbManager.Dispose()

            LogMessage("EQ12 Terminal shutting down", "INFO")
        Catch ex As Exception
            ' Silent cleanup
        End Try
    End Sub

End Class
