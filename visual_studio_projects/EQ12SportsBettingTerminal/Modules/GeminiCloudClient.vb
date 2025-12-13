Imports System.Net.Http
Imports System.Text
Imports System.Threading.Tasks
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq

''' <summary>
''' Gemini Cloud Chat Client for EQ12 Sports Betting Terminal
''' Provides operational co-pilot capabilities with Google Cloud Console integration
''' Features: conversational AI, operational commands, context-aware responses
''' </summary>
Public Class GeminiCloudClient
    Private ReadOnly _httpClient As HttpClient
    Private ReadOnly _gcpAuth As GCPAuth
    Private ReadOnly _projectId As String
    Private ReadOnly _location As String = "us-central1"
    Private ReadOnly _modelName As String = "gemini-1.5-pro"

    ''' <summary>
    ''' Gemini Chat Response with operational command support
    ''' </summary>
    Public Class GeminiChatResponse
        Public Property Success As Boolean = False
        Public Property Message As String = ""
        Public Property ErrorMessage As String = ""
        Public Property SuggestedActions As String() = {}
        Public Property OperationalCommand As Boolean = False
        Public Property CommandName As String = ""
        Public Property CommandParameters As Dictionary(Of String, String) = New Dictionary(Of String, String)()
        Public Property ConfidenceScore As Double = 0.0
        Public Property ResponseTimeMs As Integer = 0
        Public Property TokensUsed As Integer = 0
    End Class

    ''' <summary>
    ''' Operational context for Gemini responses
    ''' </summary>
    Public Enum OperationalContext
        General
        BettingAnalysis
        DataWarehouse
        CloudInfrastructure
        MonetizationStrategy
        SecurityAudit
        PerformanceOptimization
        ContentGeneration
    End Enum

    Public Sub New()
        _httpClient = New HttpClient() With {
            .Timeout = TimeSpan.FromSeconds(30)
        }
        _gcpAuth = New GCPAuth()
        _projectId = Environment.GetEnvironmentVariable("GOOGLE_CLOUD_PROJECT") ?? "eq12-sports-betting"
    End Sub

    ''' <summary>
    ''' Initialize Gemini Cloud client with authentication
    ''' </summary>
    Public Async Function InitializeAsync() As Task(Of Boolean)
        Try
            ' Initialize GCP authentication
            If Not Await _gcpAuth.InitializeAsync() Then
                Return False
            End If

            ' Get access token for Vertex AI
            Dim token = Await _gcpAuth.GetAccessTokenAsync("https://www.googleapis.com/auth/cloud-platform")
            If String.IsNullOrEmpty(token) Then
                Return False
            End If

            _httpClient.DefaultRequestHeaders.Clear()
            _httpClient.DefaultRequestHeaders.Authorization = New Headers.AuthenticationHeaderValue("Bearer", token)

            Return True

        Catch ex As Exception
            Console.WriteLine($"GeminiCloudClient initialization failed: {ex.Message}")
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Chat with Gemini using conversational context and operational awareness
    ''' </summary>
    Public Async Function ChatAsync(message As String, context As String, sessionId As String) As Task(Of GeminiChatResponse)
        Dim stopwatch = Diagnostics.Stopwatch.StartNew()

        Try
            ' Ensure authentication
            If Not Await InitializeAsync() Then
                Return New GeminiChatResponse() With {
                    .Success = False,
                    .ErrorMessage = "Authentication failed"
                }
            End If

            ' Build system prompt with operational context
            Dim systemPrompt = BuildOperationalSystemPrompt()

            ' Build conversation context
            Dim conversationContext = BuildConversationContext(context, message)

            ' Prepare request payload
            Dim requestPayload = New JObject From {
                {"contents", New JArray From {
                    New JObject From {
                        {"role", "user"},
                        {"parts", New JArray From {
                            New JObject From {{"text", $"{systemPrompt}\n\nContext:\n{conversationContext}\n\nUser: {message}"}}
                        }}
                    }
                }},
                {"generationConfig", New JObject From {
                    {"temperature", 0.7},
                    {"topP", 0.9},
                    {"topK", 40},
                    {"maxOutputTokens", 2048},
                    {"responseMimeType", "application/json"},
                    {"responseSchema", GetOperationalResponseSchema()}
                }},
                {"safetySettings", New JArray From {
                    New JObject From {
                        {"category", "HARM_CATEGORY_HARASSMENT"},
                        {"threshold", "BLOCK_MEDIUM_AND_ABOVE"}
                    },
                    New JObject From {
                        {"category", "HARM_CATEGORY_HATE_SPEECH"},
                        {"threshold", "BLOCK_MEDIUM_AND_ABOVE"}
                    },
                    New JObject From {
                        {"category", "HARM_CATEGORY_SEXUALLY_EXPLICIT"},
                        {"threshold", "BLOCK_MEDIUM_AND_ABOVE"}
                    },
                    New JObject From {
                        {"category", "HARM_CATEGORY_DANGEROUS_CONTENT"},
                        {"threshold", "BLOCK_MEDIUM_AND_ABOVE"}
                    }
                }}
            }

            ' Call Vertex AI Gemini API
            Dim url = $"https://{_location}-aiplatform.googleapis.com/v1/projects/{_projectId}/locations/{_location}/publishers/google/models/{_modelName}:generateContent"

            Dim content = New StringContent(requestPayload.ToString(), Encoding.UTF8, "application/json")
            Dim response = Await _httpClient.PostAsync(url, content)

            If response.IsSuccessStatusCode Then
                Dim responseText = Await response.Content.ReadAsStringAsync()
                Dim responseJson = JObject.Parse(responseText)

                ' Parse Gemini response
                Return ParseGeminiResponse(responseJson, stopwatch.ElapsedMilliseconds)
            Else
                Return New GeminiChatResponse() With {
                    .Success = False,
                    .ErrorMessage = $"API request failed: {response.StatusCode} - {Await response.Content.ReadAsStringAsync()}"
                }
            End If

        Catch ex As Exception
            Return New GeminiChatResponse() With {
                .Success = False,
                .ErrorMessage = $"Chat request failed: {ex.Message}",
                .ResponseTimeMs = stopwatch.ElapsedMilliseconds
            }
        Finally
            stopwatch.Stop()
        End Try
    End Function

    ''' <summary>
    ''' Query Gemini for operational analysis with specific context
    ''' </summary>
    Public Async Function AnalyzeOperationalContextAsync(query As String, context As OperationalContext) As Task(Of GeminiChatResponse)
        Dim contextualPrompt = BuildContextualPrompt(query, context)
        Return Await ChatAsync(contextualPrompt, "", Guid.NewGuid().ToString())
    End Function

    ''' <summary>
    ''' Generate operational recommendations based on system state
    ''' </summary>
    Public Async Function GetOperationalRecommendationsAsync() As Task(Of GeminiChatResponse)
        Dim systemState = Await GatherSystemStateAsync()
        Dim prompt = $"Based on the current EQ12 system state, provide operational recommendations:\n{systemState}"

        Return Await ChatAsync(prompt, "", Guid.NewGuid().ToString())
    End Function

    ''' <summary>
    ''' Build operational system prompt with EQ12 context
    ''' </summary>
    Private Function BuildOperationalSystemPrompt() As String
        Return "You are the EQ12 Operational Co-Pilot, an advanced AI assistant for the EQ12 Sports Betting Analytics platform.

