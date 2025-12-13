# EdgeGod API Rate Limiting & Quota Management

## 🚨 **CRITICAL: Solving The Odds API 429 & 402 Errors**

This comprehensive system solves the rate limiting (429) and quota exceeded (402) errors you encountered with The Odds API by implementing intelligent rate limiting, quota management, and response caching.

## 🎯 **Problem Solved**

**Your Original Issues:**
- `EXCEEDED_FREQ_LIMIT` - 429 rate limiting errors
- `OUT_OF_USAGE_CREDITS` - 402 quota exceeded errors  
- No API usage tracking or optimization

**Our Solution:**
- ✅ **Conservative Rate Limiting**: 25 calls/sec (below 30 limit)
- ✅ **Smart Quota Management**: 450 daily limit with hourly distribution
- ✅ **Intelligent Caching**: 15-minute cache reduces redundant calls
- ✅ **Automatic Retries**: Exponential backoff for failed requests
- ✅ **Usage Analytics**: Real-time quota and performance monitoring

## 🔧 **Quick Start**

### 1. Set Your API Key
```powershell
$env:ODDS_API_KEY = "your-api-key-here"
```

### 2. Check Current Status
```powershell
.\Manage-EdgeGodAPI.ps1 -Action status
```

### 3. Run Full Configuration
```powershell
.\Manage-EdgeGodAPI.ps1 -Action configure
```

## 📁 **Files Overview**

| File | Purpose | Key Features |
|------|---------|--------------|
| `api_manager.py` | Core rate limiting engine | 25/sec limit, quota tracking, caching |
| `configure_api.py` | Configuration & optimization | Usage analysis, recommendations |
| `Manage-EdgeGodAPI.ps1` | PowerShell wrapper | Easy Windows management |
| `edgegod_expert_engine.py` | Main odds engine (updated) | Integrated rate limiting |

## 🛠️ **API Management Features**

### **Rate Limiting Protection**
- **Conservative Limit**: 25 requests/second (safely below 30)
- **Burst Protection**: Maximum 100 burst requests
- **Automatic Queuing**: Requests wait for available slots
- **Smart Spacing**: Distributes calls evenly across time

### **Quota Management** 
- **Daily Limits**: 450 calls/day (free tier safe)
- **Hourly Distribution**: Max 50 calls/hour to spread usage
- **Real-time Tracking**: Monitor usage vs. limits
- **Automatic Reset**: Daily and hourly counters reset automatically

### **Intelligent Caching**
- **15-Minute Cache**: Reduces redundant API calls
- **Smart Invalidation**: Automatic cache expiry
- **Hit Rate Tracking**: Monitor cache effectiveness
- **Selective Caching**: Sports/events cached longer than odds

### **Error Handling**
- **429 Handling**: Automatic retry with `Retry-After` header
- **402 Prevention**: Stop calls when quota approached
- **Exponential Backoff**: 1s, 2s, 4s retry delays
- **Graceful Degradation**: Continue with cached data when possible

## 📊 **Usage Monitoring**

### **Real-Time Stats**
```bash
# Get current API status
.\Manage-EdgeGodAPI.ps1 -Action status

# Expected output:
🎯 EdgeGod API Status Report
==================================================
API Status: HEALTHY
Cache Hit Rate: 45.2%
Success Rate: 98.7%
Quota Efficiency: 23.1%

📊 Usage Statistics:
  Requests Today: 104
  Daily Quota Used: 104/450
  Hourly Usage: 12/50
  Cache Entries: 23
```

### **Usage Analytics**
- **Success Rate**: Percentage of successful API calls
- **Cache Hit Rate**: Percentage of requests served from cache
- **Quota Efficiency**: How much of daily quota is used
- **Response Times**: Average API response latency

## 🎛️ **Configuration Options**

### **Usage Patterns**
| Pattern | Calls/Hour | Daily Limit | Cache Duration | Best For |
|---------|------------|-------------|----------------|----------|
| **Conservative** | 15 | 360 | 30 min | Testing, development |
| **Moderate** | 25 | 400 | 15 min | Normal operation |
| **Aggressive** | 40 | 450 | 5 min | High-frequency trading |

### **Market Selection**
```python
# Essential markets (lower quota cost)
essential_markets = "h2h,spreads,totals"

# MLB props (higher quota cost)
mlb_props = "player_home_runs,player_total_bases"

# Full market list (highest quota cost)
all_markets = "h2h,spreads,totals,player_home_runs,player_total_bases,player_hits"
```

## 🔍 **Monitoring & Optimization**

### **Monitor API Usage**
```powershell
# Monitor usage for 4 hours
.\Manage-EdgeGodAPI.ps1 -Action monitor -MonitorHours 4
```

