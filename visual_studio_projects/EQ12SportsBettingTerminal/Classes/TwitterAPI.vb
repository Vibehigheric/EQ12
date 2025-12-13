' EQ12 Sports Betting Terminal - Twitter/X API Integration
' Comprehensive Twitter/X integration for sentiment analysis, automated posting, and social trading features

Imports System.Net.Http
Imports System.Threading.Tasks
Imports System.Collections.Generic
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.Text
Imports System.IO
Imports System.Text.RegularExpressions

Public Class TwitterAPI

    Private apiManager As APIManager
    Private config As Dictionary(Of String, Object)
    Private logger As Action(Of String, String)

    ' Twitter API credentials
    Private bearerToken As String
    Private apiKey As String
    Private apiSecret As String
    Private accessToken As String
    Private accessTokenSecret As String

    ' Configuration
    Private Const MaxTweetLength As Integer = 280
    Private Const MaxThreadLength As Integer = 25
    Private lastAPICall As DateTime = DateTime.MinValue
    Private callCount As Integer = 0

    ' Sentiment tracking
    Private sentimentCache As New Dictionary(Of String, SentimentResult)
    Private trendingTopics As New List(Of String)
    Private lastTrendingUpdate As DateTime = DateTime.MinValue

    Public Event TweetPosted(tweetId As String, content As String, success As Boolean)
    Public Event SentimentAnalyzed(query As String, sentiment As String, confidence As Double)
    Public Event TrendingUpdated(topics As List(Of String))
    Public Event TwitterError(errorMessage As String, statusCode As Integer)

    Public Sub New(apiManager As APIManager)
        Me.apiManager = apiManager
        InitializeTwitterAPI()

        ' Set up logging
        logger = Sub(message As String, level As String)
                     Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] [{level}] TwitterAPI: {message}")
                 End Sub

        logger("Twitter API initialized", "INFO")
    End Sub

    Private Sub InitializeTwitterAPI()
        Try
            ' Load credentials from environment variables
            bearerToken = Environment.GetEnvironmentVariable("TWITTER_BEARER_TOKEN")
            apiKey = Environment.GetEnvironmentVariable("TWITTER_API_KEY")
            apiSecret = Environment.GetEnvironmentVariable("TWITTER_API_SECRET")
            accessToken = Environment.GetEnvironmentVariable("TWITTER_ACCESS_TOKEN")
            accessTokenSecret = Environment.GetEnvironmentVariable("TWITTER_ACCESS_TOKEN_SECRET")

            ' Load configuration from EQ12 system
            LoadConfiguration()

            ' Validate credentials
            If String.IsNullOrEmpty(bearerToken) Then
                logger("Twitter Bearer Token not configured", "WARNING")
            End If

        Catch ex As Exception
            logger($"Error initializing Twitter API: {ex.Message}", "ERROR")
            Throw
        End Try
    End Sub

    Private Sub LoadConfiguration()
        Try
            ' Try to load from EQ12 config files
            Dim configPaths = New String() {
                "C:\EQ12\configs\production_config.json",
                "C:\EQ12\configs\ai_enhanced_config.json",
                "C:\EQ12\configs\copilot_system_config.json"
            }

            config = New Dictionary(Of String, Object)

            For Each configPath In configPaths
                If File.Exists(configPath) Then
                    Try
                        Dim configText = File.ReadAllText(configPath)
                        Dim configJson = JsonConvert.DeserializeObject(Of JObject)(configText)

                        ' Extract Twitter-related configuration
                        If configJson("twitter") IsNot Nothing Then
                            Dim twitterConfig = configJson("twitter")

                            For Each prop In twitterConfig.Children(Of JProperty)()
                                config(prop.Name) = prop.Value.ToObject(Of Object)()
                            Next
                        End If

                    Catch ex As Exception
                        logger($"Error loading config from {configPath}: {ex.Message}", "WARNING")
                    End Try
                End If
            Next

            ' Set defaults if not configured
            If Not config.ContainsKey("auto_tweet") Then config("auto_tweet") = False
            If Not config.ContainsKey("sentiment_tracking") Then config("sentiment_tracking") = True
            If Not config.ContainsKey("trending_refresh_minutes") Then config("trending_refresh_minutes") = 15
            If Not config.ContainsKey("max_tweets_per_hour") Then config("max_tweets_per_hour") = 10

            logger($"Twitter configuration loaded with {config.Count} settings", "SUCCESS")

        Catch ex As Exception
            logger($"Error loading Twitter configuration: {ex.Message}", "ERROR")
            config = New Dictionary(Of String, Object)
        End Try
    End Sub

    Public Async Function PostTweet(content As String, Optional replyToId As String = Nothing, Optional mediaIds As List(Of String) = Nothing) As Task(Of TwitterResponse)
        Try
            ' Validate content
            If String.IsNullOrEmpty(content) Then
                Return New TwitterResponse With {
                    .Success = False,
                    .ErrorMessage = "Tweet content cannot be empty"
                }
            End If

            If content.Length > MaxTweetLength Then
                Return Await PostTweetThread(content, replyToId)
            End If

            ' Check rate limits
            If Not CanMakeRequest() Then
                Return New TwitterResponse With {
                    .Success = False,
                    .ErrorMessage = "Rate limit exceeded for Twitter posts"
                }
            End If

            ' Prepare tweet data
            Dim tweetData As New Dictionary(Of String, Object) From {
                {"text", content}
            }

            If Not String.IsNullOrEmpty(replyToId) Then
                tweetData("reply") = New Dictionary(Of String, String) From {
                    {"in_reply_to_tweet_id", replyToId}
                }
            End If

            If mediaIds IsNot Nothing AndAlso mediaIds.Count > 0 Then
                tweetData("media") = New Dictionary(Of String, List(Of String)) From {
                    {"media_ids", mediaIds}
                }
            End If

            ' Make API call
            Dim response = Await apiManager.CallTwitter("tweets", "POST", Nothing, tweetData)

            callCount += 1
            lastAPICall = DateTime.Now

            If response.Success Then
                Dim responseData = JsonConvert.DeserializeObject(Of JObject)(response.Content)
                Dim tweetId = responseData("data")("id").ToString()

                RaiseEvent TweetPosted(tweetId, content, True)
                logger($"Tweet posted successfully: {tweetId}", "SUCCESS")

                Return New TwitterResponse With {
                    .Success = True,
                    .TweetId = tweetId,
                    .Content = response.Content
                }
            Else
                RaiseEvent TweetPosted("", content, False)
                RaiseEvent TwitterError(response.ErrorMessage, response.StatusCode)
                logger($"Failed to post tweet: {response.ErrorMessage}", "ERROR")

                Return New TwitterResponse With {
                    .Success = False,
                    .ErrorMessage = response.ErrorMessage,
                    .StatusCode = response.StatusCode
                }
            End If

        Catch ex As Exception
            logger($"Error posting tweet: {ex.Message}", "ERROR")

            Return New TwitterResponse With {
                .Success = False,
                .ErrorMessage = ex.Message
            }
        End Try
    End Function

    Public Async Function PostTweetThread(content As String, Optional replyToId As String = Nothing) As Task(Of TwitterResponse)
        Try
            ' Split content into tweet-sized chunks
            Dim tweetChunks = SplitIntoTweets(content)

            If tweetChunks.Count > MaxThreadLength Then
                Return New TwitterResponse With {
                    .Success = False,
                    .ErrorMessage = $"Thread too long: {tweetChunks.Count} tweets (max {MaxThreadLength})"
                }
            End If

            Dim threadIds As New List(Of String)
            Dim currentReplyId = replyToId

            For i As Integer = 0 To tweetChunks.Count - 1
                Dim chunk = tweetChunks(i)

                ' Add thread numbering if multiple tweets
                If tweetChunks.Count > 1 Then
                    chunk = $"{i + 1}/{tweetChunks.Count} {chunk}"
                End If

                Dim response = Await PostTweet(chunk, currentReplyId)

                If response.Success Then
                    threadIds.Add(response.TweetId)
                    currentReplyId = response.TweetId

                    ' Small delay between thread posts
                    If i < tweetChunks.Count - 1 Then
                        Await Task.Delay(2000)
                    End If
                Else
                    Return response ' Return the failed response
                End If
            Next

            logger($"Posted Twitter thread with {threadIds.Count} tweets", "SUCCESS")

            Return New TwitterResponse With {
                .Success = True,
                .TweetId = threadIds.First(),
                .ThreadIds = threadIds
            }

        Catch ex As Exception
            logger($"Error posting Twitter thread: {ex.Message}", "ERROR")

            Return New TwitterResponse With {
                .Success = False,
                .ErrorMessage = ex.Message
            }
        End Try
    End Function

    Private Function SplitIntoTweets(content As String) As List(Of String)
        Try
            Dim tweets As New List(Of String)

            If content.Length <= MaxTweetLength Then
                tweets.Add(content)
                Return tweets
            End If

            ' Split by sentences first
            Dim sentences = content.Split({".", "!", "?"}, StringSplitOptions.RemoveEmptyEntries)
            Dim currentTweet = ""

            For Each sentence In sentences
                sentence = sentence.Trim()
                If String.IsNullOrEmpty(sentence) Then Continue For

                ' Add punctuation back
                If Not sentence.EndsWith(".") AndAlso Not sentence.EndsWith("!") AndAlso Not sentence.EndsWith("?") Then
                    sentence &= "."
                End If

                If (currentTweet & " " & sentence).Length <= MaxTweetLength - 10 Then ' Reserve space for numbering
                    currentTweet = If(String.IsNullOrEmpty(currentTweet), sentence, currentTweet & " " & sentence)
                Else
                    If Not String.IsNullOrEmpty(currentTweet) Then
                        tweets.Add(currentTweet.Trim())
                    End If
                    currentTweet = sentence
                End If
            Next

            If Not String.IsNullOrEmpty(currentTweet) Then
                tweets.Add(currentTweet.Trim())
            End If

            Return tweets

        Catch ex As Exception
            logger($"Error splitting content into tweets: {ex.Message}", "ERROR")
            Return New List(Of String) From {content.Substring(0, Math.Min(content.Length, MaxTweetLength))}
        End Try
    End Function

    Public Async Function GetSentiment(query As String, Optional sampleSize As Integer = 100) As Task(Of SentimentResult)
        Try
            ' Check cache first
            If sentimentCache.ContainsKey(query) Then
                Dim cached = sentimentCache(query)
                If DateTime.Now.Subtract(cached.Timestamp).TotalMinutes < 30 Then
                    Return cached
                End If
            End If

            ' Search for recent tweets
            Dim searchParams = New Dictionary(Of String, String) From {
                {"query", query},
                {"max_results", Math.Min(sampleSize, 100).ToString()},
                {"tweet.fields", "created_at,public_metrics,context_annotations"}
            }

            Dim response = Await apiManager.CallTwitter("tweets/search/recent", "GET", searchParams)

            If Not response.Success Then
                RaiseEvent TwitterError(response.ErrorMessage, response.StatusCode)
                Return New SentimentResult With {
                    .Query = query,
                    .Sentiment = "neutral",
                    .Confidence = 0,
                    .TweetCount = 0
                }
            End If

            ' Analyze sentiment
            Dim sentimentResult = AnalyzeTweetSentiment(response.Content, query)

            ' Cache result
            sentimentCache(query) = sentimentResult

            RaiseEvent SentimentAnalyzed(query, sentimentResult.Sentiment, sentimentResult.Confidence)
            logger($"Sentiment analysis completed for '{query}': {sentimentResult.Sentiment} ({sentimentResult.Confidence:P0})", "SUCCESS")

            Return sentimentResult

        Catch ex As Exception
            logger($"Error getting sentiment for '{query}': {ex.Message}", "ERROR")

            Return New SentimentResult With {
                .Query = query,
                .Sentiment = "neutral",
                .Confidence = 0,
                .TweetCount = 0,
                .ErrorMessage = ex.Message
            }
        End Try
    End Function

    Private Function AnalyzeTweetSentiment(tweetData As String, query As String) As SentimentResult
        Try
            Dim data = JsonConvert.DeserializeObject(Of JObject)(tweetData)
            Dim tweets = data("data")

            If tweets Is Nothing Then
                Return New SentimentResult With {
                    .Query = query,
                    .Sentiment = "neutral",
                    .Confidence = 0,
                    .TweetCount = 0
                }
            End If

            Dim positiveCues = New String() {"good", "great", "excellent", "amazing", "love", "best", "win", "profit", "bullish", "moon", "🚀", "💎", "👍", "❤️"}
            Dim negativeCues = New String() {"bad", "terrible", "awful", "hate", "worst", "lose", "loss", "bearish", "crash", "dump", "👎", "😢", "💩"}

            Dim positiveCount = 0
            Dim negativeCount = 0
            Dim neutralCount = 0
            Dim totalTweets = 0

            For Each tweet In tweets
                Dim text = tweet("text").ToString().ToLower()
                totalTweets += 1

                Dim positiveScore = positiveCues.Count(Function(cue) text.Contains(cue))
                Dim negativeScore = negativeCues.Count(Function(cue) text.Contains(cue))

                If positiveScore > negativeScore Then
                    positiveCount += 1
                ElseIf negativeScore > positiveScore Then
                    negativeCount += 1
                Else
                    neutralCount += 1
                End If
            Next

            ' Determine overall sentiment
            Dim sentiment As String
            Dim confidence As Double

            If positiveCount > negativeCount AndAlso positiveCount > neutralCount Then
                sentiment = "positive"
                confidence = CDbl(positiveCount) / totalTweets
            ElseIf negativeCount > positiveCount AndAlso negativeCount > neutralCount Then
                sentiment = "negative"
                confidence = CDbl(negativeCount) / totalTweets
            Else
                sentiment = "neutral"
                confidence = CDbl(neutralCount) / totalTweets
            End If

            Return New SentimentResult With {
                .Query = query,
                .Sentiment = sentiment,
                .Confidence = confidence,
                .TweetCount = totalTweets,
                .PositiveCount = positiveCount,
                .NegativeCount = negativeCount,
                .NeutralCount = neutralCount,
                .Timestamp = DateTime.Now
            }

        Catch ex As Exception
            logger($"Error analyzing tweet sentiment: {ex.Message}", "ERROR")

            Return New SentimentResult With {
                .Query = query,
                .Sentiment = "neutral",
                .Confidence = 0,
                .TweetCount = 0,
                .ErrorMessage = ex.Message
            }
        End Try
    End Function

    Public Async Function GetTrendingTopics(Optional woeid As Integer = 1) As Task(Of List(Of String))
        Try
            ' Check if we need to refresh trending topics
            If DateTime.Now.Subtract(lastTrendingUpdate).TotalMinutes < CInt(config.GetValueOrDefault("trending_refresh_minutes", 15)) Then
                Return trendingTopics
            End If

            ' Get trending topics from Twitter API v2
            Dim response = Await apiManager.CallTwitter($"trends/by/woeid/{woeid}")

            If Not response.Success Then
                RaiseEvent TwitterError(response.ErrorMessage, response.StatusCode)
                Return trendingTopics ' Return cached topics
            End If

            Dim data = JsonConvert.DeserializeObject(Of JArray)(response.Content)
            Dim newTopics As New List(Of String)

            If data IsNot Nothing AndAlso data.Count > 0 Then
                Dim trends = data(0)("trends")

                For Each trend In trends
                    Dim name = trend("name").ToString()
                    If Not name.StartsWith("#") Then ' Skip hashtags for now
                        newTopics.Add(name)
                    End If
                Next
            End If

            trendingTopics = newTopics
            lastTrendingUpdate = DateTime.Now

            RaiseEvent TrendingUpdated(trendingTopics)
            logger($"Updated trending topics: {trendingTopics.Count} topics found", "SUCCESS")

            Return trendingTopics

        Catch ex As Exception
            logger($"Error getting trending topics: {ex.Message}", "ERROR")
            Return trendingTopics
        End Try
    End Function

    Public Async Function PostArbitrageAlert(homeTeam As String, awayTeam As String, profit As Double, bookmakers As List(Of String)) As Task(Of Boolean)
        Try
            If Not CBool(config.GetValueOrDefault("auto_tweet", False)) Then
                logger("Auto-tweet disabled, skipping arbitrage alert", "INFO")
                Return True
            End If

            Dim content = $"🚨 ARBITRAGE OPPORTUNITY 🚨
{homeTeam} vs {awayTeam}
Profit: {profit:P2}
Books: {String.Join(", ", bookmakers)}
#SportsBetting #Arbitrage #EQ12"

            Dim response = Await PostTweet(content)

            If response.Success Then
                logger($"Posted arbitrage alert tweet: {response.TweetId}", "SUCCESS")
                Return True
            Else
                logger($"Failed to post arbitrage alert: {response.ErrorMessage}", "ERROR")
                Return False
            End If

        Catch ex As Exception
            logger($"Error posting arbitrage alert: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Public Async Function PostValueBetAlert(team As String, odds As String, edge As Double, confidence As Double) As Task(Of Boolean)
        Try
            If Not CBool(config.GetValueOrDefault("auto_tweet", False)) Then
                Return True
            End If

            Dim content = $"💎 VALUE BET DETECTED 💎
Team: {team}
Odds: {odds}
Edge: {edge:P1}
Confidence: {confidence:P0}
#ValueBetting #SportsBetting #EQ12"

            Dim response = Await PostTweet(content)

            If response.Success Then
                logger($"Posted value bet alert tweet: {response.TweetId}", "SUCCESS")
                Return True
            Else
                logger($"Failed to post value bet alert: {response.ErrorMessage}", "ERROR")
                Return False
            End If

        Catch ex As Exception
            logger($"Error posting value bet alert: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Private Function CanMakeRequest() As Boolean
        Try
            Dim maxPerHour = CInt(config.GetValueOrDefault("max_tweets_per_hour", 10))
            Dim hourAgo = DateTime.Now.AddHours(-1)

            ' Simple rate limiting - could be enhanced with proper tracking
            Return callCount < maxPerHour AndAlso DateTime.Now.Subtract(lastAPICall).TotalMinutes > 6

        Catch ex As Exception
            logger($"Error checking rate limit: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Public Function GetStatistics() As Dictionary(Of String, Object)
        Try
            Return New Dictionary(Of String, Object) From {
                {"call_count", callCount},
                {"last_api_call", lastAPICall},
                {"trending_topics_count", trendingTopics.Count},
                {"sentiment_cache_size", sentimentCache.Count},
                {"auto_tweet_enabled", CBool(config.GetValueOrDefault("auto_tweet", False))},
                {"bearer_token_configured", Not String.IsNullOrEmpty(bearerToken)},
                {"api_credentials_configured", Not String.IsNullOrEmpty(apiKey) AndAlso Not String.IsNullOrEmpty(apiSecret)}
            }

        Catch ex As Exception
            logger($"Error getting Twitter statistics: {ex.Message}", "ERROR")
            Return New Dictionary(Of String, Object)
        End Try
    End Function

    Public Sub ClearCache()
        Try
            sentimentCache.Clear()
            trendingTopics.Clear()
            lastTrendingUpdate = DateTime.MinValue
            callCount = 0

            logger("Twitter cache cleared", "INFO")

        Catch ex As Exception
            logger($"Error clearing Twitter cache: {ex.Message}", "ERROR")
        End Try
    End Sub

End Class

' Supporting classes
Public Class TwitterResponse
    Public Property Success As Boolean
    Public Property TweetId As String
    Public Property ThreadIds As List(Of String)
    Public Property Content As String
    Public Property ErrorMessage As String
    Public Property StatusCode As Integer
End Class

Public Class SentimentResult
    Public Property Query As String
    Public Property Sentiment As String
    Public Property Confidence As Double
    Public Property TweetCount As Integer
    Public Property PositiveCount As Integer
    Public Property NegativeCount As Integer
    Public Property NeutralCount As Integer
    Public Property Timestamp As DateTime
    Public Property ErrorMessage As String
End Class
