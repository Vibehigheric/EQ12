' ===============================================================================
' Integration Report Generator - Automated PDF Reports with Monetization
' Creates daily/weekly integration reports with trigger recommendations
' ===============================================================================

Imports System.Data
Imports iTextSharp.text
Imports iTextSharp.text.pdf
Imports System.IO
Imports System.Data.SQLite

Public Class IntegrationReportCore

    Public Shared Function GenerateIntegrationReport(period As String, Optional outDir As String = "C:\EQ12\Reports") As String
        Try
            Directory.CreateDirectory(outDir)
            Dim timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss")
            Dim filePath = Path.Combine(outDir, $"EQ12_Integration_Report_{period}_{timestamp}.pdf")

            ' Gather data for report
            Dim reportData = GatherReportData(period)

            ' Generate PDF report
            GeneratePDFReport(filePath, period, reportData)

            ' Generate monetization recommendations
            Dim recommendations = GenerateMonetizationRecommendations(reportData)

            ' Send alerts with report and recommendations
            SendReportNotifications(filePath, recommendations, period)

            Return filePath

        Catch ex As Exception
            Console.WriteLine($"❌ Report Generation Error: {ex.Message}")
            Return ""
        End Try
    End Function

    Private Shared Function GatherReportData(period As String) As IntegrationReportData
        Dim data As New IntegrationReportData()

        Try
            Using conn As New SQLiteConnection("Data Source=C:\EQ12\Data\bankroll.db")
                conn.Open()

                ' Get integration summary
                data.Integrations = GetIntegrationSummary(conn, period)
                data.MonetizationTriggers = GetMonetizationTriggers(conn, period)
                data.RepoAnalytics = GetRepoAnalytics(conn, period)

                ' Get X/Twitter engagement metrics
                data.XEngagementMetrics = GetXEngagementMetrics(conn, period)
                data.ApiUsage = GetApiUsage(conn, period)
                data.RevenueMetrics = GetRevenueMetrics(conn, period)
                data.PremiumFeatures = GetPremiumFeatureUsage(conn, period)

            End Using

        Catch ex As Exception
            Console.WriteLine($"❌ Data Gathering Error: {ex.Message}")
        End Try

        Return data
    End Function

    Private Shared Function GetIntegrationSummary(conn As SQLiteConnection, period As String) As List(Of IntegrationSummary)
        Dim results As New List(Of IntegrationSummary)

        Using cmd = conn.CreateCommand()
            cmd.CommandText = If(period = "daily",
                "SELECT module, category, COUNT(*) as count, SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as successful, AVG(profit_potential) as avg_profit FROM integration_log WHERE ts >= datetime('now','-1 day') GROUP BY module, category",
                "SELECT module, category, COUNT(*) as count, SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) as successful, AVG(profit_potential) as avg_profit FROM integration_log WHERE ts >= datetime('now','-7 day') GROUP BY module, category")

            Using reader = cmd.ExecuteReader()
                While reader.Read()
                    results.Add(New IntegrationSummary With {
                        .Module = reader("module").ToString(),
                        .Category = reader("category").ToString(),
                        .TotalIntegrations = Convert.ToInt32(reader("count")),
                        .SuccessfulIntegrations = Convert.ToInt32(reader("successful")),
                        .AverageProfitPotential = If(reader("avg_profit") Is DBNull.Value, 0.0, Convert.ToDouble(reader("avg_profit")))
                    })
                End While
            End Using
        End Using

        Return results
    End Function

    Private Shared Function GetMonetizationTriggers(conn As SQLiteConnection, period As String) As List(Of MonetizationTriggerSummary)
        Dim results As New List(Of MonetizationTriggerSummary)

        Using cmd = conn.CreateCommand()
            cmd.CommandText = If(period = "daily",
                "SELECT trigger_type, category, COUNT(*) as count, AVG(revenue_boost) as avg_boost FROM monetization_triggers WHERE ts >= datetime('now','-1 day') GROUP BY trigger_type, category",
                "SELECT trigger_type, category, COUNT(*) as count, AVG(revenue_boost) as avg_boost FROM monetization_triggers WHERE ts >= datetime('now','-7 day') GROUP BY trigger_type, category")

            Using reader = cmd.ExecuteReader()
                While reader.Read()
                    results.Add(New MonetizationTriggerSummary With {
                        .TriggerType = reader("trigger_type").ToString(),
                        .Category = reader("category").ToString(),
                        .ActivationCount = Convert.ToInt32(reader("count")),
                        .AverageRevenueBoost = If(reader("avg_boost") Is DBNull.Value, 0.0, Convert.ToDouble(reader("avg_boost")))
                    })
                End While
            End Using
        End Using

        Return results
    End Function

    Private Shared Function GetRepoAnalytics(conn As SQLiteConnection, period As String) As RepoAnalytics
        Dim analytics As New RepoAnalytics()

        Using cmd = conn.CreateCommand()
            cmd.CommandText = "SELECT COUNT(*) FROM repo_analysis_cache"
            analytics.TotalReposAnalyzed = Convert.ToInt32(cmd.ExecuteScalar())

            cmd.CommandText = "SELECT COUNT(*) FROM repo_analysis_cache WHERE monetization_potential > 0"
            analytics.HighValueRepos = Convert.ToInt32(cmd.ExecuteScalar())

            cmd.CommandText = "SELECT AVG(analysis_score) FROM repo_analysis_cache"
            Dim avgScore = cmd.ExecuteScalar()
            analytics.AverageAnalysisScore = If(avgScore Is DBNull.Value, 0.0, Convert.ToDouble(avgScore))
        End Using

        Return analytics
    End Function

    Private Shared Function GetApiUsage(conn As SQLiteConnection, period As String) As ApiUsageMetrics
        Dim metrics As New ApiUsageMetrics()

        Using cmd = conn.CreateCommand()
            cmd.CommandText = If(period = "daily",
                "SELECT COUNT(*) as total_queries, AVG(api_quota_used) as avg_quota, SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) as successful FROM github_query_log WHERE ts >= datetime('now','-1 day')",
                "SELECT COUNT(*) as total_queries, AVG(api_quota_used) as avg_quota, SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) as successful FROM github_query_log WHERE ts >= datetime('now','-7 day')")

            Using reader = cmd.ExecuteReader()
                If reader.Read() Then
                    metrics.TotalQueries = Convert.ToInt32(reader("total_queries"))
                    metrics.AverageQuotaUsed = If(reader("avg_quota") Is DBNull.Value, 0.0, Convert.ToDouble(reader("avg_quota")))
                    metrics.SuccessfulQueries = Convert.ToInt32(reader("successful"))
                End If
            End Using
        End Using

        Return metrics
    End Function

    Private Shared Function GetXEngagementMetrics(conn As SQLiteConnection, period As String) As XEngagementMetrics
        Dim metrics As New XEngagementMetrics()

        Dim timeFilter = If(period = "daily", "-1 day", "-7 day")

        Try
            ' Get tweet posting metrics
            Using cmd = conn.CreateCommand()
                cmd.CommandText = $"SELECT COUNT(*) FROM integration_log WHERE module='XClient' AND action='post' AND timestamp >= datetime('now', '{timeFilter}')"
                metrics.TweetsPosted = Convert.ToInt32(cmd.ExecuteScalar())
            End Using

            ' Get tweet search metrics
            Using cmd = conn.CreateCommand()
                cmd.CommandText = $"SELECT COUNT(*) FROM integration_log WHERE module='XClient' AND action='search' AND timestamp >= datetime('now', '{timeFilter}')"
                metrics.SearchesPerformed = Convert.ToInt32(cmd.ExecuteScalar())
            End Using

            ' Get betting intelligence extractions
            Using cmd = conn.CreateCommand()
                cmd.CommandText = $"SELECT COUNT(*) FROM integration_log WHERE module='XClient' AND action='intelligence_extraction' AND timestamp >= datetime('now', '{timeFilter}')"
                metrics.IntelligenceExtractions = Convert.ToInt32(cmd.ExecuteScalar())
            End Using

            ' Get arbitrage alerts posted
            Using cmd = conn.CreateCommand()
                cmd.CommandText = $"SELECT COUNT(*) FROM integration_log WHERE module='XClient' AND action='arbitrage_alert' AND timestamp >= datetime('now', '{timeFilter}')"
                metrics.ArbitrageAlertsPosted = Convert.ToInt32(cmd.ExecuteScalar())
            End Using

            ' Get engagement rate (likes, retweets, replies from posted content)
            Using cmd = conn.CreateCommand()
                cmd.CommandText = $"SELECT AVG(engagement_rate) FROM x_tweet_analytics WHERE posted_date >= datetime('now', '{timeFilter}')"
                Dim engagement = cmd.ExecuteScalar()
                metrics.AverageEngagementRate = If(engagement Is DBNull.Value, 0.0, Convert.ToDouble(engagement))
            End Using

            ' Get monetization ROI from X activities
            Using cmd = conn.CreateCommand()
                cmd.CommandText = $"SELECT SUM(revenue_generated) FROM x_monetization_tracking WHERE activity_date >= datetime('now', '{timeFilter}')"
                Dim revenue = cmd.ExecuteScalar()
                metrics.MonetizationROI = If(revenue Is DBNull.Value, 0.0, Convert.ToDouble(revenue))
            End Using

            ' Get API usage efficiency
            Using cmd = conn.CreateCommand()
                cmd.CommandText = $"SELECT COUNT(*) FROM integration_log WHERE module='XClient' AND status='success' AND timestamp >= datetime('now', '{timeFilter}')"
                Dim successCount = Convert.ToInt32(cmd.ExecuteScalar())
                cmd.CommandText = $"SELECT COUNT(*) FROM integration_log WHERE module='XClient' AND timestamp >= datetime('now', '{timeFilter}')"
                Dim totalCount = Convert.ToInt32(cmd.ExecuteScalar())
                metrics.ApiSuccessRate = If(totalCount > 0, (successCount / totalCount) * 100, 0.0)
            End Using

            ' Get repository integrations from X API sources
            Using cmd = conn.CreateCommand()
                cmd.CommandText = $"SELECT COUNT(*) FROM integration_log WHERE module='XApiGitHubIntegrator' AND timestamp >= datetime('now', '{timeFilter}')"
                metrics.XApiReposIntegrated = Convert.ToInt32(cmd.ExecuteScalar())
            End Using

        Catch ex As Exception
            ' Log error but continue with partial metrics
            Console.WriteLine($"Warning: Could not gather some X engagement metrics: {ex.Message}")
        End Try

        Return metrics
    End Function

    Private Shared Function GetRevenueMetrics(conn As SQLiteConnection, period As String) As RevenueMetrics
        ' Placeholder for revenue tracking integration
        Return New RevenueMetrics With {
            .EstimatedRevenue = 0,
            .ConversionRate = 0,
            .PremiumUpgrades = 0
        }
    End Function

    Private Shared Function GetPremiumFeatureUsage(conn As SQLiteConnection, period As String) As List(Of PremiumFeatureUsage)
        ' Placeholder for premium feature tracking
        Return New List(Of PremiumFeatureUsage)()
    End Function

    Private Shared Sub GeneratePDFReport(filePath As String, period As String, data As IntegrationReportData)
        Using fs As New FileStream(filePath, FileMode.Create, FileAccess.Write)
            Dim doc As New Document(PageSize.A4, 36, 36, 36, 36)
            Dim writer = PdfWriter.GetInstance(doc, fs)
            doc.Open()

            ' Report Header
            Dim titleFont = FontFactory.GetFont("Arial", 20, Font.BOLD, BaseColor.DARK_GRAY)
            Dim headerFont = FontFactory.GetFont("Arial", 14, Font.BOLD, BaseColor.BLUE)
            Dim normalFont = FontFactory.GetFont("Arial", 10, Font.NORMAL)
            Dim boldFont = FontFactory.GetFont("Arial", 10, Font.BOLD)

            doc.Add(New Paragraph($"EQ12 GitHub Integration Report", titleFont))
            doc.Add(New Paragraph($"Period: {period.ToUpper()} - {DateTime.UtcNow:yyyy-MM-dd HH:mm}", normalFont))
            doc.Add(New Paragraph(" "))

            ' Executive Summary
            doc.Add(New Paragraph("📊 EXECUTIVE SUMMARY", headerFont))
            doc.Add(New Paragraph($"Total Integrations: {data.Integrations.Sum(Function(i) i.TotalIntegrations)}", boldFont))
            doc.Add(New Paragraph($"Successful Integrations: {data.Integrations.Sum(Function(i) i.SuccessfulIntegrations)}", boldFont))
            doc.Add(New Paragraph($"Success Rate: {If(data.Integrations.Sum(Function(i) i.TotalIntegrations) > 0, (data.Integrations.Sum(Function(i) i.SuccessfulIntegrations) / data.Integrations.Sum(Function(i) i.TotalIntegrations) * 100), 0):F1}%", boldFont))
            doc.Add(New Paragraph($"Monetization Triggers Activated: {data.MonetizationTriggers.Sum(Function(m) m.ActivationCount)}", boldFont))
            doc.Add(New Paragraph(" "))

            ' Integration Details
            doc.Add(New Paragraph("🔧 INTEGRATION BREAKDOWN", headerFont))
            For Each integration In data.Integrations
                doc.Add(New Paragraph($"• {integration.Module} ({integration.Category}): {integration.SuccessfulIntegrations}/{integration.TotalIntegrations} successful", normalFont))
                If integration.AverageProfitPotential > 0 Then
                    doc.Add(New Paragraph($"  💰 Avg Profit Potential: {integration.AverageProfitPotential:C2}", normalFont))
                End If
            Next
            doc.Add(New Paragraph(" "))

            ' Monetization Analysis
            doc.Add(New Paragraph("💰 MONETIZATION ANALYSIS", headerFont))
            If data.MonetizationTriggers.Count > 0 Then
                For Each trigger In data.MonetizationTriggers
                    doc.Add(New Paragraph($"🚀 {trigger.TriggerType} ({trigger.Category})", boldFont))
                    doc.Add(New Paragraph($"   Activations: {trigger.ActivationCount}", normalFont))
                    doc.Add(New Paragraph($"   Avg Revenue Boost: {trigger.AverageRevenueBoost:C2}", normalFont))
                Next
            Else
                doc.Add(New Paragraph("No monetization triggers activated in this period.", normalFont))
            End If
            doc.Add(New Paragraph(" "))

            ' Repository Analytics
            doc.Add(New Paragraph("📈 REPOSITORY ANALYTICS", headerFont))
            doc.Add(New Paragraph($"Total Repos Analyzed: {data.RepoAnalytics.TotalReposAnalyzed}", normalFont))
            doc.Add(New Paragraph($"High-Value Repos: {data.RepoAnalytics.HighValueRepos}", normalFont))
            doc.Add(New Paragraph($"Average Analysis Score: {data.RepoAnalytics.AverageAnalysisScore:F2}", normalFont))
            doc.Add(New Paragraph(" "))

            ' API Usage
            doc.Add(New Paragraph("🔍 API USAGE METRICS", headerFont))
            doc.Add(New Paragraph($"GitHub Queries: {data.ApiUsage.TotalQueries}", normalFont))
            doc.Add(New Paragraph($"Success Rate: {If(data.ApiUsage.TotalQueries > 0, (data.ApiUsage.SuccessfulQueries / data.ApiUsage.TotalQueries * 100), 0):F1}%", normalFont))
            doc.Add(New Paragraph($"Average Quota Used: {data.ApiUsage.AverageQuotaUsed:F0}", normalFont))
            doc.Add(New Paragraph(" "))

            ' X/Twitter Engagement Metrics
            doc.Add(New Paragraph("🐦 X/TWITTER ENGAGEMENT METRICS", headerFont))
            If data.XEngagementMetrics IsNot Nothing Then
                doc.Add(New Paragraph($"Tweets Posted: {data.XEngagementMetrics.TweetsPosted}", normalFont))
                doc.Add(New Paragraph($"Searches Performed: {data.XEngagementMetrics.SearchesPerformed}", normalFont))
                doc.Add(New Paragraph($"Betting Intelligence Extractions: {data.XEngagementMetrics.IntelligenceExtractions}", normalFont))
                doc.Add(New Paragraph($"Arbitrage Alerts Posted: {data.XEngagementMetrics.ArbitrageAlertsPosted}", normalFont))
                doc.Add(New Paragraph($"Average Engagement Rate: {data.XEngagementMetrics.AverageEngagementRate:F2}%", normalFont))
                doc.Add(New Paragraph($"X API Success Rate: {data.XEngagementMetrics.ApiSuccessRate:F1}%", normalFont))
                doc.Add(New Paragraph($"Monetization ROI: {data.XEngagementMetrics.MonetizationROI:C2}", normalFont))
                doc.Add(New Paragraph($"X API Repos Integrated: {data.XEngagementMetrics.XApiReposIntegrated}", normalFont))

                ' X Engagement Performance Indicators
                Dim performanceColor = If(data.XEngagementMetrics.AverageEngagementRate > 2.0, "🟢", If(data.XEngagementMetrics.AverageEngagementRate > 1.0, "🟡", "🔴"))
                doc.Add(New Paragraph($"{performanceColor} X Performance: {If(data.XEngagementMetrics.AverageEngagementRate > 2.0, "Excellent", If(data.XEngagementMetrics.AverageEngagementRate > 1.0, "Good", "Needs Improvement"))}", boldFont))
            Else
                doc.Add(New Paragraph("X/Twitter integration not yet active.", normalFont))
            End If
            doc.Add(New Paragraph(" "))

            ' Recommendations
            AddRecommendationsSection(doc, data, headerFont, normalFont, boldFont)

            doc.Close()
        End Using
    End Sub

    Private Shared Sub AddRecommendationsSection(doc As Document, data As IntegrationReportData, headerFont As Font, normalFont As Font, boldFont As Font)
        doc.Add(New Paragraph("🎯 MONETIZATION RECOMMENDATIONS", headerFont))

        Dim recommendations = GenerateMonetizationRecommendations(data)

        If recommendations.Count > 0 Then
            For Each rec In recommendations
                doc.Add(New Paragraph($"• {rec.Title}", boldFont))
                doc.Add(New Paragraph($"  {rec.Description}", normalFont))
                doc.Add(New Paragraph($"  Expected ROI: {rec.ExpectedROI:C0}/month", normalFont))
                doc.Add(New Paragraph($"  Priority: {rec.Priority}", normalFont))
                doc.Add(New Paragraph(" "))
            Next
        Else
            doc.Add(New Paragraph("System performing optimally. Continue current integration strategy.", normalFont))
        End If

        ' Auto-activation thresholds
        doc.Add(New Paragraph("⚡ AUTO-ACTIVATION THRESHOLDS", headerFont))
        doc.Add(New Paragraph("• Twitter Automation: 10+ arbitrage opportunities/week", normalFont))
        doc.Add(New Paragraph("• Premium Features: 5+ successful integrations/category", normalFont))
        doc.Add(New Paragraph("• Enterprise Upgrade: $5000+ monthly revenue", normalFont))
        doc.Add(New Paragraph("• Community Features: 100+ active users", normalFont))
    End Sub

    Private Shared Function GenerateMonetizationRecommendations(data As IntegrationReportData) As List(Of MonetizationRecommendation)
        Dim recommendations As New List(Of MonetizationRecommendation)

        ' Analyze data and generate specific recommendations
        Dim totalIntegrations = data.Integrations.Sum(Function(i) i.TotalIntegrations)
        Dim arbitrageIntegrations = data.Integrations.Where(Function(i) i.Category = "arbitrage").Sum(Function(i) i.SuccessfulIntegrations)
        Dim kellyIntegrations = data.Integrations.Where(Function(i) i.Category = "kelly").Sum(Function(i) i.SuccessfulIntegrations)

        ' Twitter automation recommendation
        If arbitrageIntegrations >= 3 AndAlso Not HasActiveTwitterBot() Then
            recommendations.Add(New MonetizationRecommendation With {
                .Title = "Activate Twitter Arbitrage Bot",
                .Description = "High arbitrage integration volume detected. Activate automated Twitter alerts to monetize opportunities through affiliate links.",
                .ExpectedROI = 3000,
                .Priority = "HIGH",
                .ImplementationCost = 200
            })
        End If

        ' Premium Kelly features
        If kellyIntegrations >= 5 AndAlso Not HasPremiumKellyFeatures() Then
            recommendations.Add(New MonetizationRecommendation With {
                .Title = "Activate Premium Kelly Calculator",
                .Description = "Multiple Kelly implementations integrated. Enable advanced bankroll management features for premium subscribers.",
                .ExpectedROI = 5000,
                .Priority = "MEDIUM",
                .ImplementationCost = 0
            })
        End If

        ' GitHub automation scaling
        If totalIntegrations >= 10 Then
            recommendations.Add(New MonetizationRecommendation With {
                .Title = "Scale GitHub Automation",
                .Description = "High integration volume indicates strong automation pipeline. Consider increasing API limits and adding more repo sources.",
                .ExpectedROI = 8000,
                .Priority = "MEDIUM",
                .ImplementationCost = 1000
            })
        End If

        Return recommendations.OrderByDescending(Function(r) r.ExpectedROI).ToList()
    End Function

    Private Shared Sub SendReportNotifications(filePath As String, recommendations As List(Of MonetizationRecommendation), period As String)
        Try
            ' Generate Bitly link for report
            Dim reportUrl = BitlyHelper.UploadAndShorten(Config("bitly")("token"), filePath)

            ' Create alert message
            Dim alertMsg = $"📊 EQ12 Integration Report ({period.ToUpper()}) Ready{vbNewLine}" &
                          $"📈 View Report: {reportUrl}{vbNewLine}"

            If recommendations.Count > 0 Then
                alertMsg &= $"💡 Top Recommendation: {recommendations.First().Title}{vbNewLine}"
                alertMsg &= $"💰 Potential ROI: {recommendations.First().ExpectedROI:C0}/month{vbNewLine}"
            End If

            alertMsg &= $"#EQ12 #Integration #Monetization #Report"

            ' Send to Telegram
            Alerts.Telegram(Config("telegram")("token"), Config("telegram")("chat_id"), alertMsg)

            ' Send to Discord if configured
            If Config("discord")("enabled") = "true" Then
                Alerts.Discord(Config("discord")("webhook"), alertMsg)
            End If

            ' Auto-implement high-priority recommendations
            For Each rec In recommendations.Where(Function(r) r.Priority = "HIGH")
                Console.WriteLine($"🚀 AUTO-IMPLEMENTING: {rec.Title}")
                ' Implementation would happen here based on recommendation type
            Next

        Catch ex As Exception
            Console.WriteLine($"❌ Notification Error: {ex.Message}")
        End Try
    End Sub

    ' Helper methods for checking current system state
    Private Shared Function HasActiveTwitterBot() As Boolean
        ' Check if Twitter automation is already active
        Return False ' Placeholder
    End Function

    Private Shared Function HasPremiumKellyFeatures() As Boolean
        ' Check if premium Kelly features are enabled
        Return False ' Placeholder
    End Function
