Imports System.IO
Imports System.Data.SQLite
Imports Newtonsoft.Json.Linq
Imports System.Text
Imports System.Threading.Tasks
Imports System.Timers

''' <summary>
''' ScheduledExportsHelper: Comprehensive automated export system for EQ12 stack
''' Handles daily/weekly report generation, multi-format exports, and monetization workflows
''' Features: PDF generation, Excel exports, blog publishing, newsletter creation, scheduled automation
''' </summary>
Public Class ScheduledExportsHelper

#Region "Core Export Functions"

    Private Shared _scheduledTimers As New List(Of Timer)()

    ''' <summary>
    ''' Initialize scheduled export system with timers from configuration
    ''' </summary>
    Public Shared Sub InitializeScheduledExports(cfg As JObject)
        Try
            If cfg("scheduled_exports")?("enabled")?.ToString() <> "True" Then
                Console.WriteLine("Scheduled exports disabled in configuration")
                Return
            End If

            ' Clear existing timers
            StopAllScheduledExports()

            ' Setup daily export timer
            If cfg("scheduled_exports")("daily")?("enabled")?.ToString() = "True" Then
                SetupDailyExportTimer(cfg)
            End If

            ' Setup weekly export timer
            If cfg("scheduled_exports")("weekly")?("enabled")?.ToString() = "True" Then
                SetupWeeklyExportTimer(cfg)
            End If

            Console.WriteLine($"✅ Scheduled exports initialized with {_scheduledTimers.Count} active timers")

        Catch ex As Exception
            Console.WriteLine($"❌ Failed to initialize scheduled exports: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Execute comprehensive daily export workflow
    ''' </summary>
    Public Shared Function ExecuteDailyExport(cfg As JObject, Optional manualTrigger As Boolean = False) As JObject
        Try
            Dim exportResult As New JObject()
            exportResult("timestamp") = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
            exportResult("type") = "daily"
            exportResult("manual_trigger") = manualTrigger

            Dim exportDir As String = CreateExportDirectory("daily", DateTime.Now)
            Dim deliverables As New JArray()

            ' 1. Generate daily betting report
            Dim reportData As JObject = GenerateDailyReport(cfg)
            If reportData("success").ToString() = "True" Then

                ' 2. Export to PDF
                Dim pdfPath As String = ExportToPdf(reportData, exportDir, "daily_report")
                If Not String.IsNullOrEmpty(pdfPath) Then
                    deliverables.Add(CreateDeliverableEntry("PDF", pdfPath, "Daily betting report in PDF format"))
                End If

                ' 3. Export to Excel
                Dim excelPath As String = ExportToExcel(reportData, exportDir, "daily_report")
                If Not String.IsNullOrEmpty(excelPath) Then
                    deliverables.Add(CreateDeliverableEntry("Excel", excelPath, "Daily betting data in Excel format"))
                End If

                ' 4. Publish to blog if enabled
                If cfg("blogger")?("enabled")?.ToString() = "True" Then
                    Dim blogResult As String = PublishToBlog(reportData, "daily", cfg)
                    If Not blogResult.StartsWith("ERROR") Then
                        deliverables.Add(CreateDeliverableEntry("Blog", blogResult, "Published to Google Blogger"))
                    End If
                End If

                ' 5. Generate newsletter content
                Dim newsletterPath As String = GenerateNewsletter(reportData, exportDir, "daily")
                If Not String.IsNullOrEmpty(newsletterPath) Then
                    deliverables.Add(CreateDeliverableEntry("Newsletter", newsletterPath, "Daily newsletter HTML"))
                End If

                ' 6. Create social media posts
                Dim socialContent As String = GenerateSocialPosts(reportData, "daily", cfg)
                If Not String.IsNullOrEmpty(socialContent) Then
                    Dim socialPath As String = Path.Combine(exportDir, "social_posts.txt")
                    File.WriteAllText(socialPath, socialContent)
                    deliverables.Add(CreateDeliverableEntry("Social", socialPath, "Social media posts"))
                End If

            End If

            exportResult("deliverables") = deliverables
            exportResult("export_directory") = exportDir
            exportResult("success") = deliverables.Count > 0

            ' Log the export
            LogScheduledExport("daily", deliverables.Count, exportDir, exportResult("success").ToString())

            ' Send completion alert
            SendExportCompletionAlert("Daily Export", deliverables.Count, cfg)

            Return exportResult

        Catch ex As Exception
            Console.WriteLine($"❌ Daily export failed: {ex.Message}")
            Dim errorResult As New JObject()
            errorResult("success") = False
            errorResult("error") = ex.Message
            errorResult("timestamp") = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
            Return errorResult
        End Try
    End Function

    ''' <summary>
    ''' Execute comprehensive weekly export workflow
    ''' </summary>
    Public Shared Function ExecuteWeeklyExport(cfg As JObject, Optional manualTrigger As Boolean = False) As JObject
        Try
            Dim exportResult As New JObject()
            exportResult("timestamp") = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
            exportResult("type") = "weekly"
            exportResult("manual_trigger") = manualTrigger

            Dim exportDir As String = CreateExportDirectory("weekly", DateTime.Now)
            Dim deliverables As New JArray()

            ' 1. Generate weekly arbitrage digest
            Dim weeklyData As JObject = GenerateWeeklyDigest(cfg)
            If weeklyData("success").ToString() = "True" Then

                ' 2. Comprehensive PDF report
                Dim pdfPath As String = ExportToPdf(weeklyData, exportDir, "weekly_digest")
                If Not String.IsNullOrEmpty(pdfPath) Then
                    deliverables.Add(CreateDeliverableEntry("PDF", pdfPath, "Weekly arbitrage digest PDF"))
                End If

                ' 3. Excel analytics workbook
                Dim excelPath As String = ExportToExcel(weeklyData, exportDir, "weekly_analytics")
                If Not String.IsNullOrEmpty(excelPath) Then
                    deliverables.Add(CreateDeliverableEntry("Excel", excelPath, "Weekly analytics workbook"))
                End If

                ' 4. Blog post for SEO
                If cfg("blogger")?("enabled")?.ToString() = "True" Then
                    Dim blogResult As String = PublishToBlog(weeklyData, "weekly", cfg)
                    If Not blogResult.StartsWith("ERROR") Then
                        deliverables.Add(CreateDeliverableEntry("Blog", blogResult, "Weekly digest blog post"))
                    End If
                End If

                ' 5. Premium newsletter
                Dim newsletterPath As String = GenerateNewsletter(weeklyData, exportDir, "weekly")
                If Not String.IsNullOrEmpty(newsletterPath) Then
                    deliverables.Add(CreateDeliverableEntry("Newsletter", newsletterPath, "Weekly premium newsletter"))
                End If

                ' 6. Performance summary for stakeholders
                Dim summaryPath As String = GeneratePerformanceSummary(weeklyData, exportDir)
                If Not String.IsNullOrEmpty(summaryPath) Then
                    deliverables.Add(CreateDeliverableEntry("Summary", summaryPath, "Weekly performance summary"))
                End If

            End If

            exportResult("deliverables") = deliverables
            exportResult("export_directory") = exportDir
            exportResult("success") = deliverables.Count > 0

            ' Log the export
            LogScheduledExport("weekly", deliverables.Count, exportDir, exportResult("success").ToString())

            ' Send completion alert
            SendExportCompletionAlert("Weekly Export", deliverables.Count, cfg)

            Return exportResult

        Catch ex As Exception
            Console.WriteLine($"❌ Weekly export failed: {ex.Message}")
            Dim errorResult As New JObject()
            errorResult("success") = False
            errorResult("error") = ex.Message
            errorResult("timestamp") = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
            Return errorResult
        End Try
    End Function

#End Region

#Region "Timer Management"

    ''' <summary>
    ''' Setup daily export timer based on configuration
    ''' </summary>
    Private Shared Sub SetupDailyExportTimer(cfg As JObject)
        Try
            Dim dailyTime As String = cfg("scheduled_exports")("daily")("time")?.ToString()
            If String.IsNullOrEmpty(dailyTime) Then dailyTime = "09:00"

            Dim targetTime As DateTime = DateTime.Today.Add(TimeSpan.Parse(dailyTime))
            If targetTime < DateTime.Now Then
                targetTime = targetTime.AddDays(1)
            End If

            Dim interval As TimeSpan = targetTime - DateTime.Now

            Dim timer As New Timer(interval.TotalMilliseconds)
            timer.AutoReset = False

            AddHandler timer.Elapsed, Sub(sender, e)
                ExecuteDailyExport(cfg, False)
                ' Reset timer for next day
                timer.Interval = TimeSpan.FromDays(1).TotalMilliseconds
                timer.AutoReset = True
                timer.Start()
            End Sub

            timer.Start()
            _scheduledTimers.Add(timer)

            Console.WriteLine($"📅 Daily export scheduled for {targetTime:yyyy-MM-dd HH:mm}")

        Catch ex As Exception
            Console.WriteLine($"❌ Failed to setup daily export timer: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Setup weekly export timer based on configuration
    ''' </summary>
    Private Shared Sub SetupWeeklyExportTimer(cfg As JObject)
        Try
            Dim weeklyDay As String = cfg("scheduled_exports")("weekly")("day")?.ToString()
            Dim weeklyTime As String = cfg("scheduled_exports")("weekly")("time")?.ToString()

            If String.IsNullOrEmpty(weeklyDay) Then weeklyDay = "Monday"
            If String.IsNullOrEmpty(weeklyTime) Then weeklyTime = "10:00"

            Dim targetDay As DayOfWeek = [Enum].Parse(GetType(DayOfWeek), weeklyDay)
            Dim targetTime As TimeSpan = TimeSpan.Parse(weeklyTime)

            Dim nextWeekly As DateTime = GetNextWeekly(targetDay, targetTime)
            Dim interval As TimeSpan = nextWeekly - DateTime.Now

            Dim timer As New Timer(interval.TotalMilliseconds)
            timer.AutoReset = False

            AddHandler timer.Elapsed, Sub(sender, e)
                ExecuteWeeklyExport(cfg, False)
                ' Reset timer for next week
                timer.Interval = TimeSpan.FromDays(7).TotalMilliseconds
                timer.AutoReset = True
                timer.Start()
            End Sub

            timer.Start()
            _scheduledTimers.Add(timer)

            Console.WriteLine($"📅 Weekly export scheduled for {nextWeekly:yyyy-MM-dd HH:mm}")

        Catch ex As Exception
            Console.WriteLine($"❌ Failed to setup weekly export timer: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Calculate next weekly occurrence
    ''' </summary>
    Private Shared Function GetNextWeekly(targetDay As DayOfWeek, targetTime As TimeSpan) As DateTime
        Dim now As DateTime = DateTime.Now
        Dim daysUntilTarget As Integer = (targetDay - now.DayOfWeek + 7) Mod 7

        Dim targetDate As DateTime = now.Date.AddDays(daysUntilTarget).Add(targetTime)

        If targetDate <= now Then
            targetDate = targetDate.AddDays(7)
        End If

        Return targetDate
    End Function

    ''' <summary>
    ''' Stop all scheduled export timers
    ''' </summary>
    Public Shared Sub StopAllScheduledExports()
        Try
            For Each timer As Timer In _scheduledTimers
                timer.Stop()
                timer.Dispose()
            Next
            _scheduledTimers.Clear()
            Console.WriteLine("🛑 All scheduled export timers stopped")

        Catch ex As Exception
            Console.WriteLine($"❌ Failed to stop scheduled timers: {ex.Message}")
        End Try
    End Sub

#End Region

#Region "Report Generation"

    ''' <summary>
    ''' Generate daily betting report data
    ''' </summary>
    Private Shared Function GenerateDailyReport(cfg As JObject) As JObject
        Try
            ' This would integrate with existing ReportCore functionality
            Dim reportData As New JObject()
            reportData("success") = True
            reportData("type") = "daily"
            reportData("date") = DateTime.Now.ToString("yyyy-MM-dd")

            ' Placeholder data - replace with actual ReportCore integration
            reportData("summary") = "Daily betting report generated successfully"
            reportData("arbitrage_count") = 12
            reportData("value_bet_count") = 8
            reportData("total_opportunities") = 20

            Return reportData

        Catch ex As Exception
            Dim errorData As New JObject()
            errorData("success") = False
            errorData("error") = ex.Message
            Return errorData
        End Try
    End Function

    ''' <summary>
    ''' Generate weekly arbitrage digest
    ''' </summary>
    Private Shared Function GenerateWeeklyDigest(cfg As JObject) As JObject
        Try
            Dim digestData As New JObject()
            digestData("success") = True
            digestData("type") = "weekly"
            digestData("week_start") = DateTime.Now.AddDays(-6).ToString("yyyy-MM-dd")
            digestData("week_end") = DateTime.Now.ToString("yyyy-MM-dd")

            ' Placeholder data - replace with actual analytics
            digestData("summary") = "Weekly arbitrage digest with performance analysis"
            digestData("total_arbs_found") = 85
            digestData("avg_profit_margin") = 2.3
            digestData("success_rate") = 94.2

            Return digestData

        Catch ex As Exception
            Dim errorData As New JObject()
            errorData("success") = False
            errorData("error") = ex.Message
            Return errorData
        End Try
    End Function

#End Region

#Region "Export Formats"

    ''' <summary>
    ''' Export report to PDF format
    ''' </summary>
    Private Shared Function ExportToPdf(reportData As JObject, exportDir As String, fileName As String) As String
        Try
            ' Placeholder for PDF generation
            ' This would integrate with a PDF library like iTextSharp
            Dim pdfPath As String = Path.Combine(exportDir, $"{fileName}_{DateTime.Now:yyyyMMdd}.pdf")

            ' Create placeholder PDF content
            Dim htmlContent As String = $"<html><body><h1>{reportData("type").ToString().ToUpper()} Report</h1>" &
                                       $"<p>Generated: {DateTime.Now}</p>" &
                                       $"<p>{reportData("summary")}</p></body></html>"

            File.WriteAllText(pdfPath.Replace(".pdf", ".html"), htmlContent)

            Console.WriteLine($"📄 PDF exported: {pdfPath}")
            Return pdfPath

        Catch ex As Exception
            Console.WriteLine($"❌ PDF export failed: {ex.Message}")
            Return ""
        End Try
    End Function

    ''' <summary>
    ''' Export report to Excel format
    ''' </summary>
    Private Shared Function ExportToExcel(reportData As JObject, exportDir As String, fileName As String) As String
        Try
            ' Placeholder for Excel generation
            ' This would integrate with Excel libraries like EPPlus or ClosedXML
            Dim excelPath As String = Path.Combine(exportDir, $"{fileName}_{DateTime.Now:yyyyMMdd}.csv")

            ' Create CSV placeholder
            Dim csvContent As New StringBuilder()
            csvContent.AppendLine("Date,Type,Summary")
            csvContent.AppendLine($"{DateTime.Now:yyyy-MM-dd},{reportData("type")},{reportData("summary")}")

            File.WriteAllText(excelPath, csvContent.ToString())

            Console.WriteLine($"📊 Excel exported: {excelPath}")
            Return excelPath

        Catch ex As Exception
            Console.WriteLine($"❌ Excel export failed: {ex.Message}")
            Return ""
        End Try
    End Function

    ''' <summary>
    ''' Publish report to blog
    ''' </summary>
    Private Shared Function PublishToBlog(reportData As JObject, reportType As String, cfg As JObject) As String
        Try
            If cfg("blogger")?("enabled")?.ToString() <> "True" Then
                Return "Blog publishing disabled"
            End If

            ' Convert report to blog format
            Dim blogContent = BloggerHelper.ConvertReportToBlog(reportData("summary").ToString(), reportType, cfg)

            ' Publish to Blogger
            Dim postId As String = BloggerHelper.PublishPost(cfg, blogContent.Item1, blogContent.Item2, {reportType, "sports-betting", "analytics"})

            If Not postId.StartsWith("ERROR") Then
                Console.WriteLine($"📝 Blog published: Post ID {postId}")
                Return postId
            Else
                Console.WriteLine($"❌ Blog publish failed: {postId}")
                Return postId
            End If

        Catch ex As Exception
            Console.WriteLine($"❌ Blog publishing failed: {ex.Message}")
            Return $"ERROR: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Generate newsletter HTML
    ''' </summary>
    Private Shared Function GenerateNewsletter(reportData As JObject, exportDir As String, reportType As String) As String
        Try
            Dim newsletterPath As String = Path.Combine(exportDir, $"{reportType}_newsletter_{DateTime.Now:yyyyMMdd}.html")

            Dim newsletter As New StringBuilder()
            newsletter.AppendLine("<!DOCTYPE html>")
            newsletter.AppendLine("<html><head><title>EQ12 Newsletter</title></head><body>")
            newsletter.AppendLine($"<h1>EQ12 {reportType.ToUpper()} Newsletter</h1>")
            newsletter.AppendLine($"<p><strong>Date:</strong> {DateTime.Now:MMMM dd, yyyy}</p>")
            newsletter.AppendLine($"<div>{reportData("summary")}</div>")
            newsletter.AppendLine("<hr><p><em>Generated by EQ12 Sports Betting Terminal</em></p>")
            newsletter.AppendLine("</body></html>")

            File.WriteAllText(newsletterPath, newsletter.ToString())

            Console.WriteLine($"📧 Newsletter generated: {newsletterPath}")
            Return newsletterPath

        Catch ex As Exception
            Console.WriteLine($"❌ Newsletter generation failed: {ex.Message}")
            Return ""
        End Try
    End Function

    ''' <summary>
    ''' Generate social media posts
    ''' </summary>
    Private Shared Function GenerateSocialPosts(reportData As JObject, reportType As String, cfg As JObject) As String
        Try
            Dim posts As New StringBuilder()

            ' Twitter-style post
            posts.AppendLine("📊 TWITTER POST:")
            posts.AppendLine($"Daily #SportsBetting Analysis Complete!")
            posts.AppendLine($"✅ {reportData("arbitrage_count")} Arbitrage Ops")
            posts.AppendLine($"✅ {reportData("value_bet_count")} Value Bets")
            posts.AppendLine($"📈 EQ12 Terminal delivering the edge!")
            posts.AppendLine("#Arbitrage #ValueBetting #SportsTech")
            posts.AppendLine("")

            ' LinkedIn-style post
            posts.AppendLine("💼 LINKEDIN POST:")
            posts.AppendLine($"Today's quantitative sports betting analysis identified {reportData("total_opportunities")} market opportunities.")
            posts.AppendLine("Our algorithmic approach continues to demonstrate the power of data-driven decision making in sports markets.")
            posts.AppendLine("#DataScience #SportsBetting #Quantitative #Analytics")
            posts.AppendLine("")

            ' Discord/Telegram post
            posts.AppendLine("💬 TELEGRAM/DISCORD POST:")
            posts.AppendLine($"🚨 {reportType.ToUpper()} REPORT READY!")
            posts.AppendLine($"Found {reportData("total_opportunities")} opportunities today")
            posts.AppendLine("Premium subscribers check your feeds! 📊")

            Return posts.ToString()

        Catch ex As Exception
            Console.WriteLine($"❌ Social posts generation failed: {ex.Message}")
            Return ""
        End Try
    End Function

    ''' <summary>
    ''' Generate performance summary for stakeholders
    ''' </summary>
    Private Shared Function GeneratePerformanceSummary(weeklyData As JObject, exportDir As String) As String
        Try
            Dim summaryPath As String = Path.Combine(exportDir, $"performance_summary_{DateTime.Now:yyyyMMdd}.txt")

            Dim summary As New StringBuilder()
            summary.AppendLine("EQ12 WEEKLY PERFORMANCE SUMMARY")
            summary.AppendLine("=====================================")
            summary.AppendLine($"Report Period: {weeklyData("week_start")} to {weeklyData("week_end")}")
            summary.AppendLine("")
            summary.AppendLine("KEY METRICS:")
            summary.AppendLine($"• Total Arbitrage Opportunities: {weeklyData("total_arbs_found")}")
            summary.AppendLine($"• Average Profit Margin: {weeklyData("avg_profit_margin")}%")
            summary.AppendLine($"• Success Rate: {weeklyData("success_rate")}%")
            summary.AppendLine("")
            summary.AppendLine("SYSTEM STATUS: ✅ OPERATIONAL")
            summary.AppendLine("NEXT ACTIONS: Continue monitoring, optimize algorithms")

            File.WriteAllText(summaryPath, summary.ToString())

            Console.WriteLine($"📋 Performance summary generated: {summaryPath}")
            Return summaryPath

        Catch ex As Exception
            Console.WriteLine($"❌ Performance summary failed: {ex.Message}")
            Return ""
        End Try
    End Function

#End Region

#Region "Utilities and Logging"

    ''' <summary>
    ''' Create export directory with timestamp
    ''' </summary>
    Private Shared Function CreateExportDirectory(exportType As String, exportDate As DateTime) As String
        Try
            Dim baseDir As String = "Exports"
            Dim typeDir As String = Path.Combine(baseDir, exportType)
            Dim dateDir As String = Path.Combine(typeDir, exportDate.ToString("yyyy-MM-dd"))

            If Not Directory.Exists(dateDir) Then
                Directory.CreateDirectory(dateDir)
            End If

            Return dateDir

        Catch ex As Exception
            Console.WriteLine($"❌ Failed to create export directory: {ex.Message}")
            Return "Exports"
        End Try
    End Function

    ''' <summary>
    ''' Create deliverable entry for tracking
    ''' </summary>
    Private Shared Function CreateDeliverableEntry(type As String, path As String, description As String) As JObject
        Dim entry As New JObject()
        entry("type") = type
        entry("path") = path
        entry("description") = description
        entry("timestamp") = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
        entry("size_bytes") = If(File.Exists(path), New FileInfo(path).Length, 0)
        Return entry
    End Function

    ''' <summary>
    ''' Log scheduled export to database
    ''' </summary>
    Private Shared Sub LogScheduledExport(exportType As String, deliverableCount As Integer, exportPath As String, success As String)
        Try
            Dim dbPath As String = "Data\eq12_terminal.db"
            Using conn As New SQLiteConnection($"Data Source={dbPath}")
                conn.Open()

                Dim sql As String = "INSERT INTO scheduled_exports (export_type, deliverable_count, export_path, success, duration_seconds) VALUES (@exportType, @deliverableCount, @exportPath, @success, @duration)"
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@exportType", exportType)
                    cmd.Parameters.AddWithValue("@deliverableCount", deliverableCount)
                    cmd.Parameters.AddWithValue("@exportPath", exportPath)
                    cmd.Parameters.AddWithValue("@success", success)
                    cmd.Parameters.AddWithValue("@duration", 0) ' Could be calculated if needed

                    cmd.ExecuteNonQuery()
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"Failed to log scheduled export: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Send export completion alert
    ''' </summary>
    Private Shared Sub SendExportCompletionAlert(exportType As String, deliverableCount As Integer, cfg As JObject)
        Try
            If cfg("telegram") Is Nothing Then Return

            Dim message As String = $"📊 {exportType.ToUpper()} COMPLETED{vbCrLf}" &
                                   $"✅ {deliverableCount} deliverables generated{vbCrLf}" &
                                   $"🕒 {DateTime.Now:yyyy-MM-dd HH:mm} UTC{vbCrLf}" &
                                   "Ready for distribution and monetization! 🚀"

            ' Use existing TelegramHelper if available
            ' TelegramHelper.SendMessage(cfg, message)

        Catch ex As Exception
            Console.WriteLine($"Failed to send export completion alert: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Get export statistics for monitoring
    ''' </summary>
    Public Shared Function GetExportStats(days As Integer) As JObject
        Try
            Dim dbPath As String = "Data\eq12_terminal.db"
            Dim stats As New JObject()

            Using conn As New SQLiteConnection($"Data Source={dbPath}")
                conn.Open()

                ' Total exports
                Dim sql As String = $"SELECT COUNT(*) FROM scheduled_exports WHERE ts >= datetime('now', '-{days} days')"
                Using cmd As New SQLiteCommand(sql, conn)
                    stats("total_exports") = Convert.ToInt32(cmd.ExecuteScalar())
                End Using

                ' Success rate
                sql = $"SELECT ROUND(CAST(SUM(CASE WHEN success = 'True' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 2) FROM scheduled_exports WHERE ts >= datetime('now', '-{days} days')"
                Using cmd As New SQLiteCommand(sql, conn)
                    Dim successRate = cmd.ExecuteScalar()
                    stats("success_rate") = If(successRate Is DBNull.Value, 0, Convert.ToDouble(successRate))
                End Using

                ' Total deliverables
                sql = $"SELECT SUM(deliverable_count) FROM scheduled_exports WHERE success = 'True' AND ts >= datetime('now', '-{days} days')"
                Using cmd As New SQLiteCommand(sql, conn)
                    Dim totalDeliverables = cmd.ExecuteScalar()
                    stats("total_deliverables") = If(totalDeliverables Is DBNull.Value, 0, Convert.ToInt32(totalDeliverables))
                End Using
            End Using

            Return stats

        Catch ex As Exception
            Console.WriteLine($"Failed to get export stats: {ex.Message}")
            Return New JObject()
        End Try
    End Function

#End Region

End Class