ROLE & CAPABILITIES:
- You help manage Google Cloud Platform infrastructure and operations
- You provide betting insights, market analysis, and arbitrage opportunities
- You can execute operational commands and provide system recommendations
- You understand sports betting, bankroll management, and risk assessment
- You have access to BigQuery data warehouse, Cloud Storage, and monitoring systems

EQ12 SYSTEM OVERVIEW:
- Sports betting arbitrage detection and analysis platform
- Real-time odds ingestion from multiple sportsbooks
- Advanced analytics with injury tracking and market movement detection
- Bankroll management with Kelly Criterion staking
- Content monetization with tiered access (Free, Premium, Pro, Elite)
- Google Cloud Platform integration with Jump Start Solutions

OPERATIONAL COMMANDS YOU CAN TRIGGER:
- sync_bigquery: Sync local data to BigQuery warehouse
- generate_report: Create betting analysis reports (daily/weekly/monthly)
- check_arbitrage: Scan for current arbitrage opportunities
- bankroll_status: Show current bankroll and performance metrics
- deploy_model: Deploy updated ML models to Cloud Run
- security_audit: Run security checks on the platform
- cost_analysis: Analyze GCP costs and optimization opportunities

RESPONSE FORMAT:
Always respond with a JSON object containing:
{
  ""message"": ""Your conversational response"",
  ""suggested_actions"": [""List of suggested actions""],
  ""operational_command"": false/true,
  ""command_name"": ""command_to_execute"",
  ""command_parameters"": {""key"": ""value""},
  ""confidence_score"": 0.0-1.0
}

