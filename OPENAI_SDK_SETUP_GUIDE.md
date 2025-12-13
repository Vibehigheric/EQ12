# 🤖 EQ12 OpenAI Python SDK Setup Guide

## 🚀 **Quick Start - OpenAI API Setup**

Your EQ12 environment already has OpenAI configured! Here's how to use it effectively:

### **✅ Current Configuration**
- **OpenAI SDK**: `openai>=1.0.0` (already installed)
- **API Key**: Configured in `.env` file
- **Models**: GPT-4o (primary), with intelligent fallbacks
- **Integration**: Professional client with usage tracking

---

## 📋 **Available OpenAI Tasks**

Access via **Command Palette** (`Ctrl+Shift+P`) → **Tasks: Run Task**

### **🔧 Setup & Testing**
- **`EQ12: Setup OpenAI SDK`** - Initialize and test OpenAI integration
- **`EQ12: Test OpenAI Integration`** - Verify API connection and models
- **`EQ12: Bootstrap Environment`** - Includes OpenAI dependency check

---

## 🛠️ **Using the EQ12 OpenAI Client**

### **Basic Usage**
```python
from eq12_openai_setup import EQ12OpenAIClient

# Initialize client (uses env vars automatically)
client = EQ12OpenAIClient()

# Basic chat completion
messages = [
    {"role": "system", "content": "You are a sports betting expert."},
    {"role": "user", "content": "What is expected value in betting?"}
]

response = client.chat_completion(messages)
print(response.choices[0].message.content)
```

### **Sports Betting Analysis** (EQ12 Specialized)
```python
# EQ12-specific sports betting analysis
game_data = """
NFL Game: Kansas City Chiefs vs Buffalo Bills
Spread: KC -3.5 (-110), BUF +3.5 (-110)
Total: Over 54.5 (-110), Under 54.5 (-110)
Moneyline: KC -175, BUF +145
Weather: Clear, 72°F, Wind 5mph
"""

# Different analysis types available
analysis = client.sports_betting_analysis(game_data, "general")
sgp_analysis = client.sports_betting_analysis(game_data, "sgp")
value_analysis = client.sports_betting_analysis(game_data, "value")
risk_analysis = client.sports_betting_analysis(game_data, "risk")
```

### **Async Usage**
```python
import asyncio

async def async_analysis():
    client = EQ12OpenAIClient()

    messages = [
        {"role": "user", "content": "Analyze this NBA game for betting opportunities"}
    ]

    response = await client.async_chat_completion(messages)
    return response.choices[0].message.content

# Run async
result = asyncio.run(async_analysis())
```

---

## ⚙️ **Environment Configuration**

Your `.env` file is already configured with:

```properties
# OpenAI Configuration (already set)
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7
OPENAI_TOP_P=1.0
OPENAI_FALLBACK_MODELS=gpt-4o-mini,gpt-4-turbo,gpt-4,gpt-3.5-turbo
```

### **Model Configuration Options**
- **`OPENAI_MODEL`**: Primary model (gpt-4o, gpt-4o-mini, gpt-4-turbo)
- **`OPENAI_FALLBACK_MODELS`**: Comma-separated fallback models
- **`OPENAI_MAX_TOKENS`**: Maximum tokens per request (default: 4096)
- **`OPENAI_TEMPERATURE`**: Randomness level (0.0-2.0, default: 0.7)

---

## 📊 **Professional Features**

### **Automatic Fallback System**
```python
client = EQ12OpenAIClient()

# Automatically tries models in order:
# 1. gpt-4o (primary)
# 2. gpt-4o-mini (fallback 1)
# 3. gpt-4-turbo (fallback 2)
# 4. gpt-4 (fallback 3)
# 5. gpt-3.5-turbo (final fallback)

response = client.chat_completion(messages)  # Handles failures gracefully
```

### **Usage Tracking & Cost Monitoring**
```python
# Get comprehensive usage statistics
report = client.get_usage_report()
print(f"Total requests: {report['total_requests']}")
print(f"Total tokens: {report['total_tokens']}")
print(f"Estimated cost: ${report['total_cost_estimate']:.4f}")

# Save detailed usage report
client.save_usage_report()  # Saves to logs/openai_usage_report_*.json
```

### **Professional Logging**
All OpenAI API calls are logged to:
- **`logs/openai_usage.log`** - Detailed API call logs
- **`logs/openai_usage_report_*.json`** - Periodic usage reports

---

## 🎯 **EQ12 Sports Betting Integration**

### **Analysis Types**
- **`"general"`** - Overall game analysis and betting strategy
- **`"sgp"`** - Same Game Parlay correlation analysis
- **`"value"`** - Expected value and line shopping recommendations
- **`"risk"`** - Risk management and position sizing

### **Example: NFL Game Analysis**
```python
client = EQ12OpenAIClient()

nfl_data = """
Game: Dallas Cowboys @ Green Bay Packers
Spread: GB -7.5 (-110), DAL +7.5 (-110)
Total: O/U 48.5 (-110)
Weather: 28°F, Snow, Wind 15mph
Key Injuries: DAL QB1 Questionable, GB WR1 Out
"""

# Get comprehensive analysis
analysis = client.sports_betting_analysis(nfl_data, "general")
print("General Analysis:", analysis)

# Get SGP opportunities
sgp_recs = client.sports_betting_analysis(nfl_data, "sgp")
print("SGP Recommendations:", sgp_recs)
```

