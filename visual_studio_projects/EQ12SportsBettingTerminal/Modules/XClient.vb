' ===============================================================================
' XClient.vb - X/Twitter API Integration for EQ12
' Reads tweets by keywords (injuries, trades, odds)
' Logs everything into integration_log
' Pipes data into ContentEngine + LiveWatch for real-time betting intelligence
' ===============================================================================

Imports System.Net.Http
Imports System.Net.Http.Headers
Imports Newtonsoft.Json.Linq
Imports System.Threading.Tasks
Imports System.Text.RegularExpressions
Imports System.Data.SQLite

Public Class XClient
    Private Shared ReadOnly HttpClient As New HttpClient()
    Private ReadOnly _bearerToken As String
    Private ReadOnly _apiBaseUrl As String = "https://api.x.com/2"
    Private ReadOnly _dbWriter As DBWriter
    Private ReadOnly _logger As Logger

    ' X API Rate Limits (Basic Tier - $200/month)
    Private Const MaxTweetsPerMonth As Integer = 50000
    Private Const MaxReadsPerMonth As Integer = 15000
    Private Shared _monthlyTweetCount As Integer = 0
    Private Shared _monthlyReadCount As Integer = 0

    Public Sub New(Optional bearerToken As String = "")
        _bearerToken = If(String.IsNullOrEmpty(bearerToken), Config("twitter")("bearer_token"), bearerToken)
        _dbWriter = New DBWriter()
        _logger = New Logger("XClient")

        ' Configure HttpClient
        HttpClient.DefaultRequestHeaders.Clear()
        HttpClient.DefaultRequestHeaders.Authorization = New AuthenticationHeaderValue("Bearer", _bearerToken)
        HttpClient.DefaultRequestHeaders.Add("User-Agent", "EQ12-XClient/1.0")

        _logger.Info("XClient initialized with X API v2")
    End Sub

    ' ===============================================================================
    ' CORE SEARCH FUNCTIONALITY - Read tweets by keywords
    ' ===============================================================================

    ''' <summary>
    ''' Search tweets for betting intelligence keywords (injuries, trades, odds)
    ''' </summary>
    Public Async Function SearchBettingIntelligence(Optional maxResults As Integer = 100) As Task(Of List(Of BettingTweet))
        Try
            Dim allTweets As New List(Of BettingTweet)

            ' Key betting intelligence keywords
            Dim searchQueries = {
                "injury report NFL NBA MLB",           ' Player injuries
                "trade rumors news NFL NBA MLB",      ' Trade news
                "line movement odds steam",           ' Line movements
                "inactive scratched doubtful",       ' Game status changes
                "weather delay postponed",           ' Weather impacts
                "starting lineup rotation",          ' Lineup changes
                "suspension fine disciplinary"       ' Player availability
            }

            For Each query In searchQueries
                _logger.Info($"Searching X for: {query}")

                Dim tweets = Await SearchTweetsByQuery(query, maxResults \ searchQueries.Length)
                allTweets.AddRange(tweets)

                ' Rate limiting - Basic tier allows 300 requests per 15 minutes
                Await Task.Delay(2000)
            Next

            ' Log search results to integration_log
            LogSearchResults("betting_intelligence", allTweets.Count)

            ' Process tweets for betting insights
            Await ProcessTweetsForBettingInsights(allTweets)

            Return allTweets

        Catch ex As Exception
            _logger.Error($"Betting intelligence search failed: {ex.Message}")
            Return New List(Of BettingTweet)()
        End Try
    End Function

    ''' <summary>
    ''' Search tweets by specific query with enhanced metadata
    ''' </summary>
    Public Async Function SearchTweetsByQuery(query As String, Optional maxResults As Integer = 50) As Task(Of List(Of BettingTweet))
        Try
            CheckRateLimit("search")

            ' Enhanced search with tweet fields for better analysis
            Dim url = $"{_apiBaseUrl}/tweets/search/recent" &
                     $"?query={Uri.EscapeDataString(query)}" &
                     $"&max_results={Math.Min(maxResults, 100)}" &
                     $"&tweet.fields=created_at,author_id,public_metrics,context_annotations,entities" &
                     $"&user.fields=verified,public_metrics" &
                     $"&expansions=author_id"

            Dim response = Await HttpClient.GetStringAsync(url)
            Dim data = JObject.Parse(response)

            _monthlyReadCount += 1

            Dim tweets = ParseTweetsResponse(data, query)

            ' Log successful search
            DBWriter.LogXAction("search", "", query, tweets.Count, "success", $"Retrieved {tweets.Count} tweets for query: {query}")

            ' Log monetization tracking for search
            DBWriter.LogXMonetization("search", "", 0.0, 0, 0.0, 0.01, "", "twitter") ' Estimated $0.01 API cost per search

            Return tweets

        Catch ex As HttpRequestException When ex.Message.Contains("429")
            _logger.Warning("X API rate limit hit - backing off")

            ' Log rate limit failure
            DBWriter.LogXAction("search", "", query, 0, "fail", "Rate limit exceeded - 429 error")

            Await Task.Delay(15 * 60 * 1000) ' Wait 15 minutes
            Return New List(Of BettingTweet)()
        Catch ex As Exception
            _logger.Error($"Tweet search failed: {ex.Message}")

            ' Log search failure
            DBWriter.LogXAction("search", "", query, 0, "fail", $"Search error: {ex.Message}")

            Return New List(Of BettingTweet)()
        End Try
    End Function

    ' ===============================================================================
    ' BETTING INTELLIGENCE PROCESSING
    ' ===============================================================================

    Private Async Function ProcessTweetsForBettingInsights(tweets As List(Of BettingTweet)) As Task
        Try
            For Each tweet In tweets
                ' Classify tweet type and extract betting intelligence
                Dim insight = ExtractBettingIntelligence(tweet)

                If insight IsNot Nothing Then
                    ' Log to integration_log with betting context
                    LogBettingIntelligence(tweet, insight)

                    ' Pipe to ContentEngine for content generation
                    Await PipeToContentEngine(tweet, insight)

                    ' Pipe to LiveWatch for real-time alerts
                    Await PipeToLiveWatch(tweet, insight)

                    ' Check for arbitrage opportunities triggered by news
                    Await CheckArbitrageOpportunities(insight)
                End If
            Next

        Catch ex As Exception
            _logger.Error($"Betting insights processing failed: {ex.Message}")
        End Try
    End Function

    Private Function ExtractBettingIntelligence(tweet As BettingTweet) As BettingIntelligence
        Try
            Dim intelligence As New BettingIntelligence With {
                .TweetId = tweet.Id,
                .Timestamp = tweet.CreatedAt,
                .OriginalText = tweet.Text,
                .Author = tweet.Author,
                .Metrics = tweet.Metrics
            }

            Dim text = tweet.Text.ToLower()

            ' Player injury detection
            If Regex.IsMatch(text, "\b(injured?|hurt|out|doubtful|questionable)\b") Then
                intelligence.Type = BettingIntelligenceType.PlayerInjury
                intelligence.Players = ExtractPlayerNames(tweet.Text)
                intelligence.Teams = ExtractTeamNames(tweet.Text)
                intelligence.Impact = CalculateInjuryImpact(intelligence.Players, intelligence.Teams)
            End If

            ' Trade/roster move detection
            If Regex.IsMatch(text, "\b(trade[ds]?|acquired?|sign[eds]?|released?|waived?)\b") Then
                intelligence.Type = BettingIntelligenceType.Trade
                intelligence.Players = ExtractPlayerNames(tweet.Text)
                intelligence.Teams = ExtractTeamNames(tweet.Text)
                intelligence.Impact = CalculateTradeImpact(intelligence.Players, intelligence.Teams)
            End If

            ' Line movement detection
            If Regex.IsMatch(text, "\b(line|spread|total|odds?)\b.*\b(moved?|shift[eds]?|steam)\b") Then
                intelligence.Type = BettingIntelligenceType.LineMovement
                intelligence.OddsData = ExtractOddsData(tweet.Text)
                intelligence.Impact = CalculateLineMovementImpact(intelligence.OddsData)
            End If

            ' Weather impact detection
            If Regex.IsMatch(text, "\b(weather|rain|snow|wind|delay[eds]?|postponed?)\b") Then
                intelligence.Type = BettingIntelligenceType.Weather
                intelligence.WeatherData = ExtractWeatherData(tweet.Text)
                intelligence.Impact = CalculateWeatherImpact(intelligence.WeatherData)
            End If

            ' Only return if we detected actionable intelligence
            Return If(intelligence.Type <> BettingIntelligenceType.Unknown, intelligence, Nothing)

        Catch ex As Exception
            _logger.Error($"Intelligence extraction failed: {ex.Message}")
            Return Nothing
        End Try
    End Function

    ' ===============================================================================
    ' INTEGRATION WITH EQ12 SYSTEMS
    ' ===============================================================================

    Private Async Function PipeToContentEngine(tweet As BettingTweet, insight As BettingIntelligence) As Task
        Try
            ' Generate content based on betting intelligence
            Dim contentRequest As New ContentGenerationRequest With {
                .Type = "betting_intelligence",
                .SourceTweet = tweet,
                .Intelligence = insight,
                .GenerateAlert = insight.Impact >= BettingImpact.Medium,
                .GenerateAnalysis = insight.Impact >= BettingImpact.High
            }

            ' Call ContentEngine API (assuming it exists)
            Dim contentResponse = Await CallContentEngineAPI(contentRequest)

            If contentResponse.Success Then
                _logger.Info($"ContentEngine generated {contentResponse.ItemsGenerated} items from tweet {tweet.Id}")

                ' Log content generation success
                LogIntegrationEvent("ContentEngine", "content_generated", "success",
                    $"Generated {contentResponse.ItemsGenerated} items from {insight.Type}")
            End If

        Catch ex As Exception
            _logger.Error($"ContentEngine integration failed: {ex.Message}")
        End Try
    End Function

    Private Async Function PipeToLiveWatch(tweet As BettingTweet, insight As BettingIntelligence) As Task
        Try
            ' Send high-impact intelligence to LiveWatch for real-time alerts
            If insight.Impact >= BettingImpact.High Then
                Dim alertRequest As New LiveWatchAlert With {
                    .Type = insight.Type.ToString(),
                    .Priority = GetAlertPriority(insight.Impact),
                    .Message = GenerateAlertMessage(insight),
                    .SourceTweet = tweet.Id,
                    .Timestamp = DateTime.UtcNow,
                    .MonetizationTrigger = ShouldTriggerMonetization(insight)
                }

                ' Call LiveWatch API (assuming it exists)
                Dim alertResponse = Await CallLiveWatchAPI(alertRequest)

                If alertResponse.Success Then
                    _logger.Info($"LiveWatch alert sent for {insight.Type}: {insight.Players?.FirstOrDefault()}")

                    ' Log alert success
                    LogIntegrationEvent("LiveWatch", "alert_sent", "success",
                        $"Alert sent for {insight.Type} - {insight.Impact}")

                    ' Trigger monetization if conditions are met
                    If alertRequest.MonetizationTrigger Then
                        Await TriggerMonetization(insight)
                    End If
                End If
            End If

        Catch ex As Exception
            _logger.Error($"LiveWatch integration failed: {ex.Message}")
        End Try
    End Function

    Private Async Function CheckArbitrageOpportunities(insight As BettingIntelligence) As Task
        Try
            ' Check if intelligence creates arbitrage opportunities
            If insight.Type = BettingIntelligenceType.LineMovement AndAlso
               insight.Impact >= BettingImpact.Medium Then

                ' Call ArbitrageBotEngine to check for opportunities
                Dim arbRequest As New ArbitrageCheckRequest With {
                    .TriggerSource = "twitter_intelligence",
                    .Teams = insight.Teams,
                    .Players = insight.Players,
                    .OddsData = insight.OddsData,
                    .Urgency = GetUrgencyLevel(insight.Impact)
                }

                Dim arbOpportunities = Await CheckArbitrageAPI(arbRequest)

                If arbOpportunities?.Count > 0 Then
                    _logger.Info($"Found {arbOpportunities.Count} arbitrage opportunities from Twitter intelligence")

                    ' Auto-post arbitrage alerts to Twitter
                    For Each opportunity In arbOpportunities
                        Await PostArbitrageAlert(opportunity, insight)
                    Next

                    LogIntegrationEvent("ArbitrageBotEngine", "opportunities_found", "success",
                        $"Found {arbOpportunities.Count} opportunities from {insight.Type}")
                End If
            End If

        Catch ex As Exception
            _logger.Error($"Arbitrage opportunity check failed: {ex.Message}")
        End Try
    End Function

    ' ===============================================================================
    ' POSTING FUNCTIONALITY
    ' ===============================================================================

    ''' <summary>
    ''' Post betting intelligence alert to X/Twitter
    ''' </summary>
    Public Async Function PostBettingAlert(intelligence As BettingIntelligence, Optional includeAffiliateLink As Boolean = True) As Task(Of String)
        Try
            CheckRateLimit("post")

            Dim alertText = GenerateAlertText(intelligence)

            If includeAffiliateLink Then
                Dim affiliateLink = GenerateAffiliateLink(intelligence)
                alertText &= vbNewLine & $"🔗 {affiliateLink}"
            End If

            ' Add relevant hashtags
            alertText &= vbNewLine & GenerateHashtags(intelligence)

            Dim result = Await PostTweet(alertText)

            ' Log posting success
            LogIntegrationEvent("XClient", "alert_posted", "success",
                $"Posted {intelligence.Type} alert for {intelligence.Players?.FirstOrDefault()}")

            Return result

        Catch ex As Exception
            _logger.Error($"Betting alert posting failed: {ex.Message}")
            Return ""
        End Try
    End Function

    ''' <summary>
    ''' Post arbitrage opportunity alert
    ''' </summary>
    Public Async Function PostArbitrageAlert(opportunity As ArbitrageOpportunity, Optional sourceIntel As BettingIntelligence = Nothing) As Task(Of String)
        Try
            CheckRateLimit("post")

            Dim profit = opportunity.ExpectedProfit
            Dim alertText = $"🚨 ARBITRAGE ALERT 🚨{vbNewLine}" &
                           $"💰 {profit:P2} GUARANTEED PROFIT{vbNewLine}" &
                           $"⚡ {opportunity.EventDescription}{vbNewLine}"

            ' Add source intelligence context if available
            If sourceIntel IsNot Nothing Then
                alertText &= $"📊 Triggered by: {sourceIntel.Type}{vbNewLine}"
            End If

            ' Add stakes breakdown for premium users
            If Config("premium")("enabled") = "true" Then
                alertText &= $"💡 Stakes: {String.Join(", ", opportunity.OptimalStakes.Select(Function(s) $"{s.Key}: ${s.Value:F0}"))}{vbNewLine}"
            End If

            ' Add monetization link
            Dim bitlyLink = BitlyHelper.CreateAffiliateLink(opportunity.BookmakerUrls)
            alertText &= $"🔗 Book now: {bitlyLink}{vbNewLine}"
            alertText &= "#Arbitrage #BettingTips #EQ12 #GuaranteedProfit"

            Dim result = Await PostTweet(alertText)

            ' Track monetization conversion
            MonetizationTracker.RecordTwitterConversion("arbitrage_alert", bitlyLink, profit)

            LogIntegrationEvent("XClient", "arbitrage_posted", "success",
                $"Posted {profit:P2} arbitrage opportunity")

            Return result

        Catch ex As Exception
            _logger.Error($"Arbitrage alert posting failed: {ex.Message}")
            Return ""
        End Try
    End Function

    ''' <summary>
    ''' Core tweet posting function
    ''' </summary>
    Public Async Function PostTweet(text As String) As Task(Of String)
        Try
            CheckRateLimit("post")

            Dim payload As New JObject From {
                {"text", text}
            }

            Dim content = New StringContent(payload.ToString(), System.Text.Encoding.UTF8, "application/json")
            Dim response = Await HttpClient.PostAsync($"{_apiBaseUrl}/tweets", content)

            _monthlyTweetCount += 1

            If response.IsSuccessStatusCode Then
                Dim result = JObject.Parse(Await response.Content.ReadAsStringAsync())
                Dim tweetId = result("data")("id").ToString()

                ' Log successful tweet post
                DBWriter.LogXAction("post", tweetId, text, 1, "success", $"Tweet posted: https://x.com/i/web/status/{tweetId}")

                ' Create Bitly shortlink and send alerts
                Try
                    If HasBitlyConfig() Then
                        Dim tweetUrl = $"https://x.com/i/web/status/{tweetId}"
                        Dim shortUrl = BitlyHelper.Shorten(Config("bitly")("token"), tweetUrl)
                        If Not String.IsNullOrEmpty(shortUrl) Then
                            ' Update log with Bitly URL
                            DBWriter.LogXAction("post", tweetId, text, 1, "success", $"Bitly shortened: {shortUrl}")

                            ' Log monetization tracking
                            DBWriter.LogXMonetization("post", tweetId, 0.0, 0, 0.0, 0.05, shortUrl, "twitter") ' Estimated $0.05 API cost per post
                        End If
                    End If

                    ' Send Telegram alert if configured
                    If HasTelegramConfig() Then
                        Dim alertMsg = $"🐦 Tweet posted successfully!{vbNewLine}📊 Content: {TruncateText(text, 100)}{vbNewLine}🔗 ID: {tweetId}"
                        Alerts.Telegram(Config("telegram")("token"), Config("telegram")("chat_id"), alertMsg)
                    End If
                Catch alertEx As Exception
                    _logger.Warning($"Alert/Bitly processing failed: {alertEx.Message}")
                End Try

                _logger.Info($"Tweet posted successfully: {tweetId}")
                Return tweetId
            Else
                Dim error = Await response.Content.ReadAsStringAsync()

                ' Log failed tweet post
                DBWriter.LogXAction("post", "", text, 0, "fail", $"Error {response.StatusCode}: {error}")

                _logger.Error($"Tweet posting failed: {response.StatusCode} - {error}")
                Return ""
            End If

        Catch ex As Exception
            _logger.Error($"Tweet posting error: {ex.Message}")
            Return ""
        End Try
    End Function

    ' ===============================================================================
    ' LOGGING AND INTEGRATION TRACKING
    ' ===============================================================================

    Private Sub LogSearchResults(category As String, resultCount As Integer)
        Try
            Using conn As New SQLiteConnection("Data Source=C:\EQ12\Data\bankroll.db")
                conn.Open()
                Using cmd = conn.CreateCommand()
                    cmd.CommandText = "INSERT INTO integration_log (module, repo, action, status, details, category) VALUES (@m,@r,@a,@s,@d,@c)"
                    cmd.Parameters.AddWithValue("@m", "XClient")
                    cmd.Parameters.AddWithValue("@r", "twitter_search")
                    cmd.Parameters.AddWithValue("@a", "search")
                    cmd.Parameters.AddWithValue("@s", "success")
                    cmd.Parameters.AddWithValue("@d", $"Found {resultCount} tweets for {category}")
                    cmd.Parameters.AddWithValue("@c", category)
                    cmd.ExecuteNonQuery()
                End Using
            End Using
        Catch ex As Exception
            _logger.Error($"Logging search results failed: {ex.Message}")
        End Try
    End Sub

    Private Sub LogBettingIntelligence(tweet As BettingTweet, intelligence As BettingIntelligence)
        Try
            Using conn As New SQLiteConnection("Data Source=C:\EQ12\Data\bankroll.db")
                conn.Open()
                Using cmd = conn.CreateCommand()
                    cmd.CommandText = "INSERT INTO integration_log (module, repo, action, status, details, category, profit_potential) VALUES (@m,@r,@a,@s,@d,@c,@p)"
                    cmd.Parameters.AddWithValue("@m", "XClient")
                    cmd.Parameters.AddWithValue("@r", tweet.Id)
                    cmd.Parameters.AddWithValue("@a", "intelligence_extracted")
                    cmd.Parameters.AddWithValue("@s", "success")
                    cmd.Parameters.AddWithValue("@d", $"{intelligence.Type}: {String.Join(", ", intelligence.Players ?? New List(Of String)())}")
                    cmd.Parameters.AddWithValue("@c", intelligence.Type.ToString().ToLower())
                    cmd.Parameters.AddWithValue("@p", CalculateProfitPotential(intelligence))
                    cmd.ExecuteNonQuery()
                End Using
            End Using
        Catch ex As Exception
            _logger.Error($"Logging betting intelligence failed: {ex.Message}")
        End Try
    End Sub

    Private Sub LogIntegrationEvent(module As String, action As String, status As String, details As String)
        Try
            Using conn As New SQLiteConnection("Data Source=C:\EQ12\Data\bankroll.db")
                conn.Open()
                Using cmd = conn.CreateCommand()
                    cmd.CommandText = "INSERT INTO integration_log (module, repo, action, status, details, category) VALUES (@m,@r,@a,@s,@d,@c)"
                    cmd.Parameters.AddWithValue("@m", "XClient")
                    cmd.Parameters.AddWithValue("@r", module)
                    cmd.Parameters.AddWithValue("@a", action)
                    cmd.Parameters.AddWithValue("@s", status)
                    cmd.Parameters.AddWithValue("@d", details)
                    cmd.Parameters.AddWithValue("@c", "integration")
                    cmd.ExecuteNonQuery()
                End Using
            End Using
        Catch ex As Exception
            _logger.Error($"Logging integration event failed: {ex.Message}")
        End Try
    End Sub

    ' ===============================================================================
    ' RATE LIMITING AND QUOTA MANAGEMENT
    ' ===============================================================================

    Private Sub CheckRateLimit(operationType As String)
        Select Case operationType.ToLower()
            Case "post"
                If _monthlyTweetCount >= MaxTweetsPerMonth Then
                    Throw New InvalidOperationException("Monthly tweet quota exceeded. Upgrade to Pro tier for unlimited posting.")
                End If
            Case "search"
                If _monthlyReadCount >= MaxReadsPerMonth Then
                    Throw New InvalidOperationException("Monthly read quota exceeded. Upgrade to Pro tier for unlimited searches.")
                End If
        End Select

        ' Warn when approaching limits
        If _monthlyTweetCount > MaxTweetsPerMonth * 0.8 Then
            _logger.Warning($"Approaching tweet quota: {_monthlyTweetCount}/{MaxTweetsPerMonth}")
        End If

        If _monthlyReadCount > MaxReadsPerMonth * 0.8 Then
            _logger.Warning($"Approaching read quota: {_monthlyReadCount}/{MaxReadsPerMonth}")
        End If
    End Sub

    ' ===============================================================================
    ' HELPER FUNCTIONS
    ' ===============================================================================

    Private Function ParseTweetsResponse(data As JObject, query As String) As List(Of BettingTweet)
        Dim tweets As New List(Of BettingTweet)

        Try
            If data("data") Is Nothing Then Return tweets

            ' Parse users for author information
            Dim users As New Dictionary(Of String, JObject)
            If data("includes")("users") IsNot Nothing Then
                For Each user As JObject In data("includes")("users")
                    users(user("id").ToString()) = user
                Next
            End If

            For Each tweetData As JObject In data("data")
                Dim tweet As New BettingTweet With {
                    .Id = tweetData("id").ToString(),
                    .Text = tweetData("text").ToString(),
                    .CreatedAt = DateTime.Parse(tweetData("created_at").ToString()),
                    .AuthorId = tweetData("author_id").ToString(),
                    .SearchQuery = query
                }

                ' Add author information if available
                If users.ContainsKey(tweet.AuthorId) Then
                    Dim user = users(tweet.AuthorId)
                    tweet.Author = user("username").ToString()
                    tweet.AuthorVerified = user("verified")?.Value(Of Boolean) ?? False
                End If

                ' Add metrics if available
                If tweetData("public_metrics") IsNot Nothing Then
                    Dim metrics = tweetData("public_metrics")
                    tweet.Metrics = New TweetMetrics With {
                        .LikeCount = metrics("like_count")?.Value(Of Integer) ?? 0,
                        .RetweetCount = metrics("retweet_count")?.Value(Of Integer) ?? 0,
                        .ReplyCount = metrics("reply_count")?.Value(Of Integer) ?? 0,
                        .QuoteCount = metrics("quote_count")?.Value(Of Integer) ?? 0
                    }
                End If

                tweets.Add(tweet)
            Next

        Catch ex As Exception
            _logger.Error($"Parsing tweets response failed: {ex.Message}")
        End Try

        Return tweets
    End Function

    Private Function ExtractPlayerNames(text As String) As List(Of String)
        ' Enhanced player name extraction using regex patterns
        Dim players As New List(Of String)

        Try
            ' Common patterns for player mentions
            Dim patterns = {
                "\b[A-Z][a-z]+ [A-Z][a-z]+\b",  ' First Last format
                "@\w+",                          ' Twitter handles
                "#\w+"                           ' Hashtags that might be player names
            }

            For Each pattern In patterns
                Dim matches = Regex.Matches(text, pattern)
                For Each match As Match In matches
                    Dim name = match.Value.Replace("@", "").Replace("#", "")
                    If Not players.Contains(name) AndAlso IsValidPlayerName(name) Then
                        players.Add(name)
                    End If
                Next
            Next

        Catch ex As Exception
            _logger.Error($"Player name extraction failed: {ex.Message}")
        End Try

        Return players
    End Function

    Private Function ExtractTeamNames(text As String) As List(Of String)
        ' Extract team names using common abbreviations and full names
        Dim teams As New List(Of String)

        Try
            ' NFL team patterns
            Dim nflTeams = {"Patriots", "Bills", "Dolphins", "Jets", "Steelers", "Ravens", "Browns", "Bengals", "Titans", "Colts", "Texans", "Jaguars", "Chiefs", "Raiders", "Chargers", "Broncos", "Cowboys", "Giants", "Eagles", "Washington", "Packers", "Bears", "Lions", "Vikings", "Falcons", "Panthers", "Saints", "Buccaneers", "Cardinals", "Rams", "49ers", "Seahawks"}

            ' NBA team patterns
            Dim nbaTeams = {"Lakers", "Warriors", "Celtics", "Heat", "Knicks", "Bulls", "Nets", "Sixers", "Bucks", "Nuggets", "Suns", "Mavs", "Clippers", "Jazz", "Blazers", "Kings", "Spurs", "Rockets", "Thunder", "Grizzlies", "Pelicans", "Timberwolves", "Hawks", "Hornets", "Magic", "Wizards", "Pistons", "Pacers", "Cavaliers", "Raptors"}

            ' MLB team patterns
            Dim mlbTeams = {"Yankees", "Red Sox", "Blue Jays", "Orioles", "Rays", "White Sox", "Guardians", "Tigers", "Royals", "Twins", "Astros", "Angels", "Athletics", "Mariners", "Rangers", "Braves", "Marlins", "Mets", "Phillies", "Nationals", "Cubs", "Reds", "Brewers", "Pirates", "Cardinals", "Diamondbacks", "Rockies", "Dodgers", "Padres", "Giants"}

            Dim allTeams = nflTeams.Concat(nbaTeams).Concat(mlbTeams)

            For Each team In allTeams
                If text.Contains(team, StringComparison.OrdinalIgnoreCase) Then
                    teams.Add(team)
                End If
            Next

        Catch ex As Exception
            _logger.Error($"Team name extraction failed: {ex.Message}")
        End Try

        Return teams
    End Function

    Private Function IsValidPlayerName(name As String) As Boolean
        ' Simple validation for player names
        Return name.Length > 4 AndAlso
               name.Contains(" ") AndAlso
               Not name.ToLower().Contains("http") AndAlso
               Not {"the", "and", "for", "with", "from"}.Any(Function(w) name.ToLower().Contains(w))
    End Function

    Private Function CalculateProfitPotential(intelligence As BettingIntelligence) As Double
        ' Calculate potential profit impact based on intelligence type and impact level
        Select Case intelligence.Type
            Case BettingIntelligenceType.PlayerInjury
                Return If(intelligence.Impact = BettingImpact.High, 500.0, If(intelligence.Impact = BettingImpact.Medium, 200.0, 50.0))
            Case BettingIntelligenceType.Trade
                Return If(intelligence.Impact = BettingImpact.High, 300.0, If(intelligence.Impact = BettingImpact.Medium, 150.0, 30.0))
            Case BettingIntelligenceType.LineMovement
                Return If(intelligence.Impact = BettingImpact.High, 1000.0, If(intelligence.Impact = BettingImpact.Medium, 400.0, 100.0))
            Case BettingIntelligenceType.Weather
                Return If(intelligence.Impact = BettingImpact.High, 250.0, If(intelligence.Impact = BettingImpact.Medium, 100.0, 25.0))
            Case Else
                Return 0.0
        End Select
    End Function

    ' Placeholder functions for external API calls
    Private Async Function CallContentEngineAPI(request As ContentGenerationRequest) As Task(Of ContentGenerationResponse)
        ' Placeholder for ContentEngine integration
        Return New ContentGenerationResponse With {.Success = True, .ItemsGenerated = 1}
    End Function

    Private Async Function CallLiveWatchAPI(request As LiveWatchAlert) As Task(Of LiveWatchResponse)
        ' Placeholder for LiveWatch integration
        Return New LiveWatchResponse With {.Success = True}
    End Function

    Private Async Function CheckArbitrageAPI(request As ArbitrageCheckRequest) As Task(Of List(Of ArbitrageOpportunity))
        ' Placeholder for ArbitrageBotEngine integration
        Return New List(Of ArbitrageOpportunity)()
    End Function

    ' Additional helper functions for text generation, monetization, etc.
    Private Function GenerateAlertText(intelligence As BettingIntelligence) As String
        Select Case intelligence.Type
            Case BettingIntelligenceType.PlayerInjury
                Return $"🏥 INJURY ALERT: {String.Join(", ", intelligence.Players)} - {intelligence.Impact} impact on betting lines"
            Case BettingIntelligenceType.Trade
                Return $"🔄 TRADE ALERT: {String.Join(", ", intelligence.Players)} - Market adjustment expected"
            Case BettingIntelligenceType.LineMovement
                Return $"📊 LINE MOVEMENT: Significant odds shift detected - Check arbitrage opportunities"
            Case BettingIntelligenceType.Weather
                Return $"🌧️ WEATHER IMPACT: Game conditions may affect totals and spreads"
            Case Else
                Return "📈 BETTING INTELLIGENCE: Market-moving information detected"
        End Select
    End Function

    Private Function GenerateHashtags(intelligence As BettingIntelligence) As String
        Dim hashtags = {"#EQ12", "#BettingIntel"}

        Select Case intelligence.Type
            Case BettingIntelligenceType.PlayerInjury
                hashtags = hashtags.Concat({"#InjuryReport", "#SportsBetting"}).ToArray()
            Case BettingIntelligenceType.Trade
                hashtags = hashtags.Concat({"#TradeAlert", "#FantasySports"}).ToArray()
            Case BettingIntelligenceType.LineMovement
                hashtags = hashtags.Concat({"#LineMovement", "#Arbitrage"}).ToArray()
            Case BettingIntelligenceType.Weather
                hashtags = hashtags.Concat({"#WeatherBetting", "#Totals"}).ToArray()
        End Select

        Return String.Join(" ", hashtags)
    End Function

    Private Function GenerateAffiliateLink(intelligence As BettingIntelligence) As String
        ' Generate monetized affiliate link based on intelligence
        Dim baseUrl = "https://your-affiliate-link.com"
        Return BitlyHelper.Shorten(Config("bitly")("token"), $"{baseUrl}?intel={intelligence.Type}&ref=eq12twitter")
    End Function

    Private Async Function TriggerMonetization(intelligence As BettingIntelligence) As Task
        ' Trigger monetization based on intelligence value
        If intelligence.Impact >= BettingImpact.High Then
            MonetizationTrigger.CheckAndActivate("twitter_intelligence", intelligence.Type.ToString())
        End If
    End Function

    ' Helper functions for impact calculations
    Private Function CalculateInjuryImpact(players As List(Of String), teams As List(Of String)) As BettingImpact
        ' Simple impact calculation - could be enhanced with player stats lookup
        If players?.Count > 0 Then
            Return BettingImpact.Medium ' Default to medium for any player mention
        End If
        Return BettingImpact.Low
    End Function

    Private Function CalculateTradeImpact(players As List(Of String), teams As List(Of String)) As BettingImpact
        Return BettingImpact.Medium ' Trades generally have medium impact
    End Function

    Private Function CalculateLineMovementImpact(oddsData As String) As BettingImpact
        Return BettingImpact.High ' Line movements are high priority for arbitrage
    End Function

    Private Function CalculateWeatherImpact(weatherData As String) As BettingImpact
        Return BettingImpact.Medium ' Weather can significantly impact totals
    End Function

    Private Function ExtractOddsData(text As String) As String
        ' Extract odds information from tweet text
        Dim oddsPattern = "[-+]?\d+\.?\d*"
        Dim matches = Regex.Matches(text, oddsPattern)
        Return String.Join(", ", matches.Cast(Of Match).Select(Function(m) m.Value))
    End Function

    Private Function ExtractWeatherData(text As String) As String
        ' Extract weather information from tweet text
        Return text ' Placeholder - could be enhanced with weather-specific parsing
    End Function

    Private Function GetAlertPriority(impact As BettingImpact) As String
        Select Case impact
            Case BettingImpact.High
                Return "HIGH"
            Case BettingImpact.Medium
                Return "MEDIUM"
            Case Else
                Return "LOW"
        End Select
    End Function

    Private Function GenerateAlertMessage(intelligence As BettingIntelligence) As String
        Return $"{intelligence.Type}: {String.Join(", ", intelligence.Players ?? New List(Of String)())} - {intelligence.Impact} impact"
    End Function

    Private Function ShouldTriggerMonetization(intelligence As BettingIntelligence) As Boolean
        Return intelligence.Impact >= BettingImpact.Medium
    End Function

    Private Function GetUrgencyLevel(impact As BettingImpact) As String
        Select Case impact
            Case BettingImpact.High
                Return "URGENT"
            Case BettingImpact.Medium
                Return "NORMAL"
            Case Else
                Return "LOW"
        End Select
    End Function

    ' ===============================================================================
    ' THREAD POSTING AND HELPER METHODS
    ' ===============================================================================

    ''' <summary>
    ''' Post a thread of tweets (first tweet + replies chained together)
    ''' </summary>
    Public Async Function PostThread(lines As IEnumerable(Of String)) As Task(Of List(Of String))
        Dim ids As New List(Of String)()
        Dim previousId As String = Nothing

        Try
            For Each line In lines.Where(Function(s) Not String.IsNullOrWhiteSpace(s))
                ' Post tweet, replying to previous if not the first
                Dim tweetId = Await PostTweetInThread(line, previousId)

                If String.IsNullOrEmpty(tweetId) Then
                    ' Log thread failure
                    DBWriter.LogXAction("thread", ids.FirstOrDefault(), String.Join(" | ", lines.Take(2)) & "...", ids.Count, "fail", $"Thread posting failed at tweet {ids.Count + 1}")
                    Exit For
                End If

                ids.Add(tweetId)
                previousId = tweetId

                ' Brief pause between thread tweets
                Await Task.Delay(2000)
            Next

            If ids.Count > 0 Then
                ' Log successful thread
                DBWriter.LogXAction("thread", ids.FirstOrDefault(), String.Join(" | ", lines.Take(2)) & "...", ids.Count, "success", $"Thread posted with {ids.Count} tweets")

                ' Create Bitly shortlink for thread and send alert
                Try
                    If HasBitlyConfig() AndAlso ids.Count > 0 Then
                        Dim threadUrl = $"https://x.com/i/web/status/{ids.FirstOrDefault()}"
                        Dim shortUrl = BitlyHelper.Shorten(Config("bitly")("token"), threadUrl)
                        If Not String.IsNullOrEmpty(shortUrl) Then
                            DBWriter.LogXMonetization("thread", ids.FirstOrDefault(), 0.0, 0, 0.0, 0.05 * ids.Count, shortUrl, "twitter")
                        End If
                    End If

                    ' Send Telegram alert for thread
                    If HasTelegramConfig() Then
                        Dim alertMsg = $"🧵 Thread posted successfully!{vbNewLine}📊 {ids.Count} tweets in thread{vbNewLine}🔗 First tweet: {ids.FirstOrDefault()}"
                        Alerts.Telegram(Config("telegram")("token"), Config("telegram")("chat_id"), alertMsg)
                    End If
                Catch alertEx As Exception
                    _logger.Warning($"Thread alert processing failed: {alertEx.Message}")
                End Try
            End If

            Return ids

        Catch ex As Exception
            _logger.Error($"Thread posting error: {ex.Message}")
            DBWriter.LogXAction("thread", "", "Thread posting failed", 0, "fail", ex.Message)
            Return ids
        End Try
    End Function

    ''' <summary>
    ''' Post a single tweet in a thread (with reply_to if specified)
    ''' </summary>
    Private Async Function PostTweetInThread(text As String, Optional replyToTweetId As String = Nothing) As Task(Of String)
        Try
            CheckRateLimit("post")

            Dim payload As New JObject From {
                {"text", text}
            }

            ' Add reply reference if this is not the first tweet
            If Not String.IsNullOrEmpty(replyToTweetId) Then
                payload("reply") = New JObject From {
                    {"in_reply_to_tweet_id", replyToTweetId}
                }
            End If

            Dim content = New StringContent(payload.ToString(), System.Text.Encoding.UTF8, "application/json")
            Dim response = Await HttpClient.PostAsync($"{_apiBaseUrl}/tweets", content)

            _monthlyTweetCount += 1

            If response.IsSuccessStatusCode Then
                Dim result = JObject.Parse(Await response.Content.ReadAsStringAsync())
                Dim tweetId = result("data")("id").ToString()

                _logger.Info($"Thread tweet posted successfully: {tweetId}")
                Return tweetId
            Else
                Dim error = Await response.Content.ReadAsStringAsync()
                _logger.Error($"Thread tweet posting failed: {response.StatusCode} - {error}")
                Return ""
            End If

        Catch ex As Exception
            _logger.Error($"Thread tweet posting error: {ex.Message}")
            Return ""
        End Try
    End Function

    ' ===============================================================================
    ' CONFIGURATION HELPER METHODS
    ' ===============================================================================

    Private Function HasBitlyConfig() As Boolean
        Try
            Return Config("bitly") IsNot Nothing AndAlso Not String.IsNullOrEmpty(Config("bitly")("token")?.ToString())
        Catch
            Return False
        End Try
    End Function

    Private Function HasTelegramConfig() As Boolean
        Try
            Return Config("telegram") IsNot Nothing AndAlso
                   Not String.IsNullOrEmpty(Config("telegram")("token")?.ToString()) AndAlso
                   Not String.IsNullOrEmpty(Config("telegram")("chat_id")?.ToString())
        Catch
            Return False
        End Try
    End Function

    Private Function TruncateText(text As String, maxLength As Integer) As String
        If String.IsNullOrEmpty(text) Then Return text
        If text.Length <= maxLength Then Return text
        Return text.Substring(0, maxLength) & "..."
    End Function
End Class

' ===============================================================================
' SUPPORTING DATA CLASSES
' ===============================================================================

Public Class BettingTweet
    Public Property Id As String
    Public Property Text As String
    Public Property CreatedAt As DateTime
    Public Property AuthorId As String
    Public Property Author As String
    Public Property AuthorVerified As Boolean
    Public Property Metrics As TweetMetrics
    Public Property SearchQuery As String
End Class

Public Class TweetMetrics
    Public Property LikeCount As Integer
    Public Property RetweetCount As Integer
    Public Property ReplyCount As Integer
    Public Property QuoteCount As Integer
End Class

Public Class BettingIntelligence
    Public Property TweetId As String
    Public Property Timestamp As DateTime
    Public Property OriginalText As String
    Public Property Author As String
    Public Property Metrics As TweetMetrics
    Public Property Type As BettingIntelligenceType
    Public Property Players As List(Of String)
    Public Property Teams As List(Of String)
    Public Property OddsData As String
    Public Property WeatherData As String
    Public Property Impact As BettingImpact
End Class

Public Enum BettingIntelligenceType
    Unknown
    PlayerInjury
    Trade
    LineMovement
    Weather
    Suspension
    LineupChange
End Enum

Public Enum BettingImpact
    Low = 1
    Medium = 2
    High = 3
End Enum

Public Class ContentGenerationRequest
    Public Property Type As String
    Public Property SourceTweet As BettingTweet
    Public Property Intelligence As BettingIntelligence
    Public Property GenerateAlert As Boolean
    Public Property GenerateAnalysis As Boolean
End Class

Public Class ContentGenerationResponse
    Public Property Success As Boolean
    Public Property ItemsGenerated As Integer
    Public Property ErrorMessage As String
End Class

Public Class LiveWatchAlert
    Public Property Type As String
    Public Property Priority As String
    Public Property Message As String
    Public Property SourceTweet As String
    Public Property Timestamp As DateTime
    Public Property MonetizationTrigger As Boolean
End Class

Public Class LiveWatchResponse
    Public Property Success As Boolean
    Public Property AlertId As String
    Public Property ErrorMessage As String
End Class

Public Class ArbitrageCheckRequest
    Public Property TriggerSource As String
    Public Property Teams As List(Of String)
    Public Property Players As List(Of String)
    Public Property OddsData As String
    Public Property Urgency As String
End Class
