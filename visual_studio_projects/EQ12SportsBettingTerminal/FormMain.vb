Imports Newtonsoft.Json.Linq
Imports System.IO
Imports System.Threading.Tasks

Public Class FormMain
    Private config As JObject
    Private bankrollTab As BankrollModule
    Private WithEvents timer As New Timer()

    Private Sub FormMain_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        Me.Text = "EQ12 Sports Betting Quant Terminal – Final Form"
        Me.WindowState = FormWindowState.Maximized
        Me.Icon = LoadEQ12Icon()

        ' Load configuration
        Dim cfgPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Config\config.json")
        If Not File.Exists(cfgPath) Then
            MessageBox.Show("Missing Config\config.json - Please configure API keys and settings", "Configuration Required", MessageBoxButtons.OK, MessageBoxIcon.Warning)
            Application.Exit()
            Return
        End If

        Try
            config = JObject.Parse(File.ReadAllText(cfgPath))
            InitializeApplication()
        Catch ex As Exception
            MessageBox.Show($"Failed to load configuration: {ex.Message}", "Configuration Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Application.Exit()
        End Try
    End Sub

    Private Sub InitializeApplication()
        Try
            ' Initialize database and core systems
            InitializeDatabase()

            ' Create main tab interface
            Dim mainTabs As New TabControl With {
                .Dock = DockStyle.Fill,
                .Font = New Font("Segoe UI", 9.75F, FontStyle.Regular)
            }

            ' Create tab pages
            Dim tpOddsAPI = New TabPage("📡 Odds API") With {.BackColor = Color.White}
            Dim tpBrowser = New TabPage("🌐 Browser Scrapers") With {.BackColor = Color.White}
            Dim tpArbitrage = New TabPage("⚡ Arbitrage") With {.BackColor = Color.White}
            Dim tpBankroll = New TabPage("💰 Bankroll") With {.BackColor = Color.White}
            Dim tpLLM = New TabPage("🤖 LLM Insights") With {.BackColor = Color.White}
            Dim tpSync = New TabPage("🔄 GitHub & Alerts") With {.BackColor = Color.White}
            Dim tpAPI = New TabPage("🔌 API Server") With {.BackColor = Color.White}
            Dim tpDeliverables = New TabPage("📝 Content Engine") With {.BackColor = Color.White}
            Dim tpCLI = New TabPage("⌨️ CLI Tools") With {.BackColor = Color.White}
            Dim tpLinkAnalytics = New TabPage("📊 Link Analytics") With {.BackColor = Color.White}
            Dim tpLinkSafety = New TabPage("🔐 Link Safety") With {.BackColor = Color.White}

            ' Initialize modules with configuration
            Dim oddsApiModule = New OddsApiModule(config)
            Dim browserModule = New BrowserModule(config)
            Dim arbitrageModule = New ArbitrageModule(config)
            bankrollTab = New BankrollModule(config)
            Dim llmModule = New LlmModule(config, bankrollTab)
            Dim syncModule = New SyncAndAlertsModule(config)
            Dim apiModule = New LocalApiServerModule(config)
            Dim deliverablesModule = New DeliverablesModule()
            Dim cliModule = New CLIModule(config)
            Dim linkAnalyticsModule = New LinkAnalyticsModule(config)
            Dim linkSafetyModule = New LinkSafetyModule()

            ' Wire up event handlers for real-time updates
            AddHandler DBWriter.DbChanged, Sub() RefreshAllModules()
            AddHandler DBWriter.BetAdded, Sub(betId As Integer) OnBetAdded(betId)
            AddHandler DBWriter.ArbitrageDetected, Sub(arbId As Integer) OnArbitrageDetected(arbId)
            AddHandler DBWriter.LineMovement, Sub(eventId As String, market As String, book As String, oldOdds As Integer, newOdds As Integer) OnLineMovement(eventId, market, book, oldOdds, newOdds)

            ' Add modules to tabs
            tpOddsAPI.Controls.Add(oddsApiModule)
            tpBrowser.Controls.Add(browserModule)
            tpArbitrage.Controls.Add(arbitrageModule)
            tpBankroll.Controls.Add(bankrollTab)
            tpLLM.Controls.Add(llmModule)
            tpSync.Controls.Add(syncModule)
            tpAPI.Controls.Add(apiModule)
            tpDeliverables.Controls.Add(deliverablesModule)
            tpCLI.Controls.Add(cliModule)
            tpLinkAnalytics.Controls.Add(linkAnalyticsModule)
            tpLinkSafety.Controls.Add(linkSafetyModule)

            ' Add all tabs to main control
            mainTabs.TabPages.AddRange({tpOddsAPI, tpBrowser, tpArbitrage, tpBankroll, tpLLM, tpSync, tpAPI, tpDeliverables, tpCLI, tpLinkAnalytics, tpLinkSafety})

            ' Add status bar
            Dim statusBar = CreateStatusBar()

            ' Add to form
            Me.Controls.Add(mainTabs)
            Me.Controls.Add(statusBar)

            ' Start local API server
            Task.Run(Sub() LocalApiServer.Start(config))

            ' Start periodic refresh timer (every 30 seconds)
            timer.Interval = 30000
            timer.Start()

            ' Send startup notification
            Task.Run(Sub() SendStartupNotification())

            ' Log application startup
            DBWriter.LogPerformanceMetric("application", "startup_success", 1, "count", "FormMain")

        Catch ex As Exception
            MessageBox.Show($"Failed to initialize application: {ex.Message}", "Initialization Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
            Application.Exit()
        End Try
    End Sub

    Private Sub InitializeDatabase()
        Try
            ' Ensure database directory exists
            Dim dbPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Data")
            If Not Directory.Exists(dbPath) Then
                Directory.CreateDirectory(dbPath)
            End If

            ' Initialize database with schema
            Dim schemaPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Data\schema.sql")
            If File.Exists(schemaPath) Then
                Console.WriteLine("Database schema initialized successfully")
            Else
                MessageBox.Show("Warning: Database schema file not found. Some features may not work correctly.", "Schema Warning", MessageBoxButtons.OK, MessageBoxIcon.Warning)
            End If

        Catch ex As Exception
            Throw New Exception($"Database initialization failed: {ex.Message}", ex)
        End Try
    End Sub

    Private Function CreateStatusBar() As StatusStrip
        Dim statusBar As New StatusStrip()

        Dim lblStatus As New ToolStripStatusLabel("Ready") With {
            .Name = "lblStatus",
            .Spring = True,
            .TextAlign = ContentAlignment.MiddleLeft
        }

        Dim lblBankroll As New ToolStripStatusLabel() With {
            .Name = "lblBankroll",
            .Text = "Bankroll: Loading...",
            .BorderSides = ToolStripStatusLabelBorderSides.Left
        }

        Dim lblTime As New ToolStripStatusLabel() With {
            .Name = "lblTime",
            .Text = DateTime.Now.ToString("HH:mm:ss"),
            .BorderSides = ToolStripStatusLabelBorderSides.Left
        }

        Dim lblAPI As New ToolStripStatusLabel() With {
            .Name = "lblAPI",
            .Text = "API: Starting...",
            .BorderSides = ToolStripStatusLabelBorderSides.Left
        }

        statusBar.Items.AddRange({lblStatus, lblBankroll, lblTime, lblAPI})
        statusBar.Dock = DockStyle.Bottom

        Return statusBar
    End Function

    Private Sub Timer_Tick(sender As Object, e As EventArgs) Handles timer.Tick
        Try
            ' Update time display
            UpdateStatusBar("lblTime", DateTime.Now.ToString("HH:mm:ss"))

            ' Update bankroll display
            Dim currentBankroll = DBWriter.GetCurrentBankroll()
            UpdateStatusBar("lblBankroll", $"Bankroll: ${currentBankroll:F2}")

            ' Check API server status
            Task.Run(Sub() CheckAPIStatus())

        Catch ex As Exception
            UpdateStatusBar("lblStatus", $"Error: {ex.Message}")
        End Try
    End Sub

    Private Sub UpdateStatusBar(labelName As String, text As String)
        Try
            Dim statusBar = TryCast(Me.Controls.OfType(Of StatusStrip)().FirstOrDefault(), StatusStrip)
            If statusBar IsNot Nothing Then
                Dim label = TryCast(statusBar.Items(labelName), ToolStripStatusLabel)
                If label IsNot Nothing Then
                    label.Text = text
                End If
            End If
        Catch ex As Exception
            Console.WriteLine($"Failed to update status bar: {ex.Message}")
        End Try
    End Sub

    Private Async Sub CheckAPIStatus()
        Try
            Using client As New System.Net.Http.HttpClient()
                client.Timeout = TimeSpan.FromSeconds(5)
                Dim response = Await client.GetAsync($"{config("api")("host")}:{config("api")("port")}/health")

                If response.IsSuccessStatusCode Then
                    Invoke(Sub() UpdateStatusBar("lblAPI", "API: Online"))
                Else
                    Invoke(Sub() UpdateStatusBar("lblAPI", "API: Error"))
                End If
            End Using
        Catch ex As Exception
            Invoke(Sub() UpdateStatusBar("lblAPI", "API: Offline"))
        End Try
    End Sub

    Private Sub RefreshAllModules()
        Try
            ' Refresh bankroll module
            If bankrollTab IsNot Nothing Then
                bankrollTab.RefreshData()
            End If

            ' Update status
            UpdateStatusBar("lblStatus", "Data refreshed")

        Catch ex As Exception
            UpdateStatusBar("lblStatus", $"Refresh error: {ex.Message}")
        End Try
    End Sub

    Private Async Sub OnBetAdded(betId As Integer)
        Try
            ' Send bet notification
            Await Alerts.MultiChannelAlertAsync(config, "bet_placed", "📊 New Bet Placed", $"Bet ID {betId} has been logged to the system.", "medium", Nothing, betId)

            ' Update status
            UpdateStatusBar("lblStatus", $"Bet {betId} added")

        Catch ex As Exception
            Console.WriteLine($"Failed to handle bet added event: {ex.Message}")
        End Try
    End Sub

    Private Async Sub OnArbitrageDetected(arbId As Integer)
        Try
            ' Get arbitrage details from database
            Using conn As New System.Data.SQLite.SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()
                Dim sql = "SELECT * FROM arbitrage_opportunities WHERE id = @id"

                Using cmd As New System.Data.SQLite.SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@id", arbId)

                    Using reader = cmd.ExecuteReader()
                        If reader.Read() Then
                            Await Alerts.ArbitrageAlertAsync(
                                config,
                                reader("event_id").ToString(),
                                reader("sport").ToString(),
                                reader("side_a_book").ToString(),
                                CInt(reader("side_a_odds")),
                                reader("side_b_book").ToString(),
                                CInt(reader("side_b_odds")),
                                CDbl(reader("profit_percentage")),
                                CDbl(reader("guaranteed_profit"))
                            )
                        End If
                    End Using
                End Using
            End Using

            UpdateStatusBar("lblStatus", $"🔥 Arbitrage detected (ID: {arbId})")

        Catch ex As Exception
            Console.WriteLine($"Failed to handle arbitrage detected event: {ex.Message}")
        End Try
    End Sub

    Private Async Sub OnLineMovement(eventId As String, market As String, book As String, oldOdds As Integer, newOdds As Integer)
        Try
            Dim changePercent = Math.Abs((newOdds - oldOdds) / oldOdds * 100)

            ' Only alert on significant movements (>= 10%)
            If changePercent >= 10 Then
                Await Alerts.LineMovementAlertAsync(config, eventId, market, book, oldOdds, newOdds, changePercent)
            End If

            UpdateStatusBar("lblStatus", $"Line moved: {book} {If(newOdds > oldOdds, "↑", "↓")}{Math.Abs(newOdds - oldOdds)}")

        Catch ex As Exception
            Console.WriteLine($"Failed to handle line movement event: {ex.Message}")
        End Try
    End Sub

    Private Async Sub SendStartupNotification()
        Try
            Await Alerts.SystemStatusAlertAsync(config, "online", "EQ12 Terminal", "Sports Betting Terminal has started successfully and is ready for operation.")
        Catch ex As Exception
            Console.WriteLine($"Failed to send startup notification: {ex.Message}")
        End Try
    End Sub

    Private Function LoadEQ12Icon() As Icon
        Try
            ' Try to load custom icon, fallback to default
            Dim iconPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Resources\eq12.ico")
            If File.Exists(iconPath) Then
                Return New Icon(iconPath)
            End If
        Catch ex As Exception
            Console.WriteLine($"Failed to load custom icon: {ex.Message}")
        End Try

        ' Return default system icon
        Return SystemIcons.Application
    End Function

    Private Sub FormMain_FormClosing(sender As Object, e As FormClosingEventArgs) Handles MyBase.FormClosing
        Try
            ' Stop timer
            timer?.Stop()

            ' Log shutdown
            DBWriter.LogPerformanceMetric("application", "shutdown", 1, "count", "FormMain")

            ' Send shutdown notification
            Task.Run(Async Sub()
                Try
                    Await Alerts.SystemStatusAlertAsync(config, "offline", "EQ12 Terminal", "Sports Betting Terminal is shutting down.")
                Catch ex As Exception
                    Console.WriteLine($"Failed to send shutdown notification: {ex.Message}")
                End Try
            End Sub)

        Catch ex As Exception
            Console.WriteLine($"Error during form closing: {ex.Message}")
        End Try
    End Sub

End Class