---

## 🧪 **Testing Your Setup**

### **Option 1: Run Setup Test**
```powershell
# Command Palette → Tasks: Run Task → "EQ12: Setup OpenAI SDK"
# Or in terminal:
python eq12_openai_setup.py
```

### **Option 2: Quick Integration Test**
```powershell
# Command Palette → Tasks: Run Task → "EQ12: Test OpenAI Integration"
```

### **Option 3: Manual Test**
```python
# Test in Python console
from eq12_openai_setup import EQ12OpenAIClient
client = EQ12OpenAIClient()

# Should print: ✅ EQ12 OpenAI Client initialized with model: gpt-4o
```

---

## 📚 **Advanced Usage Examples**

### **Custom Model Parameters**
```python
# Override default parameters
response = client.chat_completion(
    messages=messages,
    model="gpt-4o-mini",  # Force specific model
    temperature=0.3,      # More focused responses
    max_tokens=1024,      # Shorter responses
    top_p=0.9            # Alternative to temperature
)
```

### **Streaming Responses** (Coming Soon)
```python
# Future enhancement for real-time analysis
for chunk in client.chat_completion_stream(messages):
    print(chunk.choices[0].delta.content, end='')
```

### **Batch Processing** (Coming Soon)
```python
# Future enhancement for multiple game analysis
games = [game1_data, game2_data, game3_data]
analyses = await client.batch_sports_analysis(games)
```

---

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

#### **API Key Not Found**
```bash
❌ Error: OPENAI_API_KEY not found
💡 Solution: Check your C:\EQ12\.env file contains:
   OPENAI_API_KEY=sk-your-key-here
```

#### **Model Not Available**
```bash
❌ Error: Model gpt-4o not available
💡 Solution: Client automatically falls back to available models
   Check your OpenAI account limits and billing
```

#### **Rate Limit Exceeded**
```bash
❌ Error: Rate limit exceeded
💡 Solution: Client includes automatic retry logic
   Consider upgrading OpenAI account tier
```

#### **Import Errors**
```bash
❌ Error: No module named 'openai'
💡 Solution: Run bootstrap task or install manually:
   pip install openai>=1.0.0
```

### **Debug Mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enables detailed API call logging
client = EQ12OpenAIClient()
```

---

## 🎯 **Integration with EQ12 Workflow**

### **With EQ12 Scheduler**
```python
# In eq12_scheduler.py or similar
from eq12_openai_setup import EQ12OpenAIClient

def analyze_daily_games():
    client = EQ12OpenAIClient()

    for game in today_games:
        analysis = client.sports_betting_analysis(
            game.to_string(),
            "value"
        )
        save_analysis(game.id, analysis)
```

### **With Telegram Bot**
```python
# In telegram bot handlers
async def handle_analysis_request(update, context):
    client = EQ12OpenAIClient()

    game_data = extract_game_data(update.message.text)
    analysis = client.sports_betting_analysis(game_data, "general")

    await update.message.reply_text(f"🏈 Analysis:\n{analysis}")
```

### **With Dashboard**
```python
# In dashboard endpoints
@app.route('/api/analyze')
def analyze_game():
    client = EQ12OpenAIClient()

    game_data = request.json.get('game_data')
    analysis_type = request.json.get('type', 'general')

    result = client.sports_betting_analysis(game_data, analysis_type)
    usage = client.get_usage_report()

    return jsonify({
        'analysis': result,
        'usage': usage
    })
```

---

## 📈 **Usage Monitoring**

### **Real-Time Monitoring**
```python
# Check usage statistics anytime
client = EQ12OpenAIClient()
report = client.get_usage_report()

print(f"Session requests: {report['total_requests']}")
print(f"Session tokens: {report['total_tokens']}")
print(f"Session cost: ${report['total_cost_estimate']:.4f}")
print(f"Avg tokens/request: {report['avg_tokens_per_request']:.1f}")
```

### **Cost Control**
```python
# Set usage limits (future enhancement)
client = EQ12OpenAIClient()
client.set_daily_limit(max_cost=10.00)  # $10 daily limit
client.set_request_limit(max_requests=100)  # 100 requests/day
```

---

## 🚀 **Next Steps**

1. **Test Your Setup**:
   ```powershell
   # Run this in VS Code terminal or Command Palette
   python eq12_openai_setup.py
   ```

2. **Try Sports Analysis**:
   ```python
   from eq12_openai_setup import EQ12OpenAIClient
   client = EQ12OpenAIClient()
   # Copy game data and test analysis
   ```

3. **Monitor Usage**:
   ```python
   # Check logs/openai_usage.log for detailed logs
   # Run usage report task periodically
   ```

4. **Integrate with EQ12 Stack**:
   - Add OpenAI analysis to your betting workflows
   - Enhance Telegram bot with AI responses
   - Create AI-powered dashboard features

---

**🎉 Your EQ12 OpenAI Python SDK is ready for professional sports betting automation!**

**Use the Command Palette tasks or import `EQ12OpenAIClient` in your Python scripts to get started.**
