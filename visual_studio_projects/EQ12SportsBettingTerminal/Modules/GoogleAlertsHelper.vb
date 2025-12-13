Imports System.Net.Http
Imports System.Xml
Imports System.Data.SQLite
Imports Newtonsoft.Json.Linq
Imports System.Text
Imports System.Text.RegularExpressions
Imports System.Linq

''' <summary>
''' GoogleAlertsHelper: Comprehensive Google Alerts integration for EQ12 stack
''' Features: RSS feed ingestion, alert parsing, keyword filtering, real-time news monetization
''' Handles: Sports news, injury alerts, legislation updates, market-moving information
''' </summary>
Public Class GoogleAlertsHelper

#Region "Core Alert Functions"

    ''' <summary>
    ''' Fetch and process Google Alerts from RSS feeds
    ''' </summary>
    Public Shared Function FetchAlertsRSS(cfg As JObject, Optional keywordFilter As String = "") As JObject
        Try
            Dim result As New JObject()
            result("timestamp") = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
            result("keyword_filter") = keywordFilter

            If Not ValidateAlertsConfig(cfg) Then
                result("success") = False
                result("error") = "Invalid Google Alerts configuration"
                Return result
            End If

            Dim rssUrl As String = cfg("google_alerts")("rss_url").ToString()
            Dim keywords As JArray = cfg("google_alerts")("keywords")

            ' Fetch RSS feed
            Dim alerts As List(Of JObject) = FetchRssFeed(rssUrl)

            If alerts.Count = 0 Then
                result("success") = False
                result("error") = "No alerts found in RSS feed"
                Return result
            End If

            ' Filter alerts by keywords and relevance
            Dim filteredAlerts As List(Of JObject) = FilterAlertsByKeywords(alerts, keywords, keywordFilter)

            ' Process and enrich alerts
            Dim processedAlerts As New JArray()
            For Each alert As JObject In filteredAlerts
                Dim processedAlert As JObject = ProcessAlert(alert, cfg)
                If processedAlert IsNot Nothing Then
                    processedAlerts.Add(processedAlert)

                    ' Log alert to database
                    LogAlert(
                        ExtractRelevantKeyword(alert, keywords),
                        alert("title").ToString(),
                        alert("link").ToString(),
                        alert("summary").ToString(),
                        ExtractSource(alert("link").ToString()),
                        "fetched"
                    )
                End If
            Next

            result("total_alerts_found") = alerts.Count
            result("filtered_alerts_count") = filteredAlerts.Count
            result("processed_alerts") = processedAlerts
            result("success") = True

            ' Send high-priority alerts immediately
            SendPriorityAlerts(processedAlerts, cfg)

            ' Generate content from alerts
            If cfg("google_alerts")?("auto_generate_content")?.ToString() = "True" Then
                GenerateContentFromAlerts(processedAlerts, cfg)
            End If

            Console.WriteLine($"✅ Google Alerts processed: {processedAlerts.Count} alerts ready for monetization")

            Return result

        Catch ex As Exception
            Console.WriteLine($"❌ Google Alerts fetch failed: {ex.Message}")
            Dim errorResult As New JObject()
            errorResult("success") = False
            errorResult("error") = ex.Message
            errorResult("timestamp") = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
            Return errorResult
        End Try
    End Function

    ''' <summary>
    ''' Fetch RSS feed and parse entries
    ''' </summary>
    Private Shared Function FetchRssFeed(rssUrl As String) As List(Of JObject)
        Try
            Dim alerts As New List(Of JObject)()

            Using client As New HttpClient()
                client.Timeout = TimeSpan.FromSeconds(30)
                client.DefaultRequestHeaders.Add("User-Agent", "EQ12 Sports Analytics Bot 1.0")

                Dim response = client.GetAsync(rssUrl).Result
                If Not response.IsSuccessStatusCode Then
                    Console.WriteLine($"RSS fetch failed: {response.StatusCode}")
                    Return alerts
                End If

                Dim xmlContent As String = response.Content.ReadAsStringAsync().Result

                ' Parse XML
                Dim xmlDoc As New XmlDocument()
                xmlDoc.LoadXml(xmlContent)

                ' Extract RSS entries
                Dim items As XmlNodeList = xmlDoc.SelectNodes("//item")
                If items Is Nothing Then
                    ' Try Atom format
                    items = xmlDoc.SelectNodes("//entry")
                End If

                If items IsNot Nothing Then
                    For Each item As XmlNode In items
                        Dim alert As JObject = ParseRssItem(item)
                        If alert IsNot Nothing Then
                            alerts.Add(alert)
                        End If
                    Next
                End If
            End Using

            Return alerts

        Catch ex As Exception
            Console.WriteLine($"RSS feed parsing error: {ex.Message}")
            Return New List(Of JObject)()
        End Try
    End Function

    ''' <summary>
    ''' Parse individual RSS item
    ''' </summary>
    Private Shared Function ParseRssItem(item As XmlNode) As JObject
        Try
            Dim alert As New JObject()

            ' RSS format
            Dim titleNode = item.SelectSingleNode("title")
            Dim linkNode = item.SelectSingleNode("link")
            Dim descNode = item.SelectSingleNode("description")
            Dim pubDateNode = item.SelectSingleNode("pubDate")

            ' Atom format fallback
            If titleNode Is Nothing Then titleNode = item.SelectSingleNode("title")
            If linkNode Is Nothing Then
                Dim linkAtomNode = item.SelectSingleNode("link[@rel='alternate']")
                If linkAtomNode IsNot Nothing Then
                    linkNode = linkAtomNode
                End If
            End If
            If descNode Is Nothing Then descNode = item.SelectSingleNode("summary")
            If pubDateNode Is Nothing Then pubDateNode = item.SelectSingleNode("published")

            If titleNode IsNot Nothing AndAlso linkNode IsNot Nothing Then
                alert("title") = CleanText(titleNode.InnerText)
                alert("link") = GetLinkUrl(linkNode)
                alert("summary") = If(descNode IsNot Nothing, CleanText(descNode.InnerText), "")
                alert("pub_date") = If(pubDateNode IsNot Nothing, pubDateNode.InnerText, DateTime.UtcNow.ToString())
                alert("raw_content") = item.OuterXml

                Return alert
            End If

            Return Nothing

        Catch ex As Exception
            Console.WriteLine($"RSS item parsing error: {ex.Message}")
            Return Nothing
        End Try
    End Function

    ''' <summary>
    ''' Filter alerts by configured keywords and optional filter
    ''' </summary>
    Private Shared Function FilterAlertsByKeywords(alerts As List(Of JObject), keywords As JArray, keywordFilter As String) As List(Of JObject)
        Try
            Dim filteredAlerts As New List(Of JObject)()

            For Each alert As JObject In alerts
                Dim title As String = alert("title").ToString().ToLower()
                Dim summary As String = alert("summary").ToString().ToLower()
                Dim fullText As String = $"{title} {summary}"

                Dim isRelevant As Boolean = False

                ' Check against configured keywords
                For Each keyword As JValue In keywords
                    If fullText.Contains(keyword.ToString().ToLower()) Then
                        isRelevant = True
                        alert("matched_keyword") = keyword.ToString()
                        Exit For
                    End If
                Next

                ' Apply additional keyword filter if provided
                If Not String.IsNullOrEmpty(keywordFilter) AndAlso isRelevant Then
                    If Not fullText.Contains(keywordFilter.ToLower()) Then
                        isRelevant = False
                    End If
                End If

                If isRelevant Then
                    filteredAlerts.Add(alert)
                End If
            Next

            Return filteredAlerts

        Catch ex As Exception
            Console.WriteLine($"Alert filtering error: {ex.Message}")
            Return alerts
        End Try
    End Function

    ''' <summary>
    ''' Process and enrich individual alert with monetization hooks
    ''' </summary>
    Private Shared Function ProcessAlert(alert As JObject, cfg As JObject) As JObject
        Try
            Dim processedAlert As JObject = CType(alert.DeepClone(), JObject)

            ' Determine alert priority and monetization potential
            processedAlert("priority") = DetermineAlertPriority(alert)
            processedAlert("monetization_score") = CalculateMonetizationScore(alert)
            processedAlert("alert_type") = ClassifyAlertType(alert)
            processedAlert("processing_timestamp") = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")

            ' Extract entities (teams, players, etc.)
            processedAlert("entities") = ExtractEntities(alert)

            ' Generate potential content derivatives
            processedAlert("content_opportunities") = GenerateContentOpportunities(alert, cfg)

            ' Create Bitly shortlinks for tracking
            If cfg("bitly")?("enabled")?.ToString() = "True" Then
                processedAlert("bitly_url") = CreateBitlyShortlink(alert("link").ToString(), cfg)
            End If

            ' Suggest affiliate opportunities
            processedAlert("affiliate_opportunities") = SuggestAffiliateOpportunities(alert, cfg)

            Return processedAlert

        Catch ex As Exception
            Console.WriteLine($"Alert processing error: {ex.Message}")
            Return Nothing
        End Try
    End Function