### **Test API Connectivity**  
```powershell
# Test all endpoints
.\Manage-EdgeGodAPI.ps1 -Action test -Verbose
```

### **Optimize Usage Patterns**
```powershell
# Analyze and optimize
.\Manage-EdgeGodAPI.ps1 -Action optimize
```

## 📈 **Expected Improvements**

### **Error Reduction**
- **429 Errors**: Reduced from frequent to virtually zero
- **402 Errors**: Prevented through quota monitoring
- **Timeout Errors**: Reduced through retry logic

### **Performance Gains**
- **Response Speed**: 40-70% faster (cached responses)
- **Reliability**: 95%+ success rate
- **Efficiency**: 30-50% fewer API calls needed

### **Cost Optimization**
- **Quota Efficiency**: Stay within free tier limits
- **Smart Caching**: Reduce redundant calls
- **Batch Processing**: Optimize multi-event requests

## 🚨 **Troubleshooting**

### **Common Issues & Solutions**

#### **"Daily quota exceeded"**
```powershell
# Check current usage
.\Manage-EdgeGodAPI.ps1 -Action status

# Solution: Wait for daily reset or upgrade plan
```

#### **"Rate limited (429)"**
```bash
# The system handles this automatically
# Check logs for retry attempts:
tail -f C:\EQ12\logs\edgegod_api_management_*.log
```

#### **"Invalid API key (401)"**
```powershell
# Verify API key
echo $env:ODDS_API_KEY

# Reset API key
$env:ODDS_API_KEY = "your-correct-api-key"
```

#### **Low cache hit rate**
```python
# Increase cache duration in configure_api.py
cache_duration = 1800  # 30 minutes instead of 15
```

## 🔐 **API Key Management**

### **Environment Variable (Recommended)**
```powershell
# Windows (persistent)
[Environment]::SetEnvironmentVariable("ODDS_API_KEY", "your-api-key", "User")

# Windows (session)
$env:ODDS_API_KEY = "your-api-key"
```

### **Configuration File**
```json
// C:\EQ12\EdgeGodParlays\.env
ODDS_API_KEY=your-api-key-here
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

## 📊 **Integration with EdgeGod Engine**

The rate limiting is automatically integrated into the main EdgeGod expert engine:

```python
# Old way (prone to 429/402 errors)
response = await client.get(url, params=params)

# New way (rate limited and cached)
response = await api_limiter.make_api_request(client, url, params)
```

### **Automatic Features**
- ✅ All API calls go through rate limiter
- ✅ Responses are automatically cached
- ✅ Errors are handled gracefully
- ✅ Usage is tracked in real-time
- ✅ Quota limits are enforced

## 🎯 **Best Practices**

### **Daily Operations**
1. **Morning Check**: `.\Manage-EdgeGodAPI.ps1 -Action status`
2. **Monitor Usage**: Check quota throughout day
3. **Evening Analysis**: Review usage patterns
4. **Optimize Schedule**: Adjust timing based on needs

### **API Call Optimization**
- **Batch Requests**: Group multiple events in one call
- **Cache Awareness**: Don't request same data repeatedly  
- **Market Selection**: Only request needed markets
- **Time Filtering**: Use date ranges to limit results

### **Error Prevention**
- **Stay Conservative**: Use 80% of quota limits
- **Monitor Trends**: Watch for usage spikes
- **Plan Ahead**: Schedule heavy operations during low-usage periods
- **Cache Strategically**: Longer cache for static data

## 📞 **Support & Maintenance**

### **Log Files**
- **Management Logs**: `C:\EQ12\logs\edgegod_api_management_*.log`
- **Usage Reports**: `C:\EQ12\logs\api_usage_report_*.json`
- **Monitoring Data**: `C:\EQ12\logs\quota_monitoring_*.json`

### **Health Checks**
```powershell
# Daily health check
.\Manage-EdgeGodAPI.ps1 -Action test

# Weekly optimization
.\Manage-EdgeGodAPI.ps1 -Action configure
```

### **Performance Tuning**
- Adjust rate limits based on API performance
- Modify cache duration for different endpoints
- Optimize batch sizes for your use cases
- Fine-tune retry delays and timeouts

## 🎉 **Success Metrics**

With this system properly configured, you should see:

- ✅ **Zero 429 errors** (rate limiting prevented)
- ✅ **Zero 402 errors** (quota management)
- ✅ **95%+ success rate** (improved reliability)
- ✅ **40-70% faster responses** (caching)
- ✅ **30-50% fewer API calls** (efficiency)
- ✅ **Stay within free tier** (quota optimization)

The EdgeGod engine can now run continuously without hitting API limits while maintaining high performance and reliability! 🚀