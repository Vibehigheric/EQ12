Imports System.Net.Http
Imports Newtonsoft.Json.Linq
Imports System.Data
Imports System.Threading.Tasks

''' <summary>
''' Comprehensive Odds API integration for normalized data ingestion with multi-sport support
''' </summary>
Public Class OddsApiModule
    Inherits UserControl

    Private config As JObject
    Private WithEvents dgvOdds As New DataGridView()
    Private WithEvents btnIngestAll As New Button()
    Private WithEvents btnIngestSport As New Button()
    Private WithEvents cmbSports As New ComboBox()
    Private WithEvents cmbMarkets As New ComboBox()
    Private WithEvents lblStatus As New Label()
    Private WithEvents progressBar As New ProgressBar()
    Private WithEvents txtLog As New TextBox()

    Private ReadOnly httpClient As New HttpClient()
    Private isIngesting As Boolean = False

    Public Sub New(cfg As JObject)
        config = cfg
        InitializeComponent()
        LoadSportsAndMarkets()

        ' Configure HTTP client
        httpClient.Timeout = TimeSpan.FromSeconds(config("oddsapi")?("timeout_seconds")?.ToObject(Of Integer)() ?? 30)
    End Sub

    Private Sub InitializeComponent()
        Me.SuspendLayout()

        ' Main layout panel
        Dim mainPanel As New TableLayoutPanel() With {
            .Dock = DockStyle.Fill,
            .RowCount = 4,
            .ColumnCount = 1
        }
        mainPanel.RowStyles.Add(New RowStyle(SizeType.AutoSize))
        mainPanel.RowStyles.Add(New RowStyle(SizeType.AutoSize))
        mainPanel.RowStyles.Add(New RowStyle(SizeType.Percent, 60))
        mainPanel.RowStyles.Add(New RowStyle(SizeType.Percent, 40))

        ' Controls panel
        Dim controlsPanel As New FlowLayoutPanel() With {
            .Dock = DockStyle.Fill,
            .FlowDirection = FlowDirection.LeftToRight,
            .AutoSize = True,
            .Padding = New Padding(10)
        }

        ' Sport selection
        Dim lblSport As New Label() With {.Text = "Sport:", .AutoSize = True, .Anchor = AnchorStyles.Left}
        cmbSports.DropDownStyle = ComboBoxStyle.DropDownList
        cmbSports.Width = 150

        ' Market selection
        Dim lblMarket As New Label() With {.Text = "Market:", .AutoSize = True, .Anchor = AnchorStyles.Left}
        cmbMarkets.DropDownStyle = ComboBoxStyle.DropDownList
        cmbMarkets.Width = 150

        ' Action buttons
        btnIngestSport.Text = "Ingest Selected Sport"
        btnIngestSport.Width = 150
        btnIngestSport.BackColor = Color.LightBlue

        btnIngestAll.Text = "Ingest All Sports"
        btnIngestAll.Width = 120
        btnIngestAll.BackColor = Color.LightGreen

        controlsPanel.Controls.AddRange({lblSport, cmbSports, lblMarket, cmbMarkets, btnIngestSport, btnIngestAll})

        ' Status panel
        Dim statusPanel As New TableLayoutPanel() With {
            .Dock = DockStyle.Fill,
            .RowCount = 1,
            .ColumnCount = 2,
            .Padding = New Padding(10, 5, 10, 5)
        }
        statusPanel.ColumnStyles.Add(New ColumnStyle(SizeType.Percent, 80))
        statusPanel.ColumnStyles.Add(New ColumnStyle(SizeType.Percent, 20))

        lblStatus.Text = "Ready to ingest odds data"
        lblStatus.Dock = DockStyle.Fill
        lblStatus.AutoSize = False

        progressBar.Dock = DockStyle.Fill
        progressBar.Style = ProgressBarStyle.Continuous

        statusPanel.Controls.Add(lblStatus, 0, 0)
        statusPanel.Controls.Add(progressBar, 1, 0)

        ' Data grid
        ConfigureDataGrid()

        ' Log textbox
        txtLog.Multiline = True
        txtLog.ScrollBars = ScrollBars.Both
        txtLog.Dock = DockStyle.Fill
        txtLog.Font = New Font("Consolas", 9)
        txtLog.BackColor = Color.Black
        txtLog.ForeColor = Color.LimeGreen

        ' Add to main panel
        mainPanel.Controls.Add(controlsPanel, 0, 0)
        mainPanel.Controls.Add(statusPanel, 0, 1)
        mainPanel.Controls.Add(dgvOdds, 0, 2)
        mainPanel.Controls.Add(txtLog, 0, 3)

        Me.Controls.Add(mainPanel)
        Me.ResumeLayout()
    End Sub

    Private Sub ConfigureDataGrid()
        dgvOdds.Dock = DockStyle.Fill
        dgvOdds.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.AllCells
        dgvOdds.RowHeadersVisible = False
        dgvOdds.AllowUserToAddRows = False
        dgvOdds.AllowUserToDeleteRows = False
        dgvOdds.ReadOnly = True
        dgvOdds.BackgroundColor = Color.White
        dgvOdds.SelectionMode = DataGridViewSelectionMode.FullRowSelect

        ' Alternate row colors
        dgvOdds.AlternatingRowsDefaultCellStyle.BackColor = Color.AliceBlue

        ' Column header style
        dgvOdds.ColumnHeadersDefaultCellStyle.BackColor = Color.Navy
        dgvOdds.ColumnHeadersDefaultCellStyle.ForeColor = Color.White
        dgvOdds.ColumnHeadersDefaultCellStyle.Font = New Font("Segoe UI", 9, FontStyle.Bold)
    End Sub

    Private Sub LoadSportsAndMarkets()
        Try
            ' Load sports from config
            If config("sports") IsNot Nothing Then
                cmbSports.Items.Clear()
                For Each sport In config("sports")
                    cmbSports.Items.Add(sport.ToString())
                Next
                If cmbSports.Items.Count > 0 Then
                    cmbSports.SelectedIndex = 0
                End If
            End If

            ' Load markets from config
            If config("markets") IsNot Nothing Then
                cmbMarkets.Items.Clear()
                For Each market In config("markets")
                    cmbMarkets.Items.Add(market.ToString())
                Next
                If cmbMarkets.Items.Count > 0 Then
                    cmbMarkets.SelectedIndex = 0
                End If
            End If

        Catch ex As Exception
            LogMessage($"Error loading sports/markets: {ex.Message}", True)
        End Try
    End Sub

    Private Async Sub btnIngestSport_Click(sender As Object, e As EventArgs) Handles btnIngestSport.Click
        If isIngesting Then Return

        Dim selectedSport = cmbSports.SelectedItem?.ToString()
        Dim selectedMarket = cmbMarkets.SelectedItem?.ToString()

        If String.IsNullOrEmpty(selectedSport) OrElse String.IsNullOrEmpty(selectedMarket) Then
            MessageBox.Show("Please select a sport and market", "Selection Required", MessageBoxButtons.OK, MessageBoxIcon.Warning)
            Return
        End If

        Await IngestOddsData(selectedSport, selectedMarket)
    End Sub

    Private Async Sub btnIngestAll_Click(sender As Object, e As EventArgs) Handles btnIngestAll.Click
        If isIngesting Then Return

        Dim result = MessageBox.Show("This will ingest odds for all sports and markets. This may use significant API quota. Continue?", "Confirm Full Ingestion", MessageBoxButtons.YesNo, MessageBoxIcon.Question)
        If result = DialogResult.No Then Return

        Await IngestAllSportsData()
    End Sub

    Private Async Function IngestOddsData(sport As String, market As String) As Task
        isIngesting = True
        btnIngestSport.Enabled = False
        btnIngestAll.Enabled = False

        Try
            LogMessage($"Starting odds ingestion for {sport} - {market}", False)
            UpdateStatus($"Ingesting {sport} {market} odds...")
            progressBar.Style = ProgressBarStyle.Marquee

            Dim startTime = DateTime.UtcNow
            Dim apiKey = config("oddsapi")("key").ToString()
            Dim baseUrl = config("oddsapi")("base_url").ToString()
            Dim regions = config("oddsapi")("regions").ToString()
            Dim oddsFormat = config("oddsapi")("odds_format").ToString()
            Dim dateFormat = config("oddsapi")("date_format").ToString()

            ' Build API URL
            Dim url = $"{baseUrl}/sports/{sport}/odds/?apiKey={apiKey}&regions={regions}&markets={market}&oddsFormat={oddsFormat}&dateFormat={dateFormat}"

            LogMessage($"API Request: {url.Replace(apiKey, "***")}", False)

            ' Make API request
            Using response = Await httpClient.GetAsync(url)
                Dim responseTime = DateTime.UtcNow.Subtract(startTime).TotalMilliseconds

                If response.IsSuccessStatusCode Then
                    Dim jsonContent = Await response.Content.ReadAsStringAsync()
                    Dim oddsData = JArray.Parse(jsonContent)

                    LogMessage($"API Response: {oddsData.Count} events received in {responseTime:F0}ms", False)

                    ' Process and normalize the data
                    Dim processedCount = Await ProcessOddsData(oddsData, sport)

                    ' Update display
                    LoadOddsToGrid(sport, market)

                    UpdateStatus($"Successfully ingested {processedCount} events for {sport} {market}")
                    LogMessage($"Ingestion completed: {processedCount} events processed", False)

                    ' Record performance metrics
                    DBWriter.LogPerformanceMetric("api_latency", "odds_api_request", responseTime, "milliseconds", "OddsAPI")
                    DBWriter.LogPerformanceMetric("data_ingestion", "events_processed", processedCount, "count", "OddsAPI")

                Else
                    Dim error = Await response.Content.ReadAsStringAsync()
                    LogMessage($"API Error ({response.StatusCode}): {error}", True)
                    UpdateStatus($"API request failed: {response.StatusCode}")

                    ' Log error metrics
                    DBWriter.LogPerformanceMetric("api_errors", "odds_api_failure", 1, "count", "OddsAPI")
                End If
            End Using

        Catch ex As Exception
            LogMessage($"Exception during ingestion: {ex.Message}", True)
            UpdateStatus($"Error: {ex.Message}")
            DBWriter.LogPerformanceMetric("api_errors", "exception", 1, "count", "OddsAPI")

        Finally
            isIngesting = False
            btnIngestSport.Enabled = True
            btnIngestAll.Enabled = True
            progressBar.Style = ProgressBarStyle.Continuous
            progressBar.Value = 0
        End Try
    End Function

    Private Async Function IngestAllSportsData() As Task
        isIngesting = True
        btnIngestSport.Enabled = False
        btnIngestAll.Enabled = False

        Try
            Dim totalSports = cmbSports.Items.Count
            Dim totalMarkets = cmbMarkets.Items.Count
            Dim totalOperations = totalSports * totalMarkets
            Dim currentOperation = 0

            progressBar.Style = ProgressBarStyle.Continuous
            progressBar.Maximum = totalOperations
            progressBar.Value = 0

            LogMessage($"Starting full ingestion: {totalSports} sports × {totalMarkets} markets = {totalOperations} operations", False)

            For Each sport As String In cmbSports.Items
                For Each market As String In cmbMarkets.Items
                    currentOperation += 1

                    UpdateStatus($"Ingesting {sport} {market} ({currentOperation}/{totalOperations})...")
                    LogMessage($"Processing {sport} - {market} ({currentOperation}/{totalOperations})", False)

                    Try
                        Await IngestSingleSportMarket(sport, market)

                        ' Small delay to respect API rate limits
                        Await Task.Delay(2000)

                    Catch ex As Exception
                        LogMessage($"Failed to ingest {sport} {market}: {ex.Message}", True)
                    End Try

                    progressBar.Value = currentOperation
                Next
            Next

            ' Refresh display with all data
            LoadOddsToGrid("", "")

            UpdateStatus($"Full ingestion completed: {totalOperations} operations")
            LogMessage($"Full ingestion completed successfully", False)

        Catch ex As Exception
            LogMessage($"Exception during full ingestion: {ex.Message}", True)
            UpdateStatus($"Full ingestion error: {ex.Message}")

        Finally
            isIngesting = False
            btnIngestSport.Enabled = True
            btnIngestAll.Enabled = True
            progressBar.Value = 0
        End Try
    End Function

    Private Async Function IngestSingleSportMarket(sport As String, market As String) As Task
        Dim apiKey = config("oddsapi")("key").ToString()
        Dim baseUrl = config("oddsapi")("base_url").ToString()
        Dim regions = config("oddsapi")("regions").ToString()
        Dim oddsFormat = config("oddsapi")("odds_format").ToString()
        Dim dateFormat = config("oddsapi")("date_format").ToString()

        Dim url = $"{baseUrl}/sports/{sport}/odds/?apiKey={apiKey}&regions={regions}&markets={market}&oddsFormat={oddsFormat}&dateFormat={dateFormat}"

        Using response = Await httpClient.GetAsync(url)
            If response.IsSuccessStatusCode Then
                Dim jsonContent = Await response.Content.ReadAsStringAsync()
                Dim oddsData = JArray.Parse(jsonContent)
                Await ProcessOddsData(oddsData, sport)
            Else
                Throw New Exception($"API request failed: {response.StatusCode}")
            End If
        End Using
    End Function

    Private Async Function ProcessOddsData(oddsData As JArray, sport As String) As Task(Of Integer)
        Return Await Task.Run(Function()
            Dim processedCount = 0
            Dim timestamp = DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss")

            For Each gameData In oddsData
                Try
                    ' Extract event information
                    Dim eventId = gameData("id")?.ToString()
                    Dim homeTeam = gameData("home_team")?.ToString()
                    Dim awayTeam = gameData("away_team")?.ToString()
                    Dim commenceTime = gameData("commence_time")?.ToString()

                    If String.IsNullOrEmpty(eventId) Then Continue For

                    ' Insert/update event
                    Dim league = ExtractLeagueFromSport(sport)
                    DBWriter.UpsertEvent(eventId, sport.ToUpper(), league, commenceTime, homeTeam, awayTeam)

                    ' Process bookmaker odds
                    Dim bookmakers = gameData("bookmakers")
                    If bookmakers IsNot Nothing Then
                        For Each bookmaker In bookmakers
                            Dim bookName = bookmaker("title")?.ToString()
                            If String.IsNullOrEmpty(bookName) Then Continue For

                            Dim markets = bookmaker("markets")
                            If markets IsNot Nothing Then
                                For Each market In markets
                                    Dim marketKey = market("key")?.ToString()

                                    Dim outcomes = market("outcomes")
                                    If outcomes IsNot Nothing Then
                                        For Each outcome in outcomes
                                            Dim selection = outcome("name")?.ToString()
                                            Dim price = outcome("price")
                                            Dim point = outcome("point") ' For spreads/totals

                                            If selection IsNot Nothing AndAlso price IsNot Nothing Then
                                                Dim americanOdds = ConvertToAmericanOdds(price)
                                                Dim lineValue As Double? = If(point IsNot Nothing, CDbl(point), Nothing)

                                                DBWriter.LogLine(timestamp, eventId, sport.ToUpper(), league, marketKey, selection, bookName, americanOdds, lineValue, "api")
                                            End If
                                        Next
                                    End If
                                Next
                            End If
                        Next
                    End If

                    processedCount += 1

                Catch ex As Exception
                    LogMessage($"Error processing event data: {ex.Message}", True)
                End Try
            Next

            Return processedCount
        End Function)
    End Function

    Private Function ConvertToAmericanOdds(price As JToken) As Integer
        Try
            Dim decimalOdds = CDbl(price)

            If decimalOdds >= 2.0 Then
                ' Positive American odds
                Return CInt((decimalOdds - 1) * 100)
            Else
                ' Negative American odds
                Return CInt(-100 / (decimalOdds - 1))
            End If

        Catch ex As Exception
            Return 100 ' Default fallback
        End Try
    End Function

    Private Function ExtractLeagueFromSport(sport As String) As String
        ' Extract league identifier from sport string
        Select Case sport.ToLower()
            Case "baseball_mlb" : Return "MLB"
            Case "americanfootball_nfl" : Return "NFL"
            Case "basketball_nba" : Return "NBA"
            Case "icehockey_nhl" : Return "NHL"
            Case "soccer_epl" : Return "EPL"
            Case Else : Return sport.ToUpper()
        End Select
    End Function

    Private Sub LoadOddsToGrid(Optional filterSport As String = "", Optional filterMarket As String = "")
        Try
            Using conn As New System.Data.SQLite.SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()

                Dim sql = "SELECT e.event_id, e.home_team, e.away_team, e.start_ts, l.market, l.selection, l.book, l.odds, l.line_value, l.ts as last_updated FROM events e JOIN lines l ON e.event_id = l.event_id WHERE l.ts >= datetime('now', '-2 hours')"

                If Not String.IsNullOrEmpty(filterSport) Then
                    sql &= $" AND l.sport = '{filterSport.ToUpper()}'"
                End If

                If Not String.IsNullOrEmpty(filterMarket) Then
                    sql &= $" AND l.market = '{filterMarket}'"
                End If

                sql &= " ORDER BY e.start_ts, e.event_id, l.market, l.book"

                Using adapter As New System.Data.SQLite.SQLiteDataAdapter(sql, conn)
                    Dim dataTable As New DataTable()
                    adapter.Fill(dataTable)

                    dgvOdds.DataSource = dataTable

                    ' Format columns
                    If dgvOdds.Columns.Contains("odds") Then
                        dgvOdds.Columns("odds").DefaultCellStyle.Format = "+#;-#;0"
                    End If

                    If dgvOdds.Columns.Contains("line_value") Then
                        dgvOdds.Columns("line_value").DefaultCellStyle.Format = "F1"
                    End If
                End Using
            End Using

        Catch ex As Exception
            LogMessage($"Error loading odds to grid: {ex.Message}", True)
        End Try
    End Sub

    Private Sub UpdateStatus(message As String)
        If InvokeRequired Then
            Invoke(Sub() lblStatus.Text = message)
        Else
            lblStatus.Text = message
        End If
    End Sub

    Private Sub LogMessage(message As String, isError As Boolean)
        Dim timestamp = DateTime.Now.ToString("HH:mm:ss")
        Dim prefix = If(isError, "[ERROR]", "[INFO]")
        Dim logEntry = $"{timestamp} {prefix} {message}{Environment.NewLine}"

        If InvokeRequired Then
            Invoke(Sub()
                txtLog.AppendText(logEntry)
                txtLog.SelectionStart = txtLog.Text.Length
                txtLog.ScrollToCaret()
            End Sub)
        Else
            txtLog.AppendText(logEntry)
            txtLog.SelectionStart = txtLog.Text.Length
            txtLog.ScrollToCaret()
        End If

        ' Also log to console
        If isError Then
            Console.WriteLine($"OddsAPI Error: {message}")
        Else
            Console.WriteLine($"OddsAPI: {message}")
        End If
    End Sub

    Protected Overrides Sub Dispose(disposing As Boolean)
        If disposing Then
            httpClient?.Dispose()
        End If
        MyBase.Dispose(disposing)
    End Sub

End Class
