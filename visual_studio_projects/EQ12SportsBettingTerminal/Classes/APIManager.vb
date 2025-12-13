' EQ12 Sports Betting Terminal - API Manager
' Centralized API management for all external services including rate limiting and authentication

Imports System.Net.Http
Imports System.Threading.Tasks
Imports System.Collections.Concurrent
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.Text
Imports System.Threading
Imports System.IO

Public Class APIManager

    Private Shared ReadOnly httpClient As New HttpClient()
    Private rateLimiters As New ConcurrentDictionary(Of String, RateLimiter)
    Private apiConfigurations As New Dictionary(Of String, APIConfiguration)
    Private logger As Action(Of String, String)

    ' API Statistics
    Private requestCount As Long = 0
    Private errorCount As Long = 0
    Private lastResetTime As DateTime = DateTime.Now

    ' Configuration
    Private Const DefaultTimeout As Integer = 30
    Private Const MaxRetries As Integer = 3
    Private Const RetryDelay As Integer = 1000

    Public Event APICallCompleted(apiName As String, success As Boolean, responseTime As TimeSpan)
    Public Event RateLimitExceeded(apiName As String, resetTime As DateTime)
    Public Event APIError(apiName As String, errorMessage As String, statusCode As Integer)

    Public Sub New()
        InitializeAPIs()

        ' Set up logging
        logger = Sub(message As String, level As String)
                     Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] [{level}] APIManager: {message}")
                 End Sub

        ' Configure HTTP client
        httpClient.Timeout = TimeSpan.FromSeconds(DefaultTimeout)
        httpClient.DefaultRequestHeaders.Add("User-Agent", "EQ12-Sports-Terminal/1.0")

        logger("API Manager initialized with all services", "SUCCESS")
    End Sub

    Private Sub InitializeAPIs()
        Try
            ' The Odds API Configuration
            apiConfigurations("odds_api") = New APIConfiguration With {
                .BaseUrl = "https://api.the-odds-api.com/v4/",
                .ApiKey = Environment.GetEnvironmentVariable("ODDS_API_KEY"),
                .RateLimit = New RateLimit With {.RequestsPerMinute = 500, .RequestsPerMonth = 25000},
                .RequiresAuth = True,
                .AuthType = "query_param",
                .AuthKey = "apiKey"
            }

            ' OpenAI API Configuration
            apiConfigurations("openai") = New APIConfiguration With {
                .BaseUrl = "https://api.openai.com/v1/",
                .ApiKey = Environment.GetEnvironmentVariable("OPENAI_API_KEY"),
                .RateLimit = New RateLimit With {.RequestsPerMinute = 60, .TokensPerMinute = 90000},
                .RequiresAuth = True,
                .AuthType = "bearer",
                .AuthKey = "Authorization"
            }

            ' Telegram Bot API Configuration
            apiConfigurations("telegram") = New APIConfiguration With {
                .BaseUrl = "https://api.telegram.org/bot",
                .ApiKey = Environment.GetEnvironmentVariable("TELEGRAM_BOT_TOKEN"),
                .RateLimit = New RateLimit With {.RequestsPerMinute = 30, .RequestsPerSecond = 1},
                .RequiresAuth = True,
                .AuthType = "url_token"
            }

            ' Discord API Configuration
            apiConfigurations("discord") = New APIConfiguration With {
                .BaseUrl = "https://discord.com/api/v10/",
                .ApiKey = Environment.GetEnvironmentVariable("DISCORD_BOT_TOKEN"),
                .RateLimit = New RateLimit With {.RequestsPerMinute = 300, .RequestsPerSecond = 5},
                .RequiresAuth = True,
                .AuthType = "bearer",
                .AuthKey = "Authorization"
            }

            ' Twitter/X API Configuration
            apiConfigurations("twitter") = New APIConfiguration With {
                .BaseUrl = "https://api.twitter.com/2/",
                .ApiKey = Environment.GetEnvironmentVariable("TWITTER_BEARER_TOKEN"),
                .RateLimit = New RateLimit With {.RequestsPerMinute = 300, .RequestsPer15Minutes = 900},
                .RequiresAuth = True,
                .AuthType = "bearer",
                .AuthKey = "Authorization"
            }

            ' DraftKings API Configuration (unofficial)
            apiConfigurations("draftkings") = New APIConfiguration With {
                .BaseUrl = "https://sportsbook-us-il.draftkings.com/sites/US-IL-SB/api/v5/",
                .RateLimit = New RateLimit With {.RequestsPerMinute = 60, .RequestsPerSecond = 2},
                .RequiresAuth = False
            }

            ' FanDuel API Configuration (unofficial)
            apiConfigurations("fanduel") = New APIConfiguration With {
                .BaseUrl = "https://sbapi.il.sportsbook.fanduel.com/api/",
                .RateLimit = New RateLimit With {.RequestsPerMinute = 60, .RequestsPerSecond = 2},
                .RequiresAuth = False
            }

            ' Initialize rate limiters
            For Each api In apiConfigurations
                rateLimiters(api.Key) = New RateLimiter(api.Value.RateLimit)
            Next

        Catch ex As Exception
            logger($"Error initializing APIs: {ex.Message}", "ERROR")
            Throw
        End Try
    End Sub

    Public Async Function CallOddsAPI(endpoint As String, Optional parameters As Dictionary(Of String, String) = Nothing) As Task(Of APIResponse)
        Return Await MakeAPICall("odds_api", endpoint, "GET", parameters)
    End Function

    Public Async Function CallOpenAI(endpoint As String, requestBody As Object, Optional headers As Dictionary(Of String, String) = Nothing) As Task(Of APIResponse)
        Return Await MakeAPICall("openai", endpoint, "POST", Nothing, requestBody, headers)
    End Function

    Public Async Function CallTelegram(endpoint As String, requestBody As Object) As Task(Of APIResponse)
        Return Await MakeAPICall("telegram", endpoint, "POST", Nothing, requestBody)
    End Function

    Public Async Function CallDiscord(endpoint As String, requestBody As Object, Optional headers As Dictionary(Of String, String) = Nothing) As Task(Of APIResponse)
        Return Await MakeAPICall("discord", endpoint, "POST", Nothing, requestBody, headers)
    End Function

    Public Async Function CallTwitter(endpoint As String, Optional method As String = "GET", Optional parameters As Dictionary(Of String, String) = Nothing, Optional requestBody As Object = Nothing) As Task(Of APIResponse)
        Return Await MakeAPICall("twitter", endpoint, method, parameters, requestBody)
    End Function

    Public Async Function ScrapeOdds(sportsbook As String, sport As String) As Task(Of APIResponse)
        Try
            Select Case sportsbook.ToLower()
                Case "draftkings"
                    Return Await MakeAPICall("draftkings", $"eventgroups/{sport}/categories/487/subcategories/4511", "GET")
                Case "fanduel"
                    Return Await MakeAPICall("fanduel", $"content-managed-cms/query?machineName=fp_nj_homepage_hero", "GET")
                Case Else
                    Return New APIResponse With {
                        .Success = False,
                        .ErrorMessage = $"Unsupported sportsbook: {sportsbook}",
                        .StatusCode = 400
                    }
            End Select

        Catch ex As Exception
            logger($"Error scraping odds from {sportsbook}: {ex.Message}", "ERROR")
            Return New APIResponse With {
                .Success = False,
                .ErrorMessage = ex.Message,
                .StatusCode = 500
            }
        End Try
    End Function

    Private Async Function MakeAPICall(apiName As String, endpoint As String, method As String, Optional parameters As Dictionary(Of String, String) = Nothing, Optional requestBody As Object = Nothing, Optional customHeaders As Dictionary(Of String, String) = Nothing) As Task(Of APIResponse)
        Try
            ' Check if API is configured
            If Not apiConfigurations.ContainsKey(apiName) Then
                Return New APIResponse With {
                    .Success = False,
                    .ErrorMessage = $"API '{apiName}' not configured",
                    .StatusCode = 400
                }
            End If

            Dim config = apiConfigurations(apiName)

            ' Check rate limits
            If Not Await CheckRateLimit(apiName) Then
                Dim resetTime = rateLimiters(apiName).GetResetTime()
                RaiseEvent RateLimitExceeded(apiName, resetTime)

                Return New APIResponse With {
                    .Success = False,
                    .ErrorMessage = "Rate limit exceeded",
                    .StatusCode = 429,
                    .RetryAfter = resetTime
                }
            End If

            ' Build request URL
            Dim url = BuildRequestUrl(config, endpoint, parameters)

            ' Create HTTP request
            Dim request As HttpRequestMessage = Nothing

            Select Case method.ToUpper()
                Case "GET"
                    request = New HttpRequestMessage(HttpMethod.Get, url)
                Case "POST"
                    request = New HttpRequestMessage(HttpMethod.Post, url)
                    If requestBody IsNot Nothing Then
                        Dim json = JsonConvert.SerializeObject(requestBody)
                        request.Content = New StringContent(json, Encoding.UTF8, "application/json")
                    End If
                Case "PUT"
                    request = New HttpRequestMessage(HttpMethod.Put, url)
                    If requestBody IsNot Nothing Then
                        Dim json = JsonConvert.SerializeObject(requestBody)
                        request.Content = New StringContent(json, Encoding.UTF8, "application/json")
                    End If
                Case Else
                    Return New APIResponse With {
                        .Success = False,
                        .ErrorMessage = $"Unsupported HTTP method: {method}",
                        .StatusCode = 400
                    }
            End Select

            ' Add authentication
            AddAuthentication(request, config)

            ' Add custom headers
            If customHeaders IsNot Nothing Then
                For Each header In customHeaders
                    request.Headers.Add(header.Key, header.Value)
                Next
            End If

            ' Make the API call with retry logic
            Return Await MakeRequestWithRetry(apiName, request)

        Catch ex As Exception
            logger($"Error making API call to {apiName}: {ex.Message}", "ERROR")

            Return New APIResponse With {
                .Success = False,
                .ErrorMessage = ex.Message,
                .StatusCode = 500
            }
        End Try
    End Function

    Private Async Function CheckRateLimit(apiName As String) As Task(Of Boolean)
        Try
            If rateLimiters.ContainsKey(apiName) Then
                Return Await rateLimiters(apiName).CanMakeRequest()
            End If
            Return True

        Catch ex As Exception
            logger($"Error checking rate limit for {apiName}: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Private Function BuildRequestUrl(config As APIConfiguration, endpoint As String, parameters As Dictionary(Of String, String)) As String
        Try
            Dim url = config.BaseUrl

            ' Handle special URL patterns
            Select Case config.AuthType
                Case "url_token"
                    ' For Telegram: https://api.telegram.org/bot{token}/method
                    url &= config.ApiKey & "/" & endpoint
                Case Else
                    url &= endpoint
            End Select

            ' Add query parameters
            If parameters IsNot Nothing AndAlso parameters.Count > 0 Then
                Dim queryString = String.Join("&", parameters.Select(Function(p) $"{p.Key}={Uri.EscapeDataString(p.Value)}"))

                ' Add API key as query parameter if needed
                If config.RequiresAuth AndAlso config.AuthType = "query_param" Then
                    queryString &= $"&{config.AuthKey}={config.ApiKey}"
                End If

                url &= "?" & queryString
            ElseIf config.RequiresAuth AndAlso config.AuthType = "query_param" Then
                url &= $"?{config.AuthKey}={config.ApiKey}"
            End If

            Return url

        Catch ex As Exception
            logger($"Error building request URL: {ex.Message}", "ERROR")
            Return config.BaseUrl & endpoint
        End Try
    End Function

    Private Sub AddAuthentication(request As HttpRequestMessage, config As APIConfiguration)
        Try
            If Not config.RequiresAuth OrElse String.IsNullOrEmpty(config.ApiKey) Then
                Return
            End If

            Select Case config.AuthType
                Case "bearer"
                    request.Headers.Add("Authorization", $"Bearer {config.ApiKey}")
                Case "api_key"
                    request.Headers.Add(config.AuthKey, config.ApiKey)
                Case "query_param", "url_token"
                    ' Already handled in URL building
            End Select

        Catch ex As Exception
            logger($"Error adding authentication: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Async Function MakeRequestWithRetry(apiName As String, request As HttpRequestMessage) As Task(Of APIResponse)
        Dim lastException As Exception = Nothing

        For attempt As Integer = 1 To MaxRetries
            Try
                Dim stopwatch = Stopwatch.StartNew()

                Using response = Await httpClient.SendAsync(request)
                    stopwatch.Stop()

                    Dim content = Await response.Content.ReadAsStringAsync()
                    Dim success = response.IsSuccessStatusCode

                    ' Update statistics
                    Interlocked.Increment(requestCount)
                    If Not success Then
                        Interlocked.Increment(errorCount)
                    End If

                    ' Update rate limiter
                    If rateLimiters.ContainsKey(apiName) Then
                        rateLimiters(apiName).RecordRequest()
                    End If

                    ' Raise event
                    RaiseEvent APICallCompleted(apiName, success, stopwatch.Elapsed)

                    If success Then
                        logger($"API call to {apiName} successful ({stopwatch.ElapsedMilliseconds}ms)", "SUCCESS")

                        Return New APIResponse With {
                            .Success = True,
                            .Content = content,
                            .StatusCode = CInt(response.StatusCode),
                            .ResponseTime = stopwatch.Elapsed,
                            .Headers = response.Headers.ToDictionary(Function(h) h.Key, Function(h) String.Join(",", h.Value))
                        }
                    Else
                        ' Handle specific error cases
                        Dim errorResponse = New APIResponse With {
                            .Success = False,
                            .Content = content,
                            .StatusCode = CInt(response.StatusCode),
                            .ErrorMessage = $"HTTP {response.StatusCode}: {response.ReasonPhrase}",
                            .ResponseTime = stopwatch.Elapsed
                        }

                        ' Check if we should retry
                        If ShouldRetry(response.StatusCode) AndAlso attempt < MaxRetries Then
                            logger($"API call to {apiName} failed, retrying attempt {attempt + 1}/{MaxRetries}", "WARNING")
                            Await Task.Delay(RetryDelay * attempt)
                            Continue For
                        End If

                        RaiseEvent APIError(apiName, errorResponse.ErrorMessage, errorResponse.StatusCode)
                        logger($"API call to {apiName} failed: {errorResponse.ErrorMessage}", "ERROR")

                        Return errorResponse
                    End If
                End Using

            Catch ex As Exception
                lastException = ex
                logger($"Exception during API call to {apiName} (attempt {attempt}): {ex.Message}", "ERROR")

                If attempt < MaxRetries Then
                    Await Task.Delay(RetryDelay * attempt)
                End If
            End Try
        Next

        ' All retries exhausted
        Interlocked.Increment(errorCount)

        Return New APIResponse With {
            .Success = False,
            .ErrorMessage = lastException?.Message ?? "All retry attempts failed",
            .StatusCode = 500
        }
    End Function

    Private Function ShouldRetry(statusCode As Net.HttpStatusCode) As Boolean
        ' Retry on temporary failures
        Return statusCode = Net.HttpStatusCode.RequestTimeout OrElse
               statusCode = Net.HttpStatusCode.InternalServerError OrElse
               statusCode = Net.HttpStatusCode.BadGateway OrElse
               statusCode = Net.HttpStatusCode.ServiceUnavailable OrElse
               statusCode = Net.HttpStatusCode.GatewayTimeout
    End Function

    Public Function GetAPIStatistics() As Dictionary(Of String, Object)
        Try
            Dim stats As New Dictionary(Of String, Object) From {
                {"total_requests", requestCount},
                {"total_errors", errorCount},
                {"success_rate", If(requestCount > 0, (requestCount - errorCount) / requestCount * 100, 0)},
                {"uptime", DateTime.Now.Subtract(lastResetTime).ToString()},
                {"configured_apis", apiConfigurations.Keys.ToList()},
                {"rate_limiters", rateLimiters.Keys.ToList()}
            }

            ' Add per-API statistics
            For Each api In apiConfigurations.Keys
                If rateLimiters.ContainsKey(api) Then
                    stats($"{api}_requests_remaining") = rateLimiters(api).GetRemainingRequests()
                    stats($"{api}_reset_time") = rateLimiters(api).GetResetTime()
                End If
            Next

            Return stats

        Catch ex As Exception
            logger($"Error getting API statistics: {ex.Message}", "ERROR")
            Return New Dictionary(Of String, Object)
        End Try
    End Function

    Public Sub ResetStatistics()
        Try
            requestCount = 0
            errorCount = 0
            lastResetTime = DateTime.Now

            ' Reset rate limiters
            For Each limiter In rateLimiters.Values
                limiter.Reset()
            Next

            logger("API statistics reset", "INFO")

        Catch ex As Exception
            logger($"Error resetting statistics: {ex.Message}", "ERROR")
        End Try
    End Sub

    Public Function ValidateAPIKeys() As Dictionary(Of String, Boolean)
        Try
            Dim results As New Dictionary(Of String, Boolean)

            For Each api In apiConfigurations
                Dim config = api.Value
                Dim isValid = Not String.IsNullOrEmpty(config.ApiKey)

                ' Additional validation based on API type
                Select Case api.Key
                    Case "odds_api"
                        isValid = isValid AndAlso config.ApiKey.Length >= 30
                    Case "openai"
                        isValid = isValid AndAlso config.ApiKey.StartsWith("sk-")
                    Case "telegram"
                        isValid = isValid AndAlso config.ApiKey.Contains(":")
                End Select

                results(api.Key) = isValid
            Next

            Return results

        Catch ex As Exception
            logger($"Error validating API keys: {ex.Message}", "ERROR")
            Return New Dictionary(Of String, Boolean)
        End Try
    End Function

    Public Sub Dispose()
        Try
            httpClient?.Dispose()
            logger($"API Manager disposed. Total requests: {requestCount}", "INFO")

        Catch ex As Exception
            logger($"Error disposing API Manager: {ex.Message}", "ERROR")
        End Try
    End Sub

End Class

' Supporting classes
Public Class APIConfiguration
    Public Property BaseUrl As String
    Public Property ApiKey As String
    Public Property RateLimit As RateLimit
    Public Property RequiresAuth As Boolean
    Public Property AuthType As String ' bearer, api_key, query_param, url_token
    Public Property AuthKey As String
End Class

Public Class RateLimit
    Public Property RequestsPerSecond As Integer = 0
    Public Property RequestsPerMinute As Integer = 0
    Public Property RequestsPer15Minutes As Integer = 0
    Public Property RequestsPerMonth As Integer = 0
    Public Property TokensPerMinute As Integer = 0
End Class

Public Class APIResponse
    Public Property Success As Boolean
    Public Property Content As String
    Public Property StatusCode As Integer
    Public Property ErrorMessage As String
    Public Property ResponseTime As TimeSpan
    Public Property Headers As Dictionary(Of String, String)
    Public Property RetryAfter As DateTime?
End Class

Public Class RateLimiter
    Private ReadOnly rateLimit As RateLimit
    Private ReadOnly requests As New ConcurrentQueue(Of DateTime)
    Private ReadOnly lockObject As New Object()

    Public Sub New(rateLimit As RateLimit)
        Me.rateLimit = rateLimit
    End Sub

    Public Async Function CanMakeRequest() As Task(Of Boolean)
        Try
            SyncLock lockObject
                Dim now = DateTime.Now

                ' Clean old requests
                While requests.Count > 0
                    Dim oldRequest As DateTime
                    If requests.TryPeek(oldRequest) AndAlso now.Subtract(oldRequest).TotalMinutes > 1 Then
                        requests.TryDequeue(oldRequest)
                    Else
                        Exit While
                    End If
                End While

                ' Check limits
                If rateLimit.RequestsPerSecond > 0 Then
                    Dim recentRequests = requests.Where(Function(r) now.Subtract(r).TotalSeconds < 1).Count()
                    If recentRequests >= rateLimit.RequestsPerSecond Then
                        Return False
                    End If
                End If

                If rateLimit.RequestsPerMinute > 0 Then
                    Dim recentRequests = requests.Where(Function(r) now.Subtract(r).TotalMinutes < 1).Count()
                    If recentRequests >= rateLimit.RequestsPerMinute Then
                        Return False
                    End If
                End If

                Return True
            End SyncLock

        Catch ex As Exception
            Return False
        End Try
    End Function

    Public Sub RecordRequest()
        requests.Enqueue(DateTime.Now)
    End Sub

    Public Function GetRemainingRequests() As Integer
        Try
            SyncLock lockObject
                Dim now = DateTime.Now
                Dim recentRequests = requests.Where(Function(r) now.Subtract(r).TotalMinutes < 1).Count()
                Return Math.Max(0, rateLimit.RequestsPerMinute - recentRequests)
            End SyncLock

        Catch ex As Exception
            Return 0
        End Try
    End Function

    Public Function GetResetTime() As DateTime
        Return DateTime.Now.AddMinutes(1)
    End Function

    Public Sub Reset()
        While Not requests.IsEmpty
            Dim dummy As DateTime
            requests.TryDequeue(dummy)
        End While
    End Sub

End Class