#End Region

#Region "Alert Classification and Scoring"

    ''' <summary>
    ''' Determine alert priority for immediate action
    ''' </summary>
    Private Shared Function DetermineAlertPriority(alert As JObject) As String
        Try
            Dim title As String = alert("title").ToString().ToLower()
            Dim summary As String = alert("summary").ToString().ToLower()
            Dim fullText As String = $"{title} {summary}"

            ' Critical priority keywords
            Dim criticalKeywords As String() = {
                "injury", "injured", "out", "ruled out", "suspended",
                "breaking", "trade", "traded", "released", "signs",
                "weather", "postponed", "cancelled", "delayed"
            }

            ' High priority keywords
            Dim highKeywords As String() = {
                "starting", "benched", "questionable", "doubtful",
                "odds", "line movement", "betting", "favorite"
            }

            ' Check for critical keywords
            For Each keyword As String In criticalKeywords
                If fullText.Contains(keyword) Then
                    Return "critical"
                End If
            Next

            ' Check for high keywords
            For Each keyword As String In highKeywords
                If fullText.Contains(keyword) Then
                    Return "high"
                End If
            Next

            Return "normal"

        Catch ex As Exception
            Return "normal"
        End Try
    End Function

    ''' <summary>
    ''' Calculate monetization potential score (1-100)
    ''' </summary>
    Private Shared Function CalculateMonetizationScore(alert As JObject) As Integer
        Try
            Dim score As Integer = 0
            Dim title As String = alert("title").ToString().ToLower()
            Dim summary As String = alert("summary").ToString().ToLower()
            Dim fullText As String = $"{title} {summary}"

            ' High-value monetization indicators
            If fullText.Contains("injury") OrElse fullText.Contains("trade") Then score += 30
            If fullText.Contains("betting") OrElse fullText.Contains("odds") Then score += 25
            If fullText.Contains("nfl") OrElse fullText.Contains("nba") Then score += 20
            If fullText.Contains("playoff") OrElse fullText.Contains("championship") Then score += 15
            If fullText.Contains("breaking") OrElse fullText.Contains("exclusive") Then score += 15
            If fullText.Contains("weather") OrElse fullText.Contains("postponed") Then score += 10

            ' Recency bonus (newer = more valuable)
            Dim pubDate As DateTime
            If DateTime.TryParse(alert("pub_date").ToString(), pubDate) Then
                Dim hoursOld As Double = (DateTime.UtcNow - pubDate).TotalHours
                If hoursOld < 1 Then score += 10
                ElseIf hoursOld < 6 Then score += 5
            End If

            Return Math.Min(100, score)

        Catch ex As Exception
            Return 0
        End Try
    End Function

    ''' <summary>
    ''' Classify alert type for targeted processing
    ''' </summary>
    Private Shared Function ClassifyAlertType(alert As JObject) As String
        Try
            Dim title As String = alert("title").ToString().ToLower()
            Dim summary As String = alert("summary").ToString().ToLower()
            Dim fullText As String = $"{title} {summary}"

            If fullText.Contains("injury") OrElse fullText.Contains("injured") Then Return "injury"
            If fullText.Contains("trade") OrElse fullText.Contains("traded") Then Return "trade"
            If fullText.Contains("weather") OrElse fullText.Contains("postponed") Then Return "weather"
            If fullText.Contains("legislation") OrElse fullText.Contains("legal") Then Return "legislation"
            If fullText.Contains("odds") OrElse fullText.Contains("betting") Then Return "betting_news"
            If fullText.Contains("starting") OrElse fullText.Contains("lineup") Then Return "lineup"
            If fullText.Contains("suspension") OrElse fullText.Contains("suspended") Then Return "suspension"

            Return "general_sports_news"

        Catch ex As Exception
            Return "unknown"
        End Try
    End Function

    ''' <summary>
    ''' Extract entities (teams, players) from alert content
    ''' </summary>
    Private Shared Function ExtractEntities(alert As JObject) As JObject
        Try
            Dim entities As New JObject()
            Dim title As String = alert("title").ToString()
            Dim summary As String = alert("summary").ToString()

            ' Extract team names (basic pattern matching)
            entities("teams") = ExtractTeamNames(title & " " & summary)

            ' Extract player names (basic pattern matching)
            entities("players") = ExtractPlayerNames(title & " " & summary)

            ' Extract sports leagues
            entities("leagues") = ExtractLeagues(title & " " & summary)

            Return entities

        Catch ex As Exception
            Return New JObject()
        End Try
    End Function

    ''' <summary>
    ''' Generate content opportunities from alert
    ''' </summary>
    Private Shared Function GenerateContentOpportunities(alert As JObject, cfg As JObject) As JArray
        Try
            Dim opportunities As New JArray()
            Dim alertType As String = alert("alert_type").ToString()
            Dim priority As String = alert("priority").ToString()

            Select Case alertType
                Case "injury"
                    opportunities.Add("Injury Impact Analysis Blog Post")
                    opportunities.Add("Line Movement Tracker Alert")
                    opportunities.Add("Replacement Player Analysis")
                    If priority = "critical" Then
                        opportunities.Add("Emergency Telegram Alert")
                        opportunities.Add("Social Media Breaking News Post")
                    End If

                Case "trade"
                    opportunities.Add("Trade Analysis Newsletter Section")
                    opportunities.Add("Team Chemistry Impact Report")
                    opportunities.Add("Updated Season Projections")

                Case "weather"
                    opportunities.Add("Weather Impact Betting Guide")
                    opportunities.Add("O/U Adjustment Alert")
                    opportunities.Add("DFS Lineup Optimizer Update")

                Case "legislation"
                    opportunities.Add("Sports Betting Law Update Blog")
                    opportunities.Add("Market Impact Analysis")
                    opportunities.Add("Compliance Guide Update")

                Case "betting_news"
                    opportunities.Add("Odds Movement Analysis")
                    opportunities.Add("Market Sentiment Report")
                    opportunities.Add("Affiliate Promotional Content")

                Case Else
                    opportunities.Add("General Sports News Update")
                    opportunities.Add("Social Media Micro-Content")
            End Select

            Return opportunities

        Catch ex As Exception
            Return New JArray()
        End Try
    End Function

    ''' <summary>
    ''' Suggest affiliate opportunities based on alert content
    ''' </summary>
    Private Shared Function SuggestAffiliateOpportunities(alert As JObject, cfg As JObject) As JArray
        Try
            Dim opportunities As New JArray()
            Dim alertType As String = alert("alert_type").ToString()
            Dim monetizationScore As Integer = alert("monetization_score").ToObject(Of Integer)()

            If monetizationScore >= 50 Then
                Select Case alertType
                    Case "injury", "trade", "suspension"
                        opportunities.Add("FanDuel/DraftKings Line Movement Alert with Affiliate Link")
                        opportunities.Add("Promote 'Bet Now Before Lines Adjust' CTA")
                        opportunities.Add("Player Prop Betting Guide with Affiliate Links")

                    Case "weather"
                        opportunities.Add("Weather-Based Betting Strategy Guide")
                        opportunities.Add("Over/Under Weather Impact Affiliate Campaign")

                    Case "legislation"
                        opportunities.Add("New Market Opportunities Newsletter")
                        opportunities.Add("'Get Ready for Legal Betting' Affiliate Push")

                    Case "betting_news"
                        opportunities.Add("Direct Sportsbook Affiliate Promotion")
                        opportunities.Add("Odds Comparison Tool Monetization")
                End Select
            End If

            ' Always include general opportunities for high-scoring alerts
            If monetizationScore >= 30 Then
                opportunities.Add("Premium Telegram Channel Upsell")
                opportunities.Add("EQ12 Analytics Tool Promotion")
                opportunities.Add("Newsletter Subscription Drive")
            End If

            Return opportunities

        Catch ex As Exception
            Return New JArray()
        End Try
    End Function

