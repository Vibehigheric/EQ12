Imports System.Text
Imports System.Net.Http
Imports Newtonsoft.Json.Linq
Imports System.Data.SQLite
Imports System.IO
Imports System.Linq

''' <summary>
''' Content Engine Module - Automated Monetization Content Generation
''' Transforms EQ12 sports betting data into revenue-generating content assets
''' Features: OpenAI integration, GitHub Gists, Bitly URLs, multi-channel distribution
''' </summary>
Public Class ContentEngine
    ''' <summary>
    ''' Build all enabled deliverables for monetization
    ''' </summary>
    ''' <param name="cfg">Configuration object</param>
    ''' <param name="period">Report period (daily/weekly/monthly)</param>
    ''' <param name="summaryText">Source data summary from reports</param>
    ''' <returns>List of generated deliverable types and their Bitly URLs</returns>
    Public Shared Function BuildAll(cfg As JObject, period As String, summaryText As String) As List(Of (kind As String, bit As String))
        Dim results As New List(Of (String, String))()

        Try
            Console.WriteLine("🔄 Content Engine: Starting deliverable generation...")

            ' Check if content engine is enabled
            If Not cfg("content_engine")?("enabled")?.ToObject(Of Boolean)() Then
                Console.WriteLine("⚠️ Content Engine disabled in configuration")
                Return results
            End If

            ' Get enabled deliverable types
            Dim kinds = cfg("content_engine")("deliverables").Select(Function(t) t.ToString()).ToList()
            Console.WriteLine($"📝 Generating {kinds.Count} deliverable types: {String.Join(", ", kinds)}")

            For Each kind In kinds
                Try
                    Console.WriteLine($"🎯 Creating {kind} deliverable...")

                    ' Generate content using configured LLM provider
                    Dim payload = RenderWithLLM(cfg, kind, period, summaryText)
                    Dim title = payload.Item1
                    Dim body = payload.Item2

                    ' Create safe filename slug
                    Dim slug = SafeSlug($"{period}_{kind}_{DateTime.UtcNow:yyyyMMdd_HHmm}")

                    ' Determine file extension based on content type
                    Dim fileExt = If(kind = "thread", "md", If(kind = "landing_page", "html", "txt"))

                    ' Publish as GitHub Gist
                    Dim gist = GitHubSync.CreateGist(slug, fileExt, body)
                    Console.WriteLine($"✅ Created Gist: {gist}")

                    ' Shorten with Bitly
                    Dim bit As String = gist
                    If cfg("bitly")?("token") IsNot Nothing Then
                        Dim domain = If(cfg("bitly")?("domain")?.ToString(), "bit.ly")
                        bit = BitlyHelper.Shorten(cfg("bitly")("token").ToString(), gist, domain)
                        Console.WriteLine($"🔗 Shortened to: {bit}")
                    End If

                    ' Multi-channel distribution
                    DistributeContent(cfg, kind, period, title, bit)

                    ' Persist to database
                    SaveDeliverable(kind, title, body, gist, bit, period, $"tone={cfg("content_engine")("tone")}")

                    ' Log Bitly link for analytics
                    DBWriter.LogBitly("deliverable", gist, bit)

                    results.Add((kind, bit))
                    Console.WriteLine($"✅ {Cap(kind)} deliverable completed: {bit}")

                Catch ex As Exception
                    Console.WriteLine($"❌ Failed to create {kind} deliverable: {ex.Message}")
                End Try
            Next

            ' Integrate with new monetization systems
            IntegrateMonetizationSystems(cfg, period, summaryText, results)

            Console.WriteLine($"🎉 Content Engine completed! Generated {results.Count} deliverables")

        Catch ex As Exception
            Console.WriteLine($"❌ Content Engine failed: {ex.Message}")
        End Try

        Return results
    End Function

    ''' <summary>
    ''' Generate content using configured LLM provider (OpenAI or DeepSeek)
    ''' </summary>
    Private Shared Function RenderWithLLM(cfg As JObject, kind As String, period As String, summaryText As String) As (String, String)
        Try
            Dim key = cfg("openai")("key").ToString()
            Dim model = If(cfg("openai")("model")?.ToString(), "gpt-4o-mini")
            Dim tone = cfg("content_engine")("tone").ToString()
            Dim cta = cfg("content_engine")("cta").ToString()
            Dim disclaimer = cfg("content_engine")("affiliate_disclaimer").ToString()

            ' Build comprehensive prompt for monetization-focused content
            Dim system = "You are a senior marketing copywriter and quantitative finance expert. Generate monetization-ready content that maximizes conversions, revenue, and subscriber growth. Focus on credibility, urgency, and clear value propositions."

            Dim userPrompt As New StringBuilder()
            userPrompt.AppendLine($"📊 PERIOD: {period.ToUpper()}")
            userPrompt.AppendLine($"🎯 TONE: {tone}")
            userPrompt.AppendLine("💰 GOAL: Maximize monetization, revenue generation, conversions, and subscriber LTV via compelling, credible content")
            userPrompt.AppendLine()
            userPrompt.AppendLine("📈 EQ12 SPORTS BETTING DATA:")
            userPrompt.AppendLine(summaryText)
            userPrompt.AppendLine()
            userPrompt.AppendLine($"📝 DELIVERABLE TYPE: {kind.ToUpper()}")
            userPrompt.AppendLine("⚡ STRICT OUTPUT REQUIREMENTS:")

            Select Case kind.ToLower()
                Case "newsletter"
                    userPrompt.AppendLine("- Start with compelling subject line")
                    userPrompt.AppendLine("- 4-6 short sections with clear headers")
                    userPrompt.AppendLine("- Include specific profit numbers and ROI percentages")
                    userPrompt.AppendLine("- Add 2-3 bullet-point CTAs throughout")
                    userPrompt.AppendLine("- End with urgency-driven disclaimer")
                    userPrompt.AppendLine("- Format: plain text, email-ready")

                Case "thread"
                    userPrompt.AppendLine("- Create 8-12 numbered tweets for Twitter/X thread")
                    userPrompt.AppendLine("- Each tweet <= 260 characters")
                    userPrompt.AppendLine("- Include specific profit metrics and percentages")
                    userPrompt.AppendLine("- Add relevant hashtags (#SportsBetting #Arbitrage #Profit)")
                    userPrompt.AppendLine("- End with strong CTA in final tweet")
                    userPrompt.AppendLine("- Format: numbered list, social media ready")

                Case "landing_page"
                    userPrompt.AppendLine("- Generate complete HTML5 landing page")
                    userPrompt.AppendLine("- Hero: Compelling headline + subhead + primary CTA button")
                    userPrompt.AppendLine("- Proof: Stats section with profit metrics")
                    userPrompt.AppendLine("- Benefits: 3-5 key value propositions")
                    userPrompt.AppendLine("- Pricing: Tiered options with urgency")
                    userPrompt.AppendLine("- FAQ: Address common objections")
                    userPrompt.AppendLine("- Footer: Legal disclaimer")

                Case "promo_email"
                    userPrompt.AppendLine("- Subject: High-open-rate subject line")
                    userPrompt.AppendLine("- Preview: Compelling preview text")
                    userPrompt.AppendLine("- Body: Short paragraphs, single primary CTA")
                    userPrompt.AppendLine("- Include specific profit examples")
                    userPrompt.AppendLine("- P.S.: Urgency-driven postscript")
                    userPrompt.AppendLine("- Format: email-ready with clear structure")
            End Select

            userPrompt.AppendLine()
            userPrompt.AppendLine($"🎯 PRIMARY CTA: {cta}")
            userPrompt.AppendLine($"⚖️ DISCLAIMER: {disclaimer}")
            userPrompt.AppendLine()
            userPrompt.AppendLine("Generate content that converts browsers into subscribers and subscribers into revenue.")

            ' Use LLM Router for intelligent provider selection
            Dim taskType = $"content_{kind}"
            Dim provider = LLMRouter.DecideProvider(cfg, taskType, userPrompt.ToString())
            Console.WriteLine($"🤖 LLM Router selected {provider.ToUpper()} for {kind} generation")

            ' Generate content using selected provider
            Dim generatedContent = LLMRouter.CallLLM(cfg, provider, userPrompt.ToString(), taskType)

            ' Extract title and return result
            Dim lines = generatedContent.Split({vbCrLf, vbLf}, StringSplitOptions.RemoveEmptyEntries)
            Dim title = If(lines.Any(),
                          lines(0).Trim().Replace("Subject:", "").Replace("#", "").Trim(),
                          $"EQ12 {Cap(kind)} {DateTime.UtcNow:yyyyMMdd}")

            Console.WriteLine($"✅ {provider.ToUpper()} generated {generatedContent.Length} characters for {kind}")
            Return (title, generatedContent)

        Catch ex As Exception
            Console.WriteLine($"❌ LLM content generation failed: {ex.Message}")

            ' Fallback content if all LLMs fail
            Dim fallbackTitle = $"EQ12 {Cap(kind)} - {Cap(period)} Report"
            Dim fallbackContent = $"# {fallbackTitle}" & vbCrLf & vbCrLf &
                                 $"Generated from EQ12 Sports Betting Terminal" & vbCrLf & vbCrLf &
                                 summaryText & vbCrLf & vbCrLf &
                                 cfg("content_engine")("cta").ToString()

            Return (fallbackTitle, fallbackContent)
        End Try
    End Function

    ''' <summary>
    ''' Determine which LLM provider to use based on configuration
    ''' </summary>
    Private Shared Function GetLLMProvider(cfg As JObject) As String
        Try
            ' Check for content engine specific provider setting
            If cfg("content_engine")?.ContainsKey("llm_provider") = True Then
                Dim provider = cfg("content_engine")("llm_provider").ToString().ToLower()
                If provider = "deepseek" OrElse provider = "openai" Then
                    Return provider
                End If
            End If

            ' Check for global LLM default provider
            If cfg("llm")?.ContainsKey("default_provider") = True Then
                Return cfg("llm")("default_provider").ToString().ToLower()
            End If

            ' Default to OpenAI
            Return "openai"
        Catch
            Return "openai"
        End Try
    End Function

    ''' <summary>
    ''' Call OpenAI API for content generation (extracted method)
    ''' </summary>
    Private Shared Function CallOpenAI(cfg As JObject, userPrompt As String, systemPrompt As String) As String
        Try
            Dim key = cfg("openai")("key").ToString()
            Dim model = If(cfg("openai")("model")?.ToString(), "gpt-4o-mini")

            ' Make OpenAI API call
            Dim requestBody = New JObject From {
                {"model", model},
                {"messages", New JArray From {
                    New JObject From {{"role", "system"}, {"content", systemPrompt}},
                    New JObject From {{"role", "user"}, {"content", userPrompt}}
                }},
                {"max_tokens", If(cfg("openai")("max_tokens"), 2000)},
                {"temperature", If(cfg("openai")("temperature"), 0.7)}
            }

            Using client As New HttpClient()
                client.DefaultRequestHeaders.Add("Authorization", "Bearer " & key)
                client.Timeout = TimeSpan.FromSeconds(If(cfg("openai")("timeout_seconds"), 60))

                Dim content = New StringContent(requestBody.ToString(), Encoding.UTF8, "application/json")
                Dim response = client.PostAsync("https://api.openai.com/v1/chat/completions", content).Result

                If response.IsSuccessStatusCode Then
                    Dim responseJson = response.Content.ReadAsStringAsync().Result
                    Dim json = JObject.Parse(responseJson)
                    Return json("choices")(0)("message")("content").ToString()
                Else
                    Throw New Exception($"OpenAI API error: {response.StatusCode} - {response.ReasonPhrase}")
                End If
            End Using

        Catch ex As Exception
            Throw New Exception($"OpenAI API call failed: {ex.Message}")
        End Try
    End Function

    ''' <summary>
    ''' Distribute content across multiple channels
    ''' </summary>
    Private Shared Sub DistributeContent(cfg As JObject, kind As String, period As String, title As String, bitlyUrl As String)
        Try
            ' Email distribution
            Dim emailSubject = $"🚀 EQ12 {Cap(kind)} ({Cap(period)}) Ready"
            Dim emailBody = $"Your {period} {kind} is ready for review and distribution." & vbCrLf & vbCrLf &
                           $"📱 Quick Access: {bitlyUrl}" & vbCrLf & vbCrLf &
                           $"This content is optimized for monetization and conversion." & vbCrLf & vbCrLf &
                           "Forward this link to your audience or use in your marketing campaigns."

            Mailer.SendEmail(cfg, emailSubject, emailBody, New List(Of String))
            Console.WriteLine("✅ Content distributed via email")

            ' Telegram alert
            If cfg("telegram")?("token") IsNot Nothing AndAlso cfg("telegram")?("chat_id") IsNot Nothing Then
                Dim telegramMsg = $"📣 *{Cap(kind)}* ready ({Cap(period)})!" & vbCrLf &
                                 $"🎯 _{title}_" & vbCrLf & vbCrLf &
                                 $"🔗 {bitlyUrl}" & vbCrLf & vbCrLf &
                                 $"💰 Optimized for conversions and revenue"

                Alerts.Telegram(cfg("telegram")("token").ToString(),
                               cfg("telegram")("chat_id").ToString(),
                               telegramMsg)
                Console.WriteLine("✅ Content distributed via Telegram")
            End If

            ' Discord notification
            If cfg("discord")?("webhook") IsNot Nothing Then
                Dim discordMsg = $"📣 **{Cap(kind)}** ready ({Cap(period)})!" & vbCrLf &
                               $"🎯 {title}" & vbCrLf & vbCrLf &
                               $"🔗 {bitlyUrl}" & vbCrLf &
                               $"💰 Ready for monetization"

                Alerts.Discord(cfg("discord")("webhook").ToString(), discordMsg)
                Console.WriteLine("✅ Content distributed via Discord")
            End If

        Catch ex As Exception
            Console.WriteLine($"⚠️ Content distribution failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Save deliverable to database for tracking and analytics
    ''' </summary>
    Private Shared Sub SaveDeliverable(kind As String, title As String, content As String, gist As String, bit As String, period As String, notes As String)
        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()
                Using cmd As New SQLiteCommand("
                    INSERT INTO deliverables (kind, title, content, gist_url, bitly_url, source_window, notes)
                    VALUES (@k, @t, @c, @g, @b, @w, @n)", conn)
                    cmd.Parameters.AddWithValue("@k", kind)
                    cmd.Parameters.AddWithValue("@t", title)
                    cmd.Parameters.AddWithValue("@c", content)
                    cmd.Parameters.AddWithValue("@g", gist)
                    cmd.Parameters.AddWithValue("@b", bit)
                    cmd.Parameters.AddWithValue("@w", period)
                    cmd.Parameters.AddWithValue("@n", notes)
                    cmd.ExecuteNonQuery()
                End Using
            End Using
            Console.WriteLine($"✅ Deliverable saved to database: {kind}")
        Catch ex As Exception
            Console.WriteLine($"❌ Failed to save deliverable: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Get latest deliverables for API/reporting
    ''' </summary>
    Public Shared Function GetLatestDeliverables(Optional limit As Integer = 50) As JArray
        Dim arr As New JArray()
        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()
                Using cmd As New SQLiteCommand($"
                    SELECT ts, kind, title, bitly_url, gist_url, source_window
                    FROM deliverables ORDER BY ts DESC LIMIT {limit}", conn)
                    Using rdr = cmd.ExecuteReader()
                        While rdr.Read()
                            arr.Add(New JObject From {
                                {"ts", rdr("ts").ToString()},
                                {"kind", rdr("kind").ToString()},
                                {"title", rdr("title").ToString()},
                                {"bitly_url", rdr("bitly_url").ToString()},
                                {"gist_url", rdr("gist_url").ToString()},
                                {"window", rdr("source_window").ToString()}
                            })
                        End While
                    End Using
                End Using
            End Using
        Catch ex As Exception
            Console.WriteLine($"❌ Failed to get deliverables: {ex.Message}")
        End Try
        Return arr
    End Function

    ''' <summary>
    ''' Utility: Capitalize first letter
    ''' </summary>
    Private Shared Function Cap(s As String) As String
        If String.IsNullOrWhiteSpace(s) Then Return s
        Return Char.ToUpper(s(0)) & s.Substring(1)
    End Function

    ''' <summary>
    ''' Utility: Create safe filename slug
    ''' </summary>
    Private Shared Function SafeSlug(s As String) As String
        Dim allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        Dim result = New String(s.Select(Function(ch) If(allowed.Contains(ch), ch, "-"c)).ToArray())
        Return result.Trim("-"c)
    End Function

    ''' <summary>
    ''' Integrate with new monetization systems: Blogger, Scheduled Exports, Alerts
    ''' </summary>
    Private Shared Sub IntegrateMonetizationSystems(cfg As JObject, period As String, summaryText As String, results As List(Of (kind As String, bit As String)))
        Try
            Console.WriteLine("🚀 Integrating with monetization systems...")

            ' 1. Auto-publish to Google Blogger if enabled
            If cfg("blogger")?("enabled")?.ToString() = "True" Then
                Try
                    Console.WriteLine("📝 Publishing to Google Blogger...")
                    Dim blogContent = BloggerHelper.ConvertReportToBlog(summaryText, period, cfg)
                    Dim postId = BloggerHelper.PublishPost(cfg, blogContent.Item1, blogContent.Item2, {period, "eq12", "sports-betting"})

                    If Not postId.StartsWith("ERROR") Then
                        Console.WriteLine($"✅ Blog post published: {postId}")
                    Else
                        Console.WriteLine($"⚠️ Blog publish failed: {postId}")
                    End If
                Catch ex As Exception
                    Console.WriteLine($"❌ Blog integration failed: {ex.Message}")
                End Try
            End If

            ' 2. Fetch and integrate Google Alerts
            If cfg("google_alerts")?("enabled")?.ToString() = "True" Then
                Try
                    Console.WriteLine("📰 Fetching Google Alerts for content enrichment...")
                    Dim alertsResult = GoogleAlertsHelper.FetchAlertsRSS(cfg, "")

                    If alertsResult("success")?.ToString() = "True" Then
                        Dim alertCount = alertsResult("processed_alerts")?.Count Or 0
                        Console.WriteLine($"✅ Processed {alertCount} alerts for monetization")

                        ' High-priority alerts can trigger immediate content generation
                        If alertCount > 0 Then
                            EnrichContentWithAlerts(cfg, alertsResult("processed_alerts"), results)
                        End If
                    End If
                Catch ex As Exception
                    Console.WriteLine($"❌ Google Alerts integration failed: {ex.Message}")
                End Try
            End If

            ' 3. Trigger scheduled export if configured
            If cfg("scheduled_exports")?("enabled")?.ToString() = "True" Then
                Try
                    Console.WriteLine("📊 Checking scheduled export triggers...")

                    ' Determine if we should trigger export based on period
                    Dim shouldExport As Boolean = False
                    Select Case period.ToLower()
                        Case "daily"
                            shouldExport = cfg("scheduled_exports")("daily")?("auto_distribute")?.ToString() = "True"
                        Case "weekly"
                            shouldExport = cfg("scheduled_exports")("weekly")?("auto_distribute")?.ToString() = "True"
                    End Select

                    If shouldExport Then
                        Console.WriteLine($"📈 Triggering {period} scheduled export...")
                        Dim exportResult = If(period = "daily",
                                            ScheduledExportsHelper.ExecuteDailyExport(cfg, False),
                                            ScheduledExportsHelper.ExecuteWeeklyExport(cfg, False))

                        If exportResult("success")?.ToString() = "True" Then
                            Console.WriteLine($"✅ Scheduled export completed: {exportResult("deliverables")?.Count} deliverables")
                        End If
                    End If
                Catch ex As Exception
                    Console.WriteLine($"❌ Scheduled export integration failed: {ex.Message}")
                End Try
            End If

            ' 4. Log management and insights extraction
            If cfg("log_manager")?("enabled")?.ToString() = "True" AndAlso cfg("log_manager")?("monetization_insights")?.ToString() = "True" Then
                Try
                    Console.WriteLine("🔍 Extracting monetization insights from logs...")
                    Dim logAnalysis = LogManagerHelper.AnalyzeLogs(cfg, 1) ' Last 24 hours

                    If logAnalysis("success")?.ToString() = "True" Then
                        Dim insights = logAnalysis("monetization_insights")
                        If insights IsNot Nothing Then
                            Dim clicks = insights("affiliate_clicks")?.ToObject(Of Integer)() Or 0
                            Dim conversions = insights("conversion_rate")?.ToObject(Of Double)() Or 0
                            Console.WriteLine($"💰 Monetization insights: {clicks} affiliate clicks, {conversions:F1}% conversion")
                        End If
                    End If
                Catch ex As Exception
                    Console.WriteLine($"❌ Log insights extraction failed: {ex.Message}")
                End Try
            End If

            Console.WriteLine("🎯 Monetization systems integration completed")

        Catch ex As Exception
            Console.WriteLine($"❌ Monetization systems integration failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Enrich existing content with high-priority alerts
    ''' </summary>
    Private Shared Sub EnrichContentWithAlerts(cfg As JObject, alerts As JToken, results As List(Of (kind As String, bit As String)))
        Try
            Dim highPriorityAlerts = alerts.Where(Function(a) a("priority").ToString() = "critical" OrElse a("monetization_score").ToObject(Of Integer)() >= 70).Take(3)

            If highPriorityAlerts.Any() Then
                Console.WriteLine($"🚨 Enriching content with {highPriorityAlerts.Count()} high-priority alerts")

                ' Create alert-based micro-content
                For Each alert As JObject In highPriorityAlerts
                    Dim alertTitle = alert("title").ToString()
                    Dim alertType = alert("alert_type").ToString()

                    ' Generate social media post for alert
                    Dim socialPost = $"🚨 BREAKING: {alertTitle} - Impact on betting lines expected! Get the edge: [Premium Analysis]"

                    ' Save as additional deliverable
                    Dim slug = SafeSlug($"alert_{alertType}_{DateTime.UtcNow:HHmm}")
                    SaveDeliverable("social_alert", alertTitle, socialPost, "", "", "breaking", $"alert_type={alertType}")

                    Console.WriteLine($"📱 Created alert-based social content: {alertType}")
                Next
            End If

        Catch ex As Exception
            Console.WriteLine($"❌ Alert enrichment failed: {ex.Message}")
        End Try
    End Sub

End Class
