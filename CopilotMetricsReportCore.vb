' ================================================
' EQ12 MODULE: CopilotMetricsReportCore.vb
' Purpose: Generate PDF reports for GitHub Copilot metrics with monetization insights
' Features: iTextSharp PDF generation, SQLite data queries, ROI analysis
' ================================================
Imports iTextSharp.text
Imports iTextSharp.text.pdf
Imports System.Data
Imports System.IO
Imports System.Data.SQLite
Imports System.Globalization

Public Class CopilotMetricsReportCore

    Public Shared Function Generate(period As String, outDir As String) As String
        Try
            ' Ensure output directory exists
            If Not Directory.Exists(outDir) Then
                Directory.CreateDirectory(outDir)
            End If

            ' Generate filename with timestamp
            Dim timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss")
            Dim filename = $"EQ12_Copilot_Metrics_{period}_{timestamp}.pdf"
            Dim fullPath = Path.Combine(outDir, filename)

            ' Get data based on period
            Dim dataTable = GetMetricsData(period)
            Dim insights = CalculateInsights(dataTable)

            ' Generate PDF
            CreatePdfReport(fullPath, period, dataTable, insights)

            ' Log success
            WriteLog($"Generated Copilot metrics report: {fullPath}")

            Return fullPath

        Catch ex As Exception
            WriteLog($"Error generating Copilot metrics report: {ex.Message}")
            Throw
        End Try
    End Function

    Private Shared Function GetMetricsData(period As String) As DataTable
        Dim dataTable As New DataTable()
        Dim dbPath = "C:\EQ12\data\bankroll.db"

        If Not File.Exists(dbPath) Then
            WriteLog("Warning: Database not found, creating empty dataset")
            Return dataTable
        End If

        Using connection As New SQLiteConnection($"Data Source={dbPath}")
            connection.Open()

            Using command = connection.CreateCommand()
                Select Case period.ToLower()
                    Case "daily"
                        command.CommandText = "SELECT * FROM copilot_metrics WHERE timestamp >= datetime('now', '-1 day') ORDER BY timestamp DESC"
                    Case "weekly"
                        command.CommandText = "SELECT * FROM copilot_metrics WHERE timestamp >= datetime('now', '-7 days') ORDER BY timestamp DESC"
                    Case "monthly"
                        command.CommandText = "SELECT * FROM copilot_metrics WHERE timestamp >= datetime('now', '-30 days') ORDER BY timestamp DESC"
                    Case Else
                        command.CommandText = "SELECT * FROM copilot_metrics WHERE timestamp >= datetime('now', '-7 days') ORDER BY timestamp DESC"
                End Select

                Using adapter As New SQLiteDataAdapter(command)
                    adapter.Fill(dataTable)
                End Using
            End Using
        End Using

        WriteLog($"Retrieved {dataTable.Rows.Count} records for {period} report")
        Return dataTable
    End Function

    Private Shared Function CalculateInsights(dataTable As DataTable) As Dictionary(Of String, Object)
        Dim insights As New Dictionary(Of String, Object)

        Try
            If dataTable.Rows.Count = 0 Then
                insights("total_records") = 0
                insights("avg_acceptance_rate") = 0.0
                insights("avg_active_users") = 0
                insights("avg_licensed_users") = 0
                insights("utilization_rate") = 0.0
                insights("estimated_monthly_cost") = 0
                insights("roi_score") = 0.0
                Return insights
            End If

            ' Calculate averages
            Dim totalRecords = dataTable.Rows.Count
            Dim sumAcceptanceRate As Double = 0
            Dim sumActiveUsers As Integer = 0
            Dim sumLicensedUsers As Integer = 0
            Dim sumTotalSuggestions As Long = 0
            Dim sumAcceptedSuggestions As Long = 0

            For Each row As DataRow In dataTable.Rows
                If Not IsDBNull(row("acceptance_rate")) Then
                    sumAcceptanceRate += Convert.ToDouble(row("acceptance_rate"))
                End If
                If Not IsDBNull(row("active_users")) Then
                    sumActiveUsers += Convert.ToInt32(row("active_users"))
                End If
                If Not IsDBNull(row("licensed_users")) Then
                    sumLicensedUsers += Convert.ToInt32(row("licensed_users"))
                End If
                If Not IsDBNull(row("total_suggestions")) Then
                    sumTotalSuggestions += Convert.ToInt64(row("total_suggestions"))
                End If
                If Not IsDBNull(row("accepted_suggestions")) Then
                    sumAcceptedSuggestions += Convert.ToInt64(row("accepted_suggestions"))
                End If
            Next

            insights("total_records") = totalRecords
            insights("avg_acceptance_rate") = If(totalRecords > 0, sumAcceptanceRate / totalRecords, 0.0)
            insights("avg_active_users") = If(totalRecords > 0, sumActiveUsers / totalRecords, 0)
            insights("avg_licensed_users") = If(totalRecords > 0, sumLicensedUsers / totalRecords, 0)
            insights("total_suggestions") = sumTotalSuggestions
            insights("total_accepted") = sumAcceptedSuggestions

            ' Calculate utilization rate
            Dim avgActive = CInt(insights("avg_active_users"))
            Dim avgLicensed = CInt(insights("avg_licensed_users"))
            insights("utilization_rate") = If(avgLicensed > 0, CDbl(avgActive) / avgLicensed, 0.0)

            ' ROI Calculations
            Dim costPerLicense = 19 ' GitHub Copilot cost per user per month
            Dim totalMonthlyCost = avgLicensed * costPerLicense
            Dim avgAcceptanceRate = CDbl(insights("avg_acceptance_rate"))

            ' Productivity assumptions
            Dim hoursPerMonth = 160 ' Standard work hours
            Dim hourlyRate = 50 ' Average developer hourly rate
            Dim productivityGainPercent = avgAcceptanceRate * 0.25 ' 25% max productivity gain
            Dim monthlySavings = avgActive * hoursPerMonth * hourlyRate * productivityGainPercent

            insights("estimated_monthly_cost") = totalMonthlyCost
            insights("estimated_monthly_savings") = monthlySavings
            insights("roi_percentage") = If(totalMonthlyCost > 0, ((monthlySavings - totalMonthlyCost) / totalMonthlyCost) * 100, 0.0)
            insights("payback_months") = If(monthlySavings > totalMonthlyCost, totalMonthlyCost / (monthlySavings - totalMonthlyCost), Double.MaxValue)

            Return insights

        Catch ex As Exception
            WriteLog($"Error calculating insights: {ex.Message}")
            Return insights
        End Try
    End Function

    Private Shared Sub CreatePdfReport(filePath As String, period As String, dataTable As DataTable, insights As Dictionary(Of String, Object))
        Using fileStream As New FileStream(filePath, FileMode.Create)
            Dim document As New Document(PageSize.A4, 36, 36, 36, 36)
            Dim writer = PdfWriter.GetInstance(document, fileStream)

            document.Open()

            ' Title Page
            AddTitle(document, period)
            AddExecutiveSummary(document, insights)
            AddDetailedMetrics(document, dataTable)
            AddMonetizationAnalysis(document, insights)
            AddFooter(document)

            document.Close()
        End Using
    End Sub

    Private Shared Sub AddTitle(document As Document, period As String)
        ' Main Title
        Dim titleFont = FontFactory.GetFont("Arial", 20, Font.BOLD, BaseColor.DARK_GRAY)
        Dim title As New Paragraph($"EQ12 GitHub Copilot Metrics Report", titleFont)
        title.Alignment = Element.ALIGN_CENTER
        title.SpacingAfter = 10
        document.Add(title)

        ' Subtitle
        Dim subtitleFont = FontFactory.GetFont("Arial", 14, Font.NORMAL, BaseColor.GRAY)
        Dim subtitle As New Paragraph($"{period.ToUpper()} Analysis - Generated {DateTime.UtcNow:yyyy-MM-dd HH:mm} UTC", subtitleFont)
        subtitle.Alignment = Element.ALIGN_CENTER
        subtitle.SpacingAfter = 20
        document.Add(subtitle)

        ' Separator line
        Dim line As New Paragraph("_" & New String("_"c, 80))
        line.Alignment = Element.ALIGN_CENTER
        line.SpacingAfter = 15
        document.Add(line)
    End Sub

    Private Shared Sub AddExecutiveSummary(document As Document, insights As Dictionary(Of String, Object))
        Dim headerFont = FontFactory.GetFont("Arial", 16, Font.BOLD, BaseColor.BLACK)
        Dim normalFont = FontFactory.GetFont("Arial", 11, Font.NORMAL)
        Dim boldFont = FontFactory.GetFont("Arial", 11, Font.BOLD)

        document.Add(New Paragraph("Executive Summary", headerFont))
        document.Add(New Paragraph(" "))

        ' Key metrics table
        Dim table As New PdfPTable(2)
        table.WidthPercentage = 100
        table.SetWidths({1, 2})

        ' Add key metrics
        AddTableRow(table, "Total Records:", insights("total_records").ToString())
        AddTableRow(table, "Avg Acceptance Rate:", $"{CDbl(insights("avg_acceptance_rate")) * 100:F2}%")
        AddTableRow(table, "Avg Active Users:", insights("avg_active_users").ToString())
        AddTableRow(table, "Avg Licensed Users:", insights("avg_licensed_users").ToString())
        AddTableRow(table, "License Utilization:", $"{CDbl(insights("utilization_rate")) * 100:F2}%")

        If insights.ContainsKey("roi_percentage") Then
            Dim roi = CDbl(insights("roi_percentage"))
            Dim roiColor = If(roi > 0, BaseColor.GREEN, BaseColor.RED)
            AddTableRow(table, "ROI:", $"{roi:F2}%", roiColor)
        End If

        document.Add(table)
        document.Add(New Paragraph(" "))
    End Sub

    Private Shared Sub AddDetailedMetrics(document As Document, dataTable As DataTable)
        Dim headerFont = FontFactory.GetFont("Arial", 16, Font.BOLD, BaseColor.BLACK)
        Dim smallFont = FontFactory.GetFont("Courier", 9, Font.NORMAL)

        document.Add(New Paragraph("Detailed Metrics", headerFont))
        document.Add(New Paragraph(" "))

        If dataTable.Rows.Count = 0 Then
            document.Add(New Paragraph("No data available for the selected period.", smallFont))
            Return
        End If

        ' Create table for metrics
        Dim metricsTable As New PdfPTable(6)
        metricsTable.WidthPercentage = 100
        metricsTable.SetWidths({2, 2, 1, 1, 1, 2})

        ' Headers
        Dim headerFont2 = FontFactory.GetFont("Arial", 10, Font.BOLD, BaseColor.WHITE)
        AddTableHeaderCell(metricsTable, "Timestamp", headerFont2)
        AddTableHeaderCell(metricsTable, "Organization", headerFont2)
        AddTableHeaderCell(metricsTable, "Active", headerFont2)
        AddTableHeaderCell(metricsTable, "Licensed", headerFont2)
        AddTableHeaderCell(metricsTable, "Rate %", headerFont2)
        AddTableHeaderCell(metricsTable, "Suggestions", headerFont2)

        ' Data rows (limit to first 50 for readability)
        Dim rowCount = Math.Min(dataTable.Rows.Count, 50)
        For i As Integer = 0 To rowCount - 1
            Dim row = dataTable.Rows(i)
            Dim timestamp = If(IsDBNull(row("timestamp")), "", Convert.ToDateTime(row("timestamp")).ToString("MM/dd HH:mm"))
            Dim org = If(IsDBNull(row("organization")), "", row("organization").ToString())
            Dim active = If(IsDBNull(row("active_users")), 0, Convert.ToInt32(row("active_users")))
            Dim licensed = If(IsDBNull(row("licensed_users")), 0, Convert.ToInt32(row("licensed_users")))
            Dim rate = If(IsDBNull(row("acceptance_rate")), 0.0, Convert.ToDouble(row("acceptance_rate")) * 100)
            Dim suggestions = If(IsDBNull(row("total_suggestions")), 0, Convert.ToInt32(row("total_suggestions")))

            metricsTable.AddCell(New PdfPCell(New Phrase(timestamp, smallFont)))
            metricsTable.AddCell(New PdfPCell(New Phrase(org, smallFont)))
            metricsTable.AddCell(New PdfPCell(New Phrase(active.ToString(), smallFont)))
            metricsTable.AddCell(New PdfPCell(New Phrase(licensed.ToString(), smallFont)))
            metricsTable.AddCell(New PdfPCell(New Phrase($"{rate:F1}", smallFont)))
            metricsTable.AddCell(New PdfPCell(New Phrase(suggestions.ToString(), smallFont)))
        Next

        document.Add(metricsTable)

        If dataTable.Rows.Count > 50 Then
            document.Add(New Paragraph($"Note: Showing first 50 of {dataTable.Rows.Count} total records", smallFont))
        End If

        document.Add(New Paragraph(" "))
    End Sub

    Private Shared Sub AddMonetizationAnalysis(document As Document, insights As Dictionary(Of String, Object))
        Dim headerFont = FontFactory.GetFont("Arial", 16, Font.BOLD, BaseColor.BLACK)
        Dim normalFont = FontFactory.GetFont("Arial", 11, Font.NORMAL)
        Dim boldFont = FontFactory.GetFont("Arial", 11, Font.BOLD)

        document.Add(New Paragraph("Monetization & ROI Analysis", headerFont))
        document.Add(New Paragraph(" "))

        ' Financial metrics
        Dim finTable As New PdfPTable(2)
        finTable.WidthPercentage = 100
        finTable.SetWidths({1, 2})

        If insights.ContainsKey("estimated_monthly_cost") Then
            AddTableRow(finTable, "Monthly License Cost:", $"${CDbl(insights("estimated_monthly_cost")):F2}")
        End If

        If insights.ContainsKey("estimated_monthly_savings") Then
            AddTableRow(finTable, "Estimated Monthly Savings:", $"${CDbl(insights("estimated_monthly_savings")):F2}")
        End If

        If insights.ContainsKey("payback_months") Then
            Dim payback = CDbl(insights("payback_months"))
            Dim paybackText = If(payback = Double.MaxValue, "No payback (cost > savings)", $"{payback:F1} months")
            AddTableRow(finTable, "Payback Period:", paybackText)
        End If

        document.Add(finTable)
        document.Add(New Paragraph(" "))

        ' Recommendations
        document.Add(New Paragraph("Recommendations:", boldFont))

        Dim utilizationRate = If(insights.ContainsKey("utilization_rate"), CDbl(insights("utilization_rate")), 0.0)
        Dim acceptanceRate = If(insights.ContainsKey("avg_acceptance_rate"), CDbl(insights("avg_acceptance_rate")), 0.0)

        Dim recommendations As New List(Of String)

        If utilizationRate < 0.7 Then
            recommendations.Add("• Consider reducing licensed seats - utilization below 70%")
        End If

        If acceptanceRate < 0.3 Then
            recommendations.Add("• Provide Copilot training to improve acceptance rates")
        End If

        If utilizationRate > 0.9 Then
            recommendations.Add("• High utilization - consider expanding Copilot licenses")
        End If

        recommendations.Add("• Track ROI monthly to optimize license allocation")
        recommendations.Add("• Monitor language-specific usage patterns for targeted improvements")

        For Each rec In recommendations
            document.Add(New Paragraph(rec, normalFont))
        Next

        document.Add(New Paragraph(" "))
    End Sub

    Private Shared Sub AddFooter(document As Document)
        Dim footerFont = FontFactory.GetFont("Arial", 9, Font.ITALIC, BaseColor.GRAY)

        document.Add(New Paragraph(" "))
        document.Add(New Paragraph("Generated by EQ12 Copilot Metrics Automation System", footerFont))
        document.Add(New Paragraph($"Report ID: {Guid.NewGuid().ToString("N").Substring(0, 8).ToUpper()}", footerFont))
        document.Add(New Paragraph("For questions contact: automation@eq12.dev", footerFont))
    End Sub

    Private Shared Sub AddTableRow(table As PdfPTable, label As String, value As String, Optional valueColor As BaseColor = Nothing)
        Dim labelFont = FontFactory.GetFont("Arial", 10, Font.BOLD)
        Dim valueFont = FontFactory.GetFont("Arial", 10, Font.NORMAL)

        If valueColor IsNot Nothing Then
            valueFont = FontFactory.GetFont("Arial", 10, Font.BOLD, valueColor)
        End If

        table.AddCell(New PdfPCell(New Phrase(label, labelFont)))
        table.AddCell(New PdfPCell(New Phrase(value, valueFont)))
    End Sub

    Private Shared Sub AddTableHeaderCell(table As PdfPTable, text As String, font As Font)
        Dim cell As New PdfPCell(New Phrase(text, font))
        cell.BackgroundColor = BaseColor.DARK_GRAY
        cell.HorizontalAlignment = Element.ALIGN_CENTER
        cell.Padding = 5
        table.AddCell(cell)
    End Sub

    Private Shared Sub WriteLog(message As String)
        Try
            Dim logPath = "C:\EQ12\logs\copilot_reports.log"
            Dim logDir = Path.GetDirectoryName(logPath)
            If Not Directory.Exists(logDir) Then
                Directory.CreateDirectory(logDir)
            End If

            Dim timestamp = DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss UTC")
            Dim logEntry = $"{timestamp} - CopilotReports: {message}"
            File.AppendAllText(logPath, logEntry & Environment.NewLine)
            Console.WriteLine(logEntry)
        Catch
            ' Ignore logging errors
        End Try
    End Sub
End Class
