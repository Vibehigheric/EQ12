Imports System.Net.Http
Imports System.Text
Imports Newtonsoft.Json.Linq
Imports Newtonsoft.Json

''' <summary>
''' DeepSeek Helper - Alternative LLM API Integration
''' Provides Chat.DeepSeek API integration as OpenAI alternative for content generation
''' Features: Chat completions, error handling, token tracking, response logging
''' </summary>
Public Class DeepSeekHelper
    Private Shared ReadOnly client As New HttpClient()

    ''' <summary>
    ''' Call DeepSeek Chat API with specified prompt and configuration
    ''' </summary>
    ''' <param name="config">Configuration object containing DeepSeek settings</param>
    ''' <param name="prompt">User prompt for content generation</param>
    ''' <param name="systemPrompt">Optional system prompt for context (default: assistant role)</param>
    ''' <param name="maxTokens">Maximum tokens in response (default: 1000)</param>
    ''' <param name="temperature">Response creativity (default: 0.3)</param>
    ''' <returns>Generated content text or error message</returns>
    Public Shared Function CallDeepSeek(config As JObject, prompt As String,
                                      Optional systemPrompt As String = "You are a helpful assistant.",
                                      Optional maxTokens As Integer = 1000,
                                      Optional temperature As Double = 0.3) As String
        Try
            ' Validate configuration
            If Not ValidateConfig(config) Then
                Return "Error: DeepSeek configuration missing or invalid"
            End If

            Dim deepSeekConfig = config("deepseek")
            Dim apiKey = deepSeekConfig("api_key").ToString()
            Dim endpoint = deepSeekConfig("endpoint").ToString()
            Dim model = deepSeekConfig("model").ToString()

            ' Prepare request payload
            Dim requestPayload As New JObject(
                New JProperty("model", model),
                New JProperty("max_tokens", maxTokens),
                New JProperty("temperature", temperature),
                New JProperty("messages", New JArray(
                    New JObject(
                        New JProperty("role", "system"),
                        New JProperty("content", systemPrompt)
                    ),
                    New JObject(
                        New JProperty("role", "user"),
                        New JProperty("content", prompt)
                    )
                ))
            )

            ' Configure HTTP client
            client.Timeout = TimeSpan.FromSeconds(60)
            If Not client.DefaultRequestHeaders.Contains("Authorization") Then
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {apiKey}")
            End If

            ' Send request
            Dim jsonContent = requestPayload.ToString(Formatting.None)
            Dim httpContent As New StringContent(jsonContent, Encoding.UTF8, "application/json")

            Dim response = client.PostAsync(endpoint, httpContent).Result
            Dim responseContent = response.Content.ReadAsStringAsync().Result

            ' Handle response
            If response.IsSuccessStatusCode Then
                Dim responseJson = JObject.Parse(responseContent)

                ' Extract generated content
                Dim generatedText = responseJson("choices")(0)("message")("content").ToString()

                ' Log successful API call
                LogDeepSeekCall(prompt, generatedText, "success")

                Return generatedText.Trim()
            Else
                Dim errorMsg = $"DeepSeek API Error {response.StatusCode}: {responseContent}"
                LogDeepSeekCall(prompt, errorMsg, "error")
                Return $"Error: {errorMsg}"
            End If

        Catch ex As Exception
            Dim errorMsg = $"DeepSeek API Exception: {ex.Message}"
            LogDeepSeekCall(prompt, errorMsg, "exception")
            Return errorMsg
        End Try
    End Function

    ''' <summary>
    ''' Generate newsletter content using DeepSeek
    ''' </summary>
    Public Shared Function GenerateNewsletter(config As JObject, dataPrompt As String, tone As String) As String
        Dim systemPrompt = $"You are an expert newsletter writer specializing in sports betting and quantitative analysis. " &
                          $"Write in a {tone} tone. Create engaging, informative content that drives subscriber engagement."

        Dim userPrompt = $"Create a newsletter section based on this data: {dataPrompt}. " &
                        "Include key insights, actionable takeaways, and maintain professional credibility."

        Return CallDeepSeek(config, userPrompt, systemPrompt, 1500, 0.4)
    End Function

    ''' <summary>
    ''' Generate Twitter thread using DeepSeek
    ''' </summary>
    Public Shared Function GenerateTwitterThread(config As JObject, dataPrompt As String, tone As String) As String
        Dim systemPrompt = $"You are an expert social media strategist specializing in Twitter threads about sports betting. " &
                          $"Write in a {tone} tone. Create viral, shareable content that educates and engages."

        Dim userPrompt = $"Create a Twitter thread (numbered tweets) based on this data: {dataPrompt}. " &
                        "Each tweet should be under 280 characters. Include hooks, insights, and call-to-actions."

        Return CallDeepSeek(config, userPrompt, systemPrompt, 2000, 0.5)
    End Function

    ''' <summary>
    ''' Generate landing page content using DeepSeek
    ''' </summary>
    Public Shared Function GenerateLandingPage(config As JObject, dataPrompt As String, tone As String) As String
        Dim systemPrompt = $"You are an expert copywriter specializing in high-converting landing pages for sports betting services. " &
                          $"Write in a {tone} tone. Focus on conversion optimization and clear value propositions."

        Dim userPrompt = $"Create landing page copy based on this data: {dataPrompt}. " &
                        "Include compelling headlines, benefit statements, social proof, and strong CTAs."

        Return CallDeepSeek(config, userPrompt, systemPrompt, 2500, 0.3)
    End Function

    ''' <summary>
    ''' Generate promotional email using DeepSeek
    ''' </summary>
    Public Shared Function GeneratePromoEmail(config As JObject, dataPrompt As String, tone As String) As String
        Dim systemPrompt = $"You are an expert email marketer specializing in sports betting promotions. " &
                          $"Write in a {tone} tone. Create compelling emails that drive opens, clicks, and conversions."

        Dim userPrompt = $"Create a promotional email based on this data: {dataPrompt}. " &
                        "Include attention-grabbing subject line, personalized content, and clear call-to-action."

        Return CallDeepSeek(config, userPrompt, systemPrompt, 1800, 0.4)
    End Function

    ''' <summary>
    ''' Generate arbitrage analysis commentary using DeepSeek
    ''' </summary>
    Public Shared Function GenerateArbitrageAnalysis(config As JObject, arbData As String, marketContext As String) As String
        Dim systemPrompt = "You are a quantitative sports betting analyst specializing in arbitrage opportunities. " &
                          "Provide technical analysis with mathematical precision and strategic insights."

        Dim userPrompt = $"Analyze this arbitrage opportunity: {arbData}. Market context: {marketContext}. " &
                        "Provide strategic commentary, risk assessment, and execution recommendations."

        Return CallDeepSeek(config, userPrompt, systemPrompt, 1200, 0.2)
    End Function

    ''' <summary>
    ''' Generate report summaries using DeepSeek
    ''' </summary>
    Public Shared Function GenerateReportSummary(config As JObject, reportData As String, reportType As String) As String
        Dim systemPrompt = "You are a data analyst specializing in sports betting performance reports. " &
                          "Create executive summaries that highlight key metrics, trends, and actionable insights."

        Dim userPrompt = $"Summarize this {reportType} report data: {reportData}. " &
                        "Focus on key performance indicators, notable trends, and strategic recommendations."

        Return CallDeepSeek(config, userPrompt, systemPrompt, 1500, 0.3)
    End Function

    ''' <summary>
    ''' Validate DeepSeek configuration
    ''' </summary>
    Private Shared Function ValidateConfig(config As JObject) As Boolean
        Try
            If config Is Nothing OrElse Not config.ContainsKey("deepseek") Then
                Return False
            End If

            Dim deepSeekConfig = config("deepseek")

            Return deepSeekConfig.ContainsKey("api_key") AndAlso
                   deepSeekConfig.ContainsKey("endpoint") AndAlso
                   deepSeekConfig.ContainsKey("model") AndAlso
                   Not String.IsNullOrEmpty(deepSeekConfig("api_key").ToString()) AndAlso
                   Not String.IsNullOrEmpty(deepSeekConfig("endpoint").ToString()) AndAlso
                   Not String.IsNullOrEmpty(deepSeekConfig("model").ToString())

        Catch
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Log DeepSeek API calls to database
    ''' </summary>
    Private Shared Sub LogDeepSeekCall(prompt As String, output As String, status As String)
        Try
            Using conn As New System.Data.SQLite.SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()

                Dim sql = "INSERT INTO deepseek_calls (ts, prompt, output, status, tokens_estimated, created_at) " &
                         "VALUES (@ts, @prompt, @output, @status, @tokens, @created_at)"

                Using cmd As New System.Data.SQLite.SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@ts", DateTime.UtcNow)
                    cmd.Parameters.AddWithValue("@prompt", prompt.Substring(0, Math.Min(prompt.Length, 1000))) ' Truncate long prompts
                    cmd.Parameters.AddWithValue("@output", output.Substring(0, Math.Min(output.Length, 5000))) ' Truncate long outputs
                    cmd.Parameters.AddWithValue("@status", status)
                    cmd.Parameters.AddWithValue("@tokens", EstimateTokens(prompt & output))
                    cmd.Parameters.AddWithValue("@created_at", DateTime.UtcNow)

                    cmd.ExecuteNonQuery()
                End Using
            End Using

            ' Send Telegram notification for successful calls with significant output
            If status = "success" AndAlso output.Length > 500 Then
                Task.Run(Sub()
                    Try
                        ' Load config for alerts (simplified for demo)
                        Dim notificationMsg = $"🤖 DeepSeek Integration Active{Environment.NewLine}" &
                                            $"Generated: {output.Length} characters{Environment.NewLine}" &
                                            $"Status: {status.ToUpper()}{Environment.NewLine}" &
                                            $"Time: {DateTime.Now:HH:mm:ss}"

                        Console.WriteLine($"DeepSeek Notification: {notificationMsg}")
                    Catch ex As Exception
                        Console.WriteLine($"Failed to send DeepSeek notification: {ex.Message}")
                    End Try
                End Sub)
            End If

        Catch ex As Exception
            Console.WriteLine($"Failed to log DeepSeek call: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Estimate token count (rough approximation)
    ''' </summary>
    Private Shared Function EstimateTokens(text As String) As Integer
        ' Rough estimation: ~4 characters per token for English text
        Return Math.Ceiling(text.Length / 4)
    End Function

    ''' <summary>
    ''' Test DeepSeek API connectivity and configuration
    ''' </summary>
    Public Shared Function TestConnection(config As JObject) As String
        Try
            If Not ValidateConfig(config) Then
                Return "❌ DeepSeek configuration missing or invalid"
            End If

            Dim testPrompt = "Respond with exactly: 'DeepSeek API connection successful'"
            Dim result = CallDeepSeek(config, testPrompt, "You are a helpful assistant.", 50, 0.1)

            If result.Contains("successful") Then
                Return "✅ DeepSeek API connection verified successfully"
            Else
                Return $"⚠️ DeepSeek API responded but unexpected result: {result}"
            End If

        Catch ex As Exception
            Return $"❌ DeepSeek API test failed: {ex.Message}"
        End Try
    End Function
End Class
