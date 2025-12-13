Imports System.Threading.Tasks
Imports System.Data
Imports System.Data.SQLite
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq

''' <summary>
''' Google Apps Script Mail Merge Integration for EQ12
''' Handles document templating and email campaigns via GAS
''' Integrates with EQ12 monetization workflows and Bitly tracking
''' </summary>
Public Class GASMailMerge
    Private ReadOnly _gasClient As GASClient
    Private ReadOnly _dbPath As String
    Private ReadOnly _bitlyHelper As BitlyHelper

    Public Sub New(gasClient As GASClient, Optional dbPath As String = "", Optional bitlyHelper As BitlyHelper = Nothing)
        _gasClient = gasClient ?? Throw New ArgumentNullException(NameOf(gasClient))
        _dbPath = If(String.IsNullOrEmpty(dbPath), "Data/eq12_terminal.db", dbPath)
        _bitlyHelper = bitlyHelper

        ' Initialize campaign tracking table
        InitializeCampaignTable()
    End Sub

    ''' <summary>
    ''' Run mail merge campaign with document template
    ''' </summary>
    ''' <param name="config">Mail merge configuration</param>
    ''' <returns>Campaign execution result</returns>
    Public Async Function RunMailMergeCampaignAsync(config As MailMergeConfig) As Task(Of CampaignResult)
        If config Is Nothing Then
            Throw New ArgumentNullException(NameOf(config))
        End If

        If String.IsNullOrEmpty(config.CampaignName) Then
            config.CampaignName = $"EQ12_Campaign_{DateTime.Now:yyyyMMdd_HHmmss}"
        End If

        Dim campaignId As Integer = 0

        Try
            ' Log campaign start
            campaignId = LogCampaignStart(config)

            ' Enhance templates with Bitly links if available
            If _bitlyHelper IsNot Nothing Then
                config = Await EnhanceWithBitlyLinksAsync(config)
            End If

            ' Build GAS payload
            Dim payload As New JObject() From {
                {"action", "merge"},
                {"templateFileId", config.TemplateFileId},
                {"sheetName", config.RecipientSheetName},
                {"subjectTemplate", config.SubjectTemplate},
                {"bodyTemplate", config.BodyTemplate},
                {"campaignName", config.CampaignName},
                {"trackOpens", config.TrackOpens},
                {"attachTemplate", config.AttachRenderedDocument}
            }

            ' Execute mail merge via GAS
            Dim response = Await _gasClient.PostJsonAsync(payload)

            ' Parse results
            Dim success = response.Value(Of Boolean)("ok")

            If success Then
                Dim sentCount = response.Value(Of Integer)("sent")
                Dim errors = response.Value(Of JArray)("errors")
                Dim totalRecipients = response.Value(Of Integer)("total_recipients")

                ' Log successful campaign
                LogCampaignComplete(campaignId, "success", sentCount, errors?.Count ?? 0,
                                  $"Campaign completed successfully: {sentCount}/{totalRecipients} sent")

                ' Track Bitly clicks if applicable
                If _bitlyHelper IsNot Nothing AndAlso config.BitlyLinks?.Count > 0 Then
                    _ = Task.Run(Async Function() Await TrackBitlyPerformanceAsync(campaignId, config.BitlyLinks))
                End If

                Return New CampaignResult With {
                    .Success = True,
                    .CampaignId = campaignId,
                    .CampaignName = config.CampaignName,
                    .EmailsSent = sentCount,
                    .TotalRecipients = totalRecipients,
                    .ErrorCount = errors?.Count ?? 0,
                    .Errors = errors?.ToObject(Of String())(),
                    .Message = $"Campaign '{config.CampaignName}' completed: {sentCount} emails sent"
                }
            Else
                Dim errorMsg = response.Value(Of String)("error")
                LogCampaignComplete(campaignId, "failed", 0, 1, errorMsg)

                Return New CampaignResult With {
                    .Success = False,
                    .CampaignId = campaignId,
                    .CampaignName = config.CampaignName,
                    .EmailsSent = 0,
                    .ErrorCount = 1,
                    .ErrorMessage = errorMsg
                }
            End If

        Catch ex As Exception
            LogCampaignComplete(campaignId, "error", 0, 1, ex.Message)

            Return New CampaignResult With {
                .Success = False,
                .CampaignId = campaignId,
                .CampaignName = config.CampaignName,
                .EmailsSent = 0,
                .ErrorCount = 1,
                .ErrorMessage = ex.Message
            }
        End Try
    End Function

    ''' <summary>
    ''' Create and send automated newsletter campaign
    ''' </summary>
    ''' <param name="newsletterType">Type of newsletter (daily, weekly, monthly)</param>
    ''' <param name="templateId">Google Docs template ID</param>
    ''' <param name="recipientSegment">Target recipient segment</param>
    ''' <returns>Campaign result</returns>
    Public Async Function SendNewsletterAsync(newsletterType As String, templateId As String,
                                            recipientSegment As String) As Task(Of CampaignResult)
        Try
            ' Get recent betting data for content
            Dim recentData = GetRecentBettingData(newsletterType)

            ' Build newsletter content with monetization hooks
            Dim content = GenerateNewsletterContent(recentData, newsletterType)

            ' Create enhanced subject line
            Dim subject = GenerateNewsletterSubject(newsletterType, recentData)

            ' Configure mail merge
            Dim config As New MailMergeConfig With {
                .CampaignName = $"Newsletter_{newsletterType}_{DateTime.Now:yyyyMMdd}",
                .TemplateFileId = templateId,
                .RecipientSheetName = GetRecipientSheetName(recipientSegment),
                .SubjectTemplate = subject,
                .BodyTemplate = content,
                .TrackOpens = True,
                .AttachRenderedDocument = newsletterType = "weekly" OrElse newsletterType = "monthly",
                .Segment = recipientSegment,
                .NewsletterType = newsletterType
            }

            ' Execute campaign
            Return Await RunMailMergeCampaignAsync(config)

        Catch ex As Exception
            Return New CampaignResult With {
                .Success = False,
                .CampaignName = $"Newsletter_{newsletterType}",
                .ErrorMessage = $"Newsletter creation failed: {ex.Message}"
            }
        End Try
    End Function

    ''' <summary>
    ''' Send affiliate promotion campaign with CTR tracking
    ''' </summary>
    ''' <param name="promotion">Promotion configuration</param>
    ''' <returns>Campaign result with tracking</returns>
    Public Async Function SendAffiliatePromotionAsync(promotion As AffiliatePromotion) As Task(Of CampaignResult)
        Try
            ' Generate Bitly links for tracking if available
            Dim trackingLinks As New Dictionary(Of String, String)()

            If _bitlyHelper IsNot Nothing Then
                For Each link In promotion.AffiliateLinks
                    Dim shortLink = Await _bitlyHelper.CreateShortLinkAsync(link.Value,
                        $"EQ12_Promo_{promotion.PromotionName}_{link.Key}")
                    trackingLinks(link.Key) = shortLink
                Next
            Else
                trackingLinks = promotion.AffiliateLinks
            End If

            ' Build promotion email content
            Dim content = GeneratePromotionContent(promotion, trackingLinks)

            ' Configure mail merge
            Dim config As New MailMergeConfig With {
                .CampaignName = $"Promo_{promotion.PromotionName}_{DateTime.Now:yyyyMMdd}",
                .TemplateFileId = promotion.TemplateId,
                .RecipientSheetName = GetRecipientSheetName(promotion.TargetSegment),
                .SubjectTemplate = promotion.SubjectTemplate,
                .BodyTemplate = content,
                .TrackOpens = True,
                .AttachRenderedDocument = False,
                .Segment = promotion.TargetSegment,
                .PromotionType = promotion.PromotionName,
                .BitlyLinks = trackingLinks
            }

            ' Execute campaign
            Dim result = Await RunMailMergeCampaignAsync(config)

            ' Schedule follow-up tracking
            If result.Success AndAlso trackingLinks.Count > 0 Then
                _ = Task.Run(Async Function()
                               Await Task.Delay(TimeSpan.FromHours(24)) ' Wait 24 hours
                               Await TrackBitlyPerformanceAsync(result.CampaignId, trackingLinks)
                           End Function)
            End If

            Return result

        Catch ex As Exception
            Return New CampaignResult With {
                .Success = False,
                .CampaignName = promotion.PromotionName,
                .ErrorMessage = $"Affiliate promotion failed: {ex.Message}"
            }
        End Try
    End Function

    ''' <summary>
    ''' Get campaign performance metrics and analytics
    ''' </summary>
    ''' <param name="campaignId">Campaign ID to analyze</param>
    ''' <returns>Performance metrics</returns>
    Public Async Function GetCampaignAnalyticsAsync(campaignId As Integer) As Task(Of CampaignAnalytics)
        Try
            ' Get campaign details
            Dim campaign = GetCampaignDetails(campaignId)
            If campaign Is Nothing Then
                Return Nothing
            End If

            ' Get Bitly click analytics if available
            Dim clickData As New Dictionary(Of String, Integer)()
            Dim totalClicks As Integer = 0

            If _bitlyHelper IsNot Nothing AndAlso campaign.BitlyLinks IsNot Nothing Then
                For Each link In campaign.BitlyLinks
                    Try
                        Dim clicks = Await _bitlyHelper.GetLinkStatsAsync(link.Value)
                        clickData(link.Key) = clicks
                        totalClicks += clicks
                    Catch
                        clickData(link.Key) = 0
                    End Try
                Next
            End If

            ' Calculate metrics
            Dim openRate = If(campaign.EmailsSent > 0, (campaign.EstimatedOpens / campaign.EmailsSent) * 100, 0)
            Dim clickRate = If(campaign.EmailsSent > 0, (totalClicks / campaign.EmailsSent) * 100, 0)
            Dim conversionRate = If(totalClicks > 0, (campaign.EstimatedConversions / totalClicks) * 100, 0)

            Return New CampaignAnalytics With {
                .CampaignId = campaignId,
                .CampaignName = campaign.CampaignName,
                .EmailsSent = campaign.EmailsSent,
                .EstimatedOpens = campaign.EstimatedOpens,
                .TotalClicks = totalClicks,
                .ClicksByLink = clickData,
                .OpenRate = Math.Round(openRate, 2),
                .ClickThroughRate = Math.Round(clickRate, 2),
                .ConversionRate = Math.Round(conversionRate, 2),
                .EstimatedRevenue = campaign.EstimatedRevenue,
                .CampaignDate = campaign.Timestamp
            }

        Catch ex As Exception
            Console.WriteLine($"Campaign analytics failed: {ex.Message}")
            Return Nothing
        End Try
    End Function

    ''' <summary>
    ''' Enhance mail merge configuration with Bitly tracking links
    ''' </summary>
    ''' <param name="config">Original configuration</param>
    ''' <returns>Enhanced configuration with tracking links</returns>
    Private Async Function EnhanceWithBitlyLinksAsync(config As MailMergeConfig) As Task(Of MailMergeConfig)
        If _bitlyHelper Is Nothing Then Return config

        Try
            ' Extract URLs from templates and create Bitly links
            Dim urlPattern = "https?://[^\s<>""']+[^\s<>.""',!?]"
            Dim regex As New Text.RegularExpressions.Regex(urlPattern)

            Dim trackingLinks As New Dictionary(Of String, String)()

            ' Process subject template
            Dim subjectMatches = regex.Matches(config.SubjectTemplate)
            For Each match As Text.RegularExpressions.Match In subjectMatches
                Dim originalUrl = match.Value
                If Not trackingLinks.ContainsKey(originalUrl) Then
                    Dim shortLink = Await _bitlyHelper.CreateShortLinkAsync(originalUrl,
                        $"EQ12_{config.CampaignName}_Subject")
                    trackingLinks(originalUrl) = shortLink
                    config.SubjectTemplate = config.SubjectTemplate.Replace(originalUrl, shortLink)
                End If
            Next

            ' Process body template
            Dim bodyMatches = regex.Matches(config.BodyTemplate)
            For Each match As Text.RegularExpressions.Match In bodyMatches
                Dim originalUrl = match.Value
                If Not trackingLinks.ContainsKey(originalUrl) Then
                    Dim shortLink = Await _bitlyHelper.CreateShortLinkAsync(originalUrl,
                        $"EQ12_{config.CampaignName}_Body")
                    trackingLinks(originalUrl) = shortLink
                    config.BodyTemplate = config.BodyTemplate.Replace(originalUrl, shortLink)
                End If
            Next

            config.BitlyLinks = trackingLinks

        Catch ex As Exception
            Console.WriteLine($"Bitly enhancement failed: {ex.Message}")
        End Try

        Return config
    End Function

    ''' <summary>
    ''' Generate newsletter content based on recent data and type
    ''' </summary>
    ''' <param name="recentData">Recent betting data</param>
    ''' <param name="newsletterType">Type of newsletter</param>
    ''' <returns>HTML content for newsletter</returns>
    Private Function GenerateNewsletterContent(recentData As List(Of Object), newsletterType As String) As String
        Dim content As New Text.StringBuilder()

        content.AppendLine($"<h2>EQ12 {newsletterType.ToUpper()} Sports Betting Digest</h2>")
        content.AppendLine("<p>Hello {{{{name}}}},</p>")

        If recentData.Count > 0 Then
            content.AppendLine($"<p>Here are your latest {newsletterType} betting insights and opportunities:</p>")
            content.AppendLine("<ul>")

            For Each item In recentData.Take(5)
                Dim data = DirectCast(item, Dictionary(Of String, Object))
                Dim team = data.GetValueOrDefault("team", "Unknown")
                Dim confidence = data.GetValueOrDefault("confidence", "TBD")
                Dim analysis = data.GetValueOrDefault("analysis", "Analysis available")

                content.AppendLine($"<li><strong>{team}</strong> - {analysis} ({confidence}% confidence)</li>")
            Next

            content.AppendLine("</ul>")
        Else
            content.AppendLine($"<p>No recent {newsletterType} activity to report. Check back soon for the latest insights!</p>")
        End If

        ' Add monetization CTAs
        content.AppendLine("<div style='margin: 20px 0; padding: 15px; background: #f0f8ff; border-left: 4px solid #007cba;'>")
        content.AppendLine("<p><strong>💎 Upgrade to Premium</strong></p>")
        content.AppendLine("<p>Get advanced analytics, real-time alerts, and exclusive strategies:</p>")
        content.AppendLine("<p><a href='{{{{upgrade_link}}}}' style='background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>Upgrade Now</a></p>")
        content.AppendLine("</div>")

        ' Add affiliate promotions
        content.AppendLine("<div style='margin: 20px 0;'>")
        content.AppendLine("<p><strong>🎯 Featured Sportsbook</strong></p>")
        content.AppendLine("<p>Join our recommended sportsbook and get up to $500 in bonus bets:</p>")
        content.AppendLine("<p><a href='{{{{affiliate_link}}}}' style='background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>Claim Bonus</a></p>")
        content.AppendLine("<p><em>Terms and conditions apply. 21+ only.</em></p>")
        content.AppendLine("</div>")

        content.AppendLine("<p>Best regards,<br>The EQ12 Team</p>")

        Return content.ToString()
    End Function

    ''' <summary>
    ''' Generate promotion content with tracking links
    ''' </summary>
    ''' <param name="promotion">Promotion configuration</param>
    ''' <param name="trackingLinks">Bitly tracking links</param>
    ''' <returns>HTML promotion content</returns>
    Private Function GeneratePromotionContent(promotion As AffiliatePromotion,
                                            trackingLinks As Dictionary(Of String, String)) As String
        Dim content = promotion.ContentTemplate

        ' Replace tracking link placeholders
        For Each link In trackingLinks
            content = content.Replace($"{{{{{link.Key}}}}}", link.Value)
        Next

        ' Add standard EQ12 footer
        content &= vbCrLf & GetStandardFooter()

        Return content
    End Function

    ''' <summary>
    ''' Get standard email footer with compliance information
    ''' </summary>
    ''' <returns>HTML footer content</returns>
    Private Function GetStandardFooter() As String
        Return "
