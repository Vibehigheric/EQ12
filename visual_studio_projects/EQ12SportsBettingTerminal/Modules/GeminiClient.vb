Imports System.Threading.Tasks
Imports System.Net.Http
Imports System.Text
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.Collections.Generic

''' <summary>
''' Google Gemini API Client for EQ12
''' Handles AI-powered analysis, content generation, and insights
''' '''
Public Class GeminiClient
    Private ReadOnly _httpClient As HttpClient
    Private ReadOnly _apiKey As String
    Private ReadOnly _baseUrl As String = "https://generativelanguage.googleapis.com/v1beta/models/"

    ' Gemini models available
    Private Const GEMINI_PRO As String = "gemini-1.5-pro"
    Private Const GEMINI_FLASH As String = "gemini-1.5-flash"

    Public Sub New(apiKey As String)
        _apiKey = apiKey
        _httpClient = New HttpClient()
        _httpClient.Timeout = TimeSpan.FromMinutes(2)
    End Sub

    ''' <summary>
    ''' Generate AI analysis for sports betting data
    ''' '''
    Public Async Function GenerateBettingAnalysisAsync(prompt As String, Optional model As String = GEMINI_PRO) As Task(Of String)
        Try
            Dim sportsPrompt = $"
                You are an expert sports betting analyst for EQ12. Analyze the following data and provide insights:

                {prompt}

                Focus on:
                1. Key betting opportunities and edges
                2. Risk assessment and bankroll management recommendations
                3. Market inefficiencies to exploit
                4. Injury impacts on betting lines
                5. Sharp vs public money movement

                Provide actionable insights in a structured format with confidence levels.
            "

            Return Await GenerateContentAsync(sportsPrompt, model)

        Catch ex As Exception
            Console.WriteLine($"❌ Betting analysis generation failed: {ex.Message}")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Generate monetization content (emails, blog posts, affiliate content)
    ''' '''
    Public Async Function GenerateMonetizationContentAsync(contentType As String, data As String, Optional model As String = GEMINI_FLASH) As Task(Of String)
        Try
            Dim marketingPrompt As String

            Select Case contentType.ToLower()
                Case "email"
                    marketingPrompt = $"
                        Create a compelling email for EQ12 premium subscribers about this betting opportunity:

                        {data}

                        Include:
                        - Attention-grabbing subject line
                        - Clear value proposition
                        - Call-to-action for premium services
                        - Professional sports betting language
                        - Urgency without being pushy
                    "

                Case "blog"
                    marketingPrompt = $"
                        Write an engaging blog post about this sports betting analysis:

                        {data}

                        Include:
                        - SEO-optimized title
                        - Educational content for beginners
                        - Advanced strategies for experts
                        - Affiliate link placeholders [AFFILIATE_LINK]
                        - Social media sharing hooks
                    "

                Case "affiliate"
                    marketingPrompt = $"
                        Create affiliate marketing content for this betting opportunity:

                        {data}

                        Include:
                        - Compelling headline
                        - Social proof elements
                        - Clear benefit statements
                        - Strong call-to-action
                        - Compliance-friendly language
                    "

                Case Else
                    marketingPrompt = $"
                        Create marketing content ({contentType}) for this betting data:

                        {data}

                        Make it compelling, professional, and conversion-focused.
                    "
            End Select

            Return Await GenerateContentAsync(marketingPrompt, model)

        Catch ex As Exception
            Console.WriteLine($"❌ Monetization content generation failed: {ex.Message}")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Generate injury impact analysis
    ''' '''
    Public Async Function GenerateInjuryAnalysisAsync(injuryData As String, Optional model As String = GEMINI_PRO) As Task(Of String)
        Try
            Dim injuryPrompt = $"
                Analyze these injury reports and their betting implications:

                {injuryData}

                Provide:
                1. Impact assessment (1-5 scale) for each injury
                2. Line movement predictions
                3. Betting opportunities created by public overreaction
                4. Contrarian betting angles
                5. Risk factors for existing positions

                Focus on actionable betting insights with confidence levels.
            "

            Return Await GenerateContentAsync(injuryPrompt, model)

        Catch ex As Exception
            Console.WriteLine($"❌ Injury analysis generation failed: {ex.Message}")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Generate market movement analysis
    ''' '''
    Public Async Function GenerateMarketAnalysisAsync(marketData As String, Optional model As String = GEMINI_PRO) As Task(Of String)
        Try
            Dim marketPrompt = $"
                Analyze these betting market movements:

                {marketData}

                Identify:
                1. Reverse line moves (RLM) and their significance
                2. Steam moves and sharp money indicators
                3. Public vs sharp money conflicts
                4. Closing line value opportunities
                5. Contrarian betting spots

                Provide specific betting recommendations with confidence levels.
            "

            Return Await GenerateContentAsync(marketPrompt, model)

        Catch ex As Exception
            Console.WriteLine($"❌ Market analysis generation failed: {ex.Message}")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Core method to generate content using Gemini API
    ''' '''
    Private Async Function GenerateContentAsync(prompt As String, model As String) As Task(Of String)
        Try
            Dim requestBody = JsonConvert.SerializeObject(New With {
                .contents = New Object() {
                    New With {
                        .parts = New Object() {
                            New With {.text = prompt}
                        }
                    }
                },
                .generationConfig = New With {
                    .temperature = 0.7,
                    .maxOutputTokens = 2048,
                    .topP = 0.95,
                    .topK = 40
                }
            })

            Dim url = $"{_baseUrl}{model}:generateContent?key={_apiKey}"

            Using content = New StringContent(requestBody, Encoding.UTF8, "application/json")
                Dim response = Await _httpClient.PostAsync(url, content)
                Dim responseBody = Await response.Content.ReadAsStringAsync()

                If response.IsSuccessStatusCode Then
                    Dim jsonResponse = JObject.Parse(responseBody)
                    Dim generatedText = jsonResponse("candidates")(0)("content")("parts")(0)("text").ToString()

                    Console.WriteLine($"✅ Generated {generatedText.Length} characters using {model}")
                    Return generatedText
                Else
                    Throw New Exception($"API request failed: {response.StatusCode} - {responseBody}")
                End If
            End Using

        Catch ex As Exception
            Console.WriteLine($"❌ Gemini API call failed: {ex.Message}")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Generate comprehensive betting report combining all analyses
    ''' '''
    Public Async Function GenerateComprehensiveReportAsync(metricsData As String, injuryData As String, marketData As String) As Task(Of String)
        Try
            Dim comprehensivePrompt = $"
                Create a comprehensive EQ12 sports betting report combining:

                METRICS DATA:
                {metricsData}

                INJURY DATA:
                {injuryData}

                MARKET DATA:
                {marketData}

                Generate a professional report with:
                1. Executive Summary with top 3 opportunities
                2. Detailed Analysis by sport/game
                3. Risk Assessment and Bankroll Recommendations
                4. Injury Impact Analysis
                5. Market Movement Insights
                6. Action Items with confidence levels
                7. Monetization opportunities for premium subscribers

                Format as HTML with proper sections and styling.
            "

            Return Await GenerateContentAsync(comprehensivePrompt, GEMINI_PRO)

        Catch ex As Exception
            Console.WriteLine($"❌ Comprehensive report generation failed: {ex.Message}")
            Throw
        End Try
    End Function

    Protected Overrides Sub Finalize()
        _httpClient?.Dispose()
        MyBase.Finalize()
    End Sub
End Class
