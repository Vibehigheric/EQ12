' ===============================================================================
' XEngagementReportCore.vb - X/Twitter Engagement Report Generator
' Creates daily/weekly PDF reports with X engagement metrics and monetization CTAs
' ===============================================================================

Imports System.Data
Imports System.Data.SQLite
Imports System.IO
Imports iTextSharp.text
Imports iTextSharp.text.pdf
Imports Newtonsoft.Json.Linq

''' <summary>
''' Generates comprehensive X/Twitter engagement reports with monetization tracking
''' </summary>
Public Class XEngagementReportCore

    ''' <summary>
    ''' Generate a daily/weekly X Engagement PDF and return file path
    ''' </summary>
    Public Shared Function Generate(period As String, outDir As String) As String
        Try
            Directory.CreateDirectory(outDir)
            Dim timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss")
            Dim filePath = Path.Combine(outDir, $"EQ12_X_Engagement_{period}_{timestamp}.pdf")

            ' Pull x_actions data
            Dim actionData = GetXActionsData(period)
            Dim monetizationData = GetMonetizationData(period)
            Dim analyticsData = GetAnalyticsData(period)

            ' Generate PDF report
            GenerateEngagementPDF(filePath, period, actionData, monetizationData, analyticsData)

            ' Log deliverable
            DBWriter.LogDeliverable("x_engagement", $"X Engagement Report ({period})", "", "", period, filePath)

            Return filePath

        Catch ex As Exception
            Console.WriteLine($"❌ X Engagement Report Generation Error: {ex.Message}")
            Return ""
        End Try
    End Function

    Private Shared Function GetXActionsData(period As String) As DataTable
        Dim dt As New DataTable()

        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()
                Using cmd = conn.CreateCommand()
                    cmd.CommandText = If(period = "daily",
                        "SELECT * FROM x_actions WHERE ts >= datetime('now','-1 day') ORDER BY ts DESC",
                        "SELECT * FROM x_actions WHERE ts >= datetime('now','-7 day') ORDER BY ts DESC")
                    Using adapter As New SQLiteDataAdapter(cmd)
                        adapter.Fill(dt)
                    End Using
                End Using
            End Using
        Catch ex As Exception
            Console.WriteLine($"Warning: Could not retrieve X actions data: {ex.Message}")
        End Try

        Return dt
    End Function

    Private Shared Function GetMonetizationData(period As String) As DataTable
        Dim dt As New DataTable()

        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()
                Using cmd = conn.CreateCommand()
                    cmd.CommandText = If(period = "daily",
                        "SELECT * FROM x_monetization_tracking WHERE activity_date >= datetime('now','-1 day') ORDER BY activity_date DESC",
                        "SELECT * FROM x_monetization_tracking WHERE activity_date >= datetime('now','-7 day') ORDER BY activity_date DESC")
                    Using adapter As New SQLiteDataAdapter(cmd)
                        adapter.Fill(dt)
                    End Using
                End Using
            End Using
        Catch ex As Exception
            Console.WriteLine($"Warning: Could not retrieve monetization data: {ex.Message}")
        End Try

        Return dt
    End Function

    Private Shared Function GetAnalyticsData(period As String) As DataTable
        Dim dt As New DataTable()

        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()
                Using cmd = conn.CreateCommand()
                    cmd.CommandText = If(period = "daily",
                        "SELECT * FROM x_tweet_analytics WHERE posted_date >= datetime('now','-1 day') ORDER BY posted_date DESC",
                        "SELECT * FROM x_tweet_analytics WHERE posted_date >= datetime('now','-7 day') ORDER BY posted_date DESC")
                    Using adapter As New SQLiteDataAdapter(cmd)
                        adapter.Fill(dt)
                    End Using
                End Using
            End Using
        Catch ex As Exception
            Console.WriteLine($"Warning: Could not retrieve analytics data: {ex.Message}")
        End Try

        Return dt
    End Function

    Private Shared Sub GenerateEngagementPDF(filePath As String, period As String, actionData As DataTable, monetizationData As DataTable, analyticsData As DataTable)
        Using fs As New FileStream(filePath, FileMode.Create, FileAccess.Write)
            Dim doc As New Document(PageSize.A4, 36, 36, 36, 36)
            PdfWriter.GetInstance(doc, fs)
            doc.Open()

            ' Define fonts
            Dim titleFont = FontFactory.GetFont("Arial", 18, Font.BOLD, BaseColor.DARK_GRAY)
            Dim headerFont = FontFactory.GetFont("Arial", 14, Font.BOLD, BaseColor.BLACK)
            Dim normalFont = FontFactory.GetFont("Arial", 11, BaseColor.BLACK)
            Dim boldFont = FontFactory.GetFont("Arial", 11, Font.BOLD, BaseColor.BLACK)
            Dim monoFont = FontFactory.GetFont("Courier", 9, BaseColor.DARK_GRAY)

            ' Title and header
            doc.Add(New Paragraph($"EQ12 X Engagement Report — {period.ToUpper()}", titleFont))
            doc.Add(New Paragraph($"Generated: {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC", normalFont))
            doc.Add(New Paragraph(" "))

            ' Calculate aggregate metrics
            Dim totalPosts = actionData.AsEnumerable().Count(Function(r) r.Field(Of String)("action") = "post")
            Dim totalThreads = actionData.AsEnumerable().Count(Function(r) r.Field(Of String)("action") = "thread")
            Dim totalThreadTweets = actionData.AsEnumerable().
                Where(Function(r) r.Field(Of String)("action") = "thread").
                Sum(Function(r) If(IsDBNull(r("count")), 0, Convert.ToInt32(r("count"))))
            Dim totalSearches = actionData.AsEnumerable().Count(Function(r) r.Field(Of String)("action") = "search")
            Dim totalSearchHits = actionData.AsEnumerable().
                Where(Function(r) r.Field(Of String)("action") = "search").
                Sum(Function(r) If(IsDBNull(r("count")), 0, Convert.ToInt32(r("count"))))

            ' Executive Summary
            doc.Add(New Paragraph("📊 EXECUTIVE SUMMARY", headerFont))
            doc.Add(New Paragraph($"Posts: {totalPosts}  |  Threads: {totalThreads} ({totalThreadTweets} tweets)  |  Searches: {totalSearches} ({totalSearchHits} results)", boldFont))
            doc.Add(New Paragraph(" "))

            ' Monetization metrics
            If monetizationData.Rows.Count > 0 Then
                Dim totalRevenue = monetizationData.AsEnumerable().Sum(Function(r) If(IsDBNull(r("revenue_generated")), 0.0, Convert.ToDouble(r("revenue_generated"))))
                Dim totalClicks = monetizationData.AsEnumerable().Sum(Function(r) If(IsDBNull(r("affiliate_clicks")), 0, Convert.ToInt32(r("affiliate_clicks"))))
                Dim averageROI = monetizationData.AsEnumerable().Where(Function(r) Not IsDBNull(r("roi"))).Average(Function(r) Convert.ToDouble(r("roi")))

                doc.Add(New Paragraph("💰 MONETIZATION METRICS", headerFont))
                doc.Add(New Paragraph($"Revenue Generated: {totalRevenue:C2}", normalFont))
                doc.Add(New Paragraph($"Affiliate Clicks: {totalClicks}", normalFont))
                doc.Add(New Paragraph($"Average ROI: {averageROI:F2}%", normalFont))
                doc.Add(New Paragraph(" "))
            End If

            ' Engagement analytics
            If analyticsData.Rows.Count > 0 Then
                Dim averageEngagement = analyticsData.AsEnumerable().Where(Function(r) Not IsDBNull(r("engagement_rate"))).Average(Function(r) Convert.ToDouble(r("engagement_rate")))
                Dim totalLikes = analyticsData.AsEnumerable().Sum(Function(r) If(IsDBNull(r("likes")), 0, Convert.ToInt32(r("likes"))))
                Dim totalRetweets = analyticsData.AsEnumerable().Sum(Function(r) If(IsDBNull(r("retweets")), 0, Convert.ToInt32(r("retweets"))))
                Dim totalImpressions = analyticsData.AsEnumerable().Sum(Function(r) If(IsDBNull(r("impressions")), 0, Convert.ToInt64(r("impressions"))))

                doc.Add(New Paragraph("🎯 ENGAGEMENT ANALYTICS", headerFont))
                doc.Add(New Paragraph($"Average Engagement Rate: {averageEngagement:F2}%", normalFont))
                doc.Add(New Paragraph($"Total Likes: {totalLikes:N0}", normalFont))
                doc.Add(New Paragraph($"Total Retweets: {totalRetweets:N0}", normalFont))
                doc.Add(New Paragraph($"Total Impressions: {totalImpressions:N0}", normalFont))
                doc.Add(New Paragraph(" "))
            End If

            ' Recent activity details
            doc.Add(New Paragraph("📝 RECENT ACTIVITY", headerFont))

            If actionData.Rows.Count > 0 Then
                For Each row As DataRow In actionData.Rows.Cast(Of DataRow).Take(20) ' Top 20 most recent
                    Dim actionType = row("action").ToString().ToUpper()
                    Dim timestamp = row("ts").ToString()
                    Dim refId = If(IsDBNull(row("ref_id")), "", row("ref_id").ToString())
                    Dim count = If(IsDBNull(row("count")), 0, Convert.ToInt32(row("count")))
                    Dim status = row("status").ToString().ToUpper()

                    doc.Add(New Paragraph($"[{timestamp}] {actionType}", boldFont))
                    doc.Add(New Paragraph($"   ID: {refId}  |  Count: {count}  |  Status: {status}", monoFont))

                    Dim payload = If(IsDBNull(row("payload")), "", row("payload").ToString())
                    If Not String.IsNullOrWhiteSpace(payload) Then
                        doc.Add(New Paragraph($"   Content: {TruncateString(payload, 120)}", monoFont))
                    End If

                    Dim details = If(IsDBNull(row("details")), "", row("details").ToString())
                    If Not String.IsNullOrWhiteSpace(details) Then
                        doc.Add(New Paragraph($"   Details: {TruncateString(details, 140)}", monoFont))
                    End If

                    doc.Add(New Paragraph(" "))
                Next
            Else
                doc.Add(New Paragraph("No X/Twitter activity recorded in this period.", normalFont))
            End If

            ' Monetization CTAs
            doc.Add(New Paragraph("💎 MONETIZATION OPPORTUNITIES", headerFont))
            doc.Add(New Paragraph("• Bet Now: Premium arbitrage alerts with affiliate shortlinks", normalFont))
            doc.Add(New Paragraph("• Subscribe: Premium Telegram channel for instant notifications", normalFont))
            doc.Add(New Paragraph("• Download: Exclusive betting intelligence reports and analysis", normalFont))
            doc.Add(New Paragraph("• Follow: Real-time injury and line movement alerts via X/Twitter", normalFont))
            doc.Add(New Paragraph(" "))

            ' Performance recommendations
            doc.Add(New Paragraph("🚀 PERFORMANCE RECOMMENDATIONS", headerFont))

            If totalPosts < 5 Then
                doc.Add(New Paragraph("📈 Increase posting frequency: Aim for 5-10 posts per day for better engagement", normalFont))
            End If

            If totalSearches < 10 Then
                doc.Add(New Paragraph("🔍 Enhance search activity: More frequent searches = better betting intelligence", normalFont))
            End If

            If totalThreads = 0 Then
                doc.Add(New Paragraph("🧵 Consider thread content: Threads generate higher engagement than single posts", normalFont))
            End If

            doc.Add(New Paragraph("✅ Continue leveraging real-time betting intelligence for maximum ROI", normalFont))
            doc.Add(New Paragraph(" "))

            ' Footer
            doc.Add(New Paragraph($"Generated by EQ12 X Engagement System | {DateTime.UtcNow:yyyy-MM-dd}",
                FontFactory.GetFont("Arial", 8, Font.ITALIC, BaseColor.GRAY)))

            doc.Close()
        End Using
    End Sub

    Private Shared Function TruncateString(s As String, maxLength As Integer) As String
        If String.IsNullOrEmpty(s) Then Return s
        If s.Length <= maxLength Then Return s
        Return s.Substring(0, maxLength) & "…"
    End Function

    ''' <summary>
    ''' Generate and upload X engagement report with full monetization pipeline
    ''' </summary>
    Public Shared Function GenerateAndShare(period As String, Optional uploadToGCS As Boolean = True, Optional sendAlerts As Boolean = True) As String
        Try
            Dim outDir = "C:\EQ12\Reports"
            Dim pdfPath = Generate(period, outDir)

            If String.IsNullOrEmpty(pdfPath) Then
                Return ""
            End If

            Dim sharedUrl As String = pdfPath
            Dim bitlyUrl As String = ""

            ' Upload to GCS if configured
            If uploadToGCS AndAlso Config("gcp") IsNot Nothing Then
                Try
                    ' GCS upload implementation would go here
                    ' For now, use local file path
                    Console.WriteLine($"📤 GCS upload configured but not implemented yet. Using local path: {pdfPath}")
                Catch ex As Exception
                    Console.WriteLine($"Warning: GCS upload failed: {ex.Message}")
                End Try
            End If

            ' Shorten with Bitly if configured
            If Config("bitly") IsNot Nothing AndAlso Not String.IsNullOrEmpty(Config("bitly")("token")?.ToString()) Then
                Try
                    bitlyUrl = BitlyHelper.Shorten(Config("bitly")("token").ToString(), sharedUrl)
                    If Not String.IsNullOrEmpty(bitlyUrl) Then
                        sharedUrl = bitlyUrl
                    End If
                Catch ex As Exception
                    Console.WriteLine($"Warning: Bitly shortening failed: {ex.Message}")
                End Try
            End If

            ' Send alerts if configured
            If sendAlerts Then
                Try
                    Dim alertMessage = $"📊 EQ12 X Engagement Report ({period.ToUpper()}) Ready!{vbNewLine}" &
                                     $"📈 View Report: {sharedUrl}{vbNewLine}" &
                                     $"🐦 Track your Twitter performance and monetization opportunities{vbNewLine}" &
                                     $"#EQ12 #XEngagement #TwitterAnalytics #BettingIntelligence"

                    ' Telegram alert
                    If Config("telegram") IsNot Nothing AndAlso Not String.IsNullOrEmpty(Config("telegram")("token")?.ToString()) Then
                        Alerts.Telegram(Config("telegram")("token").ToString(), Config("telegram")("chat_id").ToString(), alertMessage)
                    End If

                    ' Discord alert
                    If Config("discord") IsNot Nothing AndAlso Not String.IsNullOrEmpty(Config("discord")("webhook")?.ToString()) Then
                        Alerts.Discord(Config("discord")("webhook").ToString(), alertMessage)
                    End If

                Catch ex As Exception
                    Console.WriteLine($"Warning: Alert sending failed: {ex.Message}")
                End Try
            End If

            ' Log deliverable with final URL
            DBWriter.LogDeliverable("x_engagement", $"X Engagement Report ({period})", sharedUrl, "", period, pdfPath)

            Return sharedUrl

        Catch ex As Exception
            Console.WriteLine($"❌ X Engagement Report Generation and Sharing Error: {ex.Message}")
            Return ""
        End Try
    End Function
End Class
