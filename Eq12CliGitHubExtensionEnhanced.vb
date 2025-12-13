' EQ12 Complete CLI X API Extension v3.0 - Production Ready
' Pre-generated for immediate deployment with full GitHub integration support
' Enhanced Eq12CliGitHubExtension.vb with comprehensive X API command suite

Imports System
Imports System.IO
Imports System.Text
Imports System.Threading.Tasks
Imports System.Collections.Generic
Imports System.Text.Json
Imports System.Globalization
Imports System.Linq
Imports System.Text.RegularExpressions
Imports System.Net.Http
Imports Microsoft.Extensions.Configuration
Imports Microsoft.Extensions.Logging

' Enhanced CLI Extension with complete X API command suite
Partial Public Class Eq12CliGitHubExtension

    ' ==================================================
    ' ENHANCED X API COMMAND HANDLERS - Production Ready
    ' ==================================================

    ''' <summary>
    ''' Enhanced x-post command with media support, OAuth handling, and GitHub integration
    ''' Usage: eq12 x-post "Your tweet content" --media "path/to/image.jpg,path/to/video.mp4" --oauth-user "username" --thread-count 3 --schedule "2024-01-01T12:00:00Z"
    ''' </summary>
    Public Async Function HandleXPostEnhancedCommand(args As String()) As Task(Of Integer)
        Try
            _logger?.LogInformation("???? Starting enhanced x-post command")

            ' Parse enhanced arguments
            Dim parsedArgs = ParseXPostEnhancedArgs(args)

            ' Validate required parameters
            If String.IsNullOrWhiteSpace(parsedArgs.Content) AndAlso parsedArgs.MediaPaths?.Count = 0 Then
                Console.WriteLine("??? Error: Either content text or media files are required")
                Console.WriteLine("Usage: eq12 x-post ""Your tweet content"" --media ""path/to/image.jpg"" --oauth-user ""username""")
                Return 1
            End If

            ' Initialize OAuth token manager
            Dim tokenManager As New OAuth2TokenManager()
            Dim token = Await tokenManager.GetValidTokenAsync(parsedArgs.OAuthUser)

            If token Is Nothing Then
                Console.WriteLine($"??? Error: No valid OAuth token found for user '{parsedArgs.OAuthUser}'")
                Console.WriteLine("???? Tip: Run 'eq12 x-oauth-setup' to configure OAuth tokens")
                Return 1
            End If

            ' Initialize enhanced XClient
            Dim xClient As New XClient()

            ' Handle media uploads if specified
            Dim mediaIds As New List(Of String)()
            If parsedArgs.MediaPaths?.Count > 0 Then
                Console.WriteLine($"???? Uploading {parsedArgs.MediaPaths.Count} media file(s)...")

                For Each mediaPath In parsedArgs.MediaPaths
                    If Not File.Exists(mediaPath) Then
                        Console.WriteLine($"??? Error: Media file not found: {mediaPath}")
                        Return 1
                    End If

                    Console.WriteLine($"?????? Uploading: {Path.GetFileName(mediaPath)}")
                    Dim mediaId = Await xClient.UploadMediaAsync(mediaPath, token.access_token, parsedArgs.AltText)

                    If Not String.IsNullOrEmpty(mediaId) Then
                        mediaIds.Add(mediaId)
                        Console.WriteLine($"??? Media uploaded successfully: {mediaId}")
                    Else
                        Console.WriteLine($"??? Failed to upload media: {mediaPath}")
                        Return 1
                    End If
                Next
            End If

            ' Post tweet or thread
            Dim result As Object
            If parsedArgs.ThreadCount > 1 Then
                ' Handle thread posting
                Console.WriteLine($"???? Creating thread with {parsedArgs.ThreadCount} tweets...")

                Dim threadContent = SplitContentForThread(parsedArgs.Content, parsedArgs.ThreadCount)

                ' Add media to first tweet only (X limitation)
                result = Await xClient.PostThreadAsync(threadContent, token.access_token,
                    If(mediaIds.Count > 0, mediaIds, Nothing), parsedArgs.ReplySettings)
            Else
                ' Handle single tweet
                Console.WriteLine("???? Posting tweet...")

                result = Await xClient.PostTweetAsync(parsedArgs.Content, token.access_token,
                    If(mediaIds.Count > 0, mediaIds, Nothing), parsedArgs.ReplySettings,
                    parsedArgs.QuoteTweetId, parsedArgs.ReplyToTweetId)
            End If

            ' Handle scheduling if specified
            If parsedArgs.ScheduledFor.HasValue Then
                Console.WriteLine($"??? Tweet scheduled for: {parsedArgs.ScheduledFor.Value:yyyy-MM-dd HH:mm:ss UTC}")
                ' Note: X API doesn't support scheduling directly, this would be handled by EQ12 scheduler
                Await ScheduleTweetAsync(parsedArgs, token.access_token, mediaIds)
            End If

            ' Process result
            If result IsNot Nothing Then
                Dim tweetData = JsonSerializer.Deserialize(Of Dictionary(Of String, Object))(result.ToString())
                Dim tweetId = tweetData("data").AsJsonElement().GetProperty("id").GetString()

                Console.WriteLine($"??? Tweet posted successfully!")
                Console.WriteLine($"???? Tweet ID: {tweetId}")
                Console.WriteLine($"???? URL: https://x.com/{token.username}/status/{tweetId}")

                ' Log to database with enhanced metadata
                Await LogEnhancedXActionAsync("post", parsedArgs.Content, result.ToString(),
                    tweetId, token.id, parsedArgs.GitHubRepo, parsedArgs.IntegrationContext)

                ' Send alerts if configured
                If parsedArgs.SendAlerts Then
                    Await SendPostSuccessAlertsAsync(tweetId, parsedArgs.Content, token.username)
                End If

                ' Trigger engagement monitoring
                If parsedArgs.MonitorEngagement Then
                    Await StartEngagementMonitoringAsync(tweetId)
                End If

                Return 0
            Else
                Console.WriteLine("??? Failed to post tweet")
                Return 1
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error in HandleXPostEnhancedCommand")
            Console.WriteLine($"??? Error: {ex.Message}")
            Return 1
        End Try
    End Function

    ''' <summary>
    ''' Enhanced x-thread command with advanced threading capabilities
    ''' Usage: eq12 x-thread "Thread content here..." --split-auto --media-first "image.jpg" --oauth-user "username"
    ''' </summary>
    Public Async Function HandleXThreadEnhancedCommand(args As String()) As Task(Of Integer)
        Try
            _logger?.LogInformation("???? Starting enhanced x-thread command")

            Dim parsedArgs = ParseXThreadEnhancedArgs(args)

            If String.IsNullOrWhiteSpace(parsedArgs.Content) Then
                Console.WriteLine("??? Error: Thread content is required")
                Console.WriteLine("Usage: eq12 x-thread ""Your thread content..."" --oauth-user ""username""")
                Return 1
            End If

            ' Initialize OAuth token manager
            Dim tokenManager As New OAuth2TokenManager()
            Dim token = Await tokenManager.GetValidTokenAsync(parsedArgs.OAuthUser)

            If token Is Nothing Then
                Console.WriteLine($"??? Error: No valid OAuth token found for user '{parsedArgs.OAuthUser}'")
                Return 1
            End If

            ' Initialize enhanced XClient
            Dim xClient As New XClient()

            ' Smart thread splitting
            Dim threadTweets As List(Of String)
            If parsedArgs.SplitAuto Then
                threadTweets = SmartSplitThread(parsedArgs.Content, parsedArgs.MaxTweetLength)
            Else
                threadTweets = parsedArgs.Content.Split(New String() {parsedArgs.ThreadSeparator}, StringSplitOptions.RemoveEmptyEntries).ToList()
            End If

            Console.WriteLine($"???? Creating thread with {threadTweets.Count} tweets...")

            ' Handle media for first tweet
            Dim mediaIds As List(Of String) = Nothing
            If Not String.IsNullOrEmpty(parsedArgs.MediaFirstTweet) AndAlso File.Exists(parsedArgs.MediaFirstTweet) Then
                Console.WriteLine($"?????? Uploading media for first tweet: {Path.GetFileName(parsedArgs.MediaFirstTweet)}")
                Dim mediaId = Await xClient.UploadMediaAsync(parsedArgs.MediaFirstTweet, token.access_token)
                If Not String.IsNullOrEmpty(mediaId) Then
                    mediaIds = New List(Of String) From {mediaId}
                End If
            End If

            ' Post thread with enhanced error handling and retry logic
            Dim result = Await xClient.PostThreadEnhancedAsync(threadTweets, token.access_token,
                mediaIds, parsedArgs.ReplySettings, parsedArgs.ThreadDelay)

            If result IsNot Nothing AndAlso result.Count > 0 Then
                Console.WriteLine($"??? Thread posted successfully with {result.Count} tweets!")

                For i = 0 To result.Count - 1
                    Dim tweetData = JsonSerializer.Deserialize(Of Dictionary(Of String, Object))(result(i).ToString())
                    Dim tweetId = tweetData("data").AsJsonElement().GetProperty("id").GetString()
                    Console.WriteLine($"???? Tweet {i + 1}: https://x.com/{token.username}/status/{tweetId}")

                    ' Log each tweet in thread
                    Await LogEnhancedXActionAsync("thread", threadTweets(i), result(i).ToString(),
                        tweetId, token.id, parsedArgs.GitHubRepo, parsedArgs.IntegrationContext, i.ToString())
                Next

                ' Send thread completion alerts
                If parsedArgs.SendAlerts Then
                    Await SendThreadSuccessAlertsAsync(result, token.username, threadTweets.Count)
                End If

                Return 0
            Else
                Console.WriteLine("??? Failed to post thread")
                Return 1
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error in HandleXThreadEnhancedCommand")
            Console.WriteLine($"??? Error: {ex.Message}")
            Return 1
        End Try
    End Function

    ''' <summary>
    ''' Enhanced x-search command with advanced filtering and export options
    ''' Usage: eq12 x-search "betting odds" --max-results 100 --export-json --sentiment-analysis --oauth-user "username"
    ''' </summary>
    Public Async Function HandleXSearchEnhancedCommand(args As String()) As Task(Of Integer)
        Try
            _logger?.LogInformation("???? Starting enhanced x-search command")

            Dim parsedArgs = ParseXSearchEnhancedArgs(args)

            If String.IsNullOrWhiteSpace(parsedArgs.Query) Then
                Console.WriteLine("??? Error: Search query is required")
                Console.WriteLine("Usage: eq12 x-search ""your search query"" --max-results 100")
                Return 1
            End If

            ' Initialize OAuth token manager
            Dim tokenManager As New OAuth2TokenManager()
            Dim token = Await tokenManager.GetValidTokenAsync(parsedArgs.OAuthUser)

            If token Is Nothing Then
                Console.WriteLine($"??? Error: No valid OAuth token found for user '{parsedArgs.OAuthUser}'")
                Return 1
            End If

            ' Initialize enhanced XClient
            Dim xClient As New XClient()

            Console.WriteLine($"???? Searching for: ""{parsedArgs.Query}""")
            Console.WriteLine($"???? Max results: {parsedArgs.MaxResults}")
            If parsedArgs.StartTime.HasValue Then
                Console.WriteLine($"???? Start time: {parsedArgs.StartTime.Value:yyyy-MM-dd HH:mm:ss UTC}")
            End If
            If parsedArgs.EndTime.HasValue Then
                Console.WriteLine($"???? End time: {parsedArgs.EndTime.Value:yyyy-MM-dd HH:mm:ss UTC}")
            End If

            ' Build enhanced search parameters
            Dim searchParams As New Dictionary(Of String, Object) From {
                {"query", parsedArgs.Query},
                {"max_results", parsedArgs.MaxResults},
                {"tweet.fields", "id,text,author_id,created_at,public_metrics,context_annotations,entities,geo,in_reply_to_user_id,lang,possibly_sensitive,referenced_tweets,reply_settings,source,withheld"},
                {"expansions", "author_id,referenced_tweets.id,attachments.media_keys,geo.place_id"},
                {"user.fields", "id,name,username,created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,verified_type,withheld"},
                {"media.fields", "duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics"},
                {"place.fields", "contained_within,country,country_code,full_name,geo,id,name,place_type"}
            }

            ' Add time filters if specified
            If parsedArgs.StartTime.HasValue Then
                searchParams("start_time") = parsedArgs.StartTime.Value.ToString("yyyy-MM-ddTHH:mm:ssZ")
            End If
            If parsedArgs.EndTime.HasValue Then
                searchParams("end_time") = parsedArgs.EndTime.Value.ToString("yyyy-MM-ddTHH:mm:ssZ")
            End If

            ' Execute search with enhanced error handling
            Dim results = Await xClient.SearchTweetsEnhancedAsync(searchParams, token.access_token)

            If results IsNot Nothing Then
                Dim searchData = JsonSerializer.Deserialize(Of Dictionary(Of String, Object))(results.ToString())

                ' Process and display results
                Dim tweets As JsonElement
                If searchData.ContainsKey("data") Then
                    tweets = searchData("data").AsJsonElement()

                    Console.WriteLine($"??? Found {tweets.GetArrayLength()} tweets")
                    Console.WriteLine("" + New String("="c, 80))

                    Dim tweetsList As New List(Of Dictionary(Of String, Object))()

                    For Each tweet In tweets.EnumerateArray()
                        Dim tweetDict = JsonSerializer.Deserialize(Of Dictionary(Of String, Object))(tweet.GetRawText())
                        tweetsList.Add(tweetDict)

                        ' Display tweet info
                        Dim tweetId = tweet.GetProperty("id").GetString()
                        Dim text = tweet.GetProperty("text").GetString()
                        Dim createdAt = tweet.GetProperty("created_at").GetString()

                        Console.WriteLine($"???? Tweet ID: {tweetId}")
                        Console.WriteLine($"???? Created: {createdAt}")
                        Console.WriteLine($"???? Text: {text}")

                        ' Show public metrics if available
                        If tweet.TryGetProperty("public_metrics", out Dim metrics) Then
                            Console.WriteLine($"???? Metrics: ??????{metrics.GetProperty("like_count")} ????{metrics.GetProperty("retweet_count")} ????{metrics.GetProperty("reply_count")}")
                        End If

                        Console.WriteLine("")
                    Next

                    ' Export options
                    If parsedArgs.ExportJson Then
                        Await ExportSearchResultsAsync(tweetsList, "json", parsedArgs.Query)
                    End If

                    If parsedArgs.ExportCsv Then
                        Await ExportSearchResultsAsync(tweetsList, "csv", parsedArgs.Query)
                    End If

                    ' Sentiment analysis if requested
                    If parsedArgs.SentimentAnalysis Then
                        Await PerformSentimentAnalysisAsync(tweetsList)
                    End If

                    ' Save to database with enhanced metadata
                    Await LogEnhancedXActionAsync("search", parsedArgs.Query, results.ToString(),
                        Nothing, token.id, parsedArgs.GitHubRepo, parsedArgs.IntegrationContext, tweetsList.Count.ToString())

                    Console.WriteLine($"??? Search completed. {tweets.GetArrayLength()} tweets processed.")
                    Return 0
                Else
                    Console.WriteLine("?????? No tweets found matching your search criteria")
                    Return 0
                End If
            Else
                Console.WriteLine("??? Search failed")
                Return 1
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error in HandleXSearchEnhancedCommand")
            Console.WriteLine($"??? Error: {ex.Message}")
            Return 1
        End Try
    End Function

    ''' <summary>
    ''' New x-media command for media-only operations
    ''' Usage: eq12 x-media upload "path/to/video.mp4" --alt-text "Description" --category "tweet_video"
    ''' </summary>
    Public Async Function HandleXMediaCommand(args As String()) As Task(Of Integer)
        Try
            _logger?.LogInformation("???? Starting x-media command")

            If args.Length < 2 Then
                ShowXMediaUsage()
                Return 1
            End If

            Dim subCommand = args(1).ToLower()

            Select Case subCommand
                Case "upload"
                    Return Await HandleXMediaUploadCommand(args)
                Case "list"
                    Return Await HandleXMediaListCommand(args)
                Case "delete"
                    Return Await HandleXMediaDeleteCommand(args)
                Case Else
                    Console.WriteLine($"??? Unknown media subcommand: {subCommand}")
                    ShowXMediaUsage()
                    Return 1
            End Select

        Catch ex As Exception
            _logger?.LogError(ex, "Error in HandleXMediaCommand")
            Console.WriteLine($"??? Error: {ex.Message}")
            Return 1
        End Try
    End Function

    ''' <summary>
    ''' New x-oauth command for OAuth token management
    ''' Usage: eq12 x-oauth setup --client-id "your_client_id" --redirect-uri "http://localhost:3000/callback"
    ''' </summary>
    Public Async Function HandleXOAuthCommand(args As String()) As Task(Of Integer)
        Try
            _logger?.LogInformation("???? Starting x-oauth command")

            If args.Length < 2 Then
                ShowXOAuthUsage()
                Return 1
            End If

            Dim subCommand = args(1).ToLower()

            Select Case subCommand
                Case "setup"
                    Return Await HandleXOAuthSetupCommand(args)
                Case "refresh"
                    Return Await HandleXOAuthRefreshCommand(args)
                Case "revoke"
                    Return Await HandleXOAuthRevokeCommand(args)
                Case "list"
                    Return Await HandleXOAuthListCommand(args)
                Case "validate"
                    Return Await HandleXOAuthValidateCommand(args)
                Case Else
                    Console.WriteLine($"??? Unknown OAuth subcommand: {subCommand}")
                    ShowXOAuthUsage()
                    Return 1
            End Select

        Catch ex As Exception
            _logger?.LogError(ex, "Error in HandleXOAuthCommand")
            Console.WriteLine($"??? Error: {ex.Message}")
            Return 1
        End Try
    End Function

    ''' <summary>
    ''' New x-monitor command for real-time engagement monitoring
    ''' Usage: eq12 x-monitor start --tweet-id "1234567890" --duration 3600 --alerts
    ''' </summary>
    Public Async Function HandleXMonitorCommand(args As String()) As Task(Of Integer)
        Try
            _logger?.LogInformation("???? Starting x-monitor command")

            If args.Length < 2 Then
                ShowXMonitorUsage()
                Return 1
            End If

            Dim subCommand = args(1).ToLower()

            Select Case subCommand
                Case "start"
                    Return Await HandleXMonitorStartCommand(args)
                Case "stop"
                    Return Await HandleXMonitorStopCommand(args)
                Case "status"
                    Return Await HandleXMonitorStatusCommand(args)
                Case "report"
                    Return Await HandleXMonitorReportCommand(args)
                Case Else
                    Console.WriteLine($"??? Unknown monitor subcommand: {subCommand}")
                    ShowXMonitorUsage()
                    Return 1
            End Select

        Catch ex As Exception
            _logger?.LogError(ex, "Error in HandleXMonitorCommand")
            Console.WriteLine($"??? Error: {ex.Message}")
            Return 1
        End Try
    End Function

    ''' <summary>
    ''' Enhanced x-github-integrate command for seamless repository integration
    ''' Usage: eq12 x-github-integrate --repo "owner/repo" --extract-samples --auto-setup --deploy
    ''' </summary>
    Public Async Function HandleXGitHubIntegrateEnhancedCommand(args As String()) As Task(Of Integer)
        Try
            _logger?.LogInformation("???? Starting enhanced x-github-integrate command")

            Dim parsedArgs = ParseXGitHubIntegrateArgs(args)

            If String.IsNullOrWhiteSpace(parsedArgs.RepoFullName) Then
                Console.WriteLine("??? Error: Repository name is required")
                Console.WriteLine("Usage: eq12 x-github-integrate --repo ""owner/repo"" --extract-samples")
                Return 1
            End If

            ' Initialize GitHub integration components
            Dim gitHubSearcher As New XApiGitHubAutoSearcher()
            Dim xClient As New XClient()

            Console.WriteLine($"???? Analyzing repository: {parsedArgs.RepoFullName}")

            ' Analyze repository for X API integration potential
            Dim repoAnalysis = Await gitHubSearcher.AnalyzeRepositoryAsync(parsedArgs.RepoFullName)

            If repoAnalysis Is Nothing Then
                Console.WriteLine($"??? Error: Could not analyze repository {parsedArgs.RepoFullName}")
                Return 1
            End If

            Console.WriteLine($"??? Repository analysis complete")
            Console.WriteLine($"???? Integration potential: {repoAnalysis.IntegrationPotential:P1}")
            Console.WriteLine($"???? Primary language: {repoAnalysis.Language}")
            Console.WriteLine($"??? Stars: {repoAnalysis.Stars}")

            ' Extract code samples if requested
            If parsedArgs.ExtractSamples Then
                Console.WriteLine("???? Extracting X API code samples...")

                Dim codeSamples = Await gitHubSearcher.ExtractCodeSamplesAsync(parsedArgs.RepoFullName)

                If codeSamples?.Count > 0 Then
                    Console.WriteLine($"??? Found {codeSamples.Count} code samples")

                    For Each sample In codeSamples
                        Console.WriteLine($"???? Sample: {sample.SampleType} in {sample.Language}")
                        Console.WriteLine($"   File: {sample.FilePath}")
                        Console.WriteLine($"   Quality Score: {sample.QualityScore:F2}")

                        If parsedArgs.ShowCode Then
                            Console.WriteLine($"   Code Preview:")
                            Console.WriteLine($"   {sample.CodeSnippet.Substring(0, Math.Min(200, sample.CodeSnippet.Length))}...")
                            Console.WriteLine("")
                        End If
                    Next

                    ' Save samples to database
                    Await SaveCodeSamplesToDatabaseAsync(repoAnalysis.Id, codeSamples)
                Else
                    Console.WriteLine("?????? No X API code samples found in repository")
                End If
            End If

            ' Auto-setup integration if requested
            If parsedArgs.AutoSetup Then
                Console.WriteLine("?????? Setting up automatic integration...")

                Dim setupResult = Await SetupRepositoryIntegrationAsync(repoAnalysis, parsedArgs)

                If setupResult Then
                    Console.WriteLine("??? Integration setup completed successfully")
                Else
                    Console.WriteLine("??? Integration setup failed")
                    Return 1
                End If
            End If

            ' Deploy integration if requested
            If parsedArgs.Deploy Then
                Console.WriteLine("???? Deploying integration...")

                Dim deployResult = Await DeployRepositoryIntegrationAsync(repoAnalysis, parsedArgs)

                If deployResult Then
                    Console.WriteLine("??? Integration deployed successfully")

                    ' Log successful integration
                    Await LogEnhancedXActionAsync("github_integrate", parsedArgs.RepoFullName,
                        JsonSerializer.Serialize(repoAnalysis), Nothing, Nothing,
                        parsedArgs.RepoFullName, $"auto_setup:{parsedArgs.AutoSetup},deploy:true")
                Else
                    Console.WriteLine("??? Integration deployment failed")
                    Return 1
                End If
            End If

            ' Update repository status in database
            Await UpdateRepositoryIntegrationStatusAsync(parsedArgs.RepoFullName,
                If(parsedArgs.Deploy, "deployed", If(parsedArgs.AutoSetup, "configured", "analyzed")))

            Console.WriteLine($"??? GitHub integration command completed successfully")
            Return 0

        Catch ex As Exception
            _logger?.LogError(ex, "Error in HandleXGitHubIntegrateEnhancedCommand")
            Console.WriteLine($"??? Error: {ex.Message}")
            Return 1
        End Try
    End Function

    ' ==================================================
    ' ARGUMENT PARSING STRUCTURES AND METHODS
    ' ==================================================

    Private Structure XPostEnhancedArgs
        Public Content As String
        Public MediaPaths As List(Of String)
        Public AltText As String
        Public OAuthUser As String
        Public ThreadCount As Integer
        Public ReplySettings As String
        Public QuoteTweetId As String
        Public ReplyToTweetId As String
        Public ScheduledFor As DateTime?
        Public SendAlerts As Boolean
        Public MonitorEngagement As Boolean
        Public GitHubRepo As String
        Public IntegrationContext As String
    End Structure

    Private Structure XThreadEnhancedArgs
        Public Content As String
        Public SplitAuto As Boolean
        Public MaxTweetLength As Integer
        Public ThreadSeparator As String
        Public MediaFirstTweet As String
        Public OAuthUser As String
        Public ReplySettings As String
        Public ThreadDelay As Integer
        Public SendAlerts As Boolean
        Public GitHubRepo As String
        Public IntegrationContext As String
    End Structure

    Private Structure XSearchEnhancedArgs
        Public Query As String
        Public MaxResults As Integer
        Public StartTime As DateTime?
        Public EndTime As DateTime?
        Public OAuthUser As String
        Public ExportJson As Boolean
        Public ExportCsv As Boolean
        Public SentimentAnalysis As Boolean
        Public GitHubRepo As String
        Public IntegrationContext As String
    End Structure

    Private Structure XGitHubIntegrateArgs
        Public RepoFullName As String
        Public ExtractSamples As Boolean
        Public ShowCode As Boolean
        Public AutoSetup As Boolean
        Public Deploy As Boolean
        Public ConfigFile As String
        Public Branch As String
    End Structure

    Private Function ParseXPostEnhancedArgs(args As String()) As XPostEnhancedArgs
        Dim result As New XPostEnhancedArgs With {
            .ThreadCount = 1,
            .ReplySettings = "everyone",
            .OAuthUser = "default"
        }

        For i = 0 To args.Length - 1
            Select Case args(i).ToLower()
                Case "--media"
                    If i + 1 < args.Length Then
                        result.MediaPaths = args(i + 1).Split(","c).ToList()
                        i += 1
                    End If
                Case "--alt-text"
                    If i + 1 < args.Length Then
                        result.AltText = args(i + 1)
                        i += 1
                    End If
                Case "--oauth-user"
                    If i + 1 < args.Length Then
                        result.OAuthUser = args(i + 1)
                        i += 1
                    End If
                Case "--thread-count"
                    If i + 1 < args.Length AndAlso Integer.TryParse(args(i + 1), result.ThreadCount) Then
                        i += 1
                    End If
                Case "--reply-settings"
                    If i + 1 < args.Length Then
                        result.ReplySettings = args(i + 1)
                        i += 1
                    End If
                Case "--quote-tweet"
                    If i + 1 < args.Length Then
                        result.QuoteTweetId = args(i + 1)
                        i += 1
                    End If
                Case "--reply-to"
                    If i + 1 < args.Length Then
                        result.ReplyToTweetId = args(i + 1)
                        i += 1
                    End If
                Case "--schedule"
                    If i + 1 < args.Length AndAlso DateTime.TryParse(args(i + 1), result.ScheduledFor) Then
                        i += 1
                    End If
                Case "--alerts"
                    result.SendAlerts = True
                Case "--monitor"
                    result.MonitorEngagement = True
                Case "--github-repo"
                    If i + 1 < args.Length Then
                        result.GitHubRepo = args(i + 1)
                        i += 1
                    End If
                Case "--integration-context"
                    If i + 1 < args.Length Then
                        result.IntegrationContext = args(i + 1)
                        i += 1
                    End If
                Case Else
                    If Not args(i).StartsWith("--") AndAlso String.IsNullOrEmpty(result.Content) Then
                        result.Content = args(i)
                    End If
            End Select
        Next

        Return result
    End Function

    Private Function ParseXThreadEnhancedArgs(args As String()) As XThreadEnhancedArgs
        Dim result As New XThreadEnhancedArgs With {
            .SplitAuto = False,
            .MaxTweetLength = 280,
            .ThreadSeparator = Environment.NewLine + Environment.NewLine,
            .OAuthUser = "default",
            .ReplySettings = "everyone",
            .ThreadDelay = 1000
        }

        For i = 0 To args.Length - 1
            Select Case args(i).ToLower()
                Case "--split-auto"
                    result.SplitAuto = True
                Case "--max-length"
                    If i + 1 < args.Length AndAlso Integer.TryParse(args(i + 1), result.MaxTweetLength) Then
                        i += 1
                    End If
                Case "--separator"
                    If i + 1 < args.Length Then
                        result.ThreadSeparator = args(i + 1).Replace("\n", Environment.NewLine)
                        i += 1
                    End If
                Case "--media-first"
                    If i + 1 < args.Length Then
                        result.MediaFirstTweet = args(i + 1)
                        i += 1
                    End If
                Case "--oauth-user"
                    If i + 1 < args.Length Then
                        result.OAuthUser = args(i + 1)
                        i += 1
                    End If
                Case "--delay"
                    If i + 1 < args.Length AndAlso Integer.TryParse(args(i + 1), result.ThreadDelay) Then
                        i += 1
                    End If
                Case "--alerts"
                    result.SendAlerts = True
                Case Else
                    If Not args(i).StartsWith("--") AndAlso String.IsNullOrEmpty(result.Content) Then
                        result.Content = args(i)
                    End If
            End Select
        Next

        Return result
    End Function

    Private Function ParseXSearchEnhancedArgs(args As String()) As XSearchEnhancedArgs
        Dim result As New XSearchEnhancedArgs With {
            .MaxResults = 10,
            .OAuthUser = "default"
        }

        For i = 0 To args.Length - 1
            Select Case args(i).ToLower()
                Case "--max-results"
                    If i + 1 < args.Length AndAlso Integer.TryParse(args(i + 1), result.MaxResults) Then
                        i += 1
                    End If
                Case "--start-time"
                    If i + 1 < args.Length AndAlso DateTime.TryParse(args(i + 1), result.StartTime) Then
                        i += 1
                    End If
                Case "--end-time"
                    If i + 1 < args.Length AndAlso DateTime.TryParse(args(i + 1), result.EndTime) Then
                        i += 1
                    End If
                Case "--oauth-user"
                    If i + 1 < args.Length Then
                        result.OAuthUser = args(i + 1)
                        i += 1
                    End If
                Case "--export-json"
                    result.ExportJson = True
                Case "--export-csv"
                    result.ExportCsv = True
                Case "--sentiment"
                    result.SentimentAnalysis = True
                Case "--github-repo"
                    If i + 1 < args.Length Then
                        result.GitHubRepo = args(i + 1)
                        i += 1
                    End If
                Case Else
                    If Not args(i).StartsWith("--") AndAlso String.IsNullOrEmpty(result.Query) Then
                        result.Query = args(i)
                    End If
            End Select
        Next

        Return result
    End Function

    Private Function ParseXGitHubIntegrateArgs(args As String()) As XGitHubIntegrateArgs
        Dim result As New XGitHubIntegrateArgs With {
            .Branch = "main"
        }

        For i = 0 To args.Length - 1
            Select Case args(i).ToLower()
                Case "--repo"
                    If i + 1 < args.Length Then
                        result.RepoFullName = args(i + 1)
                        i += 1
                    End If
                Case "--extract-samples"
                    result.ExtractSamples = True
                Case "--show-code"
                    result.ShowCode = True
                Case "--auto-setup"
                    result.AutoSetup = True
                Case "--deploy"
                    result.Deploy = True
                Case "--config"
                    If i + 1 < args.Length Then
                        result.ConfigFile = args(i + 1)
                        i += 1
                    End If
                Case "--branch"
                    If i + 1 < args.Length Then
                        result.Branch = args(i + 1)
                        i += 1
                    End If
            End Select
        Next

        Return result
    End Function

    ' ==================================================
    ' HELPER METHODS FOR ENHANCED FUNCTIONALITY
    ' ==================================================

    Private Function SplitContentForThread(content As String, threadCount As Integer) As List(Of String)
        Dim maxLength = 280
        Dim tweets As New List(Of String)()

        If content.Length <= maxLength Then
            tweets.Add(content)
            Return tweets
        End If

        ' Smart splitting algorithm
        Dim sentences = content.Split({".", "!", "?"}, StringSplitOptions.RemoveEmptyEntries)
        Dim currentTweet = ""

        For Each sentence In sentences
            Dim potentialTweet = If(String.IsNullOrEmpty(currentTweet), sentence.Trim(), currentTweet + ". " + sentence.Trim())

            If potentialTweet.Length <= maxLength - 10 Then ' Reserve space for thread numbering
                currentTweet = potentialTweet
            Else
                If Not String.IsNullOrEmpty(currentTweet) Then
                    tweets.Add(currentTweet + ".")
                End If
                currentTweet = sentence.Trim()
            End If
        Next

        If Not String.IsNullOrEmpty(currentTweet) Then
            tweets.Add(currentTweet + ".")
        End If

        ' Add thread numbering
        For i = 0 To tweets.Count - 1
            tweets(i) = $"????{i + 1}/{tweets.Count} {tweets(i)}"
        Next

        Return tweets
    End Function

    Private Function SmartSplitThread(content As String, maxTweetLength As Integer) As List(Of String)
        Dim tweets As New List(Of String)()
        Dim words = content.Split(" "c)
        Dim currentTweet = ""

        For Each word In words
            Dim potentialTweet = If(String.IsNullOrEmpty(currentTweet), word, currentTweet + " " + word)

            If potentialTweet.Length <= maxTweetLength - 15 Then ' Reserve space for thread numbering
                currentTweet = potentialTweet
            Else
                If Not String.IsNullOrEmpty(currentTweet) Then
                    tweets.Add(currentTweet)
                End If
                currentTweet = word
            End If
        Next

        If Not String.IsNullOrEmpty(currentTweet) Then
            tweets.Add(currentTweet)
        End If

        ' Add thread numbering
        For i = 0 To tweets.Count - 1
            tweets(i) = $"????{i + 1}/{tweets.Count} {tweets(i)}"
        Next

        Return tweets
    End Function

    Private Async Function ExportSearchResultsAsync(tweets As List(Of Dictionary(Of String, Object)), format As String, query As String) As Task
        Try
            Dim timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss")
            Dim filename = $"x_search_{query.Replace(" ", "_")}_{timestamp}.{format}"
            Dim filepath = Path.Combine("C:\EQ12\logs", filename)

            Select Case format.ToLower()
                Case "json"
                    Dim json = JsonSerializer.Serialize(tweets, New JsonSerializerOptions With {.WriteIndented = True})
                    Await File.WriteAllTextAsync(filepath, json)

                Case "csv"
                    Dim csv As New StringBuilder()
                    csv.AppendLine("tweet_id,created_at,text,author_id,like_count,retweet_count,reply_count")

                    For Each tweet In tweets
                        Dim tweetId = If(tweet.ContainsKey("id"), tweet("id").ToString(), "")
                        Dim createdAt = If(tweet.ContainsKey("created_at"), tweet("created_at").ToString(), "")
                        Dim text = If(tweet.ContainsKey("text"), tweet("text").ToString().Replace("""", """"""), "")
                        Dim authorId = If(tweet.ContainsKey("author_id"), tweet("author_id").ToString(), "")

                        Dim likeCount = "0"
                        Dim retweetCount = "0"
                        Dim replyCount = "0"

                        If tweet.ContainsKey("public_metrics") Then
                            Dim metrics = JsonSerializer.Deserialize(Of Dictionary(Of String, Object))(tweet("public_metrics").ToString())
                            likeCount = If(metrics.ContainsKey("like_count"), metrics("like_count").ToString(), "0")
                            retweetCount = If(metrics.ContainsKey("retweet_count"), metrics("retweet_count").ToString(), "0")
                            replyCount = If(metrics.ContainsKey("reply_count"), metrics("reply_count").ToString(), "0")
                        End If

                        csv.AppendLine($"""{tweetId}"",""{createdAt}"",""{text}"",""{authorId}"",""{likeCount}"",""{retweetCount}"",""{replyCount}""")
                    Next

                    Await File.WriteAllTextAsync(filepath, csv.ToString())
            End Select

            Console.WriteLine($"???? Export saved: {filepath}")

        Catch ex As Exception
            _logger?.LogError(ex, "Error exporting search results")
            Console.WriteLine($"??? Export failed: {ex.Message}")
        End Try
    End Function

    Private Async Function PerformSentimentAnalysisAsync(tweets As List(Of Dictionary(Of String, Object))) As Task
        Try
            Console.WriteLine("???? Performing sentiment analysis...")

            Dim positiveCount = 0
            Dim negativeCount = 0
            Dim neutralCount = 0

            For Each tweet In tweets
                If tweet.ContainsKey("text") Then
                    Dim text = tweet("text").ToString()
                    Dim sentiment = AnalyzeSentiment(text)

                    Select Case sentiment
                        Case "positive"
                            positiveCount += 1
                        Case "negative"
                            negativeCount += 1
                        Case Else
                            neutralCount += 1
                    End Select
                End If
            Next

            Console.WriteLine($"???? Sentiment Analysis Results:")
            Console.WriteLine($"   ???? Positive: {positiveCount} ({positiveCount * 100.0 / tweets.Count:F1}%)")
            Console.WriteLine($"   ???? Negative: {negativeCount} ({negativeCount * 100.0 / tweets.Count:F1}%)")
            Console.WriteLine($"   ???? Neutral:  {neutralCount} ({neutralCount * 100.0 / tweets.Count:F1}%)")

        Catch ex As Exception
            _logger?.LogError(ex, "Error performing sentiment analysis")
            Console.WriteLine($"??? Sentiment analysis failed: {ex.Message}")
        End Try
    End Function

    Private Function AnalyzeSentiment(text As String) As String
        ' Simple sentiment analysis (in production, use proper ML model)
        Dim positiveWords = {"good", "great", "excellent", "amazing", "love", "like", "awesome", "fantastic", "wonderful"}
        Dim negativeWords = {"bad", "terrible", "awful", "hate", "dislike", "horrible", "worst", "disappointing"}

        Dim lowerText = text.ToLower()
        Dim positiveScore = positiveWords.Count(Function(word) lowerText.Contains(word))
        Dim negativeScore = negativeWords.Count(Function(word) lowerText.Contains(word))

        If positiveScore > negativeScore Then
            Return "positive"
        ElseIf negativeScore > positiveScore Then
            Return "negative"
        Else
            Return "neutral"
        End If
    End Function

    Private Async Function LogEnhancedXActionAsync(actionType As String, content As String, response As String,
                                                   tweetId As String, tokenId As Integer?, gitHubRepo As String,
                                                   integrationContext As String, Optional metadata As String = Nothing) As Task
        Try
            ' Enhanced logging with all new fields
            Dim dbWriter As New DBWriter()

            ' Create comprehensive log entry
            Dim logData As New Dictionary(Of String, Object) From {
                {"action_type", actionType},
                {"content", content},
                {"response_data", response},
                {"tweet_id", tweetId},
                {"oauth_token_id", tokenId},
                {"github_source_repo", gitHubRepo},
                {"integration_context", integrationContext},
                {"metadata", metadata},
                {"api_version", "2.0"},
                {"client_event_source", "EQ12_CLI_Enhanced"},
                {"created_at", DateTime.UtcNow},
                {"status", "success"}
            }

            Await dbWriter.LogXActionEnhancedAsync(logData)

        Catch ex As Exception
            _logger?.LogError(ex, "Error logging enhanced X action")
        End Try
    End Function

    ' ==================================================
    ' USAGE METHODS
    ' ==================================================

    Private Sub ShowXMediaUsage()
        Console.WriteLine("???? X Media Management Commands:")
        Console.WriteLine("")
        Console.WriteLine("Usage: eq12 x-media <subcommand> [options]")
        Console.WriteLine("")
        Console.WriteLine("Subcommands:")
        Console.WriteLine("  upload    Upload media file to X")
        Console.WriteLine("  list      List uploaded media files")
        Console.WriteLine("  delete    Delete media file")
        Console.WriteLine("")
        Console.WriteLine("Upload Examples:")
        Console.WriteLine("  eq12 x-media upload ""photo.jpg"" --alt-text ""A beautiful sunset""")
        Console.WriteLine("  eq12 x-media upload ""video.mp4"" --category ""tweet_video""")
        Console.WriteLine("")
    End Sub

    Private Sub ShowXOAuthUsage()
        Console.WriteLine("???? X OAuth Management Commands:")
        Console.WriteLine("")
        Console.WriteLine("Usage: eq12 x-oauth <subcommand> [options]")
        Console.WriteLine("")
        Console.WriteLine("Subcommands:")
        Console.WriteLine("  setup     Set up new OAuth token")
        Console.WriteLine("  refresh   Refresh existing token")
        Console.WriteLine("  revoke    Revoke token")
        Console.WriteLine("  list      List all tokens")
        Console.WriteLine("  validate  Validate token")
        Console.WriteLine("")
        Console.WriteLine("Setup Example:")
        Console.WriteLine("  eq12 x-oauth setup --client-id ""your_id"" --redirect-uri ""http://localhost:3000/callback""")
        Console.WriteLine("")
    End Sub

    Private Sub ShowXMonitorUsage()
        Console.WriteLine("???? X Engagement Monitoring Commands:")
        Console.WriteLine("")
        Console.WriteLine("Usage: eq12 x-monitor <subcommand> [options]")
        Console.WriteLine("")
        Console.WriteLine("Subcommands:")
        Console.WriteLine("  start     Start monitoring tweet/user")
        Console.WriteLine("  stop      Stop monitoring")
        Console.WriteLine("  status    Check monitoring status")
        Console.WriteLine("  report    Generate monitoring report")
        Console.WriteLine("")
        Console.WriteLine("Examples:")
        Console.WriteLine("  eq12 x-monitor start --tweet-id ""1234567890"" --duration 3600")
        Console.WriteLine("  eq12 x-monitor report --tweet-id ""1234567890"" --format pdf")
        Console.WriteLine("")
    End Sub

    ' ==================================================
    ' X ADS API COMMAND HANDLERS - Production Ready
    ' ==================================================

    ''' <summary>
    ''' X Ads campaign management command
    ''' Usage: eq12 xads-campaign create "Campaign Name" --budget 100 --account-id "18ce54d4x5t"
    ''' </summary>
    Public Async Function HandleXAdsCampaignCommand(args As String()) As Task(Of Integer)
        Try
            _logger?.LogInformation("???? Starting xads-campaign command")

            If args.Length < 2 Then
                ShowXAdsCampaignUsage()
                Return 1
            End If

            Dim subCommand = args(1).ToLower()
            Dim tokenManager As New OAuth2TokenManager()
            Dim token = Await tokenManager.GetValidTokenAsync("default")

            If token Is Nothing Then
                Console.WriteLine("??? Error: No valid OAuth token found")
                Console.WriteLine("???? Tip: Run 'eq12 x-oauth setup' first")
                Return 1
            End If

            Dim xAdsClient As New XAdsClient(_logger, _config)

            Select Case subCommand
                Case "create"
                    Return Await HandleCreateCampaignCommand(args, xAdsClient, token.access_token)
                Case "list"
                    Return Await HandleListCampaignsCommand(args, xAdsClient, token.access_token)
                Case "update"
                    Return Await HandleUpdateCampaignCommand(args, xAdsClient, token.access_token)
                Case "delete"
                    Return Await HandleDeleteCampaignCommand(args, xAdsClient, token.access_token)
                Case "stats"
                    Return Await HandleCampaignStatsCommand(args, xAdsClient, token.access_token)
                Case "auto-promote"
                    Return Await HandleAutoPromoteCampaignCommand(args, xAdsClient, token.access_token)
                Case Else
                    Console.WriteLine($"??? Unknown campaign subcommand: {subCommand}")
                    ShowXAdsCampaignUsage()
                    Return 1
            End Select

        Catch ex As Exception
            _logger?.LogError(ex, "Error in HandleXAdsCampaignCommand")
            Console.WriteLine($"??? Error: {ex.Message}")
            Return 1
        End Try
    End Function

    Private Async Function HandleCreateCampaignCommand(args As String(), xAdsClient As XAdsClient, accessToken As String) As Task(Of Integer)
        Try
            If args.Length < 3 Then
                Console.WriteLine("??? Error: Campaign name is required")
                Console.WriteLine("Usage: eq12 xads-campaign create ""Campaign Name"" --budget 100 --account-id ""account_id""")
                Return 1
            End If

            Dim campaignName = args(2)
            Dim accountId As String = Nothing
            Dim budget As Decimal = 50 ' Default $50/day
            Dim currency As String = "USD"
            Dim startDate As DateTime? = Nothing
            Dim endDate As DateTime? = Nothing

            ' Parse additional arguments
            For i = 3 To args.Length - 2 Step 2
                Select Case args(i).ToLower()
                    Case "--account-id"
                        accountId = args(i + 1)
                    Case "--budget"
                        Decimal.TryParse(args(i + 1), budget)
                    Case "--currency"
                        currency = args(i + 1)
                    Case "--start-date"
                        DateTime.TryParse(args(i + 1), startDate)
                    Case "--end-date"
                        DateTime.TryParse(args(i + 1), endDate)
                End Select
            Next

            If String.IsNullOrEmpty(accountId) Then
                ' Try to get first available account
                Console.WriteLine("???? No account ID specified, getting available accounts...")
                Dim accounts = Await xAdsClient.GetAccountsAsync(accessToken)
                If accounts?.Count > 0 Then
                    accountId = accounts(0).Id
                    Console.WriteLine($"???? Using account: {accounts(0).Name} ({accountId})")
                Else
                    Console.WriteLine("??? Error: No advertising accounts found")
                    Return 1
                End If
            End If

            Console.WriteLine($"???? Creating campaign: {campaignName}")
            Console.WriteLine($"???? Daily budget: ${budget} {currency}")

            Dim campaignData As New CreateCampaignRequest() With {
                .AccountId = accountId,
                .Name = campaignName,
                .Currency = currency,
                .DailyBudgetAmountLocalMicro = CLng(budget * 1000000), ' Convert to micros
                .EntityStatus = "PAUSED", ' Start paused for safety
                .StartTime = startDate,
                .EndTime = endDate
            }

            Dim campaign = Await xAdsClient.CreateCampaignAsync(campaignData, accessToken)

            Console.WriteLine("??? Campaign created successfully!")
            Console.WriteLine($"???? Campaign ID: {campaign.Id}")
            Console.WriteLine($"???? Status: {campaign.EntityStatus}")
            Console.WriteLine($"???? Tip: Use 'eq12 xads-campaign update {campaign.Id} --status ACTIVE' to start the campaign")

            Return 0

        Catch ex As Exception
            Console.WriteLine($"??? Error creating campaign: {ex.Message}")
            Return 1
        End Try
    End Function

    Private Async Function HandleListCampaignsCommand(args As String(), xAdsClient As XAdsClient, accessToken As String) As Task(Of Integer)
        Try
            Dim accountId As String = Nothing
            Dim status As String = Nothing

            ' Parse arguments
            For i = 2 To args.Length - 2 Step 2
                Select Case args(i).ToLower()
                    Case "--account-id"
                        accountId = args(i + 1)
                    Case "--status"
                        status = args(i + 1)
                End Select
            Next

            If String.IsNullOrEmpty(accountId) Then
                ' Get first available account
                Console.WriteLine("???? Getting available accounts...")
                Dim accounts = Await xAdsClient.GetAccountsAsync(accessToken)
                If accounts?.Count > 0 Then
                    accountId = accounts(0).Id
                    Console.WriteLine($"???? Using account: {accounts(0).Name} ({accountId})")
                Else
                    Console.WriteLine("??? Error: No advertising accounts found")
                    Return 1
                End If
            End If

            Console.WriteLine($"???? Listing campaigns for account: {accountId}")
            If Not String.IsNullOrEmpty(status) Then
                Console.WriteLine($"???? Filtering by status: {status}")
            End If

            Dim campaigns = Await xAdsClient.GetCampaignsAsync(accountId, accessToken, False, status)

            Console.WriteLine($"??? Found {campaigns.Count} campaign(s)")
            Console.WriteLine("" + New String("="c, 80))

            For Each campaign In campaigns
                Console.WriteLine($"???? {campaign.Name}")
                Console.WriteLine($"   ID: {campaign.Id}")
                Console.WriteLine($"   Status: {campaign.EntityStatus}")
                Console.WriteLine($"   Budget: ${If(campaign.DailyBudgetAmountLocalMicro.HasValue, campaign.DailyBudgetAmountLocalMicro.Value / 1000000.0, 0):N2}/day")
                Console.WriteLine($"   Currency: {campaign.Currency}")
                Console.WriteLine($"   Created: {campaign.CreatedAt:yyyy-MM-dd HH:mm}")
                Console.WriteLine("")
            Next

            Return 0

        Catch ex As Exception
            Console.WriteLine($"??? Error listing campaigns: {ex.Message}")
            Return 1
        End Try
    End Function

    Private Async Function HandleCampaignStatsCommand(args As String(), xAdsClient As XAdsClient, accessToken As String) As Task(Of Integer)
        Try
            Dim accountId As String = Nothing
            Dim campaignId As String = Nothing
            Dim days As Integer = 7

            ' Parse arguments
            For i = 2 To args.Length - 2 Step 2
                Select Case args(i).ToLower()
                    Case "--account-id"
                        accountId = args(i + 1)
                    Case "--campaign-id"
                        campaignId = args(i + 1)
                    Case "--days"
                        Integer.TryParse(args(i + 1), days)
                End Select
            Next

            If String.IsNullOrEmpty(accountId) OrElse String.IsNullOrEmpty(campaignId) Then
                Console.WriteLine("??? Error: Both account-id and campaign-id are required")
                Console.WriteLine("Usage: eq12 xads-campaign stats --account-id ""account_id"" --campaign-id ""campaign_id"" --days 7")
                Return 1
            End If

            Console.WriteLine($"???? Getting {days}-day analytics for campaign: {campaignId}")

            Dim endDate = DateTime.UtcNow
            Dim startDate = endDate.AddDays(-days)

            Dim analytics = Await xAdsClient.GetCampaignAnalyticsAsync(accountId, campaignId, startDate, endDate, accessToken)

            Console.WriteLine("??? Campaign Analytics Retrieved")
            Console.WriteLine("" + New String("="c, 80))
            Console.WriteLine($"???? Campaign: {analytics.CampaignName}")
            Console.WriteLine($"???? Status: {analytics.CampaignStatus}")
            Console.WriteLine($"???? Period: {analytics.StartDate:yyyy-MM-dd} to {analytics.EndDate:yyyy-MM-dd}")
            Console.WriteLine("")
            Console.WriteLine("???? Performance Metrics:")
            Console.WriteLine($"   ???? Impressions: {analytics.TotalImpressions:N0}")
            Console.WriteLine($"   ?????? Engagements: {analytics.TotalEngagements:N0}")
            Console.WriteLine($"   ???? Engagement Rate: {analytics.EngagementRate:P2}")
            Console.WriteLine($"   ???? Total Spend: ${analytics.TotalSpend:N2}")
            Console.WriteLine($"   ???? CPM: ${analytics.CPM:N2}")
            Console.WriteLine($"   ???? Cost per Engagement: ${analytics.CostPerEngagement:N2}")
            Console.WriteLine("")
            Console.WriteLine("???? EQ12 Enhanced Metrics:")
            Console.WriteLine($"   ???? EQ12 Engagement Score: {analytics.EQ12EngagementScore:N1}/100")
            Console.WriteLine($"   ???? EQ12 ROI: {analytics.EQ12ROI:P1}")
            Console.WriteLine($"   ???? EQ12 Virality Score: {analytics.EQ12ViralityScore:N1}/100")

            Return 0

        Catch ex As Exception
            Console.WriteLine($"??? Error getting campaign stats: {ex.Message}")
            Return 1
        End Try
    End Function

    Private Async Function HandleAutoPromoteCampaignCommand(args As String(), xAdsClient As XAdsClient, accessToken As String) As Task(Of Integer)
        Try
            Dim tweetId As String = Nothing
            Dim accountId As String = Nothing
            Dim budget As Decimal = 25 ' Default $25/day

            ' Parse arguments
            For i = 2 To args.Length - 2 Step 2
                Select Case args(i).ToLower()
                    Case "--tweet-id"
                        tweetId = args(i + 1)
                    Case "--account-id"
                        accountId = args(i + 1)
                    Case "--budget"
                        Decimal.TryParse(args(i + 1), budget)
                End Select
            Next

            If String.IsNullOrEmpty(tweetId) Then
                Console.WriteLine("??? Error: Tweet ID is required")
                Console.WriteLine("Usage: eq12 xads-campaign auto-promote --tweet-id ""1234567890"" --budget 25")
                Return 1
            End If

            If String.IsNullOrEmpty(accountId) Then
                ' Get first available account
                Dim accounts = Await xAdsClient.GetAccountsAsync(accessToken)
                If accounts?.Count > 0 Then
                    accountId = accounts(0).Id
                Else
                    Console.WriteLine("??? Error: No advertising accounts found")
                    Return 1
                End If
            End If

            Console.WriteLine($"???? Auto-promoting tweet: {tweetId}")
            Console.WriteLine($"???? Budget: ${budget}/day")

            Dim campaignId = Await xAdsClient.AutoPromoteHighPerformingTweetAsync(tweetId, accountId, budget, accessToken)

            Console.WriteLine("??? Tweet auto-promoted successfully!")
            Console.WriteLine($"???? Campaign ID: {campaignId}")
            Console.WriteLine($"???? Tip: Use 'eq12 xads-campaign stats --campaign-id {campaignId}' to track performance")

            Return 0

        Catch ex As Exception
            Console.WriteLine($"??? Error auto-promoting tweet: {ex.Message}")
            Return 1
        End Try
    End Function

    ''' <summary>
    ''' X Ads creative management command
    ''' Usage: eq12 xads-creative upload "image.jpg" --account-id "18ce54d4x5t"
    ''' </summary>
    Public Async Function HandleXAdsCreativeCommand(args As String()) As Task(Of Integer)
        Try
            _logger?.LogInformation("???? Starting xads-creative command")

            If args.Length < 2 Then
                ShowXAdsCreativeUsage()
                Return 1
            End If

            Dim subCommand = args(1).ToLower()
            Dim tokenManager As New OAuth2TokenManager()
            Dim token = Await tokenManager.GetValidTokenAsync("default")

            If token Is Nothing Then
                Console.WriteLine("??? Error: No valid OAuth token found")
                Return 1
            End If

            Dim xAdsClient As New XAdsClient(_logger, _config)

            Select Case subCommand
                Case "upload"
                    Return Await HandleUploadCreativeCommand(args, xAdsClient, token.access_token)
                Case "promote-tweet"
                    Return Await HandlePromoteTweetCommand(args, xAdsClient, token.access_token)
                Case Else
                    Console.WriteLine($"??? Unknown creative subcommand: {subCommand}")
                    ShowXAdsCreativeUsage()
                    Return 1
            End Select

        Catch ex As Exception
            _logger?.LogError(ex, "Error in HandleXAdsCreativeCommand")
            Console.WriteLine($"??? Error: {ex.Message}")
            Return 1
        End Try
    End Function

    Private Async Function HandleUploadCreativeCommand(args As String(), xAdsClient As XAdsClient, accessToken As String) As Task(Of Integer)
        Try
            If args.Length < 3 Then
                Console.WriteLine("??? Error: File path is required")
                Console.WriteLine("Usage: eq12 xads-creative upload ""image.jpg"" --account-id ""account_id""")
                Return 1
            End If

            Dim filePath = args(2)
            Dim accountId As String = Nothing
            Dim creativeName As String = Nothing
            Dim creativeType As String = "MEDIA"

            ' Parse additional arguments
            For i = 3 To args.Length - 2 Step 2
                Select Case args(i).ToLower()
                    Case "--account-id"
                        accountId = args(i + 1)
                    Case "--name"
                        creativeName = args(i + 1)
                    Case "--type"
                        creativeType = args(i + 1)
                End Select
            Next

            If Not File.Exists(filePath) Then
                Console.WriteLine($"??? Error: File not found: {filePath}")
                Return 1
            End If

            If String.IsNullOrEmpty(accountId) Then
                ' Get first available account
                Dim accounts = Await xAdsClient.GetAccountsAsync(accessToken)
                If accounts?.Count > 0 Then
                    accountId = accounts(0).Id
                Else
                    Console.WriteLine("??? Error: No advertising accounts found")
                    Return 1
                End If
            End If

            Console.WriteLine($"???? Uploading creative: {Path.GetFileName(filePath)}")

            Dim creative = Await xAdsClient.UploadCreativeAsync(filePath, creativeType, accessToken, accountId, creativeName)

            Console.WriteLine("??? Creative uploaded successfully!")
            Console.WriteLine($"???? Creative ID: {creative.Id}")
            Console.WriteLine($"???? Name: {creative.Name}")
            Console.WriteLine($"???? Status: {creative.EntityStatus}")

            Return 0

        Catch ex As Exception
            Console.WriteLine($"??? Error uploading creative: {ex.Message}")
            Return 1
        End Try
    End Function

    ''' <summary>
    ''' X Ads analytics and reporting command
    ''' Usage: eq12 xads-report generate --account-id "18ce54d4x5t" --days 30
    ''' </summary>
    Public Async Function HandleXAdsReportCommand(args As String()) As Task(Of Integer)
        Try
            _logger?.LogInformation("???? Starting xads-report command")

            If args.Length < 2 Then
                ShowXAdsReportUsage()
                Return 1
            End If

            Dim subCommand = args(1).ToLower()
            Dim tokenManager As New OAuth2TokenManager()
            Dim token = Await tokenManager.GetValidTokenAsync("default")

            If token Is Nothing Then
                Console.WriteLine("??? Error: No valid OAuth token found")
                Return 1
            End If

            Dim xAdsClient As New XAdsClient(_logger, _config)

            Select Case subCommand
                Case "generate"
                    Return Await HandleGenerateReportCommand(args, xAdsClient, token.access_token)
                Case Else
                    Console.WriteLine($"??? Unknown report subcommand: {subCommand}")
                    ShowXAdsReportUsage()
                    Return 1
            End Select

        Catch ex As Exception
            _logger?.LogError(ex, "Error in HandleXAdsReportCommand")
            Console.WriteLine($"??? Error: {ex.Message}")
            Return 1
        End Try
    End Function

    Private Async Function HandleGenerateReportCommand(args As String(), xAdsClient As XAdsClient, accessToken As String) As Task(Of Integer)
        Try
            Dim accountId As String = Nothing
            Dim days As Integer = 30

            ' Parse arguments
            For i = 2 To args.Length - 2 Step 2
                Select Case args(i).ToLower()
                    Case "--account-id"
                        accountId = args(i + 1)
                    Case "--days"
                        Integer.TryParse(args(i + 1), days)
                End Select
            Next

            If String.IsNullOrEmpty(accountId) Then
                ' Get first available account
                Dim accounts = Await xAdsClient.GetAccountsAsync(accessToken)
                If accounts?.Count > 0 Then
                    accountId = accounts(0).Id
                    Console.WriteLine($"???? Using account: {accounts(0).Name} ({accountId})")
                Else
                    Console.WriteLine("??? Error: No advertising accounts found")
                    Return 1
                End If
            End If

            Console.WriteLine($"???? Generating EQ12 ad performance report...")
            Console.WriteLine($"???? Period: Last {days} days")
            Console.WriteLine($"???? This may take a few moments...")

            Dim reportUrl = Await xAdsClient.GenerateEQ12AdReportAsync(accountId, days, accessToken)

            Console.WriteLine("??? Report generated successfully!")
            Console.WriteLine($"???? Report URL: {reportUrl}")
            Console.WriteLine($"???? Tip: Report has been saved to C:\EQ12\logs and shared via notifications")

            Return 0

        Catch ex As Exception
            Console.WriteLine($"??? Error generating report: {ex.Message}")
            Return 1
        End Try
    End Function

    ' Usage display methods for X Ads commands
    Private Sub ShowXAdsCampaignUsage()
        Console.WriteLine("???? X Ads Campaign Management Commands:")
        Console.WriteLine("")
        Console.WriteLine("Usage: eq12 xads-campaign <subcommand> [options]")
        Console.WriteLine("")
        Console.WriteLine("Subcommands:")
        Console.WriteLine("  create        Create new campaign")
        Console.WriteLine("  list          List campaigns")
        Console.WriteLine("  update        Update campaign")
        Console.WriteLine("  delete        Delete campaign")
        Console.WriteLine("  stats         Get campaign analytics")
        Console.WriteLine("  auto-promote  Auto-promote high-performing tweet")
        Console.WriteLine("")
        Console.WriteLine("Examples:")
        Console.WriteLine("  eq12 xads-campaign create ""Holiday Sale Campaign"" --budget 100 --account-id ""18ce54d4x5t""")
        Console.WriteLine("  eq12 xads-campaign list --account-id ""18ce54d4x5t"" --status ACTIVE")
        Console.WriteLine("  eq12 xads-campaign stats --campaign-id ""abc123"" --days 7")
        Console.WriteLine("  eq12 xads-campaign auto-promote --tweet-id ""1234567890"" --budget 25")
        Console.WriteLine("")
    End Sub

    Private Sub ShowXAdsCreativeUsage()
        Console.WriteLine("???? X Ads Creative Management Commands:")
        Console.WriteLine("")
        Console.WriteLine("Usage: eq12 xads-creative <subcommand> [options]")
        Console.WriteLine("")
        Console.WriteLine("Subcommands:")
        Console.WriteLine("  upload        Upload media creative")
        Console.WriteLine("  promote-tweet Create promoted tweet")
        Console.WriteLine("")
        Console.WriteLine("Examples:")
        Console.WriteLine("  eq12 xads-creative upload ""banner.jpg"" --account-id ""18ce54d4x5t"" --name ""Holiday Banner""")
        Console.WriteLine("  eq12 xads-creative promote-tweet --tweet-id ""1234567890"" --account-id ""18ce54d4x5t""")
        Console.WriteLine("")
    End Sub

    Private Sub ShowXAdsReportUsage()
        Console.WriteLine("???? X Ads Analytics and Reporting Commands:")
        Console.WriteLine("")
        Console.WriteLine("Usage: eq12 xads-report <subcommand> [options]")
        Console.WriteLine("")
        Console.WriteLine("Subcommands:")
        Console.WriteLine("  generate      Generate comprehensive performance report")
        Console.WriteLine("")
        Console.WriteLine("Examples:")
        Console.WriteLine("  eq12 xads-report generate --account-id ""18ce54d4x5t"" --days 30")
        Console.WriteLine("")
    End Sub

    Public Async Function HandleMetricsSyncCommand(args As String()) As Task(Of Integer)
        Try
            Dim parsed = ParseCopilotMetricsArgs(args)
            If parsed.Extras.ContainsKey("help") Then
                ShowCopilotMetricsUsage()
                Return 0
            End If

            Dim request = parsed.Request
            If Not ValidateCopilotScope(request) Then
                ShowCopilotMetricsUsage()
                Return 1
            End If

            If Not request.Since.HasValue Then
                Dim defaultDays = GetWindowDays(parsed.Extras, 7)
                request.Since = DateTime.UtcNow.Date.AddDays(-defaultDays)
            End If

            Dim client As New CopilotMetricsClient(_logger, _config)
            Dim snapshot = Await client.FetchMetricsAsync(request)
            Dim logsRoot = ResolveLogsRoot()
            Dim jsonPath = snapshot.SaveRawJson(logsRoot)

            Console.WriteLine($"Copilot metrics saved to {jsonPath}")
            PrintCopilotSummary(snapshot)

            Return 0
        Catch ex As Exception
            _logger?.LogError(ex, "Error in HandleMetricsSyncCommand")
            Console.WriteLine($"Error running metrics-sync: {ex.Message}")
            Return 1
        End Try
    End Function

    Public Async Function HandleMetricsReportCommand(args As String()) As Task(Of Integer)
        Try
            Dim parsed = ParseCopilotMetricsArgs(args)
            If parsed.Extras.ContainsKey("help") Then
                ShowCopilotMetricsUsage()
                Return 0
            End If

            Dim request = parsed.Request
            If Not ValidateCopilotScope(request) Then
                ShowCopilotMetricsUsage()
                Return 1
            End If

            Dim periodLabel = GetExtrasValue(parsed.Extras, "period", "weekly")
            Dim windowDays = GetWindowDays(parsed.Extras, MapPeriodToDays(periodLabel))

            If windowDays > 0 AndAlso Not request.Since.HasValue Then
                request.Since = DateTime.UtcNow.Date.AddDays(-windowDays)
            End If

            Dim client As New CopilotMetricsClient(_logger, _config)
            Dim snapshot = Await client.FetchMetricsAsync(request)
            Dim report = CopilotMetricsReportBuilder.BuildMarkdownReport(snapshot, periodLabel.ToUpperInvariant())
            Dim logsRoot = ResolveLogsRoot()
            Dim reportPath = snapshot.SaveReport(report, logsRoot, $"report_{periodLabel.ToLowerInvariant()}")

            Console.WriteLine($"Copilot metrics report saved to {reportPath}")
            PrintCopilotSummary(snapshot)

            Return 0
        Catch ex As Exception
            _logger?.LogError(ex, "Error in HandleMetricsReportCommand")
            Console.WriteLine($"Error running metrics-report: {ex.Message}")
            Return 1
        End Try
    End Function

    Public Async Function HandleMetricsDiffCommand(args As String()) As Task(Of Integer)
        Try
            Dim parsed = ParseCopilotMetricsArgs(args)
            If parsed.Extras.ContainsKey("help") Then
                ShowCopilotMetricsUsage()
                Return 0
            End If

            Dim request = parsed.Request
            If Not ValidateCopilotScope(request) Then
                ShowCopilotMetricsUsage()
                Return 1
            End If

            Dim daysWindow = Math.Max(1, GetWindowDays(parsed.Extras, 30))

            If Not request.Since.HasValue Then
                request.Since = DateTime.UtcNow.Date.AddDays(-daysWindow * 2)
            End If

            Dim client As New CopilotMetricsClient(_logger, _config)
            Dim snapshot = Await client.FetchMetricsAsync(request)
            Dim diff = CopilotMetricsReportBuilder.CalculateDiff(snapshot, daysWindow)
            Dim diffReport = BuildDiffReport(snapshot, diff)
            Dim logsRoot = ResolveLogsRoot()
            Dim diffPath = snapshot.SaveReport(diffReport, logsRoot, $"diff_{daysWindow}d")

            Console.WriteLine($"Copilot metrics diff saved to {diffPath}")
            PrintCopilotDiff(diff)

            Return 0
        Catch ex As Exception
            _logger?.LogError(ex, "Error in HandleMetricsDiffCommand")
            Console.WriteLine($"Error running metrics-diff: {ex.Message}")
            Return 1
        End Try
    End Function

    Private Class CopilotMetricsParsedOptions
        Public Property Request As CopilotMetricsRequest
        Public Property Extras As Dictionary(Of String, String)
    End Class

    Private Function ParseCopilotMetricsArgs(args As String()) As CopilotMetricsParsedOptions
        Dim parsed As New CopilotMetricsParsedOptions With {
            .Request = New CopilotMetricsRequest(),
            .Extras = New Dictionary(Of String, String)(StringComparer.OrdinalIgnoreCase)
        }

        parsed.Request.Scope = CopilotMetricsScope.Organization

        Dim i = 1
        While i < args.Length
            Dim token = args(i)
            If String.IsNullOrWhiteSpace(token) Then
                i += 1
                Continue While
            End If

            Dim name = token
            Dim value As String = Nothing
            Dim hasInlineValue = False

            If token.StartsWith("--", StringComparison.Ordinal) AndAlso token.Contains("="c) Then
                Dim parts = token.Split(New Char() {"="c}, 2)
                name = parts(0)
                value = If(parts.Length > 1, parts(1), String.Empty)
                hasInlineValue = True
            End If

            Dim lowered = name.ToLowerInvariant()

            Select Case lowered
                Case "--help", "-h"
                    parsed.Extras("help") = "true"
                    i += 1
                    Continue While
                Case "--scope"
                    If Not hasInlineValue Then
                        value = GetNextValue(args, i)
                        i += 2
                    Else
                        i += 1
                    End If
                    SetScope(parsed.Request, value)
                    Continue While
                Case "--enterprise"
                    If Not hasInlineValue Then
                        value = GetNextValue(args, i)
                        i += 2
                    Else
                        i += 1
                    End If
                    parsed.Request.EnterpriseSlug = value
                    parsed.Request.Scope = CopilotMetricsScope.Enterprise
                    Continue While
                Case "--org", "--organization"
                    If Not hasInlineValue Then
                        value = GetNextValue(args, i)
                        i += 2
                    Else
                        i += 1
                    End If
                    parsed.Request.Organization = value
                    If parsed.Request.Scope = CopilotMetricsScope.Enterprise Then
                        ' keep enterprise if explicitly set
                    ElseIf parsed.Request.Scope <> CopilotMetricsScope.Team Then
                        parsed.Request.Scope = CopilotMetricsScope.Organization
                    End If
                    Continue While
                Case "--team"
                    If Not hasInlineValue Then
                        value = GetNextValue(args, i)
                        i += 2
                    Else
                        i += 1
                    End If
                    parsed.Request.TeamSlug = value
                    parsed.Request.Scope = CopilotMetricsScope.Team
                    Continue While
                Case "--since"
                    If Not hasInlineValue Then
                        value = GetNextValue(args, i)
                        i += 2
                    Else
                        i += 1
                    End If
                    Dim parsedDate As DateTime
                    If DateTime.TryParse(value, CultureInfo.InvariantCulture, DateTimeStyles.AdjustToUniversal Or DateTimeStyles.AssumeUniversal, parsedDate) Then
                        parsed.Request.Since = parsedDate.Date
                    Else
                        Throw New ArgumentException($"Invalid value for --since: {value}")
                    End If
                    Continue While
                Case "--days"
                    If Not hasInlineValue Then
                        value = GetNextValue(args, i)
                        i += 2
                    Else
                        i += 1
                    End If
                    parsed.Extras("days") = value
                    Dim dayCount As Integer
                    If Integer.TryParse(value, dayCount) AndAlso dayCount > 0 Then
                        parsed.Request.Since = DateTime.UtcNow.Date.AddDays(-dayCount)
                    End If
                    Continue While
                Case "--token"
                    If Not hasInlineValue Then
                        value = GetNextValue(args, i)
                        i += 2
                    Else
                        i += 1
                    End If
                    parsed.Request.AccessToken = value
                    Continue While
                Case "--period"
                    If Not hasInlineValue Then
                        value = GetNextValue(args, i)
                        i += 2
                    Else
                        i += 1
                    End If
                    parsed.Extras("period") = value
                    Continue While
                Case "--output"
                    If Not hasInlineValue Then
                        value = GetNextValue(args, i)
                        i += 2
                    Else
                        i += 1
                    End If
                    parsed.Extras("output") = value
                    Continue While
                Case Else
                    If lowered.StartsWith("--") AndAlso hasInlineValue Then
                        parsed.Extras(lowered.TrimStart("-"c)) = value
                    Else
                        parsed.Extras($"arg{i}") = token
                    End If
                    i += 1
                    Continue While
            End Select
        End While

        Return parsed
    End Function

    Private Function GetNextValue(args As String(), index As Integer) As String
        If index + 1 >= args.Length Then
            Throw New ArgumentException($"Missing value for option {args(index)}")
        End If
        Return args(index + 1)
    End Function

    Private Sub SetScope(request As CopilotMetricsRequest, value As String)
        If String.IsNullOrWhiteSpace(value) Then
            Throw New ArgumentException("Scope value cannot be empty.")
        End If

        Select Case value.ToLowerInvariant()
            Case "enterprise"
                request.Scope = CopilotMetricsScope.Enterprise
            Case "org", "organization"
                request.Scope = CopilotMetricsScope.Organization
            Case "team"
                request.Scope = CopilotMetricsScope.Team
            Case Else
                Throw New ArgumentException($"Unknown scope: {value}")
        End Select
    End Sub

    Private Function ValidateCopilotScope(request As CopilotMetricsRequest) As Boolean
        Select Case request.Scope
            Case CopilotMetricsScope.Enterprise
                If String.IsNullOrWhiteSpace(request.EnterpriseSlug) Then
                    Console.WriteLine("Error: Provide --enterprise <slug> when scope=enterprise.")
                    Return False
                End If
            Case CopilotMetricsScope.Team
                If String.IsNullOrWhiteSpace(request.Organization) OrElse String.IsNullOrWhiteSpace(request.TeamSlug) Then
                    Console.WriteLine("Error: Provide --org <name> and --team <slug> when scope=team.")
                    Return False
                End If
            Case Else
                If String.IsNullOrWhiteSpace(request.Organization) Then
                    Console.WriteLine("Error: Provide --org <name> for Copilot metrics.")
                    Return False
                End If
        End Select

        Return True
    End Function

    Private Function ResolveLogsRoot() As String
        Dim candidates = New List(Of String) From {
            Path.Combine("C:\\EQ12", "logs"),
            Path.Combine("/workspaces/EQ12", "logs"),
            Path.Combine(AppContext.BaseDirectory, "logs")
        }

        For Each candidate In candidates
            If String.IsNullOrWhiteSpace(candidate) Then
                Continue For
            End If

            Try
                Directory.CreateDirectory(candidate)
                Return candidate
            Catch
                ' try next candidate
            End Try
        Next

        Dim fallback = Path.Combine(Directory.GetCurrentDirectory(), "logs")
        Directory.CreateDirectory(fallback)
        Return fallback
    End Function

    Private Sub ShowCopilotMetricsUsage()
        Console.WriteLine("Copilot Metrics Commands:")
        Console.WriteLine("  eq12 metrics-sync --org <org> [--scope <enterprise|team>] [--since YYYY-MM-DD] [--days N]")
        Console.WriteLine("  eq12 metrics-report --org <org> [--period daily|weekly|monthly] [--output path]")
        Console.WriteLine("  eq12 metrics-diff --org <org> [--days N]")
        Console.WriteLine("Options:")
        Console.WriteLine("  --enterprise <slug>    Enterprise slug when scope=enterprise")
        Console.WriteLine("  --team <slug>          Team slug when scope=team (requires --org)")
        Console.WriteLine("  --token <value>        Override GitHub token (otherwise uses config/env)")
        Console.WriteLine("  --since <date>         ISO date (UTC) for earliest metrics to fetch")
        Console.WriteLine("  --days <n>             Convenience window size (also sets --since)")
        Console.WriteLine("  --period <p>           Report period label: daily, weekly, monthly, biweekly, quarterly")
    End Sub

    Private Sub PrintCopilotSummary(snapshot As CopilotMetricsSnapshot)
        Dim summary = snapshot?.Summary
        Console.WriteLine("")
        Console.WriteLine($"Scope: {snapshot.Identifier}")

        If summary Is Nothing Then
            Console.WriteLine("No summary metrics returned.")
            Return
        End If

        Console.WriteLine("Summary Metrics:")
        Console.WriteLine($"  Total suggestions: {FormatNumber(summary.TotalSuggestions)}")
        Console.WriteLine($"  Accepted suggestions: {FormatNumber(summary.AcceptedSuggestions)}")
        Console.WriteLine($"  Acceptance rate: {FormatPercent(summary.AcceptanceRate)}")
        Console.WriteLine($"  Active users: {FormatNumber(summary.ActiveUsers)} / {FormatNumber(summary.LicensedUsers)} licensed")
        Console.WriteLine($"  Copilot Chat sessions: {FormatNumber(summary.TotalChats)}")

        Dim latest = snapshot.DailyBuckets?.OrderBy(Function(b) b.Day).LastOrDefault()
        If latest IsNot Nothing Then
            Dim acceptance = latest.AcceptanceRate
            If Not acceptance.HasValue AndAlso latest.TotalSuggestions.HasValue AndAlso latest.TotalSuggestions.Value > 0 AndAlso latest.AcceptedSuggestions.HasValue Then
                acceptance = latest.AcceptedSuggestions.Value / latest.TotalSuggestions.Value
            End If

            Console.WriteLine($"Latest Day ({latest.Day:yyyy-MM-dd}):")
            Console.WriteLine($"  Suggestions: {FormatNumber(latest.TotalSuggestions)}")
            Console.WriteLine($"  Accepted: {FormatNumber(latest.AcceptedSuggestions)}")
            Console.WriteLine($"  Acceptance: {FormatPercent(acceptance)}")
            Console.WriteLine($"  Active users: {FormatNumber(latest.ActiveUsers)}")
        End If
    End Sub

    Private Sub PrintCopilotDiff(diff As CopilotMetricsDiff)
        If diff Is Nothing OrElse diff.Deltas.Count = 0 Then
            Console.WriteLine("Insufficient data to compute differences.")
            Return
        End If

        Console.WriteLine($"Comparing last {diff.PeriodDays}-day average to previous window:")
        For Each delta In diff.Deltas
            Dim isRate = delta.MetricName.IndexOf("rate", StringComparison.OrdinalIgnoreCase) >= 0 OrElse delta.MetricName.IndexOf("percent", StringComparison.OrdinalIgnoreCase) >= 0
            Dim recentText = If(isRate, FormatPercent(delta.RecentAverage), FormatNumber(delta.RecentAverage))
            Dim baselineText = If(isRate, FormatPercent(delta.BaselineAverage), FormatNumber(delta.BaselineAverage))
            Dim changeText As String = "n/a"

            If delta.Difference.HasValue Then
                changeText = If(isRate, (delta.Difference.Value * 100.0).ToString("+0.##;-0.##;0", CultureInfo.InvariantCulture) & " pp", delta.Difference.Value.ToString("+0.##;-0.##;0", CultureInfo.InvariantCulture))
            End If

            Console.WriteLine($"  {delta.MetricName}: {recentText} (baseline {baselineText}, change {changeText})")
        Next
    End Sub





    Private Function BuildDiffReport(snapshot As CopilotMetricsSnapshot, diff As CopilotMetricsDiff) As String
        Dim sb As New StringBuilder()
        sb.AppendLine("# EQ12 Copilot Metrics Diff")
        sb.AppendLine($"- Scope: {snapshot.Identifier}")
        sb.AppendLine($"- Retrieved: {snapshot.RetrievedAt:yyyy-MM-dd HH:mm:ss} UTC")
        sb.AppendLine($"- Window: {diff.PeriodDays} day average vs previous window")
        sb.AppendLine("")
        sb.AppendLine("| Metric | Recent Avg | Baseline Avg | Change |")
        sb.AppendLine("| --- | --- | --- | --- |")

        For Each delta In diff.Deltas
            Dim isRate = delta.MetricName.IndexOf("rate", StringComparison.OrdinalIgnoreCase) >= 0 OrElse delta.MetricName.IndexOf("percent", StringComparison.OrdinalIgnoreCase) >= 0
            Dim recentText = If(isRate, FormatPercent(delta.RecentAverage), FormatNumber(delta.RecentAverage))
            Dim baselineText = If(isRate, FormatPercent(delta.BaselineAverage), FormatNumber(delta.BaselineAverage))
            Dim changeText As String = "n/a"

            If delta.Difference.HasValue Then
                changeText = If(isRate, (delta.Difference.Value * 100.0).ToString("+0.##;-0.##;0", CultureInfo.InvariantCulture) & " pp", delta.Difference.Value.ToString("+0.##;-0.##;0", CultureInfo.InvariantCulture))
            End If

            sb.AppendLine($"| {delta.MetricName} | {recentText} | {baselineText} | {changeText} |")
        Next

        Return sb.ToString()
    End Function


        Private Function GetExtrasValue(extras As Dictionary(Of String, String), key As String, defaultValue As String) As String

        If extras Is Nothing Then

            Return defaultValue

        End If

        Dim stored As String = Nothing

        If extras.TryGetValue(key, stored) Then

            Return stored

        End If

        Return defaultValue

    End Function

    Private Function MapPeriodToDays(period As String) As Integer
        If String.IsNullOrWhiteSpace(period) Then
            Return 7
        End If

        Select Case period.ToLowerInvariant()
            Case "daily"
                Return 1
            Case "weekly"
                Return 7
            Case "biweekly"
                Return 14
            Case "monthly"
                Return 30
            Case "quarterly"
                Return 90
            Case Else
                Return 7
        End Select
    End Function

        Private Function GetWindowDays(extras As Dictionary(Of String, String), defaultDays As Integer) As Integer

        Dim rawDays As String = Nothing

        If extras Is Not Nothing AndAlso extras.TryGetValue("days", rawDays) Then

            Dim dayCount As Integer

            If Integer.TryParse(rawDays, dayCount) AndAlso dayCount > 0 Then

                Return dayCount

            End If

        End If

        Dim period As String = Nothing

        If extras Is Not Nothing AndAlso extras.TryGetValue("period", period) Then

            Return MapPeriodToDays(period)

        End If

        Return Math.Max(1, defaultDays)

    End Function

    Private Function FormatNumber(value As Double?) As String
        If Not value.HasValue Then
            Return "n/a"
        End If
        Return value.Value.ToString("0.##", CultureInfo.InvariantCulture)
    End Function

    Private Function FormatPercent(value As Double?) As String
        If Not value.HasValue Then
            Return "n/a"
        End If
        Return (value.Value * 100.0).ToString("0.##", CultureInfo.InvariantCulture) & "%"
    End Function

End Class