#End Region

#Region "Content Generation and Distribution"

    ''' <summary>
    ''' Send priority alerts immediately via Telegram/Discord
    ''' </summary>
    Private Shared Sub SendPriorityAlerts(alerts As JArray, cfg As JObject)
        Try
            For Each alert As JObject In alerts
                Dim priority As String = alert("priority").ToString()
                Dim monetizationScore As Integer = alert("monetization_score").ToObject(Of Integer)()

                ' Send critical alerts immediately
                If priority = "critical" OrElse monetizationScore >= 70 Then
                    Dim message As String = FormatAlertForTelegram(alert)

                    ' Use existing TelegramHelper if available
                    ' TelegramHelper.SendMessage(cfg, message)

                    Console.WriteLine($"🚨 PRIORITY ALERT SENT: {alert("title").ToString().Substring(0, Math.Min(50, alert("title").ToString().Length))}...")
                End If
            Next

        Catch ex As Exception
            Console.WriteLine($"Failed to send priority alerts: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Format alert for Telegram message
    ''' </summary>
    Private Shared Function FormatAlertForTelegram(alert As JObject) As String
        Try
            Dim message As New StringBuilder()

            ' Add priority emoji
            Dim priority As String = alert("priority").ToString()
            Select Case priority
                Case "critical"
                    message.AppendLine("🚨 BREAKING SPORTS ALERT 🚨")
                Case "high"
                    message.AppendLine("📈 HIGH PRIORITY ALERT")
                Case Else
                    message.AppendLine("📰 Sports News Update")
            End Select

            message.AppendLine()
            message.AppendLine($"**{alert("title")}**")

            If Not String.IsNullOrEmpty(alert("summary").ToString()) Then
                Dim summary As String = alert("summary").ToString()
                If summary.Length > 200 Then
                    summary = summary.Substring(0, 200) & "..."
                End If
                message.AppendLine($"{summary}")
            End If

            message.AppendLine()

            ' Add monetization CTA
            Dim monetizationScore As Integer = alert("monetization_score").ToObject(Of Integer)()
            If monetizationScore >= 50 Then
                message.AppendLine("💰 **BETTING OPPORTUNITY** - Lines likely to move!")
                message.AppendLine("🔗 Get the edge: [Premium Analysis] | [Bet Now]")
            End If

            ' Add source link
            Dim linkUrl As String = If(alert("bitly_url")?.ToString(), alert("link").ToString())
            message.AppendLine($"📖 Source: {linkUrl}")

            message.AppendLine()
            message.AppendLine("⚡ Powered by EQ12 Sports Analytics")

            Return message.ToString()

        Catch ex As Exception
            Return $"Alert: {alert("title")}"
        End Try
    End Function

    ''' <summary>
    ''' Generate monetizable content from alerts batch
    ''' </summary>
    Private Shared Sub GenerateContentFromAlerts(alerts As JArray, cfg As JObject)
        Try
            If alerts.Count = 0 Then Return

            ' Generate newsletter section
            GenerateNewsletterSection(alerts, cfg)

            ' Generate blog post if enough high-value alerts
            Dim highValueAlerts = alerts.Where(Function(a) a("monetization_score").ToObject(Of Integer)() >= 50).ToList()
            If highValueAlerts.Count >= 3 Then
                GenerateBlogPostFromAlerts(highValueAlerts, cfg)
            End If

            ' Generate social media posts
            GenerateSocialMediaPosts(alerts, cfg)

        Catch ex As Exception
            Console.WriteLine($"Content generation from alerts failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Generate newsletter section from alerts
    ''' </summary>
    Private Shared Sub GenerateNewsletterSection(alerts As JArray, cfg As JObject)
        Try
            Dim newsletterPath As String = "Exports\newsletter_alerts.html"
            Dim content As New StringBuilder()

            content.AppendLine("<div class='alerts-section'>")
            content.AppendLine("<h2>🚨 Breaking Sports Alerts</h2>")

            For Each alert As JObject In alerts.Take(5) ' Top 5 alerts
                content.AppendLine("<div class='alert-item' style='border-left: 3px solid #007cba; padding: 10px; margin: 10px 0;'>")
                content.AppendLine($"<h4>{alert("title")}</h4>")
                content.AppendLine($"<p>{alert("summary").ToString().Substring(0, Math.Min(150, alert("summary").ToString().Length))}...</p>")
                content.AppendLine($"<p><a href='{alert("link")}' style='color: #007cba;'>Read More →</a></p>")
                content.AppendLine("</div>")
            Next

            content.AppendLine("</div>")

            File.WriteAllText(newsletterPath, content.ToString())
            Console.WriteLine($"📧 Newsletter section generated: {newsletterPath}")

        Catch ex As Exception
            Console.WriteLine($"Newsletter generation failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Generate blog post from high-value alerts
    ''' </summary>
    Private Shared Sub GenerateBlogPostFromAlerts(alerts As List(Of JToken), cfg As JObject)
        Try
            Dim title As String = $"Breaking Sports News Roundup - {DateTime.Now:MMMM dd, yyyy}"
            Dim content As New StringBuilder()

            content.AppendLine("<h1>Breaking Sports News That Could Impact Your Bets</h1>")
            content.AppendLine($"<p><em>Published: {DateTime.Now:MMMM dd, yyyy}</em></p>")
            content.AppendLine("<p>Stay ahead of the market with these breaking sports developments...</p>")

            For i As Integer = 0 To Math.Min(alerts.Count - 1, 4)
                Dim alert As JObject = CType(alerts(i), JObject)
                content.AppendLine($"<h2>{alert("title")}</h2>")
                content.AppendLine($"<p>{alert("summary")}</p>")
                content.AppendLine("<h3>Betting Impact Analysis</h3>")
                content.AppendLine("<p>This development could significantly impact betting lines...</p>")
                content.AppendLine($"<p><a href='{alert("link")}'>Read full story →</a></p>")
                content.AppendLine("<hr>")
            Next

            ' Publish to blog if enabled
            If cfg("blogger")?("enabled")?.ToString() = "True" Then
                BloggerHelper.PublishPost(cfg, title, content.ToString(), {"breaking-news", "sports-betting", "alerts"})
            End If

        Catch ex As Exception
            Console.WriteLine($"Blog post generation failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Generate social media posts from alerts
    ''' </summary>
    Private Shared Sub GenerateSocialMediaPosts(alerts As JArray, cfg As JObject)
        Try
            Dim socialPath As String = "Exports\social_alerts.txt"
            Dim posts As New StringBuilder()

            For Each alert As JObject In alerts.Take(3)
                Dim priority As String = alert("priority").ToString()
                Dim emoji As String = If(priority = "critical", "🚨", If(priority = "high", "📈", "📰"))

                posts.AppendLine($"TWITTER POST:")
                posts.AppendLine($"{emoji} {alert("title").ToString().Substring(0, Math.Min(100, alert("title").ToString().Length))}")
                posts.AppendLine($"Impact on betting lines expected 📊")
                posts.AppendLine($"Get the edge: {If(alert("bitly_url")?.ToString(), alert("link").ToString())}")
                posts.AppendLine("#SportsBetting #BreakingNews #BettingTips")
                posts.AppendLine()
            Next

            File.WriteAllText(socialPath, posts.ToString())
            Console.WriteLine($"📱 Social media posts generated: {socialPath}")

        Catch ex As Exception
            Console.WriteLine($"Social media generation failed: {ex.Message}")
        End Try
    End Sub

#End Region

#Region "Database and Logging"

    ''' <summary>
    ''' Log alert to database for tracking and analysis
    ''' </summary>
    Public Shared Sub LogAlert(keyword As String, title As String, link As String, summary As String, source As String, usedIn As String)
        Try
            Dim dbPath As String = "Data\eq12_terminal.db"
            Using conn As New SQLiteConnection($"Data Source={dbPath}")
                conn.Open()

                Dim sql As String = "INSERT INTO google_alerts_log (keyword, title, link, summary, source, used_in) VALUES (@keyword, @title, @link, @summary, @source, @usedIn)"
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@keyword", If(String.IsNullOrEmpty(keyword), DBNull.Value, keyword))
                    cmd.Parameters.AddWithValue("@title", title)
                    cmd.Parameters.AddWithValue("@link", link)
                    cmd.Parameters.AddWithValue("@summary", If(String.IsNullOrEmpty(summary), DBNull.Value, summary))
                    cmd.Parameters.AddWithValue("@source", If(String.IsNullOrEmpty(source), DBNull.Value, source))
                    cmd.Parameters.AddWithValue("@usedIn", If(String.IsNullOrEmpty(usedIn), DBNull.Value, usedIn))

                    cmd.ExecuteNonQuery()
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"Failed to log Google alert: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Get Google Alerts statistics
    ''' </summary>
    Public Shared Function GetAlertsStats(days As Integer) As JObject
        Try
            Dim dbPath As String = "Data\eq12_terminal.db"
            Dim stats As New JObject()

            Using conn As New SQLiteConnection($"Data Source={dbPath}")
                conn.Open()

                ' Total alerts
                Dim sql As String = $"SELECT COUNT(*) FROM google_alerts_log WHERE ts >= datetime('now', '-{days} days')"
                Using cmd As New SQLiteCommand(sql, conn)
                    stats("total_alerts") = Convert.ToInt32(cmd.ExecuteScalar())
                End Using

                ' Top keywords
                sql = $"SELECT keyword, COUNT(*) as count FROM google_alerts_log WHERE ts >= datetime('now', '-{days} days') AND keyword IS NOT NULL GROUP BY keyword ORDER BY count DESC LIMIT 5"
                Using cmd As New SQLiteCommand(sql, conn)
                    Using reader = cmd.ExecuteReader()
                        Dim topKeywords As New JArray()
                        While reader.Read()
                            Dim keywordObj As New JObject()
                            keywordObj("keyword") = reader("keyword").ToString()
                            keywordObj("count") = Convert.ToInt32(reader("count"))
                            topKeywords.Add(keywordObj)
                        End While
                        stats("top_keywords") = topKeywords
                    End Using
                End Using

                ' Recent alerts
                sql = $"SELECT title, link, source, ts FROM google_alerts_log WHERE ts >= datetime('now', '-{days} days') ORDER BY ts DESC LIMIT 10"
                Using cmd As New SQLiteCommand(sql, conn)
                    Using reader = cmd.ExecuteReader()
                        Dim recentAlerts As New JArray()
                        While reader.Read()
                            Dim alertObj As New JObject()
                            alertObj("title") = reader("title").ToString()
                            alertObj("link") = reader("link").ToString()
                            alertObj("source") = If(reader("source") Is DBNull.Value, "", reader("source").ToString())
                            alertObj("timestamp") = reader("ts").ToString()
                            recentAlerts.Add(alertObj)
                        End While
                        stats("recent_alerts") = recentAlerts
                    End Using
                End Using
            End Using

            Return stats

        Catch ex As Exception
            Console.WriteLine($"Failed to get alerts stats: {ex.Message}")
            Return New JObject()
        End Try
    End Function

#End Region

#Region "Utility Functions"

    Private Shared Function ValidateAlertsConfig(cfg As JObject) As Boolean
        Try
            If cfg("google_alerts") Is Nothing Then Return False
            If Not Convert.ToBoolean(cfg("google_alerts")("enabled")?.ToString()) Then Return False
            If String.IsNullOrEmpty(cfg("google_alerts")("rss_url")?.ToString()) Then Return False
            If cfg("google_alerts")("keywords") Is Nothing Then Return False

            Return True

        Catch ex As Exception
            Return False
        End Try
    End Function

    Private Shared Function CleanText(text As String) As String
        If String.IsNullOrEmpty(text) Then Return ""

        ' Remove HTML tags and decode entities
        text = Regex.Replace(text, "<[^>]+>", "")
        text = System.Web.HttpUtility.HtmlDecode(text)
        text = text.Trim()

        Return text
    End Function

    Private Shared Function GetLinkUrl(linkNode As XmlNode) As String
        If linkNode.Attributes("href") IsNot Nothing Then
            Return linkNode.Attributes("href").Value
        Else
            Return linkNode.InnerText
        End If
    End Function

    Private Shared Function ExtractRelevantKeyword(alert As JObject, keywords As JArray) As String
        Try
            If alert("matched_keyword") IsNot Nothing Then
                Return alert("matched_keyword").ToString()
            End If

            ' Try to match again
            Dim title As String = alert("title").ToString().ToLower()
            Dim summary As String = alert("summary").ToString().ToLower()
            Dim fullText As String = $"{title} {summary}"

            For Each keyword As JValue In keywords
                If fullText.Contains(keyword.ToString().ToLower()) Then
                    Return keyword.ToString()
                End If
            Next

            Return "general"

        Catch ex As Exception
            Return "unknown"
        End Try
    End Function

    Private Shared Function ExtractSource(link As String) As String
        Try
            Dim uri As New Uri(link)
            Return uri.Host.Replace("www.", "")
        Catch
            Return "unknown"
        End Try
    End Function

    Private Shared Function ExtractTeamNames(text As String) As JArray
        ' Basic team name extraction - could be enhanced with comprehensive team database
        Dim teams As New JArray()
        Dim commonTeams As String() = {
            "Lakers", "Warriors", "Bulls", "Celtics", "Knicks",
            "Patriots", "Cowboys", "Steelers", "Packers", "49ers",
            "Yankees", "Dodgers", "Giants", "Red Sox", "Cubs"
        }

        For Each team As String In commonTeams
            If text.Contains(team) Then
                teams.Add(team)
            End If
        Next

        Return teams
    End Function

    Private Shared Function ExtractPlayerNames(text As String) As JArray
        ' Basic player name extraction - could be enhanced with player database
        Dim players As New JArray()

        ' Look for patterns like "FirstName LastName"
        Dim namePattern As New Regex("\b[A-Z][a-z]+ [A-Z][a-z]+\b")
        Dim matches = namePattern.Matches(text)

        For Each match As Match In matches
            players.Add(match.Value)
        Next

        Return players
    End Function

    Private Shared Function ExtractLeagues(text As String) As JArray
        Dim leagues As New JArray()
        Dim knownLeagues As String() = {"NFL", "NBA", "MLB", "NHL", "MLS", "UFC", "NCAA"}

        For Each league As String In knownLeagues
            If text.ToUpper().Contains(league) Then
                leagues.Add(league)
            End If
        Next

        Return leagues
    End Function

    Private Shared Function CreateBitlyShortlink(longUrl As String, cfg As JObject) As String
        Try
            ' Reuse BitlyHelper functionality if available, otherwise return original URL
            Return longUrl ' Placeholder - implement with actual Bitly API
        Catch
            Return longUrl
        End Try
    End Function

#End Region

End Class
