# EQ12 API Catalog - Free/Freemium Integration Guide

## 🎯 **Overview**

The **EQ12 API Catalog** provides centralized management of all free and freemium APIs used across the sports betting, ML, weather, and finance automation stack.

**Total APIs**: 22 (19 enabled by default)
**Categories**: odds, sports, ml, weather, props, finance, news, misc

---

## 📚 **Complete API Inventory**

### **Odds APIs** (3 total)
1. **The Odds API** ✅ (Priority 1, 98% reliability)
   - Free tier: 500 requests/month
   - Already integrated in 100-source registry
   - Primary odds source for MLB, NBA, NFL, CFB, Soccer, UFC

2. **Sports Game Odds** (Priority 3, 92% reliability)
   - Backup odds source
   - Good for cross-validation
   - Currently disabled (enable if needed)

3. **PrizePicks (Unofficial)** ✅ (Priority 1, 94% reliability)
   - No auth required
   - Player props lines
   - In 100-source registry

---

### **Sports Stats APIs** (4 total)
1. **API-SPORTS (Football)** ✅ (Priority 2, 95% reliability)
   - 100 requests/day forever free
   - Stats + fixtures + odds for football/soccer

2. **API-SPORTS (Basketball)** ✅ (Priority 2, 95% reliability)
   - NBA stats, fixtures, standings, player data

3. **API-SPORTS (Baseball)** ✅ (Priority 2, 95% reliability)
   - MLB stats, fixtures, player data

4. **ESPN Hidden API** ✅ (Priority 2, 97% reliability)
   - No auth required
   - Free stats, scores, schedules for all major sports

---

### **ML / LLM / AI APIs** (5 total)
1. **Hugging Face Hub** ✅ (Priority 1, 99% reliability)
   - Metadata for models/datasets (free)
   - Integrated in VB.NET client

2. **Hugging Face Inference** ✅ (Priority 1, 96% reliability)
   - Serverless model execution
   - Embeddings, classification, small LLMs

3. **OpenRouter** ✅ (Priority 1, 98% reliability)
   - FREE tier available
   - Already used in 20K prompt execution

4. **Groq** ✅ (Priority 1, 97% reliability)
   - FREE unlimited (500 tokens/sec)
   - Fallback in prompt system

5. **Google AI (Gemini)** ✅ (Priority 2, 98% reliability)
   - Free tier with generous limits
   - Text generation, embeddings

---

### **Weather APIs** (3 total)
1. **OpenWeatherMap** ✅ (Priority 1, 97% reliability)
   - 1000 calls/day free
   - Essential for outdoor sports
   - Integrated in VB.NET client

2. **WeatherAPI.com** ✅ (Priority 1, 96% reliability)
   - 1M calls/month free
   - Generous free tier

3. **Tomorrow.io** (Priority 2, 95% reliability)
   - Advanced weather metrics
   - Currently disabled

---

### **Props APIs** (2 total)
1. **PrizePicks** ✅ (see above)
2. **Underdog Fantasy** ✅ (Priority 1, 93% reliability)
   - No auth required
   - Player props, pick'em lines

---

### **Finance APIs** (2 total)
1. **SEC EDGAR** ✅ (Priority 1, 99% reliability)
   - Free SEC public data
   - Already integrated (eq12_sec_13f_scraper.py)

2. **Alpha Vantage** (Priority 2, 96% reliability)
   - 500 requests/day free
   - Stock quotes, forex, crypto
   - Currently disabled

---

### **News APIs** (1 total)
1. **NewsAPI.org** (Priority 2, 95% reliability)
   - 100 requests/day free
   - Sports news, injury reports
   - Currently disabled

---

### **Misc / Utility APIs** (2 total)
1. **GitHub API** ✅ (Priority 1, 99% reliability)
   - 5000 requests/hour (authenticated)
   - Used for automation

2. **Telegram Bot API** ✅ (Priority 1, 98% reliability)
   - Unlimited messages
   - Betting alerts, notifications

---

## 🔧 **Usage Examples**

### **1. List All APIs**
```vbnet
Dim catalog As New ApiCatalog()
Dim allApis = catalog.GetAll()

For Each api In allApis
    Console.WriteLine($"{api.Name} - {api.Category} - {api.FreeTierDescription}")
Next
```

### **2. Get APIs by Category**
```vbnet
Dim oddsApis = catalog.GetByCategory("odds")
Dim mlApis = catalog.GetByCategory("ml")
Dim weatherApis = catalog.GetByCategory("weather")
```

### **3. Get Recommendations for Use Case**
```vbnet
' Get best odds APIs (enabled, sorted by priority)
Dim recommendedOdds = catalog.GetRecommendation("odds")

' Get best ML/LLM APIs
Dim recommendedML = catalog.GetRecommendation("ml")

' Get best weather APIs
Dim recommendedWeather = catalog.GetRecommendation("weather")
```

### **4. Sort by Reliability**
```vbnet
Dim mostReliable = catalog.GetByReliability()
' Returns: SEC EDGAR (99%), Hugging Face Hub (99%), GitHub (99%), etc.
```

### **5. Sort by Latency (Fastest)**
```vbnet
Dim fastest = catalog.GetByLatency()
' Returns: Hugging Face Hub (120ms), GitHub (120ms), ESPN (150ms), etc.
```

---

## 🌐 **Integrated Clients**

### **The Odds API Client**
```vbnet
Dim apiKey = Environment.GetEnvironmentVariable("ODDS_API_KEY")
Using client As New OddsApiClient(apiKey)
    Dim mlbOdds = Await client.GetMlbOddsAsync()
    Dim nbaOdds = Await client.GetNbaOddsAsync()
    Dim nflOdds = Await client.GetNflOddsAsync()
End Using
```

