Imports System.Data
Imports System.Data.SQLite
Imports System.IO
Imports System.Text
Imports iText.Kernel.Pdf
Imports iText.Layout
Imports iText.Layout.Element
Imports iText.Layout.Properties
Imports OfficeOpenXml
Imports Newtonsoft.Json.Linq

''' <summary>
''' Final Form Report Generation with PDF, Excel, and GitHub Gist Integration
''' Generates comprehensive reports with mobile-friendly Gist links for instant viewing
''' </summary>
Public Class ReportCore
    ''' <summary>
    ''' Generate comprehensive report (PDF + Excel) and send via email with GitHub Gist + Bitly
    ''' </summary>
    Public Shared Function GenerateAndSend(period As String, baseDir As String, cfg As JObject) As (pdf As String, xlsx As String, gist As String)
        Try
            Console.WriteLine($"🔄 Generating {period} report...")

            Dim (startDate, periodLabel) = GetWindow(period)

            ' Get data from database
            Dim bets = GetTable($"SELECT bet_date,sport,market,selection,book,odds,stake,result,profit_loss
                              FROM bets WHERE bet_date >= date('{startDate:yyyy-MM-dd}')
                              ORDER BY bet_date DESC")

            Dim arbs = GetTable($"SELECT detected_at,event_id,side_a_selection,side_a_book,side_a_odds,
                                      side_b_selection,side_b_book,side_b_odds,profit_percentage,
                                      guaranteed_profit,mode,hedge_stakeA,hedge_stakeB,kelly_stakeA,kelly_stakeB
                              FROM arbitrage_opportunities WHERE detected_at >= datetime('{startDate:yyyy-MM-dd}')
                              ORDER BY detected_at DESC")

            ' Create reports directory
            Dim reportsDir = Path.Combine(baseDir, "Reports")
            If Not Directory.Exists(reportsDir) Then Directory.CreateDirectory(reportsDir)

            Dim ts = DateTime.UtcNow.ToString("yyyyMMdd_HHmm")
            Dim pdfPath = Path.Combine(reportsDir, $"eq12_report_{period}_{ts}.pdf")
            Dim xlsPath = Path.Combine(reportsDir, $"eq12_report_{period}_{ts}.xlsx")

            ' Generate files
            ExportPdf(pdfPath, periodLabel, startDate, bets, arbs)
            ExportExcel(xlsPath, periodLabel, bets, arbs)

            ' --- NEW: Create a concise text summary + post as a GitHub Gist ---
            Dim summaryText As String = BuildTextSummary(periodLabel, bets, arbs)
            Dim gistUrl As String = ""
            Dim shortUrl As String = ""

            Try
                gistUrl = GitHubSync.CreateGist($"eq12_{period}_{ts}_summary", "txt", summaryText)
                Console.WriteLine($"✅ Created GitHub Gist: {gistUrl}")

                ' Shorten the Gist URL with Bitly
                If Not String.IsNullOrWhiteSpace(gistUrl) Then
                    shortUrl = BitlyHelper.GetShortUrl(cfg, gistUrl)
                    If shortUrl <> gistUrl Then
                        Console.WriteLine($"✅ Shortened with Bitly: {shortUrl}")
                    End If
                End If
            Catch ex As Exception
                Console.WriteLine($"⚠️ Could not create Gist: {ex.Message}")
                gistUrl = ""
                shortUrl = ""
            End Try

            ' Email with Bitly short link in body
            Dim subject = $"📊 EQ12 Report ({periodLabel})"
            Dim body = $"Attached are the {periodLabel} reports generated at {DateTime.Now}.{Environment.NewLine}" &
                      If(String.IsNullOrWhiteSpace(shortUrl), "", $"{Environment.NewLine}📱 Quick View (Bitly): {shortUrl}")

            Mailer.SendEmail(cfg, subject, body, New List(Of String) From {pdfPath, xlsPath})

            ' --- NEW: Also send Bitly link via Telegram + Discord ---
            If Not String.IsNullOrWhiteSpace(shortUrl) Then
                Try
                    ' Telegram alert
                    If cfg("telegram")?("token") IsNot Nothing AndAlso cfg("telegram")?("chat_id") IsNot Nothing Then
                        Alerts.Telegram(cfg("telegram")("token").ToString(), cfg("telegram")("chat_id").ToString(),
                                       $"📎 EQ12 {periodLabel} Report: {shortUrl}")
                    End If

                    ' Discord alert
                    If cfg("discord")?("webhook") IsNot Nothing Then
                        Alerts.Discord(cfg("discord")("webhook").ToString(),
                                      $"📎 EQ12 {periodLabel} Report: {shortUrl}")
                    End If
                Catch ex As Exception
                    Console.WriteLine($"⚠️ Alert notification failed: {ex.Message}")
                End Try
            End If

            Console.WriteLine($"✅ {periodLabel} report generated successfully!")
            Console.WriteLine($"   📄 PDF: {pdfPath}")
            Console.WriteLine($"   📊 Excel: {xlsPath}")
            If Not String.IsNullOrEmpty(shortUrl) Then
                Console.WriteLine($"   🔗 Quick View: {shortUrl}")
            End If

            Return (pdfPath, xlsPath, If(String.IsNullOrEmpty(shortUrl), gistUrl, shortUrl))

        Catch ex As Exception
            Console.WriteLine($"❌ Report generation failed: {ex.Message}")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Build a concise text summary for GitHub Gist
    ''' </summary>
    Private Shared Function BuildTextSummary(periodLabel As String, bets As DataTable, arbs As DataTable) As String
        Dim sb As New Text.StringBuilder()
        sb.AppendLine($"EQ12 Report Summary ({periodLabel})")
        sb.AppendLine($"Generated: {DateTime.Now}")
        sb.AppendLine()

        ' Calculate bet metrics
        Dim totalBets = bets.Rows.Count
        Dim wins = 0
        Dim losses = 0
        Dim stakes = 0.0
        Dim totalPL = 0.0

        For Each row As DataRow In bets.Rows
            If Not IsDBNull(row("result")) Then
                If row("result").ToString().ToLower() = "won" Then wins += 1
                If row("result").ToString().ToLower() = "lost" Then losses += 1
            End If
            If Not IsDBNull(row("stake")) Then stakes += Convert.ToDouble(row("stake"))
            If Not IsDBNull(row("profit_loss")) Then totalPL += Convert.ToDouble(row("profit_loss"))
        Next

        sb.AppendLine($"BETS — count={totalBets}, won={wins}, lost={losses}, total_stake=${stakes:N2}, P&L=${totalPL:N2}")

        If totalBets > 0 Then
            Dim preview = Math.Min(5, totalBets)
            For i = 0 To preview - 1
                Dim r = bets.Rows(i)
                sb.AppendLine($" • {r("bet_date")} {r("sport")} {r("market")} {r("selection")} @ {r("book")} {r("odds")} stake=${If(IsDBNull(r("stake")), 0, r("stake"))} result={If(IsDBNull(r("result")), "pending", r("result"))}")
            Next
            If totalBets > preview Then sb.AppendLine($"   (+{totalBets - preview} more)")
        End If
        sb.AppendLine()

        ' Calculate arbitrage metrics
        Dim totalArbs = arbs.Rows.Count
        Dim lockSum As Double = 0.0
        Dim avgArb As Double = 0.0

        If totalArbs > 0 Then
            For Each row As DataRow In arbs.Rows
                If Not IsDBNull(row("guaranteed_profit")) Then lockSum += Convert.ToDouble(row("guaranteed_profit"))
                If Not IsDBNull(row("profit_percentage")) Then avgArb += Convert.ToDouble(row("profit_percentage"))
            Next
            avgArb = avgArb / totalArbs
        End If

        sb.AppendLine($"ARBITRAGE — count={totalArbs}, avg_arb={avgArb:N2}%, lock_profit_sum=${lockSum:N2}")

        If totalArbs > 0 Then
            Dim preview = Math.Min(5, totalArbs)
            For i = 0 To preview - 1
                Dim r = arbs.Rows(i)
                sb.AppendLine($" • {r("detected_at")} {r("side_a_selection")} {If(IsDBNull(r("side_a_odds")), 0, r("side_a_odds"))}@{r("side_a_book")} vs {r("side_b_selection")} {If(IsDBNull(r("side_b_odds")), 0, r("side_b_odds"))}@{r("side_b_book")} {If(IsDBNull(r("profit_percentage")), 0, Convert.ToDouble(r("profit_percentage"))):N2}% lock=${If(IsDBNull(r("guaranteed_profit")), 0.0, Convert.ToDouble(r("guaranteed_profit"))):N2} mode={If(IsDBNull(r("mode")), "unknown", r("mode"))}")
            Next
            If totalArbs > preview Then sb.AppendLine($"   (+{totalArbs - preview} more)")
        End If

        Return sb.ToString()
    End Function

    ''' <summary>
    ''' Get date window and label for report period
    ''' </summary>
    Private Shared Function GetWindow(period As String) As (DateTime, String)
        Select Case period.ToLower()
            Case "day", "daily"
                Return (DateTime.UtcNow.Date, "Daily")
            Case "week", "weekly"
                Return (DateTime.UtcNow.AddDays(-7), "Weekly")
            Case "month", "monthly"
                Return (DateTime.UtcNow.AddMonths(-1), "Monthly")
            Case Else
                Return (DateTime.UtcNow.Date, "Daily")
        End Select
    End Function

    ''' <summary>
    ''' Execute SQL query and return DataTable
    ''' </summary>
    Private Shared Function GetTable(sql As String) As DataTable
        Dim dt As New DataTable()
        Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
            conn.Open()
            Using da As New SQLiteDataAdapter(sql, conn)
                da.Fill(dt)
            End Using
        End Using
        Return dt
    End Function

    ''' <summary>
    ''' Generate comprehensive PDF report
    ''' </summary>
    Private Shared Sub ExportPdf(path As String, periodLabel As String, startDate As DateTime, bets As DataTable, arbs As DataTable)
        Using writer As New PdfWriter(path)
            Using pdf As New PdfDocument(writer)
                Using doc As New Document(pdf)
                    ' Header
                    doc.Add(New Paragraph($"EQ12 Sports Betting Terminal - {periodLabel} Report")
                           .SetTextAlignment(TextAlignment.CENTER)
                           .SetFontSize(20)
                           .SetBold())

                    doc.Add(New Paragraph($"Generated: {DateTime.Now:yyyy-MM-dd HH:mm:ss} UTC")
                           .SetTextAlignment(TextAlignment.CENTER)
                           .SetFontSize(10))

                    doc.Add(New Paragraph($"Report Period: {startDate:yyyy-MM-dd} to {DateTime.Now:yyyy-MM-dd}")
                           .SetTextAlignment(TextAlignment.CENTER)
                           .SetFontSize(12))

                    doc.Add(New Paragraph(" "))

                    ' Executive Summary
                    doc.Add(New Paragraph("EXECUTIVE SUMMARY").SetBold().SetFontSize(14))

                    Dim totalBets = bets.Rows.Count
                    Dim totalArbs = arbs.Rows.Count
                    Dim totalStaked = 0.0
                    Dim totalPL = 0.0

                    For Each row As DataRow In bets.Rows
                        If Not IsDBNull(row("stake")) Then totalStaked += CDbl(row("stake"))
                        If Not IsDBNull(row("profit_loss")) Then totalPL += CDbl(row("profit_loss"))
                    Next

                    Dim totalArbProfit = 0.0
                    For Each row As DataRow In arbs.Rows
                        If Not IsDBNull(row("guaranteed_profit")) Then totalArbProfit += CDbl(row("guaranteed_profit"))
                    Next

                    doc.Add(New Paragraph($"• Total Bets Placed: {totalBets}"))
                    doc.Add(New Paragraph($"• Total Amount Wagered: ${totalStaked:F2}"))
                    doc.Add(New Paragraph($"• Net Profit/Loss: ${totalPL:F2}"))
                    doc.Add(New Paragraph($"• ROI: {If(totalStaked > 0, (totalPL / totalStaked * 100), 0):F1}%"))
                    doc.Add(New Paragraph($"• Arbitrage Opportunities: {totalArbs}"))
                    doc.Add(New Paragraph($"• Total Arbitrage Profit: ${totalArbProfit:F2}"))
                    doc.Add(New Paragraph(" "))

                    ' Bets Section
                    doc.Add(New Paragraph("BETS PLACED").SetBold().SetFontSize(14))
                    If bets.Rows.Count = 0 Then
                        doc.Add(New Paragraph("No bets placed in this period."))
                    Else
                        For Each row As DataRow In bets.Rows
                            doc.Add(New Paragraph($"{row("bet_date")} | {row("sport")} {row("market")} | " &
                                                $"{row("selection")} @ {row("book")} | " &
                                                $"Odds: {row("odds")} | Stake: ${row("stake")} | " &
                                                $"Result: {row("result")} | P&L: ${If(IsDBNull(row("profit_loss")), 0, row("profit_loss"))}"))
                        Next
                    End If
                    doc.Add(New Paragraph(" "))

                    ' Arbitrage Section
                    doc.Add(New Paragraph("ARBITRAGE OPPORTUNITIES").SetBold().SetFontSize(14))
                    If arbs.Rows.Count = 0 Then
                        doc.Add(New Paragraph("No arbitrage opportunities detected in this period."))
                    Else
                        For Each row As DataRow In arbs.Rows
                            doc.Add(New Paragraph($"{row("detected_at")} | {row("event_id")}"))
                            doc.Add(New Paragraph($"  Side A: {row("side_a_selection")} @ {row("side_a_odds")} ({row("side_a_book")})"))
                            doc.Add(New Paragraph($"  Side B: {row("side_b_selection")} @ {row("side_b_odds")} ({row("side_b_book")})"))
                            doc.Add(New Paragraph($"  Profit: {row("profit_percentage")}% | Mode: {row("mode")} | " &
                                                $"Guaranteed: ${If(IsDBNull(row("guaranteed_profit")), 0, row("guaranteed_profit"))}"))
                            doc.Add(New Paragraph(" "))
                        Next
                    End If

                    ' Footer
                    doc.Add(New Paragraph($"Report generated by EQ12 Sports Betting Terminal v1.0")
                           .SetTextAlignment(TextAlignment.CENTER)
                           .SetFontSize(8))
                End Using
            End Using
        End Using
    End Sub

    ''' <summary>
    ''' Generate Excel workbook with multiple sheets
    ''' </summary>
    Private Shared Sub ExportExcel(path As String, periodLabel As String, bets As DataTable, arbs As DataTable)
        ExcelPackage.LicenseContext = LicenseContext.NonCommercial

        Using package As New ExcelPackage()
            ' Summary Sheet
            Dim summarySheet = package.Workbook.Worksheets.Add("Summary")
            summarySheet.Cells("A1").Value = $"EQ12 {periodLabel} Report Summary"
            summarySheet.Cells("A1").Style.Font.Size = 16
            summarySheet.Cells("A1").Style.Font.Bold = True

            summarySheet.Cells("A3").Value = "Metric"
            summarySheet.Cells("B3").Value = "Value"
            summarySheet.Cells("A3:B3").Style.Font.Bold = True

            summarySheet.Cells("A4").Value = "Total Bets"
            summarySheet.Cells("B4").Value = bets.Rows.Count

            summarySheet.Cells("A5").Value = "Arbitrage Opportunities"
            summarySheet.Cells("B5").Value = arbs.Rows.Count

            summarySheet.Cells("A6").Value = "Report Generated"
            summarySheet.Cells("B6").Value = DateTime.Now.ToString()

            ' Bets Sheet
            Dim betsSheet = package.Workbook.Worksheets.Add("Bets")
            betsSheet.Cells("A1").LoadFromDataTable(bets, True)
            betsSheet.Cells(betsSheet.Dimension.Address).AutoFitColumns()

            ' Arbitrage Sheet
            Dim arbsSheet = package.Workbook.Worksheets.Add("Arbitrage")
            arbsSheet.Cells("A1").LoadFromDataTable(arbs, True)
            arbsSheet.Cells(arbsSheet.Dimension.Address).AutoFitColumns()

            package.SaveAs(New FileInfo(path))
        End Using
    End Sub

    ''' <summary>
    ''' Generate GitHub Gist content for mobile viewing
    ''' </summary>
    Private Shared Function GenerateGistContent(periodLabel As String, startDate As DateTime, bets As DataTable, arbs As DataTable) As String
        Dim content As New StringBuilder()

        content.AppendLine($"# 📊 EQ12 {periodLabel} Report")
        content.AppendLine($"**Generated:** {DateTime.Now:yyyy-MM-dd HH:mm:ss} UTC")
        content.AppendLine($"**Period:** {startDate:yyyy-MM-dd} to {DateTime.Now:yyyy-MM-dd}")
        content.AppendLine()

        ' Quick Stats
        content.AppendLine("## 📈 Quick Stats")
        Dim totalBets = bets.Rows.Count
        Dim totalArbs = arbs.Rows.Count
        Dim totalStaked = bets.AsEnumerable().Where(Function(r) Not IsDBNull(r("stake"))).Sum(Function(r) CDbl(r("stake")))
        Dim totalPL = bets.AsEnumerable().Where(Function(r) Not IsDBNull(r("profit_loss"))).Sum(Function(r) CDbl(r("profit_loss")))
        Dim totalArbProfit = arbs.AsEnumerable().Where(Function(r) Not IsDBNull(r("guaranteed_profit"))).Sum(Function(r) CDbl(r("guaranteed_profit")))

        content.AppendLine($"- **Bets Placed:** {totalBets}")
        content.AppendLine($"- **Amount Wagered:** ${totalStaked:F2}")
        content.AppendLine($"- **Net P&L:** ${totalPL:F2}")
        content.AppendLine($"- **ROI:** {If(totalStaked > 0, (totalPL / totalStaked * 100), 0):F1}%")
        content.AppendLine($"- **Arbitrage Opportunities:** {totalArbs}")
        content.AppendLine($"- **Arbitrage Profit:** ${totalArbProfit:F2}")
        content.AppendLine()

        ' Recent Bets
        content.AppendLine("## 🎲 Recent Bets")
        If bets.Rows.Count = 0 Then
            content.AppendLine("*No bets placed in this period.*")
        Else
            content.AppendLine("| Date | Sport | Market | Selection | Book | Odds | Stake | Result | P&L |")
            content.AppendLine("|------|-------|---------|-----------|------|------|-------|--------|-----|")

            For Each row As DataRow In bets.Rows.Cast(Of DataRow).Take(10)
                content.AppendLine($"| {row("bet_date")} | {row("sport")} | {row("market")} | {row("selection")} | {row("book")} | {row("odds")} | ${row("stake")} | {row("result")} | ${If(IsDBNull(row("profit_loss")), 0, row("profit_loss"))} |")
            Next

            If bets.Rows.Count > 10 Then
                content.AppendLine($"*... and {bets.Rows.Count - 10} more bets (see full PDF/Excel report)*")
            End If
        End If
        content.AppendLine()

        ' Recent Arbitrage Opportunities
        content.AppendLine("## ⚡ Arbitrage Opportunities")
        If arbs.Rows.Count = 0 Then
            content.AppendLine("*No arbitrage opportunities detected in this period.*")
        Else
            content.AppendLine("| Time | Event | Side A | Side B | Profit % | Mode | Guaranteed |")
            content.AppendLine("|------|-------|--------|--------|----------|------|------------|")

            For Each row As DataRow In arbs.Rows.Cast(Of DataRow).Take(10)
                content.AppendLine($"| {DateTime.Parse(row("detected_at").ToString()):MM-dd HH:mm} | {row("event_id")} | {row("side_a_selection")} @ {row("side_a_odds")} ({row("side_a_book")}) | {row("side_b_selection")} @ {row("side_b_odds")} ({row("side_b_book")}) | {row("profit_percentage")}% | {row("mode")} | ${If(IsDBNull(row("guaranteed_profit")), 0, CDbl(row("guaranteed_profit"))):F2} |")
            Next

            If arbs.Rows.Count > 10 Then
                content.AppendLine($"*... and {arbs.Rows.Count - 10} more opportunities (see full PDF/Excel report)*")
            End If
        End If
        content.AppendLine()

        content.AppendLine("---")
        content.AppendLine("*Generated by EQ12 Sports Betting Terminal*")
        content.AppendLine($"*Report covers {startDate:yyyy-MM-dd} to {DateTime.Now:yyyy-MM-dd}*")

        Return content.ToString()
    End Function

    ''' <summary>
    ''' Generate email body with summary
    ''' </summary>
    Private Shared Function GenerateEmailBody(periodLabel As String, startDate As DateTime, bets As DataTable, arbs As DataTable, pdfPath As String, xlsPath As String) As String
        Dim body As New StringBuilder()

        body.AppendLine($"📊 EQ12 {periodLabel} Report - {DateTime.Now:yyyy-MM-dd}")
        body.AppendLine()
        body.AppendLine($"Report Period: {startDate:yyyy-MM-dd} to {DateTime.Now:yyyy-MM-dd}")
        body.AppendLine()

        ' Summary
        body.AppendLine("📈 SUMMARY:")
        body.AppendLine($"• Bets Placed: {bets.Rows.Count}")
        body.AppendLine($"• Arbitrage Opportunities: {arbs.Rows.Count}")

        If bets.Rows.Count > 0 Then
            Dim totalStaked = bets.AsEnumerable().Where(Function(r) Not IsDBNull(r("stake"))).Sum(Function(r) CDbl(r("stake")))
            Dim totalPL = bets.AsEnumerable().Where(Function(r) Not IsDBNull(r("profit_loss"))).Sum(Function(r) CDbl(r("profit_loss")))
            body.AppendLine($"• Total Wagered: ${totalStaked:F2}")
            body.AppendLine($"• Net P&L: ${totalPL:F2}")
            body.AppendLine($"• ROI: {If(totalStaked > 0, (totalPL / totalStaked * 100), 0):F1}%")
        End If

        If arbs.Rows.Count > 0 Then
            Dim totalArbProfit = arbs.AsEnumerable().Where(Function(r) Not IsDBNull(r("guaranteed_profit"))).Sum(Function(r) CDbl(r("guaranteed_profit")))
            body.AppendLine($"• Arbitrage Profit: ${totalArbProfit:F2}")
        End If

        body.AppendLine()
        body.AppendLine("📎 ATTACHMENTS:")
        body.AppendLine($"• PDF Report: {IO.Path.GetFileName(pdfPath)}")
        body.AppendLine($"• Excel Data: {IO.Path.GetFileName(xlsPath)}")
        body.AppendLine()
        body.AppendLine("Generated by EQ12 Sports Betting Terminal")

        Return body.ToString()
    End Function
End Class