<div style='margin-top: 30px; padding-top: 20px; border-top: 1px solid #ccc; font-size: 12px; color: #666;'>
  <p><strong>EQ12 Sports Betting Terminal</strong> - Advanced Analytics & Insights</p>
  <p>This email contains affiliate links. We may earn a commission from qualifying purchases.</p>
  <p>For questions or to unsubscribe, reply to this email or visit {{{{unsubscribe_link}}}}.</p>
  <p><em>Paper trading recommended. Past performance does not guarantee future results. 21+ only. Gamble responsibly.</em></p>
</div>"
    End Function

    ' Additional helper methods and database operations would continue...
    ' (Implementation continues with database methods, campaign tracking, analytics, etc.)

    Private Sub InitializeCampaignTable()
        ' Implementation for database initialization
    End Sub

    Private Function LogCampaignStart(config As MailMergeConfig) As Integer
        ' Implementation for campaign logging
        Return 0
    End Function

    Private Sub LogCampaignComplete(campaignId As Integer, status As String, sent As Integer, errors As Integer, message As String)
        ' Implementation for campaign completion logging
    End Sub

    Private Function GetRecentBettingData(newsletterType As String) As List(Of Object)
        ' Implementation for retrieving recent betting data
        Return New List(Of Object)()
    End Function

    Private Function GenerateNewsletterSubject(newsletterType As String, data As List(Of Object)) As String
        Return $"EQ12 {newsletterType.ToUpper()} Digest - {DateTime.Now:MMMM dd, yyyy}"
    End Function

    Private Function GetRecipientSheetName(segment As String) As String
        Return If(segment = "premium", "PremiumSubscribers", "Subscribers")
    End Function

    Private Async Function TrackBitlyPerformanceAsync(campaignId As Integer, links As Dictionary(Of String, String)) As Task
        ' Implementation for Bitly performance tracking
    End Function

    Private Function GetCampaignDetails(campaignId As Integer) As Object
        ' Implementation for retrieving campaign details
        Return Nothing
    End Function
