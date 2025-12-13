Imports System.Net.Http
Imports System.Text
Imports System.Threading.Tasks
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.Collections.Generic

''' <summary>
''' RAG (Retrieval-Augmented Generation) Client for EQ12
''' Integrates with Jump Start Solution: Generative AI RAG with Cloud SQL
''' Provides contextual betting insights by querying knowledge base with vector embeddings
''' '''
Public Class RAGClient
    Private ReadOnly _baseUrl As String
    Private ReadOnly _httpClient As HttpClient
    Private ReadOnly _gcpAuth As GCPAuth

    Public Sub New(baseUrl As String, gcpAuth As GCPAuth)
        _baseUrl = baseUrl.TrimEnd("/"c)
        _httpClient = New HttpClient()
        _gcpAuth = gcpAuth

        ' Set authentication headers
        SetupAuthentication()
    End Sub

    ''' <summary>
    ''' Setup OAuth authentication for RAG service calls
    ''' '''
    Private Async Sub SetupAuthentication()
        Try
            Dim token = Await _gcpAuth.GetAccessTokenAsync()
            _httpClient.DefaultRequestHeaders.Clear()
            _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {token}")
            _httpClient.DefaultRequestHeaders.Add("User-Agent", "EQ12-RAG-Client/1.0")

        Catch ex As Exception
            Console.WriteLine($"⚠️ RAG authentication setup failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Query RAG system for betting insights with context
    ''' '''
    Public Async Function QueryBettingInsightsAsync(question As String, Optional k As Integer = 6, Optional context As String = "betting") As Task(Of JObject)
        Try
            Dim payload = New JObject From {
                {"question", question},
                {"k", k},
                {"context", context},
                {"include_sources", True},
                {"min_relevance_score", 0.7}
            }

            Dim response = Await PostJsonAsync("/rag/query", payload)

            ' Log successful query for monetization tracking
            LogRAGQuery(question, context, "success")

            Return response

        Catch ex As Exception
            Console.WriteLine($"❌ RAG query failed: {ex.Message}")
            LogRAGQuery(question, context, "error")
            Return New JObject From {{"error", ex.Message}}
        End Try
    End Function

    ''' <summary>
    ''' Query historical line movements and market patterns
    ''' '''
    Public Async Function QueryLineMovementsAsync(sport As String, team As String, Optional timeframe As String = "30d") As Task(Of JObject)
        Try
            Dim question = $"Show me historical line movements for {team} in {sport} over the last {timeframe}. Include reverse line moves and steam patterns."

            Dim payload = New JObject From {
                {"question", question},
                {"context", "line_movements"},
                {"filters", New JObject From {
                    {"sport", sport},
                    {"team", team},
                    {"timeframe", timeframe}
                }},
                {"k", 10}
            }

            Return Await PostJsonAsync("/rag/line-movements", payload)

        Catch ex As Exception
            Console.WriteLine($"❌ Line movements query failed: {ex.Message}")
            Return New JObject From {{"error", ex.Message}}
        End Try
    End Function

    ''' <summary>
    ''' Query injury impacts and situational factors
    ''' '''
    Public Async Function QueryInjuryImpactsAsync(sport As String, position As String, Optional severity As Integer = 3) As Task(Of JObject)
        Try
            Dim question = $"What are the betting implications when a {position} gets injured in {sport}? Focus on line movements and public perception."

            Dim payload = New JObject From {
                {"question", question},
                {"context", "injury_analysis"},
                {"filters", New JObject From {
                    {"sport", sport},
                    {"position", position},
                    {"min_severity", severity}
                }},
                {"k", 8}
            }

            Return Await PostJsonAsync("/rag/injury-impacts", payload)

        Catch ex As Exception
            Console.WriteLine($"❌ Injury impacts query failed: {ex.Message}")
            Return New JObject From {{"error", ex.Message}}
        End Try
    End Function

    ''' <summary>
    ''' Embed new content for future RAG queries
    ''' '''
    Public Async Function EmbedContentAsync(content As String, contentType As String, metadata As JObject) As Task(Of Boolean)
        Try
            Dim payload = New JObject From {
                {"content", content},
                {"content_type", contentType},
                {"metadata", metadata},
                {"timestamp", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")}
            }

            Dim response = Await PostJsonAsync("/rag/embed", payload)

            If response("success")?.ToObject(Of Boolean)() = True Then
                Console.WriteLine($"✅ Embedded {contentType} content successfully")
                Return True
            Else
                Console.WriteLine($"⚠️ Content embedding failed: {response("error")}")
                Return False
            End If

        Catch ex As Exception
            Console.WriteLine($"❌ Content embedding failed: {ex.Message}")
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Generate monetization-focused betting narrative using RAG
    ''' '''
    Public Async Function GenerateMonetizationNarrativeAsync(topic As String, targetAudience As String) As Task(Of String)
        Try
            Dim question = $"Generate a compelling betting narrative about {topic} for {targetAudience}. Include actionable insights, risk assessment, and call-to-action for premium services."

            Dim payload = New JObject From {
                {"question", question},
                {"context", "monetization"},
                {"target_audience", targetAudience},
                {"include_cta", True},
                {"tone", "professional_persuasive"},
                {"k", 5}
            }

            Dim response = Await PostJsonAsync("/rag/generate-narrative", payload)

            Return response("narrative")?.ToString() ?? ""

        Catch ex As Exception
            Console.WriteLine($"❌ Monetization narrative generation failed: {ex.Message}")
            Return ""
        End Try
    End Function

    ''' <summary>
    ''' Get RAG system health and statistics
    ''' '''
    Public Async Function GetSystemHealthAsync() As Task(Of JObject)
        Try
            Return Await GetJsonAsync("/rag/health")
        Catch ex As Exception
            Console.WriteLine($"❌ RAG health check failed: {ex.Message}")
            Return New JObject From {{"status", "error"}, {"message", ex.Message}}
        End Try
    End Function

    ' Helper methods for HTTP operations
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
            Throw New Exception($"RAG API call failed: {ex.Message}", ex)
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
            Throw New Exception($"RAG API call failed: {ex.Message}", ex)
        End Try
    End Function

    ''' <summary>
    ''' Log RAG queries for monetization analytics
    ''' '''
    Private Sub LogRAGQuery(question As String, context As String, status As String)
        Try
            ' This would integrate with your existing logging system
            Dim logEntry = New JObject From {
                {"timestamp", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")},
                {"service", "rag"},
                {"question", question},
                {"context", context},
                {"status", status}
            }

            ' Log to file or database for analytics
            Console.WriteLine($"📊 RAG Query: {context} - {status}")

        Catch ex As Exception
            ' Silent fail for logging
        End Try
    End Sub

    Protected Overrides Sub Finalize()
        _httpClient?.Dispose()
        MyBase.Finalize()
    End Sub
End Class
