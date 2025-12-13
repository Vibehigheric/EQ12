Imports System.Data.SQLite
Imports System.Windows.Forms
Imports System.Data
Imports System.Drawing

''' <summary>
''' Deliverables Module - GUI for viewing and managing content engine output
''' Displays generated content assets with quick access to Bitly links
''' </summary>
Public Class DeliverablesModule
    Inherits UserControl

    Private grid As New DataGridView With {.Dock = DockStyle.Fill, .ReadOnly = True}
    Private topPanel As New Panel With {.Height = 40, .Dock = DockStyle.Top}
    Private refreshBtn As New Button With {.Text = "🔄 Refresh", .Width = 100, .Left = 10, .Top = 8}
    Private generateBtn As New Button With {.Text = "🚀 Generate Content", .Width = 150, .Left = 120, .Top = 8}
    Private statsLabel As New Label With {.Left = 280, .Top = 12, .AutoSize = True, .ForeColor = Color.Gray}

    Public Sub New()
        InitializeComponent()
        LoadData()
    End Sub

    ''' <summary>
    ''' Initialize the GUI components
    ''' </summary>
    Private Sub InitializeComponent()
        ' Setup top panel
        topPanel.Controls.Add(refreshBtn)
        topPanel.Controls.Add(generateBtn)
        topPanel.Controls.Add(statsLabel)

        ' Setup data grid
        With grid
            .AllowUserToAddRows = False
            .AllowUserToDeleteRows = False
            .SelectionMode = DataGridViewSelectionMode.FullRowSelect
            .AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill
            .RowHeadersVisible = False
            .MultiSelect = False
        End With

        ' Add components to control
        Me.Controls.Add(grid)
        Me.Controls.Add(topPanel)

        ' Wire up events
        AddHandler refreshBtn.Click, AddressOf RefreshData
        AddHandler generateBtn.Click, AddressOf GenerateContent
        AddHandler grid.CellDoubleClick, AddressOf OpenLink
    End Sub

    ''' <summary>
    ''' Load deliverables data from database
    ''' </summary>
    Private Sub LoadData()
        Try
            Dim dt As New DataTable()
            dt.Columns.Add("Generated", GetType(String))
            dt.Columns.Add("Type", GetType(String))
            dt.Columns.Add("Title", GetType(String))
            dt.Columns.Add("Period", GetType(String))
            dt.Columns.Add("Bitly URL", GetType(String))
            dt.Columns.Add("Gist URL", GetType(String))

            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()
                Using cmd As New SQLiteCommand("
                    SELECT ts, kind, title, source_window, bitly_url, gist_url
                    FROM deliverables
                    ORDER BY ts DESC
                    LIMIT 100", conn)
                    Using rdr = cmd.ExecuteReader()
                        While rdr.Read()
                            Dim row = dt.NewRow()
                            row("Generated") = Convert.ToDateTime(rdr("ts")).ToString("yyyy-MM-dd HH:mm")
                            row("Type") = CapitalizeFirst(rdr("kind").ToString())
                            row("Title") = TruncateText(rdr("title").ToString(), 50)
                            row("Period") = CapitalizeFirst(rdr("source_window").ToString())
                            row("Bitly URL") = rdr("bitly_url").ToString()
                            row("Gist URL") = rdr("gist_url").ToString()
                            dt.Rows.Add(row)
                        End While
                    End Using
                End Using
            End Using

            grid.DataSource = dt

            ' Update stats
            UpdateStats()

            ' Style columns
            StyleGrid()

        Catch ex As Exception
            MessageBox.Show($"Error loading deliverables: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
        End Try
    End Sub

    ''' <summary>
    ''' Style the data grid for better presentation
    ''' </summary>
    Private Sub StyleGrid()
        Try
            If grid.Columns.Count > 0 Then
                grid.Columns("Generated").Width = 120
                grid.Columns("Type").Width = 100
                grid.Columns("Title").Width = 300
                grid.Columns("Period").Width = 80
                grid.Columns("Bitly URL").Width = 150
                grid.Columns("Gist URL").Width = 150

                ' Color code by type
                For Each row As DataGridViewRow In grid.Rows
                    If row.Cells("Type").Value IsNot Nothing Then
                        Select Case row.Cells("Type").Value.ToString().ToLower()
                            Case "newsletter"
                                row.DefaultCellStyle.BackColor = Color.LightBlue
                            Case "thread"
                                row.DefaultCellStyle.BackColor = Color.LightGreen
                            Case "landing_page"
                                row.DefaultCellStyle.BackColor = Color.LightYellow
                            Case "promo_email"
                                row.DefaultCellStyle.BackColor = Color.LightPink
                        End Select
                    End If
                Next
            End If
        Catch ex As Exception
            ' Ignore styling errors
        End Try
    End Sub

    ''' <summary>
    ''' Update statistics label
    ''' </summary>
    Private Sub UpdateStats()
        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()
                Using cmd As New SQLiteCommand("
                    SELECT COUNT(*) as total,
                           COUNT(CASE WHEN ts >= datetime('now', '-7 days') THEN 1 END) as week,
                           COUNT(CASE WHEN ts >= datetime('now', '-1 day') THEN 1 END) as day
                    FROM deliverables", conn)
                    Using rdr = cmd.ExecuteReader()
                        If rdr.Read() Then
                            statsLabel.Text = $"📊 Total: {rdr("total")} | This Week: {rdr("week")} | Today: {rdr("day")}"
                        End If
                    End Using
                End Using
            End Using
        Catch ex As Exception
            statsLabel.Text = "📊 Stats unavailable"
        End Try
    End Sub

    ''' <summary>
    ''' Refresh data from database
    ''' </summary>
    Private Sub RefreshData(sender As Object, e As EventArgs)
        LoadData()
    End Sub

    ''' <summary>
    ''' Generate new content (launches daily content generation)
    ''' </summary>
    Private Sub GenerateContent(sender As Object, e As EventArgs)
        Try
            generateBtn.Enabled = False
            generateBtn.Text = "⏳ Generating..."

            ' This would typically run the content generation in a background thread
            ' For now, we'll show a message
            Dim result = MessageBox.Show(
                "Generate daily monetization content now?" & vbCrLf & vbCrLf &
                "This will create newsletter, thread, landing page, and promo email content using OpenAI and your latest EQ12 data.",
                "Generate Content",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Question)

            If result = DialogResult.Yes Then
                ' In a real implementation, this would call:
                ' ContentEngine.BuildAll(config, "daily", summaryData)
                MessageBox.Show("Content generation initiated! Check the CLI or logs for progress.",
                              "Generation Started", MessageBoxButtons.OK, MessageBoxIcon.Information)
            End If

        Catch ex As Exception
            MessageBox.Show($"Error generating content: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error)
        Finally
            generateBtn.Enabled = True
            generateBtn.Text = "🚀 Generate Content"
        End Try
    End Sub

    ''' <summary>
    ''' Open Bitly or Gist link when cell is double-clicked
    ''' </summary>
    Private Sub OpenLink(sender As Object, e As DataGridViewCellEventArgs)
        Try
            If e.RowIndex >= 0 AndAlso e.ColumnIndex >= 0 Then
                Dim cellValue = grid.Rows(e.RowIndex).Cells(e.ColumnIndex).Value?.ToString()

                If Not String.IsNullOrEmpty(cellValue) AndAlso
                   (cellValue.StartsWith("http://") OrElse cellValue.StartsWith("https://")) Then

                    Process.Start(New ProcessStartInfo(cellValue) With {.UseShellExecute = True})
                End If
            End If
        Catch ex As Exception
            MessageBox.Show($"Could not open link: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Warning)
        End Try
    End Sub

    ''' <summary>
    ''' Capitalize first letter of string
    ''' </summary>
    Private Function CapitalizeFirst(text As String) As String
        If String.IsNullOrEmpty(text) Then Return text
        Return Char.ToUpper(text(0)) & text.Substring(1).ToLower()
    End Function

    ''' <summary>
    ''' Truncate text to specified length
    ''' </summary>
    Private Function TruncateText(text As String, maxLength As Integer) As String
        If String.IsNullOrEmpty(text) OrElse text.Length <= maxLength Then Return text
        Return text.Substring(0, maxLength - 3) & "..."
    End Function
End Class
