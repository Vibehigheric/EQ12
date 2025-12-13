Imports System.Text.RegularExpressions
Imports Newtonsoft.Json.Linq
Imports System.Net.Http
Imports System.Text
Imports System.Data.SQLite

''' <summary>
''' Meta-LLM Router - Intelligent AI Provider Selection for EQ12
''' Automatically decides which AI (ChatGPT, DeepSeek, Copilot, Gemini, Claude, LLaMA) to use
''' based on task type, prompt analysis, cost optimization, and performance tracking
''' </summary>
Public Class LLMRouter

    Private Shared ReadOnly HttpClient As New HttpClient()

    ''' <summary>
    ''' Intelligently decide which AI provider to use based on task type and prompt analysis
    ''' </summary>
    ''' <param name="config">Configuration object</param>
    ''' <param name="taskType">Task type (reporting, bulk_stats, code_gen, search_insights, etc.)</param>
    ''' <param name="prompt">The actual prompt text for analysis</param>
    ''' <param name="overrideProvider">Manual override provider (optional)</param>
    ''' <returns>Selected AI provider name</returns>
    Public Shared Function DecideProvider(config As JObject, taskType As String, prompt As String,
                                        Optional overrideProvider As String = Nothing) As String
        Try
            Console.WriteLine($"🤖 LLM Router: Analyzing task '{taskType}' (prompt length: {prompt.Length})")

            ' Check for manual override first
            If Not String.IsNullOrEmpty(overrideProvider) Then
                If IsProviderAvailable(config, overrideProvider) Then
                    Console.WriteLine($"🎯 Using manual override: {overrideProvider.ToUpper()}")
                    Return overrideProvider
                Else
                    Console.WriteLine($"⚠️ Override provider '{overrideProvider}' not available, falling back to auto-selection")
                End If
            End If

            ' Get router configuration
            Dim routerConfig = config("llm_router")
            If routerConfig Is Nothing OrElse routerConfig("enabled")?.ToObject(Of Boolean)() <> True Then
                Console.WriteLine("ℹ️ LLM Router disabled, using default provider")
                Return config("llm")("default_provider")?.ToString() ?? "openai"
            End If

            ' Check explicit task type rules first
            Dim rules = routerConfig("rules")
            If rules IsNot Nothing AndAlso rules(taskType) IsNot Nothing Then
                Dim ruleProvider = rules(taskType).ToString()
                If IsProviderAvailable(config, ruleProvider) Then
                    Console.WriteLine($"📋 Rule-based selection: {taskType} → {ruleProvider.ToUpper()}")
                    Return ruleProvider
                End If
            End If

            ' Analyze prompt characteristics
            Dim analysis = AnalyzePrompt(prompt, routerConfig)
            Console.WriteLine($"📊 Prompt analysis: {String.Join(", ", analysis.Select(Function(kvp) $"{kvp.Key}={kvp.Value}"))}")

            ' Apply intelligent selection heuristics
            Dim selectedProvider = ApplySelectionHeuristics(config, taskType, prompt, analysis)

            ' Validate provider availability
            If Not IsProviderAvailable(config, selectedProvider) Then
                Console.WriteLine($"⚠️ Selected provider '{selectedProvider}' not available, falling back")
                selectedProvider = GetFallbackProvider(config, selectedProvider)
            End If

            Console.WriteLine($"✅ Selected provider: {selectedProvider.ToUpper()}")
            Return selectedProvider

        Catch ex As Exception
            Console.WriteLine($"❌ LLM Router error: {ex.Message}")
            Return config("llm")("default_provider")?.ToString() ?? "openai"
        End Try
    End Function

    ''' <summary>
    ''' Analyze prompt characteristics to inform provider selection
    ''' </summary>
    Private Shared Function AnalyzePrompt(prompt As String, routerConfig As JObject) As Dictionary(Of String, Object)
        Dim analysis As New Dictionary(Of String, Object)

        ' Basic metrics
        analysis("length") = prompt.Length
        analysis("word_count") = prompt.Split({" "c, vbTab, vbCrLf}, StringSplitOptions.RemoveEmptyEntries).Length

        ' Complexity indicators
        analysis("has_code") = Regex.IsMatch(prompt, "```|function\s|class\s|import\s|SELECT\s", RegexOptions.IgnoreCase)
        analysis("has_numbers") = Regex.Matches(prompt, "\d+").Count
        analysis("has_urls") = Regex.IsMatch(prompt, "https?://")

        ' Content type detection
        Dim creativeKeywords = routerConfig("prompt_analysis")("creative_keywords")?.ToObject(Of String())() ?? {}
        Dim analyticalKeywords = routerConfig("prompt_analysis")("analytical_keywords")?.ToObject(Of String())() ?? {}

        analysis("creative_score") = creativeKeywords.Count(Function(kw) prompt.ToLower().Contains(kw.ToLower()))
        analysis("analytical_score") = analyticalKeywords.Count(Function(kw) prompt.ToLower().Contains(kw.ToLower()))

        ' Context length thresholds
        Dim longContextThreshold = routerConfig("prompt_analysis")("long_context_threshold")?.ToObject(Of Integer)() ?? 8000
        Dim bulkThreshold = routerConfig("prompt_analysis")("bulk_processing_threshold")?.ToObject(Of Integer)() ?? 100

        analysis("is_long_context") = prompt.Length > longContextThreshold
        analysis("is_bulk_processing") = analysis("word_count") > bulkThreshold

        Return analysis
    End Function

    ''' <summary>
    ''' Apply intelligent selection heuristics based on task type and prompt analysis
    ''' </summary>
    Private Shared Function ApplySelectionHeuristics(config As JObject, taskType As String,
                                                   prompt As String, analysis As Dictionary(Of String, Object)) As String
        Try
            Dim routerConfig = config("llm_router")

            ' Long context analysis → Claude
            If CBool(analysis("is_long_context")) Then
                Console.WriteLine("📄 Long context detected → Claude")
                Return "claude"
            End If

            ' Bulk processing → DeepSeek (cost-effective)
            If CBool(analysis("is_bulk_processing")) Then
                Console.WriteLine("📊 Bulk processing detected → DeepSeek")
                Return "deepseek"
            End If

            ' Code generation → Copilot
            If CBool(analysis("has_code")) OrElse taskType.ToLower().Contains("code") Then
                Console.WriteLine("💻 Code generation detected → Copilot")
                Return "copilot"
            End If

            ' Search/fresh data needs → Gemini
            If taskType.ToLower().Contains("search") OrElse CBool(analysis("has_urls")) OrElse
               prompt.ToLower().Contains("latest") OrElse prompt.ToLower().Contains("current") Then
                Console.WriteLine("🔍 Search/fresh data detected → Gemini")
                Return "gemini"
            End If

            ' Creative content → OpenAI
            If CInt(analysis("creative_score")) > 0 OrElse taskType.ToLower().Contains("creative") OrElse
               taskType.ToLower().Contains("newsletter") OrElse taskType.ToLower().Contains("narrative") Then
                Console.WriteLine("🎨 Creative content detected → OpenAI")
                Return "openai"
            End If

            ' Analytical/statistical → DeepSeek (cost-effective)
            If CInt(analysis("analytical_score")) > 1 OrElse taskType.ToLower().Contains("stats") OrElse
               taskType.ToLower().Contains("analysis") OrElse CInt(analysis("has_numbers")) > 5 Then
                Console.WriteLine("📈 Analytical content detected → DeepSeek")
                Return "deepseek"
            End If

            ' Cost optimization for simple tasks
            If prompt.Length < 500 AndAlso CInt(analysis("word_count")) < 50 Then
                Console.WriteLine("💰 Simple task detected → DeepSeek (cost optimization)")
                Return "deepseek"
            End If

            ' Default fallback
            Dim defaultProvider = routerConfig("default")?.ToString() ?? "openai"
            Console.WriteLine($"🔄 Using default provider → {defaultProvider}")
            Return defaultProvider

        Catch ex As Exception
            Console.WriteLine($"⚠️ Heuristics error: {ex.Message}")
            Return "openai"
        End Try
    End Function

    ''' <summary>
    ''' Call the selected LLM provider with the given prompt
    ''' </summary>
    ''' <param name="config">Configuration object</param>
    ''' <param name="provider">AI provider name</param>
    ''' <param name="prompt">Prompt text</param>
    ''' <param name="taskType">Task type for logging</param>
    ''' <returns>Generated response text</returns>
    Public Shared Function CallLLM(config As JObject, provider As String, prompt As String,
                                  Optional taskType As String = "general") As String
        Dim startTime = DateTime.UtcNow
        Dim response As String = ""
        Dim status As String = "success"
        Dim tokensUsed As Integer = 0
        Dim costEstimate As Double = 0

        Try
            Console.WriteLine($"🚀 Calling {provider.ToUpper()} for {taskType} task...")

            Select Case provider.ToLower()
                Case "openai"
                    response = CallOpenAI(config, prompt, tokensUsed, costEstimate)
                Case "deepseek"
                    response = DeepSeekHelper.CallDeepSeek(config, prompt, taskType)
                    tokensUsed = EstimateTokens(prompt & response)
                    costEstimate = CalculateCost(config, "deepseek", tokensUsed)
                Case "gemini"
                    response = CallGemini(config, prompt, tokensUsed, costEstimate)
                Case "claude"
                    response = CallClaude(config, prompt, tokensUsed, costEstimate)
                Case "copilot"
                    response = CallCopilot(config, prompt, tokensUsed, costEstimate)
                Case "llama"
                    response = CallLlama(config, prompt, tokensUsed, costEstimate)
                Case Else
                    Throw New ArgumentException($"Unknown provider: {provider}")
            End Select

            If String.IsNullOrEmpty(response) Then
                status = "empty_response"
                response = "Error: Empty response from " & provider
            End If

        Catch ex As Exception
            status = "error"
            response = $"Error calling {provider}: {ex.Message}"
            Console.WriteLine($"❌ {response}")
        Finally
            ' Log the call for audit and optimization
            Dim executionTime = CInt((DateTime.UtcNow - startTime).TotalMilliseconds)
            LogLLMCall(provider, taskType, prompt, response, status, tokensUsed, costEstimate, executionTime)
        End Try

        Return response
    End Function

    ''' <summary>
    ''' Enhanced OpenAI API call with token and cost tracking
    ''' </summary>
    Private Shared Function CallOpenAI(config As JObject, prompt As String,
                                     ByRef tokensUsed As Integer, ByRef costEstimate As Double) As String
        Try
            ' Use existing OpenAI helper with enhancements
            Dim response = OpenAIHelper.CallOpenAI(config, prompt, "user")

            ' Estimate tokens (approximate)
            tokensUsed = EstimateTokens(prompt & response)
            costEstimate = CalculateCost(config, "openai", tokensUsed)

            Return response
        Catch ex As Exception
            Throw New Exception($"OpenAI call failed: {ex.Message}")
        End Try
    End Function

    ''' <summary>
    ''' Google Gemini API integration
    ''' </summary>
    Private Shared Function CallGemini(config As JObject, prompt As String,
                                     ByRef tokensUsed As Integer, ByRef costEstimate As Double) As String
        Try
            Dim geminiConfig = config("gemini")
            If geminiConfig Is Nothing Then
                Throw New Exception("Gemini configuration not found")
            End If

            Dim apiKey = geminiConfig("api_key")?.ToString()
            If String.IsNullOrEmpty(apiKey) OrElse apiKey = "YOUR_GEMINI_API_KEY" Then
                Throw New Exception("Gemini API key not configured")
            End If

            Dim requestBody As New JObject()
            Dim contents As New JArray()
            Dim content As New JObject()
            Dim parts As New JArray()
            parts.Add(New JObject() From {{"text", prompt}})
            content("parts") = parts
            contents.Add(content)
            requestBody("contents") = contents

            Dim json = requestBody.ToString()
            Dim requestContent = New StringContent(json, Encoding.UTF8, "application/json")

            Dim endpoint = geminiConfig("endpoint")?.ToString() & "?key=" & apiKey
            Dim response = HttpClient.PostAsync(endpoint, requestContent).Result

            If response.IsSuccessStatusCode Then
                Dim responseContent = response.Content.ReadAsStringAsync().Result
                Dim responseObj = JObject.Parse(responseContent)

                Dim generatedText = responseObj("candidates")?.(0)?("content")?("parts")?.(0)?("text")?.ToString()

                tokensUsed = EstimateTokens(prompt & generatedText)
                costEstimate = CalculateCost(config, "gemini", tokensUsed)

                Return generatedText ?? "No response generated"
            Else
                Throw New Exception($"Gemini API error: {response.StatusCode}")
            End If

        Catch ex As Exception
            Throw New Exception($"Gemini call failed: {ex.Message}")
        End Try
    End Function

    ''' <summary>
    ''' Anthropic Claude API integration
    ''' </summary>
    Private Shared Function CallClaude(config As JObject, prompt As String,
                                     ByRef tokensUsed As Integer, ByRef costEstimate As Double) As String
        Try
            Dim claudeConfig = config("claude")
            If claudeConfig Is Nothing Then
                Throw New Exception("Claude configuration not found")
            End If

            Dim apiKey = claudeConfig("api_key")?.ToString()
            If String.IsNullOrEmpty(apiKey) OrElse apiKey = "YOUR_CLAUDE_API_KEY" Then
                Throw New Exception("Claude API key not configured")
            End If

            Dim requestBody As New JObject() From {
                {"model", claudeConfig("model")?.ToString() ?? "claude-3-sonnet-20240229"},
                {"max_tokens", claudeConfig("max_tokens")?.ToObject(Of Integer)() ?? 4096},
                {"messages", New JArray() From {
                    New JObject() From {
                        {"role", "user"},
                        {"content", prompt}
                    }
                }}
            }

            HttpClient.DefaultRequestHeaders.Clear()
            HttpClient.DefaultRequestHeaders.Add("x-api-key", apiKey)
            HttpClient.DefaultRequestHeaders.Add("anthropic-version", "2023-06-01")

            Dim json = requestBody.ToString()
            Dim requestContent = New StringContent(json, Encoding.UTF8, "application/json")
            Dim endpoint = claudeConfig("endpoint")?.ToString()
            Dim response = HttpClient.PostAsync(endpoint, requestContent).Result

            If response.IsSuccessStatusCode Then
                Dim responseContent = response.Content.ReadAsStringAsync().Result
                Dim responseObj = JObject.Parse(responseContent)

                Dim generatedText = responseObj("content")?.(0)?("text")?.ToString()

                tokensUsed = EstimateTokens(prompt & generatedText)
                costEstimate = CalculateCost(config, "claude", tokensUsed)

                Return generatedText ?? "No response generated"
            Else
                Throw New Exception($"Claude API error: {response.StatusCode}")
            End If

        Catch ex As Exception
            Throw New Exception($"Claude call failed: {ex.Message}")
        End Try
    End Function

    ''' <summary>
    ''' GitHub Copilot API integration
    ''' </summary>
    Private Shared Function CallCopilot(config As JObject, prompt As String,
                                      ByRef tokensUsed As Integer, ByRef costEstimate As Double) As String
        Try
            ' Placeholder for GitHub Copilot API integration
            ' Note: GitHub Copilot Chat API may have different authentication requirements
            Throw New NotImplementedException("Copilot API integration pending - requires GitHub Enterprise access")

        Catch ex As Exception
            Throw New Exception($"Copilot call failed: {ex.Message}")
        End Try
    End Function

    ''' <summary>
    ''' Local LLaMA model integration (Ollama)
    ''' </summary>
    Private Shared Function CallLlama(config As JObject, prompt As String,
                                    ByRef tokensUsed As Integer, ByRef costEstimate As Double) As String
        Try
            Dim llamaConfig = config("llama")
            If llamaConfig Is Nothing Then
                Throw New Exception("LLaMA configuration not found")
            End If

            Dim requestBody As New JObject() From {
                {"model", llamaConfig("model")?.ToString() ?? "llama2:7b"},
                {"prompt", prompt},
                {"stream", False}
            }

            Dim json = requestBody.ToString()
            Dim requestContent = New StringContent(json, Encoding.UTF8, "application/json")
            Dim endpoint = llamaConfig("endpoint")?.ToString()
            Dim response = HttpClient.PostAsync(endpoint, requestContent).Result

            If response.IsSuccessStatusCode Then
                Dim responseContent = response.Content.ReadAsStringAsync().Result
                Dim responseObj = JObject.Parse(responseContent)

                Dim generatedText = responseObj("response")?.ToString()

                tokensUsed = EstimateTokens(prompt & generatedText)
                costEstimate = CalculateCost(config, "llama", tokensUsed)

                Return generatedText ?? "No response generated"
            Else
                Throw New Exception($"LLaMA API error: {response.StatusCode}")
            End If

        Catch ex As Exception
            Throw New Exception($"LLaMA call failed: {ex.Message}")
        End Try
    End Function

    ''' <summary>
    ''' Check if a provider is available and configured
    ''' </summary>
    Private Shared Function IsProviderAvailable(config As JObject, provider As String) As Boolean
        Try
            Select Case provider.ToLower()
                Case "openai"
                    Return config("openai")?("key")?.ToString() <> "YOUR_OPENAI_API_KEY"
                Case "deepseek"
                    Return config("deepseek")?("api_key")?.ToString() <> "YOUR_DEEPSEEK_API_KEY"
                Case "gemini"
                    Return config("gemini")?("api_key")?.ToString() <> "YOUR_GEMINI_API_KEY"
                Case "claude"
                    Return config("claude")?("api_key")?.ToString() <> "YOUR_CLAUDE_API_KEY"
                Case "copilot"
                    Return config("copilot")?("api_key")?.ToString() <> "YOUR_GITHUB_TOKEN"
                Case "llama"
                    Return True ' Local model, assume available if configured
                Case Else
                    Return False
            End Select
        Catch
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Get fallback provider when primary selection is unavailable
    ''' </summary>
    Private Shared Function GetFallbackProvider(config As JObject, primaryProvider As String) As String
        Dim fallbackOrder = {"deepseek", "openai", "gemini", "claude", "llama"}

        For Each provider In fallbackOrder
            If provider <> primaryProvider AndAlso IsProviderAvailable(config, provider) Then
                Console.WriteLine($"🔄 Fallback: {primaryProvider} → {provider}")
                Return provider
            End If
        Next

        ' Ultimate fallback
        Return "openai"
    End Function

    ''' <summary>
    ''' Estimate token count for cost calculation
    ''' </summary>
    Private Shared Function EstimateTokens(text As String) As Integer
        ' Rough estimation: ~4 characters per token for English text
        Return Math.Max(1, CInt(text.Length / 4))
    End Function

    ''' <summary>
    ''' Calculate estimated cost based on provider and token count
    ''' </summary>
    Private Shared Function CalculateCost(config As JObject, provider As String, tokens As Integer) As Double
        Try
            Dim routerConfig = config("llm_router")
            Dim providerConfig = routerConfig("providers")(provider)
            If providerConfig IsNot Nothing Then
                Dim costPer1k = providerConfig("cost_per_1k_tokens")?.ToObject(Of Double)() ?? 0.01
                Return (tokens / 1000.0) * costPer1k
            End If
            Return 0.0
        Catch
            Return 0.0
        End Try
    End Function

    ''' <summary>
    ''' Log LLM call for audit and performance tracking
    ''' </summary>
    Private Shared Sub LogLLMCall(provider As String, taskType As String, prompt As String,
                                 response As String, status As String, tokensUsed As Integer,
                                 costEstimate As Double, executionTimeMs As Integer)
        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()

                ' Truncate long texts for database storage
                Dim truncatedPrompt = If(prompt.Length > 1000, prompt.Substring(0, 1000) & "...", prompt)
                Dim truncatedResponse = If(response.Length > 2000, response.Substring(0, 2000) & "...", response)

                Dim sql = "INSERT INTO llm_calls (ts, provider, task_type, prompt, response, status, " &
                         "tokens_used, cost_estimate, execution_time_ms, created_at) " &
                         "VALUES (@ts, @provider, @task_type, @prompt, @response, @status, " &
                         "@tokens_used, @cost_estimate, @execution_time_ms, @created_at)"

                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@ts", DateTime.UtcNow)
                    cmd.Parameters.AddWithValue("@provider", provider)
                    cmd.Parameters.AddWithValue("@task_type", taskType)
                    cmd.Parameters.AddWithValue("@prompt", truncatedPrompt)
                    cmd.Parameters.AddWithValue("@response", truncatedResponse)
                    cmd.Parameters.AddWithValue("@status", status)
                    cmd.Parameters.AddWithValue("@tokens_used", tokensUsed)
                    cmd.Parameters.AddWithValue("@cost_estimate", costEstimate)
                    cmd.Parameters.AddWithValue("@execution_time_ms", executionTimeMs)
                    cmd.Parameters.AddWithValue("@created_at", DateTime.UtcNow)

                    cmd.ExecuteNonQuery()
                End Using
            End Using
        Catch ex As Exception
            Console.WriteLine($"⚠️ Failed to log LLM call: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Get LLM usage statistics for performance monitoring
    ''' </summary>
    Public Shared Function GetUsageStats() As String
        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()

                Dim sql = "SELECT provider, COUNT(*) as call_count, AVG(tokens_used) as avg_tokens, " &
                         "SUM(cost_estimate) as total_cost, AVG(execution_time_ms) as avg_time " &
                         "FROM llm_calls WHERE date(created_at) >= date('now', '-7 days') " &
                         "GROUP BY provider ORDER BY call_count DESC"

                Using cmd As New SQLiteCommand(sql, conn)
                    Using reader = cmd.ExecuteReader()
                        Dim stats As New StringBuilder()
                        stats.AppendLine("🤖 LLM Usage Statistics (Last 7 Days):")
                        stats.AppendLine()

                        While reader.Read()
                            Dim provider = reader("provider").ToString()
                            Dim callCount = reader("call_count").ToString()
                            Dim avgTokens = Math.Round(CDbl(reader("avg_tokens")), 0)
                            Dim totalCost = Math.Round(CDbl(reader("total_cost")), 4)
                            Dim avgTime = Math.Round(CDbl(reader("avg_time")), 0)

                            stats.AppendLine($"  {provider.ToUpper()}: {callCount} calls, ~{avgTokens} tokens avg, ${totalCost} total, {avgTime}ms avg")
                        End While

                        Return stats.ToString()
                    End Using
                End Using
            End Using
        Catch ex As Exception
            Return $"Error getting LLM stats: {ex.Message}"
        End Try
    End Function
End Class
