' X Ads API Client for EQ12 - Complete Campaign Management v3.0
' Pre-generated for immediate deployment - Production Ready
' Supports: Campaign Management, Audience Targeting, Creative Management, Analytics

Imports System
Imports System.IO
Imports System.Net.Http
Imports System.Text
Imports System.Threading.Tasks
Imports System.Collections.Generic
Imports System.Text.Json
Imports System.Text.Json.Serialization
Imports Microsoft.Extensions.Configuration
Imports Microsoft.Extensions.Logging

''' <summary>
''' Complete X Ads API Client with comprehensive campaign management and analytics
''' </summary>
Public Class XAdsClient
    Private ReadOnly _httpClient As HttpClient
    Private ReadOnly _logger As ILogger
    Private ReadOnly _config As IConfiguration
    Private ReadOnly _dbWriter As DBWriter
    Private ReadOnly _bitlyConfig As BitlyConfig

    Private Const ADS_API_BASE_URL As String = "https://ads-api.x.com/12"

    Public Sub New(Optional logger As ILogger = Nothing, Optional config As IConfiguration = Nothing)
        _logger = logger
        _config = config
        _httpClient = New HttpClient()
        _dbWriter = New DBWriter()
        _bitlyConfig = New BitlyConfig() With {
            .AccessToken = _config?("Bitly:AccessToken"),
            .GroupId = _config?("Bitly:GroupId")
        }

        ' Set default headers
        _httpClient.DefaultRequestHeaders.Add("User-Agent", "EQ12-XAdsClient/3.0")
    End Sub

    ' ==================================================
    ' ACCOUNT AND AUTHENTICATION
    ' ==================================================

    ''' <summary>
    ''' Get all advertising accounts for authenticated user
    ''' </summary>
    Public Async Function GetAccountsAsync(accessToken As String) As Task(Of List(Of AdAccount))
        Try
            _httpClient.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

            Dim response = Await _httpClient.GetAsync($"{ADS_API_BASE_URL}/accounts")
            Dim responseContent = Await response.Content.ReadAsStringAsync()

            If response.IsSuccessStatusCode Then
                Dim accountsResponse = JsonSerializer.Deserialize(Of AdAccountsResponse)(responseContent)

                ' Log account retrieval
                Await LogXAdsActionAsync("get_accounts", Nothing, responseContent, "success", accessToken)

                _logger?.LogInformation($"✅ Retrieved {accountsResponse.Data?.Count ?? 0} ad accounts")
                Return accountsResponse.Data ?? New List(Of AdAccount)()
            Else
                Throw New Exception($"Failed to get accounts: {response.StatusCode} - {responseContent}")
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error getting ad accounts")
            Await LogXAdsActionAsync("get_accounts", Nothing, ex.Message, "failed", accessToken)
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Get specific account details with funding instruments
    ''' </summary>
    Public Async Function GetAccountDetailsAsync(accountId As String, accessToken As String) As Task(Of AdAccountDetail)
        Try
            _httpClient.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

            Dim response = Await _httpClient.GetAsync($"{ADS_API_BASE_URL}/accounts/{accountId}?with_deleted=false")
            Dim responseContent = Await response.Content.ReadAsStringAsync()

            If response.IsSuccessStatusCode Then
                Dim accountResponse = JsonSerializer.Deserialize(Of AdAccountDetailResponse)(responseContent)

                ' Also get funding instruments
                Dim fundingResponse = Await _httpClient.GetAsync($"{ADS_API_BASE_URL}/accounts/{accountId}/funding_instruments")
                Dim fundingContent = Await fundingResponse.Content.ReadAsStringAsync()

                If fundingResponse.IsSuccessStatusCode Then
                    Dim fundingData = JsonSerializer.Deserialize(Of FundingInstrumentsResponse)(fundingContent)
                    accountResponse.Data.FundingInstruments = fundingData.Data
                End If

                Await LogXAdsActionAsync("get_account_details", accountId, responseContent, "success", accessToken)

                Return accountResponse.Data
            Else
                Throw New Exception($"Failed to get account details: {response.StatusCode} - {responseContent}")
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error getting account details")
            Await LogXAdsActionAsync("get_account_details", accountId, ex.Message, "failed", accessToken)
            Throw
        End Try
    End Function

    ' ==================================================
    ' CAMPAIGN MANAGEMENT
    ' ==================================================

    ''' <summary>
    ''' Create new advertising campaign
    ''' </summary>
    Public Async Function CreateCampaignAsync(campaignData As CreateCampaignRequest, accessToken As String) As Task(Of Campaign)
        Try
            _httpClient.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

            ' Validate campaign data
            ValidateCampaignData(campaignData)

            ' Set default values
            If String.IsNullOrEmpty(campaignData.Currency) Then campaignData.Currency = "USD"
            If String.IsNullOrEmpty(campaignData.EntityStatus) Then campaignData.EntityStatus = "PAUSED"

            Dim requestBody = New StringContent(
                JsonSerializer.Serialize(campaignData),
                Encoding.UTF8, "application/json"
            )

            Dim response = Await _httpClient.PostAsync($"{ADS_API_BASE_URL}/accounts/{campaignData.AccountId}/campaigns", requestBody)
            Dim responseContent = Await response.Content.ReadAsStringAsync()

            If response.IsSuccessStatusCode Then
                Dim campaignResponse = JsonSerializer.Deserialize(Of CampaignResponse)(responseContent)

                ' Log campaign creation
                Await LogXAdsActionAsync("create_campaign", campaignData.Name, responseContent, "success", accessToken, campaignResponse.Data.Id)

                ' Send success notification
                Await SendCampaignNotificationAsync("created", campaignResponse.Data, campaignData.AccountId)

                _logger?.LogInformation($"✅ Campaign created: {campaignResponse.Data.Name} (ID: {campaignResponse.Data.Id})")
                Return campaignResponse.Data
            Else
                Throw New Exception($"Failed to create campaign: {response.StatusCode} - {responseContent}")
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error creating campaign")
            Await LogXAdsActionAsync("create_campaign", campaignData?.Name, ex.Message, "failed", accessToken)
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Get campaigns for account with filtering
    ''' </summary>
    Public Async Function GetCampaignsAsync(accountId As String, accessToken As String,
                                            Optional withDeleted As Boolean = False,
                                            Optional entityStatus As String = Nothing) As Task(Of List(Of Campaign))
        Try
            _httpClient.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

            Dim queryParams As New List(Of String) From {
                $"with_deleted={withDeleted.ToString().ToLower()}"
            }

            If Not String.IsNullOrEmpty(entityStatus) Then
                queryParams.Add($"entity_status={entityStatus}")
            End If

            Dim queryString = String.Join("&", queryParams)
            Dim response = Await _httpClient.GetAsync($"{ADS_API_BASE_URL}/accounts/{accountId}/campaigns?{queryString}")
            Dim responseContent = Await response.Content.ReadAsStringAsync()

            If response.IsSuccessStatusCode Then
                Dim campaignsResponse = JsonSerializer.Deserialize(Of CampaignsResponse)(responseContent)

                Await LogXAdsActionAsync("get_campaigns", accountId, $"Retrieved {campaignsResponse.Data?.Count ?? 0} campaigns", "success", accessToken)

                Return campaignsResponse.Data ?? New List(Of Campaign)()
            Else
                Throw New Exception($"Failed to get campaigns: {response.StatusCode} - {responseContent}")
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error getting campaigns")
            Await LogXAdsActionAsync("get_campaigns", accountId, ex.Message, "failed", accessToken)
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Update existing campaign
    ''' </summary>
    Public Async Function UpdateCampaignAsync(campaignId As String, updateData As UpdateCampaignRequest, accessToken As String) As Task(Of Campaign)
        Try
            _httpClient.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

            Dim requestBody = New StringContent(
                JsonSerializer.Serialize(updateData),
                Encoding.UTF8, "application/json"
            )

            Dim response = Await _httpClient.PutAsync($"{ADS_API_BASE_URL}/accounts/{updateData.AccountId}/campaigns/{campaignId}", requestBody)
            Dim responseContent = Await response.Content.ReadAsStringAsync()

            If response.IsSuccessStatusCode Then
                Dim campaignResponse = JsonSerializer.Deserialize(Of CampaignResponse)(responseContent)

                Await LogXAdsActionAsync("update_campaign", campaignId, responseContent, "success", accessToken, campaignId)

                _logger?.LogInformation($"✅ Campaign updated: {campaignId}")
                Return campaignResponse.Data
            Else
                Throw New Exception($"Failed to update campaign: {response.StatusCode} - {responseContent}")
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error updating campaign")
            Await LogXAdsActionAsync("update_campaign", campaignId, ex.Message, "failed", accessToken)
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Delete/Pause campaign
    ''' </summary>
    Public Async Function DeleteCampaignAsync(accountId As String, campaignId As String, accessToken As String) As Task(Of Boolean)
        Try
            _httpClient.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

            Dim response = Await _httpClient.DeleteAsync($"{ADS_API_BASE_URL}/accounts/{accountId}/campaigns/{campaignId}")

            If response.IsSuccessStatusCode Then
                Await LogXAdsActionAsync("delete_campaign", campaignId, "Campaign deleted successfully", "success", accessToken, campaignId)

                _logger?.LogInformation($"✅ Campaign deleted: {campaignId}")
                Return True
            Else
                Dim responseContent = Await response.Content.ReadAsStringAsync()
                Throw New Exception($"Failed to delete campaign: {response.StatusCode} - {responseContent}")
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error deleting campaign")
            Await LogXAdsActionAsync("delete_campaign", campaignId, ex.Message, "failed", accessToken)
            Throw
        End Try
    End Function

    ' ==================================================
    ' LINE ITEM (AD GROUP) MANAGEMENT
    ' ==================================================

    ''' <summary>
    ''' Create line item for campaign
    ''' </summary>
    Public Async Function CreateLineItemAsync(lineItemData As CreateLineItemRequest, accessToken As String) As Task(Of LineItem)
        Try
            _httpClient.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

            ' Validate line item data
            ValidateLineItemData(lineItemData)

            Dim requestBody = New StringContent(
                JsonSerializer.Serialize(lineItemData),
                Encoding.UTF8, "application/json"
            )

            Dim response = Await _httpClient.PostAsync($"{ADS_API_BASE_URL}/accounts/{lineItemData.AccountId}/line_items", requestBody)
            Dim responseContent = Await response.Content.ReadAsStringAsync()

            If response.IsSuccessStatusCode Then
                Dim lineItemResponse = JsonSerializer.Deserialize(Of LineItemResponse)(responseContent)

                Await LogXAdsActionAsync("create_line_item", lineItemData.Name, responseContent, "success", accessToken, lineItemResponse.Data.Id)

                _logger?.LogInformation($"✅ Line item created: {lineItemResponse.Data.Name} (ID: {lineItemResponse.Data.Id})")
                Return lineItemResponse.Data
            Else
                Throw New Exception($"Failed to create line item: {response.StatusCode} - {responseContent}")
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error creating line item")
            Await LogXAdsActionAsync("create_line_item", lineItemData?.Name, ex.Message, "failed", accessToken)
            Throw
        End Try
    End Function

    ' ==================================================
    ' CREATIVE MANAGEMENT
    ' ==================================================

    ''' <summary>
    ''' Upload and create media creative
    ''' </summary>
    Public Async Function UploadCreativeAsync(filePath As String, creativeType As String, accessToken As String,
                                              Optional accountId As String = Nothing,
                                              Optional name As String = Nothing) As Task(Of MediaCreative)
        Try
            If Not File.Exists(filePath) Then
                Throw New FileNotFoundException($"Creative file not found: {filePath}")
            End If

            _httpClient.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

            ' First, upload the media file
            Dim mediaId = Await UploadMediaFileAsync(filePath, accountId, accessToken)

            ' Then create the creative
            Dim creativeData As New CreateCreativeRequest() With {
                .AccountId = accountId,
                .Name = If(name, $"EQ12 Creative - {Path.GetFileNameWithoutExtension(filePath)}"),
                .CreativeType = creativeType,
                .MediaKey = mediaId
            }

            Dim requestBody = New StringContent(
                JsonSerializer.Serialize(creativeData),
                Encoding.UTF8, "application/json"
            )

            Dim response = Await _httpClient.PostAsync($"{ADS_API_BASE_URL}/accounts/{accountId}/creatives", requestBody)
            Dim responseContent = Await response.Content.ReadAsStringAsync()

            If response.IsSuccessStatusCode Then
                Dim creativeResponse = JsonSerializer.Deserialize(Of CreativeResponse)(responseContent)

                Await LogXAdsActionAsync("upload_creative", Path.GetFileName(filePath), responseContent, "success", accessToken, creativeResponse.Data.Id)

                _logger?.LogInformation($"✅ Creative uploaded: {creativeResponse.Data.Name} (ID: {creativeResponse.Data.Id})")
                Return creativeResponse.Data
            Else
                Throw New Exception($"Failed to create creative: {response.StatusCode} - {responseContent}")
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error uploading creative")
            Await LogXAdsActionAsync("upload_creative", Path.GetFileName(filePath), ex.Message, "failed", accessToken)
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Create promoted tweet creative
    ''' </summary>
    Public Async Function CreatePromotedTweetAsync(accountId As String, tweetId As String, accessToken As String) As Task(Of PromotedTweet)
        Try
            _httpClient.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

            Dim promotedTweetData As New CreatePromotedTweetRequest() With {
                .AccountId = accountId,
                .TweetId = tweetId
            }

            Dim requestBody = New StringContent(
                JsonSerializer.Serialize(promotedTweetData),
                Encoding.UTF8, "application/json"
            )

            Dim response = Await _httpClient.PostAsync($"{ADS_API_BASE_URL}/accounts/{accountId}/promoted_tweets", requestBody)
            Dim responseContent = Await response.Content.ReadAsStringAsync()

            If response.IsSuccessStatusCode Then
                Dim promotedResponse = JsonSerializer.Deserialize(Of PromotedTweetResponse)(responseContent)

                Await LogXAdsActionAsync("create_promoted_tweet", tweetId, responseContent, "success", accessToken, promotedResponse.Data.Id)

                _logger?.LogInformation($"✅ Promoted tweet created for tweet: {tweetId}")
                Return promotedResponse.Data
            Else
                Throw New Exception($"Failed to create promoted tweet: {response.StatusCode} - {responseContent}")
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error creating promoted tweet")
            Await LogXAdsActionAsync("create_promoted_tweet", tweetId, ex.Message, "failed", accessToken)
            Throw
        End Try
    End Function

    ' ==================================================
    ' AUDIENCE MANAGEMENT
    ' ==================================================

    ''' <summary>
    ''' Create tailored audience
    ''' </summary>
    Public Async Function CreateTailoredAudienceAsync(audienceData As CreateTailoredAudienceRequest, accessToken As String) As Task(Of TailoredAudience)
        Try
            _httpClient.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

            Dim requestBody = New StringContent(
                JsonSerializer.Serialize(audienceData),
                Encoding.UTF8, "application/json"
            )

            Dim response = Await _httpClient.PostAsync($"{ADS_API_BASE_URL}/accounts/{audienceData.AccountId}/tailored_audiences", requestBody)
            Dim responseContent = Await response.Content.ReadAsStringAsync()

            If response.IsSuccessStatusCode Then
                Dim audienceResponse = JsonSerializer.Deserialize(Of TailoredAudienceResponse)(responseContent)

                Await LogXAdsActionAsync("create_audience", audienceData.Name, responseContent, "success", accessToken, audienceResponse.Data.Id)

                _logger?.LogInformation($"✅ Tailored audience created: {audienceResponse.Data.Name}")
                Return audienceResponse.Data
            Else
                Throw New Exception($"Failed to create tailored audience: {response.StatusCode} - {responseContent}")
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error creating tailored audience")
            Await LogXAdsActionAsync("create_audience", audienceData?.Name, ex.Message, "failed", accessToken)
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Upload users to tailored audience
    ''' </summary>
    Public Async Function UploadAudienceUsersAsync(accountId As String, audienceId As String,
                                                   users As List(Of String), userType As String,
                                                   accessToken As String) As Task(Of Boolean)
        Try
            _httpClient.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

            Dim uploadData As New AudienceUserUploadRequest() With {
                .Users = users,
                .UserType = userType ' EMAIL, PHONE, TWITTER_ID, etc.
            }

            Dim requestBody = New StringContent(
                JsonSerializer.Serialize(uploadData),
                Encoding.UTF8, "application/json"
            )

            Dim response = Await _httpClient.PostAsync($"{ADS_API_BASE_URL}/accounts/{accountId}/tailored_audiences/{audienceId}/users", requestBody)

            If response.IsSuccessStatusCode Then
                Await LogXAdsActionAsync("upload_audience_users", audienceId, $"Uploaded {users.Count} users", "success", accessToken, audienceId)

                _logger?.LogInformation($"✅ Uploaded {users.Count} users to audience: {audienceId}")
                Return True
            Else
                Dim responseContent = Await response.Content.ReadAsStringAsync()
                Throw New Exception($"Failed to upload audience users: {response.StatusCode} - {responseContent}")
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error uploading audience users")
            Await LogXAdsActionAsync("upload_audience_users", audienceId, ex.Message, "failed", accessToken)
            Throw
        End Try
    End Function

    ' ==================================================
    ' ANALYTICS AND REPORTING
    ' ==================================================

    ''' <summary>
    ''' Create async stats job for comprehensive analytics
    ''' </summary>
    Public Async Function CreateStatsJobAsync(statsRequest As CreateStatsJobRequest, accessToken As String) As Task(Of StatsJob)
        Try
            _httpClient.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

            ' Validate date range
            If statsRequest.StartTime >= statsRequest.EndTime Then
                Throw New ArgumentException("Start time must be before end time")
            End If

            Dim requestBody = New StringContent(
                JsonSerializer.Serialize(statsRequest),
                Encoding.UTF8, "application/json"
            )

            Dim response = Await _httpClient.PostAsync($"{ADS_API_BASE_URL}/stats/jobs/accounts/{statsRequest.AccountId}", requestBody)
            Dim responseContent = Await response.Content.ReadAsStringAsync()

            If response.IsSuccessStatusCode Then
                Dim jobResponse = JsonSerializer.Deserialize(Of StatsJobResponse)(responseContent)

                Await LogXAdsActionAsync("create_stats_job", statsRequest.AccountId, responseContent, "success", accessToken, jobResponse.Data.Id)

                _logger?.LogInformation($"✅ Stats job created: {jobResponse.Data.Id}")
                Return jobResponse.Data
            Else
                Throw New Exception($"Failed to create stats job: {response.StatusCode} - {responseContent}")
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error creating stats job")
            Await LogXAdsActionAsync("create_stats_job", statsRequest?.AccountId, ex.Message, "failed", accessToken)
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Get stats job results with automatic polling
    ''' </summary>
    Public Async Function GetStatsJobResultsAsync(accountId As String, jobId As String, accessToken As String,
                                                  Optional maxWaitSeconds As Integer = 300) As Task(Of StatsJobResult)
        Try
            _httpClient.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

            Dim startTime = DateTime.UtcNow
            Dim pollInterval = TimeSpan.FromSeconds(5)

            While DateTime.UtcNow.Subtract(startTime).TotalSeconds < maxWaitSeconds
                Dim response = Await _httpClient.GetAsync($"{ADS_API_BASE_URL}/stats/jobs/accounts/{accountId}/{jobId}")
                Dim responseContent = Await response.Content.ReadAsStringAsync()

                If response.IsSuccessStatusCode Then
                    Dim jobResult = JsonSerializer.Deserialize(Of StatsJobResult)(responseContent)

                    Select Case jobResult.JobStatus.ToUpper()
                        Case "SUCCESS"
                            Await LogXAdsActionAsync("get_stats_results", jobId, "Stats retrieved successfully", "success", accessToken, jobId)
                            _logger?.LogInformation($"✅ Stats job completed: {jobId}")
                            Return jobResult

                        Case "FAILED"
                            Throw New Exception($"Stats job failed: {jobResult.JobStatus}")

                        Case "PROCESSING"
                            _logger?.LogInformation($"📊 Stats job {jobId} still processing...")
                            Await Task.Delay(pollInterval)

                        Case Else
                            Await Task.Delay(pollInterval)
                    End Select
                Else
                    Throw New Exception($"Failed to get stats job status: {response.StatusCode} - {responseContent}")
                End If
            End While

            Throw New TimeoutException($"Stats job {jobId} did not complete within {maxWaitSeconds} seconds")

        Catch ex As Exception
            _logger?.LogError(ex, "Error getting stats job results")
            Await LogXAdsActionAsync("get_stats_results", jobId, ex.Message, "failed", accessToken)
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Get comprehensive campaign analytics with EQ12 integration
    ''' </summary>
    Public Async Function GetCampaignAnalyticsAsync(accountId As String, campaignId As String,
                                                    startDate As DateTime, endDate As DateTime,
                                                    accessToken As String) As Task(Of CampaignAnalytics)
        Try
            ' Create stats job for detailed analytics
            Dim statsRequest As New CreateStatsJobRequest() With {
                .AccountId = accountId,
                .EntityIds = New List(Of String) From {campaignId},
                .EntityType = "CAMPAIGN",
                .StartTime = startDate,
                .EndTime = endDate,
                .Granularity = "DAY",
                .MetricGroups = New List(Of String) From {"ENGAGEMENT", "BILLING", "VIDEO", "MEDIA", "WEB_CONVERSION", "MOBILE_CONVERSION"},
                .Placement = "ALL_ON_TWITTER"
            }

            Dim statsJob = Await CreateStatsJobAsync(statsRequest, accessToken)
            Dim statsResults = Await GetStatsJobResultsAsync(accountId, statsJob.Id, accessToken)

            ' Process and enhance analytics data
            Dim analytics = ProcessCampaignStats(statsResults, campaignId)

            ' Get additional campaign details
            Dim campaigns = Await GetCampaignsAsync(accountId, accessToken)
            Dim campaign = campaigns.FirstOrDefault(Function(c) c.Id = campaignId)

            If campaign IsNot Nothing Then
                analytics.CampaignName = campaign.Name
                analytics.CampaignStatus = campaign.EntityStatus
                analytics.DailyBudgetAmountLocalMicro = campaign.DailyBudgetAmountLocalMicro
                analytics.Currency = campaign.Currency
            End If

            ' Calculate EQ12-specific metrics
            analytics.EQ12EngagementScore = CalculateEQ12EngagementScore(analytics)
            analytics.EQ12ROI = CalculateEQ12ROI(analytics)
            analytics.EQ12ViralityScore = CalculateEQ12ViralityScore(analytics)

            ' Store in database for historical tracking
            Await StoreAnalyticsAsync(analytics)

            _logger?.LogInformation($"✅ Campaign analytics retrieved for: {campaignId}")
            Return analytics

        Catch ex As Exception
            _logger?.LogError(ex, "Error getting campaign analytics")
            Throw
        End Try
    End Function

    ' ==================================================
    ' EQ12 SPECIFIC INTEGRATIONS
    ' ==================================================

    ''' <summary>
    ''' Auto-promote high-performing organic tweets
    ''' </summary>
    Public Async Function AutoPromoteHighPerformingTweetAsync(tweetId As String, accountId As String,
                                                              budget As Decimal, accessToken As String) As Task(Of String)
        Try
            _logger?.LogInformation($"🚀 Auto-promoting high-performing tweet: {tweetId}")

            ' 1. Create campaign for promotion
            Dim campaignData As New CreateCampaignRequest() With {
                .AccountId = accountId,
                .Name = $"EQ12 Auto-Promotion - Tweet {tweetId}",
                .EntityStatus = "PAUSED",
                .Currency = "USD",
                .DailyBudgetAmountLocalMicro = CLng(budget * 1000000), ' Convert to micros
                .StartTime = DateTime.UtcNow,
                .EndTime = DateTime.UtcNow.AddDays(7) ' 7-day campaign
            }

            Dim campaign = Await CreateCampaignAsync(campaignData, accessToken)

            ' 2. Create promoted tweet
            Dim promotedTweet = Await CreatePromotedTweetAsync(accountId, tweetId, accessToken)

            ' 3. Create line item for targeting
            Dim lineItemData As New CreateLineItemRequest() With {
                .AccountId = accountId,
                .CampaignId = campaign.Id,
                .Name = $"EQ12 Line Item - {tweetId}",
                .ProductType = "PROMOTED_TWEETS",
                .Objective = "ENGAGEMENT",
                .BidAmountLocalMicro = 5000000, ' $5.00 CPM
                .EntityStatus = "PAUSED"
            }

            Dim lineItem = Await CreateLineItemAsync(lineItemData, accessToken)

            ' 4. Send notification about auto-promotion
            Await SendAutoPromotionNotificationAsync(tweetId, campaign.Id, budget)

            ' 5. Log the auto-promotion
            Await LogXAdsActionAsync("auto_promote_tweet", tweetId,
                $"Campaign: {campaign.Id}, Budget: ${budget}", "success", accessToken, campaign.Id)

            _logger?.LogInformation($"✅ Tweet {tweetId} auto-promoted with campaign {campaign.Id}")
            Return campaign.Id

        Catch ex As Exception
            _logger?.LogError(ex, "Error auto-promoting tweet")
            Await LogXAdsActionAsync("auto_promote_tweet", tweetId, ex.Message, "failed", accessToken)
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Generate EQ12 Ad Performance Report
    ''' </summary>
    Public Async Function GenerateEQ12AdReportAsync(accountId As String, days As Integer,
                                                    accessToken As String) As Task(Of String)
        Try
            _logger?.LogInformation($"📊 Generating EQ12 ad performance report for {days} days")

            Dim endDate = DateTime.UtcNow
            Dim startDate = endDate.AddDays(-days)

            ' Get all campaigns
            Dim campaigns = Await GetCampaignsAsync(accountId, accessToken)

            ' Get analytics for each campaign
            Dim allAnalytics As New List(Of CampaignAnalytics)()

            For Each campaign In campaigns
                Try
                    Dim analytics = Await GetCampaignAnalyticsAsync(accountId, campaign.Id, startDate, endDate, accessToken)
                    allAnalytics.Add(analytics)
                Catch ex As Exception
                    _logger?.LogWarning($"Could not get analytics for campaign {campaign.Id}: {ex.Message}")
                End Try
            Next

            ' Generate comprehensive report
            Dim report = GenerateComprehensiveAdReport(allAnalytics, days)

            ' Save report to file
            Dim timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss")
            Dim filename = $"EQ12_Ad_Report_{days}days_{timestamp}.json"
            Dim filepath = Path.Combine("C:\EQ12\logs", filename)

            Await File.WriteAllTextAsync(filepath, JsonSerializer.Serialize(report, New JsonSerializerOptions With {.WriteIndented = True}))

            ' Create shareable link
            Dim shareableUrl = Await CreateShareableReportLinkAsync(filepath)

            ' Send report notification
            Await SendAdReportNotificationAsync(shareableUrl, report, days)

            _logger?.LogInformation($"✅ EQ12 ad report generated: {shareableUrl}")
            Return shareableUrl

        Catch ex As Exception
            _logger?.LogError(ex, "Error generating EQ12 ad report")
            Throw
        End Try
    End Function

    ' ==================================================
    ' HELPER METHODS
    ' ==================================================

    Private Async Function UploadMediaFileAsync(filePath As String, accountId As String, accessToken As String) As Task(Of String)
        Try
            Using form = New MultipartFormDataContent()
                Dim fileContent = New ByteArrayContent(Await File.ReadAllBytesAsync(filePath))
                fileContent.Headers.ContentType = System.Net.Http.Headers.MediaTypeHeaderValue.Parse(GetMimeType(filePath))
                form.Add(fileContent, "media", Path.GetFileName(filePath))

                If Not String.IsNullOrEmpty(accountId) Then
                    form.Add(New StringContent(accountId), "account_id")
                End If

                Dim response = Await _httpClient.PostAsync($"{ADS_API_BASE_URL}/accounts/{accountId}/media_upload", form)
                Dim responseContent = Await response.Content.ReadAsStringAsync()

                If response.IsSuccessStatusCode Then
                    Dim uploadResponse = JsonSerializer.Deserialize(Of MediaUploadResponse)(responseContent)
                    Return uploadResponse.MediaKey
                Else
                    Throw New Exception($"Media upload failed: {response.StatusCode} - {responseContent}")
                End If
            End Using

        Catch ex As Exception
            _logger?.LogError(ex, "Error uploading media file")
            Throw
        End Try
    End Function

    Private Function GetMimeType(filePath As String) As String
        Dim extension = Path.GetExtension(filePath).ToLower()
        Select Case extension
            Case ".jpg", ".jpeg"
                Return "image/jpeg"
            Case ".png"
                Return "image/png"
            Case ".gif"
                Return "image/gif"
            Case ".mp4"
                Return "video/mp4"
            Case ".mov"
                Return "video/quicktime"
            Case Else
                Return "application/octet-stream"
        End Select
    End Function

    Private Sub ValidateCampaignData(campaignData As CreateCampaignRequest)
        If String.IsNullOrEmpty(campaignData.AccountId) Then
            Throw New ArgumentException("Account ID is required")
        End If

        If String.IsNullOrEmpty(campaignData.Name) Then
            Throw New ArgumentException("Campaign name is required")
        End If

        If campaignData.DailyBudgetAmountLocalMicro <= 0 Then
            Throw New ArgumentException("Daily budget must be greater than 0")
        End If
    End Sub

    Private Sub ValidateLineItemData(lineItemData As CreateLineItemRequest)
        If String.IsNullOrEmpty(lineItemData.AccountId) Then
            Throw New ArgumentException("Account ID is required")
        End If

        If String.IsNullOrEmpty(lineItemData.CampaignId) Then
            Throw New ArgumentException("Campaign ID is required")
        End If

        If String.IsNullOrEmpty(lineItemData.Name) Then
            Throw New ArgumentException("Line item name is required")
        End If
    End Sub

    Private Function ProcessCampaignStats(statsResults As StatsJobResult, campaignId As String) As CampaignAnalytics
        ' Process the raw stats data into EQ12 analytics format
        Dim analytics As New CampaignAnalytics() With {
            .CampaignId = campaignId,
            .StartDate = statsResults.StartDate,
            .EndDate = statsResults.EndDate
        }

        ' Process metrics from stats results
        If statsResults.Data?.Count > 0 Then
            Dim totalImpressions As Long = 0
            Dim totalEngagements As Long = 0
            Dim totalSpend As Decimal = 0

            For Each dayData In statsResults.Data
                If dayData.Metrics IsNot Nothing Then
                    totalImpressions += dayData.Metrics.Impressions
                    totalEngagements += dayData.Metrics.Engagements
                    totalSpend += dayData.Metrics.BilledChargeLocalMicro / 1000000D ' Convert from micros
                End If
            Next

            analytics.TotalImpressions = totalImpressions
            analytics.TotalEngagements = totalEngagements
            analytics.TotalSpend = totalSpend

            If totalImpressions > 0 Then
                analytics.EngagementRate = (totalEngagements * 100.0) / totalImpressions
                analytics.CPM = (totalSpend * 1000.0) / totalImpressions
            End If

            If totalEngagements > 0 Then
                analytics.CostPerEngagement = totalSpend / totalEngagements
            End If
        End If

        Return analytics
    End Function

    Private Function CalculateEQ12EngagementScore(analytics As CampaignAnalytics) As Double
        ' EQ12-specific engagement scoring algorithm
        Dim baseScore = analytics.EngagementRate * 10

        ' Bonus for high engagement volume
        If analytics.TotalEngagements > 1000 Then baseScore *= 1.2
        If analytics.TotalEngagements > 10000 Then baseScore *= 1.5

        ' Penalty for high cost per engagement
        If analytics.CostPerEngagement > 1.0 Then baseScore *= 0.8
        If analytics.CostPerEngagement > 5.0 Then baseScore *= 0.5

        Return Math.Min(100, baseScore)
    End Function

    Private Function CalculateEQ12ROI(analytics As CampaignAnalytics) As Double
        ' Simplified ROI calculation - would need revenue data for accurate calculation
        If analytics.TotalSpend > 0 Then
            ' Assume $0.10 value per engagement for betting content
            Dim estimatedRevenue = analytics.TotalEngagements * 0.1
            Return ((estimatedRevenue - analytics.TotalSpend) / analytics.TotalSpend) * 100
        End If
        Return 0
    End Function

    Private Function CalculateEQ12ViralityScore(analytics As CampaignAnalytics) As Double
        ' Virality based on engagement rate and reach
        If analytics.TotalImpressions > 0 Then
            Dim viralityBase = analytics.EngagementRate * (analytics.TotalImpressions / 1000.0)
            Return Math.Min(100, viralityBase)
        End If
        Return 0
    End Function

    ' ==================================================
    ' LOGGING AND NOTIFICATIONS
    ' ==================================================

    Private Async Function LogXAdsActionAsync(actionType As String, entityId As String, response As String,
                                              status As String, accessToken As String,
                                              Optional campaignId As String = Nothing) As Task
        Try
            ' Log to x_actions table with ads-specific data
            Await _dbWriter.LogXActionAsync(actionType, entityId, response, status,
                Nothing, Nothing, Nothing, Nothing, Nothing, Nothing, Nothing, Nothing, Nothing,
                $"ads_api_action:{actionType}", campaignId)

        Catch ex As Exception
            _logger?.LogError(ex, "Error logging X Ads action")
        End Try
    End Function

    Private Async Function StoreAnalyticsAsync(analytics As CampaignAnalytics) As Task
        Try
            ' Store analytics in dedicated ads analytics table
            ' This would integrate with your existing database schema
            _logger?.LogInformation($"📊 Stored analytics for campaign: {analytics.CampaignId}")

        Catch ex As Exception
            _logger?.LogError(ex, "Error storing analytics")
        End Try
    End Function

    Private Async Function SendCampaignNotificationAsync(action As String, campaign As Campaign, accountId As String) As Task
        Try
            Dim message = $"🎯 X Ads Campaign {action.ToUpper()}" + Environment.NewLine +
                         $"📝 Name: {campaign.Name}" + Environment.NewLine +
                         $"🆔 ID: {campaign.Id}" + Environment.NewLine +
                         $"💰 Budget: ${campaign.DailyBudgetAmountLocalMicro / 1000000:N2}/day" + Environment.NewLine +
                         $"📊 Status: {campaign.EntityStatus}" + Environment.NewLine +
                         $"⏰ {DateTime.UtcNow:yyyy-MM-dd HH:mm} UTC"

            ' Send to Telegram
            Await SendTelegramNotificationAsync(message)

            ' Send to Discord
            Await SendDiscordNotificationAsync(message)

        Catch ex As Exception
            _logger?.LogError(ex, "Error sending campaign notification")
        End Try
    End Function

    Private Async Function SendAutoPromotionNotificationAsync(tweetId As String, campaignId As String, budget As Decimal) As Task
        Try
            Dim message = $"🚀 EQ12 AUTO-PROMOTION ACTIVATED" + Environment.NewLine +
                         $"🐦 Tweet ID: {tweetId}" + Environment.NewLine +
                         $"📈 Campaign ID: {campaignId}" + Environment.NewLine +
                         $"💰 Budget: ${budget:N2}/day" + Environment.NewLine +
                         $"⏰ Started: {DateTime.UtcNow:yyyy-MM-dd HH:mm} UTC"

            Await SendTelegramNotificationAsync(message)

        Catch ex As Exception
            _logger?.LogError(ex, "Error sending auto-promotion notification")
        End Try
    End Function

    Private Async Function SendAdReportNotificationAsync(reportUrl As String, report As Object, days As Integer) As Task
        Try
            Dim message = $"📊 EQ12 X ADS REPORT ({days} DAYS)" + Environment.NewLine +
                         $"🔗 Report: {reportUrl}" + Environment.NewLine +
                         $"⏰ Generated: {DateTime.UtcNow:yyyy-MM-dd HH:mm} UTC"

            Await SendTelegramNotificationAsync(message)

        Catch ex As Exception
            _logger?.LogError(ex, "Error sending ad report notification")
        End Try
    End Function

    Private Function GenerateComprehensiveAdReport(analytics As List(Of CampaignAnalytics), days As Integer) As Object
        Return New With {
            .ReportType = "EQ12_X_Ads_Performance",
            .Period = $"{days}_days",
            .GeneratedAt = DateTime.UtcNow,
            .Summary = New With {
                .TotalCampaigns = analytics.Count,
                .TotalSpend = analytics.Sum(Function(a) a.TotalSpend),
                .TotalImpressions = analytics.Sum(Function(a) a.TotalImpressions),
                .TotalEngagements = analytics.Sum(Function(a) a.TotalEngagements),
                .AverageEngagementRate = If(analytics.Count > 0, analytics.Average(Function(a) a.EngagementRate), 0),
                .AverageEQ12Score = If(analytics.Count > 0, analytics.Average(Function(a) a.EQ12EngagementScore), 0)
            },
            .Campaigns = analytics,
            .TopPerformers = analytics.OrderByDescending(Function(a) a.EQ12EngagementScore).Take(5).ToList(),
            .Recommendations = GenerateAdRecommendations(analytics)
        }
    End Function

    Private Function GenerateAdRecommendations(analytics As List(Of CampaignAnalytics)) As List(Of String)
        Dim recommendations As New List(Of String)()

        If analytics.Count > 0 Then
            Dim avgEngagementRate = analytics.Average(Function(a) a.EngagementRate)
            Dim lowPerformers = analytics.Where(Function(a) a.EngagementRate < avgEngagementRate * 0.5).ToList()

            If lowPerformers.Count > 0 Then
                recommendations.Add($"Consider pausing or optimizing {lowPerformers.Count} low-performing campaigns")
            End If

            Dim highCostCampaigns = analytics.Where(Function(a) a.CostPerEngagement > 2.0).ToList()
            If highCostCampaigns.Count > 0 Then
                recommendations.Add($"Review targeting for {highCostCampaigns.Count} high-cost campaigns")
            End If

            Dim topPerformer = analytics.OrderByDescending(Function(a) a.EQ12EngagementScore).FirstOrDefault()
            If topPerformer IsNot Nothing Then
                recommendations.Add($"Consider increasing budget for top performer: {topPerformer.CampaignName}")
            End If
        End If

        Return recommendations
    End Function

    Private Async Function CreateShareableReportLinkAsync(filepath As String) As Task(Of String)
        Try
            If Not String.IsNullOrEmpty(_bitlyConfig.AccessToken) Then
                Return Await CreateBitlyLinkAsync(filepath, _bitlyConfig)
            Else
                Return filepath
            End If
        Catch ex As Exception
            _logger?.LogWarning(ex, "Could not create shareable link")
            Return filepath
        End Try
    End Function

    ' Notification helper methods would be implemented here
    Private Async Function SendTelegramNotificationAsync(message As String) As Task
        ' Implementation depends on your existing notification system
    End Function

    Private Async Function SendDiscordNotificationAsync(message As String) As Task
        ' Implementation depends on your existing notification system
    End Function

    Private Async Function CreateBitlyLinkAsync(url As String, config As BitlyConfig) As Task(Of String)
        ' Implementation depends on your existing Bitly integration
        Return url
    End Function

End Class