End Class

''' <summary>
''' Mail merge configuration class
''' </summary>
Public Class MailMergeConfig
    Public Property CampaignName As String
    Public Property TemplateFileId As String
    Public Property RecipientSheetName As String
    Public Property SubjectTemplate As String
    Public Property BodyTemplate As String
    Public Property TrackOpens As Boolean = True
    Public Property AttachRenderedDocument As Boolean = False
    Public Property Segment As String
    Public Property NewsletterType As String
    Public Property PromotionType As String
    Public Property BitlyLinks As Dictionary(Of String, String)
End Class

''' <summary>
''' Campaign execution result
''' </summary>
Public Class CampaignResult
    Public Property Success As Boolean
    Public Property CampaignId As Integer
    Public Property CampaignName As String
    Public Property EmailsSent As Integer
    Public Property TotalRecipients As Integer
    Public Property ErrorCount As Integer
    Public Property Errors As String()
    Public Property Message As String
    Public Property ErrorMessage As String
End Class

''' <summary>
''' Affiliate promotion configuration
''' </summary>
Public Class AffiliatePromotion
    Public Property PromotionName As String
    Public Property TemplateId As String
    Public Property TargetSegment As String
    Public Property SubjectTemplate As String
    Public Property ContentTemplate As String
    Public Property AffiliateLinks As Dictionary(Of String, String)
End Class

''' <summary>
''' Campaign analytics and performance metrics
''' </summary>
Public Class CampaignAnalytics
    Public Property CampaignId As Integer
    Public Property CampaignName As String
    Public Property EmailsSent As Integer
    Public Property EstimatedOpens As Integer
    Public Property TotalClicks As Integer
    Public Property ClicksByLink As Dictionary(Of String, Integer)
    Public Property OpenRate As Double
    Public Property ClickThroughRate As Double
    Public Property ConversionRate As Double
    Public Property EstimatedRevenue As Decimal
    Public Property CampaignDate As DateTime
End Class
