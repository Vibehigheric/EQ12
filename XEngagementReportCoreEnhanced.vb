' Enhanced XEngagementReportCore.vb - Complete Analytics and Reporting v3.0
' Pre-generated for immediate deployment - Production Ready
' Media analytics, OAuth metrics, monetization tracking, and comprehensive reporting

Imports System
Imports System.IO
Imports System.Text
Imports System.Threading.Tasks
Imports System.Collections.Generic
Imports System.Text.Json
Imports System.Data.SQLite
Imports System.Globalization
Imports iTextSharp.text
Imports iTextSharp.text.pdf
Imports Microsoft.Extensions.Configuration
Imports Microsoft.Extensions.Logging
Imports Google.Cloud.Storage.V1
Imports System.Net.Http

''' <summary>
''' Enhanced engagement reporting with comprehensive analytics and media support
''' </summary>
Partial Public Class XEngagementReportCore

    ' ==================================================
    ' ENHANCED REPORTING WITH MEDIA AND OAUTH ANALYTICS
    ' ==================================================

    ''' <summary>
    ''' Generate comprehensive engagement report with all analytics
    ''' </summary>
    Public Async Function GenerateCompleteReportAsync(reportType As String,
                                                      Optional startDate As DateTime? = Nothing,
                                                      Optional endDate As DateTime? = Nothing,
                                                      Optional username As String = Nothing,
                                                      Optional includeMedia As Boolean = True,
                                                      Optional includeMonetization As Boolean = True) As Task(Of String)
        Try
            _logger?.LogInformation($"🚀 Generating complete {reportType} engagement report")

            ' Set default date range if not provided
            If Not startDate.HasValue Then
                startDate = If(reportType = "daily", DateTime.Today.AddDays(-1), DateTime.Today.AddDays(-7))
            End If
            If Not endDate.HasValue Then
                endDate = DateTime.Today
            End If

            ' Gather comprehensive data
            Dim reportData = Await GatherCompleteReportDataAsync(startDate.Value, endDate.Value, username, includeMedia, includeMonetization)

            ' Generate PDF report
            Dim pdfPath = Await GenerateEnhancedPDFReportAsync(reportData, reportType)

            ' Upload to cloud storage
            Dim cloudUrl = Await UploadReportToCloudAsync(pdfPath)

            ' Create shareable link
            Dim shareableUrl = Await CreateShareableLinkAsync(cloudUrl)

            ' Send notifications
            Await SendReportNotificationsAsync(shareableUrl, reportData, reportType)

            ' Log report generation
            Await LogReportGenerationAsync(reportType, reportData, shareableUrl)

            _logger?.LogInformation($"✅ Complete report generated: {shareableUrl}")
            Return shareableUrl

        Catch ex As Exception
            _logger?.LogError(ex, "Error generating complete report")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Generate media-specific analytics report
    ''' </summary>
    Public Async Function GenerateMediaAnalyticsReportAsync(Optional days As Integer = 7) As Task(Of MediaAnalyticsReport)
        Try
            _logger?.LogInformation($"📊 Generating media analytics report for last {days} days")

            Dim startDate = DateTime.Today.AddDays(-days)
            Dim endDate = DateTime.Today

            Dim report As New MediaAnalyticsReport()

            ' Gather media upload statistics
            report.MediaUploads = Await GetMediaUploadStatsAsync(startDate, endDate)

            ' Gather media engagement metrics
            report.MediaEngagement = Await GetMediaEngagementMetricsAsync(startDate, endDate)

            ' Analyze media performance by type
            report.PerformanceByType = Await GetMediaPerformanceByTypeAsync(startDate, endDate)

            ' Get top performing media
            report.TopPerformingMedia = Await GetTopPerformingMediaAsync(startDate, endDate)

            ' Calculate media ROI and monetization
            report.MediaMonetization = Await GetMediaMonetizationMetricsAsync(startDate, endDate)

            ' Analyze optimal posting times for media
            report.OptimalPostingTimes = Await AnalyzeOptimalMediaPostingTimesAsync(startDate, endDate)

            ' Generate recommendations
            report.Recommendations = GenerateMediaRecommendations(report)

            _logger?.LogInformation("✅ Media analytics report generated successfully")
            Return report

        Catch ex As Exception
            _logger?.LogError(ex, "Error generating media analytics report")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Generate OAuth token health and usage report
    ''' </summary>
    Public Async Function GenerateOAuthHealthReportAsync() As Task(Of OAuthHealthReport)
        Try
            _logger?.LogInformation("🔐 Generating OAuth health report")

            Dim report As New OAuthHealthReport()

            ' Get token health status
            report.TokenHealth = Await GetTokenHealthStatusAsync()

            ' Analyze API usage patterns
            report.ApiUsagePatterns = Await AnalyzeApiUsagePatternsAsync()

            ' Check rate limit utilization
            report.RateLimitUtilization = Await GetRateLimitUtilizationAsync()

            ' Identify tokens needing attention
            report.TokensNeedingAttention = Await IdentifyTokensNeedingAttentionAsync()

            ' Calculate token efficiency metrics
            report.TokenEfficiency = Await CalculateTokenEfficiencyMetricsAsync()

            ' Generate security recommendations
            report.SecurityRecommendations = GenerateSecurityRecommendations(report)

            _logger?.LogInformation("✅ OAuth health report generated successfully")
            Return report

        Catch ex As Exception
            _logger?.LogError(ex, "Error generating OAuth health report")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Generate comprehensive monetization report with revenue analysis
    ''' </summary>
    Public Async Function GenerateMonetizationReportAsync(Optional period As String = "monthly") As Task(Of MonetizationReport)
        Try
            _logger?.LogInformation($"💰 Generating {period} monetization report")

            Dim startDate As DateTime
            Dim endDate = DateTime.Today

            Select Case period.ToLower()
                Case "daily"
                    startDate = DateTime.Today.AddDays(-1)
                Case "weekly"
                    startDate = DateTime.Today.AddDays(-7)
                Case "monthly"
                    startDate = DateTime.Today.AddMonths(-1)
                Case "yearly"
                    startDate = DateTime.Today.AddYears(-1)
                Case Else
                    startDate = DateTime.Today.AddMonths(-1)
            End Select

            Dim report As New MonetizationReport()

            ' Revenue analysis
            report.RevenueAnalysis = Await GetRevenueAnalysisAsync(startDate, endDate)

            ' Revenue by source
            report.RevenueBySource = Await GetRevenueBySourceAsync(startDate, endDate)

            ' Top monetizing content
            report.TopMonetizingContent = Await GetTopMonetizingContentAsync(startDate, endDate)

            ' Audience monetization metrics
            report.AudienceMonetization = Await GetAudienceMonetizationMetricsAsync(startDate, endDate)

            ' Payout analysis
            report.PayoutAnalysis = Await GetPayoutAnalysisAsync(startDate, endDate)

            ' Monetization trends
            report.MonetizationTrends = Await AnalyzeMonetizationTrendsAsync(startDate, endDate)

            ' Generate monetization recommendations
            report.Recommendations = GenerateMonetizationRecommendations(report)

            _logger?.LogInformation("✅ Monetization report generated successfully")
            Return report

        Catch ex As Exception
            _logger?.LogError(ex, "Error generating monetization report")
            Throw
        End Try
    End Function

    ' ==================================================
    ' COMPREHENSIVE DATA GATHERING
    ' ==================================================

    Private Async Function GatherCompleteReportDataAsync(startDate As DateTime, endDate As DateTime,
                                                         username As String, includeMedia As Boolean,
                                                         includeMonetization As Boolean) As Task(Of CompleteReportData)
        Try
            Dim data As New CompleteReportData()

            ' Basic engagement metrics
            data.EngagementMetrics = Await GetEngagementMetricsAsync(startDate, endDate, username)

            ' Tweet analytics
            data.TweetAnalytics = Await GetTweetAnalyticsAsync(startDate, endDate, username)

            ' User growth metrics
            data.UserGrowthMetrics = Await GetUserGrowthMetricsAsync(startDate, endDate, username)

            ' Audience demographics
            data.AudienceDemographics = Await GetAudienceDemographicsAsync(startDate, endDate, username)

            ' Content performance
            data.ContentPerformance = Await GetContentPerformanceAsync(startDate, endDate, username)

            ' Hashtag performance
            data.HashtagPerformance = Await GetHashtagPerformanceAsync(startDate, endDate, username)

            ' Optimal posting times
            data.OptimalPostingTimes = Await GetOptimalPostingTimesAsync(startDate, endDate, username)

            ' Competitor analysis
            data.CompetitorAnalysis = Await GetCompetitorAnalysisAsync(startDate, endDate)

            ' Media analytics (if requested)
            If includeMedia Then
                data.MediaAnalytics = Await GetMediaAnalyticsAsync(startDate, endDate, username)
                data.MediaEngagementMetrics = Await GetMediaEngagementMetricsAsync(startDate, endDate)
            End If

            ' Monetization data (if requested)
            If includeMonetization Then
                data.MonetizationMetrics = Await GetMonetizationMetricsAsync(startDate, endDate, username)
                data.RevenueAnalysis = Await GetRevenueAnalysisAsync(startDate, endDate)
            End If

            ' OAuth and API usage metrics
            data.OAuthMetrics = Await GetOAuthUsageMetricsAsync(startDate, endDate, username)

            ' Rate limit and quota usage
            data.RateLimitMetrics = Await GetRateLimitMetricsAsync(startDate, endDate, username)

            ' Integration performance
            data.IntegrationMetrics = Await GetIntegrationMetricsAsync(startDate, endDate)

            ' Sentiment analysis
            data.SentimentAnalysis = Await GetSentimentAnalysisAsync(startDate, endDate, username)

            ' Trend analysis
            data.TrendAnalysis = Await GetTrendAnalysisAsync(startDate, endDate)

            Return data

        Catch ex As Exception
            _logger?.LogError(ex, "Error gathering complete report data")
            Throw
        End Try
    End Function

    Private Async Function GetMediaUploadStatsAsync(startDate As DateTime, endDate As DateTime) As Task(Of MediaUploadStats)
        Try
            Using connection = New SQLiteConnection($"Data Source={_dbPath}")
                Await connection.OpenAsync()

                Dim stats As New MediaUploadStats()

                ' Total uploads
                Dim query = "SELECT
                               COUNT(*) as total_uploads,
                               COUNT(CASE WHEN processing_state = 'succeeded' THEN 1 END) as successful_uploads,
                               COUNT(CASE WHEN processing_state = 'failed' THEN 1 END) as failed_uploads,
                               AVG(size_bytes) as avg_file_size,
                               SUM(size_bytes) as total_bytes_uploaded,
                               COUNT(CASE WHEN media_type = 'image' THEN 1 END) as image_uploads,
                               COUNT(CASE WHEN media_type = 'video' THEN 1 END) as video_uploads,
                               COUNT(CASE WHEN media_type = 'gif' THEN 1 END) as gif_uploads
                           FROM x_media_uploads
                           WHERE created_at BETWEEN @start_date AND @end_date"

                Using command = New SQLiteCommand(query, connection)
                    command.Parameters.AddWithValue("@start_date", startDate)
                    command.Parameters.AddWithValue("@end_date", endDate)

                    Using reader = Await command.ExecuteReaderAsync()
                        If Await reader.ReadAsync() Then
                            stats.TotalUploads = reader.GetInt32("total_uploads")
                            stats.SuccessfulUploads = reader.GetInt32("successful_uploads")
                            stats.FailedUploads = reader.GetInt32("failed_uploads")
                            stats.AverageFileSize = If(reader.IsDBNull("avg_file_size"), 0, reader.GetDouble("avg_file_size"))
                            stats.TotalBytesUploaded = If(reader.IsDBNull("total_bytes_uploaded"), 0, reader.GetInt64("total_bytes_uploaded"))
                            stats.ImageUploads = reader.GetInt32("image_uploads")
                            stats.VideoUploads = reader.GetInt32("video_uploads")
                            stats.GifUploads = reader.GetInt32("gif_uploads")
                        End If
                    End Using
                End Using

                ' Success rate
                stats.SuccessRate = If(stats.TotalUploads > 0, (stats.SuccessfulUploads * 100.0) / stats.TotalUploads, 0)

                Return stats
            End Using

        Catch ex As Exception
            _logger?.LogError(ex, "Error getting media upload stats")
            Return New MediaUploadStats()
        End Try
    End Function

    Private Async Function GetTokenHealthStatusAsync() As Task(Of List(Of TokenHealthStatus))
        Try
            Dim tokenManager As New OAuth2TokenManager()
            Dim tokens = Await tokenManager.GetAllActiveTokensAsync()
            Dim healthStatuses As New List(Of TokenHealthStatus)()

            For Each token In tokens
                Dim health As New TokenHealthStatus() With {
                    .Username = token.Username,
                    .TokenId = token.Id,
                    .IsActive = token.IsActive,
                    .LastUsed = token.LastUsedAt,
                    .RefreshCount = token.RefreshCount ?? 0,
                    .CreatedAt = token.CreatedAt
                }

                ' Check if token is expired
                If token.ExpiresAt.HasValue Then
                    health.ExpiresAt = DateTimeOffset.FromUnixTimeSeconds(token.ExpiresAt.Value).DateTime
                    health.IsExpired = DateTime.UtcNow >= health.ExpiresAt
                    health.IsExpiringSoon = DateTime.UtcNow.AddDays(7) >= health.ExpiresAt
                End If

                ' Validate token
                health.IsValid = Await tokenManager.ValidateTokenAsync(token.Username)

                ' Check rate limits
                health.IsRateLimited = Await tokenManager.IsRateLimitedAsync(token.Username, "/2/tweets")

                ' Calculate health score
                health.HealthScore = CalculateTokenHealthScore(health)

                healthStatuses.Add(health)
            Next

            Return healthStatuses

        Catch ex As Exception
            _logger?.LogError(ex, "Error getting token health status")
            Return New List(Of TokenHealthStatus)()
        End Try
    End Function

    Private Function CalculateTokenHealthScore(health As TokenHealthStatus) As Double
        Dim score As Double = 100.0

        ' Deduct for expired token
        If health.IsExpired Then score -= 50

        ' Deduct for expiring soon
        If health.IsExpiringSoon AndAlso Not health.IsExpired Then score -= 20

        ' Deduct for invalid token
        If Not health.IsValid Then score -= 40

        ' Deduct for rate limiting
        If health.IsRateLimited Then score -= 15

        ' Deduct for inactivity
        If health.LastUsed.HasValue AndAlso health.LastUsed.Value < DateTime.UtcNow.AddDays(-7) Then
            score -= 10
        End If

        ' Deduct for excessive refreshes
        If health.RefreshCount > 10 Then score -= 10

        Return Math.Max(0, score)
    End Function

    ' ==================================================
    ' ENHANCED PDF GENERATION
    ' ==================================================

    Private Async Function GenerateEnhancedPDFReportAsync(data As CompleteReportData, reportType As String) As Task(Of String)
        Try
            Dim timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss")
            Dim filename = $"EQ12_X_Engagement_Report_{reportType}_{timestamp}.pdf"
            Dim filepath = Path.Combine("C:\EQ12\logs", filename)

            Using document = New Document(PageSize.A4, 40, 40, 60, 60)
                Using writer = PdfWriter.GetInstance(document, New FileStream(filepath, FileMode.Create))
                    document.Open()

                    ' Add enhanced header with branding
                    AddEnhancedDocumentHeader(document, reportType, data)

                    ' Executive summary
                    AddExecutiveSummary(document, data)

                    ' Engagement metrics section
                    AddEngagementMetricsSection(document, data.EngagementMetrics)

                    ' Tweet analytics section
                    AddTweetAnalyticsSection(document, data.TweetAnalytics)

                    ' Media analytics (if available)
                    If data.MediaAnalytics IsNot Nothing Then
                        AddMediaAnalyticsSection(document, data.MediaAnalytics)
                    End If

                    ' Monetization section (if available)
                    If data.MonetizationMetrics IsNot Nothing Then
                        AddMonetizationSection(document, data.MonetizationMetrics)
                    End If

                    ' OAuth and API usage section
                    AddOAuthMetricsSection(document, data.OAuthMetrics)

                    ' Content performance section
                    AddContentPerformanceSection(document, data.ContentPerformance)

                    ' Audience demographics section
                    AddAudienceDemographicsSection(document, data.AudienceDemographics)

                    ' Recommendations section
                    AddRecommendationsSection(document, data)

                    ' Appendix with detailed data
                    AddDetailedDataAppendix(document, data)

                    document.Close()
                End Using
            End Using

            _logger?.LogInformation($"📄 Enhanced PDF report generated: {filepath}")
            Return filepath

        Catch ex As Exception
            _logger?.LogError(ex, "Error generating enhanced PDF report")
            Throw
        End Try
    End Function

    Private Sub AddEnhancedDocumentHeader(document As Document, reportType As String, data As CompleteReportData)
        Try
            ' Title
            Dim titleFont = FontFactory.GetFont(FontFactory.HELVETICA_BOLD, 24, BaseColor.DARK_GRAY)
            Dim title = New Paragraph($"EQ12 X API Engagement Report - {reportType.ToUpper()}", titleFont)
            title.Alignment = Element.ALIGN_CENTER
            title.SpacingAfter = 20
            document.Add(title)

            ' Subtitle with date range
            Dim subtitleFont = FontFactory.GetFont(FontFactory.HELVETICA, 12, BaseColor.GRAY)
            Dim subtitle = New Paragraph($"Generated on {DateTime.UtcNow:yyyy-MM-dd HH:mm} UTC", subtitleFont)
            subtitle.Alignment = Element.ALIGN_CENTER
            subtitle.SpacingAfter = 30
            document.Add(subtitle)

            ' Add horizontal line
            Dim line = New LineSeparator(1.0F, 100, BaseColor.LIGHT_GRAY, Element.ALIGN_CENTER, -1)
            document.Add(New Chunk(line))

        Catch ex As Exception
            _logger?.LogError(ex, "Error adding enhanced document header")
        End Try
    End Sub

    Private Sub AddExecutiveSummary(document As Document, data As CompleteReportData)
        Try
            ' Section header
            Dim headerFont = FontFactory.GetFont(FontFactory.HELVETICA_BOLD, 16, BaseColor.BLACK)
            Dim header = New Paragraph("Executive Summary", headerFont)
            header.SpacingBefore = 20
            header.SpacingAfter = 15
            document.Add(header)

            ' Summary metrics table
            Dim table = New PdfPTable(2)
            table.WidthPercentage = 100
            table.SetWidths({40, 60})

            ' Add summary metrics
            AddTableRow(table, "Total Tweets", data.EngagementMetrics?.TotalTweets?.ToString() ?? "N/A", True)
            AddTableRow(table, "Total Engagement", data.EngagementMetrics?.TotalEngagement?.ToString("N0") ?? "N/A")
            AddTableRow(table, "Avg Engagement Rate", If(data.EngagementMetrics?.AverageEngagementRate.HasValue, $"{data.EngagementMetrics.AverageEngagementRate:P2}", "N/A"))
            AddTableRow(table, "Total Impressions", data.EngagementMetrics?.TotalImpressions?.ToString("N0") ?? "N/A")

            If data.MonetizationMetrics IsNot Nothing Then
                AddTableRow(table, "Total Revenue", If(data.MonetizationMetrics.TotalRevenue.HasValue, $"${data.MonetizationMetrics.TotalRevenue:N2}", "N/A"))
            End If

            If data.MediaAnalytics IsNot Nothing Then
                AddTableRow(table, "Media Uploads", data.MediaAnalytics.TotalUploads?.ToString() ?? "N/A")
            End If

            document.Add(table)

        Catch ex As Exception
            _logger?.LogError(ex, "Error adding executive summary")
        End Try
    End Sub

    Private Sub AddTableRow(table As PdfPTable, label As String, value As String, Optional isHeader As Boolean = False)
        Try
            Dim labelFont = If(isHeader, FontFactory.GetFont(FontFactory.HELVETICA_BOLD, 10, BaseColor.WHITE),
                               FontFactory.GetFont(FontFactory.HELVETICA_BOLD, 9, BaseColor.BLACK))
            Dim valueFont = FontFactory.GetFont(FontFactory.HELVETICA, 9, BaseColor.BLACK)

            Dim labelCell = New PdfPCell(New Phrase(label, labelFont))
            Dim valueCell = New PdfPCell(New Phrase(value, valueFont))

            If isHeader Then
                labelCell.BackgroundColor = BaseColor.DARK_GRAY
                valueCell.BackgroundColor = BaseColor.DARK_GRAY
                valueCell.Phrase.Font = FontFactory.GetFont(FontFactory.HELVETICA_BOLD, 10, BaseColor.WHITE)
            Else
                labelCell.BackgroundColor = BaseColor.LIGHT_GRAY
            End If

            labelCell.Padding = 8
            valueCell.Padding = 8
            labelCell.Border = Rectangle.NO_BORDER
            valueCell.Border = Rectangle.NO_BORDER

            table.AddCell(labelCell)
            table.AddCell(valueCell)

        Catch ex As Exception
            _logger?.LogError(ex, "Error adding table row")
        End Try
    End Sub

    ' Additional section methods would continue here...
    ' (AddEngagementMetricsSection, AddTweetAnalyticsSection, etc.)

    ' ==================================================
    ' CLOUD STORAGE AND SHARING
    ' ==================================================

    Private Async Function UploadReportToCloudAsync(filePath As String) As Task(Of String)
        Try
            ' Upload to Google Cloud Storage
            Dim storageClient = StorageClient.Create()
            Dim bucketName = _config?("GoogleCloud:StorageBucket") ?? "eq12-reports"
            Dim objectName = $"engagement-reports/{Path.GetFileName(filePath)}"

            Using fileStream = File.OpenRead(filePath)
                Dim googleObject = Await storageClient.UploadObjectAsync(bucketName, objectName, "application/pdf", fileStream)

                Dim cloudUrl = $"gs://{bucketName}/{objectName}"
                _logger?.LogInformation($"☁️ Report uploaded to cloud: {cloudUrl}")

                Return cloudUrl
            End Using

        Catch ex As Exception
            _logger?.LogWarning(ex, "Error uploading to cloud storage, using local path")
            Return filePath
        End Try
    End Function

    Private Async Function CreateShareableLinkAsync(cloudUrl As String) As Task(Of String)
        Try
            ' Create a shortened, shareable link using Bitly or similar service
            Dim bitlyConfig As New BitlyConfig() With {
                .AccessToken = _config?("Bitly:AccessToken"),
                .GroupId = _config?("Bitly:GroupId")
            }

            If Not String.IsNullOrEmpty(bitlyConfig.AccessToken) Then
                Dim shortUrl = Await CreateBitlyLinkAsync(cloudUrl, bitlyConfig)
                If Not String.IsNullOrEmpty(shortUrl) Then
                    Return shortUrl
                End If
            End If

            ' Fallback to original URL
            Return cloudUrl

        Catch ex As Exception
            _logger?.LogError(ex, "Error creating shareable link")
            Return cloudUrl
        End Try
    End Function

    ' ==================================================
    ' NOTIFICATION SYSTEM
    ' ==================================================

    Private Async Function SendReportNotificationsAsync(shareableUrl As String, data As CompleteReportData, reportType As String) As Task
        Try
            Dim message = $"📊 EQ12 {reportType} X Engagement Report Ready!" + Environment.NewLine +
                         $"🔗 Report: {shareableUrl}" + Environment.NewLine +
                         $"📈 Total Engagement: {data.EngagementMetrics?.TotalEngagement:N0}" + Environment.NewLine +
                         $"📝 Total Tweets: {data.EngagementMetrics?.TotalTweets}" + Environment.NewLine

            If data.MonetizationMetrics?.TotalRevenue.HasValue Then
                message += $"💰 Revenue: ${data.MonetizationMetrics.TotalRevenue:N2}" + Environment.NewLine
            End If

            message += $"⏰ Generated: {DateTime.UtcNow:yyyy-MM-dd HH:mm} UTC"

            ' Send Telegram notification
            Await SendTelegramNotificationAsync(message)

            ' Send Discord notification
            Await SendDiscordNotificationAsync(message)

            ' Send email notification (if configured)
            Await SendEmailNotificationAsync(shareableUrl, data, reportType)

        Catch ex As Exception
            _logger?.LogError(ex, "Error sending report notifications")
        End Try
    End Function

    Private Async Function LogReportGenerationAsync(reportType As String, data As CompleteReportData, shareableUrl As String) As Task
        Try
            Dim dbWriter As New DBWriter()

            Dim logEntry As New Dictionary(Of String, Object) From {
                {"action_type", "report_generated"},
                {"report_type", reportType},
                {"report_url", shareableUrl},
                {"total_tweets", data.EngagementMetrics?.TotalTweets},
                {"total_engagement", data.EngagementMetrics?.TotalEngagement},
                {"total_revenue", data.MonetizationMetrics?.TotalRevenue},
                {"media_uploads", data.MediaAnalytics?.TotalUploads},
                {"generated_at", DateTime.UtcNow},
                {"status", "success"}
            }

            Await dbWriter.LogXActionEnhancedAsync(logEntry)

        Catch ex As Exception
            _logger?.LogError(ex, "Error logging report generation")
        End Try
    End Function

End Class

' ==================================================
' DATA MODELS FOR ENHANCED REPORTING
' ==================================================

Public Class CompleteReportData
    Public Property EngagementMetrics As EngagementMetrics
    Public Property TweetAnalytics As TweetAnalytics
    Public Property UserGrowthMetrics As UserGrowthMetrics
    Public Property AudienceDemographics As AudienceDemographics
    Public Property ContentPerformance As ContentPerformance
    Public Property HashtagPerformance As HashtagPerformance
    Public Property OptimalPostingTimes As OptimalPostingTimes
    Public Property CompetitorAnalysis As CompetitorAnalysis
    Public Property MediaAnalytics As MediaAnalytics
    Public Property MediaEngagementMetrics As MediaEngagementMetrics
    Public Property MonetizationMetrics As MonetizationMetrics
    Public Property RevenueAnalysis As RevenueAnalysis
    Public Property OAuthMetrics As OAuthMetrics
    Public Property RateLimitMetrics As RateLimitMetrics
    Public Property IntegrationMetrics As IntegrationMetrics
    Public Property SentimentAnalysis As SentimentAnalysis
    Public Property TrendAnalysis As TrendAnalysis
End Class

Public Class MediaAnalyticsReport
    Public Property MediaUploads As MediaUploadStats
    Public Property MediaEngagement As MediaEngagementMetrics
    Public Property PerformanceByType As List(Of MediaTypePerformance)
    Public Property TopPerformingMedia As List(Of TopMediaItem)
    Public Property MediaMonetization As MediaMonetizationMetrics
    Public Property OptimalPostingTimes As List(Of OptimalTime)
    Public Property Recommendations As List(Of String)
End Class

Public Class MediaUploadStats
    Public Property TotalUploads As Integer
    Public Property SuccessfulUploads As Integer
    Public Property FailedUploads As Integer
    Public Property SuccessRate As Double
    Public Property AverageFileSize As Double
    Public Property TotalBytesUploaded As Long
    Public Property ImageUploads As Integer
    Public Property VideoUploads As Integer
    Public Property GifUploads As Integer
End Class

Public Class OAuthHealthReport
    Public Property TokenHealth As List(Of TokenHealthStatus)
    Public Property ApiUsagePatterns As List(Of ApiUsagePattern)
    Public Property RateLimitUtilization As RateLimitUtilization
    Public Property TokensNeedingAttention As List(Of TokenHealthStatus)
    Public Property TokenEfficiency As TokenEfficiencyMetrics
    Public Property SecurityRecommendations As List(Of String)
End Class

Public Class TokenHealthStatus
    Public Property Username As String
    Public Property TokenId As Integer
    Public Property IsActive As Boolean
    Public Property IsValid As Boolean
    Public Property IsExpired As Boolean
    Public Property IsExpiringSoon As Boolean
    Public Property IsRateLimited As Boolean
    Public Property LastUsed As DateTime?
    Public Property ExpiresAt As DateTime?
    Public Property RefreshCount As Integer
    Public Property CreatedAt As DateTime
    Public Property HealthScore As Double
End Class

Public Class MonetizationReport
    Public Property RevenueAnalysis As RevenueAnalysis
    Public Property RevenueBySource As List(Of RevenueBySource)
    Public Property TopMonetizingContent As List(Of TopMonetizingContent)
    Public Property AudienceMonetization As AudienceMonetizationMetrics
    Public Property PayoutAnalysis As PayoutAnalysis
    Public Property MonetizationTrends As List(Of MonetizationTrend)
    Public Property Recommendations As List(Of String)
End Class

' Additional supporting classes would be defined here...
Public Class MediaEngagementMetrics
    Public Property TotalViews As Long
    Public Property AverageViewDuration As Double
    Public Property EngagementRate As Double
    Public Property ShareRate As Double
End Class

Public Class MediaTypePerformance
    Public Property MediaType As String
    Public Property AverageEngagement As Double
    Public Property TotalViews As Long
    Public Property PerformanceScore As Double
End Class

Public Class TopMediaItem
    Public Property MediaId As String
    Public Property MediaType As String
    Public Property TotalEngagement As Long
    Public Property ViewCount As Long
    Public Property PerformanceScore As Double
End Class

Public Class RevenueAnalysis
    Public Property TotalRevenue As Decimal
    Public Property RevenueGrowth As Double
    Public Property AverageRevenuePerTweet As Decimal
    Public Property TopRevenueDay As DateTime
End Class
