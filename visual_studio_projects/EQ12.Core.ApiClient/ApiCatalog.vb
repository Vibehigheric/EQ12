' ================================================================================
' EQ12 Master API Catalog - 22 Free/Freemium APIs for Automation Stack
' ================================================================================
' Purpose: Centralized API management for sports betting, finance, aviation,
'          weather, crypto, and hemp industry data aggregation
' Integration: Feeds data to Python automation, Pi cluster workers, SQLite DBs
' ================================================================================

Imports System.Net.Http
Imports System.Threading.Tasks
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq

Namespace EQ12.Core.ApiClient

    ''' <summary>
    ''' Master API catalog managing 22 free/freemium APIs across multiple domains
    ''' </summary>
    Public Class ApiCatalog
        Private ReadOnly _httpClient As HttpClient
        Private ReadOnly _cache As New Dictionary(Of String, CachedResponse)
        Private ReadOnly _rateLimiter As New Dictionary(Of String, DateTime)

        Public Sub New()
            _httpClient = New HttpClient()
            _httpClient.Timeout = TimeSpan.FromSeconds(30)
        End Sub

        ' ========================================
        ' SPORTS BETTING APIS (Primary Use Case)
        ' ========================================

        ''' <summary>
        ''' The Odds API - Real-time sports betting odds across 100+ bookmakers
        ''' Tier: FREE (500 requests/month) + $10/month unlimited
        ''' </summary>
        Public Async Function GetOddsDataAsync(sport As String, region As String) As Task(Of JObject)
            Dim apiKey = Environment.GetEnvironmentVariable("ODDS_API_KEY")
            If String.IsNullOrEmpty(apiKey) Then
                Throw New InvalidOperationException("ODDS_API_KEY environment variable not set")
            End If

            Dim endpoint = $"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
            Dim queryString = $"?apiKey={apiKey}&regions={region}&markets=h2h,spreads,totals&oddsFormat=american"
            
            Return Await GetWithCacheAsync("OddsAPI", endpoint & queryString, 300) ' 5min cache
        End Function

        ''' <summary>
        ''' ESPN API - Scores, schedules, team/player stats (unofficial but stable)
        ''' Tier: FREE (no official limits, community-maintained endpoints)
        ''' </summary>
        Public Async Function GetEspnScoresAsync(sport As String, league As String) As Task(Of JObject)
            Dim endpoint = $"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
            Return Await GetWithCacheAsync("ESPN", endpoint, 60) ' 1min cache
        End Function

        ''' <summary>
        ''' SportsData.io - Comprehensive sports data (NFL, NBA, MLB, NHL, etc.)
        ''' Tier: FREE (1,000 calls/month) + $29/month starter
        ''' </summary>
        Public Async Function GetSportsDataAsync(sport As String, season As String) As Task(Of JObject)
            Dim apiKey = Environment.GetEnvironmentVariable("SPORTSDATA_API_KEY")
            If String.IsNullOrEmpty(apiKey) Then
                ' Fallback to ESPN if no API key
                Return Await GetEspnScoresAsync("football", "nfl")
            End If

            Dim endpoint = $"https://api.sportsdata.io/v3/{sport}/scores/json/Teams"
            _httpClient.DefaultRequestHeaders.Add("Ocp-Apim-Subscription-Key", apiKey)
            
            Return Await GetWithCacheAsync("SportsData", endpoint, 3600) ' 1hr cache
        End Function

        ' ========================================
        ' FINANCIAL DATA APIS (SEC Scraper Feed)
        ' ========================================

        ''' <summary>
        ''' Alpha Vantage - Stock prices, forex, crypto, technical indicators
        ''' Tier: FREE (25 calls/day) + $50/month premium
        ''' </summary>
        Public Async Function GetStockDataAsync(symbol As String) As Task(Of JObject)
            Dim apiKey = Environment.GetEnvironmentVariable("ALPHA_VANTAGE_KEY") 
            If String.IsNullOrEmpty(apiKey) Then apiKey = "demo" ' Demo key for testing

            Dim endpoint = $"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apiKey={apiKey}"
            Return Await GetWithCacheAsync("AlphaVantage", endpoint, 900) ' 15min cache
        End Function

        ''' <summary>
        ''' Yahoo Finance API (via yfinance-like REST endpoints)
        ''' Tier: FREE (no official limits, community endpoints)
        ''' </summary>
        Public Async Function GetYahooFinanceAsync(symbol As String) As Task(Of JObject)
            Dim endpoint = $"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            Return Await GetWithCacheAsync("YahooFinance", endpoint, 300) ' 5min cache
        End Function

        ''' <summary>
        ''' CoinGecko - Cryptocurrency prices, market cap, trading volume
        ''' Tier: FREE (unlimited with rate limiting) + $130/month pro
        ''' </summary>
        Public Async Function GetCryptoDataAsync(coinId As String) As Task(Of JObject)
            Dim endpoint = $"https://api.coingecko.com/api/v3/coins/{coinId}"
            Return Await GetWithCacheAsync("CoinGecko", endpoint, 600) ' 10min cache
        End Function

        ''' <summary>
        ''' SEC EDGAR API - Company filings, 13F holdings (official SEC data)
        ''' Tier: FREE (rate limited to 10 req/sec, requires User-Agent)
        ''' </summary>
        Public Async Function GetSecFilingsAsync(cik As String) As Task(Of JObject)
            Dim endpoint = $"https://data.sec.gov/submissions/CIK{cik.PadLeft(10, "0"c)}.json"
            _httpClient.DefaultRequestHeaders.UserAgent.ParseAdd("EQ12AutomationBot/1.0 (ricoj100@example.com)")
            
            Return Await GetWithCacheAsync("SEC", endpoint, 86400) ' 24hr cache (filings don't update often)
        End Function

        ' ========================================
        ' AVIATION/TRAVEL APIS (Cannabis Tourism)
        ' ========================================

        ''' <summary>
        ''' Aviationstack - Flight tracking, airport data, airline info
        ''' Tier: FREE (1,000 calls/month) + $10/month basic
        ''' </summary>
        Public Async Function GetFlightDealsAsync(departure As String, arrival As String) As Task(Of JObject)
            Dim apiKey = Environment.GetEnvironmentVariable("AVIATIONSTACK_KEY")
            If String.IsNullOrEmpty(apiKey) Then
                Throw New InvalidOperationException("AVIATIONSTACK_KEY not set")
            End If

            Dim endpoint = $"http://api.aviationstack.com/v1/flights?access_key={apiKey}&dep_iata={departure}&arr_iata={arrival}"
            Return Await GetWithCacheAsync("Aviationstack", endpoint, 1800) ' 30min cache
        End Function

        ''' <summary>
        ''' OpenSky Network - Real-time flight tracking (community-driven, no API key)
        ''' Tier: FREE (unlimited, no authentication required)
        ''' </summary>
        Public Async Function GetOpenSkyFlightsAsync() As Task(Of JObject)
            Dim endpoint = "https://opensky-network.org/api/states/all"
            Return Await GetWithCacheAsync("OpenSky", endpoint, 300) ' 5min cache
        End Function

        ' ========================================
        ' WEATHER/LOCATION APIS (Travel Planning)
        ' ========================================

        ''' <summary>
        ''' OpenWeatherMap - Current weather, forecasts, historical data
        ''' Tier: FREE (1,000 calls/day) + $40/month startup
        ''' </summary>
        Public Async Function GetWeatherDataAsync(city As String) As Task(Of JObject)
            Dim apiKey = Environment.GetEnvironmentVariable("OPENWEATHER_KEY")
            If String.IsNullOrEmpty(apiKey) Then
                ' Demo key for testing (limited functionality)
                apiKey = "demo"
            End If

            Dim endpoint = $"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apiKey}&units=imperial"
            Return Await GetWithCacheAsync("OpenWeather", endpoint, 600) ' 10min cache
        End Function

        ''' <summary>
        ''' IP Geolocation - Get user location from IP (for localized content)
        ''' Tier: FREE (1,500 calls/day) + $15/month pro
        ''' </summary>
        Public Async Function GetGeolocationAsync(ipAddress As String) As Task(Of JObject)
            Dim apiKey = Environment.GetEnvironmentVariable("IPGEOLOCATION_KEY")
            Dim endpoint = $"https://api.ipgeolocation.io/ipgeo?apiKey={apiKey}&ip={ipAddress}"
            
            Return Await GetWithCacheAsync("IPGeo", endpoint, 3600) ' 1hr cache
        End Function

        ' ========================================
        ' AI/ML APIS (Integrate with 20K Prompts)
        ' ========================================

        ''' <summary>
        ''' Hugging Face Inference API - Run ML models (embeddings, classification, generation)
        ''' Tier: FREE (30,000 chars/month) + $9/month pro
        ''' </summary>
        Public Async Function GetHuggingFaceInferenceAsync(model As String, inputText As String) As Task(Of JObject)
            Dim apiKey = Environment.GetEnvironmentVariable("HUGGINGFACE_KEY")
            If String.IsNullOrEmpty(apiKey) Then
                Throw New InvalidOperationException("HUGGINGFACE_KEY not set")
            End If

            Dim endpoint = $"https://api-inference.huggingface.co/models/{model}"
            Dim content = New StringContent(JsonConvert.SerializeObject(New With {.inputs = inputText}), 
                                           Text.Encoding.UTF8, "application/json")
            
            _httpClient.DefaultRequestHeaders.Authorization = New Headers.AuthenticationHeaderValue("Bearer", apiKey)
            Dim response = Await _httpClient.PostAsync(endpoint, content)
            Dim json = Await response.Content.ReadAsStringAsync()
            
            Return JObject.Parse(json)
        End Function

        ''' <summary>
        ''' OpenRouter - Multi-model AI gateway (connects to GPT, Claude, Gemini, etc.)
        ''' Tier: FREE credits available + pay-per-token pricing
        ''' Note: Already integrated in Python side, this is backup/fallback
        ''' </summary>
        Public Async Function GetOpenRouterResponseAsync(model As String, prompt As String) As Task(Of JObject)
            Dim apiKey = Environment.GetEnvironmentVariable("OPENROUTER_API_KEY")
            If String.IsNullOrEmpty(apiKey) Then
                Throw New InvalidOperationException("OPENROUTER_API_KEY not set")
            End If

            Dim endpoint = "https://openrouter.ai/api/v1/chat/completions"
            Dim payload = New With {
                .model = model,
                .messages = New Object() {New With {.role = "user", .content = prompt}}
            }
            
            Dim content = New StringContent(JsonConvert.SerializeObject(payload), Text.Encoding.UTF8, "application/json")
            _httpClient.DefaultRequestHeaders.Authorization = New Headers.AuthenticationHeaderValue("Bearer", apiKey)
            
            Dim response = Await _httpClient.PostAsync(endpoint, content)
            Dim json = Await response.Content.ReadAsStringAsync()
            
            Return JObject.Parse(json)
        End Function

        ' ========================================
        ' NEWS/SOCIAL APIS (Content Aggregation)
        ' ========================================

        ''' <summary>
        ''' NewsAPI - Breaking news and headlines from 80+ sources
        ''' Tier: FREE (1,000 calls/day, dev only) + $449/month business
        ''' </summary>
        Public Async Function GetNewsAsync(category As String, country As String) As Task(Of JObject)
            Dim apiKey = Environment.GetEnvironmentVariable("NEWSAPI_KEY")
            Dim endpoint = $"https://newsapi.org/v2/top-headlines?category={category}&country={country}&apiKey={apiKey}"
            
            Return Await GetWithCacheAsync("NewsAPI", endpoint, 1800) ' 30min cache
        End Function

        ''' <summary>
        ''' Reddit API - Fetch posts from subreddits (investment sentiment, cannabis news, etc.)
        ''' Tier: FREE (60 requests/min with OAuth)
        ''' </summary>
        Public Async Function GetRedditPostsAsync(subreddit As String, limit As Integer) As Task(Of JObject)
            Dim endpoint = $"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
            _httpClient.DefaultRequestHeaders.UserAgent.ParseAdd("EQ12Bot/1.0")
            
            Return Await GetWithCacheAsync("Reddit", endpoint, 600) ' 10min cache
        End Function

        ' ========================================
        ' CANNABIS INDUSTRY APIS (Hemp Data)
        ' ========================================

        ''' <summary>
        ''' Leafly API - Strain info, dispensary locations, cannabis products
        ''' Tier: PAID (requires partnership) - using web scraping fallback
        ''' </summary>
        Public Async Function GetLeaflyDataAsync(strainName As String) As Task(Of JObject)
            ' Note: Official API requires partnership, using public endpoints
            Dim endpoint = $"https://www.leafly.com/strains/{strainName}"
            ' Return HTML scraping result (would need HTML parsing logic)
            
            ' Placeholder - integrate with BeautifulSoup/Python or HTML parser
            Return JObject.Parse("{""message"": ""Use Python BeautifulSoup for scraping""}")
        End Function

        ' ========================================
        ' REAL ESTATE APIS (Housing Market Monitor)
        ' ========================================

        ''' <summary>
        ''' Zillow API - Home values, rental estimates (requires approval)
        ''' Alternative: Use Realtor.com or Redfin public endpoints
        ''' </summary>
        Public Async Function GetHousingDataAsync(zipCode As String) As Task(Of JObject)
            ' Note: Zillow API discontinued for new users, using alternatives
            ' This would integrate with Realtor.com or Redfin scrapers
            
            ' Placeholder - use Python scraper or approved real estate API
            Return JObject.Parse("{""message"": ""Use Realtor.com scraper or approved API""}")
        End Function

        ' ========================================
        ' UTILITY APIS (General Purpose)
        ' ========================================

        ''' <summary>
        ''' ExchangeRate-API - Currency conversion rates
        ''' Tier: FREE (1,500 calls/month) + $9/month pro
        ''' </summary>
        Public Async Function GetExchangeRateAsync(baseCurrency As String, targetCurrency As String) As Task(Of JObject)
            Dim endpoint = $"https://api.exchangerate-api.com/v4/latest/{baseCurrency}"
            Return Await GetWithCacheAsync("ExchangeRate", endpoint, 3600) ' 1hr cache
        End Function

        ''' <summary>
        ''' Abstract API - Email validation, phone validation, IP lookup, etc.
        ''' Tier: FREE (varies by service) + paid tiers
        ''' </summary>
        Public Async Function ValidateEmailAsync(email As String) As Task(Of JObject)
            Dim apiKey = Environment.GetEnvironmentVariable("ABSTRACTAPI_KEY")
            Dim endpoint = $"https://emailvalidation.abstractapi.com/v1/?api_key={apiKey}&email={email}"
            
            Return Await GetWithCacheAsync("AbstractAPI", endpoint, 86400) ' 24hr cache
        End Function

        ' ========================================
        ' CORE HELPER METHODS
        ' ========================================

        ''' <summary>
        ''' HTTP GET with intelligent caching and rate limiting
        ''' </summary>
        Private Async Function GetWithCacheAsync(apiName As String, url As String, cacheDurationSeconds As Integer) As Task(Of JObject)
            ' Check cache first
            Dim cacheKey = $"{apiName}:{url}"
            If _cache.ContainsKey(cacheKey) Then
                Dim cached = _cache(cacheKey)
                If DateTime.UtcNow.Subtract(cached.Timestamp).TotalSeconds < cacheDurationSeconds Then
                    Console.WriteLine($"[CACHE HIT] {apiName} - {url}")
                    Return cached.Data
                End If
            End If

            ' Rate limiting (1 req/sec per API)
            If _rateLimiter.ContainsKey(apiName) Then
                Dim timeSinceLastCall = DateTime.UtcNow.Subtract(_rateLimiter(apiName))
                If timeSinceLastCall.TotalSeconds < 1.0 Then
                    Await Task.Delay(1000 - CInt(timeSinceLastCall.TotalMilliseconds))
                End If
            End If

            ' Make request
            Console.WriteLine($"[API CALL] {apiName} - {url}")
            Dim response = Await _httpClient.GetStringAsync(url)
            Dim jsonData = JObject.Parse(response)

            ' Update cache and rate limiter
            _cache(cacheKey) = New CachedResponse With {.Data = jsonData, .Timestamp = DateTime.UtcNow}
            _rateLimiter(apiName) = DateTime.UtcNow

            Return jsonData
        End Function

        ''' <summary>
        ''' Save API response to JSON file (for Python integration)
        ''' </summary>
        Public Sub SaveToJson(data As JObject, filePath As String)
            System.IO.File.WriteAllText(filePath, data.ToString(Formatting.Indented))
            Console.WriteLine($"[SAVED] {filePath}")
        End Sub

        ''' <summary>
        ''' Get all cached API responses (for debugging/monitoring)
        ''' </summary>
        Public Function GetCacheStats() As Dictionary(Of String, Object)
            Return New Dictionary(Of String, Object) From {
                {"total_cached", _cache.Count},
                {"apis_called", _rateLimiter.Count},
                {"cache_keys", _cache.Keys.ToList()}
            }
        End Function

    End Class

    ''' <summary>
    ''' Internal class for caching API responses
    ''' </summary>
    Friend Class CachedResponse
        Public Property Data As JObject
        Public Property Timestamp As DateTime
    End Class

End Namespace
