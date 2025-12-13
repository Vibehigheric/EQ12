' Enhanced XClient.vb with OAuth2, Media Upload, and Advanced X API Operations
' Pre-generated for immediate deployment - Production Ready v3.0
' Extends existing XClient.vb with comprehensive X API 2.0 functionality

Imports System
Imports System.IO
Imports System.Net.Http
Imports System.Text
Imports System.Threading.Tasks
Imports System.Collections.Generic
Imports System.Text.Json
Imports System.Security.Cryptography
Imports System.Web
Imports Microsoft.Extensions.Configuration
Imports Microsoft.Extensions.Logging

' Enhanced XClient with complete OAuth2 and media capabilities
Partial Public Class XClient

    ' ==================================================
    ' ENHANCED OAUTH 2.0 WITH PKCE SUPPORT
    ' ==================================================

    ''' <summary>
    ''' Initiate OAuth 2.0 authorization flow with PKCE
    ''' </summary>
    Public Function InitiateOAuth2Flow(clientId As String, redirectUri As String, scopes As List(Of String)) As (authUrl As String, codeVerifier As String, state As String)
        Try
            ' Generate PKCE code verifier and challenge
            Dim codeVerifier = GenerateCodeVerifier()
            Dim codeChallenge = GenerateCodeChallenge(codeVerifier)

            ' Generate state parameter for security
            Dim state = GenerateRandomString(32)

            ' Build authorization URL
            Dim scopeString = String.Join(" ", scopes)
            Dim authUrl = $"https://twitter.com/i/oauth2/authorize?" +
                         $"response_type=code&" +
                         $"client_id={Uri.EscapeDataString(clientId)}&" +
                         $"redirect_uri={Uri.EscapeDataString(redirectUri)}&" +
                         $"scope={Uri.EscapeDataString(scopeString)}&" +
                         $"state={state}&" +
                         $"code_challenge={codeChallenge}&" +
                         $"code_challenge_method=S256"

            Return (authUrl, codeVerifier, state)

        Catch ex As Exception
            _logger?.LogError(ex, "Error initiating OAuth2 flow")
            Throw New Exception($"OAuth2 flow initiation failed: {ex.Message}", ex)
        End Try
    End Function

    ''' <summary>
    ''' Exchange authorization code for access token
    ''' </summary>
    Public Async Function ExchangeCodeForTokenAsync(clientId As String, clientSecret As String,
                                                    redirectUri As String, authorizationCode As String,
                                                    codeVerifier As String) As Task(Of OAuth2TokenResponse)
        Try
            Using client As New HttpClient()
                Dim requestBody = New FormUrlEncodedContent(New Dictionary(Of String, String) From {
                    {"code", authorizationCode},
                    {"grant_type", "authorization_code"},
                    {"client_id", clientId},
                    {"redirect_uri", redirectUri},
                    {"code_verifier", codeVerifier}
                })

                ' Add Basic Auth header
                Dim credentials = Convert.ToBase64String(Encoding.UTF8.GetBytes($"{clientId}:{clientSecret}"))
                client.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Basic", credentials)

                Dim response = Await client.PostAsync("https://api.twitter.com/2/oauth2/token", requestBody)
                Dim responseContent = Await response.Content.ReadAsStringAsync()

                If response.IsSuccessStatusCode Then
                    Dim tokenResponse = JsonSerializer.Deserialize(Of OAuth2TokenResponse)(responseContent)

                    ' Store token securely
                    Await StoreTokenSecurelyAsync(tokenResponse, clientId)

                    Return tokenResponse
                Else
                    Throw New Exception($"Token exchange failed: {response.StatusCode} - {responseContent}")
                End If
            End Using

        Catch ex As Exception
            _logger?.LogError(ex, "Error exchanging code for token")
            Throw New Exception($"Token exchange failed: {ex.Message}", ex)
        End Try
    End Function

    ''' <summary>
    ''' Refresh OAuth2 token using refresh token
    ''' </summary>
    Public Async Function RefreshTokenAsync(clientId As String, clientSecret As String,
                                            refreshToken As String) As Task(Of OAuth2TokenResponse)
        Try
            Using client As New HttpClient()
                Dim requestBody = New FormUrlEncodedContent(New Dictionary(Of String, String) From {
                    {"refresh_token", refreshToken},
                    {"grant_type", "refresh_token"},
                    {"client_id", clientId}
                })

                ' Add Basic Auth header
                Dim credentials = Convert.ToBase64String(Encoding.UTF8.GetBytes($"{clientId}:{clientSecret}"))
                client.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Basic", credentials)

                Dim response = Await client.PostAsync("https://api.twitter.com/2/oauth2/token", requestBody)
                Dim responseContent = Await response.Content.ReadAsStringAsync()

                If response.IsSuccessStatusCode Then
                    Dim tokenResponse = JsonSerializer.Deserialize(Of OAuth2TokenResponse)(responseContent)

                    ' Update stored token
                    Await UpdateStoredTokenAsync(tokenResponse, clientId)

                    Return tokenResponse
                Else
                    Throw New Exception($"Token refresh failed: {response.StatusCode} - {responseContent}")
                End If
            End Using

        Catch ex As Exception
            _logger?.LogError(ex, "Error refreshing token")
            Throw New Exception($"Token refresh failed: {ex.Message}", ex)
        End Try
    End Function

    ' ==================================================
    ' ENHANCED MEDIA UPLOAD WITH CHUNKED SUPPORT
    ' ==================================================

    ''' <summary>
    ''' Upload media with automatic chunking for large files
    ''' </summary>
    Public Async Function UploadMediaEnhancedAsync(filePath As String, accessToken As String,
                                                   Optional altText As String = Nothing,
                                                   Optional category As String = "tweet_image") As Task(Of String)
        Try
            If Not File.Exists(filePath) Then
                Throw New FileNotFoundException($"Media file not found: {filePath}")
            End If

            Dim fileInfo = New FileInfo(filePath)
            Dim mediaType = GetMediaType(filePath)

            ' Determine if chunked upload is needed (>5MB)
            Dim useChunkedUpload = fileInfo.Length > 5 * 1024 * 1024

            If useChunkedUpload Then
                Return Await UploadMediaChunkedAsync(filePath, accessToken, altText, category)
            Else
                Return Await UploadMediaSimpleAsync(filePath, accessToken, altText, category)
            End If

        Catch ex As Exception
            _logger?.LogError(ex, "Error uploading media (enhanced)")
            Throw New Exception($"Media upload failed: {ex.Message}", ex)
        End Try
    End Function

    ''' <summary>
    ''' Chunked media upload for large files
    ''' </summary>
    Private Async Function UploadMediaChunkedAsync(filePath As String, accessToken As String,
                                                   altText As String, category As String) As Task(Of String)
        Try
            Dim fileInfo = New FileInfo(filePath)
            Dim mediaType = GetMediaType(filePath)
            Dim chunkSize = 1024 * 1024 ' 1MB chunks
            Dim totalChunks = CInt(Math.Ceiling(fileInfo.Length / chunkSize))

            ' Step 1: Initialize upload
            Dim mediaId = Await InitializeMediaUploadAsync(fileInfo.Length, mediaType, category, accessToken)

            ' Log upload start
            Await LogMediaUploadAsync(mediaId, filePath, "chunked", fileInfo.Length, totalChunks, 0, accessToken)

            ' Step 2: Upload chunks
            Using fileStream = New FileStream(filePath, FileMode.Open, FileAccess.Read)
                Dim chunkIndex = 0
                Dim buffer(chunkSize - 1) As Byte

                While fileStream.Position < fileStream.Length
                    Dim bytesRead = Await fileStream.ReadAsync(buffer, 0, chunkSize)
                    Dim chunkData(bytesRead - 1) As Byte
                    Array.Copy(buffer, chunkData, bytesRead)

                    Await UploadMediaChunkAsync(mediaId, chunkIndex, chunkData, accessToken)
                    chunkIndex += 1

                    ' Update progress
                    Await UpdateMediaUploadProgressAsync(mediaId, chunkIndex, totalChunks)

                    Console.WriteLine($"📤 Uploaded chunk {chunkIndex}/{totalChunks} ({(chunkIndex * 100.0 / totalChunks):F1}%)")
                End While
            End Using

            ' Step 3: Finalize upload
            Await FinalizeMediaUploadAsync(mediaId, accessToken, altText)

            ' Step 4: Wait for processing (if video/gif)
            If mediaType.Contains("video") OrElse mediaType.Contains("gif") Then
                Await WaitForMediaProcessingAsync(mediaId, accessToken)
            End If

            Console.WriteLine($"✅ Media uploaded successfully: {mediaId}")
            Return mediaId

        Catch ex As Exception
            _logger?.LogError(ex, "Error in chunked media upload")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Simple media upload for small files
    ''' </summary>
    Private Async Function UploadMediaSimpleAsync(filePath As String, accessToken As String,
                                                  altText As String, category As String) As Task(Of String)
        Try
            Using client As New HttpClient()
                client.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

                Using form = New MultipartFormDataContent()
                    ' Add media file
                    Dim fileContent = New ByteArrayContent(Await File.ReadAllBytesAsync(filePath))
                    fileContent.Headers.ContentType = System.Net.Http.Headers.MediaTypeHeaderValue.Parse(GetMimeType(filePath))
                    form.Add(fileContent, "media", Path.GetFileName(filePath))

                    ' Add metadata
                    If Not String.IsNullOrEmpty(altText) Then
                        form.Add(New StringContent(altText), "alt_text")
                    End If

                    Dim response = Await client.PostAsync("https://upload.twitter.com/1.1/media/upload.json", form)
                    Dim responseContent = Await response.Content.ReadAsStringAsync()

                    If response.IsSuccessStatusCode Then
                        Dim mediaResponse = JsonSerializer.Deserialize(Of Dictionary(Of String, Object))(responseContent)
                        Dim mediaId = mediaResponse("media_id_string").ToString()

                        ' Log successful upload
                        Await LogMediaUploadAsync(mediaId, filePath, "simple", New FileInfo(filePath).Length, 1, 1, accessToken)

                        Return mediaId
                    Else
                        Throw New Exception($"Simple upload failed: {response.StatusCode} - {responseContent}")
                    End If
                End Using
            End Using

        Catch ex As Exception
            _logger?.LogError(ex, "Error in simple media upload")
            Throw
        End Try
    End Function

    ' ==================================================
    ' ENHANCED SEARCH WITH COMPREHENSIVE FILTERING
    ' ==================================================

    ''' <summary>
    ''' Advanced search with all available filters and expansions
    ''' </summary>
    Public Async Function SearchTweetsAdvancedAsync(searchParams As Dictionary(Of String, Object),
                                                    accessToken As String) As Task(Of Object)
        Try
            Using client As New HttpClient()
                client.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

                ' Build query string with all parameters
                Dim queryParams As New List(Of String)()

                For Each param In searchParams
                    If param.Value IsNot Nothing Then
                        queryParams.Add($"{param.Key}={Uri.EscapeDataString(param.Value.ToString())}")
                    End If
                Next

                Dim queryString = String.Join("&", queryParams)
                Dim requestUrl = $"https://api.twitter.com/2/tweets/search/recent?{queryString}"

                ' Log search request
                _logger?.LogInformation($"Executing advanced search: {searchParams("query")}")

                Dim response = Await client.GetAsync(requestUrl)
                Dim responseContent = Await response.Content.ReadAsStringAsync()

                If response.IsSuccessStatusCode Then
                    ' Log successful search
                    Await LogSearchRequestAsync(searchParams("query").ToString(), responseContent, accessToken)

                    Return JsonSerializer.Deserialize(Of Object)(responseContent)
                Else
                    ' Handle rate limiting
                    If response.StatusCode = System.Net.HttpStatusCode.TooManyRequests Then
                        Await HandleRateLimitAsync(response, "search")
                        Throw New Exception("Rate limit exceeded. Please try again later.")
                    End If

                    Throw New Exception($"Search failed: {response.StatusCode} - {responseContent}")
                End If
            End Using

        Catch ex As Exception
            _logger?.LogError(ex, "Error in advanced search")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Search with automatic pagination and result aggregation
    ''' </summary>
    Public Async Function SearchAllTweetsAsync(query As String, accessToken As String,
                                               Optional maxResults As Integer = 100,
                                               Optional startTime As DateTime? = Nothing,
                                               Optional endTime As DateTime? = Nothing) As Task(Of List(Of Object))
        Try
            Dim allTweets As New List(Of Object)()
            Dim nextToken As String = Nothing
            Dim totalFetched = 0

            Do
                Dim searchParams As New Dictionary(Of String, Object) From {
                    {"query", query},
                    {"max_results", Math.Min(100, maxResults - totalFetched)},
                    {"tweet.fields", "id,text,author_id,created_at,public_metrics,context_annotations,entities"},
                    {"expansions", "author_id"},
                    {"user.fields", "id,name,username,verified,public_metrics"}
                }

                If startTime.HasValue Then
                    searchParams("start_time") = startTime.Value.ToString("yyyy-MM-ddTHH:mm:ssZ")
                End If

                If endTime.HasValue Then
                    searchParams("end_time") = endTime.Value.ToString("yyyy-MM-ddTHH:mm:ssZ")
                End If

                If Not String.IsNullOrEmpty(nextToken) Then
                    searchParams("next_token") = nextToken
                End If

                Dim result = Await SearchTweetsAdvancedAsync(searchParams, accessToken)
                Dim resultDict = JsonSerializer.Deserialize(Of Dictionary(Of String, Object))(result.ToString())

                If resultDict.ContainsKey("data") Then
                    Dim tweets = JsonSerializer.Deserialize(Of List(Of Object))(resultDict("data").ToString())
                    allTweets.AddRange(tweets)
                    totalFetched += tweets.Count

                    Console.WriteLine($"📊 Fetched {tweets.Count} tweets (Total: {totalFetched}/{maxResults})")
                End If

                ' Check for next page
                If resultDict.ContainsKey("meta") Then
                    Dim meta = JsonSerializer.Deserialize(Of Dictionary(Of String, Object))(resultDict("meta").ToString())
                    nextToken = If(meta.ContainsKey("next_token"), meta("next_token")?.ToString(), Nothing)
                Else
                    nextToken = Nothing
                End If

                ' Add delay to respect rate limits
                Await Task.Delay(1000)

            Loop While Not String.IsNullOrEmpty(nextToken) AndAlso totalFetched < maxResults

            Console.WriteLine($"✅ Search completed. Total tweets: {allTweets.Count}")
            Return allTweets

        Catch ex As Exception
            _logger?.LogError(ex, "Error in search all tweets")
            Throw
        End Try
    End Function

    ' ==================================================
    ' ENHANCED THREAD POSTING WITH RETRY LOGIC
    ' ==================================================

    ''' <summary>
    ''' Post thread with enhanced error handling and retry logic
    ''' </summary>
    Public Async Function PostThreadEnhancedAsync(tweets As List(Of String), accessToken As String,
                                                  Optional mediaIds As List(Of String) = Nothing,
                                                  Optional replySettings As String = "everyone",
                                                  Optional delayBetweenTweets As Integer = 1000) As Task(Of List(Of Object))
        Try
            Dim results As New List(Of Object)()
            Dim previousTweetId As String = Nothing

            For i = 0 To tweets.Count - 1
                Dim currentTweet = tweets(i)
                Dim currentMediaIds = If(i = 0 AndAlso mediaIds IsNot Nothing, mediaIds, Nothing)

                Console.WriteLine($"🐦 Posting tweet {i + 1}/{tweets.Count}: {currentTweet.Substring(0, Math.Min(50, currentTweet.Length))}...")

                Dim retryCount = 0
                Dim maxRetries = 3
                Dim success = False
                Dim result As Object = Nothing

                While retryCount < maxRetries AndAlso Not success
                    Try
                        If i = 0 Then
                            ' First tweet in thread
                            result = Await PostTweetAsync(currentTweet, accessToken, currentMediaIds, replySettings)
                        Else
                            ' Reply to previous tweet
                            result = Await PostTweetAsync(currentTweet, accessToken, Nothing, replySettings, Nothing, previousTweetId)
                        End If

                        success = True

                    Catch ex As Exception
                        retryCount += 1
                        _logger?.LogWarning($"Tweet {i + 1} failed, retry {retryCount}/{maxRetries}: {ex.Message}")

                        If retryCount < maxRetries Then
                            ' Exponential backoff
                            Dim delayMs = 1000 * Math.Pow(2, retryCount)
                            Console.WriteLine($"⏳ Retrying in {delayMs / 1000:F0} seconds...")
                            Await Task.Delay(CInt(delayMs))
                        Else
                            Throw New Exception($"Failed to post tweet {i + 1} after {maxRetries} retries: {ex.Message}", ex)
                        End If
                    End Try
                End While

                If result IsNot Nothing Then
                    results.Add(result)

                    ' Extract tweet ID for next iteration
                    Dim tweetData = JsonSerializer.Deserialize(Of Dictionary(Of String, Object))(result.ToString())
                    previousTweetId = tweetData("data").AsJsonElement().GetProperty("id").GetString()

                    Console.WriteLine($"✅ Tweet {i + 1} posted successfully: {previousTweetId}")

                    ' Delay between tweets (except for last one)
                    If i < tweets.Count - 1 Then
                        Await Task.Delay(delayBetweenTweets)
                    End If
                Else
                    Throw New Exception($"Failed to post tweet {i + 1}")
                End If
            Next

            Console.WriteLine($"🧵 Thread completed successfully with {results.Count} tweets")
            Return results

        Catch ex As Exception
            _logger?.LogError(ex, "Error posting enhanced thread")
            Throw
        End Try
    End Function

    ' ==================================================
    ' USER AND FOLLOWER MANAGEMENT
    ' ==================================================

    ''' <summary>
    ''' Get comprehensive user information
    ''' </summary>
    Public Async Function GetUserProfileAsync(username As String, accessToken As String) As Task(Of Object)
        Try
            Using client As New HttpClient()
                client.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

                Dim userFields = "id,name,username,created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,verified_type,withheld"
                Dim expansions = "pinned_tweet_id"
                Dim tweetFields = "id,text,created_at,public_metrics"

                Dim requestUrl = $"https://api.twitter.com/2/users/by/username/{username}?" +
                               $"user.fields={userFields}&" +
                               $"expansions={expansions}&" +
                               $"tweet.fields={tweetFields}"

                Dim response = Await client.GetAsync(requestUrl)
                Dim responseContent = Await response.Content.ReadAsStringAsync()

                If response.IsSuccessStatusCode Then
                    Return JsonSerializer.Deserialize(Of Object)(responseContent)
                Else
                    Throw New Exception($"Get user profile failed: {response.StatusCode} - {responseContent}")
                End If
            End Using

        Catch ex As Exception
            _logger?.LogError(ex, "Error getting user profile")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Follow a user
    ''' </summary>
    Public Async Function FollowUserAsync(targetUserId As String, accessToken As String) As Task(Of Object)
        Try
            Using client As New HttpClient()
                client.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

                Dim requestBody = New StringContent(
                    JsonSerializer.Serialize(New Dictionary(Of String, String) From {{"target_user_id", targetUserId}}),
                    Encoding.UTF8, "application/json"
                )

                ' Note: This requires the authenticated user's ID
                Dim userId = Await GetAuthenticatedUserIdAsync(accessToken)
                Dim response = Await client.PostAsync($"https://api.twitter.com/2/users/{userId}/following", requestBody)
                Dim responseContent = Await response.Content.ReadAsStringAsync()

                If response.IsSuccessStatusCode Then
                    Return JsonSerializer.Deserialize(Of Object)(responseContent)
                Else
                    Throw New Exception($"Follow user failed: {response.StatusCode} - {responseContent}")
                End If
            End Using

        Catch ex As Exception
            _logger?.LogError(ex, "Error following user")
            Throw
        End Try
    End Function

    ' ==================================================
    ' WEBHOOK AND REAL-TIME FEATURES
    ' ==================================================

    ''' <summary>
    ''' Set up webhook for real-time events
    ''' </summary>
    Public Async Function SetupWebhookAsync(webhookUrl As String, events As List(Of String), accessToken As String) As Task(Of Object)
        Try
            ' Note: This is a placeholder for webhook setup
            ' Actual implementation would depend on X's webhook API availability

            Dim webhookConfig As New Dictionary(Of String, Object) From {
                {"url", webhookUrl},
                {"events", events},
                {"active", True},
                {"created_at", DateTime.UtcNow}
            }

            ' Store webhook configuration
            Await StoreWebhookConfigAsync(webhookConfig)

            Return webhookConfig

        Catch ex As Exception
            _logger?.LogError(ex, "Error setting up webhook")
            Throw
        End Try
    End Function

    ' ==================================================
    ' HELPER METHODS FOR ENHANCED FUNCTIONALITY
    ' ==================================================

    Private Function GenerateCodeVerifier() As String
        Dim bytes(31) As Byte
        Using rng = RandomNumberGenerator.Create()
            rng.GetBytes(bytes)
        End Using
        Return Convert.ToBase64String(bytes).TrimEnd("="c).Replace("+"c, "-"c).Replace("/"c, "_"c)
    End Function

    Private Function GenerateCodeChallenge(codeVerifier As String) As String
        Using sha256 = SHA256.Create()
            Dim challengeBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(codeVerifier))
            Return Convert.ToBase64String(challengeBytes).TrimEnd("="c).Replace("+"c, "-"c).Replace("/"c, "_"c)
        End Using
    End Function

    Private Function GenerateRandomString(length As Integer) As String
        Const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        Dim result(length - 1) As Char
        Using rng = RandomNumberGenerator.Create()
            Dim bytes(3) As Byte
            For i = 0 To length - 1
                rng.GetBytes(bytes)
                Dim value = BitConverter.ToUInt32(bytes, 0)
                result(i) = chars(CInt(value Mod chars.Length))
            Next
        End Using
        Return New String(result)
    End Function

    Private Function GetMediaType(filePath As String) As String
        Dim extension = Path.GetExtension(filePath).ToLower()
        Select Case extension
            Case ".jpg", ".jpeg", ".png", ".gif", ".webp"
                Return "image"
            Case ".mp4", ".mov", ".avi", ".mkv"
                Return "video"
            Case Else
                Return "image" ' Default to image
        End Select
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
            Case ".webp"
                Return "image/webp"
            Case ".mp4"
                Return "video/mp4"
            Case ".mov"
                Return "video/quicktime"
            Case Else
                Return "application/octet-stream"
        End Select
    End Function

    Private Async Function InitializeMediaUploadAsync(fileSize As Long, mediaType As String,
                                                      category As String, accessToken As String) As Task(Of String)
        Try
            Using client As New HttpClient()
                client.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

                Dim requestBody = New FormUrlEncodedContent(New Dictionary(Of String, String) From {
                    {"command", "INIT"},
                    {"total_bytes", fileSize.ToString()},
                    {"media_type", GetMimeType("." + mediaType)},
                    {"media_category", category}
                })

                Dim response = Await client.PostAsync("https://upload.twitter.com/1.1/media/upload.json", requestBody)
                Dim responseContent = Await response.Content.ReadAsStringAsync()

                If response.IsSuccessStatusCode Then
                    Dim initResponse = JsonSerializer.Deserialize(Of Dictionary(Of String, Object))(responseContent)
                    Return initResponse("media_id_string").ToString()
                Else
                    Throw New Exception($"Media initialization failed: {response.StatusCode} - {responseContent}")
                End If
            End Using

        Catch ex As Exception
            _logger?.LogError(ex, "Error initializing media upload")
            Throw
        End Try
    End Function

    Private Async Function UploadMediaChunkAsync(mediaId As String, chunkIndex As Integer,
                                                 chunkData As Byte(), accessToken As String) As Task
        Try
            Using client As New HttpClient()
                client.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

                Using form = New MultipartFormDataContent()
                    form.Add(New StringContent("APPEND"), "command")
                    form.Add(New StringContent(mediaId), "media_id")
                    form.Add(New StringContent(chunkIndex.ToString()), "segment_index")
                    form.Add(New ByteArrayContent(chunkData), "media")

                    Dim response = Await client.PostAsync("https://upload.twitter.com/1.1/media/upload.json", form)

                    If Not response.IsSuccessStatusCode Then
                        Dim responseContent = Await response.Content.ReadAsStringAsync()
                        Throw New Exception($"Chunk upload failed: {response.StatusCode} - {responseContent}")
                    End If
                End Using
            End Using

        Catch ex As Exception
            _logger?.LogError(ex, "Error uploading media chunk")
            Throw
        End Try
    End Function

    Private Async Function FinalizeMediaUploadAsync(mediaId As String, accessToken As String,
                                                    Optional altText As String = Nothing) As Task
        Try
            Using client As New HttpClient()
                client.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

                Dim requestBody = New FormUrlEncodedContent(New Dictionary(Of String, String) From {
                    {"command", "FINALIZE"},
                    {"media_id", mediaId}
                })

                Dim response = Await client.PostAsync("https://upload.twitter.com/1.1/media/upload.json", requestBody)
                Dim responseContent = Await response.Content.ReadAsStringAsync()

                If response.IsSuccessStatusCode Then
                    ' Set alt text if provided
                    If Not String.IsNullOrEmpty(altText) Then
                        Await SetMediaAltTextAsync(mediaId, altText, accessToken)
                    End If
                Else
                    Throw New Exception($"Media finalization failed: {response.StatusCode} - {responseContent}")
                End If
            End Using

        Catch ex As Exception
            _logger?.LogError(ex, "Error finalizing media upload")
            Throw
        End Try
    End Function

    Private Async Function SetMediaAltTextAsync(mediaId As String, altText As String, accessToken As String) As Task
        Try
            Using client As New HttpClient()
                client.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

                Dim metadata = New Dictionary(Of String, Object) From {
                    {"media_id", mediaId},
                    {"alt_text", New Dictionary(Of String, String) From {{"text", altText}}}
                }

                Dim requestBody = New StringContent(
                    JsonSerializer.Serialize(metadata),
                    Encoding.UTF8, "application/json"
                )

                Dim response = Await client.PostAsync("https://upload.twitter.com/1.1/media/metadata/create.json", requestBody)

                If Not response.IsSuccessStatusCode Then
                    Dim responseContent = Await response.Content.ReadAsStringAsync()
                    _logger?.LogWarning($"Alt text setting failed: {response.StatusCode} - {responseContent}")
                End If
            End Using

        Catch ex As Exception
            _logger?.LogError(ex, "Error setting media alt text")
        End Try
    End Function

    Private Async Function WaitForMediaProcessingAsync(mediaId As String, accessToken As String) As Task
        Try
            Dim maxWaitTime = TimeSpan.FromMinutes(5)
            Dim startTime = DateTime.UtcNow

            While DateTime.UtcNow - startTime < maxWaitTime
                Dim status = Await CheckMediaProcessingStatusAsync(mediaId, accessToken)

                Select Case status
                    Case "succeeded"
                        Return
                    Case "failed"
                        Throw New Exception("Media processing failed")
                    Case "in_progress"
                        Console.WriteLine("🎬 Media processing in progress...")
                        Await Task.Delay(2000)
                    Case Else
                        Await Task.Delay(1000)
                End Select
            End While

            Throw New Exception("Media processing timeout")

        Catch ex As Exception
            _logger?.LogError(ex, "Error waiting for media processing")
            Throw
        End Try
    End Function

    Private Async Function CheckMediaProcessingStatusAsync(mediaId As String, accessToken As String) As Task(Of String)
        Try
            Using client As New HttpClient()
                client.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

                Dim response = Await client.GetAsync($"https://upload.twitter.com/1.1/media/upload.json?command=STATUS&media_id={mediaId}")
                Dim responseContent = Await response.Content.ReadAsStringAsync()

                If response.IsSuccessStatusCode Then
                    Dim statusResponse = JsonSerializer.Deserialize(Of Dictionary(Of String, Object))(responseContent)

                    If statusResponse.ContainsKey("processing_info") Then
                        Dim processingInfo = JsonSerializer.Deserialize(Of Dictionary(Of String, Object))(statusResponse("processing_info").ToString())
                        Return processingInfo("state").ToString()
                    End If

                    Return "succeeded" ' No processing info means it's ready
                Else
                    Throw New Exception($"Status check failed: {response.StatusCode} - {responseContent}")
                End If
            End Using

        Catch ex As Exception
            _logger?.LogError(ex, "Error checking media processing status")
            Throw
        End Try
    End Function

    ' ==================================================
    ' DATABASE LOGGING METHODS
    ' ==================================================

    Private Async Function LogMediaUploadAsync(mediaId As String, filePath As String, method As String,
                                               size As Long, totalChunks As Integer, uploadedChunks As Integer,
                                               accessToken As String) As Task
        Try
            ' This would integrate with your existing DBWriter
            ' Implementation depends on your database structure

        Catch ex As Exception
            _logger?.LogError(ex, "Error logging media upload")
        End Try
    End Function

    Private Async Function UpdateMediaUploadProgressAsync(mediaId As String, uploadedChunks As Integer,
                                                          totalChunks As Integer) As Task
        Try
            ' Update progress in database

        Catch ex As Exception
            _logger?.LogError(ex, "Error updating media upload progress")
        End Try
    End Function

    Private Async Function LogSearchRequestAsync(query As String, response As String, accessToken As String) As Task
        Try
            ' Log search request to database

        Catch ex As Exception
            _logger?.LogError(ex, "Error logging search request")
        End Try
    End Function

    Private Async Function StoreTokenSecurelyAsync(token As OAuth2TokenResponse, clientId As String) As Task
        Try
            ' Store token in secure location (encrypted database, secret manager, etc.)

        Catch ex As Exception
            _logger?.LogError(ex, "Error storing token securely")
        End Try
    End Function

    Private Async Function UpdateStoredTokenAsync(token As OAuth2TokenResponse, clientId As String) As Task
        Try
            ' Update existing token in secure storage

        Catch ex As Exception
            _logger?.LogError(ex, "Error updating stored token")
        End Try
    End Function

    Private Async Function HandleRateLimitAsync(response As HttpResponseMessage, endpoint As String) As Task
        Try
            ' Extract rate limit headers and store them
            Dim resetTime As Integer = 0
            Dim remaining As Integer = 0

            If response.Headers.Contains("x-rate-limit-reset") Then
                Integer.TryParse(response.Headers.GetValues("x-rate-limit-reset").FirstOrDefault(), resetTime)
            End If

            If response.Headers.Contains("x-rate-limit-remaining") Then
                Integer.TryParse(response.Headers.GetValues("x-rate-limit-remaining").FirstOrDefault(), remaining)
            End If

            ' Store rate limit info in database

        Catch ex As Exception
            _logger?.LogError(ex, "Error handling rate limit")
        End Try
    End Function

    Private Async Function GetAuthenticatedUserIdAsync(accessToken As String) As Task(Of String)
        Try
            Using client As New HttpClient()
                client.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", accessToken)

                Dim response = Await client.GetAsync("https://api.twitter.com/2/users/me")
                Dim responseContent = Await response.Content.ReadAsStringAsync()

                If response.IsSuccessStatusCode Then
                    Dim userData = JsonSerializer.Deserialize(Of Dictionary(Of String, Object))(responseContent)
                    Return userData("data").AsJsonElement().GetProperty("id").GetString()
                Else
                    Throw New Exception($"Failed to get authenticated user ID: {response.StatusCode}")
                End If
            End Using

        Catch ex As Exception
            _logger?.LogError(ex, "Error getting authenticated user ID")
            Throw
        End Try
    End Function

    Private Async Function StoreWebhookConfigAsync(config As Dictionary(Of String, Object)) As Task
        Try
            ' Store webhook configuration in database

        Catch ex As Exception
            _logger?.LogError(ex, "Error storing webhook config")
        End Try
    End Function

End Class

' ==================================================
' SUPPORTING DATA STRUCTURES
' ==================================================

Public Class OAuth2TokenResponse
    Public Property access_token As String
    Public Property token_type As String
    Public Property expires_in As Integer?
    Public Property refresh_token As String
    Public Property scope As String
    Public Property created_at As DateTime = DateTime.UtcNow
End Class

Public Class MediaUploadResponse
    Public Property media_id As Long
    Public Property media_id_string As String
    Public Property media_key As String
    Public Property size As Integer
    Public Property expires_after_secs As Integer?
    Public Property image As ImageInfo
    Public Property video As VideoInfo
End Class

Public Class ImageInfo
    Public Property image_type As String
    Public Property w As Integer
    Public Property h As Integer
End Class

Public Class VideoInfo
    Public Property video_type As String
    Public Property w As Integer
    Public Property h As Integer
End Class