### **Hugging Face Client**
```vbnet
Dim token = Environment.GetEnvironmentVariable("HF_API_TOKEN")
Using client As New HuggingFaceClient(token)
    ' Search for models
    Dim models = Await client.SearchModelsAsync("text-classification", 10)
    
    ' Get model info
    Dim modelInfo = Await client.GetModelInfoAsync("gpt2")
End Using
```

### **Hugging Face Inference Client**
```vbnet
Using client As New HuggingFaceInferenceClient(token)
    ' Classify text
    Dim result = Await client.ClassifyTextAsync(
        "distilbert-base-uncased-finetuned-sst-2-english",
        "I love sports betting automation!"
    )
    
    ' Get embeddings
    Dim embeddings = Await client.GetEmbeddingsAsync(
        "sentence-transformers/all-MiniLM-L6-v2",
        "Aaron Judge home run probability"
    )
End Using
```

### **Weather API Client**
```vbnet
Dim apiKey = Environment.GetEnvironmentVariable("OPENWEATHER_API_KEY")
Using client As New WeatherApiClient(apiKey)
    ' Current weather
    Dim weather = Await client.GetCurrentWeatherAsync(40.8296, -73.9262) ' Yankee Stadium
    
    ' Forecast
    Dim forecast = Await client.GetForecastAsync(40.8296, -73.9262)
    
    ' Game-day weather
    Dim gameWeather = Await client.GetGameDayWeatherAsync(
        StadiumLocation.YankeeStadium,
        DateTime.Parse("2025-06-15 19:05")
    )
End Using
```

---

## 📊 **API Health Tracking**

Each `ApiInfo` object tracks runtime health:

```vbnet
Dim api = catalog.FindByName("The Odds API")

' Runtime metrics (auto-updated by ApiClientBase)
Console.WriteLine($"Last Checked: {api.LastChecked}")
Console.WriteLine($"Is Healthy: {api.IsHealthy}")
Console.WriteLine($"Success Rate: {api.SuccessRate:P2}")
Console.WriteLine($"Error Count: {api.ErrorCount}")
Console.WriteLine($"Success Count: {api.SuccessCount}")
```

---

## 🔄 **Automatic Retry & Error Handling**

All clients inherit from `ApiClientBase` which provides:
- ✅ **Automatic retries** (3 attempts with exponential backoff)
- ✅ **Health tracking** (success/error counts)
- ✅ **Timeout handling** (30 second default)
- ✅ **Authentication** (auto-loads from environment variables)

```vbnet
' Retry logic built-in
Protected Async Function GetAsync(url As String, Optional maxRetries As Integer = 3) As Task(Of String)
    ' Attempts: 1s delay → 2s delay → 4s delay
    ' Updates ApiInfo.IsHealthy, ApiInfo.ErrorCount, ApiInfo.SuccessCount
End Function
```

---

## 🎯 **Integration with Dashboard**

The catalog powers the EQ12 Sports Betting Orchestrator dashboard:

### **API Status Cards**
```vbnet
' Display in dashboard
Dim enabledApis = catalog.GetEnabled()
For Each api In enabledApis
    ' Show in UI grid:
    ' - Name, Category, Priority, Reliability
    ' - Health status (green/yellow/red)
    ' - Last checked timestamp
    ' - Success rate percentage
Next
```

### **Use Case Recommendations**
```vbnet
' When user clicks "Get Odds"
Dim oddsApis = catalog.GetRecommendation("odds")
' Use oddsApis(0) as primary, oddsApis(1) as fallback

' When user clicks "Check Weather"
Dim weatherApis = catalog.GetRecommendation("weather")
' Use fastest/most reliable weather API
```

---

## 🔐 **Environment Variables Required**

```powershell
# Odds
$env:ODDS_API_KEY = "your_key_here"

# ML / AI
$env:HF_API_TOKEN = "hf_..."
$env:OPENROUTER_API_KEY = "sk-or-v1-..."
$env:GROQ_API_KEY = "gsk_..."
$env:GOOGLE_AI_API_KEY = "AIzaSy..."

# Weather
$env:OPENWEATHER_API_KEY = "your_key_here"
$env:WEATHERAPI_KEY = "your_key_here"

# Sports Stats
$env:APISPORTS_FOOTBALL_KEY = "your_key_here"
$env:APISPORTS_BASKETBALL_KEY = "your_key_here"
$env:APISPORTS_BASEBALL_KEY = "your_key_here"

# Finance
# (SEC EDGAR requires no key)

# Misc
$env:GITHUB_TOKEN = "ghp_..."
$env:TELEGRAM_BOT_TOKEN = "123456:ABC..."
```

---

## 🚀 **Next Steps**

### **Phase 1** (Current - Complete ✅)
- API catalog with 22 APIs
- ApiClientBase with retry logic
- OddsApiClient, HuggingFaceClient, WeatherApiClient
- Health tracking and metrics

### **Phase 2** (After 20K prompts, ~54 hours)
- Implement remaining API clients:
  - API-SPORTS (Football, Basketball, Baseball)
  - ESPN API client
  - PrizePicks/Underdog clients
  - Telegram client
- Dashboard UI with API status cards
- Real-time health monitoring

### **Phase 3** (Production)
- API failover logic (auto-switch to backup if primary fails)
- Rate limit tracking per API
- Cost tracking (for paid tiers)
- API response caching layer

---

**Status**: Core Infrastructure Complete ✅
**Integrated with**: EQ12 Sports Betting Orchestrator, 100-source registry, SEC scraper, prompt execution
**Ready for**: Dashboard UI implementation, real-world testing
**Created**: 2025-11-27
