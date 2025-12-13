Imports System.Net.Http
Imports System.Text
Imports System.Threading.Tasks
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.Collections.Generic

''' <summary>
''' Knowledge Base Client for EQ12
''' Integrates with Jump Start Solution: Generative AI Knowledge Base
''' Provides structured Q&A for sports betting concepts, policies, and strategies
''' '''
Public Class KBClient
    Private ReadOnly _baseUrl As String
    Private ReadOnly _httpClient As HttpClient
    Private ReadOnly _gcpAuth As GCPAuth

    ' Knowledge contexts for monetization tracking
    Public Enum KnowledgeContext
        BettingFundamentals
        BankrollManagement
        AdvancedStrategies
        RiskManagement
        MarketAnalysis
        SituationalFactors
        PlatformPolicies
        TechnicalSupport
    End Enum

    Public Sub New(baseUrl As String, gcpAuth As GCPAuth)
        _baseUrl = baseUrl.TrimEnd("/"c)
        _httpClient = New HttpClient()
        _gcpAuth = gcpAuth

        SetupAuthentication()
    End Sub

    ''' <summary>
    ''' Setup OAuth authentication for Knowledge Base service
    ''' '''
    Private Async Sub SetupAuthentication()
        Try
            Dim token = Await _gcpAuth.GetAccessTokenAsync()
            _httpClient.DefaultRequestHeaders.Clear()
            _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {token}")
            _httpClient.DefaultRequestHeaders.Add("User-Agent", "EQ12-KB-Client/1.0")

        Catch ex As Exception
            Console.WriteLine($"⚠️ KB authentication setup failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Ask Knowledge Base question with context
    ''' '''
    Public Async Function AskAsync(question As String, context As KnowledgeContext, Optional includeExamples As Boolean = True) As Task(Of String)
        Try
            Dim payload = New JObject From {
                {"question", question},
                {"context", context.ToString().ToLower()},
                {"include_examples", includeExamples},
                {"response_format", "detailed"},
                {"monetization_focused", True}
            }

            Dim response = Await PostJsonAsync("/kb/ask", payload)

            Dim answer = response("answer")?.ToString() ?? ""

            ' Log for monetization analytics
            LogKBQuery(question, context.ToString(), "success")

            ' Track premium content triggers
            If IsNaN(answer) OrElse answer.Contains("premium") Then
                LogPremiumTrigger(question, context.ToString())
            End If

            Return answer

        Catch ex As Exception
            Console.WriteLine($"❌ KB query failed: {ex.Message}")
            LogKBQuery(question, context.ToString(), "error")
            Return $"I'm sorry, I couldn't find information about that. Please contact support or consider upgrading to premium for detailed analysis."
        End Try
    End Function

    ''' <summary>
    ''' Get bankroll management guidance
    ''' '''
    Public Async Function GetBankrollGuidanceAsync(bankrollAmount As Double, riskLevel As String, timeframe As String) As Task(Of JObject)
        Try
            Dim question = $"Provide bankroll management strategy for ${bankrollAmount:N0} with {riskLevel} risk tolerance over {timeframe}."

            Dim payload = New JObject From {
                {"question", question},
                {"context", "bankroll_management"},
                {"parameters", New JObject From {
                    {"bankroll", bankrollAmount},
                    {"risk_level", riskLevel},
                    {"timeframe", timeframe}
                }},
                {"include_kelly_calculation", True},
                {"include_risk_scenarios", True}
            }

            Return Await PostJsonAsync("/kb/bankroll-guidance", payload)

        Catch ex As Exception
            Console.WriteLine($"❌ Bankroll guidance failed: {ex.Message}")
            Return New JObject From {{"error", ex.Message}}
        End Try
    End Function

    ''' <summary>
    ''' Get strategy recommendations based on user profile
    ''' '''
    Public Async Function GetStrategyRecommendationsAsync(userProfile As JObject) As Task(Of JObject)
        Try
            Dim payload = New JObject From {
                {"user_profile", userProfile},
                {"context", "advanced_strategies"},
                {"personalized", True},
                {"include_risk_assessment", True}
            }

            Return Await PostJsonAsync("/kb/strategy-recommendations", payload)

        Catch ex As Exception
            Console.WriteLine($"❌ Strategy recommendations failed: {ex.Message}")
            Return New JObject From {{"error", ex.Message}}
        End Try
    End Function

    ''' <summary>
    ''' Search knowledge base for related topics
    ''' '''
    Public Async Function SearchRelatedTopicsAsync(topic As String, Optional limit As Integer = 10) As Task(Of List(Of JObject))
        Try
            Dim payload = New JObject From {
                {"topic", topic},
                {"limit", limit},
                {"include_premium_content", True}
            }

            Dim response = Await PostJsonAsync("/kb/search", payload)

            Dim results = response("results")?.ToObject(Of List(Of JObject))() ?? New List(Of JObject)()

            Console.WriteLine($"📚 Found {results.Count} related topics for '{topic}'")
            Return results

        Catch ex As Exception
            Console.WriteLine($"❌ KB search failed: {ex.Message}")
            Return New List(Of JObject)()
        End Try
    End Function

    ''' <summary>
    ''' Generate FAQ content for website/documentation
    ''' '''
    Public Async Function GenerateFAQContentAsync(category As String, Optional targetAudience As String = "general") As Task(Of List(Of JObject))
        Try
            Dim payload = New JObject From {
                {"category", category},
                {"target_audience", targetAudience},
                {"format", "faq"},
                {"include_seo_keywords", True},
                {"monetization_angle", True}
            }

            Dim response = Await PostJsonAsync("/kb/generate-faq", payload)

            Return response("faq_items")?.ToObject(Of List(Of JObject))() ?? New List(Of JObject)()

        Catch ex As Exception
            Console.WriteLine($"❌ FAQ generation failed: {ex.Message}")
            Return New List(Of JObject)()
        End Try
    End Function

    ''' <summary>
    ''' Get contextual help for EQ12 features
    ''' '''
    Public Async Function GetFeatureHelpAsync(featureName As String, userLevel As String) As Task(Of String)
        Try
            Dim question = $"How do I use the {featureName} feature in EQ12? I'm a {userLevel} user."

            Dim payload = New JObject From {
                {"question", question},
                {"context", "technical_support"},
                {"feature", featureName},
                {"user_level", userLevel},
                {"include_screenshots", False},
                {"include_examples", True}
            }

            Dim response = Await PostJsonAsync("/kb/feature-help", payload)
            Return response("answer")?.ToString() ?? ""

        Catch ex As Exception
            Console.WriteLine($"❌ Feature help failed: {ex.Message}")
            Return "Feature help is temporarily unavailable. Please check our documentation or contact support."
        End Try
    End Function

    ''' <summary>
    ''' Get Knowledge Base health and statistics
    ''' '''
    Public Async Function GetSystemHealthAsync() As Task(Of JObject)
        Try
            Return Await GetJsonAsync("/kb/health")
        Catch ex As Exception
            Console.WriteLine($"❌ KB health check failed: {ex.Message}")
            Return New JObject From {{"status", "error"}, {"message", ex.Message}}
        End Try
    End Function

    ''' <summary>
    ''' Update knowledge base with new content (admin function)
    ''' '''
    Public Async Function UpdateKnowledgeAsync(category As String, content As JObject) As Task(Of Boolean)
        Try
            Dim payload = New JObject From {
                {"category", category},
                {"content", content},
                {"timestamp", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")},
                {"version", "1.0"}
            }

            Dim response = Await PostJsonAsync("/kb/update", payload)

            If response("success")?.ToObject(Of Boolean)() = True Then
                Console.WriteLine($"✅ Knowledge base updated: {category}")
                Return True
            Else
                Console.WriteLine($"⚠️ KB update failed: {response("error")}")
                Return False
            End If

        Catch ex As Exception
            Console.WriteLine($"❌ KB update failed: {ex.Message}")
            Return False
        End Try
    End Function

    ' Helper methods
    Private Async Function PostJsonAsync(endpoint As String, payload As JObject) As Task(Of JObject)
        Try
            Dim content = New StringContent(payload.ToString(), Encoding.UTF8, "application/json")
            Dim response = Await _httpClient.PostAsync($"{_baseUrl}{endpoint}", content)

            If Not response.IsSuccessStatusCode Then
                Throw New HttpRequestException($"HTTP {response.StatusCode}: {response.ReasonPhrase}")
            End If

            Dim responseText = Await response.Content.ReadAsStringAsync()
            Return JObject.Parse(responseText)

        Catch ex As Exception
            Throw New Exception($"KB API call failed: {ex.Message}", ex)
        End Try
    End Function

    Private Async Function GetJsonAsync(endpoint As String) As Task(Of JObject)
        Try
            Dim response = Await _httpClient.GetAsync($"{_baseUrl}{endpoint}")

            If Not response.IsSuccessStatusCode Then
                Throw New HttpRequestException($"HTTP {response.StatusCode}: {response.ReasonPhrase}")
            End If

            Dim responseText = Await response.Content.ReadAsStringAsync()
            Return JObject.Parse(responseText)

        Catch ex As Exception
            Throw New Exception($"KB API call failed: {ex.Message}", ex)
        End Try
    End Function

    ''' <summary>
    ''' Log KB queries for analytics and monetization tracking
    ''' '''
    Private Sub LogKBQuery(question As String, context As String, status As String)
        Try
            Dim logEntry = New JObject From {
                {"timestamp", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")},
                {"service", "knowledge_base"},
                {"question", question},
                {"context", context},
                {"status", status}
            }

            Console.WriteLine($"📚 KB Query: {context} - {status}")

        Catch ex As Exception
            ' Silent fail for logging
        End Try
    End Sub

    ''' <summary>
    ''' Log premium content triggers for monetization
    ''' '''
    Private Sub LogPremiumTrigger(question As String, context As String)
        Try
            Dim logEntry = New JObject From {
                {"timestamp", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")},
                {"event", "premium_trigger"},
                {"question", question},
                {"context", context},
                {"source", "knowledge_base"}
            }

            Console.WriteLine($"💎 Premium trigger: {context}")

        Catch ex As Exception
            ' Silent fail for logging
        End Try
    End Sub

    Protected Overrides Sub Finalize()
        _httpClient?.Dispose()
        MyBase.Finalize()
    End Sub
End Class