Be helpful, accurate, and always prioritize the user's sports betting success and platform security."
    End Function

    ''' <summary>
    ''' Build conversation context with recent system activity
    ''' </summary>
    Private Function BuildConversationContext(existingContext As String, currentMessage As String) As String
        Dim contextBuilder = New StringBuilder()

        ' Add existing conversation context
        If Not String.IsNullOrEmpty(existingContext) Then
            contextBuilder.AppendLine("Recent Conversation:")
            contextBuilder.AppendLine(existingContext)
            contextBuilder.AppendLine()
        End If

        ' Add system metrics context
        contextBuilder.AppendLine("Current System Context:")
        contextBuilder.AppendLine($"- Timestamp: {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC")
        contextBuilder.AppendLine($"- Platform: EQ12 Sports Betting Terminal")
        contextBuilder.AppendLine($"- Environment: {Environment.GetEnvironmentVariable("ENVIRONMENT") ?? "production"}")

        ' Add operational context based on message content
        If currentMessage.ToLower().Contains("arbitrage") Then
            contextBuilder.AppendLine("- Context: Arbitrage analysis requested")
        ElseIf currentMessage.ToLower().Contains("bankroll") Then
            contextBuilder.AppendLine("- Context: Bankroll management inquiry")
        ElseIf currentMessage.ToLower().Contains("bigquery") Or currentMessage.ToLower().Contains("data") Then
            contextBuilder.AppendLine("- Context: Data warehouse operations")
        ElseIf currentMessage.ToLower().Contains("deploy") Or currentMessage.ToLower().Contains("cloud") Then
            contextBuilder.AppendLine("- Context: Cloud infrastructure management")
        End If

        Return contextBuilder.ToString()
    End Function

    ''' <summary>
    ''' Build contextual prompt based on operational context
    ''' </summary>
    Private Function BuildContextualPrompt(query As String, context As OperationalContext) As String
        Dim contextPrompt As String = ""

        Select Case context
            Case OperationalContext.BettingAnalysis
                contextPrompt = "As a sports betting analyst, analyze the following query with focus on profit opportunities and risk management:"
            Case OperationalContext.DataWarehouse
                contextPrompt = "As a data warehouse administrator, provide insights on the following BigQuery and data management query:"
            Case OperationalContext.CloudInfrastructure
                contextPrompt = "As a Google Cloud Platform administrator, address the following infrastructure and deployment query:"
            Case OperationalContext.MonetizationStrategy
                contextPrompt = "As a monetization strategist, analyze the following query for revenue optimization opportunities:"
            Case OperationalContext.SecurityAudit
                contextPrompt = "As a security analyst, evaluate the following query for potential security implications and recommendations:"
            Case OperationalContext.PerformanceOptimization
                contextPrompt = "As a performance optimization expert, analyze the following query for system efficiency improvements:"
            Case OperationalContext.ContentGeneration
                contextPrompt = "As a content strategist, help generate engaging content for the following query:"
            Case Else
                contextPrompt = "As the EQ12 operational co-pilot, provide comprehensive assistance for the following query:"
        End Select

        Return $"{contextPrompt}\n\nQuery: {query}"
    End Function

    ''' <summary>
    ''' Get operational response schema for structured JSON responses
    ''' </summary>
    Private Function GetOperationalResponseSchema() As JObject
        Return New JObject From {
            {"type", "object"},
            {"properties", New JObject From {
                {"message", New JObject From {
                    {"type", "string"},
                    {"description", "Conversational response to the user"}
                }},
                {"suggested_actions", New JObject From {
                    {"type", "array"},
                    {"items", New JObject From {{"type", "string"}}},
                    {"description", "List of suggested actions"}
                }},
                {"operational_command", New JObject From {
                    {"type", "boolean"},
                    {"description", "Whether to execute an operational command"}
                }},
                {"command_name", New JObject From {
                    {"type", "string"},
                    {"description", "Name of the operational command to execute"}
                }},
                {"command_parameters", New JObject From {
                    {"type", "object"},
                    {"description", "Parameters for the operational command"}
                }},
                {"confidence_score", New JObject From {
                    {"type", "number"},
                    {"minimum", 0.0},
                    {"maximum", 1.0},
                    {"description", "Confidence score of the response"}
                }}
            }},
            {"required", New JArray From {"message", "suggested_actions", "operational_command", "confidence_score"}}
        }
    End Function

    ''' <summary>
    ''' Parse Gemini API response into structured chat response
    ''' </summary>
    Private Function ParseGeminiResponse(responseJson As JObject, responseTimeMs As Long) As GeminiChatResponse
        Try
            ' Extract the generated content
            Dim candidates = responseJson("candidates")
            If candidates?.Count() > 0 Then
                Dim content = candidates(0)("content")("parts")(0)("text").ToString()

                ' Parse JSON response from Gemini
                Dim parsedContent = JObject.Parse(content)

                Dim response = New GeminiChatResponse() With {
                    .Success = True,
                    .Message = parsedContent("message")?.ToString() ?? "",
                    .SuggestedActions = parsedContent("suggested_actions")?.ToObject(Of String())() ?? {},
                    .OperationalCommand = parsedContent("operational_command")?.ToObject(Of Boolean)() ?? False,
                    .CommandName = parsedContent("command_name")?.ToString() ?? "",
                    .ConfidenceScore = parsedContent("confidence_score")?.ToObject(Of Double)() ?? 0.0,
                    .ResponseTimeMs = responseTimeMs
                }

                ' Parse command parameters if present
                If parsedContent("command_parameters") IsNot Nothing Then
                    response.CommandParameters = parsedContent("command_parameters").ToObject(Of Dictionary(Of String, String))()
                End If

                ' Extract token usage if available
                If responseJson("usageMetadata") IsNot Nothing Then
                    response.TokensUsed = responseJson("usageMetadata")("totalTokenCount")?.ToObject(Of Integer)() ?? 0
                End If

                Return response
            Else
                Return New GeminiChatResponse() With {
                    .Success = False,
                    .ErrorMessage = "No candidates in response",
                    .ResponseTimeMs = responseTimeMs
                }
            End If

        Catch ex As Exception
            Return New GeminiChatResponse() With {
                .Success = False,
                .ErrorMessage = $"Response parsing failed: {ex.Message}",
                .ResponseTimeMs = responseTimeMs
            }
        End Try
    End Function

    ''' <summary>
    ''' Gather current system state for operational analysis
    ''' </summary>
    Private Async Function GatherSystemStateAsync() As Task(Of String)
        Dim stateBuilder = New StringBuilder()

        Try
            stateBuilder.AppendLine("EQ12 SYSTEM STATE:")
            stateBuilder.AppendLine($"Timestamp: {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss} UTC")
            stateBuilder.AppendLine()

            ' System health indicators
            stateBuilder.AppendLine("SYSTEM HEALTH:")
            stateBuilder.AppendLine($"- Memory Usage: {GC.GetTotalMemory(False) / 1024 / 1024:N0} MB")
            stateBuilder.AppendLine($"- Process Uptime: {DateTime.Now - Process.GetCurrentProcess().StartTime}")
            stateBuilder.AppendLine()

            ' Recent activity (would integrate with actual monitoring)
            stateBuilder.AppendLine("RECENT ACTIVITY:")
            stateBuilder.AppendLine("- Last odds ingestion: [Would check actual timestamps]")
            stateBuilder.AppendLine("- Active arbitrage opportunities: [Would check current count]")
            stateBuilder.AppendLine("- BigQuery sync status: [Would check last sync time]")
            stateBuilder.AppendLine()

            ' GCP resource status
            stateBuilder.AppendLine("GCP RESOURCES:")
            stateBuilder.AppendLine($"- Project: {_projectId}")
            stateBuilder.AppendLine($"- Region: {_location}")
            stateBuilder.AppendLine("- Services: BigQuery, Cloud Storage, Cloud Run, Secret Manager")
            stateBuilder.AppendLine()

            Return stateBuilder.ToString()

        Catch ex As Exception
            stateBuilder.AppendLine($"Error gathering system state: {ex.Message}")
            Return stateBuilder.ToString()
        End Try
    End Function

    ''' <summary>
    ''' Test connection to Gemini Cloud API
    ''' </summary>
    Public Async Function TestConnectionAsync() As Task(Of Boolean)
        Try
            Dim testResponse = Await ChatAsync("Hello, please respond with a simple acknowledgment.", "", "test-session")
            Return testResponse.Success
        Catch
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Get Gemini API usage statistics
    ''' </summary>
    Public Async Function GetUsageStatsAsync() As Task(Of Dictionary(Of String, Object))
        Dim stats = New Dictionary(Of String, Object)()

        Try
            ' Would integrate with Cloud Monitoring for actual usage stats
            stats("total_requests") = "Available via Cloud Monitoring"
            stats("total_tokens") = "Available via Cloud Monitoring"
            stats("average_response_time") = "Available via Cloud Monitoring"
            stats("error_rate") = "Available via Cloud Monitoring"
            stats("cost_this_month") = "Available via Cloud Billing API"

        Catch ex As Exception
            stats("error") = ex.Message
        End Try

        Return stats
    End Function

    Public Sub Dispose()
        _httpClient?.Dispose()
    End Sub

End Class
