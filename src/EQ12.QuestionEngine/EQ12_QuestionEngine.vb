Imports System
Imports System.Collections.Generic
Imports System.Data.SQLite
Imports System.Diagnostics
Imports System.Linq
Imports System.Text
Imports System.Text.Json
Imports System.Threading.Tasks
Imports System.Windows.Forms

' EQ12 Question Engine UI Module
' Purpose: Load 100-question schema, execute auto-answers, display results in VB.NET UI
' Version: 1.0 | Author: EQ12 System | Date: 2025-12-04

Public Class EQ12QuestionEngine
    Inherits Form

    ' UI Controls
    Private WithEvents dgvQuestions As DataGridView
    Private WithEvents dgvAnswers As DataGridView
    Private WithEvents btnRunDiagnostic As Button
    Private WithEvents btnExportReport As Button
    Private WithEvents cmbCategory As ComboBox
    Private WithEvents lblStatus As Label
    Private WithEvents txtSummary As TextBox
    Private WithEvents prgProgress As ProgressBar

    ' Database connection
    Private _dbPath As String = "logs\eq12_question_engine.db"
    Private _conn As SQLiteConnection

    ' Schema
    Private _questionSchema As JsonDocument

    Public Sub New()
        MyBase.New()
        InitializeComponent()
        InitializeDatabase()
        LoadQuestionSchema()
    End Sub

    Private Sub InitializeComponent()
        ' Main form
        Me.Text = "EQ12 100-Question Self-Diagnostic Engine"
        Me.Width = 1200
        Me.Height = 800
        Me.StartPosition = FormStartPosition.CenterScreen

        ' Category filter
        Dim lblCategory As New Label
        lblCategory.Text = "Category:"
        lblCategory.Location = New Point(10, 10)
        lblCategory.Width = 80

        cmbCategory = New ComboBox
        cmbCategory.Location = New Point(100, 10)
        cmbCategory.Width = 300
        cmbCategory.Items.Add("All Categories")
        cmbCategory.Items.Add("File System + Code Scanning (1-15)")
        cmbCategory.Items.Add("GitHub + Copilot Automation (16-30)")
        cmbCategory.Items.Add("EQ12 Hardware + OS Optimization (31-45)")
        cmbCategory.Items.Add("AI/ML + Python Stack (46-60)")
        cmbCategory.Items.Add("Sports Betting Engine (61-75)")
        cmbCategory.Items.Add("Travel Bot + API System (76-85)")
        cmbCategory.Items.Add("Business + Funnel Automation (86-95)")
        cmbCategory.Items.Add("Raspberry Pi + Coral Cluster (96-100)")
        cmbCategory.SelectedIndex = 0
        Me.Controls.Add(lblCategory)
        Me.Controls.Add(cmbCategory)

        ' Run button
        btnRunDiagnostic = New Button
        btnRunDiagnostic.Text = "Run Diagnostic (All 100Q)"
        btnRunDiagnostic.Location = New Point(420, 10)
        btnRunDiagnostic.Width = 150
        Me.Controls.Add(btnRunDiagnostic)

        ' Export button
        btnExportReport = New Button
        btnExportReport.Text = "Export Report"
        btnExportReport.Location = New Point(580, 10)
        btnExportReport.Width = 120
        Me.Controls.Add(btnExportReport)

        ' Status label
        lblStatus = New Label
        lblStatus.Text = "Ready"
        lblStatus.Location = New Point(10, 40)
        lblStatus.Width = 500
        Me.Controls.Add(lblStatus)

        ' Progress bar
        prgProgress = New ProgressBar
        prgProgress.Location = New Point(10, 60)
        prgProgress.Width = 690
        prgProgress.Height = 20
        Me.Controls.Add(prgProgress)

        ' Questions grid
        dgvQuestions = New DataGridView
        dgvQuestions.Location = New Point(10, 90)
        dgvQuestions.Width = 690
        dgvQuestions.Height = 300
        dgvQuestions.AllowUserToAddRows = False
        dgvQuestions.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.AllCells
        dgvQuestions.Columns.Add("id", "Q#")
        dgvQuestions.Columns.Add("question", "Question")
        dgvQuestions.Columns.Add("criticality", "Priority")
        dgvQuestions.Columns.Add("answered", "Status")
        Me.Controls.Add(dgvQuestions)

        ' Answers grid
        dgvAnswers = New DataGridView
        dgvAnswers.Location = New Point(10, 400)
        dgvAnswers.Width = 690
        dgvAnswers.Height = 350
        dgvAnswers.AllowUserToAddRows = False
        dgvAnswers.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.AllCells
        dgvAnswers.Columns.Add("question_id", "Q#")
        dgvAnswers.Columns.Add("answer_summary", "Answer (Summary)")
        dgvAnswers.Columns.Add("answer_timestamp", "Timestamp")
        dgvAnswers.Columns.Add("execution_time_ms", "Runtime (ms)")
        Me.Controls.Add(dgvAnswers)

        ' Summary textbox
        Dim lblSummary As New Label
        lblSummary.Text = "Summary:"
        lblSummary.Location = New Point(710, 90)
        lblSummary.Width = 80
        Me.Controls.Add(lblSummary)

        txtSummary = New TextBox
        txtSummary.Location = New Point(710, 110)
        txtSummary.Width = 470
        txtSummary.Height = 640
        txtSummary.Multiline = True
        txtSummary.ReadOnly = True
        txtSummary.Font = New Font("Courier New", 9)
        Me.Controls.Add(txtSummary)
    End Sub

    Private Sub InitializeDatabase()
        Try
            _conn = New SQLiteConnection($"Data Source={_dbPath};Version=3;")
            _conn.Open()

            ' Create tables
            Dim cmd = _conn.CreateCommand
            cmd.CommandText = "
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY,
                    category TEXT,
                    question TEXT,
                    answer_type TEXT,
                    criticality TEXT,
                    automation_command TEXT
                );
                
                CREATE TABLE IF NOT EXISTS answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER,
                    answer TEXT,
                    answer_summary TEXT,
                    execution_time_ms INTEGER,
                    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(question_id) REFERENCES questions(id)
                );
                
                CREATE TABLE IF NOT EXISTS diagnostic_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_start_time TIMESTAMP,
                    run_end_time TIMESTAMP,
                    total_questions INTEGER,
                    answered_count INTEGER,
                    health_score FLOAT,
                    health_score_text TEXT
                );
            "
            cmd.ExecuteNonQuery()
        Catch ex As Exception
            MessageBox.Show($"Database initialization failed: {ex.Message}")
        End Try
    End Sub

    Private Sub LoadQuestionSchema()
        Try
            Dim schemaPath = "config\eq12_100q_schema.json"
            Dim json = System.IO.File.ReadAllText(schemaPath)
            _questionSchema = JsonDocument.Parse(json)

            ' Populate questions grid
            PopulateQuestionsGrid()
        Catch ex As Exception
            MessageBox.Show($"Failed to load schema: {ex.Message}")
        End Try
    End Sub

    Private Sub PopulateQuestionsGrid()
        dgvQuestions.Rows.Clear()

        Dim categories = _questionSchema.RootElement.GetProperty("categories").EnumerateObject()

        For Each category In categories
            Dim categoryData = category.Value
            Dim questions = categoryData.GetProperty("questions").EnumerateArray()

            For Each question In questions
                Dim qId = question.GetProperty("id").GetInt32()
                Dim qText = question.GetProperty("question").GetString()
                Dim criticality = question.GetProperty("criticality").GetString()

                dgvQuestions.Rows.Add(qId, qText, criticality, "Pending")
            Next
        Next
    End Sub

    Private Async Sub btnRunDiagnostic_Click(sender As Object, e As EventArgs) Handles btnRunDiagnostic.Click
        ' Run Python answerer script and capture results
        Dim runTask = RunPythonAnswerer()
        Await runTask
    End Sub

    Private Async Function RunPythonAnswerer() As Task
        Try
            btnRunDiagnostic.Enabled = False
            prgProgress.Value = 0
            lblStatus.Text = "Executing 100-question diagnostic..."
            dgvAnswers.Rows.Clear()
            txtSummary.Clear()

            ' Call Python script
            Dim psi = New ProcessStartInfo
            psi.FileName = "python"
            psi.Arguments = "scripts\eq12_100q_answerer.py --output json"
            psi.RedirectStandardOutput = True
            psi.UseShellExecute = False
            psi.CreateNoWindow = True

            Dim p = Process.Start(psi)
            Dim output = p.StandardOutput.ReadToEnd()
            p.WaitForExit()

            ' Parse results
            Dim results = JsonDocument.Parse(output)
            Dim answers = results.RootElement.GetProperty("answers").EnumerateArray()

            Dim answeredCount = 0
            Dim totalTime = 0

            For Each answer In answers
                Dim qId = answer.GetProperty("question_id").GetInt32()
                Dim answerText = answer.GetProperty("answer").GetString()
                Dim timestamp = answer.GetProperty("timestamp").GetString()
                Dim execTime = answer.GetProperty("execution_time_ms").GetInt32()

                dgvAnswers.Rows.Add(qId, Truncate(answerText, 80), timestamp, execTime)

                ' Update questions grid
                For Each row In dgvQuestions.Rows
                    If row.Cells("id").Value = qId Then
                        row.Cells("answered").Value = "✓ Answered"
                    End If
                Next

                answeredCount += 1
                totalTime += execTime
                prgProgress.Value = CInt((answeredCount / 100) * 100)
                Application.DoEvents()
            Next

            ' Calculate health score
            Dim healthScore = (answeredCount / 100) * 100

            ' Display summary
            txtSummary.AppendText($"EQ12 100-QUESTION DIAGNOSTIC" & vbCrLf)
            txtSummary.AppendText(New String("="c, 40) & vbCrLf)
            txtSummary.AppendText($"Questions Answered: {answeredCount}/100" & vbCrLf)
            txtSummary.AppendText($"Health Score: {healthScore:F1}/100" & vbCrLf)
            txtSummary.AppendText($"Total Runtime: {totalTime}ms" & vbCrLf)
            txtSummary.AppendText($"Avg per Question: {(totalTime / answeredCount):F0}ms" & vbCrLf)
            txtSummary.AppendText(vbCrLf)

            ' Store results
            StoreAnswersInDatabase(answeredCount, healthScore)

            lblStatus.Text = $"Complete! Health Score: {healthScore:F1}/100"
            prgProgress.Value = 100

        Catch ex As Exception
            MessageBox.Show($"Error running diagnostic: {ex.Message}")
        Finally
            btnRunDiagnostic.Enabled = True
        End Try
    End Function

    Private Sub StoreAnswersInDatabase(answeredCount As Integer, healthScore As Single)
        Try
            Dim cmd = _conn.CreateCommand
            cmd.CommandText = "
                INSERT INTO diagnostic_runs (run_start_time, run_end_time, total_questions, answered_count, health_score)
                VALUES (datetime('now'), datetime('now'), 100, @answered, @score)
            "
            cmd.Parameters.AddWithValue("@answered", answeredCount)
            cmd.Parameters.AddWithValue("@score", healthScore)
            cmd.ExecuteNonQuery()
        Catch ex As Exception
            Debug.WriteLine($"Database storage error: {ex.Message}")
        End Try
    End Sub

    Private Sub btnExportReport_Click(sender As Object, e As EventArgs) Handles btnExportReport.Click
        ' Export results to JSON/CSV/HTML
        Dim sfd = New SaveFileDialog
        sfd.Filter = "JSON|*.json|CSV|*.csv|HTML|*.html"
        sfd.DefaultExt = "json"

        If sfd.ShowDialog() = DialogResult.OK Then
            ExportResults(sfd.FileName, System.IO.Path.GetExtension(sfd.FileName))
        End If
    End Sub

    Private Sub ExportResults(filePath As String, fileType As String)
        Try
            Select Case fileType.ToLower()
                Case ".json"
                    ExportToJson(filePath)
                Case ".csv"
                    ExportToCsv(filePath)
                Case ".html"
                    ExportToHtml(filePath)
            End Select
            MessageBox.Show($"Report exported to: {filePath}")
        Catch ex As Exception
            MessageBox.Show($"Export failed: {ex.Message}")
        End Try
    End Sub

    Private Sub ExportToJson(filePath As String)
        ' Export all answers as JSON
        Dim json = New StringBuilder
        json.AppendLine("{")
        json.AppendLine($"  ""timestamp"": ""{DateTime.UtcNow:O}"",")
        json.AppendLine("  ""answers"": [")

        For i = 0 To dgvAnswers.Rows.Count - 1
            Dim row = dgvAnswers.Rows(i)
            json.AppendLine("    {")
            json.AppendLine($"      ""question_id"": {row.Cells(0).Value},")
            json.AppendLine($"      ""answer"": ""{EscapeJson(row.Cells(1).Value)}"",")
            json.AppendLine($"      ""timestamp"": ""{row.Cells(2).Value}"",")
            json.AppendLine($"      ""execution_time_ms"": {row.Cells(3).Value}")
            json.Append("    }")

            If i < dgvAnswers.Rows.Count - 1 Then
                json.AppendLine(",")
            Else
                json.AppendLine()
            End If
        Next

        json.AppendLine("  ]")
        json.AppendLine("}")

        System.IO.File.WriteAllText(filePath, json.ToString())
    End Sub

    Private Sub ExportToCsv(filePath As String)
        ' Export as CSV
        Dim csv = New StringBuilder
        csv.AppendLine("Q#,Answer,Timestamp,Runtime (ms)")

        For Each row In dgvAnswers.Rows
            csv.AppendLine($"{row.Cells(0).Value},""{row.Cells(1).Value}"",{row.Cells(2).Value},{row.Cells(3).Value}")
        Next

        System.IO.File.WriteAllText(filePath, csv.ToString())
    End Sub

    Private Sub ExportToHtml(filePath As String)
        ' Export as HTML
        Dim html = New StringBuilder
        html.AppendLine("<!DOCTYPE html>")
        html.AppendLine("<html>")
        html.AppendLine("<head>")
        html.AppendLine($"<title>EQ12 100-Question Diagnostic Report</title>")
        html.AppendLine("<style>")
        html.AppendLine("body { font-family: Arial, sans-serif; margin: 20px; }")
        html.AppendLine("table { border-collapse: collapse; width: 100%; }")
        html.AppendLine("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        html.AppendLine("th { background-color: #4CAF50; color: white; }")
        html.AppendLine("</style>")
        html.AppendLine("</head>")
        html.AppendLine("<body>")
        html.AppendLine($"<h1>EQ12 100-Question Diagnostic Report</h1>")
        html.AppendLine($"<p>Generated: {DateTime.Now:F}</p>")
        html.AppendLine(txtSummary.Text.Replace(vbCrLf, "<br>"))
        html.AppendLine("<table>")
        html.AppendLine("<tr><th>Q#</th><th>Answer</th><th>Timestamp</th><th>Runtime (ms)</th></tr>")

        For Each row In dgvAnswers.Rows
            html.AppendLine("<tr>")
            html.AppendLine($"<td>{row.Cells(0).Value}</td>")
            html.AppendLine($"<td>{row.Cells(1).Value}</td>")
            html.AppendLine($"<td>{row.Cells(2).Value}</td>")
            html.AppendLine($"<td>{row.Cells(3).Value}</td>")
            html.AppendLine("</tr>")
        Next

        html.AppendLine("</table>")
        html.AppendLine("</body>")
        html.AppendLine("</html>")

        System.IO.File.WriteAllText(filePath, html.ToString())
    End Sub

    Private Function Truncate(text As String, maxLength As Integer) As String
        If text.Length > maxLength Then
            Return text.Substring(0, maxLength) & "..."
        Else
            Return text
        End If
    End Function

    Private Function EscapeJson(text As Object) As String
        If text Is Nothing Then Return ""
        Return text.ToString().Replace("""", "\""").Replace(vbCrLf, "\n")
    End Function

    <STAThread()>
    Public Shared Sub Main()
        Application.EnableVisualStyles()
        Application.Run(New EQ12QuestionEngine())
    End Sub

End Class
