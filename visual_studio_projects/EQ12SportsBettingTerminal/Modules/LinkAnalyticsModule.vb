Imports System.Data
Imports System.Data.SQLite
Imports System.Drawing
Imports System.IO
Imports System.Net.Http
Imports System.Text
Imports System.Windows.Forms
Imports Newtonsoft.Json.Linq
Imports OfficeOpenXml

''' <summary>
''' Link Analytics Module - Digital Link Management & Analytics Mastery
''' Provides comprehensive Bitly link analytics, campaign tracking, and performance insights
''' Features: Click analytics, geographic breakdown, referrer tracking, branded domain support
''' </summary>
Public Class LinkAnalyticsModule
    Inherits UserControl

    ' UI Components
    Private topPanel As New Panel With {.Height = 120, .Dock = DockStyle.Top}
    Private inputPanel As New Panel With {.Height = 40, .Dock = DockStyle.Top, .Padding = New Padding(10, 5, 10, 5)}
    Private buttonPanel As New Panel With {.Height = 40, .Dock = DockStyle.Top, .Padding = New Padding(10, 5, 10, 5)}
    Private statsPanel As New Panel With {.Height = 40, .Dock = DockStyle.Top, .Padding = New Padding(10, 5, 10, 5)}

    Private urlTextBox As New TextBox With {.Width = 400, .Left = 100, .Top = 8, .PlaceholderText = "Enter Bitly link (bit.ly/xyz or custom domain)"}
    Private analyzeBtn As New Button With {.Text = "📊 Analyze Link", .Width = 120, .Left = 510, .Top = 6}
    Private exportBtn As New Button With {.Text = "📤 Export CSV", .Width = 100, .Left = 640, .Top = 6, .Enabled = False}
    Private refreshBtn As New Button With {.Text = "🔄 Refresh", .Width = 80, .Left = 750, .Top = 6}

    Private statsLabel As New Label With {.Left = 10, .Top = 8, .AutoSize = True, .ForeColor = Color.Blue, .Font = New Font("Segoe UI", 9, FontStyle.Bold)}
    Private lastUpdateLabel As New Label With {.Left = 400, .Top = 8, .AutoSize = True, .ForeColor = Color.Gray}

    Private grid As New DataGridView With {.Dock = DockStyle.Fill}

    ' Data storage
    Private currentAnalytics As JObject
    Private linkHistory As New DataTable()

    Public Sub New()
        InitializeComponents()
        SetupGrid()
        LoadLinkHistory()
    End Sub

    ''' <summary>
    ''' Initialize UI components and layout
    ''' </summary>
    Private Sub InitializeComponents()
        ' Setup panels
        inputPanel.Controls.AddRange({New Label With {.Text = "Bitly Link:", .Left = 10, .Top = 12, .Width = 80}, urlTextBox})
        buttonPanel.Controls.AddRange({analyzeBtn, exportBtn, refreshBtn})
        statsPanel.Controls.AddRange({statsLabel, lastUpdateLabel})

        topPanel.Controls.AddRange({inputPanel, buttonPanel, statsPanel})

        ' Setup main layout
        Me.Controls.AddRange({grid, topPanel})

        ' Wire events
        AddHandler analyzeBtn.Click, AddressOf AnalyzeLink
        AddHandler exportBtn.Click, AddressOf ExportAnalytics
        AddHandler refreshBtn.Click, AddressOf RefreshData
        AddHandler urlTextBox.KeyPress, AddressOf OnUrlKeyPress

        ' Initial state
        statsLabel.Text = "💡 Master Link Analytics: Track clicks, geography, referrers, and campaign performance"
    End Sub

    ''' <summary>
    ''' Setup analytics data grid
    ''' </summary>
    Private Sub SetupGrid()
        With grid
            .ReadOnly = True
            .AllowUserToAddRows = False
            .AllowUserToDeleteRows = False
            .SelectionMode = DataGridViewSelectionMode.FullRowSelect
            .AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill
            .RowHeadersVisible = False
        End With
    End Sub

    ''' <summary>
    ''' Handle Enter key press in URL textbox
    ''' </summary>
    Private Sub OnUrlKeyPress(sender As Object, e As KeyPressEventArgs)
        If e.KeyChar = ChrW(Keys.Enter) Then
            AnalyzeLink(sender, EventArgs.Empty)
            e.Handled = True
        End If
    End Sub

    ''' <summary>
    ''' Analyze Bitly link and fetch analytics
    ''' </summary>
    Private Sub AnalyzeLink(sender As Object, e As EventArgs)
        Try
            Dim url = urlTextBox.Text.Trim()
            If String.IsNullOrEmpty(url) Then
                MessageBox.Show("Please enter a Bitly link to analyze.", "Input Required", MessageBoxButtons.OK, MessageBoxIcon.Information)
                Return
            End If

            ' Normalize URL (remove http/https, extract link ID)
            Dim linkId = ExtractBitlyId(url)
            If String.IsNullOrEmpty(linkId) Then
                MessageBox.Show("Please enter a valid Bitly link (e.g., bit.ly/abc123 or yourdomain.ly/xyz).", "Invalid Link", MessageBoxButtons.OK, MessageBoxIcon.Warning)
                Return
            End If

            analyzeBtn.Text = "⏳ Analyzing..."
            analyzeBtn.Enabled = False

            ' Fetch analytics from Bitly API
            FetchBitlyAnalytics(linkId)

        Catch ex As Exception
            MessageBox.Show($"Analysis failed: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
        Finally
            analyzeBtn.Text = "📊 Analyze Link"
            analyzeBtn.Enabled = True
        End Try
    End Sub

    ''' <summary>
    ''' Extract Bitly link ID from various URL formats
    ''' </summary>
    Private Function ExtractBitlyId(url As String) As String
        Try
            ' Remove protocol
            url = url.Replace("https://", "").Replace("http://", "")

            ' Handle various formats: bit.ly/xyz, custom.domain/xyz
            If url.Contains("/") Then
                Return url.Split("/"c).Last()
            End If

            Return ""
        Catch
            Return ""
        End Try
    End Function

    ''' <summary>
    ''' Fetch analytics from Bitly API
    ''' </summary>
    Private Sub FetchBitlyAnalytics(linkId As String)
        Try
            ' Load Bitly token from config
            Dim config = LoadConfig()
            If config("bitly")?("token") Is Nothing Then
                MessageBox.Show("Bitly API token not configured. Please set your token in config.json.", "Configuration Missing", MessageBoxButtons.OK, MessageBoxIcon.Warning)
                Return
            End If

            Dim token = config("bitly")("token").ToString()
            If token = "YOUR_BITLY_GENERIC_ACCESS_TOKEN" Then
                MessageBox.Show("Please configure your actual Bitly API token in config.json.", "Token Required", MessageBoxButtons.OK, MessageBoxIcon.Warning)
                Return
            End If

            ' Fetch link information and analytics
            Using client As New HttpClient()
                client.DefaultRequestHeaders.Add("Authorization", "Bearer " & token)

                ' Get link details
                Dim linkUrl = $"https://api-ssl.bitly.com/v4/bitlinks/bit.ly/{linkId}"
                Dim linkResponse = client.GetAsync(linkUrl).Result

                If Not linkResponse.IsSuccessStatusCode Then
                    MessageBox.Show($"Failed to fetch link data: {linkResponse.StatusCode}", "API Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
                    Return
                End If

                Dim linkData = JObject.Parse(linkResponse.Content.ReadAsStringAsync().Result)

                ' Get click analytics
                Dim clicksUrl = $"https://api-ssl.bitly.com/v4/bitlinks/bit.ly/{linkId}/clicks"
                Dim clicksResponse = client.GetAsync(clicksUrl).Result

                If clicksResponse.IsSuccessStatusCode Then
                    Dim clicksData = JObject.Parse(clicksResponse.Content.ReadAsStringAsync().Result)
                    DisplayAnalytics(linkId, linkData, clicksData)

                    ' Log to database
                    LogAnalyticsData(linkId, clicksData)
                Else
                    DisplayBasicInfo(linkId, linkData)
                End If
            End Using

        Catch ex As Exception
            MessageBox.Show($"Analytics fetch failed: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    ''' <summary>
    ''' Display comprehensive analytics in grid
    ''' </summary>
    Private Sub DisplayAnalytics(linkId As String, linkData As JObject, clicksData As JObject)
        Try
            Dim dt As New DataTable()
            dt.Columns.AddRange({
                New DataColumn("Metric", GetType(String)),
                New DataColumn("Value", GetType(String)),
                New DataColumn("Details", GetType(String))
            })

            ' Basic link info
            dt.Rows.Add("Short Link", $"bit.ly/{linkId}", linkData("link")?.ToString())
            dt.Rows.Add("Long URL", linkData("long_url")?.ToString(), "Original destination")
            dt.Rows.Add("Created", Convert.ToDateTime(linkData("created_at")?.ToString()).ToString("yyyy-MM-dd HH:mm"), "Link creation date")

            ' Click metrics
            Dim totalClicks = clicksData("link_clicks")?.ToObject(Of Integer)() ?? 0
            dt.Rows.Add("Total Clicks", totalClicks.ToString("N0"), "All-time clicks")

            ' Process country data if available
            If clicksData("countries") IsNot Nothing Then
                Dim countries = clicksData("countries").Take(5)
                For Each country In countries
                    dt.Rows.Add($"Country: {country("country")}", country("clicks").ToString(), "Geographic breakdown")
                Next
            End If

            ' Process referrer data if available
            If clicksData("referrers") IsNot Nothing Then
                Dim referrers = clicksData("referrers").Take(5)
                For Each referrer In referrers
                    dt.Rows.Add($"Referrer: {referrer("referrer")}", referrer("clicks").ToString(), "Traffic source")
                Next
            End If

            grid.DataSource = dt

            ' Update stats
            statsLabel.Text = $"📊 Analytics: {totalClicks:N0} total clicks • Link: bit.ly/{linkId}"
            lastUpdateLabel.Text = $"Updated: {DateTime.Now:HH:mm:ss}"

            currentAnalytics = New JObject From {
                {"linkId", linkId},
                {"linkData", linkData},
                {"clicksData", clicksData},
                {"timestamp", DateTime.Now}
            }

            exportBtn.Enabled = True

        Catch ex As Exception
            MessageBox.Show($"Display error: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    ''' <summary>
    ''' Display basic link information when analytics unavailable
    ''' </summary>
    Private Sub DisplayBasicInfo(linkId As String, linkData As JObject)
        Dim dt As New DataTable()
        dt.Columns.AddRange({
            New DataColumn("Property", GetType(String)),
            New DataColumn("Value", GetType(String))
        })

        dt.Rows.Add("Short Link", $"bit.ly/{linkId}")
        dt.Rows.Add("Long URL", linkData("long_url")?.ToString())
        dt.Rows.Add("Created", linkData("created_at")?.ToString())
        dt.Rows.Add("Status", "Analytics not available (may require premium Bitly account)")

        grid.DataSource = dt
        statsLabel.Text = $"ℹ️ Basic Info: bit.ly/{linkId} (analytics limited)"
    End Sub

    ''' <summary>
    ''' Log analytics data to database for tracking
    ''' </summary>
    Private Sub LogAnalyticsData(linkId As String, clicksData As JObject)
        Try
            Dim totalClicks = clicksData("link_clicks")?.ToObject(Of Integer)() ?? 0

            ' Log overall stats
            DBWriter.LogBitlyStats(linkId, totalClicks, "aggregate", "bitly_api")

            ' Log country breakdown
            If clicksData("countries") IsNot Nothing Then
                For Each country In clicksData("countries")
                    DBWriter.LogBitlyStats(linkId, country("clicks").ToObject(Of Integer)(), country("country").ToString(), "geographic")
                Next
            End If

            ' Log referrer breakdown
            If clicksData("referrers") IsNot Nothing Then
                For Each referrer In clicksData("referrers")
                    DBWriter.LogBitlyStats(linkId, referrer("clicks").ToObject(Of Integer)(), "referrer", referrer("referrer").ToString())
                Next
            End If

        Catch ex As Exception
            ' Log error but don't disrupt user experience
            Console.WriteLine($"Analytics logging failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Export analytics to CSV/Excel
    ''' </summary>
    Private Sub ExportAnalytics(sender As Object, e As EventArgs)
        Try
            If currentAnalytics Is Nothing Then
                MessageBox.Show("No analytics data to export. Please analyze a link first.", "No Data", MessageBoxButtons.OK, MessageBoxIcon.Information)
                Return
            End If

            Dim dialog As New SaveFileDialog With {
                .Filter = "Excel Files (*.xlsx)|*.xlsx|CSV Files (*.csv)|*.csv",
                .FileName = $"bitly_analytics_{currentAnalytics("linkId")}_{DateTime.Now:yyyyMMdd_HHmm}"
            }

            If dialog.ShowDialog() = DialogResult.OK Then
                If dialog.FilterIndex = 1 Then
                    ExportToExcel(dialog.FileName)
                Else
                    ExportToCSV(dialog.FileName)
                End If

                MessageBox.Show($"Analytics exported successfully to: {dialog.FileName}", "Export Complete", MessageBoxButtons.OK, MessageBoxIcon.Information)
            End If

        Catch ex As Exception
            MessageBox.Show($"Export failed: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    ''' <summary>
    ''' Export to Excel format
    ''' </summary>
    Private Sub ExportToExcel(filePath As String)
        ExcelPackage.LicenseContext = LicenseContext.NonCommercial

        Using package As New ExcelPackage()
            Dim worksheet = package.Workbook.Worksheets.Add("Link Analytics")

            ' Headers
            worksheet.Cells("A1").Value = "Metric"
            worksheet.Cells("B1").Value = "Value"
            worksheet.Cells("C1").Value = "Details"

            ' Data
            Dim dt = DirectCast(grid.DataSource, DataTable)
            For i = 0 To dt.Rows.Count - 1
                worksheet.Cells(i + 2, 1).Value = dt.Rows(i)(0).ToString()
                worksheet.Cells(i + 2, 2).Value = dt.Rows(i)(1).ToString()
                worksheet.Cells(i + 2, 3).Value = If(dt.Columns.Count > 2, dt.Rows(i)(2).ToString(), "")
            Next

            ' Style
            worksheet.Cells("A1:C1").Style.Font.Bold = True
            worksheet.Cells.AutoFitColumns()

            package.SaveAs(New FileInfo(filePath))
        End Using
    End Sub

    ''' <summary>
    ''' Export to CSV format
    ''' </summary>
    Private Sub ExportToCSV(filePath As String)
        Dim dt = DirectCast(grid.DataSource, DataTable)
        Using writer As New StreamWriter(filePath)
            ' Headers
            writer.WriteLine("Metric,Value,Details")

            ' Data
            For Each row As DataRow In dt.Rows
                Dim values = row.ItemArray.Select(Function(field) $"""{field}""")
                writer.WriteLine(String.Join(",", values))
            Next
        End Using
    End Sub

    ''' <summary>
    ''' Load link analytics history from database
    ''' </summary>
    Private Sub LoadLinkHistory()
        Try
            linkHistory.Clear()
            linkHistory.Columns.Clear()
            linkHistory.Columns.AddRange({
                New DataColumn("Date", GetType(String)),
                New DataColumn("Link ID", GetType(String)),
                New DataColumn("Clicks", GetType(Integer)),
                New DataColumn("Country", GetType(String)),
                New DataColumn("Referrer", GetType(String))
            })

            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()
                Using cmd As New SQLiteCommand("
                    SELECT ts, link_id, clicks, country, referrer
                    FROM bitly_stats
                    ORDER BY ts DESC
                    LIMIT 100", conn)
                    Using rdr = cmd.ExecuteReader()
                        While rdr.Read()
                            linkHistory.Rows.Add(
                                Convert.ToDateTime(rdr("ts")).ToString("yyyy-MM-dd HH:mm"),
                                rdr("link_id").ToString(),
                                rdr("clicks"),
                                rdr("country").ToString(),
                                rdr("referrer").ToString()
                            )
                        End While
                    End Using
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"Failed to load link history: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Refresh all data
    ''' </summary>
    Private Sub RefreshData(sender As Object, e As EventArgs)
        LoadLinkHistory()
        statsLabel.Text = "🔄 Data refreshed • Master Link Analytics: Track clicks, geography, referrers, and campaign performance"
    End Sub

    ''' <summary>
    ''' Load configuration from JSON
    ''' </summary>
    Private Function LoadConfig() As JObject
        Try
            If File.Exists("Config\config.json") Then
                Return JObject.Parse(File.ReadAllText("Config\config.json"))
            End If
        Catch
        End Try
        Return New JObject()
    End Function
End Class
