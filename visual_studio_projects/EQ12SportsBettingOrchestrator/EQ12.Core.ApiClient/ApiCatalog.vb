Option Strict On
Option Explicit On

Namespace EQ12.Core.ApiClient

    ''' <summary>
    ''' Centralized catalog of free/freemium APIs for EQ12 stack
    ''' Categories: sports, odds, ml, weather, misc
    ''' </summary>
    Public Class ApiCatalog

        Private ReadOnly _apis As List(Of ApiInfo)

        Public Sub New()
            _apis = New List(Of ApiInfo)()

            ' ================================================================
            ' SPORTS / ODDS APIS
            ' ================================================================

            _apis.Add(New ApiInfo() With {
                .Name = "The Odds API",
                .Category = "odds",
                .BaseUrl = "https://api.the-odds-api.com",
                .FreeTierDescription = "500 requests/month free tier",
                .Notes = "Primary odds source - MLB, NBA, NFL, CFB, Soccer, UFC. Used in 100-source registry.",
                .AuthType = "API Key (querystring)",
                .EnvironmentVariableName = "ODDS_API_KEY",
                .Priority = 1,
                .Reliability = 0.98,
                .LatencyMs = 180,
                .Enabled = True
            })

            _apis.Add(New ApiInfo() With {
                .Name = "API-SPORTS (Football)",
                .Category = "sports",
                .BaseUrl = "https://v3.football.api-sports.io",
                .FreeTierDescription = "100 requests/day forever free",
                .Notes = "Stats + fixtures for football/soccer. Also covers odds for some leagues.",
                .AuthType = "API Key (header: x-rapidapi-key or x-apisports-key)",
                .EnvironmentVariableName = "APISPORTS_FOOTBALL_KEY",
                .Priority = 2,
                .Reliability = 0.95,
                .LatencyMs = 220,
                .Enabled = True
            })

            _apis.Add(New ApiInfo() With {
                .Name = "API-SPORTS (Basketball)",
                .Category = "sports",
                .BaseUrl = "https://v1.basketball.api-sports.io",
                .FreeTierDescription = "100 requests/day forever free",
                .Notes = "NBA stats, fixtures, standings, player data.",
                .AuthType = "API Key (header: x-apisports-key)",
                .EnvironmentVariableName = "APISPORTS_BASKETBALL_KEY",
                .Priority = 2,
                .Reliability = 0.95,
                .LatencyMs = 200,
                .Enabled = True
            })

            _apis.Add(New ApiInfo() With {
                .Name = "API-SPORTS (Baseball)",
                .Category = "sports",
                .BaseUrl = "https://v1.baseball.api-sports.io",
                .FreeTierDescription = "100 requests/day forever free",
                .Notes = "MLB stats, fixtures, player data, standings.",
                .AuthType = "API Key (header: x-apisports-key)",
                .EnvironmentVariableName = "APISPORTS_BASEBALL_KEY",
                .Priority = 2,
                .Reliability = 0.95,
                .LatencyMs = 210,
                .Enabled = True
            })

            _apis.Add(New ApiInfo() With {
                .Name = "Sports Game Odds",
                .Category = "odds",
                .BaseUrl = "https://api.sportsgameodds.com",
                .FreeTierDescription = "Free tier with reasonable limits",
                .Notes = "Backup odds source. Good for cross-validation.",
                .AuthType = "API Key",
                .EnvironmentVariableName = "SPORTS_GAME_ODDS_KEY",
                .Priority = 3,
                .Reliability = 0.92,
                .LatencyMs = 250,
                .Enabled = False
            })

            _apis.Add(New ApiInfo() With {
                .Name = "ESPN Hidden API",
                .Category = "sports",
                .BaseUrl = "https://site.api.espn.com/apis/site/v2/sports",
                .FreeTierDescription = "Unofficial but public - no auth required",
                .Notes = "Free stats, scores, schedules for MLB/NBA/NFL/CFB. No official rate limit.",
                .AuthType = "None",
                .EnvironmentVariableName = "",
                .Priority = 2,
                .Reliability = 0.97,
                .LatencyMs = 150,
                .Enabled = True
            })

            ' ================================================================
            ' ML / LLM / AI MODELS
            ' ================================================================

            _apis.Add(New ApiInfo() With {
                .Name = "Hugging Face Hub (Metadata)",
                .Category = "ml",
                .BaseUrl = "https://huggingface.co/api",
                .FreeTierDescription = "Free access to public models/datasets metadata",
                .Notes = "Discover models, datasets, spaces. Not for heavy inference.",
                .AuthType = "Optional Bearer token",
                .EnvironmentVariableName = "HF_API_TOKEN",
                .Priority = 1,
                .Reliability = 0.99,
                .LatencyMs = 120,
                .Enabled = True
            })

            _apis.Add(New ApiInfo() With {
                .Name = "Hugging Face Inference (Serverless)",
                .Category = "ml",
                .BaseUrl = "https://api-inference.huggingface.co",
                .FreeTierDescription = "Free tier with rate limits, paid for higher usage",
                .Notes = "Use for embeddings, classification, small LLMs. Rate-limited.",
                .AuthType = "Bearer token",
                .EnvironmentVariableName = "HF_API_TOKEN",
                .Priority = 1,
                .Reliability = 0.96,
                .LatencyMs = 800,
                .Enabled = True
            })

            _apis.Add(New ApiInfo() With {
                .Name = "OpenRouter",
                .Category = "ml",
                .BaseUrl = "https://openrouter.ai/api/v1",
                .FreeTierDescription = "FREE tier available, multiple models",
                .Notes = "Multi-provider LLM gateway. Already integrated in EQ12 prompt execution.",
                .AuthType = "Bearer token",
                .EnvironmentVariableName = "OPENROUTER_API_KEY",
                .Priority = 1,
                .Reliability = 0.98,
                .LatencyMs = 2000,
                .Enabled = True
            })

            _apis.Add(New ApiInfo() With {
                .Name = "Groq",
                .Category = "ml",
                .BaseUrl = "https://api.groq.com/openai/v1",
                .FreeTierDescription = "FREE unlimited tier (500 tokens/sec)",
                .Notes = "Ultra-fast LLM inference. Already used as fallback in prompt execution.",
                .AuthType = "Bearer token",
                .EnvironmentVariableName = "GROQ_API_KEY",
                .Priority = 1,
                .Reliability = 0.97,
                .LatencyMs = 500,
                .Enabled = True
            })

            _apis.Add(New ApiInfo() With {
                .Name = "Google AI (Gemini)",
                .Category = "ml",
                .BaseUrl = "https://generativelanguage.googleapis.com/v1beta",
                .FreeTierDescription = "Free tier with generous limits",
                .Notes = "Gemini models for text generation, embeddings.",
                .AuthType = "API Key",
                .EnvironmentVariableName = "GOOGLE_AI_API_KEY",
                .Priority = 2,
                .Reliability = 0.98,
                .LatencyMs = 1200,
                .Enabled = True
            })

            ' ================================================================
            ' WEATHER (for game conditions)
            ' ================================================================

            _apis.Add(New ApiInfo() With {
                .Name = "OpenWeatherMap",
                .Category = "weather",
                .BaseUrl = "https://api.openweathermap.org",
                .FreeTierDescription = "1000 calls/day free tier",
                .Notes = "Game-day weather impacts. Essential for outdoor sports (MLB, NFL, soccer).",
                .AuthType = "API Key",
                .EnvironmentVariableName = "OPENWEATHER_API_KEY",
                .Priority = 1,
                .Reliability = 0.97,
                .LatencyMs = 180,
                .Enabled = True
            })

            _apis.Add(New ApiInfo() With {
                .Name = "Tomorrow.io",
                .Category = "weather",
                .BaseUrl = "https://api.tomorrow.io",
                .FreeTierDescription = "Free developer tier with hourly/daily limits",
                .Notes = "Advanced weather metrics - wind, rain, temperature. Good for baseball.",
                .AuthType = "API Key",
                .EnvironmentVariableName = "TOMORROW_API_KEY",
                .Priority = 2,
                .Reliability = 0.95,
                .LatencyMs = 200,
                .Enabled = False
            })

            _apis.Add(New ApiInfo() With {
                .Name = "WeatherAPI.com",
                .Category = "weather",
                .BaseUrl = "https://api.weatherapi.com/v1",
                .FreeTierDescription = "1M calls/month free tier",
                .Notes = "Generous free tier. Forecast, current, historical weather.",
                .AuthType = "API Key",
                .EnvironmentVariableName = "WEATHERAPI_KEY",
                .Priority = 1,
                .Reliability = 0.96,
                .LatencyMs = 170,
                .Enabled = True
            })

            ' ================================================================
            ' PROPS / PLAYER PROPS
            ' ================================================================

            _apis.Add(New ApiInfo() With {
                .Name = "PrizePicks (Unofficial)",
                .Category = "props",
                .BaseUrl = "https://api.prizepicks.com",
                .FreeTierDescription = "Public API - no auth required",
                .Notes = "Player props lines. Unofficial but stable. In 100-source registry.",
                .AuthType = "None",
                .EnvironmentVariableName = "",
                .Priority = 1,
                .Reliability = 0.94,
                .LatencyMs = 220,
                .Enabled = True
            })

            _apis.Add(New ApiInfo() With {
                .Name = "Underdog Fantasy (Unofficial)",
                .Category = "props",
                .BaseUrl = "https://api.underdogfantasy.com",
                .FreeTierDescription = "Public API - no auth required",
                .Notes = "Player props, pick'em lines. Unofficial but reliable.",
                .AuthType = "None",
                .EnvironmentVariableName = "",
                .Priority = 1,
                .Reliability = 0.93,
                .LatencyMs = 240,
                .Enabled = True
            })

            ' ================================================================
            ' FINANCE / TRADING (SEC 13F integration)
            ' ================================================================

            _apis.Add(New ApiInfo() With {
                .Name = "SEC EDGAR API",
                .Category = "finance",
                .BaseUrl = "https://data.sec.gov",
                .FreeTierDescription = "Free - SEC public data",
                .Notes = "13F filings, hedge fund holdings. Already integrated (eq12_sec_13f_scraper.py).",
                .AuthType = "User-Agent required",
                .EnvironmentVariableName = "",
                .Priority = 1,
                .Reliability = 0.99,
                .LatencyMs = 300,
                .Enabled = True
            })

            _apis.Add(New ApiInfo() With {
                .Name = "Alpha Vantage",
                .Category = "finance",
                .BaseUrl = "https://www.alphavantage.co",
                .FreeTierDescription = "500 requests/day free tier",
                .Notes = "Stock quotes, forex, crypto, technical indicators.",
                .AuthType = "API Key",
                .EnvironmentVariableName = "ALPHA_VANTAGE_KEY",
                .Priority = 2,
                .Reliability = 0.96,
                .LatencyMs = 250,
                .Enabled = False
            })

            ' ================================================================
            ' NEWS / SENTIMENT
            ' ================================================================

            _apis.Add(New ApiInfo() With {
                .Name = "NewsAPI.org",
                .Category = "news",
                .BaseUrl = "https://newsapi.org/v2",
                .FreeTierDescription = "100 requests/day free tier",
                .Notes = "Sports news, injury reports, sentiment analysis sources.",
                .AuthType = "API Key",
                .EnvironmentVariableName = "NEWS_API_KEY",
                .Priority = 2,
                .Reliability = 0.95,
                .LatencyMs = 200,
                .Enabled = False
            })

            ' ================================================================
            ' MISC / SUPPORTIVE
            ' ================================================================

            _apis.Add(New ApiInfo() With {
                .Name = "GitHub API",
                .Category = "misc",
                .BaseUrl = "https://api.github.com",
                .FreeTierDescription = "5000 requests/hour authenticated, 60/hour unauthenticated",
                .Notes = "Access repos, workflows, releases. Used for automation.",
                .AuthType = "Bearer token (GitHub PAT)",
                .EnvironmentVariableName = "GITHUB_TOKEN",
                .Priority = 1,
                .Reliability = 0.99,
                .LatencyMs = 120,
                .Enabled = True
            })

            _apis.Add(New ApiInfo() With {
                .Name = "Telegram Bot API",
                .Category = "misc",
                .BaseUrl = "https://api.telegram.org",
                .FreeTierDescription = "Free - unlimited messages",
                .Notes = "Send betting alerts, parlay picks, system notifications.",
                .AuthType = "Bot token",
                .EnvironmentVariableName = "TELEGRAM_BOT_TOKEN",
                .Priority = 1,
                .Reliability = 0.98,
                .LatencyMs = 150,
                .Enabled = True
            })

        End Sub

        ''' <summary>
        ''' Get all registered APIs
        ''' </summary>
        Public Function GetAll() As List(Of ApiInfo)
            Return _apis.ToList()
        End Function

        ''' <summary>
        ''' Get APIs by category (sports, odds, ml, weather, props, finance, news, misc)
        ''' </summary>
        Public Function GetByCategory(category As String) As List(Of ApiInfo)
            If String.IsNullOrWhiteSpace(category) Then
                Return New List(Of ApiInfo)()
            End If
            Return _apis.Where(Function(a) a.Category.Equals(category, StringComparison.OrdinalIgnoreCase)).ToList()
        End Function

        ''' <summary>
        ''' Get only enabled APIs
        ''' </summary>
        Public Function GetEnabled() As List(Of ApiInfo)
            Return _apis.Where(Function(a) a.Enabled).ToList()
        End Function

        ''' <summary>
        ''' Get APIs sorted by priority (1 = highest)
        ''' </summary>
        Public Function GetByPriority() As List(Of ApiInfo)
            Return _apis.OrderBy(Function(a) a.Priority).ToList()
        End Function

        ''' <summary>
        ''' Get APIs sorted by reliability (highest first)
        ''' </summary>
        Public Function GetByReliability() As List(Of ApiInfo)
            Return _apis.OrderByDescending(Function(a) a.Reliability).ToList()
        End Function

        ''' <summary>
        ''' Get fastest APIs (lowest latency)
        ''' </summary>
        Public Function GetByLatency() As List(Of ApiInfo)
            Return _apis.OrderBy(Function(a) a.LatencyMs).ToList()
        End Function

        ''' <summary>
        ''' Find API by name
        ''' </summary>
        Public Function FindByName(name As String) As ApiInfo
            Return _apis.FirstOrDefault(Function(a) a.Name.Equals(name, StringComparison.OrdinalIgnoreCase))
        End Function

        ''' <summary>
        ''' Get recommendation for a use case
        ''' </summary>
        Public Function GetRecommendation(useCase As String) As List(Of ApiInfo)
            Select Case useCase.ToLowerInvariant()
                Case "odds"
                    Return GetByCategory("odds").Where(Function(a) a.Enabled).OrderBy(Function(a) a.Priority).ToList()
                Case "weather"
                    Return GetByCategory("weather").Where(Function(a) a.Enabled).OrderBy(Function(a) a.Priority).ToList()
                Case "ml", "llm", "ai"
                    Return GetByCategory("ml").Where(Function(a) a.Enabled).OrderBy(Function(a) a.Priority).ToList()
                Case "props"
                    Return GetByCategory("props").Where(Function(a) a.Enabled).OrderBy(Function(a) a.Priority).ToList()
                Case Else
                    Return New List(Of ApiInfo)()
            End Select
        End Function

    End Class

    ''' <summary>
    ''' Extended API info model with EQ12-specific metrics
    ''' </summary>
    Public Class ApiInfo
        Public Property Name As String
        Public Property Category As String          ' sports, odds, ml, weather, props, finance, news, misc
        Public Property BaseUrl As String
        Public Property FreeTierDescription As String
        Public Property Notes As String
        Public Property AuthType As String          ' None, API Key, Bearer, Custom
        Public Property EnvironmentVariableName As String
        
        ' EQ12-specific metrics
        Public Property Priority As Integer         ' 1 = highest priority
        Public Property Reliability As Double       ' 0.0-1.0 (percentage as decimal)
        Public Property LatencyMs As Integer        ' Average response time in milliseconds
        Public Property Enabled As Boolean          ' Whether API is currently active
        
        ' Runtime tracking (populated by dashboard)
        Public Property LastChecked As DateTime?
        Public Property IsHealthy As Boolean = True
        Public Property ErrorCount As Integer = 0
        Public Property SuccessCount As Integer = 0
        
        Public ReadOnly Property SuccessRate As Double
            Get
                Dim total = SuccessCount + ErrorCount
                If total = 0 Then Return 0.0
                Return SuccessCount / total
            End Get
        End Property
        
        Public ReadOnly Property DisplayName As String
            Get
                Return $"{Name} ({Category})"
            End Get
        End Property
    End Class

End Namespace