End Class

' ===============================================================================
' Supporting Data Classes for Report Generation
' ===============================================================================

Public Class IntegrationReportData
    Public Property Integrations As New List(Of IntegrationSummary)()
    Public Property MonetizationTriggers As New List(Of MonetizationTriggerSummary)()
    Public Property RepoAnalytics As New RepoAnalytics()
    Public Property ApiUsage As New ApiUsageMetrics()
    Public Property RevenueMetrics As New RevenueMetrics()
    Public Property PremiumFeatures As New List(Of PremiumFeatureUsage)()
    Public Property XEngagementMetrics As XEngagementMetrics
End Class

Public Class IntegrationSummary
    Public Property Module As String
    Public Property Category As String
    Public Property TotalIntegrations As Integer
    Public Property SuccessfulIntegrations As Integer
    Public Property AverageProfitPotential As Double
End Class

Public Class MonetizationTriggerSummary
    Public Property TriggerType As String
    Public Property Category As String
    Public Property ActivationCount As Integer
    Public Property AverageRevenueBoost As Double
End Class

Public Class RepoAnalytics
    Public Property TotalReposAnalyzed As Integer
    Public Property HighValueRepos As Integer
    Public Property AverageAnalysisScore As Double
End Class

Public Class ApiUsageMetrics
    Public Property TotalQueries As Integer
    Public Property SuccessfulQueries As Integer
    Public Property AverageQuotaUsed As Double
End Class

Public Class RevenueMetrics
    Public Property EstimatedRevenue As Double
    Public Property ConversionRate As Double
    Public Property PremiumUpgrades As Integer
End Class

Public Class PremiumFeatureUsage
    Public Property FeatureName As String
    Public Property UsageCount As Integer
    Public Property Revenue As Double
End Class

Public Class MonetizationRecommendation
    Public Property Title As String
    Public Property Description As String
    Public Property ExpectedROI As Double
    Public Property Priority As String
    Public Property ImplementationCost As Double
End Class

' ===============================================================================
' X/Twitter Engagement Metrics Data Structure
' ===============================================================================
Public Class XEngagementMetrics
    Public Property TweetsPosted As Integer
    Public Property SearchesPerformed As Integer
    Public Property IntelligenceExtractions As Integer
    Public Property ArbitrageAlertsPosted As Integer
    Public Property AverageEngagementRate As Double
    Public Property MonetizationROI As Double
    Public Property ApiSuccessRate As Double
    Public Property XApiReposIntegrated As Integer
    Public Property TotalImpressions As Long
    Public Property TotalClicks As Integer
    Public Property ConversionRate As Double
    Public Property TopPerformingKeywords As List(Of String)

    Public Sub New()
        TopPerformingKeywords = New List(Of String)()
    End Sub

    Public ReadOnly Property EngagementEfficiency As Double
        Get
            Return If(TweetsPosted > 0, AverageEngagementRate / TweetsPosted, 0.0)
        End Get
    End Property

    Public ReadOnly Property ROIPerTweet As Double
        Get
            Return If(TweetsPosted > 0, MonetizationROI / TweetsPosted, 0.0)
        End Get
    End Property
End Class
